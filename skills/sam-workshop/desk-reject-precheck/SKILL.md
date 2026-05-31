---
name: desk-reject-precheck
description: >
  Use this skill for a quick pre-submission scan against 9 common desk
  rejection causes for medical journals. Trigger when user says "desk reject
  체크", "투고 전 점검", "submission precheck", "데스크 리젝트 위험", "투고
  전 마지막 점검", or operates near Self-Gate D of sam-workshop pipeline. Do
  not use as a substitute for verify-reference-essential or stats-consistency
  (those are deeper checks). Input: paper_home/04_draft/manuscript.md +
  paper_home/01_design/journal_shortlist.md. Output:
  paper_home/08_package/desk_reject_precheck.md. Pipeline position:
  sam-workshop Step 6 quick scan and Step 8 final scan / Self-Gate C and D.
  Medical context: ICMJE-aligned 9-item checklist, 1차 reviewer/editor가 가장
  먼저 보는 항목. Trigger keywords: desk reject, 데스크 리젝트, precheck,
  투고 전, submission scan, 마지막 점검.
---

# desk-reject-precheck (Tier 2 — 5분 quick scan)

> 의학 저널 desk reject 흔한 9가지 사유 빠른 점검. 본 점검은 verify-reference-essential, stats-consistency를 **대체하지 않으며** 그것들이 통과한 후의 cross-section scan.

## 9-item Checklist (LLM coach + AST audit meter — Hybrid v1.3)

| # | 사유 | 점검 | Backend |
|---|---|---|---|
| 1 | Scope 부적합 | journal_shortlist.md의 1차 저널 scope vs 본 manuscript fit | LLM only |
| 2 | Article type 불일치 | "Brief Report" 양식인데 5000w 본문 등 | LLM only |
| 3 | Word/abstract 한도 초과 | journal_specs.md vs 실측 word count | **LLM + AST (compliance_backend G1/G2)** |
| 4 | Reporting checklist 미부착 | CONSORT/STROBE/CARE/PRISMA 누락 | LLM only |
| 5 | AI 공시 누락 | journal AI 정책 vs ai_disclosure.md | LLM only |
| 6 | IRB / 윤리 진술 누락 | Methods §IRB 문구 | LLM only |
| 7 | COI / Funding 진술 누락 | manuscript 끝/Title page | LLM only |
| 8 | Reference 형식 위반 | journal-specific style (Vancouver / NLM / APA) | LLM only |
| 9 | 이중 투고 / 중복 출판 | 본인이 별도 학회/저널에 투고 안 했는지 | 본인 입력 |

**Hybrid 원칙 (v1.3 — 2026-05-03 3AI consult):** LLM이 정성적 review (false positive 잡음), deterministic AST가 정량적 hard metric (false alarm 차단). LLM-only를 AST-only로 *완전 대체* 절대 금지. AST가 markdown 오타로 false negative 내도 LLM coach가 동시에 작동.

## 모드

| 모드 | 시간 |
|---|---|
| `workshop-mini` | 5분 quick scan |
| `standard` | 15분 full audit |

## 입력

- `paper_home/04_draft/manuscript.md`
- `paper_home/01_design/journal_shortlist.md`
- `paper_home/02_research/journal_specs.md`
- `paper_home/08_package/ai_disclosure.md` (있으면)

## 절차 (5분)

### Phase A (1분) — Deterministic word-count badge (item #3 사전 산출)

`journal_specs.md`에서 abstract / body word limit을 읽은 뒤, **본 LLM 점검 직전**에 AST badge를 먼저 산출:

```bash
# G1 abstract (예: 한도 250)
python skills/sam-workshop/_shared/scripts/compliance_backend.py wordcount-abstract \
  --abstract paper_home/04_draft/abstract.md \
  --max 250

# G2 body (예: 한도 4000)
python skills/sam-workshop/_shared/scripts/compliance_backend.py wordcount-body \
  --manuscript paper_home/04_draft/manuscript.md \
  --max 4000
```

