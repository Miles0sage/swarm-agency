"""Built-in demo scenarios with pre-computed realistic debates.

Run with: swarm-agency --demo [scenario]
No API key needed -- all responses are pre-generated.
"""

from .types import AgentVote, Decision

DEMO_SCENARIOS = {
    "startup-pivot": {
        "question": "Should we pivot from B2C to B2B?",
        "context": "B2C growth flat at 12k MAU for 6 months. Enterprise inbound up 3x. Team of 8. 14 months runway.",
        "department": "Strategy",
        "decision": Decision(
            request_id="demo-001",
            department="Strategy",
            outcome="MAJORITY",
            position="APPROVE",
            confidence=0.74,
            votes=[
                AgentVote(
                    agent_name="Visionary",
                    position="APPROVE",
                    confidence=0.88,
                    reasoning="B2B creates defensible revenue. Enterprise contracts = predictable ARR. B2C is a war of attrition we can't win at this scale.",
                    factors=["Enterprise ARR predictability", "B2C CAC unsustainable at current scale", "Defensible contracts vs viral dependency"],
                ),
                AgentVote(
                    agent_name="DevilsAdvocate",
                    position="REJECT",
                    confidence=0.76,
                    reasoning="Pivots kill startups more often than they save them. We have no enterprise sales motion, no SOC 2, no SLAs. We'd be starting from zero with 14 months runway.",
                    factors=["No enterprise sales infrastructure", "SOC 2 compliance gap", "Pivot execution risk with limited runway"],
                    dissent="We're romanticizing inbound interest. 3x of nothing is still nothing. Build the B2C moat first.",
                ),
                AgentVote(
                    agent_name="GrowthHacker",
                    position="APPROVE",
                    confidence=0.72,
                    reasoning="B2B ACV of $24k vs B2C LTV of $180. The math is obvious. 50 enterprise customers = $1.2M ARR. We need 6,700 B2C users for the same revenue.",
                    factors=["50x revenue per customer", "Shorter payback period", "Land-and-expand model fits product"],
                ),
                AgentVote(
                    agent_name="NumbersCruncher",
                    position="NEUTRAL",
                    confidence=0.41,
                    reasoning="The unit economics favor B2B but we have zero data on enterprise sales cycle length, churn, or implementation costs. Projecting ARR from 3 inbound emails is irresponsible.",
                    factors=["No enterprise churn data", "Implementation cost unknown", "Sales cycle length unvalidated"],
                ),
                AgentVote(
                    agent_name="Pragmatist",
                    position="APPROVE",
                    confidence=0.65,
                    reasoning="Hybrid approach: keep B2C running on autopilot, dedicate 5 of 8 engineers to B2B pilot. Test with 3 enterprise prospects over 90 days before full commitment.",
                    factors=["Hybrid reduces risk", "90-day pilot is reversible", "Team capacity allows parallel track"],
                ),
            ],
            summary="Strategy department recommends pivot with conditions. 3 approve (Visionary, GrowthHacker, Pragmatist), 1 rejects (DevilsAdvocate citing execution risk), 1 neutral (NumbersCruncher wanting data). Recommended: 90-day hybrid pilot before full commitment.",
            dissenting_views=[
                "DevilsAdvocate: No enterprise sales infrastructure exists. Pivoting without SOC 2, SLAs, or a sales team is a recipe for burning remaining runway.",
                "NumbersCruncher: Revenue projections based on 3 inbound inquiries are statistically meaningless. Need validated sales cycle and churn data.",
            ],
            duration_seconds=4.1,
        ),
    },
    "hire-senior": {
        "question": "Hire one senior engineer at $180k or two juniors at $85k each?",
        "context": "Series A startup. 6-person eng team. Building AI/ML product. Need to ship v2 in 4 months. Senior candidate has 12yr experience in our exact stack.",
        "department": "Engineering",
        "decision": Decision(
            request_id="demo-002",
            department="Engineering",
            outcome="MAJORITY",
            position="HIRE SENIOR",
            confidence=0.78,
            votes=[
                AgentVote(
                    agent_name="CTO",
                    position="HIRE SENIOR",
                    confidence=0.91,
                    reasoning="4-month deadline with AI/ML complexity. A senior ships production ML in week 2. Two juniors need 3 months of ramp before they're productive. We don't have time to mentor.",
                    factors=["Time-to-productivity critical", "AI/ML requires deep expertise", "Mentorship overhead on small team"],
                ),
                AgentVote(
                    agent_name="BackendLead",
                    position="HIRE SENIOR",
                    confidence=0.82,
                    reasoning="Our codebase has 40k lines of untyped Python with zero documentation. A senior can navigate that. Juniors will drown and introduce bugs we don't have time to fix.",
                    factors=["Undocumented codebase", "Bug introduction risk", "Self-directed navigation"],
                ),
                AgentVote(
                    agent_name="FrontendLead",
                    position="HIRE JUNIORS",
                    confidence=0.58,
                    reasoning="Two juniors give us more raw throughput for the UI work in v2. The frontend isn't complex -- it's volume. Senior is overkill for component work.",
                    factors=["UI work is volume-based", "Junior frontend devs ramp faster", "Senior overkill for component work"],
                    dissent="We're over-indexing on the ML side. Half of v2 is UI and two juniors ship more UI faster.",
                ),
                AgentVote(
                    agent_name="DevOps",
                    position="HIRE SENIOR",
                    confidence=0.75,
                    reasoning="Seniors understand deployment, monitoring, and incident response. We're about to 10x our inference traffic. I don't want to be paged at 3am because a junior misconfigured the GPU cluster.",
                    factors=["Production reliability at scale", "Infrastructure knowledge gap", "On-call capability"],
                ),
                AgentVote(
                    agent_name="SecurityEngineer",
                    position="HIRE SENIOR",
                    confidence=0.69,
                    reasoning="AI/ML products handle sensitive data. A senior understands threat modeling, data pipelines, and compliance from day one. Juniors will need security training we haven't built yet.",
                    factors=["Data handling compliance", "Threat modeling capability", "No security training program exists"],
                ),
            ],
            summary="Engineering department strongly favors hiring the senior (4-1). The 4-month deadline, AI/ML complexity, and undocumented codebase make seniority critical. One dissent from FrontendLead arguing UI volume work favors juniors.",
            dissenting_views=[
                "FrontendLead: Half of v2 is frontend components. Two juniors produce more UI output than one senior, and frontend work doesn't require ML expertise.",
            ],
            duration_seconds=3.8,
        ),
    },
    "pricing-change": {
        "question": "Should we switch from per-seat pricing to usage-based pricing?",
        "context": "B2B SaaS. $2.4M ARR. 180 customers. Average deal $13k/yr. Power users love us, but 60% of seats are inactive. Competitors moving to usage-based.",
        "department": "Finance",
        "decision": Decision(
            request_id="demo-003",
            department="Finance",
            outcome="SPLIT",
            position="HYBRID MODEL",
            confidence=0.52,
            votes=[
                AgentVote(
                    agent_name="CFO",
                    position="HYBRID MODEL",
                    confidence=0.67,
                    reasoning="Pure usage-based is revenue suicide with 60% inactive seats -- those customers are paying for seats they don't use and that's our margin. Hybrid: base platform fee + usage overage.",
                    factors=["60% inactive seats = free revenue at risk", "Hybrid preserves base ARR", "Usage component captures expansion"],
                ),
                AgentVote(
                    agent_name="RiskAnalyst",
                    position="KEEP PER-SEAT",
                    confidence=0.72,
                    reasoning="Usage-based revenue is inherently volatile. Our investors value predictable ARR. Switching models mid-growth will spook the board and complicate Series B narrative.",
                    factors=["Revenue predictability for Series B", "Board confidence risk", "Model transition volatility"],
                    dissent="We're solving a churn problem with a pricing change. Fix activation, not pricing.",
                ),
                AgentVote(
                    agent_name="RevenueStrategist",
                    position="USAGE-BASED",
                    confidence=0.74,
                    reasoning="Usage-based aligns our revenue with customer value. Power users currently subsidize inactive seats. Usage pricing unlocks expansion revenue -- our best customers would pay 2-3x more.",
                    factors=["Revenue-value alignment", "Expansion revenue from power users", "Competitive positioning"],
                ),
                AgentVote(
                    agent_name="TaxOptimizer",
                    position="HYBRID MODEL",
                    confidence=0.55,
                    reasoning="Revenue recognition is simpler with a base fee component. Pure usage-based creates ASC 606 complexity. Hybrid gives us the best of both for financial reporting.",
                    factors=["ASC 606 compliance simplicity", "Revenue recognition clarity", "Audit-friendly structure"],
                ),
                AgentVote(
                    agent_name="Auditor",
                    position="USAGE-BASED",
                    confidence=0.48,
                    reasoning="Per-seat pricing with 60% inactive seats is a retention time bomb. When those customers finally audit their spend, they'll churn. Better to right-size now than face a churn cliff.",
                    factors=["Inactive seat churn risk", "Customer audit exposure", "Proactive right-sizing"],
                ),
            ],
            summary="Finance department is SPLIT on pricing change. No consensus reached: 2 favor hybrid (CFO, TaxOptimizer), 2 favor usage-based (RevenueStrategist, Auditor), 1 wants to keep per-seat (RiskAnalyst). Core tension: predictable ARR vs customer value alignment.",
            dissenting_views=[
                "RiskAnalyst: This is a churn problem, not a pricing problem. Fix seat activation rates instead of rebuilding the entire pricing model before Series B.",
                "RevenueStrategist: Keeping per-seat pricing leaves 2-3x expansion revenue on the table from power users who would pay more under usage-based.",
            ],
            duration_seconds=4.6,
        ),
    },
    "open-source": {
        "question": "Should we open-source our core engine?",
        "context": "Dev tools startup. Core engine is our main product. 3 closed-source competitors. Community keeps asking for OSS. We'd monetize with cloud/enterprise tier.",
        "department": "Strategy",
        "decision": Decision(
            request_id="demo-004",
            department="Strategy",
            outcome="MAJORITY",
            position="APPROVE",
            confidence=0.71,
            votes=[
                AgentVote(
                    agent_name="Visionary",
                    position="APPROVE",
                    confidence=0.92,
                    reasoning="Open source is the dominant GTM for dev tools in 2026. Hashicorp, Elastic, MongoDB all proved the model. Community contributions reduce R&D costs. Cloud tier captures the value.",
                    factors=["Proven OSS business model for dev tools", "Community-driven R&D", "Cloud tier monetization"],
                ),
                AgentVote(
                    agent_name="DevilsAdvocate",
                    position="REJECT",
                    confidence=0.81,
                    reasoning="Hashicorp literally re-licensed because OSS wasn't working. AWS will clone your project, host it cheaper, and you'll get zero revenue. Open source is a gift to your competitors.",
                    factors=["AWS/cloud provider cloning risk", "Hashicorp BSL precedent", "IP exposure to competitors"],
                    dissent="Every OSS success story has 100 failures you never heard about because they went bankrupt giving away their product.",
                ),
                AgentVote(
                    agent_name="GrowthHacker",
                    position="APPROVE",
                    confidence=0.85,
                    reasoning="3 closed-source competitors = we're the only OSS option. That's instant differentiation. GitHub stars compound. Developer love is the best moat in dev tools.",
                    factors=["Only OSS player in market", "GitHub star compounding", "Developer community moat"],
                ),
                AgentVote(
                    agent_name="NumbersCruncher",
                    position="APPROVE",
                    confidence=0.58,
                    reasoning="Model works if cloud conversion rate hits 2-5% of OSS users. At 10k OSS users converting at 3% with $500/mo cloud plan = $1.8M ARR. Achievable in 18 months.",
                    factors=["2-5% conversion benchmark is standard", "18-month path to $1.8M ARR", "CAC drops to near-zero for OSS leads"],
                ),
                AgentVote(
                    agent_name="Pragmatist",
                    position="APPROVE",
                    confidence=0.62,
                    reasoning="Use AGPL or BSL license to prevent cloud provider cloning. Open the engine, keep the management plane proprietary. Ship OSS first, enterprise tier at 1k GitHub stars.",
                    factors=["AGPL/BSL prevents cloud cloning", "Phased release reduces risk", "Management plane stays proprietary"],
                ),
            ],
            summary="Strategy recommends open-sourcing with protective licensing (AGPL/BSL). 4 approve, 1 rejects. Key conditions: use AGPL to prevent cloud provider cloning, keep management plane proprietary, launch enterprise tier at 1k stars milestone.",
            dissenting_views=[
                "DevilsAdvocate: OSS success stories are survivorship bias. Hashicorp re-licensed, Elastic sued AWS, Redis went source-available. Open source is giving away your product to companies that will outspend you.",
            ],
            duration_seconds=3.9,
        ),
    },
    "remote-vs-office": {
        "question": "Should we enforce return-to-office 3 days a week?",
        "context": "150-person company. Fully remote since 2020. Engineering productivity metrics unchanged. CEO concerned about culture and collaboration. 30% of team hired remote-only with no relocation clause.",
        "department": "Operations",
        "decision": Decision(
            request_id="demo-005",
            department="Operations",
            outcome="MAJORITY",
            position="REJECT",
            confidence=0.76,
            votes=[
                AgentVote(
                    agent_name="COO",
                    position="REJECT",
                    confidence=0.79,
                    reasoning="30% of our team has no relocation clause. RTO means losing 45 people minimum. At $150k average fully-loaded cost per engineer, that's $2.7M in replacement costs plus 6 months of lost productivity.",
                    factors=["45 employees can't relocate", "$2.7M replacement cost", "6-month productivity gap per replacement"],
                ),
                AgentVote(
                    agent_name="HRDirector",
                    position="REJECT",
                    confidence=0.85,
                    reasoning="RTO mandates are the #1 driver of attrition in tech. Our Glassdoor rating will tank. We'll lose senior talent first because they have the most options. Mandate 'collaboration days' instead -- 4 per month, optional.",
                    factors=["Attrition acceleration", "Senior talent flight risk", "Glassdoor/employer brand damage"],
                    dissent="If you want culture, invest in offsites and team events. Mandating desk-sitting isn't culture.",
                ),
                AgentVote(
                    agent_name="ProcessEngineer",
                    position="NEUTRAL",
                    confidence=0.52,
                    reasoning="Productivity metrics are unchanged, but we're not measuring collaboration quality. Cross-team projects take 40% longer than pre-remote. The data is incomplete.",
                    factors=["Cross-team velocity decline", "Collaboration metrics missing", "Incomplete data for decision"],
                ),
                AgentVote(
                    agent_name="SupplyChain",
                    position="REJECT",
                    confidence=0.71,
                    reasoning="We closed 2 of 3 offices in 2022. Reopening costs $800k in leases plus $200k in buildout. For a 3-day mandate we'd need 60% of peak capacity. The real estate math doesn't work.",
                    factors=["$1M office reopening cost", "Lease commitment risk", "Underutilized space 2 days/week"],
                ),
            ],
            summary="Operations strongly rejects RTO mandate (3-0-1). The 30% remote-only workforce, $2.7M attrition replacement cost, and $1M office reopening cost make this economically destructive. Alternative: quarterly offsites + optional monthly collaboration days.",
            dissenting_views=[
                "ProcessEngineer: We can't prove remote is working because we never measured collaboration quality. Cross-team projects are 40% slower. Before rejecting RTO, get better data.",
            ],
            duration_seconds=3.4,
        ),
    },
}

# Ordered list for --demo without argument
DEMO_LIST = ["startup-pivot", "hire-senior", "pricing-change", "open-source", "remote-vs-office"]
