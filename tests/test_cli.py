"""Tests for CLI interface."""

import json
from unittest.mock import patch, AsyncMock

from swarm_agency.types import AgentVote, Decision
from swarm_agency.cli import main


def _mock_decision():
    return Decision(
        request_id="cli-001",
        department="Strategy",
        outcome="CONSENSUS",
        position="YES",
        confidence=0.85,
        votes=[
            AgentVote(
                agent_name="Visionary", position="YES", confidence=0.9,
                reasoning="Strong market fit", factors=["timing"],
            ),
        ],
        summary="All agents agree.",
        dissenting_views=[],
        duration_seconds=1.5,
    )


class TestCLIParsing:
    def test_basic_question(self, capsys):
        with patch("swarm_agency.cli.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = _mock_decision()
            with patch("sys.argv", ["swarm-agency", "Should we launch?", "--json"]):
                main()
            output = capsys.readouterr().out
            data = json.loads(output)
            assert data["outcome"] == "CONSENSUS"
            assert data["position"] == "YES"

    def test_department_filter(self, capsys):
        with patch("swarm_agency.cli.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = _mock_decision()
            with patch("sys.argv", [
                "swarm-agency", "Hire?", "-d", "Finance", "--json"
            ]):
                main()
            output = capsys.readouterr().out
            data = json.loads(output)
            assert data["outcome"] == "CONSENSUS"

    def test_context_argument(self, capsys):
        with patch("swarm_agency.cli.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = _mock_decision()
            with patch("sys.argv", [
                "swarm-agency", "Expand?", "--context", "Revenue growing", "--json"
            ]):
                main()
            output = capsys.readouterr().out
            assert json.loads(output)["position"] == "YES"

    def test_all_departments_valid(self):
        valid = [
            "Strategy", "Product", "Marketing", "Research",
            "Finance", "Engineering", "Legal", "Operations",
            "Sales", "Creative",
        ]
        for dept in valid:
            with patch("swarm_agency.cli.asyncio") as mock_asyncio:
                mock_asyncio.run.return_value = _mock_decision()
                with patch("sys.argv", [
                    "swarm-agency", "Test?", "-d", dept, "--json"
                ]):
                    main()


class TestCLIDemo:
    def test_demo_list(self, capsys):
        with patch("sys.argv", ["swarm-agency", "--demo"]):
            main()
        output = capsys.readouterr().out
        assert "startup-pivot" in output
        assert "hire-senior" in output
        assert "pricing-change" in output
        assert "open-source" in output
        assert "remote-vs-office" in output

    def test_demo_startup_pivot_json(self, capsys):
        with patch("sys.argv", ["swarm-agency", "--demo", "startup-pivot", "--json"]):
            main()
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["outcome"] == "MAJORITY"
        assert data["position"] == "APPROVE"
        assert data["department"] == "Strategy"
        assert len(data["votes"]) == 5

    def test_demo_hire_senior_json(self, capsys):
        with patch("sys.argv", ["swarm-agency", "--demo", "hire-senior", "--json"]):
            main()
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["outcome"] == "MAJORITY"
        assert data["position"] == "HIRE SENIOR"
        assert data["department"] == "Engineering"

    def test_demo_pricing_split(self, capsys):
        with patch("sys.argv", ["swarm-agency", "--demo", "pricing-change", "--json"]):
            main()
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["outcome"] == "SPLIT"

    def test_demo_unknown_exits(self, capsys):
        import pytest
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["swarm-agency", "--demo", "nonexistent"]):
                main()

    def test_demo_rich_output(self, capsys):
        with patch("sys.argv", ["swarm-agency", "--demo", "open-source"]):
            main()
        output = capsys.readouterr().out
        assert "QUESTION" in output or "AGENCY DECISION" in output

    def test_demo_all_scenarios_have_valid_decisions(self):
        from swarm_agency.demos import DEMO_SCENARIOS, DEMO_LIST
        for name in DEMO_LIST:
            assert name in DEMO_SCENARIOS
            s = DEMO_SCENARIOS[name]
            assert "question" in s
            assert "context" in s
            assert "department" in s
            assert "decision" in s
            assert len(s["decision"].votes) >= 4

    def test_no_question_no_demo_errors(self):
        import pytest
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["swarm-agency"]):
                main()


class TestCLIOutput:
    def test_json_output_structure(self, capsys):
        with patch("swarm_agency.cli.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = _mock_decision()
            with patch("sys.argv", ["swarm-agency", "Test?", "--json"]):
                main()
            output = capsys.readouterr().out
            data = json.loads(output)
            assert "request_id" in data
            assert "votes" in data
            assert "summary" in data
            assert "confidence" in data

    def test_plain_output_fallback(self, capsys):
        with patch("swarm_agency.cli.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = _mock_decision()
            # Force ImportError for rich
            with patch.dict("sys.modules", {"rich": None, "rich.console": None, "rich.table": None, "rich.panel": None}):
                with patch("sys.argv", ["swarm-agency", "Test?"]):
                    main()
                output = capsys.readouterr().out
                assert "CONSENSUS" in output
                assert "YES" in output
