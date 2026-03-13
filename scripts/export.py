"""Main entry point for exporting swarm-agency agents to various AI tool formats.

Usage:
    python scripts/export.py --format claude --output-dir ./output
    python scripts/export.py --format cursor --output-dir ./output
    python scripts/export.py --format windsurf --output-dir ./output
    python scripts/export.py --format aider --output-dir ./output
    python scripts/export.py --format gemini --output-dir ./output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from export_claude import export_claude
from export_cursor import export_cursor
from export_windsurf import export_windsurf
from export_aider import export_aider
from export_gemini import export_gemini


FORMATS = ("claude", "cursor", "windsurf", "aider", "gemini")

DEFAULT_AGENTS_DIR = str(Path(__file__).resolve().parent.parent / "agents")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export swarm-agency agents to AI tool formats",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=FORMATS,
        help="Target format: claude, cursor, windsurf, aider, or gemini",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--agents-dir",
        default=DEFAULT_AGENTS_DIR,
        help="Path to agents/ directory (default: auto-detected from repo)",
    )
    args = parser.parse_args()

    agents_dir = args.agents_dir
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = args.format

    if fmt == "claude":
        dest = str(output_dir / "claude")
        files = export_claude(agents_dir, dest)
        print(f"Exported {len(files)} agent(s) to {dest}/")
        for f in files:
            print(f"  {f}")

    elif fmt == "cursor":
        dest = str(output_dir / ".cursorrules")
        result = export_cursor(agents_dir, dest)
        print(f"Exported to {result}")

    elif fmt == "windsurf":
        dest = str(output_dir / ".windsurfrules")
        result = export_windsurf(agents_dir, dest)
        print(f"Exported to {result}")

    elif fmt == "aider":
        dest = str(output_dir / ".aider.conf.yml")
        result = export_aider(agents_dir, dest)
        print(f"Exported to {result}")

    elif fmt == "gemini":
        dest = str(output_dir / "GEMINI.md")
        result = export_gemini(agents_dir, dest)
        print(f"Exported to {result}")

    print("\nDone.")


if __name__ == "__main__":
    main()
