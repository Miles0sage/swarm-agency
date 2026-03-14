"""Interactive chat mode for swarm-agency.

A Claude Code-style REPL where you can have multi-turn debates
with 43 AI agents. Type questions, get debates, ask follow-ups.
"""

import asyncio
import json as json_mod
import os
import sys
import time
import uuid

from .types import AgencyRequest, Decision
from .agency import Agency
from .presets import create_full_agency_departments, DEPARTMENT_NAMES

# ── Persistent settings ──────────────────────────────────────────────

SETTINGS_FILE = os.path.expanduser("~/.swarm-agency.json")


def _load_settings():
    """Load persistent settings from ~/.swarm-agency.json."""
    defaults = {"memory": False, "department": None, "context": None}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                saved = json_mod.load(f)
            defaults.update(saved)
        except (OSError, json_mod.JSONDecodeError):
            pass
    return defaults


def _save_settings(state):
    """Save current settings to ~/.swarm-agency.json."""
    to_save = {
        "memory": state.get("memory", False),
        "department": state.get("department"),
        "context": state.get("context"),
        "provider": state.get("provider", "dashscope"),
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json_mod.dump(to_save, f, indent=2)
    except OSError:
        pass


# ── Constants ─────────────────────────────────────────────────────────

SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/last": "Show full transcript of the last debate",
    "/verbose": "Toggle verbose mode (show full debate after each question)",
    "/agents": "List all 43 agents",
    "/departments": "List all 10 departments",
    "/dept <name>": "Focus on a specific department (e.g. /dept Finance)",
    "/dept all": "Reset to consult all departments",
    "/memory on": "Enable decision memory",
    "/memory off": "Disable decision memory",
    "/history": "Show past decisions (requires memory)",
    "/context <text>": "Set persistent context for all questions",
    "/context clear": "Clear persistent context",
    "/json": "Toggle JSON output mode",
    "/provider <name>": "Switch provider (dashscope or openrouter)",
    "/dual": "Toggle dual debate mode (Chinese + Western models)",
    "/demo <name>": "Run a demo scenario",
    "/clear": "Clear the screen",
    "/exit": "Exit the chat",
}

MULTILINE_HINT = 'Tip: End a line with \\ to continue, or wrap in """ for multiline.'

WELCOME_ART = r"""
 ╔═══════════════════════════════════════════════════════════╗
 ║                                                           ║
 ║   ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗          ║
 ║   ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║          ║
 ║   ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║          ║
 ║   ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║          ║
 ║   ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║          ║
 ║   ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝          ║
 ║                   A G E N C Y                             ║
 ║                                                           ║
 ║   43 agents · 10 departments · 5 model families           ║
 ║                                                           ║
 ╚═══════════════════════════════════════════════════════════╝
"""


def _has_rich():
    try:
        import rich
        return True
    except ImportError:
        return False


def _print_welcome(console=None):
    """Print the welcome banner."""
    if console:
        from rich.panel import Panel
        from rich.text import Text

        console.print()
        console.print(Panel(
            Text.from_markup(
                "[bold cyan]SWARM AGENCY[/] — Interactive Mode\n\n"
                "[dim]43 agents · 10 departments · 5 model families[/]\n\n"
                "Type a question and press Enter to start a debate.\n"
                "Type [bold]/help[/] for commands, [bold]/exit[/] to quit."
            ),
            border_style="cyan",
            padding=(1, 3),
        ))
        console.print()
    else:
        print("\n  SWARM AGENCY — Interactive Mode")
        print("  43 agents · 10 departments · 5 model families\n")
        print("  Type a question and press Enter to start a debate.")
        print("  Type /help for commands, /exit to quit.\n")


def _print_help(console=None):
    """Print available commands."""
    if console:
        from rich.table import Table
        from rich import box

        table = Table(
            title="Commands",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold",
        )
        table.add_column("Command", style="cyan bold", width=22)
        table.add_column("Description")
        for cmd, desc in SLASH_COMMANDS.items():
            table.add_row(cmd, desc)
        console.print(table)
        console.print(f"  [dim]{MULTILINE_HINT}[/]")
        console.print()
    else:
        print("\n  Commands:")
        for cmd, desc in SLASH_COMMANDS.items():
            print(f"    {cmd:22s} {desc}")
        print(f"\n  {MULTILINE_HINT}")
        print()


