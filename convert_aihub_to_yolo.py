#!/usr/bin/env python3
"""
Convert a small AI-Hub traffic sign subset directly from .tar files to YOLO format.

This script avoids extracting the full 6GB source archive. It reads labels from the
label tar, finds images with traffic_sign annotations, and copies only the sampled
image/label pairs into a YOLO-ready folder.
"""

from __future__ import annotations

import argparse
import json
import random
import tarfile
from pathlib import Path


def yolo_box(box: list[float], width: float, height: float) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    cx = ((x1 + x2) / 2) / width
    cy = ((y1 + y2) / 2) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    return cx, cy, bw, bh


def read_label_members(label_tar_path: Path) -> list[tuple[str, dict]]:
    labels: list[tuple[str, dict]] = []
    with tarfile.open(label_tar_path) as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(".json"):
                continue
            file_obj = tar.extractfile(member)
            if file_obj is None:
                continue
            data = json.load(file_obj)
            annotations = data.get("annotation", [])
            if any(obj.get("class") == "traffic_sign" for obj in annotations):
                labels.append((member.name, data))
    return labels


def image_member_index(image_tar_path: Path) -> dict[str, tarfile.TarInfo]:
    index: dict[str, tarfile.TarInfo] = {}
    with tarfile.open(image_tar_path) as tar:
        for member in tar:
            if member.isfile() and member.name.lower().endswith((".jpg", ".jpeg", ".png")):
                index[Path(member.name).name] = member
    return index


def write_dataset_yaml(output_dir: Path) -> None:
    yaml_text = f"""path: {output_dir.resolve()}

train: images/train
val: images/val

names:
  0: traffic_sign
"""
    (output_dir / "data.yaml").write_text(yaml_text, encoding="utf-8")


def convert(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    label_tar_path = Path(args.label_tar)
    image_tar_path = Path(args.image_tar)
    output_dir = Path(args.output_dir)

    labels = read_label_members(label_tar_path)
    random.shuffle(labels)
    labels = labels[: args.limit]

    for split in ("train", "val"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    image_index = image_member_index(image_tar_path)
    train_cutoff = int(len(labels) * args.train_ratio)

    copied = 0
    skipped = 0
    with tarfile.open(image_tar_path) as image_tar:
        for idx, (_, data) in enumerate(labels):
            image_info = data.get("image", {})
            filename = image_info.get("filename")
            imsize = image_info.get("imsize", [])
            if not filename or len(imsize) != 2 or filename not in image_index:
                skipped += 1
                continue

            width, height = float(imsize[0]), float(imsize[1])
            yolo_lines: list[str] = []
            for obj in data.get("annotation", []):
                if obj.get("class") != "traffic_sign":
                    continue
                box = obj.get("box")
                if not isinstance(box, list) or len(box) != 4:
                    continue
                cx, cy, bw, bh = yolo_box(box, width, height)
                yolo_lines.append(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

            if not yolo_lines:
                skipped += 1
                continue

            split = "train" if idx < train_cutoff else "val"
            image_member = image_index[filename]
            image_obj = image_tar.extractfile(image_member)
            if image_obj is None:
                skipped += 1
                continue

            image_out = output_dir / "images" / split / filename
            label_out = output_dir / "labels" / split / f"{Path(filename).stem}.txt"
            image_out.write_bytes(image_obj.read())
            label_out.write_text("\n".join(yolo_lines) + "\n", encoding="utf-8")
            copied += 1

    write_dataset_yaml(output_dir)
    print(f"Copied {copied} image/label pairs to {output_dir}")
    print(f"Skipped {skipped} labels")
    print(f"YOLO config: {output_dir / 'data.yaml'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label-tar", required=True, help="Path to AI-Hub label .tar")
    parser.add_argument("--image-tar", required=True, help="Path to AI-Hub source image .tar")
    parser.add_argument("--output-dir", default="aihub_yolo_sample", help="Output YOLO dataset directory")
    parser.add_argument("--limit", type=int, default=200, help="Maximum images to copy")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Train split ratio")
    parser.add_argument("--seed", type=int, default=42)
    convert(parser.parse_args())


if __name__ == "__main__":
    main()
