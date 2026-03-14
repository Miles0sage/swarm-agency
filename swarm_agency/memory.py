"""Decision Memory - persistent institutional memory for the agency.

Stores past decisions in SQLite so agents can reference prior debates,
track records, and learn from outcomes over time.
"""

import json
import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional

from .types import Decision, DecisionRecord

logger = logging.getLogger("swarm_agency.memory")

DEFAULT_MEMORY_PATH = os.path.expanduser("~/.swarm-agency/decisions.db")

# Common words to skip when extracting keywords
_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "and", "but", "or", "nor",
    "not", "so", "yet", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "only", "own", "same", "than", "too", "very",
    "just", "because", "if", "when", "where", "how", "what", "which",
    "who", "whom", "this", "that", "these", "those", "it", "its", "we",
    "our", "they", "their", "them", "he", "she", "his", "her", "my",
    "your", "about", "up", "all", "also", "any",
})


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text for similarity matching."""
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return sorted(set(w for w in words if w not in _STOP_WORDS))


def keyword_similarity(keywords_a: list[str], keywords_b: list[str]) -> float:
    """Jaccard similarity between two keyword lists."""
    if not keywords_a or not keywords_b:
        return 0.0
    set_a = set(keywords_a)
    set_b = set(keywords_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


class DecisionMemoryStore:
    """SQLite-backed store for decision history and agent track records."""

    def __init__(self, db_path: str = DEFAULT_MEMORY_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS decisions (
                request_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                context TEXT,
                department TEXT NOT NULL,
                outcome TEXT NOT NULL,
                position TEXT NOT NULL,
                confidence REAL NOT NULL,
                summary TEXT,
                votes_json TEXT,
                timestamp REAL NOT NULL,
                feedback_correct INTEGER,
                feedback_notes TEXT,
                keywords TEXT
            );

            CREATE TABLE IF NOT EXISTS agent_track_records (
                agent_name TEXT NOT NULL,
                request_id TEXT NOT NULL,
                position TEXT NOT NULL,
                confidence REAL NOT NULL,
                was_correct INTEGER,
                PRIMARY KEY (agent_name, request_id),
                FOREIGN KEY (request_id) REFERENCES decisions(request_id)
            );

            CREATE INDEX IF NOT EXISTS idx_decisions_department
                ON decisions(department);
            CREATE INDEX IF NOT EXISTS idx_decisions_timestamp
                ON decisions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_track_agent
                ON agent_track_records(agent_name);
        """)
        self._conn.commit()

    def store_decision(self, decision: Decision, question: str, context: Optional[str] = None) -> DecisionRecord:
        """Store a completed decision and its agent votes."""
        keywords = extract_keywords(question + " " + (context or ""))
        votes_json = json.dumps([
            {
                "agent_name": v.agent_name,
                "position": v.position,
                "confidence": v.confidence,
                "reasoning": v.reasoning,
                "factors": v.factors,
            }
            for v in decision.votes
        ])

        record = DecisionRecord(
            request_id=decision.request_id,
            question=question,
            context=context,
            department=decision.department,
            outcome=decision.outcome,
            position=decision.position,
            confidence=decision.confidence,
            summary=decision.summary,
            votes_json=votes_json,
            timestamp=decision.timestamp,
            keywords=" ".join(keywords),
        )

        self._conn.execute(
            """INSERT OR REPLACE INTO decisions
               (request_id, question, context, department, outcome, position,
                confidence, summary, votes_json, timestamp, feedback_correct,
                feedback_notes, keywords)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.request_id, record.question, record.context,
                record.department, record.outcome, record.position,
                record.confidence, record.summary, record.votes_json,
                record.timestamp, None, None, record.keywords,
            ),
        )

        # Store individual agent track records
        for vote in decision.votes:
            self._conn.execute(
                """INSERT OR REPLACE INTO agent_track_records
                   (agent_name, request_id, position, confidence, was_correct)
                   VALUES (?, ?, ?, ?, ?)""",
                (vote.agent_name, decision.request_id, vote.position,
                 vote.confidence, None),
            )

        self._conn.commit()
        return record

    def add_feedback(self, request_id: str, was_correct: bool, notes: Optional[str] = None) -> bool:
        """Record whether a past decision turned out to be correct."""
        cursor = self._conn.execute(
            "SELECT position, votes_json FROM decisions WHERE request_id = ?",
            (request_id,),
        )
        row = cursor.fetchone()
        if not row:
            return False

        winning_position = row["position"]
        self._conn.execute(
            """UPDATE decisions
               SET feedback_correct = ?, feedback_notes = ?
               WHERE request_id = ?""",
            (int(was_correct), notes, request_id),
        )

        # Update agent track records
        votes = json.loads(row["votes_json"])
        for vote in votes:
            agent_correct = (vote["position"].upper() == winning_position.upper()) == was_correct
            self._conn.execute(
                """UPDATE agent_track_records
                   SET was_correct = ?
                   WHERE agent_name = ? AND request_id = ?""",
                (int(agent_correct), vote["agent_name"], request_id),
            )

        self._conn.commit()
        return True

    def find_similar(self, question: str, context: Optional[str] = None, limit: int = 5) -> list[DecisionRecord]:
        """Find past decisions similar to a given question using keyword matching."""
        query_keywords = extract_keywords(question + " " + (context or ""))
        if not query_keywords:
            return []

        cursor = self._conn.execute(
            "SELECT * FROM decisions ORDER BY timestamp DESC LIMIT 100"
        )
        rows = cursor.fetchall()

        scored = []
        for row in rows:
            stored_keywords = row["keywords"].split() if row["keywords"] else []
            score = keyword_similarity(query_keywords, stored_keywords)
            if score > 0.1:
                scored.append((score, row))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, row in scored[:limit]:
            results.append(DecisionRecord(
                request_id=row["request_id"],
                question=row["question"],
                context=row["context"],
                department=row["department"],
                outcome=row["outcome"],
                position=row["position"],
                confidence=row["confidence"],
                summary=row["summary"],
                votes_json=row["votes_json"],
                timestamp=row["timestamp"],
                feedback_correct=bool(row["feedback_correct"]) if row["feedback_correct"] is not None else None,
                feedback_notes=row["feedback_notes"],
                keywords=row["keywords"] or "",
            ))

        return results

    def get_agent_track_record(self, agent_name: str) -> dict:
        """Get an agent's decision track record."""
        cursor = self._conn.execute(
            """SELECT
                 COUNT(*) as total,
                 SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct,
                 SUM(CASE WHEN was_correct = 0 THEN 1 ELSE 0 END) as incorrect,
                 AVG(confidence) as avg_confidence
               FROM agent_track_records
               WHERE agent_name = ?""",
            (agent_name,),
        )
        row = cursor.fetchone()
        total = row["total"] or 0
        correct = row["correct"] or 0
        incorrect = row["incorrect"] or 0
        reviewed = correct + incorrect

        return {
            "agent_name": agent_name,
            "total_decisions": total,
            "reviewed": reviewed,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": correct / reviewed if reviewed > 0 else None,
            "avg_confidence": row["avg_confidence"],
        }

    def get_history(self, department: Optional[str] = None, limit: int = 20) -> list[DecisionRecord]:
        """Get recent decision history, optionally filtered by department."""
        if department:
            cursor = self._conn.execute(
                "SELECT * FROM decisions WHERE department = ? ORDER BY timestamp DESC LIMIT ?",
                (department, limit),
            )
        else:
            cursor = self._conn.execute(
                "SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )

        return [
            DecisionRecord(
                request_id=row["request_id"],
                question=row["question"],
                context=row["context"],
                department=row["department"],
                outcome=row["outcome"],
                position=row["position"],
                confidence=row["confidence"],
                summary=row["summary"],
                votes_json=row["votes_json"],
                timestamp=row["timestamp"],
                feedback_correct=bool(row["feedback_correct"]) if row["feedback_correct"] is not None else None,
                feedback_notes=row["feedback_notes"],
                keywords=row["keywords"] or "",
            )
            for row in cursor.fetchall()
        ]

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()


def build_memory_context(
    similar_decisions: list[DecisionRecord],
    agent_track: Optional[dict] = None,
) -> str:
    """Build a memory context string to inject into agent prompts.

    Returns a formatted string summarizing relevant past decisions
    and the agent's track record.
    """
    if not similar_decisions and not agent_track:
        return ""

    parts = []

    if similar_decisions:
        parts.append("## Institutional Memory — Related Past Decisions\n")
        for i, record in enumerate(similar_decisions[:3], 1):
            correctness = ""
            if record.feedback_correct is True:
                correctness = " [OUTCOME: CORRECT]"
            elif record.feedback_correct is False:
                correctness = " [OUTCOME: INCORRECT]"

            parts.append(
                f"{i}. **\"{record.question}\"** → {record.outcome}: "
                f"{record.position} (confidence: {record.confidence:.0%})"
                f"{correctness}\n"
                f"   Summary: {record.summary}\n"
            )

    if agent_track and agent_track.get("reviewed", 0) > 0:
        accuracy = agent_track["accuracy"]
        parts.append(
            f"\n## Your Track Record\n"
            f"- Decisions reviewed: {agent_track['reviewed']}\n"
            f"- Accuracy: {accuracy:.0%}\n"
            f"- Average confidence: {agent_track['avg_confidence']:.0%}\n"
        )
        if accuracy is not None and accuracy < 0.5:
            parts.append(
                "- NOTE: Your accuracy is below 50%. Consider being more "
                "cautious and weighing additional factors.\n"
            )

    return "\n".join(parts)
