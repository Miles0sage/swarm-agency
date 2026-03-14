"""Tests for dual debate comparison."""

import pytest
from swarm_agency.dual_debate import (
    _compare_decisions, DualDebateResult,
    format_dual_result_text, format_dual_result_dict,
)
from swarm_agency.types import Decision, AgentVote


def _decision(position="YES", confidence=0.8, outcome="MAJORITY"):
    return Decision(
        request_id="dd-1", department="Strategy", outcome=outcome,
        position=position, confidence=confidence,
        votes=[AgentVote(agent_name="A", position=position,
                         confidence=confidence, reasoning="Test", factors=[])],
        summary=f"Decision: {position}",
    )


class TestCompareDecisions:
    def test_agreement_boosts_confidence(self):
        a = _decision("YES", 0.8)
        b = _decision("YES", 0.75)
        result = _compare_decisions(a, b, "dashscope", "openrouter")
        assert result["agree"] is True
        assert result["combined_confidence"] > 0.75  # boosted
        assert result["verdict"] == "YES"

    def test_disagreement_lowers_confidence(self):
        a = _decision("YES", 0.8)
        b = _decision("NO", 0.7)
        result = _compare_decisions(a, b, "dashscope", "openrouter")
        assert result["agree"] is False
        assert result["combined_confidence"] < 0.5
        assert result["verdict"] == "YES"  # higher confidence wins

    def test_disagreement_b_wins_if_higher(self):
        a = _decision("YES", 0.5)
        b = _decision("NO", 0.9)
        result = _compare_decisions(a, b, "dash", "open")
        assert result["verdict"] == "NO"

    def test_strong_agreement_detail(self):
        a = _decision("YES", 0.85)
        b = _decision("YES", 0.9)
        result = _compare_decisions(a, b, "a", "b")
        assert "Strong agreement" in result["detail"]


class TestFormatting:
    def test_format_text(self):
        result = DualDebateResult(
            question="Test?", context=None,
            provider_a="dashscope", decision_a=_decision("YES", 0.8),
            duration_a=10.0,
            provider_b="openrouter", decision_b=_decision("NO", 0.7),
            duration_b=12.0,
            providers_agree=False, agreement_detail="They disagree",
            combined_confidence=0.3, verdict="YES",
            verdict_reasoning="DashScope has higher confidence",
        )
        text = format_dual_result_text(result)
        assert "DISAGREE" in text
        assert "dashscope" in text
        assert "openrouter" in text

    def test_format_dict(self):
        result = DualDebateResult(
            question="Test?", context=None,
            provider_a="a", decision_a=_decision(), duration_a=5.0,
            provider_b="b", decision_b=_decision(), duration_b=6.0,
            providers_agree=True, agreement_detail="agree",
            combined_confidence=0.9, verdict="YES",
            verdict_reasoning="both agree",
        )
        d = format_dual_result_dict(result)
        assert d["comparison"]["providers_agree"] is True
        assert "provider_a" in d
        assert "provider_b" in d
