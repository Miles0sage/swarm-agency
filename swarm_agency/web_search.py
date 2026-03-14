"""Web search tool for agent tool-calling.

Supports multiple backends:
1. Perplexity API (best, needs PERPLEXITY_API_KEY)
2. Tavily API (needs TAVILY_API_KEY)
3. DuckDuckGo HTML scrape (free, no key needed, slower)

The tool auto-selects the best available backend.
"""

import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger("swarm_agency.web_search")

TIMEOUT = 12.0


async def search_perplexity(query: str, api_key: str) -> Optional[str]:
    """Search using Perplexity API (sonar model)."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": f"Search for: {query}. Give concise factual results."}
                    ],
                    "max_tokens": 300,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content[:1000]
    except Exception as e:
        logger.warning(f"Perplexity search failed: {e}")
        return None


async def search_tavily(query: str, api_key: str) -> Optional[str]:
    """Search using Tavily API."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": 5,
                    "include_answer": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            parts = []
            if data.get("answer"):
                parts.append(f"Answer: {data['answer']}")

            for result in data.get("results", [])[:5]:
                title = result.get("title", "")
                content = result.get("content", "")[:150]
                parts.append(f"- {title}: {content}")

            return "\n".join(parts)[:1000] if parts else None
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
        return None


async def search_duckduckgo(query: str) -> Optional[str]:
    """Search DuckDuckGo via their instant answer API (free, no key)."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1"},
            )
            resp.raise_for_status()
            data = resp.json()

            parts = []
            if data.get("AbstractText"):
                parts.append(data["AbstractText"][:300])
            if data.get("Answer"):
                parts.append(f"Answer: {data['Answer']}")

            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and topic.get("Text"):
                    parts.append(f"- {topic['Text'][:150]}")

            return "\n".join(parts)[:1000] if parts else f"No results found for: {query}"
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return None


async def web_search(query: str) -> str:
    """Search the web using the best available backend.

    Tries in order: Perplexity > Tavily > DuckDuckGo (free fallback).
    """
    # Try Perplexity first
    perplexity_key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if perplexity_key:
        result = await search_perplexity(query, perplexity_key)
        if result:
            return result

    # Try Tavily
    tavily_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if tavily_key:
        result = await search_tavily(query, tavily_key)
        if result:
            return result

    # Free fallback: DuckDuckGo
    result = await search_duckduckgo(query)
    return result or f"Search failed for: {query}"
