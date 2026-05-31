# HITL Event Emit 표준 (모든 skill 공통)

skill 실행 종료 직전, 다음 형식의 1줄을 `paper_home/.sam/hitl/events.jsonl`에 append.

## Schema 참조

`_shared/schemas/hitl_event.schema.json`

## 필수 필드

```json
{
  "ts": "2026-06-20T13:45:00Z",
  "paper_id": "<paper_home 폴더명>",
  "step": 5,
  "gate": "C_verify_critic",
  "event_type": "gate_pass | gate_fail | critique_decision | model_strength | hallucination | human_override",
  "skill": "<skill 이름, 예: verify-reference-essential>",
  "engine": "claude | gpt-5.5 | gemini | code-script",
  "category": "<자유 문자열, 예: reference_integrity, methods_critique, paraphrase_fab>",
  "severity": 1-5,
  "description": "<한 문장>",
  "action_taken": "<본인 결정 요약, 선택>",
  "decision": "accepted | rejected | partial | deferred",
  "time_to_fix_min": <분, 선택>,
  "human_edit_level": "none | low | medium | high"
}
```

## emit 방법 (3가지)

### A. Bash/Code skill

```bash
echo '{"ts":"'$(date -u +%FT%TZ)'","paper_id":"my_paper","step":5,...}' \
  >> paper_home/.sam/hitl/events.jsonl
```

### B. Python skill

```python
import json, datetime, pathlib
event = {
  "ts": datetime.datetime.utcnow().isoformat() + "Z",
  "paper_id": paper_id,
  "step": 5,
  "gate": "C_verify_critic",
  "event_type": "gate_pass",
  "skill": "verify-reference-essential",
  "engine": "code-script+claude",
  "category": "reference_integrity",
  "severity": 2,
  "description": "R1-R5 통과, R6 1건 의심",
  "time_to_fix_min": 28
}
log = pathlib.Path("paper_home/.sam/hitl/events.jsonl")
log.parent.mkdir(parents=True, exist_ok=True)
with log.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")
```

### C. LLM-only skill

skill 종료 마지막 메시지에 다음을 포함하고 본인이 복붙으로 append:

```
=== HITL EVENT (이 줄을 .sam/hitl/events.jsonl에 추가) ===
{"ts":"...","paper_id":"...","step":...,"gate":"...","event_type":"...","skill":"...","engine":"claude","category":"...","severity":...,"description":"..."}
```

## 권장 emit 시점

| 상황 | event_type | severity |
|---|---|---|
| Self-Gate 통과 | gate_pass | 1 |
| Self-Gate 실패 | gate_fail | 3-5 |
| Critic이 본인이 채택한 의견 | critique_decision (decision=accepted) | 2-4 |
| Critic이 본인이 거절한 의견 | critique_decision (decision=rejected) | 1-2 |
| AI가 잘 한 영역 발견 | model_strength | 1 |
| Hallucination 발견 | hallucination | 3-5 |
| 본인이 큰 수정 | human_override | 2-4 |

## hitl-dial-recommender 호환성

이 이벤트들이 누적되면 워크숍 wrap에서 자동으로 분석되어 다음 논문 권장 dial을 산출. 빠진 이벤트가 있으면 권고 정확도 ↓.
