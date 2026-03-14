---
name: AI Factory Stack Guide
description: Complete guide to all AI coding agents, their strengths, how to assign tasks, error patterns, and the multi-model factory setup
type: reference
---

# AI Factory — Master Stack Guide

**Repo:** github.com/Miles0sage/ai-factory (private)
**Dashboard:** `python /root/ai-factory/dashboard.py` → port 8899
**CLI:** `python /root/ai-factory/factory.py <worker> "prompt" [model]`

---

## THE STACK ($240/mo total)

| # | Agent | Plan | Cost | Headless Command |
|---|-------|------|------|-----------------|
| 1 | **Claude Code** (Opus 4.6) | Anthropic Max 20x | $200/mo | `claude -p "prompt" --output-format json --allowedTools "Bash,Read,Edit"` |
| 2 | **Codex CLI** (GPT-5.4) | OpenAI Plus | $20/mo | `codex exec --full-auto --json "prompt"` |
| 3 | **Alibaba Coding Plan** (7 models) | Lite | $10/mo | API: `POST coding-intl.dashscope.aliyuncs.com/v1/chat/completions` |
| 4 | **MiniMax** (M2.5) | Starter | $10/mo | API: `POST api.minimax.io/v1/chat/completions` |
| 5 | **Aider** | Free | $0 | `aider --yes -m "prompt" file.py` (needs build fix on VPS) |
| 6 | **Claude Squad** | Free | $0 | `claude-squad` TUI for parallel agents |
| 7 | **Copilot** (in VS Code) | Free w/ plan | $0 | Autocomplete only, not headless |

---

## WHAT EACH AGENT IS GOOD AT

### Claude Code Opus 4.6 — THE BRAIN
- **Best at:** Complex architecture, multi-file refactors, orchestration, planning, code review
- **Use for:** Tasks needing deep reasoning, cross-file understanding, tool use (Bash/Read/Edit)
- **Weakness:** Most expensive per-token, slower than API models
- **Assign:** Orchestrator role, final review, complex debugging, system design

### Codex CLI (GPT-5.4) — THE EXECUTOR
- **Best at:** Quick autonomous edits, running shell commands, file operations
- **Use for:** Simple bug fixes, running tests, file operations, scripted tasks
- **Weakness:** Less nuanced reasoning than Opus, can be overly literal
- **Assign:** Grunt work — run tests, simple edits, shell automation, CI tasks

### Alibaba Qwen 3.5 Plus — CHEAP GENERALIST
- **Best at:** General coding, 1M context window (huge files), vision-capable
- **Use for:** Code generation, explaining code, large file analysis, research
- **Models:** qwen3.5-plus (flagship), qwen3-max (reasoning), qwen3-coder-plus/next (code)
- **Weakness:** Slightly below Opus quality, 18K req/mo limit
- **Assign:** Worker tasks, first-draft code generation, documentation

### Alibaba Kimi K2.5 — RESEARCH + VISION
- **Best at:** 262K context, vision, web browsing capability
- **Use for:** Code review with screenshots, analyzing large codebases, research
- **Weakness:** Slower than Qwen models
- **Assign:** Code review, visual tasks, long-context analysis

### Alibaba GLM-5 — CHINESE + ENGLISH
- **Best at:** Bilingual tasks, 202K context
- **Use for:** Chinese API docs, Alibaba Cloud integration, general coding
- **Assign:** Tasks involving Chinese documentation or APIs

### MiniMax M2.5 — THE DARK HORSE
- **Best at:** SWE-Bench 80.2% (within 0.6% of Opus!), Multi-SWE-Bench LEADER at 51.3%
- **Use for:** Multi-file software engineering tasks, complex bug fixes, refactoring
- **Weakness:** Smaller ecosystem, less tool-use experience
- **Assign:** Complex coding tasks that don't need tool use, second opinion on hard bugs
- **Key insight:** Best price-to-performance ratio in the stack. Nearly Opus-level at 1/20th cost.

### MiniMax M2.5 Highspeed — FAST WORKER
- **Best at:** Same quality as M2.5 but faster inference
- **Use for:** Time-sensitive coding tasks, rapid iteration
- **Assign:** When speed matters more than cost

---

## TASK ASSIGNMENT RULES

