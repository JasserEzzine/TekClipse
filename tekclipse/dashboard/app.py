from __future__ import annotations

import html
import os
import base64
import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tekclipse.dashboard import charts
from tekclipse.dashboard.security_panel import render_security_panel
from tekclipse.dashboard.data_service import (
    dataset_token,
    load_data,
    chart_data,
    detect,
    load_nominal_preview,
    save_nominal_preview,
    evaluate_preview,
)

st.set_page_config(
    page_title="TEKCLIPSE | Mission Control",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(show_spinner=False)
def local_font_css():
    rules = []
    for family, filename in [
        ("Orbitron", "orbitron"),
        ("JetBrains Mono", "jetbrainsmono"),
        ("Inter", "inter"),
    ]:
        paths = sorted(Path(__file__).with_name("assets").glob(filename + "-*.ttf"))
        for i, path in enumerate(paths):
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            weight = "100 900" if len(paths) == 1 else str(400 if i == 0 else 700)
            rules.append(
                f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;src:url(data:font/ttf;base64,{encoded}) format('truetype');}}"
            )
    return "".join(rules)


st.html("<style>" + local_font_css() + "</style>")
st.html(Path(__file__).with_name("theme.css"))
st.html(Path(__file__).with_name("mission.css"))
st.html(
    '<div class="disclaimer">SIMULATION ONLY · Alerts indicate deviation from nominal profile, not confirmed attacks.</div>'
)
st.html(
    """<div class="mission-header"><div><div class="mission-title">◉ TEKCLIPSE</div><div class="eyebrow">SATELLITE SECURITY OPERATIONS</div></div>
<div class="header-meta"><span>TEK-UP / IASTAM 6.0 / TRACK 05 · P9</span><span class="chip">STORED SIMULATION · SEED 42</span><span>Multi-source operations observatory</span></div></div>"""
)

with st.sidebar:
    st.html(
        '<div class="brand-mark">◉</div><h2>TEKCLIPSE</h2><div class="eyebrow">MISSION CONTROL / SIMULATOR</div>'
    )
    with st.expander("Mission navigation", expanded=False):
        for destination in [
            "OVERVIEW",
            "TELEMETRY",
            "COMMANDS",
            "NETWORK",
            "EVENTS",
            "ALERTS",
            "SCENARIOS E1–E7",
            "ABOUT",
        ]:

            def navigate(label=destination):
                st.session_state["mission_tabs"] = label

            st.button(
                destination,
                key="nav_" + destination,
                on_click=navigate,
                type=(
                    "primary"
                    if st.session_state.get("mission_tabs", "OVERVIEW") == destination
                    else "secondary"
                ),
                width="stretch",
            )
    cloud_demo = os.environ.get("TEKCLIPSE_CLOUD") == "1"
    days = st.selectbox(
        "Simulation range",
        [1, 7] if cloud_demo else [7, 1, 14, 30],
        format_func=lambda d: f"{d} days · 1 Hz",
    )
    if cloud_demo:
        st.caption("Hosted demo: 1 or 7 days. The local app supports up to 30 days.")
    st.caption("Select a shorter range for faster detector previews.")
    from tekclipse.pipeline.profiles import PROFILE_LABELS
    profile = st.selectbox('Detection profile', list(PROFILE_LABELS),
                           format_func=PROFILE_LABELS.get, key='detection_profile')
    st.caption(f'Active: {PROFILE_LABELS[profile]}')
    if profile != 'original':
        st.caption('Independent nominal fit and calibration. Synthetic research profile; not production validated. Published tests cover 24-hour runs.')
        if days != 1:
            st.info('This longer preview is outside the validated 24-hour experiment range.')
hours = days * 24
token = dataset_token(hours)
run_key = (hours, token, profile)
if st.session_state.get("run_key") != run_key:
    st.session_state["run_key"] = run_key
    for state_key in ('validated_evaluation', 'evaluation_key', 'pending_evaluation',
                      'pending_scenario', 'overview_replay_second', 'scenarios_replay_second'):
        st.session_state.pop(state_key, None)
    st.session_state['guided_demo'] = False
    st.session_state["result"] = load_nominal_preview(hours, token) if profile == 'original' else detect(hours, token, 'E1', profile)
    st.session_state["scenario"] = "E1"
elif st.session_state.get("result") is None:
    st.session_state["result"] = load_nominal_preview(hours, token) if profile == 'original' else detect(hours, token, 'E1', profile)
