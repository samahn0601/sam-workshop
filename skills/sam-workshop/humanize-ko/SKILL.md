---
name: humanize-ko
description: >
  Use this skill to humanize Korean medical manuscript prose drafted with AI
  assistance: remove AI-signature Korean vocabulary, normalize translation
  artifacts, retain scientific accuracy. Trigger when user says "국문 humanize",
  "한국어 자연화", "번역체 제거", "AI 시그니처 한국어", "휴머나이즈 국문",
  "natural Korean", or operates in Step 7 (Humanize & Package) of sam-workshop pipeline (Korean
  manuscripts only). Do not invent data, results, p-values, citations, or
  change effect direction. Use humanize-en for English manuscripts. Input:
  paper_home/04_draft/manuscript.md (Korean) +
  paper_home/06_critic/revision_backlog.jsonl (accepted:true only). Output: in-place edit + optional
  paper_home/04_draft/manuscript_versions/manuscript_humanized_v{N}.md.
  Pipeline position: sam-workshop Step 7. Medical context: KAMJE/한국 의학저널
  스타일, 번역체 검출, 의학 한국어 관용 표현. Trigger keywords: 국문, 한국어,
  번역체, AI 시그니처 국문, 휴머나이즈, 자연스러운 한국어, polish 한국어.
---

# humanize-ko (Step 7 — Humanize & Package)

> AI가 쓴 국문 manuscript를 한국어 학자가 쓴 것처럼 다듬되, **과학적 정확성·KAMJE 관행은 절대 깨지 않는다.**

## 윤리 원칙

이 스킬은 의미를 보존하면서 문장 흐름·자연스러움을 개선하는 도구다. **AI 사용 사실을 숨기거나 AI 탐지를 회피하기 위한 용도가 아니다.** 원고 준비에 AI를 사용했다면 대상 저널 정책에 따라 cover letter·원고 내 적절한 위치에 공개한다(ICMJE). 정확성·독창성·인용·최종 문구의 책임은 인간 저자에게 있다. (국문 자연화 = 구어화가 아니라 번역투 완화·호응 정리·과도한 수식 축소 — 자연스러운 연결어까지 전부 삭제하는 과교정 금지.)

## Non-Negotiables (humanize-en과 동일 8조)

1. 데이터/결과/p값/CI/표본수/방법/참고문헌/저자/연도/저널 **날조 금지**. 빠진 것 → `[ADD: 내용]`
2. p값/CI/명시적 출처 없이 "통계적 유의" 주장 금지
3. 효과 방향, 기준군, 통계 해석 **변경 금지**
4. 불확실성 격상 금지 ("non-significant" → "trend"로 reframe X)
5. 의미 보존 — 명료/흐름만 개선
6. 내부 일관성 — 변수, 약어, 단위, 시점, 통계 형식, 그림/표 ref
7. 인용 미제공 → `[ADD: 인용]`
8. 정확성 우선 — 문체 규칙과 충돌 시 정확성 승

## AI 시그니처 (한국어판)

**어휘**
- "더불어", "또한 (단락 시작)", "추가적으로"
- "본 연구는 ~을 시사한다" (반복)
- "포괄적인", "심층적인", "광범위한", "주요한", "결정적인"
- "탐구하다", "조명하다", "활용하다", "촉진하다"
- "주목할 만한", "특히 강조할", "중요한 점은"
- "혁신적인 통찰", "새로운 관점을 제시"

**번역체 (영문 직역)**
- "~에 있어서" → "~에서"
- "~함에 있어" → "~할 때"
- "그것은 ~이다" (대명사 직역) → 주어 명시
- "보여진다" (수동 직역) → "보인다"
- "~에 의해 보고되었다" → "~이 보고하였다"
- "이러한 결과들은" → "이 결과는" (복수형 남용 X)
- "있어서의" → 한국어로 자연 수정
- "~로의 변화" → "~으로의 변화"

**기계적 패턴**
- 모든 문장 길이 비슷 (40–60자)
- "첫째, ... 둘째, ... 셋째, ..." 기계적 enumeration
- 모든 단락이 "본 연구는"으로 시작
- "~ㄴ다" / "~다" 종결 비율 단조

## 한국어 의학 문체 표준 (KAMJE 관행)

- 학술 문체: ~다, ~이다 (구어 ~요/~죠 금지)
- 약어: 첫 등장 시 정의 ("관상동맥질환(coronary artery disease, CAD)") → 이후 CAD
- 단위: SI 단위 우선, 임상 관행 단위 병기 ("혈압 120 mmHg (16.0 kPa)")
- 약물명: 일반명 (성분명) — 상품명은 첫 등장 시만 괄호
- 인용: 본문 [n] 또는 (저자, 연도) 저널 spec 따름
- 수치: 한글 vs 아라비아 — 4 이상은 아라비아, 단위 동반 시 항상 아라비아

## 모드

| 모드 | 시간 | 범위 |
|---|---|---|
| `workshop-mini` | 15분 | AI 시그니처 + 번역체 1 pass |
| `standard` | 35분 | + 문장 리듬 + 단락 구조 |
| `deep-audit` | 60분 | + 저널-specific 표기 |

