---
name: Disaster Prevention Guide
description: How to prevent another Cursor git clean wipe. Rules for VPS file safety.
type: critical
last_updated: 2026-03-13
---

# Disaster Prevention Guide

## What Happened (March 13, 2026)

Cursor was opened on `/root/` which was a git repo (Create Next App). Cursor's Source Control UI ran `git clean -fd`, permanently deleting ALL untracked files:
- ~200 research/planning .md docs
- All .env files (secrets, API keys)
- All .mcp.json configs
- Project folders not tracked by git
- Memory files (recovered from context)

Only git-tracked files survived (13 Next.js configs from the initial commit).

## Prevention Rules

### Rule 1: NEVER open /root/ as a project in Cursor
- `/root/` should NOT be a git repo
- If it becomes one accidentally, run `rm -rf /root/.git` immediately
- Only open specific project folders (e.g., `/root/openclaw/`, `/root/edgeboard/`)

### Rule 2: Keep .env files backed up
- After creating/updating any .env, immediately back up:
  ```bash
  cp /root/openclaw/.env /root/.claude/projects/-root/memory/.env-openclaw-backup
  ```
- NEVER commit .env to public repos, but DO keep encrypted backups
- Consider: `gpg -c /root/openclaw/.env` → store encrypted version in private repo

### Rule 3: Memory files are git-backed
- Memory repo: `Miles0sage/claude-memory` (private)
- After significant memory updates, commit + push
- Auto-backup: `/root/claude-memory-backup-*.tar.gz`

### Rule 4: Cursor "Discard All Changes" = nuclear
- In Cursor's Source Control panel, "Discard All Changes" / "Clean All" runs `git clean -fd`
- This PERMANENTLY deletes all untracked files with NO recovery
- NEVER use this on a repo that has important untracked files

### Rule 5: Important configs to back up
- `/root/openclaw/.env` — all API keys and secrets
- `/root/.mcp.json` — MCP server configs for Claude Code
- `/root/.claude/settings.local.json` — auto-approve permissions
- `/root/openclaw-assistant/.env` — PA worker secrets
- `~/.notebooklm/storage_state.json` — NotebookLM auth

### Rule 6: Check before opening Cursor on VPS
- Run `git status` in the directory first
- If there are 100+ untracked files, that's a red flag
- Either .gitignore them or move them to a non-git directory
