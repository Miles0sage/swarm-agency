"""Proactive alert system — agents push important findings to you.

Supports: console print, file log, webhook, Slack, SMS (via configured handlers).
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from .types import Decision

logger = logging.getLogger("swarm_agency.alerts")

ALERTS_LOG = os.path.expanduser("~/.swarm-agency/alerts.log")


@dataclass
class Alert:
    """A proactive alert from an agent."""
    job_name: str
    department: str
    outcome: str
    position: str
    confidence: float
    summary: str
    key_insight: str
    timestamp: float
    urgency: str  # "info", "warning", "critical"


def decision_to_alert(job_name: str, decision: Decision) -> Alert:
    """Convert a decision into an alert."""
    # Determine urgency based on outcome and confidence
    if decision.outcome == "CONSENSUS" and decision.confidence > 0.8:
        urgency = "critical"  # strong agreement = pay attention
    elif decision.outcome == "SPLIT":
        urgency = "warning"  # disagreement = needs your input
    else:
        urgency = "info"

    # Extract key insight from top vote
    key_insight = ""
    if decision.votes:
        top = max(decision.votes, key=lambda v: v.confidence)
        key_insight = top.reasoning[:200]

    return Alert(
        job_name=job_name,
        department=decision.department,
        outcome=decision.outcome,
        position=decision.position,
        confidence=decision.confidence,
        summary=decision.summary,
        key_insight=key_insight,
        timestamp=time.time(),
        urgency=urgency,
    )


def format_alert_text(alert: Alert) -> str:
    """Format alert as readable text."""
    urgency_icon = {"critical": "!!!", "warning": "!", "info": "~"}
    icon = urgency_icon.get(alert.urgency, "~")
    return (
        f"[{icon}] {alert.job_name} ({alert.department})\n"
        f"    {alert.outcome}: {alert.position} ({alert.confidence:.0%})\n"
        f"    {alert.summary}\n"
        f"    Key: {alert.key_insight}"
    )


def format_alert_slack(alert: Alert) -> dict:
    """Format alert as Slack message payload."""
    urgency_emoji = {"critical": ":rotating_light:", "warning": ":warning:", "info": ":information_source:"}
    emoji = urgency_emoji.get(alert.urgency, ":memo:")

    return {
        "text": f"{emoji} *{alert.job_name}*",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{alert.job_name}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Department:* {alert.department}"},
                    {"type": "mrkdwn", "text": f"*Outcome:* {alert.outcome}"},
                    {"type": "mrkdwn", "text": f"*Position:* {alert.position}"},
                    {"type": "mrkdwn", "text": f"*Confidence:* {alert.confidence:.0%}"},
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Summary:* {alert.summary}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Key Insight:* {alert.key_insight}"}
            },
        ]
    }


# ── Alert Handlers ───────────────────────────────────────────────

def log_alert(alert: Alert) -> None:
    """Write alert to log file."""
    path = Path(ALERTS_LOG)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": alert.timestamp,
        "job": alert.job_name,
        "department": alert.department,
        "outcome": alert.outcome,
        "position": alert.position,
        "confidence": alert.confidence,
        "urgency": alert.urgency,
        "summary": alert.summary,
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def print_alert(alert: Alert) -> None:
    """Print alert to console."""
    print(format_alert_text(alert))


async def send_slack_alert(alert: Alert, webhook_url: str) -> bool:
    """Send alert to Slack via webhook."""
    try:
        payload = format_alert_slack(alert)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json=payload)
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Slack alert failed: {e}")
        return False


async def send_webhook_alert(alert: Alert, url: str) -> bool:
    """Send alert to any webhook URL."""
    try:
        payload = {
            "event": "agent_alert",
            "job": alert.job_name,
            "department": alert.department,
            "outcome": alert.outcome,
            "position": alert.position,
            "confidence": alert.confidence,
            "summary": alert.summary,
            "key_insight": alert.key_insight,
            "urgency": alert.urgency,
            "timestamp": alert.timestamp,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            return resp.status_code < 400
    except Exception as e:
        logger.warning(f"Webhook alert failed: {e}")
        return False


def create_alert_handler(job, decision):
    """Default alert handler — logs + prints."""
    alert = decision_to_alert(job.name, decision)
    log_alert(alert)
    print_alert(alert)


def get_alert_history(limit: int = 20) -> list[dict]:
    """Read recent alerts from log."""
    path = Path(ALERTS_LOG)
    if not path.exists():
        return []
    lines = path.read_text().strip().split("\n")
    alerts = []
    for line in lines[-limit:]:
        try:
            alerts.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return alerts
