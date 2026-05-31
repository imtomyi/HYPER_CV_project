// HYPER 최종결과보고서_비전초보 — docx 생성 스크립트
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Header, Footer, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageNumber, LevelFormat, PageBreak, HeadingLevel,
  ExternalHyperlink
} = require('docx');
const fs = require('fs');
const path = require('path');

const ASSETS = path.join(__dirname, 'assets');
const OUT = path.join(__dirname, 'HYPER_최종결과보고서_비전초보.docx');

// ── 공통 스타일 ──────────────────────────────────────
const FONT_KO = '맑은 고딕';
const FONT_EN = 'Calibri';
const PAGE_W = 9360; // DXA (A4 기준, 1" 여백)
const COL1 = 2340;   // 왼쪽 레이블 컬럼
const COL2 = PAGE_W - COL1;

const bdr = (color = '4472C4', sz = 6) => ({
  style: BorderStyle.SINGLE, size: sz, color
});
const tblBorders = (color = '000000') => ({
  top:     { style: BorderStyle.SINGLE, size: 6, color },
  bottom:  { style: BorderStyle.SINGLE, size: 6, color },
  left:    { style: BorderStyle.SINGLE, size: 6, color },
  right:   { style: BorderStyle.SINGLE, size: 6, color },
  insideH: { style: BorderStyle.SINGLE, size: 6, color },
  insideV: { style: BorderStyle.SINGLE, size: 6, color },
});
const noBorders = () => ({
  top:     { style: BorderStyle.NIL },
  bottom:  { style: BorderStyle.NIL },
  left:    { style: BorderStyle.NIL },
  right:   { style: BorderStyle.NIL },
  insideH: { style: BorderStyle.NIL },
  insideV: { style: BorderStyle.NIL },
});

// 텍스트 실행
function r(text, opts = {}) {
  return new TextRun({
    text,
    font: FONT_KO,
    size: opts.size || 20,
    bold: opts.bold || false,
    color: opts.color,
    italics: opts.italics,
    underline: opts.underline ? {} : undefined,
  });
}

// 단락
function p(children, opts = {}) {
  const runs = typeof children === 'string'
    ? [r(children, opts)]
    : (Array.isArray(children) ? children : [children]);
  return new Paragraph({
    children: runs,
    spacing: { before: opts.before ?? 40, after: opts.after ?? 40 },
    alignment: opts.align,
    indent: opts.indent ? { left: opts.indent } : undefined,
  });
}

// 빈 단락
function emptyP() {
  return new Paragraph({ children: [], spacing: { before: 60, after: 60 } });
}

// 이미지 삽입
function imgRun(filename, w, h) {
  const ext = path.extname(filename).slice(1).toLowerCase();
  const data = fs.readFileSync(path.join(ASSETS, filename));
  return new ImageRun({
    type: ext === 'jpg' ? 'jpeg' : ext,
    data,
    transformation: { width: w, height: h },
    altText: { title: filename, description: filename, name: filename },
  });
}

// ── 테이블 헬퍼 ──────────────────────────────────────
// 헤더 행: 레이블(회색) + 설명
function headerRow(label, desc) {
  return new TableRow({
    children: [
      new TableCell({
        width: { size: COL1, type: WidthType.DXA },
        borders: tblBorders(),
        shading: { fill: 'F3F3F3', type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 150, right: 150 },
        verticalAlign: VerticalAlign.CENTER,
        children: [p(r(label, { bold: true, size: 20 }))],
      }),
      new TableCell({
        width: { size: COL2, type: WidthType.DXA },
        borders: tblBorders(),
        margins: { top: 120, bottom: 120, left: 150, right: 150 },
        children: [p(r(desc, { size: 20, color: '555555' }))],
      }),
    ],
  });
}

// 컨텐츠 행 (colspan=2)
function contentRow(children) {
  return new TableRow({
    children: [
      new TableCell({
        columnSpan: 2,
        borders: tblBorders(),
        margins: { top: 150, bottom: 150, left: 180, right: 180 },
        children,
      }),
    ],
  });
}

