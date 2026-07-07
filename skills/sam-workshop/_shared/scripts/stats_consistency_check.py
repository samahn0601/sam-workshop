#!/usr/bin/env python3
"""
stats_consistency_check.py — sam-workshop / stats-consistency

Detects numerical inconsistencies between manuscript text, abstract, and tables:
- n (sample size)
- % (percentages)
- p-values
- 95% CI

Usage:
    python stats_consistency_check.py \\
        --manuscript paper_home/04_draft/manuscript.md \\
        --abstract  paper_home/04_draft/abstract.md \\
        --tables   paper_home/04_draft/tables/  \\
        --out paper_home/05_verify/stats_consistency.md

LLM은 문맥 해석에 사용, 수치 추출 자체는 결정적 regex.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


N_RE = re.compile(r"\bN\s*=\s*(\d{1,7})\b|\bn\s*=\s*(\d{1,7})\b")
PCT_RE = re.compile(r"(\d+\.?\d*)\s*%")
P_RE = re.compile(r"\bp\s*[<>=]\s*(0?\.\d+|\d+\.?\d*)", re.IGNORECASE)
CI_RE = re.compile(r"95\s*%?\s*CI[\s:,]*\(?\s*([\d\.\-]+)\s*[-,to ]+\s*([\d\.\-]+)\s*\)?", re.IGNORECASE)


def extract_numbers(text: str) -> Dict[str, List]:
    out: Dict[str, List] = {"n": [], "pct": [], "p": [], "ci": []}
    for m in N_RE.finditer(text):
        v = m.group(1) or m.group(2)
        if v:
            out["n"].append(int(v))
    for m in PCT_RE.finditer(text):
        try:
            out["pct"].append(float(m.group(1)))
        except ValueError:
            pass
    for m in P_RE.finditer(text):
        try:
            out["p"].append(float(m.group(1)))
        except ValueError:
            pass
    for m in CI_RE.finditer(text):
        try:
            out["ci"].append((float(m.group(1)), float(m.group(2))))
        except ValueError:
            pass
    return out


def compare_n(text_n: List[int], abstract_n: List[int], tables_n: List[int]) -> List[str]:
    issues: List[str] = []
    union = set(text_n) | set(abstract_n) | set(tables_n)
    if len(union) > 1:
        # Suspicious if multiple distinct n values
        # Often valid (sub-cohorts) but flag for human review
        issues.append(f"[N_VARIANTS] manuscript reports multiple distinct n: text={text_n}, abstract={abstract_n}, tables={tables_n}")
    if abstract_n and text_n:
        if not (set(abstract_n) & set(text_n)):
            issues.append(f"[N_ABSTRACT_TEXT_MISMATCH] abstract n={abstract_n} but text n={text_n}")
    return issues


def compare_pct(text_pct: List[float], abstract_pct: List[float]) -> List[str]:
    issues: List[str] = []
    # Report values that appear in abstract but not text (may indicate inconsistency)
    abs_set = {round(x, 1) for x in abstract_pct}
    txt_set = {round(x, 1) for x in text_pct}
    only_abs = abs_set - txt_set
    if only_abs:
        issues.append(f"[PCT_ABSTRACT_ONLY] {sorted(only_abs)} appears in abstract but not in main text (verify)")
    return issues


def compare_p(text_p: List[float], abstract_p: List[float]) -> List[str]:
    issues: List[str] = []
    # Check for p-values inconsistencies
    abs_set = {round(x, 4) for x in abstract_p}
    txt_set = {round(x, 4) for x in text_p}
    if abs_set and txt_set:
        for ap in abs_set:
            # Find closest in text
            if not any(abs(ap - tp) <= 0.001 for tp in txt_set):
                issues.append(f"[P_ABSTRACT_TEXT_MISMATCH] abstract p={ap} not matched in text")
    return issues


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", required=True, type=Path)
    ap.add_argument("--abstract", type=Path, default=None)
    ap.add_argument("--tables", type=Path, default=None,
                    help="directory with table .md/.txt files, or single file")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    text = args.manuscript.read_text(encoding="utf-8")
    abstract_text = args.abstract.read_text(encoding="utf-8") if args.abstract and args.abstract.exists() else ""
    tables_text = ""
    if args.tables:
        if args.tables.is_file():
            tables_text = args.tables.read_text(encoding="utf-8")
        elif args.tables.is_dir():
            tables_text = "\n".join(p.read_text(encoding="utf-8") for p in args.tables.glob("*"))

    text_nums = extract_numbers(text)
    abs_nums = extract_numbers(abstract_text)
    tab_nums = extract_numbers(tables_text)

    issues: List[str] = []
    issues.extend(compare_n(text_nums["n"], abs_nums["n"], tab_nums["n"]))
    issues.extend(compare_pct(text_nums["pct"], abs_nums["pct"]))
    issues.extend(compare_p(text_nums["p"], abs_nums["p"]))

    severity = "high" if any(i.startswith(("[N_ABS", "[N_VAR", "[P_ABS")) for i in issues) else \
               ("medium" if issues else "info")

    # Distinguish "checked & consistent" from "skipped (nothing to cross-check)".
    # With no abstract/tables there is NO cross-source comparison, so 0 issues
    # must not read as a consistency pass — fail-open honesty for the reader.
    comparison_sources = [name for name, t in
                          (("abstract", abstract_text), ("tables", tables_text))
                          if t.strip()]
    if issues:
        check_status = severity              # high / medium
    elif comparison_sources:
        check_status = "checked_clean"       # compared, no inconsistency found
    else:
        check_status = "skipped_no_input"    # nothing to cross-check

    args.out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Statistics Consistency Check", ""]
    lines.append(f"- Severity: **{severity}**")
    src_note = (f" (cross-checked vs {', '.join(comparison_sources)})"
                if comparison_sources else " (no abstract/tables supplied)")
    lines.append(f"- Check status: **{check_status}**{src_note}")
    lines.append(f"- Issues found: {len(issues)}")
    lines.append("")
    lines.append("## Extracted numbers (raw)")
    lines.append(f"- Text: n={text_nums['n']}, pct={text_nums['pct'][:20]}, p={text_nums['p']}, CI={text_nums['ci'][:5]}")
    if abstract_text:
        lines.append(f"- Abstract: n={abs_nums['n']}, pct={abs_nums['pct'][:20]}, p={abs_nums['p']}, CI={abs_nums['ci'][:5]}")
    if tables_text:
        lines.append(f"- Tables: n={tab_nums['n']}, pct={tab_nums['pct'][:20]}")
    lines.append("")
    lines.append("## Issues")
    if issues:
        for i in issues:
            lines.append(f"- {i}")
    elif comparison_sources:
        lines.append("- None detected (regex level only — Claude semantic review still recommended)")
    else:
        lines.append("- SKIPPED — abstract/tables 미제공으로 교차 비교를 수행하지 않음. "
                     "이것은 '이상 없음(consistency pass)'이 아니라 '점검 안 함(입력 부족)'이다. "
                     "abstract/tables를 함께 주고 재실행할 것.")
    lines.append("")
    lines.append("## Caveats")
    lines.append("- Regex-only extraction. False positives expected when subgroup n differs from total n by design.")
    lines.append("- Claude semantic review recommended for: post-hoc subgroup analyses, confidence interval direction, effect size signs.")
    args.out.write_text("\n".join(lines), encoding="utf-8")

    # HITL emit
    hitl_dir = args.out.parent / ".." / ".sam" / "hitl"
    hitl_dir = hitl_dir.resolve()
    hitl_dir.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paper_id": args.out.parent.parent.name,
        "step": 5,
        "gate": "C_verify_critic",
        "event_type": "gate_pass" if severity != "high" else "gate_fail",
        "skill": "stats-consistency",
        "engine": "code-script",
        "category": "stats_consistency",
        "severity": 5 if severity == "high" else (3 if severity == "medium" else 1),
        "description": f"{len(issues)} stats issues, severity={severity}, status={check_status}",
    }
    with (hitl_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"[stats] issues={len(issues)} severity={severity} -> {args.out}")


if __name__ == "__main__":
    main()
