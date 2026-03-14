"""Verdict — clean, human-readable decision output.

Transforms the raw debate (43 agents, votes, dissents) into what
users actually want:
1. A clear YES/NO/MAYBE
2. The confidence level
3. Top 3 reasons
4. The #1 risk (what could go wrong)
5. One-line recommendation

The 43-agent debate happens behind the scenes. The user sees a DECISION.
"""

from dataclasses import dataclass, field
from typing import Optional

from .types import Decision


@dataclass
class Verdict:
    """The clean, user-facing output of a debate."""
    answer: str  # YES, NO, MAYBE
    confidence: float  # 0.0-1.0
    confidence_label: str  # "High", "Medium", "Low"
    one_liner: str  # one sentence recommendation
    top_reasons: list[str]  # top 3 reasons for the answer
    top_risk: str  # the #1 counterargument
    agents_for: int
    agents_against: int
    agents_undecided: int
    debate_quality: str  # CONSENSUS, MAJORITY, SPLIT, DEADLOCK
    duration: float

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "confidence_label": self.confidence_label,
            "one_liner": self.one_liner,
            "top_reasons": self.top_reasons,
            "top_risk": self.top_risk,
            "vote_split": {
                "for": self.agents_for,
                "against": self.agents_against,
                "undecided": self.agents_undecided,
            },
            "debate_quality": self.debate_quality,
            "duration_seconds": self.duration,
        }


def decision_to_verdict(decision: Decision) -> Verdict:
    """Transform a raw Decision into a clean Verdict.

    This is the key function — it distills 43 agents' debate into
    what the user actually needs to make their decision.
    """
    # Count votes
    yes_votes = []
    no_votes = []
    maybe_votes = []
    error_votes = 0

    yes_terms = {"YES", "APPROVE", "APPROVED", "GO", "LAUNCH", "SHIP", "HIRE SENIOR",
                  "ACCEPT", "PROCEED", "GREENLIGHT", "SUPPORT"}
    no_terms = {"NO", "REJECT", "REJECTED", "STOP", "BLOCK", "DENY", "DECLINE",
                "HIRE JUNIORS", "VETO", "OPPOSE"}

    for v in decision.votes:
        pos = v.position.upper().strip()
        if pos in yes_terms:
            yes_votes.append(v)
        elif pos in no_terms:
            no_votes.append(v)
        elif pos == "ERROR":
            error_votes += 1
        else:
            maybe_votes.append(v)

    # Determine clean answer
    answer = decision.position.upper().strip()
    if answer in yes_terms:
        answer = "YES"
    elif answer in no_terms:
        answer = "NO"
    elif answer not in ("YES", "NO", "MAYBE"):
        # Check if it contains yes/no keywords
        tokens = set(answer.replace("-", " ").split())
        if tokens & {"YES", "APPROVE", "GO", "LAUNCH", "HIRE", "ACCEPT"}:
            answer = "YES"
        elif tokens & {"NO", "REJECT", "STOP", "BLOCK", "DENY"}:
            answer = "NO"
        else:
            answer = "MAYBE"

    # Confidence label
    conf = decision.confidence
    if conf >= 0.75:
        conf_label = "High"
    elif conf >= 0.5:
        conf_label = "Medium"
    elif conf >= 0.25:
        conf_label = "Low"
    else:
        conf_label = "Very Low"

    # Extract top reasons (from agreeing votes, sorted by confidence)
    if answer == "YES":
        agreeing = sorted(yes_votes, key=lambda v: v.confidence, reverse=True)
    elif answer == "NO":
        agreeing = sorted(no_votes, key=lambda v: v.confidence, reverse=True)
    else:
        agreeing = sorted(maybe_votes, key=lambda v: v.confidence, reverse=True)

    top_reasons = []
    seen_reasons = set()
    for v in agreeing[:5]:
        # Extract first sentence of reasoning
        reason = v.reasoning.split(".")[0].strip() + "."
        if reason.lower() not in seen_reasons:
            top_reasons.append(reason)
            seen_reasons.add(reason.lower())
        if len(top_reasons) >= 3:
            break

    # Extract top risk (from dissenting votes)
    top_risk = "No significant risks identified."
    if decision.dissenting_views:
        # Clean up dissent — remove agent name prefix
        dissent = decision.dissenting_views[0]
        if ": " in dissent:
            dissent = dissent.split(": ", 1)[1]
        top_risk = dissent
    else:
        # Find highest-confidence dissenter
        if answer == "YES" and no_votes:
            top_dissenter = max(no_votes, key=lambda v: v.confidence)
            top_risk = top_dissenter.reasoning.split(".")[0].strip() + "."
        elif answer == "NO" and yes_votes:
            top_dissenter = max(yes_votes, key=lambda v: v.confidence)
            top_risk = top_dissenter.reasoning.split(".")[0].strip() + "."

    # Build one-liner
    total = len(yes_votes) + len(no_votes) + len(maybe_votes)
    if decision.outcome == "CONSENSUS":
        one_liner = f"Clear {answer}. All {total} agents agree — {conf_label.lower()} confidence."
    elif decision.outcome == "MAJORITY":
        majority_size = len(agreeing)
        one_liner = (
            f"Leaning {answer}. {majority_size}/{total} agents agree "
            f"({conf_label.lower()} confidence), but there are counterarguments worth considering."
        )
    elif decision.outcome == "SPLIT":
        one_liner = (
            f"This is a close call. Agents are split — consider gathering more "
            f"information before deciding."
        )
    else:
        one_liner = "Unable to reach a decision. The question may need to be reframed."

    return Verdict(
        answer=answer,
        confidence=conf,
        confidence_label=conf_label,
        one_liner=one_liner,
        top_reasons=top_reasons,
        top_risk=top_risk,
        agents_for=len(yes_votes),
        agents_against=len(no_votes),
        agents_undecided=len(maybe_votes),
        debate_quality=decision.outcome,
        duration=decision.duration_seconds,
    )


