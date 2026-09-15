# Validation Plan

Run `python -m pytest` from the repository root after installing the test extra. `test_lane.py` validates independently constructed lane geometry, offsets, curves, crossing interference, resolutions, noise, illumination thresholds, missing evidence, input validation, and command-line artifacts. Object recognition and the stages below remain planned.

1. **Perception:** straight and curved roads, crossing interference, absent boundaries, color changes, and unknown signs.
2. **Control:** error sign, time-step handling, output limits, and reset behavior.
3. **Behavior:** crossing triggers once, timers advance without blocking, red light overrides release, and slow-zone exit is explicit.
4. **Integration:** deterministic closed-loop runs measuring tracking error and checking stop/slow behavior.

Use independently specified expected results and keep simulator truth available only to evaluation. The concept image is not a labeled benchmark.

`test_pid.py` covers numeric P/I/D terms, variable time steps, direction, output and integral limits, anti-windup, stops and recovery, invalid configuration, overflow, and the perception adapter. The combined suite has 54 passing tests; this does not establish closed-loop driving performance.
