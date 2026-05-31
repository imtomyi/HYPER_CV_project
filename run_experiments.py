#!/usr/bin/env python3
"""
데이터 양에 따른 YOLOv8 차량 탐지 성능 비교 실험
- 실험 4회 자동 실행 (200 / 400 / 800 / 1190장)
- 결과를 experiment_results.csv 로 저장
"""

import csv
import random
import shutil
from pathlib import Path

from ultralytics import YOLO

# ── 설정 ─────────────────────────────────────────────────────
BASE_DATASET   = Path("data/waymo_vehicle_yolo_v2")   # 전체 데이터셋
EXPERIMENT_DIR = Path("data/experiments")              # 실험용 임시 폴더
RESULTS_FILE   = Path("experiment_results.csv")        # 최종 결과 저장
MODEL_BASE     = "yolov8n.pt"                          # 베이스 모델

TRAIN_SIZES    = [200, 400, 800, 1190]                 # 실험할 데이터 수
EPOCHS         = 10                                    # 학습 횟수 (고정)
IMGSZ          = 640
BATCH          = 8
SEED           = 42
# ─────────────────────────────────────────────────────────────


def make_subset(size: int, seed: int = SEED) -> Path:
    """전체 training 이미지에서 size장만 랜덤 선택해 임시 데이터셋 생성"""
    subset_dir = EXPERIMENT_DIR / f"subset_{size}"

    # 이미 만들어진 경우 재사용
    if subset_dir.exists():
        print(f"  [재사용] 기존 subset_{size} 폴더 사용")
        return subset_dir / "data.yaml"

    all_images = sorted((BASE_DATASET / "images" / "training").glob("*.jpg"))
    random.seed(seed)
    selected = random.sample(all_images, min(size, len(all_images)))

    for split in ("training", "validation"):
        (subset_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (subset_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    # 선택된 training 이미지 + 라벨 복사
    for img_path in selected:
        label_path = BASE_DATASET / "labels" / "training" / img_path.with_suffix(".txt").name
        shutil.copy(img_path,   subset_dir / "images" / "training" / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, subset_dir / "labels" / "training" / label_path.name)

    # validation은 전체 고정 (공정한 비교)
    for img_path in (BASE_DATASET / "images" / "validation").glob("*.jpg"):
        label_path = BASE_DATASET / "labels" / "validation" / img_path.with_suffix(".txt").name
        shutil.copy(img_path, subset_dir / "images" / "validation" / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, subset_dir / "labels" / "validation" / label_path.name)

    # data.yaml 생성
    yaml_text = f"""path: {subset_dir.resolve()}
train: images/training
val: images/validation

names:
  0: vehicle
"""
    (subset_dir / "data.yaml").write_text(yaml_text, encoding="utf-8")
    print(f"  [생성] subset_{size}: training {len(selected)}장")
    return subset_dir / "data.yaml"


def run_experiment(size: int) -> dict:
    """단일 실험 실행 후 결과 반환"""
    print(f"\n{'='*50}")
    print(f"  실험: training {size}장 / epochs {EPOCHS}")
    print(f"{'='*50}")

    data_yaml = make_subset(size)

    model = YOLO(MODEL_BASE)
    results = model.train(
        data=str(data_yaml),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        workers=0,
        project="runs/experiments",
        name=f"vehicle_{size}imgs",
        exist_ok=True,
        verbose=False,
    )

    # 최고 성능 epoch 결과 추출
    metrics = results.results_dict
    return {
        "train_size":  size,
        "epochs":      EPOCHS,
        "precision":   round(metrics.get("metrics/precision(B)", 0), 4),
        "recall":      round(metrics.get("metrics/recall(B)", 0), 4),
        "mAP50":       round(metrics.get("metrics/mAP50(B)", 0), 4),
        "mAP50_95":    round(metrics.get("metrics/mAP50-95(B)", 0), 4),
    }


def main() -> None:
    all_results = []

    for size in TRAIN_SIZES:
        result = run_experiment(size)
        all_results.append(result)

        # 중간 결과 즉시 저장 (중단돼도 데이터 보존)
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)

        print(f"\n  결과: mAP50={result['mAP50']:.4f} | "
              f"Precision={result['precision']:.4f} | "
              f"Recall={result['recall']:.4f}")

    # 최종 결과 출력
    print(f"\n{'='*50}")
    print("  전체 실험 완료!")
    print(f"{'='*50}")
    print(f"{'학습 수':>8} | {'mAP50':>8} | {'Precision':>10} | {'Recall':>8}")
    print("-" * 44)
    for r in all_results:
        print(f"{r['train_size']:>8} | {r['mAP50']:>8.4f} | "
              f"{r['precision']:>10.4f} | {r['recall']:>8.4f}")
    print(f"\n결과 저장: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
