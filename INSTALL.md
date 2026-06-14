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

## 워크숍 당일 — Code 탭에서 5단계 (~5분)

> 설치 방식 = **자연어 평평(flat) 복사** (2026-06-10 Desktop Code 탭 실측 검증). Code 탭의 skill 탐지는 `.claude/skills/<skill>/SKILL.md` **1단계만** 인식하므로, 우산 폴더째 복사(2단계)는 전부 미탐지된다 — 아래 발화문이 그 함정을 피하는 검증된 경로다.

### ① Claude Desktop 앱 → **Code 탭** 열기

- 앱 실행 → 학교 지원 계정 로그인 → 상단 **Code** 탭 클릭
- (Windows 첫 실행 시) Git for Windows 설치 후 앱 재시작이 안내됨

### ② paper_home 초기화 — Code 탭 통합 터미널에서 OS별 1줄

#### 🍎 Mac / Linux
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-mac.sh) my_paper_2026
```

#### 🪟 Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-windows.ps1 | iex
sam-init my_paper_2026
```

자동으로: `~/papers/my_paper_2026/` 9개 폴더 + `.sam/{hitl,memory,logs}` 생성 · `paper_profile.json` 템플릿 · python-docx 자동 설치 · `md_to_docx --preflight` 환경 검증. (skill이 아직 미설치면 WARN만 표시 — ④에서 설치하면 됨)

### ③ Code 탭 **새 세션** → 작업 폴더를 paper_home으로

새 세션 시작 시 작업 폴더 = `~/papers/my_paper_2026` 선택.

### ④ Skill Pack 설치 — 자연어 한 줄 붙여넣기 ★ 표준 경로

입력창에 그대로 붙여넣는다:

```
https://github.com/samahn0601/sam-workshop 를 clone해서, 그 안의 skills/sam-workshop/ 폴더에 있는
18개 skill 폴더(진입점 start-here + 작업 skill 17)와 _shared 폴더를 지금 작업 폴더의 .claude/skills/ 바로 아래로 복사해줘.
(우산 폴더 sam-workshop을 만들지 말 것 — .claude/skills/journal-fit-check/SKILL.md 처럼 1단계가 되도록.)
git이 없으면 ZIP https://github.com/samahn0601/sam-workshop/archive/refs/heads/main.zip 을 받아 풀어서 똑같이 해줘.
끝나면 .claude/skills/ 바로 아래 폴더 목록을 보여줘.
```

→ Claude가 clone(또는 ZIP)→평평 복사→목록 확인까지 직접 수행. 18 폴더(start-here + 작업 skill 17) + `_shared`가 보이면 성공.

### ⑤ **새 세션 1회** → 탐지 확인 → 첫 발화

`.claude/skills/`가 새로 생긴 직후라 **새 세션을 한 번 더** 연다 (skill은 세션 시작 시점에 스캔). 입력창에 `/`를 쳐서 `start-here`·`journal-fit-check` 등이 목록에 보이면 탐지 성공. 이어서:
```
"시작하자"   (또는 "내 논문 어느 저널에 투고할까?")
```
→ `start-here`가 10-step 맵·운전 모드 제시 → `gate_plan` 작성 → Step 1(`journal-fit-check`)부터 자동 안내.

---

## Fallback — 직접 복사 (④ 발화 대신 터미널로)

⚠️ **핵심: 우산 폴더 금지.** `skills/sam-workshop` 폴더째 복사하면 2단계 깊이가 되어 **전부 미탐지**된다(실측 확인된 함정). 반드시 **내용물**을 `.claude/skills/` 바로 아래로.

#### Mac / Linux
```bash
git clone https://github.com/samahn0601/sam-workshop.git
mkdir -p ~/papers/my_paper_2026/.claude/skills
cp -R sam-workshop/skills/sam-workshop/. ~/papers/my_paper_2026/.claude/skills/
ls ~/papers/my_paper_2026/.claude/skills/   # → 18 폴더(start-here + 작업 17) + _shared 가 바로 보여야 함
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/samahn0601/sam-workshop.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\papers\my_paper_2026\.claude\skills" | Out-Null
Copy-Item -Recurse -Force sam-workshop\skills\sam-workshop\* "$env:USERPROFILE\papers\my_paper_2026\.claude\skills\"
dir "$env:USERPROFILE\papers\my_paper_2026\.claude\skills"   # → 18 폴더(start-here + 작업 17) + _shared
```

