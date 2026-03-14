# Launch Posts — swarm-agency

## Reddit: r/MachineLearning

**Title:** 43 AI personas that debate across 5 model families — use as markdown rules or Python SDK ($10/mo flat)

**Body:**

I built swarm-agency because every multi-agent framework I tried (CrewAI, AutoGen, LangGraph) runs on one model. When GPT-4 is wrong, 5 GPT-4 agents are wrong the same way. That's an echo chamber, not a debate.

**What it does:** 43 AI personas across 10 departments (Strategy, Finance, Engineering, Legal, etc.) debate your business decisions. Each agent runs on a different LLM model family (GLM, Qwen, Kimi, MiniMax) through Alibaba DashScope's $10/mo flat plan.

**Two ways to use it:**

1. **No code needed** — Copy any of the 43 markdown persona files into Claude Code, Cursor, Windsurf, Aider, or Gemini CLI. Each file has the agent's expertise, bias, and decision-making style baked in.

2. **Python SDK** — Run multi-model debates programmatically. Get structured output with votes, confidence scores, reasoning, and dissenting views.

**Key difference from CrewAI/AutoGen:** Different training data → different reasoning patterns → uncorrelated errors → better signal. A CFO agent on Qwen catches financial risks that the same prompt on GPT-4 misses, because the models were trained on different data.

**What you get:**
- 5 built-in demo scenarios (no API key needed)
- Live web UI at swarm-agency.streamlit.app
- Rich CLI with panels, tables, confidence bars
- Decision Memory that tracks outcomes over time
- Self-improving agents that adjust confidence based on track record

GitHub: https://github.com/Miles0sage/swarm-agency

---

## Reddit: r/LocalLLaMA

**Title:** Built a multi-model debate framework using 5 Chinese model families for $10/mo — 43 agents, works as standalone markdown personas too

**Body:**

Made this for people who want diverse AI opinions without the OpenAI tax.

swarm-agency runs 43 AI personas across GLM (Zhipu), Qwen (Alibaba), Kimi (Moonshot), and MiniMax — all through Alibaba DashScope's Coding Plan at $10/mo flat. That gets you 1,200 requests per 5-hour window, which is basically unlimited for debate-style queries.

**Why Chinese models?** Not political — it's practical. Different training corpora = genuinely different reasoning patterns. When you ask "should we pivot B2C to B2B?", a GLM agent and a Kimi agent catch different risks because they learned from different data. That's the whole point of multi-model.

**No Python required** — each agent is a standalone markdown file you can drop into Claude Code, Cursor, Windsurf, Aider, or Gemini CLI. The CFO persona makes your AI think like a CFO. The General Counsel makes it think like a lawyer.

Try the demos: `pip install swarm-agency[cli] && swarm-agency --demo startup-pivot`

Or just browse the personas: https://github.com/Miles0sage/swarm-agency/tree/main/agents

GitHub: https://github.com/Miles0sage/swarm-agency

---

## Hacker News

**Title:** Show HN: Swarm Agency – 43 AI agents debate decisions across 5 model families ($10/mo)

**Body:**

Multi-agent frameworks like CrewAI and AutoGen run all agents on the same model, which means correlated errors. swarm-agency runs 43 personas across 5 model families (GLM, Qwen, Kimi, MiniMax) via Alibaba DashScope for $10/mo flat.

Two usage modes:

1. Standalone markdown personas — copy `agents/finance/cfo.md` into your `.cursorrules` or `.claude/agents/` and your AI thinks like a CFO. No Python.

2. Python SDK — run debates programmatically. Each agent votes YES/NO/MAYBE with confidence and reasoning. Framework tallies votes, identifies consensus or disagreement, surfaces dissenting views.

Live demo (no API key): https://swarm-agency.streamlit.app

CLI demo: `swarm-agency --demo startup-pivot`

Why multi-model matters: when a CFO agent on Qwen says "the unit economics don't work" and the same prompt on GLM says "the market timing is wrong," you're getting genuinely independent analysis instead of the same model agreeing with itself 5 times.

https://github.com/Miles0sage/swarm-agency

---

## Twitter/X Thread

**Tweet 1:**
Built swarm-agency: 43 AI personas debate your business decisions across 5 model families.

Not another CrewAI clone. Different models = uncorrelated errors = better signal.

$10/mo flat. Works as markdown rules in any AI tool, or as a Python SDK.

🔗 github.com/Miles0sage/swarm-agency

**Tweet 2:**
The problem with multi-agent frameworks:

CrewAI → 5 GPT-4 agents = echo chamber
AutoGen → same model, same biases

swarm-agency → GLM + Qwen + Kimi + MiniMax debating each other

When GPT-4 is wrong, 5 GPT-4s are wrong the same way. Different models aren't.

**Tweet 3:**
Zero code usage:

1. Copy agents/finance/cfo.md into .cursorrules
2. Your AI now thinks like a CFO

43 personas across 10 departments:
Strategy, Product, Marketing, Research, Finance, Engineering, Legal, Operations, Sales, Creative

Each one has expertise, bias, and decision-making style built in.

**Tweet 4:**
Live demo — no API key needed:

swarm-agency.streamlit.app

Pick a scenario:
• Pivot B2C → B2B?
• Senior vs 2 juniors?
• Usage-based pricing?
• Open-source core?
• Return to office?

5 AI agents debate it in real time.

**Tweet 5:**
Cost comparison:

OpenAI multi-agent: $50-200/mo
Anthropic multi-agent: $100-400/mo
swarm-agency (DashScope): $10/mo flat

Same quality debates. Different model families. Unlimited usage.

MIT licensed. Star if useful → github.com/Miles0sage/swarm-agency
