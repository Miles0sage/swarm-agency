"""Tests for preset departments."""

from swarm_agency.presets import (
    STRATEGY_AGENTS, PRODUCT_AGENTS, MARKETING_AGENTS, RESEARCH_AGENTS,
    create_strategy_dept, create_product_dept,
    create_marketing_dept, create_research_dept,
    create_full_agency_departments,
)


class TestPresetAgents:
    def test_strategy_has_5_agents(self):
        assert len(STRATEGY_AGENTS) == 5

    def test_product_has_5_agents(self):
        assert len(PRODUCT_AGENTS) == 5

    def test_marketing_has_4_agents(self):
        assert len(MARKETING_AGENTS) == 4

    def test_research_has_4_agents(self):
        assert len(RESEARCH_AGENTS) == 4

    def test_all_agents_have_required_fields(self):
        for agents in [STRATEGY_AGENTS, PRODUCT_AGENTS, MARKETING_AGENTS, RESEARCH_AGENTS]:
            for a in agents:
                assert a.name
                assert a.role
                assert a.expertise
                assert a.bias
                assert a.system_prompt
                assert a.model

    def test_unique_names_within_departments(self):
        for agents in [STRATEGY_AGENTS, PRODUCT_AGENTS, MARKETING_AGENTS, RESEARCH_AGENTS]:
            names = [a.name for a in agents]
            assert len(names) == len(set(names))

    def test_model_diversity(self):
        all_agents = STRATEGY_AGENTS + PRODUCT_AGENTS + MARKETING_AGENTS + RESEARCH_AGENTS
        models = {a.model for a in all_agents}
        assert len(models) >= 4, f"Only {len(models)} unique models"


class TestPresetFactories:
    def test_create_strategy_dept(self):
        dept = create_strategy_dept()
        assert dept.name == "Strategy"
        assert len(dept.agents) == 5

    def test_create_product_dept(self):
        dept = create_product_dept()
        assert dept.name == "Product"

    def test_create_marketing_dept(self):
        dept = create_marketing_dept()
        assert dept.name == "Marketing"

    def test_create_research_dept(self):
        dept = create_research_dept()
        assert dept.name == "Research"

    def test_create_full_agency(self):
        depts = create_full_agency_departments()
        assert len(depts) == 4
        names = {d.name for d in depts}
        assert names == {"Strategy", "Product", "Marketing", "Research"}
