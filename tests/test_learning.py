"""Tests for the learning engine."""

import json
import tempfile
import os

from swarm_agency.types import AgentVote, Decision
from swarm_agency.learning import LearningEngine, Feedback


def _decision(votes=None):
    if votes is None:
        votes = [
            AgentVote(agent_name="A", position="YES", confidence=0.8, reasoning="R", factors=["f1"]),
            AgentVote(agent_name="B", position="NO", confidence=0.6, reasoning="R", factors=["f2"]),
        ]
    return Decision(
        request_id="d1", department="Test", outcome="MAJORITY",
        position="YES", confidence=0.7, votes=votes, summary="Test",
    )


class TestLearningEngine:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.engine = LearningEngine(memory_dir=self.tmpdir)

    def test_record_decision(self):
        decision = _decision()
        self.engine.record_decision(decision)
        path = os.path.join(self.tmpdir, "decision_d1.json")
        assert os.path.exists(path)
        data = json.loads(open(path).read())
        assert data["request_id"] == "d1"

    def test_apply_feedback_correct(self):
        decision = _decision()
        feedback = Feedback(
            request_id="d1", was_correct=True, correct_position="YES",
        )
        learnings = self.engine.apply_feedback(feedback, decision)
        assert "A" in learnings
        assert "B" in learnings

        stats_a = self.engine.get_agent_stats("A")
        assert stats_a.total_decisions == 1
        assert stats_a.correct_decisions == 1
        assert stats_a.accuracy == 1.0

        stats_b = self.engine.get_agent_stats("B")
        assert stats_b.correct_decisions == 0

    def test_apply_feedback_wrong(self):
        decision = _decision()
        feedback = Feedback(
            request_id="d1", was_correct=False, correct_position="NO",
        )
        learnings = self.engine.apply_feedback(feedback, decision)

        stats_a = self.engine.get_agent_stats("A")
        assert stats_a.correct_decisions == 0  # A said YES but correct was NO

        stats_b = self.engine.get_agent_stats("B")
        assert stats_b.correct_decisions == 1  # B said NO which was correct

    def test_persistence(self):
        decision = _decision()
        feedback = Feedback(request_id="d1", was_correct=True, correct_position="YES")
        self.engine.apply_feedback(feedback, decision)

        # Load a fresh engine from same dir
        engine2 = LearningEngine(memory_dir=self.tmpdir)
        stats = engine2.get_agent_stats("A")
        assert stats is not None
        assert stats.total_decisions == 1

    def test_get_all_stats(self):
        decision = _decision()
        feedback = Feedback(request_id="d1", was_correct=True, correct_position="YES")
        self.engine.apply_feedback(feedback, decision)

        all_stats = self.engine.get_all_stats()
        assert len(all_stats) == 2
        assert "A" in all_stats
        assert "B" in all_stats

    def test_suggest_amendment_not_enough_data(self):
        result = self.engine.suggest_prompt_amendment("A")
        assert result is None

    def test_suggest_amendment_low_accuracy(self):
        decision = _decision()
        for i in range(6):
            feedback = Feedback(
                request_id=f"d{i}", was_correct=False, correct_position="NO",
            )
            d = Decision(
                request_id=f"d{i}", department="T", outcome="M",
                position="YES", confidence=0.7,
                votes=[AgentVote(agent_name="A", position="YES", confidence=0.8, reasoning="R", factors=["f1"])],
                summary="T",
            )
            self.engine.apply_feedback(feedback, d)

        amendment = self.engine.suggest_prompt_amendment("A")
        assert amendment is not None
        assert "accuracy" in amendment.lower()


class TestEvolveAgent:
    def test_evolve_with_enough_data(self):
        tmpdir = tempfile.mkdtemp()
        engine = LearningEngine(memory_dir=tmpdir)

        from swarm_agency.types import AgentConfig
        agent = AgentConfig(
            name="A", role="R", expertise="E", bias="B",
            system_prompt="Original prompt.",
        )

        # Not enough data — should return same agent
        evolved = engine.evolve_agent(agent)
        assert evolved.system_prompt == "Original prompt."

        # Add enough bad decisions
        for i in range(6):
            d = Decision(
                request_id=f"d{i}", department="T", outcome="M",
                position="YES", confidence=0.7,
                votes=[AgentVote(agent_name="A", position="YES", confidence=0.8, reasoning="R", factors=["speed"])],
                summary="T",
            )
            engine.apply_feedback(
                Feedback(request_id=f"d{i}", was_correct=False, correct_position="NO"), d
            )

        evolved = engine.evolve_agent(agent)
        assert "Learnings" in evolved.system_prompt
        assert evolved.name == "A"  # identity preserved
