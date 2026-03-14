"""Dual Debate — run the same question through 2 different model families
and compare results. Shows where models agree and disagree.

This is the killer feature: when Chinese models (DashScope) and Western models
(OpenRouter) agree, confidence is HIGH. When they disagree, you need to think harder.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from .types import AgencyRequest, Decision

logger = logging.getLogger("swarm_agency.dual_debate")


@dataclass
class DualDebateResult:
    """Side-by-side comparison of two provider debates."""
    question: str
    context: Optional[str]

    # Provider A results
    provider_a: str
    decision_a: Decision
    duration_a: float

    # Provider B results
    provider_b: str
    decision_b: Decision
    duration_b: float

    # Comparison
    providers_agree: bool
    agreement_detail: str
    combined_confidence: float
    verdict: str  # the final recommendation
    verdict_reasoning: str


def _compare_decisions(a: Decision, b: Decision, provider_a: str, provider_b: str) -> dict:
    """Compare two decisions and produce a verdict."""
    same_position = a.position.upper() == b.position.upper()
    same_outcome = a.outcome == b.outcome

    # Combined confidence: if they agree, boost. If they disagree, reduce.
    if same_position:
        # Agreement across model families = strong signal
        combined = (a.confidence + b.confidence) / 2 * 1.2  # 20% boost
        combined = min(combined, 0.99)

        if a.confidence > 0.7 and b.confidence > 0.7:
            detail = f"Strong agreement: both {provider_a} and {provider_b} models independently reached {a.position} with high confidence"
            verdict = a.position
            reasoning = (
                f"Cross-model consensus: {provider_a} ({a.confidence:.0%}) and {provider_b} ({b.confidence:.0%}) "
                f"independently agree on {a.position}. Different training data, same conclusion = strong signal."
            )
        else:
            detail = f"Weak agreement: both say {a.position} but with moderate confidence"
            verdict = a.position
            reasoning = (
                f"Both providers agree on {a.position} but confidence is moderate. "
                f"{provider_a}: {a.confidence:.0%}, {provider_b}: {b.confidence:.0%}. "
                f"Consider gathering more information before deciding."
            )
    else:
        # Disagreement = interesting signal
        combined = abs(a.confidence - b.confidence) * 0.5
        combined = max(combined, 0.15)

        detail = (
            f"Disagreement: {provider_a} says {a.position} ({a.confidence:.0%}) "
            f"while {provider_b} says {b.position} ({b.confidence:.0%})"
        )

        # Higher confidence provider gets more weight
        if a.confidence > b.confidence:
            verdict = a.position
            reasoning = (
                f"Models disagree. {provider_a} ({a.position}, {a.confidence:.0%}) has higher conviction than "
                f"{provider_b} ({b.position}, {b.confidence:.0%}). But disagreement itself suggests this is a "
                f"close call. Key difference: {provider_a} emphasizes '{a.summary[:100]}' while "
                f"{provider_b} counters '{b.summary[:100]}'"
            )
        else:
            verdict = b.position
            reasoning = (
                f"Models disagree. {provider_b} ({b.position}, {b.confidence:.0%}) has higher conviction than "
                f"{provider_a} ({a.position}, {a.confidence:.0%}). The disagreement means this decision "
                f"has real trade-offs worth exploring."
            )

    return {
        "agree": same_position,
        "detail": detail,
        "combined_confidence": round(combined, 3),
        "verdict": verdict,
        "reasoning": reasoning,
    }


async def dual_debate(
    question: str,
    context: Optional[str] = None,
    department: Optional[str] = None,
    provider_a: str = "dashscope",
    provider_b: str = "openrouter",
    memory: bool = False,
) -> DualDebateResult:
    """Run the same question through two different providers in parallel.

    Returns a DualDebateResult with side-by-side comparison.
    """
    from .agency import Agency
    from .presets import create_full_agency_departments

    request_id_base = uuid.uuid4().hex[:8]

    async def _run_provider(provider: str, suffix: str) -> tuple[Decision, float]:
        agency = Agency(
            name=f"Dual-{provider}",
            memory_enabled=memory,
            provider=provider,
        )
        for dept in create_full_agency_departments():
            agency.add_department(dept)

        request = AgencyRequest(
            request_id=f"dual-{suffix}-{request_id_base}",
            question=question,
            context=context,
            department=department,
        )
        start = time.time()
        decision = await agency.decide(request)
        return decision, time.time() - start

    # Run both in parallel
    (decision_a, dur_a), (decision_b, dur_b) = await asyncio.gather(
        _run_provider(provider_a, "a"),
        _run_provider(provider_b, "b"),
    )

    comparison = _compare_decisions(decision_a, decision_b, provider_a, provider_b)

    return DualDebateResult(
        question=question,
        context=context,
        provider_a=provider_a,
        decision_a=decision_a,
        duration_a=round(dur_a, 2),
        provider_b=provider_b,
        decision_b=decision_b,
        duration_b=round(dur_b, 2),
        providers_agree=comparison["agree"],
        agreement_detail=comparison["detail"],
        combined_confidence=comparison["combined_confidence"],
        verdict=comparison["verdict"],
        verdict_reasoning=comparison["reasoning"],
    )


def format_dual_result_text(result: DualDebateResult) -> str:
    """Format dual debate result as readable text."""
    lines = [
        f"{'=' * 70}",
        f"  DUAL DEBATE: {result.question[:60]}",
        f"{'=' * 70}",
        f"",
        f"  Provider A: {result.provider_a} ({len(result.decision_a.votes)} agents, {result.duration_a}s)",
        f"    Outcome: {result.decision_a.outcome} → {result.decision_a.position} ({result.decision_a.confidence:.0%})",
        f"    Summary: {result.decision_a.summary[:100]}",
        f"",
        f"  Provider B: {result.provider_b} ({len(result.decision_b.votes)} agents, {result.duration_b}s)",
        f"    Outcome: {result.decision_b.outcome} → {result.decision_b.position} ({result.decision_b.confidence:.0%})",
        f"    Summary: {result.decision_b.summary[:100]}",
        f"",
        f"{'─' * 70}",
        f"  COMPARISON: {'AGREE' if result.providers_agree else 'DISAGREE'}",
        f"  {result.agreement_detail}",
        f"",
        f"  VERDICT: {result.verdict} (combined confidence: {result.combined_confidence:.0%})",
        f"  {result.verdict_reasoning}",
        f"{'=' * 70}",
    ]
    return "\n".join(lines)


def format_dual_result_rich(result: DualDebateResult) -> None:
    """Render dual debate with clean Rich visuals."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    from rich import box

    console = Console()
    console.print()

    # Header
    console.print(Panel(
        Text(result.question, style="bold white", justify="center"),
        title="[bold cyan]DUAL DEBATE[/]",
        subtitle="[dim]Same question, different AI model families[/]",
        border_style="cyan",
        padding=(1, 3),
    ))
    console.print()

    # Side-by-side verdicts
    from .verdict import decision_to_verdict

    verdict_a = decision_to_verdict(result.decision_a)
    verdict_b = decision_to_verdict(result.decision_b)

    color_a = {"YES": "green", "NO": "red", "MAYBE": "yellow"}.get(verdict_a.answer, "white")
    color_b = {"YES": "green", "NO": "red", "MAYBE": "yellow"}.get(verdict_b.answer, "white")

    provider_labels = {
        "dashscope": "Chinese Models\n(GLM, Qwen, Kimi, MiniMax)",
        "openrouter": "Western Models\n(Claude, Gemini, DeepSeek, Llama)",
    }

    panel_a = Panel(
        Text(f"{verdict_a.answer}\n{verdict_a.confidence:.0%} confidence\n{verdict_a.agents_for}v{verdict_a.agents_against}",
             style=f"bold {color_a}", justify="center"),
        title=f"[bold]{provider_labels.get(result.provider_a, result.provider_a)}[/]",
        border_style=color_a,
        width=35,
    )
    panel_b = Panel(
        Text(f"{verdict_b.answer}\n{verdict_b.confidence:.0%} confidence\n{verdict_b.agents_for}v{verdict_b.agents_against}",
             style=f"bold {color_b}", justify="center"),
        title=f"[bold]{provider_labels.get(result.provider_b, result.provider_b)}[/]",
        border_style=color_b,
        width=35,
    )
    console.print(Columns([panel_a, panel_b], padding=(0, 4)))
    console.print()

    # Agreement banner
    if result.providers_agree:
        agree_color = "green"
        agree_text = f"AGREE: Both say {result.verdict}"
        signal = "Different training data, same conclusion = strong signal"
    else:
        agree_color = "red"
        agree_text = f"DISAGREE: Split decision"
        signal = "Models trained on different data reach different conclusions"

    console.print(Panel(
        Text(f"{agree_text}\nCombined confidence: {result.combined_confidence:.0%}\n{signal}",
             style=f"bold {agree_color}", justify="center"),
        border_style=agree_color,
    ))
    console.print()

    # Reasons comparison table
    table = Table(
        title="Reasoning Comparison",
        box=box.ROUNDED, show_header=True, header_style="bold", expand=True,
    )
    table.add_column(result.provider_a, style="cyan", ratio=1)
    table.add_column(result.provider_b, style="magenta", ratio=1)

    reasons_a = verdict_a.top_reasons[:3]
    reasons_b = verdict_b.top_reasons[:3]
    max_rows = max(len(reasons_a), len(reasons_b))
    for i in range(max_rows):
        ra = reasons_a[i] if i < len(reasons_a) else ""
        rb = reasons_b[i] if i < len(reasons_b) else ""
        table.add_row(ra[:80], rb[:80])

    console.print(table)
    console.print()

    # Final verdict
    console.print(Panel(
        Text(f"VERDICT: {result.verdict}\n\n{result.verdict_reasoning[:200]}",
             justify="center"),
        title="[bold]COMBINED DECISION[/]",
        border_style="cyan",
        padding=(1, 2),
    ))

    console.print(f"\n  [dim]{result.provider_a}: {result.duration_a}s · {result.provider_b}: {result.duration_b}s · swarm-agency v1.0.0[/]\n")


