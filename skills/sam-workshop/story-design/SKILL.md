---
name: story-design
description: >
  Use this skill when the manuscript needs a one-sentence message, a logical
  IMRaD/section storyline, and an outline that maps each claim to evidence.
  Trigger when the user says "outline 짜줘", "스토리 설계", "논문 구조",
  "어떻게 풀어갈까", "narrative arc", "outline draft", "IMRaD 구조", or operates
  in Step 3 Outline of the sam-workshop pipeline. Do not use for figure planning
  (use figure-prompt-eng) or reference verification (use verify-reference-essential).
  Input: paper_home/01_design/{article_type.md, journal_shortlist.md} +
  paper_home/02_research/{claim_bank.jsonl, evidence_table.md} (+
  deep_research.md as backup source). Output:
  paper_home/03_outline/{story_1pager.md, outline.md, evidence_map.md}.
  Pipeline position: sam-workshop Step 3 / Self-Gate A. Medical context: ICMJE
  IMRaD structure, journal-specific section requirements, claim-evidence
  ledger discipline. Trigger keywords: outline, 스토리, 구조, IMRaD, narrative,
  논문 흐름, key message, one-sentence message, claim evidence, gap statement.
---

# story-design (Step 3)

> Deep Research + journal specs를 받아 **논문의 골격 + 핵심 메시지 + claim-evidence 매핑**을 산출. Step 4 Draft 진입 전 마지막 디자인 단계.

## 모드

| 모드 | 시간 | 산출 |
|---|---|---|
| `workshop-mini` | 25분 | one-sentence message + outline + evidence map |
| `standard` | 50분 | + alternative narrative arcs 2개 비교 |
| `deep-audit` | 90분 | + section-by-section claim ledger 채움 |

## 입력

- `paper_home/01_design/article_type.md` — 잠정 article type
- `paper_home/01_design/journal_shortlist.md` — target 저널 spec (**Scope fit·Fit verdict·Reject risk 칼럼 반영** — Strong fit 1순위, 없으면 Reject risk 낮은 후보 기준)
- **`paper_home/02_research/claim_bank.jsonl` + `evidence_table.md`** (evidence-harvest 산출 — **근거의 단일 작업대**. evidence_table을 1차 인덱스로 읽고, high-risk·locked claim만 claim_bank에서 발췌)
- `paper_home/02_research/deep_research.md` — 원문 확인용 보조 (claim_bank 있으면 재해석 금지)
- (선택) 본인 보유 데이터/케이스 기술

## 절차 (workshop-mini, 25분)

### 3.1 One-sentence message (5분)

논문의 단일 메시지를 한 문장으로. 기준:
- **Specific**: "AI는 의학에 도움된다" ✗ → "전자담배 사용은 청소년의 사회적 우울 위험을 1.4배 증가시킨다" ✓
- **Defensible**: 본인 데이터 또는 인용된 근거로 방어 가능
- **Novel**: deep_research에서 동일 주장이 직접적으로 입증되지 않은 영역
- **Clinical**: target 독자가 진료에 적용 가능

산출 → `paper_home/03_outline/story_1pager.md`의 첫 줄

### 3.2 Gap statement (5분)

기존 문헌이 "무엇을 안 다뤘는가"를 1단락으로. Introduction의 마지막 문단 골격.

### 3.3 Outline 구조 결정 (10분)

Article type별 분기:

#### Letter / Commentary (800–1500w)
```
1. Hook (기존 RCT/가이드라인 한 줄 인용)
2. Counterpoint (본인 주장)
3. Supporting points (3개)
4. Implication (1단락)
```

#### Case Report (1500–2500w)
```
1. Introduction (case 의의 1단락)
2. Case Presentation (시간순)
3. Discussion (감별진단, 문헌 비교, 학습 포인트)
4. Conclusion
```

#### Brief Report (Original) (2000–3000w)
```
1. Introduction (gap → research question)
2. Methods (데이터, 변수, 분석)
3. Results (1–2 표 + 1 figure 권고)
4. Discussion (key finding, 비교, 한계, 결론)
```

#### Narrative Review (3000–5000w)
```
1. Introduction (scope, methods of review)
2. Body 섹션 5–8개 (시간/기전/임상 분류축 결정)
3. Synthesis (현재 합의 + 논쟁)
4. Future directions
```

#### Editorial / Viewpoint (1500–3000w)
```
1. 문제제기 (현 상황)
2. 분석 (왜 그런가)
3. 제안 (해야 할 일)
```

산출 → `paper_home/03_outline/outline.md` (Live Artifact 후보)

### 3.4 Evidence map (5분) — claim_id 기반

