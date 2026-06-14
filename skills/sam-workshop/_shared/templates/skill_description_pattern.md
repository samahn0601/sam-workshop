# Skill Description 7요소 표준 (자동 트리거 정확도용)

모든 sam-workshop skill의 `description` 필드는 다음 7요소를 포함한다 (skill-creator로 benchmark 후 정밀 조정).

## 7요소

1. **When to use** — 자연어 트리거 (사용자가 어떤 말을 했을 때 발화?)
2. **When NOT to use** — 오발화 방지 (다른 skill이 더 적합한 경우 명시)
3. **Input artifact** — 어떤 파일/내용을 입력으로 받는가
4. **Output artifact** — 어떤 파일/구조를 산출하는가
5. **Pipeline 위치** — sam-workshop 10-step 중 어디
6. **Self-Gate** — A/B/C/D 중 어느 게이트
7. **Medical context** — 의학 논문 특성 (예: 환자 안전, ICMJE, KAMJE)

## 표준 description 양식

```yaml
description: >
  [When to use 1-2문장]. Trigger when the user is in [pipeline 위치] and asks
  about [핵심 의도]. Use this when manuscript [구체 상황].
  Do not use when [when NOT to use 명시].
  Input: [input artifact path/format]. Output: [output artifact path/format].
  Pipeline position: Step [N] / Self-Gate [X].
  Medical context: [의학 논문 특수성, 예: ICMJE references / clinical safety / etc.].
  Trigger keywords: [한국어 트리거 5-10개], [영문 트리거 3-5개].
```

## 예시 (`verify-reference-essential`)

```yaml
description: >
  Use this skill when the user is preparing a medical manuscript and needs to
  verify references for desk-rejection-level errors: DOI existence, PubMed
  metadata mismatch, ghost/orphan citations, citation chimera, retracted
  papers, or paraphrase fabrication (whether cited abstracts actually support
  nearby claims). Trigger when user mentions "reference 검증", "DOI 확인",
  "인용 검증", "참고문헌 확인", "ghost citation", "retracted paper", "verify
  references", or operates in Step 5 Verify of the sam-workshop pipeline.
  Do not use this skill for general literature search (use Chat Deep Research
  instead) or for full 7-Layer audit (use verify-7layer for that).
  Input: paper_home/04_draft/manuscript.{md,docx} + paper_home/04_draft/references.{txt,bib}.
  Output: paper_home/05_verify/refcheck_refs.csv,
  refcheck_issues.md, r6_claim_support.jsonl, verification_certificate.md.
  Pipeline position: sam-workshop Step 5 / Self-Gate B.
  Medical context: Desk rejection from medical journals frequently triggered by
  fabricated DOIs, citation chimera, and unsupported paraphrases. Mandatory
  pass before Step 6 Critic. Mortality/safety/guideline claims must not be
  passed on abstract-only check.
```

## description 길이 가이드

- 너무 짧음 (< 50 단어): 자동 트리거 부정확
- 적정 (80–160 단어): 워크숍 표준
- 너무 김 (> 250 단어): 토큰 낭비, 트리거 정확도 ↓

## benchmark 표준

각 skill은 benchmark 30개 작성 (skill-creator의 description 최적화 입력):
- positive trigger 15개 (이 skill이 발화되어야 할 사용자 발화)
- negative trigger 10개 (이 skill이 발화되면 안 되는 발화)
- ambiguous trigger 5개 (다른 skill과 경쟁할 수 있는 발화 → tiebreak 룰)

benchmark 파일 위치: `<skill>/examples/triggers.jsonl`

## skill-creator 활용

```
"description 정밀화하고 싶음. 다음 trigger benchmark로 vary 분석해서 정확도 80% 이상 보고해."
```

→ skill-creator가 description 변형 + benchmark run + 가장 정확한 변형 채택.
