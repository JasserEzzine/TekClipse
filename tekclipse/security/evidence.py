"""Resolve findings to observed inputs without asserting actor identity or causality."""
from __future__ import annotations

import csv
import hashlib
import io
import json

import pandas as pd

CATEGORIES = {'R1': 'Command authorization', 'R2': 'Command rate',
              'R3': 'Telemetry limit', 'ML': 'Statistical anomaly',
              'NET': 'Network anomaly', 'SYS': 'Subsystem event'}
SEVERITY_POLICY = 'Preserve detector severity: R1/R2/SYS CRITICAL; R3/ML WARNING; NET WARNING or HIGH according to its reason count. Not attack certainty.'


def utc(value):
    value = pd.to_datetime(value, utc=True)
    if pd.isna(value):
        raise ValueError('A valid UTC time is required')
    return value.isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()[:24]


def operational_rows(data, run_id):
    """Stable IDs address rows in the supplied run, not authenticated identities."""
    rows = []
    for stream, frame in data.items():
        for position, record in enumerate(frame.to_dict('records')):
            record = dict(record, timestamp=utc(record['timestamp']))
            rows.append(dict(record_id=f'{run_id}:{stream}:{position}', stream=stream,
                             timestamp=record['timestamp'], observation=record))
    return rows


def build_findings(alerts, raw, run_id, scenario, profile):
    by_time = {}
    for record in raw:
        by_time.setdefault((record['stream'], record['timestamp']), []).append(record)
    commands = sorted((r for r in raw if r['stream'] == 'commands'), key=lambda r:r['timestamp'])
    command_times = pd.DatetimeIndex([r['timestamp'] for r in commands])
    findings = []
    for alert in alerts:
        at = utc(alert['observed_at'])
        detector = alert['source']
        stream = {'R1':'commands','R2':'commands','R3':'telemetry','ML':'telemetry',
                  'NET':'network','SYS':'system_events'}.get(detector)
        related = list(by_time.get((stream, at), []))
        relation = 'Same observed sample time; no cross-source causal identifier exists.'
        explanation = alert['description']
        if detector == 'R1':
            related = [r for r in related if r['observation'].get('source') == 'UNKNOWN_1' or not r['observation'].get('authorized', True)]
            related = [r for r in related if f"source {r['observation'].get('source')} with type {r['observation'].get('type')}" in explanation]
            relation = 'Matching timestamp, source, command type and R1 authorization predicate; identical duplicates remain ambiguous.'
        elif detector == 'R2':
            rolling = alert.get('window_kind') == 'rolling60'
            start = pd.Timestamp(at)-pd.Timedelta(seconds=60) if rolling else pd.Timestamp(alert['timestamp']).floor('min')
            left = command_times.searchsorted(start, side='right' if rolling else 'left') if len(commands) else 0
            right = command_times.searchsorted(pd.Timestamp(at), side='right') if len(commands) else 0
            related = commands[left:right]
            # Legacy detector description includes the completed minute's future total.
            explanation = f'R2 threshold >10 crossed; {len(related)} command records observed in the '+('trailing (t-60s, t] window.' if rolling else 'current minute through detection time.')
            relation = 'Aggregate rate evidence; every listed command contributed, but no individual station is proven malicious.'
        elif detector == 'SYS':
            related = [r for r in related if f"{r['observation'].get('event_type')} on {r['observation'].get('source')}:" in explanation]
        elif detector == 'NET':
            relation = 'All flows contributing to the anomalous second. Aggregate evidence does not identify which peer is malicious.'
        elif detector == 'ML':
            related = []
            for second in range(60):
                related.extend(by_time.get(('telemetry', utc(pd.Timestamp(at)-pd.Timedelta(seconds=second))), []))
            relation = 'Available current/trailing 60-second feature inputs, not causal attribution. Training/calibration remain separate.'
        sources = sorted({str(r['observation'][k]) for r in related for k in ('src_ip','source') if k in r['observation']})
        targets = sorted({str(r['observation']['dst_ip']) for r in related if 'dst_ip' in r['observation']})
        findings.append(dict(event_id='EV-'+digest([run_id, alert['id']]), run_id=run_id,
                             alert_id=alert['id'], timestamp=at, scenario=scenario, profile=profile,
                             detector=detector, category=CATEGORIES.get(detector, 'Other finding'),
                             severity=alert['severity'], severity_policy=SEVERITY_POLICY,
                             source_ids=sources, target_ids=targets, asset_context='SAT-01 / single-spacecraft simulation',
                             subsystems=alert.get('subsystems', []), evidence=explanation,
                             record_ids=[r['record_id'] for r in related], provenance=relation,
                             status='Observed; not adjudicated', operator_response=[]))
    return findings


def filter_findings(rows, *, at, start=None, detector=None, scenario=None, severity=None, source=None, incident=None):
    end = utc(at)
    start = utc(start) if start else None
    return [r for r in rows if r['timestamp'] <= end and (not start or r['timestamp'] >= start)
            and (not detector or r['detector'] == detector) and (not scenario or r['scenario'] == scenario)
            and (not severity or r['severity'] == severity) and (not source or source in r['source_ids'])
            and (not incident or incident in r.get('incident_ids', []))]


def safe_review(snapshot, findings):
    """Presentation copy: remove completed-minute totals from causal R2 narration."""
    explanations = {f['alert_id']:f['evidence'] for f in findings if f['timestamp'] <= utc(snapshot['at'])}
    return dict(snapshot, active_alerts=[dict(a, description=explanations.get(a['id'],a['description']))
                                         for a in snapshot['active_alerts']])


def csv_export(rows):
    if not rows:
        return 'event_id,timestamp,detector,severity\n'
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        cells = {}
        for key, value in row.items():
            value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict,list)) else str(value)
            # Spreadsheet formula injection protection; JSON retains exact strings.
            cells[key] = "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r')) else value
        writer.writerow(cells)
    return output.getvalue()
