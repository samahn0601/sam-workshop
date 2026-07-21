#!/usr/bin/env python3
"""
ref_verify_pubmed.py — sam-workshop / verify-reference-essential R1-R5 자동 검증

R1: DOI 실재 (Crossref/doi.org)
R2: 메타데이터 정합 (PubMed esummary)
R3: Ghost/Orphan citation (manuscript ↔ reference list 대조)
R4: Citation chimera 의심 (DOI metadata vs reference string)
R5: Retracted publication (PubMed publication_type)

R6 (paraphrase fabrication)는 abstract fetch만 여기서 수행, semantic check는
Claude가 별도 처리 (`r6_claim_support.jsonl`로 출력).

Usage:
    python ref_verify_pubmed.py \\
        --manuscript paper_home/04_draft/manuscript.md \\
        --references paper_home/04_draft/references.txt \\
        --email your_email@example.com \\
        --out paper_home/05_verify/ \\
        --r6-sample 8

Dependencies: httpx (or requests), python-docx (manuscript가 .docx인 경우만)

NCBI E-utilities 권장사항: tool, email 포함. API key 없으면 초당 3회 이하.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CROSSREF_API = "https://api.crossref.org/works"
TOOL_NAME = "sam-workshop"
RATE_LIMIT_SLEEP = 0.4  # without API key, ~3 req/s


# ============================================================
# Data classes
# ============================================================

@dataclass
class Reference:
    ref_id: str
    raw_text: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None


@dataclass
class CheckResult:
    ref_id: str
    raw: str
    doi: Optional[str]
    pmid: Optional[str]
    R1_doi_resolves: Optional[bool] = None
    R2_title_match: Optional[bool] = None
    R2_year_match: Optional[bool] = None
    R2_authors_match: Optional[bool] = None
    R2_journal_match: Optional[bool] = None
    R3_orphan: Optional[bool] = None
    R3_ghost: Optional[bool] = None
    R4_chimera_risk: str = "none"  # none|low|medium|high
    R5_retracted: Optional[bool] = None
    # v1.4.1 R5b: Crossref retraction 교차 — True=철회/공지 감지, False=없음 확인,
    # None=확인 불가(네트워크 — unchecked, PASS 집계 금지)
    R5b_crossref: Optional[bool] = None
    pubmed_title: Optional[str] = None
    pubmed_authors: List[str] = field(default_factory=list)
    pubmed_year: Optional[int] = None
    pubmed_journal: Optional[str] = None
    pubmed_pubtypes: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    severity: str = "info"


# ============================================================
# Helpers
# ============================================================

def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
    headers = headers or {"User-Agent": f"{TOOL_NAME}/1.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fuzzy_eq(a: Optional[str], b: Optional[str], threshold: float = 0.85) -> bool:
    if not a or not b:
        return False
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    # token Jaccard
    sa, sb = set(na.split()), set(nb.split())
    if not sa or not sb:
        return False
    j = len(sa & sb) / len(sa | sb)
    return j >= threshold


# ============================================================
# Parsing manuscript and references
# ============================================================

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
PMID_RE = re.compile(r"\b(?:PMID[:\s]+|pubmed/)(\d{6,9})\b", re.IGNORECASE)


def read_manuscript_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("python-docx required for .docx manuscript. pip install python-docx")
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return path.read_text(encoding="utf-8")


def parse_references(path: Path) -> List[Reference]:
    """Parse reference list. Each entry separated by blank line or numbered prefix."""
    text = path.read_text(encoding="utf-8")
    # Try numbered (1. ... \n2. ...)
    entries = re.split(r"\n\s*(?=\d+[\.\)]\s)", text)
    entries = [e.strip() for e in entries if e.strip()]

    refs: List[Reference] = []
    for i, e in enumerate(entries, 1):
        m = re.match(r"^(\d+)[\.\)]\s*(.*)$", e, re.DOTALL)
        if m:
            ref_id = m.group(1)
            body = m.group(2).strip()
        else:
            ref_id = str(i)
            body = e
        refs.append(_make_reference(ref_id, body))
    return refs


def _make_reference(ref_id: str, raw: str) -> Reference:
    doi = None
    m = DOI_RE.search(raw)
    if m:
        doi = m.group(0).rstrip(".,;)")
    pmid = None
    m = PMID_RE.search(raw)
    if m:
        pmid = m.group(1)
    year = None
    m = YEAR_RE.search(raw)
    if m:
        year = int(m.group(0))
    return Reference(ref_id=ref_id, raw_text=raw, doi=doi, pmid=pmid, year=year)


# ============================================================
# R1: DOI resolves (Crossref)
# ============================================================

def r1_doi_resolve(doi: str) -> Tuple[bool, Dict[str, Any]]:
    if not doi:
        return False, {}
    url = f"{CROSSREF_API}/{urllib.parse.quote(doi, safe='/')}"
    try:
        body = http_get(url, timeout=15)
        data = json.loads(body)
        if data.get("status") == "ok":
            return True, data.get("message", {})
    except Exception:
        return False, {}
    return False, {}


# ============================================================
# R2: PubMed metadata via esummary (and abstract via efetch for R6 prep)
# ============================================================

def pubmed_search(term: str, email: str, retmax: int = 3) -> Optional[List[str]]:
    """esearch. [] = searched, no match. None = search itself failed
    (network/API) — callers must record [EXCEPTION], never treat as no-match."""
    url = (
        f"{NCBI_EUTILS}/esearch.fcgi?db=pubmed&retmode=json"
        f"&retmax={retmax}&tool={TOOL_NAME}&email={urllib.parse.quote(email)}"
        f"&term={urllib.parse.quote(term)}"
    )
    try:
        body = http_get(url, timeout=15)
        data = json.loads(body)
        return data.get("esearchresult", {}).get("idlist", []) or []
    except Exception:
        return None


def extract_title_segment(raw_text: str) -> Optional[str]:
    """Vancouver 'Authors. Title. Journal. …' → best-effort title segment.
    The first sentence-ender-delimited segment is authors; the second is
    usually the title — a far better [Title] query than the raw head (which
    mixes author names in and matches nothing). Splits on . ? ! so titles
    ending in a question mark don't swallow the journal name."""
    segs = [s.strip() for s in re.split(r"(?<=[.?!])\s+", raw_text) if s.strip()]
    if len(segs) >= 2 and len(segs[1].split()) >= 3:
        return segs[1].rstrip(".?!")
    return None


