---
name: figure-prompt-eng
description: >
  Use this skill when the manuscript needs figures and the author must decide
  figure type (statistical / conceptual / illustrative / visual abstract) and
  generate prompts for parallel image generation with two role-based engines
  (English-strong ∥ Korean-text-strong; as-of examples: GPT-image-2, Nano
  Banana 2). Trigger when user says "figure 만들기", "그림 생성", "visual
  abstract", "프롬프트 작성", "GPT image", "Nano Banana", "figure prompt", or
  operates in Step 7 of sam-workshop pipeline. Do not use for statistical chart
  generation directly (use Code with matplotlib/R for Type S) or for figure
  legend writing (use humanize-en/ko). Input:
  paper_home/03_outline/outline.md + paper_home/04_draft/manuscript.md +
  (optional) data files for Type S. Output:
  paper_home/07_figures/{figure_plan.md, prompts/, candidates/, selected/,
  final/}. Pipeline position: sam-workshop Step 7 (figure brief = step 7
  option). Medical context: Korean medical infographics need an engine strong
  at Korean text rendering; English figures often better with English-strong
  engines; statistical figures deterministically generated via Code. Trigger keywords: figure, 그림,
  infographic, visual abstract, 그래프, schematic, GPT-image, Nano Banana,
  matplotlib, 도식.
---

# figure-prompt-eng (Step 7)

> Figure type 분기 → prompt 정제 → 병렬 생성 → 평가 → 선택의 풀 워크플로우. **"1트에 성공 어려움" 인식하고 병렬이 표준**.

## Figure type 4분류

| Type | 예 | 도구 (역할 기반) |
|---|---|---|
| **S (Statistical)** | bar/forest plot, KM curve, ROC, scatter | **Claude Code** (matplotlib/R) — image gen 부적합 |
| **C (Conceptual)** | 연구 design, 메커니즘 모식도, flowchart | 이미지 생성 엔진 2종 병렬 (영문 강함 ∥ 한글 강함) |
| **I (Illustrative)** | 해부 schematic, 병태생리 | 이미지 생성 엔진 2종 병렬 |
| **V (Visual Abstract)** | infographic, 한글/영문 visual abstract | **한글 텍스트 렌더링 강한 엔진 우선**, 타 엔진 비교 |

> 도구명은 영구 규칙이 아니라 **역할로 선택**한다. 작성 시점 예시(as of 2026-06): 영문·정밀 편집 = OpenAI GPT-image-2 / 한글 렌더링 = Google Nano Banana 2(gemini-3.1-flash-image). **실행 시점의 가용 최신 도구·저널 figure 정책을 확인**할 것.

## 모드

| 모드 | 시간 | 산출 |
|---|---|---|
| `workshop-mini` | 15분 | figure_plan(브리핑·캡션·프롬프트). 이미지 렌더링은 fallback 또는 homework |
| `standard` | 60분 | + iter 3회 prompt 다듬기 + 1–2 figure 병렬 생성 + 선택 |
| `deep-audit` | 120분 | + 다중 후보 비교 + 5차원 평가 ≥ 20/25 |

### v1.2 — Auto-Pilot fallback renderer (NEW)

워크숍 워크플로우 안에서 free-tier 이미지 생성기(Gemini Nano Banana 2 / GPT-image-2)가 가용하지 않거나, 한국어/영어 텍스트 렌더링이 깨질 때, **matplotlib으로 schematic figure를 직접 렌더링하는 fallback** 경로를 제공한다.

- **Auto-Pilot 모드(H1) 필수**: brief+caption만 산출하면 reference run이 figure 없이 끝난다. 따라서 H1 모드에서는 fallback renderer를 default로 호출.
- **인간 워크숍(H3) 선택**: step 7(Humanize & Package) 안에서는 brief+caption만, 이미지 렌더링은 step 7 이후 또는 homework로 미룸.
- **사용법** (함수 추가는 standard/deep 모드에서 — mini에서는 복사·실행까지만):
  ```bash
  # Claude가 OS 무관하게 복사 (Windows는 PowerShell Copy-Item)
  # 원본: ${CLAUDE_SKILL_DIR}/../_shared/scripts/figure_render_fallback.py
  # 대상: paper_home/07_figures/build_figures.py
  # 본인 figure 함수 추가 후
  python paper_home/07_figures/build_figures.py
  # → paper_home/07_figures/final/figure_<n>_<slug>.png (300 dpi)
  ```
