#!/usr/bin/env python3
"""
HYPER 최종 결과 보고서 HTML 생성기
실행: python generate_report.py
결과: report/HYPER_최종결과보고서_팀명.html
"""

import base64
import csv
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── 설정 ─────────────────────────────────
RESULTS_FILE = Path("experiment_results.csv")
OUTPUT_DIR   = Path("report")
OUTPUT_FILE  = OUTPUT_DIR / "HYPER_최종결과보고서_비전초보.html"
TEAM_NAME    = "비전초보"
# ─────────────────────────────────────────

plt.rcParams["font.family"]        = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def load_results():
    with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def make_map_chart(rows) -> str:
    sizes   = [int(r["train_size"]) for r in rows]
    map50   = [float(r["mAP50"])    for r in rows]
    map5095 = [float(r["mAP50_95"]) for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(sizes, map50,   marker="o", lw=2.5, color="#2E75B6", label="mAP50")
    ax.plot(sizes, map5095, marker="s", lw=2,   color="#70AD47",
            linestyle="--", label="mAP50-95")
    for x, y in zip(sizes, map50):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=10, color="#2E75B6")
    ax.set_xlabel("학습 데이터 수 (장)", fontsize=12)
    ax.set_ylabel("mAP", fontsize=12)
    ax.set_title("데이터 양에 따른 탐지 정확도(mAP) 변화", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(map50) * 1.4)
    fig.tight_layout()
    b64 = fig_to_base64(fig)
    plt.close(fig)
    return b64


def make_pr_chart(rows) -> str:
    sizes     = [int(r["train_size"])   for r in rows]
    precision = [float(r["precision"])  for r in rows]
    recall    = [float(r["recall"])     for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(sizes, precision, marker="o", lw=2.5, color="#ED7D31", label="Precision")
    ax.plot(sizes, recall,    marker="s", lw=2.5, color="#4CAF50", label="Recall")
    ax.set_xlabel("학습 데이터 수 (장)", fontsize=12)
    ax.set_ylabel("값", fontsize=12)
    ax.set_title("데이터 양에 따른 Precision / Recall 변화", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 0.6)
    fig.tight_layout()
    b64 = fig_to_base64(fig)
    plt.close(fig)
    return b64


def make_bar_chart(rows) -> str:
    sizes  = [f"{int(r['train_size'])}장" for r in rows]
    map50  = [float(r["mAP50"])           for r in rows]
    colors = ["#BDD7EE", "#70AD47", "#2E75B6"]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(sizes, map50, color=colors, width=0.5, edgecolor="white")
    for bar, v in zip(bars, map50):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.003,
                f"{v:.4f}", ha="center", fontsize=11, fontweight="bold")
    ax.set_xlabel("학습 데이터 수", fontsize=12)
    ax.set_ylabel("mAP50", fontsize=12)
    ax.set_title("실험별 최종 mAP50 비교", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(map50) * 1.35)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    b64 = fig_to_base64(fig)
    plt.close(fig)
    return b64


