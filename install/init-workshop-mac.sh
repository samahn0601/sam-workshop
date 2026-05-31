#!/usr/bin/env bash
# sam-workshop init — Mac/Linux
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-mac.sh) [paper_name]
#
# Or after clone:
#   bash workshop/install/init-workshop-mac.sh my_paper_2026
#
# What this does:
#   1. Verify Claude Code plugin is installed (else print install hint and exit)
#   2. Create paper_home/ folder structure (00_intake .. 08_package + .sam/{hitl,memory,logs})
#   3. Drop a paper_profile.json template inside .sam/hitl/
#   4. pip install python-docx (best effort, only if pip available)
#   5. Run md_to_docx --preflight to verify environment
#   6. Print next-step instructions
#
# Designed for Cowork-novice medical professors. Does NOT install Quarto/pandoc
# — that should be done by participants BEFORE the workshop using the pre-mail
# instructions (Quarto installer link). If pandoc missing, preflight will say so
# and the workshop falls back to "docx packaging as homework."

set -euo pipefail

PAPER_NAME="${1:-my_paper_$(date +%Y%m%d)}"
PAPERS_DIR="${HOME}/papers"
PAPER_HOME="${PAPERS_DIR}/${PAPER_NAME}"
PLUGIN_BASE="${HOME}/.claude/plugins/sam-workshop"
SKILL_BASE_FALLBACK="${HOME}/.claude/skills/sam-workshop"

# Color helpers (fall back to plain if not a TTY)
if [[ -t 1 ]]; then
  C_OK="\033[1;32m"; C_WARN="\033[1;33m"; C_FAIL="\033[1;31m"; C_DIM="\033[0;90m"; C_RESET="\033[0m"
else
  C_OK=""; C_WARN=""; C_FAIL=""; C_DIM=""; C_RESET=""
fi
ok()   { printf "${C_OK}[OK]${C_RESET}   %s\n" "$*"; }
warn() { printf "${C_WARN}[WARN]${C_RESET} %s\n" "$*"; }
fail() { printf "${C_FAIL}[FAIL]${C_RESET} %s\n" "$*"; }
dim()  { printf "${C_DIM}%s${C_RESET}\n" "$*"; }

echo "============================================================"
echo "  sam-workshop init (Mac/Linux)"
echo "  paper_home: ${PAPER_HOME}"
echo "============================================================"

# 1. Locate the skill pack (plugin install path or manual fallback)
SKILL_BASE=""
if [[ -d "${PLUGIN_BASE}/skills/sam-workshop" ]]; then
  SKILL_BASE="${PLUGIN_BASE}/skills/sam-workshop"
  ok "Plugin install detected: ${SKILL_BASE}"
elif [[ -d "${SKILL_BASE_FALLBACK}" ]]; then
  SKILL_BASE="${SKILL_BASE_FALLBACK}"
  ok "Manual install detected: ${SKILL_BASE}"
else
  fail "sam-workshop skill pack not found in either:"
  fail "    ${PLUGIN_BASE}/skills/sam-workshop"
  fail "    ${SKILL_BASE_FALLBACK}"
  echo
  echo "Install first via Claude Code:"
  echo "    /plugin install sam-workshop@samahn0601"
  echo
  echo "Or manually clone the repo and copy:"
  echo "    cp -R workshop/skills/sam-workshop ~/.claude/skills/"
  exit 1
fi

# 2. Create paper_home structure
echo
echo "Step 1/4: paper_home folder structure"
mkdir -p "${PAPERS_DIR}"
if [[ -d "${PAPER_HOME}" ]]; then
  warn "${PAPER_HOME} already exists. Existing files preserved; new dirs added."
fi
for d in 00_intake 01_design 02_research 03_outline 04_draft 05_verify 06_critic 07_figures 08_package; do
  mkdir -p "${PAPER_HOME}/${d}"
done
mkdir -p "${PAPER_HOME}/.sam/hitl" "${PAPER_HOME}/.sam/memory" "${PAPER_HOME}/.sam/logs"
ok "9 main folders + .sam/{hitl,memory,logs} created"

# 3. Drop paper_profile.json template (idempotent — don't overwrite)
PROFILE="${PAPER_HOME}/.sam/hitl/paper_profile.json"
if [[ ! -f "${PROFILE}" ]]; then
  cat > "${PROFILE}" <<'EOF'
{
  "paper_id": "REPLACE_ME",
  "article_type": "original_article",
  "target_journal": "REPLACE_ME",
  "target_journal_tier": "Q2",
  "previous_papers_with_pipeline": 0,
  "submission_intent": "journal_submission",
  "novel_method": false,
  "target_audience_language": "ko"
}
EOF
  ok "paper_profile.json template created (edit before Step 1 of workshop)"
else
  warn "paper_profile.json already exists — left untouched"
fi

# 4. Empty events.jsonl so HITL emit doesn't fail on first call
EVENTS="${PAPER_HOME}/.sam/hitl/events.jsonl"
[[ ! -f "${EVENTS}" ]] && touch "${EVENTS}"

# 5. python-docx (best effort)
echo
echo "Step 2/4: python-docx (.docx manuscript 처리용)"
if command -v python3 >/dev/null 2>&1; then
  PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PY_BIN="python"
else
  fail "python not found in PATH. Install Python 3.9+ from https://python.org"
  exit 1
fi
ok "Python: $(${PY_BIN} --version 2>&1)"
if ${PY_BIN} -c "import docx" >/dev/null 2>&1; then
  ok "python-docx already installed"
else
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install --quiet python-docx 2>/dev/null && ok "python-docx installed via pip3" || \
      warn "python-docx install failed — .docx manuscript은 homework로 가능"
  elif command -v pip >/dev/null 2>&1; then
    pip install --quiet python-docx 2>/dev/null && ok "python-docx installed via pip" || \
      warn "python-docx install failed — .docx manuscript은 homework로 가능"
  else
    warn "pip not found. Install python-docx manually if needed: pip install python-docx"
  fi
fi

# 6. Run preflight
echo
echo "Step 3/4: md_to_docx 환경 검증 (--preflight)"
PREFLIGHT_SCRIPT="${SKILL_BASE}/_shared/scripts/md_to_docx.py"
if [[ -f "${PREFLIGHT_SCRIPT}" ]]; then
  set +e
  PYTHONIOENCODING=utf-8 ${PY_BIN} "${PREFLIGHT_SCRIPT}" --preflight
  PREFLIGHT_RC=$?
  set -e
  case ${PREFLIGHT_RC} in
    0) ok "All preflight checks passed";;
    2) warn "Preflight passed with warnings (workshop OK to proceed)";;
    *) warn "Preflight reported blocking issues — facilitator will announce 'docx packaging as homework' fallback";;
  esac
else
  fail "md_to_docx.py not found at ${PREFLIGHT_SCRIPT}"
fi

# 7. Print next-step instructions
echo
echo "Step 4/4: 다음 단계"
echo "============================================================"
ok "초기화 완료. Claude Desktop Code 탭에서:"
echo
echo "  1. paper_profile.json 본인 정보 편집:"
dim "     ${PROFILE}"
echo
echo "  2. Step 1 시작 — journal-fit-check 발화:"
dim "     '내 논문 어느 저널에 투고할까?'"
echo
echo "  3. paper_home 위치:"
dim "     ${PAPER_HOME}"
echo
echo "============================================================"
