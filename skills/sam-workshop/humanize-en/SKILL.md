---
name: humanize-en
description: >
  Use this skill to humanize English medical manuscript prose drafted with AI
  assistance: remove AI-signature vocabulary, vary sentence rhythm, retain
  scientific accuracy and journal style. Trigger when user says "humanize",
  "AI 시그니처 제거", "문체 다듬기", "natural English", "remove AI markers",
  "ESL 자연화", "휴머나이즈", or operates in Step 7 (Humanize & Package) of
  sam-workshop pipeline (English manuscripts only). Do not invent data, results, p-values, citations,
  or change effect direction. Use humanize-ko for Korean manuscripts. Input:
  paper_home/04_draft/manuscript.md (English) +
  paper_home/06_critic/revision_backlog.jsonl (accepted:true only). Output: in-place edit + optional
  paper_home/04_draft/manuscript_versions/manuscript_humanized_v{N}.md.
  Pipeline position: sam-workshop Step 7. Medical context: ICMJE compliance,
  ESL-aware (non-native English author), journal-specific style overrides
  default. Mandatory after critic-multi-persona, before desk-reject-precheck. Trigger
  keywords: humanize, AI signature, Moreover, Furthermore, delve, leverage,
  자연스럽게, 문체, 영어, polish.
---

# humanize-en (Step 7 — Humanize & Package)

> AI가 쓴 영문 manuscript를 인간 학자가 쓴 것처럼 다듬되, **과학적 정확성·저널 스타일은 절대 깨지 않는다.** Sam pipeline의 humanize-en-v4.1 기반 + 워크숍 단순화.

## 윤리 원칙 (Ethical framing)

이 스킬은 의미를 보존하면서 문장 흐름·자연스러움을 개선하는 도구다. **AI 사용 사실을 숨기거나 AI 탐지를 회피하기 위한 용도가 아니다.** 원고 준비에 AI를 사용했다면 대상 저널 정책에 따라 cover letter·원고 내 적절한 위치에 공개한다(ICMJE). 정확성·독창성·인용·최종 문구의 책임은 인간 저자에게 있다.

## Non-Negotiables (8 절대 규칙)

1. **Never invent** data, results, p-values, CIs, sample sizes, methods details, references, author names, publication years, journal titles, quotations. Missing → `[ADD: what's needed]`.
2. **Never claim "statistically significant"** without p-value/CI/explicit source. Missing → `[ADD: significance evidence]` or rephrase descriptively.
3. **Never change** effect direction, reference groups, or statistical interpretation.
4. **Never upgrade uncertainty** — "non-significant" stays "non-significant" unless author reframes.
5. **Preserve meaning** — improve clarity/flow without altering claims.
6. **Maintain internal consistency** — variables, abbreviations, units, timepoints, statistical format, figure/table refs.
7. **Citations not provided → `[ADD: citation(s)]`.** Don't fabricate.
8. **Accuracy wins** when stylistic rule conflicts with science or journal convention.

## AI Signature Blacklist

다음 어휘/패턴 발견 시 → 자연 영어로 교체. **기계적 전면 삭제 금지** — 문맥상 불필요·과장된 경우에 평이한 동의어로 대체(과교정은 오히려 어색):

**어휘**
- Moreover, Furthermore, Additionally, In addition (start of paragraph)
- delve, crucial, comprehensive, leverage, facilitate, underscore
- "novel insights", "shed light on", "in this study, we"
- "It is important to note that" (filler)
- "It is worth noting that" (filler)
- "In this paper, we present"

**패턴**
- 모든 단락이 동일 길이 (15–20 단어 sentences)
- 모든 sentence가 SVO opener (다양화 필요)
- "First, ... Second, ... Third, ..." 기계적 enumeration
- Em dash 1단락에 3개+
- "Not only... but also..." 반복

## Stylistic Rules (요약)

### Sentence Architecture — 가장 중요

- **Vary sentence length intentionally** — short (5–12 words) ↔ long (25–40 words). 3+ consecutive 같은 길이 → rewrite.
- **Vary sentence openers** — SVO 반복 시 prepositional phrase / subordinate clause / framing adverbial 도입
- "And", "But", "Yet" 시작 — rare but human (저널이 허용 시)
- Em dashes — like this — ≤ 1 per paragraph
- **Paragraph length must vary** — 2–3 sentences vs 6–8 sentences 혼합. Rare 1-sentence paragraph for emphasis.
- Each paragraph: claim → support → bridge. *Shape* should differ.
- **Methods/Results exempt** — uniform precision is natural there.

### Vocabulary

- Replace generic "important/significant/various" with specific terms
- Use field-specific terminology (cardiology paper uses cardiology vocabulary)
- ESL natural patterns: 가끔 minor article omission이 OK ("Patients underwent CT scan" vs "Patients underwent a CT scan")

### Voice

- Active voice preferred for Methods (per AMA Manual)
- Passive OK for Results
- First-person plural ("we") allowed in most journals

## 모드

| 모드 | 시간 | 범위 |
|---|---|---|
| `workshop-mini` | 15분 | AI signature 제거 + sentence rhythm vary 1 pass |
| `standard` | 35분 | + paragraph 구조 재배치 |
| `deep-audit` | 60분 | + 저널-specific style 정밀 매칭 |

## 입력

- `paper_home/04_draft/manuscript.md` (English)
- `paper_home/01_design/journal_shortlist.md` (저널 style 반영)
- `paper_home/06_critic/revision_backlog.jsonl` — **accepted:true 항목만 반영** (비승인 항목 반영 금지 — Step 6 선별 우회 방지; 포맷 위반 시 `revision_backlog_format_invalid` HITL emit)

