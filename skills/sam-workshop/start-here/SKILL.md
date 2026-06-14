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

> 워크숍·논문 세션의 **첫 발화 진입점**. 한 번 부르면 (1) 10-step 맵 + 운전 모드 제시 → (2) `gate_plan.json` 작성 → (3) Step 1부터 각 단계를 **반자동으로 안내**한다(다음 작업 skill을 호출하거나, 불확실하면 참가자가 입력할 명령을 제시). 참가자가 개별 skill 이름을 몰라도 흐름을 탄다.
>
> ⚠️ **"끝까지 무인 자동"이 아니다.** Claude Code에서 skill은 확정적 워크플로 엔진이 아니라 모델이 자연어/Skill tool로 트리거하는 비결정적 구조다. 그래서 start-here는 **각 단계를 안내하는 내비게이터** — 참가자가 **"다음"** 하기 전엔 다음 단계로 넘어가지 않는다(정차 ①⑤⑥⑩·의학 floor는 강제). "정지 없이 진행"이지 "검토 생략"이 아니다.

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
자연어로 모드를 받아 `.sam/hitl/gate_plan.json`에 저장한다. **반드시 아래 형식(`gate_plan.schema.json` 준수)을 그대로 따른다** — 🛡️표준(H3) 예시를 복사해 모드에 맞게만 바꾸고, `mode`/`stops`/`selected_by` 같은 임의 필드는 만들지 않는다:

```json
{
  "preset": "standard", "dial": "H3",
  "medical_floor_override": true, "publication_ethics_floor": true, "submission_review_floor": true,
  "soft_floor_steps": [1, 10],
  "steps": [
    {"n": 1, "name": "Idea Lock", "mode": "review", "locked_reason": "soft floor + Self-Gate A"},
    {"n": 2, "name": "Deep Research", "mode": "auto"},
    {"n": 3, "name": "Story & Outline", "mode": "auto"},
    {"n": 4, "name": "Draft", "mode": "auto"},
    {"n": 5, "name": "Verify", "mode": "review", "locked_reason": "Self-Gate B"},
    {"n": 6, "name": "Critic", "mode": "review", "locked_reason": "Self-Gate C"},
    {"n": 7, "name": "Humanize & Package", "mode": "auto"},
    {"n": 8, "name": "Submission", "mode": "review", "locked_reason": "Submission floor (사람)"},
    {"n": 9, "name": "Review Response", "mode": "review", "locked_reason": "Review floor (사람)"},
    {"n": 10, "name": "Wrap & Next", "mode": "review", "locked_reason": "soft floor + Human Final Gate"}
  ]
}
```
> ⚡ 시간절약 = `preset:"light"`·`dial:"H2"`·정차 ①⑤⑩(⑥ Critic도 `"auto"`). 🚗 전체정차 = 전부 `"review"`. 기본값 🛡️표준(H3).

**모드 선택 직후 책임 배너 1회**:
> AI는 초안을, 저자는 책임을 집니다. 정차하지 않은 단계도 마지막 요약에서 반드시 확인합니다. (전체 배너 = `pipeline_map.md`)

### 3) Step별 반자동 내비게이션 (핵심)
각 step **종료 시 반드시 다음 3줄을 출력**(종료 훅 — 참가자가 "지금 어디 있고 다음에 뭘 할지"를 항상 알게):
```
✅ [현재 단계] 완료 — [핵심 산출물 1줄]
다음: [Step N+1 이름]  →  /[다음-skill-name]
계속하려면 "다음"   (수정·재실행은 그대로 지시)
```
- 참가자가 **"다음"** 하기 전엔 다음 단계로 넘어가지 않는다(정차든 진행이든 동일 — 비개발자 통제감·교착 방지).
- "다음" 입력 시 다음 단계 skill을 Skill tool로 호출한다. **호출이 불확실하면 멈추지 말고** *"`/[skill-name]` 을 입력하세요"* 로 정확한 명령을 제시(참가자가 막히지 않게).
- gate_plan의 정차(review) 단계(①⑤⑥⑩)에선 [승인/수정/계속]을 명시적으로 받는다.

| Step | 단계 skill / 도구 | 정차 |
|---|---|---|
| ① Idea Lock | journal-fit-check | ✋ Self-Gate A |
| ② Deep Research | reporting-guideline-router (+ Chat Deep Research) | 진행 |
| ③ Story & Outline | evidence-harvest-claim-bank → story-design | 진행 |
| ④ Draft | (Code 파일 에디터) + section-boundary | 진행 |
| ⑤ Verify | verify-reference-essential + stats-consistency | ✋ Self-Gate B |
| ⑥ Critic | critic-multi-persona + scorecard-9d | ✋ Self-Gate C |
| ⑦ Humanize & Package | humanize-ko/en + desk-reject-precheck (figure-prompt-eng 옵션) | 진행 * (자동 점검 → ⑩서 최종 확인) |
| ⑧ Submission | 🔒 **사람 주도** — submission worksheet 작성 + 포털 강사 데모 | floor (사람) |
| ⑨ Review Response | 🔒 **사람 주도** — 가상 reviewer fixture → response matrix (revision-response 보조) | floor (사람) |
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
