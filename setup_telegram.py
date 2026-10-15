"""텔레그램 봇 토큰과 친구 chat id를 GitHub 시크릿에 등록한다.

토큰은 화면에 보이지 않게 입력받고, 출력하지 않은 채 바로 `gh secret set`으로 넘긴다.
친구가 봇에 /start를 보낸 뒤 실행해야 chat 목록에 나타난다.
    python3 setup_telegram.py
"""

import getpass
import json
import os
import ssl
import subprocess
import urllib.request

REPO = "AhnJoonSung/boardlife-watch"

# python.org 설치본은 기본 인증서가 없어 macOS 시스템 인증서를 쓴다
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem" if os.path.exists("/etc/ssl/cert.pem") else None)


def call(token: str, method: str) -> dict:
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}", context=CTX, timeout=30) as res:
        return json.load(res)


def set_secret(name: str, value: str) -> None:
    subprocess.run(["gh", "secret", "set", name, "--repo", REPO], input=value.encode(), check=True)


def main() -> None:
    token = getpass.getpass("BotFather가 준 봇 토큰을 붙여넣고 Enter (화면에 안 보임): ").strip()
    bot = call(token, "getMe")["result"]
    print(f"봇 확인: @{bot['username']}")

    chats = {}
    for u in call(token, "getUpdates")["result"]:
        chat = (u.get("message") or u.get("my_chat_member") or {}).get("chat")
        if chat:
            chats[chat["id"]] = " ".join(filter(None, [chat.get("first_name"), chat.get("last_name")])) or chat.get("title", "")
    if not chats:
        print(f"아직 아무도 봇에 말을 걸지 않았다. 친구가 https://t.me/{bot['username']} 에서 /start를 보낸 뒤 다시 실행.")
        set_secret("TELEGRAM_BOT_TOKEN", token)
        print("봇 토큰만 먼저 등록했다.")
        return

    ids = list(chats)
    for i, cid in enumerate(ids, 1):
        print(f"  {i}. {chats[cid]}")
    picked = input("알림 받을 사람 번호 (여러 명이면 쉼표, 예: 1,2): ")
    chat_ids = ",".join(str(ids[int(n) - 1]) for n in picked.split(","))

    set_secret("TELEGRAM_BOT_TOKEN", token)
    set_secret("TELEGRAM_CHAT_ID", chat_ids)
    print("시크릿 2개 등록 완료.")


if __name__ == "__main__":
    main()
