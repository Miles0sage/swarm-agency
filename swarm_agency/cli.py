"""CLI interface for swarm-agency.

A polished Rich-powered terminal UI showing agents debating in real-time.
Supports both one-shot questions and interactive chat mode.
"""

import argparse
import asyncio
import json
import os
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


# ── Transcript save/replay ────────────────────────────────────────────

LAST_DEBATE_FILE = os.path.expanduser("~/.swarm-agency/last_debate.json")


def _save_last_debate(question, context, decision, mode_label):
    """Save the last debate for --last replay."""
    import os
    from pathlib import Path
    Path(LAST_DEBATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    data = {
        "question": question,
        "context": context,
        "mode_label": mode_label,
        "decision": decision.to_dict(),
    }
    with open(LAST_DEBATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _show_last_debate(json_mode=False):
    """Replay the last debate's full transcript."""
    if not os.path.exists(LAST_DEBATE_FILE):
        print("No previous debate found. Run a debate first.")
        return

    with open(LAST_DEBATE_FILE) as f:
        data = json.load(f)

    from .types import AgentVote, Decision
    d = data["decision"]
    decision = Decision(
        request_id=d["request_id"],
        department=d["department"],
        outcome=d["outcome"],
        position=d["position"],
        confidence=d["confidence"],
        votes=[AgentVote(**v) for v in d["votes"]],
        summary=d["summary"],
        dissenting_views=d.get("dissenting_views", []),
        duration_seconds=d.get("duration_seconds", 0),
    )

    if json_mode:
        print(json.dumps(d, indent=2))
        return

    # Show verdict first
    from .verdict import decision_to_verdict, format_verdict_rich, format_verdict_text
    verdict = decision_to_verdict(decision)
    try:
        format_verdict_rich(verdict)
    except ImportError:
        print(format_verdict_text(verdict))

    # Then full debate
    try:
        from rich.console import Console
        Console().print("\n[dim]──── Full Agent Deliberation ────[/]\n")
    except ImportError:
        print("\n---- Full Agent Deliberation ----\n")

    try:
        _render_rich(data["question"], data["context"], decision, data["mode_label"])
    except ImportError:
        _render_plain(data["question"], data["context"], decision)


# ── Live debate with progress ────────────────────────────────────────

def _run_live_with_progress(question, context, department, api_key, base_url, memory, provider=None, quiet=False, rounds=1, stream=False, tools=False):
    """Run a live debate with Rich progress display."""
    provider = provider or "dashscope"
    families = "7" if provider == "openrouter" else "5"

    try:
        if quiet:
            raise ImportError("skip Rich for JSON output")

        from rich.console import Console
        from rich.text import Text
        from rich.panel import Panel

        console = Console()
        console.print()
        console.print(Panel(
            Text(question, style="bold white"),
            title="[bold cyan]DEBATING[/]",
            subtitle=f"[dim]Agents deliberating across {families} model families ({provider})...[/]",
            border_style="cyan",
            padding=(1, 3),
        ))

        with console.status(
            "[bold cyan]Agents are deliberating...[/]",
            spinner="dots",
        ):
            agency = Agency(
                name="SwarmAgency",
                api_key=api_key,
                base_url=base_url,
                memory_enabled=memory,
                provider=provider,
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
        agency = Agency(
            name="SwarmAgency",
            api_key=api_key,
            base_url=base_url,
            memory_enabled=memory,
            provider=provider,
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

        if not quiet:
            print("\nAgents deliberating...")
        decision = asyncio.run(agency.decide(request))
        return decision


# ── Main ──────────────────────────────────────────────────────────────

def _load_config_env():
    """Load API key from ~/.swarm-agency.env if it exists."""
    config_file = os.path.expanduser("~/.swarm-agency.env")
    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key, value = key.strip(), value.strip()
                        if key and value and key not in os.environ:
                            os.environ[key] = value
        except OSError:
            pass


def main():
    # Load config before anything else
    _load_config_env()

    # Check for subcommands first (init, chat)
    if len(sys.argv) > 1 and sys.argv[1] in ("init", "setup"):
        from .setup import run_setup
        run_setup()
        return

    if len(sys.argv) > 1 and sys.argv[1] in ("serve", "server", "api"):
        import uvicorn
        port = 8000
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                pass
        print(f"\n  Starting Swarm Agency API server on http://0.0.0.0:{port}")
        print(f"  Open http://localhost:{port} for the web UI")
        print(f"  API docs: http://localhost:{port}/docs\n")
        uvicorn.run("swarm_agency.server:app", host="0.0.0.0", port=port, reload=False)
        return

    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        # Parse chat-specific args
        chat_parser = argparse.ArgumentParser(prog="swarm-agency chat")
        chat_parser.add_argument("--api-key", help="API key")
        chat_parser.add_argument("--base-url", help="API base URL override")
        chat_parser.add_argument("--memory", action="store_true", help="Enable decision memory")
        chat_parser.add_argument(
            "--provider", "-p",
            choices=["dashscope", "openrouter"],
            help="Model provider (default: from settings or dashscope)",
        )
        chat_parser.add_argument(
            "--department", "-d",
            choices=DEPARTMENTS,
            help="Start focused on a department",
        )
        chat_args = chat_parser.parse_args(sys.argv[2:])

        from .chat import run_chat
        run_chat(
            api_key=chat_args.api_key,
            base_url=chat_args.base_url,
            memory=chat_args.memory,
            department=chat_args.department,
            provider=chat_args.provider,
        )
        return

    parser = argparse.ArgumentParser(
        prog="swarm-agency",
        description="43 AI agents debate your business decisions across 5 model families.",
        epilog="Commands:\n"
               "  swarm-agency init                          Setup API key\n"
               "  swarm-agency chat                          Interactive mode\n"
               "\n"
               "One-shot:\n"
               "  swarm-agency \"Should we raise a Series A?\"\n"
               "  swarm-agency \"Open-source our SDK?\" -d Engineering\n"
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
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show full agent deliberation (default: clean verdict only)",
    )
    parser.add_argument("--api-key", help="API key (or set env var for your provider)")
    parser.add_argument("--base-url", help="API base URL override")
    parser.add_argument(
        "--provider", "-p",
        choices=["dashscope", "openrouter"],
        default="dashscope",
        help="Model provider: dashscope (default) or openrouter",
    )
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
        "--last", action="store_true",
        help="Replay the last debate with full agent transcript",
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
    parser.add_argument(
        "--dual", action="store_true",
        help="Run same question through Chinese AND Western AI models, compare results",
    )
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=1,
        metavar="N",
        help="Multi-round debate: agents revise after seeing others' votes (default: 1)",
    )
    parser.add_argument(
        "--stream", action="store_true",
        help="Stream agent votes as they arrive",
    )
    parser.add_argument(
        "--tools", action="store_true",
        help="Enable tool-calling (agents can use calculator, ROI, etc.)",
    )
    parser.add_argument(
        "--template",
        choices=["hire", "pricing", "launch", "vendor", "pivot"],
        help="Use a decision template instead of a raw question.",
    )
    parser.add_argument(
        "--candidate", help="Candidate name (for hire template)",
    )
    parser.add_argument(
        "--role", help="Role (for hire template)",
    )
    parser.add_argument(
        "--product", help="Product name (for launch/pricing templates)",
    )
    parser.add_argument(
        "--market", help="Target market (for launch template)",
    )
    parser.add_argument(
        "--current-price", help="Current price (for pricing template)",
    )
    parser.add_argument(
        "--new-price", help="New price (for pricing template)",
    )
    parser.add_argument(
        "--vendor-name", help="Vendor name (for vendor template)",
    )
    parser.add_argument(
        "--service", help="Service type (for vendor template)",
    )
    parser.add_argument(
        "--current-direction", help="Current direction (for pivot template)",
    )
    parser.add_argument(
        "--new-direction", help="New direction (for pivot template)",
    )

    args = parser.parse_args()

    # ── Agents list ──
    if args.agents:
        _list_agents()
        return

    # ── Last debate replay ──
    if args.last:
        _show_last_debate(json_mode=args.json)
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

    # ── Template mode ──
    if args.template:
        from .templates import create_request
        template_kwargs = {}
        if args.template == "hire":
            if args.candidate: template_kwargs["candidate"] = args.candidate
            if args.role: template_kwargs["role"] = args.role
        elif args.template == "pricing":
            if args.product: template_kwargs["product"] = args.product
            if args.current_price: template_kwargs["current_price"] = args.current_price
            if args.new_price: template_kwargs["new_price"] = args.new_price
        elif args.template == "launch":
            if args.product: template_kwargs["product"] = args.product
            if args.market: template_kwargs["market"] = args.market
        elif args.template == "vendor":
            if args.vendor_name: template_kwargs["vendor"] = args.vendor_name
            if args.service: template_kwargs["service"] = args.service
        elif args.template == "pivot":
            if args.current_direction: template_kwargs["current_direction"] = args.current_direction
            if args.new_direction: template_kwargs["new_direction"] = args.new_direction

        try:
            tmpl_request = create_request(args.template, context=args.context, **template_kwargs)
        except ValueError as e:
            print(f"Template error: {e}")
            sys.exit(1)

        question = tmpl_request.question
        context = tmpl_request.context
        decision = _run_live_with_progress(
            question=question,
            context=context,
            department=args.department,
            api_key=args.api_key,
            base_url=args.base_url,
            memory=args.memory,
            provider=args.provider,
            quiet=args.json,
        )
        mode_label = f"Template: {args.template}"

        if args.json:
            print(json.dumps(decision.to_dict(), indent=2))
            return
        try:
            _render_rich(question, context or "", decision, mode_label)
        except ImportError:
            _render_plain(question, context or "", decision)
        return

    # ── Demo mode ──
    if args.demo is not None:
        if args.demo == "__list__":
            _list_demos()
            return
        question, context, decision = _run_demo(args.demo)
        mode_label = "Demo"
    else:
        # ── No question? Launch chat mode ──
        if not args.question:
            from .chat import run_chat
            run_chat(
                api_key=args.api_key,
                base_url=args.base_url,
                memory=args.memory,
                department=args.department,
            )
            return

        question = args.question
        context = args.context

        # Dual debate mode
        if args.dual:
            from .dual_debate import dual_debate, format_dual_result_rich, format_dual_result_text, format_dual_result_dict

            try:
                from rich.console import Console
                console = Console()
                console.print()
                with console.status("[bold cyan]Running dual debate (Chinese + Western models)...[/]", spinner="dots"):
                    result = asyncio.run(dual_debate(
                        question, context, args.department,
                        provider_a="dashscope", provider_b="openrouter",
                    ))
            except ImportError:
                print("\n  Running dual debate...")
                result = asyncio.run(dual_debate(
                    question, context, args.department,
                    provider_a="dashscope", provider_b="openrouter",
                ))

            if args.json:
                print(json.dumps(format_dual_result_dict(result), indent=2))
            else:
                try:
                    format_dual_result_rich(result)
                except ImportError:
                    print(format_dual_result_text(result))
            return

        decision = _run_live_with_progress(
            question=question,
            context=context,
            department=args.department,
            api_key=args.api_key,
            base_url=args.base_url,
            memory=args.memory,
            provider=args.provider,
            quiet=args.json,
            rounds=args.rounds,
            stream=args.stream,
            tools=args.tools,
        )
        mode_label = "Live"
        if args.rounds > 1:
            mode_label = f"Live ({args.rounds} rounds)"

    # ── Output ──
    if args.json:
        print(json.dumps(decision.to_dict(), indent=2))
        return

    # Save transcript for --last replay
    _save_last_debate(question, context or "", decision, mode_label)

    # Always show the verdict first
    from .verdict import decision_to_verdict, format_verdict_rich, format_verdict_text
    verdict = decision_to_verdict(decision)
    try:
        format_verdict_rich(verdict)
    except ImportError:
        print(format_verdict_text(verdict))

    if args.verbose:
        # Then show the full debate below
        try:
            from rich.console import Console
            Console().print("\n[dim]──── Full Agent Deliberation ────[/]\n")
        except ImportError:
            print("\n---- Full Agent Deliberation ----\n")
        try:
            _render_rich(question, context or "", decision, mode_label)
        except ImportError:
            _render_plain(question, context or "", decision)
    else:
        # Hint to see full debate
        try:
            from rich.console import Console
            Console().print("  [dim]See full debate:[/] [bold]swarm-agency --last[/]\n")
        except ImportError:
            print("  See full debate: swarm-agency --last\n")


if __name__ == "__main__":
    main()
