---
name: Claude Code Full Setup (Post-Wipe Recovery)
description: Complete Claude Code environment setup after March 13 wipe — all configs, agents, commands, skills, MCP servers, token optimization
type: project
---

## Claude Code Setup — COMPLETE (2026-03-13)

Everything restored and configured. User must restart Claude Code to activate.

### What Was Installed
- **everything-claude-code** repo cloned to `/root/everything-claude-code/`
- **12 agents** installed to `/root/.claude/agents/` (planner, architect, tdd-guide, code-reviewer, security-reviewer, build-error-resolver, e2e-runner, refactor-cleaner, database-reviewer, python-reviewer, loop-operator, doc-updater)
- **48 slash commands** installed to `/root/.claude/commands/` (plan, tdd, code-review, build-fix, e2e, refactor-clean, save-session, resume-session, orchestrate, loop-start, quality-gate, etc.)
- **17 skills** installed to `/root/.claude/skills/`
- **Rules** installed to `/root/.claude/rules/` (common, python, typescript)

### Token Optimization Applied
- `MAX_THINKING_TOKENS=10000` in settings.local.json (saves ~70% vs default 31,999)
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` (compact at 50% context, not 80%)
- `/root/.claudeignore` excludes node_modules, build artifacts, media, lock files
- Ultrathink keywords: "think" (routine), "megathink" (design), "ultrathink" (hard problems)

### MCP Servers (9 configured in /root/.mcp.json)
openclaw, perplexity, github, memory, sequential-thinking, context7, playwright, firecrawl, cloudflare-docs

### API Keys Restored (/root/openclaw/.env)
All keys restored EXCEPT:
- **Bailian/DashScope** — still placeholder, needs key from https://dashscope.console.aliyun.com/api-keys
- **Mystery key** `sb_publishable_BBmdx-n0abPdJN_-LtSg-w_IY_IZbW6` — likely Stripe publishable, saved as comment

### Permissions
All tools auto-approved in `/root/.claude/settings.local.json` including all MCP server wildcards.

**Why:** Disaster recovery after `git clean -fd` wiped all configs on March 13, 2026.
**How to apply:** Setup is done. If anything breaks, check these paths first. Token optimization settings are in settings.local.json env block.