def pubmed_efetch_xml(pmids: List[str], email: str) -> Optional[ET.Element]:
    if not pmids:
        return None
    url = (
        f"{NCBI_EUTILS}/efetch.fcgi?db=pubmed&retmode=xml"
        f"&id={','.join(pmids)}&tool={TOOL_NAME}&email={urllib.parse.quote(email)}"
    )
    try:
        body = http_get(url, timeout=30)
        return ET.fromstring(body)
    except Exception:
        return None


def parse_pubmed_article(art: ET.Element) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "pmid": None,
        "title": None,
        "authors": [],
        "year": None,
        "journal": None,
        "publication_types": [],
        "abstract": None,
    }
    pmid_el = art.find(".//PMID")
    if pmid_el is not None:
        out["pmid"] = pmid_el.text
    title_el = art.find(".//ArticleTitle")
    if title_el is not None:
        out["title"] = "".join(title_el.itertext()).strip()
    journal_el = art.find(".//Journal/Title")
    if journal_el is not None:
        out["journal"] = journal_el.text
    year_el = art.find(".//JournalIssue/PubDate/Year")
    if year_el is not None and year_el.text:
        try:
            out["year"] = int(year_el.text)
        except ValueError:
            pass
    if out["year"] is None:
        # fallback: MedlineDate
        md = art.find(".//JournalIssue/PubDate/MedlineDate")
        if md is not None and md.text:
            m = YEAR_RE.search(md.text)
            if m:
                out["year"] = int(m.group(0))
    for au in art.findall(".//Author"):
        ln = au.find("LastName")
        if ln is not None and ln.text:
            out["authors"].append(ln.text)
    for pt in art.findall(".//PublicationType"):
        if pt.text:
            out["publication_types"].append(pt.text)
    abstract_parts = []
    for ab in art.findall(".//Abstract/AbstractText"):
        label = ab.attrib.get("Label", "")
        text = "".join(ab.itertext()).strip()
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)
    if abstract_parts:
        out["abstract"] = "\n".join(abstract_parts)
    return out


