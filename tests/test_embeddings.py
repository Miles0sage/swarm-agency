"""Tests for the embeddings module — all mocked, zero real API calls."""

import asyncio
import struct
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from swarm_agency.embeddings import (
    get_embedding,
    get_embeddings_batch,
    cosine_similarity,
    embedding_to_bytes,
    bytes_to_embedding,
)


class TestGetEmbedding:
    @pytest.mark.asyncio
    async def test_success_returns_vector(self):
        mock_values = [0.1] * 3072
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "embedding": {"values": mock_values}
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("swarm_agency.embeddings.httpx.AsyncClient", return_value=mock_client):
            result = await get_embedding("test text", "fake-key")

        assert result is not None
        assert len(result) == 3072
        assert result[0] == 0.1

    @pytest.mark.asyncio
    async def test_http_error_returns_none(self):
        import httpx
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=MagicMock()
        )

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("swarm_agency.embeddings.httpx.AsyncClient", return_value=mock_client):
            result = await get_embedding("test", "fake-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_returns_none(self):
        import httpx
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with patch("swarm_agency.embeddings.httpx.AsyncClient", return_value=mock_client):
            result = await get_embedding("test", "fake-key", timeout=1.0)

        assert result is None

    @pytest.mark.asyncio
    async def test_malformed_json_returns_none(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"bad": "response"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("swarm_agency.embeddings.httpx.AsyncClient", return_value=mock_client):
            result = await get_embedding("test", "fake-key")

        assert result is None


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = np.array([1.0, 2.0, 3.0])
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 2.0, 3.0])
        assert cosine_similarity(a, b) == 0.0
        assert cosine_similarity(b, a) == 0.0

    def test_both_zero_vectors(self):
        z = np.zeros(3)
        assert cosine_similarity(z, z) == 0.0


class TestEmbeddingSerDe:
    def test_roundtrip_preserves_values(self):
        original = [0.1, 0.2, 0.3, -0.5, 1.0]
        blob = embedding_to_bytes(original)
        recovered = bytes_to_embedding(blob)
        np.testing.assert_array_almost_equal(recovered, original, decimal=6)

    def test_roundtrip_3072_dim(self):
        original = list(np.random.randn(3072).astype(np.float32))
        blob = embedding_to_bytes(original)
        recovered = bytes_to_embedding(blob)
        assert len(recovered) == 3072
        np.testing.assert_array_almost_equal(recovered, original, decimal=6)

    def test_empty_embedding(self):
        blob = embedding_to_bytes([])
        recovered = bytes_to_embedding(blob)
        assert len(recovered) == 0

    def test_bytes_format(self):
        data = [1.0, 2.0]
        blob = embedding_to_bytes(data)
        assert len(blob) == 8  # 2 * 4 bytes per float32


class TestGetEmbeddingsBatch:
    @pytest.mark.asyncio
    async def test_batch_all_succeed(self):
        async def mock_get_embedding(text, api_key, timeout=10.0):
            return [0.1] * 3072

        with patch("swarm_agency.embeddings.get_embedding", side_effect=mock_get_embedding):
            results = await get_embeddings_batch(["a", "b", "c"], "key")

        assert len(results) == 3
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_batch_partial_failures(self):
        call_count = 0
        async def mock_get_embedding(text, api_key, timeout=10.0):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return None
            return [0.1] * 3072

        with patch("swarm_agency.embeddings.get_embedding", side_effect=mock_get_embedding):
            results = await get_embeddings_batch(["a", "b", "c"], "key")

        assert len(results) == 3
        assert results[0] is not None
        assert results[1] is None
        assert results[2] is not None

    @pytest.mark.asyncio
    async def test_batch_empty_list(self):
        results = await get_embeddings_batch([], "key")
        assert results == []
