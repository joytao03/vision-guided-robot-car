# Configuration

Future configuration files will hold perception thresholds, PID settings, behavior timing, and scenario parameters. Keep these separate from algorithm code.

`perception.json` contains baseline settings for the included synthetic fixtures. Units and limitations are documented in the [perception guide](../docs/perception.md). These settings are not calibrated for a physical camera.

`control.json` holds untuned PID gains and control limits. Load it into `PIDConfig`; see [units and integration](../docs/control.md). Parameters remain fixed for a controller instance; construct a fresh instance after changing them.
