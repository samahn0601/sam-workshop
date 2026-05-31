#!/usr/bin/env python3
"""
hitl_recommend.py — sam-workshop / hitl-dial-recommender

Reads paper_home/.sam/hitl/events.jsonl, computes risk score, applies hard
guardrails, and emits dial_recommendation.md (Lab Report metaphor).

Usage:
    python hitl_recommend.py \\
        --events paper_home/.sam/hitl/events.jsonl \\
        --profile paper_home/.sam/hitl/paper_profile.json \\
        --out paper_home/.sam/hitl/dial_recommendation.md
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


DIAL_NAMES = {
    "H4": "8-gate hand-holding",
    "H3": "4-gate standard",
    "H2": "2-gate accelerated",
    "H1": "1-gate Auto-Pilot",
    "H0": "0-gate Sakana style (의학 비권장)",
}


def load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def load_profile(path: Optional[Path]) -> Dict[str, Any]:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def compute_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_gate: Dict[str, List[Dict]] = defaultdict(list)
    by_type: Dict[str, List[Dict]] = defaultdict(list)
    for e in events:
        if e.get("gate"):
            by_gate[e["gate"]].append(e)
        if e.get("event_type"):
            by_type[e["event_type"]].append(e)

    n_events = len(events)
    n_gate_pass = len(by_type.get("gate_pass", []))
    n_gate_fail = len(by_type.get("gate_fail", []))
    n_hallucinations = len(by_type.get("hallucination", []))
    n_critique_accepted = sum(1 for e in by_type.get("critique_decision", [])
                              if e.get("decision") == "accepted")
    n_critique_total = len(by_type.get("critique_decision", []))

    severe_hallucinations = sum(1 for e in by_type.get("hallucination", [])
                                if (e.get("severity") or 0) >= 4)

    # severity by gate
    high_severity_by_gate = {}
    for gate, evs in by_gate.items():
        high_severity_by_gate[gate] = sum(1 for e in evs if (e.get("severity") or 0) >= 4)

    # categories
    cat_counts: Dict[str, int] = defaultdict(int)
    for e in events:
        if e.get("event_type") == "hallucination":
            loc = e.get("location") or e.get("category") or "unknown"
            cat_counts[loc] += 1

    return {
        "n_events": n_events,
        "n_gate_pass": n_gate_pass,
        "n_gate_fail": n_gate_fail,
        "n_hallucinations": n_hallucinations,
        "severe_hallucinations": severe_hallucinations,
        "n_critique_total": n_critique_total,
        "n_critique_accepted": n_critique_accepted,
        "critique_accept_rate": (n_critique_accepted / n_critique_total) if n_critique_total else 0,
        "high_severity_by_gate": high_severity_by_gate,
        "hallucination_locations": dict(cat_counts),
    }


def compute_risk_score(metrics: Dict[str, Any], profile: Dict[str, Any]) -> float:
    """Stage 2: Additive risk score (0-100). Negative terms capped at -5 max
    so that 'clean runs' bonus can never lower the medical safety floor.
    """
    severe_rate = min(1.0, metrics["severe_hallucinations"] / 3)
    verify_fail = min(1.0, metrics["high_severity_by_gate"].get("C_verify_critic", 0) / 2)
    ref_errors = min(1.0, metrics["hallucination_locations"].get("references", 0) / 5)
    stats_errors = min(1.0, metrics["hallucination_locations"].get("statistics", 0) / 3)
    critic_accepted_severe = min(1.0, metrics["n_critique_accepted"] / 5)
    journal_stakes = {"Q1": 1.0, "Q2": 0.7, "Q3": 0.4, "Q4": 0.2}.get(
        profile.get("target_journal_tier", "unknown"), 0.5)
    novelty_penalty = 1.0 if profile.get("novel_method") else 0.0
    clean_runs = min(1.0, profile.get("previous_papers_with_pipeline", 0) / 3)

    score = (
        25 * severe_rate
        + 20 * verify_fail
        + 15 * ref_errors
        + 15 * stats_errors
        + 10 * critic_accepted_severe
        + 10 * journal_stakes
        + 5 * novelty_penalty
        - 5 * clean_runs  # cap: clean run bonus reduced from 10→5 (medical safety)
    )
    return max(0.0, min(100.0, score))


# ============================================================
# Stage 1: Hard Floor Override (Medical Circuit Breaker)
# ============================================================
# 의학 안전 critical 이벤트 발생 시 Risk score와 무관하게 강제 H4.
# Floor는 Stage 2 risk score 계산 결과를 절대 깰 수 없다.

MEDICAL_FLOOR_CATEGORIES_H4 = (
    # 환자 안전 직결 — 반드시 본인 결정
    "drug_dose_error", "drug_contraindication",
    "clinical_recommendation", "guideline_change",
    "irb_violation", "consent_violation", "privacy_breach",
    "mortality_unsupported", "safety_unsupported",
    "guideline_unsupported", "primary_outcome_unsupported",
)

MEDICAL_FLOOR_CATEGORIES_H3 = (
    "retracted_citation", "citation_chimera",
    "primary_outcome_inconsistency", "first_ai_paper",
    "real_journal_submission", "verify_gate_high_severity",
)


# v1.3.1 (post 3AI consult, 2026-05-03) — keyword set expanded after
# Gemini-3.1-pro + GPT-5.5 flagged that the original 7-keyword set missed
# common clinical-trial endpoint terminology. Both English and Korean
# equivalents added. Proximity-rule filtering not yet applied — currently
# any match in category/location/description triggers escalation when
# severity ≥ 3 and the event is stats-related (see _stats_event_is_mortality_or_safety).
# A future patch (P1) may add proximity windowing if D-30 dry-run shows
# false-positive H4 over-escalation.
_MORTALITY_SAFETY_KEYWORDS = (
    # Original v1.3 (preserved)
    "mortality", "safety", "guideline", "drug", "primary_outcome",
    "사망", "안전성", "가이드라인", "1차변수",
    # v1.3.1 — clinical trial endpoints (English)
    "primary endpoint", "primary outcome",
    "secondary endpoint", "secondary outcome",
    "composite endpoint", "composite outcome",
    "adverse event", "adverse effect", "adverse drug reaction",
    "sae",            # serious adverse event
    "saes",
    "adr",            # adverse drug reaction
    "morbidity",
    "complication", "complications",
    "efficacy",
    "toxicity",
    "survival",
    "overall survival",
    "os",             # overall survival (단독 약어, proximity rule 도입 시 demote)
    "progression-free survival", "progression free survival",
    "pfs",
    "disease-free survival",
    "dfs",
    "recurrence", "recurrence-free",
    "relapse",
    "noninferiority", "non-inferiority",
    "superiority",
    "hazard ratio",   # spelled out
    # v1.3.1 — Korean equivalents
    "이상반응", "이상 반응",
    "부작용",
    "합병증",
    "유효성",
    "독성",
    "생존율", "전체 생존율", "무진행 생존율", "무재발 생존율",
    "재발",
    "1차 평가변수", "일차 평가변수", "일차변수", "주요 결과", "주평가변수",
    "이차 평가변수", "복합 평가변수",
    "비열등성", "우월성",
)


def _stats_event_is_mortality_or_safety(event: Dict[str, Any]) -> bool:
    """v1.3 — stats consistency event가 mortality/safety/primary outcome과
    관련되어 있는지 판정. category/location/description 모두 스캔.

    v1.3.1 (post 3AI consult): keyword set 확장 (clinical trial endpoints +
    Korean equivalents). 향후 D-30 dry-run에서 false-positive over-escalation
    관찰되면 proximity rule (e.g., death + outcome/rate within 5 tokens)으로
    demote 검토. 현재는 단순 substring match.
    """
    if (event.get("category") or "").lower() not in (
        "stats_consistency", "statistics", "stats_inconsistency",
        "primary_outcome_inconsistency",
    ) and "stats" not in (event.get("skill") or "").lower():
        return False
    blob = " ".join([
        str(event.get("category", "")),
        str(event.get("location", "")),
        str(event.get("description", "")),
    ]).lower()
    return any(k in blob for k in _MORTALITY_SAFETY_KEYWORDS)


def apply_hard_floor_override(events: List[Dict[str, Any]],
                              profile: Dict[str, Any]) -> Optional[str]:
    """Stage 1: Medical safety circuit breaker.
    Returns 'H4' if any H4 trigger fires, 'H3' if any H3 trigger fires, else None.
    This OVERRIDES any Risk score computation downward — never the other way.

    v1.3 신규 H4 트리거: stats consistency mismatch가 mortality/safety/guideline/
    primary outcome 수치와 관련되면 자동 H4 + Human review 등급 escalate.
    """
    # H4 floor triggers (가장 위험)
    for e in events:
        cat = (e.get("category") or "").lower()
        loc = (e.get("location") or "").lower()
        if any(c in cat or c in loc for c in MEDICAL_FLOOR_CATEGORIES_H4):
            return "H4"
        # Severe hallucination on safety-critical content
        if e.get("event_type") == "hallucination" and \
           (e.get("severity") or 0) >= 4 and \
           any(k in loc for k in ("mortality", "safety", "guideline", "drug")):
            return "H4"
        # v1.3: stats consistency mismatch on mortality/safety/primary outcome
        if (e.get("severity") or 0) >= 3 and _stats_event_is_mortality_or_safety(e):
            return "H4"

    # H3 floor triggers
    h3_hit = False
    for e in events:
        cat = (e.get("category") or "").lower()
        if any(c in cat for c in MEDICAL_FLOOR_CATEGORIES_H3):
            h3_hit = True
            break
    if profile.get("previous_papers_with_pipeline", 0) <= 1:
        h3_hit = True
    if profile.get("submission_intent") == "journal_submission":
        # 실제 투고 의도 시 최소 H3
        h3_hit = True
    return "H3" if h3_hit else None


def apply_hard_guardrails(metrics: Dict[str, Any], profile: Dict[str, Any]) -> Optional[str]:
    """Legacy guardrail (event-summary based). Kept for backward compatibility.
    Prefer apply_hard_floor_override() which inspects raw events directly."""
    if metrics["hallucination_locations"].get("references", 0) >= 2 and \
       metrics["severe_hallucinations"] >= 2:
        return "H4"
    triggers = []
    if metrics["high_severity_by_gate"].get("C_verify_critic", 0) >= 1:
        triggers.append("verify gate high-severity")
    if metrics["hallucination_locations"].get("statistics", 0) >= 1:
        triggers.append("statistics inconsistency")
    if profile.get("previous_papers_with_pipeline", 0) <= 1:
        triggers.append("first/second AI-assisted paper")
    if profile.get("submission_intent") == "journal_submission":
        triggers.append("real journal submission")
    if triggers:
        return "H3"
    return None


def map_score_to_dial(score: float) -> str:
    if score >= 75:
        return "H4"
    if score >= 50:
        return "H3"
    if score >= 30:
        return "H2"
    if score >= 15:
        return "H1"
    return "H0"


def render_report(profile: Dict[str, Any], metrics: Dict[str, Any],
                  risk_score: float, recommended_dial: str,
                  guardrail_min: Optional[str], rationale: List[str],
                  floor_dial: Optional[str] = None) -> str:
    lines = [
        "# 🩺 HITL Dial 처방전 (Lab Report)",
        "",
        f"- 환자 (paper_id): {profile.get('paper_id', 'unknown')}",
        f"- Article type: {profile.get('article_type', 'unknown')}",
        f"- Target journal: {profile.get('target_journal', '-')}",
        f"- 기록된 이벤트: {metrics['n_events']}건",
        "",
        "## 검사 결과",
        "",
        f"| 항목 | 값 |",
        f"|---|---|",
        f"| Risk score | **{risk_score:.1f} / 100** |",
        f"| Gate pass | {metrics['n_gate_pass']} |",
        f"| Gate fail | {metrics['n_gate_fail']} |",
        f"| Hallucinations | {metrics['n_hallucinations']} (severe {metrics['severe_hallucinations']}) |",
        f"| Critique accept rate | {metrics['critique_accept_rate']:.0%} |",
        "",
        "## Hallucination 분포",
        "",
    ]
    if metrics["hallucination_locations"]:
        for loc, cnt in metrics["hallucination_locations"].items():
            lines.append(f"- {loc}: {cnt}")
    else:
        lines.append("- (없음)")
    lines.append("")
    lines.append("## 처방")
    lines.append("")
    score_dial = map_score_to_dial(risk_score)
    if floor_dial == "H4":
        lines.append(f"- ⛔ **Medical Safety Floor (Stage 1)**: 강제 H4 ({DIAL_NAMES['H4']})")
        lines.append(f"  → 임상 안전 critical 이벤트 (drug / IRB / mortality / safety / guideline) 감지. 본 dial 이하 불가.")
    elif floor_dial == "H3":
        lines.append(f"- 🟧 **Conservative Floor (Stage 2)**: 강제 최소 H3 ({DIAL_NAMES['H3']})")
        lines.append(f"  → 첫 파이프라인 사용 / 실제 저널 투고 의도 등의 보수 조건 충족. 임상 안전 알람과는 별개.")
    elif floor_dial:
        # 다른 floor 값이 추가될 경우 generic fallback
        lines.append(f"- ⛔ **HITL Floor Override**: 강제 최소 {floor_dial} ({DIAL_NAMES[floor_dial]})")
    lines.append(f"- Risk score 기반 ({risk_score:.1f}/100): {score_dial} ({DIAL_NAMES[score_dial]})")
    if guardrail_min:
        lines.append(f"- Legacy guardrail: 최소 {guardrail_min} ({DIAL_NAMES[guardrail_min]})")
    lines.append(f"- **최종 권장 Dial: {recommended_dial} ({DIAL_NAMES[recommended_dial]})**")
    lines.append("")
    lines.append("## 사유")
    for r in rationale:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## 절대 위임 불가 영역 (Floor — 모든 dial에서 유지)")
    lines.append("- 임상 권고 / 가이드라인 변경 제안 → 본인 판단")
    lines.append("- 약물 용량, 오리지널 vs 제네릭 → 본인 판단")
    lines.append("- IRB / 윤리 / 환자 동의 문구 → 본인 작성")
    lines.append("- Reference Discussion 핵심 paraphrase 검증 (R6) → 본인 통과")
    lines.append("")
    lines.append("## 재진 시점")
    lines.append("- 다음 논문 1편 후 본 처방전 재발행")
    lines.append("- 누적 3편 깨끗하게 끝나면 한 단계 dial 낮춤 검토")
    return "\n".join(lines)


def render_self_deadline_checklist(profile: Dict[str, Any],
                                    metrics: Dict[str, Any],
                                    events: List[Dict[str, Any]],
                                    floor_dial: Optional[str]) -> str:
    """v1.3 — 워크숍 wrap에서 산출하는 5–7일 자가-마감 체크리스트.
    `last_5min_checklist.py` 템플릿을 워크숍 의미로 재해석:
      - 본 파이프라인 last_5min: '제출 직전 5분 체크'
      - 워크숍 self-deadline: '자가-마감 5–7일 동안 반드시 통과해야 할 항목'
    """
    import time
    paper_id = profile.get("paper_id", "unknown")
    article_type = profile.get("article_type", "unknown")
    target = profile.get("target_journal", "-")
    today = time.strftime("%Y-%m-%d")
    deadline_start = "(워크숍 wrap +5일)"
    deadline_end = "(워크숍 wrap +7일)"

    # open issues from events: gate_fail / hallucination still flagged
    open_issues = []
    for e in events:
        if e.get("event_type") == "gate_fail":
            open_issues.append(
                f"Gate {e.get('gate', '?')} fail — {e.get('description', '미해결')}")
        elif e.get("event_type") == "hallucination" and (e.get("severity") or 0) >= 4:
            open_issues.append(
                f"Severe hallucination at {e.get('location', '?')} — "
                f"{e.get('description', 'fix 필요')}")

    floor_banner = ""
    if floor_dial == "H4":
        floor_banner = (
            "\n> ⛔ **Medical Safety Floor 발동 (Stage 1)**: "
            "본 워크숍 산출물은 의학 안전 critical 이벤트로 인해 H4 강제. "
            "본 체크리스트 ⓪을 반드시 본인이 통과시켜야 투고 가능.\n"
        )
    elif floor_dial == "H3":
        floor_banner = (
            "\n> 🟧 **Conservative Floor 발동 (Stage 2)**: "
            "보수 조건 (첫 파이프라인 / 실제 저널 투고 의도 등)으로 H3 최소. "
            "본 체크리스트 모든 항목 통과 권장.\n"
        )

    open_block = ""
    if open_issues:
        open_block = "\n".join(f"- [ ] {x}" for x in open_issues[:10])
    else:
        open_block = "- (워크숍 wrap 시점에 추적된 미해결 이슈 없음)"

    return f"""# 🗓️ 자가-마감 체크리스트 (Self-Deadline, 5–7일)

