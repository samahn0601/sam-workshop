---
name: exam-item-builder
description: >
  Use this skill to generate medical exam items (multiple choice questions,
  short-answer questions) from the user's lecture slides or completed
  manuscript, with NBME-style item-flaw checking, Bloom/Miller-level tagging,
  rationales for each distractor, and source/guideline linkage. Trigger when
  user says "시험문제 생성", "exam questions", "MCQ 만들어줘", "문항 만들기",
  "강의 시험문제", "OSCE", "USMLE 스타일", "KMLE 스타일", "Bloom level",
  "rationale", or operates near workshop wrap or after Step 8 manuscript draft.
  Do not use for paper drafting (use story-design or humanize-en/ko) or
  reference verification (use verify-reference-essential). Input:
  paper_home/00_intake/lecture_slides.pdf (또는 본 manuscript) + (선택) learning
  objectives. Output: paper_home/exam_items/{exam_items.jsonl, exam_items.md,
  item_flaw_report.md}. Pipeline position: parallel during lunch break + Step 8
  wrap. Medical context: NBME 'Constructing Written Test Questions for the
  Basic and Clinical Sciences' item-writing principles, Bloom's taxonomy,
  Miller's pyramid (knows / knows how / shows how / does), USMLE/KMLE
  clinical-vignette style. Trigger keywords: 시험문제, MCQ, exam items, item
  writing, NBME, Bloom, Miller, distractor, rationale, 객관식, 단답형, OSCE,
  EMQ, USMLE, KMLE.
---

# exam-item-builder (Tier 1 — workshop deliverable)

> 의대 교수의 워크숍 두 번째 deliverable: **20–30 시험문제** (강의자료 기반 또는 작성한 manuscript 기반). NBME 표준 item-writing 원칙 + Bloom/Miller 태깅 + flaw check.

## 모드

| 모드 | 시간 | 산출 |
|---|---|---|
| `workshop-mini` | 25분 | 8–12 문항 + flaw check |
| `standard` | 45분 | 20–30 문항 + 정답 해설 풀버전 |
| `deep-audit` | 90분 | + Beta-test simulation (예상 정답률 추정) |

워크숍에서는 **점심 백그라운드 발사 + Bonus choice block(15:25–15:45)에서 검토** 운영. 점심 직전 발사해 백그라운드로 문항을 생성하고, 오후 Bonus 블록에서 결과를 검토한다. workshop-mini(8–12 문항)는 이 슬롯에서 검토 가능, standard(20–30 문항)는 사후 자가 검토 병행. (시간표 SSOT: `workshop/TIMETABLE.md`)

## 입력

- `paper_home/00_intake/lecture_slides.pdf` (또는 .pptx) — 1차 source
- 또는 `paper_home/04_draft/manuscript.md` (본 워크숍 작성 논문) — manuscript-based
- (선택) learning objectives 텍스트 — 본인 입력
- **`paper_home/.sam/paper_profile.json`의 `target_audience_language`** (v1.2 NEW) — 산출 언어 결정. 없으면 `preferred_language` fallback. 한국 의대 청중에게는 영문 manuscript여도 한국어 문항집을 default로 산출.

### 산출 언어 결정 규칙 (v1.2)

```
audience_lang = paper_profile.target_audience_language
              or paper_profile.preferred_language
              or "en"

if audience_lang == "ko":
    primary  → exam_items_ko.md (KMLE/NBME 혼합 스타일, 한국어 stem·보기·해설)
    secondary → exam_items.md   (영문, KJME/JEEHP 이중언어 부록 대비)
elif audience_lang == "en":
    primary  → exam_items.md
    secondary → exam_items_ko.md (선택, 본인 요청 시)
else:
    primary  → exam_items_<lang>.md (해당 언어)
    secondary → exam_items.md
```

**v1.1 reference run에서 확인된 회귀**: 영문 manuscript에 대해 영문 문항집만 산출되어 한국 의대 청중 워크숍에서 재번역이 필요했음. v1.2는 audience_lang을 먼저 검사하여 이를 방지.

## 절차 (workshop-mini, 25분)

### 1단계 (5분) — Learning Objective 추출

PDF/PPTX/manuscript에서 LO 자동 추출 (또는 본인 입력):

