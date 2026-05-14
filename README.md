# HYPER_CV_project

Waymo Open Dataset **Perception v1.4.3** 기반 자율주행 인식 실험 프로젝트입니다.

## 구조

```text
HYPER_CV_project/
  README.md
  data/                 # Waymo 원본/추출 데이터
  legacy/               # 예전 AI-Hub 데이터와 YOLO 학습 산출물
  models/               # YOLO 가중치
  outputs/              # 실행 결과
  requirements/         # 설치 파일
  scripts/
    detect/             # 표지판/차선/차량 인식
    waymo/              # Waymo TFRecord 처리
  src/                  # 공통 코드
```

## 현재 데이터

```text
data/waymo_perception/
  training/segment-10017090168044687777_6380_000_6400_000_with_camera_labels.tfrecord
  validation/segment-10203656353524179475_7625_000_7645_000_with_camera_labels.tfrecord
```

## 설치

현재 로컬 `python3`가 3.14라면 Waymo/TensorFlow 패키지가 맞지 않을 수 있습니다. Python 3.10/3.11 환경을 쓰거나, Waymo 처리만 Linux/Colab에서 실행하세요.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/waymo-perception.txt
python -m pip install -r requirements/vision.txt
```

## Waymo 처리

파일 확인:

```bash
python scripts/waymo/check_dataset.py --splits training validation --max-frames 5
```

카메라 이미지 추출:

```bash
python scripts/waymo/extract_frames.py \
  --splits training validation \
  --cameras FRONT \
  --max-frames 20
```

차량 라벨을 YOLO 데이터셋으로 변환:

```bash
python scripts/waymo/convert_vehicle_yolo.py \
  --splits training validation \
  --cameras FRONT \
  --max-frames 200
```

차선/도로 지도 프리뷰:

```bash
python scripts/waymo/preview_lanes.py \
  --splits training validation \
  --max-frames 3
```

## 인식 실행

Waymo에서 추출한 이미지를 대상으로 실행합니다.

```bash
python scripts/detect/traffic_sign.py --source data/waymo_camera_frames/validation
python scripts/detect/lane.py --source data/waymo_camera_frames/validation
python scripts/detect/vehicle.py --source data/waymo_camera_frames/validation
```

참고: Waymo Perception의 2D 카메라 라벨은 차량, 보행자, 자전거 중심입니다. 교통표지판은 Waymo 카메라 2D 정답 라벨로 바로 학습하기 어렵기 때문에 `models/traffic_sign_best.pt`를 추출 이미지에 적용하는 방식으로 시작합니다.
