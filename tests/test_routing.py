"""Tests for auto-department routing."""

from unittest.mock import AsyncMock, patch, MagicMock

import numpy as np
import pytest

from swarm_agency.agency import Agency
from swarm_agency.department import Department
from swarm_agency.types import AgentConfig, AgencyRequest, AgentVote
from swarm_agency.presets import (
    DEPARTMENT_DESCRIPTIONS,
    create_full_agency_departments,
)


def _agent(name="A"):
    return AgentConfig(
        name=name, role="Tester", expertise="testing", bias="test",
        system_prompt="Test", model="test-model",
    )


def _make_agency(gemini_key="fake-gemini-key", memory=False):
    agency = Agency(
        name="Test",
        api_key="fake-key",
        base_url="http://test",
        memory_enabled=memory,
        gemini_api_key=gemini_key,
    )
    return agency


class TestDepartmentDescriptions:
    def test_all_departments_have_descriptions(self):
        depts = create_full_agency_departments()
        for dept in depts:
            assert dept.description, f"{dept.name} missing description"

    def test_descriptions_match_preset_map(self):
        assert len(DEPARTMENT_DESCRIPTIONS) == 10
        for name in ["Strategy", "Product", "Marketing", "Research", "Finance",
                      "Engineering", "Legal", "Operations", "Sales", "Creative"]:
            assert name in DEPARTMENT_DESCRIPTIONS
            assert len(DEPARTMENT_DESCRIPTIONS[name]) > 10


class TestRouteToDepartments:
    @pytest.mark.asyncio
    async def test_routes_to_relevant_departments(self):
        agency = _make_agency()
        for dept in create_full_agency_departments():
            agency.add_department(dept)

        # Mock embeddings: make Legal dept description very similar to query
        legal_vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        query_vec = [1.0, 0.0, 0.0]  # matches Legal perfectly

        call_count = 0
        async def mock_get_embedding(text, api_key, timeout=10.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return query_vec  # query
            if "compliance" in text or "contracts" in text:
                return legal_vec.tolist()
            if "planning" in text and "market positioning" in text:
                return [0.8, 0.6, 0.0]
            return [0.1, 0.1, 0.1]  # low similarity for others

        with patch("swarm_agency.embeddings.get_embedding", side_effect=mock_get_embedding):
            routed = await agency.route_to_departments("Should we file a patent?")

        assert len(routed) <= 3
        assert "Legal" in routed

    @pytest.mark.asyncio
    async def test_fallback_on_no_gemini_key(self):
        agency = _make_agency(gemini_key="")
        dept = Department(name="Strategy", agents=[_agent()], description="strategy")
        agency.add_department(dept)

        routed = await agency.route_to_departments("test question")
        assert routed == ["Strategy"]

    @pytest.mark.asyncio
    async def test_fallback_on_api_failure(self):
        agency = _make_agency()
        dept = Department(name="Strategy", agents=[_agent()], description="strategy")
        agency.add_department(dept)

        async def mock_fail(text, api_key, timeout=10.0):
            return None

        with patch("swarm_agency.embeddings.get_embedding", side_effect=mock_fail):
            routed = await agency.route_to_departments("test question")

        assert "Strategy" in routed


class TestDebateWithEmbedding:
    @pytest.mark.asyncio
    async def test_debate_passes_query_embedding(self):
        dept = Department(
            name="Test",
            agents=[_agent()],
            api_key="k",
            base_url="http://test",
            description="testing department",
        )

        mock_vote = AgentVote(
            agent_name="A", position="YES", confidence=0.8,
            reasoning="Good", factors=["f1"],
        )

        with patch("swarm_agency.department.call_agent", new_callable=AsyncMock, return_value=mock_vote):
            request = AgencyRequest(request_id="t1", question="Test?")
            query_emb = [0.1] * 10
            decision = await dept.debate(request, query_embedding=query_emb)

            assert decision.request_id == "t1"
            assert decision.outcome in ("CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK")


class TestWeightedVotingInDepartment:
    def test_weighted_tally_high_accuracy_wins(self):
        dept = Department(name="Test", agents=[], threshold=0.6)

        votes = [
            AgentVote(agent_name="Expert", position="YES", confidence=0.9,
                      reasoning="Yes", factors=[]),
            AgentVote(agent_name="Novice", position="NO", confidence=0.9,
                      reasoning="No", factors=[]),
            AgentVote(agent_name="Neutral", position="NO", confidence=0.5,
                      reasoning="Maybe not", factors=[]),
        ]

        # Expert has 90% accuracy → weight 0.95
        # Novice has 50% accuracy → weight 0.75
        # Neutral has no history → weight 1.0
        agent_weights = {
            "Expert": 0.95,  # 0.5 + 0.9 * 0.5
            "Novice": 0.75,  # 0.5 + 0.5 * 0.5
        }

        outcome, pos, conf, summary, dissents = dept._tally(
            votes, agent_weights=agent_weights
        )
        # YES: 0.95, NO: 0.75 + 1.0 = 1.75
        # NO wins by weight
        assert pos == "NO"

    def test_unweighted_fallback(self):
        dept = Department(name="Test", agents=[], threshold=0.6)

        votes = [
            AgentVote(agent_name="A", position="YES", confidence=0.8,
                      reasoning="Yes", factors=[]),
            AgentVote(agent_name="B", position="YES", confidence=0.7,
                      reasoning="Yes", factors=[]),
            AgentVote(agent_name="C", position="NO", confidence=0.6,
                      reasoning="No", factors=[]),
        ]

        # No weights → same as before (count-based)
        outcome, pos, conf, summary, dissents = dept._tally(votes)
        assert pos == "YES"
        assert outcome == "MAJORITY"

    def test_weight_bounds(self):
        # Weights should be 0.5-1.0 per formula
        for accuracy in [0.0, 0.25, 0.5, 0.75, 1.0]:
            weight = 0.5 + (accuracy * 0.5)
            assert 0.5 <= weight <= 1.0
