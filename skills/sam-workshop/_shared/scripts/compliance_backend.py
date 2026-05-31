#!/usr/bin/env python3
"""
compliance_backend.py — sam-workshop deterministic compliance checks (v1.3)

Self-contained backend for hybrid LLM+AST compliance checking, ported from
the main pipeline's `shared/scripts/compliance.py` (v1.2 patches G1/G2/G2.6).
Workshop pack ships standalone — code lives inside the workshop repo, not
referenced cross-pipeline.

Functions exposed:
  - abstract_wordcount_max  (G1)
  - body_wordcount_max      (G2) + _extract_body_text helper
  - citation_reference_integrity  (G2.6, ghost/orphan deterministic)

Workshop integration:
  1. desk-reject-precheck #3 word count   → abstract_wordcount_max + body_wordcount_max
  2. verify-reference-essential R3        → citation_reference_integrity
     (complements the regex-only check already in ref_verify_pubmed.py with
      bracket-range expansion: [1,2], [1-3], [1, 2-4] all expand correctly)

Design from 2026-05-03 3AI consult (workshop-port-strategy):
  - LLM is coach, AST is audit meter — never replace the LLM precheck wholesale.
  - Pass / Fix before self-deadline / Human review (3-grade output).
  - Korean 어절 + Vancouver citations [1] mixed text supported.

CLI:
    # Single-skill use, JSON output:
    python compliance_backend.py wordcount-abstract \\
        --abstract paper_home/04_draft/abstract.md \\
        --max 250

    python compliance_backend.py wordcount-body \\
        --manuscript paper_home/04_draft/manuscript.md \\
        --max 4000

    python compliance_backend.py citation-integrity \\
        --manuscript paper_home/04_draft/manuscript.md \\
        --refs      paper_home/04_draft/references.txt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ============================================================
# 0. ValidationResult dataclass (3-grade workshop output)
# ============================================================

@dataclass
class ValidationResult:
    """Compliance result with workshop-friendly 3-grade output."""
    name: str
    status: str  # "pass" | "fail" | "warn" | "skip"
    message: str = ""
    evidence: dict = field(default_factory=dict)
    auto_fixable: bool = False
    suggested_fix: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "evidence": self.evidence,
            "auto_fixable": self.auto_fixable,
            "suggested_fix": self.suggested_fix,
            "workshop_grade": self.workshop_grade(),
        }

    def workshop_grade(self) -> str:
        """3-grade label for workshop UX (consensus from 2026-05-03 3AI consult).

        v1.3.1 (post 3AI consult): label changed from bare "Pass" to
        "Workshop check passed" to prevent participants misreading green
        as "submission-ready" / "journal-approved" (automation bias risk
        flagged by both Gemini and GPT-5.5). The full Green-meaning
        disclaimer is rendered in the SKILL.md output, not duplicated here.
        """
        if self.status == "pass":
            return "Workshop check passed"
        if self.status == "skip":
            return "Workshop check passed"  # spec didn't require this
        if self.status == "warn":
            return "Fix before self-deadline"
        # fail
        if self.auto_fixable:
            return "Fix before self-deadline"
        return "Human review required"


def _pass(name: str, msg: str = "", evidence: dict | None = None) -> ValidationResult:
    return ValidationResult(name=name, status="pass", message=msg,
                            evidence=evidence or {})


def _fail(name: str, msg: str, evidence: dict | None = None,
          auto_fixable: bool = False, suggested_fix: str = "") -> ValidationResult:
    return ValidationResult(name=name, status="fail", message=msg,
                            evidence=evidence or {},
                            auto_fixable=auto_fixable, suggested_fix=suggested_fix)


def _warn(name: str, msg: str, evidence: dict | None = None) -> ValidationResult:
    return ValidationResult(name=name, status="warn", message=msg,
                            evidence=evidence or {})


def _skip(name: str, msg: str = "") -> ValidationResult:
    return ValidationResult(name=name, status="skip", message=msg)


# ============================================================
# 1. Patterns (Vancouver citations, markdown links, URLs, emails)
# ============================================================

# Vancouver-style numeric inline citations: [1], [1,2], [1-3], [1, 2, 3]
_VANCOUVER_CITE_PAT = re.compile(r"\[\s*\d+(?:\s*[\-,]\s*\d+)*\s*\]")

# Markdown links: count by label only, drop the URL
_MD_LINK_PAT = re.compile(r"\[([^\]]+)\]\([^\)]+\)")

# Bare URLs (http/https) — drop from word count
_BARE_URL_PAT = re.compile(r"https?://\S+")

# Email addresses — drop from body word count (rare in body anyway)
_EMAIL_PAT = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


# Default body section labels (Markdown H2/H3). Covers IMRaD, Letters/Brief
# Reports, Case Reports (Case Presentation / Case Description), Korean-language
# manuscripts, and JAMA-style structured-abstract subsections.
#
# History:
#   2026-05-03 D-37 smoke: case_report_ghost fixture surfaced "Case Presentation"
#     missing → added Case-report family.
#   2026-05-03 v1.3.1 (post 3AI consult): added Patients and Methods, Case
#     Description / Clinical Presentation / Patient Perspective / Informed
#     Consent variants (GPT-5.5 + Gemini consensus). Numbered-heading prefixes
#     handled via _normalize_heading() rather than bloating this list. Korean
#     headings (서론/방법/결과/고찰/증례) added to support mixed-language manuscripts.
_DEFAULT_BODY_SECTION_LABELS = [
    # IMRaD core
    r"Background",
    r"Introduction",
    r"Materials and Methods",
    r"Methods",
    r"Patients and Methods",
    r"Methodology",
    r"Study Design",
    r"Results",
    r"Findings",
    r"Discussion",
    r"Limitations and Implications",
    r"Limitations",
    r"Implications",
    r"Conclusion",
    r"Conclusions",
    # Case-report family
    r"Case Presentation",
    r"Case Description",
    r"Case Summary",
    r"Case Report",
    r"Clinical Presentation",
    r"Patient Perspective",
    r"Case",
    # Editorial / commentary / viewpoint variants
    r"Main Text",
    r"Body",
    r"Commentary",
    r"Viewpoint",
    r"Observation",
    r"Observations",
    # Korean equivalents (서론/방법/결과/고찰/증례 + variations)
    r"서론",
    r"배경",
    r"방법",
    r"연구 ?방법",
    r"대상 및 방법",
    r"결과",
    r"고찰",
    r"논의",
    r"결론",
    r"증례",
    r"환자",
    r"증례 보고",
    r"임상 ?소견",
]

# Default back-matter / excluded sections. Anything inside these is dropped
# from word count and citation-integrity body extraction.
#
# History:
#   2026-05-03 v1.3.1: added Declarations / Ethics approval variants /
#     Consent for publication / Availability of data and materials /
#     Bibliography / Literature Cited / Works Cited / Korean equivalents.
_DEFAULT_EXCLUDED_SECTION_LABELS = [
    r"Title Page",
    r"Structured Abstract",
    r"Abstract",
    # Ethics / consent variants
    r"Ethics",
    r"Ethics approval",
    r"Ethics approval and consent to participate",
    r"Consent for publication",
    r"Informed Consent",
    r"IRB(?:\s*Statement)?",
    r"Acknowledg(?:e?ments)?",
    r"AI Use Disclosure",
    r"Author Contributions",
    r"CRediT",
    r"Competing Interests",
    r"Conflicts? of Interest",
    r"Declarations",
    r"Funding",
    r"Data Availability",
    r"Availability of data and materials",
    r"Code Availability",
    r"Supplementary",
    r"Supplementary Material",
    r"Supplementary Information",
    # Reference list variants
    r"References",
    r"Reference",
    r"Bibliography",
    r"Literature Cited",
    r"Works Cited",
    # Floats
    r"Table\s*\d+\.?",
    r"Figure\s*\d+\.?",
    r"Tables?",
    r"Figures?",
    # Korean back-matter
    r"초록",
    r"감사의 글",
    r"이해상충",
    r"이해 ?상충",
    r"연구비",
    r"자료 ?이용 ?가능성",
    r"저자 ?기여",
    r"참고 ?문헌",
    r"인용 ?문헌",
]


# Numbered-heading prefix that should be stripped before label matching.
# Examples: "1. Introduction" → "Introduction", "2 Methods" → "Methods",
# "III. Results" → "Results" (Roman numerals up to L), "1.1 Subsection" → ignored
# (only top-level numbering stripped — sub-numbering left intact for clarity).
_NUMBERED_HEADING_PREFIX = re.compile(
    r"^\s*(?:"
    r"(?:[IVXL]+\.?)|"          # Roman numerals
    r"(?:\d+\.?)"               # Arabic numerals (no sub-numbering like 1.1)
    r")\s+",
    re.IGNORECASE,
)


def _normalize_heading(heading: str) -> str:
    """Strip numbered-prefix and surrounding whitespace before label matching.
    Returns the lowered, trimmed heading text. Idempotent."""
    return _NUMBERED_HEADING_PREFIX.sub("", heading).strip()


# ============================================================
# 2. Word-count helpers
# ============================================================

def _strip_vancouver_citations(text: str) -> str:
    """Remove Vancouver-style numeric inline citations [1], [1,2], [1-3]
    so they don't inflate word count."""
    return _VANCOUVER_CITE_PAT.sub(" ", text)