def format_verdict_text(verdict: Verdict) -> str:
    """Format verdict as clean, readable text."""
    lines = [
        "",
        f"  {'=' * 56}",
        f"  VERDICT: {verdict.answer}  ({verdict.confidence_label} confidence, {verdict.confidence:.0%})",
        f"  {'=' * 56}",
        "",
        f"  {verdict.one_liner}",
        "",
    ]

    if verdict.top_reasons:
        lines.append(f"  WHY:")
        for i, reason in enumerate(verdict.top_reasons, 1):
            lines.append(f"    {i}. {reason}")
        lines.append("")

    lines.append(f"  TOP RISK:")
    lines.append(f"    {verdict.top_risk}")
    lines.append("")

    lines.append(
        f"  Vote: {verdict.agents_for} for / {verdict.agents_against} against / "
        f"{verdict.agents_undecided} undecided  ({verdict.debate_quality})"
    )
    lines.append(f"  {'=' * 56}")
    lines.append("")

    return "\n".join(lines)


def format_verdict_rich(verdict: Verdict) -> None:
    """Render verdict with Rich formatting."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.rule import Rule

        console = Console()
        console.print()

        # Answer banner
        color = {"YES": "green", "NO": "red", "MAYBE": "yellow"}.get(verdict.answer, "white")
        console.print(Panel(
            Text(
                f"{verdict.answer}  —  {verdict.confidence_label} confidence ({verdict.confidence:.0%})",
                style=f"bold {color}",
                justify="center",
            ),
            border_style=color,
            padding=(1, 3),
        ))

        # One-liner
        console.print(f"  {verdict.one_liner}")
        console.print()

        # Top reasons
        if verdict.top_reasons:
            console.print(Rule("[bold]Why[/]"))
            for i, reason in enumerate(verdict.top_reasons, 1):
                console.print(f"  [bold]{i}.[/] {reason}")
            console.print()

        # Top risk
        console.print(Rule("[bold red]Top Risk[/]"))
        console.print(f"  [red]{verdict.top_risk}[/]")
        console.print()

        # Vote bar
        total = verdict.agents_for + verdict.agents_against + verdict.agents_undecided
        if total > 0:
            bar_width = 40
            for_w = int(verdict.agents_for / total * bar_width)
            against_w = int(verdict.agents_against / total * bar_width)
            maybe_w = bar_width - for_w - against_w
            bar = f"[green]{'█' * for_w}[/][red]{'█' * against_w}[/][yellow]{'█' * maybe_w}[/]"
            console.print(
                f"  {bar}  "
                f"[green]{verdict.agents_for}[/] for / "
                f"[red]{verdict.agents_against}[/] against / "
                f"[yellow]{verdict.agents_undecided}[/] undecided"
            )
            console.print()

        console.print(f"  [dim]{verdict.debate_quality} · {verdict.duration:.1f}s · swarm-agency v1.0.0[/]")
        console.print()

    except ImportError:
        print(format_verdict_text(verdict))
