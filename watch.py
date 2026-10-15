"""보드라이프 게임 게시판에 새 글이 올라오면 텔레그램으로 알린다.

이 Mac의 launchd가 10분마다 실행한다(보드라이프가 클라우드 서버 IP를 403으로 막아
GitHub Actions에서는 돌릴 수 없다). 이미 본 글은 seen.json에 남긴다.
seen.json이 없으면(첫 실행) 현재 글을 기록만 하고 알림은 보내지 않는다.
봇 토큰·chat id는 환경변수가 없으면 macOS 키체인(setup_telegram.py가 저장)에서 읽는다.
"""

import html
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

GAME_ID = os.environ.get("GAME_ID", "15778")
BOARD_URL = f"https://boardlife.co.kr/game/{GAME_ID}/board"
SEEN_PATH = Path(__file__).with_name("seen.json")
SEEN_LIMIT = 500  # 목록이 20개라 넉넉히만 보관
KEYCHAIN_SERVICE = "boardlife-watch"

# python.org 설치본은 기본 인증서가 없어 macOS 시스템 인증서를 쓴다
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem" if os.path.exists("/etc/ssl/cert.pem") else None)

ROW_RE = re.compile(
    r"<a class='post-row' href='(?P<href>[^']+)'[^>]*?"
    r"data-tb='(?P<tb>[^']+)' data-num='(?P<num>\d+)' data-ad-on='(?P<ad>\d)'"
    r".*?<span class='post-cat[^']*'>(?P<cat>.*?)</span>"
    r"<span class='post-title-txt'>(?P<title>.*?)</span>"
    r".*?<span class='post-author'>(?P<author>.*?)</span>",
    re.S,
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (boardlife-watch)"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as res:
        return res.read().decode("utf-8")


def parse_posts(page: str) -> list[dict]:
    posts = []
    for m in ROW_RE.finditer(page):
        if m["ad"] != "0":
            continue
        posts.append({
            "key": f"{m['tb']}:{m['num']}",
            "url": urllib.parse.urljoin(BOARD_URL, html.unescape(m["href"])),
            "category": html.unescape(re.sub(r"<[^>]+>", "", m["cat"])).strip(),
            "title": html.unescape(re.sub(r"<[^>]+>", "", m["title"])).strip(),
            "author": html.unescape(re.sub(r"<[^>]+>", "", m["author"])).strip(),
        })
    return posts


def secret(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    return subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", name, "-w"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def send_telegram(text: str) -> None:
    token = secret("TELEGRAM_BOT_TOKEN")
    for chat_id in secret("TELEGRAM_CHAT_ID").split(","):
        data = urllib.parse.urlencode({
            "chat_id": chat_id.strip(),
            "text": text,
            "disable_web_page_preview": "true",
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data, timeout=30, context=CTX
        ).read()


def main() -> int:
    posts = parse_posts(fetch(BOARD_URL))
    if not posts:
        # 사이트 구조가 바뀌면 조용히 넘어가지 말고 실패로 드러낸다
        print("게시글을 하나도 찾지 못했다 — 페이지 구조 변경 가능성", file=sys.stderr)
        return 1

    first_run = not SEEN_PATH.exists()
    seen = [] if first_run else json.loads(SEEN_PATH.read_text())
    seen_set = set(seen)
    new_posts = [p for p in posts if p["key"] not in seen_set]

    if first_run:
        print(f"첫 실행: 현재 글 {len(posts)}개를 기록만 하고 알림은 보내지 않는다")
    else:
        # 오래된 글부터 보내 대화창에서 시간순으로 읽히게 한다
        for p in reversed(new_posts):
            send_telegram(f"[보드라이프 새 글] {p['category']}\n{p['title']} - {p['author']}\n{p['url']}")
        print(f"새 글 {len(new_posts)}개 알림")

    merged = [p["key"] for p in new_posts] + seen
    SEEN_PATH.write_text(json.dumps(merged[:SEEN_LIMIT], ensure_ascii=False, indent=0) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
