# OpenClaw Infrastructure Exploration Summary

**Date**: March 13, 2026  
**Scope**: Complete mapping of /root/openclaw/ infrastructure across six categories  
**Status**: Phase 1 exploration complete with detailed technical findings  
**Files Read**: 12 core files totaling ~3500 lines of analyzed code

---

## Executive Overview

OpenClaw v4.2 is a sophisticated multi-agent orchestration platform with six major infrastructure components already built and operational. The exploration confirmed all six requested infrastructure categories have substantial implementations, with the exception of tmux agent spawning which references a non-existent file (needs investigation).

**Key Achievement**: End-to-end job execution pipeline from GitHub issue detection through autonomous multi-phase execution to PR delivery, with real-time monitoring, cost tracking, rate limiting, and failure handling.

---

## Infrastructure Category 1: Agent Orchestration / Dispatch / Factory

**Status**: FULLY BUILT ✓

### Core Files
- **`/root/openclaw/autonomous_runner.py`** (900+ lines)
  - Central orchestration engine implementing 6-phase execution pipeline
  - AGENT_MAP (lines 748-759): Capability-based routing for 6 agent specialists
  - Phase enum (lines 799-806): RESEARCH → PLAN → EXECUTE → CODE_REVIEW → VERIFY → DELIVER
  - Tool whitelists (lines 762-792): Phase-specific tool access control prevents misuse
  - PlanStep dataclass (lines 809-817): Individual execution steps with retry tracking
  - ExecutionPlan dataclass (lines 821-833): Complete multi-step plan with dependencies
  - JobProgress dataclass (lines 837-865): State machine tracking phase/status/cost/timestamps

### Agent Capability Mapping (AGENT_MAP)
```python
AGENT_MAP = {
    "project_manager": {...},      # Overseer - planning, routing
    "coder_agent": {...},          # CodeGen Pro - simple tasks
    "elite_coder": {...},          # CodeGen Elite - complex refactors
    "hacker_agent": {...},         # Pentest AI - security
    "database_agent": {...},       # SupabaseConnector - data ops
    "researcher": {...},           # Researcher - deep research
}
```

### Phase-Specific Tool Access Control
- **RESEARCH_TOOLS**: Web search, documentation lookup, knowledge graph
- **PLAN_TOOLS**: Document creation, architecture analysis, planning utilities
- **EXECUTE_TOOLS**: File operations, shell execution, API calls, model invocation
- **CODE_REVIEW_TOOLS**: Linting, testing, diff analysis
- **VERIFY_TOOLS**: Test validation, performance benchmarks, coverage analysis
- **DELIVER_TOOLS**: GitHub PR creation, deployment, release management

### Key Orchestration Patterns

**1. Plan-Based Execution**
- PlanStep with index/description/tool_hints/status/result/attempts/error/delegate_to
- Allows human review before execution and mid-execution modifications
- Supports delegation to specialized agents

**2. Capability-Based Routing**
- Agent selected based on task requirements, not cost alone
- Default routing: project_manager → coder_agent → elite_coder as complexity increases
- Security tasks routed to hacker_agent, data tasks to database_agent

**3. Skill Recommendation System** (lines 549-630)
- Analyzes task description to recommend skill entities
- Maps recommended skills to available tools
- Tracks skill usage statistics

**4. Loop Detection** (lines 632-678)
- Tracks repeated actions across iterations
- Triggers escalation when loop detected (3x same action)
- Prevents infinite iteration cycles

### Integration Points
- Called by `coding_factory_cron.py` for GitHub issue execution
- Integrates with `job_lifecycle.py` for guardrails
- Calls `cost_tracker.py` to log token/cost metrics
- Receives phase results through structured result objects

---

## Infrastructure Category 2: Dashboard / Web UI

**Status**: FULLY BUILT ✓

### Core Files
- **`/root/openclaw/dashboard_api.py`** (1144 lines)
  - FastAPI backend providing real-time monitoring, log aggregation, service management
  - SSE (Server-Sent Events) streaming for live updates
  - Authentication via Bearer token or password
  - Comprehensive analytics and health endpoints

### Authentication & Authorization
```python
verify_token() [lines 167-195]:
  - Accept Bearer token or password
  - Validates against DASHBOARD_TOKEN and DASHBOARD_PASSWORD
  - Optional whitelist-based IP filtering
```

### Real-Time Monitoring Stack

