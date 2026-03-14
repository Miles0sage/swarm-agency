---
name: swarm-agency-status
description: Swarm Agency v0.6.0 — 43 agents with SOULS, 328 tests, 10K lines. Semantic memory, multi-round debate, streaming, tools, optimizer, belief system, episodic memory. Path /root/swarm-agency/
type: project
---

## Swarm Agency v0.6.0 — March 14, 2026

**Path:** `/root/swarm-agency/` | **Repo:** github.com/Miles0sage/swarm-agency | **License:** MIT

### Stats
- **328 tests** (2.1s) | **23 modules** | **23 test files** | **10,062 lines** | **55 exports**

### Architecture (v0.6.0)
```
Question → [Auto-Route to 1-3 depts] → [43 agents w/ souls debate] → [Weighted vote tally] → Decision
                                              ↑                              ↓
                                    [Beliefs, Episodes,              [Store decision +
                                     Voice, Track Record]             update beliefs]
```

### The Soul System (KEY DIFFERENTIATOR)
Agents have persistent identity computed from history — NOT stored as mutable state:
- **Beliefs**: `(subject, predicate, confidence)` triples, Bayesian updates
- **Episodes**: Past debates remembered as subjective narratives with emotional tags
- **Reflections**: Metacognitive self-observations ("I'm weak on cost estimates")
- **Voice**: Consistent verbal style per agent (CFO quantifies everything, DevilsAdvocate opens with "Let me push back")
- **Temperament**: confrontational, diplomatic, cautious, enthusiastic, analytical
- All COMPUTED at call time from SQLite — reproducible, inspectable, no drift

### All Features
| Feature | Module | Status |
|---------|--------|--------|
| Semantic memory (Gemini embeddings) | `embeddings.py` | Working |
| Multi-round debate (stability detection) | `rounds.py` | Working |
| Streaming votes (asyncio.as_completed) | `streaming.py` | Working |
| Weighted voting (track record) | `department.py` | Working |
| Auto-department routing | `agency.py` | Working |
| Tool-calling (AST-safe math, ROI, web search) | `tools.py`, `web_search.py` | Working |
| Decision templates (5 presets) | `templates.py` | Working |
| Prompt optimizer (feedback-driven) | `optimizer.py` | Working |
| DSPy integration (MIPROv2 ready) | `dspy_optimizer.py` | Architecture ready |
| FastAPI server + SSE streaming | `server.py` | Working |
| Sports agents (10 across 3 depts) | `sports.py` | Working |
| Agent Soul system | `soul.py` | Working |
| Streamlit web UI (v0.5 features) | `app.py` | Working |

### CLI
```bash
swarm-agency --demo startup-pivot     # No API key
swarm-agency "question" --memory      # Semantic memory + auto-routing
swarm-agency "question" --rounds 3    # Multi-round debate
swarm-agency "question" --stream      # Stream votes
swarm-agency "question" --tools       # Agent tools
swarm-agency --template hire --candidate "Jane" --role "CTO"
swarm-agency serve                    # FastAPI server on :8000
swarm-agency chat -p openrouter       # Interactive REPL
```

### Research Findings (8 parallel agents total)
- Multi-round: max 2-3 rounds, anti-sycophancy prompting, stability detection
- Tools: OpenRouter+DashScope both OpenAI-compatible, selective per agent
- DSPy: ONE module, role/expertise/bias as inputs, ~$2 to optimize
- Streaming: asyncio.Queue pattern, SSE for web, Rich Live for CLI
- Monetization: Sports betting $49-299/mo, Hosted API $29-299/mo, Prediction markets $79-499/mo
- Persistent identity: Stanford GenAgents memory stream, MemGPT tiered memory, computed personality
- Chain-of-reasoning: Belief triples with Bayesian confidence, episodic memory with salience decay
- Alive-feeling agents: Voice consistency, surprising callbacks, relationship memory, disagreement personality

### Revenue Paths
1. **Sports Betting Advisory** — "43 agents debate your bet", $49-299/mo, 2 weeks to ship
2. **Hosted Decision API** — embeddable, $29-299/mo, developer play
3. **Prediction Market Intel** — Polymarket/Kalshi, zero competition, $79-499/mo

### Cost
- DashScope: $10/mo flat (5 model families)
- OpenRouter: pay-per-use (7 model families)
- Soul system: ~$1-2/mo additional (pure SQLite, minimal extra tokens)
- Gemini embeddings: FREE

**Why:** Only multi-model debate engine that exists. Agents with souls = can't be replicated by copying prompts.
**How to apply:** Ship sports betting vertical first, then hosted API. Soul system is the moat.
