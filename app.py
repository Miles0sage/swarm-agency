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


def _run_live_debate(question: str, context: str, department: str, api_key: str):
    """Run a live debate via the API."""
    import asyncio
    from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

    dept_filter = None if department == "All Departments" else department

    agency = Agency(name="WebUI", api_key=api_key.strip())
    for dept in create_full_agency_departments():
        agency.add_department(dept)

    import uuid
    request = AgencyRequest(
        request_id=f"web-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context or None,
        department=dept_filter,
    )

    with st.spinner("5 AI agents are debating your question across 5 different models..."):
        decision = asyncio.run(agency.decide(request))

    _render_debate(question, context or "", department, decision)


# ── Header ───────────────────────────────────────────────────────────

st.title("Swarm Agency")
st.markdown("**43 AI personas debate your business decisions.** Pick a scenario below or type your own question.")
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
    department = st.selectbox(
        "Department",
        ["All Departments", "Strategy", "Product", "Marketing", "Research",
         "Finance", "Engineering", "Legal", "Operations", "Sales", "Creative"],
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
        if not question:
            st.error("Type a question first.")
        elif not api_key:
            st.error("Paste your DashScope API key to run live debates. Or try a demo scenario in the sidebar.")
        else:
            _run_live_debate(question, context, department, api_key)
