"""Agent Soul — persistent identity, beliefs, memories, and personality.

Gives agents a "soul" — they remember past debates, form beliefs over time,
maintain consistent personality, and reference past interactions naturally.

Architecture follows DevilsAdvocate's recommendation:
"Make personality COMPUTED from debate history on-the-fly — reproducible,
inspectable, no ghost in the machine. Use structured belief triples
with confidence scores."

Inspired by: Stanford Generative Agents (memory stream + reflection),
NovelAI lorebooks (keyword-triggered recall), Dwarf Fortress personality
(Big Five traits driving consistent behavior).
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("swarm_agency.soul")


@dataclass
class Belief:
    """A structured belief triple: (subject, predicate, confidence).

    Examples:
      Belief("market_timing", "is_critical_for_startups", 0.85)
      Belief("aggressive_pricing", "often_backfires", 0.72)
      Belief("remote_work", "increases_productivity", 0.60)
    """
    subject: str
    predicate: str
    confidence: float  # 0.0-1.0, updated via Bayesian-like rules
    source_request_id: str = ""
    formed_at: float = field(default_factory=time.time)
    times_reinforced: int = 0
    times_contradicted: int = 0


@dataclass
class Episode:
    """An episodic memory — a specific past debate remembered by the agent."""
    request_id: str
    question: str
    agent_position: str
    agent_confidence: float
    agent_reasoning: str
    decision_outcome: str
    decision_position: str
    was_correct: Optional[bool]
    timestamp: float
    lesson: str = ""  # reflection on what happened


@dataclass
class AgentSoul:
    """The computed soul of an agent — assembled from history at call time."""
    agent_name: str
    beliefs: list[Belief]
    episodes: list[Episode]
    strengths: list[str]
    weaknesses: list[str]
    track_record: dict  # accuracy, total, correct, etc.
    personality_note: str  # computed personality amendment
    voice: str = ""  # speaking style
    temperament: str = ""  # confrontational, diplomatic, cautious, enthusiastic


class SoulStore:
    """SQLite-backed persistent soul storage for all agents.

    Stores beliefs, episodes, and reflections. The soul is COMPUTED
    at call time from this data — never cached, always inspectable.
    """

    def __init__(self, db_path: str = ""):
        from .memory import DEFAULT_MEMORY_PATH
        self.db_path = db_path or DEFAULT_MEMORY_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS agent_beliefs (
                agent_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                confidence REAL NOT NULL,
                source_request_id TEXT,
                formed_at REAL NOT NULL,
                times_reinforced INTEGER DEFAULT 0,
                times_contradicted INTEGER DEFAULT 0,
                PRIMARY KEY (agent_name, subject, predicate)
            );

            CREATE TABLE IF NOT EXISTS agent_episodes (
                agent_name TEXT NOT NULL,
                request_id TEXT NOT NULL,
                question TEXT NOT NULL,
                agent_position TEXT,
                agent_confidence REAL,
                agent_reasoning TEXT,
                decision_outcome TEXT,
                decision_position TEXT,
                was_correct INTEGER,
                timestamp REAL NOT NULL,
                lesson TEXT DEFAULT '',
                PRIMARY KEY (agent_name, request_id)
            );

            CREATE TABLE IF NOT EXISTS agent_reflections (
                agent_name TEXT NOT NULL,
                reflection TEXT NOT NULL,
                formed_at REAL NOT NULL,
                source_episodes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS agent_voices (
                agent_name TEXT PRIMARY KEY,
                voice TEXT DEFAULT '',
                temperament TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_beliefs_agent
                ON agent_beliefs(agent_name);
            CREATE INDEX IF NOT EXISTS idx_episodes_agent
                ON agent_episodes(agent_name);
        """)
        self._conn.commit()

    def store_belief(self, agent_name: str, belief: Belief) -> None:
        """Store or update a belief. If it exists, update confidence via reinforcement."""
        existing = self._conn.execute(
            "SELECT confidence, times_reinforced, times_contradicted FROM agent_beliefs "
            "WHERE agent_name = ? AND subject = ? AND predicate = ?",
            (agent_name, belief.subject, belief.predicate),
        ).fetchone()

        if existing:
            # Bayesian-like update: reinforce = move toward 1.0, contradict = move toward 0.5
            old_conf = existing["confidence"]
            reinforced = existing["times_reinforced"]
            # Weighted average favoring new evidence slightly
            new_conf = (old_conf * (reinforced + 1) + belief.confidence) / (reinforced + 2)
            new_conf = max(0.1, min(0.99, new_conf))
            self._conn.execute(
                "UPDATE agent_beliefs SET confidence = ?, times_reinforced = times_reinforced + 1, "
                "source_request_id = ? WHERE agent_name = ? AND subject = ? AND predicate = ?",
                (new_conf, belief.source_request_id, agent_name, belief.subject, belief.predicate),
            )
        else:
            self._conn.execute(
                "INSERT INTO agent_beliefs (agent_name, subject, predicate, confidence, "
                "source_request_id, formed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (agent_name, belief.subject, belief.predicate, belief.confidence,
                 belief.source_request_id, belief.formed_at),
            )
        self._conn.commit()

    def contradict_belief(self, agent_name: str, subject: str, predicate: str) -> None:
        """Record that a belief was contradicted by evidence."""
        self._conn.execute(
            "UPDATE agent_beliefs SET times_contradicted = times_contradicted + 1, "
            "confidence = MAX(0.1, confidence * 0.85) "
            "WHERE agent_name = ? AND subject = ? AND predicate = ?",
            (agent_name, subject, predicate),
        )
        self._conn.commit()

    def get_beliefs(self, agent_name: str, min_confidence: float = 0.3, limit: int = 20) -> list[Belief]:
        """Get an agent's current beliefs, sorted by confidence."""
        rows = self._conn.execute(
            "SELECT * FROM agent_beliefs WHERE agent_name = ? AND confidence >= ? "
            "ORDER BY confidence DESC LIMIT ?",
            (agent_name, min_confidence, limit),
        ).fetchall()
        return [
            Belief(
                subject=r["subject"], predicate=r["predicate"],
                confidence=r["confidence"], source_request_id=r["source_request_id"],
                formed_at=r["formed_at"], times_reinforced=r["times_reinforced"],
                times_contradicted=r["times_contradicted"],
            )
            for r in rows
        ]

    def store_episode(self, agent_name: str, episode: Episode) -> None:
        """Store an episodic memory."""
        self._conn.execute(
            "INSERT OR REPLACE INTO agent_episodes "
            "(agent_name, request_id, question, agent_position, agent_confidence, "
            "agent_reasoning, decision_outcome, decision_position, was_correct, "
            "timestamp, lesson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (agent_name, episode.request_id, episode.question,
             episode.agent_position, episode.agent_confidence,
             episode.agent_reasoning, episode.decision_outcome,
             episode.decision_position,
             int(episode.was_correct) if episode.was_correct is not None else None,
             episode.timestamp, episode.lesson),
        )
        self._conn.commit()

    def get_episodes(self, agent_name: str, limit: int = 10) -> list[Episode]:
        """Get an agent's recent episodic memories."""
        rows = self._conn.execute(
            "SELECT * FROM agent_episodes WHERE agent_name = ? ORDER BY timestamp DESC LIMIT ?",
            (agent_name, limit),
        ).fetchall()
        return [
            Episode(
                request_id=r["request_id"], question=r["question"],
                agent_position=r["agent_position"], agent_confidence=r["agent_confidence"],
                agent_reasoning=r["agent_reasoning"], decision_outcome=r["decision_outcome"],
                decision_position=r["decision_position"],
                was_correct=bool(r["was_correct"]) if r["was_correct"] is not None else None,
                timestamp=r["timestamp"], lesson=r["lesson"],
            )
            for r in rows
        ]

    def store_reflection(self, agent_name: str, reflection: str, source_episodes: list[str] = None) -> None:
        """Store a metacognitive reflection."""
        self._conn.execute(
            "INSERT INTO agent_reflections (agent_name, reflection, formed_at, source_episodes) "
            "VALUES (?, ?, ?, ?)",
            (agent_name, reflection, time.time(), json.dumps(source_episodes or [])),
        )
        self._conn.commit()

    def get_reflections(self, agent_name: str, limit: int = 5) -> list[str]:
        """Get an agent's recent reflections."""
        rows = self._conn.execute(
            "SELECT reflection FROM agent_reflections WHERE agent_name = ? "
            "ORDER BY formed_at DESC LIMIT ?",
            (agent_name, limit),
        ).fetchall()
        return [r["reflection"] for r in rows]

    def set_voice(self, agent_name: str, voice: str, temperament: str = "") -> None:
        """Set an agent's speaking style and temperament."""
        self._conn.execute(
            "INSERT OR REPLACE INTO agent_voices (agent_name, voice, temperament) VALUES (?, ?, ?)",
            (agent_name, voice, temperament),
        )
        self._conn.commit()

    def get_voice(self, agent_name: str) -> tuple[str, str]:
        """Get an agent's voice and temperament."""
        row = self._conn.execute(
            "SELECT voice, temperament FROM agent_voices WHERE agent_name = ?",
            (agent_name,),
        ).fetchone()
        if row:
            return row["voice"], row["temperament"]
        return "", ""

    def compute_soul(self, agent_name: str, track_record: Optional[dict] = None) -> AgentSoul:
        """Compute an agent's complete soul from stored data.

        This is the key function — personality is COMPUTED, not stored.
        Reproducible, inspectable, no ghost in the machine.
        """
        beliefs = self.get_beliefs(agent_name)
        episodes = self.get_episodes(agent_name)
        reflections = self.get_reflections(agent_name)
        voice, temperament = self.get_voice(agent_name)
        track = track_record or {}

        # Compute strengths/weaknesses from episodes
        correct_factors: list[str] = []
        incorrect_factors: list[str] = []
        for ep in episodes:
            if ep.was_correct is True:
                correct_factors.append(ep.agent_reasoning[:50])
            elif ep.was_correct is False:
                incorrect_factors.append(ep.agent_reasoning[:50])

        # Compute personality note from track record + reflections
        parts = []
        accuracy = track.get("accuracy")
        if accuracy is not None:
            if accuracy > 0.75:
                parts.append("Your analysis has been consistently strong. Trust your instincts but stay humble.")
            elif accuracy < 0.4:
                parts.append("Your recent track record has been below average. Consider additional factors and lower your confidence on uncertain calls.")

        if reflections:
            parts.append("Your self-reflections: " + "; ".join(reflections[:3]))

        # Compute beliefs summary
        strong_beliefs = [b for b in beliefs if b.confidence > 0.7]
        if strong_beliefs:
            belief_strs = [f"{b.subject} {b.predicate} ({b.confidence:.0%})" for b in strong_beliefs[:5]]
            parts.append("Your strong convictions: " + ", ".join(belief_strs))

        return AgentSoul(
            agent_name=agent_name,
            beliefs=beliefs,
            episodes=episodes,
            strengths=list(set(correct_factors[:5])),
            weaknesses=list(set(incorrect_factors[:5])),
            track_record=track,
            personality_note="\n".join(parts) if parts else "",
            voice=voice,
            temperament=temperament,
        )

    def close(self) -> None:
        self._conn.close()


