#!/usr/bin/env python3
"""
실시간 교통 표지판 탐지
- 아이폰(Continuity Camera) USB 연결 후 실행
- 종료: q 키
"""

import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

# ── 설정 ──────────────────────────────────────────────
WEIGHTS = Path("HYPER_CV_project/runs/detect/runs/traffic_sign_sample-2/weights/best.pt")
CONF_THRESHOLD = 0.25  # 신뢰도 25% 이상만 탐지
IMGSZ = 640            # 추론 이미지 크기
CAM_INDEX = 0          # None: 자동 탐지 / 정수 지정 시 해당 인덱스 강제 사용

# 클래스별 한글 이름 & 색상 (BGR)  ← 모델 클래스 인덱스와 맞춰 설정
CLASS_INFO = {
    0: {"name": "교통표지판", "color": (0, 200, 0)},   # 초록
}
# ──────────────────────────────────────────────────────


def _get_font(size: int = 22):
    """시스템 한글 폰트 로드 (없으면 PIL 기본 폰트)"""
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_detections(frame: np.ndarray, results, cam_name: str, fps: float) -> np.ndarray:
    """PIL로 탐지 결과를 프레임 위에 그린다 (한글 지원)."""
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    font_label = _get_font(22)
    font_info  = _get_font(18)

    boxes = results[0].boxes
    det_count = len(boxes)

    for box in boxes:
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        info = CLASS_INFO.get(cls_id, {"name": f"Class{cls_id}", "color": (255, 100, 0)})
        label_text = f"{info['name']}  {conf*100:.0f}%"
        r, g, b = info["color"][2], info["color"][1], info["color"][0]  # BGR→RGB

        # 박스 그리기
        draw.rectangle([x1, y1, x2, y2], outline=(r, g, b), width=3)

        # 라벨 배경
        bbox = font_label.getbbox(label_text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([x1, y1 - th - 8, x1 + tw + 10, y1], fill=(r, g, b))
        draw.text((x1 + 5, y1 - th - 4), label_text, font=font_label, fill=(255, 255, 255))

    # 상단 오버레이 (FPS / 탐지수 / 카메라)
    draw.text((10, 8),  f"FPS: {fps:.1f}   탐지: {det_count}개", font=font_info, fill=(0, 255, 0))
    draw.text((10, 32), f"CAM: {cam_name}",                       font=font_info, fill=(0, 200, 255))

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _iphone_connected() -> str | None:
    """AVFoundation으로 iPhone 연결 여부 확인. 연결되면 장치 이름, 없으면 None."""
    try:
        from AVFoundation import AVCaptureDevice, AVMediaTypeVideo
        devices = AVCaptureDevice.devicesWithMediaType_(AVMediaTypeVideo)
        print("  감지된 카메라 (AVFoundation):")
        iphone_name = None
        for i, d in enumerate(devices):
            name = str(d.localizedName())
            is_iphone = "MacBook" not in name and "FaceTime" not in name
            print(f"    [{i}] {name}{' ← iPhone' if is_iphone else ''}")
            if is_iphone and iphone_name is None:
                iphone_name = name
        return iphone_name
    except Exception as e:
        print(f"  AVFoundation 오류: {e}")
        return None


def find_camera():
    """
    iPhone Continuity Camera를 찾아 열기.

    AVFoundation 인덱스와 OpenCV 인덱스가 일치하지 않을 수 있으므로
    인덱스 매핑 대신 해상도를 기준으로 정렬해 iPhone(고해상도)을 우선 선택.
    자동 탐지가 틀릴 경우 상단 CAM_INDEX로 강제 지정 가능.
    """
    # ── 강제 지정 모드 ─────────────────────────────────
    if CAM_INDEX is not None:
        print(f"  CAM_INDEX={CAM_INDEX} 강제 사용")
        cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            print(f"  index {CAM_INDEX} 열기 실패")
            return None, None
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"  ✓ index {CAM_INDEX} 열림 ({w}x{h})")
        return cap, f"카메라 [idx={CAM_INDEX}, {w}x{h}]"

    # ── 자동 탐지 ──────────────────────────────────────
    iphone_name = _iphone_connected()
    if iphone_name is None:
        print("  ❌ 아이폰 미감지. USB 연결 → 잠금 해제 → '이 컴퓨터 신뢰' 확인")
        return None, None

    # OpenCV 인덱스 0~5를 열어 해상도 수집
    print("\n  OpenCV 카메라 스캔 중...")
    candidates: list[tuple[int, cv2.VideoCapture, int, int]] = []
    for idx in range(6):
        cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"    [OpenCV {idx}] {w}x{h}")
            candidates.append((idx, cap, w, h))
        else:
            cap.release()

    if not candidates:
        print("  ❌ 사용 가능한 카메라 없음")
        return None, None

    # 해상도 내림차순 정렬: iPhone(1080p↑) > MacBook 내장(720p)
    candidates.sort(key=lambda c: c[2] * c[3], reverse=True)
    print(f"\n  해상도 기준 탐색 순서: {[f'idx={c[0]}({c[2]}x{c[3]})' for c in candidates]}")
    print("  ※ 잘못된 카메라가 열리면 상단 CAM_INDEX에 인덱스를 직접 지정하세요.")

    selected: tuple[int, cv2.VideoCapture, int, int] | None = None
    for i, (idx, cap, w, h) in enumerate(candidates):
        print(f"\n  [index {idx}, {w}x{h}] 프레임 수신 대기 (최대 4초)...")
        deadline = time.time() + 4.0
        got_frame = False
        while time.time() < deadline:
            ret, frame = cap.read()
            if ret and frame is not None and frame.mean() > 2:
                print(f"  [index {idx}] ✓ 성공 (밝기={frame.mean():.1f})")
                got_frame = True
                break

        if got_frame:
            selected = (idx, cap, w, h)
            # 뒤에 열려 있는 나머지 cap 해제
            for _, other_cap, _, _ in candidates[i + 1:]:
                other_cap.release()
            break

        cap.release()

    if selected is None:
        print("\n  ❌ 모든 카메라에서 프레임 수신 실패. 아이폰 재연결 후 시도하세요.")
        return None, None

    idx, cap, w, h = selected
    return cap, f"{iphone_name} [idx={idx}, {w}x{h}]"


