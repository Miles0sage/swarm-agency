"""Interactive setup wizard for swarm-agency.

Guides users through API key configuration with validation.
"""

import os
import sys

CONFIG_FILE = os.path.expanduser("~/.swarm-agency.env")
DASHSCOPE_SIGNUP_URL = "https://dashscope.console.aliyun.com/"
DASHSCOPE_API_URL = "https://coding-intl.dashscope.aliyuncs.com/v1"


def _has_rich():
    try:
        import rich
        return True
    except ImportError:
        return False


def _test_api_key(api_key: str) -> tuple[bool, str]:
    """Test if the API key works by making a lightweight API call."""
    import httpx

    try:
        resp = httpx.post(
            f"{DASHSCOPE_API_URL}/chat/completions",
            json={
                "model": "qwen3-coder-plus",
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 5,
            },
            headers={
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )
        if resp.status_code == 200:
            return True, "API key is valid!"
        elif resp.status_code == 401:
            return False, "Invalid API key (401 Unauthorized)"
        elif resp.status_code == 403:
            return False, "API key doesn't have access (403 Forbidden)"
        else:
            return False, f"Unexpected response: {resp.status_code} {resp.text[:100]}"
    except httpx.TimeoutException:
        return False, "Connection timed out — check your network"
    except Exception as e:
        return False, f"Connection failed: {str(e)[:100]}"


def _save_env_file(api_key: str, base_url: str | None = None):
    """Save API key to ~/.swarm-agency.env."""
    lines = [f"ALIBABA_CODING_API_KEY={api_key}\n"]
    if base_url:
        lines.append(f"ALIBABA_CODING_BASE_URL={base_url}\n")

    with open(CONFIG_FILE, "w") as f:
        f.writelines(lines)
    os.chmod(CONFIG_FILE, 0o600)  # Owner read/write only


def _save_to_shell_profile(api_key: str):
    """Offer to add export to shell profile."""
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        profile = os.path.expanduser("~/.zshrc")
    else:
        profile = os.path.expanduser("~/.bashrc")

    export_line = f'export ALIBABA_CODING_API_KEY="{api_key}"'

    # Check if already in profile
    if os.path.exists(profile):
        with open(profile, "r") as f:
            content = f.read()
        if "ALIBABA_CODING_API_KEY" in content:
            return "already_exists", profile

    return "not_exists", profile, export_line


def run_setup():
    """Interactive setup wizard."""
    console = None
    if _has_rich():
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        console = Console()

    # Header
    if console:
        console.print()
        console.print(Panel(
            Text.from_markup(
                "[bold cyan]SWARM AGENCY SETUP[/]\n\n"
                "This will configure your API key for live debates.\n"
                "You need a [bold]DashScope Coding Plan[/] ($10/mo) from Alibaba Cloud.\n"
                f"Sign up at: [link={DASHSCOPE_SIGNUP_URL}]{DASHSCOPE_SIGNUP_URL}[/]"
            ),
            border_style="cyan",
            padding=(1, 3),
        ))
        console.print()
    else:
        print("\n  SWARM AGENCY SETUP")
        print("  ─────────────────")
        print("  This will configure your API key for live debates.")
        print("  You need a DashScope Coding Plan ($10/mo) from Alibaba Cloud.")
        print(f"  Sign up at: {DASHSCOPE_SIGNUP_URL}\n")

    # Check existing key
    existing = os.environ.get("ALIBABA_CODING_API_KEY", "").strip()
    if existing:
        if console:
            console.print(f"  [green]Found existing key:[/] [dim]{existing[:8]}...{existing[-4:]}[/]")
            answer = console.input("  [bold]Replace it? (y/N):[/] ").strip().lower()
        else:
            print(f"  Found existing key: {existing[:8]}...{existing[-4:]}")
            answer = input("  Replace it? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            if console:
                console.print("  [green]Keeping existing key. You're all set![/]\n")
            else:
                print("  Keeping existing key. You're all set!\n")
            return

    # Get API key
    if console:
        console.print("  [bold]Steps:[/]")
        console.print("  1. Go to [cyan]dashscope.console.aliyun.com[/]")
        console.print("  2. Sign up / log in")
        console.print("  3. Subscribe to the [bold]Coding Plan[/] ($10/mo)")
        console.print("  4. Go to [bold]API Keys[/] → Create New Key")
        console.print("  5. Paste it below\n")
        api_key = console.input("  [bold]API Key:[/] ").strip()
    else:
        print("  Steps:")
        print("  1. Go to dashscope.console.aliyun.com")
        print("  2. Sign up / log in")
        print("  3. Subscribe to the Coding Plan ($10/mo)")
        print("  4. Go to API Keys → Create New Key")
        print("  5. Paste it below\n")
        api_key = input("  API Key: ").strip()

    if not api_key:
        if console:
            console.print("  [red]No key entered. Aborting.[/]\n")
        else:
            print("  No key entered. Aborting.\n")
        sys.exit(1)

    # Validate
    if console:
        console.print()
        with console.status("[bold cyan]Testing API key...[/]", spinner="dots"):
            ok, msg = _test_api_key(api_key)
    else:
        print("  Testing API key...")
        ok, msg = _test_api_key(api_key)

    if ok:
        if console:
            console.print(f"  [bold green]✓ {msg}[/]\n")
        else:
            print(f"  ✓ {msg}\n")
    else:
        if console:
            console.print(f"  [bold red]✗ {msg}[/]")
            answer = console.input("  [bold]Save anyway? (y/N):[/] ").strip().lower()
        else:
            print(f"  ✗ {msg}")
            answer = input("  Save anyway? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            if console:
                console.print("  [dim]Aborting.[/]\n")
            else:
                print("  Aborting.\n")
            sys.exit(1)

    # Save to config file
    _save_env_file(api_key)
    if console:
        console.print(f"  [green]Saved to:[/] [dim]{CONFIG_FILE}[/] (chmod 600)")
    else:
        print(f"  Saved to: {CONFIG_FILE} (chmod 600)")

    # Offer shell profile integration
    result = _save_to_shell_profile(api_key)
    if result[0] == "already_exists":
        if console:
            console.print(f"  [dim]Already in {result[1]}[/]")
        else:
            print(f"  Already in {result[1]}")
    else:
        _, profile, export_line = result
        if console:
            answer = console.input(f"  [bold]Add to {profile}? (Y/n):[/] ").strip().lower()
        else:
            answer = input(f"  Add to {profile}? (Y/n): ").strip().lower()

        if answer in ("", "y", "yes"):
            with open(profile, "a") as f:
                f.write(f"\n# swarm-agency\n{export_line}\n")
            if console:
                console.print(f"  [green]Added to {profile}[/]")
                console.print(f"  [dim]Run: source {profile}[/]")
            else:
                print(f"  Added to {profile}")
                print(f"  Run: source {profile}")
        else:
            if console:
                console.print(f"\n  [dim]To set manually:[/]")
                console.print(f"  [cyan]{export_line}[/]")
            else:
                print(f"\n  To set manually:")
                print(f"  {export_line}")

    # Done
    if console:
        console.print()
        console.print(Panel(
            Text.from_markup(
                "[bold green]Setup complete![/]\n\n"
                "Try these:\n"
                "  [bold]swarm-agency chat[/]                    — Interactive mode\n"
                "  [bold]swarm-agency \"Should we launch?\"[/]     — Quick debate\n"
                "  [bold]swarm-agency --demo startup-pivot[/]    — See a demo"
            ),
            border_style="green",
            padding=(1, 3),
        ))
        console.print()
    else:
        print("\n  Setup complete!")
        print("  Try: swarm-agency chat")
        print("  Or:  swarm-agency \"Should we launch?\"\n")
