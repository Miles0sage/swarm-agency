"""Learning module - agents improve from feedback over time."""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .types import AgentConfig, Decision

logger = logging.getLogger("swarm_agency.learning")

DEFAULT_MEMORY_DIR = os.path.expanduser("~/.swarm-agency/memory")


@dataclass
class Feedback:
    """User feedback on a decision."""
    request_id: str
    was_correct: bool  # did the decision lead to a good outcome?
    notes: Optional[str] = None
    correct_position: Optional[str] = None  # what should the answer have been?


@dataclass
class AgentMemory:
    """Tracked performance and learnings for an agent."""
    agent_name: str
    total_decisions: int = 0
    correct_decisions: int = 0
    accuracy: float = 0.0
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    prompt_amendments: list[str] = field(default_factory=list)


class LearningEngine:
    """Tracks agent performance and evolves their prompts based on feedback."""

    def __init__(self, memory_dir: str = DEFAULT_MEMORY_DIR):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memories: dict[str, AgentMemory] = {}
        self._load_memories()

    def _load_memories(self) -> None:
        """Load agent memories from disk."""
        memory_file = self.memory_dir / "agent_memories.json"
        if memory_file.exists():
            try:
                data = json.loads(memory_file.read_text())
                for name, mem_data in data.items():
                    self.memories[name] = AgentMemory(**mem_data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to load memories: {e}")

    def _save_memories(self) -> None:
        """Persist agent memories to disk."""
        memory_file = self.memory_dir / "agent_memories.json"
        data = {name: asdict(mem) for name, mem in self.memories.items()}
        memory_file.write_text(json.dumps(data, indent=2))

    def record_decision(self, decision: Decision) -> None:
        """Record a decision for future learning."""
        decision_file = self.memory_dir / f"decision_{decision.request_id}.json"
        decision_file.write_text(json.dumps(decision.to_dict(), indent=2))

    def apply_feedback(self, feedback: Feedback, decision: Decision) -> dict[str, str]:
        """
        Apply user feedback to update agent memories.

        Returns a dict of agent_name → learning note.
        """
        learnings: dict[str, str] = {}

        for vote in decision.votes:
            name = vote.agent_name
            if name not in self.memories:
                self.memories[name] = AgentMemory(agent_name=name)

            mem = self.memories[name]
            mem.total_decisions += 1

            # Did this agent's vote align with the correct outcome?
            agent_correct = (
                feedback.correct_position
                and vote.position.upper() == feedback.correct_position.upper()
            ) or (
                not feedback.correct_position and feedback.was_correct
                and vote.position == decision.position
            )

            if agent_correct:
                mem.correct_decisions += 1
                note = f"Correct on {decision.request_id}"
                if vote.factors:
                    mem.strengths.extend(vote.factors[:2])
                    mem.strengths = list(set(mem.strengths))[-10:]  # keep last 10
            else:
                note = f"Wrong on {decision.request_id}"
                if vote.factors:
                    mem.weaknesses.extend(vote.factors[:2])
                    mem.weaknesses = list(set(mem.weaknesses))[-10:]

            mem.accuracy = (
                mem.correct_decisions / mem.total_decisions
                if mem.total_decisions > 0
                else 0.0
            )
            learnings[name] = note

        self._save_memories()
        return learnings

    def get_agent_stats(self, agent_name: str) -> Optional[AgentMemory]:
        """Get performance stats for an agent."""
        return self.memories.get(agent_name)

    def get_all_stats(self) -> dict[str, AgentMemory]:
        """Get performance stats for all agents."""
        return dict(self.memories)

    def suggest_prompt_amendment(self, agent_name: str) -> Optional[str]:
        """
        Based on accumulated feedback, suggest a prompt amendment.

        Returns a suggested addition to the agent's system prompt, or None.
        """
        mem = self.memories.get(agent_name)
        if not mem or mem.total_decisions < 5:
            return None  # not enough data

        suggestions = []

        if mem.accuracy < 0.4:
            suggestions.append(
                f"WARNING: Your accuracy is {mem.accuracy:.0%}. "
                "Consider being less confident in your predictions and "
                "weighing more factors before deciding."
            )

        if mem.weaknesses:
            weak_str = ", ".join(mem.weaknesses[:5])
            suggestions.append(
                f"Areas where you've been wrong before: {weak_str}. "
                "Pay extra attention to these factors."
            )

        if mem.strengths:
            strong_str = ", ".join(mem.strengths[:5])
            suggestions.append(
                f"Your strongest factors: {strong_str}. "
                "Lean into these in your analysis."
            )

        if suggestions:
            amendment = " ".join(suggestions)
            mem.prompt_amendments.append(amendment)
            mem.prompt_amendments = mem.prompt_amendments[-5:]  # keep last 5
            self._save_memories()
            return amendment

        return None

    def evolve_agent(self, agent: AgentConfig) -> AgentConfig:
        """
        Return a new AgentConfig with an evolved system prompt
        based on accumulated learnings.
        """
        amendment = self.suggest_prompt_amendment(agent.name)
        if not amendment:
            return agent

        evolved_prompt = (
            f"{agent.system_prompt}\n\n"
            f"## Learnings from past decisions\n{amendment}"
        )

        return AgentConfig(
            name=agent.name,
            role=agent.role,
            expertise=agent.expertise,
            bias=agent.bias,
            system_prompt=evolved_prompt,
            model=agent.model,
        )
