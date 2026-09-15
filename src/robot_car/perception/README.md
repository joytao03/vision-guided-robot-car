# Perception

**Implemented:** grayscale conversion, paired white-border tracking, center estimation, and a command-line image demo. See the [perception guide](../../../docs/perception.md) for the actual input/output contract and limitations. Object detectors below remain planned.

Input: the vehicle's local camera image and a timestamp. Preserve the original color image; grayscale is a derived image for lane processing.

Planned components:

- Lane detection: grayscale conversion, white-marking extraction, left/right boundary selection, and center estimation at several look-ahead positions.
- Crossing detection: look for repeated transverse white stripes inside the road region; exclude these from lane-boundary candidates.
- Traffic-light detection: combine circular candidates, color information, and housing or lamp-group layout.
- Sign recognition: detect a candidate sign and compare its interior against a small set of known patterns. Circular custom signs are the initial scope.

Outputs: lane estimates and detected objects with image locations, confidence, and explicit unknown or missing states. A Hough circle is only a shape candidate, not a semantic label.

This layer must not set driving behavior, apply motor commands, or read hidden simulator object positions.

First milestone: identify both road edges in a local road view and export a diagnostic overlay. Test straight sections, curves, crossing interference, and missing boundaries before adding other detectors.
