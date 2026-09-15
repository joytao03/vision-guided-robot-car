# Steering PID

This module computes steering from normalized image-space lane error. It has no simulator dependency and does not move a vehicle by itself.

## Initial Configuration

Load [control.json](../configs/control.json) into `PIDConfig`. Initial gains are **kp=0.5, ki=0, kd=0**: P-only starting values, not validated driving parameters. Keep a fixed low test speed when tuning in the future simulator. Tune P first, then D if needed, and enable I only if persistent bias warrants it.

| Setting | Meaning |
| --- | --- |
| `kp` | Steering per unit normalized error |
| `ki` | Steering per normalized error-second |
| `kd` | Steering-seconds per normalized error |
| `steering_limit` | Symmetric output limit, at most 1 |
| `integral_limit` | Symmetric bound on accumulated error-seconds |
| `min_dt`, `max_dt` | Accepted elapsed seconds, inclusive; defaults 0.001–0.2 |

Configuration is immutable. Construct a fresh controller to apply new settings. Keep the same instance across frames during a run so it retains history.

## Calculation and Sign

The input is `LaneResult.lateral_error_normalized`: positive means the road center lies right of the image center. The output uses positive for a requested right turn. A future vehicle adapter must convert this convention to its steering angle or wheel velocities; [-1, 1] is not radians.

For each fresh observation, P is `kp * error`, I uses the bounded sum of `error * dt`, and D is `kd * (error - previous_error) / dt`. The first derivative after a reset is zero. Output is clipped to the configured steering limit. An integral increment is rejected if it would push the proposed output further into saturation; increments that unwind the integral are allowed. When `ki=0`, no integral is accumulated.

Derivative filtering and steering rate limiting are not implemented. Noisy camera errors can amplify D, so leave `kd=0` until its behavior can be measured.

## Perception Integration Example

After the root README installation steps, run this Python code from the repository root:

```python
import json
from pathlib import Path

from robot_car.control import PIDConfig, SteeringPID
from robot_car.perception import detect_lane
from robot_car.simulation.fixtures import road_fixture

config = PIDConfig(**json.loads(Path("configs/control.json").read_text()))
controller = SteeringPID(config)
lane = detect_lane(road_fixture("curve"))
command = controller.update_lane(lane, dt=1 / 30)
print(command)
```

This is one static integration step, not a simulation. In a real loop, pass a fresh frame each update and elapsed seconds from the simulation clock or a monotonic clock. The controller does not infer time or check frame timestamps. The caller must reject stale/duplicate observations and stop through a watchdog when frames cease to arrive.

## Stop and Recovery

`ControlCommand` contains steering, `stop_requested`, status, P/I/D contributions, and a saturation flag. Invalid/missing lane evidence, non-finite error, invalid elapsed time, numeric overflow, or an external stop request produce zero steering and `stop_requested=True`, resetting the integral and previous error. Stop results have zero diagnostic terms.

Use `controller.update_lane(lane, dt, stop_requested=True)` for a behavior-layer stop. Keep requesting it throughout the stop; this module has no stop latch or behavior timer. A subsequent valid update resumes automatically with fresh history. `reset()` also clears history explicitly.

**Zero steering does not brake a vehicle.** The future adapter must enforce `stop_requested` by applying its stop/brake command. A false stop request only permits the caller's chosen speed; this controller does not select or regulate speed.

## Validation

Run `python -m pytest`. On September 15, 2026, all **54 tests passed** (30 control, 24 perception), using the same Python 3.12/OpenCV 4.11 environment documented in the perception guide. Checks cover hand-computed PID terms, time-step scaling, both steering directions, saturation, bounded integration, anti-windup, reset/recovery, invalid inputs, and the actual perception-to-control adapter.

These tests establish the numeric/control contract. Stable driving, cornering, gains, and recovery on a moving vehicle remain unvalidated until closed-loop simulation is connected.
