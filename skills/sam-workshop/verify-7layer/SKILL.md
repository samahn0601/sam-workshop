---
name: verify-7layer
description: >
  Use this skill for full 7-Layer verification (post-workshop, deep audit) of a
  medical manuscript: L1 DOI, L2 metadata, L3 numbers/dates, L4 citation
  paraphrase, L5 logical coherence, L6 ghost/orphan, L7 academic consensus.
  This is the FULL audit version — for workshop time-budget use
  verify-reference-essential instead. Trigger when user says "7-Layer 검증",
  "full audit", "deep verification", "post-workshop verify", "정밀 검증", or
  is preparing high-stakes submission (IF≥10, original article). Do not use in
  workshop time budget (use verify-reference-essential). Input:
  paper_home/04_draft/manuscript.md + paper_home/04_draft/references.txt.
  Output: paper_home/05_verify/verification_log_v{N}.md (comprehensive).
  Pipeline position: post-workshop deep audit, also Step 5 of standard
  (non-workshop) Sam pipeline. Medical context: NEJM/JAMA/Lancet 수준 정밀
  검증, IRB 직접 영향, 환자 안전. Trigger keywords: 7-Layer, full verification,
  deep audit, post-workshop, 정밀 검증, IF 10, NEJM, JAMA.
---

# verify-7layer (Tier 2 — post-workshop full audit)

> Sam pipeline의 원본 7-Layer 검증. **워크숍 시간 안에는 부적합** — verify-reference-essential 사용. 본 skill은 사후 정밀 검증 / IF≥10 저널 투고 전 / 임상 권고 영향 논문에 사용.

## 7-Layer 정의

| Layer | 목적 | 도구 | 자동화율 |
|---|---|---|---|
| L1 DOI 실재 | DOI/PMID 실재 | Crossref + PubMed | 100% |
| L2 메타데이터 | 저자/제목/저널/연도/권/페이지 **+ publication status (retracted / correction / expression of concern / 최신판)** | esummary 비교 + publication_type/update 확인 | 100% |
| L3 수치/날짜 | 본문 핵심 수치 vs 정부 DB / 원논문 | 웹검색 + 저자 본인 직접 확인 | 80% |
| L4 인용 구문 | 인용 paraphrase 정확성 (5분류) | Claude semantic + abstract fetch | 90% |
| L5 논리 정합성 | Intro gap → Methods → Results → Discussion 연결 | Claude reasoning | 80% |
| L6 Ghost/Orphan | 본문 ↔ reference list | regex | 100% |
| L7 학계 합의 | 가이드라인/consensus와 일치 | 웹검색·grounding 가능한 LLM (Claude 웹검색 또는 외부 LLM) | 90% |

## 모드

본 skill은 항상 `deep-audit` 모드. 시간 60–120분.

## 입력

- `paper_home/04_draft/manuscript.md`
- `paper_home/04_draft/references.txt`
- (Optional) raw data files for L3 verification

## 절차 (60–120분)

### L1+L2+L6 (15분) — verify-reference-essential 재실행

```bash
python ${CLAUDE_SKILL_DIR}/../_shared/scripts/ref_verify_pubmed.py \
  --manuscript paper_home/04_draft/manuscript.md \
  --references paper_home/04_draft/references.txt \
  --email <연락 가능한 이메일 — 더미 그대로 실행 금지> \
  --r6-sample 0 \
  --out paper_home/05_verify/
```

> 경로: 공유 스크립트는 형제 폴더 `_shared` (`${CLAUDE_SKILL_DIR}` 미확장 시 Claude가 절대경로 치환). **Fail-closed**: 스크립트/네트워크 실패·retraction/최신판 미확인·핵심 수치(L3) 미검증·임상 권고(L7) 최신성 미확인 시 해당 layer `INCOMPLETE` — 전체 PASS 금지. 핵심 주장에 연결된 인용이 L4 `Cannot judge`여도 PASS 금지.

### L3 (20분) — 수치/날짜 정밀 검증

