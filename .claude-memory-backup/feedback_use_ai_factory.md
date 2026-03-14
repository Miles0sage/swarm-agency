---
name: Use AI Factory not OpenClaw MCP
description: Dispatch grunt work to AI Factory (factory.py) in background, never use mcp__openclaw__claude_code_build for code generation
type: feedback
---

Dispatch grunt work (code gen, script writing, boilerplate) to AI Factory — NOT OpenClaw MCP tools.

**Why:** User built the factory specifically for parallel background dispatch. OpenClaw MCP tools like `claude_code_build` are synchronous, slow, and expensive. The factory dispatches to cheap workers (Alibaba Qwen at $0.14/M tokens) in background.

**How to apply:**
- Import from `/root/ai-factory/factory.py`
- Use `Task` dataclass: `Task(id=make_task_id(), prompt="...", worker=WorkerType.ALIBABA, cwd="/root/openclaw")`
- Dispatch with: `asyncio.run(dispatch_parallel([task1, task2]))`
- Run in background Bash task so I don't block waiting
- Collect output from `data/logs/{task_id}.json`
- CLI shortcut: `python3 /root/ai-factory/factory.py alibaba "prompt here"`
- Available workers: `CLAUDE_CODE`, `CODEX`, `ALIBABA`, `MINIMAX`, `AIDER`
- NEVER use `mcp__openclaw__claude_code_build` or `mcp__openclaw__codex_build` for code gen tasks
