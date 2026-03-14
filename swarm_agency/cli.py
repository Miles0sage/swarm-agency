"""CLI interface for swarm-agency.

A polished Rich-powered terminal UI showing agents debating in real-time.
"""

import argparse
import asyncio
import json
import sys
import time

from .types import AgencyRequest, Decision
from .agency import Agency
from .presets import create_full_agency_departments
from .demos import DEMO_SCENARIOS, DEMO_LIST

# ── Constants ─────────────────────────────────────────────────────────

DEPARTMENTS = [
    "Strategy", "Product", "Marketing", "Research",
    "Finance", "Engineering", "Legal", "Operations",
    "Sales", "Creative",
]

OUTCOME_STYLE = {
    "CONSENSUS": ("green", "bold green"),
    "MAJORITY": ("yellow", "bold yellow"),
    "SPLIT": ("red", "bold red"),
    "DEADLOCK": ("dim", "bold dim"),
}

POSITION_STYLE = {
    "APPROVE": ("bold green", "[green]YES[/]"),
    "REJECT": ("bold red", "[red]NO[/]"),
    "NEUTRAL": ("bold yellow", "[yellow]MAYBE[/]"),
    "YES": ("bold green", "[green]YES[/]"),
    "NO": ("bold red", "[red]NO[/]"),
    "MAYBE": ("bold yellow", "[yellow]MAYBE[/]"),
    "ERROR": ("bold red", "[red]ERR[/]"),
}


# ── Rich rendering ──────────────────────────────────────────────────

