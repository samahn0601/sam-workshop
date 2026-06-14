---
name: start-here
description: >
  워크숍·논문 세션의 첫 진입점(오케스트레이터). 한 번 부르면 10-step 파이프라인
  맵과 운전 모드를 보여주고, gate_plan을 작성한 뒤 Step 1부터 각 단계 skill을
  자동으로 이어 호출하며 안내한다. 참가자가 개별 skill 이름을 몰라도 전체 흐름을
  탄다. 단계별 정차(①⑤⑥⑩)와 의학 floor(약물·IRB·임상·AI 공개문)는 유지 —
  "정지 없이 진행"이지 검토 생략이 아니다. Trigger when the user starts a paper
  or workshop session, asks "어디서부터 / 시작하자 / 논문 쓰자", or is unsure
  which skill to use first. Do not use for a specific stage task — call that
  stage's skill directly (journal-fit-check, verify-reference-essential,
  critic-multi-persona 등). Input: paper_home (신규 또는 진행 중) + (선택)
  .sam/hitl/paper_profile.json, .sam/pipeline_state.json. Output:
  .sam/hitl/gate_plan.json + Step 1 진입. Pipeline position: 진입점 / 전체
  10-step 오케스트레이션. Medical context: Medical Safety·Publication Ethics·
  ⑧⑨ Submission/Review floor는 운전 모드와 무관하게 강제. Trigger keywords:
  시작, 시작하자, 워크숍 시작, 논문 시작, 논문 쓰자, 어디서부터, 어디부터, 처음,
  진입점, 파이프라인 시작, 운전 모드, start, start here, begin, get started,
  kick off, where to start.
---

# start-here — 논문 파이프라인 진입점 (10-step 오케스트레이터)

> 워크숍·논문 세션의 **첫 발화 진입점**. 한 번 부르면 (1) 10-step 맵 + 운전 모드 제시 → (2) `gate_plan.json` 작성 → (3) Step 1부터 각 단계 skill을 자동으로 이어 호출하며 안내한다. 참가자가 개별 skill 이름을 몰라도 흐름을 탄다. **단계별 정차(①⑤⑥⑩)·의학 floor는 유지** — "정지 없이 진행"이지 "검토 생략"이 아니다.

## 언제 부르나

- 새 `paper_home`에서 논문을 시작할 때 ("시작하자", "어디서부터 할까")
- 진행 중 세션을 다시 열어 "지금 어느 단계지?"를 물을 때 (`.sam/pipeline_state.json` 참조해 이어감)
- 특정 단계 작업은 이 skill이 아니라 **해당 단계 skill을 직접** (journal-fit-check, verify-reference-essential, critic-multi-persona 등)

## 절차

### 0) 현재 상태 파악
- `.sam/pipeline_state.json`의 `current_step` 확인 → 있으면 그 단계부터 이어가고, 없으면 Step 1 신규 시작.
- `.sam/hitl/paper_profile.json` 있으면 로드(없으면 ①에서 함께 작성).

### 1) 10-step 맵 + 운전 모드 제시
`${CLAUDE_SKILL_DIR}/../_shared/templates/pipeline_map.md`의 10-step 맵과 운전 모드 표를 보여준다. (변수 미확장 시 Claude가 절대경로로 치환)

```
작성 ①Idea → ②Research → ③Story → ④Draft → ⑤Verify → ⑥Critic → ⑦Package
제출·리뷰·마무리   ⑧Submission → ⑨Review → ⑩Wrap
```
현장은 2모드만 전면: **🛡️ 표준(정차 ①⑤⑥⑩)** / **⚡ 시간절약(①⑤⑩)**. 나머지(🚗전체정차·🏁최종집중·🎛️커스텀)는 1분 소개 후 사후 자산.

### 2) 모드 선택 → gate_plan 작성
자연어로 모드를 받아 `.sam/hitl/gate_plan.json`(`gate_plan.schema.json`)에 저장. 기본값 🛡️표준(H3). **모드 선택 직후 책임 배너 1회**:
> AI는 초안을, 저자는 책임을 집니다. 정차하지 않은 단계도 마지막 요약에서 반드시 확인합니다. (전체 배너 = `pipeline_map.md`)

