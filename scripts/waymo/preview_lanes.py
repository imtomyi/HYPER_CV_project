#!/usr/bin/env python3
"""Render top-down Waymo map lane/road features from Perception TFRecords."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from waymo_perception_io import (
    DEFAULT_WAYMO_PERCEPTION_ROOT,
    discover_tfrecords,
    frame_stem,
    iter_frames,
    split_input_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview Waymo map lane features.")
    parser.add_argument("--root", type=Path, default=DEFAULT_WAYMO_PERCEPTION_ROOT)
    parser.add_argument("--splits", nargs="+", default=["training", "validation"])
    parser.add_argument("--max-frames", type=int, default=3)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/waymo_map_lanes"),
    )
    return parser.parse_args()


def import_plotting():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print(
            "Install plotting dependencies with: "
            "python3 -m pip install -r requirements-waymo-perception.txt",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return plt


def points_from_feature(feature):
    for name in ("lane", "road_line", "road_edge", "crosswalk", "speed_bump", "driveway"):
        try:
            if not feature.HasField(name):
                continue
        except ValueError:
            continue
        item = getattr(feature, name)
        if hasattr(item, "polyline"):
            return name, [(point.x, point.y) for point in item.polyline]
        if hasattr(item, "polygon"):
            return name, [(point.x, point.y) for point in item.polygon]
    try:
        if feature.HasField("stop_sign"):
            point = feature.stop_sign.position
            return "stop_sign", [(point.x, point.y)]
    except ValueError:
        pass
    return None, []


def main() -> int:
    args = parse_args()
    plt = import_plotting()
    files = discover_tfrecords(split_input_paths(args.root, args.splits))
    if not files:
        print(f"No TFRecord files found under: {args.root}")
        return 2

    colors = {
        "lane": "#1f77b4",
        "road_line": "#ffbf00",
        "road_edge": "#444444",
        "crosswalk": "#2ca02c",
        "speed_bump": "#d62728",
        "driveway": "#9467bd",
        "stop_sign": "#d62728",
    }
    saved = 0
    for file_path, frame_index, frame in iter_frames(files, max_frames=args.max_frames):
        if not frame.map_features:
            continue
        fig, ax = plt.subplots(figsize=(8, 8))
        used_labels: set[str] = set()
        for feature in frame.map_features:
            kind, points = points_from_feature(feature)
            if not kind or not points:
                continue
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            label = kind if kind not in used_labels else None
            used_labels.add(kind)
            if len(points) == 1:
                ax.scatter(xs, ys, s=35, color=colors.get(kind, "#111111"), label=label)
            else:
                ax.plot(xs, ys, linewidth=1.1, color=colors.get(kind, "#111111"), label=label)

        if not used_labels:
            plt.close(fig)
            continue
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.3, alpha=0.4)
        ax.set_title("Waymo map lane/road preview")
        ax.legend(frameon=False, loc="best")
        output = args.output_dir / file_path.parent.name / f"{frame_stem(file_path, frame_index)}_map.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(output, dpi=180)
        plt.close(fig)
        print(f"saved: {output}")
        saved += 1

    print(f"saved map previews: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
