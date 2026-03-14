# Claude Code Memory -- Index

> Concise index. Detailed info in topic files linked below.

---

## AI Factory (March 13, 2026) — START HERE FOR CODING
- **[ai-factory-stack-guide.md](ai-factory-stack-guide.md)** -- **MASTER GUIDE**: All agents, what they're good at, task assignment rules, error patterns, budget management
- **[feedback_use_ai_factory.md](feedback_use_ai_factory.md)** -- CRITICAL: Use AI Factory for grunt work, NEVER OpenClaw MCP. CLI: `python3 /root/ai-factory/factory.py alibaba "prompt"`
- **Repo:** github.com/Miles0sage/ai-factory (private) | **Path:** /root/ai-factory/
- **Workers:** Claude Code Opus ($200), Codex GPT-5 ($20), Alibaba 7-model ($10), MiniMax M2.5 ($10) = $240/mo
- **Dashboard:** `python /root/ai-factory/dashboard.py` → port 8899
- **MiniMax key needed:** Get from platform.minimax.io → API Keys → Create Coding Plan Key

## DISASTER RECOVERY (March 13, 2026)
- **[disaster-prevention-guide.md](disaster-prevention-guide.md)** -- How to prevent another Cursor git clean wipe. NEVER open /root/ in Cursor.
- **[secrets-recovery-checklist.md](secrets-recovery-checklist.md)** -- ALL API keys/secrets that Miles must re-enter. Full checklist with URLs.
- **[openclaw-iteration-history.md](openclaw-iteration-history.md)** -- Complete v1-v5 development timeline recovered from git commits

## RESOLVED BLOCKERS (March 13, 2026)
- ~~[CRITICAL] .env FILES~~ -- **RESTORED**. All API keys back in /root/openclaw/.env (except Bailian placeholder)
- ~~[HIGH] .mcp.json~~ -- **RESTORED**. 9 MCP servers configured
- **[CRITICAL] EdgeBoard Dashboard Source Missing** -- Must recover OR rebuild. [TASK-EDGEBOARD-RECOVERY.md](TASK-EDGEBOARD-RECOVERY.md)
- **[HIGH] GWS OAuth Incomplete** -- Gmail/Calendar/Drive blocked. [TASK-GWS-OAUTH-SETUP.md](TASK-GWS-OAUTH-SETUP.md)
- **[LOW] Bailian API key** -- Still placeholder, needs key from DashScope console

## Claude Code Setup
- [claude-code-setup-complete.md](claude-code-setup-complete.md) -- Full setup: 12 agents, 48 commands, 17 skills, 9 MCP servers, token optimization

**What works:** gh CLI, Cloudflare tunnel, gateway (systemd), all API keys, full Claude Code toolkit

---

## Active Builds (March 14, 2026)
- **[swarm-agency-status.md](swarm-agency-status.md)** -- **SHIPPED**: 43 agents, 10 depts, 136 tests, CLI+SDK+Web. Path: `/root/swarm-agency/`, repo: Miles0sage/swarm-agency
- [edgeboard-dashboard-status.md](edgeboard-dashboard-status.md) -- EdgeBoard betting dashboard: all code written, needs build verification (OOM fix)
- [mirofish-clone-status.md](mirofish-clone-status.md) -- MiroFish AI prediction engine: clone + English translation in progress

## Revenue & Monetization
- [prediction-market-passive-income-plan.md](prediction-market-passive-income-plan.md) -- 3 paths to passive income (sports +EV, prediction bonds, picks-as-a-service), 7-day revenue plan
- [openclaw-action-plan-march2026.md](openclaw-action-plan-march2026.md) -- 14-day action plan, 4 parallel tracks, daily schedule
- [openclaw-2week-revenue-plan.md](openclaw-2week-revenue-plan.md) -- UPDATED: Self-fund via sports betting, steal GitHub UI, agent improvements

## Strategy & Competitive (START HERE)
- [openclaw-strategy-synthesis-2026.md](openclaw-strategy-synthesis-2026.md) -- **START HERE**: 1-workflow focus, brutal timeline, Moltbook context, competitive matrix, next moves
- [openclaw-battle-plan-2026.md](openclaw-battle-plan-2026.md) -- What to steal from Devin/Manus/Bolt/Cursor, build order, pricing
- [openclaw-competitive-analysis-2026.md](openclaw-competitive-analysis-2026.md) -- 8 unique moats, competitor gaps, top 5 features
- [openclaw-one-pager-2026.md](openclaw-one-pager-2026.md) -- Competitive matrix, positioning, pricing tiers
- [openclaw-commercialization-tactics-2026.md](openclaw-commercialization-tactics-2026.md) -- 90-day GTM playbook, outreach, demo scripts

## Active Plan (March 12-26, 2026)
- [openclaw-action-plan-march2026.md](openclaw-action-plan-march2026.md) -- **ACTIVE NOW**: 4 tracks (demos, sports agency, monolith split, NotebookLM additions), daily schedule