**Generated:** {today} (워크숍 wrap)
**Paper:** {paper_id} / {article_type} / {target}
**자가-마감일:** {deadline_start} ~ {deadline_end}

> **워크숍 산출물 = submission-directed ≠ submission-ready.**
> 본 체크리스트는 워크숍 6시간 동안 통과한 항목을 5–7일 후 본인이 한 번 더 검증하도록 설계.
{floor_banner}
---

## ⓪ Medical Safety Floor (필수, dial 무관)

- [ ] Mortality / safety / guideline claim 직접 full text 확인 (R6)
- [ ] 약물 용량 / 상호작용 / 금기 — 본인 1차자료 확인
- [ ] IRB 진술 — 승인 기관, 일자, 환자동의 면제 사유 확인
- [ ] Primary outcome 수치 정합 (Abstract = Results = Table) 본인 재확인

## ① Reporting checklist 부착 (1–2일차)

- [ ] STROBE / CONSORT / CARE / PRISMA / STARD / TRIPOD PDF 첨부
- [ ] Checklist의 모든 item이 manuscript에 어디 있는지 row 기재

## ② AI Use Disclosure 정확성 (2일차)

- [ ] 사용한 AI 모델명 (Claude / GPT / Gemini 등) 정확
- [ ] 어느 단계에서 사용했는지 (draft / verify / critic / figure / 통계)
- [ ] 본인이 검증한 항목 명시

