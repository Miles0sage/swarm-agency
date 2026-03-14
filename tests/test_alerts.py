"""Tests for the alert system."""

import pytest
from swarm_agency.alerts import (
    Alert, decision_to_alert, format_alert_text,
    format_alert_slack, log_alert, get_alert_history,
)
from swarm_agency.types import Decision, AgentVote


def _decision(outcome="CONSENSUS", position="YES", confidence=0.9):
    return Decision(
        request_id="alert-1", department="Finance", outcome=outcome,
        position=position, confidence=confidence,
        votes=[AgentVote(agent_name="CFO", position=position,
                         confidence=confidence, reasoning="Strong metrics",
                         factors=["revenue", "growth"])],
        summary="All agree.",
    )


class TestAlerts:
    def test_decision_to_alert_critical(self):
        d = _decision("CONSENSUS", "YES", 0.9)
        alert = decision_to_alert("Daily Check", d)
        assert alert.urgency == "critical"
        assert alert.job_name == "Daily Check"

    def test_decision_to_alert_warning(self):
        d = _decision("SPLIT", "MAYBE", 0.4)
        alert = decision_to_alert("Review", d)
        assert alert.urgency == "warning"

    def test_decision_to_alert_info(self):
        d = _decision("MAJORITY", "NO", 0.6)
        alert = decision_to_alert("Scan", d)
        assert alert.urgency == "info"

    def test_format_text(self):
        alert = Alert(
            job_name="Test", department="Finance",
            outcome="CONSENSUS", position="YES", confidence=0.9,
            summary="All agree", key_insight="Revenue up",
            timestamp=1000.0, urgency="critical",
        )
        text = format_alert_text(alert)
        assert "!!!" in text
        assert "Test" in text
        assert "Revenue up" in text

    def test_format_slack(self):
        alert = Alert(
            job_name="Test", department="Finance",
            outcome="MAJORITY", position="NO", confidence=0.7,
            summary="Most disagree", key_insight="Risk high",
            timestamp=1000.0, urgency="warning",
        )
        payload = format_alert_slack(alert)
        assert "text" in payload
        assert "blocks" in payload

    def test_log_and_read(self, tmp_path):
        import swarm_agency.alerts as alerts_mod
        old_path = alerts_mod.ALERTS_LOG
        alerts_mod.ALERTS_LOG = str(tmp_path / "alerts.log")

        alert = Alert(
            job_name="Test", department="Eng", outcome="MAJORITY",
            position="YES", confidence=0.8, summary="Ship it",
            key_insight="Ready", timestamp=1000.0, urgency="info",
        )
        log_alert(alert)
        log_alert(alert)

        history = get_alert_history(limit=10)
        assert len(history) == 2
        assert history[0]["job"] == "Test"

        alerts_mod.ALERTS_LOG = old_path
