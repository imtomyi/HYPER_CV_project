#!/usr/bin/env python3
"""Convert Waymo 2D camera vehicle labels to a YOLO dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from waymo_perception_io import (
    DEFAULT_WAYMO_PERCEPTION_ROOT,
    camera_name,
    decode_jpeg_size,
    discover_tfrecords,
    frame_stem,
    iter_frames,
    label_type_value,
    labels_for_camera,
    require_waymo,
    selected_camera_names,
    split_input_paths,
    yolo_box_from_waymo_label,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a YOLO vehicle dataset from Waymo Perception camera labels."
    )
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
        default=Path("data/waymo_vehicle_yolo"),
    )
    parser.add_argument(
        "--keep-empty",
        action="store_true",
        help="Also save images with no vehicle label.",
    )
    return parser.parse_args()


def write_dataset_yaml(output_dir: Path) -> None:
    yaml_text = f"""path: {output_dir.resolve()}

train: images/training
val: images/validation

names:
  0: vehicle
"""
    (output_dir / "data.yaml").write_text(yaml_text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    _, dataset_pb2, label_pb2 = require_waymo()
    selected = selected_camera_names(dataset_pb2, args.cameras)
    vehicle_type = label_type_value(label_pb2, "TYPE_VEHICLE", 1)
    files = discover_tfrecords(split_input_paths(args.root, args.splits))
    if not files:
        print(f"No TFRecord files found under: {args.root}")
        return 2

    saved_images = 0
    saved_boxes = 0
    for file_path, frame_index, frame in iter_frames(files, max_frames=args.max_frames):
        split = file_path.parent.name
        base = frame_stem(file_path, frame_index)
        for image in frame.images:
            cam_name = camera_name(dataset_pb2, image.name)
            if selected is not None and cam_name not in selected:
                continue

            width, height = decode_jpeg_size(image.image)
            yolo_lines: list[str] = []
            for label in labels_for_camera(frame, image.name):
                if label.type != vehicle_type:
                    continue
                line = yolo_box_from_waymo_label(label, width, height)
                if line is not None:
                    yolo_lines.append(line)

            if not yolo_lines and not args.keep_empty:
                continue

            stem = f"{base}_{cam_name}"
            image_out = args.output_dir / "images" / split / f"{stem}.jpg"
            label_out = args.output_dir / "labels" / split / f"{stem}.txt"
            image_out.parent.mkdir(parents=True, exist_ok=True)
            label_out.parent.mkdir(parents=True, exist_ok=True)
            image_out.write_bytes(image.image)
            label_out.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")
            saved_images += 1
            saved_boxes += len(yolo_lines)

    write_dataset_yaml(args.output_dir)
    print(f"saved images: {saved_images}")
    print(f"saved vehicle boxes: {saved_boxes}")
    print(f"dataset yaml: {args.output_dir / 'data.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