def build_html(rows, chart_map, chart_pr, chart_bar) -> str:
    best = max(rows, key=lambda r: float(r["mAP50"]))

    rows_html = ""
    for r in rows:
        is_best = r == best
        style = ' style="background:#EBF3FB;font-weight:bold;"' if is_best else ""
        badge = ' <span class="badge">최고</span>' if is_best else ""
        rows_html += f"""
        <tr{style}>
          <td>{int(r['train_size']):,}장</td>
          <td>{r['epochs']}</td>
          <td>{float(r['precision']):.4f}</td>
          <td>{float(r['recall']):.4f}</td>
          <td>{float(r['mAP50']):.4f}{badge}</td>
          <td>{float(r['mAP50_95']):.4f}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>HYPER 최종 결과 보고서 — {TEAM_NAME}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
            background: #F5F7FA; color: #222; line-height: 1.7; }}

    /* 커버 */
    .cover {{
      background: linear-gradient(135deg, #1a3a6b 0%, #2E75B6 60%, #4a9fd4 100%);
      color: white; text-align: center;
      padding: 80px 40px 60px;
    }}
    .cover .tag {{ font-size: 13px; letter-spacing: 4px; opacity: 0.75;
                   text-transform: uppercase; margin-bottom: 20px; }}
    .cover h1 {{ font-size: 36px; font-weight: 800; margin-bottom: 12px; }}
    .cover .sub {{ font-size: 18px; opacity: 0.85; margin-bottom: 40px; }}
    .cover .meta {{ display: flex; justify-content: center; gap: 48px;
                    font-size: 14px; opacity: 0.8; }}
    .cover .meta span b {{ display: block; font-size: 16px; opacity: 1;
                            font-weight: 700; margin-bottom: 2px; }}

    /* 본문 */
    .container {{ max-width: 900px; margin: 0 auto; padding: 48px 24px; }}
    section {{ background: white; border-radius: 12px; padding: 36px 40px;
               margin-bottom: 32px; box-shadow: 0 2px 12px rgba(0,0,0,.06); }}
    h2 {{ font-size: 22px; color: #1a3a6b; border-left: 4px solid #2E75B6;
          padding-left: 14px; margin-bottom: 20px; }}
    h3 {{ font-size: 16px; color: #2E75B6; margin: 20px 0 10px; }}
    p  {{ color: #444; margin-bottom: 12px; font-size: 15px; }}

    /* 하이라이트 카드 */
    .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
              margin: 24px 0; }}
    .card  {{ background: #F0F6FF; border-radius: 10px; padding: 20px;
               text-align: center; border: 1px solid #D0E4F7; }}
    .card .num  {{ font-size: 32px; font-weight: 800; color: #2E75B6; }}
    .card .label {{ font-size: 13px; color: #666; margin-top: 4px; }}

    /* 표 */
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0;
             font-size: 14px; }}
    th    {{ background: #1a3a6b; color: white; padding: 12px 16px;
             text-align: center; font-weight: 600; }}
    td    {{ padding: 11px 16px; text-align: center; border-bottom: 1px solid #EEE; }}
    tr:hover td {{ background: #F7FBFF; }}
    .badge {{ background: #2E75B6; color: white; font-size: 11px;
               padding: 2px 7px; border-radius: 10px; margin-left: 6px;
               font-weight: 600; vertical-align: middle; }}

    /* 차트 */
    .chart-wrap {{ text-align: center; margin: 20px 0; }}
    .chart-wrap img {{ max-width: 100%; border-radius: 8px;
                       box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}

    /* 파이프라인 */
    .pipeline {{ display: flex; align-items: center; gap: 0;
                 margin: 20px 0; flex-wrap: wrap; }}
    .step {{ background: #F0F6FF; border: 1px solid #C5DEFF;
              border-radius: 8px; padding: 14px 18px; font-size: 14px;
              text-align: center; flex: 1; min-width: 120px; }}
    .step b {{ display: block; color: #1a3a6b; font-size: 13px;
                margin-bottom: 4px; }}
    .arrow {{ font-size: 22px; color: #2E75B6; padding: 0 6px; }}

    /* 분석 박스 */
    .insight {{ background: #F0F6FF; border-left: 4px solid #2E75B6;
                border-radius: 0 8px 8px 0; padding: 16px 20px;
                margin: 12px 0; font-size: 14px; color: #333; }}
    .insight b {{ color: #1a3a6b; }}

    /* 한계 리스트 */
    ul.limit {{ padding-left: 20px; }}
    ul.limit li {{ margin-bottom: 8px; color: #555; font-size: 14px; }}

    /* 푸터 */
    footer {{ text-align: center; padding: 32px; color: #999; font-size: 13px; }}
  </style>
</head>
<body>

<!-- 커버 -->
<div class="cover">
  <div class="tag">HYPER Robotics · Computer Vision</div>
  <h1>자율주행 차량 탐지 성능 분석</h1>
  <div class="sub">데이터 양이 YOLOv8 차량 탐지 성능에 미치는 영향</div>
  <div class="meta">
    <span><b>{TEAM_NAME}</b>팀명</span>
    <span><b>YOLOv8n</b>모델</span>
    <span><b>Waymo Open Dataset</b>데이터셋</span>
    <span><b>2026</b>년도</span>
  </div>
</div>

<div class="container">

  <!-- 1. 개요 -->
  <section>
    <h2>1. 프로젝트 개요</h2>
    <p>
      본 프로젝트는 자율주행 환경에서의 컴퓨터 비전 기술 습득을 목표로,
      <b>Waymo Open Dataset</b>의 실제 도로 주행 영상을 활용하여
      <b>YOLOv8</b> 기반 차량 탐지 모델을 학습하고,
      <b>학습 데이터 양</b>이 탐지 성능에 미치는 영향을 정량적으로 분석하였습니다.
    </p>
    <div class="cards">
      <div class="card">
        <div class="num">{len(rows)}</div>
        <div class="label">실험 횟수</div>
      </div>
      <div class="card">
        <div class="num">1,190</div>
        <div class="label">최대 학습 이미지 수</div>
      </div>
      <div class="card">
        <div class="num">{float(best['mAP50']):.1%}</div>
        <div class="label">최고 mAP50</div>
      </div>
    </div>
  </section>

  <!-- 2. 실험 환경 -->
  <section>
    <h2>2. 실험 환경 및 방법론</h2>
    <h3>데이터 파이프라인</h3>
    <div class="pipeline">
      <div class="step"><b>원본 데이터</b>Waymo .tfrecord</div>
      <div class="arrow">→</div>
      <div class="step"><b>프레임 추출</b>FRONT 카메라</div>
      <div class="arrow">→</div>
      <div class="step"><b>YOLO 변환</b>라벨 좌표 정규화</div>
      <div class="arrow">→</div>
      <div class="step"><b>학습/검증</b>80% / 20%</div>
      <div class="arrow">→</div>
      <div class="step"><b>성능 평가</b>mAP50 측정</div>
    </div>

    <h3>실험 조건 (모든 실험 동일)</h3>
    <table>
      <tr>
        <th>항목</th><th>설정값</th>
        <th>항목</th><th>설정값</th>
      </tr>
      <tr><td>모델</td><td>YOLOv8n</td>
          <td>Epochs</td><td>10</td></tr>
      <tr><td>이미지 크기</td><td>640×640</td>
          <td>Batch Size</td><td>8</td></tr>
      <tr><td>Optimizer</td><td>Auto (SGD)</td>
          <td>하드웨어</td><td>Apple M4 Pro (CPU)</td></tr>
      <tr><td>탐지 클래스</td><td>vehicle (1개)</td>
          <td>검증 데이터</td><td>198장 (고정)</td></tr>
    </table>

    <h3>학습 데이터 구성</h3>
    <p>Waymo Open Dataset Perception v1.4.3 — training 세그먼트 6개 (총 1,190장) 중
    각 실험별로 무작위 샘플링하여 사용. 검증 세트는 별도 세그먼트(198장)로 고정.</p>
  </section>

  <!-- 3. 결과 -->
  <section>
    <h2>3. 실험 결과</h2>
    <table>
      <tr>
        <th>학습 데이터 수</th><th>Epochs</th>
        <th>Precision</th><th>Recall</th>
        <th>mAP50</th><th>mAP50-95</th>
      </tr>
      {rows_html}
    </table>

    <div class="chart-grid" style="margin-top:28px;">
      <div class="chart-wrap">
        <img src="data:image/png;base64,{chart_map}" alt="mAP 차트"/>
      </div>
      <div class="chart-wrap">
        <img src="data:image/png;base64,{chart_bar}" alt="bar 차트"/>
      </div>
    </div>
    <div class="chart-wrap" style="margin-top:12px;">
      <img src="data:image/png;base64,{chart_pr}" alt="PR 차트"/>
    </div>
  </section>

  <!-- 4. 분석 -->
  <section>
    <h2>4. 결과 분석</h2>
    <div class="insight">
      <b>📈 데이터 증가에 따른 성능 변화</b><br/>
      200장 → 400장 구간에서 mAP50이 15.5% → 16.7%로 가장 큰 폭으로 상승하였습니다.
      이후 800장에서는 16.2%로 소폭 하락하였는데, 이는 데이터 다양성 없이
      단순히 유사한 장면의 이미지만 추가될 경우 오히려 과적합이 발생할 수 있음을 시사합니다.
    </div>
    <div class="insight">
      <b>🎯 Precision vs Recall 트레이드오프</b><br/>
      Precision(정밀도)은 세 실험에서 약 34~36%로 안정적인 반면,
      Recall(재현율)은 18.6% → 20.1%로 꾸준히 증가하는 경향을 보였습니다.
      이는 데이터가 늘어날수록 모델이 더 많은 차량을 놓치지 않고 탐지하게 됨을 의미합니다.
    </div>
    <div class="insight">
      <b>🔍 전반적 성능 수준</b><br/>
      전체적인 mAP50 수치(15~17%)는 낮은 편으로, 이는 10 epoch의 제한된 학습 횟수,
      단일 클래스 모델, 그리고 데이터셋 내 장면 다양성 부족에서 기인합니다.
      epoch 수를 50~100으로 늘리거나 다양한 도로 환경의 세그먼트를 추가하면
      성능이 크게 향상될 것으로 예상됩니다.
    </div>
  </section>

  <!-- 5. 결론 -->
  <section>
    <h2>5. 결론 및 향후 과제</h2>
    <p>
      본 실험을 통해 <b>학습 데이터의 양이 YOLOv8 차량 탐지 성능에 유의미한 영향을 미침</b>을
      확인하였습니다. 특히 소량(200장) 구간에서 데이터를 늘릴수록 성능 향상 효과가
      크게 나타났습니다.
    </p>
    <h3>향후 개선 방향</h3>
    <ul class="limit">
      <li>학습 epoch 확대 (10 → 50~100) 및 GPU 환경에서의 재실험</li>
      <li>Waymo 세그먼트 추가 확보를 통한 데이터 다양성 확보 (야간, 우천 등)</li>
      <li>차량 종류 세분화 (승용차 / 트럭 / 버스 / 오토바이) 멀티클래스 확장</li>
      <li>아이폰 카메라 연동 실시간 탐지 데모 완성</li>
      <li>별도 test 세트 구성을 통한 공정한 최종 성능 평가</li>
    </ul>
  </section>

</div>

<footer>
  HYPER Robotics · {TEAM_NAME} · 2026 &nbsp;|&nbsp;
  Model: YOLOv8n &nbsp;|&nbsp; Dataset: Waymo Open Dataset v1.4.3
</footer>

</body>
</html>"""


def main() -> None:
    if not RESULTS_FILE.exists():
        print("experiment_results.csv 파일이 없습니다.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = load_results()

    print("그래프 생성 중...")
    chart_map = make_map_chart(rows)
    chart_pr  = make_pr_chart(rows)
    chart_bar = make_bar_chart(rows)

    print("HTML 보고서 작성 중...")
    html = build_html(rows, chart_map, chart_pr, chart_bar)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"\n✅ 완료: {OUTPUT_FILE}")
    print("브라우저에서 열어서 확인하세요!")


if __name__ == "__main__":
    main()
