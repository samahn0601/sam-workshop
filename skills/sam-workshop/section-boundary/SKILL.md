---
name: section-boundary
description: >
  Use this skill to detect IMRaD section boundary violations: interpretation in
  Results, new data in Discussion, methods bleeding into Results, etc. Trigger
  when user says "섹션 경계", "section boundary", "Results 해석", "Discussion
  새 데이터", "IMRaD 위반", or after Step 4 Draft / Step 6 Revision in
  sam-workshop pipeline. Frequently auto-invoked by scorecard-9d (dimension 9)
  and humanize. Do not use for figure caption (use figure-prompt-eng) or
  reference verification. Input: paper_home/04_draft/manuscript.md. Output:
  paper_home/05_verify/section_boundary.md (Pass/Fail + violations list).
  Pipeline position: sam-workshop after Step 4 (auto), before Self-Gate C.
  Medical context: ICMJE-aligned IMRaD discipline, KAMJE peer-review standard,
  reviewer가 가장 자주 잡는 구조 위반. Trigger keywords: section boundary,
  IMRaD, 섹션 경계, Results 해석, Discussion 새 데이터, 섹션 위반.
---

# section-boundary (Tier 2 — auto)

> IMRaD 섹션 경계 위반 자동 검출. scorecard-9d의 차원 9 (Pass/Fail)와 직접 연동.

## 4가지 위반 유형

| 유형 | 설명 | 심각도 |
|---|---|---|
| **B1** Results 해석 | Results 섹션에 "이는 ~을 시사한다" 같은 해석 | Major |
| **B2** Discussion 새 데이터 | Discussion에 처음 등장하는 수치/표 | Major |
| **B3** Methods → Results 누수 | Methods에 결과 수치 ("우리는 ~을 발견했다") | Minor |
| **B4** Intro에 결론 | Intro에 본 연구의 결론 ("우리는 ~을 보였다") | Minor |
| **B5** Abstract ↔ 본문 불일치 | Abstract에 본문에 없는 결과·결론 (또는 수치 상이 — 수치 자체는 stats-consistency 담당) | Major |

## 모드

기본 자동 (scorecard-9d 호출 시 함께). 단독 실행도 가능.

| 모드 | 시간 |
|---|---|
| `workshop-mini` | 5분 |
| `standard` | 15분 (수정 제안 포함) |

## 입력

- `paper_home/04_draft/manuscript.md`

## 절차 (5분)

```
당신은 IMRaD 섹션 경계 검사관입니다. 다음 manuscript에서:

B1 (Results 해석): Results 섹션에서 "이는 ~을 시사한다", "이 결과는 ~을 의미한다",
   "~로 해석할 수 있다", "임상적으로 ~을 의미한다" 같은 해석성 문장 검출

B2 (Discussion 새 데이터): Discussion에서 Results에 없던 수치(N, %, p, OR/HR/RR/CI),
   표, 그림, p-value 처음 등장 검출

B3 (Methods → Results): Methods 섹션에서 결과 진술 ("우리는 X를 발견했다",
   "결과적으로 ~", 수치 등) 검출

B4 (Intro 결론): Introduction에서 본 연구의 결과 진술 ("본 연구는 ~을 보였다",
   "우리는 ~을 입증했다") 검출

B5 (Abstract↔본문): Abstract에 있는데 본문(Results/Discussion)에 없는 결과·결론 검출
   (수치 일치 자체는 stats-consistency가 담당 — 여기선 존재 여부만)

각 위반에:
- 위치 (section, paragraph, sentence)
- 위반 유형 (B1-B4)
- 위반 문구 인용
- 어디로 옮겨야 하는지 (또는 삭제)

종합: 위반 0건 → Pass / 1건 이상 → Fail (scorecard 차원 9 = Fail)
```

## Output 표준

`paper_home/05_verify/section_boundary.md`:

```markdown
# Section Boundary Check

## 종합: Fail

## 위반
| # | 유형 | 위치 | 위반 문구 | 권고 |
|---|---|---|---|---|
| 1 | B1 | Results §3 ¶2 | "이는 SGLT2 억제제의 우월성을 시사한다" | Discussion §1로 이동 |
| 2 | B2 | Discussion §2 ¶1 | "추가 분석에서 N=237" | Results로 이동 또는 삭제 |
| 3 | B3 | Methods §2.3 | "우리는 ~을 확인하였다" | Results §1로 |

## scorecard-9d 차원 9: Fail
```

## HITL Event Emit

```json
{"ts":"...","step":4,"gate":"B_draft","event_type":"gate_fail","skill":"section-boundary","engine":"claude","category":"section_violation","severity":3,"description":"3 violations: 1 B1, 1 B2, 1 B3"}
```

(실행은 Step 4 직후 가능 — 결과는 B_draft(Step 5 후) 판정의 입력 + scorecard-9d 차원 9로 전달. 본 스킬은 flag만, Pass/Fail 종합 판정은 scorecard가.)

## 자주 발생하는 함정

1. **B1 Results 해석 — 가장 흔함** — "이는 X을 의미한다" 자주 누락
2. **B2 새 데이터 — 두 번째로 흔함** — Discussion에서 추가 분석 결과 처음 등장
3. **B3 — 의대 교수 자주 함** — Methods에 "결과적으로" 표현 자연스러워서

## 다음 단계

→ 위반 수정 → scorecard-9d 차원 9 Pass → Self-Gate C
