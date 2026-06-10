---
name: reporting-guideline-router
description: >
  Use this skill to identify which reporting guideline applies to a study
  (CONSORT/STROBE/STARD/PRISMA/CARE/TRIPOD/SPIRIT/etc.) and verify the manuscript
  meets its required items. Trigger when user says "reporting checklist", 
  "CONSORT STROBE", "보고지침", "study type 분류", "reporting guideline", or
  is auto-invoked by journal-fit-check / story-design / desk-reject-precheck.
  Do not use for journal style guides (저널 author instructions는 공식 페이지에서 직접 확인 — 본 스킬 범위 밖). Input:
  paper_home/01_design/article_type.md + paper_home/04_draft/manuscript.md.
  Output: paper_home/08_package/reporting_checklist.md +
  reporting_checklist.pdf (when downloadable). Pipeline position: invoked
  automatically by journal-fit-check (Step 1) for routing, by
  desk-reject-precheck (Step 7 quick scan) for verification. Medical context: 의학 저널
  대다수가 reporting checklist 부착을 desk requirement로 함. Trigger keywords:
  reporting guideline, CONSORT, STROBE, CARE, PRISMA, TRIPOD, STARD, SPIRIT,
  보고지침, checklist.
---

# reporting-guideline-router (Tier 2 — auto)

> Study design별 reporting guideline 자동 라우팅 + checklist 매핑.

## Routing Table

> **버전은 2026-06 기준 고정(pinned)** — 실행 시 EQUATOR·각 guideline 공식 사이트에서 **최신판·확장(extension) 존재를 확인**하고, 더 새 버전이 있으면 그쪽을 우선·표는 superseded로 표시.

| Study type | Guideline | Canonical URL |
|---|---|---|
| Randomized controlled trial | **CONSORT 2025** (2010 대체, 30-item) | consort-spirit.org |
| Observational (cohort/case-control/cross-sectional) | **STROBE** (2007; RECORD·STROBE-MR 확장 후보) | strobe-statement.org |
| Diagnostic accuracy | **STARD 2015 (v1.1)** | equator-network.org/reporting-guidelines/stard/ |
| Systematic review / meta-analysis | **PRISMA 2020** (scoping이면 PRISMA-ScR) | prisma-statement.org |
| Case report | **CARE** (2013) | care-statement.org |
| Trial protocol | **SPIRIT 2025** (2013 대체) | consort-spirit.org |
| Prediction model (development/validation) | **TRIPOD+AI** (TRIPOD-2015 공식 대체; LLM 연구는 TRIPOD-LLM 후보) | tripod-statement.org |
| Qualitative research | **SRQR** (2014) or **COREQ** (2007) | equator-network.org |
| Quality improvement | **SQUIRE 2.0** | squire-statement.org |
| Animal preclinical | **ARRIVE 2.0** | arriveguidelines.org |
| Economic evaluation | **CHEERS 2022** (AI 중재는 CHEERS-AI 후보) | equator-network.org |
| AI in healthcare | **TRIPOD+AI / CONSORT-AI / SPIRIT-AI / DECIDE-AI** (parent 2025판과 AI extension 병행 적용 여부는 실행 시 확인) | equator-network.org |

## 모드

| 모드 | 시간 |
|---|---|
| `workshop-mini` | 3분 (라우팅만) |
| `standard` | 15분 (라우팅 + 본문 vs checklist 매칭) |
| `deep-audit` | 30분 (item-by-item 통과 여부) |

## 입력

- `paper_home/01_design/article_type.md`
- `paper_home/04_draft/manuscript.md`

## 절차 (3분 routing)

```
당신은 의학 reporting guideline 라우터입니다. 다음 article에서:

1. Study design 식별 (RCT / cohort / case-control / cross-sectional /
   diagnostic / systematic review / case report / animal / 등)
2. 해당 reporting guideline 1차/2차 매칭
3. AI 사용 시 추가 가이드라인 (TRIPOD-AI 등) 매칭
4. checklist URL 제공
5. checklist 부착 의무인지 confirmation
```

## 절차 (15분 standard, 본문 매칭)

```
1. 위 라우팅 결과 확인
2. CONSORT 또는 STROBE 같은 checklist의 핵심 item을 본문에서 검색:
   - STROBE 6: 모집 방법, eligibility
   - STROBE 11: 표본 크기 산정
   - STROBE 12c: 결측 데이터 처리
   - STROBE 17: 잠재 confounder 보정
   - ... (study type별 다름)

3. 누락 item list:
   - missing_items: [...]
   - location_suggestion: [...]
```

## Output 표준

`paper_home/08_package/reporting_checklist.md`:

```markdown
# Reporting Guideline Routing

- Study design: 단면 관찰 연구 (cross-sectional)
- Primary guideline: STROBE
- Secondary: 해당 없음 (AI 미사용 시)
- Checklist URL: https://www.strobe-statement.org/checklists/

## STROBE Items 본문 매칭
| # | Item | Status | 위치 |
|---|---|---|---|
| 1a | Title indicates design | Pass | Title |
| 1b | Abstract structured | Pass | Abstract |
| 6 | Eligibility | **Fail** | Methods §2 보강 필요 |
| 12c | Missing data | Pass | Methods §3.2 |
...

## 누락 item: 3건
→ 본문 보강 후 STROBE checklist PDF 부착

## checklist 부착
- [ ] STROBE checklist PDF 다운로드 → paper_home/08_package/reporting_checklist.pdf
- [ ] 각 item에 본문 페이지 표기
```

## HITL Event Emit

```json
{"ts":"...","step":1,"gate":"A_design","event_type":"gate_pass","skill":"reporting-guideline-router","engine":"claude","category":"checklist_routing","severity":1,"description":"STROBE routed; 3 items need attention"}
```

## 자주 발생하는 함정

1. **Study design 자가 판정 오류** — case series를 case-control로 혼동
2. **AI 사용 시 추가 가이드라인 미적용** — TRIPOD-AI, CONSORT-AI
3. **checklist PDF 부착 누락** — 라우팅만 하고 부착 안 함 → desk reject
4. **각 item 본문 페이지 표기 안 함** — checklist 양식의 "page #" 칸 비워두면 desk reject

## 다음 단계

→ 본문 보강 → checklist PDF/파일 부착 → desk-reject-precheck (Step 7 quick scan) → Step 8 Wrap