pending_scenario = st.session_state.pop("pending_scenario", None)
if pending_scenario is not None:
    with st.spinner(
        f"Running {pending_scenario}: nominal-only training, then full-resolution rules + IF…"
    ):
        output = detect(hours, token, pending_scenario, profile)
        if pending_scenario == "E1" and profile == 'original':
            save_nominal_preview(hours, token, output)
    st.session_state["result"] = output
    st.session_state["scenario"] = pending_scenario
scenario = st.session_state.get("scenario", "E1")
result = st.session_state.get("result")
if st.session_state.pop("pending_evaluation", False):
    with st.spinner("Running labeled held-out comparison…"):
        st.session_state["validated_evaluation"] = evaluate_preview(
            hours, token, scenario, profile
        )
        st.session_state["evaluation_key"] = (run_key, scenario)
with st.spinner("Loading mission streams…"):
    view = chart_data(hours, token, scenario)
with st.sidebar:
    st.divider()
    st.html('<div class="eyebrow">DATA MANIFEST / UTC</div>')
    st.write(f'{view["start"]:%d %b %Y %H:%M:%S}')
    st.write(f'{view["end"]:%d %b %Y %H:%M:%S}')
    for label, name in [
        ("Telemetry points", "telemetry"),
        ("Commands", "commands"),
        ("Network rows", "network"),
        ("System events", "system_events"),
    ]:
        st.markdown(f"{label} **{view['counts'][name]:,}**")
    st.html(
        f'<span class="chip">{scenario} ACTIVE</span> <span class="chip">4 SOURCES</span>'
    )
    st.caption(
        "Nominal train / full-resolution preview. Alerts are observations, not validated detection metrics."
    )
    st.divider()
    st.caption("IF · 100 trees / contamination 0.05 / seed 42")
    st.caption(
        "Network baseline + explicit subsystem-event checks + temporal correlation."
    )
    if result and result.get('profile_metadata'):
        with st.expander('Scientific profile / reproducibility and authorized flows'):
            st.json(result['profile_metadata'])
    # Wall clock retained separately from the simulation review UTC.
    # Bounded, one-second clock only; starfield is pure CSS.
    st.iframe(
        """<body style="margin:0;color:#8198AE;font:11px monospace;background:transparent"><span id="clock"></span> · WALL CLOCK / DATA IS A STORED SIMULATION
    <script>function tick(){document.getElementById('clock').textContent=new Date().toISOString().replace('T',' ').slice(0,19)+' UTC'}tick();setInterval(tick,1000)</script></body>""",
        height=22,
    )


def plot(fig, key):
    started = perf_counter()
    st.plotly_chart(
        fig,
        width="stretch",
        theme=None,
        key=key,
        config={"displaylogo": False, "scrollZoom": False},
    )
    st.session_state.setdefault("chart_submit_seconds", {})[key] = (
        perf_counter() - started
    )


def run(scenario_name):
    # Widget callbacks run before the script: process once before charts are built.
    st.session_state["pending_scenario"] = scenario_name
    st.session_state["mission_tabs"] = "SCENARIOS E1–E7"
    st.session_state["guided_demo"] = False
    for prefix in ("overview", "scenarios"):
        st.session_state.pop(prefix + "_replay_second", None)


def demo_run(scenario_name):
    run(scenario_name)
    st.session_state["guided_demo"] = True
    st.session_state["mission_tabs"] = "OVERVIEW"


def reset_demo():
    # Reset all review-only state; cached detector output is reused, not retrained.
    for key in ("validated_evaluation", "evaluation_key", "pending_evaluation"):
        st.session_state.pop(key, None)
    demo_run("E1")


def request_evaluation():
    st.session_state["pending_evaluation"] = True
    st.session_state["mission_tabs"] = "SCENARIOS E1–E7"


def kpi(label, value, foot, series=(), icon="◈"):
    y = np.asarray(series, dtype=float)
    if len(y) > 1:
        y = 4 + 22 * (y - y.min()) / max(np.ptp(y), 1e-9)
        bars = "".join(f'<i style="height:{v:.1f}px"></i>' for v in y)
        spark = f'<div class="spark" aria-label="Last hour trend">{bars}</div>'
    else:
        spark = '<div class="spark"></div>'
    st.html(
        f'<div class="card kpi"><span class="icon-chip">{icon}</span><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div>{spark}</div>'
    )


