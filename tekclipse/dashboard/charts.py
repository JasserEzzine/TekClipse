from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CYAN, VIOLET, GREEN, AMBER, RED = "#22D3EE", "#8B5CF6", "#34D399", "#FBBF24", "#F87171"
COLORS = [CYAN, VIOLET, GREEN, AMBER, RED, "#60A5FA", "#F472B6"]
LABELS = {
    "temperature_c": "Temperature · °C",
    "cpu_percent": "CPU · %",
    "ram_percent": "RAM · %",
    "battery_percent": "Battery · %",
    "voltage_v": "Voltage · V",
    "power_w": "Power · W",
    "signal_dbm": "Signal · dBm",
}
COLOR_MAP = dict(zip(LABELS, COLORS)) | {
    "TCP": CYAN,
    "UDP": VIOLET,
    "WARNING": AMBER,
    "HIGH": AMBER,
    "CRITICAL": RED,
    "GS_PRIMARY": CYAN,
    "GS_BACKUP": VIOLET,
    "UNKNOWN_1": RED,
}


def style(fig, title="", height=350, time_axis=False):
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=title, font=dict(family="Inter, sans-serif", size=15)),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORS,
        margin=dict(l=35, r=25, t=55, b=35),
        font=dict(family="Inter, sans-serif", color="#C3D2DD", size=12),
        hoverlabel=dict(
            bgcolor="#132b3d", font_family="JetBrains Mono, monospace", font_size=12
        ),
        legend=dict(orientation="h", y=-0.18),
        uirevision=title,
    )
    fig.update_xaxes(gridcolor="rgba(34,211,238,.10)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(34,211,238,.10)", zeroline=False)
    if time_axis:
        fig.update_xaxes(
            rangeslider=dict(visible=True, thickness=0.055),
            rangeselector=dict(
                bgcolor="#0E223E",
                activecolor="#155E75",
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=24, label="24h", step="hour", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
            ),
        )
    return fig


def orbit():
    fig = go.Figure()
    a = np.linspace(0, 2 * np.pi, 100)
    for latitude in np.linspace(-np.pi / 2, np.pi / 2, 13):
        fig.add_trace(
            go.Scatter3d(
                x=np.cos(latitude) * np.cos(a),
                y=np.cos(latitude) * np.sin(a),
                z=np.full_like(a, np.sin(latitude)),
                mode="lines",
                line=dict(color="#12617A", width=1),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    for longitude in np.linspace(0, 2 * np.pi, 18):
        fig.add_trace(
            go.Scatter3d(
                x=np.cos(a) * np.cos(longitude),
                y=np.cos(a) * np.sin(longitude),
                z=np.sin(a),
                mode="lines",
                line=dict(color="#12617A", width=1),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    x, y, z = 1.4 * np.cos(a), 1.4 * np.sin(a) * 0.7, 1.4 * np.sin(a) * 0.714
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color=CYAN, width=4),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=x[-20:],
            y=y[-20:],
            z=z[-20:],
            mode="lines",
            line=dict(color=VIOLET, width=8),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[x[-1]],
            y=[y[-1]],
            z=[z[-1]],
            mode="markers",
            marker=dict(color=GREEN, size=5),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    style(fig, "ORBITAL CONTEXT / SCHEMATIC", 420)
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(0,0,0,0)",
            aspectmode="cube",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
        ),
        margin=dict(l=0, r=0, t=35, b=0),
    )
    return fig


def gauge(result):
    low = min(-0.05, result["score_min"])
    high = max(0.05, result["score_max"])
    threshold = result["threshold"]
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=result["latest_score"],
            number=dict(valueformat=".4f", font=dict(family="JetBrains Mono")),
            gauge=dict(
                axis=dict(range=[low, high]),
                bar=dict(color=CYAN),
                steps=[
                    dict(range=[low, 0], color="rgba(52,211,153,.2)"),
                    dict(range=[0, threshold], color="rgba(251,191,36,.3)"),
                    dict(range=[threshold, high], color="rgba(248,113,113,.3)"),
                ],
                threshold=dict(value=threshold, line=dict(color=RED, width=3)),
            ),
        )
    )
    return style(fig, "LATEST TELEMETRY / IF SCORE", 280)


