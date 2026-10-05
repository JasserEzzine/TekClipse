"""Small Plotly views using the existing TekClipse palette."""

import pandas as pd
import plotly.graph_objects as go

from tekclipse.dashboard.charts import style, CYAN, RED as CRITICAL
from tekclipse.pipeline.correlation import DOMAINS


def attack_timeline(evidence, incidents):
    fig = go.Figure()
    # Collapse adjacent samples into episodes for display only; incidents keep IDs.
    for source in sorted({a["source"] for a in evidence}):
        rows = sorted(
            [a for a in evidence if a["source"] == source],
            key=lambda a: a["observed_at"],
        )
        episodes = []
        for row in rows:
            ts = pd.Timestamp(row["observed_at"])
            if episodes and ts - episodes[-1]["end"] <= pd.Timedelta(seconds=5):
                episodes[-1]["end"] = ts
                episodes[-1]["count"] += 1
            else:
                episodes.append(
                    dict(start=ts, end=ts, count=1, description=row["description"])
                )
        fig.add_trace(
            go.Scatter(
                x=[r["start"] for r in episodes],
                y=[DOMAINS.get(source, source)] * len(episodes),
                mode="markers",
                name=source,
                marker=dict(size=12, color=CYAN if source == "ML" else CRITICAL),
                text=[
                    f"{source}: {r['description']}<br>{r['count']} samples; through {r['end']}"
                    for r in episodes
                ],
                hovertemplate="%{x}<br>%{text}<extra></extra>",
            )
        )
    if incidents:
        fig.add_trace(
            go.Scatter(
                x=[i["end"] for i in incidents],
                y=["Correlated incident"] * len(incidents),
                mode="markers",
                name="Incidents",
                marker=dict(symbol="diamond", size=18, color=CRITICAL),
                text=[i["severity"] + ": " + i["explanation"] for i in incidents],
                hovertemplate="%{x}<br>%{text}<extra></extra>",
            )
        )
    fig.update_xaxes(title="Observation time / UTC")
    return style(fig, "ATTACK CHAIN / OBSERVED EVIDENCE", 330)


def trust_history(history):
    fig = go.Figure(
        go.Scatter(
            x=[r["at"] for r in history],
            y=[r["score"] for r in history],
            mode="lines+markers",
            line=dict(color=CYAN, shape="hv"),
            name="Trust indicator",
        )
    )
    fig.add_hline(y=80, line_dash="dot", line_color="#34D399")
    fig.add_hline(y=50, line_dash="dot", line_color=CRITICAL)
    fig.update_yaxes(range=[0, 105], title="Prototype trust / 100")
    fig.update_xaxes(title="Simulation time / UTC")
    return style(fig, "TRUST PROGRESSION / POLICY INDICATOR", 260)
