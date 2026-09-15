"""Independent analytic images check geometry and explicit failure behavior."""

import json

import cv2
import numpy as np
import pytest

from robot_car.perception import LaneConfig, detect_lane, to_grayscale
from robot_car.perception.demo import main


def analytic_road(width=640, height=480, offset=0, curve=0, crossing=False, missing=False):
    # This test oracle does not call the demo fixture renderer.
    image = np.full((height, width, 3), 105, dtype=np.uint8)
    ys = np.arange(height)
    centers = (width - 1) / 2 + offset + curve * ((height - 1 - ys) / height) ** 2
    half_widths = width * (0.12 + 0.24 * ys / height)
    for y, center, half_width in zip(ys, centers, half_widths):
        for x in ([center - half_width] if missing else [center - half_width, center + half_width]):
            image[y, round(x) - 3:round(x) + 4] = 245
    if crossing:
        for y in (260, 300, 340):
            image[y:y+10, round(centers[y]-half_widths[y]):round(centers[y]+half_widths[y])+1] = 245
    return image, centers, half_widths


def test_grayscale_color_order_and_no_mutation():
    frame = np.zeros((40, 40, 3), np.uint8)
    frame[:] = (0, 0, 255)
    before = frame.copy()
    gray = to_grayscale(frame)
    assert np.all(gray == 76)  # Red in BGR, not blue.
    np.testing.assert_array_equal(frame, before)
    copied = to_grayscale(gray)
    copied[:] = 0
    assert gray[0, 0] == 76


@pytest.mark.parametrize("width,height,offset,curve,crossing", [
    (640, 480, 0, 0, False), (640, 480, 35, 0, False),
    (640, 480, -35, 0, False), (640, 480, 0, 110, False),
    (640, 480, 0, -110, True), (320, 240, 10, 35, False),
    (960, 720, -40, 140, False),
])
def test_measured_borders_and_centers(width, height, offset, curve, crossing):
    image, centers, half_widths = analytic_road(width, height, offset, curve, crossing)
    before = image.copy()
    result = detect_lane(image)
    assert result.valid
    rows = result.samples[:, 0].astype(int)
    np.testing.assert_allclose(result.samples[:, 1], centers[rows]-half_widths[rows], atol=1.5)
    np.testing.assert_allclose(result.samples[:, 2], centers[rows]+half_widths[rows], atol=1.5)
    np.testing.assert_allclose(result.samples[:, 3], centers[rows], atol=1)
    expected = centers[int(result.reference_y)] - (width - 1) / 2
    assert result.lateral_error_px == pytest.approx(expected, abs=1)
    np.testing.assert_array_equal(image, before)


@pytest.mark.parametrize("kind", ["missing", "blank", "white", "horizontal"])
def test_no_fabricated_lane(kind):
    image, _, _ = analytic_road(missing=True)
    if kind == "blank":
        image[:] = 100
    elif kind == "white":
        image[:] = 255
    elif kind == "horizontal":
        image[:] = 100
        for y in range(200, 460, 30):
            image[y:y+7, 100:540] = 255
    result = detect_lane(image)
    assert not result.valid
    assert result.lateral_error_px is None
    assert result.lateral_error_normalized is None


def test_noise_and_moderate_dimming():
    image, centers, _ = analytic_road(curve=80)
    noise = np.random.default_rng(43).normal(0, 2, image.shape)
    image = np.clip(image.astype(float)*0.88 + noise, 0, 255).astype(np.uint8)
    result = detect_lane(image)
    assert result.valid
    rows = result.samples[:, 0].astype(int)
    np.testing.assert_allclose(result.samples[:, 3], centers[rows], atol=1.5)


def test_config_controls_dark_scene_threshold():
    image, _, _ = analytic_road()
    image = (image * 0.65).astype(np.uint8)
    assert not detect_lane(image).valid
    assert detect_lane(image, LaneConfig(white_threshold=130)).valid


@pytest.mark.parametrize("image", [np.zeros((5, 5), np.uint8), np.zeros((40, 40), float), np.zeros((40, 40, 4), np.uint8)])
def test_reject_invalid_images(image):
    with pytest.raises(ValueError):
        detect_lane(image)


@pytest.mark.parametrize("settings", [{"sample_step": 0}, {"sample_step": 2.5}, {"roi_top": 0.98}, {"white_threshold": 300}, {"reference_y": 1}, {"tracking_margin": float("nan")}])
def test_reject_invalid_settings(settings):
    with pytest.raises(ValueError):
        LaneConfig(**settings)


def test_cli_roundtrip_and_missing_input(tmp_path):
    assert main(["--fixture", "crossing", "--output", str(tmp_path)]) == 0
    data = json.loads((tmp_path / "result.json").read_text())
    assert data["valid"]
    for name in ("input", "grayscale", "white-mask", "lane-mask", "overlay"):
        assert cv2.imread(str(tmp_path / f"{name}.png")) is not None
    with pytest.raises(SystemExit) as exc:
        main(["--image", str(tmp_path / "absent.png")])
    assert exc.value.code == 2