function sectionTable(label, desc, children) {
  return [
    new Table({
      width: { size: PAGE_W, type: WidthType.DXA },
      columnWidths: [COL1, COL2],
      rows: [headerRow(label, desc), contentRow(children)],
    }),
    emptyP(),
  ];
}

// ── 제목 스타일 ──────────────────────────────────────
function h1(text) {
  return new Paragraph({
    children: [r(text, { bold: true, size: 28 })],
    spacing: { before: 280, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '4472C4', space: 4 } },
  });
}

// ── 메인 빌더 ────────────────────────────────────────
const children = [];

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 1. 제목
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
children.push(
  new Paragraph({
    children: [r('HYPER 프로젝트 최종 결과보고서', { bold: true, size: 40 })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 100 },
  }),
  new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: '4472C4', space: 2 } },
    children: [],
    spacing: { before: 0, after: 200 },
  }),
);

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 2. 작성 안내 (원본 템플릿 그대로)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
children.push(
  p(r('[결과보고서 작성 안내]', { bold: true, size: 24 }), { before: 80, after: 60 }),
  p('본 결과보고서는 단순 제출용 문서가 아니라, HYPER 내부의 프로젝트 경험과 기술 자료를 축적하기 위한 아카이브입니다. 프로젝트를 진행하며 사용한 기술, 시스템 구조, 문제 해결 과정 등을 기록함으로써 이후 후배 부원들이 시행착오를 줄이고 더 높은 수준의 프로젝트에 도전할 수 있도록 하는 것을 목표로 합니다.', {}, ),
  p('또한 팀원 개인에게도 프로젝트를 다시 돌아보며 자신이 어떤 문제를 해결했고 무엇을 배웠는지 정리하는 과정이 될 수 있습니다. 가능한 한 실제 구현 과정과 고민, 실패 사례까지 포함하여 작성해주시기 바랍니다. 페이지 수는 제한 없습니다.'),
  emptyP(),
  p(r('[제출 안내]', { bold: true, size: 22 }), { before: 60, after: 40 }),
  ...['파일명: HYPER_최종결과보고서_비전초보',
      '제출 형식: PDF 변환 후 hyper.robotics.khu@gmail.com 으로 이메일 제출 권장',
      '기타: GitHub Repository는 가능한 한 Public으로 설정하여 HYPER 아카이브에 기여하는 것을 권장합니다.']
    .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),
  emptyP(),
);

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 3. 팀명 & 프로젝트 요약 테이블
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
children.push(
  new Table({
    width: { size: PAGE_W, type: WidthType.DXA },
    columnWidths: [COL1, COL2],
    rows: [
      // 팀명 행
      new TableRow({
        children: [
          new TableCell({
            columnSpan: 2,
            borders: tblBorders(),
            shading: { fill: 'EDF2FB', type: ShadingType.CLEAR },
            margins: { top: 140, bottom: 140, left: 180, right: 180 },
            children: [new Paragraph({
              children: [
                r('팀명:  ', { bold: true, size: 22 }),
                r('비전초보', { bold: true, size: 24, color: '1F3864' }),
                r('   |   소속: HYPER Robotics   |   연도: 2026', { size: 20, color: '555555' }),
              ],
            })],
          }),
        ],
      }),
      // 프로젝트 요약 헤더
      new TableRow({
        children: [
          new TableCell({
            width: { size: COL1, type: WidthType.DXA },
            borders: tblBorders(),
            shading: { fill: 'F3F3F3', type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 150, right: 150 },
            verticalAlign: VerticalAlign.CENTER,
            children: [p(r('프로젝트 요약', { bold: true, size: 20 }))],
          }),
          new TableCell({
            width: { size: COL2, type: WidthType.DXA },
            borders: tblBorders(),
            margins: { top: 120, bottom: 120, left: 150, right: 150 },
            children: [p(r('프로젝트 주제, 목표, 시나리오 등을 간략히 소개합니다.', { size: 20, color: '888888' }))],
          }),
        ],
      }),
      // 프로젝트 요약 내용
      new TableRow({
        children: [
          new TableCell({
            columnSpan: 2,
            borders: tblBorders(),
            margins: { top: 150, bottom: 150, left: 180, right: 180 },
            children: [
              p([
                r('주제: ', { bold: true }),
                r('학습 데이터 양이 YOLOv8n 차량 탐지 성능에 미치는 영향 분석'),
              ]),
              p([
                r('목표: ', { bold: true }),
                r('이론적 이해에서 실제 구현까지 — Waymo Open Dataset으로 YOLOv8n 모델을 학습하고, 데이터 양(200/400/800장) 변화에 따른 mAP50, Precision, Recall 변화를 정량 분석. 최종적으로 아이폰 카메라를 활용한 실시간 교통표지판 탐지 시연 완성.'),
              ]),
              p([
                r('결과: ', { bold: true }),
                r('최고 mAP50 16.7% (400장 학습), 실시간 탐지 37~50 FPS 달성'),
              ]),
              p([
                r('모델: YOLOv8n  |  데이터셋: Waymo Open Dataset v1.4.3  |  실험 횟수: 3회  |  하드웨어: Apple M4 Pro', { color: '444444' }),
              ], { before: 60, after: 20 }),
            ],
          }),
        ],
      }),
    ],
  }),
  emptyP(),
);

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 4. 조별 공통 항목 제목
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
children.push(h1('[조별 공통 항목]'));

