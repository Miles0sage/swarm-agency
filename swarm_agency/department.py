"""Department - a group of agents that debate and reach decisions."""

import asyncio
import logging
import time
from typing import Optional, TYPE_CHECKING

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .agent import call_agent

if TYPE_CHECKING:
    from .memory import DecisionMemoryStore

logger = logging.getLogger("swarm_agency.department")


class Department:
    """A department of agents that debate questions and produce decisions."""

    def __init__(
        self,
        name: str,
        agents: list[AgentConfig],
        threshold: float = 0.6,
        api_key: str = "",
        base_url: str = "",
        description: str = "",
    ):
        self.name = name
        self.agents = agents
        self.threshold = threshold  # fraction needed for CONSENSUS/MAJORITY
        self.api_key = api_key
        self.base_url = base_url
        self.description = description

    async def debate(
        self,
        request: AgencyRequest,
        memory_store: Optional["DecisionMemoryStore"] = None,
        query_embedding: Optional[list[float]] = None,
    ) -> Decision:
        """Run all agents in parallel, tally positions, return a Decision."""
        start = time.time()

        # Build per-agent memory context if memory is enabled
        memory_contexts: dict[str, str] = {}
        agent_weights: Optional[dict[str, float]] = None
        if memory_store:
            from .memory import build_memory_context
            similar = memory_store.find_similar(
                request.question, request.context, limit=3,
                query_embedding=query_embedding,
            )

            # Compute agent weights from track records
            weights: dict[str, float] = {}
            for agent in self.agents:
                track = memory_store.get_agent_track_record(agent.name)
                memory_contexts[agent.name] = build_memory_context(
                    similar, track
                )
                if track.get("reviewed", 0) > 0 and track.get("accuracy") is not None:
                    weights[agent.name] = 0.5 + (track["accuracy"] * 0.5)
            if weights:
                agent_weights = weights

        tasks = [
            call_agent(
                agent, request, self.api_key, self.base_url,
                memory_context=memory_contexts.get(agent.name, ""),
            )
            for agent in self.agents
        ]
        votes: list[AgentVote] = await asyncio.gather(*tasks)

        duration = time.time() - start
        outcome, position, confidence, summary, dissents = self._tally(
            votes, agent_weights=agent_weights
        )

        return Decision(
            request_id=request.request_id,
            department=self.name,
            outcome=outcome,
            position=position,
            confidence=confidence,
            votes=votes,
            summary=summary,
            dissenting_views=dissents,
            duration_seconds=round(duration, 2),
        )

    def _normalize_position(self, position: str) -> str:
        """Map freeform agent positions to YES/NO/MAYBE."""
        normalized = (position or "").strip().upper()

        if not normalized:
            return "MAYBE"
        if normalized == "ERROR":
            return "ERROR"
        if normalized in {"YES", "NO", "MAYBE"}:
            return normalized

        yes_terms = {
            "YES", "Y", "APPROVE", "APPROVED", "ACCEPT", "ACCEPTED", "GO",
            "GO FOR IT", "PROCEED", "PROCEEDING", "SHIP", "LAUNCH", "GREENLIGHT",
            "GREEN LIGHT", "SUPPORT", "SUPPORTED", "FAVOR", "IN FAVOR",
        }
        no_terms = {
            "NO", "N", "REJECT", "REJECTED", "DECLINE", "DECLINED", "DENY",
            "DENIED", "STOP", "BLOCK", "BLOCKED", "VETO", "OPPOSE", "AGAINST",
            "REJECTION",
        }
        maybe_terms = {
            "MAYBE", "UNSURE", "UNCERTAIN", "MIXED", "HOLD", "WAIT",
            "PROCEED WITH CAUTION", "CAUTION", "CONDITIONAL", "NEEDS MORE DATA",
        }

        if normalized in yes_terms:
            return "YES"
        if normalized in no_terms:
            return "NO"
        if normalized in maybe_terms:
            return "MAYBE"

        tokens = set(normalized.replace("-", " ").replace(",", " ").split())
        if {"YES", "APPROVE", "ACCEPT", "PROCEED", "GO", "LAUNCH", "SHIP"} & tokens:
            return "YES"
        if {"NO", "REJECT", "REJECTION", "DECLINE", "DENY", "STOP", "BLOCK", "VETO"} & tokens:
            return "NO"
        if {"MAYBE", "CAUTION", "UNCERTAIN", "UNSURE", "HOLD", "WAIT", "CONDITIONAL"} & tokens:
            return "MAYBE"

        return "MAYBE"

    def _tally(
        self,
        votes: list[AgentVote],
        agent_weights: Optional[dict[str, float]] = None,
    ) -> tuple[str, str, float, str, list[str]]:
        """Tally votes and determine outcome.

        If agent_weights is provided, votes are weighted by agent track record.
        Weight formula: 0.5 + (accuracy * 0.5) → range [0.5, 1.0].
        """
        if not votes:
            return "DEADLOCK", "NONE", 0.0, "No votes received.", []

        # Count positions (excluding ERROR votes)
        valid_votes = [v for v in votes if self._normalize_position(v.position) != "ERROR"]
        if not valid_votes:
            return "DEADLOCK", "NONE", 0.0, "All agents failed.", []

        # Group votes by normalized position with weights
        position_weights: dict[str, float] = {}
        position_votes: dict[str, list[AgentVote]] = {}
        for v in valid_votes:
            normalized_position = self._normalize_position(v.position)
            position_votes.setdefault(normalized_position, []).append(v)
            weight = 1.0
            if agent_weights is not None:
                weight = agent_weights.get(v.agent_name, 1.0)
            position_weights[normalized_position] = (
                position_weights.get(normalized_position, 0.0) + weight
            )

        # Find the leading position by weighted count
        sorted_positions = sorted(
            position_weights.items(), key=lambda x: x[1], reverse=True
        )
        top_position = sorted_positions[0][0]
        top_votes = position_votes[top_position]
        top_weighted = position_weights[top_position]
        total_weighted = sum(position_weights.values())
        ratio = top_weighted / total_weighted

        # Unweighted counts for summary messages
        top_count = len(top_votes)
        total = len(valid_votes)

        # Calculate confidence as weighted average of agreeing votes
        avg_conf = sum(v.confidence for v in top_votes) / top_count

        # Collect dissenting views
        dissents = []
        for v in valid_votes:
            if self._normalize_position(v.position) != top_position and v.dissent:
                dissents.append(f"{v.agent_name}: {v.dissent}")

        # Determine outcome
        if top_count == total:
            outcome = "CONSENSUS"
            summary = (
                f"Unanimous: all {total} agents in {self.name} agree on {top_position}."
            )
        elif ratio >= self.threshold:
            outcome = "MAJORITY"
            summary = (
                f"{top_count}/{total} agents in {self.name} favor {top_position}. "
                f"{total - top_count} dissenting."
            )
        else:
            outcome = "SPLIT"
            positions_str = ", ".join(
                f"{pos}: {len(position_votes[pos])}"
                for pos, _ in sorted_positions
            )
            summary = (
                f"No clear majority in {self.name}. Positions: {positions_str}."
            )

        confidence = round(avg_conf * ratio, 3)
        return outcome, top_position, confidence, summary, dissents
