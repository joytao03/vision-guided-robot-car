# Architecture and Development Stages

## Status

Repository structure and a visual course concept are available. Functional perception, control, behavior, simulation, and visualization are not implemented yet.

## Data Flow

```mermaid
flowchart LR
    S[Simulation or camera source] -->|Color frame and timestamp| P[Perception]
    P -->|Objects and confidence| B[Behavior]
    P -->|Lane estimate| C[Control]
    B -->|State and target speed| C
    C -->|Vehicle command| S
    P --> V[Visualization]
    B --> V
    C --> V
```

An application runner will coordinate the layers and load configuration. Shared data contracts will be introduced when the first runnable slice requires them.

## Planned Contracts

| Data | Producer | Consumers | Intended contents |
| --- | --- | --- | --- |
| Frame | Camera source / simulation | Perception, visualization | Color image, timestamp, frame identifier |
| Lane estimate | Perception | Control, visualization | Left/right boundaries, center estimate, error, confidence |
| Object observations | Perception | Behavior, visualization | Type or unknown, image location, signal/sign class, confidence |
| Driving intent | Behavior | Control, visualization | State, target speed, active stop/slow reasons |
| Vehicle command | Control | Simulation or future hardware adapter | Steering and speed command with documented units |

Missing detections must be explicit. Establish one coordinate convention, timestamp source, and error-sign convention before connecting modules. Behavior timers use the same clock as observations.

## Boundaries

- Perception sees camera observations, not the simulator's object list or true lane coordinates.
- Keep the color frame for traffic lights and signs; derive grayscale separately for white-line extraction.
- Behavior handles temporal decisions and restriction priority; control handles numeric steering and speed commands.
- Visualization is an observer. Detection input never includes its overlays.
- Ground truth is for evaluation only.

## Development Order

1. **Visual baseline:** extract the two white road boundaries from a simple local road image and save an overlay. Handle curves and crossing interference.
2. **Steering control:** define lane error, implement PID, and validate its response with controlled inputs.
3. **Closed-loop simulation:** update the vehicle from commands and generate the next camera view. Measure tracking behavior.
4. **Scene recognition:** add crossing, traffic-light, and simple sign detectors, including unknown states.
5. **Behavior integration:** add stopping, timed waiting, light handling, and school-zone slowing.
6. **Robustness and demonstration:** vary conditions, record results, and publish reproducible run instructions.

The first deliverable is a perception result, not an autonomous-driving claim. Update the root roadmap only after each stage has been implemented and checked.
