# Perception Baseline

## Three Implemented Functions

1. Convert an unsigned 8-bit OpenCV BGR image to grayscale while preserving the original color image.
2. Blur and threshold a lower image region, then track pairs of narrow white runs upward from the bottom. Pair spacing and continuity reject some unrelated markings. Broad horizontal stripes are skipped, with a bounded gap for reacquisition.
3. Compute the midpoint of every observed border pair and a lateral error near a configurable reference row.

This is a scanline baseline for local forward-facing road images. It does not interpret the full overhead concept map, detect crosswalk semantics, classify signs, or command a vehicle. A crossing fixture checks interference with lane extraction only.

## Output Contract

`detect_lane(frame, config)` returns `LaneResult`. Coordinates use pixels with x increasing right and y increasing down. Samples contain `y`, `left_x`, `right_x`, and `center_x`. The center is `(left_x + right_x) / 2` at the same row.

`lateral_error_px = center_x - (image_width - 1) / 2`; positive means the road center lies right of the image center. Normalized error divides this by half the measured lane width at the reference row. These are image-space quantities, not meters or steering angles. `reference_y` reports the actual observed row selected near the requested fraction of image height.

`coverage` is the fraction of sampled rows with paired observations, not a probability. Validity requires enough support, vertical span, and an observation near the reference row. Invalid results set both errors and the reference row to JSON `null`. Partial samples remain available for diagnostics; consumers must check `valid` before using them. The detector does not infer a missing border or fill gaps with invented samples.

## Configuration

Defaults are in [perception.json](../configs/perception.json). Fractional x distances use image width; fractional y positions use image height minus one.

| Setting | Meaning |
| --- | --- |
| `white_threshold` | Grayscale cutoff, 0–255, after blur |
| `roi_top`, `roi_bottom` | Vertical region fractions |
| `sample_step` | Vertical distance between scanlines, pixels |
| `max_marking_width` | Maximum bright-run width / image width |
| `min_lane_width`, `max_lane_width` | Allowed distance between border centers / image width |
| `tracking_margin` | Allowed displacement from predicted border x / image width |
| `max_gap_rows` | Maximum consecutive missing sampled rows; also bounds initial search |
| `min_coverage` | Minimum fraction of paired scanlines |
| `min_vertical_span` | Minimum observed vertical span / image height minus one |
| `reference_y` | Requested error-measurement row fraction |

## Reproduce and Inspect

```bash
python -m robot_car.perception.demo --fixture crossing --config configs/perception.json --output runs/crossing
python -m robot_car.perception.demo --fixture missing --output runs/missing
python -m pytest
```

Inspect `overlay.png` and `result.json` together. `white-mask.png` contains all threshold candidates in the region; `lane-mask.png` contains accepted border pixels on sampled rows only. Rendering never feeds overlays back into perception. A completed demo exits zero even when detection is invalid, so check the JSON status; unreadable inputs or invalid configuration exit with an argument error.

Tests use independently constructed road geometry for measured-coordinate assertions. They cover offsets, curves, resolutions, crossing interference, moderate noise and dimming, absent borders, blank/white/stripe-only frames, invalid inputs, and CLI artifacts. These are controlled synthetic checks, not real-camera accuracy measurements.

Validation on September 15, 2026: **24 tests passed** on Windows with Python 3.12, OpenCV 4.11.0, NumPy 2.2.6, and pytest 8.4.2. The checked-in crossing example reports 88.1% scanline support and approximately +1.8 pixels of lateral error. Support is not an accuracy score. Regenerate the example with `--fixture crossing --output docs/examples`.

## Known Limits

The road should enclose the image center near the bottom, with two visible white borders, sufficient contrast, and moderate curvature. Fixed thresholding needs tuning under lighting changes. Sharp turns, intersections, long occlusions, shadows, broken markings, or other parallel white structures can fail or produce a false lane. The current geometry checks do not prove that a pair is a road. There is no temporal tracking, camera calibration, perspective correction, or dynamic vehicle model yet.
