from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tekclipse.config import load_config
from tekclipse.data.generator import generate_synthetic_dataset


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "tekclipse" / "data" / "generated"


st.set_page_config(page_title="TEKCLIPSE SOC", layout="wide")


def load_or_generate_data():
    if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
        with st.spinner("Generating synthetic satellite data…"):
            generate_synthetic_dataset(hours=24)
    telemetry = pd.read_csv(DATA_DIR / "telemetry.csv")
    commands = pd.read_csv(DATA_DIR / "commands.csv")
    network = pd.read_csv(DATA_DIR / "network.csv")
    events = pd.read_csv(DATA_DIR / "system_events.csv")
    return telemetry, commands, network, events


telemetry, commands, network, events = load_or_generate_data()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > div:first-child {
        background: #0A1628 !important;
        color: #E6F7FF !important;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #0A1628;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .card {
        background: rgba(14, 34, 62, 0.9);
        border: 1px solid rgba(34, 211, 238, 0.5);
        border-radius: 18px;
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.2), 0 0 24px rgba(34, 211, 238, 0.18);
        padding: 1rem 1.1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.35), 0 0 30px rgba(34, 211, 238, 0.23);
    }
    .kpi {
        background: linear-gradient(180deg, rgba(14,34,62,0.9), rgba(10,22,40,0.9));
    }
    .monospace {
        font-family: 'JetBrains Mono', monospace;
    }
    .glow-cyan { border-color: rgba(34,211,238,0.6); }
    p, div, span, li, td, th, .stDataFrame { font-family: 'Inter', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


cfg = load_config()
header_cols = st.columns([3, 1, 1, 2])
with header_cols[0]:
    st.markdown("<div class='card glow-cyan'><h2 style='margin:0;'>◉ TEKCLIPSE — Satellite Security Operations</h2></div>", unsafe_allow_html=True)
with header_cols[1]:
    st.markdown("<div class='card'><div class='monospace'>SIMULATION</div></div>", unsafe_allow_html=True)
with header_cols[2]:
    st.markdown(f"<div class='card'><div class='monospace'>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</div></div>", unsafe_allow_html=True)
with header_cols[3]:
    st.markdown("<div class='card'><div class='monospace'>Alerts indicate deviation from nominal profile — not confirmed attacks.</div></div>", unsafe_allow_html=True)

kpis = st.columns(4)
with kpis[0]:
    st.markdown(f"<div class='card kpi'><div class='monospace' style='color:#22D3EE'>Telemetry Health</div><h3>{telemetry['temperature_c'].mean():.1f}°C</h3></div>", unsafe_allow_html=True)
with kpis[1]:
    cmd_rate = commands.shape[0] / max(len(telemetry) / 3600, 1)
    st.markdown(f"<div class='card kpi'><div class='monospace' style='color:#22D3EE'>Commands/min</div><h3>{cmd_rate:.2f}</h3></div>", unsafe_allow_html=True)
with kpis[2]:
    net_load = network['traffic_rate'].mean()
    st.markdown(f"<div class='card kpi'><div class='monospace' style='color:#22D3EE'>Network Load</div><h3>{net_load:.0f}</h3></div>", unsafe_allow_html=True)
with kpis[3]:
    st.markdown("<div class='card kpi'><div class='monospace' style='color:#22D3EE'>Active Alerts</div><h3>0</h3></div>", unsafe_allow_html=True)

tabs = st.tabs(["OVERVIEW", "TELEMETRY", "COMMANDS", "NETWORK", "EVENTS", "ALERTS", "SCENARIOS", "ABOUT"])
with tabs[0]:
    st.subheader("Anomaly score overview")
    score = float(telemetry["temperature_c"].mean() / 45.0)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Nominal score"},
        gauge={
            "axis": {"range": [0, 1.2], "tickwidth": 1, "tickcolor": "lightgray"},
            "bar": {"color": "#22D3EE"},
            "steps": [
                {"range": [0, 0.7], "color": "rgba(52,211,153,0.35)"},
                {"range": [0.7, 1.0], "color": "rgba(251,191,36,0.35)"},
                {"range": [1.0, 1.2], "color": "rgba(248,113,113,0.35)"},
            ],
            "threshold": {"line": {"color": "#F87171", "width": 4}, "thickness": 0.75, "value": 0.9},
        }
    ))
    fig.update_layout(height=350, paper_bgcolor="#0A1628", plot_bgcolor="#0A1628", font={"color": "#E6F7FF"})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='card'><div class='monospace'>Simulated orbit diagram</div><div style='height:120px;border-radius:16px;background:radial-gradient(circle at center, rgba(34,211,238,0.2), transparent 60%), linear-gradient(180deg,#0A1628,#0E223E);'></div></div>", unsafe_allow_html=True)
    st.subheader("Recent alerts")
    for alert in [
        {"timestamp": "2026-01-01T12:00:00Z", "source": "R3", "severity": "WARNING", "description": "Telemetry deviation — nominal profile exceeded"},
        {"timestamp": "2026-01-01T12:02:00Z", "source": "ML", "severity": "WARNING", "description": "Isolation Forest anomaly score above threshold"},
    ]:
        st.markdown(f"<div class='card'><div class='monospace' style='color:{'#FBBF24' if alert['severity']=='WARNING' else '#22D3EE'}'>{alert['timestamp']} · {alert['source']} · {alert['severity']}</div><div>{alert['description']}</div></div>", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Telemetry")
    variables = st.multiselect("Variables", telemetry.columns[1:], default=["temperature_c", "cpu_percent", "voltage_v"], key="telemetry_select")
    fig = go.Figure()
    for var in variables:
        fig.add_trace(go.Scatter(x=pd.to_datetime(telemetry["timestamp"]), y=telemetry[var], mode="lines", name=var))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0A1628", plot_bgcolor="#0A1628", legend_title_text="Signal")
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("Commands")
    if not commands.empty:
        fig = go.Figure()
        for cmd_type in sorted(commands["type"].unique()):
            subset = commands[commands["type"] == cmd_type]
            fig.add_trace(go.Scatter(x=pd.to_datetime(subset["timestamp"]), y=[1]*len(subset), mode="markers", name=cmd_type, marker=dict(size=10, symbol="diamond" if subset.iloc[0].get("source") == "GS_BACKUP" else "circle")))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0A1628", plot_bgcolor="#0A1628")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(commands.head(20), use_container_width=True)

with tabs[3]:
    st.subheader("Network")
    chart = go.Figure()
    chart.add_trace(go.Scatter(x=pd.to_datetime(network["timestamp"]), y=network["traffic_rate"], mode="lines", fill="tozeroy", name="Traffic rate"))
    chart.update_layout(template="plotly_dark", paper_bgcolor="#0A1628", plot_bgcolor="#0A1628")
    st.plotly_chart(chart, use_container_width=True)
    st.dataframe(network.head(30), use_container_width=True)

with tabs[4]:
    st.subheader("Events")
    st.dataframe(events.head(50), use_container_width=True)

with tabs[5]:
    st.subheader("Alerts")
    alert_data = pd.DataFrame([
        {"timestamp": "2026-01-01T12:00:00Z", "source": "R3", "severity": "WARNING", "score": 0.81},
        {"timestamp": "2026-01-01T12:02:00Z", "source": "ML", "severity": "WARNING", "score": 0.92},
    ])
    st.dataframe(alert_data, use_container_width=True)

with tabs[6]:
    st.subheader("Scenarios")
    scenarios = pd.DataFrame([
        {"Scenario": "E1", "Status": "IMPLEMENTED (runnable)"},
        {"Scenario": "E2", "Status": "runnable via injection"},
        {"Scenario": "E3", "Status": "runnable via injection"},
        {"Scenario": "E4", "Status": "runnable via injection"},
        {"Scenario": "E5", "Status": "runnable via injection"},
        {"Scenario": "E6", "Status": "runnable via injection"},
    ])
    st.table(scenarios)

with tabs[7]:
    st.subheader("Pipeline overview")
    st.markdown(
        """
        <div style='display:flex;gap:12px;flex-wrap:wrap'>
            <div class='card'>Synthetic generator</div>
            <div class='card'>Preprocess</div>
            <div class='card'>Feature engineering</div>
            <div class='card'>Rules R1-R3</div>
            <div class='card'>Isolation Forest</div>
            <div class='card'>Alerts + metrics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Isolation Forest is a practical baseline only; not claimed optimal for a flight system.")
    st.caption("Phase 2 feasibility demonstrator; Phase 3 would include richer attack models and operator feedback loops.")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
