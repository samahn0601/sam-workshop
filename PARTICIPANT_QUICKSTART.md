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

## 워크숍 당일 — 4단계 (~5분)

### ① Claude Desktop 앱 → **Code 탭** 열기
로그인 후 상단 **Code** 탭. (Windows 첫 실행 시 Git 설치 안내 따르고 앱 재시작)

### ② Plugin 설치 (+버튼>Plugins>Add plugin, 또는 명령)
```
/plugin marketplace add samahn0601/sam-workshop
/plugin install sam-workshop@samahn0601
```
→ 17 skill + scripts 자동 설치.

### ③ paper_home 초기화 (Code 탭 통합 터미널)

🍎 **Mac**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-mac.sh) my_paper_2026
```
🪟 **Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/samahn0601/sam-workshop/main/install/init-workshop-windows.ps1 | iex
sam-init my_paper_2026
```

### ④ paper_home 폴더로 세션 → 첫 발화
```
"내 논문 어느 저널에 투고할까?"
```
→ `journal-fit-check` 자동 발화 + 운전 모드 제시. Step 1 시작.

---

## 슬라이드 인쇄용 요약 (4줄)

```
[Code 탭]  /plugin marketplace add samahn0601/sam-workshop
[설치]     /plugin install sam-workshop@samahn0601
[Mac]      bash <(curl -fsSL .../init-workshop-mac.sh) my_paper_2026
[Windows]  irm .../init-workshop-windows.ps1 | iex; sam-init my_paper_2026
[첫 발화]  "내 논문 어느 저널에 투고할까?"
```

---

## 트러블 — facilitator에게 묻기 전에 1번만 시도

| 증상 | 1차 대응 |
|---|---|
| (Windows) Code 탭이 안 열림 | Git for Windows 설치 → 앱 완전 종료 후 재시작 |
| "skill not found" | Code 탭 새 세션 |
| Plugin install이 멈춤 | 인터넷 + GitHub access 확인 |
| `sam-init` 못 찾음 (Windows) | PowerShell 새 창에서 `irm ... \| iex` 다시 |
| "pandoc not found" | preflight가 알려줌 → "docx 패키징은 homework"로 진행 |

해결 안 됨 → facilitator 호출. 워크숍은 다음 step으로 진행(멈추지 않음).

---

## Fallback — Plugin install이 안 되는 경우 (manual copy)

#### Mac
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

`~/.claude/skills/`에 둔 skill은 Code 탭이 그대로 인식한다.
