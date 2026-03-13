"""Tests for preset departments."""

from swarm_agency.presets import (
    STRATEGY_AGENTS, PRODUCT_AGENTS, MARKETING_AGENTS, RESEARCH_AGENTS,
    FINANCE_AGENTS, ENGINEERING_AGENTS, LEGAL_AGENTS, OPERATIONS_AGENTS,
    SALES_AGENTS, CREATIVE_AGENTS, ALL_AGENTS, DEPARTMENT_NAMES,
    create_strategy_dept, create_product_dept,
    create_marketing_dept, create_research_dept,
    create_finance_dept, create_engineering_dept,
    create_legal_dept, create_operations_dept,
    create_sales_dept, create_creative_dept,
    create_full_agency_departments,
)


ALL_AGENT_LISTS = [
    ("Strategy", STRATEGY_AGENTS, 5),
    ("Product", PRODUCT_AGENTS, 5),
    ("Marketing", MARKETING_AGENTS, 4),
    ("Research", RESEARCH_AGENTS, 4),
    ("Finance", FINANCE_AGENTS, 5),
    ("Engineering", ENGINEERING_AGENTS, 5),
    ("Legal", LEGAL_AGENTS, 4),
    ("Operations", OPERATIONS_AGENTS, 4),
    ("Sales", SALES_AGENTS, 4),
    ("Creative", CREATIVE_AGENTS, 3),
]


class TestPresetAgents:
    def test_strategy_has_5_agents(self):
        assert len(STRATEGY_AGENTS) == 5

    def test_product_has_5_agents(self):
        assert len(PRODUCT_AGENTS) == 5

    def test_marketing_has_4_agents(self):
        assert len(MARKETING_AGENTS) == 4

    def test_research_has_4_agents(self):
        assert len(RESEARCH_AGENTS) == 4

    def test_finance_has_5_agents(self):
        assert len(FINANCE_AGENTS) == 5

    def test_engineering_has_5_agents(self):
        assert len(ENGINEERING_AGENTS) == 5

    def test_legal_has_4_agents(self):
        assert len(LEGAL_AGENTS) == 4

    def test_operations_has_4_agents(self):
        assert len(OPERATIONS_AGENTS) == 4

    def test_sales_has_4_agents(self):
        assert len(SALES_AGENTS) == 4

    def test_creative_has_3_agents(self):
        assert len(CREATIVE_AGENTS) == 3

    def test_total_agent_count(self):
        total = sum(len(agents) for agents in ALL_AGENTS.values())
        assert total == 43

    def test_all_agents_have_required_fields(self):
        for dept_name, agents, _ in ALL_AGENT_LISTS:
            for a in agents:
                assert a.name, f"{dept_name}: agent missing name"
                assert a.role, f"{dept_name}/{a.name}: missing role"
                assert a.expertise, f"{dept_name}/{a.name}: missing expertise"
                assert a.bias, f"{dept_name}/{a.name}: missing bias"
                assert a.system_prompt, f"{dept_name}/{a.name}: missing system_prompt"
                assert a.model, f"{dept_name}/{a.name}: missing model"

    def test_unique_names_within_departments(self):
        for dept_name, agents, _ in ALL_AGENT_LISTS:
            names = [a.name for a in agents]
            assert len(names) == len(set(names)), f"Duplicate names in {dept_name}"

    def test_unique_names_globally(self):
        all_names = []
        for agents in ALL_AGENTS.values():
            all_names.extend(a.name for a in agents)
        assert len(all_names) == len(set(all_names)), "Duplicate agent names across departments"

    def test_model_diversity(self):
        all_agents = []
        for agents in ALL_AGENTS.values():
            all_agents.extend(agents)
        models = {a.model for a in all_agents}
        assert len(models) >= 5, f"Only {len(models)} unique models: {models}"

    def test_all_agents_dict_keys_match_department_names(self):
        assert list(ALL_AGENTS.keys()) == DEPARTMENT_NAMES

    def test_department_names_has_10(self):
        assert len(DEPARTMENT_NAMES) == 10

    def test_system_prompts_contain_role(self):
        for agents in ALL_AGENTS.values():
            for a in agents:
                assert a.role.lower() in a.system_prompt.lower(), (
                    f"{a.name}: system_prompt doesn't mention role '{a.role}'"
                )

    def test_system_prompts_contain_expertise(self):
        for agents in ALL_AGENTS.values():
            for a in agents:
                assert a.expertise[:20] in a.system_prompt, (
                    f"{a.name}: system_prompt doesn't mention expertise"
                )


class TestPresetFactories:
    def test_create_strategy_dept(self):
        dept = create_strategy_dept()
        assert dept.name == "Strategy"
        assert len(dept.agents) == 5

    def test_create_product_dept(self):
        dept = create_product_dept()
        assert dept.name == "Product"
        assert len(dept.agents) == 5

    def test_create_marketing_dept(self):
        dept = create_marketing_dept()
        assert dept.name == "Marketing"
        assert len(dept.agents) == 4

    def test_create_research_dept(self):
        dept = create_research_dept()
        assert dept.name == "Research"
        assert len(dept.agents) == 4

    def test_create_finance_dept(self):
        dept = create_finance_dept()
        assert dept.name == "Finance"
        assert len(dept.agents) == 5

    def test_create_engineering_dept(self):
        dept = create_engineering_dept()
        assert dept.name == "Engineering"
        assert len(dept.agents) == 5

    def test_create_legal_dept(self):
        dept = create_legal_dept()
        assert dept.name == "Legal"
        assert len(dept.agents) == 4

    def test_create_operations_dept(self):
        dept = create_operations_dept()
        assert dept.name == "Operations"
        assert len(dept.agents) == 4

    def test_create_sales_dept(self):
        dept = create_sales_dept()
        assert dept.name == "Sales"
        assert len(dept.agents) == 4

    def test_create_creative_dept(self):
        dept = create_creative_dept()
        assert dept.name == "Creative"
        assert len(dept.agents) == 3

    def test_create_full_agency(self):
        depts = create_full_agency_departments()
        assert len(depts) == 10
        names = {d.name for d in depts}
        assert names == {
            "Strategy", "Product", "Marketing", "Research",
            "Finance", "Engineering", "Legal", "Operations",
            "Sales", "Creative",
        }

    def test_full_agency_total_agents(self):
        depts = create_full_agency_departments()
        total = sum(len(d.agents) for d in depts)
        assert total == 43

    def test_factory_passes_kwargs(self):
        dept = create_strategy_dept(threshold=0.8)
        assert dept.threshold == 0.8
