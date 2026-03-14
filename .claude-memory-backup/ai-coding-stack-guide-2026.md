---
name: ai-coding-stack-guide-2026
description: Full stack - Claude Code + Codex + Gemini + Aider
type: reference
---

# AI Coding Stack Guide 2026

## Full Stack Overview

Optimal setup combines 4 tools for maximum coverage and cost efficiency.

## 1. Claude Code (Anthropic)

### What It Is
- Official Claude IDE (terminal + web)
- Installed locally, connects to Claude API
- Full codebase awareness, running tests, git integration

### Specs
- **Cost**: $200/mo (Claude Opus 4.6, Max Plan)
- **Model**: Claude 3.5 Sonnet (most use), Claude Opus for complex
- **Quality**: 95%+ accuracy
- **Speed**: 1-3 minutes per task

### Use Cases
1. **Complex architecture work** (designing systems)
2. **Multi-file refactoring** (coordinating changes)
3. **Bug investigation** (debugging subtle issues)
4. **Code review** (finding patterns/issues)

### Setup
```bash
git clone https://github.com/anthropics/claude-code
cd claude-code
npm install
npm start  # Opens http://localhost:3000
```

### Cost Optimization
- Use Sonnet for 90% of tasks ($0.003/1K tokens input)
- Reserve Opus for 10% of hard problems ($0.015/1K tokens)
- Estimated monthly: $30-50 actual usage (not $200)

## 2. Codex CLI (GPT-5, via ChatGPT Plus)

### What It Is
- Terminal CLI for GPT-5 (newer model, different strengths)
- Better at certain patterns than Claude
- Faster for code generation

### Specs
- **Cost**: $20/mo (ChatGPT Plus)
- **Model**: GPT-5 (latest), GPT-4 Turbo as fallback
- **Quality**: 90%+ accuracy (different areas than Claude)
- **Speed**: 2-5 minutes per task (slower, more thorough)

### Use Cases
1. **Code generation from scratch** (greenfield projects)
2. **Leetcode-style problem solving**
3. **API integration** (often faster than Claude)
4. **TypeScript/React** (GPT-5 is strong here)

### Setup
```bash
npm install -g @openai/cli
export OPENAI_API_KEY=your_key
codex --help
```

### Strengths vs. Claude
- **GPT-5 better at**: Frontend (React, CSS), complex logic puzzles, API design
- **Claude better at**: Debugging, refactoring, system design, writing

## 3. Gemini CLI (Google)

### What It Is
- Free CLI tool using Gemini 2.5 Flash
- Lightweight, good for quick tasks
- Rate limited but free tier is generous

### Specs
- **Cost**: Free (15K calls/day limit)
- **Model**: Gemini 2.5 Flash (fast), Gemini 2.0 Pro (slower)
- **Quality**: 80-85% accuracy
- **Speed**: 30 seconds - 2 minutes

### Use Cases
1. **Quick bug fixes** (small targeted edits)
2. **Documentation writing**
3. **Code review suggestions**
4. **Daily routine tasks** (pre-review before Claude)

### Setup
```bash
pip install google-generativeai
export GOOGLE_API_KEY=your_key
gemini "write a Python sort function"
```

### Free Tier Strategy
- Use for first pass (quick review)
- If quality is good (80%+), keep it
- If quality is low, escalate to Claude or Codex
- Result: 70% of tasks solved free

## 4. Aider (Multi-Backend)

### What It Is
- Specialized tool for multi-file editing
- Works with Claude, GPT, or Ollama backend
- Best for test-driven development

### Specs (varies by backend)
- **Cost**: $0-200/mo depending on backend
- **Models**: Claude 3.5, GPT-5, Qwen 2.5 (local)
- **Quality**: 90%+ (Claude backend)
- **Speed**: 2-10 minutes

