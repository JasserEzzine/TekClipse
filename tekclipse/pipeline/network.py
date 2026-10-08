"""Explainable per-second network baseline, fitted only on nominal records."""

from __future__ import annotations

import pandas as pd

METRICS = ("packets", "bytes", "traffic_rate")


def network_seconds(frame):
    data = frame.copy()
    data["timestamp"] = pd.to_datetime(data.timestamp, utc=True).dt.floor("s")
    return data.groupby("timestamp")[list(METRICS)].sum().sort_index()


def fit_network_baseline(nominal):
    if nominal.empty:
        raise ValueError("A nonempty nominal network baseline is required")
    seconds = network_seconds(nominal)
    return {
        "limits": {
            c: max(float(seconds[c].quantile(0.999)) * 1.5, 1.0) for c in METRICS
        },
        "medians": {c: max(float(seconds[c].median()), 1.0) for c in METRICS},
        "categories": {
            c: sorted(nominal[c].astype(str).unique().tolist())
            for c in ("src_ip", "dst_ip", "protocol")
        },
        "spike_limit": max(
            float(seconds.traffic_rate.diff().abs().quantile(0.999)) * 6, 500.0
        ),
    }


def detect_network_alerts(network, baseline, *, authorized_flows=()):
    """One NET alert per anomalous second; repeated rows are summed, not dropped.

    Packet/byte fields are counts per simulator second; traffic_rate has simulator
    units. Category novelty is relative to training, not proof of maliciousness.
    """
    if network.empty:
        return []
    seconds = network_seconds(network)
    reasons = {}
    for column in METRICS:
        limit = baseline["limits"][column]
        for ts, value in seconds.loc[seconds[column] > limit, column].items():
            unit = {
                "packets": "packets/sec",
                "bytes": "bytes/sec",
                "traffic_rate": "traffic-rate units",
            }[column]
            reasons.setdefault(ts, []).append(
                f"{value:.1f} {unit}: {value / baseline['medians'][column]:.1f}x nominal median; threshold {limit:.1f}"
            )
    jumps = seconds.traffic_rate.diff()
    # Only adjacent observations establish a one-second rise.
    adjacent = seconds.index.to_series().diff().eq(pd.Timedelta(seconds=1))
    for ts, value in jumps[(jumps > baseline["spike_limit"]) & adjacent].items():
        reasons.setdefault(ts, []).append(
            f"One-second traffic rise {value:.1f}; threshold {baseline['spike_limit']:.1f}"
        )
    # Explicit operator registration exempts only category novelty, never volume.
    # Every field must match; observing a peer repeatedly does not register it.
    authorized = pd.Series(False, index=network.index)
    for flow in authorized_flows:
        if not {"src_ip", "dst_ip", "protocol"}.issubset(flow):
            raise ValueError("Authorized flows require source, destination and protocol")
        matching = pd.Series(True, index=network.index)
        for column in ("src_ip", "dst_ip", "protocol"):
            matching &= network[column].astype(str).eq(str(flow[column]))
        times = pd.to_datetime(network.timestamp, utc=True)
        if flow.get("valid_from"):
            matching &= times >= pd.to_datetime(flow["valid_from"], utc=True)
        if flow.get("valid_until"):
            matching &= times <= pd.to_datetime(flow["valid_until"], utc=True)
        authorized |= matching
    for column, known in baseline["categories"].items():
        unseen = network.loc[
            ~network[column].astype(str).isin(known) & ~authorized, ["timestamp", column]
        ].copy()
        unseen["timestamp"] = pd.to_datetime(unseen.timestamp, utc=True).dt.floor("s")
        for ts, values in unseen.groupby("timestamp")[column]:
            reasons.setdefault(ts, []).append(
                f"Previously unseen {column}: {', '.join(sorted(set(map(str, values))))}"
            )
    return [
        dict(
            timestamp=ts,
            source="NET",
            severity="HIGH" if len(why) >= 2 else "WARNING",
            description="; ".join(why),
            score=min(1.0, len(why) / 5),
        )
        for ts, why in sorted(reasons.items())
    ]
