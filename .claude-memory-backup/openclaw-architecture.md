---
title: OpenClaw v4.2+ Architecture
version: "4.2"
last_updated: "2026-03-13"
status: "Production"
vps_endpoint: "152.53.55.207:18789"
---

# OpenClaw Architecture Documentation

## System Overview

OpenClaw is a **multi-agent AI orchestration platform** that decomposes complex tasks into parallel workflows, routes them to specialized agents, and delivers results via multiple channels.

```
User Request
    ↓
[Gateway] FastAPI 18789 → Routing Decision
    ↓
[AutonomousRunner] 5-Phase Pipeline
  RESEARCH → PLAN → EXECUTE → VERIFY → DELIVER
    ↓
[Agent Router] Semantic + Keyword Matching
    ↓
[Multi-Agent Execution] Parallel Workers
  Overseer (Opus 4.6) + CodeGen + Pentest + Finance + Research
    ↓
[Cost Tracker] Invoice-Grade Accounting
    ↓
[DAG Executor] Topological Sort for Sub-Tasks
    ↓
[Tool System] 75+ MCP Tools (Git, Web, SQL, Finance, Trading)
    ↓
[Supabase] Source of Truth (Jobs, Events, Agents, Costs)
    ↓
[Webhooks] Slack, Telegram, GitHub, Email
```

## Directory Structure

```
openclaw/
├── package.json                    # Next.js 14.2.5 (React 18.3.1, Jest, Tailwind)
├── tsconfig.json                   # TypeScript config
├── docker-compose.yml              # Docker deployment
├── gateway.py                       # FastAPI app startup (~100 lines)
├── autonomous_runner.py            # 5-phase job executor core
├── agent_router.py                 # Intelligent routing engine
├── agent_registry.py               # Agent health + metrics
├── dag_executor.py                 # DAG execution + topological sort
├── cost_tracker.py                 # Invoice-grade cost accounting
├── .env.example                    # 150 keys: API credentials, models, trading, Telegram
├── agents/
│   ├── overseer.json              # Opus 4.6, all-rounder, router fallback
│   ├── codegen_pro.json           # DeepSeek Kimi 2.5, senior coder
│   ├── codegen_elite.json         # MiniMax M2.5, junior/specific tasks
│   ├── pentest_ai.json            # Security audits
│   ├── database_agent.json        # SQL/Supabase ops
│   ├── test_generator.json        # Pytest/Jest
│   ├── researcher.json            # Research tasks
│   ├── technical_writer.json      # Documentation
│   ├── finance_ops.json           # Cost tracking, invoices
│   ├── project_decomposer.json    # Plan creation
│   ├── debugger.json              # Error recovery
│   └── betting_bot.json           # Trading/prediction markets
├── routers/                        # 20+ FastAPI route modules
│   ├── shared.py                  # Config, model callers, auth, memory
│   ├── health.py                  # /health, /agents, /cost_summary
│   ├── chat.py                    # /chat, /chat/stream
│   ├── jobs.py                    # /jobs/*, /approve, /cancel
│   ├── analytics.py               # /analytics, /job_costs, /agent_usage
│   ├── admin.py                   # Admin endpoints
│   ├── telegram.py                # Telegram webhooks
│   ├── slack.py                   # Slack integration
│   ├── approval.py                # Approval gates
│   ├── dispatch.py                # Dispatch jobs
│   ├── memory.py                  # Memory management
│   ├── trading.py                 # Polymarket/Kalshi
│   ├── workflows.py               # Workflow creation
│   ├── proposals.py               # Proposal generation
│   ├── events.py                  # Event streaming (WebSocket)
│   └── [12 more routers]
├── tests/
│   ├── test_runner.py             # Core pipeline tests
│   ├── test_dag_executor_v5.py    # DAG parallelism (99 tests)
│   ├── test_agent_registry_v5.py  # Agent health tracking
│   ├── test_cost_dashboard_api.py # Cost endpoint
│   ├── test_approval_gate.py      # Manual approval flows
│   ├── test_error_recovery.py     # Self-repair loops
│   ├── test_job_dispatch.py       # Job queuing
│   ├── [205 more files]
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Next.js root layout
│   │   ├── page.tsx               # Dashboard homepage
│   │   ├── globals.css            # Tailwind styling
│   │   ├── api/
│   │   │   ├── chat/route.ts      # Next.js API routes (mirror FastAPI)
│   │   │   └── [routes...]
│   │   └── [pages, components]
│   └── [React components, lib utilities]
└── [Systemd services, Dockerfile, etc.]
```

## 7 Core Components

### 1. Gateway (FastAPI, Port 18789)
- **File**: `gateway.py` (~100 lines)
- **Role**: HTTP API entry point, request routing, CORS/auth middleware
- **Key Features**:
  - 20+ imported routers (health, chat, jobs, analytics, admin, telegram, slack, trading, etc.)
  - Lifespan management (startup/shutdown hooks)
  - JSON error handling, request/response logging
  - WebSocket event streaming for real-time job progress
- **Authentication**: Bearer token (Supabase JWT or custom)
- **Rate Limiting**: Per-agent, per-user (configurable)

### 2. AutonomousRunner (5-Phase Job Executor)
- **File**: `autonomous_runner.py` (core executor)
- **Role**: Execute jobs through 5 sequential phases
- **Phases**:
  1. **RESEARCH** (~10% time) — Context gathering, semantic search, dependency analysis
  2. **PLAN** (~20% time) — Agent decomposition, DAG workflow generation, cost estimation
  3. **EXECUTE** (~50% time) — Run tasks (tools, code, LLM calls), parallel via DAG executor
  4. **VERIFY** (~10% time) — Quality checks, test execution, assertion validation
  5. **DELIVER** (~10% time) — Formatting, webhook delivery, state persistence
- **Cost Tracking**: Per-phase, per-tool, per-agent
- **Error Recovery**: Automatic self-repair loops (debugger agent re-attempts failed phases)
- **State Machine**: QUEUED → ANALYZING → RUNNING → VERIFIED → DELIVERING → DONE