def format_dual_result_dict(result: DualDebateResult) -> dict:
    """Format dual debate result as JSON-serializable dict."""
    return {
        "question": result.question,
        "context": result.context,
        "provider_a": {
            "name": result.provider_a,
            "outcome": result.decision_a.outcome,
            "position": result.decision_a.position,
            "confidence": result.decision_a.confidence,
            "summary": result.decision_a.summary,
            "agents": len(result.decision_a.votes),
            "duration": result.duration_a,
            "votes": [
                {"agent": v.agent_name, "position": v.position,
                 "confidence": v.confidence, "reasoning": v.reasoning[:200]}
                for v in result.decision_a.votes
            ],
        },
        "provider_b": {
            "name": result.provider_b,
            "outcome": result.decision_b.outcome,
            "position": result.decision_b.position,
            "confidence": result.decision_b.confidence,
            "summary": result.decision_b.summary,
            "agents": len(result.decision_b.votes),
            "duration": result.duration_b,
            "votes": [
                {"agent": v.agent_name, "position": v.position,
                 "confidence": v.confidence, "reasoning": v.reasoning[:200]}
                for v in result.decision_b.votes
            ],
        },
        "comparison": {
            "providers_agree": result.providers_agree,
            "agreement_detail": result.agreement_detail,
            "combined_confidence": result.combined_confidence,
            "verdict": result.verdict,
            "verdict_reasoning": result.verdict_reasoning,
        },
    }
