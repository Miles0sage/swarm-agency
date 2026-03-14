#!/usr/bin/env python3
"""Generate a static terminal demo of swarm-agency.

Uses the real "startup-pivot" demo scenario -- no API key needed.

Outputs:
  demo/demo_output.txt      - plain text (for copy-paste)
  demo/demo_output_ansi.txt - ANSI colored (for terminal replay)
"""

import sys
from io import StringIO
from pathlib import Path

# Add parent dir so we can import swarm_agency
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich import box

from swarm_agency.demos import DEMO_SCENARIOS


# ── Load real scenario ────────────────────────────────────────────────

SCENARIO = DEMO_SCENARIOS["startup-pivot"]
QUESTION = SCENARIO["question"]
CONTEXT = SCENARIO["context"]
DEPARTMENT = SCENARIO["department"]
DECISION = SCENARIO["decision"]
COMMAND = f'swarm-agency --demo startup-pivot'

# Model assignments per agent (from agents/ persona files)
AGENT_MODELS = {
    "Visionary": "glm-4.7",
    "DevilsAdvocate": "kimi-k2.5",
    "GrowthHacker": "MiniMax-M2.5",
    "NumbersCruncher": "qwen3-coder-plus",
    "Pragmatist": "qwen3.5-plus",
}

MODEL_COLORS = {
    "glm-4.7": "bright_magenta",
    "kimi-k2.5": "bright_cyan",
    "MiniMax-M2.5": "bright_yellow",
    "qwen3-coder-plus": "bright_green",
    "qwen3.5-plus": "bright_blue",
}


# ── Render Functions ──────────────────────────────────────────────────

def render_header(console: Console) -> None:
    console.print()
    header = Text()
    header.append("  $ ", style="bold green")
    header.append(COMMAND, style="bold white")
    console.print(Panel(header, border_style="dim", padding=(0, 1)))
    console.print()


