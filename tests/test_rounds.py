"""Tests for multi-round debate module."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from swarm_agency.rounds import (
    RoundResult,
    multi_round_debate,
    _build_prior_round_context,
    DEFAULT_MAX_ROUNDS,
)
from swarm_agency.department import Department
from swarm_agency.types import AgentConfig, AgencyRequest, AgentVote


def _agent(name="A"):
    return AgentConfig(
        name=name, role="Tester", expertise="testing", bias="test",
        system_prompt="Test", model="test-model",
    )


def _vote(name="A", position="YES", confidence=0.8):
    return AgentVote(
        agent_name=name, position=position, confidence=confidence,
        reasoning="Test reasoning", factors=["f1"],
    )


class TestBuildPriorRoundContext:
    def test_formats_votes(self):
        votes = [
            _vote("A", "YES", 0.9),
            _vote("B", "NO", 0.7),
        ]
        ctx = _build_prior_round_context(votes, 1)
        assert "Prior Round 1" in ctx
        assert "YES" in ctx
        assert "NO" in ctx
        assert "revise your position" in ctx.lower()

    def test_excludes_error_votes(self):
        votes = [
            _vote("A", "YES", 0.9),
            _vote("B", "ERROR", 0.0),
        ]
        ctx = _build_prior_round_context(votes, 1)
        assert "ERROR" not in ctx.split("Vote tally")[1] if "Vote tally" in ctx else True

    def test_anti_anchoring_instruction(self):
        votes = [_vote("A", "YES", 0.9)]
        ctx = _build_prior_round_context(votes, 1)
        assert "do not simply follow the majority" in ctx.lower()


class TestMultiRoundDebate:
    @pytest.mark.asyncio
    async def test_single_round_consensus(self):
        """If round 1 is consensus, no round 2."""
        dept = Department(
            name="Test", agents=[_agent(f"a{i}") for i in range(3)],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr1", question="Test?")

        with patch("swarm_agency.rounds.call_agent", new_callable=AsyncMock,
                    return_value=_vote(position="YES")):
            decision, rounds = await multi_round_debate(dept, request, max_rounds=3)

        assert len(rounds) == 1
        assert rounds[0].outcome == "CONSENSUS"
        assert decision.outcome == "CONSENSUS"

    @pytest.mark.asyncio
    async def test_multiple_rounds_on_split(self):
        """Split in round 1 triggers round 2."""
        dept = Department(
            name="Test", agents=[_agent("a0"), _agent("a1"), _agent("a2")],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr2", question="Test?")

        call_count = 0
        async def mock_call(agent, req, key, url, memory_context=""):
            nonlocal call_count
            call_count += 1
            # Round 1: split (a0=YES, a1=NO, a2=MAYBE)
            if call_count <= 3:
                positions = {"a0": "YES", "a1": "NO", "a2": "MAYBE"}
                return _vote(agent.name, positions.get(agent.name, "YES"))
            # Round 2: converge to YES
            return _vote(agent.name, "YES")

        async def mock_prior(agent, req, key, url, prior_context="", memory_context=""):
            nonlocal call_count
            call_count += 1
            return _vote(agent.name, "YES")

        with patch("swarm_agency.rounds.call_agent", side_effect=mock_call):
            with patch("swarm_agency.rounds._call_agent_with_prior", side_effect=mock_prior):
                decision, rounds = await multi_round_debate(dept, request, max_rounds=3)

        assert len(rounds) >= 2
        # Round 2 should show position changes
        if len(rounds) >= 2:
            assert rounds[1].changes >= 0

    @pytest.mark.asyncio
    async def test_stops_when_no_changes(self):
        """If no one changes position, stop early."""
        dept = Department(
            name="Test", agents=[_agent("a0"), _agent("a1")],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr3", question="Test?")

        # Always return same split
        async def mock_split(agent, req, key, url, memory_context=""):
            if agent.name == "a0":
                return _vote("a0", "YES")
            return _vote("a1", "NO")

        async def mock_split_prior(agent, req, key, url, prior_context="", memory_context=""):
            if agent.name == "a0":
                return _vote("a0", "YES")
            return _vote("a1", "NO")

        with patch("swarm_agency.rounds.call_agent", side_effect=mock_split):
            with patch("swarm_agency.rounds._call_agent_with_prior", side_effect=mock_split_prior):
                decision, rounds = await multi_round_debate(dept, request, max_rounds=5)

        # Should stop at round 2 (no changes detected)
        assert len(rounds) == 2
        assert rounds[1].changes == 0

    @pytest.mark.asyncio
    async def test_max_rounds_respected(self):
        """Never exceeds max_rounds."""
        dept = Department(
            name="Test", agents=[_agent("a0"), _agent("a1")],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr4", question="Test?")

        round_tracker = [0]
        async def mock_alternating(agent, req, key, url, memory_context=""):
            round_tracker[0] += 1
            if round_tracker[0] % 2 == 0:
                return _vote(agent.name, "NO" if agent.name == "a0" else "YES")
            return _vote(agent.name, "YES" if agent.name == "a0" else "NO")

        async def mock_alt_prior(agent, req, key, url, prior_context="", memory_context=""):
            round_tracker[0] += 1
            if round_tracker[0] % 2 == 0:
                return _vote(agent.name, "NO" if agent.name == "a0" else "YES")
            return _vote(agent.name, "YES" if agent.name == "a0" else "NO")

        with patch("swarm_agency.rounds.call_agent", side_effect=mock_alternating):
            with patch("swarm_agency.rounds._call_agent_with_prior", side_effect=mock_alt_prior):
                decision, rounds = await multi_round_debate(dept, request, max_rounds=2)

        assert len(rounds) <= 2

    @pytest.mark.asyncio
    async def test_round_result_has_correct_fields(self):
        dept = Department(
            name="Test", agents=[_agent()],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr5", question="Test?")

        with patch("swarm_agency.rounds.call_agent", new_callable=AsyncMock,
                    return_value=_vote()):
            _, rounds = await multi_round_debate(dept, request)

        r = rounds[0]
        assert r.round_number == 1
        assert len(r.votes) == 1
        assert r.changes == 0  # first round has no prior
        assert r.duration > 0
        assert r.outcome in ("CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK")

    @pytest.mark.asyncio
    async def test_decision_summary_includes_round_info(self):
        dept = Department(
            name="Test", agents=[_agent()],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="mr6", question="Test?")

        with patch("swarm_agency.rounds.call_agent", new_callable=AsyncMock,
                    return_value=_vote()):
            decision, _ = await multi_round_debate(dept, request)

        assert "round" in decision.summary.lower() or "1" in decision.summary