def _strip_for_wordcount(text: str) -> str:
    """Apply all word-count normalizations: Vancouver citations stripped,
    markdown links collapsed to label, bare URLs/emails removed.

    INCLUDES markdown link labels (visible reader text). EXCLUDES URL/href
    (machine-readable navigation).
    """
    text = _strip_vancouver_citations(text)
    text = _MD_LINK_PAT.sub(r"\1", text)        # [label](url) → label
    text = _BARE_URL_PAT.sub(" ", text)          # bare URLs → drop
    text = _EMAIL_PAT.sub(" ", text)             # emails → drop
    # Strip Markdown emphasis markers / heading hashes / bullet markers
    text = re.sub(r"[#*_`]+", " ", text)
    text = re.sub(r"^\s*[-+>]\s+", " ", text, flags=re.MULTILINE)
    return text


def _count_words(text: str) -> int:
    """Word count after normalization. Whitespace-separated tokens of word
    characters or alphanumerics. Korean 어절 (whitespace-separated chunks)
    are counted; ASCII tokens are counted; mixed tokens counted as one.
    Punctuation-only tokens are not counted."""
    normalized = _strip_for_wordcount(text)
    tokens = [t for t in re.split(r"\s+", normalized.strip()) if t]
    return sum(1 for t in tokens if re.search(r"\w", t))