JSON 산출의 `count`, `max`, `workshop_grade`를 받아 item #3 row에 그대로 표기 ("AST: N words ≤ M ✓" 또는 "AST: N words > M ✗"). LLM은 narrative ("abstract feels appropriate length") 동시에 작성 → 한 줄에 두 값을 같이 보여줌.

**Markdown 오타로 AST가 0 word / 0 section 결과를 내면**: workshop_grade = "Fix before self-deadline" warn으로 자동 전이. LLM narrative는 별도 동작 → false negative에 의한 흐름 단절 없음.

### Phase B (4분) — LLM 9-item scan (Phase A 결과를 #3에 주입)

```
당신은 의학 저널 desk editor입니다. 첨부 manuscript와 journal_specs를 비교하여
9-item desk reject precheck:

1. Scope: journal scope vs manuscript topic (Pass/Fail + 사유)
2. Article type: 양식 vs 본문 (Pass/Fail)
3. Word count: AST 결과 [Phase A에서 주입] + LLM 정성 평가 (Pass/Fail + 실측 수치)
4. Reporting checklist: 해당 study design에 맞는 checklist 부착? (CONSORT/STROBE/CARE/PRISMA/STARD/TRIPOD)
5. AI 공시: journal AI policy vs ai_disclosure.md (Pass/Fail)
6. IRB / 윤리: Methods에 IRB 진술 (Pass/Fail)
7. COI / Funding: 진술 (Pass/Fail)
8. Reference 형식: journal style vs 실측 (Pass/Fail + 위반 예시)
9. 이중 투고: 본인 확인 진술 (사용자 입력 필요)

출력 표:
| # | item | Status (Workshop check passed / Fix before self-deadline / Human review required) | 사유 / audit_meter (있으면) |
|---|---|---|---|

Status 등급 (3단계, v1.3.1):
- "Workshop check passed" — 워크숍 자동 점검에서 즉시 차단 신호 없음
- "Fix before self-deadline" — 5–7일 내 본인 수정 가능 (auto_fixable / minor)
- "Human review required" — 본인 판단 필수 (clinical / ethical / score critical)

종합: "Human review required" ≥ 1 → 반드시 본인 판단 후 투고
       "Fix before self-deadline" ≥ 1 → 자가-마감 5–7일 동안 수정
       All "Workshop check passed" → submission-**directed** (절대 "submission-ready" 아님)
```

### Green = "Workshop check passed"의 정확한 의미 (v1.3.1, 3AI consult 반영)

> **Green은 본 워크숍 자동 점검에서 즉시 차단할 문제가 발견되지 않았다는 뜻입니다.**
> Green은 **다음을 보증하지 않습니다**:
> - 게재 가능 (editorial acceptance)
> - 통계적 타당성 (statistical validity)
> - 의학적 안전성 (medical safety)
> - 저널 승인 (journal approval)
> - 최종 제출 적합성 (submission readiness)
>
> **최종 판단과 책임은 저자에게 있습니다.**

Facilitator 응답 스크립트는 [FACILITATOR_SCRIPTS.md](../../../FACILITATOR_SCRIPTS.md) 참고.

## Output 표준

`paper_home/08_package/desk_reject_precheck.md`:

```markdown
# Desk Reject Precheck (Round N)

| # | Item | Status | 사유 / audit_meter |
|---|---|---|---|
| 1 | Scope | Workshop check passed | JKMS scope (general medicine) 부합 |
| 2 | Article type | Workshop check passed | Brief Report 2,847 words |
| 3 | Word count | Workshop check passed | LLM: "abstract feels appropriate length" / AST: 142 words ≤ 150 ✓ (G1) · 2,847 ≤ 3,500 ✓ (G2) |
| 4 | Reporting checklist | **Human review required** | STROBE 미부착 (관찰연구) |
| 5 | AI 공시 | Workshop check passed | ai_disclosure.md 작성됨 |
| 6 | IRB | **Human review required** | Methods §2에 IRB 번호만, 승인 기관명 누락 |
| 7 | COI/Funding | Workshop check passed | Title page 진술 |
| 8 | Reference 형식 | Workshop check passed | Vancouver |
| 9 | 이중 투고 | (본인 확인) | - |

## Human review required (반드시 본인 판단)
- #4: STROBE checklist 부착 (PDF) 필요
- #6: IRB 진술 보강

## Fix before self-deadline (5–7일 자가-마감 내)
- (없음)

## 종합
- 투고 차단: #4, #6 본인 판단 후
- "Workshop check passed" 등급은 submission-**directed** ≠ submission-**ready**. 자가-마감 5–7일 추가 점검 필수.
```

