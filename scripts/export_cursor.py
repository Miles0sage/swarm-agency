"""Export swarm-agency agents to Cursor rules format.

Produces a single .cursorrules file combining all agents as sections.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML-like frontmatter from markdown text."""
    metadata: dict[str, str] = {}
    body = text

    stripped = text.strip()
    if not stripped.startswith("---"):
        return metadata, body

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
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result)


def _extract_role_section(body: str) -> str:
    """Extract the Role section content from the body."""
    lines = body.splitlines()
    capturing = False
    result = []
    for line in lines:
        if line.strip().startswith("## Role"):
            capturing = True
            continue
        if capturing and line.strip().startswith("## "):
            break
        if capturing:
            result.append(line)
    return "\n".join(result).strip()


def export_cursor(agents_dir: str, output_path: str) -> str:
    """Export all agent markdown files to a single .cursorrules file.

    Args:
        agents_dir: Path to the agents/ directory containing department subdirs.
        output_path: Path to write the .cursorrules file.

    Returns:
        The output file path.
    """
    agents_path = Path(agents_dir)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    sections: list[str] = []

    sections.append("# Swarm Agency — Agent Personas")
    sections.append("")
    sections.append(
        "These personas provide diverse analytical perspectives for decision-making."
    )
    sections.append(
        "When asked for multi-perspective analysis, adopt these roles in sequence."
    )
    sections.append("")

    # Group by department
    departments: dict[str, list[tuple[dict[str, str], str]]] = {}

    for md_file in sorted(agents_path.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue

        text = md_file.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(text)

        if not metadata.get("name"):
            continue

        dept = metadata.get("department", "General")
        departments.setdefault(dept, []).append((metadata, body))

    for dept_name in sorted(departments.keys()):
        agents = departments[dept_name]
        for metadata, body in agents:
            name = metadata.get("name", "Agent")
            expertise = metadata.get("expertise", "")
            bias = metadata.get("bias", "")

            sections.append(f"## {dept_name} -- {name}")
            sections.append("")

            role_text = _extract_role_section(body)
            if role_text:
                sections.append(role_text)
                sections.append("")

            if bias:
                sections.append(f"**Analytical bias:** {bias}.")
                sections.append("")

            cleaned = _strip_compatible_tools_section(body)
            # Extract Decision-Making Style if present
            dm_lines = []
            capturing = False
            for line in cleaned.splitlines():
                if line.strip().startswith("## Decision-Making Style"):
                    capturing = True
                    continue
                if capturing and line.strip().startswith("## "):
                    break
                if capturing:
                    dm_lines.append(line)
            dm_text = "\n".join(dm_lines).strip()
            if dm_text:
                sections.append(f"**Decision-making style:** {dm_text}")
                sections.append("")

            sections.append("---")
            sections.append("")

    content = "\n".join(sections)
    out_file.write_text(content, encoding="utf-8")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export agents to Cursor format")
    parser.add_argument(
        "--agents-dir",
        default="agents",
        help="Path to agents/ directory (default: agents)",
    )
    parser.add_argument(
        "--output-path",
        default="output/.cursorrules",
        help="Output file path (default: output/.cursorrules)",
    )
    args = parser.parse_args()

    result = export_cursor(args.agents_dir, args.output_path)
    print(f"Created: {result}")
    sys.exit(0)
