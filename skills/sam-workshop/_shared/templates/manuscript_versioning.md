# Manuscript Versioning 표준 (v1.1 — Sam Workshop)

> 워크숍 중 파일 덮어쓰기 panic 방지 + factual drift 추적 보장. 모든 skill은 이 명명 규약 준수.

## 표준 명명 규약

각 단계 종료 시 manuscript snapshot을 다음 명명으로 저장:

```
04_draft/manuscript_v0.1_draft.md           ← Step 4 초고 (Code 탭 작업본의 첫 snapshot)
05_verify/manuscript_v0.2_verified.md        ← Step 5 verify 후 수정 반영
06_critic/manuscript_v0.3_revised.md         ← Step 6 critic 채택 사항 반영
08_package/manuscript_v0.4_humanized.md      ← Step 7 humanize 후
08_package/manuscript_v0.4.1_driftchecked.md ← humanize 후 R6/locked claim 재검증 통과
```

**Live Artifact**는 항상 `04_draft/manuscript.md` (별칭). 위 versioned 파일은 **history**.

## 명명 규칙

```
manuscript_v{major}.{minor}[_{tag}].md
```

| 위치 | 의미 |
|---|---|
| `major` | Big iteration (1.x = pre-submission, 2.x = R&R revision, 3.x = R&R round 2 ...) |
| `minor` | Step 단위 진행 (0.1=draft, 0.2=verified, 0.3=revised, 0.4=humanized) |
| `tag` (선택) | step 식별자 (`_draft`, `_verified`, `_revised`, `_humanized`, `_driftchecked`) |

## .sam/manifest.json

각 paper_home의 `.sam/manifest.json`에 현재 manuscript 상태 추적:

```json
{
  "schema_version": "manifest-v1.1",
  "paper_id": "paper_2026_001",
  "current_manuscript": "08_package/manuscript_v0.4.1_driftchecked.md",
  "previous_version": "08_package/manuscript_v0.4_humanized.md",
  "history": [
    {
      "version": "v0.1_draft",
      "path": "04_draft/manuscript_v0.1_draft.md",
      "timestamp": "2026-06-20T11:25:00Z",
      "step": 4,
      "sha256": "a3f2c9...",
      "word_count": 2847
    },
    {
      "version": "v0.2_verified",
      "path": "05_verify/manuscript_v0.2_verified.md",
      "timestamp": "2026-06-20T13:45:00Z",
      "step": 5,
      "sha256": "b41d8e...",
      "word_count": 2891,
      "changes_from_prev": "Reference 12, 23 replaced; stat consistency note added §3.2"
    }
  ],
  "locked_claims": ["C003", "C007", "C012"],
  "locked_claims_meta": {
    "C003": {
      "text": "SGLT2 억제제는 CKD 환자 사망률 30% 감소",
      "type": "mortality_outcome",
      "lock_reason": "guideline + safety claim, must not be paraphrased to drift",
      "locked_at_step": 5,
      "lock_check_status": "PASS"
    }
  },
  "last_gate": "D_finish",
  "last_skill": "humanize-en"
}
```

## locked_claims (★ humanize 단계 안전판)

다음 claim은 **humanize 단계에서 의미 lock** — 문장 다듬기는 가능, 의미 변경 금지:

| Claim type | Lock 여부 | 사유 |
|---|---|---|
| Mortality outcome | 🔒 Lock | 환자 안전 직결 |
| Safety claim | 🔒 Lock | 환자 안전 직결 |
| Guideline-changing claim | 🔒 Lock | 임상 영향 |
| Drug dose / contraindication | 🔒 Lock | 환자 안전 직결 |
| Primary outcome | 🔒 Lock | 통계 일관성 |
| Effect direction | 🔒 Lock | 결과 해석 |
| Effect size (수치) | 🔒 Lock | 통계 정확성 |
| 일반 prose | 🔓 Unlock | 자유 humanize |

`evidence-harvest-claim-bank`가 high-risk claim 자동 lock 후보 표시 → 본인 확정.

## Drift Check (Step 7 Humanize 후 필수)

`humanize-en` 또는 `humanize-ko` 종료 후 자동 검사:

```python
# pseudo-code
for claim_id in manifest["locked_claims"]:
    pre_humanize_text = get_claim_text_in(prev_version, claim_id)
    post_humanize_text = get_claim_text_in(humanized_version, claim_id)
    semantic_match = claude_compare(pre, post)
    if not semantic_match:
        FLAG[DRIFT] claim_id changed meaning
        require manual review
```

→ Drift 발견 시 `manuscript_v0.4_humanized.md` 폐기, locked claim 복원하여 `v0.4.1_driftchecked.md` 생성.

## 이전 버전 보존

**원본은 절대 삭제 안 함**. 모든 historical version은 `manuscript_versions/`에 보존:

```
04_draft/
├── manuscript.md                      ← Live (항상 최신)
├── manuscript_v0.1_draft.md           ← 명시적 snapshot
└── manuscript_versions/
    ├── manuscript_v0.1_draft.md       ← 복사본 (안전)
    └── ... (Step 진행 시마다 복사)
```

## Skill 운영 규약

각 핵심 skill 종료 시:
1. 작업 결과를 `manuscript_v{N}_{tag}.md`로 저장
2. `.sam/manifest.json` 갱신 (history append + current_manuscript 갱신)
3. 본 manuscript의 sha256 기록
4. `manuscript.md` Live Artifact는 최신 버전과 동기화

## 워크숍 패닉 방지

문제 발생 시 (예: humanize가 의미 변경):

```bash
# 즉시 이전 버전으로 복원
cp paper_home/06_critic/manuscript_v0.3_revised.md paper_home/04_draft/manuscript.md

# manifest 업데이트
# (또는 사람 수동 결정)
```

**모든 step의 input은 직전 step의 versioned snapshot에서 읽음** — Live Artifact만 의존하지 않음.

## HITL Event Emit 연동

각 versioned snapshot 생성 시:
```json
{"ts":"...","event_type":"version_snapshot","skill":"humanize-en","category":"manuscript_versioning","description":"v0.4_humanized created from v0.3_revised, locked claims preserved","artifact":"08_package/manuscript_v0.4_humanized.md"}
```

## 다음 단계 (skill v1.2 후속)

- `manuscript_versioner.py` Code script — 자동 snapshot + manifest 갱신
- Drift check 자동 비교 (locked claim semantic comparison)
- Diff visualization (Step간 변경 사항 시각화)
