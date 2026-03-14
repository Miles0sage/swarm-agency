"""Tests for sports-specific agent personas."""

import pytest

from swarm_agency.sports import (
    ANALYTICS_AGENTS,
    INTELLIGENCE_AGENTS,
    CONTRARIAN_AGENTS,
    ALL_SPORTS_AGENTS,
    SPORTS_DEPARTMENT_DESCRIPTIONS,
    create_analytics_dept,
    create_intelligence_dept,
    create_contrarian_dept,
    create_sports_departments,
    create_sports_agency,
)


class TestSportsAgents:
    def test_total_agents_count(self):
        total = sum(len(agents) for agents in ALL_SPORTS_AGENTS.values())
        assert total == 10

    def test_three_departments(self):
        assert len(ALL_SPORTS_AGENTS) == 3
        assert "Analytics" in ALL_SPORTS_AGENTS
        assert "Intelligence" in ALL_SPORTS_AGENTS
        assert "Contrarian" in ALL_SPORTS_AGENTS

    def test_analytics_has_3_agents(self):
        assert len(ANALYTICS_AGENTS) == 3
        names = [a.name for a in ANALYTICS_AGENTS]
        assert "StatsGuru" in names
        assert "LineShark" in names
        assert "EVCalculator" in names

    def test_intelligence_has_4_agents(self):
        assert len(INTELLIGENCE_AGENTS) == 4
        names = [a.name for a in INTELLIGENCE_AGENTS]
        assert "InjuryAnalyst" in names
        assert "WeatherWatcher" in names

    def test_contrarian_has_3_agents(self):
        assert len(CONTRARIAN_AGENTS) == 3
        names = [a.name for a in CONTRARIAN_AGENTS]
        assert "PublicFader" in names
        assert "DevilsAdvocate" in names

    def test_all_agents_have_system_prompts(self):
        for dept_name, agents in ALL_SPORTS_AGENTS.items():
            for agent in agents:
                assert agent.system_prompt, f"{agent.name} missing system_prompt"
                assert agent.model, f"{agent.name} missing model"
                assert agent.expertise, f"{agent.name} missing expertise"

    def test_all_agents_have_unique_names(self):
        names = []
        for agents in ALL_SPORTS_AGENTS.values():
            names.extend(a.name for a in agents)
        assert len(names) == len(set(names)), "Duplicate agent names"

    def test_department_descriptions(self):
        assert len(SPORTS_DEPARTMENT_DESCRIPTIONS) == 3
        for name, desc in SPORTS_DEPARTMENT_DESCRIPTIONS.items():
            assert len(desc) > 10, f"{name} description too short"


class TestSportsDepartmentCreation:
    def test_create_analytics(self):
        dept = create_analytics_dept()
        assert dept.name == "Analytics"
        assert len(dept.agents) == 3
        assert dept.description

    def test_create_intelligence(self):
        dept = create_intelligence_dept()
        assert dept.name == "Intelligence"
        assert len(dept.agents) == 4

    def test_create_contrarian(self):
        dept = create_contrarian_dept()
        assert dept.name == "Contrarian"
        assert len(dept.agents) == 3

    def test_create_all_sports_departments(self):
        depts = create_sports_departments()
        assert len(depts) == 3
        total_agents = sum(len(d.agents) for d in depts)
        assert total_agents == 10


class TestSportsAgency:
    def test_create_sports_agency(self):
        agency = create_sports_agency(api_key="test", provider="dashscope", memory=False)
        assert agency.name == "SportsAgency"
        assert len(agency.departments) == 3
        total = sum(len(d.agents) for d in agency.departments.values())
        assert total == 10
