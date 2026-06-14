# sam-workshop init — Windows PowerShell
# Usage:
#   irm https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-windows.ps1 | iex
#   sam-init my_paper_2026
#
# Or after clone:
#   .\workshop\install\init-workshop-windows.ps1 -PaperName my_paper_2026
#
# What this does:
#   1. Locate the skill pack (v1.4: flat install first) - warn-only if missing, never aborts
#   2. Create paper_home/ folder structure (00_intake .. 08_package + .sam/{hitl,memory,logs})
#   3. Drop a paper_profile.json template inside .sam/hitl/
#   4. pip install python-docx (best effort, only if pip available)
#   5. Run md_to_docx --preflight to verify environment
#   6. Print next-step instructions
#
# Designed for medical professors new to Claude Desktop. Does NOT install Quarto/pandoc
# — that should be done by participants BEFORE the workshop. If pandoc missing,
# preflight will say so and the workshop falls back to "docx packaging as homework."

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$PaperName = ""
)

$ErrorActionPreference = "Stop"

# When invoked via `irm | iex`, the function `sam-init` is exposed for the
# user to call with their paper name. When run as a script directly, the
# logic runs immediately with $PaperName.
function Invoke-SamWorkshopInit {
    [CmdletBinding()]
    param(
        [string]$PaperName = ""
    )

    if ([string]::IsNullOrWhiteSpace($PaperName)) {
        $PaperName = "my_paper_$(Get-Date -Format 'yyyyMMdd')"
    }

    $PapersDir = Join-Path $env:USERPROFILE "papers"
    $PaperHome = Join-Path $PapersDir $PaperName
    $PluginBase = Join-Path $env:USERPROFILE ".claude\plugins\sam-workshop"
    $LegacyUmbrella = Join-Path $env:USERPROFILE ".claude\skills\sam-workshop"
    # v1.4: flat install is the workshop standard - 18 folders (start-here + 17 task) + _shared directly under .claude\skills\
    $FlatProject = Join-Path (Get-Location).Path ".claude\skills"
    $FlatGlobal = Join-Path $env:USERPROFILE ".claude\skills"

    function Write-Ok($msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
    function Write-Warn2($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
    function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red }
    function Write-Dim($msg)  { Write-Host "       $msg" -ForegroundColor DarkGray }

    Write-Host "============================================================"
    Write-Host "  sam-workshop init (Windows)"
    Write-Host "  paper_home: $PaperHome"
    Write-Host "============================================================"

    # 1. Locate the skill pack - flat first; do NOT abort when missing (v1.4)
    $SkillBase = $null
    $PluginSkillPath = Join-Path $PluginBase "skills\sam-workshop"
    if (Test-Path (Join-Path $FlatProject "journal-fit-check\SKILL.md")) {
        $SkillBase = $FlatProject
        Write-Ok "Flat install detected (project): $SkillBase"
    } elseif (Test-Path (Join-Path $FlatGlobal "journal-fit-check\SKILL.md")) {
        $SkillBase = $FlatGlobal
        Write-Ok "Flat install detected (global): $SkillBase"
    } elseif (Test-Path $PluginSkillPath -PathType Container) {
        $SkillBase = $PluginSkillPath
        Write-Ok "Plugin install detected (CLI/IDE): $SkillBase"
    } elseif (Test-Path $LegacyUmbrella -PathType Container) {
        $SkillBase = $LegacyUmbrella
        Write-Warn2 "Umbrella copy detected: $LegacyUmbrella"
        Write-Warn2 "Desktop Code tab does NOT detect this depth (2-level). Move the 18 skill"
        Write-Warn2 "folders + _shared directly under .claude\skills\ (see INSTALL.md Fallback)."
    } else {
        Write-Warn2 "skill pack not found yet - paper_home will still be created."
        Write-Warn2 "Install (workshop standard): open a Code tab session at paper_home, then run the INSTALL.md step 4 utterance."
        Write-Dim  "  (CLI/IDE users: /plugin install sam-workshop@samahn0601)"
    }

    # 2. Create paper_home structure
    Write-Host ""
    Write-Host "Step 1/4: paper_home folder structure"
    if (-not (Test-Path $PapersDir)) {
        New-Item -ItemType Directory -Path $PapersDir -Force | Out-Null
    }
    if (Test-Path $PaperHome) {
        Write-Warn2 "$PaperHome already exists. Existing files preserved; new dirs added."
    }
    $folders = @(
        "00_intake", "01_design", "02_research", "03_outline",
        "04_draft", "05_verify", "06_critic", "07_figures", "08_package",
        ".sam\hitl", ".sam\memory", ".sam\logs"
    )
    foreach ($f in $folders) {
        $p = Join-Path $PaperHome $f
        if (-not (Test-Path $p)) {
            New-Item -ItemType Directory -Path $p -Force | Out-Null
        }
    }
    Write-Ok "9 main folders + .sam\{hitl,memory,logs} created"

    # 3. paper_profile.json template
    $Profile = Join-Path $PaperHome ".sam\hitl\paper_profile.json"
    if (-not (Test-Path $Profile)) {
        $template = @"
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
"@
        # Write as UTF-8 (no BOM) so Python reads cleanly
        [System.IO.File]::WriteAllText($Profile, $template, [System.Text.UTF8Encoding]::new($false))
        Write-Ok "paper_profile.json template created (edit before Step 1 of workshop)"
    } else {
        Write-Warn2 "paper_profile.json already exists - left untouched"
    }

    # 4. Empty events.jsonl
    $Events = Join-Path $PaperHome ".sam\hitl\events.jsonl"
    if (-not (Test-Path $Events)) {
        New-Item -ItemType File -Path $Events -Force | Out-Null
    }

    # 5. python-docx (best effort)
    Write-Host ""
    Write-Host "Step 2/4: python-docx (.docx manuscript 처리용)"
    $PyBin = $null
    foreach ($candidate in @("python", "python3", "py")) {
        $found = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($found) { $PyBin = $found.Source; break }
    }
    if (-not $PyBin) {
        Write-Fail "python not found in PATH. Install Python 3.9+ from https://python.org"
        return
    }
    $pyVer = & $PyBin --version 2>&1
    Write-Ok "Python: $pyVer"

    $hasDocx = $false
    & $PyBin -c "import docx" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $hasDocx = $true
        Write-Ok "python-docx already installed"
    } else {
        try {
            & $PyBin -m pip install --quiet python-docx 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "python-docx installed via pip"
                $hasDocx = $true
            } else {
                Write-Warn2 "python-docx install failed - .docx manuscript은 homework로 가능"
            }
        } catch {
            Write-Warn2 "python-docx install failed - .docx manuscript은 homework로 가능"
        }
    }

    # 6. Preflight
    Write-Host ""
    Write-Host "Step 3/4: md_to_docx 환경 검증 (--preflight)"
    $PreflightScript = $null
    if ($SkillBase) { $PreflightScript = Join-Path $SkillBase "_shared\scripts\md_to_docx.py" }
    if ($PreflightScript -and (Test-Path $PreflightScript)) {
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONUTF8 = "1"
        & $PyBin $PreflightScript --preflight
        $rc = $LASTEXITCODE
        switch ($rc) {
            0 { Write-Ok "All preflight checks passed" }
            2 { Write-Warn2 "Preflight passed with warnings (workshop OK to proceed)" }
            default { Write-Warn2 "Preflight reported blocking issues - facilitator will announce 'docx packaging as homework' fallback" }
        }
    } else {
        Write-Warn2 "md_to_docx.py not found (skill pack not installed yet?) - preflight skipped."
        Write-Warn2 "Re-run this script after installing skills to verify the environment."
    }

    # 7. Next steps
    Write-Host ""
    Write-Host "Step 4/4: 다음 단계"
    Write-Host "============================================================"
    Write-Ok "초기화 완료. Claude Desktop Code 탭에서:"
    Write-Host ""
    Write-Host "  1. paper_profile.json 본인 정보 편집:"
    Write-Dim $Profile
    Write-Host ""
    Write-Host "  2. Step 1 시작 - journal-fit-check 발화:"
    Write-Dim "'내 논문 어느 저널에 투고할까?'"
    Write-Host ""
    Write-Host "  3. paper_home 위치:"
    Write-Dim $PaperHome
    Write-Host ""
    Write-Host "============================================================"
}

# Expose function and (if PaperName supplied) run immediately
Set-Alias -Name sam-init -Value Invoke-SamWorkshopInit -Scope Global -ErrorAction SilentlyContinue

if ($PSBoundParameters.Count -gt 0 -or -not [string]::IsNullOrWhiteSpace($PaperName)) {
    Invoke-SamWorkshopInit -PaperName $PaperName
} else {
    Write-Host ""
    Write-Host "sam-workshop init helper loaded." -ForegroundColor Cyan
    Write-Host "Run:   sam-init my_paper_2026" -ForegroundColor Cyan
    Write-Host ""
}
