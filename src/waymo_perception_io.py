#!/usr/bin/env python3
"""Shared helpers for Waymo Perception v1 TFRecord files."""

from __future__ import annotations

import glob
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any


DEFAULT_WAYMO_PERCEPTION_ROOT = Path("data/waymo_perception")
DEFAULT_SPLITS = ("training", "validation", "testing")


def require_waymo() -> tuple[Any, Any, Any]:
    if sys.version_info >= (3, 12):
        print(
            "Waymo/TensorFlow dependencies are not expected to work with "
            f"Python {sys.version_info.major}.{sys.version_info.minor}. "
            "Use Python 3.10 or 3.11, or run this part in Linux/Colab.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    try:
        import tensorflow as tf
        from waymo_open_dataset import dataset_pb2
        from waymo_open_dataset import label_pb2
    except ModuleNotFoundError:
        print(
            "Waymo Perception reading requires TensorFlow and the official "
            "Waymo package. Install with: "
            "python -m pip install -r requirements/waymo-perception.txt",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return tf, dataset_pb2, label_pb2


def discover_tfrecords(paths: Iterable[str | Path]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path_text = str(raw_path)
        path = Path(path_text)
        if any(char in path_text for char in "*?[]"):
            files.extend(sorted(Path(match) for match in glob.glob(path_text, recursive=True)))
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.tfrecord*")))
            files.extend(sorted(child for child in path.rglob("segment-*") if child.is_file()))
        elif path.is_file():
            files.append(path)

    seen: set[Path] = set()
    deduped: list[Path] = []
    for file_path in files:
        resolved = file_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(file_path)
    return deduped


def split_input_paths(root: Path, splits: Iterable[str]) -> list[Path]:
    return [root / split for split in splits]


def iter_frames(
    files: Iterable[str | Path],
    max_frames: int | None = None,
) -> Iterator[tuple[Path, int, Any]]:
    tf, dataset_pb2, _ = require_waymo()
    frame_count = 0
    for file_path in discover_tfrecords(files):
        dataset = tf.data.TFRecordDataset(str(file_path), compression_type="")
        for frame_index, raw in enumerate(dataset):
            frame = dataset_pb2.Frame()
            frame.ParseFromString(bytearray(raw.numpy()))
            yield file_path, frame_index, frame
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                return


def camera_name(dataset_pb2: Any, camera_id: int) -> str:
    try:
        return dataset_pb2.CameraName.Name.Name(camera_id)
    except Exception:
        return f"CAMERA_{camera_id}"


def label_type_name(label_pb2: Any, label_type: int) -> str:
    try:
        return label_pb2.Label.Type.Name(label_type)
    except Exception:
        return f"TYPE_{label_type}"


def label_type_value(label_pb2: Any, enum_name: str, fallback: int) -> int:
    return int(getattr(label_pb2.Label, enum_name, fallback))


def frame_stem(file_path: Path, frame_index: int) -> str:
    return f"{file_path.stem}_frame{frame_index:06d}"


def labels_for_camera(frame: Any, camera_id: int) -> list[Any]:
    for camera_labels in frame.camera_labels:
        if camera_labels.name == camera_id:
            return list(camera_labels.labels)
    return []


def selected_camera_names(dataset_pb2: Any, names: list[str]) -> set[str] | None:
    normalized = {name.upper() for name in names}
    if "ALL" in normalized:
        return None
    valid = set()
    for name in normalized:
        if name.startswith("FRONT") or name.startswith("SIDE") or name.startswith("REAR"):
            valid.add(name)
        else:
            valid.add(name.replace("CAMERA_", ""))
    return valid


def decode_jpeg_size(image_bytes: bytes) -> tuple[int, int]:
    tf, _, _ = require_waymo()
    image = tf.io.decode_jpeg(image_bytes, channels=3)
    height, width = [int(value) for value in tf.shape(image)[:2].numpy()]
    return width, height


def yolo_box_from_waymo_label(label: Any, image_width: int, image_height: int) -> str | None:
    box = label.box
    x_center = float(box.center_x)
    y_center = float(box.center_y)
    box_width = float(box.length)
    box_height = float(box.width)
    if box_width <= 0 or box_height <= 0:
        return None

    x_center = max(0.0, min(1.0, x_center / image_width))
    y_center = max(0.0, min(1.0, y_center / image_height))
    box_width = max(0.0, min(1.0, box_width / image_width))
    box_height = max(0.0, min(1.0, box_height / image_height))
    if box_width <= 0.0 or box_height <= 0.0:
        return None
    return f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