## v5 Build Plan (COMPLETE)
- [openclaw-v5-7day-blitz.md](openclaw-v5-7day-blitz.md) -- v5 COMPLETE: 119+ tests, all 6 components built
- [openclaw-v5-battle-plan-revised.md](openclaw-v5-battle-plan-revised.md) -- Gap analysis 60/100, what to steal/skip, competitive positioning
- [openclaw-v5-master-plan.md](openclaw-v5-master-plan.md) -- Original 3 additions plan (registry, sandbox, GraphRAG -- GraphRAG DROPPED)
- [speed-build-research-2026.md](speed-build-research-2026.md) -- Parallel agents 2x speedup, case studies, stack distribution

## Architecture & Technical
- [openclaw-architecture.md](openclaw-architecture.md) -- OpenClaw v4.2 components, gateway, PA worker, session logs
- [v4.2-roadmap.md](v4.2-roadmap.md) -- v4.2 plan: PA tools, plugins, scientific skills
- [error-patterns.md](error-patterns.md) -- Hard-won debugging lessons (NEVER repeat)
- [openclaw-runner-bugs.md](openclaw-runner-bugs.md) -- Runner bug patterns
- [openclaw-next-steps.md](openclaw-next-steps.md) -- Technical next steps

## AI Agent Research
- [ai-agent-builder-patterns-2026.md](ai-agent-builder-patterns-2026.md) -- 6-question research on tools, self-improvement, founder stories
- [ai-agency-landscape-2026.md](ai-agency-landscape-2026.md) -- $8.5B market, pricing, stacks, trending repos
- [ai-ceo-strategy-2026.md](ai-ceo-strategy-2026.md) -- Moats, OSS business models, defensible position
- [autonomous-agents-research.md](autonomous-agents-research.md) -- Self-improving agents, reflexion, dynamic tool creation
- [self-improving-agents-research.md](self-improving-agents-research.md) -- DSPy recommended, cognee debunked, swarm-agency build plan (NOW SHIPPED → see swarm-agency-status.md)
- [big-tech-agent-patterns.md](big-tech-agent-patterns.md) -- Leaked prompts analysis, identity anchoring, PRMs
- [leaked-prompts-error-patterns.md](leaked-prompts-error-patterns.md) -- Error recovery from 30+ leaked AI agent prompts
- [ai-system-prompts-research.md](ai-system-prompts-research.md) -- 25+ AI tool system prompts analysis

## Alibaba Cloud / DashScope
- [dashscope-qwen-integration-guide.md](dashscope-qwen-integration-guide.md) -- Full integration guide: API endpoints, models, pricing, OpenAI-compatible SDK, free tier, MCP support, OpenClaw config

## Coding Tools & Infrastructure
- [free-coding-tools-2026.md](free-coding-tools-2026.md) -- Gemini CLI, Goose, OpenCode, Aider, Ollama
- [ai-coding-stack-guide-2026.md](ai-coding-stack-guide-2026.md) -- Full stack: Claude Code + Codex + Gemini + Aider
- [tool-stack-strategy-2026.md](tool-stack-strategy-2026.md) -- Claude Max + Cursor + Copilot, 6 gaps
- [automation-blueprint-2026.md](automation-blueprint-2026.md) -- Ollama local, OpenRouter, Claude headless
- [ai-coding-automation-research-2026.md](ai-coding-automation-research-2026.md) -- Headless coding agents, 4-week build plan
- [ollama-gpu-setup.md](ollama-gpu-setup.md) -- RTX 4060, Tailscale VPN, Qwen 2.5 Coder 7B
- [mcp-servers-installed.md](mcp-servers-installed.md) -- 7 MCP servers (Twitter, Reddit, Slack, etc.)

## Claude Code
- [everything-claude-code.md](everything-claude-code.md) -- Token optimization, subagents, hooks
- [claude-code-quick-wins.md](claude-code-quick-wins.md) -- Worktrees, skills, /compact, ultrathink
- [claude-code-remote-sessions.md](claude-code-remote-sessions.md) -- Remote, cloud, headless, Agent SDK

## PA & Operations
- [pa-agent-build-order.md](pa-agent-build-order.md) -- Week-by-week PA build order
- [tool-patterns-reference.md](tool-patterns-reference.md) -- Tool hierarchy, design patterns, testing
- [personal-assistant-plan-status.md](personal-assistant-plan-status.md) -- PA plan status
- [ai-agency-pa-operations.md](ai-agency-pa-operations.md) -- PA "Holy 7" capabilities, automations
- [pa-full-life-automation-2026.md](pa-full-life-automation-2026.md) -- 8-domain life automation
- [pa-deploy-status.md](pa-deploy-status.md) -- PA deploy, gws setup, pending auth
- [agency-implementation-plan.md](agency-implementation-plan.md) -- Agency implementation plan