- **헬퍼**: `_draw_box`, `_draw_arrow`, `_draw_diamond`, `_draw_dial`, `_draw_halo` 5개 primitive로 schematic 대부분 커버.
- **한계**: 통계 chart(Type S)는 본인 matplotlib 작성, 사진형 illustration(Type I)은 fallback 부적합 — 이 경우 image-gen LLM 또는 Inkscape로 후처리.

## 입력

- `paper_home/03_outline/outline.md` — 어디에 어떤 figure 필요?
- `paper_home/04_draft/manuscript.md` — 본문에서 figure 참조
- (Type S용) 본인 데이터 파일

## 절차

> **workshop-mini(15분) = 7.1 + 7.3.1까지만** (figure plan + 캡션 + prompt 작성). 7.2 Type S 렌더·7.3.2 이후 생성·평가·변환은 **standard 모드 또는 homework** — 모드 표와 동일.

### 7.1 Figure plan (5분, Claude Chat/Code 탭)

```
당신은 의학 figure designer입니다. 본 manuscript에 필요한 figure를 list화:

| # | 위치 | 목적 | Type | 우선순위 |
|---|---|---|---|---|
| 1 | Methods | 연구 design flow | C | 필수 |
| 2 | Results | 효과 비교 forest plot | S | 필수 |
| 3 | Discussion | 기전 도식 | I | 선택 |
| 4 | Visual Abstract | 전체 요약 | V | 선택 |
```

산출 → `paper_home/07_figures/figure_plan.md`

### 7.2 Type S 처리 (Code, 10분 — standard/homework)

```bash
# Claude Code에서 matplotlib/R script 즉석 작성·실행
# 예: forest plot
python << 'EOF'
import matplotlib.pyplot as plt
# ... data, axes, journal-spec DPI/font ...
plt.savefig("paper_home/07_figures/final/Fig2_forest.tif", dpi=300, format="tiff")
EOF
```

저널 spec (DPI 300/600, color mode RGB/CMYK, font Arial 7pt 등) 자동 적용.

### 7.3 Type C/I/V 병렬 생성 (prompt 정제는 mini 포함 10분 — 생성·평가는 standard/homework)

#### 7.3.1 Prompt 정제 (Claude)

```
당신은 medical figure prompt engineer입니다. 다음 의도를 영문 prompt로:

의도: "당뇨병 진단 후 SGLT2 억제제 vs DPP-4 억제제 처방 비교 시 심혈관 사건 발생 mechanism 도식"

Type 분기 자동 감지 (S/C/I/V).
한글 텍스트 포함 시 → 한글 렌더링 강한 엔진 우선 표시.

Prompt 양식:
- Subject: "..."
- Style: "clean medical diagram, white background, professional"
- Layout: "left to right flow, 3 stages"
- Colors: "blue/grey palette, color-blind safe"
- Text overlay: (한글 또는 영문)
- Avoid: "photorealistic skin, cartoon, watermark"

저널 spec 반영:
- Min DPI: ___
- Color mode: RGB/CMYK
- Font: ___ (text overlay 시)
```

#### 7.3.2 병렬 생성

| Engine (역할) | 사용 |
|---|---|
| 영문·정밀 편집 강한 엔진 | 동일 prompt |
| 한글 렌더링 강한 엔진 | 동일 prompt — 한글 텍스트 우선 |

(as-of 예시는 위 Type 표 참조 — 실행 시점 가용 도구 확인)

→ 결과 모두 `paper_home/07_figures/candidates/`에 저장:
- `Fig1_v1_engineA.png`
- `Fig1_v1_engineB.png`

#### 7.3.3 비교·평가 (vision 가능 LLM)

5차원 평가:

| 차원 | 척도 | 기준 |
|---|---|---|
| 1. Legibility | 1–5 | 텍스트/숫자 명확? |
| 2. Accuracy | 1–5 | 의학적 사실 맞음? |
| 3. Aesthetics | 1–5 | 학술 figure 느낌? |
| 4. Journal-fit | 1–5 | 저널 스타일 부합? |
| 5. Message clarity | 1–5 | 한 눈에 이해? |