def _print_status(department, memory, context, provider=None, console=None):
    """Print current session status."""
    dept_str = department or "All (10)"
    mem_str = "on" if memory else "off"
    ctx_str = context[:50] + "..." if context and len(context) > 50 else (context or "none")
    prov_str = provider or "dashscope"
    families = "7" if prov_str == "openrouter" else "5"

    if console:
        console.print(
            f"  [dim]Provider:[/] [magenta]{prov_str}[/] ({families} families)  "
            f"[dim]Dept:[/] [cyan]{dept_str}[/]  "
            f"[dim]Memory:[/] [{'green' if memory else 'red'}]{mem_str}[/]  "
            f"[dim]Context:[/] [yellow]{ctx_str}[/]"
        )
    else:
        print(f"  Provider: {prov_str} ({families} families)  Dept: {dept_str}  Memory: {mem_str}  Context: {ctx_str}")


def _prompt_text(department):
    """Generate the prompt string."""
    dept_label = department or "all"
    return f"swarm [{dept_label}]> "


def _render_decision_rich(question, context, decision, console, elapsed):
    """Render decision using the shared Rich renderer."""
    from .cli import _render_rich
    _render_rich(question, context or "", decision, mode_label="Chat")


def _render_decision_plain(question, context, decision):
    """Render decision in plain text."""
    from .cli import _render_plain
    _render_plain(question, context or "", decision)


def _run_debate(agency, question, context, department, quiet=False):
    """Run a debate and return the decision."""
    request = AgencyRequest(
        request_id=f"chat-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context,
        department=department,
    )

    start = time.time()
    decision = asyncio.run(agency.decide(request))
    elapsed = time.time() - start

    if decision.duration_seconds == 0:
        decision.duration_seconds = round(elapsed, 1)

    return decision, elapsed


KNOWN_COMMANDS = [
    "/help", "/exit", "/quit", "/q", "/clear", "/agents", "/departments",
    "/dept", "/memory", "/history", "/context", "/json", "/demo", "/provider",
    "/last", "/verbose", "/dual",
]

# Words that trigger commands even without the / prefix
BARE_COMMANDS = {
    "help": "/help",
    "exit": "/exit",
    "quit": "/exit",
    "agents": "/agents",
    "departments": "/departments",
    "history": "/history",
    "clear": "/clear",
}


def _fuzzy_match_command(cmd):
    """Find the closest matching command for typos."""
    cmd = cmd.lower()
    # Exact match
    if cmd in KNOWN_COMMANDS:
        return cmd

    # Prefix match (e.g. /mem → /memory)
    prefix_matches = [c for c in KNOWN_COMMANDS if c.startswith(cmd)]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    # Edit distance 1-2 (simple typo tolerance)
    best = None
    best_dist = 3  # max distance to tolerate
    for known in KNOWN_COMMANDS:
        dist = _edit_distance(cmd, known)
        if dist < best_dist:
            best_dist = dist
            best = known
    return best


def _edit_distance(a, b):
    """Simple Levenshtein distance."""
    if len(a) > len(b):
        a, b = b, a
    dists = range(len(a) + 1)
    for j, cb in enumerate(b):
        new_dists = [j + 1]
        for i, ca in enumerate(a):
            if ca == cb:
                new_dists.append(dists[i])
            else:
                new_dists.append(1 + min(dists[i], dists[i + 1], new_dists[-1]))
        dists = new_dists
    return dists[-1]


