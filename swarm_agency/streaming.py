"""Streaming debate — emit agent votes as they arrive, not all at once.

Provides async generators and callback patterns for real-time debate output.
Works with both CLI (Rich Live) and web (SSE/WebSocket).
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import AsyncIterator, Callable, Optional, TYPE_CHECKING

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .agent import call_agent

if TYPE_CHECKING:
    from .memory import DecisionMemoryStore

logger = logging.getLogger("swarm_agency.streaming")


@dataclass
class VoteEvent:
    """A single agent vote as it arrives during streaming."""
    agent_name: str
    department: str
    vote: AgentVote
    votes_so_far: int
    total_agents: int
    elapsed: float


@dataclass
class DebateProgress:
    """Tracks streaming debate state."""
    department: str
    total_agents: int
    votes: list[AgentVote] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    completed: bool = False


async def stream_debate(
    agents: list[AgentConfig],
    request: AgencyRequest,
    api_key: str,
    base_url: str,
    department_name: str = "Department",
    memory_contexts: Optional[dict[str, str]] = None,
) -> AsyncIterator[VoteEvent]:
    """Stream agent votes as they complete.

    Usage:
        async for event in stream_debate(agents, request, key, url):
            print(f"{event.agent_name}: {event.vote.position}")
    """
    start = time.time()
    memory_contexts = memory_contexts or {}

    # Create all tasks
    tasks = {
        asyncio.create_task(
            call_agent(
                agent, request, api_key, base_url,
                memory_context=memory_contexts.get(agent.name, ""),
            )
        ): agent
        for agent in agents
    }

    votes_received = 0
    total = len(agents)

    for coro in asyncio.as_completed(tasks.keys()):
        vote = await coro
        votes_received += 1
        elapsed = time.time() - start

        yield VoteEvent(
            agent_name=vote.agent_name,
            department=department_name,
            vote=vote,
            votes_so_far=votes_received,
            total_agents=total,
            elapsed=elapsed,
        )


async def stream_department_debate(
    department,  # Department instance
    request: AgencyRequest,
    memory_store: Optional["DecisionMemoryStore"] = None,
    query_embedding: Optional[list[float]] = None,
    on_vote: Optional[Callable[[VoteEvent], None]] = None,
) -> Decision:
    """Run a department debate with streaming callbacks.

    Like Department.debate() but calls on_vote() as each agent finishes.
    Returns the final Decision.
    """
    start = time.time()

    # Build memory contexts (same logic as Department.debate)
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

    # Stream votes
    all_votes: list[AgentVote] = []
    async for event in stream_debate(
        department.agents, request,
        department.api_key, department.base_url,
        department_name=department.name,
        memory_contexts=memory_contexts,
    ):
        all_votes.append(event.vote)
        if on_vote:
            on_vote(event)

    duration = time.time() - start
    outcome, position, confidence, summary, dissents = department._tally(
        all_votes, agent_weights=agent_weights
    )

    return Decision(
        request_id=request.request_id,
        department=department.name,
        outcome=outcome,
        position=position,
        confidence=confidence,
        votes=all_votes,
        summary=summary,
        dissenting_views=dissents,
        duration_seconds=round(duration, 2),
    )
