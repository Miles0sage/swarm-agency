"""Agent-to-Agent Messaging — agents can flag issues to other agents.

CTO flags a concern → triggers DevilsAdvocate to challenge it →
CFO runs the numbers → you get ONE consolidated summary.

This creates internal "conversations" between agents that resolve
before reaching the user.
"""

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("swarm_agency.messaging")


@dataclass
class AgentMessage:
    """A message from one agent to another."""
    message_id: str
    from_agent: str
    to_agent: str  # or "all" for broadcast, or department name
    subject: str
    body: str
    priority: str  # "low", "normal", "high", "urgent"
    source_request_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    read: bool = False
    response: Optional[str] = None
    response_timestamp: Optional[float] = None


class MessageBus:
    """SQLite-backed message bus for inter-agent communication."""

    def __init__(self, db_path: str = ""):
        from .memory import DEFAULT_MEMORY_PATH
        self.db_path = db_path or DEFAULT_MEMORY_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS agent_messages (
                message_id TEXT PRIMARY KEY,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'normal',
                source_request_id TEXT,
                timestamp REAL NOT NULL,
                read INTEGER DEFAULT 0,
                response TEXT,
                response_timestamp REAL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_to
                ON agent_messages(to_agent, read);
            CREATE INDEX IF NOT EXISTS idx_messages_from
                ON agent_messages(from_agent);
        """)
        self._conn.commit()

    def send(
        self,
        from_agent: str,
        to_agent: str,
        subject: str,
        body: str,
        priority: str = "normal",
        source_request_id: Optional[str] = None,
    ) -> AgentMessage:
        """Send a message from one agent to another."""
        msg = AgentMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            from_agent=from_agent,
            to_agent=to_agent,
            subject=subject,
            body=body,
            priority=priority,
            source_request_id=source_request_id,
        )
        self._conn.execute(
            """INSERT INTO agent_messages
               (message_id, from_agent, to_agent, subject, body, priority,
                source_request_id, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (msg.message_id, msg.from_agent, msg.to_agent, msg.subject,
             msg.body, msg.priority, msg.source_request_id, msg.timestamp),
        )
        self._conn.commit()
        logger.info(f"Message {msg.message_id}: {from_agent} → {to_agent}: {subject}")
        return msg

    def get_unread(self, agent_name: str, limit: int = 10) -> list[AgentMessage]:
        """Get unread messages for an agent."""
        rows = self._conn.execute(
            """SELECT * FROM agent_messages
               WHERE (to_agent = ? OR to_agent = 'all') AND read = 0
               ORDER BY
                 CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1
                              WHEN 'normal' THEN 2 ELSE 3 END,
                 timestamp DESC
               LIMIT ?""",
            (agent_name, limit),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    def mark_read(self, message_id: str) -> None:
        self._conn.execute(
            "UPDATE agent_messages SET read = 1 WHERE message_id = ?",
            (message_id,),
        )
        self._conn.commit()

    def respond(self, message_id: str, response: str) -> None:
        """Agent responds to a message."""
        self._conn.execute(
            "UPDATE agent_messages SET response = ?, response_timestamp = ?, read = 1 WHERE message_id = ?",
            (response, time.time(), message_id),
        )
        self._conn.commit()

    def get_conversation(self, agent_a: str, agent_b: str, limit: int = 20) -> list[AgentMessage]:
        """Get message history between two agents."""
        rows = self._conn.execute(
            """SELECT * FROM agent_messages
               WHERE (from_agent = ? AND to_agent = ?) OR (from_agent = ? AND to_agent = ?)
               ORDER BY timestamp DESC LIMIT ?""",
            (agent_a, agent_b, agent_b, agent_a, limit),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    def get_recent(self, limit: int = 20) -> list[AgentMessage]:
        """Get all recent messages across the agency."""
        rows = self._conn.execute(
            "SELECT * FROM agent_messages ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    def build_message_context(self, agent_name: str) -> str:
        """Build context string from unread messages for injection into agent prompt."""
        messages = self.get_unread(agent_name, limit=3)
        if not messages:
            return ""

        lines = ["\n## Messages From Colleagues\n"]
        for msg in messages:
            priority_tag = f" [{msg.priority.upper()}]" if msg.priority in ("high", "urgent") else ""
            lines.append(
                f"**From {msg.from_agent}**{priority_tag}: {msg.subject}\n"
                f"{msg.body}\n"
            )
            self.mark_read(msg.message_id)
        return "\n".join(lines)

    def _row_to_message(self, row) -> AgentMessage:
        return AgentMessage(
            message_id=row["message_id"],
            from_agent=row["from_agent"],
            to_agent=row["to_agent"],
            subject=row["subject"],
            body=row["body"],
            priority=row["priority"],
            source_request_id=row["source_request_id"],
            timestamp=row["timestamp"],
            read=bool(row["read"]),
            response=row["response"],
            response_timestamp=row["response_timestamp"],
        )

    def close(self) -> None:
        self._conn.close()


def auto_escalate(decision, message_bus: MessageBus) -> list[AgentMessage]:
    """Auto-generate inter-agent messages based on debate results.

    Called after a debate completes. Creates messages when:
    - Strong dissent exists → message to DevilsAdvocate to investigate
    - Financial impact detected → message to CFO
    - Technical risk mentioned → message to CTO
    """
    messages = []

    if not decision.votes:
        return messages

    # If there's strong dissent, flag to DevilsAdvocate
    if decision.dissenting_views and decision.outcome != "CONSENSUS":
        for view in decision.dissenting_views[:2]:
            agent_name = view.split(":")[0].strip() if ":" in view else "Unknown"
            messages.append(message_bus.send(
                from_agent=agent_name,
                to_agent="DevilsAdvocate",
                subject=f"Dissent on: {decision.votes[0].reasoning[:50]}",
                body=view,
                priority="high",
                source_request_id=decision.request_id,
            ))

    # If confidence is very low, escalate to all
    if decision.confidence < 0.3:
        messages.append(message_bus.send(
            from_agent="System",
            to_agent="all",
            subject=f"Low confidence decision: {decision.position} ({decision.confidence:.0%})",
            body=f"The agency reached {decision.outcome} on '{decision.summary[:100]}' "
                 f"with only {decision.confidence:.0%} confidence. This needs review.",
            priority="urgent",
            source_request_id=decision.request_id,
        ))

    return messages
