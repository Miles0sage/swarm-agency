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
