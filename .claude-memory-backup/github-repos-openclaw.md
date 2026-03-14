---
name: GitHub Repos - OpenClaw Ecosystem
description: All OpenClaw-related repos, their status, and relationships
type: reference
---

# OpenClaw GitHub Repositories - Ecosystem Analysis

Last updated: March 13, 2026

---

## 1. Miles0sage/openclaw (Main Project - PRIVATE)

### Description & Purpose
Production-grade multi-agent autonomous job pipeline. Routes tasks through specialized AI agents, executes with 75+ tools, and delivers results with cost tracking.

**License**: MIT
**Status**: ACTIVE & PRODUCTION

### Key Features
- Multi-agent autonomous job pipeline
- 75+ integrated tools (file ops, git, code execution, API calls)
- Task decomposition and routing to specialized agents
- Cost tracking and attribution
- Job execution engine with result verification

### v5 Features (Recent)
- **Simulation Sandbox**: 3-agent debate loop validates plans before execution
- **JSON Agent Registry**: Define agents via JSON without touching Python code
- **Cost Dashboard API**: Detailed JSON endpoints for per-agent and per-project cost tracking
- **Docker Compose**: 5-minute self-hosted deployment
- **DAG Execution**: Sub-tasks run in parallel for 3x speedup

### Tech Stack
- **Runtime**: Python 3.11+
- **Dependencies**: Supabase (free tier works), multiple LLM API keys
- **Supported LLMs**: Claude, Gemini, Kimi/DeepSeek, Bailian
- **Deployment**: Docker Compose or Local

### Key Files (Expected)
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template
- `gateway.py` - Main gateway entry point
- Docker Compose configuration

### Current State
**Active Production System**
- Running on VPS at 152.53.55.207:18789
- Multiple workers (AI CEO, PA, Researcher)
- 190+ tests, 97% benchmark success (105 jobs, $7.30)
- Cost tracking fully operational
- Daily active use for internal task execution

### Relationships
- **Parent repo**: Main monolith serving multiple purposes
- **Consumes**: openclaw-agents (multi-agent framework)
- **Provides**: Core job execution engine to PA and assistant
- **Interfaces**: openclaw-web-ui (Cloudflare proxy)

---

## 2. Miles0sage/openclaw-agents (Multi-Agent Framework - PUBLIC)

### Description & Purpose
Multi-agent AI framework with 75+ tools and 12 specialist agents. Routes tasks intelligently across specialized agents (CodeGen, Security, Testing, Research, etc.) and delivers working code.

**License**: MIT
**Status**: ACTIVE & MAINTAINED

### Key Features
- 12 specialized agents with different capabilities
- 75+ integrated tools
- Priority job routing system
- Reflexion quality gates (validation loops)
- 4-tier LLM fallback mechanism
- Task decomposition and execution

### Tech Stack
- **Language**: TypeScript/Python
- **Runtime**: Python 3.11+
- **Database**: Supabase
- **LLM Support**: Claude, Gemini, DeepSeek, Bailian
- **Deployment**: Local or Docker

### Quick Start
```bash
git clone https://github.com/Miles0sage/openclaw-agents.git
cd openclaw-agents
pip install -r requirements.txt
cp .env.example .env
python gateway.py
```

### Key Endpoints
- `POST /api/job/create` - Create new job
- `GET /health` - Health check

### Current State
**Active & Public**
- Open source for community use
- Public documentation and examples
- Actively maintained with task routing improvements
- Used as foundation for all OpenClaw services

### Relationships
- **Foundation**: Core multi-agent framework used by openclaw
- **Provides**: Agent routing, task decomposition, tool execution
- **Used by**: Main openclaw repo, PA worker, assistant services
- **Sits below**: openclaw-web-ui and gateway services

---

## 3. Miles0sage/openclaw-assistant (Assistant - PRIVATE)

### Description & Purpose
Personal AI assistant layer running on own devices. Answers on multiple channels (WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, Teams) with extension channels (BlueBubbles, Matrix, Zalo).

**Status**: ACTIVE & PRODUCTION

### Key Features
- Multi-channel communication (9+ platforms)
- Voice support on macOS/iOS/Android
- Live Canvas rendering
- Gateway control plane
- Local fast execution
- Always-on operation
- Single-user focus

### Tech Stack
- **Runtime**: Node.js ≥22
- **Language**: TypeScript
- **Supported Models**: Claude Pro/Max (recommended Opus 4.6), ChatGPT/Codex
- **LLM Auth**: OAuth (Anthropic, OpenAI)

### Recommended Setup
- Claude Pro/Max (100/200 tokens)
- Opus 4.6 for long-context strength
- Onboarding wizard: `openclaw onboard`

### Key Files (Expected)
- Channel connectors (Telegram, Slack, Discord, etc.)
- Voice/speech modules
- Canvas rendering engine
- Model failover/rotation logic

### Current State
**Active Production**
- Running as personal assistant for Miles0sage
- Connected to multiple communication channels
- Integrated with OpenClaw gateway
- Daily use with multiple users/channels

### Relationships
- **Consumer**: Uses openclaw job engine for task execution
- **Layer**: Sits above openclaw-agents framework
- **Provides**: User interface and communication layer
- **Integrates**: With openclaw gateway for job routing

---

## 4. Miles0sage/openclaw-web-ui (Web UI / Proxy Worker - PRIVATE)