### audit_meter JSON 필드 (output에 함께 저장)

`compliance_backend.py wordcount-abstract` / `wordcount-body` JSON을 별도 필드로 보존:

```json
{
  "audit_meter": {
    "G1_abstract_wordcount_max": {
      "status": "pass", "count": 142, "max": 150, "workshop_grade": "Pass"
    },
    "G2_body_wordcount_max": {
      "status": "pass", "count": 2847, "max": 3500, "workshop_grade": "Pass",
      "included_sections": ["Background", "Methods", "Results", "Discussion"]
    }
  }
}
```

## HITL Event Emit

```json
{"ts":"...","step":8,"gate":"D_finish","event_type":"gate_fail","skill":"desk-reject-precheck","engine":"claude","category":"submission_readiness","severity":4,"description":"2 critical fails: #4 STROBE missing, #6 IRB statement weak"}
```

## Facilitator-run docx 패키징 — Step 7 Humanize & Package 마무리 (v1.3 신규, 참가자에게 비노출)

desk-reject-precheck Phase A+B 완료 후(step 7 마무리), **facilitator만** 다음을 호출해서 `manuscript_full.docx`를 자동 생성:

```bash
python skills/sam-workshop/_shared/scripts/md_to_docx.py \
  --paper-home paper_home/ \
  --double-spaced
```

산출: `paper_home/08_package/manuscript_full.docx` (TNR 12pt, 1in margins, double-spacing).

**참가자에게 노출 X**. 참가자는 17 skill 내에서 desk-reject-precheck 결과만 봄. 본 facilitator-run은 Cowork 백엔드에서 조용히 실행.

**Fallback (pandoc 또는 python-docx 미설치 등 facilitator 환경 이슈 발생 시)**:
- `[FACILITATOR_FALLBACK]` exit code 2 출력. facilitator는 워크숍 흐름 끊지 않고 "docx 패키징은 homework로 진행" 안내. 워크숍 KPI인 *교육 상품 안정성* 우선.

**왜 facilitator-only인가:**
- pandoc 설치 / python-docx 의존성 / Quarto bundle 위치 등 환경 변수가 너무 많음. 6h 워크숍에서 참가자가 직면하면 흐름 파괴.
- Dry-run (D-30) 결과 stable하면 D-21에 self-service 승격 검토 (Tier 2).

## Self-Gate D 체크리스트

- [ ] "Human review required" (#1, #2, #4, #5, #6, #7) 0건 또는 본인 판단 완료
- [ ] "Fix before self-deadline" (#3, #8) 0건 또는 5–7일 자가-마감 작업 리스트 추가
- [ ] #9 본인 진술 완료
- [ ] G1/G2 audit_meter 결과를 self-deadline 체크리스트에 복사

## 자주 발생하는 함정

1. **Reporting checklist 분실** — STROBE/CONSORT/CARE 등 PDF 부착 필수
2. **IRB 진술이 번호만** — 승인 기관, 일자, IRB 면제 사유까지
3. **AI 공시가 너무 모호** — 어떤 AI가 어디서 어떻게 사용되었는지 명시
4. **Word count가 references/legends 포함하는지 헷갈림** — journal_specs 기준 따름
5. **Vancouver vs NLM 차이 무시** — 미세하지만 desk editor 반환 사유

## 다음 단계

→ Self-Gate D 통과 → package-docx (.docx 조립)
