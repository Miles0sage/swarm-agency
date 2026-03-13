# swarm-agency Launch Posts

---

## 1. Reddit r/MachineLearning

**Title:** [P] swarm-agency: Multi-model debate framework with 43 AI agent personas across 5 LLM families

**Body:**

I've been working on a problem that's been bugging me about existing multi-agent frameworks: they all run on a single model. CrewAI (46k stars), AutoGen (55k stars), LangGraph -- they let you spin up multiple agents, but those agents share identical training biases. When GPT-4 hallucinates on a topic, five GPT-4 agents will hallucinate the same way. You get correlated errors masquerading as consensus.

**swarm-agency** takes a different approach. It runs 43 agent personas across 5 model families (GLM, Qwen, MiniMax, Kimi) through a single API endpoint (Alibaba DashScope). Different training corpora produce different reasoning patterns, which means errors are uncorrelated -- closer to an actual ensemble in the ML sense.

**Architecture:**

- 10 departments (Strategy, Engineering, Product, Marketing, Sales, Finance, Legal, Operations, Research, Creative) with 3-5 agents each
- Each agent has defined expertise, a declared cognitive bias, and a specific model assignment
- Agents independently analyze a question through their domain lens, then vote YES/NO/MAYBE with confidence scores and reasoning
- Framework tallies votes into four outcomes: CONSENSUS (100%), MAJORITY (60%+), SPLIT (<60%), DEADLOCK
- Dissenting views are surfaced, not suppressed
- A LearningEngine tracks accuracy over time and evolves underperforming agent prompts

**What's interesting technically:**

1. The multi-model aspect is the key differentiator. Assigning agents to different model families means the "committee" has genuinely diverse reasoning, not just different system prompts on the same weights.
2. Each agent persona is a standalone markdown file with YAML frontmatter (name, department, model, expertise, bias, full system prompt). You can use them without the Python SDK at all -- just drop them into Cursor, Claude Code, Windsurf, Aider, or Gemini CLI as rule files.
3. The debate-and-vote mechanism is deliberately simple. No complex graph orchestration. Agents run in parallel, vote, results get tallied. The value comes from model diversity, not workflow complexity.

102 tests, CI/CD, MIT licensed.

GitHub: https://github.com/Miles0sage/swarm-agency

Happy to discuss the multi-model ensemble approach and where it breaks down. I've found it works best for strategic/ambiguous decisions and worst for tasks with clear right answers (where you're better off just using the strongest model).

---

## 2. Reddit r/LocalLLaMA

**Title:** 43 AI agents, 5 model families, $10/month flat -- no GPT-4 required

**Body:**

I built a multi-agent debate framework that runs entirely on Alibaba DashScope's Coding Plan: **$10/month flat** for 1,200 requests per 5-hour window. That's enough to run full 43-agent consultations for essentially $0 per query.

**Why this matters for the cost-conscious:**

Most multi-agent frameworks assume you're running GPT-4 or Claude. A single CrewAI run with 5 GPT-4 agents can cost $0.50-2.00. Run that 100 times a month and you're at $200+. swarm-agency uses GLM-4.7, GLM-5, Qwen 3.5 Plus, Qwen 3 Coder, MiniMax M2.5, and Kimi K2.5 -- all through one API key.

**The zero-code path:**

You don't even need to install anything. The repo has 43 markdown files (one per agent persona) organized into 10 departments. Each file has YAML frontmatter defining the agent's role, expertise, cognitive bias, and system prompt. You can:

- Copy any `.md` file into `.cursorrules` for Cursor
- Drop it into `.claude/agents/` for Claude Code
- Append to `.windsurfrules` for Windsurf
- Reference in `.aider.conf.yml` for Aider
- Append to `GEMINI.md` for Gemini CLI

There are also 5 export scripts that batch-convert for each IDE.

Even without the SDK, having a library of well-defined expert personas with declared biases is useful. Instead of prompting "you are a helpful assistant," you get a CFO who is "biased toward capital preservation," a DevOps engineer who "assumes everything will break at scale," or a Devil's Advocate who "challenges every assumption by default."

**If you do want the SDK:**

```bash
pip install swarm-agency
```

