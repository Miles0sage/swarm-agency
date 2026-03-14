"""Tests for the Agent Soul system."""

import os
import tempfile

import pytest

from swarm_agency.soul import (
    Belief,
    Episode,
    AgentSoul,
    SoulStore,
    format_soul_context,
    initialize_default_voices,
    DEFAULT_VOICES,
)


@pytest.fixture
def store(tmp_path):
    db_path = str(tmp_path / "soul_test.db")
    s = SoulStore(db_path=db_path)
    yield s
    s.close()


class TestBelief:
    def test_store_and_retrieve(self, store):
        b = Belief(subject="pricing", predicate="should_be_value_based", confidence=0.8,
                   source_request_id="r1")
        store.store_belief("Visionary", b)
        beliefs = store.get_beliefs("Visionary")
        assert len(beliefs) == 1
        assert beliefs[0].subject == "pricing"
        assert beliefs[0].confidence == pytest.approx(0.8)

    def test_reinforcement_updates_confidence(self, store):
        b1 = Belief(subject="growth", predicate="matters_most", confidence=0.7)
        store.store_belief("GrowthHacker", b1)

        b2 = Belief(subject="growth", predicate="matters_most", confidence=0.9)
        store.store_belief("GrowthHacker", b2)

        beliefs = store.get_beliefs("GrowthHacker")
        assert len(beliefs) == 1
        # Confidence should have moved toward 0.9
        assert beliefs[0].confidence > 0.7
        assert beliefs[0].times_reinforced == 1

    def test_contradiction_lowers_confidence(self, store):
        b = Belief(subject="risk", predicate="is_manageable", confidence=0.8)
        store.store_belief("CFO", b)
        store.contradict_belief("CFO", "risk", "is_manageable")

        beliefs = store.get_beliefs("CFO")
        assert beliefs[0].confidence < 0.8
        assert beliefs[0].times_contradicted == 1

    def test_min_confidence_filter(self, store):
        b1 = Belief(subject="a", predicate="strong", confidence=0.9)
        b2 = Belief(subject="b", predicate="weak", confidence=0.2)
        store.store_belief("Agent", b1)
        store.store_belief("Agent", b2)

        beliefs = store.get_beliefs("Agent", min_confidence=0.5)
        assert len(beliefs) == 1
        assert beliefs[0].subject == "a"

    def test_empty_beliefs(self, store):
        beliefs = store.get_beliefs("Nonexistent")
        assert beliefs == []


class TestEpisode:
    def test_store_and_retrieve(self, store):
        ep = Episode(
            request_id="ep-1", question="Should we pivot?",
            agent_position="YES", agent_confidence=0.85,
            agent_reasoning="Market signals are strong",
            decision_outcome="MAJORITY", decision_position="YES",
            was_correct=True, timestamp=1000.0,
            lesson="My market analysis was on point",
        )
        store.store_episode("Visionary", ep)

        episodes = store.get_episodes("Visionary")
        assert len(episodes) == 1
        assert episodes[0].question == "Should we pivot?"
        assert episodes[0].was_correct is True
        assert episodes[0].lesson == "My market analysis was on point"

    def test_multiple_episodes_ordered_by_time(self, store):
        for i in range(5):
            ep = Episode(
                request_id=f"ep-{i}", question=f"Q{i}",
                agent_position="YES", agent_confidence=0.5,
                agent_reasoning="reason", decision_outcome="MAJORITY",
                decision_position="YES", was_correct=None,
                timestamp=1000.0 + i,
            )
            store.store_episode("Agent", ep)

        episodes = store.get_episodes("Agent", limit=3)
        assert len(episodes) == 3
        # Most recent first
        assert episodes[0].request_id == "ep-4"


class TestReflections:
    def test_store_and_retrieve(self, store):
        store.store_reflection("Visionary", "I tend to be overconfident about market timing")
        store.store_reflection("Visionary", "My cost estimates are consistently too low")

        reflections = store.get_reflections("Visionary")
        assert len(reflections) == 2
        assert "overconfident" in reflections[0] or "cost estimates" in reflections[0]


