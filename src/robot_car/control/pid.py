"""Discrete steering PID with explicit seconds and a stop/reset contract."""

from dataclasses import dataclass
import math
from typing import Protocol


class LaneObservation(Protocol):
    valid: bool
    lateral_error_normalized: float | None


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


@dataclass(frozen=True)
class PIDConfig:
    # Untuned starting values: P only. Tune with fixed low speed in simulation.
    kp: float = 0.5
    ki: float = 0.0
    kd: float = 0.0
    steering_limit: float = 1.0
    integral_limit: float = 1.0  # Integral of normalized error, in seconds.
    min_dt: float = 0.001
    max_dt: float = 0.2

    def __post_init__(self):
        for name in ("kp", "ki", "kd", "steering_limit", "integral_limit", "min_dt", "max_dt"):
            if not _finite(getattr(self, name)):
                raise ValueError(f"{name} must be a finite number")
        if min(self.kp, self.ki, self.kd, self.integral_limit) < 0:
            raise ValueError("Gains and integral_limit must be nonnegative")
        if not 0 < self.steering_limit <= 1:
            raise ValueError("steering_limit must be in (0, 1]")
        if not 0 < self.min_dt <= self.max_dt:
            raise ValueError("Require 0 < min_dt <= max_dt, in seconds")


@dataclass(frozen=True)
class ControlCommand:
    steering: float  # [-1, 1]; positive requests a right turn.
    stop_requested: bool
    status: str
    p_term: float = 0.0
    i_term: float = 0.0
    d_term: float = 0.0
    saturated: bool = False


class SteeringPID:
    """Consumes normalized lane error; produces no physical actuator commands.

    Call once per fresh observation with elapsed seconds. The caller must stop
    the vehicle when stop_requested is true, and must provide its own watchdog
    if observations stop arriving. No internal clock or simulator dependency.
    """

    def __init__(self, config: PIDConfig | None = None):
        self.config = config or PIDConfig()
        self.reset()

    def reset(self):
        self._integral = 0.0
        self._previous_error = None

    def _stop(self, status):
        self.reset()
        return ControlCommand(0.0, True, status)

    def update(self, error: float | None, dt: float, *, lane_valid: bool = True,
               stop_requested: bool = False) -> ControlCommand:
        """Apply P + I + D; invalid observations/timing reset all history.

        Integration uses the current error times dt. The derivative is zero
        on the first valid update after construction/reset. Integral state is
        bounded and frozen when its update would push further into saturation.
        """
        cfg = self.config
        if stop_requested:
            return self._stop("external_stop")
        if not lane_valid:
            return self._stop("lane_unavailable")
        if not _finite(error):
            return self._stop("invalid_error")
        if not _finite(dt) or not cfg.min_dt <= dt <= cfg.max_dt:
            return self._stop("invalid_dt")

        derivative = 0.0 if self._previous_error is None else (error - self._previous_error) / dt
        p = cfg.kp * error
        d = cfg.kd * derivative if cfg.kd else 0.0
        candidate = max(-cfg.integral_limit, min(cfg.integral_limit, self._integral + error * dt)) if cfg.ki else 0.0
        proposed = p + cfg.ki * candidate + d
        increment = cfg.ki * (candidate - self._integral)
        if (proposed > cfg.steering_limit and increment > 0) or (proposed < -cfg.steering_limit and increment < 0):
            candidate = self._integral
        i = cfg.ki * candidate
        raw = p + i + d
        if not all(math.isfinite(v) for v in (p, i, d, raw)):
            return self._stop("numeric_overflow")
        self._integral = candidate
        self._previous_error = error
        steering = max(-cfg.steering_limit, min(cfg.steering_limit, raw))
        return ControlCommand(steering, False, "ok", p, i, d, abs(raw) > cfg.steering_limit)

    def update_lane(self, lane: LaneObservation, dt: float, *, stop_requested: bool = False) -> ControlCommand:
        """Accept LaneResult directly without importing image-processing code."""
        return self.update(lane.lateral_error_normalized, dt, lane_valid=lane.valid,
                           stop_requested=stop_requested)
