const pptxgen = require("pptxgenjs");
const path = require("path");

const ASSETS = path.resolve(__dirname, "assets");

// ── 색상 팔레트 ─────────────────────────────────────────
const C = {
  navy:    "1A3A6B",
  blue:    "2E75B6",
  skyBlue: "4A9FD4",
  white:   "FFFFFF",
  light:   "F5F7FA",
  gray:    "64748B",
  lightGray: "E2E8F0",
  accent:  "00C4CC",
  green:   "70AD47",
  orange:  "ED7D31",
  dark:    "0F1F3D",
};

const makeShadow = () => ({
  type: "outer", color: "000000", opacity: 0.12,
  blur: 8, offset: 3, angle: 135
});

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title  = "자율주행 차량 탐지 성능 분석";
pres.author = "비전초보";


// ══════════════════════════════════════════════════
// 슬라이드 1 — 타이틀
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  // 왼쪽 세로 포인트 바
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: C.blue }, line: { type: "none" }
  });

  // 배경 그라데이션 느낌 원
  s.addShape(pres.shapes.OVAL, {
    x: 6.5, y: -1.5, w: 6, h: 6,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -0.5, w: 4, h: 4,
    fill: { color: C.blue, transparency: 70 }, line: { type: "none" }
  });

  // 태그
  s.addText("HYPER ROBOTICS  ·  비전초보  ·  COMPUTER VISION", {
    x: 0.5, y: 0.55, w: 9, h: 0.35,
    fontSize: 10, color: C.skyBlue, bold: false,
    charSpacing: 3, margin: 0
  });

  // 메인 타이틀
  s.addText("자율주행 차량 탐지", {
    x: 0.5, y: 1.2, w: 8.5, h: 0.95,
    fontSize: 44, color: C.white, bold: true, margin: 0
  });
  s.addText("성능 분석 보고서", {
    x: 0.5, y: 2.05, w: 8.5, h: 0.95,
    fontSize: 44, color: C.accent, bold: true, margin: 0
  });

  // 서브타이틀
  s.addText("데이터 양이 YOLOv8 탐지 성능에 미치는 영향", {
    x: 0.5, y: 3.1, w: 8, h: 0.45,
    fontSize: 16, color: "A0B4CC", margin: 0
  });

  // 하단 메타 정보
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.8, w: 10, h: 0.825,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("YOLOv8n  |  Waymo Open Dataset v1.4.3  |  2026", {
    x: 0.5, y: 4.85, w: 9, h: 0.5,
    fontSize: 12, color: "7FA8C9", margin: 0
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 2 — 목차
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  // 헤더 바
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("목  차", {
    x: 0.5, y: 0.1, w: 9, h: 0.75,
    fontSize: 28, color: C.white, bold: true, margin: 0
  });

  const items = [
    ["01", "프로젝트 개요",   "목표 및 배경"],
    ["02", "데이터셋",        "Waymo Open Dataset"],
    ["03", "실험 설계",       "4가지 데이터 크기 비교"],
    ["04", "실험 결과",       "mAP50 / Precision / Recall"],
    ["05", "결과 분석",       "데이터 증가 효과 해석"],
    ["06", "결론 및 향후 과제", "개선 방향 제시"],
  ];

  items.forEach(([num, title, sub], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.4 + col * 4.85;
    const y = 1.25 + row * 1.35;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.5, h: 1.15,
      fill: { color: C.white }, line: { type: "none" },
      shadow: makeShadow()
    });
    // 왼쪽 번호 바
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.55, h: 1.15,
      fill: { color: C.blue }, line: { type: "none" }
    });
    s.addText(num, {
      x, y: y + 0.28, w: 0.55, h: 0.5,
      fontSize: 15, color: C.white, bold: true, align: "center", margin: 0
    });
    s.addText(title, {
      x: x + 0.65, y: y + 0.12, w: 3.75, h: 0.42,
      fontSize: 14, color: C.navy, bold: true, margin: 0
    });
    s.addText(sub, {
      x: x + 0.65, y: y + 0.62, w: 3.75, h: 0.35,
      fontSize: 11, color: C.gray, margin: 0
    });
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 3 — 프로젝트 개요
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("01  프로젝트 개요", {
    x: 0.5, y: 0.12, w: 9, h: 0.72,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  // 목표 텍스트
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 9.2, h: 0.75,
    fill: { color: C.blue, transparency: 88 }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 0.06, h: 0.75,
    fill: { color: C.accent }, line: { type: "none" }
  });
  s.addText("Waymo 실제 도로 영상 + YOLOv8 으로 차량을 탐지하고, 학습 데이터 양이 성능에 미치는 영향을 정량 분석", {
    x: 0.6, y: 1.15, w: 8.8, h: 0.6,
    fontSize: 13.5, color: C.navy, margin: 0
  });

  // 핵심 지표 카드 3개
  const cards = [
    { num: "3회",    sub: "실험 횟수" },
    { num: "1,190장", sub: "최대 학습 이미지" },
    { num: "16.7%",  sub: "최고 mAP50" },
  ];
  cards.forEach(({ num, sub }, i) => {
    const x = 0.5 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.1, w: 2.85, h: 1.45,
      fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.1, w: 2.85, h: 0.1,
      fill: { color: C.blue }, line: { type: "none" }
    });
    s.addText(num, {
      x, y: 2.25, w: 2.85, h: 0.75,
      fontSize: 30, color: C.blue, bold: true, align: "center", margin: 0
    });
    s.addText(sub, {
      x, y: 3.05, w: 2.85, h: 0.4,
      fontSize: 12, color: C.gray, align: "center", margin: 0
    });
  });

  // 파이프라인
  s.addText("전체 파이프라인", {
    x: 0.5, y: 3.75, w: 4, h: 0.35,
    fontSize: 13, color: C.navy, bold: true, margin: 0
  });

  const steps = ["Waymo\n.tfrecord", "프레임\n추출", "YOLO\n변환", "학습 /\n검증", "성능\n평가"];
  steps.forEach((label, i) => {
    const x = 0.4 + i * 1.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.2, w: 1.5, h: 0.9,
      fill: { color: C.blue }, line: { type: "none" }, shadow: makeShadow()
    });
    s.addText(label, {
      x, y: 4.2, w: 1.5, h: 0.9,
      fontSize: 10.5, color: C.white, bold: true, align: "center", valign: "middle", margin: 0
    });
    if (i < steps.length - 1) {
      s.addText("→", {
        x: x + 1.5, y: 4.35, w: 0.35, h: 0.5,
        fontSize: 18, color: C.blue, align: "center", margin: 0
      });
    }
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 4 — 데이터셋
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("02  데이터셋", {
    x: 0.5, y: 0.12, w: 9, h: 0.72,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  // 왼쪽: Waymo 설명
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 4.5, h: 4.1,
    fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 4.5, h: 0.08,
    fill: { color: C.blue }, line: { type: "none" }
  });
  s.addText("Waymo Open Dataset v1.4.3", {
    x: 0.55, y: 1.25, w: 4.2, h: 0.45,
    fontSize: 14, color: C.navy, bold: true, margin: 0
  });

  const waymoInfo = [
    "Google 자율주행 팀 공개 데이터셋",
    "실제 도로 주행 영상 (전방 카메라)",
    "1920×1280 고해상도 이미지",
    "차량 · 보행자 · 자전거 라벨 포함",
    "training 6개 세그먼트 사용",
  ];
  s.addText(waymoInfo.map(t => ({ text: t, options: { bullet: true, breakLine: true } })).slice(0, -1)
    .concat([{ text: waymoInfo[waymoInfo.length - 1], options: { bullet: true } }]), {
    x: 0.6, y: 1.8, w: 4.1, h: 2.4,
    fontSize: 12.5, color: "333333", paraSpaceAfter: 6
  });

  // 오른쪽: 데이터 구성
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.1, w: 4.5, h: 4.1,
    fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.1, w: 4.5, h: 0.08,
    fill: { color: C.green }, line: { type: "none" }
  });
  s.addText("데이터 구성", {
    x: 5.25, y: 1.25, w: 4.2, h: 0.45,
    fontSize: 14, color: C.navy, bold: true, margin: 0
  });

  const tableRows = [
    [{ text: "구분", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "세그먼트", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "이미지 수", options: { bold: true, color: C.white, fill: { color: C.navy } } }],
    ["Training", "6개", "1,190장"],
    ["Validation", "1개 (고정)", "198장"],
    ["탐지 클래스", "vehicle", "1개"],
  ];
  s.addTable(tableRows, {
    x: 5.25, y: 1.85, w: 4.2, h: 1.9,
    fontSize: 12,
    border: { pt: 0.5, color: C.lightGray },
    colW: [1.5, 1.5, 1.2],
    fill: { color: "F8FAFC" }
  });

  s.addText("* 검증 세트는 모든 실험에서 동일하게 고정\n  → 공정한 성능 비교를 위해", {
    x: 5.25, y: 3.85, w: 4.2, h: 0.7,
    fontSize: 11, color: C.gray, italic: true, margin: 0
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 5 — 실험 설계
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("03  실험 설계", {
    x: 0.5, y: 0.12, w: 9, h: 0.72,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  // 공통 조건 카드
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 9.2, h: 1.5,
    fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.1, w: 0.06, h: 1.5,
    fill: { color: C.accent }, line: { type: "none" }
  });
  s.addText("공통 실험 조건 (모든 실험 동일)", {
    x: 0.6, y: 1.18, w: 8.8, h: 0.38,
    fontSize: 13, color: C.navy, bold: true, margin: 0
  });

  const conds = [
    ["모델", "YOLOv8n (nano)"],
    ["Epochs", "10 (고정)"],
    ["이미지 크기", "640×640"],
    ["Batch Size", "8"],
    ["하드웨어", "Apple M4 Pro CPU"],
    ["Optimizer", "Auto SGD"],
  ];
  conds.forEach(([k, v], i) => {
    const x = 0.65 + (i % 3) * 3.05;
    const y = 1.65 + Math.floor(i / 3) * 0.42;
    s.addText(`${k}:  `, { x, y, w: 1.0, h: 0.35, fontSize: 11.5, color: C.gray, margin: 0 });
    s.addText(v, { x: x + 0.9, y, w: 2.0, h: 0.35, fontSize: 11.5, color: C.navy, bold: true, margin: 0 });
  });

  // 실험 4개 카드
  s.addText("실험 구성 — 학습 데이터 수만 변경", {
    x: 0.5, y: 2.8, w: 6, h: 0.38,
    fontSize: 13, color: C.navy, bold: true, margin: 0
  });

  const exps = [
    { n: "Exp 1", size: "200장",  col: C.lightGray },
    { n: "Exp 2", size: "400장",  col: "D6E8F8" },
    { n: "Exp 3", size: "800장",  col: "AACFEE" },
    { n: "Exp 4", size: "1,190장", col: C.blue },
  ];
  exps.forEach(({ n, size, col }, i) => {
    const x = 0.4 + i * 2.35;
    const isLast = i === 3;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.3, w: 2.1, h: 1.75,
      fill: { color: col }, line: { type: "none" }, shadow: makeShadow()
    });
    s.addText(n, {
      x, y: 3.42, w: 2.1, h: 0.42,
      fontSize: 13, color: isLast ? C.white : C.navy, bold: true, align: "center", margin: 0
    });
    s.addText(size, {
      x, y: 3.92, w: 2.1, h: 0.65,
      fontSize: 26, color: isLast ? C.white : C.blue, bold: true, align: "center", margin: 0
    });
    s.addText("학습 이미지", {
      x, y: 4.65, w: 2.1, h: 0.3,
      fontSize: 10, color: isLast ? "C0D8F0" : C.gray, align: "center", margin: 0
    });
  });

  // 화살표
  s.addText("→  데이터 증가", {
    x: 0.4, y: 5.15, w: 9, h: 0.3,
    fontSize: 11, color: C.gray, align: "center", italic: true, margin: 0
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 6 — 실험 결과 (표)
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("04  실험 결과", {
    x: 0.5, y: 0.12, w: 9, h: 0.72,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  const header = [
    { text: "학습 데이터 수", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "Precision",    options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "Recall",       options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "mAP50",        options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "mAP50-95",     options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
  ];

  const dataRows = [
    ["200장",   "34.1%", "18.6%", "15.5%", "5.8%"],
    ["400장",   "34.1%", "20.0%", "16.7% ★", "6.3%"],
    ["800장",   "36.0%", "20.1%", "16.2%", "5.9%"],
  ];

  const tableData = [header, ...dataRows.map((row, ri) =>
    row.map((cell, ci) => ({
      text: cell,
      options: {
        align: "center",
        color: cell.includes("★") ? C.blue : "333333",
        bold: cell.includes("★"),
        fill: { color: ri % 2 === 0 ? "F8FAFC" : C.white }
      }
    }))
  )];

  s.addTable(tableData, {
    x: 0.8, y: 1.2, w: 8.4, h: 2.0,
    fontSize: 13.5,
    border: { pt: 0.5, color: C.lightGray },
    colW: [2.2, 1.8, 1.8, 1.8, 1.8],
    rowH: [0.5, 0.45, 0.45, 0.45],
  });

  // 인사이트 박스
  const insights = [
    { emoji: "📈", text: "400장에서 mAP50 최고치(16.7%) 달성" },
    { emoji: "🎯", text: "Precision은 세 실험 모두 34~36%로 안정적" },
    { emoji: "👁", text: "Recall은 데이터 증가와 함께 꾸준히 향상" },
  ];
  insights.forEach(({ emoji, text }, i) => {
    const x = 0.4 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.55, w: 2.9, h: 1.6,
      fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 3.55, w: 2.9, h: 0.07,
      fill: { color: C.blue }, line: { type: "none" }
    });
    s.addText(emoji, {
      x, y: 3.7, w: 2.9, h: 0.55,
      fontSize: 26, align: "center", margin: 0
    });
    s.addText(text, {
      x: x + 0.1, y: 4.32, w: 2.7, h: 0.7,
      fontSize: 11.5, color: C.navy, align: "center", margin: 0
    });
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 7 — 결과 분석 (차트)
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.0,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("05  결과 분석", {
    x: 0.5, y: 0.12, w: 9, h: 0.72,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  // 차트 2개
  s.addImage({ path: `${ASSETS}/chart_map.png`, x: 0.3, y: 1.1, w: 4.8, h: 2.8 });
  s.addImage({ path: `${ASSETS}/chart_pr.png`,  x: 5.1, y: 1.1, w: 4.6, h: 2.8 });

  // 분석 코멘트
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 4.05, w: 9.4, h: 1.25,
    fill: { color: C.white }, line: { type: "none" }, shadow: makeShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 4.05, w: 0.06, h: 1.25,
    fill: { color: C.accent }, line: { type: "none" }
  });
  s.addText([
    { text: "분석: ", options: { bold: true, color: C.navy } },
    { text: "200→400장 구간에서 성능이 가장 크게 향상(+1.2%p). 800장에서 소폭 하락은 유사 장면 반복으로 인한 과적합 가능성.\n", options: { color: "333333" } },
    { text: "Recall의 꾸준한 증가", options: { bold: true, color: C.navy } },
    { text: "는 데이터가 많을수록 놓치는 차량이 줄어든다는 것을 의미.", options: { color: "333333" } },
  ], {
    x: 0.5, y: 4.1, w: 9.0, h: 1.1,
    fontSize: 12, margin: 0
  });
}


// ══════════════════════════════════════════════════
// 슬라이드 8 — 결론
// ══════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.dark };

  // 왼쪽 포인트 바
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: C.accent }, line: { type: "none" }
  });

  s.addText("06  결론 및 향후 과제", {
    x: 0.5, y: 0.3, w: 9, h: 0.6,
    fontSize: 26, color: C.white, bold: true, margin: 0
  });

  // 결론 박스
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.05, w: 9.2, h: 0.9,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.05, w: 0.06, h: 0.9,
    fill: { color: C.accent }, line: { type: "none" }
  });
  s.addText("학습 데이터 양은 YOLOv8 차량 탐지 성능에 유의미한 영향을 미치며,\n소량 구간(200→400장)에서 데이터 추가 효과가 가장 크게 나타남.", {
    x: 0.6, y: 1.1, w: 8.8, h: 0.75,
    fontSize: 12.5, color: "D0E8FF", margin: 0
  });

  // 향후 과제
  s.addText("향후 개선 방향", {
    x: 0.5, y: 2.15, w: 4, h: 0.4,
    fontSize: 14, color: C.accent, bold: true, margin: 0
  });

  const futures = [
    "Epoch 확대 (10 → 100) 및 GPU 환경 재실험",
    "다양한 세그먼트 추가 (야간 / 우천 / 교외)",
    "차량 종류 세분화 (승용차 / 트럭 / 버스)",
    "아이폰 연동 실시간 탐지 데모 고도화",
    "별도 test 세트 구성 → 공정한 최종 평가",
  ];
  s.addText(
    futures.map((t, i) => ({
      text: t,
      options: { bullet: true, breakLine: i < futures.length - 1 }
    })),
    {
      x: 0.55, y: 2.65, w: 8.8, h: 2.5,
      fontSize: 13, color: "C0D8F0", paraSpaceAfter: 8
    }
  );

  // 하단
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.15, w: 10, h: 0.475,
    fill: { color: C.navy }, line: { type: "none" }
  });
  s.addText("HYPER Robotics  ·  비전초보  ·  YOLOv8n  ·  Waymo Open Dataset  ·  2026", {
    x: 0.3, y: 5.2, w: 9.4, h: 0.35,
    fontSize: 10.5, color: "7FA8C9", align: "center", margin: 0
  });
}


// ── 저장 ────────────────────────────────────────
pres.writeFile({ fileName: path.resolve(__dirname, "HYPER_최종결과보고서_비전초보.pptx") })
  .then(() => console.log("✅ 완료: report/HYPER_최종결과보고서_팀명.pptx"))
  .catch(e => { console.error("오류:", e); process.exit(1); });