### Use Cases
1. **Test-driven development** (write test, generate code, run tests)
2. **Refactoring** (coordinate changes across files)
3. **Feature implementation** (guided by tests)
4. **Large codebase changes** (maintains consistency)

### Setup
```bash
pip install aider-chat
aider --model claude-3-5-sonnet  # Or gpt-4, or ollama/...
```

### Workflow Example
```
aider> Write a test for calculating user age
aider> Implement the function
aider> Run the tests
aider> Refactor for performance
aider> Add error handling
```

## Optimal Stack Distribution

### By Task Type

| Task | Tool | Reason | Cost |
|------|------|--------|------|
| Small fix | Gemini | Free, fast | $0 |
| Bug investigation | Claude Code | Full context | $0.01 |
| Feature implementation | Aider | Tests guide | $0.02 |
| Code generation | Codex CLI | Strongest | $0.02 |
| Design/architecture | Claude Code | Best reasoning | $0.05 |
| API integration | Codex + Claude | Compare approaches | $0.04 |

### Monthly Cost Estimate

**Conservative Stack** (focus on free + Claude):
- Gemini CLI: Free (15K calls)
- Claude Code: ~$50 actual usage
- Codex CLI: $20/mo (keep active)
- Aider: $0 (use free Gemini backend)
- **Total**: $70/mo

**Professional Stack** (maximize quality):
- All four tools active
- Claude Code: $100 actual usage
- Codex CLI: $20/mo
- Gemini: Free
- Aider: $20/mo (premium backend)
- **Total**: $140/mo

**Budget Stack** (all free):
- Ollama local (free)
- Gemini CLI (free)
- Aider with Ollama backend
- No premium tools
- **Total**: $0/mo (+ 1-time hardware)

## Decision Tree for Choosing Tool

```
1. Is task < 5 minutes?
   → Try Gemini CLI (free)

2. Is it debugging or architectural?
   → Use Claude Code

3. Is it code generation from scratch?
   → Use Codex CLI

4. Do you need tests + refactoring?
   → Use Aider

5. Is it a routine/daily task?
   → Pre-filter with Gemini, escalate if needed

6. Are you learning or prototyping?
   → Use Ollama (local, free)
```

## Integration Strategy for OpenClaw PA

### Routing Logic
```python
if complexity == "trivial":
    use("gemini-cli")  # Free, fast
elif complexity == "small":
    use("aider-with-ollama")  # Free, working tests
elif complexity == "medium":
    use("claude-code")  # Best all-rounder
elif complexity == "hard":
    use("claude-code")  # With Opus model
elif task_type == "code-gen":
    use("codex-cli")  # GPT-5 best at generation
else:
    use("aider-with-claude")  # Multi-file + tests
```

### Cost Control
- **Monthly budget**: $100 actual usage
- **Per-task limit**: $1 max
- **Free first**: Always try Gemini free tier first
- **Escalation**: Only use expensive tools if needed

## Real-World Example: Adding Feature

**Task**: Add user authentication to Django app

**Steps**:
1. **Pre-review with Gemini** (free): "Outline auth approach" → 1min
2. **Write test with Aider** ($0.01): "Create test for login endpoint" → 3min
3. **Implement with Codex** ($0.02): "Create login view function" → 2min
4. **Refactor with Claude Code** ($0.01): "Security review + optimization" → 3min
5. **Run tests + debugging** (Aider): "Debug failing test" → $0.01
6. **Final review** (Gemini free): "Check for vulnerabilities" → 1min

**Total time**: 10 minutes
**Total cost**: $0.05 (vs. $200/mo if using only Claude)

## Recommended for Miles

1. **Keep Claude Code** ($200/mo plan, ~$50 actual)
2. **Add Codex CLI** ($20/mo, very different strengths)
3. **Use Gemini CLI** (free, pre-filter tasks)
4. **Setup Aider** (with Ollama locally, free)
5. **Monitor spend** (track actual vs. budget monthly)

**Expected**: $70/mo total, 90% task coverage
