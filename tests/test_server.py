"""Tests for FastAPI server endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from swarm_agency.server import app


@pytest.fixture
def client():
    return TestClient(app)


class TestEndpoints:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Swarm Agency" in resp.text
        assert "startStream" in resp.text

    def test_list_agents(self, client):
        resp = client.get("/api/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 43
        assert len(data["agents"]) == 43
        assert data["agents"][0]["name"]
        assert data["agents"][0]["department"]

    def test_list_departments(self, client):
        resp = client.get("/api/departments")
        assert resp.status_code == 200
        depts = resp.json()["departments"]
        assert len(depts) == 10
        assert all(d["description"] for d in depts)

    def test_list_templates(self, client):
        resp = client.get("/api/templates")
        assert resp.status_code == 200
        templates = resp.json()["templates"]
        assert "hire" in templates
        assert "pricing" in templates
        assert len(templates) == 5


class TestDecideEndpoint:
    def test_missing_question_returns_422(self, client):
        resp = client.get("/api/decide")
        assert resp.status_code == 422  # FastAPI validation error
