"""Generate deterministic local-road images, not a vehicle simulator.

These programmatic test fixtures are separate from the approved concept art.
Only the rendered pixels are passed to perception.
"""

import cv2
import numpy as np


def road_fixture(kind: str = "curve", width: int = 640, height: int = 480) -> np.ndarray:
    if kind not in {"straight", "curve", "crossing", "missing"}:
        raise ValueError("Unknown fixture")
    image = np.full((height, width, 3), (65, 125, 55), np.uint8)
    y = np.arange(height)
    t = y / (height - 1)
    bend = 0 if kind == "straight" else 0.13 * width * (1 - t) ** 2
    center = width / 2 + bend
    half_width = width * (0.07 + 0.33 * t)
    left = np.column_stack((np.broadcast_to(center - half_width, y.shape), y)).astype(np.int32)
    right = np.column_stack((np.broadcast_to(center + half_width, y.shape), y)).astype(np.int32)
    cv2.fillPoly(image, [np.concatenate((left, right[::-1]))], (115, 115, 115))
    if kind == "crossing":
        for fraction in (0.57, 0.64, 0.71):
            yy = int(fraction * height)
            cv2.rectangle(image, (int(left[yy, 0]), yy), (int(right[yy, 0]), yy + 10), (245, 245, 245), -1)
    cv2.polylines(image, [left], False, (245, 245, 245), 7)
    if kind != "missing":
        cv2.polylines(image, [right], False, (245, 245, 245), 7)
    return image
