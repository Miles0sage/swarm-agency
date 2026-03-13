"""Export swarm-agency agents to Gemini CLI format.

Produces a GEMINI.md file with all agents as markdown sections.
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


def export_gemini(agents_dir: str, output_path: str) -> str:
    """Export all agent markdown files to a GEMINI.md file.

    Args:
        agents_dir: Path to the agents/ directory containing department subdirs.
        output_path: Path to write the GEMINI.md file.

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
        "This file defines agent personas for multi-perspective analysis."
    )
    sections.append(
        "When asked for diverse viewpoints, adopt these roles to provide "
        "comprehensive analysis from different angles."
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
        sections.append(f"---")
        sections.append("")
        sections.append(f"# {dept_name} Department")
        sections.append("")

        for metadata, body in agents:
            cleaned = _strip_compatible_tools_section(body)
            # The body already contains the heading (# Name -- Role),
            # so bump all headings down one level for nesting under department
            adjusted = []
            for line in cleaned.splitlines():
                if line.startswith("# ") and not line.startswith("## "):
                    adjusted.append("#" + line)  # # -> ##
                elif line.startswith("## "):
                    adjusted.append("#" + line)  # ## -> ###
                else:
                    adjusted.append(line)
            sections.append("\n".join(adjusted))
            sections.append("")

    content = "\n".join(sections)
    out_file.write_text(content, encoding="utf-8")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export agents to Gemini CLI format")
    parser.add_argument(
        "--agents-dir",
        default="agents",
        help="Path to agents/ directory (default: agents)",
    )
    parser.add_argument(
        "--output-path",
        default="output/GEMINI.md",
        help="Output file path (default: output/GEMINI.md)",
    )
    args = parser.parse_args()

    result = export_gemini(args.agents_dir, args.output_path)
    print(f"Created: {result}")
    sys.exit(0)