// ─── 1. 개발 환경 ─────────────────────────────────
children.push(
  ...sectionTable(
    '1. 개발 환경',
    '프로젝트에 사용된 소프트웨어 및 하드웨어 환경을 명시합니다.',
    [
      p(r('■ 운영체제 및 버전', { bold: true }), { before: 60, after: 20 }),
      p(r('macOS (Apple M4 Pro MacBook)'), { indent: 360 }),

      p(r('■ 주요 소프트웨어', { bold: true }), { before: 80, after: 20 }),
      ...['Python 3.11',
          'ultralytics (YOLOv8n) — YOLO 모델 학습 및 추론',
          'OpenCV 4.x — 카메라 입력 및 이미지 처리',
          'Pillow (PIL) — 한글 라벨 렌더링 (OpenCV 미지원)',
          'PyObjC / AVFoundation — macOS Continuity Camera 제어',
          'NumPy — 이미지 배열 처리',
          'TensorFlow (tfrecord 파싱용)']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),

      p(r('■ 사용 하드웨어', { bold: true }), { before: 80, after: 20 }),
      ...['Apple M4 Pro MacBook — CPU 기반 학습 및 추론',
          'iPhone 16 (Continuity Camera, USB 연결) — 실시간 입력 카메라']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),

      p(r('■ 사용 센서', { bold: true }), { before: 80, after: 20 }),
      p(r('• iPhone 16 내장 카메라 (USB Continuity Camera)'), { before: 20, after: 20, indent: 360 }),

      p(r('■ 기타 개발 환경', { bold: true }), { before: 80, after: 20 }),
      ...['macOS Continuity Camera API — iPhone을 외부 웹캠으로 활용',
          'AVFoundation 카메라 열거 — OpenCV와 AVFoundation 인덱스 불일치 문제 직접 해결',
          'GPU 미사용 — M4 Pro CPU만으로 학습 (Epoch=10 제한)']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),
      emptyP(),
    ],
  ),
);

