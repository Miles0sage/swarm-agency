"""Basic example: Ask your AI agency a business question."""

import asyncio
from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

agency = Agency(name="MyCo")
for dept in create_full_agency_departments():
    agency.add_department(dept)

request = AgencyRequest(
    request_id="q1",
    question="Should we launch our MVP this week or wait for the redesign?",
    context="500 beta users. Competitor raised $10M. Team is burned out.",
)

decision = asyncio.run(agency.decide(request))
print(f"Outcome: {decision.outcome}")
print(f"Position: {decision.position}")
print(f"Confidence: {decision.confidence:.0%}")
print(f"Summary: {decision.summary}")
