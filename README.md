# swarm-agency

> **43 AI personas across 10 departments.** Use as markdown rules in any AI tool, or as a Python multi-model debate engine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Miles0sage/swarm-agency/actions/workflows/ci.yml/badge.svg)](https://github.com/Miles0sage/swarm-agency/actions)

**Zero production-ready multi-model debate frameworks exist.** CrewAI (46k stars) and AutoGen (55k) run on one model. This framework runs 5 model families in parallel — different models produce uncorrelated analysis, which means better signal. Now with **multi-round debate**, **semantic memory**, **streaming**, **tool-calling agents**, and **auto-department routing**.

Cost: **$10/mo flat** (Alibaba DashScope Coding Plan) = unlimited debates.

### Try it now — no API key needed:

**[Live Web Demo](https://swarm-agency.streamlit.app)** — click a scenario and see 5 AI agents debate it in your browser.

**CLI (developers):**
```bash
pip install swarm-agency[cli]
swarm-agency --demo startup-pivot
swarm-agency --agents  # See all 43 agents
```

<p align="center">
  <img src="demo.svg" alt="swarm-agency CLI: 5 AI agents debate whether a startup should pivot from B2C to B2B" width="700">
</p>

*↑ Real output. 5 agents across 5 different LLM models debating "Should we pivot from B2C to B2B?" — with reasoning, confidence scores, dissenting views, and vote tally.*

---

## Real-World Usage Flows

### Flow 1: "I just want quick advice" (2 minutes)

**Option A — Web UI (no terminal skills needed):**

```bash
pip install swarm-agency[web]
streamlit run app.py
```

Opens a browser with clickable buttons — pick a scenario, see 5 AI agents debate it. No API key, no command line, no code.

**Option B — Terminal:**

```bash
pip install swarm-agency[cli]
swarm-agency --demo startup-pivot
```

5 built-in scenarios: `startup-pivot`, `hire-senior`, `pricing-change`, `open-source`, `remote-vs-office`.

### Flow 2: "I want my own debates" (5 minutes)

```bash
# Get API key from Alibaba DashScope ($10/mo flat)
export ALIBABA_CODING_API_KEY=your_key

# Ask anything — 5 agents debate in parallel across 5 models
swarm-agency "Should we raise a Series A or bootstrap?" \
  --context "Revenue $30k MRR, growing 15% m/m. 2 competing term sheets."

# Target a specific department
swarm-agency "Should we open-source our SDK?" --department Engineering

# Get JSON output for scripts/dashboards
swarm-agency "Cut the marketing budget by 40%?" --json
```

### Flow 3: "I want institutional memory" (10 minutes)

```bash
# Enable memory — decisions get stored in SQLite
swarm-agency "Should we hire a VP Sales?" \
  --context "3 AEs, no manager. Pipeline growing." --memory

# A week later, record whether it worked
swarm-agency --feedback cli-a1b2c3d4 yes

# Next time you ask a similar question, agents SEE the past decision
# and adjust their confidence based on track record
swarm-agency "Should we hire a VP Marketing?" \
  --context "No marketing team yet." --memory

# View full decision history
swarm-agency --history
swarm-agency --history Finance --json
```

### Flow 4: "I want AI personas in my editor" (1 minute)

No Python needed. Just copy a persona file into your AI tool:

```bash
# Claude Code — drop the CFO persona into your project
cp agents/finance/cfo.md .claude/agents/cfo.md

# Cursor — append to your rules
cat agents/strategy/chief-strategist.md >> .cursorrules

# Or export all personas at once
python scripts/export.py --format cursor --output-dir .
python scripts/export.py --format claude --output-dir .claude/agents/
```

Now when you ask Claude/Cursor/Windsurf a business question, it answers **as that persona** — with the expertise, bias, and decision-making style baked in.

### Flow 5: "I want to build on this" (Python SDK)

```python
import asyncio
from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

# Spin up all 43 agents across 10 departments
agency = Agency(name="MyCo", memory_enabled=True)
for dept in create_full_agency_departments():
    agency.add_department(dept)

# Run a debate — all agents deliberate in parallel
decision = asyncio.run(agency.decide(AgencyRequest(
    request_id="q-001",
    question="Should we acquire CompetitorX for $2M?",
    context="They have 50k users, declining. Our product overlaps 60%.",
)))

# Use the result
print(decision.outcome)      # CONSENSUS | MAJORITY | SPLIT | DEADLOCK
print(decision.position)     # APPROVE | REJECT | NEUTRAL
print(decision.confidence)   # 0.0 - 1.0
print(decision.summary)      # Human-readable summary
print(decision.dissenting_views)  # What the minority thinks

# Feed back outcomes to improve future debates
agency.feedback("q-001", was_correct=True, notes="Acquisition went well")
```

---

## The 43 Agents

| Department | Agents | Models | Focus |
|---|---|---|---|
| **Strategy** (5) | Visionary, Pragmatist, NumbersCruncher, GrowthHacker, DevilsAdvocate | glm-4.7, qwen3.5-plus, qwen3-coder-plus, MiniMax-M2.5, kimi-k2.5 | Long-term planning, execution, financial modeling |
| **Product** (5) | UserAdvocate, TechLead, DesignThinker, DataDriven, ShipIt | glm-5, qwen3-coder-plus, glm-4.7, kimi-k2.5, qwen3-coder-next | User research, architecture, design, analytics |
| **Marketing** (4) | BrandBuilder, ContentEngine, ViralMarketer, Skeptic | glm-5, qwen3.5-plus, MiniMax-M2.5, kimi-k2.5 | Brand, content, social, ROI analysis |
| **Research** (4) | DeepDiver, TrendSpotter, Synthesizer, FactChecker | qwen3-coder-plus, glm-4.7, kimi-k2.5, qwen3.5-plus | Literature review, trends, synthesis, verification |
| **Finance** (5) | CFO, RiskAnalyst, RevenueStrategist, TaxOptimizer, Auditor | glm-5, qwen3-coder-plus, kimi-k2.5, MiniMax-M2.5, qwen3-coder-plus | Financial planning, risk, revenue, compliance |
| **Engineering** (5) | CTO, BackendLead, FrontendLead, DevOps, SecurityEngineer | qwen3-coder-next, glm-4.7, qwen3.5-plus, kimi-k2.5, glm-5 | Architecture, infrastructure, security |
| **Legal** (4) | GeneralCounsel, IPAttorney, ComplianceOfficer, ContractReviewer | qwen3-coder-plus, glm-5, MiniMax-M2.5, kimi-k2.5 | Corporate law, IP, compliance, contracts |
| **Operations** (4) | COO, SupplyChain, HRDirector, ProcessEngineer | glm-4.7, qwen3-coder-plus, MiniMax-M2.5, qwen3.5-plus | Execution, logistics, people, process |
| **Sales** (4) | VPSales, AccountExecutive, SalesEngineer, CustomerSuccess | kimi-k2.5, qwen3-coder-plus, glm-5, qwen3-coder-plus | Pipeline, deals, demos, retention |
| **Creative** (3) | CreativeDirector, BrandStrategist, ContentLead | MiniMax-M2.5, qwen3.5-plus, glm-4.7 | Visual identity, brand, content strategy |

---

## How Debate Works

```
              ┌──────────────────┐
              │  Your Question   │
              └────────┬─────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐  ┌─────────▼──────┐  ┌────────▼───────┐
│Strategy│  │    Finance     │  │  Engineering   │  ... (10 depts)
│5 agents│  │   5 agents     │  │   5 agents     │
│5 models│  │   5 models     │  │   5 models     │
└───┬────┘  └─────────┬──────┘  └────────┬───────┘
    │                  │                  │
    │      Each agent runs in parallel    │
    │      on a DIFFERENT LLM model       │
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
              ┌────────▼─────────┐
              │   Vote & Tally   │
              │                  │
              │  CONSENSUS (100%)│
              │  MAJORITY  (60%+)│
              │  SPLIT    (<60%) │
              │  DEADLOCK  (0)   │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │    Decision      │
              │  position + conf │
              │  + dissenting    │
              └──────────────────┘
```

Each agent independently analyzes the question through its expertise lens, then votes YES/NO/MAYBE with confidence and reasoning. The framework tallies votes, identifies consensus or disagreement, and surfaces dissenting views.

---

## Why Multi-Model?

Single-model frameworks (CrewAI, AutoGen, LangGraph) have a fundamental flaw: **all agents share the same training biases**. When GPT-4 is wrong, 5 GPT-4 agents will be wrong in the same way.

swarm-agency uses **5 model families** (GLM, Qwen, Kimi, MiniMax) through one API. Different training data → different reasoning patterns → uncorrelated errors → better decisions.

| Model Family | Models Used | Strengths |
|---|---|---|
| **GLM** (Zhipu) | glm-4.7, glm-5 | Strong reasoning, balanced |
| **Qwen** (Alibaba) | qwen3.5-plus, qwen3-coder-plus, qwen3-coder-next, qwen3-coder-plus | Fast, code-aware, analytical |
| **MiniMax** | MiniMax-M2.5 | Creative, contrarian thinking |
| **Kimi** (Moonshot) | kimi-k2.5 | Deep analysis, long context |

---

## Decision Memory (Semantic Search)

When `--memory` is enabled, decisions are stored with **Gemini embeddings** for semantic search. Each agent's prompt automatically includes:

- **Related past decisions** — found by meaning (not just keywords) using cosine similarity on 3072-dim embeddings
- **Agent track record** — individual accuracy stats so agents can self-calibrate
- **Outcome feedback** — which past decisions turned out correct or incorrect
- **Weighted voting** — agents with better track records get more influence (weight range: 0.5-1.0)

```bash
# Set your free Gemini API key for semantic search
export GEMINI_API_KEY=your_key  # Free tier from Google AI Studio

# Decisions are now matched by meaning, not just keywords
swarm-agency "Should we enter the European market?" --memory
```

---

## Multi-Round Debate

Agents see each other's votes and can **revise their positions** in subsequent rounds. Stops automatically when consensus is reached, no one changes position, or confidence stabilizes.

```bash
# 3-round debate — agents deliberate, see results, and revise
swarm-agency "Should we acquire CompetitorX?" --rounds 3

# Combine with memory for maximum intelligence
swarm-agency "Cut engineering headcount by 20%?" --rounds 2 --memory
```

```python
from swarm_agency import multi_round_debate, create_strategy_dept, AgencyRequest

dept = create_strategy_dept(api_key="...", base_url="...")
request = AgencyRequest(request_id="q1", question="Should we pivot?")

decision, rounds = await multi_round_debate(dept, request, max_rounds=3)
print(f"Converged in {len(rounds)} rounds")
for r in rounds:
    print(f"  Round {r.round_number}: {r.outcome} ({r.changes} position changes)")
```

---

## Streaming Debates

See agent votes **as they arrive** instead of waiting for all 43 to finish.

```python
from swarm_agency import stream_debate, AgencyRequest
from swarm_agency.presets import STRATEGY_AGENTS

request = AgencyRequest(request_id="s1", question="Launch now?")

async for event in stream_debate(STRATEGY_AGENTS, request, api_key, base_url):
    print(f"[{event.votes_so_far}/{event.total_agents}] "
          f"{event.agent_name}: {event.vote.position} ({event.vote.confidence:.0%})")
```

---

## Agent Tools

Agents can optionally use **built-in tools** during deliberation: calculator, ROI, break-even analysis, compound growth, and percentage calculations.

```bash
swarm-agency "Is this acquisition worth $2M?" --tools
```

```python
from swarm_agency.tools import default_registry

# See available tools
print(default_registry.list_tools())
# ['calculate', 'percentage', 'compound_growth', 'roi', 'break_even']

# Register custom tools
from swarm_agency.tools import ToolDefinition
default_registry.register(ToolDefinition(
    name="lookup_revenue",
    description="Look up company revenue",
    parameters={"company": "Company name"},
    handler=lambda company="": f"Revenue for {company}: $10M ARR",
))
```

---

## Decision Templates

Pre-built question formats for common decisions:

```bash
swarm-agency --template hire --candidate "Jane" --role "CTO"
swarm-agency --template pricing --product "Pro Plan" --current-price "$29" --new-price "$49"
swarm-agency --template launch --product "Mobile App" --market "Europe"
swarm-agency --template vendor --vendor-name "AWS" --service "cloud hosting"
swarm-agency --template pivot --current-direction "B2C" --new-direction "B2B"
```

---

## Auto-Department Routing

When no department is specified and `GEMINI_API_KEY` is set, questions are **automatically routed** to the most relevant 1-3 departments instead of consulting all 43 agents.

```bash
# Automatically routes to Legal + Strategy (not all 10 departments)
swarm-agency "Should we file a patent?" --memory

# Force a specific department
swarm-agency "Should we file a patent?" -d Legal
```

---

## Prompt Optimization

The `PromptOptimizer` analyzes feedback patterns and generates targeted prompt amendments for underperforming agents.

```python
from swarm_agency import PromptOptimizer, DecisionMemoryStore
from swarm_agency.presets import STRATEGY_AGENTS

store = DecisionMemoryStore()
optimizer = PromptOptimizer(store)

# Optimize all agents based on feedback
results = optimizer.optimize_all(STRATEGY_AGENTS)
for r in results:
    print(f"{r.agent_name}: {r.improvement_notes}")

# Apply optimized prompts
optimized_agents = optimizer.apply_optimizations(STRATEGY_AGENTS)
```

---

## Self-Improving Agents

The `LearningEngine` tracks agent accuracy and evolves their prompts over time:

```python
from swarm_agency import LearningEngine, Feedback

learning = LearningEngine()

# After a decision plays out...
learning.apply_feedback(Feedback(
    request_id="001",
    was_correct=True,
    correct_position="LAUNCH",
))

# Evolve underperforming agents
from swarm_agency.presets import STRATEGY_AGENTS
evolved = learning.evolve_agent(STRATEGY_AGENTS[0])
```

---

## Custom Departments

```python
from swarm_agency import Agency, Department, AgentConfig, AgencyRequest

my_dept = Department(
    name="Security",
    agents=[
        AgentConfig(
            name="RedTeam",
            role="Offensive Security Lead",
            expertise="penetration testing, exploit analysis",
            bias="assumes everything is vulnerable until proven otherwise",
            system_prompt="You are an offensive security expert...",
            model="kimi-k2.5",
        ),
    ],
    threshold=0.6,
)

agency = Agency(api_key="your-key")
agency.add_department(my_dept)
```

---

## Cost

| Plan | Price | What You Get |
|---|---|---|
| Alibaba DashScope Coding Plan | $10/mo | 1,200 requests per 5-hour window |
| Full agency consultation (43 agents) | ~$0.00 | 43 parallel API calls |
| Single department (3-5 agents) | ~$0.00 | 3-5 parallel API calls |

---

## Setup

```bash
git clone https://github.com/Miles0sage/swarm-agency.git
cd swarm-agency
pip install -e ".[dev]"
```

```bash
export ALIBABA_CODING_API_KEY=your_key_here
```

Get your API key from [Alibaba DashScope](https://dashscope.console.aliyun.com/) → Coding Plan ($10/mo).

---

## Contributing

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