## 절차 (workshop-mini, 15분)

### Step 1 (5분) — AI signature 제거

```
다음 manuscript에서 AI signature 어휘 (Moreover, Furthermore, delve, leverage,
crucial, comprehensive, ...) 모두 자연 영어로 교체. 
8 Non-Negotiables 준수.
변경 사항을 diff 형식으로 출력 (before/after 쌍).
```

### Step 2 (5분) — Sentence rhythm vary

```
다음 단락에서 sentence length variance를 점검. 3+ consecutive sentences가
같은 length band면 1개를 rewrite.
SVO opener 반복 시 다른 opener로.

Methods/Results는 면제.
8 Non-Negotiables 절대 위반 금지.
```

### Step 3 (3분) — Internal consistency

```
다음 manuscript에서 일관성 점검:
- 약어 (첫 등장 시 정의 → 이후 약어만)
- 단위 (mg vs mg/kg, mmHg)
- 변수명 (consistent across Methods, Results, Tables)
- 통계 형식 (p<0.001 vs p < 0.001)
- Figure/Table ref ("Fig 1" vs "Figure 1")

수정 사항 list.
```

### Step 4 (2분) — Post-humanize drift check + Self-Gate D pre-check

```
Drift check (diff에 잡힌 변경 문장만 — 전체 원고 재검증 금지):
1. humanize_diff.md의 각 변경을 태깅: style-only / claim-touching / uncertain
2. claim-touching·uncertain만 대조:
   - 수치·p·CI·효과방향 → 원문과 Δ check (필요 시 stats-consistency)
   - 인용 문장 → verify-reference-essential R6 spot 재확인
   - revision_backlog accepted:true 항목과 일치 여부
3. drift 의심 1건이라도 → 해당 문장 원문으로 롤백 + diff에 기록

Final pass: AI signature 잔존 0건 / [ADD: ...] 해결 / Effect direction 변경 0건 /
종합 가독성: 인간 학자가 쓴 것 같은가?
```

## Output 표준

In-place edit `manuscript.md`. 추가:
- `manuscript_versions/manuscript_humanized_v1.md` (snapshot)
- `humanize_diff.md` (변경 사항 표 — 본인 검토용)

```markdown
# Humanize Diff

| # | Section | Before | After | Reason |
|---|---|---|---|---|
| 1 | Discussion §1 | "Moreover, our findings..." | "Our findings..." | AI signature removed |
| 2 | Intro §2 | "It is crucial to note that..." | "(removed filler)" | Filler |
| 3 | Discussion §3 | 5 consecutive 17-word sentences | mixed 8/22/14/27/11 | Rhythm vary |
```

## HITL Event Emit

```json
{"ts":"...","step":7,"gate":"D_finish","event_type":"gate_pass","skill":"humanize-en","engine":"claude","category":"humanize","severity":1,"description":"AI signatures removed: 12 instances. Sentence rhythm pass: 3 paragraphs rewritten.","time_to_fix_min":15}
```

## 결정적 vs LLM 분리

- **결정적 (regex)**: AI signature blacklist 검출
- **LLM**: 자연 영어 대체 표현 생성, sentence rhythm 평가, voice 결정

## Solo + Claude-only

기본. 외부 도구 불필요.

## Floor (절대 위임 불가)

- **Effect direction** — humanize 중 reviewer가 가장 잡는 reward hacking 사례. 본인 매 문장 verify
- **Citation 추가/삭제** — humanize는 citation 변경 금지
- **수치/단위** — humanize는 prose만, 수치는 그대로

## Self-Gate D 체크리스트

- [ ] AI signature 어휘 0건 (regex 재검증)
- [ ] [ADD: ...] 모두 해결 또는 본인 결정 표시
- [ ] Effect direction 변경 0건 (Δ check)
- [ ] Sentence length variance 확보 (3+ 동일 길이 패턴 0건)
- [ ] 약어/단위 internal consistency

## Few-shot 예시

### Before (AI 시그니처)
```
Moreover, our study underscores the crucial importance of comprehensive
screening. Furthermore, it is worth noting that delving into the underlying
mechanisms could leverage these novel insights to facilitate better outcomes.
```

### After (humanized)
```
Our study highlights the value of routine screening. The mechanisms behind
these associations remain unclear, and clarifying them may improve outcomes.
```

→ 26→16 단어, 문장당 변형, 시그니처 0개, 의미 보존.

### Before (단조 rhythm)
```
Patients were enrolled from January 2022. Patients underwent baseline
assessment. Patients received the intervention. Patients were followed for
12 months. Patients completed final assessment.
```

### After
```
Between January 2022 and December 2023, we enrolled 287 patients, all of
whom underwent baseline assessment. Following the intervention, we observed
participants over 12 months. Final assessment was completed by 268 patients
(93.4%).
```

→ Methods 면제 영역도 SVO 반복은 깬다.

## 자주 발생하는 함정

1. **Effect direction 부지불식 변경** — "decreased risk" → "did not increase" 같은 reframe도 위험
2. **Citation 갈아끼움** — humanize는 prose만, 절대 citation 변경 X
3. **수치 단위 변환** — "30 mg" → "30 mg/kg" 같은 사고. 단위는 그대로
4. **Methods uniform precision 깨기** — Methods/Results는 면제 영역, 시적 변형 X
5. **Em dash 남용** — 1 paragraph에 3개+ → AI 시그니처

## 다음 단계

→ Step 4의 drift check 완료 → desk-reject-precheck (Step 7 quick scan) → Step 8 Wrap & Next
