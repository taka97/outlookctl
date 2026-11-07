# outlookctl

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> **🔍 Also check out [GNO](https://gno.sh)** ([gmickel/gno](https://github.com/gmickel/gno)) - Local semantic search for your documents, notes, and knowledge base. Combines perfectly with outlookctl: let Claude search your emails *and* your local files. Same privacy-first, local-only philosophy.

Local CLI bridge for Outlook Classic automation on Windows via COM. Includes a Claude Code Skill for AI-assisted email and calendar management.

> **TL;DR**: Can't access Exchange via Microsoft Graph API? No problem. Control Outlook directly through COM automation on your Windows workstation. Let Claude help manage your email and calendar - no API keys, no OAuth, just your existing Outlook session.

## What This Is

`outlookctl` is a **local automation tool** that controls the Outlook desktop client already running on your Windows workstation. It:

- **Uses your existing Outlook session** - No separate authentication, API keys, or OAuth tokens
- **Operates entirely locally** - No network calls to external services, no cloud dependencies
- **Controls the desktop client via COM** - Same automation interface used by VBA macros and Office add-ins
- **Respects your security context** - Runs with your existing permissions, subject to Outlook's security settings

This is **not** a workaround or bypass - it's the standard Windows COM automation interface that Microsoft provides for programmatic Outlook access. The same technology powers countless enterprise tools, email archivers, and Office integrations.

## Use Cases

### Email
- **AI-assisted email triage** - Let Claude help summarize and categorize your inbox
- **Automated drafting** - Generate draft responses with AI assistance, review before sending
- **Email search and retrieval** - Find specific messages across your mailbox
- **Attachment management** - Bulk save attachments to disk

### Calendar
- **View upcoming meetings** - List events across date ranges
- **Create meetings** - Schedule meetings with attendees (draft-first workflow)
- **Respond to invitations** - Accept, decline, or tentatively accept meeting requests
- **Shared calendars** - Access colleagues' calendars (with permissions)

## Documentation

Full documentation is available at [**gmickel.github.io/outlookctl**](https://gmickel.github.io/outlookctl/):

- [CLI Reference](https://gmickel.github.io/outlookctl/cli.html) - Complete command reference
- [JSON Schema](https://gmickel.github.io/outlookctl/json-schema.html) - Output format documentation
- [Security & Data Handling](https://gmickel.github.io/outlookctl/security.html) - Security model and best practices
- [Troubleshooting](https://gmickel.github.io/outlookctl/troubleshooting.html) - Common issues and solutions

## Requirements

- Windows workstation with Classic Outlook (not "New Outlook")
- Outlook running and logged into your account
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/gmickel/outlookctl.git
cd outlookctl
uv sync
```

### 2. Verify Environment

```bash
uv run python -m outlookctl.cli doctor
```

All checks should pass. If not, see [Troubleshooting](https://gmickel.github.io/outlookctl/troubleshooting.html).

### 3. Test Commands

```bash
# List recent emails
uv run python -m outlookctl.cli list --count 5

# Search emails
uv run python -m outlookctl.cli search --from "someone@example.com" --since 2025-01-01

# Create a draft email
uv run python -m outlookctl.cli draft --to "recipient@example.com" --subject "Test" --body-text "Hello"

# List upcoming calendar events (next 7 days)
uv run python -m outlookctl.cli calendar list

# Create a calendar event
uv run python -m outlookctl.cli calendar create --subject "Focus Time" --start "2025-01-20 14:00" --duration 60
```

## CLI Commands

### Email Commands

| Command | Description |
|---------|-------------|
| `doctor` | Validate environment and prerequisites |
| `list` | List messages from a folder |
| `folders` | List the folder tree of the default store (`--all-stores` for every store) |
| `get` | Get a single message by ID |
| `search` | Search messages with filters |
| `draft` | Create a draft, reply or reply-all (keeps the quoted thread) |
| `send` | Send a draft or new message |
| `move` | Move message to another folder |
| `delete` | Delete a message |
| `mark-read` | Mark message as read/unread |
| `forward` | Create a forward draft |
| `attachments save` | Save attachments to disk |

### Calendar Commands

| Command | Description |
|---------|-------------|
| `calendar list` | List events in a date range |
| `calendar get` | Get event details by ID |
| `calendar create` | Create an event or meeting |
| `calendar send` | Send meeting invitations |
| `calendar respond` | Accept/decline/tentative response |
| `calendar update` | Update an existing event |
| `calendar delete` | Delete/cancel an event |

### Contact Group Commands

| Command | Description |
|---------|-------------|
| `contacts group list` | List contact groups (default store; `--all-stores` for every store) |
| `contacts group show` | Show a group and its members |
| `contacts group create` | Create a group (default Contacts folder) |
| `contacts group add` | Add members to a group |
| `contacts group remove` | Remove members from a group |
| `contacts group delete` | Delete a group (to Deleted Items, needs `--confirm YES`) |

### Recipients

- Addresses are cleaned before use: wrapping quotes (`'a@b.com'`) and `Name <a@b.com>` wrappers are removed, duplicates dropped.
- Contact group names (e.g. `--cc "Technical Team"`) are accepted wherever addresses are.
- `draft`, `forward` and `send` (new message) stop with `UNRESOLVED_RECIPIENTS` when Outlook cannot resolve a recipient; pass `--allow-unresolved` to save anyway.

### Replies

```bash
outlookctl draft --reply-to-id <id> --reply-to-store <store> --reply-all \
  --to "boss@example.com" --cc "Technical Team" --attach report.xlsx \
  --body-text "Dear Boss,
Please find the report attached."
```

New text is inserted above the quoted original, which keeps its HTML formatting. On replies `--to/--cc/--bcc` **replace** that recipient type (omit them to keep what Outlook filled in), and the `RE:` subject is kept unless `--subject` is given.

### Folders

`outlookctl folders` lists the folder tree of the default store, the one holding the default Inbox (mail folders only by default; `--type all|calendar|contacts|...`, `--store <name>` or `--all-stores`, `--depth N`). Each entry has a `folder_spec` you can pass straight to `--folder`.

`--folder by-name:<name>` and `--folder by-path:<path>` look in the default store; add `--all-stores` to look in every store. Prefix the path with a store name to pick a store: `by-path:me@example.com/Inbox/Projects`.

### Stores

Commands work on the **default store** (the account that holds the default Inbox) unless told otherwise:

- `--store "<store display name>"` picks one store (`folders`, `calendar calendars`, `contacts group ...`).
- `--all-stores` uses every store, default store first (`folders`, `list`/`search`/`move` with `by-name:`/`by-path:`, `calendar calendars`, `calendar list --calendar/--all`, `contacts group list|show|add|remove|delete`).
- A `by-path:` that starts with a store name always uses that store: `by-path:me@example.com/Inbox/Projects`.

Lookups that fail in the default store say so in the error and suggest `--all-stores`.

See [CLI Reference](https://gmickel.github.io/outlookctl/cli.html) for full documentation.

## Installing the Skill

The skill enables AI assistants (Claude Code, OpenAI Codex, or VS Code) to assist with email and calendar operations safely.

> **Note:** Agent Skills support in VS Code is currently in preview and only available in VS Code Insiders. Enable the `chat.useAgentSkills` setting to use Agent Skills.

### Claude Code - Personal Installation

```bash
uv run python tools/install_skill.py --personal
```

Installs to: `~/.claude/skills/outlook-automation/`

### Claude Code - Project Installation (for team)

```bash
uv run python tools/install_skill.py --project
```

Installs to: `.claude/skills/outlook-automation/`

### OpenAI Codex Installation

```bash
uv run python tools/install_skill.py --codex
```

Installs to: `~/.codex/skills/outlook-automation/`

> **Note:** Codex skills require the experimental `skills` feature flag. Add `[features]\nskills = true` to `~/.codex/config.toml` and restart Codex.

### Verify Installation

```bash
uv run python tools/install_skill.py --verify --personal  # Claude Code
uv run python tools/install_skill.py --verify --codex     # OpenAI Codex
```

## Safety Features

`outlookctl` is designed with safety as a priority:

1. **Draft-First Workflow** - Create drafts/meetings, review, then send
2. **Explicit Confirmation** - Sending emails/meeting invites requires `--confirm-send YES`
3. **Metadata by Default** - Body content only retrieved on explicit request
4. **Audit Logging** - Send operations logged to `%LOCALAPPDATA%/outlookctl/audit.log`

### Example Safe Workflow

```bash
# 1. Create draft
uv run python -m outlookctl.cli draft \
  --to "recipient@example.com" \
  --subject "Project Update" \
  --body-text "Here is the update..."

# 2. Review the draft in Outlook or via CLI

# 3. Send with explicit confirmation
uv run python -m outlookctl.cli send \
  --draft-id "<entry_id from step 1>" \
  --draft-store "<store_id from step 1>" \
  --confirm-send YES
```

## Output Format

All commands output JSON:

```json
{
  "version": "1.0",
  "folder": {"name": "Inbox"},
  "items": [
    {
      "id": {"entry_id": "...", "store_id": "..."},
      "subject": "Meeting Tomorrow",
      "from": {"name": "Jane", "email": "jane@example.com"},
      "unread": true,
      "has_attachments": false
    }
  ]
}
```

See [JSON Schema](https://gmickel.github.io/outlookctl/json-schema.html) for details.

## Project Structure

```
outlookctl/
├── pyproject.toml              # Project configuration (uv/hatch)
├── README.md                   # This file
├── CLAUDE.md                   # Development guide for AI assistants
├── src/outlookctl/             # Python package
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point (argparse)
│   ├── models.py               # Dataclasses for JSON output
│   ├── outlook_com.py          # COM automation wrapper
│   ├── safety.py               # Send confirmation gates
│   └── audit.py                # Audit logging
├── skills/
│   └── outlook-automation/
│       ├── SKILL.md            # Claude Code Skill definition
│       └── reference/          # Skill documentation
│           ├── cli.md
│           ├── json-schema.md
│           ├── security.md
│           └── troubleshooting.md
├── tools/
│   └── install_skill.py        # Skill installer
├── tests/                      # pytest test suite
│   ├── test_models.py
│   ├── test_calendar_models.py
│   └── test_safety.py
└── evals/                      # Skill evaluation scenarios
    ├── eval_summarize.md
    ├── eval_draft_reply.md
    └── eval_refuse_send.md
```

## Development

### Prerequisites

- Python 3.12+
- uv package manager
- Windows with Classic Outlook

### Setup

```bash
uv sync
```

### Run Tests

```bash
uv run python -m pytest tests/ -v
```

### Run CLI During Development

```bash
uv run python -m outlookctl.cli <command> [options]
```

### Update Skill After Changes

```bash
uv run python tools/install_skill.py --personal
```

## Technical Details

### Why COM Automation?

Windows COM (Component Object Model) is Microsoft's standard interface for inter-process communication. Outlook exposes its functionality through the `Outlook.Application` COM object, which:

- Is the same interface used by VBA macros inside Outlook
- Is how enterprise tools integrate with Outlook
- Runs in the security context of the logged-in user
- Is subject to Outlook's Trust Center settings

### Classic vs New Outlook

**Classic Outlook** (the traditional desktop app) supports COM automation.

**New Outlook** (the modern, web-based app) does **not** support COM automation - it requires Microsoft Graph API with OAuth authentication.

This tool only works with Classic Outlook. Check which version you have:
- Classic: Has File menu, Trust Center settings
- New: Toggle at top-right says "New Outlook"

### Security Model

- No API keys or tokens stored
- No network calls to external services
- Uses Windows authentication (your logged-in session)
- Outlook may show security prompts for programmatic access
- All operations logged locally for audit

## Limitations

- **Classic Outlook Only** - New Outlook requires Microsoft Graph API
- **Windows Only** - COM is a Windows technology
- **Same Session** - Must run in same Windows session as Outlook
- **Security Prompts** - Outlook may show security dialogs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Outlook COM unavailable" | Start Classic Outlook (not New Outlook) |
| "pywin32 not installed" | Run `uv sync` |
| "Message not found" | IDs expire; re-run list/search |
| Permission denied on CLI | Use `uv run python -m outlookctl.cli` instead |

See [Troubleshooting Guide](https://gmickel.github.io/outlookctl/troubleshooting.html) for more.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run python -m pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built for use with [Claude Code](https://claude.ai/code)
- Powered by [pywin32](https://github.com/mhammond/pywin32) for COM automation
- Package management via [uv](https://docs.astral.sh/uv/)
