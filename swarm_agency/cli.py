"""CLI interface for swarm-agency."""

import argparse
import asyncio
import json
import sys

from .types import AgencyRequest
from .agency import Agency
from .presets import create_full_agency_departments


def main():
    parser = argparse.ArgumentParser(
        description="AI Agency - multi-model agents debate your decisions"
    )
    parser.add_argument("question", help="The question/decision for the agency")
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

    args = parser.parse_args()

    agency = Agency(
        name="SwarmAgency",
        api_key=args.api_key,
        base_url=args.base_url,
    )
    for dept in create_full_agency_departments():
        agency.add_department(dept)

    request = AgencyRequest(
        request_id="cli-001",
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

        console = Console()

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
