# Sam Workshop Skill Pack — INSTALL (Claude Desktop **Code 탭** 기준)

> **최신·정본 설치 안내(복사 버튼 포함): https://sam-workshop-landing.vercel.app**
> 이 문서는 상세 참조본. 1-page 요약: [PARTICIPANT_QUICKSTART.md](PARTICIPANT_QUICKSTART.md).
> 흐름: **계정 2개(메일 안내·미리) → 앱·(Win)Git 설치(당일·더블클릭) → Code 탭 발화 2개.** 터미널 타이핑 없음.
> 주력 환경 = Claude Desktop 앱의 **Code 탭**(곧 Claude Code — skill·script·로컬 파일이 네이티브).

---

## 0. 계정 — 안내 메일 (미리 권장 · 안 했으면 당일)

| 계정 | 용도 | 가입 |
|---|---|---|
| **Claude 팀 플랜 'DCU Medicine RISE'** | 오늘 쓰는 Claude (프리미엄 팀 = Max급 시트 → Code 탭 OK) | [가입 링크](https://claude.ai/join/org/aHKL8WbLw92x94OBr3a1PA) · **@cu.ac.kr 메일로 로그인 필수** (6/11~7/10) |
| **교직원포털 AI** (blue.cu.ac.kr) | 당일 교차검증용 보조 (GPT·Claude·Gemini) | 행정 › 정보처리서비스 › 생성형AI 서비스신청 → 'Super Agent' (의료원 포털과 다름) |

준비물: 개인 노트북(**배터리 완충 + 충전기 지참**) · 구글 / @cu.ac.kr 계정 · (필요시) 연구 데이터.

## 1. 설치 — 당일, 설치파일 더블클릭 (터미널 X · OT와 동시)

| 프로그램 | 역할 | 설치 |
|---|---|---|
| **Claude Desktop 앱** | AI 작업실 (Code 탭에서 파일·폴더 작업) | claude.ai/download → **@cu.ac.kr (DCU Medicine RISE 팀) 로그인** |
| **Git for Windows** (Windows만) | 자료 받아오기 · **Windows Code 탭 첫 실행 전제** | git-scm.com/downloads/win → 앱 재시작 *(Code 탭에선 못 깖)* |
| **Python** | 참고문헌·통계 점검 스크립트 실행기 | 아래 **발화 1이 자동 설치** (user-scope, 관리자 권한 불필요) |

> Mac은 Git·Python이 대개 기본 포함. 미리 안 해와도 됨 — 설치는 OT와 동시에 진행하고 막히면 손 들기.

## 2. Code 탭에서 — 발화 2개

> Code 탭의 skill 탐지는 `.claude/skills/<skill>/SKILL.md` **1단계만** 인식한다. 우산 폴더째(2단계) 복사는 전부 미탐지 — 아래 발화가 그 함정을 피하는 검증된 경로(2026-06-10 Desktop 실측).

### ① 작업 폴더
Code 탭 → **폴더 선택(Select folder)** → 오늘 논문용 빈 폴더. (Windows 첫 실행이면 1의 Git 설치·재시작 먼저)

### ② 발화 1 — 셋업 (붙여넣기, 권한 물으면 승인)
```
지금 선택한 이 폴더를 제 논문 작업 폴더로 셋업해줘. 터미널 명령은 네가 실행하고, 권한 물으면 내가 승인할게.
1) https://github.com/samahn0601/sam-workshop 를 clone하고, 그 안 skills/sam-workshop/ 의 18개 skill 폴더(진입점 start-here + 작업 skill 17)와 _shared 폴더를 이 폴더의 .claude/skills/ 바로 아래로 복사해줘. (우산 폴더 sam-workshop을 만들지 말 것 — .claude/skills/start-here 처럼 1단계가 되도록.)
2) git이 없으면 ZIP https://github.com/samahn0601/sam-workshop/archive/refs/heads/main.zip 을 받아서 풀어 같은 위치에 넣어줘.
3) python이 있는지 확인하고, 없으면 관리자 권한 없이(user 설치) 깔아줘 — Windows면 'winget --scope user' 또는 python.org 설치파일을 사용자 모드(PATH 추가)로, Mac이면 이미 있는 python3 사용. 그다음 'pip install --user python-docx'까지. 막히면 건너뛰고 무엇이 막혔는지 알려줘.
끝나면 .claude/skills/ 바로 아래 폴더 목록을 보여줘.
```
→ Claude가 clone(또는 ZIP)→평평 복사→(필요시) Python 설치→목록까지 직접 수행. 18 폴더(start-here + 작업 17) + `_shared`가 보이면 성공.

### ③ 발화 2 — 새 세션 → 첫 발화
`.claude/skills/`가 새로 생긴 직후라 **새 세션을 한 번 더** 연다(skill은 세션 시작 시점에 스캔). `/`를 쳐서 `start-here`·`journal-fit-check` 등 **18개**가 보이면 탐지 성공. 이어서:
```
시작하자
```
→ `start-here`가 10-step 맵·운전 모드 제시 → `gate_plan` 작성 → Step 1부터 안내(각 단계 끝에 **"다음"** — 한 번에 끝까지 자동이 아니라 단계별 내비게이션).

---

## Fallback — 발화 대신 직접 복사 (터미널 익숙한 분만)

⚠️ **우산 폴더 금지** — `skills/sam-workshop` 폴더째 복사하면 2단계가 되어 전부 미탐지(실측 함정). **내용물**을 `.claude/skills/` 바로 아래로.

#### Mac / Linux
```bash
git clone https://github.com/samahn0601/sam-workshop.git
mkdir -p ~/papers/my_paper_2026/.claude/skills
cp -R sam-workshop/skills/sam-workshop/. ~/papers/my_paper_2026/.claude/skills/
ls ~/papers/my_paper_2026/.claude/skills/   # → 18 폴더(start-here + 작업 17) + _shared
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/samahn0601/sam-workshop.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\papers\my_paper_2026\.claude\skills" | Out-Null
Copy-Item -Recurse -Force sam-workshop\skills\sam-workshop\* "$env:USERPROFILE\papers\my_paper_2026\.claude\skills\"
dir "$env:USERPROFILE\papers\my_paper_2026\.claude\skills"   # → 18 폴더 + _shared
```
복사 후 Code 탭에서 해당 폴더로 **새 세션** → `/` 목록 확인.

### (참고) CLI · VS Code/JetBrains 사용자 — `/plugin` 경로
```
/plugin marketplace add samahn0601/sam-workshop
/plugin install sam-workshop@samahn0601
```
⚠️ **Desktop 앱 Code 탭에는 `/plugin`이 없고** Plugins GUI는 공식 마켓플레이스 읽기 전용 → **워크숍(Desktop) 경로 아님.**

---

## 트러블슈팅

**Windows에서 Code 탭이 안 열림 / "Git not found"** → Git for Windows 설치 후 **앱 완전 종료 후 재시작**. (Code 탭은 세션 격리에 Git을 씀)

**"Skill을 못 찾음" (`/`에 안 보임)**
1. **새 세션인가?** skill은 세션 시작 시점에 스캔 — 설치한 그 세션에선 안 보이는 게 정상.
2. **깊이 확인** — `.claude/skills/start-here/SKILL.md`가 보이면 정상 / `.claude/skills/sam-workshop/`(우산)이 있으면 잘못. 우산이면 그 안의 18 폴더 + `_shared`를 한 단계 위로 옮기고 새 세션.
3. 그래도면 앱 완전 종료 후 재시작 → 새 세션 → facilitator.

**로그인/팀 접속 안 됨** → 반드시 **@cu.ac.kr 메일**로 'DCU Medicine RISE' 팀에 가입·로그인했는지 확인(가입 링크는 0번). 안 되면 손 들기.

**"권한 없음 / Access denied"로 설치 실패** → 관리형(기관) 노트북에서 본체(Git·Python) 전역 설치가 막힌 경우. 더블클릭 설치파일로 깔거나 보조진 호출. **python-docx 등 패키지(user-scope)는 영향 없음.**

**"pandoc not found"** → ⑦ docx 패키징은 homework. 그대로 진행.

**Python script 오류 / PubMed** → 발화 1이 방금 Python을 깔았으면 **새 세션**에서 PATH 반영. PubMed/Crossref는 인터넷 + 본인 이메일(`--email YOUR_EMAIL`) 필요, API key 없이 초당 3회 정상.

**교차검증용 GPT/Gemini** → 교직원포털 AI(blue.cu.ac.kr) 또는 본인 계정. 무료 한도 초과 시 ⑥ critic은 Claude "External Skeptic" 페르소나로 대체.

---

## (참고) Cowork / Chat은 안 쓰나?

워크숍 10-step lifecycle은 **Code 탭에서 완결**한다(skill·script·파일·버전관리가 전부 Code 탭 네이티브).
- **Chat**: 문헌 검색(②)에서 Deep Research가 필요하면 잠깐 사용 (선택).
- **Cowork**: 이번 워크숍에서는 사용하지 않는다.

## 업그레이드 / 제거

- 업그레이드 = ② 발화 1을 다시 실행(새 버전 덮어쓰기) → 새 세션
- 제거 = paper_home의 `.claude/skills/` 폴더 삭제 (논문 폴더 본문은 영향 없음)
- CLI plugin 사용자: `/plugin update sam-workshop` · `/plugin uninstall sam-workshop`

---

facilitator 응답 스크립트: [FACILITATOR_SCRIPTS.md](FACILITATOR_SCRIPTS.md) (참가자 비공개).
