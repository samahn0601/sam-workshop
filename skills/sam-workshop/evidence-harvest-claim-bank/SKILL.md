---
name: evidence-harvest-claim-bank
description: >
  Use this skill at Step 2 (after Chat Deep Research) to convert raw research
  findings into a structured claim bank and source bank with stable claim IDs
  that all downstream skills (story-design, verify-reference-essential R6,
  critic, humanize) can reference. Trigger when user says "claim bank", 
  "evidence map 만들어줘", "근거 정리", "deep research 정리", "structured
  evidence", "claim_id", "source bank", or operates between Step 2 and Step 3
  of sam-workshop pipeline. Do not use for raw web search (use Chat Deep
  Research first) or for verification (use verify-reference-essential). Input:
  paper_home/02_research/deep_research.md + (optional) reference PDFs in
  00_intake/existing_pdfs/. Output:
  paper_home/02_research/{source_bank.jsonl, claim_bank.jsonl,
  evidence_table.md}. Pipeline position: sam-workshop Step 2.5 (between Deep
  Research and Outline). Medical context: ICMJE-aligned source-claim
  traceability, locked claim IDs for downstream factual drift detection,
  mortality/safety/guideline flagging. Trigger keywords: claim bank, source
  bank, evidence harvest, evidence map, 근거 정리, claim ID, deep research
  정리, claim mapping, supporting evidence.
---

# evidence-harvest-claim-bank (Tier 1 — Step 2 hand-off skill)

> **Step 2 → Step 3 hand-off의 결정적 봉합.** Deep Research raw markdown을 구조화된 claim/source bank로 변환. 모든 downstream skill이 같은 claim_id 공유 → R6 검증, critic, humanize에서 factual drift 추적 가능.

## 모드

| 모드 | 시간 | 산출 |
|---|---|---|
| `workshop-mini` | 15분 | 핵심 claim 10–20개 + source 5–15개 |
| `standard` | 30분 | + 자세한 limitation tagging + safety flag |
| `deep-audit` | 60분 | + verbatim quote 모든 claim + 가이드라인 cross-check |

## 입력

- `paper_home/02_research/deep_research.md` — Chat DR 결과
- (선택) `paper_home/00_intake/existing_pdfs/` — 본인 보유 PDF
- `paper_home/01_design/article_type.md` — 문맥 (claim 선별 우선순위)

## 절차 (workshop-mini, 15분)

### 1단계 (5분) — Source bank 추출

```
당신은 의학 evidence librarian입니다. 첨부 deep_research.md에서 모든 cited
source를 추출하여 source_bank.jsonl 생성:

각 source:
{
  "source_id": "S001",
  "type": "journal_article | guideline | government_db | book_chapter | preprint",
  "doi": "10.xxxx/...",
  "pmid": "...",
  "title": "...",
  "authors": ["LastName1", "LastName2"],
  "year": 2024,
  "journal": "...",
  "url": "...",
  "verification_status": "PENDING_VERIFY"  // verify-reference-essential에서 갱신
}

규칙:
- 중복 제거 (DOI/PMID 기준)
- type 정확히 분류
- 메타데이터 부족하면 그대로 표시 (LLM 추정 금지, "[INCOMPLETE]" 마크)
```

산출 → `paper_home/02_research/source_bank.jsonl`

### 2단계 (8분) — Claim bank 추출

```
당신은 의학 claim extractor입니다. deep_research.md에서 본 논문 작성에 사용할
claim을 추출하여 claim_bank.jsonl 생성:

각 claim:
{
  "claim_id": "C001",
  "claim_text": "한국 청소년 전자담배 사용률은 2018년 대비 2023년 2.3배 증가했다",
  "claim_type": "epidemiology | mechanism | clinical_outcome | guideline | methodology | comparison | safety | drug_efficacy",
  "risk_level": "high | medium | low",  // mortality/safety/guideline = high
  "guideline_or_safety_flag": false,
  "source_ids": ["S003", "S007"],
  "verbatim_support": "Park 2024 abstract: 'Among Korean adolescents, e-cigarette use rose from 2.7% in 2018 to 6.2% in 2023.'",
  "effect_size": "OR 2.3 (95% CI 2.1–2.5)",  // 있으면
  "limitations": "단면연구, 자가 보고",
  "intended_section": "Introduction §2",  // 어느 섹션에 들어갈지 잠정
  "review_status": "PENDING_HUMAN_RATIFY",
  "locked": false  // mortality/safety/guideline은 humanize 시 lock 후보
}

규칙:
- 모든 claim에 verbatim_support 필수 (없으면 "[NO_VERBATIM]" 마크 + risk_level=high)
- safety/mortality/guideline-changing claim은 자동으로 risk_level=high + guideline_or_safety_flag=true
- claim_id는 C001부터 순차
- 중복 claim 통합 (같은 주장은 1개)
```