### 3. Agent Router (Intelligent Routing)
- **File**: `agent_router.py` (~100 lines)
- **Role**: Match incoming requests to best agent
- **Algorithms**:
  - **Semantic Analysis** (embeddings): Compare request to agent descriptions
  - **Keyword Fallback** (cost-optimized): Pattern match task type to agent specialization
  - **Load Balancing**: Route to lowest-cost, lowest-latency available agent
  - **Caching** (5-min TTL): Avoid repeated routing calculations
- **Routing Rules** (from CLAUDE.md):
  - `code|build|fix|deploy|review` → CodeGen Pro (Kimi, $0.20/1M)
  - `test|pytest|jest` → Test Generator
  - `pentest|security|audit` → Pentest AI
  - `sql|database|query` → Database Agent
  - `research|knowledge|analysis` → Researcher
  - Default fallback → Overseer (Opus 4.6, all-rounder, $15/1M)

### 4. Cost Tracker (Invoice-Grade Accounting)
- **File**: `cost_tracker.py` (~60 lines)
- **Role**: Calculate, log, aggregate costs
- **Model Pricing** (2026 market rates):
  - Opus 4.6: $15/1M in, $60/1M out
  - Kimi 2.5 (DeepSeek): $0.20/1M in, $0.80/1M out
  - MiniMax M2.5: $0.15/1M in, $0.60/1M out
  - Gemini 2.0 Flash: $0.075/1M in, $0.30/1M out
  - MiniMax Vision: +$0.10/image
- **Storage**: Supabase `costs` table + JSONL fallback (`data/costs.jsonl`)
- **Granularity**: Per-job, per-phase, per-agent, per-tool
- **Dashboard**: Cost API endpoint returns JSON with daily/weekly/monthly summaries

### 5. DAG Executor (Parallel Execution Engine)
- **File**: `dag_executor.py` (~467 lines)
- **Role**: Execute sub-tasks in parallel using topological sort
- **Algorithm**: Kahn's algorithm → compute execution layers
  - Example: `[lint, test]` (layer 0) → `[review]` (layer 1) → `[deploy]` (layer 2)
- **Concurrency**: `asyncio.Semaphore(max_concurrent=3)` (configurable)
- **Features**:
  - Dependency graph validation (cycle detection)
  - Per-node timing + cost tracking
  - Skip upstream failures (fault tolerance)
  - Fail-fast option (stop on first failure)
- **Speed-up**: 2-3x faster than sequential execution (verified in tests)

### 6. Agent Registry (Health + Metrics)
- **File**: `agent_registry.py` (~80 lines)
- **Role**: Track agent availability, performance, error rates
- **AgentStatus Dataclass**:
  ```
  node_id, model_id, status (HEALTHY/DEGRADED/UNAVAILABLE)
  last_heartbeat, call_count, error_count, avg_latency_ms
  total_cost_usd, success_rate, uptime_percent
  ```
- **Features**:
  - Auto-register agents from `agents/*.json` on startup
  - Health checks every 30s (HTTP GET to agent endpoint)
  - Degrade/restore agents automatically
  - /agents endpoint returns live status

### 7. Tool System (75+ MCP Tools)
- **Location**: Referenced in shared.py, dispatched by runners
- **9 Categories**:
  1. **File Operations** (10 tools): read, write, edit, glob, delete, mkdir, tree, zip
  2. **Git** (8 tools): status, add, commit, push, pull, branch, log, diff
  3. **Code Execution** (12 tools): bash, python, node.js, docker, shell_execute
  4. **Web** (10 tools): web_fetch, web_search, web_scrape, screenshot, navigate, evaluate
  5. **Database** (8 tools): query_data_sources, update_data_source, create_database, sql_query
  6. **Finance** (9 tools): expense tracking, invoice tracker, financial summary, crypto
  7. **Trading** (12 tools): Polymarket (buy/sell/cancel), Kalshi orders, price monitoring, arb scanner
  8. **Research** (5 tools): deep_research, perplexity_sonar, news feeds, lemma search
  9. **Admin/Special** (1 tool): process_manage, send_sms, telegram_send, slack_message
- **Phase-Gated Access**: Tools unlocked per phase (e.g., deploy tools in EXECUTE phase only)
- **Error Recovery**: Tool failure triggers debugger agent re-attempt

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System health + agent status |
| `/agents` | GET | List all agents + metrics |
| `/cost_summary` | GET | Daily/weekly/monthly costs |
| `/chat` | POST | Single-turn request |
| `/chat/stream` | POST | Streaming response |
| `/jobs` | POST | Create new job |
| `/jobs/{job_id}` | GET | Job status + result |
| `/jobs/{job_id}/cancel` | POST | Cancel running job |
| `/approve/{job_id}` | POST | Manual approval (for P0/P1 jobs) |
| `/analytics/job_costs` | GET | Per-job cost breakdown |
| `/analytics/agent_usage` | GET | Agent usage stats |
| `/admin/agents/reload` | POST | Reload agent registry |
| `/telegram/webhook` | POST | Telegram integration |
| `/slack/webhook` | POST | Slack integration |
| `/events` | WebSocket | Real-time job progress |

## Systemd Services (VPS 152.53.55.207:18789)

| Service | Port | Workers | Purpose |
|---------|------|---------|---------|
| `openclaw-gateway.service` | 18789 | 1 | HTTP API (FastAPI) |
| `openclaw-worker-p0.service` | — | 2 | P0 jobs (critical: security, deploys) |
| `openclaw-worker-p1.service` | — | 4 | P1 jobs (feature builds, tests) |
| `openclaw-worker-p2.service` | — | 2 | P2 jobs (research, analysis) |
| `openclaw-watchdog.service` | — | 1 | Health monitoring, auto-restart |
| `openclaw-dashboard.service` | 3000 | 1 | Next.js UI |
| `openclaw-mcp-bridge.service` | — | 1 | Tool execution sandbox |
| `openclaw-cleaner.service` | — | cron | Cleanup old jobs (daily 2am) |

**Domain Mapping**:
- `gateway.overseerclaw.uk` → Gateway (18789)
- `dashboard.overseerclaw.uk` → Dashboard UI (3000)
- `pa.overseerclaw.uk` → Personal Assistant

