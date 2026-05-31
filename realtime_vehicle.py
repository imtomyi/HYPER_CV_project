#!/usr/bin/env python3
"""
실시간 차량 종류 구분 탐지
- 승용차 / 트럭 / 버스 / 오토바이 / 자전거 구분
- 아이폰 or 웹캠 연결 후 실행
- 종료: q 키
"""

import time
from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO

# ── 설정 ──────────────────────────────────────────────────────
CAMERA_INDEX = 0        # 0 = 아이폰(Continuity Camera), 1 = 내장 웹캠
CONF         = 0.40     # 신뢰도 임계값 (높을수록 확실한 것만 탐지)
IMGSZ        = 640

# 실험 완료 후 custom 모델로 교체하려면 아래 주석 해제:
# WEIGHTS = "runs/experiments/vehicle_1190imgs/weights/best.pt"
WEIGHTS      = "yolov8n.pt"   # COCO 사전학습 모델 (차종 구분 가능)
# ──────────────────────────────────────────────────────────────

# COCO 차량 클래스 (ID: 한글 이름, 색상 BGR)
VEHICLE_CLASSES = {
    2: ("승용차",    (255, 100,   0)),   # 파란색
    3: ("오토바이", ( 0,  200, 255)),   # 노란색
    5: ("버스",     ( 0,  200,   0)),   # 초록색
    7: ("트럭",     (  0,  60, 220)),   # 빨간색
    1: ("자전거",   (200,   0, 200)),   # 보라색
}


def draw_box(frame, box, label: str, color: tuple) -> None:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    conf = float(box.conf[0])

    # 박스
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # 라벨 배경
    text = f"{label} {conf:.0%}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)

    # 라벨 텍스트
    cv2.putText(frame, text, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def draw_dashboard(frame, counts: Counter, fps: float) -> None:
    """우측 상단에 차량 종류별 카운트 대시보드 표시"""
    h, w = frame.shape[:2]
    x_start = w - 200
    y_start = 10

    # 배경 반투명 박스
    overlay = frame.copy()
    cv2.rectangle(overlay, (x_start - 10, y_start),
                  (w - 5, y_start + 30 + len(VEHICLE_CLASSES) * 28),
                  (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (x_start, y_start + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)

    # 차종별 카운트
    for i, (cls_id, (name, color)) in enumerate(VEHICLE_CLASSES.items()):
        count = counts.get(name, 0)
        y = y_start + 50 + i * 28
        dot_x = x_start
        cv2.circle(frame, (dot_x, y - 5), 7, color, -1)
        cv2.putText(frame, f"{name}: {count}대",
                    (dot_x + 15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 2)


def main() -> None:
    print(f"모델 로드 중: {WEIGHTS}")
    model = YOLO(WEIGHTS)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"카메라(index={CAMERA_INDEX})를 열 수 없습니다.")
        return

    print("카메라 연결 성공! 종료하려면 q 를 누르세요.")

    fps_list: list[float] = []
    target_classes = list(VEHICLE_CLASSES.keys())

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        t0 = time.perf_counter()

        results = model.predict(
            source=frame,
            conf=CONF,
            imgsz=IMGSZ,
            classes=target_classes,   # 차량 클래스만 탐지
            verbose=False,
        )

        elapsed = time.perf_counter() - t0
        fps_list.append(1.0 / elapsed if elapsed > 0 else 0)
        if len(fps_list) > 30:
            fps_list.pop(0)
        fps = sum(fps_list) / len(fps_list)

        # 탐지된 차량 그리기 + 카운트
        counts: Counter = Counter()
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue
            name, color = VEHICLE_CLASSES[cls_id]
            draw_box(frame, box, name, color)
            counts[name] += 1

        # 대시보드 오버레이
        draw_dashboard(frame, counts, fps)

        cv2.imshow("Vehicle Detection (q: 종료)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("종료되었습니다.")


if __name__ == "__main__":
    main()
