"""Example: Self-improving agents with the learning engine."""

import asyncio
from swarm_agency import Agency, AgencyRequest, create_strategy_dept
from swarm_agency import LearningEngine, Feedback

# Set up agency
agency = Agency(name="MyCo")
agency.add_department(create_strategy_dept())

learning = LearningEngine()

# Make a decision
request = AgencyRequest(
    request_id="learn-001",
    question="Should we enter the European market?",
    context="US market saturating. EU has GDPR compliance costs.",
)

decision = asyncio.run(agency.decide(request))
learning.record_decision(decision)

print(f"Decision: {decision.position} ({decision.outcome})")

# Later, when you know the outcome...
learning.apply_feedback(Feedback(
    request_id="learn-001",
    was_correct=True,
    correct_position=decision.position,
    notes="EU expansion was successful, 30% revenue increase",
))

# Check agent accuracy
stats = learning.get_all_stats()
for name, mem in stats.items():
    print(f"  {name}: {mem.accuracy:.0%} accuracy ({mem.total_decisions} decisions)")