**Control**:
```bash
systemctl restart openclaw-gateway      # Restart gateway
systemctl status openclaw-worker-p*     # Check all workers
journalctl -u openclaw-gateway -f       # Live logs
```

## Job Lifecycle

```
POST /jobs {"task": "...", "priority": "P1"}
         ↓
[QUEUED] Supabase: insert into jobs table
         ↓
[ANALYZING] Route via agent_router → Overseer (RESEARCH phase)
         ↓
[PLANNING] Decompose task → DAGWorkflow (PLAN phase)
         ↓
[APPROVAL?] If P0/P1: await manual /approve (or auto-approve if configured)
         ↓
[RUNNING] DAG executor spawns workers (EXECUTE phase, parallel)
         ↓
[VERIFYING] Run tests/assertions (VERIFY phase)
         ↓
[DELIVERING] Format output, send webhooks (DELIVER phase)
         ↓
[DONE] Return result via HTTP + broadcast to Slack/Telegram/email
```

## Test Coverage

- **Total Tests**: 212+
- **Pass Rate**: 97% (105/108 jobs in benchmark)
- **Key Test Files**:
  - `test_dag_executor_v5.py`: 99 tests (parallelism, topological sort, cycle detection)
  - `test_agent_registry_v5.py`: 20 tests (health checks, registration, metrics)
  - `test_cost_dashboard_api.py`: 15 tests (cost calculations, Supabase fallback)
  - `test_approval_gate.py`: 12 tests (manual approval flow)
  - `test_error_recovery.py`: 10 tests (self-repair loops)
  - `test_job_dispatch.py`: 8 tests (job queuing, routing)

**Command**: `pytest tests/ -v --cov=openclaw`

## Environment Variables (Critical)

| Key | Required | Default | Purpose |
|-----|----------|---------|---------|
| `ANTHROPIC_API_KEY` | YES | — | Claude API key |
| `SUPABASE_URL` | YES | — | Database endpoint |
| `SUPABASE_KEY` | YES | — | Supabase JWT secret |
| `DEEPSEEK_API_KEY` | NO | — | Kimi 2.5 (optional) |
| `MINIMAX_API_KEY` | NO | — | MiniMax M2.5 (optional) |
| `GOOGLE_API_KEY` | NO | — | Gemini 2.0 (optional) |
| `PORT` | NO | 18789 | Gateway port |
| `OPENCLAW_DATA_DIR` | NO | ./data | Data volume path |
| `TELEGRAM_BOT_TOKEN` | NO | — | Telegram webhook |
| `SLACK_WEBHOOK_URL` | NO | — | Slack integration |
| `GITHUB_TOKEN` | NO | — | GitHub API access |

See `.env.example` for full 150-key list.

## Known Limitations & v5.1+ Roadmap

**Current Gaps**:
- Per-agent runners spawn sequentially (v5.1: actor model)
- No persistent session state across requests (v5.1: Redis cache)
- Cost tracking lags 2-3 min (v5.1: real-time events)
- DAG executor max 10 nodes (v5.1: 100+ node graphs)

**Planned v5.1 Features**:
- **Agent Registry Plus**: Dynamic plugin system (add agents without restart)
- **Simulation Sandbox**: Test workflows before execution
- **GraphRAG Memory**: Long-term context across jobs
- **Streaming Dashboard**: Real-time job visualization

## Quick Start

```bash
# Install
git clone https://github.com/your-org/openclaw.git
cd openclaw
pip install -r requirements.txt
npm install

# Configure
cp .env.example .env
# Edit .env with API keys

# Run locally
python gateway.py       # Starts on http://localhost:18789
npm run dev            # Starts dashboard on http://localhost:3000

# Deploy (systemd)
sudo systemctl start openclaw-gateway openclaw-worker-p{0,1,2}
sudo systemctl status openclaw-gateway

# Monitor
curl http://localhost:18789/health
curl http://localhost:18789/cost_summary
```

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| gateway.py | ~100 | FastAPI app startup |
| autonomous_runner.py | ~300 | 5-phase job executor |
| agent_router.py | ~100 | Intelligent routing |
| agent_registry.py | ~80 | Health tracking |
| dag_executor.py | ~467 | Parallel execution |
| cost_tracker.py | ~60 | Cost accounting |
| routers/shared.py | ~80+ | Config, model callers |
| .env.example | ~150 | Environment config |
| docker-compose.yml | ~17 | Docker deployment |
| package.json | ~36 | Node.js dependencies |

---

**Last Updated**: 2026-03-13 | **Version**: 4.2 | **Status**: Production Ready

### High-Level Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Interfaces                         │
│  Telegram  Slack  Discord  WhatsApp  Teams  iMessage  Github   │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              openclaw-assistant (Node.js)                        │
│         Multi-channel communication layer                        │
│  • 9+ channel support (BlueBubbles, Signal, Zalo, Matrix, etc)  │
│  • Voice support (macOS/iOS/Android)                            │
│  • Live Canvas rendering                                        │
│  • OAuth (Anthropic, OpenAI) for model auth                    │
│  • Recommended: Claude Pro/Max (Opus 4.6)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│      openclaw-web-ui (Cloudflare Workers JS/TS)                │
│         Token-based proxy authentication layer                  │
│  • URL: openclaw-ui.amit-shah-5201.workers.dev                 │
│  • Auth: X-Auth-Token header or query param                    │
│  • Target: 152.53.55.207:18789 (VPS gateway)                   │
│  • CORS handling for cross-origin requests                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│             OpenClaw Gateway (FastAPI, Python 3.11+)            │
│                  PRIMARY JOB EXECUTION CORE                     │
│  • Port: 18789 (Hetzner VPS 152.53.55.207)                     │
│  • Domains: gateway.overseerclaw.uk                             │
│  • Multi-agent routing (least-loaded first)                     │
│  • Cost tracking per job/agent/model                            │
│  • Session state persistence (Redis + Supabase)                 │
│  • Error recovery with retry logic                              │
│  • 190+ unit tests (97% benchmark success)                      │
│  • Cost efficiency: $0.02-$2.50 per job                         │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                  │
   ┌─────────▼──────────┐        ┌──────────────▼───────────────┐
   │  PA Worker (Fast   │        │  Router + Agent Pool          │
   │   API) Port 8001   │        │  Routing Logic:               │
   │                    │        │  • time<30s → Sonnet 3.5      │
   │ 8 Domains:         │        │  • complex>0.8 → Opus 4.6    │
   │ 1. Email (IMAP)    │        │  • else → Ollama (local)     │
   │ 2. Calendar (GCal) │        │  • Fallback chain             │
   │ 3. Tasks (Notion)  │        │                               │
   │ 4. Expenses        │        │  Agent Pool:                  │
   │ 5. Slack (WebAPI)  │        │  • Opus 4.6 (max 2 conc)     │
   │ 6. GitHub (GraphQL)│        │  • Sonnet 3.5 (max 5 conc)   │
   │ 7. News/RSS        │        │  • Ollama Qwen 7B (max 10)   │
   │ 8. Shopping        │        │                               │
   │                    │        │  Cost Tracking:              │
   │ Background Loops:  │        │  • Per-job billing           │
   │ • 5min: Email      │        │  • Model-specific rates      │
   │ • 30min: Calendar  │        │  • Token counting            │
   │ • 1h: Expenses     │        │  • Audit trail logging       │
   │ • 6h: GitHub       │        │                               │
   └────────┬───────────┘        └──────────────┬────────────────┘
            │                                   │
            └──────────────────┬────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Session Store    │
                    │ (Supabase + Redis) │
                    │                    │
                    │ Tables:            │
                    │ • jobs             │
                    │ • sessions         │
                    │ • costs            │
                    │ • agents           │
                    │ • processed        │
                    │ • memories         │
                    └────────────────────┘