## 입력

- `paper_home/04_draft/manuscript.md` (Korean)
- `paper_home/01_design/journal_shortlist.md` — KAMJE 저널 spec
- `paper_home/06_critic/revision_backlog.jsonl` — **accepted:true 항목만 반영** (비승인 반영 금지; 포맷 위반 시 HITL emit)

## 절차 (workshop-mini, 15분)

### Step 1 (5분) — AI 시그니처 + 번역체 제거

```
다음 manuscript에서:
1. AI 시그니처 어휘 ("더불어", "탐구하다", "포괄적인" 등) 자연 한국어로 교체
2. 번역체 ("~에 있어서", "보여진다", "~로 보고되었다") 자연 표현으로
3. 8 Non-Negotiables 준수
4. 변경 사항 diff 형식 출력
```

### Step 2 (5분) — 문장 리듬 + 단락 구조

```
다음 단락에서:
- 모든 문장 40–60자 비슷한 패턴이면 1개 짧게/길게 변형
- "본 연구는"으로 시작하는 단락 반복 → 다른 시작
- 종결 패턴 ("~다" / "~이다") 단조 → 변형
- 단락 길이 다양성 확보

Methods/Results 면제.
```

### Step 3 (3분) — 표기 일관성

```
한국어 의학 표기 점검:
- 약어 첫 정의 후 일관 사용
- 단위 형식 통일
- 약물 일반명/상품명 일관
- 한글-아라비아 숫자 규칙 (4 이상 아라비아)
- 인용 형식 통일

수정 list.
```

### Step 4 (2분) — Post-humanize drift check + Self-Gate D pre-check

diff에 잡힌 변경 문장만(전체 재검증 금지): `style-only / claim-touching / uncertain` 태깅 → claim-touching·uncertain만 원문 Δ check(수치·효과방향) + R6 spot 재확인 + revision_backlog accepted:true 대조 → drift 의심 시 해당 문장 원문 롤백 + diff 기록.

## Output 표준

In-place edit + diff 표:

```markdown
# Humanize-ko Diff

| # | Section | Before | After | Reason |
|---|---|---|---|---|
| 1 | Discussion §1 | "본 연구는 포괄적인 분석을 통해..." | "본 연구는 X를 분석하여..." | AI 시그니처 + 의미 명료화 |
| 2 | Methods §2 | "~에 있어서" | "~에서" | 번역체 제거 |
```

## HITL Event Emit

```json
{"ts":"...","step":7,"gate":"D_finish","event_type":"gate_pass","skill":"humanize-ko","engine":"claude","category":"humanize_ko","severity":1,"description":"AI 시그니처 8건, 번역체 12건 수정","time_to_fix_min":15}
```

## 결정적 vs LLM 분리

- **결정적 (regex)**: AI 시그니처 어휘 검출, 번역체 패턴, 한글-숫자 규칙
- **LLM**: 자연 한국어 대체, 의학 관용 표현, 단락 구조 판단

## Solo + Claude-only

기본. 외부 도구 불필요.

## Floor (절대 위임 불가)

- 효과 방향
- 인용 추가/삭제
- 약물명 (일반명 vs 상품명) — 본인 검증

## Self-Gate D 체크리스트

- [ ] AI 시그니처 어휘 0건
- [ ] 번역체 핵심 패턴 0건
- [ ] [ADD: ...] 모두 해결
- [ ] 효과 방향 변경 0건
- [ ] 약어/단위/약물명 일관성

## Few-shot 예시

### Before (AI 번역체 + 시그니처)
```
본 연구는 한국 청소년에 있어서의 전자담배 사용에 대한 포괄적인 분석을
통해, 그것이 사회적 우울에 미치는 영향에 대한 새로운 통찰을 제공한다.
더불어, 이러한 결과들은 향후 연구를 위한 중요한 기초를 마련한다고 볼 수
있다.
```

### After (humanized)
```
본 연구는 한국 청소년의 전자담배 사용이 사회적 우울에 어떻게 영향을
미치는지 분석하였다. 이 결과는 향후 연구의 출발점이 될 수 있다.
```

→ 86자→64자, 시그니처 6건 제거, 번역체 4건 제거, 의미 보존.

## 자주 발생하는 함정

1. **"본 연구는" 단락 반복** — 4–5단락 모두 같은 시작 → 의심
2. **"있어서/통해/등을" 남용** — 번역체 마커
3. **약어 정의 누락** — 첫 등장 후 영문 약어만 사용 → KAMJE 표기 위반
4. **약물 일반명/상품명 혼용** — Champix/varenicline 일관성
5. **숫자 표기** — "다섯 명의 환자"(N≥4 아라비아 위반) → "5명의 환자"
6. **종결 단조** — 모든 문장 "~다" → 가끔 "~이다", "~한다" 변형

## 다음 단계

→ Step 4의 drift check 완료 → desk-reject-precheck (Step 7 quick scan) → Step 10 Wrap & Next
