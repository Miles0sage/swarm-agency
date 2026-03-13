"""Example: Consult a single department."""

import asyncio
from swarm_agency import Agency, AgencyRequest, create_strategy_dept

agency = Agency(name="MyCo")
agency.add_department(create_strategy_dept())

request = AgencyRequest(
    request_id="s1",
    question="Should we raise a seed round or bootstrap?",
    context="$5k MRR, growing 20% MoM. Two term sheets on the table.",
    department="Strategy",
)

decision = asyncio.run(agency.decide(request))
print(f"\nStrategy Department says: {decision.position}")
print(f"Outcome: {decision.outcome} ({decision.confidence:.0%})")
print(f"\n{decision.summary}")

if decision.dissenting_views:
    print("\nDissenting views:")
    for d in decision.dissenting_views:
        print(f"  - {d}")
