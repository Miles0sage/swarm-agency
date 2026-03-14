"""Tests for DSPy optimizer module (without requiring dspy-ai installed)."""

import json
import os
import tempfile

import pytest

from swarm_agency.dspy_optimizer import (
    _check_dspy,
    build_trainset_from_memory,
    load_optimized_instruction,
)
from swarm_agency.memory import DecisionMemoryStore
from swarm_agency.types import AgentConfig, AgentVote, Decision


def _decision(request_id, position="YES"):
    return Decision(
        request_id=request_id,
        department="Strategy",
        outcome="MAJORITY",
        position=position,
        confidence=0.8,
        votes=[
            AgentVote(
                agent_name="Visionary", position=position, confidence=0.85,
                reasoning="Good analysis", factors=["market", "team"],
            ),
        ],
        summary="Test",
    )


class TestBuildTrainset:
    def test_builds_from_feedback(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = DecisionMemoryStore(db_path=db_path)

        agents = {
            "Visionary": AgentConfig(
                name="Visionary", role="CSO", expertise="strategy",
                bias="long-term", system_prompt="test", model="test",
            ),
        }

        # Store decisions with feedback
        for i in range(5):
            d = _decision(f"dspy-{i}")
            store.store_decision(d, f"Question {i}")
            store.add_feedback(f"dspy-{i}", True)

        records = build_trainset_from_memory(store, agents)
        assert len(records) >= 5
        assert all("question" in r for r in records)
        assert all("position" in r for r in records)
        assert all("role" in r for r in records)
        store.close()

    def test_skips_unfeedback_decisions(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = DecisionMemoryStore(db_path=db_path)

        d = _decision("no-fb")
        store.store_decision(d, "No feedback question")
        # Don't add feedback

        records = build_trainset_from_memory(store)
        assert len(records) == 0
        store.close()


class TestLoadOptimized:
    def test_returns_none_when_no_file(self, tmp_path):
        result = load_optimized_instruction(str(tmp_path))
        assert result is None


class TestCheckDspy:
    def test_returns_bool(self):
        result = _check_dspy()
        assert isinstance(result, bool)
