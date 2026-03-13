"""Department - a group of agents that debate and reach decisions."""

import asyncio
import logging
import time

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .agent import call_agent

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
    ):
        self.name = name
        self.agents = agents
        self.threshold = threshold  # fraction needed for CONSENSUS/MAJORITY
        self.api_key = api_key
        self.base_url = base_url

    async def debate(self, request: AgencyRequest) -> Decision:
        """Run all agents in parallel, tally positions, return a Decision."""
        start = time.time()

        tasks = [
            call_agent(agent, request, self.api_key, self.base_url)
            for agent in self.agents
        ]
        votes: list[AgentVote] = await asyncio.gather(*tasks)

        duration = time.time() - start
        outcome, position, confidence, summary, dissents = self._tally(votes)

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
        self, votes: list[AgentVote]
    ) -> tuple[str, str, float, str, list[str]]:
        """Tally votes and determine outcome."""
        if not votes:
            return "DEADLOCK", "NONE", 0.0, "No votes received.", []

        # Count positions (excluding ERROR votes)
        valid_votes = [v for v in votes if self._normalize_position(v.position) != "ERROR"]
        if not valid_votes:
            return "DEADLOCK", "NONE", 0.0, "All agents failed.", []

        position_counts: dict[str, list[AgentVote]] = {}
        for v in valid_votes:
            normalized_position = self._normalize_position(v.position)
            position_counts.setdefault(normalized_position, []).append(v)

        # Find the leading position
        sorted_positions = sorted(
            position_counts.items(), key=lambda x: len(x[1]), reverse=True
        )
        top_position, top_votes = sorted_positions[0]
        top_count = len(top_votes)
        total = len(valid_votes)
        ratio = top_count / total

        # Calculate confidence as weighted average of agreeing votes
        avg_conf = sum(v.confidence for v in top_votes) / top_count

        # Collect dissenting views
        dissents = []
        for v in valid_votes:
            if self._normalize_position(v.position) != top_position and v.dissent:
                dissents.append(f"{v.agent_name}: {v.dissent}")

        # Determine outcome
        if ratio >= 1.0:
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
                f"{pos}: {len(vs)}" for pos, vs in sorted_positions
            )
            summary = (
                f"No clear majority in {self.name}. Positions: {positions_str}."
            )

        confidence = round(avg_conf * ratio, 3)
        return outcome, top_position, confidence, summary, dissents
