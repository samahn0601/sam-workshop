---
name: verify-reference-essential
description: >
  Use this skill when a medical manuscript needs reference verification at the
  desk-rejection prevention level: DOI existence, PubMed metadata mismatch,
  ghost/orphan citations, citation chimera, retracted papers, and paraphrase
  fabrication (whether cited abstracts actually support nearby claims). Trigger
  when user says "reference 검증", "DOI 확인", "인용 검증", "참고문헌 확인",
  "ghost citation", "retracted paper", "verify references", "citation hallucination",
  "paraphrase fabrication", or operates in Step 5 Verify of the sam-workshop
  pipeline. Do not use this skill for general literature search (use Chat Deep
  Research) or for full 7-Layer audit (use verify-7layer). Input:
  paper_home/04_draft/{manuscript.md or .docx} +
  paper_home/04_draft/references.{txt,bib}. Output:
  paper_home/05_verify/{refcheck_refs.csv, refcheck_issues.md,
  r6_claim_support.jsonl, verification_certificate.md}. Pipeline position:
  sam-workshop Step 5 / Self-Gate B. Medical context: Desk rejection from
  medical journals frequently triggered by fabricated DOIs, citation chimera,
  retracted citations, and unsupported paraphrases. Mortality/safety/guideline
  claims must NOT be passed on abstract-only check. Mandatory pass before Step 6
  Critic. Trigger keywords: reference, 인용, 참고문헌, DOI, PMID, ghost, orphan,
  retracted, 철회, paraphrase, citation chimera, abstract verify.
---

# verify-reference-essential (Step 5)

> **Reviewer는 AI 의심 원고에서 reference를 가장 먼저 본다.**
> R1–R6 6-Layer로 desk reject 면역을 30분 안에 확보. Sam Workshop의 핵심 skill.

## R1–R6 정의

| Layer | 목적 | 도구 |
|---|---|---|
| **R1** DOI 실재 | DOI가 실제 존재? | Crossref API (비-Crossref DOI — 예: DataCite — 는 doi.org resolve로 수동 확인) |
| **R2** 메타 정합 | title/authors/year/journal 일치? | PubMed esummary + Crossref |
| **R3** Ghost / Orphan | 본문↔reference list 상호 대응? | Script regex |
| **R4** Citation chimera | DOI는 실재하나 다른 논문 메타 섞임? | metadata diff |
| **R5** Retracted | 철회 논문 인용? | PubMed publication_type + **R5b Crossref update-to 교차**(v1.4.1 — 비-MEDLINE 갭 보조, PMID 없어도 DOI만으로 확인; 실패 시 `[R5B_UNCHECKED]` = PASS 집계 금지). Retraction Watch 전수 대조는 deep-audit |
| **R6** Paraphrase fabrication | 인용 주장이 실제 abstract 지원? | abstract fetch + Claude semantic |

## 모드

| 모드 | 시간 | 범위 |
|---|---|---|
| `workshop-mini` | 30분 | R1-R5 전수 + R6 위험 기반 5–10개 샘플 |
| `standard` | 60분 | + R6 모든 Discussion 인용 |
| `deep-audit` | 120분+ | + 전수 R6 + full text 확인 |

기본 `workshop-mini`.

> **워크숍 20명 단체 운영(3AI 합의)**: 동시 라이브 호출은 NCBI 무키 **3 req/s(공유 IP)** 에 막힌다 → **강사 데모(사전 산출물 활용·라이브 1~2개) + 참가자 본인 초안 ref 1~3개 가벼운 실행 + 429 시 Degraded Mode(수동 top-5)**. NCBI API 키 전원 발급은 **비권장**(가입 마찰 + 같은 NAT에서 키별 독립 할당 보장 불확실). 운영 대본: `FACILITATOR_SCRIPTS.md` "참조검증 단체 실습 운영".

## 입력

- `paper_home/04_draft/manuscript.md` — **workshop-mini는 `.md` 우선.** `.docx`만 있으면 먼저 `.md`로 변환(Claude가 수행, 원본 `.docx`는 읽기 전용 보존) 후 실행 — 변환 실패 시 R3·R6는 `INCOMPLETE`
- `paper_home/04_draft/references.txt` (또는 `.bib`)

