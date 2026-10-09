"""Additive security briefing and judge-friendly replay for the existing dashboard."""

import json
import html

import pandas as pd
import streamlit as st

from tekclipse.data.coordinated import ONSET, STAGES
from tekclipse.dashboard.security_charts import attack_timeline, trust_history
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.response import recommended_responses
from tekclipse.pipeline.subsystems import subsystem_statuses
from tekclipse.dashboard.mission_state import mission_briefing
from tekclipse.dashboard.mission_visuals import mission_console, impact_reasoning_html
from tekclipse.dashboard.investigation import subsystem_panel, replay_panel, render_investigation, render_research_notes
from tekclipse.dashboard.defense_panel import render_defense
from tekclipse.dashboard.defense_service import load_evidence
from tekclipse.security.evidence import safe_review, digest


def render_security_panel(result, prefix="overview", view=None):
    if not result or "security" not in result:
        st.info("Run a detector preview to populate the security briefing.")
        return
    security = result["security"]
    evidence = security["evidence"]
    scenario = result["scenario"]
    st.toggle('Open cyber defense workspace', key='defense_open', help='Persistent findings, source investigation, manual simulated restrictions and incident reports.')
    if scenario == "E7":
        key = prefix + "_replay_second"
        if key not in st.session_state:
            st.session_state[key] = 0 if st.session_state.get("guided_demo") else 160

        def keep_tab():
            st.session_state["mission_tabs"] = (
                "OVERVIEW" if prefix == "overview" else "SCENARIOS E1–E7"
            )

        replay_controls = st.columns([1, 3])
        with replay_controls[1]:
            second = st.slider(
                "E7 replay / seconds after 12:00 UTC",
                0,
                180,
                key=key,
                on_change=keep_tab,
                label_visibility="collapsed",
            )

        def advance():
            current = st.session_state[key]
            st.session_state[key] = next((s for s, _ in STAGES if s > current), 180)
            st.session_state["mission_tabs"] = (
                "OVERVIEW" if prefix == "overview" else "SCENARIOS E1–E7"
            )

        with replay_controls[0]:
            st.button(
                "Next attack stage",
                key=prefix + "_next_stage",
                on_click=advance,
                disabled=second >= 180,
                type="primary",
                width="stretch",
            )
        st.caption(
            f"REPLAY +{second:03d}s / "
            + next(label for s, label in reversed(STAGES) if s <= second)
        )

        at = ONSET + pd.Timedelta(seconds=second)
    else:
        second = st.number_input('Defense review / seconds after 12:00 UTC', 0, 180, 160,
                           key='defense_review_second') if st.session_state.get('defense_open') else 160
        at = ONSET + pd.Timedelta(seconds=second)
    window = security["window_seconds"]
    policy = security.get('correlation_policy', 'legacy')
    snapshot = trust_snapshot(evidence, at, window, correlation_policy=policy)
    journal = load_evidence(result)
    snapshot = safe_review(snapshot, journal[3])
    briefing = mission_briefing(snapshot, view)
    history = []
    if scenario == "E7":
        points = sorted({s for s, _ in STAGES if s <= second} | {second})
        history = [
            safe_review(trust_snapshot(evidence, ONSET + pd.Timedelta(seconds=s), window, correlation_policy=policy), journal[3])
            for s in points
        ]
    st.html(mission_console(snapshot, briefing, history, scenario=scenario))
    if scenario == 'E7':
        st.html(replay_panel(history))
    st.html(subsystem_panel(snapshot))
    render_defense(snapshot, result, prefix, journal=journal)
    render_investigation(snapshot, prefix)
    render_research_notes()
    with st.expander(
        "Mission impact reasoning / cyber evidence to potential consequence",
        expanded=False,
    ):
        if briefing["impacts"]:
            st.html(impact_reasoning_html(briefing["impacts"]))
        else:
            st.write(
                "No potential mission consequence is inferred from the active evidence."
            )
        st.caption(
            "Mission impact represents simulated decision-support reasoning and does not predict physical spacecraft failure."
        )
    with st.expander(
        "Analyst briefing / trust formula, timelines, evidence and full operator response",
        expanded=False,
    ):
        st.caption(
            f"Historical simulation review at {at:%d %b %Y %H:%M:%S} UTC · trailing {window}s · not live spacecraft health"
        )
        a, b, c, d = st.columns(4)
        a.metric("Satellite status", snapshot["status"])
        b.metric("Trust score", f"{snapshot['score']}/100")
        c.metric("Active alerts", len(snapshot["active_alerts"]))
        d.metric("Correlated incidents", len(snapshot["incidents"]))
        st.caption(
            "Prototype Operational Trust Indicator — deterministic policy, not a validated probability. Correlation does not confirm an attack."
        )
        with st.expander(
            "Why did the trust score change?", expanded=snapshot["score"] < 80
        ):
            if snapshot["contributors"]:
                st.dataframe(
                    pd.DataFrame(snapshot["contributors"]),
                    hide_index=True,
                    width="stretch",
                )
            else:
                st.write(
                    "100: no active evidence from the implemented checks in this window."
                )
            st.caption(
                "Start at 100; subtract each detector-family cap once, weighted by maximum severity (WARNING 0.75; HIGH/CRITICAL 1). Caps: R1 20, R2 12, R3 18, NET 12, SYS 12, ML 3. Correlation subtracts 10 (HIGH) or 19 (CRITICAL). Floor 0. NORMAL ≥80; SUSPICIOUS ≥50; CRITICAL <50. Evidence expires after the review window; score recovery is not confirmed remediation."
            )
        states = subsystem_statuses(snapshot)
        columns = st.columns(5)
        colors = {"NORMAL": "🟢", "WARNING": "🟠", "CRITICAL": "🔴"}
        for column, state in zip(columns, states):
            column.markdown(
                f"**{state['subsystem']}**\n\n{colors[state['status']]} {state['status']}"
            )
        st.caption(
            "Subsystem status reflects mapped active evidence only; NORMAL does not certify safety."
        )
        # Replay never includes future observations or incident evidence.
        active = snapshot["active_alerts"]
        if active:
            st.plotly_chart(
                attack_timeline(active, snapshot["incidents"]),
                width="stretch",
                key=prefix + "_attack_timeline",
            )
        else:
            st.success("Attack timeline: no detector evidence in this review window.")
        if scenario == "E7":
            points = [s for s, _ in STAGES if s <= second]
            points = sorted(set(points + [second]))
            history = [
                trust_snapshot(evidence, ONSET + pd.Timedelta(seconds=s), window, correlation_policy=policy)
                for s in points
            ]
            st.plotly_chart(
                trust_history(history), width="stretch", key=prefix + "_trust_history"
            )
        if snapshot["incidents"]:
            for incident in snapshot["incidents"]:
                st.warning(
                    f"{incident['severity']} CORRELATED SECURITY INCIDENT · {incident['id']} · correlation score {incident['correlation_score']}/100"
                )
                st.write(incident["explanation"])
                st.caption(
                    f"Range {incident['start']} to {incident['end']}; first multi-source association {incident['detected_at']}. Score: 20/domain + 5/non-ML detector family + 10 if critical evidence, capped at 100. Not confidence in attack attribution."
                )
        with st.expander("Explainable evidence and contributing alerts"):
            if active:
                frame = pd.DataFrame(active)
                priority = frame.source.ne("ML")
                shown = pd.concat([frame[priority], frame[~priority]]).head(100)
                st.dataframe(
                    shown[["id", "observed_at", "source", "severity", "description"]],
                    hide_index=True,
                    width="stretch",
                )
                st.caption(
                    "Showing up to 100 records, actionable evidence first. ML feature deviations are descriptive context, not causal feature attribution."
                )
            else:
                st.write("No active detector evidence.")
            st.download_button(
                "Export incident evidence / JSON",
                json.dumps(snapshot, indent=2),
                file_name=f"tekclipse-{scenario}-incident.json",
                mime="application/json",
                key=prefix + "_export",
            )
        st.markdown("#### Recommended Operator Response")
        responses = recommended_responses(snapshot)
        if responses:
            for response in responses:
                st.markdown("- " + response)
        else:
            st.write(
                "Continue monitoring; no high/critical response recommendation in this review window."
            )
        st.caption(
            "SIMULATED RECOMMENDATIONS ONLY. These suggestions execute no action. Use the cyber defense workspace for manual simulation admission policies; no real firewall or spacecraft is controlled."
        )
    # Browser automation must wait for downloads as well as earlier visible cards.
    ready = {k:v for k,v in st.session_state.items() if k.startswith('defense_') or k.startswith(prefix+'_investigation')}
    ready.update(at=snapshot['at'],scenario=scenario)
    family = html.escape(st.session_state.get(prefix+'_investigation_family','All observed evidence'),quote=True)
    st.html(f'<span class="security-render-complete" data-token="{digest(ready)}" data-family="{family}"></span>')
