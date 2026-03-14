"""CLI interface for swarm-agency."""

import argparse
import asyncio
import json
import sys

from .types import AgencyRequest
from .agency import Agency
from .presets import create_full_agency_departments
from .demos import DEMO_SCENARIOS, DEMO_LIST


def _run_demo(scenario_name):
    """Run a pre-computed demo scenario. Returns the Decision object."""
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

        console = Console()
        console.print("\n[bold]Available demo scenarios:[/]\n")
        table = Table(show_header=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan bold")
        table.add_column("Question")
        table.add_column("Dept", style="yellow")
        for i, name in enumerate(DEMO_LIST, 1):
            s = DEMO_SCENARIOS[name]
            table.add_row(str(i), name, s["question"], s["department"])
        console.print(table)
        console.print("\n[dim]Run with: swarm-agency --demo <name>[/]\n")
    except ImportError:
        print("\nAvailable demo scenarios:\n")
        for i, name in enumerate(DEMO_LIST, 1):
            s = DEMO_SCENARIOS[name]
            print(f"  {i}. {name}: {s['question']} ({s['department']})")
        print(f"\nRun with: swarm-agency --demo <name>\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI Agency - multi-model agents debate your decisions"
    )
    parser.add_argument("question", nargs="?", help="The question/decision for the agency")
    parser.add_argument("--context", "-c", help="Additional context")
    parser.add_argument(
        "--department", "-d",
        choices=[
            "Strategy", "Product", "Marketing", "Research",
            "Finance", "Engineering", "Legal", "Operations",
            "Sales", "Creative",
        ],
        help="Target a specific department (default: all)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--api-key", help="API key (or set ALIBABA_CODING_API_KEY)")
    parser.add_argument("--base-url", help="API base URL")
    parser.add_argument(
        "--demo",
        nargs="?",
        const="__list__",
        metavar="SCENARIO",
        help="Run a pre-computed demo (no API key needed). Use --demo to list scenarios.",
    )
    parser.add_argument(
        "--memory", action="store_true",
        help="Enable decision memory (stores decisions in SQLite for future reference)",
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

    # Feedback mode
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

    # History mode
    if args.history is not None:
        from .memory import DecisionMemoryStore
        store = DecisionMemoryStore()
        dept_filter = None if args.history == "__all__" else args.history
        records = store.get_history(department=dept_filter)
        store.close()
        if not records:
            print("No decisions in memory yet.")
            return
        if args.json:
            print(json.dumps([r.to_dict() for r in records], indent=2))
            return
        try:
            from rich.console import Console
            from rich.table import Table
            console = Console()
            table = Table(title="Decision History")
            table.add_column("ID", style="dim")
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

    # Demo mode
    if args.demo is not None:
        if args.demo == "__list__":
            _list_demos()
            return
        question, context, decision = _run_demo(args.demo)
    else:
        if not args.question:
            parser.error("question is required (or use --demo)")

        agency = Agency(
            name="SwarmAgency",
            api_key=args.api_key,
            base_url=args.base_url,
            memory_enabled=args.memory,
        )
        for dept in create_full_agency_departments():
            agency.add_department(dept)

        import uuid
        request = AgencyRequest(
            request_id=f"cli-{uuid.uuid4().hex[:8]}",
            question=args.question,
            context=args.context,
            department=args.department,
        )

        decision = asyncio.run(agency.decide(request))

    if args.json:
        print(json.dumps(decision.to_dict(), indent=2))
        return

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.align import Align
        from rich.text import Text

        console = Console()

        # Question panel (demo mode)
        if args.demo is not None and args.demo != "__list__":
            console.print()
            console.print(Panel(
                Align.center(Text(question, style="bold white")),
                title="[bold cyan]QUESTION",
                subtitle=f"[dim]Department: {decision.department} | {len(decision.votes)} agents | Demo mode[/dim]",
                border_style="cyan",
                padding=(1, 2),
            ))
            if context:
                console.print(f"[dim]Context: {context}[/]")
            console.print()

        # Outcome panel
        color = {"CONSENSUS": "green", "MAJORITY": "yellow", "SPLIT": "red"}.get(
            decision.outcome, "white"
        )
        console.print(Panel(
            f"[bold {color}]{decision.outcome}: {decision.position}[/]",
            title="AGENCY DECISION",
            border_style=color,
        ))

        # Votes table
        table = Table(title="Agent Votes")
        table.add_column("Agent", style="cyan")
        table.add_column("Position", style="bold")
        table.add_column("Confidence", justify="right")
        table.add_column("Reasoning")

        for vote in decision.votes:
            conf_color = "green" if vote.confidence >= 0.7 else "yellow" if vote.confidence >= 0.4 else "red"
            table.add_row(
                vote.agent_name,
                vote.position,
                f"[{conf_color}]{vote.confidence:.0%}[/]",
                vote.reasoning[:60] + "..." if len(vote.reasoning) > 60 else vote.reasoning,
            )

        console.print(table)
        console.print(f"\n[dim]{decision.summary}[/]")
        console.print(f"[dim]Confidence: {decision.confidence:.1%} | Duration: {decision.duration_seconds}s[/]")

        if decision.dissenting_views:
            console.print("\n[bold red]Dissenting Views:[/]")
            for d in decision.dissenting_views:
                console.print(f"  - {d}")

    except ImportError:
        print(f"\n{'='*50}")
        print(f"  AGENCY DECISION: {decision.outcome}")
        print(f"  Position: {decision.position}")
        print(f"  Confidence: {decision.confidence:.1%}")
        print(f"{'='*50}")
        print(f"\n{decision.summary}")
        print(f"\nVotes:")
        for vote in decision.votes:
            print(f"  {vote.agent_name}: {vote.position} ({vote.confidence:.0%}) - {vote.reasoning[:80]}")
        if decision.dissenting_views:
            print(f"\nDissenting:")
            for d in decision.dissenting_views:
                print(f"  - {d}")


if __name__ == "__main__":
    main()