names = [
    "OVERVIEW",
    "TELEMETRY",
    "COMMANDS",
    "NETWORK",
    "EVENTS",
    "ALERTS",
    "SCENARIOS E1–E7",
    "ABOUT",
]
st.caption(f'Detection profile: {PROFILE_LABELS[profile]} · Published scientific results use independent test seeds; this preview uses seed 42.')
tabs = st.tabs(names, key="mission_tabs", on_change="rerun")
# Stateful tabs render only their active content; heavy charts do not run offscreen.
if tabs[0].open:
    with tabs[0]:
        demo_a, demo_b, demo_c = st.columns([1, 1.3, 1])
        demo_a.button(
            "Start nominal E1",
            key="mission_E1",
            on_click=demo_run,
            args=("E1",),
            width="stretch",
        )
        demo_b.button(
            "Launch E7 attack",
            key="mission_E7",
            on_click=demo_run,
            args=("E7",),
            type="primary",
            width="stretch",
        )
        demo_c.button(
            "Reset demo", key="mission_reset", on_click=reset_demo, width="stretch"
        )
        render_security_panel(result, view=view)
        with st.expander("Judge demo / 2–3 minutes", expanded=False):
            st.write(
                "1. Start E1 and explain the nominal indicator. 2. Launch E7. 3. Advance through the attack stages. 4. Review the incident, deductions and simulated operator response."
            )
            demo_a, demo_b = st.columns(2)
            demo_a.button(
                "Start nominal E1", key="demo_E1", on_click=demo_run, args=("E1",)
            )
            demo_b.button(
                "Launch E7 guided replay",
                key="demo_E7",
                on_click=demo_run,
                args=("E7",),
                type="primary",
            )
        st.divider()
        st.markdown("### Mission overview")
        st.caption(
            f"{scenario} / {days}-day stored simulation · sparklines show the last hour"
        )
        cards = st.columns(5)
        latest = view["latest"]
        end = view["end"]
        command_hour = view["commands"].timestamp.between(
            end - pd.Timedelta(hours=1), end
        )
        with cards[0]:
            kpi(
                "Temperature",
                f'{latest["temperature_c"]:.1f} °C',
                "LATEST SAMPLE",
                view["last_hour"].temperature_c,
            )
        with cards[1]:
            kpi(
                "Battery",
                f'{latest["battery_percent"]:.1f} %',
                "LATEST SAMPLE",
                view["last_hour"].battery_percent,
            )
        with cards[2]:
            bins = (
                view["commands"]
                .set_index("timestamp")
                .resample("min")
                .size()
                .reindex(
                    pd.date_range(
                        end.floor("min") - pd.Timedelta(minutes=59),
                        end.floor("min"),
                        freq="min",
                    ),
                    fill_value=0,
                )
            )
            kpi("Command rate", f"{command_hour.sum()/60:.2f} /min", "LAST HOUR", bins)
        with cards[3]:
            kpi(
                "CPU utilization",
                f'{latest["cpu_percent"]:.1f} %',
                "SIMULATED PROCESS",
                view["last_hour"].cpu_percent,
            )
        with cards[4]:
            a = result["alerts"] if result else None
            series = (
                a.set_index("timestamp").resample("min").size().tail(60)
                if a is not None and not a.empty
                else []
            )
            kpi(
                "Detector alerts",
                f"{len(a):,}" if a is not None else "—",
                "CURRENT PREVIEW" if result else "NOT RUN",
                series,
            )
        left, right = st.columns([1.65, 1])
        with left:
            # Plotly scene rotates in its isolated component; honors reduced motion.
            from plotly.offline import get_plotlyjs

            fig = charts.orbit()
            orbit_html = fig.to_html(
                include_plotlyjs=False,
                full_html=False,
                div_id="orbit",
                config={"displayModeBar": False},
                post_script="""
            const el=document.getElementById('orbit');let angle=0;let visible=true;
            new IntersectionObserver(entries=>visible=entries[0].isIntersecting).observe(el);
            if(!matchMedia('(prefers-reduced-motion: reduce)').matches){setInterval(()=>{if(document.hidden||!visible)return;angle+=0.012;Plotly.relayout(el,{'scene.camera.eye':{x:2.1*Math.cos(angle),y:2.1*Math.sin(angle),z:1.0}})},160)}
            """,
            )
            st.iframe(
                "<style>"
                + local_font_css()
                + "body{margin:0;background:#091727;border:1px solid #164156;border-radius:14px}</style><script>"
                + get_plotlyjs()
                + "</script>"
                + orbit_html,
                height=430,
            )
            st.caption(
                "Illustrative orbital geometry; not measured position or a flight dynamics model. Drag to inspect."
            )
        with right:
            if result:
                plot(charts.gauge(result), "gauge")
                st.caption(
                    f'−decision_function; alert threshold {result["threshold"]:.4f}. This is not an attack probability.'
                )
            else:
                st.html(
                    '<div class="card" style="min-height:215px"><div class="eyebrow">DETECTION STATUS</div><h2>Awaiting detector run</h2><p>Execute the existing rules and nominal-trained Isolation Forest to inspect actual alerts.</p><span class="chip">NO PLACEHOLDER SCORES</span></div>'
                )
            st.button(
                "Run nominal detector preview",
                type="primary",
                width="stretch",
                on_click=run,
                args=("E1",),
            )
            st.caption(
                "First run takes longer; repeated runs are cached. Full dataset is retained for detection."
            )
        if result and not result["alerts"].empty:
            lines = [
                f"{r.timestamp:%d %b %H:%M:%S} UTC / {r.source} / {r.severity} / deviation from nominal profile"
                for r in result["alerts"].tail(8).itertuples()
            ]
            st.html(
                '<div class="ticker"><span>'
                + html.escape("　 •　 ".join(lines))
                + "</span></div>"
            )
        else:
            st.info(
                "No detector output yet."
                if not result
                else "No deviations detected by the current preview."
            )
        st.caption(
            "Four synchronized sources / 90-minute synthetic orbital cycle / correlated ground-pass activity"
        )
        if result and result.get("saved_at"):
            st.caption(
                f'Saved nominal detector preview computed {result["saved_at"]}. Alerts below are actual model output on synthetic data.'
            )
        st.markdown("### Mission activity")
        event_counts = view["events"].event_type.value_counts()
        a, b, c = st.columns(3)
        with a:
            st.metric(
                "Ground contacts acquired", int(event_counts.get("contact_acquired", 0))
            )
        with b:
            st.metric("Eclipse entries", int(event_counts.get("eclipse_entry", 0)))
        with c:
            st.metric(
                "Command acknowledgements", int(event_counts.get("command_ack", 0))
            )
        st.caption("Recorded activity across the selected synthetic mission window.")
        milestones = view["events"][
            view["events"].event_type.isin(
                [
                    "contact_acquired",
                    "contact_closed",
                    "eclipse_entry",
                    "sunlight_entry",
                    "config_change",
                ]
            )
        ]
        st.dataframe(
            milestones.tail(10).sort_values("timestamp", ascending=False),
            hide_index=True,
            width="stretch",
        )