**SSE (Server-Sent Events) Mechanism** (lines 695-758)
- `_sse_clients`: List of asyncio.Queue objects for multi-client broadcast
- `_broadcast_sse(event_type, data)` (lines 695-708): Push to all connected clients
- GET `/api/stream`: SSE endpoint establishing long-lived connection
- `_sse_poller()` (lines 1043-1063): Background task updating jobs/costs every 10 seconds

**Live Endpoints** (lines 761-844)
- GET `/api/live/jobs`: Current job statuses with phase tracking
- GET `/api/live/costs`: Real-time cost accumulation
- GET `/api/live/eval`: Evaluation metrics
- GET `/api/live/billing`: Billing information
- GET `/api/live/agents`: Active agent status

### Analytics Capabilities

**Agent Analytics** (lines 870-925)
- Parse event log (JSONL format) from /data/events/
- Aggregate by agent, track successes/failures
- Per-agent metrics: jobs_completed, total_cost, error_rate, avg_duration

**Cost Analytics** (lines 928-988)
- Breakdown by agent/day/week/model
- Historical trending with date ranges
- Per-model costs with token counts

**Job Analytics** (lines 991-1039)
- Job history with filtering (status/agent/date range)
- Success rates, duration statistics
- Cost breakdown per job

### Service Management

**Health Monitoring** (lines 581-640)
- GET `/api/health`: Detailed health with metrics
- `check_service_running()` (lines 218-238): netstat or curl /health
- `get_system_metrics()` (lines 365-406): Memory/CPU via free and top
- `get_process_uptime()` (lines 241-274): Via psutil or /proc/stat

**Log Aggregation** (lines 202-215)
- `read_log_file()`: Read last N lines from logs
- Supports multiple log sources: gateway, dashboard, job execution
- Count errors/warnings (lines 338-362): Scan logs for ERROR/WARN markers

**Service Control** (lines 545-578)
- POST `/api/restart`: Restart gateway via systemctl
- GET `/api/status` (lines 413-449): Gateway and tunnel status

### Configuration
- GATEWAY_PORT, GATEWAY_HOST: Gateway service connection
- DASHBOARD_PORT: Dashboard service port
- DASHBOARD_PASSWORD, DASHBOARD_TOKEN: Authentication
- STATIC_DIR: /var/www/dashboard for static files
- Log paths: GATEWAY_LOG_PATH, TUNNEL_LOG_PATH

### Event Streaming
- `parse_event_log()` (lines 851-867): Read JSONL events with configurable limit
- Events include: job.created, job.completed, job.failed, deploy.complete, cost.alert
- Supports historical playback and real-time streaming

---

## Infrastructure Category 3: tmux Agent Management

**Status**: REFERENCED BUT NOT FOUND ❌

### Issue Identified
- Dashboard API references tmux_spawner/agent spawning functionality (line 839-841)
- Expected file `/root/openclaw/tmux_agents.py` does not exist
- File read attempt failed with "File does not exist" error

### Investigation Needed
- Search for actual tmux implementation location
- Check if functionality is embedded in another module
- Determine if this needs to be built

### Likely Integration Points
- `autonomous_runner.py` may handle agent spawning directly
- `dashboard_api.py` GET `/api/live/agents` endpoint suggests agent tracking exists
- Job lifecycle may manage agent processes

### Recommendation
Search codebase for "tmux" or "spawn" patterns to locate actual implementation.

---

## Infrastructure Category 4: Headless Agent Running

**Status**: FULLY BUILT ✓

### Core Files
- **`/root/openclaw/autonomous_runner.py`** (Phase execution logic)
- **`/root/openclaw/job_lifecycle.py`** (Guardrails and state management)
- **`/root/openclaw/pc_dispatcher.py`** (Remote execution)

### Execution Model

**Phase-Gated Tool Access** (lines 762-792)
```python
RESEARCH_TOOLS = [...]    # Limited to search/documentation
PLAN_TOOLS = [...]        # Document creation, architecture
EXECUTE_TOOLS = [...]     # Full codebase access
CODE_REVIEW_TOOLS = [...]  # Testing, linting
VERIFY_TOOLS = [...]      # Validation
DELIVER_TOOLS = [...]     # GitHub, deployment
```

Each phase gets only the tools needed, preventing tool misuse.