// ─── 2. 프로젝트 구조 ────────────────────────────
children.push(
  ...sectionTable(
    '2. 프로젝트 구조',
    '프로젝트의 전체 시스템 구조와 데이터 흐름을 설명합니다.',
    [
      p(r('■ 학습 파이프라인 (데이터 → 모델)', { bold: true }), { before: 60, after: 20 }),
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: Array(5).fill(Math.floor((PAGE_W - 360) / 5)),
        rows: [
          new TableRow({
            children: [
              'Waymo .tfrecord\n(원본 데이터)',
              '프레임 추출\n(FRONT 카메라)',
              'YOLO 변환\n(라벨 좌표 정규화)',
              '학습/검증 분리\n(80% / 20%)',
              'YOLOv8n 학습\n(Epochs=10)',
            ].map((text, i) => new TableCell({
              width: { size: Math.floor((PAGE_W - 360) / 5), type: WidthType.DXA },
              borders: tblBorders('4472C4'),
              shading: { fill: i % 2 === 0 ? 'EDF2FB' : 'FFFFFF', type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 80, right: 80 },
              children: [new Paragraph({
                children: text.split('\n').map((line, j) => new TextRun({
                  text: line,
                  font: FONT_KO,
                  size: 16,
                  bold: j === 0,
                  break: j > 0 ? 1 : undefined,
                })),
                alignment: AlignmentType.CENTER,
              })],
            })),
          }),
        ],
      }),
      emptyP(),

      p(r('■ 실시간 탐지 파이프라인', { bold: true }), { before: 60, after: 20 }),
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: Array(4).fill(Math.floor((PAGE_W - 360) / 4)),
        rows: [
          new TableRow({
            children: [
              'iPhone 16 (USB)\nContinuity Camera',
              'AVFoundation\n카메라 입력',
              'YOLOv8n 추론\n37~50 FPS',
              'PIL 한글 렌더링\n→ 화면 출력',
            ].map((text, i) => new TableCell({
              width: { size: Math.floor((PAGE_W - 360) / 4), type: WidthType.DXA },
              borders: tblBorders('2E8B57'),
              shading: { fill: i % 2 === 0 ? 'EDF7F0' : 'FFFFFF', type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 80, right: 80 },
              children: [new Paragraph({
                children: text.split('\n').map((line, j) => new TextRun({
                  text: line,
                  font: FONT_KO,
                  size: 16,
                  bold: j === 0,
                  break: j > 0 ? 1 : undefined,
                })),
                alignment: AlignmentType.CENTER,
              })],
            })),
          }),
        ],
      }),
      emptyP(),

      p(r('■ 실험 조건 (공통)', { bold: true }), { before: 60, after: 20 }),
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: [Math.floor((PAGE_W-360)/4), Math.floor((PAGE_W-360)/4),
                       Math.floor((PAGE_W-360)/4), Math.floor((PAGE_W-360)/4)],
        rows: [
          new TableRow({
            children: ['항목', '설정값', '항목', '설정값'].map((text, i) =>
              new TableCell({
                width: { size: Math.floor((PAGE_W-360)/4), type: WidthType.DXA },
                borders: tblBorders(),
                shading: { fill: 'F3F3F3', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 100, right: 100 },
                children: [p(r(text, { bold: true, size: 18 }))],
              })
            ),
          }),
          ...[
            ['모델', 'YOLOv8n', 'Epochs', '10'],
            ['이미지 크기', '640×640', 'Batch Size', '8'],
            ['Optimizer', 'Auto (SGD)', '하드웨어', 'Apple M4 Pro (CPU)'],
            ['탐지 클래스', 'vehicle (1개)', '검증 데이터', '198장 (고정)'],
          ].map(row => new TableRow({
            children: row.map((text, i) => new TableCell({
              width: { size: Math.floor((PAGE_W-360)/4), type: WidthType.DXA },
              borders: tblBorders(),
              shading: { fill: i % 2 === 0 ? 'F9F9F9' : 'FFFFFF', type: ShadingType.CLEAR },
              margins: { top: 70, bottom: 70, left: 100, right: 100 },
              children: [p(r(text, { size: 18 }))],
            })),
          })),
        ],
      }),
      emptyP(),
    ],
  ),
);

