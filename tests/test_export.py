"""Tests for export scripts."""

import tempfile
import os
import sys
from pathlib import Path

# Add scripts/ to path so we can import export modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from export_claude import export_claude, _parse_frontmatter
from export_cursor import export_cursor
from export_windsurf import export_windsurf
from export_aider import export_aider
from export_gemini import export_gemini


SAMPLE_AGENT = """---
name: TestAgent
department: Strategy
model: qwen3-coder-plus
expertise: strategic planning
bias: long-term thinking
---

# TestAgent — Chief Strategy Officer

> Strategic planning expert.

## Role

You are the Chief Strategy Officer.

## Decision-Making Style

Focuses on long-term outcomes.

## When to Use This Agent

- Strategic planning sessions
- Competitive analysis

## Compatible Tools

This persona works in any AI tool.
"""


def _create_agents_dir(tmpdir: str) -> str:
    """Create a minimal agents/ dir with one agent file."""
    agents_dir = os.path.join(tmpdir, "agents", "strategy")
    os.makedirs(agents_dir)
    agent_file = os.path.join(agents_dir, "test-agent.md")
    with open(agent_file, "w") as f:
        f.write(SAMPLE_AGENT)
    return os.path.join(tmpdir, "agents")


class TestParseFrontmatter:
    def test_parses_name(self):
        meta, body = _parse_frontmatter(SAMPLE_AGENT)
        assert meta["name"] == "TestAgent"

    def test_parses_department(self):
        meta, body = _parse_frontmatter(SAMPLE_AGENT)
        assert meta["department"] == "Strategy"

    def test_parses_model(self):
        meta, body = _parse_frontmatter(SAMPLE_AGENT)
        assert meta["model"] == "qwen3-coder-plus"

    def test_body_starts_with_heading(self):
        meta, body = _parse_frontmatter(SAMPLE_AGENT)
        assert body.startswith("# TestAgent")

    def test_no_frontmatter(self):
        meta, body = _parse_frontmatter("# Just a heading\nSome text.")
        assert meta == {}
        assert "Just a heading" in body


class TestExportClaude:
    def test_creates_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_dir = os.path.join(tmpdir, "output")
            files = export_claude(agents_dir, output_dir)
            assert len(files) == 1
            assert files[0].endswith(".md")

    def test_output_has_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_dir = os.path.join(tmpdir, "output")
            files = export_claude(agents_dir, output_dir)
            content = Path(files[0]).read_text()
            assert "---" in content
            assert "name: TestAgent" in content

    def test_strips_compatible_tools(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_dir = os.path.join(tmpdir, "output")
            files = export_claude(agents_dir, output_dir)
            content = Path(files[0]).read_text()
            assert "Compatible Tools" not in content

    def test_skips_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            # Add a _template.md that should be skipped
            template = os.path.join(agents_dir, "_template.md")
            with open(template, "w") as f:
                f.write("---\nname: Template\n---\n# Template")
            output_dir = os.path.join(tmpdir, "output")
            files = export_claude(agents_dir, output_dir)
            assert len(files) == 1  # Only the real agent, not template


class TestExportCursor:
    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, ".cursorrules")
            result = export_cursor(agents_dir, output_path)
            assert os.path.exists(result)

    def test_contains_agent_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, ".cursorrules")
            result = export_cursor(agents_dir, output_path)
            content = Path(result).read_text()
            assert "TestAgent" in content


class TestExportWindsurf:
    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, ".windsurfrules")
            result = export_windsurf(agents_dir, output_path)
            assert os.path.exists(result)


class TestExportAider:
    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, ".aider.conf.yml")
            result = export_aider(agents_dir, output_path)
            assert os.path.exists(result)


class TestExportGemini:
    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, "GEMINI.md")
            result = export_gemini(agents_dir, output_path)
            assert os.path.exists(result)

    def test_contains_agent_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = _create_agents_dir(tmpdir)
            output_path = os.path.join(tmpdir, "GEMINI.md")
            result = export_gemini(agents_dir, output_path)
            content = Path(result).read_text()
            assert "TestAgent" in content
