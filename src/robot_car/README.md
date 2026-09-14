# Application Layers

This directory reserves the implementation boundaries for the rebuild. The layer directories currently contain design notes, not working algorithms.

| Layer | Responsibility |
| --- | --- |
| `perception/` | Extract lane geometry, crossings, lights, and signs from images. |
| `behavior/` | Decide when to follow, slow down, stop, wait, or resume. |
| `control/` | Turn lane error and a speed target into steering and motion commands. |
| `simulation/` | Update the vehicle and environment, then render camera observations. |
| `visualization/` | Display observations, detections, decisions, and diagnostics. |

See [architecture](../../docs/architecture.md) for the data flow and dependency rules.
