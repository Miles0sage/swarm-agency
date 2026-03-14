"""Streamlit web UI for swarm-agency.

Run with: streamlit run app.py
No terminal knowledge needed — just open the browser.
"""

import streamlit as st

from swarm_agency.demos import DEMO_SCENARIOS, DEMO_LIST
from swarm_agency.types import Decision

# ── Page config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Swarm Agency — AI Board of Directors",
    page_icon="🏛️",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { max-width: 1100px; margin: 0 auto; }
    .agent-card {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .approve { border-left: 4px solid #22c55e; }
    .reject { border-left: 4px solid #ef4444; }
    .neutral { border-left: 4px solid #eab308; }
    .big-result {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ── Render functions ─────────────────────────────────────────────────

def _render_debate(question: str, context: str, department: str, decision: Decision):
    """Render a debate result with cards and vote breakdown."""

    # Question banner
    st.markdown(f"### {question}")
    if context:
        st.caption(f"Context: {context}")
    st.markdown(f"**Department:** {department} · **Agents:** {len(decision.votes)} · **Models:** 5")
    st.markdown("---")

    # Decision outcome — big banner
    outcome_colors = {
        "CONSENSUS": "green",
        "MAJORITY": "orange",
        "SPLIT": "red",
        "DEADLOCK": "gray",
    }
    outcome_emoji = {
        "CONSENSUS": "✅",
        "MAJORITY": "📊",
        "SPLIT": "⚖️",
        "DEADLOCK": "🔒",
    }
    color = outcome_colors.get(decision.outcome, "gray")
    emoji = outcome_emoji.get(decision.outcome, "")

    st.markdown(
        f'<div class="big-result" style="color: {color};">'
        f'{emoji} {decision.outcome}: {decision.position}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Confidence bar
    st.progress(decision.confidence, text=f"Overall confidence: {decision.confidence:.0%}")

    # Summary (escape $ to prevent LaTeX)
    st.markdown(f"**Summary:** {decision.summary.replace('$', '&#36;')}", unsafe_allow_html=True)
    st.markdown("---")

    # Agent deliberation cards
    st.subheader("Agent Deliberation")

    for vote in decision.votes:
        pos_class = vote.position.lower()
        if pos_class not in ("approve", "reject", "neutral"):
            pos_class = "neutral"

        pos_emoji = {"APPROVE": "👍", "REJECT": "👎", "NEUTRAL": "🤷"}.get(vote.position, "❓")

        with st.container():
            # Escape dollar signs to prevent Streamlit LaTeX rendering
            reasoning = vote.reasoning.replace("$", "&#36;")
            st.markdown(
                f'<div class="agent-card {pos_class}">'
                f'<strong>{vote.agent_name}</strong> · {pos_emoji} {vote.position} · '
                f'Confidence: {vote.confidence:.0%}'
                f'<br><span style="color: #888;">{reasoning}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Vote tally
    st.markdown("---")
    st.subheader("Vote Breakdown")

    counts = {}
    for vote in decision.votes:
        counts[vote.position] = counts.get(vote.position, 0) + 1

    tally_cols = st.columns(len(counts))
    position_colors = {"APPROVE": "green", "REJECT": "red", "NEUTRAL": "orange"}
    for i, (pos, count) in enumerate(counts.items()):
        with tally_cols[i]:
            st.metric(pos, count)

    # Dissenting views
    if decision.dissenting_views:
        st.markdown("---")
        st.subheader("Dissenting Views")
        for view in decision.dissenting_views:
            # Use HTML entity to fully prevent Streamlit LaTeX rendering
            escaped = view.replace("$", "&#36;")
            st.markdown(
                f'<div style="background-color: #2d2000; border-left: 4px solid #eab308; '
                f'padding: 12px 16px; border-radius: 4px; margin: 8px 0;">'
                f'{escaped}</div>',
                unsafe_allow_html=True,
            )


def _run_live_debate(
    question: str, context: str, department: str, api_key: str,
    rounds: int = 1, memory: bool = False, sports_mode: bool = False,
):
    """Run a live debate via the API."""
    import asyncio
    from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

    dept_filter = None if department == "All Departments" else department

    agency = Agency(name="WebUI", api_key=api_key.strip(), memory_enabled=memory)

    if sports_mode:
        from swarm_agency.sports import create_sports_departments
        for dept in create_sports_departments():
            agency.add_department(dept)
        agent_count = 10
        dept_count = 3
    else:
        for dept in create_full_agency_departments():
            agency.add_department(dept)
        agent_count = 43
        dept_count = 10

    import uuid
    request = AgencyRequest(
        request_id=f"web-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context or None,
        department=dept_filter,
    )

    label = f"{agent_count} agents across {dept_count} departments"
    if rounds > 1:
        label += f" ({rounds} rounds)"

    if rounds > 1:
        from swarm_agency.rounds import multi_round_debate
        with st.spinner(f"{label} deliberating..."):
            target_depts = list(agency.departments.values())
            if dept_filter and dept_filter in agency.departments:
                target_depts = [agency.departments[dept_filter]]
            # Run multi-round on first matching department
            decision, round_results = asyncio.run(
                multi_round_debate(target_depts[0], request, max_rounds=rounds)
            )
            st.info(f"Converged in {len(round_results)} round(s). "
                     + ", ".join(f"R{r.round_number}: {r.outcome}" for r in round_results))
    else:
        with st.spinner(f"{label} deliberating..."):
            decision = asyncio.run(agency.decide(request))

    _render_debate(question, context or "", department, decision)


# ── Header ───────────────────────────────────────────────────────────

st.title("Swarm Agency v0.5")
st.markdown("**43 AI personas debate your business decisions.** Multi-round debate, semantic memory, streaming, tool-calling. Pick a scenario or ask your own.")
st.markdown("---")

# ── Sidebar: mode selection ──────────────────────────────────────────

mode = st.sidebar.radio(
    "Mode",
    ["Try a Demo (no API key)", "Ask Your Own Question"],
    index=0,
)

# ── Demo mode ────────────────────────────────────────────────────────

if mode == "Try a Demo (no API key)":
    st.subheader("Pick a scenario")

    scenario_labels = {
        "startup-pivot": ("Pivot B2C → B2B?", "Strategy"),
        "hire-senior": ("Senior vs 2 Juniors?", "Engineering"),
        "pricing-change": ("Usage-Based Pricing?", "Finance"),
        "open-source": ("Open-Source Core?", "Engineering"),
        "remote-vs-office": ("Return to Office?", "Operations"),
    }

    cols = st.columns(len(DEMO_LIST))
    selected = None
    for i, name in enumerate(DEMO_LIST):
        label, dept = scenario_labels.get(name, (name, "?"))
        with cols[i]:
            if st.button(label, key=f"demo-{name}", use_container_width=True):
                selected = name

    if selected:
        st.session_state["selected_demo"] = selected
    chosen = st.session_state.get("selected_demo")

    if chosen:
        scenario = DEMO_SCENARIOS[chosen]
        _render_debate(
            question=scenario["question"],
            context=scenario["context"],
            department=scenario["department"],
            decision=scenario["decision"],
        )
    else:
        st.info("Click a scenario above to see 5 AI agents debate it.")

# ── Custom question mode ─────────────────────────────────────────────

else:
    st.subheader("Ask your board of directors")

    question = st.text_input(
        "Your question",
        placeholder="Should we raise a Series A or bootstrap?",
    )
    context = st.text_area(
        "Context (optional)",
        placeholder="Revenue $30k MRR, growing 15% m/m. 2 competing term sheets.",
        height=80,
    )
    col1, col2 = st.columns(2)
    with col1:
        department = st.selectbox(
            "Department",
            ["All Departments", "Strategy", "Product", "Marketing", "Research",
             "Finance", "Engineering", "Legal", "Operations", "Sales", "Creative"],
        )
    with col2:
        rounds = st.selectbox("Debate Rounds", [1, 2, 3], index=0, help="Multi-round: agents see others' votes and revise")

    # v0.5.0 features
    feat_cols = st.columns(3)
    with feat_cols[0]:
        use_memory = st.checkbox("Semantic Memory", help="Store decisions with embeddings for future reference")
    with feat_cols[1]:
        use_tools = st.checkbox("Agent Tools", help="Let agents use calculator, ROI analysis, etc.")
    with feat_cols[2]:
        use_sports = st.checkbox("Sports Mode", help="Use 10 sports-specific agents instead of business agents")

    # Template picker
    template = st.selectbox(
        "Use Template (optional)",
        ["None", "hire", "pricing", "launch", "vendor", "pivot"],
        help="Pre-built question formats for common decisions",
    )

    # Use server-side secret so visitors can test without their own key
    default_key = st.secrets.get("DASHSCOPE_API_KEY", "")
    has_default = bool(default_key)

    if has_default:
        st.success("API key provided — ready to debate. No key needed from you.")
        api_key_override = st.text_input(
            "Use your own API key instead (optional)",
            type="password",
            help="Leave blank to use the built-in key, or paste your own.",
        )
        api_key = api_key_override.strip() if api_key_override else default_key
    else:
        api_key = st.text_input(
            "DashScope API Key",
            type="password",
            help="Get one at dashscope.console.aliyun.com — $10/mo flat for unlimited debates.",
        )

    if st.button("Run Debate", type="primary", use_container_width=True):
        final_question = question
        final_context = context

        # Handle template
        if template and template != "None" and not question:
            st.error("Templates need field values. Use the CLI: swarm-agency --template hire --candidate Jane --role CTO")
            st.stop()

        if not final_question:
            st.error("Type a question first.")
        elif not api_key:
            st.error("Paste your DashScope API key to run live debates. Or try a demo scenario in the sidebar.")
        else:
            _run_live_debate(
                final_question, final_context, department, api_key,
                rounds=rounds, memory=use_memory, sports_mode=use_sports,
            )
