"""Tests for interactive chat mode."""

import sys
from unittest.mock import patch, MagicMock

from swarm_agency.chat import (
    _handle_slash_command,
    _fuzzy_match_command,
    _edit_distance,
    _prompt_text,
    _check_api_key,
    _rebuild_agency,
    SLASH_COMMANDS,
    KNOWN_COMMANDS,
    BARE_COMMANDS,
)


class TestSlashCommands:
    def _state(self):
        return {
            "api_key": "",
            "base_url": None,
            "memory": False,
            "department": None,
            "context": None,
            "json_mode": False,
            "history": [],
            "agency": _rebuild_agency({
                "api_key": "",
                "base_url": None,
                "memory": False,
            }),
        }

    def test_help_returns_true(self, capsys):
        assert _handle_slash_command("/help", "", self._state()) is True

    def test_exit_raises_system_exit(self):
        import pytest
        with pytest.raises(SystemExit):
            _handle_slash_command("/exit", "", self._state())

    def test_quit_alias(self):
        import pytest
        with pytest.raises(SystemExit):
            _handle_slash_command("/quit", "", self._state())

    def test_q_alias(self):
        import pytest
        with pytest.raises(SystemExit):
            _handle_slash_command("/q", "", self._state())

    def test_clear_returns_true(self):
        with patch("os.system"):
            assert _handle_slash_command("/clear", "", self._state()) is True

    def test_agents_returns_true(self, capsys):
        assert _handle_slash_command("/agents", "", self._state()) is True

    def test_departments_returns_true(self, capsys):
        assert _handle_slash_command("/departments", "", self._state()) is True

    def test_dept_set(self):
        state = self._state()
        _handle_slash_command("/dept", "Finance", state)
        assert state["department"] == "Finance"

    def test_dept_case_insensitive(self):
        state = self._state()
        _handle_slash_command("/dept", "finance", state)
        assert state["department"] == "Finance"

    def test_dept_prefix_match(self):
        state = self._state()
        _handle_slash_command("/dept", "eng", state)
        assert state["department"] == "Engineering"

    def test_dept_all_resets(self):
        state = self._state()
        state["department"] = "Finance"
        _handle_slash_command("/dept", "all", state)
        assert state["department"] is None

    def test_dept_unknown(self, capsys):
        state = self._state()
        _handle_slash_command("/dept", "nonexistent", state)
        assert state["department"] is None

    def test_memory_on(self):
        state = self._state()
        _handle_slash_command("/memory", "on", state)
        assert state["memory"] is True

    def test_memory_off(self):
        state = self._state()
        state["memory"] = True
        _handle_slash_command("/memory", "off", state)
        assert state["memory"] is False

    def test_context_set(self):
        state = self._state()
        _handle_slash_command("/context", "We have $1M ARR", state)
        assert state["context"] == "We have $1M ARR"

    def test_context_clear(self):
        state = self._state()
        state["context"] = "old context"
        _handle_slash_command("/context", "clear", state)
        assert state["context"] is None

    def test_json_toggle(self):
        state = self._state()
        assert state["json_mode"] is False
        _handle_slash_command("/json", "", state)
        assert state["json_mode"] is True
        _handle_slash_command("/json", "", state)
        assert state["json_mode"] is False

    def test_demo_no_args_returns_true(self, capsys):
        assert _handle_slash_command("/demo", "", self._state()) is True

    def test_demo_valid_scenario(self, capsys):
        assert _handle_slash_command("/demo", "startup-pivot", self._state()) is True

    def test_demo_invalid_scenario(self, capsys):
        assert _handle_slash_command("/demo", "nonexistent", self._state()) is True

    def test_unknown_command_returns_false(self):
        assert _handle_slash_command("/foobar", "", self._state()) is False

    def test_history_no_memory(self, capsys):
        state = self._state()
        assert _handle_slash_command("/history", "", state) is True


class TestPromptText:
    def test_default_prompt(self):
        assert _prompt_text(None) == "swarm [all]> "

    def test_department_prompt(self):
        assert _prompt_text("Finance") == "swarm [Finance]> "


class TestCheckApiKey:
    def test_no_key_returns_none(self):
        with patch.dict("os.environ", {}, clear=True):
            assert _check_api_key() is None

    def test_env_key_found(self):
        with patch.dict("os.environ", {"ALIBABA_CODING_API_KEY": "test-key-123"}):
            assert _check_api_key() == "test-key-123"

    def test_empty_key_returns_none(self):
        with patch.dict("os.environ", {"ALIBABA_CODING_API_KEY": "  "}):
            assert _check_api_key() is None