if tabs[1].open:
    with tabs[1]:
        st.markdown("### Telemetry observatory")
        variables = st.multiselect(
            "Signals",
            list(charts.LABELS),
            default=["temperature_c", "cpu_percent", "battery_percent"],
            format_func=lambda v: charts.LABELS[v],
        )
        small = st.toggle("Small multiples · separate units", value=True)
        if variables:
            plot(
                charts.telemetry_chart(
                    view, variables, small, result["spans"] if result else []
                ),
                "telemetry",
            )
        st.caption(
            f'{view["step"]}-second display means; temperature bin maxima retain spikes. Red shading marks bins containing IF flags. Detection uses every sample.'
            if result
            else f'{view["step"]}-second display means. Run a detector preview to add IF anomaly shading.'
        )
        if not small:
            st.caption(
                "Overlay uses native, mixed units; use small multiples to compare each scale."
            )
        corr = view["correlation"]
        fig = go.Figure(
            go.Heatmap(
                z=corr.values,
                x=[charts.LABELS[c] for c in corr.columns],
                y=[charts.LABELS[c] for c in corr.index],
                zmin=-1,
                zmax=1,
                colorscale=[[0, charts.VIOLET], [0.5, "#0A1628"], [1, charts.CYAN]],
            )
        )
        plot(
            charts.style(fig, "FULL-RESOLUTION PEARSON CORRELATION", 430), "correlation"
        )

if tabs[2].open:
    with tabs[2]:
        st.markdown("### Command uplink")
        commands = view["commands"]
        # Time filter bounds scatter payload while compositions use all commands.
        dates = sorted(commands.timestamp.dt.strftime("%Y-%m-%d").unique())
        selected = st.selectbox("Timeline day (UTC)", dates, index=len(dates) - 1)
        day_commands = commands[commands.timestamp.dt.strftime("%Y-%m-%d") == selected]
        timeline, _, _ = charts.command_charts(day_commands)
        _, step, sun = charts.command_charts(commands)
        plot(timeline, "command_timeline")
        a, b = st.columns([1.4, 1])
        with a:
            plot(step, "command_count")
        with b:
            plot(sun, "command_sunburst")
        st.caption(
            "Timeline shows selected day; cumulative count and composition cover the entire selected simulation."
        )
        st.dataframe(commands.tail(100), hide_index=True, width="stretch")

