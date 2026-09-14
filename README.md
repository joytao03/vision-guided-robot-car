# Vision-Guided Robot Car

A reconstruction of a robot car project I built in secondary school, focusing on visual line following, PID steering, and traffic-sign recognition.

**Status:** Project layers and a course concept are in place. Current focus: visual lane perception. Functional code, tests, and driving demonstrations are not yet available.

## Background

The original project used existing libraries to implement line following, PID control, and traffic-sign recognition on a physical robot car. The original source code and hardware materials are no longer available.

This repository will contain a new implementation based on that experience. It is not an archive of the original project. Features and results from the reconstruction will be documented as they are implemented and tested.

## Course Concept

![Gray road with white boundaries, grass, a crossing, a traffic light, and a school sign](assets/concepts/track-concept-v1.png)

AI-generated planning reference, not a calibrated map or a photograph of the original project. See [asset notes and generation prompt](assets/concepts/README.md). The simulation will generate its own local vehicle-camera views.

## Repository Structure

```text
assets/concepts/           Approved course image and provenance
configs/                   Future detector, control, and scenario settings
docs/architecture.md       Data flow, boundaries, and development order
src/robot_car/
    perception/            Lane, crossing, light, and sign detection
    behavior/              Driving states, priorities, and timers
    control/               PID steering and speed commands
    simulation/            Vehicle model, scene, and camera rendering
    visualization/         Overlays and diagnostics
tests/                     Validation plan; tests follow implementation
```

Each layer currently contains a README defining its responsibility. Start with [perception](src/robot_car/perception/README.md); see the [architecture guide](docs/architecture.md) for interfaces and staged development.

## Planned Scope

The first version will run without physical hardware:

- **Perception:** Use OpenCV to extract a track or line from video frames and estimate lateral deviation.
- **Control:** Implement a PID controller that converts deviation into a steering command.
- **Decision logic:** Recognize a small set of traffic signs or markers and use a state machine to trigger corresponding behavior.
- **Visualization:** Show detection overlays, current state, error, and steering output.
- **Simulation:** Connect the controller to a simple vehicle simulation to evaluate closed-loop behavior.

Video processing alone will demonstrate perception and command generation; closed-loop tracking claims will require simulation or physical-vehicle testing.

## Planned Workflow

```text
Camera frame / recorded video / simulated view
                    |
         Line and sign detection
                    |
         Deviation + behavior state
                    |
               PID controller
                    |
             Steering command
                    |
        Vehicle simulation (planned)
                    |
          Updated simulated view
```

## Roadmap

- [x] Initialize the repository and document the reconstruction scope.
- [x] Add the course concept and define implementation layers.
- [ ] Select reusable libraries and appropriately licensed input materials.
- [ ] Build a reproducible line-following perception demo.
- [ ] Implement and test the PID controller.
- [ ] Integrate a simple vehicle simulation and evaluate tracking behavior.
- [ ] Add crossing, traffic-light, and sign recognition, then a behavior state machine.
- [ ] Publish setup instructions, a demonstration, and measured results.

## Attribution

External libraries, reused code, and datasets will be credited with their sources and applicable licenses when added. Newly implemented components will be distinguished from reused components.