def _handle_slash_command(cmd, args_str, state, console=None):
    """Handle a slash command. Returns True if handled, False otherwise."""
    cmd = cmd.lower()

    # Fuzzy match typos
    matched = _fuzzy_match_command(cmd)
    if matched and matched != cmd:
        if console:
            console.print(f"  [dim](matched: {matched})[/]")
        else:
            print(f"  (matched: {matched})")
        cmd = matched

    if cmd == "/help":
        _print_help(console)
        return True

    if cmd == "/exit" or cmd == "/quit" or cmd == "/q":
        if console:
            console.print("\n  [dim]Goodbye! 👋[/]\n")
        else:
            print("\n  Goodbye!\n")
        sys.exit(0)

    if cmd == "/clear":
        os.system("clear" if os.name != "nt" else "cls")
        return True

    if cmd == "/agents":
        from .cli import _list_agents
        _list_agents()
        return True

    if cmd == "/departments":
        if console:
            from rich.table import Table
            from rich import box
            table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
            table.add_column("#", style="dim", width=3)
            table.add_column("Department", style="cyan bold")
            table.add_column("Agents", style="yellow", justify="right")
            depts = create_full_agency_departments()
            for i, dept in enumerate(depts, 1):
                table.add_row(str(i), dept.name, str(len(dept.agents)))
            console.print(table)
        else:
            for name in DEPARTMENT_NAMES:
                print(f"  {name}")
        return True

    if cmd == "/dept":
        if not args_str or args_str.lower() == "all":
            state["department"] = None
            msg = "Consulting all departments"
        else:
            # Find matching department (case-insensitive)
            match = None
            for name in DEPARTMENT_NAMES:
                if name.lower() == args_str.lower():
                    match = name
                    break
                if name.lower().startswith(args_str.lower()):
                    match = name
                    break
            if match:
                state["department"] = match
                msg = f"Focused on {match} department"
            else:
                msg = f"Unknown department: {args_str}. Use /departments to list."
                if console:
                    console.print(f"  [red]{msg}[/]")
                else:
                    print(f"  {msg}")
                return True

        if console:
            console.print(f"  [green]{msg}[/]")
        else:
            print(f"  {msg}")
        return True

    if cmd == "/memory":
        if args_str and args_str.lower() == "on":
            state["memory"] = True
            state["agency"] = _rebuild_agency(state)
            msg = "Memory enabled"
        elif args_str and args_str.lower() == "off":
            state["memory"] = False
            state["agency"] = _rebuild_agency(state)
            msg = "Memory disabled"
        else:
            # No args → toggle
            state["memory"] = not state["memory"]
            state["agency"] = _rebuild_agency(state)
            msg = f"Memory {'enabled' if state['memory'] else 'disabled'}"

        if console:
            console.print(f"  [green]{msg}[/]")
        else:
            print(f"  {msg}")
        return True

    if cmd == "/provider":
        valid_providers = ["dashscope", "openrouter"]
        if args_str and args_str.lower() in valid_providers:
            new_provider = args_str.lower()
            state["provider"] = new_provider
            # Auto-resolve API key for new provider
            if new_provider == "openrouter":
                key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            else:
                key = os.environ.get("ALIBABA_CODING_API_KEY", "").strip()
            if key:
                state["api_key"] = key
            state["agency"] = _rebuild_agency(state)
            families = "7" if new_provider == "openrouter" else "5"
            msg = f"Switched to {new_provider} ({families} model families)"
        elif not args_str:
            # Toggle between providers
            current = state.get("provider", "dashscope")
            new_provider = "openrouter" if current == "dashscope" else "dashscope"
            state["provider"] = new_provider
            if new_provider == "openrouter":
                key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            else:
                key = os.environ.get("ALIBABA_CODING_API_KEY", "").strip()
            if key:
                state["api_key"] = key
            state["agency"] = _rebuild_agency(state)
            families = "7" if new_provider == "openrouter" else "5"
            msg = f"Switched to {new_provider} ({families} model families)"
        else:
            msg = f"Unknown provider: {args_str}. Use: dashscope or openrouter"

        if console:
            console.print(f"  [green]{msg}[/]")
        else:
            print(f"  {msg}")
        return True

    if cmd == "/history":
        if not state["memory"]:
            msg = "Memory is off. Use /memory on first."
            if console:
                console.print(f"  [yellow]{msg}[/]")
            else:
                print(f"  {msg}")
            return True
        agency = state["agency"]
        records = agency.history(limit=10)
        if not records:
            msg = "No decisions in memory yet."
            if console:
                console.print(f"  [dim]{msg}[/]")
            else:
                print(f"  {msg}")
            return True
        if console:
            from rich.table import Table
            from rich import box
            table = Table(title="Recent Decisions", box=box.SIMPLE)
            table.add_column("ID", style="dim", width=14)
            table.add_column("Question", max_width=40)
            table.add_column("Outcome")
            table.add_column("Position", style="bold")
            for r in records:
                color = {"CONSENSUS": "green", "MAJORITY": "yellow", "SPLIT": "red"}.get(r.outcome, "white")
                table.add_row(r.request_id[:14], r.question[:40], f"[{color}]{r.outcome}[/]", r.position)
            console.print(table)
        else:
            for r in records:
                print(f"  {r.request_id[:14]}  {r.outcome:10s}  {r.position:8s}  {r.question[:50]}")
        return True

    if cmd == "/context":
        if not args_str or args_str.lower() == "clear":
            state["context"] = None
            msg = "Context cleared"
        else:
            state["context"] = args_str
            msg = f"Context set: {args_str[:60]}{'...' if len(args_str) > 60 else ''}"

        if console:
            console.print(f"  [green]{msg}[/]")
        else:
            print(f"  {msg}")
        return True

    if cmd == "/json":
        state["json_mode"] = not state.get("json_mode", False)
        mode = "on" if state["json_mode"] else "off"
        if console:
            console.print(f"  [green]JSON output: {mode}[/]")
        else:
            print(f"  JSON output: {mode}")
        return True

    if cmd == "/demo":
        from .demos import DEMO_SCENARIOS, DEMO_LIST
        if not args_str:
            from .cli import _list_demos
            _list_demos()
            return True
        if args_str not in DEMO_SCENARIOS:
            if console:
                console.print(f"  [red]Unknown demo: {args_str}. Available: {', '.join(DEMO_LIST)}[/]")
            else:
                print(f"  Unknown demo: {args_str}. Available: {', '.join(DEMO_LIST)}")
            return True
        scenario = DEMO_SCENARIOS[args_str]
        if console:
            _render_decision_rich(
                scenario["question"], scenario["context"],
                scenario["decision"], console, 0,
            )
        else:
            _render_decision_plain(
                scenario["question"], scenario["context"],
                scenario["decision"],
            )
        return True

    if cmd == "/last":
        last_decision = state.get("last_decision")
        last_question = state.get("last_question", "")
        last_context = state.get("last_context", "")
        if not last_decision:
            msg = "No debate yet. Ask a question first."
            if console:
                console.print(f"  [yellow]{msg}[/]")
            else:
                print(f"  {msg}")
            return True

        # Show verdict first
        from .verdict import decision_to_verdict, format_verdict_rich, format_verdict_text
        verdict = decision_to_verdict(last_decision)
        try:
            format_verdict_rich(verdict)
        except ImportError:
            print(format_verdict_text(verdict))

        # Then full debate
        if console:
            console.print("\n[dim]──── Full Agent Deliberation ────[/]\n")
        else:
            print("\n---- Full Agent Deliberation ----\n")

        if console:
            from .cli import _render_rich
            _render_rich(last_question, last_context, last_decision, "Chat")
        else:
            from .cli import _render_plain
            _render_plain(last_question, last_context, last_decision)
        return True

    if cmd == "/verbose":
        state["verbose"] = not state.get("verbose", False)
        mode = "on" if state["verbose"] else "off"
        if console:
            console.print(f"  [green]Verbose mode: {mode}[/] {'(full debate after each question)' if state['verbose'] else '(verdict only)'}")
        else:
            print(f"  Verbose mode: {mode}")
        return True

    if cmd == "/dual":
        state["dual"] = not state.get("dual", False)
        mode = "on" if state["dual"] else "off"
        if console:
            console.print(f"  [green]Dual debate mode: {mode}[/] {'(Chinese + Western models)' if state['dual'] else ''}")
        else:
            print(f"  Dual debate mode: {mode}")
        return True

    return False


