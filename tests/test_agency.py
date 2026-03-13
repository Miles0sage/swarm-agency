"""Tests for Agency orchestration."""

from unittest.mock import AsyncMock, patch

import pytest

from swarm_agency.types import AgentConfig, AgencyRequest, AgentVote, Decision
from swarm_agency.department import Department
from swarm_agency.agency import Agency


def _agent(name="A"):
    return AgentConfig(
        name=name, role="R", expertise="E", bias="B",
        system_prompt="S", model="test",
    )


def _request(**kw):
    defaults = dict(request_id="r1", question="Launch?")
    defaults.update(kw)
    return AgencyRequest(**defaults)


def _decision(dept="Strategy", position="YES", confidence=0.8, outcome="CONSENSUS"):
    return Decision(
        request_id="r1", department=dept, outcome=outcome,
        position=position, confidence=confidence,
        summary=f"{dept} says {position}",
    )


class TestAgencyInit:
    def test_create(self):
        agency = Agency(name="TestCo", api_key="k", base_url="http://test")
        assert agency.name == "TestCo"
        assert agency.api_key == "k"

    def test_env_fallback(self):
        import os
        from unittest.mock import patch as mock_patch
        with mock_patch.dict(os.environ, {"ALIBABA_CODING_API_KEY": "env-k"}):
            agency = Agency()
            assert agency.api_key == "env-k"

    def test_add_remove_department(self):
        agency = Agency(api_key="k", base_url="http://test")
        dept = Department(name="Strategy", agents=[_agent()])
        agency.add_department(dept)
        assert "Strategy" in agency.list_departments()
        agency.remove_department("Strategy")
        assert "Strategy" not in agency.list_departments()

    def test_add_department_inherits_credentials(self):
        agency = Agency(api_key="secret", base_url="http://api")
        dept = Department(name="D", agents=[])
        agency.add_department(dept)
        assert dept.api_key == "secret"
        assert dept.base_url == "http://api"


class TestSynthesize:
    def test_consensus_all_agree(self):
        agency = Agency(api_key="k", base_url="http://test")
        request = _request()
        decisions = [
            _decision("Strategy", "YES", 0.9),
            _decision("Product", "YES", 0.8),
        ]
        result = agency._synthesize(decisions, request)
        assert result.outcome == "CONSENSUS"
        assert result.position == "YES"

    def test_majority(self):
        agency = Agency(api_key="k", base_url="http://test")
        request = _request()
        decisions = [
            _decision("Strategy", "YES", 0.9),
            _decision("Product", "YES", 0.8),
            _decision("Marketing", "NO", 0.6),
        ]
        result = agency._synthesize(decisions, request)
        assert result.outcome == "MAJORITY"
        assert result.position == "YES"

    def test_split(self):
        agency = Agency(api_key="k", base_url="http://test")
        request = _request()
        decisions = [
            _decision("Strategy", "YES", 0.9),
            _decision("Product", "NO", 0.9),
        ]
        result = agency._synthesize(decisions, request)
        # With equal weights, one will win by position name sort
        assert result.outcome in ("MAJORITY", "SPLIT")


class TestConsultAndDecide:
    @pytest.mark.asyncio
    async def test_decide_single_department(self):
        agency = Agency(api_key="k", base_url="http://test")
        agents = [_agent(f"a{i}") for i in range(3)]
        dept = Department(name="Strategy", agents=agents)
        agency.add_department(dept)

        mock_vote = AgentVote(
            agent_name="mock", position="GO", confidence=0.85,
            reasoning="Test", factors=["f1"],
        )

        with patch("swarm_agency.department.call_agent", new_callable=AsyncMock, return_value=mock_vote):
            decision = await agency.decide(_request(department="Strategy"))
            assert decision.department == "Strategy"
            assert decision.outcome in ("CONSENSUS", "MAJORITY", "SPLIT", "DEADLOCK")

    @pytest.mark.asyncio
    async def test_decide_no_departments(self):
        agency = Agency(api_key="k", base_url="http://test")
        decision = await agency.decide(_request())
        assert decision.outcome == "DEADLOCK"
        assert decision.position == "NONE"

    @pytest.mark.asyncio
    async def test_consult_specific_departments(self):
        agency = Agency(api_key="k", base_url="http://test")
        for name in ["Strategy", "Product", "Marketing"]:
            dept = Department(name=name, agents=[_agent()])
            agency.add_department(dept)

        mock_vote = AgentVote(
            agent_name="m", position="YES", confidence=0.8,
            reasoning="T", factors=[],
        )

        with patch("swarm_agency.department.call_agent", new_callable=AsyncMock, return_value=mock_vote):
            decisions = await agency.consult(_request(), departments=["Strategy", "Product"])
            assert len(decisions) == 2
            dept_names = {d.department for d in decisions}
            assert dept_names == {"Strategy", "Product"}
