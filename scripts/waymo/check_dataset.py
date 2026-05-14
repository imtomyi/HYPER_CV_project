#!/usr/bin/env python3
"""Inspect downloaded Waymo Perception v1.4.3 TFRecord files."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from waymo_perception_io import (
    DEFAULT_WAYMO_PERCEPTION_ROOT,
    camera_name,
    discover_tfrecords,
    iter_frames,
    label_type_name,
    require_waymo,
    split_input_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Waymo Perception TFRecords.")
    parser.add_argument("--root", type=Path, default=DEFAULT_WAYMO_PERCEPTION_ROOT)
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["training", "validation"],
        help="Subfolders under --root to inspect.",
    )
    parser.add_argument("--max-frames", type=int, default=5)
    return parser.parse_args()


def map_feature_type(feature) -> str:
    for name in (
        "lane",
        "road_line",
        "road_edge",
        "crosswalk",
        "speed_bump",
        "stop_sign",
        "driveway",
    ):
        try:
            if feature.HasField(name):
                return name
        except ValueError:
            continue
    return "unknown"


def main() -> int:
    args = parse_args()
    _, dataset_pb2, label_pb2 = require_waymo()
    input_paths = split_input_paths(args.root, args.splits)
    files = discover_tfrecords(input_paths)
    if not files:
        print(f"No TFRecord files found under: {args.root}")
        return 2

    print("files:")
    for file_path in files[:10]:
        print(f"  {file_path}")
    if len(files) > 10:
        print(f"  ... {len(files) - 10} more")

    frame_total = 0
    image_counts: Counter[str] = Counter()
    camera_label_counts: Counter[str] = Counter()
    laser_label_counts: Counter[str] = Counter()
    map_counts: Counter[str] = Counter()

    for _, _, frame in iter_frames(files, max_frames=args.max_frames):
        frame_total += 1
        for image in frame.images:
            image_counts[camera_name(dataset_pb2, image.name)] += 1
        for camera_labels in frame.camera_labels:
            for label in camera_labels.labels:
                camera_label_counts[label_type_name(label_pb2, label.type)] += 1
        for label in frame.laser_labels:
            laser_label_counts[label_type_name(label_pb2, label.type)] += 1
        for feature in frame.map_features:
            map_counts[map_feature_type(feature)] += 1

    print(f"\nframes inspected: {frame_total}")
    print(f"camera images: {dict(image_counts)}")
    print(f"camera labels: {dict(camera_label_counts)}")
    print(f"lidar labels: {dict(laser_label_counts)}")
    print(f"map features: {dict(map_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
