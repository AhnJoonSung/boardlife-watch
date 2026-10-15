# boardlife-watch

보드라이프 「히트: 질주의 열기」 게시판(https://boardlife.co.kr/game/15778/board)에
새 글이 올라오면 텔레그램으로 알린다. GitHub Actions가 10분마다 확인한다.

## 설정

1. 텔레그램에서 @BotFather → `/newbot` → 봇 토큰을 받는다.
2. 친구가 그 봇을 열고 `/start`를 보낸다.
3. 아래 주소를 브라우저로 열어 `"chat":{"id":...}` 숫자를 찾는다(친구의 chat id).
   `https://api.telegram.org/bot<봇토큰>/getUpdates`
4. GitHub 레포 Settings → Secrets and variables → Actions에 두 개를 등록한다.
   - `TELEGRAM_BOT_TOKEN` = 봇 토큰
   - `TELEGRAM_CHAT_ID` = 친구 chat id (여러 명이면 쉼표로 구분)
5. Actions 탭 → boardlife-watch → Run workflow로 한 번 실행한다.
   첫 실행은 현재 글을 기록만 하고, 그 뒤 새로 올라온 글부터 알림이 간다.

## 참고

- 다른 게임을 보려면 워크플로 env에 `GAME_ID`를 넣는다.
- public 레포면 Actions 실행 시간이 무료로 무제한이다. private이면 무료 한도(월 2,000분)를
  넘으니 cron 간격을 30분 이상으로 늘린다.
- 레포에 60일간 활동이 없으면 GitHub이 예약 실행을 멈춘다. 그러면 Actions 탭에서 다시 켠다.
