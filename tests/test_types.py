"""Tests for core types."""

from swarm_agency.types import AgentConfig, AgencyRequest, AgentVote, Decision


class TestAgentConfig:
    def test_create(self):
        agent = AgentConfig(
            name="TestAgent",
            role="Tester",
            expertise="testing",
            bias="test everything",
            system_prompt="You are a tester.",
        )
        assert agent.name == "TestAgent"
        assert agent.model == "qwen3-coder-plus"  # default

    def test_custom_model(self):
        agent = AgentConfig(
            name="A", role="R", expertise="E", bias="B",
            system_prompt="S", model="glm-4.7",
        )
        assert agent.model == "glm-4.7"


class TestAgencyRequest:
    def test_create_minimal(self):
        req = AgencyRequest(request_id="r1", question="Should we launch?")
        assert req.request_id == "r1"
        assert req.context is None
        assert req.department is None
        assert req.metadata == {}

    def test_create_full(self):
        req = AgencyRequest(
            request_id="r2",
            question="Hire?",
            context="Budget tight",
            department="Strategy",
            metadata={"urgency": "high"},
        )
        assert req.department == "Strategy"
        assert req.metadata["urgency"] == "high"


class TestAgentVote:
    def test_create(self):
        vote = AgentVote(
            agent_name="A", position="YES", confidence=0.8,
            reasoning="Makes sense", factors=["f1"],
        )
        assert vote.position == "YES"
        assert vote.dissent is None

    def test_with_dissent(self):
        vote = AgentVote(
            agent_name="A", position="NO", confidence=0.6,
            reasoning="Bad idea", factors=[], dissent="Too risky",
        )
        assert vote.dissent == "Too risky"


class TestDecision:
    def test_to_dict(self):
        vote = AgentVote(
            agent_name="A", position="YES", confidence=0.8,
            reasoning="Good", factors=["f1"],
        )
        decision = Decision(
            request_id="r1", department="Strategy",
            outcome="CONSENSUS", position="YES",
            confidence=0.8, votes=[vote],
            summary="All agree",
        )
        d = decision.to_dict()
        assert d["request_id"] == "r1"
        assert d["outcome"] == "CONSENSUS"
        assert len(d["votes"]) == 1
        assert d["votes"][0]["agent_name"] == "A"

    def test_defaults(self):
        decision = Decision(
            request_id="r1", department="D",
            outcome="SPLIT", position="NONE", confidence=0.0,
        )
        assert decision.votes == []
        assert decision.dissenting_views == []
        assert decision.duration_seconds == 0.0
