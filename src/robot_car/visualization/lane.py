"""Render measured lane points without feeding overlays back to perception."""

import cv2
import numpy as np

from robot_car.perception.lane import LaneResult


def draw_lane_overlay(frame: np.ndarray, result: LaneResult) -> np.ndarray:
    image = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) if frame.ndim == 2 else frame.copy()
    h, w = image.shape[:2]
    cv2.line(image, ((w - 1) // 2, 0), ((w - 1) // 2, h - 1), (140, 140, 140), 1)
    for y, left, right, center in result.samples:
        for x, color in ((left, (255, 180, 0)), (right, (0, 180, 255)), (center, (255, 0, 255))):
            cv2.circle(image, (round(x), round(y)), 2, color, -1)
    label = f"{result.status} | support {result.coverage:.0%}"
    if result.valid:
        label += f" | error {result.lateral_error_px:+.1f}px"
    cv2.rectangle(image, (0, 0), (w - 1, 53), (25, 25, 25), -1)
    cv2.putText(image, label, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, "Left: cyan | Right: orange | Center: magenta", (8, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (230, 230, 230), 1, cv2.LINE_AA)
    return image
