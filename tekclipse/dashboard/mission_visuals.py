"""Original lightweight HTML/SVG mission graphics; all state is supplied by data.

No scripts, external assets, random telemetry or independent scoring logic.
"""

from __future__ import annotations

from html import escape
import base64

import pandas as pd

from tekclipse.pipeline.mission_impact import IMPACT_DISCLAIMER

COLORS = {
    "NORMAL": "#50d9ac",
    "WARNING": "#efba62",
    "SUSPICIOUS": "#efba62",
    "HIGH": "#efba62",
    "CRITICAL": "#ff727c",
    "UNKNOWN": "#8196aa",
}
NAMES = {"NORMAL": "NOMINAL", "SUSPICIOUS": "WARNING"}
SHORT = {
    "Communications": "COMMS",
    "Command channel": "COMMAND",
    "On-board computer": "OBC",
    "Power": "POWER / EPS",
    "Thermal": "THERMAL",
}


def label(value):
    return escape(str(value), quote=True)


def badge(status):
    return f'<span class="mission-badge" style="--state:{COLORS.get(status, COLORS["UNKNOWN"])}"><i></i>{label(NAMES.get(status, status))}</span>'


def svg_image(svg, css_class, description):
    # Streamlit sanitizes inline SVG in st.html. A self-contained image preserves
    # the original vector graphic without scripts or weakening HTML sanitization.
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    embedded_style = "<style>.svg-overline{fill:#92a9b9;font:10px monospace;letter-spacing:1.2px}.svg-label{font:10px monospace}.security-link{animation:linkflow 4s linear 2}@keyframes linkflow{to{stroke-dashoffset:-48}}@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>"
    svg = svg.replace(">", ">" + embedded_style, 1)
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{css_class}" src="data:image/svg+xml;base64,{encoded}" alt="{label(description)}"/>'


def satellite_svg(briefing):
    states = {r["subsystem"]: r["status"] for r in briefing["states"]}
    link = COLORS[briefing["link_status"]]
    thermal = COLORS[states["Thermal"]]
    obc = COLORS[states["On-board computer"]]
    command = COLORS[states["Command channel"]]
    power = COLORS[states["Power"]]
    panel_lines = "".join(
        f'<path d="M{x} 116v74 M{x+222} 116v74"/>' for x in range(368, 490, 20)
    )
    svg = f"""<svg class="spacecraft-scene" viewBox="0 0 820 300" role="img" aria-label="SAT-01 security schematic. Communications {label(states['Communications'])}; command {label(states['Command channel'])}; OBC {label(states['On-board computer'])}; power {label(states['Power'])}; thermal {label(states['Thermal'])}.">
    <defs><radialGradient id="mc-earth"><stop stop-color="#21516b"/><stop offset=".7" stop-color="#102b43"/><stop offset="1" stop-color="#091624"/></radialGradient>
    <linearGradient id="mc-body" x2="1" y2="1"><stop stop-color="#b0c7d4"/><stop offset="1" stop-color="#374e63"/></linearGradient>
    <pattern id="mc-grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" fill="none" stroke="#244258" stroke-width=".5" opacity=".4"/></pattern>
    <clipPath id="mc-globe"><circle cx="147" cy="190" r="79"/></clipPath></defs>
    <rect width="820" height="300" fill="url(#mc-grid)"/>
    <ellipse cx="440" cy="164" rx="322" ry="94" transform="rotate(-13 440 164)" fill="none" stroke="#304958" stroke-dasharray="4 7"/>
    <text x="27" y="30" class="svg-overline">GROUND SEGMENT</text><text x="514" y="30" class="svg-overline">SPACE SEGMENT / SAT-01</text>
    <circle cx="147" cy="190" r="85" fill="none" stroke="#2d6683" opacity=".5"/>
    <circle cx="147" cy="190" r="79" fill="url(#mc-earth)" stroke="#48768c"/>
    <g clip-path="url(#mc-globe)" stroke="#4d8091" stroke-width=".8" fill="none" opacity=".6"><ellipse cx="147" cy="190" rx="38" ry="79"/><ellipse cx="147" cy="190" rx="64" ry="79"/><ellipse cx="147" cy="190" rx="79" ry="32"/><path d="M68 190H226 M147 110V270"/>
    <path d="M94 140l22-12 16 9 9 27-15 12-7 25-20-6-8-19-19-8 M156 154l27-12 35 22-5 21-24 10-6 26-20 6-9-31-13-13z" fill="#386775" stroke="none"/></g>
    <path class="security-link" d="M214 172Q360 52 525 142" fill="none" stroke="{link}" stroke-width="2" stroke-dasharray="5 7"/>
    <circle cx="215" cy="173" r="6" fill="{link}"/><circle cx="521" cy="140" r="4" fill="{link}"/>
    <g stroke="#c1d7e1" stroke-width="2" fill="none"><path d="M193 149q18 26 39 4z M211 163l-9 17 M221 165l6 14 M196 180h35 M215 157l14-17"/><circle cx="230" cy="139" r="2"/></g>
    <rect x="282" y="64" width="164" height="28" rx="5" fill="#0a1b2b" stroke="{link}" stroke-opacity=".6"/>
    <text x="364" y="82" text-anchor="middle" fill="{link}" class="svg-label">LINK SECURITY · {label(NAMES.get(briefing['link_status'],briefing['link_status']))}</text>
    <g transform="rotate(-9 554 155)">
    <path d="M358 107H493V203H358Z M591 107H726V203H591Z" fill="#132c48" stroke="#6484a2"/>
    <g stroke="#587692" stroke-width="1" opacity=".8">{panel_lines}<path d="M358 136h135 M358 160h135 M358 183h135 M591 136h135 M591 160h135 M591 183h135"/></g>
    <path d="M493 149h18 M578 149h13" stroke="{power}" stroke-width="5"/>
    <path d="M507 112l64-20 24 31-64 20z" fill="#ced8d8" stroke="#89a7bc"/>
    <path d="M531 143l64-20v82l-64 23z" fill="url(#mc-body)" stroke="#91adbe"/>
    <path d="M507 112l24 31v85l-24-32z" fill="#4c657b" stroke="#91adbe"/>
    <rect x="546" y="151" width="31" height="32" rx="3" fill="#172838" stroke="{obc}" stroke-width="2"/>
    <path d="M551 157h21v20h-21z M557 151v-6 M568 151v-6 M557 183v6 M568 183v6" fill="none" stroke="{obc}"/>
    <circle cx="548" cy="114" r="12" fill="#172d3c" stroke="{command}" stroke-width="2"/>
    <path d="M548 105v-16l10-9 M546 114h5" stroke="{command}" stroke-width="2"/>
    <path d="M584 160v27" stroke="{thermal}" stroke-width="4"/><circle cx="584" cy="191" r="5" fill="{thermal}"/>
    </g>
    <path d="M538 230v23h75" stroke="#587386" fill="none"/><text x="621" y="258" class="svg-label" fill="#c5d4df">SAT-01 / SIMULATED</text>
    <text x="80" y="289" class="svg-label" fill="#b3c8d5">EARTH / GROUND STATION</text>
    <text x="788" y="290" text-anchor="end" class="svg-overline">SECURITY TOPOLOGY · NOT RF PHYSICS</text></svg>"""
    return svg_image(
        svg,
        "spacecraft-scene",
        "Earth, ground station, communication link and simulated SAT-01; colors show current subsystem security evidence.",
    )


