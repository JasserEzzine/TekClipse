"""Cache provenance once per detector run, without changing its scientific signature."""
import os

import pandas as pd
import streamlit as st

from tekclipse.data.coordinated import ONSET
from tekclipse.data.injection import get_scenario
from tekclipse.dashboard.data_service import load_data, _detector_signature
from tekclipse.security.evidence import digest, operational_rows, build_findings
from tekclipse.security.store import EvidenceStore


@st.cache_data(max_entries=4, show_spinner=False)
def prepare_evidence(hours, token, scenario, profile, signature, _result):
    result = _result
    data, _ = get_scenario(scenario)(load_data(hours,token))
    start, end = ONSET-pd.Timedelta(seconds=180), ONSET+pd.Timedelta(seconds=180)
    # Keep 60s of preceding feature context. Full raw simulation remains in existing storage.
    bounded = {name:frame.loc[frame.timestamp.between(start-pd.Timedelta(seconds=60),end)].copy() for name,frame in data.items()}
    context = dict(run_id='RUN-'+digest([hours,token,scenario,profile,signature]), scenario=scenario,
                   profile=profile, hours=hours, seed=42, mission_start=start.isoformat(),mission_end=end.isoformat(),
                   scope='Findings in 11:57–12:03 UTC; supporting raw records may include the preceding 60 seconds. Original full-run stores remain available.')
    raw = operational_rows(bounded,context['run_id'])
    alerts = [a for a in result['security']['evidence'] if start<=pd.Timestamp(a['observed_at'])<=end]
    return context, raw, build_findings(alerts,raw,context['run_id'],scenario,profile)


def load_evidence(result):
    hours, token, profile = st.session_state['run_key']
    scenario = st.session_state['scenario']
    context, raw, findings = prepare_evidence(hours,token,scenario,profile,_detector_signature(),result)
    store = EvidenceStore(os.environ.get('TEKCLIPSE_EVIDENCE_DB'))
    if st.session_state.get('defense_run') != context['run_id']:
        st.session_state.pop('defense_exercise', None)
        st.session_state['defense_run'] = context['run_id']
    if 'defense_exercise' not in st.session_state:
        st.session_state['defense_exercise'] = store.exercise(context['run_id'])
    return store, context, raw, findings, st.session_state['defense_exercise']


def reset_defense():
    for key in list(st.session_state):
        if key.startswith('defense_'):
            del st.session_state[key]
    # Explicit widget values also reset the browser's retained frontend state.
    st.session_state['defense_open'] = False
    st.session_state['defense_review_second'] = 160