```python
from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

agency = Agency(name="MyCo")
for dept in create_full_agency_departments():
    agency.add_department(dept)

decision = asyncio.run(agency.decide(AgencyRequest(
    request_id="001",
    question="Should we launch the MVP or wait?",
    context="500 beta users. Competitor just raised $10M.",
)))

print(decision.outcome)     # CONSENSUS | MAJORITY | SPLIT | DEADLOCK
print(decision.confidence)  # 0.0 - 1.0
```

CLI too:

```bash
swarm-agency "Should we pivot to B2B?" --context "B2C growth is flat"
```

102 tests, MIT license, Python 3.10+.

GitHub: https://github.com/Miles0sage/swarm-agency

---

## 3. Hacker News "Show HN"

**Title:** Show HN: Swarm-Agency -- 43 AI agents across 5 model families debate your decisions ($10/mo)

**Body:**

Multi-agent frameworks like CrewAI and AutoGen run all agents on the same model. Same training data means correlated errors -- five GPT-4 agents will be wrong in the same way.

swarm-agency runs 43 agent personas across 5 model families (GLM, Qwen, MiniMax, Kimi) via Alibaba DashScope ($10/mo flat). Different models produce uncorrelated analysis. Agents are organized into 10 departments (Strategy, Engineering, Product, Finance, Legal, etc.), each with defined expertise and declared cognitive biases.

Each agent independently analyzes a question, then votes YES/NO/MAYBE with confidence and reasoning. The framework tallies votes into CONSENSUS, MAJORITY, SPLIT, or DEADLOCK -- and surfaces dissenting views.

Two ways to use it:

1. **Zero-code**: Each agent is a standalone markdown file. Copy into Cursor, Claude Code, Windsurf, Aider, or Gemini CLI as a rules file. No dependencies.

2. **Python SDK**: `pip install swarm-agency` for programmatic multi-model debates with a LearningEngine that evolves agent prompts based on outcome feedback.

102 tests, CI/CD, MIT licensed.

https://github.com/Miles0sage/swarm-agency

---

## 4. Twitter/X Thread

**Tweet 1:**

I just open-sourced swarm-agency: 43 AI agents across 10 departments that debate your decisions like a real company.

Strategy. Engineering. Finance. Legal. Marketing. Sales. Product. Operations. Research. Creative.

Each agent runs on a DIFFERENT model. Cost: $10/month.

github.com/Miles0sage/swarm-agency

---

**Tweet 2:**

The problem with CrewAI, AutoGen, LangGraph: all agents run on the same model.

Same training data = same biases = correlated errors.

Five GPT-4 agents agreeing doesn't mean they're right. It means GPT-4 is confident.

swarm-agency uses 5 model families. Different weights. Uncorrelated reasoning.

---

**Tweet 3:**

Every agent has:
- A specific expertise (penetration testing, tax optimization, brand strategy...)
- A declared cognitive bias ("assumes everything will break at scale")
- A different LLM model (GLM, Qwen, MiniMax, Kimi)

They vote YES/NO/MAYBE with confidence scores.

Results: CONSENSUS / MAJORITY / SPLIT / DEADLOCK.

Dissenting views are surfaced, not buried.

---

**Tweet 4:**

You don't even need to install anything.

Each agent is a standalone markdown file. Drop it into:
- Cursor (.cursorrules)
- Claude Code (.claude/agents/)
- Windsurf (.windsurfrules)
- Aider (.aider.conf.yml)
- Gemini CLI (GEMINI.md)

43 expert personas, ready to copy-paste. Zero dependencies.

---

**Tweet 5:**

Cost comparison:

CrewAI + GPT-4 swarm: $200+/month
AutoGen + Claude: $150+/month
swarm-agency + DashScope: $10/month flat

1,200 requests per 5-hour window. Full 43-agent consultations for ~$0.00 per query.

Alibaba's Coding Plan is absurdly underpriced. Use it before they figure that out.

---

**Tweet 6:**

If you want the Python SDK:

```
pip install swarm-agency
swarm-agency "Should we pivot to B2B?" --context "B2C growth flat"
```

LearningEngine tracks which agents are right over time and evolves the underperformers.

102 tests. CI/CD. MIT licensed.

---

**Tweet 7:**

Link: github.com/Miles0sage/swarm-agency

Star it if multi-model agent debate is something you've been thinking about.

PRs welcome -- especially new departments, model integrations, or benchmark results.

Built by @Miles0sage
