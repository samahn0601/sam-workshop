# Sam Workshop Skill Pack — INSTALL (v1.4 · Claude Desktop **Code 탭** 기준)

> **워크숍 당일 ~5분, 모든 참가자 동일 환경.**
> **주력 환경 = Claude Desktop 앱의 Code 탭** (Cowork/CLI 아님). Code 탭은 곧 Claude Code라 plugin·skill·script·로컬 파일이 모두 네이티브로 작동한다.
> 1-page 슬라이드: [PARTICIPANT_QUICKSTART.md](PARTICIPANT_QUICKSTART.md).

---

## 사전 준비 (D-7 안내문 미리 발송)

| 항목 | 필수 / 선택 | 설치 |
|---|---|---|
| 학교 지원 Claude Pro/Max 계정 | **필수** | https://claude.ai |
| **Claude Desktop 앱** | **필수** | claude.ai에서 Mac/Windows 다운로드 |
| **Git for Windows** (Windows 사용자만) | **필수** | https://git-scm.com/downloads/win — **Code 탭 첫 실행 전제**, 설치 후 앱 재시작 |
| Python 3.9+ | **필수** | https://python.org (대부분 OS에 이미 있음) |
| 본인 이메일 (PubMed E-utilities 식별용) | **필수** | — |
| Quarto (pandoc 포함) | 권장 | https://quarto.org/docs/get-started/ — ⑦ docx 패키징용 |
| ChatGPT / Gemini (무료 OK) | 권장 | ⑥ critic / ⑦ figure 선택적 멀티엔진 |

> Mac은 Git이 대개 기본 포함. Windows만 Git for Windows를 미리 깔아두면 당일 Code 탭이 바로 열린다.

---

## 워크숍 당일 — Code 탭에서 (~5분)

### ① Claude Desktop 앱 → **Code 탭** 열기

- 앱 실행 → 학교 지원 계정 로그인 → 상단 **Code** 탭 클릭
- (Windows 첫 실행 시) Git for Windows 설치 후 앱 재시작이 안내됨

### ② Plugin 설치 — GUI 또는 명령 (둘 중 하나)

**방법 A — GUI (터미널 0):**
프롬프트 박스 옆 **+ 버튼 → Plugins → Add plugin** → plugin browser에서 marketplace 추가 후 `sam-workshop` 설치.

**방법 B — 명령 (한 줄씩 붙여넣기):**
```
/plugin marketplace add samahn0601/sam-workshop
/plugin install sam-workshop@samahn0601
```

→ 17 skill + `_shared/scripts`(compliance_backend, hitl_recommend, ref_verify_pubmed, md_to_docx, stats_consistency_check, figure_render_fallback) 자동 설치. 같은 `~/.claude/`를 쓰므로 CLI와도 공유된다.

### ③ paper_home 초기화 + 환경 검증 — Code 탭 통합 터미널에서 OS별 1줄

#### 🍎 Mac / Linux
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-mac.sh) my_paper_2026
```

#### 🪟 Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-windows.ps1 | iex
sam-init my_paper_2026
```

자동으로: `~/papers/my_paper_2026/` 9개 폴더 + `.sam/{hitl,memory,logs}` 생성 · `paper_profile.json` 템플릿 · python-docx 자동 설치 · `md_to_docx --preflight` 환경 검증 · 결과 요약.

### ④ Code 탭에서 paper_home 폴더로 세션 열기 + 첫 발화

Code 탭에서 새 세션의 작업 폴더를 `~/papers/my_paper_2026/`로 지정한 뒤:
```
"내 논문 어느 저널에 투고할까?"
```
→ `journal-fit-check` skill 자동 발화. 운전 모드(`pipeline_map`) 제시 → Step 1 시작.

---

## Fallback — Plugin install이 안 되는 경우 (manual copy)

Desktop 버전이 오래되었거나 사내 정책으로 GitHub plugin이 차단된 경우:

#### Mac / Linux
```bash
git clone https://github.com/samahn0601/sam-workshop.git
cp -R sam-workshop/skills/sam-workshop ~/.claude/skills/
bash sam-workshop/install/init-workshop-mac.sh my_paper_2026
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/samahn0601/sam-workshop.git
Copy-Item -Recurse sam-workshop\skills\sam-workshop "$env:USERPROFILE\.claude\skills\"
.\sam-workshop\install\init-workshop-windows.ps1 -PaperName my_paper_2026
```

`~/.claude/skills/`에 둔 skill은 Code 탭이 그대로 인식한다(plugin 위치와 동일하게 자동 탐지).

---

## 트러블슈팅

### Windows에서 Code 탭이 안 열림 / "Git not found"
Git for Windows 미설치. https://git-scm.com/downloads/win 설치 후 **앱 완전 종료 후 재시작**. Code 탭은 세션 격리에 Git을 쓴다.

### "Skill을 못 찾음"
```bash
# Plugin 설치 위치
ls ~/.claude/plugins/sam-workshop/skills/sam-workshop/   # 17 skill 폴더
# Manual copy 위치
ls ~/.claude/skills/sam-workshop/
```
해결 안 됨 → Code 탭 새 세션. 그래도 안 되면 앱 로그아웃→재로그인. 그래도면 facilitator.

### "pandoc not found"
워크숍 그대로 진행. ⑦ docx 패키징은 homework. preflight가 자동 fallback 안내.

### "Python script 오류" / PubMed
```bash
python3 --version   # Mac/Linux 3.9+
python --version    # Windows 3.9+
```
PubMed/Crossref 호출은 인터넷 + 본인 이메일(`--email YOUR_EMAIL@example.com`). API key 없이 초당 3회 정상.

### "GPT/Gemini 무료 한도 초과"
- ⑥ critic: Claude 4번째 페르소나 "External Skeptic"로 대체
- ⑦ figure: Code matplotlib/SVG fallback

### Windows PowerShell 실행 차단
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```
또는 init을 `irm | iex` 방식으로 실행.

---

## (참고) Cowork / Chat은 안 쓰나?

워크숍 8단계는 **Code 탭에서 완결**한다(skill·script·파일·버전관리가 전부 Code 탭 네이티브).
- **Chat**: 문헌 검색(②)에서 Deep Research가 필요하면 잠깐 사용 가능 (선택).
- **Cowork**: 이번 워크숍에서는 사용하지 않는다. (Code 탭의 파일 에디터·diff·버전관리가 논문 폴더 작업에 더 적합)
- claude.ai **Chat/Cowork에서 skill을 쓰려면** `Settings > Capabilities`에서 code execution을 켜고 `Customize > Skills`에 ZIP을 업로드해야 하는데, **본 워크숍은 그 경로를 쓰지 않는다**(Code 탭 plugin이 더 강력·간단).

---

## 업그레이드 / 제거

```
/plugin update sam-workshop      # 업그레이드
/plugin uninstall sam-workshop   # 제거 (paper_home은 ~/papers/ 별도 보존)
```
manual copy 사용자: `rm -rf ~/.claude/skills/sam-workshop` 후 git pull + 재복사.

---

## 다음

1. `~/papers/my_paper_2026/.sam/hitl/paper_profile.json` 본인 정보 편집
2. (선택) `~/.claude/plugins/sam-workshop/skills/sam-workshop/README.md` 통독 (10분)
3. Code 탭에서 `"내 논문 어느 저널에 투고할까?"` 발화 → 워크숍 시작

facilitator 응답 스크립트: [FACILITATOR_SCRIPTS.md](FACILITATOR_SCRIPTS.md) (참가자 비공개).
