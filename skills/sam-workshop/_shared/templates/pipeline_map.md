# 파이프라인 맵 & 운전 모드 (HITL Gate Plan)

> 의대 교수가 자기 논문 파이프라인의 **자동화 수준을 직접 운전**하는 도구. 세션 시작 시 이 맵을 보여주고 운전 모드를 받는다. 교수는 코드를 만지지 않고 **자연어 한 줄**로 고른다.
>
> "AI에게 통제권을 넘기는" 장치가 아니라, **저자가 자동화의 양을 단계별로 골라 쓰는** 장치다. (3AI consult 2026-05-31: 2 floor + soft floor + "정지 없이 진행" 용어 + 현장 2모드 / 2026-06-13 lifecycle 전환으로 8→10-step·soft floor = ①⑩)

## 맵 (세션 시작 시 표시 — 🛡️표준 예시)

```
        내 논문 파이프라인              [운전 모드: 🛡️ 표준]

  작성 ①Idea → ②Research → ③Story → ④Draft → ⑤Verify → ⑥Critic → ⑦Package
        ⭐✋        ▶️         ▶️        ▶️        ✋          ✋         ▶️
  제출·리뷰·마무리   ⑧Submission → ⑨Review → ⑩Wrap
                      🔒✋            🔒✋        ⭐✋

  ▶️ 정지 없이 진행 (요약 확인·저자 책임은 유지)    ✋ 정차: 저자 검토 [승인/수정/계속]
  ⭐ soft floor: 어떤 모드에서도 최소 1회 저자 확인 (① Idea · ⑩ Wrap = Human Final Gate)
  🔒 Floor: 모드 무관 강제 정차 — 🔒Medical Safety / 🔒Publication Ethics(AI 공개문·⑦) / 🔒⑧⑨ Submit·로그인·실제 리뷰 원문은 사람
```

> **용어 주의**: "auto/풀오토"라고 부르지 않는다(검토 생략·책임 면제로 오해). **"정지 없이 진행"**이라 부르고, 자동 통과 단계도 **요약은 반드시 읽고 최종 책임은 저자**에게 있음을 명시한다.

## 운전 모드 (프리셋)

| 모드 | dial | 정차 단계 | 워크숍 노출 |
|---|---|---|---|
| 🛡️ 표준 *(기본)* | H3 | ①⑤⑥⑩ | **현장 기본값** |
| ⚡ 시간절약 | H2 | ①⑤⑩ | 현장 옵션 (시간 부족 시) |
| 🚗 전체 정차 | H4 | ①~⑩ 전부 | 강사 데모 / 신중한 참가자 |
| 🏁 최종 집중 | H1 | ①⑩ | **사후 자산** (반복 작업용) |
| 🎛️ 커스텀 | — | 내가 지정 (단 ①⑩은 ⭐ 최소 유지) | **사후 자산** (고급) |

> ⑧ Submission·⑨ Review는 정차 단계가 아니라 **🔒 floor**(자격증명·Submit·실제 리뷰 원문은 어떤 모드에서도 사람) — 모드 표의 토글 대상 밖. ⑦ Package의 AI 공개문은 Publication Ethics floor로 확인.

> **현장에서는 🛡️표준 + ⚡시간절약 2개만 전면.** 🏁최종집중·🎛️커스텀은 "여러분 자산엔 이런 것도 있다"고 1분 소개 후 **사후 가이드**로(progressive disclosure — 인지부하 관리). 모드 설명에 5~7분 이상 쓰지 않는다.

### ⭐ Soft Floor — ① Idea Lock, ⑩ Wrap = Human Final Gate (모든 모드 공통)

- **① Idea Lock**: 어떤 모드든 주제·article type·target journal은 저자가 직접 확정. *교육 근거*: 첫 단추를 자동으로 넘기면 "도구가 논문을 만든다"는 잘못된 mental model이 생기고 학습이 일어나지 않음.
- **⑩ Wrap = Human Final Gate**: 어떤 모드든 마지막에 저자가 원자료·참고문헌·저자 전원 승인·IRB·COI·funding·AI 공개·표절·저널 checklist를 본인이 최종 확인하고, 실제 제출은 이 게이트 통과 후 본인이 누른다. (시점 표현 없음 — 본인 검증·제출 책임만 강조)
- **⑦ Package의 AI 활용 공개문·cover letter** 핵심 항목(target journal, article type, AI disclosure 포함 여부, originality/no dual submission, COI, corresponding author)은 soft floor가 아니라 **🔒 Publication Ethics floor**로 어떤 모드든 저자가 보고 승인(아래 Floor 절).

### 🔒 Floor — 모드 무관 강제 정차 (절대 안 풀림)

| Floor | 트리거 |
|---|---|
| 🔒 **Medical Safety** | 약물 용량·상호작용, IRB·윤리·환자동의, 임상 가이드라인 변경 제안, mortality/safety/guideline claim |
| 🔒 **Publication Ethics** | AI 활용 공개문, authorship, 이해상충(COI), IRB/ethics statement, data availability, 저널 정책 불일치 |
| 🔒 **⑧ Submission / ⑨ Review** | 포털 자격증명·로그인·Submit 버튼·실제 reviewer 원문 — 어떤 모드에서도 사람이 수행. 실제 제출은 ⑩ Human Final Gate 통과 후 본인이 누른다(워크숍에선 submission worksheet·가상 reviewer fixture로 연습). |

