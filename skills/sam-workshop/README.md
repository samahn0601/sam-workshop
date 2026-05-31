# Sam Workshop Skill Pack v1.2

> 의대 교수 워크숍용 Claude Skill Pack (10:00–16:00, 5h 실습 + 1h 점심). 단계·시간 SSOT: `workshop/TIMETABLE.md` · `workshop/README.md`.
> 단독저자 모드, Cowork-centered, HITL Dial 4-gate supervised 표준 + Medical Floor circuit breaker.
> v1.2 변경 (reference run 결과 반영): Step 8b 시간 분할 (5+20), figure-prompt-eng matplotlib fallback renderer 추가, paper_profile.target_audience_language 필드 추가 (한국 청중 한국어 문항집 default), hitl_recommend.py H3/H4 floor 메시지 분리, revision_backlog.jsonl 표준 포맷 명문화.
> v1.1 변경 (이전): exam-item-builder + evidence-harvest-claim-bank 추가, hard floor override, manuscript versioning, 5h timetable reconciled.

## 설치

### 옵션 A — 단순 폴더 복사 (권장 워크숍 표준)

```bash
# 본 폴더(sam-workshop)를 ~/.claude/skills/ 안으로 복사
# Mac/Linux:
cp -R sam-workshop ~/.claude/skills/

# Windows (PowerShell):
Copy-Item -Recurse sam-workshop "$env:USERPROFILE\.claude\skills\"
```

### 옵션 B — 심볼릭 링크 (개발용)

```bash
ln -s "$(pwd)/sam-workshop" ~/.claude/skills/sam-workshop
```

설치 확인:
```
~/.claude/skills/sam-workshop/
├── README.md (이 파일)
├── _shared/
│   ├── schemas/ (3 JSON schemas)
│   ├── scripts/ (3 Python scripts)
│   └── templates/ (4 markdown templates)
├── journal-fit-check/SKILL.md
├── story-design/SKILL.md
├── verify-reference-essential/SKILL.md
├── stats-consistency/SKILL.md
├── critic-multi-persona/SKILL.md
├── scorecard-9d/SKILL.md
├── figure-prompt-eng/SKILL.md
├── humanize-en/SKILL.md
├── humanize-ko/SKILL.md
├── desk-reject-precheck/SKILL.md
├── section-boundary/SKILL.md
├── reporting-guideline-router/SKILL.md
├── verify-7layer/SKILL.md
├── revision-response/SKILL.md
├── hitl-dial-recommender/SKILL.md
├── evidence-harvest-claim-bank/SKILL.md   ★ v1.1 NEW
└── exam-item-builder/SKILL.md             ★ v1.1 NEW
```

Claude Desktop 재시작 후 자연어로 skill 자동 발화 가능.

## Skill Pack 구성 (17개, v1.1)

### Tier 1 — 핵심 실습 (워크숍 시연·실습)

| # | Skill | Step | 묶음 |
|---|---|---|---|
| 1 | journal-fit-check | 1 | Idea Lock |
| 2 | **evidence-harvest-claim-bank** ★ | 3 | Story & Outline (claim/source 분리) |
| 3 | story-design | 3 | Story & Outline |
| 4 | verify-reference-essential | 5 | Verify (with stats-consistency) |
| 5 | stats-consistency | 5 | Verify |
| 6 | critic-multi-persona | 6 | Critic (with scorecard-9d) |
| 7 | scorecard-9d | 6 | Critic |
| 8 | figure-prompt-eng | 7 | Humanize & Package 내 figure brief (옵션) |
| 9 | humanize-en 또는 humanize-ko | 7 | Humanize & Package (locked claims drift check) |
| 10 | **exam-item-builder** ★ | 점심+Bonus | 시험문항 deliverable (병행 트랙) |

→ exam은 점심 백그라운드 + Bonus choice block에서 검토 (별도 메인 블록 X).

### Tier 2 — 자동 호출 또는 5분 데모

| # | Skill | 사용 |
|---|---|---|
| 9 | desk-reject-precheck | Step 7 quick scan |
| 10 | section-boundary | scorecard-9d 차원 9 자동 |
| 11 | reporting-guideline-router | journal-fit-check 내부 자동 |
| 12 | verify-7layer | post-workshop full audit |
| 13 | (선택 안 한 humanize 언어) | 부록 |

### Tier 3 — Post-workshop only

| # | Skill | 사용 |
|---|---|---|
| 14 | revision-response | R&R 받았을 때 |

### Meta — Workshop wrap

| # | Skill | 사용 |
|---|---|---|
| 15 | hitl-dial-recommender | 워크숍 마지막 10분 + 사후 매 논문 종료 시 |

## 의존성

### 필수 (Claude Pro에 모두 내장)
- Python 3.9+ (스크립트 실행용, 시스템에 이미 있을 가능성 ★)

### 선택 (외부 도구)
- ChatGPT (무료 OK, Plus 권장) — Step 6 GPT-5.5 critic
- Gemini (무료 OK, Advanced 권장) — Step 7 Nano Banana 2 figure
- python-docx (Step 5 .docx manuscript 사용 시): `pip install python-docx`

## 워크숍 시간표