## 절차 (workshop-mini, 30분)

### Phase 1 (3분) — Preflight: 파일·환경·이메일

```bash
ls paper_home/04_draft/
# manuscript.md, references.txt 확인 (paper_home이 안 보이면 위치부터 탐색·조정)
python --version
# Python 3.9+ 확인 + ${CLAUDE_SKILL_DIR}/../_shared/scripts/ 에 스크립트 존재 확인
```

연락 가능한 이메일 입력 (NCBI E-utilities `tool/email` 식별용 스크립트 인자 — 아래 Phase 2b에서 **이 값으로 치환**해 실행, 더미 예시 그대로 실행 금지).

### Phase 2 (10분) — R1–R5 자동 검사 (Code Phase)

#### Phase 2a (1분) — R3 deterministic ghost/orphan badge (compliance_backend G2.6)

`ref_verify_pubmed.py`도 R3을 검사하지만, v1.3에서 **bracket-range 확장 + ref list `N.` 정규식**까지 강화한 결정적 백엔드를 추가로 호출:

```bash
python ${CLAUDE_SKILL_DIR}/../_shared/scripts/compliance_backend.py citation-integrity \
  --manuscript paper_home/04_draft/manuscript.md \
  --refs       paper_home/04_draft/references.txt
```

> 경로 규칙: 공유 스크립트는 **이 스킬 폴더의 형제 폴더 `_shared`** 에 있다 (`${CLAUDE_SKILL_DIR}` = 이 SKILL.md가 있는 폴더). 셸(특히 PowerShell)이 이 변수를 자동 확장하지 않을 수 있으므로 **Claude가 실제 절대경로로 치환해 실행**한다. 절대경로·홈(`~`)·repo root·`sam-workshop` 우산 폴더 가정 금지.

JSON 산출:
```json
{
  "name": "citation_reference_integrity", "status": "fail",
  "message": "본문 인용 [9] 있으나 ref list에 항목 없음 (ghost); ref list에 항목 [7] 있으나 본문 미인용 (orphan)",
  "evidence": {"cited_count": 8, "ref_count": 7, "ghost_citations": [9], "orphan_references": [7]},
  "workshop_grade": "Human review required"
}
```

`workshop_grade`가 "Human review required"면 R3 deterministic 결과를 `refcheck_issues.md` 상단에 prepend (LLM coach가 동시에 보는 input).

#### Phase 2b (9분) — R1, R2, R4, R5 + R3 LLM cross-check (PubMed)

```bash
python ${CLAUDE_SKILL_DIR}/../_shared/scripts/ref_verify_pubmed.py \
  --manuscript paper_home/04_draft/manuscript.md \
  --references paper_home/04_draft/references.txt \
  --email <Phase 1에서 받은 이메일> \
  --r6-sample 8 \
  --out paper_home/05_verify/
```

> 단체 실습 주의: 같은 회장 IP에서 다수가 동시 실행하면 NCBI/Crossref가 429(rate limit)를 줄 수 있다 (API key 없는 E-utilities는 3 req/s). 실패 시 재시도는 1회만, 간격을 두고 — 지속되면 아래 **Degraded Mode**로.

산출:
- `refcheck_refs.csv` — 전체 reference R1–R5 결과
- `refcheck_issues.md` — high / medium severity 이슈 정리 (G2.6 결과를 상단 prepend)
- `r6_claim_support.jsonl` — R6 검증 대기 (다음 단계)
- `verification_certificate.md` — pass/fail 요약

**Hybrid 원칙 (v1.3):** compliance_backend G2.6은 deterministic ghost/orphan을 정확하게 잡고, ref_verify_pubmed.py R3은 LLM precheck로 false negative를 보완. 두 결과 일치하면 신뢰도↑, 불일치하면 LLM 출력에 (G2.6 결과)를 그대로 인용.

#### ⚠️ Degraded Mode — 스크립트/네트워크 실패 시 (fail-closed)