각 outline 섹션에 **claim_bank의 claim_id**를 매핑 (섹션당 핵심 claim 1–3개; `[NO_VERBATIM]`/`[INCOMPLETE]` claim은 스토리 중심축에 두지 않고 `Step 5 보강` 표시):

| 섹션 | claim_id | 핵심 주장 (요약) | source/DOI | risk | fit 관련성 | action |
|---|---|---|---|---|---|---|
| Intro §2 | C001 | 한국 청소년 e-cig 사용률 증가 | S003, S007 | medium | Strong-fit 저널 독자 관심 | keep |
| Discussion §1 | C003 | 사회적 우울 매개 | S009 | high ★ | 핵심 novelty | 본인 verbatim 확인 |
| Discussion §2 | — | (인용 후보 없음) | — | — | — | `NO_CLAIM_YET` → Step 5 보강 |

산출 → `paper_home/03_outline/evidence_map.md`

→ claim_id 없는 섹션(`NO_CLAIM_YET`)은 **Step 5 verify에서 보강 검색** 필요로 표시. claim_bank가 없으면(evidence-harvest 미실행) deep_research에서 직접 매핑하되 그 사실을 명시.

## Solo + Claude-only fallback

기본 Claude. 외부 엔진 불필요.

## Output 표준

### `story_1pager.md`
```markdown
# Story 1-Pager

## One-sentence message
{한 문장}

## Gap statement
{1 단락}

## Why now / why this journal
{1–2 문장}

## Section storyline
{각 섹션의 1줄 요약}

## Risk / counterargument
{예상되는 reviewer 반박 1–2개}
```

### `outline.md`
Section-by-section, 각 섹션마다:
- 핵심 주장 1–2 bullet
- 인용 후보 (evidence_map 링크)
- word budget (target journal 기반)

### `evidence_map.md`
표 형식 (위 참조)

## HITL Event Emit

```json
{"ts":"...","paper_id":"...","step":3,"gate":"A_design","event_type":"gate_pass","skill":"story-design","engine":"claude","category":"narrative_design","severity":1,"description":"outline 6 sections, evidence gaps in 2 sections","time_to_fix_min":25}
```

## 결정적 vs LLM 분리

- **LLM 판단**: narrative arc, 섹션 분류축, 메시지 정제, gap statement
- **결정적**: word budget (journal_specs 기반 산술), reporting checklist 섹션 강제 (CONSORT 등)

## Self-Gate A2 체크리스트 (Step 3 종료)

- [ ] One-sentence message가 specific + defensible + novel + clinical
- [ ] Gap statement가 deep_research 인용으로 뒷받침됨
- [ ] Outline의 모든 섹션에 핵심 주장 ≥ 1개
- [ ] Evidence map에서 인용 후보 0–1개인 섹션 식별 (Step 5 보강 표시)
- [ ] Section word budget이 target 저널 word limit 내
- [ ] Article type 확정 (Step 1 잠정 → Step 3 lock)

## Few-shot 예시

### Before (느슨한 outline)
```
1. Intro
2. Methods
3. Results
4. Discussion
```

### After (story-design)
```
1. Intro (350w)
   - Hook: 한국 흡연율 OECD 상위 (KOSIS 2024)
   - Gap: 전자담배-사회적 우울 관계 한국 데이터 부재
   - Question: 청소년에서 둘의 연관성?
2. Methods (500w)
   - Data: 2022 KYRBS N=51,850
   - Outcome: PHQ-9 ≥ 10
   - Exposure: 전자담배 30일 사용
   - Analysis: multivariate logistic
3. Results (450w)
   - Table 1: 인구학적
   - Table 2: 다변량 OR
   - Key: aOR 1.42 (95% CI 1.28-1.57)
4. Discussion (700w)
   - Main finding (1단락)
   - 기전 가설 (2단락) - Park 2025 비교
   - Limitation (1단락) - 단면연구, 잔류 교란
   - Implication (1단락) - 학교 보건
```

## 자주 발생하는 함정

1. **One-sentence가 너무 broad** — "AI는 의학에 도움된다" → 단일 측정 가능 주장으로
2. **Gap이 deep_research 인용으로 뒷받침 안 됨** — Step 5에서 reviewer가 잡음
3. **Word budget 무시** — Letter에 5000자 outline → Step 4에서 반드시 깎임
4. **Reporting checklist 섹션 누락** — CONSORT items가 Methods 섹션에 명시되지 않음
5. **Discussion limitation 부재** — Self-Gate에서 잡혀야 함

## 다음 단계

→ Step 4 Draft (Code 탭 작업본 `manuscript.md`)
