---
name: journal-fit-check
description: >
  Use this skill when a medical-faculty author is at the start of a manuscript
  and needs to lock article type and target journal short list. Trigger when the
  user says "타깃 저널 정해줘", "어느 저널이 맞을까", "article type 추천", 
  "journal fit", "저널 후보", "submission target", or operates in Step 1 Idea
  Lock of the sam-workshop pipeline. Do not use for in-depth literature search
  (use Chat Deep Research) or for already-locked submission packaging (use
  desk-reject-precheck and the Step 7 packaging flow). Input: paper_home/00_intake/topic_seed.md plus author's
  available data/case description. Output:
  paper_home/01_design/{idea_variants.md, article_type.md, journal_shortlist.md}.
  Pipeline position: sam-workshop Step 1 / Self-Gate A. Medical context: Korean
  medical faculty, ICMJE-compliant journals, KAMJE-indexed candidates considered.
  Mandatory check on AI-disclosure policy of each candidate journal. Trigger
  keywords: 저널, journal, 타깃 저널, target journal, article type, IF, ESL,
  KAMJE, KoreaMed, KJMS, JKMS, JMIR.
---

# journal-fit-check (Step 1)

> 의대 교수가 워크숍 시작 시 본인 주제를 가져왔을 때, **30분 안에 article type 잠정 + 저널 short list 2–3개**를 결정하도록 돕는다. 단독 저자 모드, AI 초보 가정.

## 모드 (3-tier)

| 모드 | 시간 | 용도 |
|---|---|---|
| `workshop-mini` | 10분 | 워크숍 표준 — short list 2–3개 |
| `standard` | 25분 | 사후 작업 — full landscape + 5 후보 |
| `deep-audit` | 45분+ | 본격 투고 전 — IF 추이, RR, accept rate |

기본은 `workshop-mini`.

## 입력

- `paper_home/00_intake/topic_seed.md` — 한 문장 주제
- (선택) 본인 보유 데이터/케이스 description (구두로)
- (선택) 평소 투고하시는 저널 1–2개

## 절차 (workshop-mini, 10분)

### 1.1 Idea variants 생성 (2분)

본인 시드 → 2–3개 idea variant 생성. 각 variant는:
- thesis 1문장
- 가능한 article type 후보 1–2개
- 본인 보유 material (데이터/케이스/주장)에 맞는지 표시

산출 → `paper_home/01_design/idea_variants.md`

### 1.2 Article type 잠정 결정 (2분)

| 본인 보유 | 권고 article type | 시간 가능성 |
|---|---|---|
| 후향 데이터 (N≥100, IRB OK) | Brief Report (Original) | IMRaD 골격 + Discussion 1차 |
| 후향 데이터 (N<100) | Letter / Commentary | Submission-ready |
| 본인 케이스 1건 + 사진/검사 | Case Report | Submission-ready (환자 동의서 + CARE 체크 전제) |
| 본인 의견 강함 + 근거 5–10편 | Editorial / Viewpoint | Submission-ready |
| 주제 종합 (선행연구 30+편) | Narrative Review (⚠️ 초청제 다수) | outline + 핵심 근거맵 (1차 draft는 사후) |
| 메타분석 protocol | Systematic Review | Protocol + 검색전략 draft |

→ 본인이 선택. AI는 권고만.
※ **IRB 불명/미승인은 article type으로 우회할 문제가 아니라 제출 가능성 red flag** — 기관 IRB 확인 선행.
※ Narrative Review는 다수 저널이 초청(invited)제 — 비초청(unsolicited) 접수 여부를 저널 공식 페이지에서 확인 후 선택.

산출 → `paper_home/01_design/article_type.md`

### 1.3 Scope-Fit Gate + Journal short list 2–3개 (5분) ★ desk reject 1차 방어선

> **조건 충족(IF·word limit·정책) ≠ scope fit.** desk reject의 흔한 사유는 "outside scope / narrow focus / limited innovation" — 형식이 아니라 적합성이다. 각 후보마다 Scope-Fit 4종을 먼저 채운다.

**필수 ① — Scope-Fit Gate (후보당 4종):**
- **Aims & Scope 적합 논증** — 공식 Aims & Scope 1줄 요약 + "이 원고가 이 저널 독자에게 주는 새 가치" 1문장 (공식 페이지 미확인 시 `잠정` 표기)
- **유사 논문 실증** — 최근 1–2년 이 저널에 비슷한 유형·주제 논문 1–2편 (제목 수준; 기억/빠른 확인 한도, 못 찾으면 `Step 2에서 확인` 표기 — 못 찾는 것 자체가 red flag 신호)
- **Desk-reject red flag 1개** — "에디터가 이 원고를 거절한다면 그 사유는?" (악마의 변호인)
- **Fit verdict** — `Strong` / `Possible` / `Risky`

**필수 ② — 조건:**
- **저널명 (full + abbreviation)**
- **AI 사용 공시 정책** ★ — accept / disclosure required / strict. 공식 instructions 인용으로 확정하기 전까지 `잠정` 표기 (워크숍 중 미확인이면 `미확인`으로 남기고 투고 전 확정)
- **Word limit** (article type별)
- **KAMJE/KoreaMed 인덱스** 여부
- **Reporting checklist** (CONSORT/STROBE/etc.)

**선택 (가능하면 — 추정 금지, 모르면 비움):**
- IF (연도·출처 명기 시에만) / ESL 친화성 / 평균 turnaround
- **추천 사유** 1–2 문장

산출 → `paper_home/01_design/journal_shortlist.md`

### 1.4 Self-Gate A1 결정 (1분)

