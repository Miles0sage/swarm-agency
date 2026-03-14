"""Tests for the verdict output layer."""

import pytest
from swarm_agency.verdict import (
    Verdict, decision_to_verdict, format_verdict_text, format_verdict_rich,
)
from swarm_agency.types import Decision, AgentVote


def _votes(positions):
    return [
        AgentVote(agent_name=f"Agent{i}", position=pos, confidence=0.8,
                  reasoning=f"Reason for {pos}. Second sentence.", factors=["f1"])
        for i, pos in enumerate(positions)
    ]


class TestDecisionToVerdict:
    def test_consensus_yes(self):
        d = Decision(
            request_id="v1", department="Strategy", outcome="CONSENSUS",
            position="YES", confidence=0.9,
            votes=_votes(["YES", "YES", "YES"]),
            summary="All agree.", duration_seconds=5.0,
        )
        v = decision_to_verdict(d)
        assert v.answer == "YES"
        assert v.confidence_label == "High"
        assert "Clear YES" in v.one_liner
        assert v.agents_for == 3
        assert v.agents_against == 0

    def test_majority_no(self):
        d = Decision(
            request_id="v2", department="Finance", outcome="MAJORITY",
            position="NO", confidence=0.65,
            votes=_votes(["NO", "NO", "NO", "YES"]),
            summary="Most say no.",
            dissenting_views=["Agent3: We should go for it because growth."],
            duration_seconds=10.0,
        )
        v = decision_to_verdict(d)
        assert v.answer == "NO"
        assert v.confidence_label == "Medium"
        assert "Leaning NO" in v.one_liner
        assert "growth" in v.top_risk

    def test_split(self):
        d = Decision(
            request_id="v3", department="Strategy", outcome="SPLIT",
            position="MAYBE", confidence=0.3,
            votes=_votes(["YES", "NO", "MAYBE"]),
            summary="Split.", duration_seconds=8.0,
        )
        v = decision_to_verdict(d)
        assert v.answer == "MAYBE"
        assert "close call" in v.one_liner.lower()

    def test_approve_maps_to_yes(self):
        d = Decision(
            request_id="v4", department="S", outcome="MAJORITY",
            position="APPROVE", confidence=0.7,
            votes=_votes(["APPROVE", "APPROVE"]),
            summary="Approved.", duration_seconds=3.0,
        )
        v = decision_to_verdict(d)
        assert v.answer == "YES"

    def test_top_reasons_extracted(self):
        d = Decision(
            request_id="v5", department="S", outcome="MAJORITY",
            position="YES", confidence=0.8,
            votes=_votes(["YES", "YES", "YES", "NO"]),
            summary="Yes.", duration_seconds=5.0,
        )
        v = decision_to_verdict(d)
        assert len(v.top_reasons) >= 1
        assert all(r.endswith(".") for r in v.top_reasons)

    def test_to_dict(self):
        d = Decision(
            request_id="v6", department="S", outcome="CONSENSUS",
            position="NO", confidence=0.85,
            votes=_votes(["NO", "NO"]),
            summary="No.", duration_seconds=4.0,
        )
        v = decision_to_verdict(d)
        result = v.to_dict()
        assert result["answer"] == "NO"
        assert result["confidence"] == 0.85
        assert "vote_split" in result
        assert result["vote_split"]["against"] == 2


class TestFormatting:
    def test_format_text(self):
        v = Verdict(
            answer="YES", confidence=0.8, confidence_label="High",
            one_liner="Go for it.", top_reasons=["Market timing.", "Team ready."],
            top_risk="Competitor may launch first.",
            agents_for=4, agents_against=1, agents_undecided=0,
            debate_quality="MAJORITY", duration=5.0,
        )
        text = format_verdict_text(v)
        assert "YES" in text
        assert "High" in text
        assert "Market timing" in text
        assert "Competitor" in text
        assert "4 for" in text

    def test_format_rich_no_crash(self):
        v = Verdict(
            answer="NO", confidence=0.6, confidence_label="Medium",
            one_liner="Probably not.", top_reasons=["Too risky."],
            top_risk="Could lose market share.",
            agents_for=1, agents_against=3, agents_undecided=1,
            debate_quality="MAJORITY", duration=8.0,
        )
        # Should not crash
        format_verdict_rich(v)