def telemetry_chart(data, variables, small=False, spans=()):
    df = data["telemetry"]
    if small:
        fig = make_subplots(
            rows=len(variables),
            cols=1,
            shared_xaxes=True,
            subplot_titles=[LABELS[v] for v in variables],
            vertical_spacing=0.06,
        )
    else:
        fig = go.Figure()
    for i, var in enumerate(variables):
        trace = go.Scatter(
            x=df.timestamp,
            y=df[var],
            name=LABELS[var],
            mode="lines",
            line=dict(color=COLOR_MAP[var], width=1.5),
        )
        if small:
            fig.add_trace(trace, row=i + 1, col=1)
        else:
            fig.add_trace(trace)
        if var == "temperature_c":
            kwargs = dict(row=i + 1, col=1) if small else {}
            fig.add_hline(
                y=85,
                line_dash="dot",
                line_color=RED,
                annotation_text="R3 · 85°C",
                **kwargs,
            )
            # Bin maxima keep a short injected step visible even across 30 days.
            fig.add_trace(
                go.Scatter(
                    x=data["extrema"].timestamp,
                    y=data["extrema"]["max"],
                    name="Temperature bin maximum",
                    mode="lines",
                    line=dict(color=RED, width=1, dash="dot"),
                ),
                **kwargs,
            )
    # Merge flags into display bins to bound geometry without hiding flagged bins.
    if spans:
        bins = set()
        step = data["step"]
        for start, end in spans:
            bins.update(
                range(int(start.timestamp()) // step, int(end.timestamp()) // step + 1)
            )
        ordered = sorted(bins)
        groups = []
        for b in ordered:
            if groups and b == groups[-1][1] + 1:
                groups[-1][1] = b
            else:
                groups.append([b, b])
        for a, b in groups:
            # Paper coordinates shade all small multiples with one shape.
            fig.add_shape(
                type="rect",
                xref="x",
                yref="paper",
                x0=pd.Timestamp(a * step, unit="s", tz="UTC"),
                x1=pd.Timestamp((b + 1) * step, unit="s", tz="UTC"),
                y0=0,
                y1=1,
                fillcolor="rgba(248,113,113,.12)",
                line_width=0,
                layer="below",
            )
    style(
        fig,
        "TELEMETRY / NOMINAL PROFILE",
        max(400, 180 * len(variables)) if small else 450,
        time_axis=not small,
    )
    if small:
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeslider_thickness=0.03,
            rangeselector=dict(
                bgcolor="#0E223E",
                activecolor="#155E75",
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=24, label="24h", step="hour", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
            ),
            row=len(variables),
            col=1,
        )
    return fig


def command_charts(commands):
    timeline = px.scatter(
        commands,
        x="timestamp",
        y="type",
        color="source",
        symbol="authorized",
        color_discrete_map=COLOR_MAP,
        symbol_map={True: "circle", False: "x"},
        hover_data=["authorized"],
    )
    cumulative = commands.sort_values("timestamp").assign(
        count=np.arange(1, len(commands) + 1)
    )
    # Preserve endpoints and unauthorized commands when limiting large timelines.
    if len(cumulative) > 4000:
        ix = np.unique(
            np.r_[
                np.linspace(0, len(cumulative) - 1, 4000, dtype=int),
                np.flatnonzero(~cumulative.authorized),
            ]
        )
        cumulative = cumulative.iloc[ix]
    step = go.Figure(
        go.Scatter(
            x=cumulative.timestamp,
            y=cumulative["count"],
            mode="lines",
            line_shape="hv",
            line_color=CYAN,
            name="Commands",
        )
    )
    composition = commands.groupby(["type", "source"]).size().reset_index(name="count")
    sun = px.sunburst(
        composition,
        path=["type", "source"],
        values="count",
        color_discrete_sequence=COLORS,
    )
    return (
        style(timeline, "COMMAND UPLINK / AUTHORIZATION", 400, True),
        style(step, "CUMULATIVE COMMANDS", 300, True),
        style(sun, "COMMAND → SOURCE", 340),
    )