본인이 결정:
- [ ] Article type 잠정: ___
- [ ] Target journal short list: 1차 ___ / 2차 ___ / 3차 ___
- [ ] 5h 워크숍 안 commitment: "오늘 ___까지 도달한다"

→ `paper_home/01_design/decision_history.md`에 기록

## 한국 의대 교수 자주 투고하는 저널 (예시 seed — 최신 아님 · 투고 전 공식 페이지 당일 확인 필수)

| 저널 | IF | 분야 | AI 정책 | ESL |
|---|---|---|---|---|
| JKMS (J Korean Med Sci) | ~3 | General medicine | Disclosure required | ★★★ |
| KJIM (Korean J Intern Med) | ~2.5 | Internal medicine | Disclosure required | ★★★ |
| KJFM (Korean J Family Med) | ~2 | Family medicine | Disclosure required | ★★★ |
| Yonsei Med J | ~3 | General | Disclosure required | ★★★ |
| JMIR (J Med Internet Res) | ~7 | Digital health | Strict, AI tools listed | ★★ |
| JMIR AI | new | AI in medicine | Welcomes AI, full disclosure | ★★ |
| NTR (Nicotine Tob Res) | ~5 | Tobacco | Disclosure required | ★★ |
| BMC Primary Care (구 BMC Family Practice, 2022 개명) | 2.6 (2024 JIF) | Family medicine / primary care | Disclosure | ★★ |
| Diabetes Metab J | ~3 | Endocrinology | Disclosure | ★★ |

→ 표의 IF·정책은 작성 시점 값(추정 포함) — **확정은 저널 공식 Instructions for Authors 직접 인용으로만** (연도·출처 없는 IF 신뢰 금지). 저널별 상세 specs(word limit·섹션 구성·AI 정책 원문)는 Step 2 Deep Research에서 공식 페이지 기준으로 수집.

## Solo + Claude-only fallback

기본 동작이 Claude-only. 외부 도구 불필요.

선택적 보조:
- 외부 LLM·학교 멀티모델 포털(가용 시)에 후보 저널별 **"이 원고를 desk reject 한다면 사유는?"**만 교차 질문 (특정 모델 무관 · 결과는 참고용, 확정은 공식 페이지 인용)

## Output 표준

### `idea_variants.md`
```markdown
# Idea Variants
## V1 — {thesis}
- Article type 후보: ...
- Material 적합성: ...
## V2 — {thesis}
...
```

### `article_type.md`
```markdown
# Article Type 잠정 결정
- 선택: {type}
- 사유: ...
- 5h 도달점: ...
```

### `journal_shortlist.md`
```markdown
| 순위 | 저널 | Scope fit (1문장) | Fit verdict | Reject risk | AI 정책 | Word limit | 추천 사유 |
|---|---|---|---|---|---|---|---|
| 1차 | JKMS | 일반의학 + 한국 임상 데이터 환영 — 본 주제 부합 | Strong | 유사 논문 미확인 시 novelty 의문 | Disclosure required (잠정) | 3500 | ESL 친화, KAMJE, ICMJE 표준 |
| 2차 | ... |
| 3차 | ... |
```

## HITL Event Emit

skill 종료 시:
```json
{"ts":"...","paper_id":"...","step":1,"gate":"A_design","event_type":"gate_pass","skill":"journal-fit-check","engine":"claude","category":"design_lock","severity":1,"description":"article type=Brief Report, journals=[JKMS,KJIM,Diabetes Metab J]","time_to_fix_min":10}
```

## 결정적 vs LLM 분리

- **LLM 판단**: idea variant 생성, article type 권고, 저널 권고 사유, ESL 친화성 평가
- **결정적**: IF lookup (저널 사이트 또는 본인 입력), KAMJE 인덱스 (KAMJE 사이트 lookup), AI 정책 (저널 instructions for authors 직접 인용)

→ AI 정책은 **저널 공식 instructions 페이지를 직접 인용**하라고 사용자에게 요청. 메모리에서 추정 금지.

## Self-Gate A1 체크리스트

- [ ] **1차 저널 Aims & Scope를 공식 페이지에서 확인 + fit 1문장 작성** (공식 scope 확인 전 1차 확정 금지)
- [ ] 후보마다 desk-reject red flag 1개 + Fit verdict 기록
- [ ] Article type이 5h 안에 도달 가능한가
- [ ] Target 저널 1차의 AI 정책 확인 (공식 인용 기준; 미확인이면 `미확인` 표기 → 투고 전 확정)
- [ ] Word limit이 본인 material에 맞는가
- [ ] Reporting checklist (CONSORT/STROBE) 매칭 확인
- [ ] AI disclosure 문구 표준 미리 본인 인지

## 자주 발생하는 함정

1. **article type을 너무 넓게** — 5h 안에 review 1차 draft까지만 약속, submission-ready 아님
2. **저널 AI 정책 미확인** — 일부 저널은 critic·draft·figure에 AI 사용 자체를 제한. 사전 확인 필수
3. **IF 우선** — 의대 교수는 본인 도메인 영향력 + 평균 turnaround 더 중요. IF만으로 결정 X
4. **ESL 비친화 저널** — 영문 폴리싱 부담 큼. ESL 점수 확인
5. **조건 충족 = fit 착각** — IF·word limit·정책이 다 맞아도 scope가 어긋나면 desk reject ("outside scope, narrow focus, limited innovation"). Scope-Fit Gate를 건너뛰지 말 것 — 실제 투고 사고 사례에서 추가된 방어선

## 다음 단계 (Self-Gate A 통과 시)

→ Step 2 Deep Research + journal_specs 수집
