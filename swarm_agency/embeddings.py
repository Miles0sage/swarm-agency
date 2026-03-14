"""Embedding module — thin async wrapper around Google Gemini embedding API.

Uses gemini-embedding-001 (FREE) to generate 3072-dimensional embeddings
for semantic search in decision memory.
"""

import logging
import struct
from typing import Optional

import httpx
import numpy as np

logger = logging.getLogger("swarm_agency.embeddings")

GEMINI_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-embedding-001:embedContent"
)


async def get_embedding(
    text: str, api_key: str, timeout: float = 10.0
) -> Optional[list[float]]:
    """Get embedding vector from Gemini API.

    Returns a list of floats (3072-dim) on success, None on any failure.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{GEMINI_EMBED_URL}?key={api_key}",
                json={"content": {"parts": [{"text": text}]}},
            )
            resp.raise_for_status()
            data = resp.json()
            values = data["embedding"]["values"]
            return values
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as e:
        logger.warning("Embedding request failed: %s", e)
        return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors. Returns 0.0 for zero vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def embedding_to_bytes(embedding: list[float]) -> bytes:
    """Pack a list of floats into a compact binary blob."""
    return struct.pack(f"{len(embedding)}f", *embedding)


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """Unpack a binary blob back into a numpy float32 array."""
    return np.frombuffer(data, dtype=np.float32).copy()


async def get_embeddings_batch(
    texts: list[str], api_key: str, timeout: float = 10.0
) -> list[Optional[list[float]]]:
    """Get embeddings for multiple texts. Handles partial failures."""
    import asyncio as _asyncio

    tasks = [get_embedding(t, api_key, timeout) for t in texts]
    return list(await _asyncio.gather(*tasks))