```
다음 manuscript의 모든 수치 (유병률, OR/HR/RR, 날짜, 비용, 인구 통계)를:
1. 추출
2. 출처 식별 (정부 DB / 원논문 / 본인 데이터)
3. 본인이 직접 정부 DB / 원논문 abstract를 웹검색해서 cross-check
4. LLM의 "기억"으로 수치 확정 절대 금지 — 웹검색은 출처 화면 확인용 보조, 확정은 결정적 소스(원문·DB)만

표:
| # | 수치 | 본문 값 | 원문 값 | 출처 URL | 일치 | 비고 |
```

### L4 (25분) — 인용 구문 paraphrase 5분류

```
모든 인용 [n]에 대해 (verify-reference-essential R6의 full version):
- claim 문장 vs cited paper의 abstract (또는 full text 가능 시)
- 5분류: Supported / Partially / Not supported / Contradicted / Cannot judge
- evidence_span 인용

CITE 5 sub-codes:
- CITE_FABRICATED: 존재하지 않는 저자/저널/연도 (L1 미발견)
- CITE_DISTORTED: 결론 왜곡
- CITE_OUT_OF_CONTEXT: 맥락 무시
- CITE_OVERSTATED: 과장
- CITE_UNSUPPORTED: 원문에 해당 내용 없음
```

### L5 (15분) — 논리 정합성

```
Intro gap statement → Methods question → Results finding → Discussion answer
의 연결성 검사:
- gap이 방법으로 해결 가능?
- methods가 results를 산출 가능?
- results가 discussion claim을 지원?
- discussion이 gap에 답?

깨진 사슬 위치 list.
```

### L6 (5분) — Ghost/Orphan

verify-reference-essential 결과 재사용.

### L7 (15분) — 학계 합의

```
본 manuscript의 핵심 임상 권고 / 약물 사용 / 가이드라인 인용을:
- 현재 (2026) 가이드라인 (KSCVD/ESC/AHA/등)과 비교
- consensus_tag: established | emerging | controversial | outdated

웹검색·grounding 가능한 LLM(Claude 웹검색 또는 외부 LLM)으로 가이드라인 직접 확인.
LLM 단독 메모리만으로 통과 금지.
```

## Output 표준

`verification_log_v{N}.md`:

```markdown
# Verification Log Round N (Full 7-Layer)

## L1 DOI: PASS (N/N resolve)
## L2 Metadata: 1 mismatch
   - Ref 12: year 2023 → CrossRef 2024 [BIBLIO_MISMATCH:year]
## L3 Numbers: 2 mismatches
   - "30.4% smoking rate" → KOSIS 2023 confirms 32.4% [NUMBER_MISMATCH]
## L4 Citations: 18/20 Supported, 2 CITE_OVERSTATED
   - Ref 8: "X reduces mortality 30%" → abstract reports LOS only
## L5 Logic: 1 gap
   - Discussion §3 conclusion not supported by Results §2
## L6 Ghost/Orphan: PASS
## L7 Consensus: 1 outdated
   - "current guidelines recommend X" → KSCVD 2025 updated
```

## HITL Event Emit

```json
{"ts":"...","step":5,"gate":"B_draft","event_type":"gate_pass","skill":"verify-7layer","engine":"code+llm","category":"full_audit","severity":3,"description":"L1 PASS, L2 1 mismatch, L3 2 mismatch, L4 2 CITE_OVERSTATED, L5 1 gap, L7 1 outdated"}
```

## Floor

- 모든 layer 본인 ratify 필수 (auto-fix만으로 통과 금지)
- L7 가이드라인 outdated 발견 시 본문 수정 + Discussion에 명시
- (layer 밖) **AI 공시·저자권·COI 점검은 desk-reject-precheck #5·#7** — 본 감사 통과와 별도로 투고 전 필수

## 다음 단계

→ 강사 본 파이프라인(sam-ai-autopilot 16단계)의 ⑩ Final Verify에 해당하는 사후 정밀 감사 routine (참가자 10단계 체계 밖). Workshop에서는 verify-reference-essential 만으로 충분.
