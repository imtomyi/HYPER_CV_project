#!/usr/bin/env python3
"""Extract camera JPEGs from Waymo Perception v1 TFRecord files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from waymo_perception_io import (
    DEFAULT_WAYMO_PERCEPTION_ROOT,
    camera_name,
    discover_tfrecords,
    frame_stem,
    iter_frames,
    require_waymo,
    selected_camera_names,
    split_input_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Waymo camera images.")
    parser.add_argument("--root", type=Path, default=DEFAULT_WAYMO_PERCEPTION_ROOT)
    parser.add_argument("--splits", nargs="+", default=["training", "validation"])
    parser.add_argument(
        "--cameras",
        nargs="+",
        default=["FRONT"],
        help="Camera names to export, or ALL.",
    )
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/waymo_camera_frames"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, dataset_pb2, _ = require_waymo()
    selected = selected_camera_names(dataset_pb2, args.cameras)
    files = discover_tfrecords(split_input_paths(args.root, args.splits))
    if not files:
        print(f"No TFRecord files found under: {args.root}")
        return 2

    saved = 0
    for file_path, frame_index, frame in iter_frames(files, max_frames=args.max_frames):
        split = file_path.parent.name
        base = frame_stem(file_path, frame_index)
        for image in frame.images:
            name = camera_name(dataset_pb2, image.name)
            if selected is not None and name not in selected:
                continue
            output = args.output_dir / split / f"{base}_{name}.jpg"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(image.image)
            saved += 1
    print(f"saved camera images: {saved}")
    print(f"output: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