if tabs[3].open:
    with tabs[3]:
        st.markdown("### Ground–space network")
        area, bubble, donut = charts.network_charts(view)
        plot(area, "network_area")
        a, b = st.columns([1.6, 1])
        with a:
            plot(bubble, "network_bubbles")
        with b:
            plot(donut, "network_protocol")
        st.caption(
            "Traffic rate uses simulator units. Bubble size sums connection_count samples; it is not a count of distinct connections."
        )
        st.caption(
            "NET alerts compare per-second packet/byte totals, traffic rises and peer/protocol novelty with an untouched nominal baseline."
        )

if tabs[4].open:
    with tabs[4]:
        st.markdown("### System event observatory")
        event_type = st.selectbox(
            "Event type", ["All"] + sorted(view["events"].event_type.unique())
        )
        heat, feed = charts.event_charts(view, event_type)
        plot(heat, "event_heatmap")
        plot(feed, "event_feed")
        st.dataframe(view["events"].tail(100), hide_index=True, width="stretch")

if tabs[5].open:
    with tabs[5]:
        st.markdown("### Deviations from nominal profile")
        if result is None:
            st.info("Run a nominal or scenario detector preview to populate this view.")
        else:
            alerts = result["alerts"]
            st.caption(
                f'{scenario} · {len(alerts):,} actual detector alerts · measured execution {result["seconds"]:.2f}s'
            )
            if not alerts.empty:
                donut, bar, radar = charts.alert_charts(alerts, view)
                a, b = st.columns(2)
                with a:
                    plot(donut, "alert_severity")
                with b:
                    plot(radar, "alert_radar")
                st.caption(
                    "Radar reports actual alert counts including NET and SYS checks. Zero alerts does not establish safety."
                )
                plot(bar, "alert_time")
                selected_sources = st.multiselect(
                    "Detector sources",
                    sorted(alerts.source.unique()),
                    default=sorted(alerts.source.unique()),
                )
                shown = alerts[alerts.source.isin(selected_sources)].tail(200).copy()
                shown["description"] = (
                    "Deviation from nominal profile · " + shown.description
                )
                st.dataframe(
                    shown.style.apply(
                        lambda row: [
                            (
                                "background-color: #45232B"
                                if row.severity == "CRITICAL"
                                else "background-color: #3A321E"
                            )
                        ]
                        * len(row),
                        axis=1,
                    ),
                    hide_index=True,
                    width="stretch",
                )
                st.download_button(
                    "Export actual alerts · CSV",
                    alerts.to_csv(index=False),
                    file_name=f"tekclipse-{scenario}-alerts.csv",
                    mime="text/csv",
                )
            else:
                st.success("No deviations detected by these detectors in this preview.")
            st.caption(
                "Preview scores overlap the nominal training timeline. Use the separate held-out evaluation in Scenarios for explicitly labeled synthetic measurements."
                if profile == 'original' else 'Scientific profile uses independent nominal seeds. These display-seed results are separate from the published frozen benchmark.'
            )

