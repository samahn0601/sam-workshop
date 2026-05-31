---
name: stats-consistency
description: >
  Use this skill when a medical manuscript with quantitative results needs
  numerical consistency check between text, abstract, and tables: sample size
  (n), percentages (%), p-values, and 95% CI. Trigger when user says "통계
  일관성", "수치 확인", "n p value 일치", "abstract text mismatch", "stats
  consistency", "table text mismatch", or operates in Step 5 Verify of the
  sam-workshop pipeline. Do not use for raw data analysis (use Code with R/Python)
  or for reference verification (use verify-reference-essential). Input:
  paper_home/04_draft/{manuscript.md, abstract.md} + paper_home/04_draft/tables/.
  Output: paper_home/05_verify/stats_consistency.md. Pipeline position:
  sam-workshop Step 5 / Self-Gate B. Medical context: Inconsistent numbers
  between abstract/text/tables is a top reviewer-detected red flag and a common
  desk reject trigger. Trigger keywords: 통계, stats, n, p-value, 95% CI,
  일관성, mismatch, abstract, table, 표.
---

# stats-consistency (Step 5)

> 본문 / Abstract / Table에서 n, %, p, 95% CI가 일치하는지 자동 검출. AI 작성 의심 시 reviewer가 자주 잡는 항목.

## 모드

| 모드 | 시간 | 범위 |
|---|---|---|
| `workshop-mini` | 5–10분 | regex 자동 + Claude 1차 review |
| `standard` | 20분 | + 표 cell-by-cell 비교 |
| `deep-audit` | 45분 | + 원시 데이터 재계산 |

## 입력

- `paper_home/04_draft/manuscript.md`
- (선택) `paper_home/04_draft/abstract.md` (분리되어 있다면)
- (선택) `paper_home/04_draft/tables/` (.md 또는 .txt 형식)

## 절차 (workshop-mini, 5–10분)

### 1. 자동 추출 + 비교 (Code, 3분)

```bash
python ~/.claude/skills/sam-workshop/_shared/scripts/stats_consistency_check.py \
  --manuscript paper_home/04_draft/manuscript.md \
  --abstract  paper_home/04_draft/abstract.md \
  --tables    paper_home/04_draft/tables/ \
  --out       paper_home/05_verify/stats_consistency.md
```

자동 검출:
- `[N_VARIANTS]` 본문/abstract/표에 다른 n
- `[N_ABSTRACT_TEXT_MISMATCH]` abstract n과 text n 불일치
- `[PCT_ABSTRACT_ONLY]` abstract에만 있는 %
- `[P_ABSTRACT_TEXT_MISMATCH]` p-value 불일치

### 2. Claude semantic review (5분)

자동 검출이 false positive 가능 (subgroup 등 정당한 차이). Claude에 다음 입력:

```
이 stats_consistency.md 자동 검출 결과를 검토해주세요.

각 항목에 대해:
- 실제 불일치인가, subgroup 등 정당한 차이인가?
- 정당한 차이면 본문에서 명시적으로 표시되어 있는가?
- 명시 안 됐으면 어느 부분에 무엇을 추가해야 하는가?

특별히 확인:
- Table 1 baseline n vs Methods 진술 n
- Abstract의 핵심 효과크기 vs Results 본문의 OR/HR/95% CI
- Discussion에서 인용한 본인 수치 vs Results 표 수치
- p-value 자릿수 (text "p<0.001" vs table "0.0003" 등)
```

### 3. Self-Gate B 결정

본인이:
- [ ] 모든 high severity 항목 결정
- [ ] subgroup 정당화 명시 추가 (필요 시)
- [ ] 단위 통일 (mg vs mg/kg)
- [ ] 자릿수 통일

## Output 표준

### `stats_consistency.md`
```markdown
# Statistics Consistency Check

- Severity: high | medium | info
- Issues found: N

## Extracted numbers (raw)
- Text: n=[51850], pct=[42.1, 14.3], p=[0.001], CI=[(1.28, 1.57)]
- Abstract: n=[51850], pct=[14.3], p=[0.001]
- Tables: n=[51850, 21340, 30510], pct=[14.3, 12.1, 16.8]

## Issues
- [N_VARIANTS] tables show subgroup n (21340, 30510) — verify subgroup labeling explicit
- [PCT_ABSTRACT_ONLY] 42.1% in text but not in abstract — verify both correct

## Caveats
- Regex-only extraction. Claude semantic review still recommended.
```

## 결정적 vs LLM 분리

- **결정적 (script)**: 숫자 추출, 1차 비교
- **LLM (Claude)**: subgroup 정당성 판단, 단위 통일 권고, 자릿수 정책

## HITL Event Emit

스크립트 자동:
```json
{"ts":"...","step":5,"gate":"C_verify_critic","event_type":"gate_pass","skill":"stats-consistency","engine":"code-script","category":"stats_consistency","severity":1}
```

## Floor (절대 위임 불가)

- 효과크기 방향 (감소 vs 증가) — 본인 확인
- 통계적 유의성 → 임상적 유의성 비약 — 본인 본문 점검
- 단위 변환 (mg ↔ mg/kg, mmHg ↔ kPa) — 본인 검증

## Self-Gate B 체크리스트

- [ ] [N_*] 항목 모두 정당화 또는 수정
- [ ] [PCT_*] 항목 모두 정당화 또는 수정
- [ ] [P_*] 항목 모두 정당화 또는 수정
- [ ] 단위/자릿수 통일
- [ ] Subgroup labeling 본문 명시 확인

## 자주 발생하는 함정

1. **Abstract와 Results 본문 OR/HR 자릿수 다름** — "1.42 (1.28-1.57)" vs "1.4 (1.3-1.6)"
2. **Total n과 analyzed n 차이** — 결측치 명시 안 됨
3. **Table 1 합계가 안 맞음** — 결측 또는 % 반올림 누적 오차
4. **p<0.05 와 p=0.04** — 같은 결과인데 표현 다름 → reviewer 의심
5. **95% CI 방향이 효과 방향과 모순** — OR<1인데 CI 0.x-1.x

## 다음 단계

→ Self-Gate B 통과 후 Step 6 Critic
