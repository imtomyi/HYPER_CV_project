#!/usr/bin/env python3
"""
실험 결과에서 가장 좋은 모델을 자동으로 찾아 validation 이미지에 예측 실행
실험 완료 후 실행하세요.
"""

import csv
from pathlib import Path

from ultralytics import YOLO

RESULTS_FILE = Path("experiment_results.csv")
RUNS_DIR     = Path("runs/experiments")
VAL_IMAGES   = Path("data/waymo_vehicle_yolo_v2/images/validation")
CONF         = 0.25


def find_best_model() -> tuple[int, float, Path]:
    """experiment_results.csv에서 mAP50 가장 높은 실험 찾기"""
    with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    best = max(rows, key=lambda r: float(r["mAP50"]))
    size = int(best["train_size"])
    map50 = float(best["mAP50"])

    weights = RUNS_DIR / f"vehicle_{size}imgs" / "weights" / "best.pt"
    return size, map50, weights


def main() -> None:
    if not RESULTS_FILE.exists():
        print("experiment_results.csv 없음. run_experiments.py 먼저 실행하세요.")
        return

    size, map50, weights = find_best_model()
    print(f"최고 모델: training {size}장 (mAP50={map50:.4f})")
    print(f"가중치: {weights}")

    if not weights.exists():
        print("가중치 파일을 찾을 수 없습니다.")
        return

    model = YOLO(str(weights))
    model.predict(
        source=str(VAL_IMAGES),
        conf=CONF,
        imgsz=640,
        save=True,
        save_txt=True,
        project="runs/predictions",
        name=f"best_model_{size}imgs",
    )
    print(f"\n예측 결과 저장: runs/predictions/best_model_{size}imgs/")


if __name__ == "__main__":
    main()
