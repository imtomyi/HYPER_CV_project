#!/usr/bin/env python3
"""Run traffic sign detection on the converted validation images."""

from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    weights = Path("runs/detect/runs/traffic_sign_sample-2/weights/best.pt")
    source = Path("aihub_yolo_sample/images/val")

    model = YOLO(str(weights))
    model.predict(
        source=str(source),
        conf=0.25,
        imgsz=640,
        save=True,
        project="runs",
        name="traffic_sign_predictions",
    )


if __name__ == "__main__":
    main()
