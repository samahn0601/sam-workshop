---
name: critic-multi-persona
description: >
  Use this skill when a medical manuscript draft needs reviewer-style critique
  before submission: methodology weakness, statistics/logic issues, structure
  problems, and reward-hacking risk. Implemented as Claude multi-persona
  (Reviewer-Method, Reviewer-Stats, Editor) plus optional external LLM
  critic (multi-LLM portal 등), integrated by an Area Chair persona. Trigger when user says "critic",
  "리뷰어 시각", "심사자처럼 봐줘", "weakness 점검", "area chair", "전문가
  비평", "peer review simulation", or operates in Step 6 Multi-Engine Critic of
  the sam-workshop pipeline. Do not use for reference verification (use
  verify-reference-essential) or grammar polish (use humanize-en/ko). Input:
  paper_home/04_draft/manuscript.md (and post-Step-5 verify reports +
  journal_shortlist.md). Output:
  paper_home/06_critic/{claude_personas.md, external_critic.md (optional),
  area_chair_round1.md, revision_backlog.jsonl}. Pipeline position: sam-workshop Step 6 / Self-Gate C.
  Medical context: ICMJE manuscript critique standards, RH1-RH4 reward-hacking
  defense, multi-engine cross-validation when an external LLM is available. Trigger
  keywords: critic, 리뷰어, 비평, peer review, area chair, weakness, reviewer,
  critique.
---

# critic-multi-persona (Step 6)

> Multi-engine peer review simulation. Claude 다중 페르소나 + 외부 LLM(선택) → Area Chair 통합. 워크숍 단순화 모드 표준.

## 모드

| 모드 | 시간 | 페르소나 |
|---|---|---|
| `workshop-mini` | 35분 | Claude 3-persona + 외부 LLM 1회 (선택) → AC |
| `standard` | 60분 | + RH1-RH4 reward hacking full check |
| `deep-audit` | 90분+ | + 저널-specific mock review |

## 페르소나 (워크숍 simplified)

| 페르소나 | 시각 | 출력 |
|---|---|---|
| **R1: Methods Reviewer** | 연구 설계, 통계, 교란, 일반화 가능성 | top 3 weakness |
| **R2: Stats/Logic Reviewer** | 통계 보고, 논증 흐름, 인과관계 비약 | top 3 issue |
| **Editor** | 구조, 임상적 함의, novelty, 저널 fit | top 3 strategic comment |
| (선택) **External LLM** | 외부 시각 (Claude 외 모델) | top 5 issue |
| **Area Chair** (Claude) | 통합, RH1–RH4 reward hacking 체크 | Must Fix / Should Fix / Optional |

## 입력

- `paper_home/04_draft/manuscript.md`
- `paper_home/05_verify/verification_certificate.md` (Step 5 통과 확인)
- `paper_home/03_outline/story_1pager.md` (편집 ↔ 본문 일관성 체크)
- `paper_home/01_design/journal_shortlist.md` (있으면 — Editor가 Scope fit·Fit verdict·Reject risk 반영)

## 절차 (workshop-mini, 35분)

### Phase 1 (15분) — Claude 3-persona critique

각 페르소나 프롬프트를 Code 탭에서 순차 발화. 각 5분.

#### Persona R1: Methods Reviewer
```
당신은 의학 저널의 Methods Reviewer입니다. 다음 manuscript의 methodology
약점을 top 3 지적하세요. 각 지적에:
- location (section + paragraph)
- issue (구체적)
- severity (Major/Minor)
- suggested_fix
- reward_hacking_risk (RH1-RH4 중 해당 시 표시)

RH1 (한계 나열로 점수 올리기): "limitations" 섹션을 추가만 했는가
RH2 (검증 우회): 결정적 검증 없이 LLM 의견만으로 통과
RH3 (이중 카운트): 같은 이슈를 여러 곳에서 언급해서 점수 분산 회피
RH4 (과장): "first/only/definitive"로 over-claim

(※ RH = reward-hacking. Step 5 verify-reference-essential의 reference 레이어 R1–R6과 별개 명명 — 혼동 금지.)
```

#### Persona R2: Stats/Logic Reviewer
```
당신은 의학 저널의 Statistics/Logic Reviewer입니다. 다음을 본문에서 검출:
- 통계 보고 형식 (n, %, p, 95% CI 일관성)
- 인과관계 비약 (correlation → causation)
- Effect size 해석 (clinical vs statistical significance)
- 다중비교 보정 누락
- Confounder 미처리

Top 3 issue + severity + suggested_fix + reward_hacking_risk.
```

