---
name: claude-code-remote-sessions
description: Remote, cloud, headless, Agent SDK
type: reference
---

# Claude Code Remote Sessions

## Remote Development Patterns

### Pattern 1: SSH Remote (VPS/Server)

**Use Case**: Develop on powerful server, local client lightweight

**Setup**:
```bash
# On server
ssh user@152.53.55.207
claude code --listen 0.0.0.0:3000  # Listen on all interfaces

# On local machine
claude code --connect 152.53.55.207:3000  # Connect to server
# Opens browser → localhost, connects to remote Claude Code
```

**Benefits**:
- Local machine stays light (no heavy compute)
- Server does compilation, testing
- Works on low-power devices (tablets, Chromebooks)
- GPU acceleration on remote machine

**Costs**:
- VPS: $5-50/mo (Northflank, DigitalOcean, AWS)
- Bandwidth: Usually included

**Typical Setup**:
```
Local laptop (8GB RAM)
    ↓ SSH tunnel ↓
152.53.55.207 VPS (32GB RAM, GPU)
    ↓
Claude Code runs here, executes tests/builds
    ↓
Results stream back to browser
```

### Pattern 2: Cloud Workspace (Hosted IDE)

**Services**:
- Replit (full IDE, Claude integration coming)
- GitHub Codespaces (VS Code in browser)
- Vercel.com cloud (Next.js optimized)
- Modal Labs (serverless compute)

**Setup Example (GitHub Codespaces)**:
```bash
# Push code to GitHub
git push origin main

# Open GitHub, click "Code" → "Codespaces" → "Create"
# VS Code opens in browser

# Install Claude Code
npm install -g @anthropics/claude-code

# Run remotely
claude code
```

**Benefits**:
- Instant environment (no setup)
- Works anywhere (browser-based)
- Built-in git integration
- Scales on demand

**Costs**:
- GitHub Codespaces: $0.18/hour (120/mo free)
- Replit Pro: $10/mo
- Vercel: Free-tier (or $20+ for pro)

### Pattern 3: Headless Mode (Automation)

**Use Case**: Agent runs Claude Code without GUI

**Setup**:
```bash
# Enable headless
export CLAUDE_HEADLESS=1
claude code --task "fix the auth bug"
```

**What Happens**:
1. No browser window opens
2. Claude Code executes task autonomously
3. Makes file edits, runs tests, commits
4. Returns result (success/failure + logs)

**Ideal For**:
- CI/CD pipelines
- Scheduled maintenance
- Autonomous agents
- Batch processing

**Example (CI/CD Integration)**:
```yaml
# GitHub Actions workflow
name: Auto-fix tests
on: [push]
jobs:
  fix-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          export CLAUDE_HEADLESS=1
          export ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}
          claude code --task "fix failing tests"
      - run: git commit -am "Auto-fix from Claude" || true
      - run: git push || true
```

**Cost**: Only API calls (no GUI overhead)

## Agent SDK Integration

### What Is Agent SDK
Claude's official framework for building autonomous agents.

**Install**:
```bash
pip install anthropic
```

### Basic Agent Using Claude Code

```python
from anthropic import Anthropic

client = Anthropic()

def code_agent(task: str):
    """Autonomous agent that uses Claude Code"""

    messages = [
        {
            "role": "user",
            "content": f"""
You are an autonomous code agent.
Your task: {task}

You have access to:
- File system (read/write)
- Git (commit, branch)
- Testing (run tests locally)
- Shell (execute commands)

Complete the task, then summarize what you did.
"""
        }
    ]

    response = client.messages.create(
        model="claude-3-5-sonnet",
        max_tokens=4096,
        messages=messages
    )

    return response.content[0].text

# Use it
result = code_agent("Add type hints to all functions in src/")
print(result)
```

### Advanced: Multi-Turn Agent

```python
def multi_turn_agent(initial_task: str):
    """Agent that can iterate, request clarification, etc."""

    messages = []

    # Initial task
    messages.append({
        "role": "user",
        "content": f"Task: {initial_task}"
    })

    # First response
    response = client.messages.create(
        model="claude-3-5-sonnet",
        max_tokens=2048,
        messages=messages
    )

    agent_response = response.content[0].text
    messages.append({"role": "assistant", "content": agent_response})
    print(f"Agent: {agent_response}\n")

    # User feedback loop
    for i in range(3):  # Allow 3 rounds of refinement
        user_feedback = input("You: ")
        if user_feedback.lower() in ["done", "looks good", "ok"]:
            break

        messages.append({"role": "user", "content": user_feedback})

        response = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=2048,
            messages=messages
        )

        agent_response = response.content[0].text
        messages.append({"role": "assistant", "content": agent_response})
        print(f"Agent: {agent_response}\n")

    return messages
```

### With Tool Use (Execute Code)

