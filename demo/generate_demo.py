#!/usr/bin/env python3
"""Generate a static terminal demo of swarm-agency.

Produces a visually impressive Rich-rendered demo showing the Strategy
department debating "Should we launch feature X?" -- no API key needed.

Outputs:
  demo/demo_output.txt      - plain text (for copy-paste)
  demo/demo_output_ansi.txt - ANSI colored (for terminal replay)
"""

import sys
import time
from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich.live import Live
from rich.padding import Padding
from rich.layout import Layout
from rich import box


# ── Demo Data ──────────────────────────────────────────────────────────

QUESTION = "Should we launch feature X?"
DEPARTMENT = "Strategy"
COMMAND = 'swarm-agency ask "Should we launch feature X?" --department strategy'

AGENTS = [
    {
        "name": "Visionary",
        "role": "Chief Strategy Officer",
        "model": "glm-4.7",
        "position": "APPROVE",
        "confidence": 0.85,
        "reasoning": "Feature X aligns with our 3-year roadmap and creates a defensible moat in the mid-market segment. Competitors are 6-12 months behind on this capability.",
        "factors": [
            "Strategic alignment with long-term vision",
            "First-mover advantage in underserved segment",
            "Creates switching costs for enterprise users",
        ],
    },
    {
        "name": "DevilsAdvocate",
        "role": "Board Advisor",
        "model": "kimi-k2.5",
        "position": "REJECT",
        "confidence": 0.72,
        "reasoning": "Risk profile is unclear. We haven't validated demand beyond internal assumptions. Launch could cannibalize our core product's revenue by 15-20%.",
        "factors": [
            "No external demand validation completed",
            "Cannibalization risk to core product line",
            "Engineering capacity already stretched thin",
        ],
        "dissent": "Launching without market validation is hubris disguised as strategy.",
    },
    {
        "name": "GrowthHacker",
        "role": "VP Growth",
        "model": "MiniMax-M2.5",
        "position": "APPROVE",
        "confidence": 0.78,
        "reasoning": "Market timing is ideal. TAM expands by $4.2B if we capture the prosumer segment. Feature X is the wedge product we need for bottom-up adoption.",
        "factors": [
            "TAM expansion into prosumer segment",
            "PLG motion fits feature X perfectly",
            "Q2 launch catches seasonal demand wave",
        ],
    },
    {
        "name": "NumbersCruncher",
        "role": "CFO",
        "model": "qwen3-coder-plus",
        "position": "NEUTRAL",
        "confidence": 0.45,
        "reasoning": "Unit economics are promising but unproven. Need 2,400 paid conversions in Q3 to hit break-even. Current projections show 1,800-3,200 range -- too wide.",
        "factors": [
            "Break-even requires 2,400 paid conversions",
            "Projection confidence interval too wide",
            "R&D investment recoverable in 8-14 months",
        ],
    },
    {
        "name": "Pragmatist",
        "role": "COO",
        "model": "qwen3.5-plus",
        "position": "APPROVE",
        "confidence": 0.68,
        "reasoning": "Operationally feasible with current team if we defer the Platform v2 migration by one sprint. Recommend phased rollout: beta in Q2, GA in Q3.",
        "factors": [
            "Team capacity available with schedule trade-off",
            "Phased rollout reduces blast radius",
            "Existing CI/CD pipeline supports feature flags",
        ],
        "conditions": "Defer Platform v2 migration by one sprint; phased rollout mandatory.",
    },
]

SUMMARY = (
    "The Strategy department recommends APPROVAL with conditions. "
    "3 of 5 agents support launch (Visionary, GrowthHacker, Pragmatist), "
    "1 rejects (DevilsAdvocate citing unvalidated risk), and 1 is neutral "
    "(NumbersCruncher requesting tighter financial projections). "
    "Recommended path: phased rollout with market validation gate before GA."
)

DISSENTING_VIEWS = [
    "DevilsAdvocate: No external demand validation -- launching on assumptions alone.",
    "NumbersCruncher: Financial projections need tighter confidence interval before committing full resources.",
]


# ── Render Functions ───────────────────────────────────────────────────

def render_header(console: Console) -> None:
    """Render the command header."""
    console.print()
    header = Text()
    header.append("  $ ", style="bold green")
    header.append(COMMAND, style="bold white")
    console.print(Panel(
        header,
        border_style="dim",
        padding=(0, 1),
    ))
    console.print()


