# Workshop — 의대 교수 대상 AI 활용 논문 작성 (v1.2)

> 작성: 2026-04-28 / 갱신: 2026-04-30 (v1.2 reference-run) / 2026-05-31 (6/20 운영 정본 정합)
> 워크숍 일정: 2026-06-20 (토) **10:00–16:00** (+16:00–16:15 optional Q&A)
> **5h 실습 + 1h 점심 일정.** 단독저자 모드. Deliverable: **논문 lifecycle 전체 한 바퀴**(작성 → submit 직전 제출 패키지 → 리뷰 대응 연습) + (선택) AI-assisted item bank + 18 skill 영구 설치
> 타임라인 SSOT: [TIMETABLE.md](TIMETABLE.md) · 당일 운영: [D_DAY_RUNBOOK](D_DAY_RUNBOOK_20260620.md) / [BLUEPRINT](WORKSHOP_EXECUTION_BLUEPRINT_20260620.md)

## 현 상태 (D-20, 6/20 운영 정본 확정)

- **2026-06-13 (D-7) lifecycle 전환**: "초안에서 멈춤(submission-ready 아님·5–7일 후 마감)" 폐기 → 작성 8-step을 압축하고 **⑧ Submission·⑨ Review를 추가한 10-step lifecycle 부트캠프**로 재설계. 도달점 = submit 버튼 직전 + 리뷰 대응 연습. 안전선 = **Human Final Gate**(시점 표현 삭제, 본인 최종 검증·제출 책임은 유지). 3AI 3/3(sha8 `e0e3da8b`). ⚠️ Verify/Critic 깊이↓·완주율↓ trade-off 수용(성격: 깊은 작성 → lifecycle 부트캠프).
- **2026-05-31 (D-20)**: 타임라인·파이프라인 라벨을 6/20 운영 정본(10:00–16:00, 8-step + Bonus)으로 정합 완료 — TIMETABLE / skill README / OT slide·script 동기화. **아래 항목은 개발 이력**(8b 분할 등은 v1.2 시점, 운영본에서 step 7/Bonus로 재배치됨).
- **Skill Pack v1.2 완성** (17 skills + 5 schemas + 4 scripts + 5 templates) → `skills/sam-workshop/`
- **v1.3 포팅 plan 채택 (2026-05-03)** — 본 파이프라인(autopilot+collab) v1.2 패치 일부를 워크숍 백엔드로 흡수. 3AI 합의 도출, Tier 1/2/3 분류, dry-run 5월 중순 예정. **상세: [handoff_20260503_v1_3_plan.md](handoff_20260503_v1_3_plan.md)**
- v1.2 변경 (reference run 결과 반영, 2026-04-30):
  - Step 8b 시간 분할: *8b1 desk-reject 5분* + *8b2 exam wrap 20분* (총 25분)
  - `figure_render_fallback.py` 추가: free-tier 이미지 생성 미가용 시 matplotlib schematic
  - `paper_profile.schema.json`에 `target_audience_language` 필드 추가 → 영문 manuscript도 한국 청중이면 한국어 문항집 default
  - `hitl_recommend.py` 메시지 분리: **Medical Safety Floor (H4)** vs **Conservative Floor (H3)**
  - `revision_backlog.jsonl` 포맷 spec 명문화 (critic-multi-persona SKILL.md)
- v1.1 신규 (이전): `evidence-harvest-claim-bank`, `exam-item-builder`
- v1.1 패치 (이전): HITL hard floor override, manuscript versioning + manifest.json, 5h timetable reconciled
- **다음 (D-45 ~ D-0)**: Tier 1 코드 통합 → smoke test 3건 → dry-run → v1.3 hotfix → freeze → 본 행사 2026-06-20

## 한 줄 요약

Sam AI Pipeline (16-step Auto-Pilot/Collab)을 **단독저자 + Claude Desktop Code 탭 중심 + 4 Self-Gate supervised** 모드로 다이어트하되, **lifecycle 전체를 한 바퀴 도는 10-step**(작성 ①~⑦ + ⑧ Submission + ⑨ Review + ⑩ Wrap). Claude 주력 + GPT-5.5 critic + GPT-image-2/Nano Banana 2 figure 병렬. 무료 티어 활용 권장.

## 목표 산출물 (참가자 1인당)

