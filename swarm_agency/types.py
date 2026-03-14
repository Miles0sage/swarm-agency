"""Core types for swarm-agency."""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class AgentConfig:
    """Configuration for a single agent in a department."""
    name: str
    role: str  # e.g. "CFO", "Head of Marketing", "Devil's Advocate"
    expertise: str  # what they know
    bias: str  # their analytical bias/perspective
    system_prompt: str  # full system prompt
    model: str = "qwen3-coder-plus"  # which LLM to use


@dataclass
class AgencyRequest:
    """A question or decision for the agency to debate."""
    request_id: str
    question: str  # the question/decision to debate
    context: Optional[str] = None  # additional context
    department: Optional[str] = None  # target specific department, or None for all
    metadata: dict = field(default_factory=dict)  # arbitrary extra data


@dataclass
class AgentVote:
    """A single agent's response to a request."""
    agent_name: str
    position: str  # their stance (e.g. "APPROVE", "REJECT", "YES", "NO", or freeform)
    confidence: float  # 0.0 - 1.0
    reasoning: str
    factors: list[str] = field(default_factory=list)
    dissent: Optional[str] = None  # if they disagree, why specifically

    def __repr__(self) -> str:
        return f"AgentVote(agent_name={self.agent_name}, position={self.position}, confidence={self.confidence})"


@dataclass
class Decision:
    """The agency's collective decision after debate."""
    request_id: str
    department: str
    outcome: str  # "CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK"
    position: str  # the winning position
    confidence: float  # 0.0 - 1.0
    votes: list[AgentVote] = field(default_factory=list)
    summary: str = ""
    dissenting_views: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (
            "Decision("
            f"department={self.department}, "
            f"outcome={self.outcome}, "
            f"position={self.position}, "
            f"confidence={self.confidence:.2f}"
            ")"
        )

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "department": self.department,
            "outcome": self.outcome,
            "position": self.position,
            "confidence": self.confidence,
            "votes": [
                {
                    "agent_name": v.agent_name,
                    "position": v.position,
                    "confidence": v.confidence,
                    "reasoning": v.reasoning,
                    "factors": v.factors,
                    "dissent": v.dissent,
                }
                for v in self.votes
            ],
            "summary": self.summary,
            "dissenting_views": self.dissenting_views,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }


@dataclass
class DecisionRecord:
    """A stored decision with optional feedback for institutional memory."""
    request_id: str
    question: str
    context: Optional[str]
    department: str
    outcome: str
    position: str
    confidence: float
    summary: str
    votes_json: str  # JSON-serialized list of vote dicts
    timestamp: float = field(default_factory=time.time)
    feedback_correct: Optional[bool] = None
    feedback_notes: Optional[str] = None
    keywords: str = ""  # space-separated keywords for similarity matching

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "question": self.question,
            "context": self.context,
            "department": self.department,
            "outcome": self.outcome,
            "position": self.position,
            "confidence": self.confidence,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "feedback_correct": self.feedback_correct,
            "feedback_notes": self.feedback_notes,
        }