def mission_console(snapshot, briefing, history=()):
    status = snapshot["status"]
    color = COLORS[status]
    at = pd.Timestamp(snapshot["at"])
    elapsed = briefing["elapsed_seconds"]
    timecode = f"+{elapsed // 86400:02d}D {elapsed % 86400 // 3600:02d}:{elapsed % 3600 // 60:02d}:{elapsed % 60:02d}"
    data_status = (
        "LINK DATA ACTIVE" if briefing["network_active"] else "NO RECENT LINK DATA"
    )
    tel_status = (
        "TELEMETRY ACTIVE" if briefing["telemetry_active"] else "TELEMETRY UNAVAILABLE"
    )
    sample = briefing["sample"]
    samples = (
        ""
        if sample is None
        else "".join(
            f"<span>{name}<b>{float(sample[key]):.1f} {unit}</b></span>"
            for name, key, unit in [
                ("THERMAL", "temperature_c", "°C"),
                ("BATTERY", "battery_percent", "%"),
                ("BUS", "voltage_v", "V"),
            ]
        )
    )
    reasons = "".join(
        f'<div class="trust-reason"><span>{label(r["contributor"])}</span><b>−{r["penalty"]}</b></div>'
        for r in snapshot["contributors"]
    )
    if not reasons:
        reasons = '<div class="trust-clear">No active detector evidence<br><small>Across the current review window</small></div>'
    points = ""
    if history:
        points = " ".join(
            f"{8 + index * 224 / max(1, len(history)-1):.1f},{42-r['score']*.34:.1f}"
            for index, r in enumerate(history)
        )
    spark = (
        svg_image(
            f'<svg viewBox="0 0 240 48"><path d="M8 42H232" stroke="#294154"/><polyline points="{points}" stroke="{color}" stroke-width="2" fill="none"/></svg>',
            "trust-spark",
            "Actual calculated trust at observed replay stages",
        )
        if points
        else ""
    )
    subsystems = "".join(
        f'<div class="subsystem-tile"><span>{label(SHORT[r["subsystem"]])}</span>{badge(r["status"])}<small>{r["evidence_count"]} active evidence records</small></div>'
        for r in briefing["states"]
    )
    chain = "".join(
        f'<div class="attack-node" style="--state:{COLORS.get(n["severity"],color)}"><time>{pd.Timestamp(n["at"]):%H:%M:%S}</time><b>{label(n["label"])}</b><small>{len(n["evidence_ids"])} evidence records</small></div>'
        for n in briefing["chain"]
    )
    if not chain:
        chain = '<div class="attack-empty"><span class="monitor-line"></span><b>Monitoring four sources</b><span>No attack evidence in this review window.</span></div>'
    incident = max(
        snapshot["incidents"], key=lambda i: i["correlation_score"], default=None
    )
    if incident:
        incident_body = f'<div class="incident-title">{badge(incident["severity"])}<b>Correlated security incident</b></div><p>{label(" + ".join(incident["sources"]))}</p><span class="mission-muted">{len(incident["contributing_alerts"])} contributing records · association score {incident["correlation_score"]}/100</span>'
    elif snapshot["active_alerts"]:
        incident_body = "<b>Evidence requires review</b><p>Independent anomalies observed. No multi-source incident in this window.</p>"
    else:
        incident_body = "<b>No active security incident</b><p>The implemented checks have no active evidence in this review window.</p>"
    impacts = briefing["impacts"]
    if impacts:
        impact_body = "".join(
            f'<div class="impact-preview"><span>{label(i["subsystem"])}</span><b>{label(i["potential_consequence"])}</b></div>'
            for i in impacts[:2]
        )
        if len(impacts) > 2:
            impact_body += f"<small>{len(impacts)-2} further supported mappings in Mission impact reasoning below.</small>"
    else:
        impact_body = "<b>No evidence-based impact mapped</b><p>No impact inference is raised in this window. This is not a safety certification.</p>"
    responses = briefing["recommendations"]
    response_body = (
        "".join(
            f'<div class="response-preview"><span>{i+1:02d}</span><b>{label(r)}</b></div>'
            for i, r in enumerate(responses[:2])
        )
        if responses
        else "<b>Continue observation</b><p>No high/critical response is recommended by the current evidence.</p>"
    )
    if len(responses) > 2:
        response_body += (
            f"<small>All {len(responses)} recommendations are available below.</small>"
        )
    return f"""<section class="mission-console" style="--state:{color}" data-security="{status}" aria-label="Satellite cybersecurity mission control">
    <div class="mission-status-bar"><div><span class="mission-kicker">MISSION WATCH / SAT-01</span><strong>Satellite security {badge(status)}</strong></div><div class="mission-data-flags"><span>{data_status}</span><span>{tel_status}</span><span>MISSION {timecode}</span><time>{at:%H:%M:%S} UTC</time></div></div>
    <div class="mission-hero-grid"><div class="spacecraft-card"><div class="panel-heading"><span>GROUND-TO-SPACE SECURITY</span><span>Scheduled contact: {label(briefing['scheduled_contact'])}</span></div>{satellite_svg(briefing)}<div class="sample-strip">{samples}<small>Exact stored sample at {at:%H:%M:%S} UTC</small></div></div>
    <div class="operational-trust"><div class="mission-kicker">CAN THE SATELLITE STILL BE TRUSTED?</div><h3>Operational trust</h3><div class="trust-score-row"><div class="trust-ring" style="--progress:{snapshot['score']}%"><strong>{snapshot['score']}<small>/100</small></strong></div><div class="trust-status">{badge(status)}{spark}<span>Calculated from observed evidence</span></div></div><div class="why-heading">WHY THIS TRUST SCORE?</div><div class="trust-reasons">{reasons}</div><div class="trust-disclaimer">Prototype Operational Trust Indicator<br><b>Not a probability of compromise.</b></div></div></div>
    <div class="subsystem-strip">{subsystems}</div>
    <div class="mission-chain"><div class="panel-heading"><span>OBSERVED ATTACK PROGRESSION</span><span>{len(snapshot['active_alerts'])} active alerts · {len(snapshot['incidents'])} incidents</span></div><div class="attack-chain">{chain}</div></div>
    <div class="mission-decisions"><article class="decision-card incident-card"><div class="mission-kicker">01 / ACTIVE INCIDENT</div>{incident_body}<small>Correlation ≠ causation. Anomaly ≠ confirmed attack.</small></article><article class="decision-card"><div class="mission-kicker">02 / POTENTIAL MISSION IMPACT</div>{impact_body}<small>Simulated reasoning; not physical failure prediction.</small></article><article class="decision-card"><div class="mission-kicker">03 / OPERATOR DECISION SUPPORT</div>{response_body}<small>SIMULATED · NO REAL SATELLITE ACTIONS EXECUTED</small></article></div>
    <div class="mission-footer">SYNTHETIC MISSION · {at:%d %b %Y} · trailing {snapshot['window_seconds']}s evidence window · illustrative spacecraft, not flight dynamics</div></section>"""


def impact_reasoning_html(impacts):
    cards = []
    for impact in impacts:
        cells = [
            impact["event"],
            impact["security_consequence"],
            impact["subsystem"],
            impact["potential_consequence"],
        ]
        flow = '<span class="impact-arrow">→</span>'.join(
            f"<span>{label(cell)}</span>" for cell in cells
        )
        cards.append(
            f'<div class="impact-flow">{flow}<small>Evidence: {label(", ".join(impact["evidence_ids"][:3]))}{" …" if len(impact["evidence_ids"]) > 3 else ""}</small></div>'
        )
    return (
        '<div class="impact-reasoning">'
        + "".join(cards)
        + f'<p class="mission-muted">{IMPACT_DISCLAIMER}</p></div>'
    )