산출 → `paper_home/02_research/claim_bank.jsonl`

### 3단계 (2분) — Evidence table (사람이 읽는 형식)

source_bank + claim_bank를 합쳐서 표 형식:

```markdown
# Evidence Table

## High-risk claims (mortality / safety / guideline)
| claim_id | claim | sources | flag |
|---|---|---|---|
| C003 | "SGLT2 억제제는 CKD 환자 사망률 30% 감소" | S005 (KDIGO 2024) | safety + guideline |

## Medium-risk
| claim_id | claim | sources |
|---|---|---|
| C001 | 한국 청소년 e-cig 사용률 2.3배 ↑ | S003, S007 |

## Verbatim 누락 ([NO_VERBATIM])
- C012: "..." → original source confirm 필요

## 통계
- Total claims: 15
- High-risk: 3
- Medium-risk: 9
- Low-risk: 3
- Verbatim 누락: 2 (C012, C014) — Step 5 verify에서 우선 검증
```

산출 → `paper_home/02_research/evidence_table.md`

## Output 표준

위 3 파일 + HITL emit.

## HITL Event Emit

```json
{"ts":"...","step":2,"gate":"A_design","event_type":"gate_pass","skill":"evidence-harvest-claim-bank","engine":"claude","category":"evidence_structure","severity":2,"description":"15 claims (3 high-risk, 9 medium, 3 low) from 12 sources. 2 missing verbatim flagged for Step 5.","time_to_fix_min":15}
```

## 결정적 vs LLM 분리

- **LLM**: claim/source 추출, type 분류, verbatim 발견, risk_level 판단
- **결정적**: 중복 DOI/PMID merge, claim_id 순차 부여, JSONL schema validation

## Solo + Claude-only

기본 Claude. 외부 도구 불필요.

## Floor (절대 위임 불가)

- **High-risk claim 검토** — guideline/safety/mortality claim의 verbatim_support는 본인이 abstract 직접 확인
- **Risk_level 판단 검증** — Claude가 medium 분류한 것 중 본인이 보기에 high면 승격
- **Locked claims 결정** — humanize 단계에서 lock할 claim 본인 표시

## Downstream 연결 (가장 중요한 가치)

이 skill의 산출물 → 다음 skill들의 입력:

| Skill | 사용 |
|---|---|
| `story-design` | claim_bank를 outline 섹션에 매핑 (evidence_map.md) |
| `verify-reference-essential` R6 | high-risk claim 자동 sampling |
| `critic-multi-persona` | claim_id 단위 critique |
| `humanize-en/ko` | locked claim_id의 의미 보존 |
| `verify-7layer` | full audit 시 claim 단위 추적 |

→ **claim_id는 워크숍 전체의 공통 단위**. 통일된 추적이 desk reject 면역력 핵심.

## Self-Gate A 체크리스트

- [ ] All claims have source_ids (또는 [NO_VERBATIM] 마크)
- [ ] High-risk claims 식별 완료
- [ ] Verbatim_support 인용 명시 (요약 X, abstract 인용)
- [ ] 중복 claim 통합
- [ ] Step 5 verify를 위한 우선 검증 list 생성

## 자주 발생하는 함정

1. **Verbatim 없이 paraphrase만** — 가장 위험. R6에서 잡힘. 추출 단계에서 "[NO_VERBATIM]" 표시 의무화
2. **Risk_level 과소 평가** — "guideline에 따르면"을 medium으로 → 모든 guideline 인용은 high
3. **Claim 중복** — 같은 주장이 4–5개 paraphrase로 분산 → 통합 필요
4. **Source 없이 LLM 메모리에서 인용** — 절대 금지. deep_research.md에 명시된 것만
5. **section 매핑 누락** — claim이 어느 섹션에 들어갈지 미정 → story-design에서 혼란

## 다음 단계

→ Self-Gate A2 → Step 3 story-design (claim_bank를 outline에 매핑)
