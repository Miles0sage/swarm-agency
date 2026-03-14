---
name: self-improving-agents-research
description: Research findings on self-improving AI agent skills - cognee debunked, DSPy recommended, build plan for swarm-agency
type: project
---

## Self-Improving Agent Skills Research (March 13, 2026)

4-agent parallel research completed. Key findings:

### Cognee Assessment: SKIP
- `amendify()` does NOT exist — zero hits in codebase/docs/PyPI
- "Self-improving skills" is marketing for `memify()`, a graph enrichment pipeline
- SKILL.md ingestion isn't even cognee — separate repo by muratcankoylan
- Cognee is good for knowledge graph routing, NOT skill optimization
- Overkill for our scale (17 skills, 1 user)

### What Actually Works
1. **DSPy** (Stanford) — production-ready prompt optimization with MIPROv2. Best for systematic skill improvement.
2. **EvoAgentX** — self-evolving multi-agent workflows, 2.5k stars, integrates TextGrad + MIPRO
3. **TextGrad** — gradient-based prompt optimization, published in Nature 2025
4. **continuous-learning-v2** — WE ALREADY BUILT THIS. Observe→inspect→amend→evaluate loop in bash/python. Was disabled.

### Market Opportunity
- 351k+ skills indexed on SkillsMP, ecosystem exploding
- Agency Agents: 40k stars with static personas (gap = living personas that learn)
- Skill drift is documented pain point (only 4% of sessions use skills due to drift)
- Window is NOW — ship in 1 week or don't bother
- Realistic: 500-2k star repo, portfolio piece + OpenClaw differentiator

### Build Plan: swarm-agency
Generalize swarm-predict pattern into business-like AI agency with self-improving departments.
Use DSPy for skill optimization. Skip cognee entirely.

**Why:** Proven approach. Built on what we have. Fills a real gap.
**How to apply:** When building the agency system, use DSPy MIPROv2 for prompt optimization, continuous-learning-v2 hooks for observation, and the swarm debate pattern for multi-persona decisions.