def _strip_structured_abstract_labels(abstract_text: str,
                                       known_labels: list[str] | None = None) -> str:
    """Remove leading 'Background:' / 'Methods:' / 'Conclusion.' style
    structured-abstract labels. Spec-mandated structural markers, not prose."""
    if not known_labels:
        known_labels = [
            "Objective", "Background", "Materials and Methods", "Methods",
            "Results", "Findings", "Discussion", "Conclusion", "Conclusions",
            "Aim", "Aims", "Purpose",
        ]
    label_alts = "|".join(re.escape(l) for l in known_labels)
    pat = re.compile(rf"(?:^|\n)(?:\*\*\s*)?(?:{label_alts})(?:\*\*)?\s*[:\.]\s*",
                     flags=re.IGNORECASE)
    return pat.sub(" ", abstract_text)


# ============================================================
# 3. G1: Abstract word count
# ============================================================

def abstract_wordcount_max(abstract_text: str, *,
                            max_words: int,
                            exclude_section_labels: bool = True,
                            exclude_vancouver_citations: bool = True) -> ValidationResult:
    """G1: Verify abstract word count ≤ max_words.

    Spec-driven defaults:
      - Vancouver citations [1] excluded (not prose tokens).
      - Structured-abstract labels (Background:/Methods:/etc) excluded.

    Returns FAIL if over max, PASS otherwise.
    """
    text = abstract_text or ""
    if exclude_section_labels:
        text = _strip_structured_abstract_labels(text)
    count = _count_words(text)
    evidence = {
        "count": count,
        "max": max_words,
        "exclude_section_labels": exclude_section_labels,
        "exclude_vancouver_citations": exclude_vancouver_citations,
    }
    if count <= max_words:
        return _pass("abstract_wordcount_max",
                     f"abstract is {count} words (≤ {max_words})",
                     evidence)
    return _fail("abstract_wordcount_max",
                 f"abstract is {count} words, exceeds spec max of {max_words}",
                 evidence,
                 auto_fixable=False,
                 suggested_fix=f"Trim {count - max_words} word(s) from the abstract. "
                               f"Look for redundant qualifiers and adverbs first.")