복사 후 Code 탭에서 해당 paper_home으로 **새 세션** → `/` 목록 확인.

### (참고) CLI · VS Code/JetBrains 사용자 — `/plugin` 경로

터미널 Claude Code(CLI)·IDE 사용자는 plugin으로 설치할 수 있다:
```
/plugin marketplace add samahn0601/sam-workshop
/plugin install sam-workshop@samahn0601
```
⚠️ **Desktop 앱 Code 탭에는 `/plugin` 명령이 없고**, Plugins GUI는 공식 마켓플레이스 읽기 전용이라 커스텀 마켓플레이스를 추가할 수 없다 — **워크숍(Desktop) 경로 아님.**

---

## 트러블슈팅

### Windows에서 Code 탭이 안 열림 / "Git not found"
Git for Windows 미설치. https://git-scm.com/downloads/win 설치 후 **앱 완전 종료 후 재시작**. Code 탭은 세션 격리에 Git을 쓴다.

### "Skill을 못 찾음" (`/` 목록에 안 보임)
1. **새 세션인가?** skill은 세션 시작 시점에 스캔된다 — 설치를 수행한 그 세션에서는 안 보이는 게 정상.
2. **깊이 확인** (1단계가 정답):
```bash
ls ~/papers/my_paper_2026/.claude/skills/journal-fit-check/SKILL.md   # ← 이게 보이면 정상
ls ~/papers/my_paper_2026/.claude/skills/sam-workshop/                # ← 이 우산 폴더가 있으면 잘못된 설치
```
3. 우산 폴더가 있으면: 그 안의 18개 폴더 + `_shared`를 한 단계 위(`.claude/skills/`)로 이동 후 새 세션.
4. 그래도 안 되면 앱 완전 종료 후 재시작 → 새 세션. 그래도면 facilitator.
(CLI plugin 사용자 확인 위치: `ls ~/.claude/plugins/sam-workshop/skills/sam-workshop/`)

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

워크숍 10-step lifecycle은 **Code 탭에서 완결**한다(skill·script·파일·버전관리가 전부 Code 탭 네이티브).
- **Chat**: 문헌 검색(②)에서 Deep Research가 필요하면 잠깐 사용 가능 (선택).
- **Cowork**: 이번 워크숍에서는 사용하지 않는다. (Code 탭의 파일 에디터·diff·버전관리가 논문 폴더 작업에 더 적합)
- claude.ai **Chat/Cowork에서 skill을 쓰려면** `Settings > Capabilities`에서 code execution을 켜고 `Customize > Skills`에 ZIP을 업로드해야 하는데, **본 워크숍은 그 경로를 쓰지 않는다**(Code 탭 plugin이 더 강력·간단).

---

## 업그레이드 / 제거

**Desktop (워크숍 표준)**:
- 업그레이드 = ④ 설치 발화문을 다시 실행 (새 버전으로 덮어쓰기) → 새 세션
- 제거 = paper_home의 `.claude/skills/` 폴더 삭제 (논문 폴더 본문은 영향 없음)

**CLI plugin 사용자**:
```
/plugin update sam-workshop      # 업그레이드
/plugin uninstall sam-workshop   # 제거
```

---

## 다음

1. `~/papers/my_paper_2026/.sam/hitl/paper_profile.json` 본인 정보 편집
2. (선택) `~/papers/my_paper_2026/.claude/skills/README.md` 통독 (10분)
3. Code 탭에서 `"내 논문 어느 저널에 투고할까?"` 발화 → 워크숍 시작

facilitator 응답 스크립트: [FACILITATOR_SCRIPTS.md](FACILITATOR_SCRIPTS.md) (참가자 비공개).
