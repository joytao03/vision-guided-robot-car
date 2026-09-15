"""Numeric PID expectations and perception-to-control integration."""

import json
from pathlib import Path

import pytest

from robot_car.control import PIDConfig, SteeringPID
from robot_car.perception import detect_lane
from robot_car.simulation.fixtures import road_fixture


@pytest.mark.parametrize("error, expected", [(0, 0), (0.4, 0.2), (-0.4, -0.2), (3, 1), (-3, -1)])
def test_default_direction_and_limit(error, expected):
    command = SteeringPID().update(error, 0.1)
    assert command.steering == pytest.approx(expected)
    assert not command.stop_requested
    assert command.saturated == (abs(error) > 2)


def test_pid_terms_use_elapsed_seconds():
    pid = SteeringPID(PIDConfig(kp=0.2, ki=0.3, kd=0.1))
    first = pid.update(0.2, 0.1)
    assert first.d_term == 0
    second = pid.update(0.3, 0.2)
    assert second.p_term == pytest.approx(0.06)
    assert second.i_term == pytest.approx(0.024)
    assert second.d_term == pytest.approx(0.05)
    assert second.steering == pytest.approx(0.134)


def test_integral_tracks_time_not_call_count_and_is_bounded():
    a = SteeringPID(PIDConfig(kp=0, ki=1, integral_limit=0.3))
    b = SteeringPID(a.config)
    for _ in range(10):
        x = a.update(0.2, 0.1)
    for _ in range(5):
        y = b.update(0.2, 0.2)
    assert x.i_term == pytest.approx(y.i_term)
    for _ in range(100):
        x = a.update(0.2, 0.1)
    assert x.i_term == pytest.approx(0.3)


@pytest.mark.parametrize("sign", [-1, 1])
def test_saturation_does_not_accumulate_integral(sign):
    pid = SteeringPID(PIDConfig(kp=1, ki=1))
    for _ in range(100):
        command = pid.update(sign * 2, 0.1)
    assert command.saturated
    assert command.i_term == 0
    recovered = pid.update(-sign * 0.1, 0.1)
    assert recovered.steering == pytest.approx(-sign * 0.11)


@pytest.mark.parametrize("kwargs, status", [
    ({"error": None}, "invalid_error"),
    ({"error": float("nan")}, "invalid_error"),
    ({"error": float("inf")}, "invalid_error"),
    ({"lane_valid": False}, "lane_unavailable"),
    ({"stop_requested": True}, "external_stop"),
    ({"dt": 0}, "invalid_dt"), ({"dt": -1}, "invalid_dt"),
    ({"dt": 0.5}, "invalid_dt"), ({"dt": float("nan")}, "invalid_dt"),
    ({"dt": 0.0001}, "invalid_dt"),
])
def test_stop_resets_history(kwargs, status):
    pid = SteeringPID(PIDConfig(ki=0.2, kd=0.1))
    pid.update(0.4, 0.1)
    arguments = {"error": 0.2, "dt": 0.1, **kwargs}
    stopped = pid.update(**arguments)
    assert stopped.stop_requested and stopped.steering == 0
    assert stopped.status == status
    # Equivalent to a fresh controller: no old integral or derivative kick.
    assert pid.update(-0.1, 0.1) == SteeringPID(pid.config).update(-0.1, 0.1)


def test_explicit_reset_and_overflow():
    pid = SteeringPID(PIDConfig(ki=0.1, kd=0.1))
    pid.update(0.3, 0.1)
    pid.reset()
    assert pid.update(0.2, 0.1) == SteeringPID(pid.config).update(0.2, 0.1)
    assert SteeringPID(PIDConfig(kp=1e308)).update(1e308, 0.1).stop_requested


@pytest.mark.parametrize("config", [{"kp": -1}, {"ki": float("inf")}, {"kd": "1"},
    {"kp": True}, {"steering_limit": 2}, {"steering_limit": 0}, {"integral_limit": -1},
    {"min_dt": 0}, {"max_dt": 0.0001}])
def test_invalid_config(config):
    with pytest.raises(ValueError):
        PIDConfig(**config)


def test_checked_in_config_and_perception_adapter():
    config_path = Path(__file__).parents[1] / "configs" / "control.json"
    config = PIDConfig(**json.loads(config_path.read_text()))
    assert config == PIDConfig()
    pid = SteeringPID(config)
    lane = detect_lane(road_fixture("curve"))
    command = pid.update_lane(lane, 1 / 30)
    assert lane.valid and not command.stop_requested
    assert command.steering == pytest.approx(config.kp * lane.lateral_error_normalized)
    missing = detect_lane(road_fixture("missing"))
    assert pid.update_lane(missing, 1 / 30).stop_requested
    assert pid.update_lane(lane, 1 / 30, stop_requested=True).status == "external_stop"
