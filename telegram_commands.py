#!/usr/bin/env python3
"""Register chat-scoped slash commands for the Jean-Clawd Telegram bot.

Chat scope wins over the plugin's all_private_chats defaults and survives
plugin restarts. Edit COMMANDS, re-run, done.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

CHAT_ID = 8581449495  # Yann
ENV_PATH = Path.home() / ".claude/channels/telegram/.env"

COMMANDS = [
    {"command": "start",   "description": "Welcome and setup guide"},
    {"command": "help",    "description": "What this bot can do"},
    {"command": "status",  "description": "Check your pairing status"},
    {"command": "usage",   "description": "Token / cost report for this bot"},
    {"command": "review",  "description": "Review a pull request"},
    {"command": "security_review", "description": "Security review of pending changes"},
    {"command": "simplify", "description": "Review and simplify changed code"},
    {"command": "serve_streamlit", "description": "Expose a Streamlit app on jean-clawd.com"},
    {"command": "init",    "description": "Initialize CLAUDE.md for a repo"},
    {"command": "memory",  "description": "Dump current memory state"},
]


def load_token() -> str:
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"TELEGRAM_BOT_TOKEN not found in {ENV_PATH}")


def api(token: str, method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main() -> None:
    token = load_token()
    scope = {"type": "chat", "chat_id": CHAT_ID}

    result = api(token, "setMyCommands", {"commands": COMMANDS, "scope": scope})
    if not result.get("ok"):
        sys.exit(f"setMyCommands failed: {result}")

    confirm = api(token, "getMyCommands", {"scope": scope})
    cmds = confirm.get("result", [])
    print(f"registered {len(cmds)} commands for chat {CHAT_ID}:")
    width = max(len(c["command"]) for c in cmds) + 2
    for c in cmds:
        print(f"  /{c['command']:<{width}} {c['description']}")


if __name__ == "__main__":
    main()
