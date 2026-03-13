"""Export swarm-agency agents to Claude Code agent format.

Produces individual .md files suitable for .claude/agents/ directory,
each with frontmatter containing name and description.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML-like frontmatter from markdown text.

    Returns (metadata_dict, body_without_frontmatter).
    """
    metadata: dict[str, str] = {}
    body = text

    stripped = text.strip()
    if not stripped.startswith("---"):
        return metadata, body

    # Find second '---' delimiter
    rest = stripped[3:]
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return metadata, body

    front_block = rest[:end_idx].strip()
    body = rest[end_idx + 4:].strip()

    for line in front_block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        metadata[key.strip()] = value.strip()

    return metadata, body


def _build_claude_agent(metadata: dict[str, str], body: str) -> str:
    """Build a Claude Code agent markdown file from parsed agent data."""
    name = metadata.get("name", "Agent")
    department = metadata.get("department", "General")
    expertise = metadata.get("expertise", "")
    bias = metadata.get("bias", "")

    description = f"{department} department agent"
    if expertise:
        description += f" with expertise in {expertise}"

    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "---",
        "",
    ]

    # Include the body (role description, decision-making style, etc.)
    # but strip the "Compatible Tools" section since it is meta-documentation
    cleaned_body = _strip_compatible_tools_section(body)
    lines.append(cleaned_body)

    # Append the bias as a guiding instruction
    if bias:
        lines.append("")
        lines.append("## Analytical Bias")
        lines.append("")
        lines.append(f"Your analytical bias: {bias}.")

    return "\n".join(lines) + "\n"


def _strip_compatible_tools_section(body: str) -> str:
    """Remove the '## Compatible Tools' section from the body."""
    lines = body.splitlines()
    result = []
    skip = False
    for line in lines:
        if line.strip().startswith("## Compatible Tools"):
            skip = True
            continue
        if skip and line.strip().startswith("## "):
            skip = False
        if not skip:
            result.append(line)
    # Remove trailing blank lines
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result)


def export_claude(agents_dir: str, output_dir: str) -> list[str]:
    """Export all agent markdown files to Claude Code format.

    Args:
        agents_dir: Path to the agents/ directory containing department subdirs.
        output_dir: Path to write the output .md files.

    Returns:
        List of output file paths created.
    """
    agents_path = Path(agents_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    for md_file in sorted(agents_path.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue

        text = md_file.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(text)

        if not metadata.get("name"):
            continue

        output_content = _build_claude_agent(metadata, body)
        out_file = out_path / md_file.name
        out_file.write_text(output_content, encoding="utf-8")
        created.append(str(out_file))

    return created


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export agents to Claude Code format")
    parser.add_argument(
        "--agents-dir",
        default="agents",
        help="Path to agents/ directory (default: agents)",
    )
    parser.add_argument(
        "--output-dir",
        default="output/claude",
        help="Output directory (default: output/claude)",
    )
    args = parser.parse_args()

    files = export_claude(args.agents_dir, args.output_dir)
    for f in files:
        print(f"Created: {f}")
    print(f"\n{len(files)} agent(s) exported to Claude Code format.")
    sys.exit(0)