Python 미설치·스크립트 미발견·PubMed/Crossref timeout·429가 **재시도 1회 후에도** 지속되면, 디버깅에 3분 이상 쓰지 말고 즉시 전환:

1. **R3만 로컬 가능하면 수행** (compliance_backend는 네트워크 불필요).
2. 위험 상위 **5개 reference만** doi.org·PubMed 웹을 **직접 조회**해 R1·R2 수동 확인 (브라우저/웹검색 — 출처 화면 기준).
3. **certificate Status = `INCOMPLETE_EXTERNAL_CHECK`** 로 기록 — **PASS 금지.** (네트워크 장애는 원고 오류가 아니므로 FAIL도 아님 — 구분 기록.) Required next step에 "네트워크 회복 후 동일 명령 재실행" 명시.
4. **하지 않는 것**: LLM 기억으로 DOI·메타·철회 여부 판정(검증 아님) / 의존성 자동 설치(pip install) / full text 크롤링 / 원본 `.docx` 직접 수정.

→ 외부 검증이 미완이면 Self-Gate B를 통과할 수 없다. "검증한 척"이 가장 위험하다.

### Phase 3 (10분) — R6 Paraphrase 검증 (Claude Phase)

`r6_claim_support.jsonl`을 Claude에 입력:

```
이 r6_claim_support.jsonl을 읽고, 각 항목에 대해:
- 주장 문장 vs 인용된 abstract를 비교
- verdict 5분류: Supported / Partially supported / Not supported / Contradicted / Cannot judge from abstract
- evidence_span (abstract에서 지원/모순 근거 문구) 인용
- problem (있으면)
- recommended_action (keep | revise claim | replace citation | check full text)

CRITICAL:
- abstract만으로 확인 불가 → "Cannot judge from abstract"로 표시 (pass 처리 X)
- mortality / safety / guideline claim → abstract만으로 통과 절대 금지
- "아마 맞다"고 판단해도 evidence_span이 없으면 pass X
```

산출 갱신: `r6_claim_support.jsonl`의 `verdict` 필드 채움 + `r6_summary.md` 생성

### Phase 4 (5분) — Self-Gate B 결정

본인이:
- [ ] 모든 R1–R5 high severity 항목 결정 (수정/교체/제거)
- [ ] R6 "Not supported / Contradicted" 항목 → 본문 수정 또는 인용 교체
- [ ] R6 "Cannot judge" 항목 → full text 확인 follow-up 표시
- [ ] mortality/safety/guideline 주장은 본인이 직접 abstract+full text로 통과 결정

→ verification_certificate.md 갱신: PASS / FAIL / **INCOMPLETE_EXTERNAL_CHECK** (외부 검증 미완 — PASS 불가, Degraded Mode 참조)

### Phase 5 (2분) — HITL emit

스크립트가 자동으로 `events.jsonl` 갱신.

## R6 위험 기반 샘플링 7 카테고리

스크립트가 다음 패턴 매칭으로 자동 우선순위:

1. **수치/효과크기** ("reduced mortality by 30%", "OR 1.42") — 0순위 키워드: mortality, survival, adverse, complication, harm/benefit, recommend
2. **Causal claim** ("X causes Y", "leads to")
3. **Strong claim** ("first", "only", "definitive", "gold standard")
4. **Guideline / consensus** ("current guidelines recommend")
5. **Discussion 과장된 해석**
6. **AI가 새로 추가한 reference**
7. **DOI/meta mismatch 의심**

각 패턴마다 risk_score +1. 점수 높은 순으로 N개 샘플.

## R6 Claude 의미 검증 프롬프트 (표준)