```
PLANNING / ARCHITECTURE  → Claude Code Opus (unlimited Max plan)
COMPLEX MULTI-FILE BUGS  → Claude Code Opus OR MiniMax M2.5
CODE GENERATION          → Alibaba qwen3-coder-plus (cheapest)
CODE REVIEW              → MiniMax M2.5 (near-Opus quality, cheap)
RESEARCH / ANALYSIS      → Alibaba qwen3.5-plus (1M context)
TESTING / CI             → Codex CLI (fast, autonomous)
SIMPLE EDITS             → Codex CLI (--full-auto)
SHELL AUTOMATION         → Codex CLI
SECOND OPINION           → MiniMax M2.5 (different model = different perspective)
VISION / SCREENSHOTS     → Alibaba kimi-k2.5 or qwen3.5-plus
LARGE CODEBASE SCAN      → Alibaba qwen3.5-plus (1M tokens)
```

---

## PARALLEL EXECUTION PATTERN

From inside Claude Code (this session), dispatch workers:
```python
# Python — asyncio.gather for parallel
from factory import Task, WorkerType, dispatch_parallel

tasks = [
    Task(id="t1", prompt="Fix auth bug", worker=WorkerType.ALIBABA, model="qwen3-coder-plus"),
    Task(id="t2", prompt="Write tests", worker=WorkerType.CODEX),
    Task(id="t3", prompt="Review security", worker=WorkerType.MINIMAX),
]
results = await dispatch_parallel(tasks)
```

From CLI:
```bash
# Run 3 workers in parallel via background jobs
python factory.py alibaba "generate helper functions" &
python factory.py codex "run pytest" &
python factory.py minimax "review the auth module" &
wait
```

---

## API KEYS & ENDPOINTS

| Provider | Key Env Var | Base URL |
|----------|------------|----------|
| Anthropic | (Max plan, auto) | https://api.anthropic.com |
| OpenAI | CODEX_API_KEY | https://api.openai.com/v1 |
| Alibaba | ALIBABA_CODING_API_KEY=sk-sp-7424af93... | https://coding-intl.dashscope.aliyuncs.com/v1 |
| MiniMax | MINIMAX_API_KEY=(get from platform.minimax.io) | https://api.minimax.io/v1 |

**MiniMax also supports Anthropic protocol:** https://api.minimax.io/anthropic/v1

---

## BUDGET MANAGEMENT

| Provider | Limit | Daily Budget | Strategy |
|----------|-------|-------------|----------|
| Anthropic Max | Unlimited* | N/A | Use for orchestration, complex tasks |
| OpenAI Plus | Unlimited* | N/A | Use for quick autonomous tasks |
| Alibaba Lite | 18K req/mo, 9K/week, 1.2K/5hr | ~600/day | Use for worker tasks, code gen |
| MiniMax Starter | 100 prompts/5hr (~1500 req/5hr) | ~7200 req/day | Use for reviews, complex coding |

*Subject to rate limits, not hard caps

**Priority order when budget is low:** Codex (unlimited) → MiniMax → Alibaba → Claude Code

---

## ERROR PATTERNS & REFLECTION

### Common Failures — ALWAYS Check These
1. **Alibaba "model not supported"** → Wrong model name. Use exact IDs from ALIBABA_MODELS list
2. **Codex hangs** → Task too vague. Be specific: "in file X, change Y to Z"
3. **Claude Code timeout** → Task too broad. Break into smaller subtasks
4. **MiniMax API key invalid** → Coding plan key vs general key are different
5. **Rate limit hit** → Check budget with `/api/stats`. Fall back to another worker
6. **Aider build failure** → Known issue on VPS. Use Codex or Alibaba instead

### Reflection Protocol — After Every Complex Task
1. Did the right worker get assigned? (Was Opus wasted on a simple task?)
2. Could this have been parallelized? (Multiple subtasks → dispatch_parallel)
3. Did any worker fail? Why? Log the pattern
4. Was the budget efficient? (Check /api/stats)
5. What would make this faster next time?

### Anti-Patterns — NEVER Do These
- DON'T use Claude Code Opus for simple code generation (use Alibaba/MiniMax)
- DON'T run sequential tasks that could be parallel
- DON'T retry the same failing prompt — analyze why it failed first
- DON'T burn Alibaba budget on tasks Codex can do (shell commands, simple edits)
- DON'T forget to check budget before dispatching Alibaba/MiniMax tasks

---

## SETUP ON NEW SESSION

Every Claude Code session should know:
1. AI Factory is at `/root/ai-factory/`
2. Dashboard: `python /root/ai-factory/dashboard.py` (port 8899)
3. CLI: `python /root/ai-factory/factory.py <worker> "prompt"`
4. 4 working workers: claude_code, codex, alibaba, minimax
5. Assign tasks based on the rules above
6. Always reflect on errors and update this guide