# ============================================================
# 4. G2: Body word count + section extractor
# ============================================================

def _extract_body_text(manuscript_text: str,
                       body_section_labels: list[str] | None = None,
                       excluded_section_labels: list[str] | None = None) -> tuple[str, list[str]]:
    """Extract the 'body' portion of a Markdown manuscript: everything
    inside H2 sections whose heading matches a body label, excluding
    everything inside excluded labels.

    Returns: (body_text, list_of_section_names_included).
    """
    body_pats = [re.compile(rf"^{l}\b", re.IGNORECASE)
                 for l in (body_section_labels or _DEFAULT_BODY_SECTION_LABELS)]
    excl_pats = [re.compile(rf"^{l}\b", re.IGNORECASE)
                 for l in (excluded_section_labels or _DEFAULT_EXCLUDED_SECTION_LABELS)]

    parts = re.split(r"\n##\s+", "\n" + manuscript_text)
    sections: list[tuple[str, str]] = []
    for raw in parts[1:]:
        lines = raw.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""
        sections.append((heading, body))

    included: list[str] = []
    body_chunks: list[str] = []
    for heading, body in sections:
        # Normalize: strip "1. ", "III. " prefixes so "1. Introduction" → matches "Introduction"
        h_norm = _normalize_heading(heading)
        is_body = any(p.match(h_norm) for p in body_pats)
        is_excl = any(p.match(h_norm) for p in excl_pats)
        # Excluded wins over body when both match — back-matter takes priority
        # (e.g., "Acknowledgements" should never count as body even if some body
        # label list happens to contain a substring).
        if is_excl:
            continue
        if is_body:
            included.append(heading)  # report original heading, not normalized
            body_chunks.append(body)
    return ("\n\n".join(body_chunks), included)


def body_wordcount_max(manuscript_text: str, *,
                       max_words: int,
                       body_section_labels: list[str] | None = None,
                       excluded_section_labels: list[str] | None = None,
                       exclude_vancouver_citations: bool = True) -> ValidationResult:
    """G2: Verify body word count ≤ max_words.

    Body = sections matching `body_section_labels` (default IMRaD-ish set).
    Everything else (Title page, Abstract, Ethics, Funding, CRediT,
    Competing Interests, Data Availability, References, Table/Figure
    captions) is excluded.

    Vancouver inline citations [n] are not counted by default.
    """
    body_text, included = _extract_body_text(
        manuscript_text,
        body_section_labels=body_section_labels,
        excluded_section_labels=excluded_section_labels,
    )
    count = _count_words(body_text) if exclude_vancouver_citations else \
            _count_words(body_text.replace("[", " [ "))
    evidence = {
        "count": count,
        "max": max_words,
        "included_sections": included,
        "exclude_vancouver_citations": exclude_vancouver_citations,
    }
    if not included:
        return _warn("body_wordcount_max",
                     "no body sections matched the label set; "
                     "spec or section names may need adjustment",
                     evidence)
    if count <= max_words:
        return _pass("body_wordcount_max",
                     f"body is {count} words (≤ {max_words}) "
                     f"across {len(included)} section(s)",
                     evidence)
    return _fail("body_wordcount_max",
                 f"body is {count} words, exceeds spec max of {max_words}",
                 evidence,
                 auto_fixable=False,
                 suggested_fix=f"Trim {count - max_words} word(s) from the body. "
                               f"Discussion is usually the most compressible.")


# ============================================================
# 5. G2.6: Citation–reference integrity (ghost/orphan deterministic)
# ============================================================

