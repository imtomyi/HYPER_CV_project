#!/usr/bin/env python3
"""Run a short YOLO training test on the converted AI-Hub sample dataset."""

from ultralytics import YOLO


def main() -> None:
    model = YOLO("yolov8n.pt")
    model.train(
        data="aihub_yolo_sample/data.yaml",
        epochs=3,
        imgsz=640,
        batch=4,
        workers=0,
        project="runs",
        name="traffic_sign_sample",
    )


if __name__ == "__main__":
    main()