# ============================================================
# R3: Ghost / Orphan
# ============================================================

# Range separator accepts ASCII hyphen plus en-dash (–, U+2013) / em-dash
# (—, U+2014), common when [1–3] is pasted from Word/PDF. Dashes are normalized
# to ASCII hyphen before range expansion below (keeps ASCII behavior identical).
INTEXT_CITE_RE = re.compile(r"\[(\d+(?:\s*[-–—,]\s*\d+)*)\]")
_RANGE_DASHES = ("–", "—")  # en-dash, em-dash


def find_intext_refs(manuscript: str) -> set:
    cited: set = set()
    for m in INTEXT_CITE_RE.finditer(manuscript):
        chunk = m.group(1)
        for d in _RANGE_DASHES:
            chunk = chunk.replace(d, "-")
        for part in re.split(r"\s*,\s*", chunk):
            if "-" in part:
                a, b = part.split("-", 1)
                try:
                    for n in range(int(a), int(b) + 1):
                        cited.add(str(n))
                except ValueError:
                    pass
            else:
                cited.add(part.strip())
    return cited


def check_ghost_orphan(manuscript: str, refs: List[Reference]) -> Dict[str, Tuple[bool, bool]]:
    """Returns dict ref_id -> (orphan, ghost). orphan=in list but not cited. ghost=cited but not in list."""
    cited_in_text = find_intext_refs(manuscript)
    listed = {r.ref_id for r in refs}
    orphans = listed - cited_in_text
    ghosts = cited_in_text - listed
    out: Dict[str, Tuple[bool, bool]] = {}
    for r in refs:
        out[r.ref_id] = (r.ref_id in orphans, False)
    for g in ghosts:
        out[g] = (False, True)
    return out


# ============================================================
# R4: Citation chimera risk
# ============================================================

def assess_chimera_risk(ref: Reference, pubmed_meta: Optional[Dict[str, Any]],
                       crossref_meta: Optional[Dict[str, Any]]) -> str:
    """High if multiple metadata fields disagree between manuscript-stated and resolved DOI."""
    if not ref.doi and not ref.pmid:
        return "none"
    src = pubmed_meta or {}
    if not src and crossref_meta:
        src = {
            "title": (crossref_meta.get("title") or [None])[0],
            "year": (crossref_meta.get("issued") or {}).get("date-parts", [[None]])[0][0],
            "journal": (crossref_meta.get("container-title") or [None])[0] if crossref_meta.get("container-title") else None,
        }
    if not src:
        return "none"
    mismatches = 0
    if ref.year and src.get("year") and ref.year != src["year"]:
        mismatches += 1
    if src.get("title"):
        # raw_text usually contains title fragment; do fuzzy
        if not fuzzy_eq(src["title"], ref.raw_text, threshold=0.3):
            mismatches += 1
    if mismatches >= 2:
        return "high"
    if mismatches == 1:
        return "low"
    return "none"


# ============================================================
# R5: Retraction
# ============================================================

RETRACT_KEYWORDS = ("retracted", "retraction")


def is_retracted(pubmed_meta: Dict[str, Any]) -> bool:
    pts = [p.lower() for p in pubmed_meta.get("publication_types", [])]
    if any("retract" in p for p in pts):
        return True
    title = (pubmed_meta.get("title") or "").lower()
    return any(kw in title for kw in RETRACT_KEYWORDS)


# ── v1.4.1 R5b: Crossref retraction 교차 (비-MEDLINE 갭 보조) ──
# PubMed R5는 MEDLINE 색인 저널만 본다. CrossRef update 체계
# (filter=updates:DOI → 이 DOI를 철회/갱신한 공지 검색)로 교차 확인.
# fail-closed: 네트워크 실패는 None 반환 — 호출자는 [R5B_UNCHECKED]로
# 표기하고 PASS로 집계 금지. Retraction Watch 전수 대조는 deep-audit 영역.

CROSSREF_RETRACTION_TYPES = (
    "retraction", "withdrawal", "removal",
    "partial_retraction", "expression_of_concern",
)


