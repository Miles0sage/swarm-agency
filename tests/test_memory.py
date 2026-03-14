"""Tests for decision memory system."""

import json
import os
import tempfile

import pytest

from swarm_agency.types import AgentVote, Decision, DecisionRecord
from swarm_agency.memory import (
    DecisionMemoryStore,
    build_memory_context,
    extract_keywords,
    keyword_similarity,
)


def _make_decision(request_id="test-001", department="Strategy", position="YES"):
    return Decision(
        request_id=request_id,
        department=department,
        outcome="MAJORITY",
        position=position,
        confidence=0.75,
        votes=[
            AgentVote(
                agent_name="Visionary",
                position="YES",
                confidence=0.9,
                reasoning="Strong opportunity",
                factors=["market timing", "team strength"],
            ),
            AgentVote(
                agent_name="DevilsAdvocate",
                position="NO",
                confidence=0.7,
                reasoning="Too risky",
                factors=["market risk", "execution risk"],
            ),
        ],
        summary="Majority favors yes.",
        dissenting_views=["DevilsAdvocate: Too risky."],
        duration_seconds=3.2,
    )


@pytest.fixture
def memory_store(tmp_path):
    db_path = str(tmp_path / "test_decisions.db")
    store = DecisionMemoryStore(db_path=db_path)
    yield store
    store.close()


class TestExtractKeywords:
    def test_basic_extraction(self):
        keywords = extract_keywords("Should we pivot from B2C to B2B?")
        assert "pivot" in keywords
        assert "should" not in keywords  # stop word

    def test_empty_string(self):
        assert extract_keywords("") == []

    def test_short_words_filtered(self):
        keywords = extract_keywords("I am at an OK AI")
        assert len(keywords) == 0  # all words are < 3 chars or stop words

    def test_deduplication(self):
        keywords = extract_keywords("pivot pivot pivot to pivot")
        assert keywords.count("pivot") == 1


class TestKeywordSimilarity:
    def test_identical(self):
        assert keyword_similarity(["a", "b", "c"], ["a", "b", "c"]) == 1.0

    def test_no_overlap(self):
        assert keyword_similarity(["a", "b"], ["c", "d"]) == 0.0

    def test_partial_overlap(self):
        sim = keyword_similarity(["a", "b", "c"], ["b", "c", "d"])
        assert 0.4 < sim < 0.6  # 2/4 = 0.5

    def test_empty_lists(self):
        assert keyword_similarity([], ["a"]) == 0.0
        assert keyword_similarity(["a"], []) == 0.0
        assert keyword_similarity([], []) == 0.0


