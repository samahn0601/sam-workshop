---
name: hitl-dial-recommender
description: >
  Two-way HITL control for the workshop pipeline. (A) At SESSION START: show the
  8-step pipeline map (pipeline_map.md) and let the user pick a "운전 모드" (drive
  mode) — manual/standard/light/full_auto/custom — then write
  paper_home/.sam/hitl/gate_plan.json (gate_plan.schema.json) so each step stops
  (review) or passes (auto) as chosen. (B) At SESSION END or after each paper:
  read the accumulated event log and produce a Lab Report recommending the HITL
  dial (H0–H4) for the NEXT paper. Trigger at session start for "운전 모드",
  "gate plan", "어디서 멈출지", "자동화 수준", "HITL 설정"; trigger at wrap for
  "HITL dial", "다음 논문 dial", "처방전", "calibration", "lab report". Do not use
  during draft writing itself (use other skills). Input:
  paper_home/.sam/hitl/events.jsonl + paper_home/.sam/hitl/paper_profile.json.
  Output: gate_plan.json (start) / dial_recommendation.md +
  self_deadline_checklist.md (end). Medical floor (clinical recommendation, drug,
  IRB, reference R6) is always enforced regardless of mode/dial. Trigger keywords:
  운전 모드, drive mode, gate plan, HITL dial, calibration, 처방전, AI 위임 수준,
  supervision level, 어디서 멈출지, 자동화 수준, lab report, retrospective.
---

# hitl-dial-recommender (Meta — session start + wrap + post-paper)

> **양방향 HITL 운전.** (A) 세션 **시작**: 8단계 파이프라인 맵을 보여주고 운전 모드를 받아 `gate_plan.json` 작성. (B) 세션 **끝**: events.jsonl → 다음 논문 권장 Dial (H0–H4) **Lab Report**. 의학 floor (임상/약물/IRB/R6)는 모드·dial 무관 강제.

## 세션 시작 — Gate Plan 구성 (운전 모드 선택)

워크숍/논문 세션 시작 시(Idea Lock 직전) 수행:

1. `~/.claude/skills/sam-workshop/_shared/templates/pipeline_map.md`의 8단계 맵 + 운전 모드 표를 보여준다.
2. 사용자가 자연어로 모드를 고르게 한다 (예: "표준", "다 맡기고 끝에만", "③⑤만 내가"). 기본값 🛡️표준(H3).
3. 선택을 `paper_home/.sam/hitl/gate_plan.json` (`gate_plan.schema.json` 형식)으로 저장한다.
4. 이후 각 step 종료 시 Cowork project instructions의 gate_plan 참조 규칙에 따라 정지(`review`)/자동(`auto`)이 동작한다.

| 운전 모드 | dial | 정차 단계 | 노출 |
|---|---|---|---|
| 🛡️ 표준 *(기본)* | H3 | ①③⑤⑥⑦ | 현장 기본 |
| ⚡ 시간절약 | H2 | ①⑤⑦ | 현장 옵션 |
| 🚗 전체 정차 | H4 | ①~⑧ 전부 | 강사 데모 |
| 🏁 최종 집중 | H1 | ①⑦ | 사후 자산 |
| 🎛️ 커스텀 | — | 지정 (①⑦은 ⭐ 최소 유지) | 사후 자산 |

> ⭐ **Soft floor ①⑦**: 어떤 모드든 최소 1회 저자 확인 (① 주제·저널 확정[교육], ⑦ AI 공개문·cover letter[윤리]).
> 🔒 **2 Floor 자동 정차**(gate_plan 우선): **Medical Safety**(약물·IRB·임상권고·R6) + **Publication Ethics**(AI 공개문·authorship·COI·저널정책).
> 용어: "auto/풀오토" 대신 **"정지 없이 진행"**(요약 확인·저자 책임 유지). 현장은 🛡️표준+⚡시간절약 2개만, 나머지는 사후 자산으로 소개.
> 시작에서 모드를 고르고(이 절), 끝에서 다음 논문 모드를 처방받는다(아래 dial 권고) — 양방향 루프.

## HITL Dial 5단계

| Dial | 이름 | 의미 | 권고 대상 |
|---|---|---|---|
| **H4** | 8-gate hand-holding | 8 step 모두 human gate | 초보, 고위험, 이전 hallucination 多 |
| **H3** | 4-gate standard | A/B/C/D Self-Gate | **워크숍 default** |
| **H2** | 2-gate accelerated | Design + Verify/Critic gate | 경험자, 저위험 |
| **H1** | 1-gate Auto-Pilot | 제출 전 final human gate | 사전검토, 내부문서 |
| **H0** | 0-gate Sakana style | autonomous run | 의학 논문 제출용 **비권장** |

## 모드

| 모드 | 시간 |
|---|---|
| `workshop-mini` | 5–10분 (워크숍 wrap) |
| `standard` | 15분 (사후 논문 종료 시) |

## 입력

