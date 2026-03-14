"""Tests for agent-to-agent messaging."""

import pytest
from swarm_agency.messaging import MessageBus, AgentMessage, auto_escalate
from swarm_agency.types import Decision, AgentVote


@pytest.fixture
def bus(tmp_path):
    db = str(tmp_path / "msg.db")
    b = MessageBus(db_path=db)
    yield b
    b.close()


class TestMessageBus:
    def test_send_and_receive(self, bus):
        bus.send("CTO", "CFO", "Budget needed", "We need $50K for infra", "high")
        messages = bus.get_unread("CFO")
        assert len(messages) == 1
        assert messages[0].from_agent == "CTO"
        assert messages[0].subject == "Budget needed"
        assert messages[0].priority == "high"

    def test_mark_read(self, bus):
        msg = bus.send("A", "B", "Hi", "Test")
        bus.mark_read(msg.message_id)
        unread = bus.get_unread("B")
        assert len(unread) == 0

    def test_respond(self, bus):
        msg = bus.send("A", "B", "Question", "What do you think?")
        bus.respond(msg.message_id, "I think YES")
        conv = bus.get_conversation("A", "B")
        assert conv[0].response == "I think YES"

    def test_broadcast(self, bus):
        bus.send("CEO", "all", "Announcement", "Company meeting tomorrow")
        assert len(bus.get_unread("CFO")) == 1
        assert len(bus.get_unread("CTO")) == 1
        assert len(bus.get_unread("anyone")) == 1

    def test_priority_ordering(self, bus):
        bus.send("A", "B", "Low", "body", "low")
        bus.send("A", "B", "Urgent", "body", "urgent")
        bus.send("A", "B", "Normal", "body", "normal")
        messages = bus.get_unread("B")
        assert messages[0].priority == "urgent"

    def test_message_context(self, bus):
        bus.send("CTO", "CFO", "Infra costs rising", "Cloud bill up 30%", "high")
        ctx = bus.build_message_context("CFO")
        assert "CTO" in ctx
        assert "Infra costs" in ctx
        assert "30%" in ctx
        # Should be marked read now
        assert len(bus.get_unread("CFO")) == 0

    def test_recent(self, bus):
        for i in range(5):
            bus.send(f"A{i}", "B", f"Msg {i}", "body")
        recent = bus.get_recent(limit=3)
        assert len(recent) == 3


class TestAutoEscalate:
    def test_dissent_triggers_message(self, bus):
        d = Decision(
            request_id="esc-1", department="Strategy", outcome="MAJORITY",
            position="YES", confidence=0.7,
            votes=[AgentVote(agent_name="A", position="YES", confidence=0.8,
                             reasoning="Good", factors=[])],
            summary="Majority yes",
            dissenting_views=["Pragmatist: This is too risky for our runway"],
        )
        messages = auto_escalate(d, bus)
        assert len(messages) >= 1
        assert any(m.to_agent == "DevilsAdvocate" for m in messages)

    def test_low_confidence_escalates(self, bus):
        d = Decision(
            request_id="esc-2", department="Strategy", outcome="SPLIT",
            position="MAYBE", confidence=0.2,
            votes=[AgentVote(agent_name="A", position="MAYBE", confidence=0.2,
                             reasoning="Unclear", factors=[])],
            summary="No agreement",
        )
        messages = auto_escalate(d, bus)
        assert any(m.to_agent == "all" for m in messages)
        assert any(m.priority == "urgent" for m in messages)
