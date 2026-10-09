"""Additive SQLite evidence journal. Original alert/operational stores are untouched."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pandas as pd

from tekclipse.storage.db import ensure_results_dir
from tekclipse.security.evidence import utc, digest, filter_findings
from tekclipse.security.defense import available_policies, active_policies, probe


class EvidenceStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else ensure_results_dir() / 'security-evidence.sqlite'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS defense_runs (run_id TEXT PRIMARY KEY, document TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS defense_raw (run_id TEXT, record_id TEXT, timestamp TEXT, document TEXT NOT NULL, PRIMARY KEY(run_id,record_id));
                CREATE TABLE IF NOT EXISTS defense_findings (run_id TEXT, event_id TEXT, timestamp TEXT, document TEXT NOT NULL, PRIMARY KEY(run_id,event_id));
                CREATE TABLE IF NOT EXISTS defense_reviews (run_id TEXT, at TEXT, document TEXT NOT NULL, PRIMARY KEY(run_id,at));
                CREATE TABLE IF NOT EXISTS defense_exercises (exercise_id TEXT PRIMARY KEY, run_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS defense_actions (sequence INTEGER PRIMARY KEY AUTOINCREMENT, exercise_id TEXT, timestamp TEXT, document TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS defense_actions_exercise ON defense_actions(exercise_id,sequence);
                CREATE INDEX IF NOT EXISTS defense_findings_time ON defense_findings(run_id,timestamp);
                CREATE INDEX IF NOT EXISTS defense_raw_time ON defense_raw(run_id,timestamp);
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def record_review(self, context, raw, findings, snapshot):
        run_id, at = context['run_id'], utc(snapshot['at'])
        with self.connection() as db:
            db.execute('INSERT OR IGNORE INTO defense_runs VALUES (?,?)', (run_id,json.dumps(context)))
            db.executemany('INSERT OR IGNORE INTO defense_raw VALUES (?,?,?,?)',
                           [(run_id,r['record_id'],r['timestamp'],json.dumps(r)) for r in raw if r['timestamp'] <= at])
            db.executemany('INSERT OR IGNORE INTO defense_findings VALUES (?,?,?,?)',
                           [(run_id,r['event_id'],r['timestamp'],json.dumps(r)) for r in findings if r['timestamp'] <= at])
            # Retain only safe reviewed evidence: legacy R2 text may contain future bin totals.
            safe = {r['alert_id']:r['evidence'] for r in findings if r['timestamp'] <= at}
            review = dict(snapshot, active_alerts=[dict(a, description=safe.get(a['id'],a['description'])) for a in snapshot['active_alerts']])
            db.execute('INSERT OR IGNORE INTO defense_reviews VALUES (?,?,?)', (run_id,at,json.dumps(review)))

    def exercise(self, run_id):
        identifier = 'EXERCISE-'+str(uuid4())
        with self.connection() as db:
            db.execute('INSERT INTO defense_exercises VALUES (?,?)', (identifier,run_id))
        return identifier

    def review(self, run_id, at):
        with self.connection() as db:
            row = db.execute('SELECT document FROM defense_reviews WHERE run_id=? AND at=?',(run_id,utc(at))).fetchone()
        if not row:
            raise ValueError('Review has not been recorded')
        return json.loads(row[0])

    def raw(self, run_id, at):
        with self.connection() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT document FROM defense_raw WHERE run_id=? AND timestamp<=? ORDER BY timestamp,record_id',(run_id,utc(at)))]

    def findings(self, run_id, at, **filters):
        review = self.review(run_id, at)
        with self.connection() as db:
            rows = [json.loads(r[0]) for r in db.execute('SELECT document FROM defense_findings WHERE run_id=? AND timestamp<=? ORDER BY timestamp DESC,event_id',(run_id,utc(at)))]
        for row in rows:
            row['incident_ids'] = [i['id'] for i in review['incidents'] if row['alert_id'] in i['contributing_alerts']]
        return filter_findings(rows, at=at, **filters)

    def actions(self, exercise_id, at):
        with self.connection() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT document FROM defense_actions WHERE exercise_id=? AND timestamp<=? ORDER BY sequence',(exercise_id,utc(at)))]

    def act(self, exercise_id, at, *, event_id, policy=None, target=None, reason, reverses=None):
        """Validate against persisted observed evidence; serialize audit/state transitions."""
        at = utc(at)
        if not reason.strip() or len(reason) > 1000:
            raise ValueError('Provide a reason of 1–1000 characters')
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            run = db.execute('SELECT run_id FROM defense_exercises WHERE exercise_id=?',(exercise_id,)).fetchone()
            if not run:
                raise ValueError('Unknown exercise')
            actions = [json.loads(r[0]) for r in db.execute('SELECT document FROM defense_actions WHERE exercise_id=? ORDER BY sequence',(exercise_id,))]
            if actions and at < actions[-1]['timestamp']:
                raise ValueError('Replay is before the latest action. Advance the review or start a new response exercise.')
            found = db.execute('SELECT document FROM defense_findings WHERE run_id=? AND event_id=? AND timestamp<=?',(run[0],event_id,at)).fetchone()
            if not found:
                raise ValueError('Action requires observed evidence from this run')
            finding = json.loads(found[0])
            raw = [json.loads(r[0]) for r in db.execute('SELECT document FROM defense_raw WHERE run_id=? AND timestamp<=?',(run[0],at))]
            active = active_policies(actions, at)
            if reverses:
                original = next((a for a in active if a['action_id']==reverses),None)
                if not original:
                    raise ValueError('Restriction is not active')
                policy, target = original['policy'], original['target']
                if event_id != original['event_id']:
                    raise ValueError('Reversal must retain its original evidence')
            elif (policy,target) not in available_policies(finding,raw):
                raise ValueError('Policy/target is unsupported by the selected evidence')
            elif any(a['policy']==policy and a['target']==target for a in active):
                raise ValueError('This restriction is already active')
            supporting = [r for r in raw if r['record_id'] in finding['record_ids']]
            selected = next((r for r in supporting if r['observation'].get('source',r['observation'].get('src_ip'))==target), supporting[0] if supporting else None)
            if selected is None:
                raise ValueError('No observed payload is available to test')
            action = dict(action_id='ACT-'+str(uuid4()), exercise_id=exercise_id, run_id=run[0],
                          actor='Simulated operator', timestamp=at, recorded_at=pd.Timestamp.now(tz='UTC').isoformat(),
                          target=target, policy=policy, reason=reason.strip(), event_id=event_id,
                          operation='restore' if reverses else 'apply', reverses=reverses,
                          expires_at=utc(pd.Timestamp(at)+pd.Timedelta(seconds=300)),
                          result='Restriction removed' if reverses else 'Simulation policy enabled for 300 simulated seconds')
            action['probe_before'] = probe(selected, actions, at)
            action['probe_after'] = probe(selected, actions+[action], at)
            db.execute('INSERT INTO defense_actions(exercise_id,timestamp,document) VALUES (?,?,?)',(exercise_id,at,json.dumps(action)))
        return action