```

### Technology Stack

| Component | Language | Framework | Port | Domain |
|---|---|---|---|---|
| **Gateway** | Python 3.11+ | FastAPI | 18789 | gateway.overseerclaw.uk |
| **PA Worker** | Python 3.11+ | FastAPI | 8001 | pa.overseerclaw.uk |
| **Assistant** | TypeScript | Node.js ≥22 | varies | messenger channels |
| **Web UI** | TypeScript | Cloudflare Workers | edge | openclaw-ui.workers.dev |
| **DB** | SQL | Supabase PostgreSQL | 5432 | remote (Supabase cloud) |
| **Cache** | - | Redis | 6379 | localhost or remote |

---

## 2. Core Components (v5)

### 2.1 Gateway (Main API Server)

**Path**: `/root/openclaw/gateway/`
**Language**: Python 3.11+ (FastAPI + Pydantic)
**Port**: 18789 (VPS 152.53.55.207)
**Domain**: gateway.overseerclaw.uk

#### Routes

```
POST /job/create
  Input: { prompt, urgency, timeout_sec, agent_id? }
  Output: { job_id, status, created_at }

GET /job/{id}
  Output: { id, status, result, cost_usd, logs, agent_used }

GET /job/{id}/logs
  Output: Stream of log lines (text/event-stream)

POST /agent/register
  Input: { agent_id, capabilities[], model, version }
  Output: { registered_agent_id, endpoints }

GET /agents
  Output: [ { id, name, capabilities, status, concurrent_limit } ]

POST /cost/summary
  Input: { user_id?, start_date, end_date }
  Output: { total_cost, by_agent, by_model, by_project }
```

#### Key Features

- **Multi-agent routing**: Least-loaded first strategy
- **Cost tracking**: Per-job, per-agent, per-model attribution
- **Session persistence**: State saved to Supabase + Redis cache
- **Error recovery**: Automatic retry with exponential backoff
- **Idempotency**: Idempotency keys prevent double-execution (v5 feature)
- **Heartbeat monitoring**: Background health checks on all agents (v5)
- **Approval gates**: Risk-scored actions auto/manual/email approval (v5)

#### Request Flow

```python
# Pseudocode
1. User: POST /job/create
   - Payload: { prompt, urgency, agent_id? }
   - Validate payload
   - Generate job_id (UUID)

2. Router selects agent
   - Check: time_budget < 30s? → Sonnet 3.5
   - Else: complexity > 0.8? → Opus 4.6
   - Else: → Ollama Qwen 7B

3. Session created
   - Store state in Redis (TTL 24h)
   - Write job record to Supabase
   - Set status = "pending"

4. Agent executes
   - Run prompt through LLM
   - Tool invocation if needed (75+ tools)
   - Collect logs, token counts
   - Idempotency check (skip if duplicate)

5. Result returned
   - Calculate cost_usd (tokens * rate)
   - Write result to Supabase
   - Set status = "done"
   - Update cost tracking

6. User: GET /job/{id}
   - Return full result + cost breakdown
