#!/usr/bin/env python3
"""
실험 결과 시각화 — experiment_results.csv → 그래프 이미지 저장
실험 완료 후 실행하세요.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

RESULTS_FILE = Path("experiment_results.csv")
OUTPUT_DIR   = Path("report_figures")


def load_results(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    if not RESULTS_FILE.exists():
        print(f"{RESULTS_FILE} 파일이 없습니다. 실험 먼저 실행하세요.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = load_results(RESULTS_FILE)

    sizes      = [int(r["train_size"]) for r in rows]
    map50      = [float(r["mAP50"])     for r in rows]
    precision  = [float(r["precision"]) for r in rows]
    recall     = [float(r["recall"])    for r in rows]
    map50_95   = [float(r["mAP50_95"])  for r in rows]

    plt.rcParams["font.family"] = "AppleGothic"   # 맥 한글 폰트
    plt.rcParams["axes.unicode_minus"] = False

    # ── 그래프 1: mAP50 vs 데이터 수 ──────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, map50, marker="o", linewidth=2.5, color="#2E75B6", label="mAP50")
    ax.plot(sizes, map50_95, marker="s", linewidth=2, color="#70AD47",
            linestyle="--", label="mAP50-95")
    ax.set_xlabel("학습 데이터 수 (장)", fontsize=13)
    ax.set_ylabel("mAP", fontsize=13)
    ax.set_title("데이터 양에 따른 탐지 정확도 변화", fontsize=15, fontweight="bold")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.4)
    ax.set_ylim(0, max(map50 + map50_95) * 1.2 + 0.05)
    for x, y in zip(sizes, map50):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=10, color="#2E75B6")
    fig.tight_layout()
    out1 = OUTPUT_DIR / "figure1_mAP.png"
    fig.savefig(out1, dpi=150)
    print(f"저장: {out1}")
    plt.close(fig)

    # ── 그래프 2: Precision & Recall vs 데이터 수 ─────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, precision, marker="o", linewidth=2.5, color="#ED7D31", label="Precision")
    ax.plot(sizes, recall,    marker="s", linewidth=2.5, color="#A9D18E", label="Recall")
    ax.set_xlabel("학습 데이터 수 (장)", fontsize=13)
    ax.set_ylabel("값", fontsize=13)
    ax.set_title("데이터 양에 따른 Precision / Recall 변화", fontsize=15, fontweight="bold")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.4)
    ax.set_ylim(0, 1.1)
    fig.tight_layout()
    out2 = OUTPUT_DIR / "figure2_precision_recall.png"
    fig.savefig(out2, dpi=150)
    print(f"저장: {out2}")
    plt.close(fig)

    # ── 그래프 3: 4개 지표 한눈에 (막대그래프) ────────────────
    metrics = {"mAP50": map50, "mAP50-95": map50_95,
               "Precision": precision, "Recall": recall}
    colors  = ["#2E75B6", "#70AD47", "#ED7D31", "#A9D18E"]

    fig, axes = plt.subplots(1, 4, figsize=(14, 5), sharey=False)
    fig.suptitle("데이터 양별 성능 요약", fontsize=15, fontweight="bold")
    for ax, (name, values), color in zip(axes, metrics.items(), colors):
        bars = ax.bar([str(s) for s in sizes], values, color=color, alpha=0.85)
        ax.set_title(name, fontsize=12, fontweight="bold")
        ax.set_xlabel("학습 데이터 수", fontsize=10)
        ax.set_ylim(0, max(values) * 1.3 + 0.02)
        ax.grid(axis="y", alpha=0.3)
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    out3 = OUTPUT_DIR / "figure3_summary.png"
    fig.savefig(out3, dpi=150)
    print(f"저장: {out3}")
    plt.close(fig)

    print(f"\n그래프 3개 → {OUTPUT_DIR}/ 폴더에 저장됐습니다.")
    print("보고서에 바로 삽입 가능합니다!")


if __name__ == "__main__":
    main()
