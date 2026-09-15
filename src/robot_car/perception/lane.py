"""A conservative scanline baseline for two continuous white road borders.

Coordinates are image pixels: x right, y down. Only matched observations
produce center points; missing borders are never silently reconstructed.
"""

from dataclasses import dataclass
import math

import cv2
import numpy as np


@dataclass(frozen=True)
class LaneConfig:
    white_threshold: int = 190
    roi_top: float = 0.40
    roi_bottom: float = 0.95
    sample_step: int = 4
    max_marking_width: float = 0.045
    min_lane_width: float = 0.16
    max_lane_width: float = 0.95
    tracking_margin: float = 0.045
    max_gap_rows: int = 8
    min_coverage: float = 0.55
    min_vertical_span: float = 0.32
    reference_y: float = 0.85

    def __post_init__(self):
        for name in ("white_threshold", "sample_step", "max_gap_rows"):
            if type(getattr(self, name)) is not int:
                raise ValueError(f"{name} must be an integer")
        if not 0 <= self.white_threshold <= 255:
            raise ValueError("white_threshold must be in [0, 255]")
        if not 0 <= self.roi_top < self.roi_bottom < 1:
            raise ValueError("Require 0 <= roi_top < roi_bottom < 1")
        if self.sample_step < 1 or self.max_gap_rows < 0:
            raise ValueError("sample_step must be positive; max_gap_rows nonnegative")
        for name in ("max_marking_width", "tracking_margin", "min_coverage", "min_vertical_span"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if not 0 < self.min_lane_width < self.max_lane_width <= 1:
            raise ValueError("Invalid lane-width fractions")
        if not self.roi_top <= self.reference_y <= self.roi_bottom:
            raise ValueError("reference_y must lie inside the region of interest")


@dataclass
class LaneResult:
    grayscale: np.ndarray
    white_mask: np.ndarray
    lane_mask: np.ndarray
    # Columns: y, left_x, right_x, center_x. Observed pairs only.
    samples: np.ndarray
    valid: bool
    status: str
    coverage: float
    lateral_error_px: float | None
    lateral_error_normalized: float | None
    reference_y: float | None

    def to_dict(self):
        return {
            "valid": self.valid,
            "status": self.status,
            "coverage": self.coverage,
            "lateral_error_px": self.lateral_error_px,
            "lateral_error_normalized": self.lateral_error_normalized,
            "reference_y": self.reference_y,
            "coordinate_system": "image pixels; x right, y down; positive error means road center is right of image center",
            "samples": [dict(zip(("y", "left_x", "right_x", "center_x"), row.tolist())) for row in self.samples],
        }


def to_grayscale(frame: np.ndarray) -> np.ndarray:
    """Convert uint8 OpenCV BGR input; copy uint8 grayscale input unchanged."""
    if not isinstance(frame, np.ndarray) or frame.dtype != np.uint8:
        raise ValueError("Expected a uint8 numpy image")
    if frame.ndim not in (2, 3) or min(frame.shape[:2]) < 32:
        raise ValueError("Expected an image at least 32 x 32 pixels")
    if frame.ndim == 2:
        return frame.copy()
    if frame.shape[2] != 3:
        raise ValueError("Color input must have three BGR channels")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _runs(row: np.ndarray, max_width: int) -> list[tuple[float, int, int]]:
    edges = np.diff(np.pad((row > 0).astype(np.int8), (1, 1)))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    return [((a + b - 1) / 2, int(a), int(b)) for a, b in zip(starts, ends)
            if 2 <= b - a <= max_width and a > 0 and b < len(row)]


def detect_lane(frame: np.ndarray, config: LaneConfig | None = None) -> LaneResult:
    """Track two narrow bright runs upward from a plausible bottom pair.

    Assumes a forward/local view, visible borders, a road enclosing the image
    center near the bottom, and moderate curvature. Coverage is a support
    fraction, NOT a calibrated probability. No temporal state or ground truth.
    """
    cfg = config or LaneConfig()
    gray = to_grayscale(frame)
    h, w = gray.shape
    smoothed = cv2.GaussianBlur(gray, (3, 3), 0)
    _, mask = cv2.threshold(smoothed, cfg.white_threshold, 255, cv2.THRESH_BINARY)
    top, bottom = int(cfg.roi_top * (h - 1)), int(cfg.roi_bottom * (h - 1))
    mask[:top] = 0
    mask[bottom + 1:] = 0
    rows = list(range(bottom, top - 1, -cfg.sample_step))
    lane_mask = np.zeros_like(mask)
    samples = []
    history = []
    gap = 0
    image_center = (w - 1) / 2
    for row_index, y in enumerate(rows):
        runs = _runs(mask[y], max(2, int(w * cfg.max_marking_width)))
        pairs = [(a, b) for i, a in enumerate(runs) for b in runs[i + 1:]
                 if cfg.min_lane_width * w <= b[0] - a[0] <= cfg.max_lane_width * w]
        if not history:
            # Do not invent a new lane from arbitrary markings high in the image.
            if row_index > cfg.max_gap_rows:
                break
            pairs = [(a, b) for a, b in pairs if a[0] < image_center < b[0]]
            if not pairs:
                continue
            left, right = min(pairs, key=lambda p: abs((p[0][0] + p[1][0]) / 2 - image_center))
        else:
            last_y, last_left, last_right = history[-1]
            pred_left, pred_right = last_left, last_right
            if len(history) > 1:
                prev_y, prev_left, prev_right = history[-2]
                ratio = (y - last_y) / (last_y - prev_y)
                pred_left += (last_left - prev_left) * ratio
                pred_right += (last_right - prev_right) * ratio
            margin = w * cfg.tracking_margin
            pairs = [(a, b) for a, b in pairs
                     if abs(a[0] - pred_left) <= margin and abs(b[0] - pred_right) <= margin]
            if not pairs:
                gap += 1
                if gap > cfg.max_gap_rows:
                    break
                continue
            left, right = min(pairs, key=lambda p: abs(p[0][0] - pred_left) + abs(p[1][0] - pred_right))
        gap = 0
        history.append((y, left[0], right[0]))
        samples.append((y, left[0], right[0], (left[0] + right[0]) / 2))
        lane_mask[y, left[1]:left[2]] = 255
        lane_mask[y, right[1]:right[2]] = 255

    observations = np.asarray(samples, dtype=float).reshape(-1, 4)
    coverage = len(samples) / len(rows)
    valid = False
    error = normalized = reference = None
    status = "insufficient_lane_evidence"
    if len(samples) >= 3:
        span = (observations[:, 0].max() - observations[:, 0].min()) / (h - 1)
        target = cfg.reference_y * (h - 1)
        idx = int(np.argmin(abs(observations[:, 0] - target)))
        close_reference = abs(observations[idx, 0] - target) <= cfg.sample_step * (cfg.max_gap_rows + 1)
        if coverage >= cfg.min_coverage and span >= cfg.min_vertical_span and close_reference:
            valid = True
            reference, left, right, center = observations[idx]
            error = float(center - image_center)
            normalized = float(error / ((right - left) / 2))
            reference = float(reference)
            status = "ok"
    return LaneResult(gray, mask, lane_mask, observations, valid, status, coverage,
                      error, normalized, reference)