def citation_reference_integrity(body_text: str, refs_text: str) -> ValidationResult:
    """G2.6: every [n] cited in body has a matching numbered reference in
    the reference list, and every numbered reference is cited at least once.

    Ghost citation = cited [n] but no ref n in the list.
    Orphan reference = ref n in list but not cited in body.

    Bracket-range expansion: [1,2], [1-3], [1, 2-4] all expand correctly.
    """
    cited: set[int] = set()
    for m in _VANCOUVER_CITE_PAT.finditer(body_text):
        token = m.group(0).strip("[]").replace(" ", "")
        for chunk in token.split(","):
            if "-" in chunk:
                a, b = chunk.split("-", 1)
                try:
                    a, b = int(a), int(b)
                    cited.update(range(min(a, b), max(a, b) + 1))
                except ValueError:
                    continue
            else:
                try:
                    cited.add(int(chunk))
                except ValueError:
                    continue

    ref_nums: set[int] = set()
    for line in refs_text.split("\n"):
        m = re.match(r"^\s*(\d+)\.\s+\S", line)
        if m:
            ref_nums.add(int(m.group(1)))

    if not cited and not ref_nums:
        return _skip("citation_reference_integrity",
                     "no inline citations or numbered references found")

    ghosts = sorted(cited - ref_nums)
    orphans = sorted(ref_nums - cited)
    evidence = {
        "cited_count": len(cited),
        "ref_count": len(ref_nums),
        "ghost_citations": ghosts,
        "orphan_references": orphans,
    }
    if ghosts or orphans:
        msgs = []
        if ghosts:
            msgs.append(f"본문 인용 {ghosts} 있으나 ref list에 항목 없음 (ghost)")
        if orphans:
            msgs.append(f"ref list에 항목 {orphans} 있으나 본문 미인용 (orphan)")
        return _fail("citation_reference_integrity",
                     "; ".join(msgs),
                     evidence,
                     auto_fixable=False,
                     suggested_fix="Either add the missing reference entries or "
                                   "remove the orphan reference(s) from the list. "
                                   "Re-number remaining refs sequentially.")
    return _pass("citation_reference_integrity",
                 f"all {len(cited)} citations resolve to refs; "
                 f"all {len(ref_nums)} refs cited at least once",
                 evidence)


# ============================================================
# 6. CLI
# ============================================================

def _read_text(path: Path) -> str:
    if not path.exists():
        sys.exit(f"file not found: {path}")
    return path.read_text(encoding="utf-8")


def _emit(result: ValidationResult) -> int:
    """Print result as JSON and return exit code (0=pass, 1=fail)."""
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.status in ("pass", "skip", "warn") else 1


def cli_wordcount_abstract(args: argparse.Namespace) -> int:
    text = _read_text(Path(args.abstract))
    result = abstract_wordcount_max(text, max_words=args.max)
    return _emit(result)


def cli_wordcount_body(args: argparse.Namespace) -> int:
    text = _read_text(Path(args.manuscript))
    result = body_wordcount_max(text, max_words=args.max)
    return _emit(result)


def cli_citation_integrity(args: argparse.Namespace) -> int:
    body_md = _read_text(Path(args.manuscript))
    refs_text = _read_text(Path(args.refs))
    body_only, _ = _extract_body_text(body_md)
    target = body_only or body_md
    result = citation_reference_integrity(target, refs_text)
    return _emit(result)


def main() -> None:
    p = argparse.ArgumentParser(
        prog="compliance_backend",
        description="sam-workshop deterministic compliance checks (G1/G2/G2.6)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ab = sub.add_parser("wordcount-abstract", help="G1: abstract word count")
    p_ab.add_argument("--abstract", required=True, help="path to abstract .md")
    p_ab.add_argument("--max", type=int, required=True, help="spec word limit")
    p_ab.set_defaults(func=cli_wordcount_abstract)

    p_bd = sub.add_parser("wordcount-body", help="G2: body word count")
    p_bd.add_argument("--manuscript", required=True, help="path to manuscript .md")
    p_bd.add_argument("--max", type=int, required=True, help="spec word limit")
    p_bd.set_defaults(func=cli_wordcount_body)

    p_ci = sub.add_parser("citation-integrity",
                          help="G2.6: ghost/orphan citation–reference check")
    p_ci.add_argument("--manuscript", required=True, help="path to manuscript .md")
    p_ci.add_argument("--refs", required=True, help="path to references.txt")
    p_ci.set_defaults(func=cli_citation_integrity)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