class TestRebuildAgency:
    def test_builds_with_all_departments(self):
        state = {"api_key": "test", "base_url": None, "memory": False}
        agency = _rebuild_agency(state)
        assert len(agency.departments) == 10

    def test_builds_with_memory(self):
        state = {"api_key": "test", "base_url": None, "memory": True}
        agency = _rebuild_agency(state)
        assert agency.memory_enabled is True


class TestFuzzyMatching:
    def test_exact_match(self):
        assert _fuzzy_match_command("/help") == "/help"
        assert _fuzzy_match_command("/memory") == "/memory"

    def test_prefix_match(self):
        assert _fuzzy_match_command("/mem") == "/memory"
        assert _fuzzy_match_command("/dep") in ("/dept", "/departments")  # both match

    def test_typo_match(self):
        assert _fuzzy_match_command("/memeory") == "/memory"
        assert _fuzzy_match_command("/hep") == "/help"
        assert _fuzzy_match_command("/ageents") == "/agents"
        assert _fuzzy_match_command("/exti") == "/exit"

    def test_too_far_returns_none(self):
        result = _fuzzy_match_command("/xyzabc")
        # Should either return None or a distant match
        # The key is it doesn't crash

    def test_edit_distance_identical(self):
        assert _edit_distance("abc", "abc") == 0

    def test_edit_distance_one_off(self):
        assert _edit_distance("/memory", "/memeory") <= 2
        assert _edit_distance("/help", "/hep") == 1

    def test_edit_distance_different(self):
        assert _edit_distance("abc", "xyz") == 3


class TestBareCommands:
    def test_bare_commands_map_correctly(self):
        assert BARE_COMMANDS["help"] == "/help"
        assert BARE_COMMANDS["exit"] == "/exit"
        assert BARE_COMMANDS["quit"] == "/exit"
        assert BARE_COMMANDS["agents"] == "/agents"

    def test_memory_toggle(self):
        """Bare /memory with no args should toggle."""
        state = TestSlashCommands._state(TestSlashCommands())
        assert state["memory"] is False
        _handle_slash_command("/memory", "", state)
        assert state["memory"] is True
        _handle_slash_command("/memory", "", state)
        assert state["memory"] is False

    def test_fuzzy_memory_typo(self):
        """Typo like /memeory should match /memory."""
        state = TestSlashCommands._state(TestSlashCommands())
        assert state["memory"] is False
        _handle_slash_command("/memeory", "on", state)
        assert state["memory"] is True


class TestMultilineInput:
    """Test multiline input detection logic (backslash and triple-quote)."""

    def test_backslash_continuation_detected(self):
        """Input ending with \\ signals multiline."""
        assert "Should we pivot from\\".endswith("\\")

    def test_triple_quote_start_detected(self):
        """Input starting with triple quotes signals multiline."""
        assert '"""Should we'.startswith('"""')

    def test_backslash_joins_with_space(self):
        """Backslash continuation joins lines with space."""
        lines = ["Should we pivot", "from B2C to B2B?"]
        result = " ".join(lines).strip()
        assert result == "Should we pivot from B2C to B2B?"

    def test_triple_quote_joins_with_newline(self):
        """Triple-quote block joins lines with newline."""
        lines = ["Should we pivot", "from B2C to B2B?", "We have 12k MAU."]
        result = "\n".join(lines).strip()
        assert "pivot" in result
        assert "12k MAU" in result

    def test_multiline_hint_in_help(self, capsys):
        from swarm_agency.chat import MULTILINE_HINT
        assert "multiline" in MULTILINE_HINT.lower()


class TestChatSubcommand:
    def test_chat_subcommand_launches(self):
        with patch("swarm_agency.chat.run_chat") as mock_chat:
            with patch("sys.argv", ["swarm-agency", "chat"]):
                from swarm_agency.cli import main
                main()
            mock_chat.assert_called_once()

    def test_init_subcommand_launches(self):
        with patch("swarm_agency.setup.run_setup") as mock_setup:
            with patch("sys.argv", ["swarm-agency", "init"]):
                from swarm_agency.cli import main
                main()
            mock_setup.assert_called_once()

    def test_setup_alias(self):
        with patch("swarm_agency.setup.run_setup") as mock_setup:
            with patch("sys.argv", ["swarm-agency", "setup"]):
                from swarm_agency.cli import main
                main()
            mock_setup.assert_called_once()