def render_question_panel(console: Console) -> None:
    console.print(Panel(
        Align.center(Text(QUESTION, style="bold white on blue", justify="center")),
        title="[bold cyan]QUESTION",
        subtitle=f"[dim]Department: {DEPARTMENT} | {len(DECISION.votes)} agents | 5 models[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print(f"[dim]Context: {CONTEXT}[/]")
    console.print()


def render_deliberation(console: Console) -> None:
    console.print(Rule("[bold yellow]Agent Deliberation", style="yellow"))
    console.print()

    for vote in DECISION.votes:
        model = AGENT_MODELS.get(vote.agent_name, "unknown")
        model_color = MODEL_COLORS.get(model, "white")

        pos_style = {
            "APPROVE": "[bold green]APPROVE[/]",
            "REJECT": "[bold red]REJECT[/]",
            "NEUTRAL": "[bold yellow]NEUTRAL[/]",
        }.get(vote.position, f"[bold]{vote.position}[/]")

        panel = Panel(
            f"[dim]{vote.reasoning}[/dim]\n\n"
            f"  Position: {pos_style}  |  "
            f"Confidence: [bold]{vote.confidence:.0%}[/bold]  |  "
            f"Model: [{model_color}]{model}[/{model_color}]",
            title=f"[bold]{vote.agent_name}[/bold]",
            border_style="dim",
            padding=(0, 2),
        )
        console.print(panel)

    console.print()


def render_vote_table(console: Console) -> None:
    console.print(Rule("[bold]Vote Summary", style="white"))
    console.print()

    table = Table(
        box=box.HEAVY_HEAD,
        show_lines=True,
        border_style="bright_blue",
        header_style="bold bright_white on dark_blue",
        pad_edge=True,
        padding=(0, 1),
    )
    table.add_column("Agent", style="bold cyan")
    table.add_column("Model", no_wrap=True)
    table.add_column("Position", justify="center")
    table.add_column("Confidence", justify="center")

    for vote in DECISION.votes:
        model = AGENT_MODELS.get(vote.agent_name, "unknown")
        model_color = MODEL_COLORS.get(model, "white")

        pos_style = {
            "APPROVE": "[bold green]APPROVE[/]",
            "REJECT": "[bold red]REJECT[/]",
            "NEUTRAL": "[bold yellow]NEUTRAL[/]",
        }.get(vote.position, f"[bold]{vote.position}[/]")

        conf = vote.confidence
        filled = int(conf * 10)
        empty = 10 - filled
        bar_color = "green" if conf >= 0.7 else "yellow" if conf >= 0.5 else "red"
        conf_bar = f"[{bar_color}]{'█' * filled}{'░' * empty}[/{bar_color}] {conf:.0%}"

        table.add_row(
            vote.agent_name,
            f"[{model_color}]{model}[/{model_color}]",
            pos_style,
            conf_bar,
        )

    console.print(Align.center(table))
    console.print()


def render_tally(console: Console) -> None:
    counts = {}
    for vote in DECISION.votes:
        counts[vote.position] = counts.get(vote.position, 0) + 1

    approve = counts.get("APPROVE", 0)
    reject = counts.get("REJECT", 0)
    neutral = counts.get("NEUTRAL", 0)

    tally_text = Text(justify="center")
    tally_text.append(f"  APPROVE: {approve}  ", style="bold white on green")
    tally_text.append("  ")
    tally_text.append(f"  REJECT: {reject}  ", style="bold white on red")
    tally_text.append("  ")
    tally_text.append(f"  NEUTRAL: {neutral}  ", style="bold white on dark_orange3")

    console.print(Align.center(tally_text))
    console.print()


def render_decision_panel(console: Console) -> None:
    pos_color = "green" if DECISION.position == "APPROVE" else "red" if DECISION.position == "REJECT" else "yellow"
    outcome_color = {"CONSENSUS": "green", "MAJORITY": "yellow", "SPLIT": "red"}.get(DECISION.outcome, "white")

    decision_text = Text()
    decision_text.append(f"{DECISION.outcome}: ", style=f"bold {outcome_color}")
    decision_text.append(DECISION.position, style=f"bold {pos_color}")

    console.print(Panel(
        Align.center(decision_text),
        title="[bold white]AGENCY DECISION[/bold white]",
        border_style=pos_color,
        padding=(1, 4),
    ))
    console.print()


def render_summary(console: Console) -> None:
    console.print(Panel(
        f"[dim]{DECISION.summary}[/dim]",
        title="[bold]Summary",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    if DECISION.dissenting_views:
        console.print("[bold red]Dissenting Views:[/]")
        for view in DECISION.dissenting_views:
            console.print(f"  [dim red]>[/] {view}")
        console.print()

    models_used = ", ".join(AGENT_MODELS.get(v.agent_name, "?") for v in DECISION.votes)
    console.print(
        f"[dim]Confidence: {DECISION.confidence:.0%} | "
        f"Duration: {DECISION.duration_seconds}s | "
        f"Models: {models_used}[/dim]"
    )
    console.print()


def render_memory_section(console: Console) -> None:
    """Render the Decision Memory feature showcase."""
    console.print(Rule("[bold magenta]Decision Memory", style="magenta"))
    console.print()

    # Simulated "stored" confirmation
    console.print(
        "[dim green]Decision stored to memory [dim](~/.swarm-agency/decisions.db)[/dim][/]"
    )
    console.print()

    # Show the --history command
    history_header = Text()
    history_header.append("  $ ", style="bold green")
    history_header.append("swarm-agency --history", style="bold white")
    console.print(Panel(history_header, border_style="dim", padding=(0, 1)))
    console.print()

    # History table with realistic past decisions + our current one
    history_table = Table(
        title="[bold]Decision History[/bold]",
        box=box.HEAVY_HEAD,
        border_style="bright_magenta",
        header_style="bold bright_white on dark_magenta",
        pad_edge=True,
        padding=(0, 1),
        show_lines=True,
    )
    history_table.add_column("ID", style="dim", width=12)
    history_table.add_column("Question", max_width=30)
    history_table.add_column("Dept", style="yellow", width=10)
    history_table.add_column("Outcome", width=10)
    history_table.add_column("Position", style="bold", width=8)
    history_table.add_column("Correct?", width=8)

    # Current decision (just stored)
    history_table.add_row(
        "demo-001",
        "Should we pivot from B2C to B2B?",
        "Strategy",
        "[yellow]MAJORITY[/]",
        "[green]APPROVE[/]",
        "[dim]?[/dim]",
    )
    # Past decisions from memory
    history_table.add_row(
        "test-mem-001",
        "Acquire struggling competitor\nwith 50k users?",
        "Strategy",
        "[yellow]MAJORITY[/]",
        "[red]NO[/]",
        "[green]yes[/]",
    )
    history_table.add_row(
        "test-mem-002",
        "Acquire competitor with key\npatents for $1.5M?",
        "Strategy",
        "[yellow]MAJORITY[/]",
        "[green]YES[/]",
        "[dim]?[/dim]",
    )
    history_table.add_row(
        "test-mem-003",
        "Counter-offer lead engineer\nwith 40% raise + equity?",
        "Engineering",
        "[yellow]MAJORITY[/]",
        "[green]YES[/]",
        "[dim]?[/dim]",
    )

    console.print(Align.center(history_table))
    console.print()

    # Show feedback command
    feedback_header = Text()
    feedback_header.append("  $ ", style="bold green")
    feedback_header.append("swarm-agency --feedback demo-001 yes", style="bold white")
    console.print(Panel(feedback_header, border_style="dim", padding=(0, 1)))
    console.print(
        "[green]Feedback recorded for demo-001: correct[/]"
    )
    console.print()

    # Show memory-aware deliberation hint
    console.print(Panel(
        "[dim]When [bold]--memory[/bold] is enabled, agents see prior decisions on similar "
        "topics\nand adjust confidence based on their track record. Past outcomes\n"
        "improve future debates — institutional memory that compounds.[/dim]",
        title="[bold magenta]How Decision Memory Works[/]",
        border_style="magenta",
        padding=(0, 2),
    ))
    console.print()


def render_full_demo(console: Console) -> None:
    render_header(console)
    render_question_panel(console)
    render_deliberation(console)
    render_vote_table(console)
    render_tally(console)
    render_decision_panel(console)
    render_summary(console)
    render_memory_section(console)


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    demo_dir = Path(__file__).parent

    # 1. Render to terminal (live)
    live_console = Console(force_terminal=True)
    render_full_demo(live_console)

    # 2. Save ANSI output (80 cols for SVG compatibility)
    ansi_buffer = StringIO()
    ansi_console = Console(file=ansi_buffer, force_terminal=True, width=80)
    render_full_demo(ansi_console)
    ansi_path = demo_dir / "demo_output_ansi.txt"
    ansi_path.write_text(ansi_buffer.getvalue())
    print(f"\nSaved ANSI output to {ansi_path}")

    # 3. Save plain text output
    plain_buffer = StringIO()
    plain_console = Console(file=plain_buffer, no_color=True, width=80)
    render_full_demo(plain_console)
    plain_path = demo_dir / "demo_output.txt"
    plain_path.write_text(plain_buffer.getvalue())
    print(f"Saved plain text output to {plain_path}")


if __name__ == "__main__":
    main()