def network_charts(data):
    area = px.area(
        data["area"],
        x="timestamp",
        y="traffic_rate",
        color="protocol",
        color_discrete_map=COLOR_MAP,
    )
    bubble = px.scatter(
        data["bubbles"],
        x="bytes",
        y="packets",
        size="connections",
        color="protocol",
        animation_frame="day",
        animation_group="src_ip",
        hover_data=["src_ip", "dst_ip"],
        color_discrete_map=COLOR_MAP,
        size_max=30,
        range_x=[0, float(data["bubbles"].bytes.max()) * 1.1],
        range_y=[0, float(data["bubbles"].packets.max()) * 1.1],
    )
    donut = px.pie(
        data["protocols"],
        names="protocol",
        values="rows",
        hole=0.75,
        color="protocol",
        color_discrete_map=COLOR_MAP,
    )
    return (
        style(area, "TRAFFIC RATE / PROTOCOL", 360, True),
        style(bubble, "DAILY FLOW TOTALS / CONNECTION-COUNT SUM", 400),
        style(donut, "PROTOCOL / FLOW ROWS", 340),
    )


def event_charts(data, event_type="All"):
    events = data["events"]
    if event_type != "All":
        events = events[events.event_type == event_type]
    grid = (
        events.assign(
            day=events.timestamp.dt.strftime("%Y-%m-%d"), hour=events.timestamp.dt.hour
        )
        .groupby(["day", "hour"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=data["event_grid"].index, columns=range(24), fill_value=0)
    )
    heat = go.Figure(
        go.Heatmap(
            z=grid.values,
            x=list(range(24)),
            y=grid.index,
            colorscale=[[0, "#0A1628"], [0.5, "#155E75"], [1, CYAN]],
            colorbar=dict(title="Events"),
        )
    )
    recent = events.tail(250)
    feed = px.scatter(
        recent,
        x="timestamp",
        y="event_type",
        color="event_type",
        hover_data=["source", "details"],
        color_discrete_sequence=COLORS,
    )
    return style(heat, "EVENT DENSITY / DAY × UTC HOUR", 360), style(
        feed, "EVENT FEED / LATEST 250", 350, True
    )


def alert_charts(alerts, data):
    counts = alerts.groupby("severity").size().reset_index(name="count")
    donut = px.pie(
        counts,
        names="severity",
        values="count",
        color="severity",
        hole=0.75,
        color_discrete_map=COLOR_MAP,
    )
    hourly = (
        alerts.set_index("timestamp")
        .resample("h")
        .size()
        .reindex(data["hourly_alert_bins"], fill_value=0)
    )
    bar = go.Figure(
        go.Bar(x=hourly.index, y=hourly.values, marker_color=AMBER, name="Alerts")
    )
    # Actual alert counts, not invented normalized dimension scores.
    tel = int(alerts.source.isin(["R3", "ML"]).sum())
    cmd = int(alerts.source.isin(["R1", "R2"]).sum())
    radar = go.Figure(
        go.Scatterpolar(
            r=[
                tel,
                cmd,
                int(alerts.source.eq("NET").sum()),
                int(alerts.source.eq("SYS").sum()),
                tel,
            ],
            theta=["Telemetry", "Commands", "Network", "Events", "Telemetry"],
            fill="toself",
            line_color=CYAN,
            name="Alert count",
        )
    )
    style(radar, "ALERT DIMENSIONS / COUNTS", 320)
    radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(gridcolor="#163448"),
            angularaxis=dict(gridcolor="#163448"),
        )
    )
    return (
        style(donut, "SEVERITY DISTRIBUTION", 320),
        style(bar, "ALERTS / UTC HOUR", 340, True),
        radar,
    )
