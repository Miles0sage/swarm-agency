"""Multi-round debate — agents see prior votes and can revise their positions.

Round 1: Normal debate (agents vote independently)
Round 2+: Agents see prior round results and can change their vote
Stops when: consensus reached, max rounds hit, or no votes changed
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .agent import call_agent, format_agent_prompt

if TYPE_CHECKING:
    from .memory import DecisionMemoryStore

logger = logging.getLogger("swarm_agency.rounds")

DEFAULT_MAX_ROUNDS = 3
CONVERGENCE_THRESHOLD = 1.0  # 100% agreement = stop early
STABILITY_DELTA = 0.05  # if avg confidence change < this, positions are stable


@dataclass
class RoundResult:
    """Result of a single debate round."""
    round_number: int
    votes: list[AgentVote]
    outcome: str
    position: str
    confidence: float
    changes: int  # how many agents changed position from prior round
    duration: float


def _build_prior_round_context(prior_votes: list[AgentVote], round_num: int) -> str:
    """Build context string showing prior round results for agents to see."""
    lines = [
        f"\n## Prior Round {round_num} Results",
        "",
    ]

    # Tally
    counts: dict[str, int] = {}
    for v in prior_votes:
        pos = v.position.upper()
        if pos != "ERROR":
            counts[pos] = counts.get(pos, 0) + 1

    if counts:
        tally = ", ".join(f"{pos}: {c}" for pos, c in sorted(counts.items(), key=lambda x: -x[1]))
        lines.append(f"**Vote tally:** {tally}")
        lines.append("")

    # Individual votes (without names to reduce anchoring bias on specific agents)
    for i, v in enumerate(prior_votes, 1):
        if v.position.upper() != "ERROR":
            lines.append(
                f"- Agent {i}: {v.position} ({v.confidence:.0%}) — {v.reasoning[:100]}"
            )

    lines.extend([
        "",
        "**You may revise your position based on these results.**",
        "If you still hold your original position, keep it. Only change if the arguments convince you.",
        "Do NOT simply follow the majority — maintain your analytical perspective.",
    ])

    return "\n".join(lines)


async def _call_agent_with_prior(
    agent: AgentConfig,
    request: AgencyRequest,
    api_key: str,
    base_url: str,
    prior_context: str,
    memory_context: str = "",
) -> AgentVote:
    """Call agent with prior round context injected."""
    # Create modified request with prior round info
    augmented_request = AgencyRequest(
        request_id=request.request_id,
        question=request.question,
        context=(request.context or "") + prior_context,
        department=request.department,
        metadata=request.metadata,
    )
    return await call_agent(
        agent, augmented_request, api_key, base_url,
        memory_context=memory_context,
    )


async def multi_round_debate(
    department,  # Department instance
    request: AgencyRequest,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    memory_store: Optional["DecisionMemoryStore"] = None,
    query_embedding: Optional[list[float]] = None,
) -> tuple[Decision, list[RoundResult]]:
    """Run a multi-round debate where agents can revise positions.

    Returns (final_decision, list_of_round_results).
    """
    start = time.time()

    # Build memory contexts once
    memory_contexts: dict[str, str] = {}
    agent_weights: Optional[dict[str, float]] = None
    if memory_store:
        from .memory import build_memory_context
        similar = memory_store.find_similar(
            request.question, request.context, limit=3,
            query_embedding=query_embedding,
        )
        weights: dict[str, float] = {}
        for agent in department.agents:
            track = memory_store.get_agent_track_record(agent.name)
            memory_contexts[agent.name] = build_memory_context(similar, track)
            if track.get("reviewed", 0) > 0 and track.get("accuracy") is not None:
                weights[agent.name] = 0.5 + (track["accuracy"] * 0.5)
        if weights:
            agent_weights = weights

    rounds: list[RoundResult] = []
    prior_votes: Optional[list[AgentVote]] = None

    for round_num in range(1, max_rounds + 1):
        round_start = time.time()

        if round_num == 1:
            # Round 1: Normal debate
            tasks = [
                call_agent(
                    agent, request, department.api_key, department.base_url,
                    memory_context=memory_contexts.get(agent.name, ""),
                )
                for agent in department.agents
            ]
        else:
            # Round 2+: Include prior round context
            prior_context = _build_prior_round_context(prior_votes, round_num - 1)
            tasks = [
                _call_agent_with_prior(
                    agent, request, department.api_key, department.base_url,
                    prior_context=prior_context,
                    memory_context=memory_contexts.get(agent.name, ""),
                )
                for agent in department.agents
            ]

        votes: list[AgentVote] = list(await asyncio.gather(*tasks))
        round_duration = time.time() - round_start

        # Count position changes from prior round
        changes = 0
        if prior_votes:
            prior_positions = {v.agent_name: v.position.upper() for v in prior_votes}
            for v in votes:
                prev = prior_positions.get(v.agent_name)
                if prev and prev != v.position.upper():
                    changes += 1
                    logger.info(
                        f"Round {round_num}: {v.agent_name} changed {prev} → {v.position}"
                    )

        # Tally this round
        outcome, position, confidence, summary, dissents = department._tally(
            votes, agent_weights=agent_weights
        )

        rounds.append(RoundResult(
            round_number=round_num,
            votes=votes,
            outcome=outcome,
            position=position,
            confidence=confidence,
            changes=changes,
            duration=round_duration,
        ))

        prior_votes = votes

        # Check convergence: stop if consensus, no changes, or stable confidence
        if outcome == "CONSENSUS":
            logger.info(f"Consensus reached in round {round_num}")
            break
        if round_num > 1 and changes == 0:
            # Also check confidence stability
            if prior_votes:
                prior_confs = {v.agent_name: v.confidence for v in rounds[-2].votes if rounds[-2].votes}
                conf_deltas = []
                for v in votes:
                    prev_conf = prior_confs.get(v.agent_name)
                    if prev_conf is not None:
                        conf_deltas.append(abs(v.confidence - prev_conf))
                avg_delta = sum(conf_deltas) / len(conf_deltas) if conf_deltas else 0
                if avg_delta < STABILITY_DELTA:
                    logger.info(
                        f"Stable in round {round_num} (avg conf delta={avg_delta:.3f}), stopping"
                    )
                    break
            else:
                logger.info(f"No position changes in round {round_num}, stopping")
                break

    # Build final decision from last round
    final_round = rounds[-1]
    total_duration = time.time() - start

    # Enrich summary with round info
    round_summary = f" ({len(rounds)} round{'s' if len(rounds) > 1 else ''})"
    if len(rounds) > 1:
        total_changes = sum(r.changes for r in rounds)
        round_summary = (
            f" ({len(rounds)} rounds, {total_changes} position change{'s' if total_changes != 1 else ''})"
        )

    return Decision(
        request_id=request.request_id,
        department=department.name,
        outcome=final_round.outcome,
        position=final_round.position,
        confidence=final_round.confidence,
        votes=final_round.votes,
        summary=final_round.outcome + round_summary + ". " + summary
        if summary != final_round.outcome
        else final_round.outcome + round_summary,
        dissenting_views=dissents,
        duration_seconds=round(total_duration, 2),
    ), rounds