def _render_rich(question, context, decision, mode_label="Live"):
    """Render a debate with full Rich formatting."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.rule import Rule
    from rich import box

    console = Console()
    console.print()

    # ── Header ──
    console.print(Rule("[bold cyan]SWARM AGENCY[/]", style="cyan"))
    console.print()

    # ── Question panel ──
    q_text = Text(question, style="bold white")
    subtitle_parts = [
        f"{len(decision.votes)} agents",
        f"5 models",
        mode_label,
    ]
    if decision.duration_seconds > 0:
        subtitle_parts.append(f"{decision.duration_seconds:.1f}s")

    console.print(Panel(
        q_text,
        title="[bold]QUESTION[/]",
        subtitle=f"[dim]{' · '.join(subtitle_parts)}[/]",
        border_style="cyan",
        padding=(1, 3),
    ))

    if context:
        console.print(f"  [dim]Context:[/] {context}")
        console.print()

    # ── Decision outcome ──
    color, bold_color = OUTCOME_STYLE.get(decision.outcome, ("white", "bold white"))
    outcome_emoji = {
        "CONSENSUS": "✅", "MAJORITY": "📊", "SPLIT": "⚖️", "DEADLOCK": "🔒",
    }.get(decision.outcome, "")

    console.print(Panel(
        Text(f"{outcome_emoji}  {decision.outcome}: {decision.position}", style=bold_color, justify="center"),
        border_style=color,
        padding=(0, 2),
    ))

    # ── Confidence bar ──
    conf = decision.confidence
    bar_width = 40
    filled = int(conf * bar_width)
    bar_color = "green" if conf >= 0.6 else "yellow" if conf >= 0.3 else "red"
    bar = f"[{bar_color}]{'█' * filled}[/][dim]{'░' * (bar_width - filled)}[/]"
    console.print(f"  Confidence: {bar} [bold]{conf:.0%}[/]")
    console.print()

    # ── Summary ──
    console.print(f"  [bold]Summary:[/] {decision.summary}")
    console.print()

    # ── Vote tally ──
    counts = {}
    for v in decision.votes:
        pos = v.position
        counts[pos] = counts.get(pos, 0) + 1

    tally_parts = []
    for pos, count in sorted(counts.items(), key=lambda x: -x[1]):
        _, label = POSITION_STYLE.get(pos, ("white", pos))
        tally_parts.append(f"  {label}: [bold]{count}[/]")

    console.print(Rule("[bold]VOTE TALLY[/]"))
    console.print("  " + "    ".join(tally_parts))
    console.print()

    # ── Agent votes table ──
    console.print(Rule("[bold]AGENT DELIBERATION[/]"))
    console.print()

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Agent", style="cyan bold", width=20, no_wrap=True)
    table.add_column("Vote", width=6, justify="center")
    table.add_column("Conf", width=5, justify="right")
    table.add_column("Reasoning", ratio=1)

    for vote in decision.votes:
        _, pos_label = POSITION_STYLE.get(vote.position, ("white", vote.position))
        conf_val = vote.confidence
        conf_color = "green" if conf_val >= 0.7 else "yellow" if conf_val >= 0.4 else "red"
        conf_str = f"[{conf_color}]{conf_val:.0%}[/]"

        reasoning = vote.reasoning
        if len(reasoning) > 120:
            reasoning = reasoning[:117] + "..."

        table.add_row(vote.agent_name, pos_label, conf_str, reasoning)

    console.print(table)

    # ── Key factors (if any votes have them) ──
    votes_with_factors = [v for v in decision.votes if v.factors]
    if votes_with_factors:
        console.print()
        console.print(Rule("[bold]KEY FACTORS[/]"))
        console.print()
        for vote in votes_with_factors[:5]:  # Top 5 to keep it concise
            factors_str = " · ".join(vote.factors[:3])
            console.print(f"  [cyan]{vote.agent_name}[/]: [dim]{factors_str}[/]")
        console.print()

    # ── Dissenting views ──
    if decision.dissenting_views:
        console.print(Rule("[bold red]DISSENTING VIEWS[/]"))
        console.print()
        for view in decision.dissenting_views:
            # Split agent name from view if format is "Name: view"
            if ": " in view:
                name, text = view.split(": ", 1)
                console.print(f"  [red bold]{name}[/]: [dim]{text}[/]")
            else:
                console.print(f"  [dim]{view}[/]")
        console.print()

    # ── Footer ──
    console.print(Rule(style="dim"))
    console.print(
        f"  [dim]swarm-agency · {len(decision.votes)} agents · 5 model families · "
        f"github.com/Miles0sage/swarm-agency[/]"
    )
    console.print()


def _render_plain(question, context, decision):
    """Fallback rendering without Rich."""
    print(f"\n{'=' * 60}")
    print(f"  SWARM AGENCY DECISION")
    print(f"{'=' * 60}")
    print(f"\n  Question: {question}")
    if context:
        print(f"  Context: {context}")
    print(f"\n  Outcome: {decision.outcome}")
    print(f"  Position: {decision.position}")
    print(f"  Confidence: {decision.confidence:.0%}")
    print(f"  Agents: {len(decision.votes)}")
    print(f"\n  Summary: {decision.summary}")

    # Vote tally
    counts = {}
    for v in decision.votes:
        counts[v.position] = counts.get(v.position, 0) + 1
    tally = " | ".join(f"{pos}: {count}" for pos, count in sorted(counts.items(), key=lambda x: -x[1]))
    print(f"\n  Votes: {tally}")

    # Agent votes
    print(f"\n{'─' * 60}")
    print(f"  AGENT DELIBERATION")
    print(f"{'─' * 60}")
    for vote in decision.votes:
        reasoning = vote.reasoning[:80] + "..." if len(vote.reasoning) > 80 else vote.reasoning
        print(f"  {vote.agent_name:20s}  {vote.position:8s}  {vote.confidence:4.0%}  {reasoning}")

    # Dissenting views
    if decision.dissenting_views:
        print(f"\n{'─' * 60}")
        print(f"  DISSENTING VIEWS")
        print(f"{'─' * 60}")
        for d in decision.dissenting_views:
            print(f"  - {d}")

    print(f"\n{'=' * 60}\n")


# ── Demo mode ────────────────────────────────────────────────────────

def _run_demo(scenario_name):
    """Run a pre-computed demo scenario."""
    if scenario_name not in DEMO_SCENARIOS:
        print(f"Unknown demo: {scenario_name}")
        print(f"Available: {', '.join(DEMO_LIST)}")
        sys.exit(1)
    scenario = DEMO_SCENARIOS[scenario_name]
    return scenario["question"], scenario["context"], scenario["decision"]


def _list_demos():
    """Print available demo scenarios."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich import box

        console = Console()
        console.print()

        table = Table(
            title="Available Scenarios",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan bold")
        table.add_column("Question")
        table.add_column("Dept", style="yellow")
        for i, name in enumerate(DEMO_LIST, 1):
            s = DEMO_SCENARIOS[name]
            table.add_row(str(i), name, s["question"], s["department"])
        console.print(table)
        console.print()
        console.print("[dim]  Run with:[/] [bold]swarm-agency --demo <name>[/]")
        console.print("[dim]  Example:[/] [bold]swarm-agency --demo startup-pivot[/]")
        console.print()
    except ImportError:
        print("\nAvailable demo scenarios:\n")
        for i, name in enumerate(DEMO_LIST, 1):
            s = DEMO_SCENARIOS[name]
            print(f"  {i}. {name}: {s['question']} ({s['department']})")
        print(f"\nRun with: swarm-agency --demo <name>\n")


def _list_agents():
    """List all 43 agents across 10 departments."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()
        console.print()

        depts = create_full_agency_departments()
        total = 0

        table = Table(
            title="All Agents",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
        )
        table.add_column("Department", style="yellow bold", width=14)
        table.add_column("Agent", style="cyan bold", width=20)
        table.add_column("Role", width=24)
        table.add_column("Model", style="dim", width=20)
        table.add_column("Bias")

        for dept in depts:
            for i, agent in enumerate(dept.agents):
                dept_name = dept.name if i == 0 else ""
                table.add_row(
                    dept_name,
                    agent.name,
                    agent.role,
                    agent.model,
                    agent.bias[:50] + "..." if len(agent.bias) > 50 else agent.bias,
                )
                total += 1

        console.print(table)
        console.print(f"\n  [bold]{total} agents[/] across [bold]{len(depts)} departments[/] using [bold]5 model families[/]")
        console.print()
    except ImportError:
        depts = create_full_agency_departments()
        for dept in depts:
            print(f"\n{dept.name}:")
            for agent in dept.agents:
                print(f"  {agent.name} ({agent.role}) - {agent.model}")


# ── Live debate with progress ────────────────────────────────────────

def _run_live_with_progress(question, context, department, api_key, base_url, memory):
    """Run a live debate with Rich progress display."""
    try:
        from rich.console import Console
        from rich.live import Live
        from rich.spinner import Spinner
        from rich.text import Text
        from rich.panel import Panel

        console = Console()
        console.print()
        console.print(Panel(
            Text(question, style="bold white"),
            title="[bold cyan]DEBATING[/]",
            subtitle="[dim]Agents deliberating across 5 model families...[/]",
            border_style="cyan",
            padding=(1, 3),
        ))

        # Show spinner during API calls
        with console.status(
            "[bold cyan]Agents are deliberating...[/]",
            spinner="dots",
        ):
            agency = Agency(
                name="SwarmAgency",
                api_key=api_key,
                base_url=base_url,
                memory_enabled=memory,
            )
            for dept in create_full_agency_departments():
                agency.add_department(dept)

            import uuid
            request = AgencyRequest(
                request_id=f"cli-{uuid.uuid4().hex[:8]}",
                question=question,
                context=context,
                department=department,
            )

            start = time.time()
            decision = asyncio.run(agency.decide(request))
            elapsed = time.time() - start

        if decision.duration_seconds == 0:
            decision.duration_seconds = round(elapsed, 1)

        return decision

    except ImportError:
        # No Rich — run without progress
        agency = Agency(
            name="SwarmAgency",
            api_key=api_key,
            base_url=base_url,
            memory_enabled=memory,
        )
        for dept in create_full_agency_departments():
            agency.add_department(dept)

        import uuid
        request = AgencyRequest(
            request_id=f"cli-{uuid.uuid4().hex[:8]}",
            question=question,
            context=context,
            department=department,
        )

        print("\nAgents deliberating...")
        decision = asyncio.run(agency.decide(request))
        return decision


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="swarm-agency",
        description="43 AI agents debate your business decisions across 5 model families.",
        epilog="Examples:\n"
               "  swarm-agency \"Should we raise a Series A?\"\n"
               "  swarm-agency \"Open-source our SDK?\" --department Engineering\n"
               "  swarm-agency --demo startup-pivot\n"
               "  swarm-agency --agents\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("question", nargs="?", help="The question for the agency to debate")
    parser.add_argument("--context", "-c", help="Additional context for the decision")
    parser.add_argument(
        "--department", "-d",
        choices=DEPARTMENTS,
        help="Target a specific department (default: all 10)",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--api-key", help="DashScope API key (or set ALIBABA_CODING_API_KEY)")
    parser.add_argument("--base-url", help="API base URL override")
    parser.add_argument(
        "--demo",
        nargs="?",
        const="__list__",
        metavar="SCENARIO",
        help="Run a pre-computed demo (no API key). Use --demo to list.",
    )
    parser.add_argument(
        "--agents", action="store_true",
        help="List all 43 agents across 10 departments",
    )
    parser.add_argument(
        "--memory", action="store_true",
        help="Enable decision memory (SQLite)",
    )
    parser.add_argument(
        "--feedback",
        nargs=2,
        metavar=("REQUEST_ID", "CORRECT"),
        help="Record feedback: --feedback <request_id> yes|no",
    )
    parser.add_argument(
        "--history",
        nargs="?",
        const="__all__",
        metavar="DEPARTMENT",
        help="Show decision history. Optionally filter by department.",
    )

    args = parser.parse_args()

    # ── Agents list ──
    if args.agents:
        _list_agents()
        return

    # ── Feedback mode ──
    if args.feedback:
        from .memory import DecisionMemoryStore
        store = DecisionMemoryStore()
        request_id, correct_str = args.feedback
        was_correct = correct_str.lower() in ("yes", "true", "1", "correct")
        if store.add_feedback(request_id, was_correct):
            print(f"Feedback recorded for {request_id}: {'correct' if was_correct else 'incorrect'}")
        else:
            print(f"Decision {request_id} not found in memory.")
            sys.exit(1)
        store.close()
        return

    # ── History mode ──
    if args.history is not None:
        from .memory import DecisionMemoryStore
        store = DecisionMemoryStore()
        dept_filter = None if args.history == "__all__" else args.history
        records = store.get_history(department=dept_filter)
        store.close()
        if not records:
            print("No decisions in memory yet. Run with --memory to start tracking.")
            return
        if args.json:
            print(json.dumps([r.to_dict() for r in records], indent=2))
            return
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import box
            console = Console()
            table = Table(title="Decision History", box=box.ROUNDED)
            table.add_column("ID", style="dim", width=12)
            table.add_column("Question", max_width=40)
            table.add_column("Dept", style="yellow")
            table.add_column("Outcome")
            table.add_column("Position", style="bold")
            table.add_column("Correct?")
            for r in records:
                outcome_color = {"CONSENSUS": "green", "MAJORITY": "yellow", "SPLIT": "red"}.get(r.outcome, "white")
                correct_str = "?" if r.feedback_correct is None else ("yes" if r.feedback_correct else "no")
                table.add_row(
                    r.request_id[:12],
                    r.question[:40],
                    r.department,
                    f"[{outcome_color}]{r.outcome}[/]",
                    r.position,
                    correct_str,
                )
            console.print(table)
        except ImportError:
            for r in records:
                correct_str = "?" if r.feedback_correct is None else ("yes" if r.feedback_correct else "no")
                print(f"  {r.request_id[:12]}  {r.department:12s}  {r.outcome:10s}  {r.position:10s}  correct={correct_str}  {r.question[:50]}")
        return

    # ── Demo mode ──
    if args.demo is not None:
        if args.demo == "__list__":
            _list_demos()
            return
        question, context, decision = _run_demo(args.demo)
        mode_label = "Demo"
    else:
        # ── Live debate ──
        if not args.question:
            parser.error("question is required (or use --demo)")
        question = args.question
        context = args.context
        decision = _run_live_with_progress(
            question=question,
            context=context,
            department=args.department,
            api_key=args.api_key,
            base_url=args.base_url,
            memory=args.memory,
        )
        mode_label = "Live"

    # ── Output ──
    if args.json:
        print(json.dumps(decision.to_dict(), indent=2))
        return

    try:
        _render_rich(question, context or "", decision, mode_label)
    except ImportError:
        _render_plain(question, context or "", decision)


if __name__ == "__main__":
    main()