- `paper_home/.sam/hitl/events.jsonl` — 워크숍/논문 동안 누적된 모든 이벤트
- `paper_home/.sam/hitl/paper_profile.json` — paper_profile.schema.json 형식
- (Optional) `~/.sam-workshop/memory/user_memory.json` — 누적 사용자 history

## 절차 (10분, workshop-mini)

### Step 1 (3분) — 데이터 집계

```bash
python ~/.claude/skills/sam-workshop/_shared/scripts/hitl_recommend.py \
  --events paper_home/.sam/hitl/events.jsonl \
  --profile paper_home/.sam/hitl/paper_profile.json \
  --out paper_home/.sam/hitl/dial_recommendation.md
```

자동 산출:
- Risk score 계산 (0–100)
- Score → Dial mapping
- Hard guardrails 적용
- Lab Report 양식 출력

### Step 2 (5분) — 본인 검토

본인이:
- [ ] 권고 dial 동의?
- [ ] Hard guardrail 발동 항목 검토
- [ ] 다음 논문에서 강화/완화할 영역
- [ ] 처방전 본인 노트 추가

### Step 3 (2분) — 다음 논문 setup + 자가-마감 5–7일 체크리스트 생성

다음 논문 paper_home 생성 시 권고 dial을 starting point로.

**v1.3 신규**: workshop wrap 마지막에 본 워크숍 산출물에 대한 **자가-마감 5–7일 체크리스트**를 자동 생성:

```bash
python skills/sam-workshop/_shared/scripts/hitl_recommend.py \
  --events  paper_home/.sam/hitl/events.jsonl \
  --profile paper_home/.sam/hitl/paper_profile.json \
  --out     paper_home/.sam/hitl/dial_recommendation.md \
  --self-deadline-out paper_home/08_package/self_deadline_checklist.md
```

`self_deadline_checklist.md`는 워크숍 산출물이 **submission-directed**임을 강조하고, 5–7일 사이 본인이 수정/검증해야 할 작업을 행동 단위로 나열. 본 파이프라인의 `last_5min_checklist.py` 템플릿을 응용했지만 의미가 다름:
- 본 파이프라인 last_5min: "제출 직전 5분 체크"
- 워크숍 self-deadline: "**자가-마감 5–7일 동안 반드시 통과해야 할 항목**"

## 권고 알고리즘 (요약)

### Risk Score
```
score = 25 × severe_hallucination_rate
      + 20 × verify_gate_fail_rate
      + 15 × reference_error_rate
      + 15 × stats_inconsistency_rate
      + 10 × external_critic_severe_accept_rate
      + 10 × journal_stakes (Q1=1.0, Q4=0.2)
      + 5  × novelty_penalty
      - 10 × clean_runs_last_2_papers
```

### Score → Dial
| Risk | Dial |
|---|---|
| 75–100 | H4 |
| 50–74 | H3 |
| 30–49 | H2 |
| 15–29 | H1 |
| 0–14 | H0 (의학 비권장) |

### Hard Guardrails (절대 못 낮춤)

| 조건 | 최소 dial |
|---|---|
| 최근 논문에서 retracted citation 발견 | H3 |
| Citation chimera ≥ 1건 | H3 |
| Unsupported paraphrase severe ≥ 2건 | H4 |
| 통계 high-severity 불일치 | H3 |
| 첫/두번째 AI-assisted manuscript | H3 |
| 실제 journal submission 목표 | H2 이하면 C gate 필수 |

→ Score 기반 dial과 guardrail 중 더 높은 쪽 채택.

## Output 표준 (Lab Report + Self-Deadline Checklist)

### 1) `dial_recommendation.md` (기존)

```markdown
# 🩺 HITL Dial 처방전 (Lab Report)

- 환자 (paper_id): paper-2026-001
- Article type: brief_report
- Target journal: JKMS
- 기록된 이벤트: 47건

## 검사 결과

| 항목 | 값 |
|---|---|
| Risk score | **52.3 / 100** |
| Gate pass | 4 |
| Gate fail | 2 |
| Hallucinations | 3 (severe 1) |
| Critique accept rate | 64% |

## Hallucination 분포
- references: 2
- discussion_claim: 1

## 처방
- Risk score 기반: H3 (4-gate standard)
- Hard guardrail 적용: 최소 H3 (verification gate fail + first AI paper)
- **최종 권장 Dial: H3 (4-gate standard)**

## 사유
- 최근 논문에서 verify gate에서 high-severity 이슈 발생
- Severe hallucination 1건 — verify 강화 유지 권고
- 외부 critic 채택률 64% — critic gate는 유지
- 첫/두번째 파이프라인 사용 — 표준 4-gate 유지

## 절대 위임 불가 영역 (Floor — 모든 dial에서 유지)
- 임상 권고 / 가이드라인 변경 제안 → 본인 판단
- 약물 용량, 오리지널 vs 제네릭 → 본인 판단
- IRB / 윤리 / 환자 동의 문구 → 본인 작성
- Reference Discussion 핵심 paraphrase 검증 (R6) → 본인 통과

## 재진 시점
- 다음 논문 1편 후 본 처방전 재발행
- 누적 3편 깨끗하게 끝나면 한 단계 dial 낮춤 검토
```