종합 ≥ 20/25 → 통과. 미달 → prompt 재정제 후 재생성 (standard 3 iter / deep-audit max 5 iter).

#### 7.3.4 선택

승자 → `paper_home/07_figures/selected/Fig1.png`
패자 → candidates에 보존 (학습용)

### 7.4 Final 변환 (Code)

```bash
# 저널 규격 변환 (DPI, format, color mode)
python << 'EOF'
from PIL import Image
img = Image.open("paper_home/07_figures/selected/Fig1.png")
# ... DPI 300, TIFF, RGB→CMYK 등 ...
img.save("paper_home/07_figures/final/Fig1.tif", dpi=(300, 300), format="TIFF")
EOF
```

## Output 표준

### `figure_plan.md`
(위 표 형식)

### `prompts/Fig1_v1.md`
```
## Prompt
{영문 prompt 전문}

## Engine assignments (역할 기반)
- 영문·정밀 편집 엔진: yes
- 한글 렌더링 엔진: yes (한글 텍스트 포함)

## Iteration log
- v1: ...
- v2: prompt 정제 (Legibility ↑)
- ...
```

### `candidates/`
- 모든 생성 결과 보존, 파일명 = `Fig{N}_v{iter}_{engine}.{ext}`

### `selected/`
- 채택본, 본문 ref 가능한 형태

### `final/`
- 저널 규격 변환 후, 투고 패키지로 직행 가능

## HITL Event Emit

```json
{"ts":"...","step":7,"gate":"D_finish","event_type":"gate_pass","skill":"figure-prompt-eng","engine":"image-gen-parallel","category":"figure_generation","severity":1,"description":"Fig1 generated v2 iter, score 22/25, engineA won","time_to_fix_min":24}
```

(emit은 figure 산출 기록용 — Self-Gate D 종합 판정은 desk-reject-precheck가 담당)

## 결정적 vs LLM 분리

- **LLM**: prompt 정제, type 분기 결정, 5차원 평가
- **결정적**: file 변환 (DPI/format), 저널 spec 매칭, 파일 명명 규약

## Solo + Claude-only fallback

외부 이미지 생성 엔진 무료 한도 초과 또는 미사용:
1. **Type S**: Code로 직접 그림 — 백업 가능
2. **Type C/I**: Claude Code로 SVG 직접 작성 (간단 schematic)
3. **Type V (visual abstract)**: PowerPoint/Keynote에서 수동 작성 권고

## Floor (절대 위임 불가)

- **임상 데이터 시각화 정확도** — 본인 본문 수치와 figure 수치 일치 확인
- **약물 화학구조** — AI 생성 부정확 가능. 본인 PubChem 검증
- **해부학 정확도** — illustrative figure는 본인 의학 지식 검증

## Self-Gate D 체크리스트

- [ ] 모든 Type S figure data와 본문 수치 일치
- [ ] Type C/I/V figure 5차원 ≥ 20/25
- [ ] 저널 spec (DPI/format/color) 모두 충족
- [ ] Figure caption 본인 작성 (AI 시그니처 점검)
- [ ] candidates/ 보존 (사후 다른 figure에 학습 자산)

## 자주 발생하는 함정

1. **이미지 생성 엔진이 약물 화학구조 멋대로 그림** — 임상적 무의미. Type C/I 사용 시 화학구조는 ChemDraw 외부 권고
2. **한글 텍스트가 영문 중심 엔진에서 깨짐** — 한글 렌더링 강한 엔진 우선, 또는 영문으로 작성 후 후처리
3. **DPI 부족 (72dpi 등)** — 저널 desk reject. 반드시 Code로 변환 검증
4. **Figure 1trier 시도** — 1번에 성공 거의 없음. 병렬 + iter 표준 사고
5. **Figure caption AI 시그니처** — humanize-en/ko로 후처리

## 다음 단계

→ Step 7 Humanize & Package로 복귀 (figure brief는 step 7의 옵션) → Step 10 Wrap & Next. 렌더링 미완 figure는 homework.
