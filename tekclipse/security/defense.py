"""Pure simulation admission policy. Never executes infrastructure commands."""
from __future__ import annotations

import pandas as pd

from tekclipse.security.evidence import utc

POLICIES = {'reject_unauthorized': 'Reject unauthorized commands',
            'block_network': 'Block network source', 'quarantine_station': 'Quarantine command station'}


def available_policies(finding, raw):
    records = [r for r in raw if r['record_id'] in finding['record_ids']]
    choices = []
    if finding['detector'] == 'R1' and records:
        choices.append(('reject_unauthorized', 'command-channel'))
    if finding['detector'] in {'R1','R2'}:
        choices.extend(('quarantine_station', s) for s in finding['source_ids'])
    if finding['detector'] == 'NET':
        choices.extend(('block_network', s) for s in finding['source_ids'])
    return choices


def active_policies(actions, at):
    at = utc(at)
    active = {}
    for action in actions:
        if action['timestamp'] > at:
            continue
        if action['operation'] == 'restore':
            active.pop(action['reverses'], None)
        elif at < action['expires_at']:
            active[action['action_id']] = action
    return list(active.values())


def evaluate_record(record, actions, *, at=None):
    """Unrestricted evaluator baseline is ALLOW, not a claim of historical execution."""
    timestamp = utc(at or record['timestamp'])
    sample = record['observation']
    matches = []
    for action in active_policies(actions, timestamp):
        # Policy affects subsequent observations only; original triggering row is preserved.
        if timestamp <= action['timestamp']:
            continue
        policy, target = action['policy'], action['target']
        if record['stream'] == 'commands':
            if policy == 'reject_unauthorized' and (sample.get('source') == 'UNKNOWN_1' or not sample.get('authorized', True)):
                matches.append(action['action_id'])
            if policy == 'quarantine_station' and sample.get('source') == target:
                matches.append(action['action_id'])
        elif record['stream'] == 'network' and policy == 'block_network' and sample.get('src_ip') == target:
            matches.append(action['action_id'])
    return dict(record_id=record['record_id'], timestamp=timestamp, stream=record['stream'],
                source=sample.get('source',sample.get('src_ip','Unknown')),
                baseline='ALLOW', outcome='DENY' if matches else 'ALLOW', matched_actions=matches,
                meaning='Counterfactual simulation admission only; original observation unchanged.')


def outcomes(raw, actions, at):
    actions = [a for a in actions if a['timestamp'] <= utc(at)]
    if not actions:
        return []
    first = min(a['timestamp'] for a in actions)
    return [evaluate_record(r, actions) for r in raw if r['stream'] in {'commands','network'}
            and first < r['timestamp'] <= utc(at)]


def probe(record, actions, at):
    result = evaluate_record(record, actions, at=pd.Timestamp(at)+pd.Timedelta(microseconds=1))
    return dict(result, mode='Explicit synthetic resubmission of an observed payload; not a new detection or future observation.',
                original_timestamp=record['timestamp'])