### Description & Purpose
Secure token-based proxy worker for accessing OpenClaw gateway endpoints. Cloudflare Workers-based authentication layer.

**Status**: ACTIVE & DEPLOYED

### Key Features
- Token-based authentication (X-Auth-Token header or query param)
- CORS headers for cross-origin requests
- Transparent proxying to OpenClaw gateway
- Error handling and status reporting
- GET and POST support

### Tech Stack
- **Platform**: Cloudflare Workers
- **Build Tool**: Wrangler CLI
- **Runtime**: Node.js
- **Language**: JavaScript/TypeScript

### Deployment
- **Live URL**: https://openclaw-ui.amit-shah-5201.workers.dev
- **Target Gateway**: 152.53.55.207:18789
- **Provider**: Cloudflare Workers

### Authentication Methods
1. **Header** (Recommended): `X-Auth-Token: <token>`
2. **Query Parameter**: `?token=<token>`

### Setup
```bash
npm install -g wrangler
wrangler secret put AUTH_TOKEN
wrangler deploy
```

### Current State
**Active & Deployed**
- Live on Cloudflare edge network
- Proxying requests to main gateway
- Token authentication active
- Handles cross-domain requests

### Relationships
- **Interface Layer**: Sits between frontend and openclaw gateway
- **Proxies**: Requests to 152.53.55.207:18789
- **Security**: Provides token-based access control
- **Deployment**: Cloudflare edge deployment

---

## 5. Miles0sage/overseerclaw-worker (DOESN'T EXIST)

**Status**: NOT FOUND

The repository `Miles0sage/overseerclaw-worker` does not exist. This may be:
- Renamed or deleted
- Misspelled (check for similar names)
- A planned repo not yet created

**Possible Alternatives**:
- Related worker code may be in `openclaw` repo under a workers/ directory
- Could be integrated into `openclaw-agents`
- May exist under different owner or name

---

## Ecosystem Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   openclaw-assistant                         │
│            (Multi-channel communication layer)              │
│   Slack, Discord, Telegram, WhatsApp, Teams, etc.          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   openclaw-web-ui                           │
│      (Cloudflare Workers proxy + auth layer)                │
│   152.53.55.207:18789 ◄─ openclaw-ui.amit-shah.workers.dev │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     openclaw                                │
│         (Production job execution gateway)                  │
│   • Cost dashboard API                                      │
│   • Job routing & execution                                 │
│   • 190+ tests, 97% success rate                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 openclaw-agents                             │
│       (Multi-agent framework + tool execution)              │
│   • 12 specialized agents                                   │
│   • 75+ tools (file, git, code, API)                        │
│   • Reflexion gates & 4-tier LLM fallback                   │
│   • Public open-source foundation                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Technologies Across Repos

| Technology | Usage | Repos |
|---|---|---|
| Python 3.11+ | Agent execution, job routing | openclaw, openclaw-agents |
| TypeScript | Web/assistant layers | openclaw-assistant, openclaw-web-ui |
| Node.js ≥22 | Runtime for assistant and web | openclaw-assistant, openclaw-web-ui |
| Docker Compose | Deployment | openclaw, openclaw-agents |
| Supabase | Database/backend | openclaw, openclaw-agents |
| Cloudflare Workers | Edge deployment | openclaw-web-ui |
| Claude/Gemini/DeepSeek | LLM backends | All repos |
| Git/GitHub API | Task routing | openclaw, openclaw-agents |

---

## Current Status Summary

| Repo | Status | Version | Activity | Public/Private |
|---|---|---|---|---|
| openclaw | ✅ ACTIVE PRODUCTION | v5 | Daily use (190+ tests) | Private |
| openclaw-agents | ✅ ACTIVE MAINTAINED | v5 | Ongoing development | Public |
| openclaw-assistant | ✅ ACTIVE PRODUCTION | Current | Daily multi-channel | Private |
| openclaw-web-ui | ✅ ACTIVE DEPLOYED | Current | Live on Cloudflare | Private |
| overseerclaw-worker | ❌ NOT FOUND | N/A | N/A | N/A |

---

## Key Insights

### Strengths
1. **Layered Architecture**: Clean separation between framework, execution, and interfaces
2. **Production Ready**: Running live with cost tracking and 97% success rate
3. **Open Source Foundation**: openclaw-agents is public; others leverage it
4. **Multi-LLM Support**: 4-tier fallback (Claude → Gemini → DeepSeek → Bailian)
5. **Edge Deployment**: Cloudflare Workers for global accessibility

### Current Bottlenecks
1. **overseerclaw-worker** doesn't exist (may need creation or recovery)
2. **Private repos** limit community contributions
3. **Version coordination** across 4 active repos

### Recommended Next Steps
1. Locate or recreate overseerclaw-worker
2. Document integration points between repos
3. Consider versioning strategy for shared dependencies
4. Add cross-repo CI/CD testing
5. Monitor cost tracking (currently $7.30 for 105 jobs)

---

## Repository Links

- **Main Repo**: https://github.com/Miles0sage/openclaw
- **Agent Framework**: https://github.com/Miles0sage/openclaw-agents
- **Assistant**: https://github.com/Miles0sage/openclaw-assistant
- **Web UI**: https://github.com/Miles0sage/openclaw-web-ui
- **Missing**: openclaw-worker (investigate)

---

**Sources**:
- `gh repo view` output (direct GitHub API)
- README files from public repos
- VPS deployment status from memory files
- Architecture documented in openclaw-architecture.md
