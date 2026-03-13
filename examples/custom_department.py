"""Example: Build a custom Sales department with your own agents."""

import asyncio
from swarm_agency import Agency, Department, AgentConfig, AgencyRequest


sales_dept = Department(
    name="Sales",
    agents=[
        AgentConfig(
            name="Closer",
            role="VP Sales",
            expertise="enterprise sales, deal negotiation, pipeline management",
            bias="always be closing — revenue now, relationships later",
            system_prompt=(
                "You are an aggressive VP of Sales. You optimize for deal velocity "
                "and revenue growth. You push for action and commitment. "
                "Always respond with valid JSON matching the requested format."
            ),
            model="qwen3-coder-plus",
        ),
        AgentConfig(
            name="RelationshipBuilder",
            role="Account Manager",
            expertise="customer success, retention, upselling, NPS",
            bias="long-term relationships over quick wins",
            system_prompt=(
                "You are a relationship-focused Account Manager. You prioritize "
                "customer satisfaction and long-term value over short-term revenue. "
                "Always respond with valid JSON matching the requested format."
            ),
            model="glm-4.7",
        ),
        AgentConfig(
            name="SalesAnalyst",
            role="Sales Operations",
            expertise="CRM data, conversion rates, sales cycle analysis, forecasting",
            bias="data over gut feel — show me the numbers",
            system_prompt=(
                "You are a data-driven Sales Operations analyst. You make decisions "
                "based on pipeline metrics, conversion rates, and historical data. "
                "Always respond with valid JSON matching the requested format."
            ),
            model="kimi-k2.5",
        ),
    ],
    threshold=0.6,
)

agency = Agency(name="MyCo")
agency.add_department(sales_dept)

request = AgencyRequest(
    request_id="sales-001",
    question="Should we offer a 30% discount to close Enterprise Corp this quarter?",
    context="$500K deal. They're comparing us to a competitor. Q4 target is $2M, we're at $1.4M.",
    department="Sales",
)

decision = asyncio.run(agency.decide(request))
print(f"Sales says: {decision.position} ({decision.outcome})")
print(f"Confidence: {decision.confidence:.0%}")
print(f"\n{decision.summary}")
for vote in decision.votes:
    print(f"\n  {vote.agent_name}: {vote.position} ({vote.confidence:.0%})")
    print(f"    {vote.reasoning}")
