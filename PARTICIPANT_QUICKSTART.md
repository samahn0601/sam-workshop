# Workshop Quickstart — 설치 1장 (Claude Desktop **Code 탭**)

> **최신·정본 안내(복사 버튼 포함): https://sam-workshop-landing.vercel.app**
> 이 문서는 그 텍스트 요약본. **터미널 타이핑 없음** — 설치파일 더블클릭 + Code 탭에 붙여넣기.

---

## 먼저 — 계정 2개 (안내 메일, 미리 권장 · 안 했으면 당일도 OK)

1. **Claude 팀 플랜 'DCU Medicine RISE'** 가입 — https://claude.ai/join/org/aHKL8WbLw92x94OBr3a1PA
   · **반드시 @cu.ac.kr 메일로 로그인** (프리미엄 팀 = Max급 시트, 6/11~7/10)
2. **교직원포털 AI** 가입 (교차검증용) — blue.cu.ac.kr → 행정 › 정보처리서비스 › 생성형AI 서비스신청 → 'Super Agent'에서 모델 선택 (메일 첨부 매뉴얼)

🔋 **준비물**: 개인 노트북 **배터리 완충 + 충전기 지참** · 구글 / @cu.ac.kr 계정.

## STEP 1 · 지금 설치 (설치파일 더블클릭 · OT와 동시 진행)

- **Claude Desktop 앱** — claude.ai/download → **@cu.ac.kr 계정(DCU Medicine RISE 팀)** 으로 로그인
- **(Windows만) Git for Windows** — git-scm.com/downloads/win → 설치 후 앱 재시작
  *(Windows에선 Code 탭 첫 실행 전제라 Code 탭에선 못 깖. Mac은 보통 이미 있음)*
- **Python은 안 깔아도 됨** → STEP 2 발화 1이 자동 설치(관리자 권한 불필요)

## STEP 2 · 설치되면 Code 탭에서 (보통 OT 중에 끝남)

**① 작업 폴더** — Code 탭 → **폴더 선택** → 오늘 논문용 빈 폴더 하나

**② 발화 1 (셋업)** — 입력창에 붙여넣기 (권한 물으면 승인만):
```
지금 선택한 이 폴더를 제 논문 작업 폴더로 셋업해줘. 터미널 명령은 네가 실행하고, 권한 물으면 내가 승인할게.
1) https://github.com/samahn0601/sam-workshop 를 clone하고, 그 안 skills/sam-workshop/ 의 18개 skill 폴더(진입점 start-here + 작업 skill 17)와 _shared 폴더를 이 폴더의 .claude/skills/ 바로 아래로 복사해줘. (우산 폴더 sam-workshop을 만들지 말 것 — .claude/skills/start-here 처럼 1단계가 되도록.)
2) git이 없으면 ZIP https://github.com/samahn0601/sam-workshop/archive/refs/heads/main.zip 을 받아서 풀어 같은 위치에 넣어줘.
3) python이 있는지 확인하고, 없으면 관리자 권한 없이(user 설치) 깔아줘 — Windows면 'winget --scope user' 또는 python.org 설치파일을 사용자 모드(PATH 추가)로, Mac이면 이미 있는 python3 사용. 그다음 'pip install --user python-docx'까지. 막히면 건너뛰고 무엇이 막혔는지 알려줘.
끝나면 .claude/skills/ 바로 아래 폴더 목록을 보여줘.
```
⚠️ **우산 폴더 금지** — `sam-workshop` 폴더째 넣으면 skill이 안 잡힘 (발화에 이미 반영됨).

**③ 발화 2** — **새 세션**(설치한 세션엔 안 보임) → `/`로 **18개** 확인 → 입력:
```
시작하자
```
→ `start-here`가 논문 10단계를 차례로 안내. 단계 끝마다 **"다음"**.

---

## 막히면 — 손 들기 전에 1번만

| 증상 | 1차 대응 |
|---|---|
| (Win) Code 탭이 안 열림 | Git for Windows 설치 → 앱 완전 종료 후 재시작 |
| `/`에 skill이 안 보임 | **새 세션**인지 + `.claude/skills/start-here`가 1단계인지(우산 금지) |
| 발화 1이 멈춤 | github.com 접근 확인 → 발화의 ZIP 폴백이 자동 시도 |
| "권한 없음"으로 설치 실패 | 관리형 노트북 — 손 들기 (Git·Python 본체만 해당, 패키지는 영향 없음) |
| "pandoc not found" | docx 변환은 나중으로 미루고 진행 (무시 OK) |

해결 안 되면 손 들어 주세요 — 워크숍은 멈추지 않고 진행합니다. (정 안 되면 claude.ai 웹 + 옆자리 pairing)