```python
import subprocess

def code_agent_with_tools(task: str):
    """Agent that can execute code, tests, git commands"""

    messages = [{
        "role": "user",
        "content": f"""
Task: {task}

You can:
- Read files: cat_file(path)
- Write files: write_file(path, content)
- Run tests: run_tests()
- Commit: git_commit(message)
- Execute shell: execute(command)

Always verify your work before declaring done.
"""
    }]

    response = client.messages.create(
        model="claude-3-5-sonnet",
        max_tokens=4096,
        tools=[
            {
                "name": "cat_file",
                "description": "Read file contents",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    }
                }
            },
            {
                "name": "run_tests",
                "description": "Run test suite",
                "input_schema": {"type": "object"}
            },
            # ... more tools
        ],
        messages=messages
    )

    return response
```

## Deployment Strategies

### Strategy 1: OpenClaw VPS

**Current Setup**:
```
152.53.55.207 (Cloudflare VPS)
├── Gateway (port 18789)
├── OpenClaw PA worker
├── Claude Code (headless)
└── Ollama (local LLM)
```

**Optimal for OpenClaw PA**:
```bash
# On VPS
export ANTHROPIC_API_KEY=sk-...
export CLAUDE_HEADLESS=1
claude code --daemon --task-file /tmp/tasks.json
```

### Strategy 2: Modal Labs Serverless

**Ideal for**: Burst workloads (don't need always-on)

```python
import modal

app = modal.App("code-agent")

@app.function(
    image=modal.Image.debian_slim().pip_install("anthropic"),
    timeout=600
)
def run_code_agent(task: str):
    from anthropic import Anthropic
    client = Anthropic()

    response = client.messages.create(
        model="claude-3-5-sonnet",
        max_tokens=4096,
        messages=[{"role": "user", "content": task}]
    )

    return response.content[0].text

@app.local_entrypoint()
def main(task: str):
    result = run_code_agent.remote(task)
    print(result)
```

**Cost**: $0.10/GPU-hour (vs. $50/mo VPS, good for bursty)

### Strategy 3: Vercel Edge Functions

**Ideal for**: Lightweight agents, fast response

```typescript
// api/code-agent.ts (Vercel Edge Function)
import { Anthropic } from "@anthropic-ai/sdk";

export const runtime = "edge";

export default async function handler(request: Request) {
  const { task } = await request.json();

  const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  const response = await client.messages.create({
    model: "claude-3-5-sonnet",
    max_tokens: 1024,
    messages: [{ role: "user", content: task }],
  });

  return new Response(JSON.stringify({
    result: response.content[0].type === "text"
      ? response.content[0].text
      : ""
  }));
}
```

**Cost**: Free tier (100k calls/mo), then $0.50/M calls

## Cost Comparison

| Method | Startup | Monthly | Best For |
|--------|---------|---------|----------|
| Local Claude Code | $0 | $0 | Learning |
| Remote VPS | $0 | $5-50 | OpenClaw |
| GitHub Codespaces | $0 | $20 | Teams |
| Modal Serverless | $0 | $50-500 | Burst workloads |
| Vercel Edge | $0 | $0-100 | Lightweight API |

## For OpenClaw PA

### Recommended Architecture
```
PA Agent (headless, VPS)
├── Task 1: Code review (use Claude Haiku, fast)
├── Task 2: Bug fix (use Sonnet, medium)
└── Task 3: Architecture (use Opus, slow but good)

All via Agent SDK → remote Claude Code instance
Cost: ~$10-20/mo for unlimited tasks
```

### Setup
```bash
# VPS: /root/openclaw/pa_agent.py
from anthropic import Anthropic
import subprocess

def pa_code_task(task_description, budget_cents=50):
    """Run code task via Agent SDK + Claude Code"""

    client = Anthropic()

    # Choose model based on budget
    if budget_cents < 10:
        model = "claude-3-haiku"
    elif budget_cents < 30:
        model = "claude-3-5-sonnet"
    else:
        model = "claude-3-5-opus"

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""
You are PA's coding assistant.
Budget: {budget_cents} cents.
Task: {task_description}

Complete efficiently.
"""
        }]
    )

    return response.content[0].text
```

## Monitoring & Logging

### Log All Agent Runs
```python
import json
from datetime import datetime

def log_agent_run(task, result, cost_cents, duration_seconds):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "result": result[:200],  # Summary
        "cost_cents": cost_cents,
        "duration_seconds": duration_seconds,
        "status": "success" if "error" not in result.lower() else "failure"
    }

    with open("/var/log/pa_agent_runs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### Dashboard Query
```bash
# Summary of last 7 days
jq 'select(.timestamp > now-7*24*60*60) | .status' /var/log/pa_agent_runs.jsonl \
  | sort | uniq -c

# Total cost
jq '.cost_cents' /var/log/pa_agent_runs.jsonl | awk '{s+=$1} END {print s " cents"}'
```

## Key Takeaways

1. **Headless mode** = Autonomous agents (perfect for PA)
2. **Remote sessions** = Powerful compute, light client
3. **Agent SDK** = Multi-turn conversations with Claude
4. **Tool use** = Execute code during reasoning
5. **Cost optimization** = Haiku for simple, Sonnet for medium, Opus for hard