def crossref_retraction_check(doi: str,
                              crossref_meta: Optional[Dict[str, Any]] = None,
                              ) -> Optional[Dict[str, Any]]:
    """Returns {"flag": bool, "types": [...], "notices": [doi,...]} 또는
    None(확인 불가 — unchecked로 처리할 것)."""
    if not doi:
        return None
    types: List[str] = []
    notices: List[str] = []

    # 1차 (네트워크 0): R1에서 받은 메타 재사용 — 철회 시 제목에 prefix가 흔함
    if crossref_meta:
        title = ((crossref_meta.get("title") or [""])[0] or "").lower()
        if title.startswith("retracted") or "retracted article" in title:
            types.append("title_prefix")

    # 2차: updates:DOI 필터 — 이 DOI를 대상으로 한 철회/갱신 공지 검색
    url = f"{CROSSREF_API}?filter=updates:{urllib.parse.quote(doi, safe='')}&rows=5"
    try:
        data = json.loads(http_get(url, timeout=15))
        for it in data.get("message", {}).get("items", []) or []:
            for u in it.get("update-to", []) or []:
                if (u.get("DOI") or "").lower() != doi.lower():
                    continue
                t = (u.get("type") or "").lower()
                if t:
                    types.append(t)
                if it.get("DOI"):
                    notices.append(it["DOI"])
    except Exception:
        if types:  # 제목 prefix만으로도 경고는 성립
            return {"flag": True, "types": types, "notices": notices}
        return None

    flag = any(
        t == "title_prefix" or t in CROSSREF_RETRACTION_TYPES or "retract" in t
        for t in types
    )
    return {"flag": flag, "types": types, "notices": notices}


# ============================================================
# Main per-reference verification
# ============================================================