```

### 2.2 PA Worker (Personal Assistant)

**Path**: `/root/openclaw/pa_worker/`
**Language**: Python 3.11+ (FastAPI + aiohttp)
**Port**: 8001
**Domain**: pa.overseerclaw.uk

#### 8 Capability Domains

1. **Email Integration** (IMAP)
   - Read/summarize emails
   - Draft responses
   - Search and filter
   - Auto-reply templates
   - Integration: Gmail OAuth (GWS pending)

2. **Calendar Management** (Google Calendar)
   - Fetch events
   - Suggest meeting times
   - Create bookings
   - Timezone handling
   - Integration: Google Calendar API (GWS pending)

3. **Task Management** (Notion)
   - Sync database
   - Update task status
   - Track deadlines
   - Priority scoring
   - Integration: Notion API token (MISSING)

4. **Expense Tracking**
   - Categorize spending (8 categories)
   - Budget alerts
   - Receipt OCR (document processing)
   - Monthly reports
   - Database: Supabase finance_transactions

5. **Slack Integration** (WebAPI)
   - Monitor channels
   - Send messages
   - Auto-respond to mentions
   - Channel summaries
   - Thread tracking
   - Integration: Slack bot token (pending)

6. **GitHub Integration** (GraphQL)
   - PR reviews
   - Issue triage
   - Notification filtering
   - Commit tracking
   - Integration: GitHub OAuth (pending)

7. **News & Research** (RSS + Perplexity)
   - Aggregate RSS feeds
   - Web research (Perplexity)
   - News digest compilation
   - Topic clustering
   - Integration: Perplexity API key needed

8. **Shopping & Deal Tracking**
   - Price tracking (Amazon, etc)
   - Deal alerts
   - Price comparison
   - Budget matching
   - Integration: 3rd-party scraping APIs

#### Background Loops (Always Running)

- **Every 5 min**: Check email, aggregate urgent messages
- **Every 30 min**: Sync calendar events, suggest meetings
- **Every 1 hour**: Process expense reports, compile digest
- **Every 6 hours**: GitHub notifications, security alerts
- **Daily at 9am**: News digest, market updates

#### Status: Partially Deployed

**Working**:
- Core PA task invocation
- Tool routing

**Pending Authentication**:
- Gmail OAuth (GWS setup)
- Google Calendar API
- Slack bot token
- GitHub OAuth
- Notion API token

See: [pa-deploy-status.md](pa-deploy-status.md)

### 2.3 Router & Agent Pool

**Path**: `/root/openclaw/router/`
**Language**: Python (routing logic)

#### Routing Algorithm

```python
def select_agent(task):
    """Route task to optimal agent based on constraints."""

    # Tier 1: Time constraint
    if task.time_budget < 30 seconds:
        return SONNET_35  # Fastest, cheapest

    # Tier 2: Complexity
    if task.complexity_score > 0.8:
        return OPUS_46  # Smartest, best reasoning

    # Tier 3: Cost optimization
    if OLLAMA_AVAILABLE:
        return OLLAMA_QWEN_7B  # Free/cheap local model

    # Fallback chain
    try:
        return attempt_first_choice()
    except RateLimitError:
        return try_fallback_agent()
    except Exception as e:
        log_error(e)
        return DEFAULT_AGENT
```

#### Agent Pool

| Agent | Model | Max Concurrent | Cost/1M tokens | Latency | Best For |
|---|---|---|---|---|---|
| **Agent A** | Claude Opus 4.6 | 2 | $15 in / $45 out | 2-5s | Complex reasoning, long-context |
| **Agent B** | Claude Sonnet 3.5 | 5 | $3 in / $12 out | 0.5-2s | Fast tasks, simple logic |
| **Agent C** | Ollama Qwen 2.5 Coder 7B | 10 | $0 (local) | 1-3s | Code generation, fallback |

#### Cost Calculation

```python
cost_usd = (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000

# Example: Opus 4.6
input_tokens = 5000
output_tokens = 2000
cost = (5000 * 0.000015 + 2000 * 0.000045) = $0.165 per job
```

### 2.4 Session Store (Database)

**Tech**: Supabase PostgreSQL + Redis cache
**TTL**: Redis cache 24 hours

#### Schema

```sql
-- Jobs table (main execution log)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending','running','done','error')),
    prompt TEXT NOT NULL,
    result JSONB,
    error_message TEXT,
    cost_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT now(),
    completed_at TIMESTAMP,
    INDEX (user_id, created_at),
    INDEX (status)
);

-- Sessions table (state persistence)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    state JSONB,  -- Agent context, tool state, memory
    updated_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT now() + interval '24 hours'
);

-- Cost tracking
CREATE TABLE costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    model TEXT,
    input_tokens INT,
    output_tokens INT,
    cost_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT now()
);

-- Agents registry
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    capabilities TEXT[],
    model TEXT,
    version TEXT,
    status TEXT CHECK (status IN ('active','inactive','deprecated')),
    concurrent_limit INT,
    cost_per_1m_in DECIMAL(10, 6),
    cost_per_1m_out DECIMAL(10, 6),
    registered_at TIMESTAMP DEFAULT now()
);

-- Processed jobs (idempotency, v5)
CREATE TABLE processed (
    idempotency_key UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    processed_at TIMESTAMP DEFAULT now(),
    result JSONB
);

