# Workshop Quickstart — 1-page (Claude Desktop **Code 탭**, 5분)

> 이 문서가 그대로 워크숍 첫 슬라이드. 본인 OS 옆 명령어만 복붙. **주력 환경 = Code 탭** (Cowork/CLI 아님).

---

## 사전 준비 (D-7 안내문에서 미리 안내)

**모든 참가자**:
- 학교 지원 Claude Pro/Max + **Claude Desktop 앱** 설치 (claude.ai)
- Python 3.9+
- **Windows 사용자: Git for Windows** (https://git-scm.com/downloads/win) — Code 탭 첫 실행 전제
- (권장) Quarto (pandoc 자동 포함)

**확인 1줄** (Code 탭 통합 터미널):
```
Mac/Linux:   python3 --version && git --version
Windows:     python --version; git --version
```

---

## 워크숍 당일 — 5단계 (~5분)

### ① Claude Desktop 앱 → **Code 탭** 열기
로그인 후 상단 **Code** 탭. (Windows 첫 실행 시 Git 설치 안내 따르고 앱 재시작)

### ② paper_home 초기화 (Code 탭 통합 터미널)

🍎 **Mac**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-mac.sh) my_paper_2026
```
🪟 **Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-windows.ps1 | iex
sam-init my_paper_2026
```

### ③ Code 탭 **새 세션** → 작업 폴더 = `~/papers/my_paper_2026`

### ④ Skill 설치 — 아래 발화문 그대로 붙여넣기

```
https://github.com/samahn0601/sam-workshop 를 clone해서, 그 안의 skills/sam-workshop/ 폴더에 있는
18개 skill 폴더(진입점 start-here + 작업 skill 17)와 _shared 폴더를 지금 작업 폴더의 .claude/skills/ 바로 아래로 복사해줘.
(우산 폴더 sam-workshop을 만들지 말 것 — 1단계가 되도록.) git이 없으면
ZIP https://github.com/samahn0601/sam-workshop/archive/refs/heads/main.zip 으로.
끝나면 .claude/skills/ 바로 아래 폴더 목록을 보여줘.
```

### ⑤ **새 세션 1회** → `/` 쳐서 18개 확인 → 첫 발화
```
"시작하자"   (또는 "내 논문 어느 저널에 투고할까?")
```
→ `start-here`가 10-step 맵·운전 모드 제시 → Step 1(`journal-fit-check`)부터 자동 안내.

---

## 슬라이드 인쇄용 요약 (4줄)

```
[터미널·Mac]  bash <(curl -fsSL .../init-workshop-mac.sh) my_paper_2026
[터미널·Win]  irm .../init-workshop-windows.ps1 | iex; sam-init my_paper_2026
[새 세션]     작업 폴더 = ~/papers/my_paper_2026
[설치 발화]   "sam-workshop repo를 clone해서 18개 skill(start-here 포함)+_shared를 .claude/skills/ 바로 아래로" (우산 금지)
[새 세션 후]  "/" 목록에 18개 확인 → "시작하자"
```

---

## 트러블 — facilitator에게 묻기 전에 1번만 시도

| 증상 | 1차 대응 |
|---|---|
| (Windows) Code 탭이 안 열림 | Git for Windows 설치 → 앱 완전 종료 후 재시작 |
| `/` 목록에 skill이 안 보임 | **새 세션**(설치한 세션에선 안 보임) + `.claude/skills/journal-fit-check`가 **1단계**인지 확인(우산 폴더 금지) |
| 설치 발화가 멈춤 | 인터넷 + github.com 접근 확인 → 발화문의 ZIP 폴백 사용 |
| `sam-init` 못 찾음 (Windows) | PowerShell 새 창에서 `irm ... \| iex` 다시 |
| "pandoc not found" | preflight가 알려줌 → "docx 패키징은 homework"로 진행 |

해결 안 됨 → facilitator 호출. 워크숍은 다음 step으로 진행(멈추지 않음).

---

## Fallback — 설치 발화 대신 터미널로 직접 복사

⚠️ **우산 폴더 금지** — `skills/sam-workshop` 폴더째 복사하면 2단계가 되어 전부 미탐지(실측 확인). **내용물**을 `.claude/skills/` 바로 아래로:

#### Mac
```bash
git clone https://github.com/samahn0601/sam-workshop.git
mkdir -p ~/papers/my_paper_2026/.claude/skills
cp -R sam-workshop/skills/sam-workshop/. ~/papers/my_paper_2026/.claude/skills/
```
#### Windows (PowerShell)
```powershell
git clone https://github.com/samahn0601/sam-workshop.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\papers\my_paper_2026\.claude\skills" | Out-Null
Copy-Item -Recurse -Force sam-workshop\skills\sam-workshop\* "$env:USERPROFILE\papers\my_paper_2026\.claude\skills\"
```

복사 후 **새 세션**에서 `/` 목록 확인. (CLI·IDE 사용자만: `/plugin marketplace add samahn0601/sam-workshop` → `/plugin install sam-workshop@samahn0601` — Desktop Code 탭엔 `/plugin` 없음)
