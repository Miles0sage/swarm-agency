---
name: Secrets & Config Recovery Checklist
description: All API keys, .env vars, and configs that need to be restored after the March 13 wipe
type: critical
last_updated: 2026-03-13
status: NEEDS_USER_ACTION
---

# Secrets & Config Recovery Checklist

ALL .env files were wiped. Miles needs to re-enter API keys. This is the full list.

## Status Key
- LOST = was set before, now gone, Miles must re-enter
- MISSING = was never set up (blocked before wipe too)
- OK = still working / not affected

## 1. OpenClaw Gateway (.env at /root/openclaw/.env)

Copy template first: `cp /root/openclaw/.env.example /root/openclaw/.env`

| Variable | Status | Where to get it |
|----------|--------|-----------------|
| ANTHROPIC_API_KEY | LOST | https://console.anthropic.com/account/keys |
| SUPABASE_URL | LOST | https://supabase.com → project settings → API |
| SUPABASE_KEY | LOST | Same page → Service Role key |
| DEEPSEEK_API_KEY | LOST | https://platform.deepseek.com/api_keys |
| MINIMAX_API_KEY | LOST | https://www.minimaxi.com/user-center/api-keys |
| BAILIAN_API_KEY | LOST | https://dashscope.console.aliyun.com/api-keys |
| GEMINI_API_KEY | LOST | https://aistudio.google.com/apikey |
| PERPLEXITY_API_KEY | LOST | https://www.perplexity.ai/api |
| TELEGRAM_BOT_TOKEN | LOST | @BotFather on Telegram |
| SLACK_BOT_TOKEN | MISSING | Was never configured |
| GITHUB_TOKEN | LOST | gh auth token (may still be in gh CLI config) |
| OPENAI_API_KEY | LOST | https://platform.openai.com/api-keys |
| ODDS_API_KEY | LOST | https://the-odds-api.com |
| KALSHI_API_KEY_ID | LOST | Kalshi dashboard |
| KALSHI_PRIVATE_KEY_PATH | LOST | Was at ./data/trading/kalshi_private.pem |
| UPSTASH_REDIS_REST_URL | LOST | https://console.upstash.com |
| UPSTASH_REDIS_REST_TOKEN | LOST | Same dashboard |
| PORT | default 18789 | Hardcoded |
| GATEWAY_AUTH_TOKEN | LOST | Generate: `openssl rand -hex 32` |

## 2. OpenClaw Assistant PA (.env at /root/openclaw-assistant/.env)

| Variable | Status | Notes |
|----------|--------|-------|
| All PA env vars | LOST | Needs same Supabase + Anthropic keys, plus GWS creds |
| GMAIL_CREDENTIALS | MISSING | Was never set up (GWS OAuth blocker) |
| GOOGLE_CALENDAR_CREDENTIALS | MISSING | Same |
| GOOGLE_DRIVE_CREDENTIALS | MISSING | Same |
| NOTION_API_TOKEN | MISSING | Was never added |

## 3. .mcp.json (was at /root/.mcp.json)

| MCP Server | Status | Notes |
|------------|--------|-------|
| Twitter/X | LOST | Need API keys |
| Reddit | LOST | Need OAuth credentials |
| Slack | MISSING | Was never configured |
| GitHub | LOST | Uses gh CLI token |
| Gmail | MISSING | Blocked on GWS OAuth |
| Google Drive | MISSING | Blocked on GWS OAuth |
| Perplexity | LOST | Need API key |

## 4. Other Configs

| Config | Status | Notes |
|--------|--------|-------|
| ~/.claude/settings.local.json | OK | Still intact (not in /root/ git) |
| gh CLI auth | OK | Still authenticated as Miles0sage |
| Cloudflare tunnel | OK | systemd service still running |
| NotebookLM storage_state.json | LOST | Was already broken before wipe |
| Ollama | OK | Runs on home PC, not VPS |

## 5. Systemd Services Status

| Service | Status | Notes |
|---------|--------|-------|
| openclaw-gateway | RUNNING | But .env missing so likely erroring |
| openclaw-watchdog | RUNNING | Same |
| openclaw-worker-p2 | RUNNING | Same |
| openclaw.service | FAILED | Needs .env |
| cloudflared-tunnel | RUNNING | OK |

## Quick Recovery Steps

1. Miles: Log into each API dashboard and copy keys
2. Create /root/openclaw/.env from .env.example
3. Paste all keys
4. `systemctl restart openclaw-gateway`
5. Recreate /root/.mcp.json (I can generate the template once keys are ready)
6. Create /root/openclaw-assistant/.env
7. Back up: `cp /root/openclaw/.env /root/.claude/projects/-root/memory/.env-backup-encrypted`

## What I (Claude) Still Know

- Full OpenClaw architecture (54KB doc in memory)
- Complete iteration history v1→v5 (800 lines)
- All agent souls and routing rules (from CLAUDE.md in repo)
- Competitive analysis, strategy, battle plans
- All GitHub repo structures (18 repos documented)
- Build order, what worked, what failed
- User preferences, schedule, workflow

## What Was Lost Forever

- ~200 loose .md research/planning docs in /root/ (never committed)
- Exact .env values (API keys) — Miles must re-enter from dashboards
- .mcp.json exact config — can be regenerated from template
- Some session-specific context from older conversations