#### Persona Editor
```
당신은 target 저널의 Editor입니다. journal_shortlist.md가 있으면 그 안의
Scope fit·Fit verdict·Reject risk를 먼저 읽고 반영하세요 (Fit verdict가
Risky면 그 사유를 1순위 코멘트로). 본 manuscript에 대해:
- 본 저널 scope 부합? 
- Novelty가 reader에게 실제 가치?
- 임상적 함의 명확?
- Section structure가 ICMJE/저널 표준 준수?
- One-sentence message가 abstract와 일치?

Top 3 strategic comment + accept_likelihood (low/medium/high) + 사유.
```

산출 → `paper_home/06_critic/claude_personas.md`

### Phase 2 (10분) — 외부 LLM critic (선택)

외부 LLM 웹챗(학교 멀티LLM 포털 등 가용한 것)에서 실행. **기본 1개 모델**, 시간·크레딧 여유 시에만 2개 모델 비교(포털의 동시 비교는 모델 수만큼 크레딧 소모). 업로드 전 확인: 원고에 환자 식별정보 없음 + (실제 투고 원고면) 외부 업로드에 대한 저널 정책. 다음 프롬프트 발사:

```
You are a senior reviewer for a medical journal. Read the attached manuscript
and identify the top 5 issues that would matter most to a desk editor and
reviewer. For each:
- exact location (section, paragraph)
- issue
- severity (Critical / Major / Minor)
- specific fix
- reward-hacking risk if any

Be terse. No prose. Bullet form.
```

→ 결과 복붙 → `paper_home/06_critic/external_critic.md` (legacy `gpt55_critic.md`가 있으면 AC가 함께 읽음)

(외부 LLM 사용 불가 시 — 포털 미접속·크레딧 소진 등 → Phase 3에서 Claude 4번째 페르소나 "External Skeptic"로 대체)

### Phase 3 (10분) — Area Chair 통합 (Claude)

```
당신은 Area Chair입니다. 다음 입력을 통합:
- claude_personas.md (R1, R2, Editor)
- external_critic.md (있으면; legacy gpt55_critic.md도 호환)

다음 산출:
1. 모든 issue를 claim_id 단위로 정리 (location 기반 식별자)
2. 양쪽 동일 지적 → Must Fix
3. 한쪽만 + 타당 → Should Fix
4. 한쪽만 + 선택적 → Optional
5. 양쪽 상반 → Sam 판정 + 사유

RH1-RH4 Reward Hacking 체크:
- RH1: limitations만 추가한 척 → reject
- RH2: LLM 의견만으로 통과 → reject  
- RH3: 이슈 분산 → reject
- RH4: over-claim → reject

Score-Driven Revert 알림 (scorecard-9d 산출이 **있을 때만**):
- v2 → v3 변경 시 종합 scorecard 비교
- 점수 ↓ → 즉시 revert 권고
- scorecard 산출 없으면 명시적으로 skip — 점수 임의 생성 금지

Output:
- Must Fix 목록 (우선순위 순)
- Should Fix 목록
- Optional 목록
- Reward hacking으로 reject한 항목 + 사유
```

산출 → `paper_home/06_critic/area_chair_round1.md`

### Phase 4 (Self-Gate C 결정)

본인이:
- [ ] 모든 Must Fix 채택 또는 사유 명시 reject
- [ ] Should Fix 중 시간 허락하는 것 채택
- [ ] Reward hacking reject 항목 재검토
- [ ] manuscript.md 즉석 수정

## Output 표준

### `area_chair_round1.md`
```markdown
# Area Chair Round 1

## Must Fix (우선순위 순)
| # | claim_id | location | issue | engine | suggested_fix |
|---|---|---|---|---|---|
| 1 | C-Methods-3 | Methods §3.2 | 교란 변수 미보정 | R1+EXT | 다변량 분석 추가 |
| 2 | ... |

## Should Fix
| ... |

## Reward Hacking Rejected
| # | original | reject reason |
|---|---|---|
| 1 | "여러 limitations 추가하여 점수 ↑ 의도" | R1 detected: cosmetic only |

## Score Comparison (v2 → v3 if applicable)
| 차원 | v2 | v3 (예상) |
|---|---|---|
| 방법론적 엄밀성 | 3 | 4 |
```

### `revision_backlog.jsonl` (v1.2 — 표준 포맷 강제)

Area Chair가 채택한 모든 항목 + reward-hacking으로 거부한 항목 모두 한 줄씩 JSONL로 emit. humanise/drift-check가 입력으로 사용하므로 **다음 필드 모두 필수**.

