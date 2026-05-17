# telegram-claude-shortcuts

Add custom `/slash` shortcuts to the [Claude Code](https://claude.com/claude-code) Telegram plugin without forking it.

The official plugin ships three commands (`/start`, `/help`, `/status`). This repo shows how to add as many more as you want — `/usage`, `/review`, `/security_review`, whatever — by registering a **chat-scoped** command list directly with the Telegram Bot API. The plugin never touches it, so the shortcuts survive plugin updates.

## TL;DR

A Telegram bot has **two independent layers**:

| Layer | What it is | How we configure it |
|---|---|---|
| **Menu** | The autocomplete list the user sees behind the `×` button | Bot API `setMyCommands` |
| **Handling** | What happens when `/foo` is sent | Plugin `bot.command(...)` handler **or** fallback to `bot.on('message:text')` |

Anything not claimed by `bot.command(...)` falls through as plain text. The Claude Code plugin forwards that text to Claude, which routes it via [skills](https://docs.claude.com/en/docs/claude-code/skills) or your `CLAUDE.md`. **So adding new shortcuts requires zero plugin changes** — just register the menu entry and let Claude do the work.

## Why chat scope

Telegram's command-scope precedence (highest first):

1. `BotCommandScopeChatMember` — one user in one chat
2. **`BotCommandScopeChat` — one chat (← we use this)**
3. `BotCommandScopeAllChatAdministrators` / `BotCommandScopeAllGroupChats`
4. `BotCommandScopeAllPrivateChats` ← the Claude Code plugin sets its three defaults here on startup
5. `BotCommandScopeDefault`

A chat-scoped list wins over the plugin's `all_private_chats` defaults and **is not overwritten when the plugin restarts**. That's the whole trick.

## Usage

### Prereqs

- A working Claude Code Telegram plugin install (token in `~/.claude/channels/telegram/.env` as `TELEGRAM_BOT_TOKEN=...`)
- Python 3 (no external deps — `urllib` only)
- Your Telegram numeric `chat_id`

### Run it

```bash
# edit CHAT_ID and COMMANDS at the top
$ ./telegram_commands.py
registered 10 commands for chat 8581449495:
  /start             Welcome and setup guide
  /help              What this bot can do
  /status            Check your pairing status
  /usage             Token / cost report for this bot
  /review            Review a pull request
  /security_review   Security review of pending changes
  /simplify          Review and simplify changed code
  /serve_streamlit   Expose a Streamlit app on jean-clawd.com
  /init              Initialize CLAUDE.md for a repo
  /memory            Dump current memory state
```

To **change** the menu: edit the `COMMANDS = [...]` block and re-run. To **wipe** it and fall back to the plugin defaults:

```bash
TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' ~/.claude/channels/telegram/.env | cut -d= -f2)
curl -s "https://api.telegram.org/bot${TOKEN}/deleteMyCommands" \
  -H 'Content-Type: application/json' \
  -d '{"scope":{"type":"chat","chat_id":<YOUR_CHAT_ID>}}'
```

### How Claude handles the new shortcuts

When `/usage` arrives, the plugin has no `bot.command('usage', ...)` handler, so the text falls through to `bot.on('message:text', …)` and reaches Claude as the literal string `"/usage"`. Two ways to route it:

- **Skill** — create `~/.claude/skills/usage/SKILL.md` whose frontmatter `description` names the trigger ("Use when the user invokes /usage…"). The skill body is the procedure. Best for repeatable actions.
- **Inline CLAUDE.md** — fine for one-offs; document what should happen when the slash is seen.

## Command name rules

Strictly enforced by the Bot API:

- `[a-z0-9_]+` — lowercase ASCII, digits, underscores only. No hyphens, no camelCase.
- 1–32 chars.
- No leading `/` in the API payload.
- Don't reassign `start` / `help` / `status` — the plugin already has handlers for those (you *can* re-list them in the menu, just don't expect different behavior).

## Caveats

- **Per-client cache.** The menu refreshes after the user taps × Menu twice, switches chats, or restarts the Telegram app.
- **Per-user scope.** If you also use the bot in a group, register a separate `{type:"chat", chat_id:-100…}` scope for it.
- **Single source of truth.** If you run the script from machine A, don't also maintain the list on machine B — chat scope is *replace*, not merge.

## References

- [Telegram Bot API — setMyCommands](https://core.telegram.org/bots/api#setmycommands)
- [Telegram Bot API — BotCommandScope](https://core.telegram.org/bots/api#botcommandscope)
- [Claude Code Telegram plugin](https://github.com/anthropics/claude-plugins)
- [Claude Code skills docs](https://docs.claude.com/en/docs/claude-code/skills)

## License

MIT.
