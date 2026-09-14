# Vision-Guided Robot Car

A reconstruction of a robot car project I built in secondary school, focusing on visual line following, PID steering, and traffic-sign recognition.

**Status:** Repository initialized. The new implementation, tests, and demonstrations are not yet available.

## Background

The original project used existing libraries to implement line following, PID control, and traffic-sign recognition on a physical robot car. The original source code and hardware materials are no longer available.

This repository will contain a new implementation based on that experience. It is not an archive of the original project. Features and results from the reconstruction will be documented as they are implemented and tested.

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
- [ ] Select reusable libraries and appropriately licensed input materials.
- [ ] Build a reproducible line-following perception demo.
- [ ] Implement and test the PID controller.
- [ ] Add traffic-sign recognition and a behavior state machine.
- [ ] Integrate a simple vehicle simulation and evaluate tracking behavior.
- [ ] Publish setup instructions, a demonstration, and measured results.

## Attribution

External libraries, reused code, and datasets will be credited with their sources and applicable licenses when added. Newly implemented components will be distinguished from reused components.
