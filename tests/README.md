# Validation Plan

Tests will be added alongside the implementation, not as empty passing placeholders.

1. **Perception:** straight and curved roads, crossing interference, absent boundaries, color changes, and unknown signs.
2. **Control:** error sign, time-step handling, output limits, and reset behavior.
3. **Behavior:** crossing triggers once, timers advance without blocking, red light overrides release, and slow-zone exit is explicit.
4. **Integration:** deterministic closed-loop runs measuring tracking error and checking stop/slow behavior.

Use independently specified expected results and keep simulator truth available only to evaluation. The concept image is not a labeled benchmark.