### 2) `self_deadline_checklist.md` (v1.3 신규, `paper_home/08_package/`)

```markdown
# 🗓️ 자가-마감 체크리스트 (Self-Deadline, 5–7일)

**Generated:** 2026-06-20 16:00 KST
**Paper:** paper-2026-001 / Brief Report / JKMS
**자가-마감일:** 2026-06-25 ~ 2026-06-27

> **워크숍 산출물 = submission-directed ≠ submission-ready.**
> 본 체크리스트는 워크숍 6시간 동안 통과한 항목을 5–7일 후 본인이 한 번 더 검증하도록 설계.

---

## ① 본인 사실 검증 (의학 floor — 1일차 권장)
- [ ] Mortality / safety / guideline claim 직접 full text 확인
- [ ] 약물 용량 / 상호작용 — 본인 1차자료 확인
- [ ] IRB 진술 — 승인 기관, 일자, 환자동의 면제 사유 확인

## ② Reporting checklist 부착 (1–2일차)
- [ ] STROBE / CONSORT / CARE / PRISMA / STARD / TRIPOD PDF 첨부
- [ ] checklist의 모든 item이 manuscript에 어디 있는지 row 기재

## ③ AI Use Disclosure 정확성 (2일차)
- [ ] 사용한 AI 모델명 (Claude Opus 4.7 / GPT-5 / Gemini 3.1 등) 정확
- [ ] 어느 단계에서 사용했는지 (draft / verify / critic / figure / 통계)
- [ ] 본인이 검증한 항목 명시

## ④ 결정적 검증 결과 재확인 (3–4일차)
- [ ] G1 abstract word count: AST {abstract_count}/{abstract_max} ✓
- [ ] G2 body word count: AST {body_count}/{body_max} ✓
- [ ] G2.6 ghost/orphan: ghosts={ghosts} orphans={orphans}
- [ ] R5 retracted citation 0건
- [ ] R6 mortality/safety claim — 본인 abstract+full text 통과

## ⑤ 통계 정합성 재확인 (4–5일차)
- [ ] Abstract 수치 = Results 수치 = Table 수치 (3-way agreement)
- [ ] CI / p-value 표기 일관성
- [ ] denominator / N 명시

## ⑥ 투고 직전 (5–7일차)
- [ ] 1차 저널 spec 최신 버전 재확인 (변경 가능성)
- [ ] Cover letter — 본인 sender info / reviewer 추천 (있으면)
- [ ] Blinded version identity scrub (이름/소속 0 hits)
- [ ] 이중 투고 0 — 본인 진술

---

## 본 워크숍 단계별 미해결 이슈

(`events.jsonl`에서 자동 추출 — 본 wrap 시점 open issues)
- [ ] {issue_1}
- [ ] {issue_2}

---

> 본 체크리스트의 모든 항목 통과 → 투고 시점 결정.
> 어느 한 항목이라도 unchecked → 투고 보류 + facilitator (or co-author) 상의.
```

**주의**: facilitator 워크숍 시연 시 G5 `md_to_docx`가 별도 호출되어 `manuscript_full.docx`까지 패키징. 참가자에게는 노출하지 않고 wrap 단계에서 자동 실행.

## HITL Event Emit (자기 자신)

```json
{"ts":"...","step":"wrap","event_type":"model_strength","skill":"hitl-dial-recommender","engine":"code-script","category":"calibration","severity":1,"description":"H3 recommended for next paper, risk_score=52.3"}
```

## 결정적 vs LLM 분리

- **결정적**: risk score 산출, hard guardrail 적용, dial mapping
- **LLM**: rationale 자연어 생성, 사용자 본인 노트 정제

## Floor (영구 — dial과 무관)

이 4영역은 **H0~H4 어느 위치에서도** 본인 결정:
- 임상 권고 / 가이드라인
- 약물 용량 / 제네릭
- IRB / 윤리 / 환자 동의
- Reference R6 (특히 mortality/safety/guideline claim)

## 자주 발생하는 함정

1. **Workshop wrap에서 events.jsonl 비어 있음** — 다른 skill에서 emit 누락. SKILL.md emit 표준 미준수
2. **paper_profile.json 누락** — 자동 dial이 H3 default로 떨어짐. journal_shortlist.md에서 자동 채워야 함
3. **첫 워크숍 권고를 너무 신뢰** — 1편 데이터로는 부정확. "재진 시점"에서 재발행 권고

## 다음 단계

- Workshop 종료: 본 처방전을 본인 디바이스에 보관
- 다음 논문 시작 시: paper_home 생성 + 본 처방전을 starting point dial로
- 1편 완료 시: 재실행 (사후 calibration)
