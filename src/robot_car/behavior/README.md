# Behavior

**Planned.** Converts perception results into a driving state and target speed.

Initial states: follow, slow, approach stop, wait at crossing, wait for light, and cautious stop when essential observations are missing.

- Confirm detections across frames instead of reacting to every isolated candidate.
- Stop before a crossing, wait for a configurable duration, and avoid retriggering the same crossing until it has been passed.
- Wait at a red light and require a confirmed green signal before release. Define a conservative yellow-light policy for this simulated course.
- Enter a school slow zone and leave it using an explicit exit condition, such as traveled distance or an end marker.
- Combine active restrictions: finishing a crossing timer does not override a red light, and a stop condition overrides a slow-zone speed target.

Use simulation timestamps and state timers rather than blocking sleeps. This layer selects intent; it does not process raw pixels or implement PID arithmetic.