## Projects
- [projects.md](projects.md) -- Barber CRM, Delhi Palace, PrestressCalc, Concrete Canoe
- [notion-setup.md](notion-setup.md) -- Notion API token, page/DB IDs
- [business-strategy.md](business-strategy.md) -- Stripe, commercialization, cost optimization
- [prestresscalc-status.md](prestresscalc-status.md) -- 1597 tests, Phase A-G, 29 section types
- [prestresscalc-gap-analysis.md](prestresscalc-gap-analysis.md) -- Commercial comparison, ~90% Eriksson parity
- [prestresscalc-research-findings.md](prestresscalc-research-findings.md) -- FHWA/TxDOT/FDOT examples
- [concrete-canoe-status.md](concrete-canoe-status.md) -- Concrete canoe project status
- [twitter-ai-news-plan.md](twitter-ai-news-plan.md) -- Twitter AI news automation
- [barber-crm-phase3-plan.md](barber-crm-phase3-plan.md) -- Barber CRM phase 3
- [barber-crm-vapi.md](barber-crm-vapi.md) -- Barber CRM AI receptionist

## Market Research (Fresh)
- [perplexity-ai-landscape-march2026.md](perplexity-ai-landscape-march2026.md) -- March 2026: $7.8B->$52B market, AgentX leads, multi-agent wins, CrewAI surging

## LLM Providers
- [dashscope-qwen-integration-guide.md](dashscope-qwen-integration-guide.md) -- Alibaba DashScope/Qwen API: pricing, endpoints, code examples, OpenClaw integration, 20-35x cheaper than GPT-4o

## Misc Research
- [local-coder-mcp.md](local-coder-mcp.md) -- Opus delegates to Aider+Ollama
- [oz-capabilities.md](oz-capabilities.md) -- Warp Oz CLI (DISABLED)
- [opensandbox-research.md](opensandbox-research.md) -- Alibaba OpenSandbox
- [airi-research.md](airi-research.md) -- AIRI: NOT suitable as PA
- [copaw-shannon-prompt-research.md](copaw-shannon-prompt-research.md) -- CoPaw, Shannon, Prompt.ai
- [claude-scientific-skills-research.md](claude-scientific-skills-research.md) -- K-Dense scientific skills
- [awesome-claude-code-research.md](awesome-claude-code-research.md) -- Curated lists, top plugins
- [notebooklm-obsidian-research.md](notebooklm-obsidian-research.md) -- NotebookLlama, Obsidian MCP
- [skill-graphs-research.md](skill-graphs-research.md) -- Skill graph research
- [polymarket-trading-research.md](polymarket-trading-research.md) -- Polymarket trading research
- [prestresscalc-competitive-analysis.md](prestresscalc-competitive-analysis.md) -- PrestressCalc competitors

## Feedback
- [feedback_restart_for_permissions.md](feedback_restart_for_permissions.md) -- Must restart Claude Code after settings.local.json changes
- [feedback_notebooklm_auth.md](feedback_notebooklm_auth.md) -- NotebookLM auth keeps disappearing
- [feedback_ship_use_cases.md](feedback_ship_use_cases.md) -- Ship use cases & demos BEFORE more architecture work
- [feedback_delegate_task_files.md](feedback_delegate_task_files.md) -- Create TASK-*.md files only, Miles runs Codex/Gemini manually

---

## OpenClaw Quick Status
- **Version:** v4.2 | **Path:** `/root/openclaw/` | **VPS:** 152.53.55.207:18789
- **Gateway:** `systemctl restart openclaw-gateway` | **Domains:** gateway/dashboard/pa.overseerclaw.uk
- **Workers:** AI CEO (assistant.overseerclaw.uk) + PA (pa.overseerclaw.uk) + Researcher (Kimi 2.5)
- **Dual-AI Factory:** Claude Code (Opus 4.6, Max $200/mo) + Codex CLI (GPT-5, Plus $20/mo)
- **Free Tools:** Aider, Gemini CLI, Goose, OpenCode -- all headless on VPS
- **190+ tests** | **97% benchmark success** (105 jobs, $7.30)
- **ProcessTracker:** phases_completed, models_used, execution_timeline all working (fixed 2026-03-11)
- See [openclaw-architecture.md](openclaw-architecture.md) for full details

## User Preferences (Miles)
- Action-first, typo-tolerant, direct. Ship fast, iterate, MVP mentality
- NOT a tech person -- has vision, wants Claude to make technical decisions
- Cost-aware ($200/mo Max Plan). Parallel agents for speed. Auto-approve when away
- **Schedule**: 5pm-10pm Tue-Sun, Monday OFF. Soccer Thursdays ~9:20pm
- [user-devices.md](user-devices.md) -- Work MacBook (8GB, VS Code+SSH), Home Windows (32GB, Cursor), VPS details

## Delegation
- [feedback_delegate_task_files.md](feedback_delegate_task_files.md) -- Create TASK-*.md files only, Miles runs Codex/Gemini manually

## Key Feedback
- [feedback_ship_use_cases.md](feedback_ship_use_cases.md) -- Ship use cases & demos BEFORE more architecture work
- [feedback_delegate_task_files.md](feedback_delegate_task_files.md) -- Create TASK-*.md files only, Miles runs Codex/Gemini manually

## Behavior Rules
- Make decisions -- don't ask, just do if clearly needed
- Run in parallel whenever possible
- Add tools to ALL layers (gateway + MCP + PA). Commit after significant work
- Restart gateway via systemd. Test features after building them
- See [error-patterns.md](error-patterns.md) for pitfalls
