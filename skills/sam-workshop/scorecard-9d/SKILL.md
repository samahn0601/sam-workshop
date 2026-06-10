---
name: scorecard-9d
description: >
  Use this skill to score a medical manuscript draft on 9 dimensions (clinical
  relevance, methodological rigor, evidence sufficiency, logical coherence,
  novelty, style/readability, journal fit, humanness, section boundaries) for
  Self-Gate decisions and version comparison. Trigger when user says "scorecard",
  "9차원 점수", "원고 평가", "manuscript score", "draft 점수", "version
  comparison", "점수 비교", or operates in Step 6 of sam-workshop pipeline.
  Pairs with critic-multi-persona for combined critique-and-score exercise. Do
  not use for desk-rejection precheck (use desk-reject-precheck) or final
  packaging (use the Step 7 packaging flow). Input: paper_home/04_draft/manuscript.md (and
  prior version if comparing + journal_shortlist.md for dimension 7). Output: paper_home/06_critic/scorecard_9d.md.
  Pipeline position: sam-workshop Step 6 / Self-Gate C, optional re-score at
  D_finish (after Step 7, before submission).
  Medical context: ICMJE-aligned dimensions, KAMJE peer-review aligned scoring,
  reward-hacking detection through dimension-by-dimension diff. Trigger keywords:
  scorecard, 점수표, 9차원, 평가, score, dimension, version diff, 점수 비교.
---

# scorecard-9d (Step 6, optional 투고 직전 re-score)

> 9차원 정량 평가. v1 → v2 → v3 진행 시 차원별 변화 추적 (Score-Driven Revert 감지). critic-multi-persona와 자주 묶어 운영.

## 9차원

| # | 차원 | 척도 |
|---|---|---|
| 1 | 임상적 관련성 | 1–5 |
| 2 | 방법론적 엄밀성 | 1–5 |
| 3 | 근거 충분성 | 1–5 |
| 4 | 논리적 일관성 | 1–5 |
| 5 | 독창성 | 1–5 |
| 6 | 문체/가독성 | 1–5 |
| 7 | 저널 적합성 | 1–5 |
| 8 | Humanness (AI 시그니처 부재) | 1–5 |
| 9 | Section Boundaries | Pass / Fail |

종합: 1–8 합산 (max 40) + 9 통과 여부.

## 점수 기준 (1–8)

| 점수 | 의미 |
|---|---|
| 5 Excellent | 수정 불필요 |
| 4 Good | Minor revision 수준 |
| 3 Acceptable | 의미 있는 개선 필요 (reviewer 지적 가능성 ↑) |
| 2 Weak | 재채점 필요한 심각한 문제 |
| 1 Critical | 근본적 재작업 |

## 모드

| 모드 | 시간 | 특징 |
|---|---|---|
| `workshop-mini` | 10분 | 1–8 점수 + 9 Pass/Fail, 간단 사유 |
| `standard` | 25분 | + dimension별 evidence span 인용 |
| `deep-audit` | 50분 | + version diff (v1 vs v2 vs v3) |

## Gate 연동

- **Self-Gate A2 (Step 3 후)**: 차원 7 (저널 적합성) ≥ 3
- **Self-Gate C (Step 6 후)**: 종합 ≥ 32/40 + 차원 ≤ 2 = 0건 + 차원 9 = Pass
- **Self-Gate D_finish (Step 7 후, 투고 직전 re-score)**: 종합 ≥ 36/40 + 차원 9 = Pass

> 차원 7 (저널 적합성)은 `journal_shortlist.md`의 **Scope fit·Fit verdict·Reject risk를 필수 참조** — "Reject risk를 상쇄할 논리가 draft에 있는가"를 본다 (Step 1 Scope-Fit Gate의 downstream 반영).

## 입력

- `paper_home/04_draft/manuscript.md`
- (선택) `paper_home/04_draft/manuscript_versions/manuscript_vN.md` (비교용)

## 절차 (workshop-mini, 10분)

### Step 1: 9차원 채점