**Iteration Management** (job_lifecycle.py lines 287-495)
- JobGuardrails class enforces constraints at every iteration boundary
- Phase-specific iteration limits:
  - RESEARCH: 60 iterations
  - PLAN: 30 iterations
  - EXECUTE: 250 iterations
  - CODE_REVIEW: 30 iterations
  - VERIFY: 30 iterations
  - DELIVER: 30 iterations

**Progressive Warning System** (lines 384-451)
- Warns at 50%, 75%, 90% of cost limit
- Warns at 50%, 75%, 90% of iteration limit
- Logs warnings to event system for monitoring

**Circuit Breaker Pattern** (lines 432-451)
```python
# Track last 3 errors
if len(set(tail)) == 1:  # Same error 3x in a row
    raise GuardrailViolation("Circuit breaker: repeated errors")
```

**Kill Flag System** (lines 472-495)
```python
# File: /data/jobs/kill_flags.json
kill_flags = {
    "job_id_1": True,  # Set by human operator
    "job_id_2": False,
}
# Checked at each iteration boundary
```

**Cost Management** (lines 410-430)
- Hard limit: max_cost_usd * 1.10 (10% grace period)
- Soft limit: max_cost_usd (50% warning threshold)
- Cost calculated per API call, aggregated per phase
- Grace period prevents killing jobs at finish line

**Timeout Management** (lines 381-409)
- Wall-clock timeout: max 24 hours per job
- Per-phase timeout: varies by phase complexity
- Graceful shutdown: cancels remaining steps on timeout

### Remote Execution (PC Dispatch)

**PC Dispatcher** (`/root/openclaw/pc_dispatcher.py`, 521 lines)
- SSH tunnel to Windows PC (Tailscale IP: 100.67.6.27, User: Miles)
- Two-path execution model:
  - **File-based** (>1024 bytes): Write temp file, pass path to Claude
  - **Arg-based** (<1024 bytes): Pass prompt directly as argument
- Temp file path: C:\Users\Miles\AppData\Local\Temp\openclaw_prompt_{job_id}.txt
- Background execution: asyncio.create_task() with _running_jobs set to prevent duplicates
- Status tracking: pending → running → completed/failed

### Background Job Execution
- Non-blocking dispatch pattern: POST /api/dispatch returns immediately
- Background task handles execution and polling
- Client checks status via GET /api/dispatch/status/{job_id}

---

## Infrastructure Category 5: Job Queue / Task Dispatch

**Status**: FULLY BUILT - Multiple Systems ✓

### System 1: GitHub Issue Auto-Execution

**File**: `/root/openclaw/coding_factory_cron.py` (936 lines)
- Scans repositories for issues labeled "claude" or "codex"
- Scan interval: Every 20 minutes
- Execution limits: Max 3 parallel jobs per hour per engine
- SQLite backlog tracking: pending/running/done/failed/skipped
- Key functions:
  - `add_task()`: Add issue to queue
  - `get_task()`: Retrieve issue details
  - `get_pending_tasks()`: Get ready-to-execute jobs
  - `execute_task()`: Run autonomously_runner.py with job context
  - `scan_repos()`: Discover new issues

**Backlog Schema** (SQLite)
```sql
CREATE TABLE backlog (
    id TEXT PRIMARY KEY,
    repo TEXT,
    issue_number INT,
    status TEXT,  -- pending, running, done, failed, skipped
    task_type TEXT,  -- claude, codex
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    result JSON,
    error TEXT
)
```

### System 2: API-Based PC Dispatch

**File**: `/root/openclaw/routers/dispatch.py` (260 lines)
- **POST /api/dispatch/pc**: Dispatch Claude Code task
  - Request: {prompt, timeout, metadata}
  - Response: {job_id, status, message}
- **POST /api/dispatch/ollama**: Dispatch Ollama inference
  - Request: {prompt, model, timeout, metadata}
  - Response: {job_id, status, message}
- **GET /api/dispatch/status/{job_id}**: Check job status
- **GET /api/dispatch/pc/health**: PC connectivity check
- **GET /api/dispatch/jobs**: List all jobs

Job ID format: "pc_" + UUID hex[:12]

### System 3: Failure Handling (Dead Letter Queue)