def verify_reference(ref: Reference, email: str,
                     ghost_orphan: Dict[str, Tuple[bool, bool]]) -> CheckResult:
    res = CheckResult(ref_id=ref.ref_id, raw=ref.raw_text, doi=ref.doi, pmid=ref.pmid)
    issues: List[str] = []

    # R1: DOI
    crossref_meta: Optional[Dict[str, Any]] = None
    if ref.doi:
        ok, meta = r1_doi_resolve(ref.doi)
        res.R1_doi_resolves = ok
        if ok:
            crossref_meta = meta
        else:
            issues.append(f"[DOI_NOT_RESOLVED] {ref.doi}")

    # R2 + R5 via PubMed
    pubmed_meta: Optional[Dict[str, Any]] = None
    pmid_used = ref.pmid
    if not pmid_used and ref.doi:
        # Try DOI -> PMID
        ids = pubmed_search(f"{ref.doi}[AID]", email, retmax=1)
        time.sleep(RATE_LIMIT_SLEEP)
        if ids is None:
            issues.append("[EXCEPTION] pubmed esearch failed (DOI->PMID lookup)")
        elif ids:
            pmid_used = ids[0]
    if not pmid_used and ref.year:
        # fallback queries, best first: title segment (Vancouver 2nd segment),
        # then legacy raw-head 12 words (kept for non-Vancouver formats)
        queries = []
        title_seg = extract_title_segment(ref.raw_text)
        if title_seg:
            # unquoted + punctuation-stripped: PubMed's quoted phrase search
            # misses titles absent from its phrase index (live-verified), while
            # unquoted [Title] term mapping finds them.
            clean = " ".join(re.sub(r"[^\w\s-]", " ", title_seg).split())
            if clean:
                queries.append(f'{clean}[Title] AND {ref.year}[PDAT]')
        first_words = " ".join(ref.raw_text.split()[:12])
        queries.append(f'"{first_words}"[Title] AND {ref.year}[PDAT]')
        for q in queries:
            ids = pubmed_search(q, email, retmax=1)
            time.sleep(RATE_LIMIT_SLEEP)
            if ids is None:
                issues.append("[EXCEPTION] pubmed esearch failed (title fallback)")
                break
            if ids:
                pmid_used = ids[0]
                break

    # Fail-closed: a reference with no DOI, no PMID, and no PubMed match has
    # had ZERO external verification — it must never count as a clean pass.
    # (Ghost/AI-fabricated refs typically arrive exactly in this shape.)
    if (not ref.doi and not pmid_used
            and not any(i.startswith("[EXCEPTION]") for i in issues)):
        issues.append(
            "[UNVERIFIED_NO_MATCH] no DOI/PMID and no PubMed match — "
            "existence unverified (human check required; 단행본·지침·비-PubMed "
            "출처면 원문으로 직접 확인)")

    if pmid_used:
        res.pmid = pmid_used
        root = pubmed_efetch_xml([pmid_used], email)
        time.sleep(RATE_LIMIT_SLEEP)
        if root is not None:
            arts = root.findall(".//PubmedArticle")
            if arts:
                pubmed_meta = parse_pubmed_article(arts[0])
                res.pubmed_title = pubmed_meta.get("title")
                res.pubmed_authors = pubmed_meta.get("authors", [])
                res.pubmed_year = pubmed_meta.get("year")
                res.pubmed_journal = pubmed_meta.get("journal")
                res.pubmed_pubtypes = pubmed_meta.get("publication_types", [])

                # R2 checks
                if pubmed_meta.get("title"):
                    res.R2_title_match = fuzzy_eq(pubmed_meta["title"], ref.raw_text, threshold=0.3)
                if pubmed_meta.get("year") and ref.year:
                    res.R2_year_match = (pubmed_meta["year"] == ref.year)
                if pubmed_meta.get("authors"):
                    # simple: any of pubmed authors appears in raw_text
                    raw_norm = normalize_text(ref.raw_text)
                    res.R2_authors_match = any(
                        a.lower() in raw_norm for a in pubmed_meta["authors"][:3]
                    )
                if pubmed_meta.get("journal"):
                    res.R2_journal_match = fuzzy_eq(pubmed_meta["journal"], ref.raw_text, threshold=0.2)

                # R5: retraction
                res.R5_retracted = is_retracted(pubmed_meta)
                if res.R5_retracted:
                    issues.append("[RETRACTED] cited paper has been retracted")

    # R5b (v1.4.1): Crossref retraction 교차 — PMID 유무와 무관 (비-MEDLINE 갭이 표적)
    if ref.doi:
        cr = crossref_retraction_check(ref.doi, crossref_meta)
        if cr is None:
            res.R5b_crossref = None
            issues.append("[R5B_UNCHECKED] Crossref retraction 확인 불가(네트워크) — PASS 집계 금지")
        elif cr["flag"]:
            res.R5b_crossref = True
            notice = f" notice={','.join(cr['notices'])}" if cr["notices"] else ""
            issues.append(f"[RETRACTED_CROSSREF] type={','.join(cr['types'])}{notice}")
        else:
            res.R5b_crossref = False

    # R3: ghost/orphan
    orphan, ghost = ghost_orphan.get(ref.ref_id, (False, False))
    res.R3_orphan = orphan
    res.R3_ghost = ghost
    if orphan:
        issues.append("[ORPHAN] in reference list but not cited in manuscript")
    if ghost:
        issues.append("[GHOST] cited in manuscript but not in reference list")

    # R4: chimera
    res.R4_chimera_risk = assess_chimera_risk(ref, pubmed_meta, crossref_meta)
    if res.R4_chimera_risk == "high":
        issues.append("[CHIMERA_HIGH] DOI resolves but metadata disagrees with reference text")
    elif res.R4_chimera_risk == "low":
        issues.append("[CHIMERA_LOW] possible metadata mismatch")

    if res.R2_title_match is False:
        issues.append("[META_TITLE_MISMATCH]")
    if res.R2_year_match is False:
        issues.append("[META_YEAR_MISMATCH]")
    if res.R2_journal_match is False:
        issues.append("[META_JOURNAL_MISMATCH]")

    res.issues = issues
    # Severity mapping. Two independent signals feed the certificate:
    #   - severity=="high"  → certificate FAIL (real manuscript / retraction finding)
    #   - INCOMPLETE_CHECK_MARKERS ([R5B_UNCHECKED]/[EXCEPTION]) → certificate
    #     INCOMPLETE_EXTERNAL_CHECK (fail-closed; see count_incomplete_checks +
    #     write_certificate). An unresolved external check is NOT a clean run: it
    #     is kept at >= medium here so it stays visible in refcheck_issues.md and
    #     can never be silently downgraded to a PASSing certificate.
    if any(s.startswith(("[RETRACTED]", "[RETRACTED_CROSSREF]", "[CHIMERA_HIGH]", "[GHOST]", "[DOI_NOT_RESOLVED]")) for s in issues):
        res.severity = "high"
    elif issues:
        # includes [R5B_UNCHECKED]/[EXCEPTION] — never "info" while unresolved
        res.severity = "medium"
    else:
        res.severity = "info"
    return res


