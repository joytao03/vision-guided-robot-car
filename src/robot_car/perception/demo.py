"""Command-line image demo: grayscale, white borders, and center estimates."""

import argparse
import json
from pathlib import Path

import cv2

from robot_car.perception.lane import LaneConfig, detect_lane
from robot_car.simulation.fixtures import road_fixture
from robot_car.visualization.lane import draw_lane_overlay


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--image", type=Path, help="Local forward-facing BGR-compatible image")
    inputs.add_argument("--fixture", choices=["straight", "curve", "crossing", "missing"], default="curve")
    parser.add_argument("--output", type=Path, default=Path("runs/perception"))
    parser.add_argument("--config", type=Path, help="JSON object containing LaneConfig settings")
    args = parser.parse_args(argv)
    try:
        config = LaneConfig(**json.loads(args.config.read_text(encoding="utf-8"))) if args.config else LaneConfig()
        if args.image:
            frame = cv2.imread(str(args.image), cv2.IMREAD_COLOR)
            if frame is None:
                parser.error(f"Cannot read image: {args.image}")
        else:
            frame = road_fixture(args.fixture)
        result = detect_lane(frame, config)
        args.output.mkdir(parents=True, exist_ok=True)
        for name, image in {"input.png": frame, "grayscale.png": result.grayscale,
                            "white-mask.png": result.white_mask, "lane-mask.png": result.lane_mask,
                            "overlay.png": draw_lane_overlay(frame, result)}.items():
            if not cv2.imwrite(str(args.output / name), image):
                raise OSError(f"Could not write {name}")
        (args.output / "result.json").write_text(json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (ValueError, TypeError, OSError) as exc:
        parser.error(str(exc))
    print(f"{result.status}: support={result.coverage:.1%}; output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
