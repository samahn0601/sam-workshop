---
name: revision-response
description: >
  Use this skill to draft point-by-point response to reviewer comments after
  receiving major/minor revision decision from a medical journal. Trigger when
  user says "R&R 응답", "revision response", "reviewer 답변", "리뷰어 답변",
  "rebuttal", "point-by-point", or has received a revision decision and is
  preparing the response letter. Do not use for initial submission packaging
  (use desk-reject-precheck and the Step 7 packaging flow). Input: editor decision letter +
  reviewer comments + current manuscript. Output:
  paper_home/.../revision/response_letter.md +
  manuscript_v{N+1}_revised.md (with track changes equivalent). Pipeline
  position: Post-acceptance/post-revision (워크숍 v1 미사용, post-workshop).
  Medical context: ICMJE-aligned response format, point-by-point rebuttal,
  reviewer mood management. Trigger keywords: revision response, R&R, rebuttal,
  리비전 응답, 리뷰어 답변, point-by-point, major revision, minor revision.
---

# revision-response (Tier 3 — post-workshop)

> Major/minor revision 받았을 때 reviewer 응답 + 본문 수정 동시 진행. **워크숍에서는 다루지 않음** — 라이프사이클 sustenance 자산.

## 모드

| 모드 | 시간 |
|---|---|
| `standard` | 2–4시간 (reviewer 1–2명, 5–10 comments each) |
| `deep-audit` | 4–8시간 (reviewer 3+, 20+ comments) |

## 입력

- Editor decision letter
- Reviewer 1, 2, 3 comments
- 현 manuscript

## 출력 구조

```
paper_home/
├── revision/
│   ├── decision_letter.md
│   ├── reviewer_comments.md
│   ├── response_letter.md           ← point-by-point
│   ├── changes_summary.md           ← 본문 변경 요약
│   └── manuscript_v{N+1}_revised.md ← 수정된 본문
```

## response_letter.md 표준 양식

```markdown
Dear Editor [name],

We thank you and the reviewers for the careful and constructive comments. We
have addressed all points and revised the manuscript accordingly. Below we
provide a point-by-point response. Reviewer comments are in *italic*; our
responses follow each.

---

# Reviewer 1

## Comment 1.1
*Reviewer wrote: "The methodology section lacks adjustment for confounders."*

**Response:** We agree. We have added multivariate adjustment for age, sex,
BMI, and smoking status (Methods §3.2, p. 5). Updated Table 2 reports adjusted
ORs (aOR 1.42, 95% CI 1.28–1.57). The conclusion remains directionally same;
effect magnitude attenuated by 8% after adjustment, consistent with our prior
hypothesis.

**Changes in manuscript:**
- Methods §3.2 (p. 5): added adjustment description
- Table 2: replaced crude OR with adjusted OR
- Discussion §1 (p. 8): noted attenuation

## Comment 1.2
*"Limitations should mention residual confounding."*

**Response:** Added to Limitations (Discussion §4, p. 9, last paragraph).

# Reviewer 2

## Comment 2.1
...

# Editor

## Comment E.1
...

---

We hope these revisions adequately address all concerns. We look forward to
your decision.

Sincerely,
{Authors}
```

## 절차

### Step 0 — 기밀성 + AI 공시 게이트 (fail-closed) ★

R&R 자료는 일반 문헌이 아니다. 시작 전 확인:

- [ ] **기밀성** — editor decision letter·reviewer comments는 confidential correspondence. 외부 LLM/포털에 올리기 전 **저널 정책과 도구의 데이터 처리 조건**을 확인 ("무조건 금지"가 아니라 **정책 확인 전 진행 금지**). 불확실하면 비식별·요약본만 사용.
- [ ] **보관** — `revision/` 폴더의 기밀 자료는 로컬 보관, 외부 공유 금지.
- [ ] **AI 공시 갱신(ICMJE 2026)** — 이번 revision에서 AI를 응답 작성·본문 수정에 사용했다면, 원고 내 AI disclosure와 cover letter를 **수정 단계에 맞게 갱신**할 항목으로 표시 (AI 저자 불가·인간 책임 불변).

미확인 항목이 있으면 response finalization 금지 (`INCOMPLETE`).

### Step 1 — Comment 분류

```
다음 reviewer comments를 각각 분류:
- Major (반드시 본문 수정 필요)
- Minor (본문 수정 또는 단순 응답)
- Disagree (정중히 반박할 것)
- Already addressed (이미 본문에 있음, 페이지 인용)

각 comment에 fix_strategy 표시.
```

### Step 2 — 본문 수정

각 Major comment에 대응하여 manuscript 수정. version 번호 올림.

### Step 3 — Response 작성

위 표준 양식. 각 comment에:
- Italic 인용 (reviewer 원문)
- Response (정중, 구체적, 위치 인용 — page/line/section/table 중 원고 포맷에서 가용한 식별자)
- Changes (본문 변경 위치)

### Step 4 — Changes summary

editor가 빠르게 훑을 수 있도록 1–2 페이지로:
```markdown
# Summary of Major Changes
1. Methods §3.2: Multivariate adjustment added
2. Table 2: aOR replaces crude OR
3. Discussion §4: Residual confounding limitation added
4. Figure 1: Forest plot updated with adjusted estimates
```

### Step 5 — 본인 정밀 검토

R&R는 reviewer가 매 줄을 본다. AI 작성 100% 의존 금지. 본인이 모든 응답 정독.

## Reviewer 응답 톤

| 상황 | 톤 |
|---|---|
| Major 동의 | "We agree. We have added..." |
| Major 부분 동의 | "We thank the reviewer. We have partially addressed... regarding [부분], we respectfully maintain... because..." |
| Major 정중 반박 | "We thank the reviewer for raising this point. We considered... however, we believe... because [구체적 근거]. We have clarified this in [위치]." |
| Minor 단순 fix | "Done. (p. X)" 또는 "Changed as suggested." |
| Already addressed | "This is addressed in [위치]. We have made it more explicit." |

## Floor (절대 위임 불가)

- **모든 응답 본인 정독** — AI가 작성한 응답 100% 그대로 보내기 금지
- **임상 권고 변경** — reviewer가 권고 변경 요구 시 본인 책임
- **Data re-analysis** — reviewer가 재분석 요구 시 본인 또는 통계사 직접
- **기밀성·AI 공시 게이트(Step 0)** — 확인 전 외부 업로드·제출 금지

## HITL Event Emit

```json
{"ts":"...","step":"R&R","event_type":"critique_decision","skill":"revision-response","engine":"claude","category":"reviewer_response","severity":3,"description":"R1 5 comments: 4 accepted, 1 partial; R2 8 comments: 7 accepted, 1 disagree","decision":"accepted"}
```

## 자주 발생하는 함정

1. **Reviewer mood 무시** — 정중함이 결정적. "Reviewer is wrong" 절대 금지
2. **답변이 모호** — "We have addressed this"만으로 → 페이지/줄 표시 누락 → reviewer 분노
3. **Disagree 사유 부실** — "We respectfully disagree" + 1줄 → 구체 근거 부족
4. **Manuscript와 response letter 불일치** — response에 "added" 했는데 manuscript에 안 들어감
5. **AI 시그니처 응답** — humanize-en/ko 적용 후 본인 정독

## 다음 단계

→ Editor에 response letter + revised manuscript + (필요 시) supplementary 제출