if tabs[6].open:
    with tabs[6]:
        st.markdown("### Scenario laboratory")
        st.caption(
            "E1–E6 retain their original injectors. E7 adds a staged sequence. Injection reference: 01 Jan 2026, 12:00 UTC."
        )
        items = [
            ("E1", "Normal operation", "Nominal baseline"),
            ("E2", "Unauthorized command", "R1 command source check"),
            ("E3", "Command flooding", "R2 command rate check"),
            ("E4", "Network traffic spike", "Network statistical baseline"),
            ("E5", "Temperature manipulation", "R3 + telemetry IF"),
            ("E6", "Combined anomalies", "R1 + R3 + telemetry IF + NET + correlation"),
            (
                "E7",
                "Coordinated multi-stage attack",
                "Commands → network → telemetry → subsystem impact",
            ),
        ]
        for code, name, coverage in items:
            a, b, c = st.columns([1.5, 2, 0.8])
            with a:
                st.markdown(f"**{code} / {name}**")
            with b:
                st.caption(f"IMPLEMENTED · {coverage}")
            with c:
                st.button(f"Run {code}", key=f"run_{code}", on_click=run, args=(code,))
        st.info(
            "Preview training uses the untouched nominal baseline. The separate evaluation below uses a non-overlapping split and explicit synthetic labels."
            if profile == 'original' else 'The selected scientific profile is fitted and calibrated on independent nominal runs, then applied unchanged to this scenario. No displayed attack data is used for training.'
        )
        if result:
            st.write(
                f'Last preview: **{scenario}**, {result["evaluated_samples"]:,} telemetry samples; {result["seconds"]:.2f}s detector execution.'
            )
            if result["truth"]:
                st.dataframe(
                    pd.DataFrame(
                        result["truth"],
                        columns=["Injection timestamp", "Scenario description"],
                    ),
                    hide_index=True,
                )
            render_security_panel(result, prefix="scenarios", view=view)
        st.markdown("### Held-out synthetic evaluation")
        st.caption(
            "Separate from the preview: fit on the first six nominal hours, score later samples against explicit injected windows. A run can take time. Undefined metrics are left blank."
            if profile == 'original' else 'Evaluate the selected scientific profile on independent display seed 42 using the same fitted model and threshold as the preview. Official published metrics use different frozen test seeds.'
        )
        st.button(
            "Evaluate selected scenario",
            key="evaluate_selected",
            on_click=request_evaluation,
        )
        evaluation = st.session_state.get("validated_evaluation")
        if evaluation and st.session_state.get("evaluation_key") == (run_key, scenario):
            if evaluation["available"]:
                st.dataframe(pd.DataFrame(evaluation["comparisons"]).T, width="stretch")
                st.caption(evaluation["method"])
                st.caption(
                    f"Training through {evaluation['train_end']}; test {evaluation['test_start']} to {evaluation['test_end']}."
                )
                st.download_button(
                    "Export evaluation / JSON",
                    json.dumps(evaluation, indent=2),
                    file_name=f"tekclipse-{scenario}-evaluation.json",
                    mime="application/json",
                )
            else:
                st.info(evaluation["reason"])

if tabs[7].open:
    with tabs[7]:
        st.markdown("### Engineering scope")
        st.html(
            '<div class="pipeline"><div class="card">Simulated environment<br>4 data sources</div><span class="arrow">→</span><div class="card">Preprocessing<br>Temporal features</div><span class="arrow">→</span><div class="card">Parallel checks<br>Rules R1–R3 ∥ Isolation Forest</div><span class="arrow">→</span><div class="card">Merged alerts<br>Source · time · severity</div><span class="arrow">→</span><div class="card">Mission dashboard</div></div>'
        )
        a, b = st.columns(2)
        with a:
            st.markdown("#### Established baseline")
            st.write(
                "Isolation Forest is a practical baseline, not optimal. It learns only from nominal telemetry; temporal features use 60-sample rolling windows."
            )
            st.code("n_estimators=100\ncontamination=0.05\nrandom_state=42")
            st.write(
                "Anomaly ≠ attack. Alerts indicate deviation from nominal profile; neither attribution nor cause is established."
            )
        with b:
            st.markdown("#### Validation roadmap")
            st.markdown(
                "- Validate held-out splits and injection windows\n- Measure detection rate, FPR and detection latency\n- Compare single-source and multi-source monitoring\n- Measure monitoring CPU/RAM overhead\n- Report negative and inconclusive outcomes"
            )
            st.caption(
                "Synthetic orbital patterns support reproducible engineering experiments. They do not validate behavior on a real satellite."
            )
        st.caption(
            "Python · Pandas / NumPy · scikit-learn · Streamlit / Plotly · CSV / SQLite / optional Parquet"
        )
        st.caption(
            "Implementation assisted by AI tooling; team review is required before submission."
        )

if tabs[0].open:
    st.html(
        r"""<script>
    if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
      document.querySelectorAll('.kpi-value').forEach(el=>{
        const final=el.textContent, match=final.match(/^([\d,.]+)/);
        if(!match || el.dataset.animated)return;
        el.dataset.animated='true';
        const target=Number(match[1].replaceAll(',','')), decimals=(match[1].split('.')[1]||'').length;
        const suffix=final.slice(match[1].length), start=performance.now();
        function frame(now){const p=Math.min((now-start)/650,1);el.textContent=(target*(1-Math.pow(1-p,3))).toLocaleString('en-US',{minimumFractionDigits:decimals,maximumFractionDigits:decimals})+suffix;if(p<1)requestAnimationFrame(frame);else el.textContent=final;}
        requestAnimationFrame(frame);
      });
    }
    </script>""",
        unsafe_allow_javascript=True,
    )