# Markers meaning an external check could NOT be completed (network/API outage,
# rate-limit, per-reference exception) — as opposed to a manuscript defect.
# Fail-closed: their presence forbids a PASS certificate; Status becomes
# INCOMPLETE_EXTERNAL_CHECK (SKILL.md Degraded Mode). Distinct from FAIL, which
# is reserved for real high-severity findings.
# [UNVERIFIED_NO_MATCH] (2026-07-21): a no-DOI/no-PMID reference with zero
# PubMed hits received no external verification at all — treating it as clean
# was the fail-open path AI-fabricated references walked through.
INCOMPLETE_CHECK_MARKERS = ("[R5B_UNCHECKED]", "[EXCEPTION]", "[UNVERIFIED_NO_MATCH]")


def count_incomplete_checks(results: List[CheckResult]) -> int:
    """Number of references whose external verification is unresolved."""
    return sum(
        1 for r in results
        if any(iss.startswith(INCOMPLETE_CHECK_MARKERS) for iss in r.issues)
    )


# ============================================================
# R6 prep — pick high-risk citations and output JSONL with abstracts
# ============================================================

CLAIM_PATTERNS = [
    re.compile(r"\b\d+(?:\.\d+)?\s*%"),                    # numeric %
    re.compile(r"\b(OR|HR|RR|aOR|aHR|95%\s*CI)\b", re.I),  # effect size
    re.compile(r"\b(causes?|prevents?|leads?\s+to|results?\s+in)\b", re.I),
    re.compile(r"\b(first|only|definitive|gold\s+standard|novel)\b", re.I),
    re.compile(r"\b(guidelines?|consensus|recommend)\b", re.I),
    re.compile(r"\b(reduces?|increases?|improves?)\s+\w+\s+by\s+\d+", re.I),
]


def find_high_risk_claims(manuscript: str, refs_by_id: Dict[str, Reference],
                          n_sample: int) -> List[Dict[str, Any]]:
    """Find sentences containing in-text citations that match high-risk patterns."""
    sentences = re.split(r"(?<=[.!?])\s+", manuscript)
    candidates: List[Tuple[int, str, List[str]]] = []  # (risk_score, sentence, ref_ids)
    for sent in sentences:
        m_iter = list(INTEXT_CITE_RE.finditer(sent))
        if not m_iter:
            continue
        ref_ids = []
        for m in m_iter:
            for part in re.split(r"\s*,\s*", m.group(1)):
                ref_ids.append(part.split("-")[0].strip())
        score = 0
        for pat in CLAIM_PATTERNS:
            if pat.search(sent):
                score += 1
        if score > 0:
            candidates.append((score, sent.strip(), ref_ids))
    candidates.sort(key=lambda x: -x[0])
    out = []
    for score, sent, ref_ids in candidates[:n_sample]:
        out.append({
            "claim_sentence": sent,
            "ref_ids": ref_ids,
            "risk_score": score,
        })
    return out


def emit_r6_jsonl(claims: List[Dict[str, Any]], results: Dict[str, CheckResult],
                  email: str, out_path: Path) -> None:
    # Fetch abstracts for unique pmids
    needed = []
    for c in claims:
        for rid in c["ref_ids"]:
            res = results.get(rid)
            if res and res.pmid and res.pmid not in needed:
                needed.append(res.pmid)
    abstracts: Dict[str, Dict[str, Any]] = {}
    # batch in groups of 50
    for i in range(0, len(needed), 50):
        batch = needed[i:i + 50]
        root = pubmed_efetch_xml(batch, email)
        time.sleep(RATE_LIMIT_SLEEP)
        if root is not None:
            for art in root.findall(".//PubmedArticle"):
                meta = parse_pubmed_article(art)
                if meta.get("pmid"):
                    abstracts[meta["pmid"]] = meta

    with out_path.open("w", encoding="utf-8") as f:
        for idx, c in enumerate(claims, 1):
            for rid in c["ref_ids"]:
                res = results.get(rid)
                if not res:
                    continue
                meta = abstracts.get(res.pmid) if res.pmid else None
                payload = {
                    "claim_id": f"CIT-{idx:03d}",
                    "ref_id": rid,
                    "claim_sentence": c["claim_sentence"],
                    "risk_score": c["risk_score"],
                    "pmid": res.pmid,
                    "title": (meta or {}).get("title"),
                    "abstract": (meta or {}).get("abstract"),
                    "verdict": "PENDING_CLAUDE_SEMANTIC_CHECK",
                }
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")