1. **submit 직전까지의 제출 패키지(연습본) + 리뷰 대응 연습** — 실제 제출은 **Human Final Gate**(원자료·참고문헌·저자 전원 승인·IRB·COI·funding·AI공개·표절·저널 checklist 본인 확인) 통과 후 본인이 누른다
   - Letter / Commentary / Case Report / Editorial: 본문 + cover letter + checklist + submission worksheet
   - Narrative Review: 1차 outline + 2 핵심 섹션 draft
   - Original (Brief Report): IMRaD 골격 + Discussion 1차
2. **본인 강의 시험문제 20–30문항**
3. **Sam Workshop Skill Pack** (15 skills 영구 설치) — **1년+ 라이프사이클 자산**
4. **paper_home 폴더 (Code 탭 세션)** — 논문 1년 라이프사이클 home (투고 → R&R → 출판)

## 핵심 차별점

- **HITL Dial + 단계별 운전 모드** — 파이프라인 맵에서 각 단계를 "정지 없이 진행/정차"로 토글: 현장 🛡️표준(①③⑤⑥⑦)·⚡시간절약(①⑤⑦), 사후 자산 🏁최종집중·🎛️커스텀. 세션 시작 시 한 줄로 선택(`pipeline_map.md`/`gate_plan.json`), 끝에 dial 처방 — 양방향. **2 Floor 강제 정차**(Medical Safety: 임상권고/약물/IRB/R6 + Publication Ethics: AI 공개문/저자권/COI/저널정책) + **①⑦ soft floor**(주제·AI공개문)는 어떤 모드에서도 저자 확인
- **Code 탭 중심 + Chat 보조**: Claude Desktop Code 탭에서 skill·script·파일·검증을 완결, 문헌검색(②)만 Chat Deep Research 선택 활용
- **결정적 검증 vs LLM 추론 엄격 분리** — DOI/PMID/regex는 script, 의미는 LLM
- **무료 티어 보조 멀티엔진** — Claude Pro 필수, GPT/Gemini 무료 OK
- **Frontier 인식** — Sakana AI Scientist (Nature 2026.3), Google PaperOrchestra (2026.4) hook으로 supervised semi-automation 정직 포지셔닝

## 정본 파이프라인 (메인 10-step: 작성 ①~⑦ + ⑧ Submission + ⑨ Review + ⑩ Wrap, + Bonus 병행)

> 이 절이 **파이프라인 단계 정의 SSOT**다. 시간 배치는 [TIMETABLE.md](TIMETABLE.md), 당일 카드는 [FACILITATOR_PROMPT_CARD](FACILITATOR_PROMPT_CARD_20260620.md). 모든 발표/대본 자료(OT slide·OT script)는 이 라벨을 따른다.

```
DESIGN
  1. Idea Lock                  [journal-fit-check]               [Self-Gate A]
  2. Deep Research              [Chat DR + reporting-guideline-router]
  3. Story & Outline            [evidence-harvest-claim-bank
                                 + story-design]
WRITE
  4. Draft                      [Code 탭 파일 에디터 + section-boundary]
  5. Verify                     [verify-reference-essential
                                 + stats-consistency]             [Self-Gate B]
REFINE
  6. Critic                     [critic-multi-persona +
                                 GPT-5.5 ext + scorecard-9d]      [Self-Gate C]
FINISH
  7. Humanize & Package         [humanize-en/ko + desk-reject-precheck
                                 + cover letter + AI disclosure]  [Self-Gate D]
                                 (figure brief 옵션: figure-prompt-eng)
SUBMIT & REVIEW  (lifecycle 뒷단 — 사람 주도)
  8. Submission                 [submission_portal_adapter → submission
                                 worksheet 전원 작성 + 포털 강사 데모(녹화)
                                 · 🔒 Submit·로그인·자격증명 = 사람]
  9. Review Response            [가상 reviewer fixture → response matrix
                                 + rejection_resubmit 경로 A/B/C]
CLOSE
 10. Wrap & Next                [hitl-dial-recommender →
                                 🔒 Human Final Gate checklist + 다음 논문 dial]

+ Bonus (선택·시간 여유 시): 목업 통계 흐름 / 강의자료 기반 시험문항 초안
```

> **Figures는 메인 블록이 아니다** — 당일은 step 7에서 figure brief/caption만, 렌더링은 homework. 옛 v1.2의 "step 7 = Figures(병렬)" 라벨이 10:00–16:00 운영 흐름과 어긋나 step 7(Humanize & Package)에 흡수하고, Wrap을 step 8로 승격했다.