| 필드 | 타입 | 의무 | 설명 |
|---|---|:---:|---|
| `id` | string | ✓ | "AC-01", "AC-02" 형식 순차 |
| `section` | string | ✓ | "§3", "abstract", "references" 등 위치 |
| `severity` | enum | ✓ | "major" / "minor" |
| `accepted` | boolean | ✓ | true=채택, false=reject |
| `action` | string | ✓ | 1문장 명령형 ("Add failure-mode statement per step") |
| `origin` | string | ✓ | 원 critic 페르소나 ("R1-02+G-01" 형식) |
| `claim_id` | string | — | claim_bank 참조 시 (있으면) |
| `reward_hacking_reason` | string | — | reject 시 사유 (RH1-RH4 표시 또는 자유 텍스트; legacy 산출의 R1-R4 표기는 읽기 호환) |
| `score_impact` | object | — | `{"dim_2_methods": "+1"}` 형식 (scorecard-9d 연동 시) |

#### 예시 (v1.1 reference run, paper_meta_workshop)

```jsonl
{"id":"AC-01","section":"§2","severity":"major","accepted":true,"action":"Add failure-mode statement per step","origin":"R1-02+G-01"}
{"id":"AC-08","section":"references","severity":"minor","accepted":true,"action":"Drop duplicate Ref 13; renumber","origin":"E-04"}
{"id":"AC-XX","section":"§7","severity":"minor","accepted":false,"action":"Inflate limitations list","origin":"R1-rh","reward_hacking_reason":"R1: limitations만 추가하여 점수 ↑ 의도"}
```

#### 검증

`humanize-en/ko`는 `accepted: true`만 입력으로 받음. `accepted: false`는 audit trail로만 보존하며 본인 사후 검토용. 포맷 위반 시 humanise skill이 `revision_backlog_format_invalid` 카테고리로 HITL event emit.

→ **v1.2 NEW**: 본 포맷은 v1.1 reference run에서 비공식 사용된 포맷을 정식화한 것. v1.1 critic 산출은 후방 호환되며, v1.2부터 신규 critic 산출은 본 spec 의무 준수.

## HITL Event Emit

각 critic 의견 채택/거절 시:
```json
{"ts":"...","step":6,"gate":"C_verify_critic","event_type":"critique_decision","skill":"critic-multi-persona","engine":"claude_personas+external_llm","category":"methods_critique","severity":3,"description":"Multivariate adjustment missing","decision":"accepted","backlog_id":"AC-01"}
```

## 결정적 vs LLM 분리

전부 LLM. 단:
- Reward hacking 체크는 **rule-based** (RH1-RH4 정의 기반)
- Score comparison은 **결정적** (수치 비교 — scorecard-9d 산출 있을 때만)

## Solo + Claude-only fallback

외부 LLM 사용 불가 (포털 미접속·크레딧 소진·외부 도구 없음):
→ Claude 4번째 페르소나 "External Skeptic" 추가:
```
당신은 본 manuscript와 무관한 외부 회의주의자입니다. 가장 의심스러운 주장
3개를 찾아 reject 사유 제시. Claude의 R1/R2/Editor가 못 본 사각지대를 노려라.
```

엔진 다양성이 줄어 같은 맹점을 공유할 수 있으나(단일 모델 한계), 워크숍 산출은 가능.

## Floor (절대 위임 불가)

- 임상 권고에 영향: AC가 채택해도 본인 최종 결정
- IRB / 윤리: AC 의견과 무관하게 본인 검토
- Reward hacking 거부: AC가 reject한 것 중 본인이 valid하다 판단하면 다시 채택 가능 (단 사유 명시)

## Self-Gate C 체크리스트

- [ ] Must Fix 100% 처리
- [ ] Score-Driven Revert 발동 시 본인 ratify
- [ ] Reward hacking reject 항목 본인 검토
- [ ] manuscript.md 수정 반영

## 자주 발생하는 함정

1. **AC가 모든 critic 채택** — 거꾸로 reward hacking. 본인 판단 무 → reject 일부 정당
2. **외부 LLM critic이 Claude와 너무 비슷** — 유사 학습 데이터 영향. Step 5 R6(인용-주장 검증) 결과·웹근거로 보강
3. **Editor 페르소나가 too positive** — accept_likelihood 너무 후함. "가장 가혹한 desk editor" 페르소나 강화
4. **Score 비교 없이 진행** — scorecard-9d 산출이 있으면 v2/v3 비교 필수, 없으면 명시적으로 skip(임의 점수 금지)

## 다음 단계

→ Self-Gate C 통과 → Step 7 Humanize & Package (figure brief는 step 7 옵션)
