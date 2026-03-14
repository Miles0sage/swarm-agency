"""Prompt optimizer — uses feedback data to improve agent system prompts.

Two strategies:
1. Built-in heuristic optimization (no dependencies, always available)
2. DSPy MIPROv2 optimization (requires dspy-ai package, optional)

The built-in optimizer analyzes feedback patterns and generates prompt
amendments. DSPy does proper Bayesian optimization of the full prompt.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .types import AgentConfig
from .memory import DecisionMemoryStore

logger = logging.getLogger("swarm_agency.optimizer")

DEFAULT_OPTIMIZED_DIR = os.path.expanduser("~/.swarm-agency/optimized")


@dataclass
class OptimizationResult:
    """Result of a prompt optimization run."""
    agent_name: str
    original_prompt: str
    optimized_prompt: str
    improvement_notes: list[str]
    feedback_used: int  # number of feedback records analyzed
    accuracy_before: Optional[float] = None
    accuracy_after: Optional[float] = None


class PromptOptimizer:
    """Optimizes agent prompts based on accumulated feedback.

    Uses a heuristic approach: analyzes patterns in correct/incorrect
    decisions and generates targeted prompt amendments.
    """

    def __init__(
        self,
        memory_store: DecisionMemoryStore,
        output_dir: str = DEFAULT_OPTIMIZED_DIR,
    ):
        self.memory_store = memory_store
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_agent(self, agent_name: str) -> dict:
        """Analyze an agent's performance patterns from feedback."""
        track = self.memory_store.get_agent_track_record(agent_name)
        if track["total_decisions"] == 0:
            return {"status": "no_data", "agent": agent_name}

        # Get detailed decision history for this agent
        history = self.memory_store.get_history(limit=100)
        agent_decisions = []
        for record in history:
            if record.votes_json:
                votes = json.loads(record.votes_json)
                for vote in votes:
                    if vote.get("agent_name") == agent_name:
                        agent_decisions.append({
                            "question": record.question,
                            "agent_position": vote.get("position", ""),
                            "agent_confidence": vote.get("confidence", 0.5),
                            "agent_reasoning": vote.get("reasoning", ""),
                            "agent_factors": vote.get("factors", []),
                            "decision_position": record.position,
                            "decision_outcome": record.outcome,
                            "was_correct": record.feedback_correct,
                        })

        # Analyze patterns
        correct_factors: list[str] = []
        incorrect_factors: list[str] = []
        overconfident = 0
        underconfident = 0
        correct_count = 0
        incorrect_count = 0

        for d in agent_decisions:
            if d["was_correct"] is None:
                continue

            agent_agreed = d["agent_position"].upper() == d["decision_position"].upper()
            agent_was_right = (agent_agreed and d["was_correct"]) or (
                not agent_agreed and not d["was_correct"]
            )

            if agent_was_right:
                correct_count += 1
                correct_factors.extend(d["agent_factors"][:2])
                if d["agent_confidence"] < 0.5:
                    underconfident += 1
            else:
                incorrect_count += 1
                incorrect_factors.extend(d["agent_factors"][:2])
                if d["agent_confidence"] > 0.7:
                    overconfident += 1

        return {
            "status": "analyzed",
            "agent": agent_name,
            "total": track["total_decisions"],
            "reviewed": track["reviewed"],
            "accuracy": track["accuracy"],
            "correct_factors": list(set(correct_factors)),
            "incorrect_factors": list(set(incorrect_factors)),
            "overconfident_count": overconfident,
            "underconfident_count": underconfident,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
        }

    def optimize_prompt(self, agent: AgentConfig, min_feedback: int = 5) -> OptimizationResult:
        """Generate an optimized prompt based on feedback patterns.

        Requires at least min_feedback reviewed decisions.
        """
        analysis = self.analyze_agent(agent.name)
        notes: list[str] = []

        if analysis["status"] == "no_data" or analysis.get("reviewed", 0) < min_feedback:
            return OptimizationResult(
                agent_name=agent.name,
                original_prompt=agent.system_prompt,
                optimized_prompt=agent.system_prompt,
                improvement_notes=["Not enough feedback data yet"],
                feedback_used=analysis.get("reviewed", 0),
            )

        amendments: list[str] = []

        # Calibration amendment
        accuracy = analysis.get("accuracy")
        if accuracy is not None:
            if accuracy < 0.4:
                amendments.append(
                    "CALIBRATION: Your past accuracy is below 40%. Be more cautious: "
                    "lower your confidence scores, consider more factors, and look for "
                    "evidence that contradicts your initial instinct."
                )
                notes.append(f"Low accuracy ({accuracy:.0%}): added caution amendment")
            elif accuracy > 0.8:
                amendments.append(
                    "CALIBRATION: Your track record is strong (>80% accuracy). "
                    "Trust your analytical framework but stay humble about edge cases."
                )
                notes.append(f"High accuracy ({accuracy:.0%}): added confidence amendment")

        # Overconfidence amendment
        if analysis.get("overconfident_count", 0) > 2:
            amendments.append(
                "CONFIDENCE: You have been overconfident on incorrect calls. "
                "Reserve confidence above 70% for decisions where you have strong "
                "supporting evidence from multiple factors."
            )
            notes.append("Overconfidence pattern detected")

        # Strength reinforcement
        correct_factors = analysis.get("correct_factors", [])
        if correct_factors:
            top_factors = correct_factors[:5]
            amendments.append(
                f"STRENGTHS: Your strongest analytical factors: {', '.join(top_factors)}. "
                f"Lean into these when they're relevant."
            )
            notes.append(f"Reinforced {len(top_factors)} strength factors")

        # Weakness awareness
        incorrect_factors = analysis.get("incorrect_factors", [])
        if incorrect_factors:
            top_weak = incorrect_factors[:5]
            amendments.append(
                f"BLIND SPOTS: You've been wrong when focusing on: {', '.join(top_weak)}. "
                f"When these factors dominate your analysis, seek additional perspectives."
            )
            notes.append(f"Flagged {len(top_weak)} weakness factors")

        # Build optimized prompt
        if amendments:
            amendment_text = "\n".join(f"- {a}" for a in amendments)
            optimized = (
                f"{agent.system_prompt}\n\n"
                f"## Performance-Based Calibration\n{amendment_text}"
            )
        else:
            optimized = agent.system_prompt
            notes.append("No amendments needed — performance is balanced")

        result = OptimizationResult(
            agent_name=agent.name,
            original_prompt=agent.system_prompt,
            optimized_prompt=optimized,
            improvement_notes=notes,
            feedback_used=analysis.get("reviewed", 0),
            accuracy_before=accuracy,
        )

        # Save optimized prompt
        self._save_optimized(result)
        return result

    def optimize_all(self, agents: list[AgentConfig], min_feedback: int = 5) -> list[OptimizationResult]:
        """Optimize prompts for all agents."""
        return [self.optimize_prompt(agent, min_feedback) for agent in agents]

    def load_optimized(self, agent_name: str) -> Optional[str]:
        """Load a previously optimized prompt from disk."""
        path = self.output_dir / f"{agent_name}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                return data.get("optimized_prompt")
            except (json.JSONDecodeError, OSError):
                pass
        return None

    def apply_optimizations(self, agents: list[AgentConfig]) -> list[AgentConfig]:
        """Return new AgentConfigs with optimized prompts where available."""
        result = []
        for agent in agents:
            optimized = self.load_optimized(agent.name)
            if optimized:
                result.append(AgentConfig(
                    name=agent.name,
                    role=agent.role,
                    expertise=agent.expertise,
                    bias=agent.bias,
                    system_prompt=optimized,
                    model=agent.model,
                ))
            else:
                result.append(agent)
        return result

    def _save_optimized(self, result: OptimizationResult) -> None:
        """Save optimization result to disk."""
        path = self.output_dir / f"{result.agent_name}.json"
        data = {
            "agent_name": result.agent_name,
            "optimized_prompt": result.optimized_prompt,
            "improvement_notes": result.improvement_notes,
            "feedback_used": result.feedback_used,
            "accuracy_before": result.accuracy_before,
        }
        path.write_text(json.dumps(data, indent=2))
