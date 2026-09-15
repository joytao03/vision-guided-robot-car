# Visualization

**Implemented:** `lane.py` draws observed borders, midpoints, validity, support coverage, and lateral error on a copy of the input image. Candidate objects, behavior state, target speed, and control output remain planned.

Consume outputs from other layers without changing decisions or vehicle state. Keep overlays separate from detector input so annotations cannot influence recognition. Support saved diagnostic images as well as a future live display.