// ─── 3. 참고한 자료 ───────────────────────────────
children.push(
  ...sectionTable(
    '3. 참고한 자료 (선택)',
    '프로젝트 진행에 실질적인 도움을 준 문헌 및 링크를 기록합니다.',
    [
      p(r('■ 데이터셋', { bold: true }), { before: 60, after: 20 }),
      p(r('• Waymo Open Dataset v1.4.3 공식 사이트:'), { before: 20, after: 4, indent: 360 }),
      new Paragraph({
        children: [
          new ExternalHyperlink({
            link: 'https://waymo.com/open/',
            children: [new TextRun({ text: 'https://waymo.com/open/', style: 'Hyperlink', font: FONT_KO, size: 18 })],
          }),
        ],
        spacing: { before: 4, after: 20 },
        indent: { left: 540 },
      }),
      p(r('• Waymo Open Dataset GitHub (tfrecord 파싱):'), { before: 20, after: 4, indent: 360 }),
      new Paragraph({
        children: [
          new ExternalHyperlink({
            link: 'https://github.com/waymo-research/waymo-open-dataset',
            children: [new TextRun({ text: 'https://github.com/waymo-research/waymo-open-dataset', style: 'Hyperlink', font: FONT_KO, size: 18 })],
          }),
        ],
        spacing: { before: 4, after: 20 },
        indent: { left: 540 },
      }),

      p(r('■ 모델 및 라이브러리', { bold: true }), { before: 80, after: 20 }),
      p(r('• Ultralytics YOLOv8 공식 문서:'), { before: 20, after: 4, indent: 360 }),
      new Paragraph({
        children: [
          new ExternalHyperlink({
            link: 'https://docs.ultralytics.com/',
            children: [new TextRun({ text: 'https://docs.ultralytics.com/', style: 'Hyperlink', font: FONT_KO, size: 18 })],
          }),
        ],
        spacing: { before: 4, after: 20 },
        indent: { left: 540 },
      }),
      p(r('• PyObjC AVFoundation (카메라 제어):'), { before: 20, after: 4, indent: 360 }),
      new Paragraph({
        children: [
          new ExternalHyperlink({
            link: 'https://pypi.org/project/pyobjc-framework-AVFoundation/',
            children: [new TextRun({ text: 'https://pypi.org/project/pyobjc-framework-AVFoundation/', style: 'Hyperlink', font: FONT_KO, size: 18 })],
          }),
        ],
        spacing: { before: 4, after: 20 },
        indent: { left: 540 },
      }),

      p(r('■ 기타', { bold: true }), { before: 80, after: 20 }),
      ...['macOS Continuity Camera 공식 문서 (Apple Developer)',
          'OpenCV Python 공식 문서: https://docs.opencv.org/']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),
      emptyP(),
    ],
  ),
);

// ─── 4. 관련 링크 ────────────────────────────────
children.push(
  ...sectionTable(
    '4. 관련 링크',
    '소스코드 및 산출물 링크를 첨부합니다.',
    [
      p(r('■ GitHub Repository (필수)', { bold: true }), { before: 60, after: 20 }),
      p(r('• 링크: (별도 제출 예정 — Public Repository 권장)', { color: '888888' }), { indent: 360 }),

      p(r('■ 시연 영상 (선택)', { bold: true }), { before: 80, after: 20 }),
      ...['교통표지판_시연.mov — 아이폰 카메라로 실제 도로 교통표지판 실시간 탐지',
          '차량감지_시연.mov — 주행 중 차량 복수 동시 탐지']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),

      p(r('■ 발표 자료 (선택)', { bold: true }), { before: 80, after: 20 }),
      p(r('• presentation.html — HTML 슬라이드 (로컬 실행)'), { before: 20, after: 20, indent: 360 }),
      emptyP(),
    ],
  ),
);