-- Memory/reflexion logs (v5)
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    agent_id TEXT,
    memory_type TEXT CHECK (memory_type IN ('success','failure','recovery','pattern')),
    content TEXT,
    embedding VECTOR(1536),  -- pgvector for semantic search
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT now() + interval '30 days'
);
```

---

## 3. Tool Ecosystem (75+ Tools)

### File Operations
- Read file, Write file, List directory
- Delete, Copy, Move, Rename
- Permissions (chmod, chown)
- Archive (zip, tar, gzip)

### Git Operations
- Clone, commit, push, pull
- Branch management
- Diff, merge, rebase
- Tag management
- GitHub API (PRs, issues, code review)

### Code Execution
- Python exec (subprocess)
- Node.js execution
- Bash script execution
- Docker container spawn
- Environment variable injection

### Data Processing
- CSV/JSON parsing
- Database queries (SQL)
- Data aggregation
- Sorting, filtering, transformation

### API Integrations
- HTTP requests (GET, POST, PUT, DELETE)
- GraphQL queries
- Webhook registration
- Rate limiting handling
- OAuth token refresh

### Research & Web
- Web scraping (BeautifulSoup, Selenium)
- PDF extraction
- Screenshot capture
- HTML parsing
- Perplexity web search

### Communication
- Email send/receive (IMAP/SMTP)
- Slack messages
- Discord webhooks
- Telegram API
- GitHub notifications

### Finance & Betting
- Polymarket API (live odds, place bets)
- Kalshi API (prediction markets)
- Sportsbook odds (200+ bookmakers)
- XGBoost prediction model (local)
- Kelly criterion calculator
- Cost tracking + billing

### System Tools
- Process monitoring
- Port checking
- Network diagnostics
- Memory profiling
- Log aggregation

---

## 4. Multi-Agent Specialization

### Core Agent Pool (v5)

Each agent is optimized for specific task types:

#### Agent Type 1: Code Agent
- **Model**: Opus 4.6
- **Specialization**: Code generation, debugging, refactoring
- **Tools**: Git, code execution, testing frameworks
- **Success Rate**: 92%
- **Avg Cost**: $0.45 per job

#### Agent Type 2: Research Agent
- **Model**: Sonnet 3.5
- **Specialization**: Data analysis, web research, synthesis
- **Tools**: Web scraping, API integrations, Perplexity
- **Success Rate**: 94%
- **Avg Cost**: $0.12 per job

#### Agent Type 3: Sports Agent
- **Model**: Opus 4.6
- **Specialization**: Odds analysis, arbitrage detection, betting
- **Tools**: Polymarket, Kalshi, sportsbook APIs, XGBoost
- **Success Rate**: 88%
- **Avg Cost**: $0.38 per job

#### Agent Type 4: PA Agent
- **Model**: Sonnet 3.5
- **Specialization**: Email, calendar, tasks, notifications
- **Tools**: Gmail, Google Calendar, Notion, Slack
- **Success Rate**: 96%
- **Avg Cost**: $0.08 per job

#### Agent Type 5: Security Agent
- **Model**: Opus 4.6
- **Specialization**: Vulnerability scanning, access control
- **Tools**: SAST/DAST, CVE databases, penetration testing
- **Success Rate**: 85%
- **Avg Cost**: $0.62 per job

#### Agent Type 6: CI/CD Agent
- **Model**: Sonnet 3.5
- **Specialization**: Build pipeline management, deployment
- **Tools**: Docker, Kubernetes, GitHub Actions
- **Success Rate**: 91%
- **Avg Cost**: $0.19 per job

---

## 5. v5 Features (Released March 9, 2026)

### Component A: Agent Registry

**Purpose**: Discover, install, manage agents dynamically (no code changes needed)

**Features**:
- Registry UI (React dashboard)
- Search + filter by capability, cost, rating
- One-click install (auto-download + verify signature)
- Version management (pin to version, auto-upgrade)
- Usage analytics (calls/day, cost, success rate)

**Tests**: 32 unit + 8 integration = 40 tests
**Cost**: $18.50 shipped

### Component B: Simulation Sandbox

**Purpose**: Test agents before production (zero cost, instant)

**Features**:
- Replay past sessions (mock LLM responses from history)
- Dry-run mode (no actual API calls)
- Cost predictor (estimate bill before running)
- Failure injection (test error handling paths)
- Time travel (test with historical data)

**Tests**: 28 unit + 10 integration = 38 tests
**Cost**: $22.10 shipped

### Component C: Memory Framework

**Purpose**: Agents learn from past jobs (reflexion + embedding storage)

**Features**:
- Session persistence (SQLite + Redis)
- Reflexion logs (what failed, what worked)
- Semantic search (pgvector embeddings)
- Auto-cleanup (forget after 30 days)
- Context injection (auto-prepend relevant memories)
- Note: GraphRAG dropped (too complex for timeline)

**Tests**: 32 unit + 9 integration = 41 tests
**Cost**: $26.40 shipped

### Component D: Idempotency Layer

**Purpose**: Retry jobs without double-execution (100% reliability)

**Features**:
- Idempotency key tracking (UUID + content hash)
- Duplicate detection (skip if same job ran)
- Partial retry (resume from checkpoint)
- State snapshots (save every step)

**Tests**: 18 unit + 7 integration = 25 tests
**Cost**: $14.20 shipped

### Component E: Venv Support

**Purpose**: Isolated Python environments per job (no dependency bloat)

**Features**:
- Auto-create venv from requirements.txt
- Package isolation (no global install)
- Auto-cleanup on completion
- Timeout (force-kill after 5 min)

**Tests**: 15 unit + 5 integration = 20 tests
**Cost**: $11.80 shipped

### Component F: Heartbeat + Approval

**Purpose**: Monitor agent health + human gates on risky actions

**Features**:
- Heartbeat pings (every 30s)
- Auto-recovery (restart failed agents)
- Risk scoring (0-100, configurable threshold)
- Multi-level approvals (email, Slack, UI)
- Audit trail (who approved what when)

**Tests**: 22 unit + 6 integration = 28 tests
**Cost**: $19.20 shipped

**Total v5 Tests**: 119 unit + 46 integration = **165 total**
**Total v5 Cost**: **$112.20 shipped** (March 9 blitz)

---

## 6. MCP Servers (7 Installed)

Modular tool ecosystem via Model Context Protocol

| Server | Tool | Status | Auth | Config |
|---|---|---|---|---|
| **Twitter/X** | Posts, timeline, search | ✅ Installed | API key | mcp.json |
| **Reddit** | Posts, comments, subreddits, search | ✅ Installed | OAuth | mcp.json |
| **Slack** | Send/read messages, channels | ✅ Installed | Bot token | .mcp.json MISSING |
| **GitHub** | PRs, issues, code review, commits | ✅ Installed | OAuth | mcp.json |
| **Gmail** | Read, send, label emails | ✅ Installed | OAuth | .mcp.json MISSING (GWS pending) |
| **Google Drive** | Read, create docs, folders | ✅ Installed | OAuth | .mcp.json MISSING (GWS pending) |
| **Perplexity** | Web research, citations | ✅ Installed | API key | mcp.json |

**Status**: .mcp.json missing (lost in deploy), GWS OAuth flow pending

See: [mcp-servers-installed.md](mcp-servers-installed.md)

---

## 7. Deployment & Infrastructure

### VPS Configuration

**Provider**: Hetzner (https://console.hetzner.cloud)
**IP**: 152.53.55.207
**Specs**: 4 vCPU, 8GB RAM, 160GB SSD
**OS**: Ubuntu 22.04 LTS

### Systemd Services

```bash
# Main gateway
systemctl restart openclaw-gateway      # Port 18789
systemctl status openclaw-gateway

# PA worker
systemctl restart openclaw-pa          # Port 8001
systemctl status openclaw-pa

# Router dispatcher
systemctl restart openclaw-router      # Internal routing
systemctl status openclaw-router

# Database cache
systemctl restart redis-server         # Port 6379
systemctl status redis-server

# Check all services
systemctl status openclaw-*
journalctl -u openclaw-gateway -f     # Live logs
```

### Domains & DNS

| Domain | Target | Service | Status |
|---|---|---|---|
| **gateway.overseerclaw.uk** | 152.53.55.207:18789 | Main API | ✅ ACTIVE |
| **pa.overseerclaw.uk** | 152.53.55.207:8001 | PA Worker | ✅ ACTIVE (partial) |
| **dashboard.overseerclaw.uk** | 152.53.55.207 | Cost dashboard | ⚠️ Pending deploy |
| **openclaw-ui.workers.dev** | Cloudflare proxy | Web UI | ✅ ACTIVE |

**DNS Provider**: Cloudflare (automatic SSL/TLS)

### Environment Variables

```bash
# .env (VPS)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
KIMI_API_KEY=...
BAILIAN_API_KEY=...

SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=eyJhbGc...

REDIS_URL=redis://localhost:6379

# GWS (PENDING)
GMAIL_CREDENTIALS={}  # Service account JSON
GOOGLE_CALENDAR_CREDENTIALS={}
GOOGLE_DRIVE_CREDENTIALS={}

# MCP/Integration
NOTION_API_TOKEN=ntn_...  # MISSING
SLACK_BOT_TOKEN=xoxb-...  # MISSING
GITHUB_TOKEN=ghp_...

# Prediction Markets
POLYMARKET_API_KEY=...
KALSHI_API_KEY=...
```

### Deployment Checklist

- [x] Gateway service running (systemd)
- [x] PA worker deployed (partial, auth pending)
- [x] Redis cache operational
- [x] Supabase connection verified
- [x] SSL/TLS (Cloudflare)
- [ ] .mcp.json recovered or regenerated
- [ ] GWS OAuth flow completed
- [ ] Notion API token configured
- [ ] All background loops tested

---

## 8. Current State & Metrics (March 13, 2026)

### Production Statistics

- **Uptime**: 99.2% (Feb-Mar 2026)
- **Jobs Executed**: 105 total ($7.30 cost)
- **Success Rate**: 97% benchmark success
- **Avg Response Time**: 1.2s (P50), 4.5s (P95)
- **Cost Efficiency**: $0.02-$2.50 per job
- **Test Coverage**: 190+ unit tests

### Active Builds (March 13)

1. **EdgeBoard Dashboard**
   - Status: All code written, awaiting build verification
   - Issue: OOM (out of memory) during Next.js build
   - Priority: HIGH (investor demo potential)
   - Path: /root/edgeboard/
   - See: [edgeboard-dashboard-status.md](edgeboard-dashboard-status.md)

2. **MiroFish Clone**
   - Status: Clone + English translation in progress
   - Priority: MEDIUM
   - See: [mirofish-clone-status.md](mirofish-clone-status.md)

### Recent Commits (Estimated)

Based on git status from environment:

```
• Initial commit from Create Next App (5f2b587)
  - Next.js 16 setup with TypeScript
  - Globals CSS, layout, page component
  - tsconfig.json, package.json configured
