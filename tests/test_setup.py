"""Tests for setup wizard."""

import os
from unittest.mock import patch, MagicMock

from swarm_agency.setup import (
    _test_api_key,
    _save_env_file,
    _save_to_shell_profile,
    CONFIG_FILE,
)


class TestApiKeyValidation:
    def test_valid_key_returns_true(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.post", return_value=mock_resp):
            ok, msg = _test_api_key("valid-key")
        assert ok is True
        assert "valid" in msg.lower()

    def test_invalid_key_returns_false(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        with patch("httpx.post", return_value=mock_resp):
            ok, msg = _test_api_key("bad-key")
        assert ok is False
        assert "401" in msg

    def test_forbidden_key(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        with patch("httpx.post", return_value=mock_resp):
            ok, msg = _test_api_key("forbidden-key")
        assert ok is False
        assert "403" in msg

    def test_timeout_returns_false(self):
        import httpx
        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            ok, msg = _test_api_key("any-key")
        assert ok is False
        assert "timed out" in msg.lower()

    def test_connection_error(self):
        with patch("httpx.post", side_effect=ConnectionError("no network")):
            ok, msg = _test_api_key("any-key")
        assert ok is False
        assert "failed" in msg.lower()

    def test_unexpected_status(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        with patch("httpx.post", return_value=mock_resp):
            ok, msg = _test_api_key("any-key")
        assert ok is False
        assert "500" in msg


class TestSaveEnvFile:
    def test_saves_key(self, tmp_path):
        config = tmp_path / ".swarm-agency.env"
        with patch("swarm_agency.setup.CONFIG_FILE", str(config)):
            _save_env_file("test-key-123")
        content = config.read_text()
        assert "ALIBABA_CODING_API_KEY=test-key-123" in content

    def test_saves_base_url(self, tmp_path):
        config = tmp_path / ".swarm-agency.env"
        with patch("swarm_agency.setup.CONFIG_FILE", str(config)):
            _save_env_file("test-key", base_url="https://custom.api.com")
        content = config.read_text()
        assert "ALIBABA_CODING_BASE_URL=https://custom.api.com" in content


class TestShellProfile:
    def test_not_exists(self, tmp_path):
        profile = tmp_path / ".bashrc"
        with patch.dict("os.environ", {"SHELL": "/bin/bash"}):
            with patch("swarm_agency.setup.os.path.expanduser", return_value=str(profile)):
                result = _save_to_shell_profile("test-key")
        assert result[0] == "not_exists"

    def test_already_exists(self, tmp_path):
        profile = tmp_path / ".bashrc"
        profile.write_text('export ALIBABA_CODING_API_KEY="old-key"\n')
        with patch.dict("os.environ", {"SHELL": "/bin/bash"}):
            with patch("swarm_agency.setup.os.path.expanduser", return_value=str(profile)):
                result = _save_to_shell_profile("test-key")
        assert result[0] == "already_exists"