> ⑦ Package의 AI disclosure는 Publication Ethics floor — 어떤 모드든 저자 확인을 반드시 거친다. ⑦에서 생성한 공개문은 **"저널 지침 확인 전 임시 문안"**으로 표시(저널별 요구가 빠르게 변동).

## 정차 후 복귀 규칙

```
floor/정차 감지 → 저자 수정·판단 → 그 단계 재실행(해소 확인) → 원래 운전 모드로 복귀
```

- 기본은 **(i) 그 단계 재실행 + (iii) 원래 gate_plan 복귀.** 수정 후 바로 다음 단계로 넘기지 않는다(수정이 새 오류를 부를 수 있음).
- **같은 이슈 2회 이상 반복** → unresolved log에 기록 + 후속 Verify/Critic을 자동 review로 승격 + 임상/통계 전문가·가이드라인 원문 확인 권고.

## Alert fatigue 방지 — severity tiering

| 등급 | 동작 |
|---|---|
| 🔴 Red | 강제 정차 (Medical Safety / Publication Ethics floor) |
| 🟡 Amber | 정차 안 함, 요약에 경고 (근거 약함·과일반화) |
| 🔵 Blue | 정차 안 함, 문체 메모 |

중복 경고는 묶고, "위험할 수 있음"이 아니라 **"이 문장을 이렇게 고쳐라/근거를 더해라"**처럼 actionable하게. 오탐이라 판단해 넘길 땐 저자가 사유를 남긴다.

## 책임 배너 (모드 선택 직후 1회)

> **정지 없이 진행은 검토 생략이 아닙니다.** 정차 횟수만 줄일 뿐, 모든 내용·인용·임상 주장·AI 활용 공개문의 최종 책임은 저자에게 있습니다. **AI는 초안을, 저자는 책임을 집니다.** 정차하지 않은 단계도 마지막 요약에서 반드시 확인합니다.

## 진행 표시 (각 단계 종료 시 맵 갱신)

```
  ①Idea → ②Research → ③Story → ④Draft → ⑤Verify → ⑥Critic → ⑦Package → ⑧Submission → ⑨Review → ⑩Wrap
   ✅       ✅          ✅       ✅        ▶▶🔒        ·          ·            ·            ·         ·
                                          └ 🔒Medical Safety 감지(자동 진행 중단). [확인/수정]
```

상태 라벨: `저자 확인 완료` / `AI 초안 생성됨 — 저자 미확인` / `🔒 Floor 확인 필요`.

## Wrap 미확인 로그 (⑩ Wrap = Human Final Gate에서 자동 제공)

정지 없이 진행한 단계가 많을수록 audit trail이 중요하다. ⑩ Wrap에서 다음을 모아 보여준다:
- 정지 없이 통과한 단계 목록
- 생성된 핵심 claim
- 확인되지 않은 참고문헌
- AI 활용 공개문 문구
- unresolved Medical/Publication floor 항목

🔒 **Human Final Gate** 체크박스(통과 후 본인이 제출 버튼을 누른다): ☐ 원자료·모든 주장·인용을 본인이 확인 ☐ AI는 저자가 아니며 최종 책임은 본인 ☐ 저널 AI disclosure 지침 별도 확인.

## 교수가 모드 고르는 법 (자연어 한 줄)

- "표준으로 갈게요" → 🛡️표준
- "시간이 없어요 / 빠르게" → ⚡시간절약
- "처음이라 단계마다 볼게요" → 🚗전체 정차
- (사후) "다 맡기고 끝에만" → 🏁최종 집중 · "③⑤만 내가" → 🎛️커스텀
- 진행 중 변경: "⑥부터 정지 없이 진행" → ⑥ 이후 review 해제 (단 ⑩⭐ Human Final Gate·⑧⑨ floor는 유지)

## harness 동작 (참가자 비노출, Claude가 자동 수행)

1. **세션 시작**: 맵 + 모드 제시 → 자연어 선택 → 책임 배너 1회 → `.sam/hitl/gate_plan.json`(`gate_plan.schema.json`) 저장.
2. **각 step 종료**: gate_plan 참조. `review`/⭐soft floor → 정차. `진행` → ✅ + 1줄 요약 후 다음 step.
3. **floor 트리거** → gate_plan 무시 강제 정차 → events.jsonl emit → 복귀 규칙 적용.
4. **세션 끝**: `hitl-dial-recommender`가 events.jsonl로 다음 논문 권장 모드 처방 + Wrap 미확인 로그.

> 운전 모드는 **시작에서 고르고(이 맵), 끝에서 처방받는(`hitl-dial-recommender`)** 양방향 루프.

## OT/슬라이드용 한 줄 메시지

> "오늘 여러분은 이 10단계 파이프라인(작성 ①~⑦ + 제출 ⑧·리뷰 ⑨·마무리 ⑩)을 손에 넣습니다. 각 단계를 **정지 없이 흘려보낼지, 직접 운전대를 잡을지** 고릅니다 — 오늘은 🛡️표준으로. 단, ①주제·⑩ Human Final Gate(+⑦ AI 공개문 윤리)와 환자에게 닿는 결정(🔒), 그리고 ⑧⑨ 실제 제출·리뷰 원문은 어떤 모드에서도 저자가 반드시 봅니다."