```

**Modified Files** (uncommitted):
- package-lock.json (dep updates)
- package.json (version bump)
- src/app/globals.css (styling)
- src/app/layout.tsx (layout changes)
- src/app/page.tsx (page content)
- tsconfig.json (TS config)

---

## 9. Known Issues & Blockers

### Critical

1. **EdgeBoard OOM (Out of Memory)**
   - **Impact**: Dashboard demo blocked
   - **Status**: Investigating build optimization
   - **Mitigation**: Larger build environment or code splitting
   - **Timeline**: URGENT (for investor pitch)

2. **GWS OAuth Incomplete**
   - **Impact**: Email, calendar, Google integrations broken
   - **Status**: Service account not configured
   - **Blocker**: Missing OAuth consent screen setup
   - **Timeline**: 2-3 hours to complete

3. **.mcp.json Lost**
   - **Impact**: All MCP tools offline
   - **Status**: File missing from deployment
   - **Recovery**: Recreate from backup or re-setup all 7 servers
   - **Timeline**: 1-2 hours

### Important

4. **Notion API Token Missing**
   - **Impact**: Task sync disabled
   - **Status**: Token not in .env
   - **Timeline**: 5 min to add

5. **PA Background Loops Untested**
   - **Impact**: Email/calendar automation may fail
   - **Status**: Auth pending, not fully tested
   - **Timeline**: Complete after GWS setup

### Nice-to-Have

6. **Dashboard OOM** (same as #1)
7. **Streaming responses** (not yet implemented, v5.1 candidate)
8. **Slash commands** (UX improvement, low priority)

---

## 10. Error Patterns & Lessons Learned

See: [error-patterns.md](error-patterns.md)

### Critical Mistakes (NEVER Repeat)

1. **Async/Await Context Switching**
   - Mixing sync Redis with async FastAPI blocks event loop
   - Fix: Always use async Redis client (redis.asyncio)
   - Cost: 4 hours debugging

2. **Session State Mutation**
   - Modifying shared session dict affects all jobs
   - Fix: Deep copy before mutation
   - Cost: 3 hours, 8 failed test runs

3. **Token Counting Off-by-One**
   - Using word count instead of actual tokens
   - Fix: Use tokenizer or count from API response
   - Cost: 2 hours billing debugging

4. **Router Deadlock**
   - Always routing to "fastest" agent creates bottleneck
   - Fix: Weight by both load and capability
   - Cost: 6 hours, system unresponsive

5. **Git Conflicts in Lock Files**
   - Committing package-lock.json during multi-agent builds
   - Fix: Add to .gitignore for local builds
   - Cost: Merge conflict headaches

---

## 11. Architecture Decisions & Trade-offs

### Why Monolithic Gateway (Not Kubernetes)

**Decision**: Single FastAPI gateway on VPS, not K8s cluster
**Reasoning**:
- VPS sufficient for current load (4 vCPU, 8GB RAM)
- K8s adds 2+ weeks overhead
- Docker Compose for scaling when needed
- Cost: VPS $10-20/mo vs K8s $50-100+/mo

### Why Redis + Supabase (Not just one DB)

**Decision**: Redis cache + Supabase for persistence
**Reasoning**:
- Redis: Fast session state (< 1ms)
- Supabase: Durable job history, analytics
- Cache misses fall back to Supabase
- Cost: $10-20/mo Supabase + local Redis

### Why 3-Tier Agent Pool (Not LLM Router)

**Decision**: Manual routing rules, not LLM-based
**Reasoning**:
- Deterministic (no hallucination in routing)
- Faster (no LLM call overhead)
- Cheaper (no cost for routing decision)
- LLM-based adds latency + cost with marginal benefit

### Why Local Ollama (Not all cloud)

**Decision**: Fallback to local Ollama Qwen 7B
**Reasoning**:
- Free tier (no API calls)
- Always available (no rate limits)
- Good for code generation (acceptable quality)
- Reduces cloud spend by ~10%

---

## 12. Next Steps (Roadmap)

### Immediate (March 13-20)

1. **URGENT**: Fix EdgeBoard OOM, deploy demo
2. **URGENT**: Complete GWS OAuth setup
3. Recover .mcp.json file
4. Add Notion API token to .env
5. Test PA background loops end-to-end

### Short Term (March 20-31)

6. Ship sports betting agent (revenue-generating)
7. Deploy cost dashboard (investor ready)
8. Implement approval gates (enterprise feature)
9. Add streaming responses (UX improvement)

### Medium Term (April 2026)

10. Slash commands (/sports, /research, /pa)
11. Browser automation (Playwright integration)
12. Approval UI (dashboard-based approvals)
13. Team/multi-user support (Phase 2)

### Long Term (Q2 2026)

14. GraphRAG memory (defer from v5)
15. IDE integration (Cursor-like experience)
16. Multi-team workspaces
17. Advanced RBAC (role-based access)

---

## 13. Key Relationships & Dependencies

### GitHub Repos

- **Miles0sage/openclaw** (MAIN, PRIVATE)
  - Core monolith, everything lives here
  - All agents, tools, costs
  - Production on VPS

- **Miles0sage/openclaw-agents** (PUBLIC)
  - Multi-agent framework foundation
  - 12 specialist agents, 75+ tools
  - Used by main openclaw repo

- **Miles0sage/openclaw-assistant** (PRIVATE)
  - Communication layer (9+ channels)
  - Consumes openclaw job engine
  - Sits above agents framework

- **Miles0sage/openclaw-web-ui** (PRIVATE)
  - Cloudflare Workers proxy
  - Token-based auth
  - Cloudflare deployment

### External Services

| Service | Purpose | Status | Cost |
|---|---|---|---|
| Anthropic API | Claude Opus/Sonnet | ✅ Active | $200/mo (Max) |
| OpenAI API | Codex fallback | ✅ Active | ~$20/mo |
| Supabase | Database + auth | ✅ Active | Free tier |
| Cloudflare | DNS + Workers | ✅ Active | Free tier |
| Hetzner VPS | Infrastructure | ✅ Active | $10/mo |
| Redis | Cache (local) | ✅ Active | Free |
| GitHub | Code + API | ✅ Active | Free (public repos) |

---

## 14. References & Related Documentation

### Architecture & Technical
- [openclaw-architecture.md](openclaw-architecture.md) - THIS FILE
- [error-patterns.md](error-patterns.md) - Hard-won debugging lessons
- [openclaw-next-steps.md](openclaw-next-steps.md) - Technical roadmap
- [openclaw-runner-bugs.md](openclaw-runner-bugs.md) - Runner bug patterns

### Strategy & Plans
- [openclaw-strategy-synthesis-2026.md](openclaw-strategy-synthesis-2026.md) - **START HERE**
- [openclaw-action-plan-march2026.md](openclaw-action-plan-march2026.md) - **ACTIVE NOW**
- [openclaw-v5-battle-plan-revised.md](openclaw-v5-battle-plan-revised.md) - Feature gaps + what to steal
- [openclaw-competitive-analysis-2026.md](openclaw-competitive-analysis-2026.md) - vs Devin/Bolt/Cursor

### Deployment & Operations
- [pa-deploy-status.md](pa-deploy-status.md) - PA auth setup
- [mcp-servers-installed.md](mcp-servers-installed.md) - Tool ecosystem
- [edgeboard-dashboard-status.md](edgeboard-dashboard-status.md) - Dashboard demo
- [github-repos-openclaw.md](github-repos-openclaw.md) - Repo ecosystem

### Active Projects
- [edgeboard-dashboard-status.md](edgeboard-dashboard-status.md) - Betting dashboard
- [mirofish-clone-status.md](mirofish-clone-status.md) - AI prediction engine
- [prediction-market-passive-income-plan.md](prediction-market-passive-income-plan.md) - Revenue plan

---

## 15. Quick Reference Commands

```bash
# Gateway control
systemctl restart openclaw-gateway
systemctl status openclaw-gateway
journalctl -u openclaw-gateway -f

# Test gateway
curl https://gateway.overseerclaw.uk/health
curl -H "X-Auth-Token: <token>" https://openclaw-ui.workers.dev/agents

# Check costs
curl https://gateway.overseerclaw.uk/cost/summary

# PA worker
systemctl restart openclaw-pa
curl https://pa.overseerclaw.uk/health

# Redis
redis-cli ping
redis-cli keys "*"

# View logs
journalctl -u openclaw-gateway -f --since "10 minutes ago"
tail -f /var/log/openclaw/gateway.log

# SSH to VPS
ssh root@152.53.55.207
```

---

## 16. FAQ & Troubleshooting

### Q: Jobs stuck in "pending" state?
A: Check router service: `systemctl restart openclaw-router`
   Check Redis: `redis-cli ping` should return PONG
   Check logs: `journalctl -u openclaw-gateway -f`

### Q: Cost tracking shows $0?
A: Verify token counting in gateway code
   Check token_count field populated from LLM response
   Ensure cost rates match model pricing

### Q: PA not sending emails?
A: Check .mcp.json exists
   Verify Gmail OAuth credentials in .env
   Restart PA: `systemctl restart openclaw-pa`
   Check logs: `journalctl -u openclaw-pa -f`

### Q: Memory usage high?
A: Check session TTL (should auto-expire at 24h)
   Verify Redis FLUSHDB not holding old keys
   Monitor with: `redis-cli INFO memory`

### Q: How to add new agent?
A: Registry is JSON-based (v5 feature)
   Create agent JSON in registry
   POST /agent/register
   Agent available immediately

---

**Last Updated**: March 13, 2026
**Status**: PRODUCTION
**Version**: v5 (stable)
**Maintainer**: Miles0sage
**Repository**: https://github.com/Miles0sage/openclaw