// ─── 5. 최종 결과물 ───────────────────────────────
children.push(
  ...sectionTable(
    '5. 최종 결과물',
    '구현된 프로젝트의 주요 기능과 시연 결과를 종합합니다.',
    [
      // 5-1. 실험 결과 표
      p(r('■ 실험 결과 (정량 지표)', { bold: true }), { before: 60, after: 20 }),
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: [1500, 900, 1300, 1100, 1400, 1460],
        rows: [
          new TableRow({
            children: ['학습 데이터 수', 'Epochs', 'Precision', 'Recall', 'mAP50', 'mAP50-95'].map(h =>
              new TableCell({
                width: { size: 0, type: WidthType.AUTO },
                borders: tblBorders(),
                shading: { fill: '1F3864', type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 100, right: 100 },
                children: [new Paragraph({
                  children: [new TextRun({ text: h, font: FONT_KO, size: 18, bold: true, color: 'FFFFFF' })],
                  alignment: AlignmentType.CENTER,
                })],
              })
            ),
          }),
          ...([
            ['200장', '10', '34.1%', '18.6%', '15.5%', '5.8%'],
            ['400장', '10', '34.1%', '20.0%', '16.7% ★', '6.3%'],
            ['800장', '10', '36.0%', '20.1%', '16.2%', '5.9%'],
          ].map((row, ri) => new TableRow({
            children: row.map((text, ci) => new TableCell({
              width: { size: 0, type: WidthType.AUTO },
              borders: tblBorders(),
              shading: { fill: (ri === 1 && ci >= 4) ? 'EDF7F0' : (ri % 2 === 0 ? 'F9F9F9' : 'FFFFFF'), type: ShadingType.CLEAR },
              margins: { top: 70, bottom: 70, left: 100, right: 100 },
              children: [new Paragraph({
                children: [new TextRun({ text, font: FONT_KO, size: 18, bold: ri === 1 && ci >= 4, color: ri === 1 && ci >= 4 ? '1F6B30' : '000000' })],
                alignment: AlignmentType.CENTER,
              })],
            })),
          }))),
        ],
      }),
      emptyP(),

      // 5-2. 성능 그래프
      p(r('■ 성능 변화 그래프', { bold: true }), { before: 60, after: 20 }),
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: [Math.floor((PAGE_W-360)/2), Math.ceil((PAGE_W-360)/2)],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                width: { size: Math.floor((PAGE_W-360)/2), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 60, bottom: 60, left: 60, right: 60 },
                children: [
                  new Paragraph({ children: [imgRun('chart_map.png', 280, 158)], alignment: AlignmentType.CENTER }),
                  p(r('mAP50 변화 (데이터 양별)', { size: 16, color: '555555' }), { align: AlignmentType.CENTER }),
                ],
              }),
              new TableCell({
                width: { size: Math.ceil((PAGE_W-360)/2), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 60, bottom: 60, left: 60, right: 60 },
                children: [
                  new Paragraph({ children: [imgRun('chart_pr.png', 280, 158)], alignment: AlignmentType.CENTER }),
                  p(r('Precision / Recall 변화', { size: 16, color: '555555' }), { align: AlignmentType.CENTER }),
                ],
              }),
            ],
          }),
        ],
      }),
      emptyP(),

      // 5-3. 시연 결과
      p(r('■ 실시간 탐지 시연 결과 (iPhone 16 + Continuity Camera)', { bold: true }), { before: 60, after: 20 }),
      p(r('Apple M4 Pro MacBook · iPhone 16 (USB) · YOLOv8n · 37~50 FPS 실시간 추론', { size: 18, color: '444444' }), { before: 10, after: 20 }),

      // 데모 사진 레이아웃: demo_2 (좌 large), demo_3 / demo_5 (우 위아래)
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: [Math.floor((PAGE_W-360)*0.55), Math.ceil((PAGE_W-360)*0.45)],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                width: { size: Math.floor((PAGE_W-360)*0.55), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 40, bottom: 40, left: 40, right: 40 },
                children: [
                  new Paragraph({ children: [imgRun('demo_2.png', 220, 304)], alignment: AlignmentType.CENTER }),
                  p(r('2개 동시 탐지 (신뢰도 74% / 52%) ★', { size: 16, color: '1F3864' }), { align: AlignmentType.CENTER }),
                ],
              }),
              new TableCell({
                width: { size: Math.ceil((PAGE_W-360)*0.45), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 40, bottom: 40, left: 40, right: 40 },
                children: [
                  new Paragraph({ children: [imgRun('demo_3.png', 190, 226)], alignment: AlignmentType.CENTER }),
                  p(r('진입금지 표지판 탐지 46%', { size: 16, color: '444444' }), { align: AlignmentType.CENTER, before: 20, after: 30 }),
                  new Paragraph({ children: [imgRun('demo_5.png', 190, 103)], alignment: AlignmentType.CENTER }),
                  p(r('차량 복수 탐지 (42~53%)', { size: 16, color: '444444' }), { align: AlignmentType.CENTER }),
                ],
              }),
            ],
          }),
        ],
      }),
      emptyP(),
      // 추가 시연 사진
      new Table({
        width: { size: PAGE_W - 360, type: WidthType.DXA },
        columnWidths: [Math.floor((PAGE_W-360)/2), Math.ceil((PAGE_W-360)/2)],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                width: { size: Math.floor((PAGE_W-360)/2), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 40, bottom: 40, left: 40, right: 40 },
                children: [
                  new Paragraph({ children: [imgRun('demo_1.png', 230, 149)], alignment: AlignmentType.CENTER }),
                  p(r('차량 내부 촬영 — 탐지 51%', { size: 16, color: '444444' }), { align: AlignmentType.CENTER }),
                ],
              }),
              new TableCell({
                width: { size: Math.ceil((PAGE_W-360)/2), type: WidthType.DXA },
                borders: noBorders(),
                margins: { top: 40, bottom: 40, left: 40, right: 40 },
                children: [
                  new Paragraph({ children: [imgRun('demo_4.png', 230, 129)], alignment: AlignmentType.CENTER }),
                  p(r('실제 도로 촬영 장면', { size: 16, color: '444444' }), { align: AlignmentType.CENTER }),
                ],
              }),
            ],
          }),
        ],
      }),
      emptyP(),

      // 5-4. 요약
      p(r('■ 프로젝트 요약 및 성공 여부', { bold: true }), { before: 60, after: 20 }),
      ...['학습 데이터 양(200→400장)에서 mAP50이 가장 크게 향상 (15.5% → 16.7%)',
          '800장에서 소폭 하락 → 데이터 다양성 없이 유사 장면만 추가 시 과적합 가능성 시사',
          'Precision(34~36%) 안정적, Recall(18.6→20.1%) 지속 향상 — 데이터 증가 효과 확인',
          '아이폰 Continuity Camera를 이용한 37~50 FPS 실시간 교통표지판 탐지 시연 성공',
          '한계: 10 epoch 제한, GPU 미사용, 단일 클래스, Waymo 미국 데이터 → 한국 표지판 인식률 저조']
        .map(t => p(r('• ' + t), { before: 20, after: 20, indent: 360 })),
      emptyP(),
    ],
  ),
);

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 5. 인원별 개별 작성 항목
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
children.push(
  new Paragraph({ children: [new PageBreak()] }),
  h1('[인원별 개별 작성 항목]'),
  p(r('※ 팀원 1인당 1페이지 작성 (최대 4명). 아래 양식을 팀원 수만큼 복사하여 각자 작성하세요.', { size: 18, color: '666666' }), { before: 40, after: 60 }),
);