### 3) Step별 오케스트레이션 (핵심)
각 step에서 해당 skill을 자동 호출하고, 완료되면 gate_plan을 참조해 **정차(review)** 또는 **정지 없이 진행(auto)**:
- 정차 → 맵 갱신 + *"⑤ Verify 완료. [승인/수정/계속]?"* 입력 대기
- 진행 → ✅ + 1줄 요약 후 **다음 step skill을 이어서 호출**

| Step | 자동 호출 skill | 표준 정차 |
|---|---|---|
| ① Idea Lock | journal-fit-check | ✋ Self-Gate A |
| ② Deep Research | reporting-guideline-router (+ Chat Deep Research) | 진행 |
| ③ Story & Outline | evidence-harvest-claim-bank → story-design | 진행 |
| ④ Draft | (Code 파일 에디터) + section-boundary | 진행 |
| ⑤ Verify | verify-reference-essential + stats-consistency | ✋ Self-Gate B |
| ⑥ Critic | critic-multi-persona + scorecard-9d | ✋ Self-Gate C |
| ⑦ Humanize & Package | humanize-ko/en + desk-reject-precheck (figure-prompt-eng 옵션) | 진행 * |
| ⑧ Submission | submission worksheet + 포털 강사 데모 | 🔒 floor (사람) |
| ⑨ Review Response | revision-response (가상 reviewer fixture → response matrix) | 🔒 floor (사람) |
| ⑩ Wrap & Next | hitl-dial-recommender → 🔒 Human Final Gate + 다음 dial | ✋ Human Final Gate |

\* ⑦의 AI 공개문·cover letter는 표준 정차는 아니지만 **Publication Ethics floor**로 어떤 모드든 저자가 확인한다.
(+ Bonus 병행: **exam-item-builder** = 점심 백그라운드 + Bonus 트랙)

### 4) 안전선 (운전 모드와 무관하게 강제)
- 🔒 **Medical Safety** — 약물 용량·상호작용, IRB·윤리·환자동의, 임상 가이드라인 변경, R6(mortality/safety/guideline claim) → 강제 정차.
- 🔒 **Publication Ethics** — AI 활용 공개문·authorship·COI·IRB/ethics·data availability·저널 정책 불일치 → 강제 정차.
- 🔒 **⑧ Submission · ⑨ Review** — 포털 자격증명·로그인·Submit 버튼·실제 reviewer 원문은 사람이 수행. 실제 제출은 **⑩ Human Final Gate** 통과 후 본인이 누른다.
- 워크숍 산출물 = **submission-directed ≠ submission-ready**.

## 출력
- `.sam/hitl/gate_plan.json` (운전 모드)
- `.sam/pipeline_state.json` 갱신 (`current_step`)
- Step 1 진입 — `journal-fit-check` 호출

## HITL Event Emit
세션 시작 직후 `.sam/hitl/events.jsonl`에 1줄 append:
```json
{"ts":"...","step":0,"event_type":"session_start","skill":"start-here","engine":"claude","category":"orchestration","severity":1,"description":"workshop session started, mode=H3 standard"}
```

## 자주 발생하는 함정
1. **운전 모드를 안 받고 바로 작성 시작** — 반드시 1) 맵 → 2) 모드 → 3) Step 1 순서. 모드 미선택 시 🛡️표준(H3) default + 사유 표기.
2. **⑧⑨를 자동으로 넘김** — Submission/Review는 floor라 어떤 모드든 사람. 가상 fixture·worksheet로 연습하고 실제 제출 금지.
3. **개별 단계 재작업 시 start-here 재호출** — 특정 단계만 다시 할 땐 해당 skill을 직접 부른다(여긴 진입/이어가기 전용).

## 다음 단계
→ 운전 모드 확정 후 **Step 1 `journal-fit-check`** 자동 시작. 이후 각 단계는 gate_plan대로 정차/진행하며 **⑩ Wrap(Human Final Gate)**까지 이어간다.
