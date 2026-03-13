"""Export swarm-agency agents to Aider configuration format.

Produces a .aider.conf.yml file with a conventions section listing agent rules.
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


def _yaml_escape(text: str) -> str:
    """Escape a string for safe inclusion in YAML values."""
    # Replace backslashes, then quotes
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", " ")
    return text


def export_aider(agents_dir: str, output_path: str) -> str:
    """Export all agent markdown files to an Aider config file.

    Args:
        agents_dir: Path to the agents/ directory containing department subdirs.
        output_path: Path to write the .aider.conf.yml file.

    Returns:
        The output file path.
    """
    agents_path = Path(agents_dir)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Swarm Agency — Agent Personas for Aider")
    lines.append("# Auto-generated. Do not edit manually.")
    lines.append("")
    lines.append("# Conventions define the agent personas available for analysis.")
    lines.append("# Use --read to include specific agent files, or reference")
    lines.append("# these conventions in your prompts.")
    lines.append("")
    lines.append("conventions:")

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
        lines.append(f"  # --- {dept_name} Department ---")
        for metadata, body in agents:
            name = metadata.get("name", "Agent")
            expertise = metadata.get("expertise", "")
            bias = metadata.get("bias", "")
            role_text = _extract_role_section(body)

            # Build the convention entry
            description = role_text if role_text else f"Expertise: {expertise}"
            if bias:
                description += f" Analytical bias: {bias}."

            escaped = _yaml_escape(description)
            lines.append(f'  - name: "{dept_name}/{name}"')
            lines.append(f'    rule: "{escaped}"')

    lines.append("")

    content = "\n".join(lines)
    out_file.write_text(content, encoding="utf-8")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export agents to Aider format")
    parser.add_argument(
        "--agents-dir",
        default="agents",
        help="Path to agents/ directory (default: agents)",
    )
    parser.add_argument(
        "--output-path",
        default="output/.aider.conf.yml",
        help="Output file path (default: output/.aider.conf.yml)",
    )
    args = parser.parse_args()

    result = export_aider(args.agents_dir, args.output_path)
    print(f"Created: {result}")
    sys.exit(0)
