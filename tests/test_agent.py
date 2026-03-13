"""Tests for agent prompt formatting."""

from swarm_agency.types import AgentConfig, AgencyRequest
from swarm_agency.agent import format_agent_prompt


def _agent():
    return AgentConfig(
        name="TestAgent", role="CFO", expertise="finance",
        bias="ROI focused", system_prompt="You are a CFO.",
    )


def _request(**kw):
    defaults = dict(request_id="r1", question="Should we hire?")
    defaults.update(kw)
    return AgencyRequest(**defaults)


class TestFormatAgentPrompt:
    def test_includes_question(self):
        prompt = format_agent_prompt(_agent(), _request())
        assert "Should we hire?" in prompt

    def test_includes_role(self):
        prompt = format_agent_prompt(_agent(), _request())
        assert "CFO" in prompt

    def test_includes_expertise(self):
        prompt = format_agent_prompt(_agent(), _request())
        assert "finance" in prompt

    def test_includes_context_when_provided(self):
        prompt = format_agent_prompt(_agent(), _request(context="Budget is tight"))
        assert "Budget is tight" in prompt

    def test_no_context_when_none(self):
        prompt = format_agent_prompt(_agent(), _request(context=None))
        assert "Context:" not in prompt

    def test_includes_metadata(self):
        prompt = format_agent_prompt(_agent(), _request(metadata={"deadline": "Friday"}))
        assert "Friday" in prompt

    def test_json_format_instructions(self):
        prompt = format_agent_prompt(_agent(), _request())
        assert '"position"' in prompt
        assert '"confidence"' in prompt
        assert '"reasoning"' in prompt