```
당신은 의학교육 전문가입니다. 첨부 자료에서 학습 목표(LO) 8–12개를 추출하세요.

각 LO에:
- LO ID (LO-01, LO-02, ...)
- 1문장 LO statement (Bloom verb 사용: identify, explain, analyze, apply, evaluate, ...)
- Bloom level (Remember / Understand / Apply / Analyze / Evaluate / Create)
- Miller level (Knows / Knows How / Shows How / Does)
- domain (basic science / clinical knowledge / clinical skill / professionalism)

만약 LO가 자료에 명시되어 있으면 그대로 사용. 없으면 자료 내용에서 합리적 추출.
```

산출 → `paper_home/exam_items/learning_objectives{,_ko,_<lang>}.md`
(v1.2: audience_lang에 따라 파일명 suffix 결정)

### 2단계 (15분) — MCQ 생성 (audience_lang 분기)

각 LO당 1–2문항 (총 8–12문항, mini 기준). `audience_lang == "ko"`인 경우 stem·보기·해설을 한국어로, NBME 원칙에 KMLE 스타일을 결합:

```
당신은 NBME 표준 item-writer입니다. 다음 LO를 평가하는 single-best-answer MCQ를
USMLE Step / KMLE 스타일로 작성하세요.

NBME 원칙 (절대 준수):
1. Stem은 clinical vignette (환자 증례)으로 시작 — basic science도 임상 맥락
2. Stem은 자족적 (lead-in 한 문장으로 답이 결정 가능)
3. Single-best-answer — 5개 옵션 중 1개만 명백히 정답
4. Distractors는 모두 그럴듯해야 함 (homogeneous, 같은 카테고리)
5. 모두 비슷한 길이 (정답이 길지 않게)
6. "All of the above", "None of the above" 금지
7. 부정형 stem ("which is NOT") 가급적 회피
8. 문법적 단서 금지 (a/an 등으로 정답 노출)
9. 절대적 표현 금지 (always, never)
10. 단순 암기형 회피 — 추론 단계 1개 이상

각 문항에:
- item_id
- LO link (LO-N)
- Bloom level
- Miller level
- stem (clinical vignette)
- options A–E (single best answer)
- correct_answer (A–E)
- rationale_correct (왜 정답인가, 1–2문장)
- rationale_distractors: A: ..., B: ..., ... (각 오답이 왜 틀렸는가)
- source: PMID 또는 가이드라인 (Manuscript 기반이면 본문 위치)
- difficulty_estimate: easy / medium / hard
- estimated_correct_pct: 학생 예상 정답률 — **휴리스틱**(40–80%; 총괄평가 권장대는 60–85%, 40–60%는 고난도/형성평가로 태깅. 실제 난이도·변별도는 pilot 후 실측으로 대체)
```

산출 → `paper_home/exam_items/exam_items.jsonl`

### 3단계 (5분) — Item flaw check

```
당신은 medical educator입니다. 위 exam_items.jsonl의 모든 문항을
NBME flaw checklist로 점검:

Critical flaws (반드시 수정):
- **unfocused stem — "cover the options" 위반** (선택지를 가리고 발문만 읽어도 답을 낼 수 있어야 함; 불가하면 재작성)
- ambiguous stem (정답 결정 불가)
- multiple correct answers
- "all of the above" / "none of the above"
- 정답이 옵션 중 가장 김 (>50% 길이 차이)
- 문법적 단서 (a/an으로 노출, 또는 plural-singular mismatch)
- 임상적 부정확

Major flaws (개선 권고):
- **test-wiseness cue** (정답 단서: stem 단어가 정답에 반복[clang], 절대어/빈도어 패턴, 선택지 간 포괄 관계)
- 부정형 stem (NOT, EXCEPT)
- 절대적 표현 (always, never)
- 단순 암기형 (Bloom Remember만)
- distractors 비균질 (서로 다른 카테고리)
- vignette 너무 짧음 (clinical context 부족)

Minor flaws (선택):
- distractor 1–2개가 약함
- rationale 길이 불균등

각 문항에 flaw flag list + severity. 종합:
- Critical 0건 → Pass
- Critical ≥1 → 본인 수정 필수
```

산출 → `paper_home/exam_items/item_flaw_report.md`

## Output 표준

### `exam_items.jsonl` (1줄 = 1문항)