def _rebuild_agency(state):
    """Create a new Agency with current state."""
    agency = Agency(
        name="SwarmAgency",
        api_key=state.get("api_key", ""),
        base_url=state.get("base_url"),
        memory_enabled=state.get("memory", False),
        provider=state.get("provider", "dashscope"),
    )
    for dept in create_full_agency_departments():
        agency.add_department(dept)
    return agency


def _check_api_key(provider: str = "dashscope"):
    """Check if API key is configured for the given provider. Return key or None."""
    # Check provider-specific key first
    if provider == "openrouter":
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if key:
            return key
    else:
        key = os.environ.get("ALIBABA_CODING_API_KEY", "").strip()
        if key:
            return key

    # Try both keys as fallback
    for env_var in ("ALIBABA_CODING_API_KEY", "OPENROUTER_API_KEY"):
        key = os.environ.get(env_var, "").strip()
        if key:
            return key

    # Check .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        for env_var in ("ALIBABA_CODING_API_KEY", "OPENROUTER_API_KEY"):
            key = os.environ.get(env_var, "").strip()
            if key:
                return key
    except ImportError:
        pass
    return None


def run_chat(api_key=None, base_url=None, memory=False, department=None, provider=None):
    """Main chat loop."""
    console = None
    if _has_rich():
        from rich.console import Console
        from rich.prompt import Prompt
        console = Console()

    _print_welcome(console)

    # Load persistent settings first so we know the provider
    saved = _load_settings()
    resolved_provider = provider or saved.get("provider", "dashscope")

    # Auto-detect provider from available keys
    if not provider:
        if os.environ.get("OPENROUTER_API_KEY", "").strip() and not os.environ.get("ALIBABA_CODING_API_KEY", "").strip():
            resolved_provider = "openrouter"

    # Check API key for the resolved provider
    resolved_key = api_key or _check_api_key(resolved_provider)
    if not resolved_key:
        provider_name = "OpenRouter" if resolved_provider == "openrouter" else "DashScope"
        env_var = "OPENROUTER_API_KEY" if resolved_provider == "openrouter" else "ALIBABA_CODING_API_KEY"
        if console:
            console.print(
                f"  [yellow]No API key configured.[/]\n"
                f"  Set [bold]{env_var}[/] or run [bold]swarm-agency init[/].\n"
                f"  You can still use [bold]/demo[/] scenarios without a key.\n"
            )
        else:
            print(f"  No API key configured.")
            print(f"  Set {env_var} or run 'swarm-agency init'.")
            print(f"  You can still use /demo scenarios without a key.\n")

    state = {
        "api_key": resolved_key or "",
        "base_url": base_url,
        "memory": memory or saved.get("memory", False),
        "department": department or saved.get("department"),
        "context": saved.get("context"),
        "provider": resolved_provider,
        "json_mode": False,
        "history": [],  # list of (question, decision) tuples
    }
    state["agency"] = _rebuild_agency(state)

    # Print initial status
    _print_status(state["department"], state["memory"], state["context"], state.get("provider"), console)
    if console:
        console.print()

    while True:
        try:
            prompt = _prompt_text(state["department"])
            if console:
                user_input = console.input(f"[bold green]{prompt}[/]").strip()
            else:
                user_input = input(prompt).strip()

            if not user_input:
                continue

            # Multiline: if input ends with \ or starts with """, collect more lines
            if user_input.endswith("\\"):
                lines = [user_input[:-1].rstrip()]
                continuation = "    ... "
                while True:
                    if console:
                        line = console.input(f"[dim]{continuation}[/]").rstrip()
                    else:
                        line = input(continuation).rstrip()
                    if line.endswith("\\"):
                        lines.append(line[:-1].rstrip())
                    else:
                        lines.append(line)
                        break
                user_input = " ".join(lines).strip()
                if not user_input:
                    continue

            elif user_input.startswith('"""'):
                lines = [user_input[3:]]
                continuation = "    ... "
                while True:
                    if console:
                        line = console.input(f"[dim]{continuation}[/]")
                    else:
                        line = input(continuation)
                    if line.rstrip().endswith('"""'):
                        lines.append(line.rstrip()[:-3])
                        break
                    lines.append(line)
                user_input = "\n".join(lines).strip()
                if not user_input:
                    continue

            # Handle slash commands
            if user_input.startswith("/"):
                parts = user_input.split(None, 1)
                cmd = parts[0]
                args_str = parts[1] if len(parts) > 1 else ""
                if _handle_slash_command(cmd, args_str, state, console):
                    _save_settings(state)
                    continue
                # Unknown command
                if console:
                    console.print(f"  [red]Unknown command: {cmd}. Type /help for commands.[/]")
                else:
                    print(f"  Unknown command: {cmd}. Type /help for commands.")
                continue

            # Detect bare commands without / (e.g. "memory on", "help", "exit")
            bare_parts = user_input.lower().split(None, 1)
            bare_word = bare_parts[0]
            bare_args = bare_parts[1] if len(bare_parts) > 1 else ""

            # Check exact bare commands
            if bare_word in BARE_COMMANDS:
                mapped = BARE_COMMANDS[bare_word]
                if console:
                    console.print(f"  [dim](matched: {mapped})[/]")
                else:
                    print(f"  (matched: {mapped})")
                if _handle_slash_command(mapped, bare_args, state, console):
                    _save_settings(state)
                    continue

            # Check "command arg" patterns (e.g. "memory on", "dept finance", "context ...")
            bare_as_slash = f"/{bare_word}"
            if bare_as_slash in KNOWN_COMMANDS:
                if console:
                    console.print(f"  [dim](matched: {bare_as_slash})[/]")
                else:
                    print(f"  (matched: {bare_as_slash})")
                if _handle_slash_command(bare_as_slash, bare_args, state, console):
                    _save_settings(state)
                    continue

            # It's a question — run the debate
            if not state["api_key"]:
                if console:
                    console.print(
                        "  [red]No API key configured.[/] Run [bold]swarm-agency init[/] first,\n"
                        "  or try [bold]/demo startup-pivot[/] to see a pre-computed debate."
                    )
                else:
                    print("  No API key configured. Run 'swarm-agency init' first.")
                    print("  Or try /demo startup-pivot to see a pre-computed debate.")
                continue

            # Prompt for context on each question (Enter to skip)
            if console:
                console.print()
                inline_ctx = console.input(
                    "  [yellow]Context[/] [dim](Enter to skip):[/] "
                ).strip()
            else:
                print()
                inline_ctx = input("  Context (Enter to skip): ").strip()

            # Support multiline context with \ continuation
            if inline_ctx.endswith("\\"):
                ctx_lines = [inline_ctx[:-1].rstrip()]
                continuation = "    ... "
                while True:
                    if console:
                        line = console.input(f"[dim]{continuation}[/]").rstrip()
                    else:
                        line = input(continuation).rstrip()
                    if line.endswith("\\"):
                        ctx_lines.append(line[:-1].rstrip())
                    else:
                        ctx_lines.append(line)
                        break
                inline_ctx = " ".join(ctx_lines).strip()

            # Build full context: persistent + inline + conversation history
            context_parts = []

            # Add persistent context
            if state["context"]:
                context_parts.append(state["context"])

            # Add inline context
            if inline_ctx:
                context_parts.append(inline_ctx)

            # Add conversation history (last 3 decisions for follow-up awareness)
            if state["history"]:
                history_lines = []
                for prev_q, prev_d in state["history"][-3:]:
                    history_lines.append(
                        f"Previous question: \"{prev_q}\" → "
                        f"{prev_d.outcome} {prev_d.position} "
                        f"({prev_d.confidence:.0%} confidence). "
                        f"Summary: {prev_d.summary}"
                    )
                context_parts.append(
                    "Conversation history:\n" + "\n".join(history_lines)
                )

            context = "\n\n".join(context_parts) if context_parts else ""

            # Show thinking indicator
            if console:
                console.print()
                with console.status("[bold cyan]Agents are deliberating...[/]", spinner="dots"):
                    decision, elapsed = _run_debate(
                        state["agency"], user_input, context,
                        state["department"],
                    )
            else:
                print("\n  Agents deliberating...")
                decision, elapsed = _run_debate(
                    state["agency"], user_input, context,
                    state["department"],
                )

            # Store in session history + for /last replay
            state["history"].append((user_input, decision))
            state["last_decision"] = decision
            state["last_question"] = user_input
            display_context_parts = []
            if state["context"]:
                display_context_parts.append(state["context"])
            if inline_ctx:
                display_context_parts.append(inline_ctx)
            display_context = "\n".join(display_context_parts) if display_context_parts else ""
            state["last_context"] = display_context

            # Render
            if state.get("json_mode"):
                import json
                print(json.dumps(decision.to_dict(), indent=2))
            else:
                # Always show verdict first
                from .verdict import decision_to_verdict, format_verdict_rich, format_verdict_text
                verdict = decision_to_verdict(decision)
                try:
                    format_verdict_rich(verdict)
                except ImportError:
                    print(format_verdict_text(verdict))

                # Show full debate if verbose mode
                if state.get("verbose"):
                    if console:
                        console.print("\n[dim]──── Full Agent Deliberation ────[/]\n")
                        _render_decision_rich(user_input, display_context, decision, console, elapsed)
                    else:
                        print("\n---- Full Agent Deliberation ----\n")
                        _render_decision_plain(user_input, display_context, decision)
                else:
                    if console:
                        console.print("  [dim]Full transcript:[/] [bold]/last[/]  [dim]Always show:[/] [bold]/verbose[/]\n")
                    else:
                        print("  Full transcript: /last  |  Always show: /verbose\n")

        except KeyboardInterrupt:
            if console:
                console.print("\n\n  [dim]Interrupted. Type /exit to quit.[/]\n")
            else:
                print("\n\n  Interrupted. Type /exit to quit.\n")
            continue

        except EOFError:
            if console:
                console.print("\n  [dim]Goodbye! 👋[/]\n")
            else:
                print("\n  Goodbye!\n")
            break
