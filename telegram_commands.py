#!/usr/bin/env python3
"""Register chat-scoped slash commands for a Claude Code Telegram bot.

Chat scope wins over the plugin's all_private_chats defaults and survives
plugin restarts. Edit COMMANDS, re-run, done.

Configuration (via env, or via ~/.claude/channels/telegram/.env):
  TELEGRAM_BOT_TOKEN   — required, the bot token from @BotFather
  TELEGRAM_CHAT_ID     — required, the numeric chat_id to scope commands to
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

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
    {"command": "projects", "description": "List past projects; add a name to reload one"},
]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    env.update({k: v for k, v in os.environ.items() if k.startswith("TELEGRAM_")})
    return env


def require(env: dict[str, str], key: str) -> str:
    val = env.get(key)
    if not val:
        sys.exit(f"{key} not set (looked in env and {ENV_PATH})")
    return val


def api(token: str, method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main() -> None:
    env = load_env()
    token = require(env, "TELEGRAM_BOT_TOKEN")
    chat_id = int(require(env, "TELEGRAM_CHAT_ID"))
    scope = {"type": "chat", "chat_id": chat_id}

    result = api(token, "setMyCommands", {"commands": COMMANDS, "scope": scope})
    if not result.get("ok"):
        sys.exit(f"setMyCommands failed: {result}")

    confirm = api(token, "getMyCommands", {"scope": scope})
    cmds = confirm.get("result", [])
    print(f"registered {len(cmds)} commands for chat {chat_id}:")
    width = max(len(c["command"]) for c in cmds) + 2
    for c in cmds:
        print(f"  /{c['command']:<{width}} {c['description']}")


if __name__ == "__main__":
    main()