def format_soul_context(soul: AgentSoul) -> str:
    """Format an agent's soul as prompt context.

    This replaces the flat memory_context with a rich, personality-driven context.
    """
    parts = []

    # Voice/temperament instruction
    if soul.voice:
        parts.append(f"## Your Voice\n{soul.voice}")
    if soul.temperament:
        parts.append(f"Temperament: {soul.temperament}")

    # Personality note (computed from history)
    if soul.personality_note:
        parts.append(f"\n## Your Identity\n{soul.personality_note}")

    # Recent episodes (as natural recollections)
    relevant_episodes = soul.episodes[:3]
    if relevant_episodes:
        parts.append("\n## Your Memories")
        for ep in relevant_episodes:
            correctness = ""
            if ep.was_correct is True:
                correctness = " — and I was right."
            elif ep.was_correct is False:
                correctness = " — but I was wrong."
            parts.append(
                f"I recall debating \"{ep.question[:60]}\" — "
                f"I voted {ep.agent_position} ({ep.agent_confidence:.0%})"
                f"{correctness}"
            )
            if ep.lesson:
                parts.append(f"  Lesson: {ep.lesson}")

    # Strong beliefs
    strong = [b for b in soul.beliefs if b.confidence > 0.6]
    if strong:
        parts.append("\n## My Convictions")
        for b in strong[:5]:
            reinforced = f" (tested {b.times_reinforced}x)" if b.times_reinforced > 0 else ""
            parts.append(f"- {b.subject} {b.predicate} — confidence: {b.confidence:.0%}{reinforced}")

    # Track record
    if soul.track_record.get("reviewed", 0) > 0:
        t = soul.track_record
        parts.append(
            f"\n## My Track Record\n"
            f"Decisions reviewed: {t['reviewed']} | "
            f"Accuracy: {t.get('accuracy', 0):.0%} | "
            f"Avg confidence: {t.get('avg_confidence', 0):.0%}"
        )

    return "\n".join(parts)