```json
{
  "item_id": "Q01",
  "lo_link": "LO-03",
  "bloom_level": "Apply",
  "miller_level": "Knows How",
  "domain": "clinical_knowledge",
  "stem": "A 65-year-old man with type 2 diabetes (HbA1c 8.5%) and chronic kidney disease (eGFR 45 mL/min/1.73m²) presents for follow-up. He is currently taking metformin 1000 mg twice daily. Which of the following antidiabetic agents is MOST appropriate to add to optimize glycemic control while providing cardiorenal benefit?",
  "options": {
    "A": "Glimepiride",
    "B": "Empagliflozin",
    "C": "Pioglitazone",
    "D": "Sitagliptin",
    "E": "Insulin glargine"
  },
  "correct_answer": "B",
  "rationale_correct": "SGLT2 inhibitors (empagliflozin) are recommended in T2DM with CKD (eGFR ≥20–25 mL/min/1.73m²) for both glycemic control and cardiorenal protection (KDIGO 2024, ADA Standards of Care 2025).",
  "rationale_distractors": {
    "A": "Sulfonylureas increase hypoglycemia risk and lack cardiorenal benefit",
    "C": "Pioglitazone causes fluid retention, contraindicated in advanced CKD with HF risk",
    "D": "DPP-4 inhibitors (sitagliptin) are glycemia-neutral but lack cardiorenal benefit",
    "E": "Insulin is effective but not first-add when SGLT2i is appropriate"
  },
  "source": "ADA Standards of Care 2025; KDIGO 2024 Diabetes in CKD",
  "difficulty_estimate": "medium",
  "estimated_correct_pct": 65
}
```

### `exam_items.md` (인쇄/공유용)

```markdown
# Exam Items — {date}

## Q01 (Apply / Knows How / clinical_knowledge)
65세 남성, 제2형 당뇨, ...

A. Glimepiride
B. Empagliflozin
C. Pioglitazone
D. Sitagliptin
E. Insulin glargine

**정답: B**

해설: SGLT2 억제제 (empagliflozin)는 ...

(오답)
- A. Sulfonylureas는 ...
- C. Pioglitazone은 ...

출처: ADA Standards of Care 2025
```

### `item_flaw_report.md`

```markdown
# Item Flaw Report

| item_id | flaws | severity | 권고 |
|---|---|---|---|
| Q01 | (없음) | Pass | 그대로 |
| Q03 | distractor C가 약함 | Minor | 선택 수정 |
| Q07 | "all of the above" | Critical | 반드시 수정 |
```

## HITL Event Emit

```json
{"ts":"...","step":"wrap","event_type":"gate_pass","skill":"exam-item-builder","engine":"claude","category":"exam_items","severity":1,"description":"12 items generated, 0 critical flaws, Bloom levels: 3 Remember / 5 Apply / 4 Analyze","time_to_fix_min":25}
```

## 결정적 vs LLM 분리

- **LLM**: 모든 단계 (LO 추출, MCQ 생성, flaw check, rationale)
- **결정적**: NBME flaw checklist 패턴 매칭 (regex로 "all of the above" / "NOT" 등 검출)

## Solo + Claude-only

기본 Claude. 외부 도구 불필요.

## Floor (절대 위임 불가)

- **임상 정확성** — 본인 분야 문항은 본인이 정답·rationale 검증 필수
- **약물 용량 / 금기** — 모든 약물 관련 문항 본인 검증
- **가이드라인 인용 정확성** — KDIGO/ADA/ESC 등 인용 시 본인 최신 버전 확인

## Self-Gate 체크리스트

- [ ] Critical flaw 0건
- [ ] 약물/용량/금기 임상 정확성 확인
- [ ] 가이드라인 인용 최신 확인
- [ ] Bloom level 분포 (Remember 30% 이하 권장)
- [ ] Miller level Shows How 이상이 50%+ 권장 (실제 진료 능력)

## 자주 발생하는 함정

1. **단순 암기형 과다** — Bloom Remember만 → 학습 효과 ↓. Apply/Analyze 50%+ 권장
2. **Distractor 비균질** — A는 약물, B는 진단, C는 검사 → 그럴듯하지 않음. 같은 카테고리
3. **정답이 가장 김** — 학생이 정답 추측 가능. 모든 옵션 비슷한 길이
4. **부정형 stem** — "Which is NOT" — 인지 부담 ↑, 회피
5. **임상 vignette 부족** — basic science도 임상 시나리오로 wrap

## Workshop 운영

**점심 시작 직전 (12:00 직후)**: 강의자료 PDF 업로드 → 1단계 LO 추출 발화 → 백그라운드

**점심 후 (13:00)**: LO 검토 → 2–3단계 발화 → Step 4 Draft와 병행

**Step 8 wrap (15:30 경)**: 최종 검토 + flaw 수정

→ 총 점유 시간 25–30분, 워크숍 main flow에 영향 최소화

## 다음 단계

→ 본인 시험에 즉시 사용 가능. 사후 다른 강의 자료에 동일 skill 재사용.