## ③ 결정적 검증 결과 재확인 (3–4일차)

- [ ] G1 abstract word count: AST audit_meter ≤ 한도 ✓
- [ ] G2 body word count: AST audit_meter ≤ 한도 ✓
- [ ] G2.6 ghost/orphan: ghosts 0건 + orphans 0건
- [ ] R1 DOI / R2 metadata / R5 retracted 0건
- [ ] R6 mortality/safety claim — 본인 abstract+full text 통과

## ④ 통계 정합성 재확인 (4–5일차)

- [ ] Abstract 수치 = Results 수치 = Table 수치 (3-way agreement)
- [ ] CI / p-value 표기 일관성
- [ ] denominator / N 명시

## ⑤ 투고 직전 (5–7일차)

- [ ] 1차 저널 spec 최신 버전 재확인 (변경 가능성)
- [ ] Cover letter — 본인 sender info / reviewer 추천 (있으면)
- [ ] Blinded version identity scrub (이름/소속 0 hits)
- [ ] 이중 투고 0 — 본인 진술

---

## 본 워크숍에서 추적된 미해결 이슈

{open_block}

---

> 본 체크리스트의 모든 항목 통과 → 투고 시점 결정.
> 어느 한 항목이라도 unchecked → 투고 보류 + facilitator (or co-author) 상의.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, type=Path)
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--self-deadline-out", type=Path, default=None,
                    help="v1.3: 워크숍 wrap 시 자가-마감 5–7일 체크리스트 출력 경로 "
                         "(예: paper_home/08_package/self_deadline_checklist.md). "
                         "지정 안 하면 생성 안 함.")
    args = ap.parse_args()

    events = load_events(args.events)
    profile = load_profile(args.profile)
    metrics = compute_metrics(events)

    # ═══════════════════════════════════════════════════════════════
    # Stage 1: Medical Floor Override (Hard Circuit Breaker)
    # 의학 안전 critical 이벤트가 있으면 Risk score 무관하게 강제
    # ═══════════════════════════════════════════════════════════════
    floor_dial = apply_hard_floor_override(events, profile)
    floor_triggered = floor_dial is not None

    # ═══════════════════════════════════════════════════════════════
    # Stage 2: Additive Risk Score (참고용, floor를 깰 수 없음)
    # ═══════════════════════════════════════════════════════════════
    risk_score = compute_risk_score(metrics, profile)
    score_dial = map_score_to_dial(risk_score)

    # ═══════════════════════════════════════════════════════════════
    # Legacy guardrail (event-summary 기반, floor와 별도 레이어)
    # ═══════════════════════════════════════════════════════════════
    guardrail_min = apply_hard_guardrails(metrics, profile)

    # ═══════════════════════════════════════════════════════════════
    # Stage 3: 최종 dial 결정
    # — floor가 발동하면 절대 그 아래로 못 내려감
    # — score, guardrail은 floor 위에서만 작동
    # ═══════════════════════════════════════════════════════════════
    dial_order = ["H0", "H1", "H2", "H3", "H4"]
    candidates = [score_dial]
    if guardrail_min:
        candidates.append(guardrail_min)
    if floor_dial:
        candidates.append(floor_dial)
    # 가장 높은 (안전한) dial 선택
    recommended_dial = max(candidates, key=lambda d: dial_order.index(d))

    rationale = []
    if floor_triggered and floor_dial == "H4":
        rationale.append(
            "⛔ **Medical Safety Floor (Stage 1) 발동 → 강제 H4**: "
            "임상 안전 critical 이벤트 (drug / IRB / mortality / safety / guideline) 감지. "
            "Risk score와 무관하게 본 dial 이하로 내릴 수 없음."
        )
    elif floor_triggered and floor_dial == "H3":
        rationale.append(
            "🟧 **Conservative Floor (Stage 2) 발동 → 강제 최소 H3**: "
            "보수 조건 (첫 파이프라인 사용 / 실제 저널 투고 의도 / verify high-severity) 충족. "
            "임상 안전 알람은 아님."
        )
    elif floor_triggered:
        rationale.append(
            f"**HITL Floor 발동 → 강제 최소 {floor_dial}**: "
            f"floor 트리거 충족."
        )
    if metrics["high_severity_by_gate"].get("C_verify_critic", 0) >= 1:
        rationale.append("최근 논문에서 verify gate에서 high-severity 이슈 발생")
    if metrics["severe_hallucinations"] >= 2:
        rationale.append(f"Severe hallucination {metrics['severe_hallucinations']}건 — verify 강화 필요")
    if metrics["critique_accept_rate"] >= 0.5:
        rationale.append(f"외부 critic 채택률 {metrics['critique_accept_rate']:.0%} — critic gate는 유지 권고")
    if profile.get("previous_papers_with_pipeline", 0) <= 1:
        rationale.append("첫/두번째 파이프라인 사용 — 표준 4-gate 유지 권장")
    if profile.get("submission_intent") == "journal_submission":
        rationale.append("실제 저널 투고 목표 — 안전 우선")
    if not rationale:
        rationale.append("이벤트 부족 — 더 많은 데이터 누적 후 재계산 권고")

    report = render_report(profile, metrics, risk_score, recommended_dial,
                            guardrail_min, rationale, floor_dial=floor_dial)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"[dial] floor={floor_dial or '-'} score={risk_score:.1f}/{score_dial} -> {recommended_dial} -> {args.out}")

    # v1.3: self-deadline 5–7일 체크리스트 (--self-deadline-out 지정 시)
    if args.self_deadline_out:
        checklist = render_self_deadline_checklist(profile, metrics, events, floor_dial)
        args.self_deadline_out.parent.mkdir(parents=True, exist_ok=True)
        args.self_deadline_out.write_text(checklist, encoding="utf-8")
        print(f"[self-deadline] -> {args.self_deadline_out}")


if __name__ == "__main__":
    main()
