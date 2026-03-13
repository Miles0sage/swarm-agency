"""Tests for Department debate and tallying logic."""

from unittest.mock import AsyncMock, patch

import pytest

from swarm_agency.types import AgentConfig, AgencyRequest, AgentVote
from swarm_agency.department import Department


def _agent(name="A", model="test-model"):
    return AgentConfig(
        name=name, role="Tester", expertise="testing", bias="test",
        system_prompt="Test", model=model,
    )


def _request(**kw):
    defaults = dict(request_id="t1", question="Should we launch?")
    defaults.update(kw)
    return AgencyRequest(**defaults)


def _vote(position="YES", confidence=0.8, name="A"):
    return AgentVote(
        agent_name=name, position=position, confidence=confidence,
        reasoning="Test", factors=["f1"],
    )


class TestTally:
    def setup_method(self):
        self.dept = Department(
            name="Test", agents=[_agent(f"a{i}") for i in range(5)],
        )

    @pytest.mark.parametrize(
        ("raw_position", "expected"),
        [
            ("YES", "YES"),
            ("go for it", "YES"),
            ("APPROVE", "YES"),
            ("REJECT", "NO"),
            ("NO, OPERATIONAL OVERLOAD", "NO"),
            ("PROCEED WITH CAUTION", "MAYBE"),
            ("STRATEGIC REJECTION", "NO"),
            ("needs more data", "MAYBE"),
        ],
    )
    def test_normalize_position(self, raw_position, expected):
        assert self.dept._normalize_position(raw_position) == expected

    def test_consensus_all_agree(self):
        votes = [_vote("YES", 0.9, f"a{i}") for i in range(5)]
        outcome, pos, conf, summary, dissents = self.dept._tally(votes)
        assert outcome == "CONSENSUS"
        assert pos == "YES"
        assert "all 5" in summary.lower()

    def test_majority(self):
        votes = [_vote("YES", 0.8, f"a{i}") for i in range(4)]
        votes.append(_vote("NO", 0.6, "a4"))
        outcome, pos, conf, summary, dissents = self.dept._tally(votes)
        assert outcome == "MAJORITY"
        assert pos == "YES"
        assert "4/5" in summary

    def test_split(self):
        votes = [_vote("YES", 0.7, f"a{i}") for i in range(2)]
        votes += [_vote("NO", 0.7, f"a{i}") for i in range(2, 4)]
        votes.append(_vote("MAYBE", 0.5, "a4"))
        outcome, pos, conf, summary, dissents = self.dept._tally(votes)
        assert outcome == "SPLIT"

    def test_empty_votes(self):
        outcome, pos, conf, summary, dissents = self.dept._tally([])
        assert outcome == "DEADLOCK"
        assert conf == 0.0

    def test_all_errors(self):
        votes = [_vote("ERROR", 0.0, f"a{i}") for i in range(5)]
        outcome, pos, conf, summary, dissents = self.dept._tally(votes)
        assert outcome == "DEADLOCK"

    def test_dissenting_views_collected(self):
        votes = [_vote("YES", 0.8, f"a{i}") for i in range(4)]
        dissent_vote = AgentVote(
            agent_name="a4", position="NO", confidence=0.7,
            reasoning="Bad", factors=["risk"], dissent="Too expensive",
        )
        votes.append(dissent_vote)
        _, _, _, _, dissents = self.dept._tally(votes)
        assert len(dissents) == 1
        assert "Too expensive" in dissents[0]

    def test_custom_threshold(self):
        dept = Department(name="Strict", agents=[], threshold=0.8)
        votes = [_vote("YES", 0.8, f"a{i}") for i in range(3)]
        votes += [_vote("NO", 0.6, f"a{i}") for i in range(3, 5)]
        # 3/5 = 60% < 80% threshold
        outcome, _, _, _, _ = dept._tally(votes)
        assert outcome == "SPLIT"


class TestDebate:
    @pytest.mark.asyncio
    async def test_debate_returns_decision(self):
        agents = [_agent(f"a{i}") for i in range(3)]
        dept = Department(name="Test", agents=agents, api_key="k", base_url="http://test")

        mock_vote = _vote("APPROVE", 0.85, "mock")

        with patch("swarm_agency.department.call_agent", new_callable=AsyncMock, return_value=mock_vote):
            request = _request()
            decision = await dept.debate(request)

            assert decision.request_id == "t1"
            assert decision.department == "Test"
            assert decision.outcome in ("CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK")
            assert len(decision.votes) == 3
            assert decision.duration_seconds >= 0
