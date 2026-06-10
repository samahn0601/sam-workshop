# `paper_home/` 표준 레이아웃

모든 sam-workshop skill은 다음 폴더 구조를 가정한다. Code 탭 작업 폴더 1개 = 1 논문 = `paper_home/` 1개.

```
paper_home/
├── 00_intake/
│   ├── topic_seed.md              # 한 문장 주제
│   ├── existing_pdfs/             # 본인이 가져온 참고 PDF
│   └── lecture_slides.pdf         # (선택) 시험문제 생성용
├── 01_design/
│   ├── idea_variants.md           # journal-fit-check 산출
│   ├── article_type.md
│   ├── journal_shortlist.md
│   └── decision_history.md        # Self-Gate A 결정
├── 02_research/
│   ├── deep_research.md           # Chat Deep Research 결과
│   ├── reference_candidates.bib
│   └── journal_specs.md           # journal_specs-fetch 결과
├── 03_outline/
│   ├── story_1pager.md            # story-design 산출
│   ├── outline.md                 # Live Artifact 후보
│   └── evidence_map.md
├── 04_draft/
│   ├── manuscript.md                       # ★ Live Artifact (항상 최신)
│   ├── manuscript_v0.1_draft.md            # Step 4 snapshot
│   └── manuscript_versions/                # 모든 history 보존
│       └── manuscript_v0.1_draft.md
├── 05_verify/
│   ├── manuscript_v0.2_verified.md         # 본 step 후 snapshot
│   ├── refcheck_refs.csv                   # R1-R5 결과
│   ├── refcheck_issues.md
│   ├── r6_claim_support.jsonl              # R6 paraphrase 결과
│   ├── r6_summary.md
│   ├── stats_consistency.md
│   └── verification_certificate.md
├── 06_critic/
│   ├── manuscript_v0.3_revised.md          # 본 step 후 snapshot
│   ├── claude_personas.md                  # Reviewer1/2/Editor 페르소나 critique
│   ├── gpt55_critic.md                     # 외부 critic (있으면)
│   ├── area_chair_round1.md                # 통합 판정
│   ├── revision_backlog.jsonl              # accepted=true만 humanize에 전달
│   └── scorecard_9d.md
├── 07_figures/
│   ├── figure_plan.md
│   ├── prompts/                   # figure-prompt-eng 산출
│   ├── candidates/                # GPT-image-2, Nano Banana 2 결과 병렬
│   ├── selected/                  # 최종 채택
│   └── final/                     # DPI/포맷 변환 후
├── 08_package/
│   ├── manuscript_v0.4_humanized.md        # humanize 후 snapshot
│   ├── manuscript_v0.4.1_driftchecked.md   # locked claim drift check 통과
│   ├── manuscript_full.docx                # 최종 .docx (= v0.4.1 변환)
│   ├── manuscript_blinded.docx
│   ├── cover_letter.docx
│   ├── ai_disclosure.md
│   ├── reporting_checklist.pdf
│   ├── tables/
│   └── figures/
├── exam_items/                             # exam-item-builder 산출
│   ├── learning_objectives.md
│   ├── exam_items.jsonl
│   ├── exam_items.md
│   └── item_flaw_report.md
└── .sam/
    ├── manifest.json              # ★ 현재 manuscript 상태 + locked_claims (manifest.schema.json)
    ├── pipeline_state.json        # current_step / mode / target_language (트리거 충돌 방지)
    ├── hitl/
    │   ├── gate_plan.json         # ★ 운전 모드 (gate_plan.schema.json) — 세션 시작 시 작성, 각 step에서 참조
    │   ├── events.jsonl           # HITL 이벤트 누적 (모든 skill이 append)
    │   ├── paper_profile.json     # paper_profile.schema.json
    │   ├── gate_summary.md
    │   └── dial_recommendation.md # hitl-dial-recommender 산출
    ├── memory/
    │   └── session_notes.md
    └── logs/
        └── skill_runs.jsonl
```

## Code 탭 작업 폴더 설정

1. 로컬 폴더 1개 생성: 위 구조
2. Claude Desktop Code 탭에서 이 폴더를 작업 폴더로 연다
3. `manuscript.md`를 메인 작업 파일로 둔다
4. Project Instructions: `_shared/templates/project_instructions.md` 내용을 폴더의 `CLAUDE.md`로 저장(또는 세션 instructions에 붙여넣기)

## Skill의 폴더 접근 규약

- **모든 skill은 `paper_home/` 안에서 상대경로 사용**
- 절대경로 하드코딩 금지
- skill 자신의 자산은 `~/.claude/skills/sam-workshop/{skill}/` 안에서만 읽음

## HITL 이벤트 emit 표준

모든 핵심 skill은 실행 종료 직전 다음 1줄을 `paper_home/.sam/hitl/events.jsonl`에 append:

```json
{"ts":"2026-06-20T13:45:00Z","paper_id":"...","step":5,"gate":"C_verify_critic","event_type":"gate_pass","skill":"verify-reference-essential","engine":"code-script+claude","category":"reference_integrity","severity":2,"description":"...","time_to_fix_min":28}
```

이게 hitl-dial-recommender의 입력.