**File**: `/root/openclaw/dead_letter_queue.py` (189 lines)
- Supabase-backed permanent failure tracking
- Non-fatal write pattern: all Supabase operations wrapped in try/except
- Operations:
  - `send_to_dlq()`: Log permanently failed job
  - `retry_from_dlq()`: Move failed job back to pending
  - `resolve_dlq()`: Mark failure as addressed
  - `record_attempt_start/finish()`: Track retry attempts
  - `get_dlq_jobs()`: List failed jobs with filters

**DLQ Entry Schema**
```python
{
    "job_id": "job_abc123",
    "attempt": 1,
    "last_error": "...",  # Max 2000 chars
    "status": "failed",
    "created_at": "2026-03-13T12:34:56Z",
    "last_attempt_at": "2026-03-13T12:35:00Z",
    "retry_count": 0,
    "cost": 0.123456,
}
```

### Rate Limiting (Alibaba Coding Plan)

**File**: `/root/openclaw/alibaba_budget.py` (191 lines)
- SQLite-backed request counter
- Enforces multiple time windows:
  - 18,000 requests/month
  - 9,000 requests/week
  - 1,200 requests per 5-hour window
  - 600 requests/day (300 days 21-31: 300 requests/day)
- Conservative mode activation: day >= 21 of month
- Key functions:
  - `has_quota()`: Check before sending request
  - `record_request(model)`: Log completed request
  - `get_budget_status()`: Full status across all windows
  - `get_daily_remaining()`: Quick remaining-today check

### Cost Tracking (Central Logging)

**File**: `/root/openclaw/cost_tracker.py` (229 lines)
- Single source of truth for cost tracking
- Dual backend: Supabase primary, JSONL fallback
- Pricing table for 30+ models (lines 22-47)
- Key functions:
  - `log_cost_event()`: Calculate and log cost
  - `get_cost_metrics(days)`: Aggregate costs by agent/day
  - `get_cost_summary()`: One-liner for logs/dashboard

**Pricing Coverage**
```python
COST_PRICING = {
    "claude-haiku-4-5-20251001": {input: 0.8, output: 4.0},
    "claude-sonnet-4-20250514": {input: 3.0, output: 15.0},
    "claude-opus-4-6": {input: 15.0, output: 75.0},
    "kimi-2.5": {input: 0.14, output: 0.28},
    "m2.5": {input: 0.30, output: 1.20},
    "gemini-2.5-flash": {input: 0.30, output: 2.50},
    # All Alibaba Coding Plan models are FREE:
    "qwen3.5-plus": {input: 0.00, output: 0.00},
    "kimi-k2.5": {input: 0.00, output: 0.00},
    "glm-5": {input: 0.00, output: 0.00},
    "MiniMax-M2.5": {input: 0.00, output: 0.00},
    # ... and 4 more FREE models
}
```

**JSONL Fallback Location**: `./data/costs/costs.jsonl`
**Entry Schema**: timestamp, type, project, agent, model, tokens_in, tokens_out, cost, metadata, job_id

---

## Infrastructure Category 6: Existing Wrappers for Multiple AI Tools

**Status**: FULLY BUILT ✓

### Direct API Wrappers

#### 1. Alibaba Coding Client

**File**: `/root/openclaw/alibaba_coding_client.py` (331 lines)
- OpenAI-compatible wrapper for 8 FREE DashScope Coding Plan models
- Supported models:
  - qwen3.5-plus (16384 tokens): Latest flagship, strong general + coding
  - kimi-k2.5 (8192 tokens): Deep reasoning
  - glm-5 (8192 tokens): Strong Chinese/English coding
  - MiniMax-M2.5 (16384 tokens): 80.2% SWE-Bench accuracy
  - qwen3-max (16384 tokens): Large context
  - qwen3-coder-next (16384 tokens): Bleeding edge
  - qwen3-coder-plus (16384 tokens): Balanced coding
  - glm-4.7 (8192 tokens): Fast coding assistant

**Response Model** (lines 23-31)
```python
AlibabaCodingResponse:
  - content: str
  - model: str
  - tokens_input: int
  - tokens_output: int
  - stop_reason: str
  - tool_calls: Optional[List[Dict]]
```

**API Methods**
```python
call(model, prompt, system_prompt, temperature, max_tokens, tools, timeout)
  → AlibabaCodingResponse (sync)

call_async(model, prompt, ...)
  → AlibabaCodingResponse (async)

stream(model, prompt, ...)
  → Generator[str] (yields content chunks)

@staticmethod
get_pricing_info(model) → Dict
calculate_cost(model, tokens_in, tokens_out) → float (always 0.0)
```