# ============================================================
# Output writers
# ============================================================

def write_csv(results: List[CheckResult], path: Path) -> None:
    cols = [
        "ref_id", "doi", "pmid", "R1_doi_resolves",
        "R2_title_match", "R2_year_match", "R2_authors_match", "R2_journal_match",
        "R3_orphan", "R3_ghost", "R4_chimera_risk", "R5_retracted",
        "R5b_crossref", "severity", "issues",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in results:
            w.writerow([
                r.ref_id, r.doi or "", r.pmid or "",
                r.R1_doi_resolves, r.R2_title_match, r.R2_year_match,
                r.R2_authors_match, r.R2_journal_match,
                r.R3_orphan, r.R3_ghost, r.R4_chimera_risk, r.R5_retracted,
                r.R5b_crossref, r.severity, "; ".join(r.issues),
            ])


def write_issues_md(results: List[CheckResult], path: Path) -> None:
    high = [r for r in results if r.severity == "high"]
    med = [r for r in results if r.severity == "medium"]
    lines = ["# Reference Check Issues\n"]
    lines.append(f"- Total references: {len(results)}")
    lines.append(f"- High severity: {len(high)}")
    lines.append(f"- Medium severity: {len(med)}")
    lines.append("")
    if high:
        lines.append("## HIGH severity (desk-reject risk)\n")
        for r in high:
            lines.append(f"### Ref {r.ref_id}")
            lines.append(f"- DOI: {r.doi or '(none)'}")
            lines.append(f"- PMID: {r.pmid or '(none)'}")
            for i in r.issues:
                lines.append(f"- {i}")
            lines.append("")
    if med:
        lines.append("## MEDIUM severity\n")
        for r in med:
            lines.append(f"- Ref {r.ref_id}: {'; '.join(r.issues)}")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_certificate(results: List[CheckResult], n_high: int, n_med: int,
                      r6_count: int, path: Path, n_incomplete: int = 0) -> None:
    # Status precedence (fail-closed, SKILL.md Degraded Mode):
    #   1) real high-severity findings         → FAIL
    #   2) any unresolved external check        → INCOMPLETE_EXTERNAL_CHECK
    #      (network/API outage is NOT a manuscript error, so it is neither PASS
    #       nor FAIL — it is recorded distinctly; PASS is forbidden)
    #   3) fully checked & clean                → PASS
    # A run with [R5B_UNCHECKED]/partial outage can therefore never report PASS.
    if n_high > 0:
        pass_status = "FAIL"
    elif n_incomplete > 0:
        pass_status = "INCOMPLETE_EXTERNAL_CHECK"
    else:
        pass_status = "PASS"
    lines = [
        "# Verification Certificate (R1-R5 + R6 prep)",
        "",
        f"- Status (R1-R5): **{pass_status}**",
        f"- Total references checked: {len(results)}",
        f"- High severity issues: {n_high}",
        f"- Medium severity issues: {n_med}",
        f"- Incomplete external checks: {n_incomplete} "
        f"(network/API 미완 — PASS 집계 금지)",
        f"- R6 paraphrase claims sampled: {r6_count} (Claude semantic check pending)",
        "",
        "## Required next step",
        "1. R1-R5 high severity 항목을 본인 결정 (수정/교체/제거)",
        "2. R6 `r6_claim_support.jsonl`을 Claude로 semantic check (지원/부분지원/미지원/모순/판단불가)",
        "3. Self-Gate B (verify) 통과 결정",
    ]
    if n_incomplete > 0:
        lines.append(
            "4. ⚠️ 외부 검증 미완(INCOMPLETE_EXTERNAL_CHECK): 네트워크 회복 후 동일 "
            "명령 재실행 후 재판정 — 미완 상태로는 Self-Gate B 통과 금지 "
            "(SKILL.md Degraded Mode)."
        )
    lines += [
        "",
        "→ Mortality/safety/guideline claim은 abstract만으로 통과 금지. full text 확인 필수.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ============================================================
# Main
# ============================================================

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", required=True, type=Path)
    ap.add_argument("--references", required=True, type=Path)
    ap.add_argument("--email", required=True)
    ap.add_argument("--out", required=True, type=Path, help="output directory")
    ap.add_argument("--r6-sample", type=int, default=8,
                    help="number of high-risk claims to sample for R6 (default 8)")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manuscript = read_manuscript_text(args.manuscript)
    refs = parse_references(args.references)
    refs_by_id = {r.ref_id: r for r in refs}
    print(f"[parse] manuscript={len(manuscript)} chars, refs={len(refs)}")

    ghost_orphan = check_ghost_orphan(manuscript, refs)

    results: List[CheckResult] = []
    for i, ref in enumerate(refs, 1):
        print(f"[verify] {i}/{len(refs)} ref_id={ref.ref_id} doi={ref.doi or '-'}")
        try:
            res = verify_reference(ref, args.email, ghost_orphan)
        except Exception as e:
            print(f"  ! exception: {e}")
            res = CheckResult(ref_id=ref.ref_id, raw=ref.raw_text,
                              doi=ref.doi, pmid=ref.pmid,
                              issues=[f"[EXCEPTION] {e}"], severity="medium")
        results.append(res)

    # add ghost-only entries (in-text but missing from list)
    for rid, (orphan, ghost) in ghost_orphan.items():
        if ghost and rid not in refs_by_id:
            results.append(CheckResult(
                ref_id=rid, raw="(missing from reference list)",
                doi=None, pmid=None, R3_ghost=True,
                issues=["[GHOST] cited in manuscript but not in reference list"],
                severity="high",
            ))

    n_high = sum(1 for r in results if r.severity == "high")
    n_med = sum(1 for r in results if r.severity == "medium")
    n_incomplete = count_incomplete_checks(results)

    # R6 prep
    r6_claims = find_high_risk_claims(manuscript, refs_by_id, args.r6_sample)
    r6_results_map = {r.ref_id: r for r in results}
    emit_r6_jsonl(r6_claims, r6_results_map, args.email, args.out / "r6_claim_support.jsonl")
    print(f"[r6] sampled {len(r6_claims)} high-risk claims for paraphrase check")

    # Outputs
    write_csv(results, args.out / "refcheck_refs.csv")
    write_issues_md(results, args.out / "refcheck_issues.md")
    write_certificate(results, n_high, n_med, len(r6_claims),
                      args.out / "verification_certificate.md",
                      n_incomplete=n_incomplete)

    # HITL emit
    hitl_dir = args.out.parent / ".sam" / "hitl"
    hitl_dir.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paper_id": args.out.parent.name,
        "step": 5,
        "gate": "C_verify_critic",
        # fail-closed: an incomplete external check is not a gate_pass
        "event_type": "gate_pass" if (n_high == 0 and n_incomplete == 0) else "gate_fail",
        "skill": "verify-reference-essential",
        "engine": "code-script+pubmed",
        "category": "reference_integrity",
        "severity": 5 if n_high > 0 else (3 if n_incomplete > 0 else 1),
        "description": (
            f"R1-R5: {n_high} high, {n_med} medium, {n_incomplete} incomplete. "
            f"R6 prepped {len(r6_claims)} samples."
        ),
    }
    with (hitl_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"\n[done] high={n_high} medium={n_med} incomplete={n_incomplete} "
          f"r6_samples={len(r6_claims)}")
    print(f"  -> {args.out}/refcheck_refs.csv")
    print(f"  -> {args.out}/refcheck_issues.md")
    print(f"  -> {args.out}/r6_claim_support.jsonl  (Claude semantic check 대기)")
    print(f"  -> {args.out}/verification_certificate.md")


if __name__ == "__main__":
    main()
