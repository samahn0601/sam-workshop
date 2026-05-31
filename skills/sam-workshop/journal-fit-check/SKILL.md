---
name: journal-fit-check
description: >
  Use this skill when a medical-faculty author is at the start of a manuscript
  and needs to lock article type and target journal short list. Trigger when the
  user says "타깃 저널 정해줘", "어느 저널이 맞을까", "article type 추천", 
  "journal fit", "저널 후보", "submission target", or operates in Step 1 Idea
  Lock of the sam-workshop pipeline. Do not use for in-depth literature search
  (use Chat Deep Research) or for already-locked submission packaging (use
  package-docx). Input: paper_home/00_intake/topic_seed.md plus author's
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

### 1.1 Idea variants 생성 (3분)

본인 시드 → 3–5개 idea variant 생성. 각 variant는:
- thesis 1문장
- 가능한 article type 후보 1–2개
- 본인 보유 material (데이터/케이스/주장)에 맞는지 표시

산출 → `paper_home/01_design/idea_variants.md`

### 1.2 Article type 잠정 결정 (2분)

| 본인 보유 | 권고 article type | 시간 가능성 |
|---|---|---|
| 후향 데이터 (N≥100, IRB OK) | Brief Report (Original) | IMRaD 골격 + Discussion 1차 |
| 후향 데이터 (N<100) 또는 IRB 불명 | Letter / Commentary (RCT 재해석) | Submission-ready |
| 본인 케이스 1건 + 사진/검사 | Case Report | Submission-ready |
| 본인 의견 강함 + 근거 5–10편 | Editorial / Viewpoint | Submission-ready |
| 주제 종합 (선행연구 30+편) | Narrative Review | 1차 draft 완성 |
| 메타분석 protocol | Systematic Review | Protocol + 검색전략 draft |

→ 본인이 선택. AI는 권고만.

산출 → `paper_home/01_design/article_type.md`

### 1.3 Journal short list 2–3개 (4분)

각 후보에 대해:
- **저널명 (full + abbreviation)**
- **IF (가장 최근)**
- **AI 사용 공시 정책** (필수 ★) — accept / disclosure required / strict
- **Word limit** (article type별)
- **ESL 친화성** (한국 의대 교수 투고 경험)
- **KAMJE/KoreaMed 인덱스** 여부
- **평균 turnaround** (가능하면)
- **Reporting checklist** (CONSORT/STROBE/etc.)
- **추천 사유** 1–2 문장

산출 → `paper_home/01_design/journal_shortlist.md`

### 1.4 Self-Gate A1 결정 (1분)

본인이 결정:
- [ ] Article type 잠정: ___
- [ ] Target journal short list: 1차 ___ / 2차 ___ / 3차 ___
- [ ] 5h 워크숍 안 commitment: "오늘 ___까지 도달한다"

→ `paper_home/01_design/decision_history.md`에 기록

## 한국 의대 교수 자주 투고하는 저널 (사전 정비 — 부분, 확대 예정)

| 저널 | IF | 분야 | AI 정책 | ESL |
|---|---|---|---|---|
| JKMS (J Korean Med Sci) | ~3 | General medicine | Disclosure required | ★★★ |
| KJIM (Korean J Intern Med) | ~2.5 | Internal medicine | Disclosure required | ★★★ |
| KJFM (Korean J Family Med) | ~2 | Family medicine | Disclosure required | ★★★ |
| Yonsei Med J | ~3 | General | Disclosure required | ★★★ |
| JMIR (J Med Internet Res) | ~7 | Digital health | Strict, AI tools listed | ★★ |
| JMIR AI | new | AI in medicine | Welcomes AI, full disclosure | ★★ |
| NTR (Nicotine Tob Res) | ~5 | Tobacco | Disclosure required | ★★ |
| BMC Family Practice | ~3 | Family medicine | Disclosure | ★★ |
| Diabetes Metab J | ~3 | Endocrinology | Disclosure | ★★ |

→ 저널별 specs는 Step 2 `journal-specs-fetch`에서 자동 수집.

## Solo + Claude-only fallback

기본 동작이 Claude-only. 외부 도구 불필요.

선택적 보조:
- Gemini grounding으로 "{저널명} AI policy 2026" 빠른 cross-check (선택)

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
| 순위 | 저널 | IF | AI 정책 | Word limit | ESL | 추천 사유 |
|---|---|---|---|---|---|---|
| 1차 | JKMS | 3.0 | Disclosure required | 3500 | ★★★ | ESL 친화, KAMJE, ICMJE 표준 |
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

- [ ] Article type이 5h 안에 도달 가능한가
- [ ] Target 저널 1차의 AI 정책 확인 완료
- [ ] Word limit이 본인 material에 맞는가
- [ ] Reporting checklist (CONSORT/STROBE) 매칭 확인
- [ ] AI disclosure 문구 표준 미리 본인 인지

## 자주 발생하는 함정

1. **article type을 너무 넓게** — 5h 안에 review 1차 draft까지만 약속, submission-ready 아님
2. **저널 AI 정책 미확인** — 일부 저널은 critic·draft·figure에 AI 사용 자체를 제한. 사전 확인 필수
3. **IF 우선** — 의대 교수는 본인 도메인 영향력 + 평균 turnaround 더 중요. IF만으로 결정 X
4. **ESL 비친화 저널** — 영문 폴리싱 부담 큼. ESL 점수 확인

## 다음 단계 (Self-Gate A 통과 시)

→ Step 2 Deep Research + journal_specs 수집