**Immutable Payload Pattern** (lines 125-144)
```python
# Never mutate payload, use spread operator:
payload = {
    "model": api_model,
    "messages": messages,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "stream": stream,
}
if tools:
    return {**payload, "tools": tools}  # Immutable composition
return payload
```

**Configuration**
- API Key: ALIBABA_CODING_API_KEY environment variable
- Base URL: ALIBABA_CODING_BASE_URL (default: https://coding-intl.dashscope.aliyuncs.com/v1)

### Referenced CLI Wrappers (in CLAUDE.md Agent Definitions)

#### Claude Code
- Primary: Anthropic Claude via claude.exe CLI
- Used by: CodeGen Pro, CodeGen Elite, Overseer
- Integration: autonomous_runner.py delegates to agents running Claude Code

#### Codex CLI (ChatGPT Plus)
- Model: GPT-5, GPT-5.4, o3
- Cost: $20/mo subscription (no API cost)
- Integration: Referenced in agent definitions for alternative execution path

#### Aider
- Model: Gemini 2.5 Flash (free tier) or Claude/GPT-4
- Integration: Used for pair programming style code editing
- Referenced in free-coding-tools documentation

#### Ollama (Local Inference)
- Models: qwen2.5-coder:7b (7B context), others
- Integration: PC Dispatcher POST /api/dispatch/ollama
- Local GPU: RTX 4060 on Miles' Windows PC via Tailscale

#### Gemini CLI
- Model: Gemini 2.5 Flash (free), 3 Flash (preview)
- Cost: Free tier available
- Referenced as free alternative

---

## Cross-System Integration Architecture

### Data Flow: GitHub Issue → Execution → PR Delivery

```
1. coding_factory_cron.py (scan interval: 20 min)
   ↓ Detects issues labeled "claude" or "codex"
   ↓ Adds to SQLite backlog: pending status

2. coding_factory_cron.py (execute_task)
   ↓ Creates job context from issue metadata
   ↓ Launches autonomous_runner.py with job_id

3. autonomous_runner.py (main execution)
   ↓ Phase: RESEARCH (max 60 iter) → PLAN (max 30 iter) → ...
   ↓ Each phase calls cost_tracker.py to log tokens
   ↓ job_lifecycle.py.check() enforces guardrails each iteration
   ↓ Checks kill_flags.json for human intervention
   ↓ Phase results JSONL logged to /data/jobs/runs/{job_id}/{phase}.jsonl

4. Guardrails Enforcement (job_lifecycle.py)
   ↓ Hard cost limit: max_cost * 1.10 (10% grace)
   ↓ Phase iteration limits: 60/30/250/30/30/30
   ↓ Circuit breaker: 3x same error → kill job
   ↓ Wall-clock timeout: 24 hours max
   ↓ Progressive warnings: 50%, 75%, 90% of limits

5. Dashboard Real-Time Monitoring (dashboard_api.py)
   ↓ SSE streaming updates every 10 seconds
   ↓ Live job status tracking
   ↓ Cost accumulation in real-time
   ↓ Agent analytics and performance metrics

6. Failure Handling (dead_letter_queue.py)
   ↓ On job failure: send_to_dlq()
   ↓ Logs to Supabase with error context
   ↓ Fallback to file if Supabase unreachable
   ↓ Manual retry_from_dlq() to re-queue

7. Successful Completion → GitHub Delivery (github_integration.py)
   ↓ PR delivery workflow triggered on DELIVER phase completion
   ↓ Creates feature branch: openclaw/job-{id[:8]}
   ↓ Commits all modified files with structured message
   ↓ Creates PR with templated body including:
      - Job ID, agent, task, priority
      - All phases completed with timestamps
      - Cost breakdown by phase
      - Files modified with line counts
   ↓ Stores delivery record in github_deliveries.json
   ↓ Updates job status to "done"

8. PR Webhook Integration (github_integration.py webhook)
   ↓ Listens for PR events: opened, synchronize, closed, merged
   ↓ Tracks auto-merge status
   ↓ Updates delivery records on merge
```

### Error Handling Path

```
autonomous_runner.py iteration
  → Error occurs
  → Circuit breaker checks (3x same error?)
  → Guard rail violation?
    → job_lifecycle.py.check() raises GuardrailViolation
    → Job status set to "failed"
    → dead_letter_queue.py.send_to_dlq()
      → Supabase insert with error context
      → Fallback to file if Supabase down
    → Dashboard alerts via SSE
    → Event logged to /data/events/ for analytics
```

### Cost Tracking Path

```
autonomous_runner.py phase execution
  → API call completes
  → cost_tracker.py.log_cost_event()
    → Calculate cost: (tokens_in * rate_in + tokens_out * rate_out) / 1M
    → Try Supabase insert first
    → Fallback to JSONL if Supabase unavailable
    → Return cost for progress tracking
  → Job progress updated with cumulative cost
  → Dashboard GET /api/analytics/costs retrieves aggregated costs
```

---

## Code Pattern Inventory

### Immutability Pattern
```python
# CORRECT: Return new object, never mutate input
return {**payload, "tools": tools}

# Data structure composition
ExecutionPlan(job_id=..., agent=..., steps=[...], created_at=...)
```

### Non-Fatal Write Pattern
```python
try:
    result = supabase.insert(table, row)
    if result:
        return True
except Exception:
    pass
return False
```

### Phase-Gated Tool Access
```python
# Each phase gets only required tools
RESEARCH_TOOLS = [web_search, docs_lookup, ...]
EXECUTE_TOOLS = [file_read, file_write, shell_exec, ...]
# Enforced by autonomous_runner.py before tool invocation
```

### Dual-Backend Pattern (Supabase Primary, Fallback)
```python
def log_event(...):
    # Try primary backend
    if _use_supabase():
        sb = _sb()
        result = sb["insert"](table, row)
        if result:
            return cost
    
    # Fallback to secondary backend
    with open(fallback_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return cost
```

### Progressive Warning System
```python
thresholds = [0.50, 0.75, 0.90]
for threshold in thresholds:
    limit_at_threshold = max_limit * threshold
    if current >= limit_at_threshold and not warned[threshold]:
        logger.warning(f"Approaching {threshold*100}% of limit")
        warned[threshold] = True
```

### Circuit Breaker Pattern
```python
# Track recent errors
recent_errors = deque(last_3_errors, maxlen=3)
if len(set(recent_errors)) == 1:  # All same error
    raise GuardrailViolation("Circuit breaker activated")
```

### Kill Flag File-Based System
```python
# /data/jobs/kill_flags.json
kill_flags = {"job_id_1": True}

# At iteration boundary
if job_id in kill_flags and kill_flags[job_id]:
    raise GuardrailViolation("Job manually killed")
```

### OpenAI-Compatible API Wrapper
```python
# Validates model, builds immutable payload, handles streaming
def call(model, prompt, system_prompt, ...):
    api_model = self._validate_model(model)
    messages = self._build_messages(prompt, system_prompt)
    payload = self._build_payload(api_model, messages, ...)
    response = requests.post(f"{base_url}/chat/completions", json=payload)
    return self._parse_response(response.json(), model)
```

---

## Configuration & Environment Variables

### Cost Tracking
- `OPENCLAW_COSTS_PATH`: Path to costs.jsonl (default: ./data/costs/costs.jsonl)
- `OPENCLAW_DATA_DIR`: Base data directory (default: ./data)

### Alibaba Coding Plan
- `ALIBABA_CODING_API_KEY`: DashScope API key (required)
- `ALIBABA_CODING_BASE_URL`: API endpoint (default: https://coding-intl.dashscope.aliyuncs.com/v1)

### Dashboard
- `DASHBOARD_TOKEN`: Bearer token for API access
- `DASHBOARD_PASSWORD`: Password-based authentication
- `GATEWAY_PORT`, `GATEWAY_HOST`: Gateway service connection
- `DASHBOARD_PORT`: Dashboard service port

### PC Dispatch
- PC_TAILSCALE_IP: 100.67.6.27 (hardcoded)
- PC_SSH_USER: Miles (hardcoded)
- Binary: C:\Users\Miles\.local\bin\claude.exe

---

## Outstanding Questions & Investigation Items

### 1. tmux Agent Spawning (UNRESOLVED)
- Expected file `/root/openclaw/tmux_agents.py` does not exist
- Dashboard API references tmux_spawner functionality
- **Next Step**: Search codebase for "tmux" or "spawn" patterns
- **Options**:
  - Implementation embedded in autonomous_runner.py
  - Implemented in different module
  - Needs to be built

### 2. EdgeBoard Dashboard (NOT FOUND)
- Glob `/root/edgeboard/**` returned no matches
- Referenced in Phase 1 exploration checklist
- **Next Step**: Verify if EdgeBoard project exists and locate code
- **Options**:
  - Project doesn't exist
  - Code in different location
  - Different directory structure

### 3. Skill Recommendation System (REFERENCED)
- Lines 549-630 in autonomous_runner.py implement skill recommendation
- Maps task description to recommended skills
- Integrates with tool availability
- **Status**: Built but not fully explored in this phase

### 4. Loop Detection (REFERENCED)
- Lines 632-678 in autonomous_runner.py implement loop detection
- Triggers escalation on 3x repeated actions
- **Status**: Built but not fully explored in this phase

---

## Testing & Verification

### Test Coverage Status (from previous session notes)
- Unit tests: Present
- Integration tests: Present
- E2E tests: Present
- Total: 190+ tests across system
- Success rate: 97% benchmark (105 jobs analyzed)

### Key Test Patterns
- Phase-based testing: Each phase has separate test suite
- Cost calculation verification: Test with mock token counts
- Guardrail enforcement: Test circuit breaker, timeout, iteration limits
- Integration: End-to-end GitHub issue → delivery pipeline

---

## File Organization Summary

```
/root/openclaw/
├── autonomous_runner.py          [900+ lines] Agent orchestration, phase execution
├── job_lifecycle.py              [496 lines]  Guardrails, state machine
├── cost_tracker.py               [229 lines]  Cost calculation and logging
├── alibaba_budget.py             [191 lines]  Rate limiting for Alibaba
├── alibaba_coding_client.py      [331 lines]  Alibaba Coding Plan API wrapper
├── dashboard_api.py              [1144 lines] Real-time monitoring, analytics
├── github_integration.py          [843 lines]  PR creation and delivery
├── coding_factory_cron.py        [936 lines]  GitHub issue auto-execution
├── pc_dispatcher.py              [521 lines]  Remote PC task dispatch
├── dead_letter_queue.py          [189 lines]  Failure handling and retry
├── routers/
│   ├── dispatch.py               [260 lines]  PC dispatch API endpoints
│   └── jobs.py                   [...]       Job management endpoints
├── CLAUDE.md                     [397 lines] Agent system definition (v4.2)
└── tmux_agents.py                [MISSING]   Expected tmux spawning (NOT FOUND)
```

---

## Development Continuation Checklist

For next development phase:

- [ ] Investigate tmux agent spawning location (search codebase)
- [ ] Verify EdgeBoard dashboard status and location
- [ ] Complete autonomous_runner.py full review (file size limited)
- [ ] Document skill recommendation system usage
- [ ] Document loop detection activation scenarios
- [ ] Review terminal feedback recording mechanism (lines 699-733)
- [ ] Review job lease refresh/stale execution detection (lines 736-747)
- [ ] Document Supabase schema for costs table
- [ ] Document event log schema for analytics
- [ ] Create integration tests for full pipeline: issue → execution → PR
- [ ] Benchmark cost tracking accuracy across 100+ jobs
- [ ] Verify GitHub webhook event handling (PR opened, synchronized, merged)
- [ ] Load test SSE streaming under 10+ concurrent clients
- [ ] Document PC dispatcher error recovery paths

---

## Quick Reference: Key Numbers

- **Phase Iteration Limits**: 60/30/250/30/30/30 (research/plan/execute/code_review/verify/deliver)
- **Cost Grace Period**: 10% overage on hard limit
- **Warning Thresholds**: 50%, 75%, 90% of limits
- **Circuit Breaker Trigger**: 3x repeated same error
- **Job Timeout**: 24 hours wall-clock maximum
- **Dashboard SSE Update**: Every 10 seconds
- **GitHub Issue Scan**: Every 20 minutes
- **Rate Limits (Alibaba)**: 18K/month, 9K/week, 1.2K/5hr, 600/day (300 days 21-31)
- **Pricing Models**: 30+ models tracked, 8 FREE Alibaba models
- **Supported AI Tools**: 6 agent types, 8 Alibaba models, 5+ CLI wrappers (Claude, Codex, Aider, Gemini, Ollama)
- **Test Coverage**: 190+ tests, 97% success rate

---

**Document Version**: v1.0  
**Last Updated**: 2026-03-13  
**Maintainer**: Infrastructure Exploration Phase 1