class TestDecisionMemoryStore:
    def test_store_and_retrieve(self, memory_store):
        decision = _make_decision()
        record = memory_store.store_decision(
            decision, "Should we launch?", "Revenue growing"
        )
        assert record.request_id == "test-001"
        assert record.question == "Should we launch?"

        history = memory_store.get_history()
        assert len(history) == 1
        assert history[0].request_id == "test-001"

    def test_store_multiple(self, memory_store):
        for i in range(5):
            d = _make_decision(request_id=f"test-{i:03d}")
            memory_store.store_decision(d, f"Question {i}")
        history = memory_store.get_history()
        assert len(history) == 5

    def test_history_department_filter(self, memory_store):
        memory_store.store_decision(
            _make_decision("s-001", "Strategy"), "Q1"
        )
        memory_store.store_decision(
            _make_decision("f-001", "Finance"), "Q2"
        )
        strategy_history = memory_store.get_history(department="Strategy")
        assert len(strategy_history) == 1
        assert strategy_history[0].department == "Strategy"

    def test_find_similar(self, memory_store):
        memory_store.store_decision(
            _make_decision("p-001"),
            "Should we pivot from B2C to B2B?",
            "B2C growth flat",
        )
        memory_store.store_decision(
            _make_decision("h-001"),
            "Should we hire a senior engineer?",
            "Need ML expertise",
        )

        results = memory_store.find_similar("Should we pivot to enterprise B2B?")
        assert len(results) >= 1
        assert results[0].request_id == "p-001"

    def test_find_similar_empty_store(self, memory_store):
        results = memory_store.find_similar("anything")
        assert results == []

    def test_feedback(self, memory_store):
        decision = _make_decision()
        memory_store.store_decision(decision, "Test question")

        result = memory_store.add_feedback("test-001", True, "Worked out well")
        assert result is True

        history = memory_store.get_history()
        assert history[0].feedback_correct is True
        assert history[0].feedback_notes == "Worked out well"

    def test_feedback_nonexistent(self, memory_store):
        result = memory_store.add_feedback("nonexistent", True)
        assert result is False

    def test_agent_track_record(self, memory_store):
        decision = _make_decision()
        memory_store.store_decision(decision, "Test question")

        track = memory_store.get_agent_track_record("Visionary")
        assert track["total_decisions"] == 1
        assert track["agent_name"] == "Visionary"

    def test_agent_track_record_with_feedback(self, memory_store):
        decision = _make_decision()
        memory_store.store_decision(decision, "Test question")
        memory_store.add_feedback("test-001", True)

        track = memory_store.get_agent_track_record("Visionary")
        assert track["reviewed"] == 1
        assert track["correct"] == 1

    def test_agent_track_record_unknown(self, memory_store):
        track = memory_store.get_agent_track_record("NonexistentAgent")
        assert track["total_decisions"] == 0

    def test_upsert_on_duplicate(self, memory_store):
        d1 = _make_decision("dup-001", position="YES")
        memory_store.store_decision(d1, "First version")
        d2 = _make_decision("dup-001", position="NO")
        memory_store.store_decision(d2, "Updated version")

        history = memory_store.get_history()
        assert len(history) == 1
        assert history[0].question == "Updated version"


class TestBuildMemoryContext:
    def test_empty_inputs(self):
        assert build_memory_context([], None) == ""

    def test_with_similar_decisions(self):
        records = [
            DecisionRecord(
                request_id="past-001",
                question="Should we expand?",
                context=None,
                department="Strategy",
                outcome="MAJORITY",
                position="YES",
                confidence=0.8,
                summary="Team agrees to expand.",
                votes_json="[]",
                feedback_correct=True,
            ),
        ]
        ctx = build_memory_context(records)
        assert "Institutional Memory" in ctx
        assert "Should we expand?" in ctx
        assert "CORRECT" in ctx

    def test_with_track_record(self):
        track = {
            "agent_name": "Visionary",
            "total_decisions": 10,
            "reviewed": 8,
            "correct": 6,
            "incorrect": 2,
            "accuracy": 0.75,
            "avg_confidence": 0.82,
        }
        ctx = build_memory_context([], track)
        assert "Track Record" in ctx
        assert "75%" in ctx

    def test_low_accuracy_warning(self):
        track = {
            "agent_name": "BadAgent",
            "total_decisions": 10,
            "reviewed": 10,
            "correct": 3,
            "incorrect": 7,
            "accuracy": 0.3,
            "avg_confidence": 0.9,
        }
        ctx = build_memory_context([], track)
        assert "below 50%" in ctx

    def test_with_incorrect_decision(self):
        records = [
            DecisionRecord(
                request_id="past-002",
                question="Should we cut prices?",
                context=None,
                department="Finance",
                outcome="CONSENSUS",
                position="YES",
                confidence=0.95,
                summary="All agreed.",
                votes_json="[]",
                feedback_correct=False,
            ),
        ]
        ctx = build_memory_context(records)
        assert "INCORRECT" in ctx

    def test_limits_to_three_records(self):
        records = [
            DecisionRecord(
                request_id=f"past-{i}",
                question=f"Question {i}",
                context=None,
                department="Strategy",
                outcome="MAJORITY",
                position="YES",
                confidence=0.7,
                summary="Summary",
                votes_json="[]",
            )
            for i in range(5)
        ]
        ctx = build_memory_context(records)
        assert ctx.count("Question") == 3
