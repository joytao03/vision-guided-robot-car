# Control

**Implemented:** `SteeringPID`, `PIDConfig`, and `ControlCommand` in `pid.py`.

Converts normalized lane error into steering in [-1, 1], positive right. Explicit time steps are in seconds. Output limiting, bounded integration with conditional anti-windup, stop/reset handling, and a direct `LaneResult` adapter are tested. Initial gains are not tuned for a vehicle.

See the [control guide](../../../docs/control.md) for configuration, an executable example, and the integration contract. The future vehicle adapter must enforce stop requests and convert normalized steering into its actuator units. Speed regulation and closed-loop driving remain planned.

Control does not classify signs, start crossing timers, or access simulator ground truth.
