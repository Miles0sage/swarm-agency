"""Tests for streaming debate module."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from swarm_agency.streaming import (
    VoteEvent,
    stream_debate,
    stream_department_debate,
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


class TestStreamDebate:
    @pytest.mark.asyncio
    async def test_yields_events_as_completed(self):
        agents = [_agent(f"a{i}") for i in range(3)]
        request = AgencyRequest(request_id="s1", question="Test?")

        async def mock_call(agent, req, key, url, memory_context=""):
            await asyncio.sleep(0.01 * hash(agent.name) % 3)
            return _vote(name=agent.name)

        with patch("swarm_agency.streaming.call_agent", side_effect=mock_call):
            events = []
            async for event in stream_debate(agents, request, "k", "http://test"):
                events.append(event)

        assert len(events) == 3
        # Events arrive incrementally
        for i, event in enumerate(events, 1):
            assert event.votes_so_far == i
            assert event.total_agents == 3
            assert isinstance(event.vote, AgentVote)
            assert event.elapsed > 0

    @pytest.mark.asyncio
    async def test_empty_agents(self):
        request = AgencyRequest(request_id="s2", question="Test?")
        events = []
        async for event in stream_debate([], request, "k", "http://test"):
            events.append(event)
        assert events == []

    @pytest.mark.asyncio
    async def test_event_has_department_name(self):
        agents = [_agent("solo")]
        request = AgencyRequest(request_id="s3", question="Test?")

        with patch("swarm_agency.streaming.call_agent", new_callable=AsyncMock, return_value=_vote("solo")):
            events = []
            async for event in stream_debate(
                agents, request, "k", "http://test", department_name="Finance"
            ):
                events.append(event)

        assert events[0].department == "Finance"


class TestStreamDepartmentDebate:
    @pytest.mark.asyncio
    async def test_returns_decision_with_callbacks(self):
        dept = Department(
            name="Test", agents=[_agent(f"a{i}") for i in range(3)],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="sd1", question="Test?")

        with patch("swarm_agency.streaming.call_agent", new_callable=AsyncMock, return_value=_vote()):
            callback_events = []
            decision = await stream_department_debate(
                dept, request,
                on_vote=lambda e: callback_events.append(e),
            )

        assert decision.request_id == "sd1"
        assert decision.department == "Test"
        assert len(decision.votes) == 3
        assert len(callback_events) == 3

    @pytest.mark.asyncio
    async def test_works_without_callback(self):
        dept = Department(
            name="Test", agents=[_agent()],
            api_key="k", base_url="http://test",
        )
        request = AgencyRequest(request_id="sd2", question="Test?")

        with patch("swarm_agency.streaming.call_agent", new_callable=AsyncMock, return_value=_vote()):
            decision = await stream_department_debate(dept, request)

        assert decision.outcome in ("CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK")
