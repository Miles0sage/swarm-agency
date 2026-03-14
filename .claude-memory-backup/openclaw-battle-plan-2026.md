---
name: openclaw-battle-plan-2026
description: What to steal from Devin/Manus/Bolt/Cursor, build order, pricing
type: reference
---

# OpenClaw Battle Plan 2026

## What to Steal (Ranked by Impact)

### From Bolt (Lightning Speed)
- Streaming responses + progressive rendering
- Edge compute for instant feedback
- Hot reload for multi-step workflows
- Checkpoint-restore (git states)

### From Cursor (UX/IDE)
- Inspector mode (click to select code)
- In-editor AI explanations
- Command palette
- Inline edits with acceptance gates

### From Devin (Reliability)
- Task checkpoints (save state between steps)
- Browser automation with visual feedback
- Error recovery with context window
- Subtask delegation

### From Manus (Control)
- Slider-based confidence thresholds
- Human approval gates on risky actions
- Undo/rewind workflows
- Detailed execution logs

## Build Order (14 Days)
**Days 1-3: Sports Odds Pipeline**
- Ingest from 200+ sportsbooks
- Real-time line movement detection
- XGBoost prediction model
- Live odds comparison

**Days 4-6: Arbitrage Detection**
- Polymarket + Kalshi cross-matching
- Mispricing (YES+NO != $1) alerts
- Optimal stake calculator
- Whale activity tracker

**Days 7-9: Betting Safety Layer**
- Dry-run by default
- Kill switch (emergency pause)
- Position limits per market
- Audit trail + P&L tracking

**Days 10-12: Multi-Agent Orchestration**
- Parallel prediction jobs
- Smart routing (Opus for complex, Sonnet for simple)
- Fallback to local Ollama
- Session state persistence

**Days 13-14: Demo + Documentation**
- 5 recorded use case videos
- API documentation
- Pricing tier validation

## Pricing Tiers

**Free**
- 5 sports predictions/day
- Public Polymarket data
- 24-hour data retention

**Pro ($29/mo)**
- Unlimited predictions
- Real-time odds feeds
- Arbitrage alerts
- API access (100 req/day)
- Email digests

**Enterprise (Custom)**
- Private sportsbook feeds
- Dedicated agent instance
- White-label API
- Custom sports models

## Key Integrations
- **Sportsbooks**: The Odds API (200+ books)
- **Prediction**: Polymarket, Kalshi
- **LLM**: Claude Opus (Sonnet fallback)
- **Local**: Ollama Qwen 2.5 Coder 7B
- **Data**: Redis (cache), Supabase (persistence)

## Not Doing
- Full IDE integration (focus on web UI)
- GitHub OAuth (API keys only, auth.js later)
- Mobile app (web-responsive)
- Multi-user workspaces
