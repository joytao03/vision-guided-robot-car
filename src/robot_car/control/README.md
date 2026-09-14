# Control

**Planned.** Converts the lane estimate and behavior's target speed into vehicle commands.

Implement steering PID with an explicit time step, documented error sign and units, output limits, and a deliberate reset policy when stopping or losing the lane. Speed commands must respect the behavior layer's stop and slow states.

Test zero error, error sign, changing time steps, saturation, and recovery. PID output alone is not evidence of successful tracking; that requires a closed-loop simulation or physical test.

Control must not classify signs, start crossing timers, or access simulator ground truth.