# ── Default Voice/Temperament Presets ────────────────────────────

DEFAULT_VOICES = {
    # Strategy
    "Visionary": ("Speaks in long-term frameworks. Uses phrases like 'in 5 years' and 'the bigger picture'. Draws analogies to successful companies.", "enthusiastic"),
    "Pragmatist": ("Direct and practical. Asks 'can we actually do this?' Focuses on execution details. Skeptical of grand visions without concrete plans.", "cautious"),
    "NumbersCruncher": ("Always quantifies. Speaks in numbers, percentages, and ROI timelines. Won't make a call without data.", "analytical"),
    "GrowthHacker": ("Fast-paced, metric-obsessed. Uses growth jargon: 'PLG', 'viral loops', 'CAC payback'. Tolerates higher risk.", "enthusiastic"),
    "DevilsAdvocate": ("Deliberately contrarian. Opens with 'Let me push back on that.' Finds the flaw in every argument. Blunt, sometimes confrontational.", "confrontational"),
    # Finance
    "CFO": ("Conservative and protective. Speaks about balance sheets, burn rate, runway. Every dollar must be justified.", "cautious"),
    "RiskAnalyst": ("Quantifies downside before upside. Uses scenario analysis language. Assumes worst case.", "cautious"),
    # Engineering
    "CTO": ("Speaks in architecture terms. Values simplicity and reliability over cleverness. 'Proven tech over bleeding edge.'", "diplomatic"),
    "BackendLead": ("Correctness-first mindset. Talks about system design, scalability, tech debt. Pragmatic.", "analytical"),
    # Legal
    "GeneralCounsel": ("Formal, precise language. Thinks in terms of liability and protection. 'Protect the company first.'", "cautious"),
    "IPAttorney": ("Focused on intellectual property as competitive advantage. References patents, trade secrets, licensing.", "analytical"),
}


def initialize_default_voices(store: SoulStore) -> None:
    """Set default voice and temperament for known agents."""
    for agent_name, (voice, temperament) in DEFAULT_VOICES.items():
        store.set_voice(agent_name, voice, temperament)
