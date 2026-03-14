"""Tests for agent prompt formatting and JSON extraction."""

from swarm_agency.types import AgentConfig, AgencyRequest
from swarm_agency.agent import format_agent_prompt, _extract_json


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


class TestExtractJson:
    def test_clean_json(self):
        result = _extract_json('{"position": "YES", "confidence": 0.8, "reasoning": "Good", "factors": []}')
        assert result["position"] == "YES"
        assert result["confidence"] == 0.8

    def test_markdown_fenced(self):
        result = _extract_json('```json\n{"position": "NO", "confidence": 0.6, "reasoning": "Bad", "factors": []}\n```')
        assert result["position"] == "NO"

    def test_text_before_json(self):
        result = _extract_json('Let me analyze this carefully.\n\n{"position": "MAYBE", "confidence": 0.5, "reasoning": "Uncertain", "factors": ["risk"]}')
        assert result["position"] == "MAYBE"
        assert result["factors"] == ["risk"]

    def test_text_after_json(self):
        result = _extract_json('{"position": "YES", "confidence": 0.9, "reasoning": "Strong", "factors": []}\n\nI hope this helps!')
        assert result["position"] == "YES"

    def test_nested_braces_in_reasoning(self):
        result = _extract_json('{"position": "NO", "confidence": 0.7, "reasoning": "The ratio {2:1} is bad", "factors": []}')
        assert result["position"] == "NO"

    def test_truncated_json_regex_fallback(self):
        # Simulates truncation mid-output
        result = _extract_json('{"position": "YES", "confidence": 0.85, "reasoning": "This is a long reason that gets cut off because the model hit max_tok')
        assert result["position"] == "YES"
        assert result["confidence"] == 0.85

    def test_completely_mangled(self):
        result = _extract_json("I think we should say YES with 80% confidence because the market is ready")
        # Should still return a dict with defaults
        assert "position" in result
        assert "confidence" in result

    def test_thinking_tokens_before_json(self):
        result = _extract_json('<think>Let me consider this...</think>\n{"position": "NO", "confidence": 0.65, "reasoning": "Too risky", "factors": ["market"]}')
        assert result["position"] == "NO"
        assert result["confidence"] == 0.65

    def test_multiple_json_objects(self):
        # Picks first valid JSON object — if it has position, great; if not, still a dict
        result = _extract_json('{"invalid": true} {"position": "YES", "confidence": 0.7, "reasoning": "OK", "factors": []}')
        assert isinstance(result, dict)

    def test_escaped_quotes_in_reasoning(self):
        result = _extract_json('{"position": "YES", "confidence": 0.8, "reasoning": "The CEO said \\"go for it\\"", "factors": []}')
        assert result["position"] == "YES"
