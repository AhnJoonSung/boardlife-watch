# boardlife-watch

보드라이프 「히트: 질주의 열기」 게시판(https://boardlife.co.kr/game/15778/board)에
새 글이 올라오면 텔레그램으로 알린다. 이 Mac의 launchd가 10분마다 확인한다.

보드라이프가 클라우드 서버 IP(GitHub Actions 등)를 403으로 막아 집/사무실 Mac에서 돌린다.
Mac이 꺼져 있거나 잠자기 중이면 확인하지 않고, 깨어나면 놓친 새 글을 한꺼번에 보낸다(목록 20개 범위 안).

## 설정

1. 텔레그램 @BotFather → `/newbot` → 봇 토큰을 받는다.
2. 친구가 `https://t.me/<봇아이디>`를 열고 `/start`를 보낸다.
3. `python3 setup_telegram.py` 실행 → 토큰 붙여넣기 → 친구 번호 선택.
   토큰과 chat id는 macOS 키체인(서비스명 `boardlife-watch`)에 저장된다.

## 실행 주기 (launchd)

- 설정 파일: `~/Library/LaunchAgents/com.ahn.boardlife-watch.plist`
- 로그: `watch.log`
- 끄기: `launchctl bootout gui/$(id -u)/com.ahn.boardlife-watch`
