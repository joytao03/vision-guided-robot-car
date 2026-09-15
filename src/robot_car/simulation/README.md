# Simulation

**Implemented:** `fixtures.py` renders static local road images for the perception demo. A dynamic simulator remains planned and will own road geometry, vehicle state, traffic-light timing, signs, and camera rendering.

The initial course will have gray road, continuous white edge lines, green surroundings, a zebra crossing, traffic lights, and a school-warning sign. The approved [concept image](../../../assets/concepts/track-concept-v1.png) is a visual reference, not a calibrated map or working simulator.

Render a local vehicle-facing observation for perception. World coordinates and object labels may be used by evaluation tools, but must not be supplied to the driving pipeline as detections.

Use deterministic scenarios, simulation time, and documented coordinates. Add lighting, blur, and viewpoint variation after the clean baseline works. Video replay can test perception, but only simulation feedback or a physical vehicle can validate closed-loop control.