> **시간표 SSOT는 `workshop/TIMETABLE.md`** (10:00–16:00 운영 정본). 갈라짐 방지를 위해 여기서 중복 유지하지 않는다.
>
> 정본 파이프라인: **1 Idea Lock → 2 Deep Research → 3 Story & Outline → 4 Draft → 5 Verify → 6 Critic → 7 Humanize & Package → 8 Wrap & Next** (+ Bonus 병행).
> 각 skill이 어느 step에 쓰이는지는 위 "Skill Pack 구성" 표 참조. (figure-prompt-eng = step 7 옵션, exam-item-builder = 점심 백그라운드 + Bonus, hitl-dial-recommender = step 8)

## Skill 사용 예 (자연어 트리거)

```
"내 논문 어느 저널에 투고할까?" → journal-fit-check
"outline 짜줘" → story-design  
"reference 검증" → verify-reference-essential
"통계 일관성 점검" → stats-consistency
"critic 받아줘" → critic-multi-persona
"점수 매겨줘" → scorecard-9d
"figure prompt 만들어줘" → figure-prompt-eng
"AI 시그니처 제거" → humanize-en (영문) / humanize-ko (국문)
"투고 전 마지막 점검" → desk-reject-precheck
"섹션 경계 확인" → section-boundary
"reporting checklist" → reporting-guideline-router
"full 7-Layer 검증" → verify-7layer
"reviewer 응답 작성" → revision-response (post-workshop)
"다음 논문 dial 처방" → hitl-dial-recommender (workshop wrap)
```

## 폴더 구조 표준

각 논문 = Cowork Project 1개 = 로컬 폴더 1개:

```
paper_home/
├── 00_intake/
├── 01_design/
├── 02_research/
├── 03_outline/
├── 04_draft/        ← manuscript.md (Live Artifact)
├── 05_verify/
├── 06_critic/
├── 07_figures/
├── 08_package/
└── .sam/
    ├── hitl/events.jsonl
    └── memory/
```

자세한 규약: `_shared/templates/paper_home_layout.md`

## 7개 공통 개선 항목 (모든 skill 적용)

1. ★ Description 자동 트리거 7요소 (when use, when NOT use, input, output, pipeline 위치, self-gate, medical context)
2. ★ Solo + Claude-only fallback (외부 엔진 못 쓸 때 Claude 다중 페르소나 대체)
3. ★ Time-budget 3 모드 (workshop-mini / standard / deep-audit)
4. 결정적 검증 vs LLM 추론 분리 (DOI/PMID/regex는 script, 의미는 LLM)
5. Cowork 로컬 폴더 상대경로 표준화
6. Structured output 표준 (issue table / scorecard / checklist / JSONL log)
7. HITL Event Emit hook (모든 skill 종료 시 .sam/hitl/events.jsonl append)

## HITL Floor (영구 — dial과 무관, 모든 skill 적용)

다음 4영역은 **항상 본인 결정** (위임 불가):

1. **임상 권고 / 가이드라인 변경 제안** — 환자 영향
2. **약물 용량, 오리지널 vs 제네릭** — 환자 안전
3. **IRB / 윤리 / 환자 동의 문구** — 법적·윤리적 책임
4. **Reference Discussion 핵심 paraphrase 검증** (R6) — desk reject 직접 트리거. mortality/safety/guideline claim은 abstract만으로 통과 절대 금지

## Self-Gate (4개)

| Gate | 위치 | 통과 기준 |
|---|---|---|
| **A_design** | Step 1+3 후 | journal locked, outline 통과, evidence map 작성 |
| **B_draft** | Step 5 후 | verify-reference-essential PASS, stats-consistency 정당화 |
| **C_verify_critic** | Step 6 후 | scorecard-9d ≥ 32, 차원 9 = Pass |
| **D_finish** | Step 7 후 | scorecard-9d ≥ 36, desk-reject-precheck 0 critical fail |

## HITL Dial 5단계

| Dial | 이름 | 워크숍 사용 |
|---|---|---|
| H4 | 8-gate hand-holding | 초보자 옵션 |
| **H3** | 4-gate standard | **워크숍 default** |
| H2 | 2-gate accelerated | 경험자 옵션 |
| H1 | 1-gate Auto-Pilot | 워크숍 미사용 (사후 옵션) |
| H0 | 0-gate Sakana style | 의학 비권장 |

## 라이센스 / 출처

- 기반: Sam AI Pipeline (sam-ai-autopilot v1.x, sam-ai-collab v1.x)
- 워크숍 변형: 단독저자 모드, Claude-only baseline + GPT/Gemini optional
- 작성: Sam (Sang Hyun Ahn, MD) — 2026-04
- 라이센스: 워크숍 참가자 본인 사용 (재배포는 출처 표기)

## 다음 작업

- [ ] Reference run 1회 (Letter 1편) — skill 자동 트리거 정확도 측정
- [ ] Skill description benchmark 30개씩 (skill-creator 적용)
- [ ] 한국 의대 교수 자주 투고 저널 5–10개 specs 사전 정비
- [ ] 워크숍 슬라이드 v3 제작 (8-step diagram)
- [ ] 참가자 사전 안내문 작성

## 문의 / 개선 제안

Sam (admin@modoc-ai.com) — 본 skill pack에 대한 피드백/이슈/개선 제안.

---

🎯 본 skill pack은 의대 교수 1년+ 라이프사이클 자산입니다. 워크숍 5h는 시작점.
