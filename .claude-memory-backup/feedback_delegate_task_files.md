---
name: feedback_delegate_task_files
description: Delegate work to other AI tools via TASK files, not direct invocation
type: feedback
---

# Delegate via TASK Files

## Decision
When delegating work to Codex (GPT-5), Gemini CLI, or other external AI tools:
**Create a TASK-*.md file with instructions instead of invoking the tool directly**.

## Why
- Miles runs Codex/Gemini manually on his Windows PC
- He controls when and what runs (cost control, focus)
- Direct invocation from VPS would bypass his oversight
- TASK files allow async handoff and explicit review

## How to Apply

### Example Workflow
1. Identify work suitable for another AI (GPT-5, Gemini, Aider)
2. Create `/root/TASK-[name]-[date].md` with:
   - Clear objective
   - Context (relevant code/docs)
   - Acceptance criteria
   - Links to related files
3. Reference the TASK file in commit message
4. Miles picks it up manually when ready

### TASK File Template
```
# TASK: [Brief Title]

## Objective
[What needs to be done]

## Context
[Relevant background, file paths]

## Acceptance Criteria
- [ ] Specific outcome 1
- [ ] Specific outcome 2

## Tool Recommendation
[Codex / Gemini CLI / Aider - justify choice]

## Notes
[Edge cases, performance considerations]
```

## Tools to Delegate To
- **Codex (GPT-5)**: Complex refactoring, analysis
- **Gemini CLI**: Quick builds, free tier
- **Aider**: Code editing, interactive sessions
- **Ollama**: Local inference on PC

## Tools NOT to Delegate
- Claude Code on VPS (keep for system tasks)
- Direct file modifications in /root/openclaw
- Production deployments

---

See: feedback_ship_use_cases.md (sibling file)