class TestVoice:
    def test_set_and_get(self, store):
        store.set_voice("CFO", "Conservative speaker", "cautious")
        voice, temperament = store.get_voice("CFO")
        assert voice == "Conservative speaker"
        assert temperament == "cautious"

    def test_missing_voice(self, store):
        voice, temperament = store.get_voice("Unknown")
        assert voice == ""
        assert temperament == ""

    def test_default_voices(self, store):
        initialize_default_voices(store)
        voice, temp = store.get_voice("Visionary")
        assert "5 years" in voice or "bigger picture" in voice
        assert temp == "enthusiastic"

        voice, temp = store.get_voice("DevilsAdvocate")
        assert "contrarian" in voice.lower() or "push back" in voice.lower()
        assert temp == "confrontational"


class TestComputeSoul:
    def test_computes_from_data(self, store):
        # Add some data
        store.store_belief("Visionary", Belief("growth", "is_essential", 0.9))
        store.store_episode("Visionary", Episode(
            request_id="s1", question="Pivot?", agent_position="YES",
            agent_confidence=0.9, agent_reasoning="Strong signals",
            decision_outcome="MAJORITY", decision_position="YES",
            was_correct=True, timestamp=1000.0,
        ))
        store.store_reflection("Visionary", "I have strong market intuition")
        store.set_voice("Visionary", "Visionary speaker", "enthusiastic")

        track = {"reviewed": 5, "accuracy": 0.8, "avg_confidence": 0.75}
        soul = store.compute_soul("Visionary", track)

        assert soul.agent_name == "Visionary"
        assert len(soul.beliefs) >= 1
        assert len(soul.episodes) >= 1
        assert soul.voice == "Visionary speaker"
        assert soul.temperament == "enthusiastic"
        assert "strong" in soul.personality_note.lower() or "conviction" in soul.personality_note.lower()

    def test_empty_soul(self, store):
        soul = store.compute_soul("NewAgent")
        assert soul.agent_name == "NewAgent"
        assert soul.beliefs == []
        assert soul.episodes == []
        assert soul.personality_note == ""


class TestFormatSoulContext:
    def test_formats_with_data(self, store):
        store.store_belief("V", Belief("cost", "matters", 0.85))
        store.store_episode("V", Episode(
            request_id="f1", question="Cut costs?", agent_position="YES",
            agent_confidence=0.8, agent_reasoning="Revenue falling",
            decision_outcome="MAJORITY", decision_position="YES",
            was_correct=True, timestamp=1000.0, lesson="Cost cuts worked",
        ))
        store.set_voice("V", "Quantitative speaker", "analytical")

        soul = store.compute_soul("V", {"reviewed": 10, "accuracy": 0.7, "avg_confidence": 0.8})
        ctx = format_soul_context(soul)

        assert "Quantitative speaker" in ctx
        assert "Memories" in ctx
        assert "Cut costs?" in ctx
        assert "Convictions" in ctx
        assert "Track Record" in ctx

    def test_empty_soul_returns_empty(self):
        soul = AgentSoul(
            agent_name="Empty", beliefs=[], episodes=[],
            strengths=[], weaknesses=[], track_record={},
            personality_note="",
        )
        ctx = format_soul_context(soul)
        assert ctx == ""

    def test_includes_lesson(self, store):
        store.store_episode("V", Episode(
            request_id="l1", question="Hire?",
            agent_position="NO", agent_confidence=0.6,
            agent_reasoning="Too expensive",
            decision_outcome="MAJORITY", decision_position="YES",
            was_correct=False, timestamp=1000.0,
            lesson="I underestimated the value of senior hires",
        ))
        soul = store.compute_soul("V")
        ctx = format_soul_context(soul)
        assert "underestimated" in ctx
