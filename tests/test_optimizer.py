"""Tests for prompt optimizer."""

import json
import os
import tempfile

import pytest

from swarm_agency.optimizer import PromptOptimizer, OptimizationResult
from swarm_agency.memory import DecisionMemoryStore
from swarm_agency.types import AgentConfig, AgentVote, Decision


def _agent(name="Visionary"):
    return AgentConfig(
        name=name, role="CSO", expertise="strategy", bias="long-term",
        system_prompt="You are a strategic advisor.", model="test",
    )


def _decision(request_id, position="YES", votes=None):
    return Decision(
        request_id=request_id,
        department="Strategy",
        outcome="MAJORITY",
        position=position,
        confidence=0.8,
        votes=votes or [
            AgentVote(
                agent_name="Visionary", position=position, confidence=0.85,
                reasoning="Good analysis", factors=["market timing", "team strength"],
            ),
        ],
        summary="Test decision",
    )


@pytest.fixture
def optimizer(tmp_path):
    db_path = str(tmp_path / "test.db")
    store = DecisionMemoryStore(db_path=db_path)
    opt = PromptOptimizer(store, output_dir=str(tmp_path / "optimized"))
    yield opt
    store.close()


class TestAnalyzeAgent:
    def test_no_data(self, optimizer):
        result = optimizer.analyze_agent("NonexistentAgent")
        assert result["status"] == "no_data"

    def test_with_feedback(self, optimizer):
        # Store some decisions with feedback
        for i in range(5):
            d = _decision(f"opt-{i}")
            optimizer.memory_store.store_decision(d, f"Question {i}")
            optimizer.memory_store.add_feedback(f"opt-{i}", i < 3)  # 3 correct, 2 wrong

        result = optimizer.analyze_agent("Visionary")
        assert result["status"] == "analyzed"
        assert result["total"] == 5
        assert result["reviewed"] == 5


class TestOptimizePrompt:
    def test_not_enough_feedback(self, optimizer):
        agent = _agent()
        result = optimizer.optimize_prompt(agent, min_feedback=5)
        assert result.optimized_prompt == agent.system_prompt
        assert "Not enough" in result.improvement_notes[0]

    def test_low_accuracy_adds_caution(self, optimizer):
        # Create many wrong decisions
        for i in range(10):
            d = _decision(f"lo-{i}")
            optimizer.memory_store.store_decision(d, f"Question {i}")
            optimizer.memory_store.add_feedback(f"lo-{i}", i < 2)  # 2/10 correct

        agent = _agent()
        result = optimizer.optimize_prompt(agent, min_feedback=5)
        assert result.optimized_prompt != agent.system_prompt
        assert "Calibration" in result.optimized_prompt or "CALIBRATION" in result.optimized_prompt
        assert any("accuracy" in n.lower() for n in result.improvement_notes)

    def test_high_accuracy_adds_confidence(self, optimizer):
        for i in range(10):
            d = _decision(f"hi-{i}")
            optimizer.memory_store.store_decision(d, f"Question {i}")
            optimizer.memory_store.add_feedback(f"hi-{i}", True)  # 100% correct

        agent = _agent()
        result = optimizer.optimize_prompt(agent, min_feedback=5)
        assert "strong" in result.optimized_prompt.lower() or "CALIBRATION" in result.optimized_prompt

    def test_saves_to_disk(self, optimizer):
        for i in range(10):
            d = _decision(f"sv-{i}")
            optimizer.memory_store.store_decision(d, f"Question {i}")
            optimizer.memory_store.add_feedback(f"sv-{i}", i < 3)

        agent = _agent()
        optimizer.optimize_prompt(agent, min_feedback=5)

        # Check file was saved
        saved = optimizer.load_optimized("Visionary")
        assert saved is not None
        assert len(saved) > len(agent.system_prompt)


class TestApplyOptimizations:
    def test_applies_saved_optimization(self, optimizer):
        # Manually save an optimization
        result = OptimizationResult(
            agent_name="Visionary",
            original_prompt="old prompt",
            optimized_prompt="optimized prompt with amendments",
            improvement_notes=["test"],
            feedback_used=10,
        )
        optimizer._save_optimized(result)

        agents = [_agent("Visionary"), _agent("Other")]
        optimized = optimizer.apply_optimizations(agents)

        assert optimized[0].system_prompt == "optimized prompt with amendments"
        assert optimized[1].system_prompt == agents[1].system_prompt  # unchanged

    def test_no_optimization_returns_original(self, optimizer):
        agents = [_agent()]
        optimized = optimizer.apply_optimizations(agents)
        assert optimized[0].system_prompt == agents[0].system_prompt


class TestOptimizeAll:
    def test_optimizes_multiple(self, optimizer):
        for i in range(10):
            d = _decision(f"all-{i}")
            optimizer.memory_store.store_decision(d, f"Q {i}")
            optimizer.memory_store.add_feedback(f"all-{i}", i < 5)

        agents = [_agent("Visionary"), _agent("Other")]
        results = optimizer.optimize_all(agents, min_feedback=5)
        assert len(results) == 2
        assert all(isinstance(r, OptimizationResult) for r in results)