```
You are checking whether a cited PubMed abstract supports a paraphrased claim
in a medical manuscript.

Use only the supplied title and abstract. Do not use outside knowledge.

Classify the relationship between the manuscript claim and the cited abstract
as one of:
1. Supported
2. Partially supported
3. Not supported
4. Contradicted
5. Cannot judge from abstract

Check:
- population match
- intervention/exposure match
- comparator match
- outcome match
- direction of effect
- magnitude or numeric claim
- study design
- whether the manuscript overstates the abstract

Return JSON:
{
  "claim_id": "...",
  "verdict": "...",
  "confidence": "low|medium|high",
  "evidence_span": "...",
  "problem": "...",
  "recommended_action": "keep|revise claim|replace citation|add citation|check full text"
}

CRITICAL: If the abstract does not contain the information needed, set verdict
to "Cannot judge from abstract". Do not guess. Mortality, safety, or guideline
claims must NEVER be marked Supported on abstract-only evidence; they require
full text follow-up.
```

## Output 표준

### `verification_certificate.md`
```markdown
# Verification Certificate

- Status (R1-R5): PASS | FAIL | INCOMPLETE_EXTERNAL_CHECK
- Total references: N
- High severity: N
- Medium severity: N
- R6 sampled: N
- R6 verdict distribution: Supported X / Partially X / Not supported X / Contradicted X / Cannot judge X
  (상세: r6_claim_support.jsonl verdict + r6_summary.md)

## Required next step
1. R1-R5 high 항목 본인 결정
2. R6 Not supported/Contradicted 본문 수정
3. R6 Cannot judge → full text 확인 follow-up
4. Self-Gate B 통과 결정
```

## HITL Event Emit

스크립트가 자동:
```json
{"ts":"...","paper_id":"...","step":5,"gate":"B_draft","event_type":"gate_pass","skill":"verify-reference-essential","engine":"code-script+pubmed","category":"reference_integrity","severity":2,"description":"R1-R5: 0 high, 2 medium. R6 prepped 8 samples."}
```

추가로 R6 verdict 별도 emit (Claude phase):
```json
{"event_type":"hallucination","location":"discussion_claim","severity":4,"detected_by":"r6_paraphrase_check","description":"Claim about mortality benefit not supported by abstract; reference 23 replaced.","fixed":true}
```

## 결정적 vs LLM 분리 (가장 중요한 원칙)

| 검증 항목 | 도구 |
|---|---|
| DOI 실재 | Crossref API (결정적) |
| PMID 실재 | PubMed esearch (결정적) |
| Title/year/journal 일치 | esummary + 비교 (결정적) |
| Ghost/Orphan (R3) | **compliance_backend.citation_reference_integrity (결정적, v1.3 강화)** + ref_verify_pubmed.py regex (결정적) |
| Retracted | PubMed publication_type (결정적) |
| Citation chimera 의심 | metadata diff score (결정적) |
| **Paraphrase 의미 일치** | **Claude semantic (LLM)** ← R6만 |

→ "Claude가 DOI 맞다고 했다"는 검증이 아니다. 반드시 Crossref/PubMed에서 직접.

## Self-Gate B 체크리스트

- [ ] **외부 검증 완결** — certificate가 `INCOMPLETE_EXTERNAL_CHECK`면 통과 불가 (재실행 후 재판정)
- [ ] 모든 R1–R5 high severity 처리
- [ ] R6 Not supported / Contradicted 0건 (또는 본문 수정 완료)
- [ ] mortality/safety/guideline 주장 본인 full text 확인
- [ ] verification_certificate.md PASS
- [ ] HITL events.jsonl 업데이트

## Floor (절대 위임 불가)

- Mortality / safety / guideline 주장의 R6 통과 — **항상 본인** (abstract만으로 자동 통과 금지)
- Retracted citation 발견 시 — **본인 결정** (제거 vs 교체 vs 유지+사유 명시)

## 자주 발생하는 함정

1. **DOI는 resolve되나 다른 논문** (chimera) — R4에서 잡힘
2. **Reference list는 깨끗하나 본문에 안 인용** — R3 orphan
3. **본문 [12]인데 reference list 11개만** — R3 ghost
4. **AI가 만든 reference가 PubMed에 있는 다른 논문 metadata 섞음** — R4 high
5. **Retracted 논문 인용 (notice 없이)** — R5
6. **Discussion에 "X가 사망률 30% 감소"인데 인용 abstract는 ICU LOS 보고** — R6 Not supported

## 다음 단계

→ Self-Gate B 통과 → Step 6 Multi-Engine Critic