// 팀원 섹션 생성 (팀원 수 불명이므로 1개 작성, 나머지는 플레이스홀더 포함)
function memberSection(idx, exName) {
  return [
    new Table({
      width: { size: PAGE_W, type: WidthType.DXA },
      columnWidths: [PAGE_W],
      rows: [
        new TableRow({
          children: [
            new TableCell({
              columnSpan: 1,
              borders: tblBorders(),
              shading: { fill: 'EDF2FB', type: ShadingType.CLEAR },
              margins: { top: 120, bottom: 120, left: 180, right: 180 },
              children: [p(r(`작성자: ${exName}`, { bold: true, size: 22 }))],
            }),
          ],
        }),
      ],
    }),
    new Table({
      width: { size: PAGE_W, type: WidthType.DXA },
      columnWidths: [COL1, COL2],
      rows: [
        headerRow(
          '6. 배운 점',
          '프로젝트 과정에서 새롭게 학습한 내용과 경험을 서술합니다.',
        ),
        contentRow([
          p(r('■ 새롭게 익힌 프레임워크/기술', { bold: true }), { before: 40, after: 20 }),
          ...['YOLOv8 모델 학습 및 추론 파이프라인 전체 흐름 이해',
              'Waymo Open Dataset tfrecord 파싱 및 YOLO 포맷 변환',
              'OpenCV + Pillow 조합으로 한글 라벨 렌더링 문제 해결',
              'macOS AVFoundation / Continuity Camera API 활용법',
              'mAP50, Precision, Recall 등 객체 탐지 평가 지표 실전 적용']
            .map(t => p(r('• ' + t), { before: 16, after: 16, indent: 360 })),
          p(r('■ 실제 구현 과정의 문제 해결', { bold: true }), { before: 60, after: 20 }),
          ...['iPhone(AVFoundation) 인덱스와 OpenCV VideoCapture 인덱스 불일치 문제 직접 디버깅',
              '카메라 입력에서 검은 프레임 처리 로직 설계',
              'Apple M4 CPU 전용 학습 환경에서 메모리·속도 최적화 경험']
            .map(t => p(r('• ' + t), { before: 16, after: 16, indent: 360 })),
          emptyP(),
        ]),
        headerRow(
          '7. 아쉬운 점 및 발전 방향',
          '한계점과 향후 개선 가능성을 객관적으로 분석합니다.',
        ),
        contentRow([
          p(r('■ 한계점', { bold: true }), { before: 40, after: 20 }),
          ...['에폭(10) 제한 및 GPU 미사용 → 수치 자체가 낮은 편',
              '단일 클래스(vehicle) 실험 → 다중 클래스 일반화 부족',
              '별도 test 세트 미구성 → 공정한 최종 평가 불가',
              'Waymo 미국 데이터 기반 학습 → 한국 교통표지판 인식률 저조']
            .map(t => p(r('• ' + t), { before: 16, after: 16, indent: 360 })),
          p(r('■ 향후 개선 방향', { bold: true }), { before: 60, after: 20 }),
          ...['학습 epoch 확대 (10 → 50~100) 및 GPU 환경 재실험',
              'Waymo 세그먼트 추가 확보 — 야간, 우천, 다양한 도로 환경 데이터 확충',
              '차량 종류 세분화 (승용차/트럭/버스/오토바이) 멀티클래스 확장',
              '한국 도로 환경 데이터 수집 → 한국 교통표지판 탐지 성능 개선',
              '별도 test 세트 구성으로 공정한 최종 성능 평가']
            .map(t => p(r('• ' + t), { before: 16, after: 16, indent: 360 })),
          emptyP(),
        ]),
      ],
    }),
    emptyP(),
    emptyP(),
  ];
}

