"""Tests for web search module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from swarm_agency.web_search import (
    search_duckduckgo,
    search_perplexity,
    search_tavily,
    web_search,
)


class TestDuckDuckGo:
    @pytest.mark.asyncio
    async def test_returns_results(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "AbstractText": "Python is a programming language.",
            "Answer": "",
            "RelatedTopics": [
                {"Text": "Related topic 1"},
                {"Text": "Related topic 2"},
            ],
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("swarm_agency.web_search.httpx.AsyncClient", return_value=mock_client):
            result = await search_duckduckgo("python programming")

        assert result is not None
        assert "Python" in result

    @pytest.mark.asyncio
    async def test_returns_fallback_on_empty(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "AbstractText": "",
            "Answer": "",
            "RelatedTopics": [],
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("swarm_agency.web_search.httpx.AsyncClient", return_value=mock_client):
            result = await search_duckduckgo("xyznonexistent")

        assert "No results" in result or "xyznonexistent" in result


class TestWebSearchAutoSelect:
    @pytest.mark.asyncio
    async def test_falls_back_to_duckduckgo(self):
        """With no API keys set, should use DuckDuckGo."""
        with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "", "TAVILY_API_KEY": ""}):
            with patch("swarm_agency.web_search.search_duckduckgo", new_callable=AsyncMock,
                       return_value="DDG result"):
                result = await web_search("test query")
        assert result == "DDG result"

    @pytest.mark.asyncio
    async def test_prefers_perplexity(self):
        with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "fake-key", "TAVILY_API_KEY": ""}):
            with patch("swarm_agency.web_search.search_perplexity", new_callable=AsyncMock,
                       return_value="Perplexity result") as mock_pp:
                result = await web_search("test")
        assert result == "Perplexity result"
        mock_pp.assert_called_once()

    @pytest.mark.asyncio
    async def test_falls_to_tavily_on_perplexity_fail(self):
        with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "fake", "TAVILY_API_KEY": "fake"}):
            with patch("swarm_agency.web_search.search_perplexity", new_callable=AsyncMock,
                       return_value=None):
                with patch("swarm_agency.web_search.search_tavily", new_callable=AsyncMock,
                           return_value="Tavily result"):
                    result = await web_search("test")
        assert result == "Tavily result"