def main() -> None:
    # 모델 로드
    print(f"모델 로드 중: {WEIGHTS}")
    model = YOLO(str(WEIGHTS))

    # 카메라 열기
    print("카메라 탐색 중...")
    cap, cam_name = find_camera()
    if cap is None:
        print("카메라를 찾을 수 없습니다. 아이폰 USB 연결 후 재시도하세요.")
        return

    print(f"카메라 연결 성공! [{cam_name}]  종료: q")

    fps_list: list[float] = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue  # 프레임 실패 → 스킵

            # 검은 화면(초기화 중)이면 YOLO 스킵하고 그냥 표시만
            if frame.mean() < 2:
                cv2.imshow("Traffic Sign Detection (q: 종료)", frame)
                if (cv2.waitKey(1) & 0xFF) in (ord("q"), ord("Q"), 27):
                    break
                continue

            # YOLO 추론
            t0 = time.perf_counter()
            results = model.predict(
                source=frame,
                conf=CONF_THRESHOLD,
                imgsz=IMGSZ,
                verbose=False,
            )
            elapsed = time.perf_counter() - t0

            # FPS (최근 30프레임 평균)
            fps_list.append(1.0 / elapsed if elapsed > 0 else 0)
            if len(fps_list) > 30:
                fps_list.pop(0)
            fps = sum(fps_list) / len(fps_list)

            # 탐지 결과 그리기 (PIL 한글 렌더링)
            annotated = draw_detections(frame, results, cam_name, fps)

            cv2.imshow("Traffic Sign Detection (q: 종료)", annotated)

            key = cv2.waitKey(1)
            if (key & 0xFF) in (ord("q"), ord("Q"), 27) or key == ord("ㅂ"):
                break

    except KeyboardInterrupt:
        print("\nCtrl+C 감지 — 정리 중...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("종료되었습니다.")


if __name__ == "__main__":
    main()