Code 탭에서:
```
당신은 Area Chair입니다. 첨부 manuscript.md를 9차원에서 채점하세요.

각 차원에 대해:
- 점수 (1-5 또는 Pass/Fail)
- 1줄 사유 (구체적, "전반적으로 좋음" 같은 모호 X)
- evidence_location (해당 판단의 근거가 된 본문 위치)

차원 9는 Pass/Fail만. Results에 해석 0건, Discussion에 새 데이터 0건이면 Pass.
```

### Step 2: 종합 + Gate 매칭

| 종합 | 수준 | 다음 단계 |
|---|---|---|
| 36–40 + 9=Pass | 투고 준비 | Self-Gate D 통과 가능 |
| 32–35 + 9=Pass | Gate C 통과 | 마무리 정제 후 Step 7-8 |
| 25–31 | Major revision | Step 6 critic 재실행 |
| < 25 | 재작성 | Step 3 outline 회귀 |

### Step 3: Humanness 자동 트리거

차원 8 ≤ 3점 → `humanize-en` 또는 `humanize-ko` 자동 발화 권고.

### Step 4: Version diff (있을 때)

```
v1 vs v2 비교:
| 차원 | v1 | v2 | Δ |
|---|---|---|---|
| 1 임상적 관련성 | 4 | 4 | 0 |
| 2 방법론적 엄밀성 | 3 | 4 | +1 |
| 3 근거 충분성 | 3 | 4 | +1 |
| 4 논리적 일관성 | 4 | 3 | -1 ⚠️ |
...

⚠️ 차원 4 하락 → Score-Driven Revert 검토 권고.
```

## Output 표준

### `scorecard_9d.md`
```markdown
# Scorecard 9D — Round N

## 점수
| 차원 | 점수 | 사유 | Evidence |
|---|---|---|---|
| 1. 임상적 관련성 | 4/5 | family physician 진료에 적용 가능 | Discussion §1 |
| 2. 방법론적 엄밀성 | 3/5 | 단면연구 한계 명시되나 잔류 교란 미언급 | Methods §2 |
| ... |
| 9. Section Boundaries | Pass | Results 해석 0건, Discussion 새 데이터 0건 | - |

## 종합
- 1–8 합: 32/40
- 차원 9: Pass

## Gate 판정
- Gate C: PASS (≥32 + 차원 ≤2 = 0건 + 9=Pass)

## Humanness 트리거
- 차원 8 = 4 → humanize 재실행 불필요

## Version Diff (있을 때)
- v1 합 28 → v2 합 32 (+4)
- 차원 4 변화 없음, Score-Driven Revert 미발동
```

## HITL Event Emit

```json
{"ts":"...","step":6,"gate":"C_verify_critic","event_type":"gate_pass","skill":"scorecard-9d","engine":"claude","category":"manuscript_score","severity":2,"description":"Score 32/40, dim9=Pass, no Score-Driven Revert"}
```

## 결정적 vs LLM 분리

- **LLM**: 9차원 점수 자체 (정성)
- **결정적**: 종합 산술, Gate 임계 비교, Score-Driven Revert 감지 (수치 ↓ 룰)

## Self-Gate 체크리스트

### Self-Gate C (Step 6)
- [ ] 종합 ≥ 32
- [ ] 1–8 차원 중 ≤ 2점 = 0건
- [ ] 차원 9 = Pass
- [ ] Score-Driven Revert 미발동 (또는 본인 ratify)

### Self-Gate D_finish (Step 7 후 · 투고 직전 re-score)
- [ ] 종합 ≥ 36
- [ ] 차원 9 = Pass
- [ ] 차원 8 ≥ 4 (Humanness 안정)

## 자주 발생하는 함정

1. **AI가 본인 score를 후하게 줌** — 자체평가 편향. "당신은 가장 가혹한 reviewer" 페르소나로 강화
2. **Evidence_location 누락** — 근거 없는 점수 → reward hacking 의심
3. **v1→v2 차원별 비교 없이 종합만 비교** — 한 차원 하락 못 봄 (Score-Driven Revert)
4. **Humanness 단순 체크** — AI 시그니처 단어 (Moreover, Furthermore...)는 humanize-en/ko에서 별도 검증

## 다음 단계

→ Self-Gate C/D 통과 후 다음 step