## 폴더 구조 (현재)

```
workshop/
├── README.md                              ← 이 파일
├── INSTALL.md                             ← 설치 가이드
├── FINAL_REPORT.md                        ← 자율 완수 보고서 (skill pack v1)
└── skills/sam-workshop/                   ← 배포 단위
    ├── README.md                          ← Skill Pack 사용법
    ├── _shared/                           
    │   ├── schemas/   (3 JSON)
    │   ├── scripts/   (3 Python, 1147 lines)
    │   └── templates/ (4 markdown)
    └── (15 skills × SKILL.md)
```

## 다음 작업 (사용자 액션 필요)

- [x] Reference run 1회 (Letter 1편) — skill 자동 트리거 정확도, R1-R5 script 정확성 실측 (2026-04-30 완료)
- [ ] **v1.3 Tier 1 코드 통합** (5월 1째주, ~5h) — `compliance_backend.py` + 3 SKILL.md 갱신 + 회귀 테스트 5건. 상세: `handoff_20260503_v1_3_plan.md`
- [ ] **Smoke test 3건** (5월 2째주 초) — Letter / Brief Report / Case Report
- [ ] **Dry-run 1회** (5월 중순) — 외부 의대 교수 1-2명, Brief Report 통계 포함, shadow baseline 동시 캡처
- [ ] **v1.3 hotfix** (5월 셋째주, dry-run +48h 분류 후)
- [ ] (5월 말) 슬라이드 v3 (8-step + Hybrid backend evidence 흐름) + 사전 안내문
- [ ] (사후) Skill description benchmark 30개씩 (skill-creator 활용)
- [ ] (사후) 한국 의대 교수 자주 투고 저널 5–10개 specs 사전 정비
- [ ] (v2 후속) `exam-item-generator` skill 별도 분리

## 빠른 시작 (Desktop Code 탭 · 평평 설치 — 2026-06-10 실측 검증)

1. Code 탭 통합 터미널에서 paper_home 생성: `install/init-workshop-{mac.sh,windows.ps1}`
2. Code 탭 **새 세션** → 작업 폴더 = paper_home
3. 설치 발화 한 줄 붙여넣기: *"sam-workshop repo를 clone해서 skills/sam-workshop 안의 18개 skill 폴더와 `_shared`를 지금 작업 폴더의 `.claude/skills/` 바로 아래로 복사해줘 (우산 폴더 금지 — 1단계)"*
4. **새 세션 1회** → `/` 목록에 18개 확인 → 첫 발화: `"시작하자"` (또는 `"내 논문 어느 저널에 투고할까?"`)

⚠️ Code 탭 skill 탐지는 `.claude/skills/<skill>/SKILL.md` **1단계만** 인식 — `cp -R skills/sam-workshop ~/.claude/skills/` 같은 **우산 복사는 전부 미탐지**(실측). 반드시 평평하게.

자세한 설치/검증: `INSTALL.md`. Skill Pack 사용법: `skills/sam-workshop/README.md`.

## 의사결정 이력

- 2026-04-28: 워크숍 컨셉 시작 (12-step v2 슬라이드)
- 2026-04-29: HITL Dial 5단계 도입, Cowork-centered 아키텍처 확정 (→ 2026-05-31 **Code 탭 중심으로 전환**: skill·script가 Claude Code 네이티브라 Code 탭이 자산 보존에 유리, 환경 단일화)
- 2026-04-29: 3-AI consult #1 (Gemini + GPT-5.5 + Claude) → 합의안 산출
- 2026-04-30 AM: Skill Pack v1 자율 완수 (15 skills, 3823 lines)
- 2026-04-30 PM: 3-AI review #2 → 6 critical issues 식별
- 2026-04-30 PM: **v1.1 P0 패치 자율 완수** — exam-item-builder + evidence-harvest-claim-bank 신규, hitl_recommend.py hard floor override, manuscript versioning, 5h timetable reconciled (3-AI consult #3)

## 참고

- 기반 파이프라인: `../sam-ai-autopilot/`, `../sam-ai-collab/`, `../shared/`
- 3-AI consult 기록: `~/.claude/skills/3ai-consult/outputs/3ai-consult_20260430_FINAL.md`
- 워크숍 슬라이드 (현재): `../파이프라인 소개.png` (12-step v2)