// 팀원 플레이스홀더 — 이름/학번은 팀원이 직접 채워야 함
children.push(...memberSection(1, '[이름 / 학번] — 팀원이 직접 작성하세요'));

// ── 푸터용 단락 ──────────────────────────────────
children.push(
  new Paragraph({
    children: [],
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 4 } },
    spacing: { before: 240, after: 40 },
  }),
  new Paragraph({
    children: [r('HYPER Robotics · 비전초보 · 2026  |  Model: YOLOv8n  |  Dataset: Waymo Open Dataset v1.4.3', { size: 16, color: '888888' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 20, after: 20 },
  }),
);

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 문서 생성
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT_KO, size: 20 } },
    },
    paragraphStyles: [
      {
        id: 'Hyperlink', name: 'Hyperlink', basedOn: 'Normal',
        run: { color: '0563C1', underline: {}, font: FONT_KO },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 1000, right: 1000, bottom: 1000, left: 1000 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [
            r('HYPER 프로젝트 최종 결과보고서 — 비전초보', { size: 16, color: '888888' }),
          ],
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 2 } },
          spacing: { before: 0, after: 60 },
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            r('비전초보 | HYPER Robotics  ', { size: 16, color: '888888' }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT_KO, size: 16, color: '888888' }),
            r(' / ', { size: 16, color: '888888' }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT_KO, size: 16, color: '888888' }),
          ],
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 2 } },
          spacing: { before: 60, after: 0 },
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('✓ 완료:', OUT);
}).catch(err => {
  console.error('오류:', err);
  process.exit(1);
});
