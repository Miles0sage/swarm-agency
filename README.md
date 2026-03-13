# swarm-agency

> Multi-model AI agency where agents debate like departments in a business. Self-improving.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## What is this?

An AI agency framework where specialized agents — organized into departments like a real business — independently analyze decisions using **different AI models**, then debate and vote. Departments (Strategy, Product, Marketing, Research) each have 4-5 agents with distinct roles, expertise, and analytical biases.

Built on the proven [swarm-predict](https://github.com/Miles0sage/swarm-predict) pattern: parallel multi-model debate produces **uncorrelated analysis** that outperforms any single agent.

## Quick Start

```bash
pip install swarm-agency
```

```bash
export ALIBABA_CODING_API_KEY=your_key_here
```

```python
import asyncio
from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

agency = Agency(name="MyCo")
for dept in create_full_agency_departments():
    agency.add_department(dept)

request = AgencyRequest(
    request_id="decision-001",
    question="Should we launch our MVP this week or wait for the redesign?",
    context="We have 500 beta users. Competitor just raised $10M.",
)

decision = asyncio.run(agency.decide(request))

print(decision.outcome)    # CONSENSUS, MAJORITY, SPLIT, or DEADLOCK
print(decision.position)   # The winning position
print(decision.confidence)  # 0.0 - 1.0
print(decision.summary)    # Human-readable summary
```

## CLI

```bash
pip install swarm-agency[cli]
```

```bash
swarm-agency "Should we pivot to B2B?" --context "B2C growth is flat"
swarm-agency "Hire a senior engineer or two juniors?" -d Strategy --json
```

## Architecture

```
                    ┌─────────────────┐
                    │  AgencyRequest   │
                    │  (your question) │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼──────┐  ┌───────▼────────┐  ┌──────▼───────┐
│   Strategy     │  │    Product     │  │  Marketing   │  ...
│ (5 agents)     │  │  (5 agents)    │  │  (4 agents)  │
│ CSO,COO,CFO,   │  │ CPO,CTO,      │  │  CMO,Content │
│ Growth,Devil   │  │ Design,Data,   │  │  Social,     │
│                │  │ ShipIt         │  │  Analyst     │
└─────────┬──────┘  └───────┬────────┘  └──────┬───────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Synthesize    │
                    │  Cross-dept     │
                    │  decision       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Decision     │
                    │ CONSENSUS /     │
                    │ MAJORITY /      │
                    │ SPLIT           │
                    └─────────────────┘
```

## Departments & Agents

### Strategy (5 agents)

| Agent | Role | Bias |
|-------|------|------|
| **Visionary** | CSO | Thinks 5 years ahead |
| **Pragmatist** | COO | Asks "can we actually do this?" |
| **NumbersCruncher** | CFO | Everything needs positive ROI |
| **GrowthHacker** | VP Growth | Speed and scale over safety |
| **DevilsAdvocate** | Board Advisor | Argues the opposite |

### Product (5 agents)

| Agent | Role | Bias |
|-------|------|------|
| **UserAdvocate** | Head of Product | What does the user need? |
| **TechLead** | CTO | Proven tech, resist complexity |
| **DesignThinker** | Head of Design | Simplicity over features |
| **DataDriven** | Head of Analytics | No decision without data |
| **ShipIt** | Engineering Manager | 80% now beats 100% later |

### Marketing (4 agents)

| Agent | Role | Bias |
|-------|------|------|
| **BrandBuilder** | CMO | Reinforce the narrative |
| **ContentEngine** | Head of Content | Organic > paid |
| **ViralMarketer** | Head of Social | Shareability over polish |
| **Skeptic** | Marketing Analyst | Prove the ROI |

### Research (4 agents)

| Agent | Role | Bias |
|-------|------|------|
| **DeepDiver** | Head of Research | Thoroughness over speed |
| **TrendSpotter** | Market Intelligence | Early adopter mindset |
| **Synthesizer** | Chief Scientist | Non-obvious connections |
| **FactChecker** | Research Analyst | Demands primary sources |

## Self-Improving Agents

The `LearningEngine` tracks agent performance and evolves their prompts over time:

```python
from swarm_agency import LearningEngine, Feedback

learning = LearningEngine()

# After a decision plays out...
learning.apply_feedback(Feedback(
    request_id="decision-001",
    was_correct=True,
    correct_position="LAUNCH",
))

# Check agent stats
stats = learning.get_all_stats()
for name, mem in stats.items():
    print(f"{name}: {mem.accuracy:.0%} accuracy over {mem.total_decisions} decisions")

# Evolve an agent's prompt based on learnings
from swarm_agency.presets import STRATEGY_AGENTS
evolved = learning.evolve_agent(STRATEGY_AGENTS[0])
# evolved.system_prompt now includes learnings from past decisions
```

## Custom Departments

```python
from swarm_agency import Agency, Department, AgentConfig, AgencyRequest

# Create your own agents
sales_team = Department(
    name="Sales",
    agents=[
        AgentConfig(
            name="Closer",
            role="VP Sales",
            expertise="enterprise sales, deal negotiation",
            bias="always be closing, revenue over relationships",
            system_prompt="You are an aggressive VP of Sales...",
            model="qwen3-coder-plus",
        ),
        AgentConfig(
            name="RelationshipBuilder",
            role="Account Manager",
            expertise="customer success, retention, upselling",
            bias="long-term relationships over quick wins",
            system_prompt="You are a relationship-focused account manager...",
            model="glm-4.7",
        ),
    ],
    threshold=0.6,  # 60% agreement for majority
)

agency = Agency(api_key="your-key")
agency.add_department(sales_team)
```

## Models Used (5 Families)

| Family | Models | Why |
|--------|--------|-----|
| GLM (Zhipu) | glm-4.7, glm-5 | Strong reasoning |
| Qwen (Alibaba) | qwen3.5-plus, qwen3-coder-plus, qwen3-coder-next | Fast, code-aware |
| MiniMax | MiniMax-M2.5 | Creative, contrarian |
| Kimi (Moonshot) | kimi-k2.5 | Deep analysis |

All via single API endpoint (Alibaba DashScope Coding Plan, ~$10/mo).

## Cost

**Effectively free** with Alibaba DashScope Coding Plan:
- $10/month for 1,200 requests per 5-hour window
- Full agency consultation (18 agents) = 18 API calls
- Single department = 4-5 API calls
- Cost per decision: ~$0.00

## Contributing

```bash
git clone https://github.com/Miles0sage/swarm-agency.git
cd swarm-agency
pip install -e ".[dev]"
pytest
```

## License

MIT
