import html
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from connections import shared_tag_links  # noqa: E402
import streamlit.components.v1 as components  # noqa: E402
from viz3d import network_3d_html  # noqa: E402
from llm import LLMError, ask_gemini, load_key  # noqa: E402
from planner import PlanError, build_plan  # noqa: E402
from qloo_client import QlooError, live_search, mock_search, normalize_search  # noqa: E402

st.set_page_config(page_title="CultureMix", page_icon="🎶", layout="wide")

CSS = """
<style>
.hero {font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0;}
.sub {color: #6b7280; margin-top: 0.2rem; margin-bottom: 1.2rem;}
.badge {display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; margin-right: 6px;}
.b-qloo {background: #d1fae5; color: #065f46;}
.b-mock {background: #e5e7eb; color: #374151;}
.b-hyp {background: #fef3c7; color: #92400e;}
.card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;}
.muted {color: #6b7280; font-size: 0.9rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

BADGES = {
    "qloo": '<span class="badge b-qloo">Qloo-backed</span>',
    "mock": '<span class="badge b-mock">Mock, not Qloo</span>',
    "hypothesis": '<span class="badge b-hyp">LLM hypothesis</span>',
}


def load_secrets_into_env() -> None:
    for name in ("QLOO_API_KEY", "GEMINI_API_KEY"):
        try:
            if name in st.secrets and not os.environ.get(name):
                os.environ[name] = st.secrets[name]
        except Exception:
            pass


def run_pipeline(brief: dict, qloo_live: bool, compare: bool) -> dict:
    if qloo_live:
        raw = live_search(brief["interest"], "urn:entity:artist")
    else:
        raw = mock_search(brief["interest"], "artist")
    evidence = normalize_search(raw, live=qloo_live)
    if not evidence:
        raise ValueError("Qloo returned no usable entities. Try an artist name, such as Daft Punk.")
    if not load_key("GEMINI_API_KEY"):
        raise LLMError("GEMINI_API_KEY is not set. Add it to .env or Streamlit Secrets.")
    result = build_plan(brief, evidence, ask_gemini)
    out = {"brief": brief, "qloo_live": qloo_live, "evidence": evidence, **result}
    if compare:
        try:
            out["baseline"] = build_plan(brief, [], ask_gemini)["plan"]
        except PlanError as exc:
            out["baseline_error"] = str(exc)
    return out


def build_graph(res: dict) -> str:
    def esc(text) -> str:
        return str(text).replace('"', "'")

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'graph [bgcolor="transparent"];',
        'node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#9ca3af"];',
        'edge [color="#6b7280" fontname="Helvetica" fontsize=9];',
        f'brief [label="{esc(res["brief"]["interest"])}\\n{esc(res["brief"]["city"])}" fillcolor="#dbeafe"];',
    ]
    ids = {}
    for i, e in enumerate(res["evidence"]):
        nid = f"e{i}"
        ids[e["name"]] = nid
        color = "#d1fae5" if e["source"] == "qloo" else "#e5e7eb"
        lines.append(f'{nid} [label="{esc(e["name"])}" fillcolor="{color}"];')
        edge_label = "Qloo" if e["source"] == "qloo" else "mock"
        lines.append(f'brief -> {nid} [label="{edge_label}"];')
    for link in shared_tag_links(res["evidence"]):
        label = esc(", ".join(link["shared"][:2]))
        lines.append(f'{ids[link["a"]]} -> {ids[link["b"]]} [dir=none label="{label}" color="#059669" penwidth=2];')
    for j, r in enumerate(res["plan"]["recommendations"]):
        rid = f"r{j}"
        name = esc(r["name"])
        if r["source"] == "hypothesis":
            lines.append(f'{rid} [label="{name}" fillcolor="#fef3c7" style="rounded,filled,dashed"];')
            lines.append(f"brief -> {rid} [style=dashed];")
        else:
            lines.append(f'{rid} [label="{name}" fillcolor="#ffffff"];')
            if r["name"] in ids:
                lines.append(f"{ids[r['name']]} -> {rid};")
    lines.append("}")
    return "\n".join(lines)


def render(res: dict) -> None:
    plan = res["plan"]
    tabs = st.tabs(["Concept", "Connections", "Evidence", "Compare", "Schedule", "Budget", "Assumptions"])
    tab_concept, tab_graph, tab_evidence, tab_compare, tab_schedule, tab_budget, tab_notes = tabs

    with tab_concept:
        st.markdown(
            f'<div class="card"><div class="muted">Concept</div>'
            f'<div style="font-size:1.15rem;margin-top:4px">{html.escape(plan["concept"])}</div></div>',
            unsafe_allow_html=True,
        )
        st.subheader("Recommendations")
        for r in plan["recommendations"]:
            st.markdown(
                f'<div class="card"><b>{html.escape(r["name"])}</b> '
                f'<span class="muted">{html.escape(str(r.get("type", "")))}</span><br>'
                f'{BADGES[r["source"]]}<br>'
                f'<span>{html.escape(str(r.get("reason", "")))}</span></div>',
                unsafe_allow_html=True,
            )

    with tab_graph:
        links = shared_tag_links(res["evidence"])
        components.html(network_3d_html(res["evidence"], links), height=520)
        st.caption(f"{len(links)} Qloo tag connection(s). Drag to rotate, scroll to zoom. Green lines are shared Qloo tags.")
        with st.expander("2D diagram"):
            st.graphviz_chart(build_graph(res))

    with tab_evidence:
        st.dataframe(pd.DataFrame(res["evidence"]), hide_index=True)

    with tab_compare:
        st.caption("Same brief, with and without Qloo evidence.")
        left, right = st.columns(2)
        with left:
            st.markdown("**With Qloo evidence**")
            st.write(plan["concept"])
            for r in plan["recommendations"]:
                st.markdown(f"- {r['name']} · `{r['source']}`")
        with right:
            st.markdown("**Plain LLM, no Qloo**")
            if res.get("baseline_error"):
                st.warning(res["baseline_error"])
            elif res.get("baseline"):
                base = res["baseline"]
                st.write(base["concept"])
                for r in base["recommendations"]:
                    st.markdown(f"- {r['name']} · `{r['source']}`")
            else:
                st.info("Tick 'Also run plain-LLM comparison' in the sidebar and rebuild.")

    with tab_schedule:
        for slot in plan["schedule"]:
            st.markdown(
                f'<div class="card"><b>{html.escape(str(slot.get("time", "")))}</b> &nbsp; '
                f'{html.escape(str(slot.get("activity", "")))}</div>',
                unsafe_allow_html=True,
            )

    with tab_budget:
        check = res["budget"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", f"₹{check.total:,.0f}")
        c2.metric("Budget", f"₹{check.budget:,.0f}")
        c3.metric("Remaining", f"₹{check.remaining:,.0f}")
        if not check.within_budget:
            st.error("This plan is over budget.")
        df = pd.DataFrame([{"item": i.name, "INR": i.cost} for i in res["costs"]]).set_index("item")
        st.bar_chart(df)
        st.caption("Planning estimates, not vendor prices.")

    with tab_notes:
        for a in plan["assumptions"]:
            st.write(f"- {a}")


load_secrets_into_env()
qloo_live = bool(load_key("QLOO_API_KEY"))
gemini_ready = bool(load_key("GEMINI_API_KEY"))

with st.sidebar:
    st.header("Event brief")
    with st.form("brief"):
        city = st.text_input("City", "Mumbai")
        interest = st.text_input("Primary interest (an artist name works best)", "Daft Punk")
        budget = st.number_input("Budget (INR)", min_value=0, value=1_000_000, step=50_000)
        compare = st.checkbox("Also run plain-LLM comparison", value=True)
        submitted = st.form_submit_button("Build event plan", type="primary")
    st.divider()
    st.markdown(
        f'<span class="badge {"b-qloo" if qloo_live else "b-mock"}">Qloo {"LIVE" if qloo_live else "MOCK"}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="badge {"b-qloo" if gemini_ready else "b-mock"}">Gemini {"ready" if gemini_ready else "no key"}</span>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="hero">CultureMix</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Event concepts grounded in cultural data, checked against your budget.</div>',
    unsafe_allow_html=True,
)

if submitted:
    brief = {"city": city, "budget": float(budget), "interest": interest}
    try:
        with st.spinner("Designing the event..."):
            st.session_state["result"] = run_pipeline(brief, qloo_live, compare)
        st.session_state["error"] = None
    except (QlooError, LLMError, PlanError, ValueError) as exc:
        st.session_state["result"] = None
        st.session_state["error"] = str(exc)

if st.session_state.get("error"):
    st.error(st.session_state["error"])
if st.session_state.get("result"):
    render(st.session_state["result"])
elif not st.session_state.get("error"):
    st.info("Enter a brief in the sidebar and build a plan.")