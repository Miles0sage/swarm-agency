"""Streamlit web UI for swarm-agency v1.0.

Pressure-test any decision from multiple AI perspectives.
Run with: streamlit run app.py
"""

import asyncio
import json
import uuid

import streamlit as st

from swarm_agency.demos import DEMO_SCENARIOS, DEMO_LIST
from swarm_agency.types import Decision, AgentVote
from swarm_agency.verdict import decision_to_verdict, Verdict

# ── Page config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Swarm Agency — Pressure-Test Your Decisions",
    page_icon="⚡",
    layout="centered",
)

# ── CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .verdict-box {
        text-align: center; padding: 24px; border-radius: 16px;
        margin: 16px 0; font-size: 1.1rem;
    }
    .verdict-yes { background: #0d3320; border: 2px solid #22c55e; }
    .verdict-no { background: #3b1114; border: 2px solid #ef4444; }
    .verdict-maybe { background: #3b2f08; border: 2px solid #eab308; }
    .verdict-answer { font-size: 2.5rem; font-weight: bold; }
    .reason-card {
        padding: 12px 16px; margin: 6px 0; border-radius: 8px;
        background: #1a1a2e; border-left: 3px solid #444;
    }
    .risk-card {
        padding: 12px 16px; margin: 6px 0; border-radius: 8px;
        background: #2d1f00; border-left: 3px solid #eab308;
    }
    .agent-row {
        padding: 8px 12px; margin: 4px 0; border-radius: 6px;
        background: #111827; font-size: 0.9rem;
    }
    .vote-bar { display: flex; height: 24px; border-radius: 6px; overflow: hidden; margin: 8px 0; }
    .vote-yes { background: #22c55e; }
    .vote-no { background: #ef4444; }
    .vote-maybe { background: #eab308; }
</style>
""", unsafe_allow_html=True)


def _esc(text: str) -> str:
    """Escape dollar signs to prevent Streamlit LaTeX rendering."""
    return text.replace("$", "&#36;")


# ── Render verdict ───────────────────────────────────────────────────

def _render_verdict(question: str, context: str, decision: Decision, show_agents: bool = False):
    """Render the clean verdict view — what users actually want to see."""
    verdict = decision_to_verdict(decision)

    # Answer colors
    color_class = {"YES": "verdict-yes", "NO": "verdict-no"}.get(verdict.answer, "verdict-maybe")
    color_hex = {"YES": "#22c55e", "NO": "#ef4444"}.get(verdict.answer, "#eab308")

    # Big verdict banner
    st.markdown(
        f'<div class="verdict-box {color_class}">'
        f'<div class="verdict-answer" style="color: {color_hex};">{verdict.answer}</div>'
        f'<div style="color: #aaa;">{verdict.confidence_label} confidence &middot; {verdict.confidence:.0%}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # One-liner
    st.markdown(f"**{_esc(verdict.one_liner)}**")

    # Vote bar
    total = verdict.agents_for + verdict.agents_against + verdict.agents_undecided
    if total > 0:
        pct_yes = verdict.agents_for / total * 100
        pct_no = verdict.agents_against / total * 100
        pct_maybe = verdict.agents_undecided / total * 100
        st.markdown(
            f'<div class="vote-bar">'
            f'<div class="vote-yes" style="width:{pct_yes}%"></div>'
            f'<div class="vote-no" style="width:{pct_no}%"></div>'
            f'<div class="vote-maybe" style="width:{pct_maybe}%"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#888;">'
            f'<span>🟢 {verdict.agents_for} for</span>'
            f'<span>🔴 {verdict.agents_against} against</span>'
            f'<span>🟡 {verdict.agents_undecided} undecided</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Top reasons
    if verdict.top_reasons:
        st.markdown("#### Why")
        for i, reason in enumerate(verdict.top_reasons, 1):
            st.markdown(
                f'<div class="reason-card"><strong>{i}.</strong> {_esc(reason)}</div>',
                unsafe_allow_html=True,
            )

    # Top risk
    st.markdown("#### Top Risk")
    st.markdown(
        f'<div class="risk-card">⚠️ {_esc(verdict.top_risk)}</div>',
        unsafe_allow_html=True,
    )

    # Expandable: full agent deliberation
    if show_agents and decision.votes:
        with st.expander(f"See all {len(decision.votes)} agent votes", expanded=False):
            for vote in decision.votes:
                pos_emoji = {"YES": "🟢", "APPROVE": "🟢", "NO": "🔴", "REJECT": "🔴"}.get(
                    vote.position.upper(), "🟡"
                )
                reasoning = _esc(vote.reasoning[:200])
                st.markdown(
                    f'<div class="agent-row">'
                    f'{pos_emoji} <strong>{vote.agent_name}</strong> '
                    f'&middot; {vote.position} &middot; {vote.confidence:.0%}'
                    f'<br><span style="color:#888;">{reasoning}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Dissenting views
        if decision.dissenting_views:
            with st.expander("Dissenting views", expanded=False):
                for view in decision.dissenting_views:
                    st.markdown(
                        f'<div class="risk-card">{_esc(view)}</div>',
                        unsafe_allow_html=True,
                    )

    st.caption(f"{verdict.debate_quality} · {len(decision.votes)} agents · {verdict.duration:.1f}s · swarm-agency v1.0")


# ── Run live debate ──────────────────────────────────────────────────

def _run_live(question: str, context: str, department: str, api_key: str, provider: str = "dashscope"):
    """Run a live debate and show the verdict."""
    from swarm_agency import Agency, AgencyRequest, create_full_agency_departments

    dept_filter = None if department == "All Departments" else department

    agency = Agency(name="WebUI", api_key=api_key.strip(), provider=provider)
    for dept in create_full_agency_departments():
        agency.add_department(dept)

    request = AgencyRequest(
        request_id=f"web-{uuid.uuid4().hex[:8]}",
        question=question,
        context=context or None,
        department=dept_filter,
    )

    with st.spinner("Agents are debating your question across multiple AI models..."):
        decision = asyncio.run(agency.decide(request))

    _render_verdict(question, context or "", decision, show_agents=True)


# ── Main UI ──────────────────────────────────────────────────────────

st.markdown("# ⚡ Swarm Agency")
st.markdown("**Pressure-test any decision from multiple AI perspectives in under a minute.**")

tab_demo, tab_live = st.tabs(["Try a Demo", "Ask Your Own"])

# ── Demo tab ─────────────────────────────────────────────────────────

with tab_demo:
    st.markdown("Pick a scenario — no API key needed:")

    scenario_labels = {
        "startup-pivot": ("🔄 Pivot B2C → B2B?", "Strategy"),
        "hire-senior": ("👤 Senior vs 2 Juniors?", "Engineering"),
        "pricing-change": ("💰 Usage-Based Pricing?", "Finance"),
        "open-source": ("📖 Open-Source Core?", "Strategy"),
        "remote-vs-office": ("🏢 Return to Office?", "Operations"),
    }

    cols = st.columns(len(DEMO_LIST))
    for i, name in enumerate(DEMO_LIST):
        label, dept = scenario_labels.get(name, (name, "?"))
        with cols[i]:
            if st.button(label, key=f"demo-{name}", use_container_width=True):
                st.session_state["selected_demo"] = name

    chosen = st.session_state.get("selected_demo")
    if chosen:
        scenario = DEMO_SCENARIOS[chosen]
        st.markdown(f"**Question:** {scenario['question']}")
        st.caption(f"Context: {scenario['context']}")
        _render_verdict(
            scenario["question"], scenario["context"],
            scenario["decision"], show_agents=True,
        )
    else:
        st.info("Click a scenario above to see AI agents debate it.")

# ── Live debate tab ──────────────────────────────────────────────────

with tab_live:
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
        provider = st.selectbox(
            "AI Models",
            ["dashscope", "openrouter"],
            help="dashscope = Chinese models ($10/mo flat). openrouter = Western models (pay-per-use).",
        )

    # API key handling
    default_key = ""
    try:
        default_key = st.secrets.get("DASHSCOPE_API_KEY", "")
        if provider == "openrouter":
            default_key = st.secrets.get("OPENROUTER_API_KEY", "") or default_key
    except Exception:
        pass

    if default_key:
        st.success("API key configured — ready to debate.")
        api_key = default_key
    else:
        env_label = "OPENROUTER_API_KEY" if provider == "openrouter" else "ALIBABA_CODING_API_KEY"
        api_key = st.text_input(
            f"{env_label}",
            type="password",
            help="Or try the Demo tab — no key needed.",
        )

    if st.button("Run Debate", type="primary", use_container_width=True):
        if not question:
            st.error("Type a question first.")
        elif not api_key:
            st.error("API key required for live debates. Try the Demo tab instead.")
        else:
            _run_live(question, context, department, api_key, provider)
