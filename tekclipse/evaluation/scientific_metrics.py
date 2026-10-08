"""Separate second, source-matched event and temporal-association measurements."""
from __future__ import annotations

import numpy as np
import pandas as pd

from tekclipse.evaluation.validated import labeled_metrics


def truth_mask(timeline, events):
    truth = np.zeros(len(timeline), dtype=bool)
    for event in events:
        truth |= (timeline >= pd.Timestamp(event['start'])) & (timeline <= pd.Timestamp(event['end']))
    return truth


def intervals_from_mask(timeline, mask):
    edges = np.diff(np.r_[False, mask, False].astype(int))
    return [(timeline[a], timeline[b-1]) for a, b in
            zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))]


def supports_event(alert, event):
    timestamp = pd.Timestamp(alert.get('observed_at', alert['timestamp']))
    return (alert['source'] in event['detectors']
            and pd.Timestamp(event['start']) <= timestamp <= pd.Timestamp(event['end']))


def measure(timeline, events, alerts):
    """Raw alerts remain intact. Episodes are an additional rate, never a TP/FP replacement."""
    truth = truth_mask(timeline, events)
    times = [a.get('observed_at', a['timestamp']) for a in alerts]
    result = labeled_metrics(timeline, truth, times, intervals_from_mask(timeline, truth))
    if not result['available']:
        raise ValueError(result['reason'])
    predicted = timeline.isin(pd.to_datetime(times, utc=True).floor('s'))
    false_episodes = intervals_from_mask(timeline, predicted & ~truth)
    hours = len(timeline) / 3600
    result.update(false_positive_seconds_per_hour=result['fp']/hours,
                  false_alarm_episodes=len(false_episodes),
                  false_alarm_episodes_per_hour=len(false_episodes)/hours,
                  raw_alert_count=len(alerts),
                  # Delay uses the simulation clock; processing time is elsewhere.
                  mean_interval_detection_delay_seconds=result['detection_latency_seconds'])
    event_results = []
    for event in events:
        hits = [pd.Timestamp(a.get('observed_at', a['timestamp']))
                for a in alerts if supports_event(a, event)]
        delay = (min(hits)-pd.Timestamp(event['start'])).total_seconds() if hits else None
        event_results.append(dict(id=event['id'], domain=event['domain'],
                                  detected=bool(hits), delay_seconds=delay))
    detected = sum(e['detected'] for e in event_results)
    delays = [e['delay_seconds'] for e in event_results if e['detected']]
    return dict(seconds=result,
                events=dict(total=len(events), detected=detected,
                            recall=detected/len(events) if events else None,
                            mean_detection_delay_seconds=float(np.mean(delays)) if delays else None,
                            details=event_results))


def measure_incidents(incidents, evidence, events, coordinated):
    """No incident TN universe is invented. Match at least two labeled domains.

    One deliberately combined injection is one reference incident. Additional
    matched fragments are reported, not treated as extra true-positive incidents.
    """
    by_id = {a['id']: a for a in evidence}
    matched, delays = [], []
    for incident in incidents:
        matches = [(by_id[i], e) for i in incident['contributing_alerts']
                   for e in events if supports_event(by_id[i], e)]
        domains = {e['domain'] for _, e in matches}
        valid = coordinated and len(domains) >= 2
        matched.append(valid)
        if valid:
            first = {}
            for alert, event in matches:
                timestamp = pd.Timestamp(alert['observed_at'])
                first[event['domain']] = min(first.get(event['domain'], timestamp), timestamp)
            observable = sorted(first.values())[1]
            onset = min(pd.Timestamp(e['start']) for e in events)
            delays.append((observable-onset).total_seconds())
    count = sum(matched)
    return dict(reference_incidents=int(coordinated), emitted_incidents=len(incidents),
                detected_reference_incidents=int(count > 0), matched_groups=count,
                unmatched_groups=len(incidents)-count, extra_matched_fragments=max(0,count-1),
                group_precision=count/len(incidents) if incidents else None,
                reference_recall=float(count > 0) if coordinated else None,
                first_supported_association_delay_seconds=min(delays) if delays else None,
                true_negatives=None,
                note='Temporal support only; no causal attribution. TN/FPR undefined for incident groups.')