def render_question_panel(console: Console) -> None:
    """Render the question being debated."""
    console.print(Panel(
        Align.center(
            Text(QUESTION, style="bold white on blue", justify="center"),
        ),
        title="[bold cyan]QUESTION",
        subtitle=f"[dim]Department: {DEPARTMENT} | 5 agents | 5 models[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def render_deliberation(console: Console) -> None:
    """Render the agent deliberation progress."""
    console.print(Rule("[bold yellow]Agent Deliberation", style="yellow"))
    console.print()

    for agent in AGENTS:
        model_color = {
            "glm-4.7": "bright_magenta",
            "kimi-k2.5": "bright_cyan",
            "MiniMax-M2.5": "bright_yellow",
            "qwen3-coder-plus": "bright_green",
            "qwen3.5-plus": "bright_blue",
        }.get(agent["model"], "white")

        status_icon = {
            "APPROVE": "[bold green]APPROVE[/]",
            "REJECT": "[bold red]REJECT[/]",
            "NEUTRAL": "[bold yellow]NEUTRAL[/]",
        }[agent["position"]]

        agent_panel = Panel(
            f"[dim]{agent['reasoning']}[/dim]\n\n"
            f"  Position: {status_icon}  |  "
            f"Confidence: [bold]{agent['confidence']:.0%}[/bold]  |  "
            f"Model: [{model_color}]{agent['model']}[/{model_color}]",
            title=f"[bold]{agent['name']}[/bold] [dim]({agent['role']})[/dim]",
            border_style="dim",
            padding=(0, 2),
        )
        console.print(agent_panel)

    console.print()


def render_vote_table(console: Console) -> None:
    """Render the votes as a styled table."""
    console.print(Rule("[bold]Vote Summary", style="white"))
    console.print()

    table = Table(
        title=None,
        box=box.HEAVY_HEAD,
        show_lines=True,
        title_style="bold",
        border_style="bright_blue",
        header_style="bold bright_white on dark_blue",
        pad_edge=True,
        padding=(0, 1),
    )
    table.add_column("Agent", style="bold cyan", min_width=16)
    table.add_column("Role", style="dim", min_width=20)
    table.add_column("Model", min_width=16)
    table.add_column("Position", justify="center", min_width=9)
    table.add_column("Confidence", justify="center", min_width=14)
    table.add_column("Key Factor", no_wrap=True)

    for agent in AGENTS:
        # Position styling
        pos_style = {
            "APPROVE": "[bold green]APPROVE[/]",
            "REJECT": "[bold red]REJECT[/]",
            "NEUTRAL": "[bold yellow]NEUTRAL[/]",
        }[agent["position"]]

        # Confidence bar
        conf = agent["confidence"]
        filled = int(conf * 10)
        empty = 10 - filled
        if conf >= 0.7:
            bar_color = "green"
        elif conf >= 0.5:
            bar_color = "yellow"
        else:
            bar_color = "red"
        conf_bar = f"[{bar_color}]{'█' * filled}{'░' * empty}[/{bar_color}] {conf:.0%}"

        # Model coloring
        model_color = {
            "glm-4.7": "bright_magenta",
            "kimi-k2.5": "bright_cyan",
            "MiniMax-M2.5": "bright_yellow",
            "qwen3-coder-plus": "bright_green",
            "qwen3.5-plus": "bright_blue",
        }.get(agent["model"], "white")

        table.add_row(
            agent["name"],
            agent["role"],
            f"[{model_color}]{agent['model']}[/{model_color}]",
            pos_style,
            conf_bar,
            agent["factors"][0],
        )

    console.print(Align.center(table))
    console.print()


def render_tally(console: Console) -> None:
    """Render the vote tally bar."""
    approve_count = sum(1 for a in AGENTS if a["position"] == "APPROVE")
    reject_count = sum(1 for a in AGENTS if a["position"] == "REJECT")
    neutral_count = sum(1 for a in AGENTS if a["position"] == "NEUTRAL")

    tally_text = Text(justify="center")
    tally_text.append(f"  APPROVE: {approve_count}  ", style="bold white on green")
    tally_text.append("  ")
    tally_text.append(f"  REJECT: {reject_count}  ", style="bold white on red")
    tally_text.append("  ")
    tally_text.append(f"  NEUTRAL: {neutral_count}  ", style="bold white on dark_orange3")

    console.print(Align.center(tally_text))
    console.print()


def render_decision(console: Console) -> None:
    """Render the final decision panel."""
    decision_text = Text()
    decision_text.append("MAJORITY: ", style="bold yellow")
    decision_text.append("APPROVE", style="bold green")
    decision_text.append(" (3-1-1)", style="bold white")

    console.print(Panel(
        Align.center(decision_text),
        title="[bold white]AGENCY DECISION[/bold white]",
        border_style="green",
        padding=(1, 4),
    ))
    console.print()


def render_summary(console: Console) -> None:
    """Render the summary and dissenting views."""
    console.print(Panel(
        f"[dim]{SUMMARY}[/dim]",
        title="[bold]Summary",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    # Dissenting views
    console.print("[bold red]Dissenting Views:[/]")
    for view in DISSENTING_VIEWS:
        console.print(f"  [dim red]>[/] {view}")
    console.print()

    # Footer stats
    console.print(
        "[dim]Confidence: 72.0% | "
        "Duration: 3.2s | "
        "Models used: glm-4.7, kimi-k2.5, MiniMax-M2.5, qwen3-coder-plus, qwen3.5-plus[/dim]"
    )
    console.print()


def render_full_demo(console: Console) -> None:
    """Render the complete demo output."""
    render_header(console)
    render_question_panel(console)
    render_deliberation(console)
    render_vote_table(console)
    render_tally(console)
    render_decision(console)
    render_summary(console)


# ── Main ───────────────────────────────────────────────────────────────

def main() -> None:
    demo_dir = Path(__file__).parent

    # 1. Render to terminal (live)
    live_console = Console(force_terminal=True)
    render_full_demo(live_console)

    # 2. Save ANSI output
    ansi_buffer = StringIO()
    ansi_console = Console(file=ansi_buffer, force_terminal=True, width=140)
    render_full_demo(ansi_console)
    ansi_path = demo_dir / "demo_output_ansi.txt"
    ansi_path.write_text(ansi_buffer.getvalue())
    print(f"\nSaved ANSI output to {ansi_path}")

    # 3. Save plain text output
    plain_buffer = StringIO()
    plain_console = Console(file=plain_buffer, no_color=True, width=140)
    render_full_demo(plain_console)
    plain_path = demo_dir / "demo_output.txt"
    plain_path.write_text(plain_buffer.getvalue())
    print(f"Saved plain text output to {plain_path}")


if __name__ == "__main__":
    main()
