from copy import deepcopy
from pathlib import Path
import base64
import re

import pandas as pd
from streamlit.testing.v1 import AppTest

from tekclipse.data.coordinated import ONSET
from tekclipse.dashboard.investigation import investigation_rows, subsystem_briefings, replay_stages, replay_panel, subsystem_panel
from tekclipse.dashboard.mission_visuals import mission_console, satellite_svg
from tekclipse.dashboard.mission_state import mission_briefing
from tekclipse.pipeline.subsystems import SUBSYSTEMS
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.response import recommended_responses


def alert(source, second, subsystem, severity='CRITICAL'):
    return dict(id=f'{source}-{second}',timestamp=(ONSET+pd.Timedelta(seconds=second)).isoformat(),
                observed_at=(ONSET+pd.Timedelta(seconds=second)).isoformat(),source=source,severity=severity,
                description=f'Actual {source} observation',subsystems=[subsystem])


def evidence():
    return [alert('R1',20,'Command channel'),alert('NET',45,'Communications','HIGH'),
            alert('R3',100,'Thermal','WARNING'),alert('SYS',120,'On-board computer'),
            alert('ML',150,'Thermal','WARNING')]


def test_investigation_only_contains_observed_evidence_and_real_incident_ids():
    snapshot = trust_snapshot(evidence(), ONSET+pd.Timedelta(seconds=45), correlation_policy='supported')
    original = deepcopy(snapshot)
    rows = investigation_rows(snapshot)
    assert {r['detector'] for r in rows} == {'R1','NET'}
    assert all(r['incidents'] == snapshot['incidents'][0]['id'] for r in rows)
    assert all(pd.Timestamp(r['observed_at']) <= pd.Timestamp(snapshot['at']) for r in rows)
    assert snapshot == original


def test_subsystem_cards_preserve_names_status_and_supported_actions():
    snapshot = trust_snapshot(evidence(), ONSET+pd.Timedelta(seconds=120), correlation_policy='supported')
    rows = subsystem_briefings(snapshot)
    assert tuple(r['subsystem'] for r in rows) == SUBSYSTEMS
    power = next(r for r in rows if r['subsystem']=='Power')
    assert power['status']=='NORMAL' and power['evidence_ids']==[] and power['incidents']==[]
    assert power['impact']=='No supported mission impact mapped.'
    permitted = recommended_responses(snapshot)
    assert all(r['action'] in permitted for r in rows if r['evidence_ids'])
    markup = subsystem_panel(snapshot)
    assert markup.count('data-subsystem=') == 5
    assert all(name in markup for name in SUBSYSTEMS)


def test_replay_uses_actual_score_changes_and_does_not_invent_ml():
    history = [trust_snapshot(evidence(), ONSET+pd.Timedelta(seconds=s),correlation_policy='supported') for s in [0,20,45,86,100,120]]
    original = deepcopy(history)
    stages = replay_stages(history)
    assert [s['score'] for s in stages] == [s['score'] for s in history]
    assert stages[-1]['sources'] == ['SYS']
    assert 'ML-150' not in replay_panel(history)
    assert 'Telemetry deviation' not in replay_panel(history)
    assert stages[-1]['change'] == history[-1]['score']-history[-2]['score']
    assert history == original


def test_custom_replay_time_does_not_invent_an_extra_stage():
    history = [trust_snapshot(evidence(),ONSET+pd.Timedelta(seconds=s)) for s in [0,20,30]]
    stages = replay_stages(history)
    assert [s['number'] for s in stages] == [0,1,1]
    assert stages[-1]['summary']=='No new detector evidence'
    assert stages[-1]['evidence_ids']==[]


def test_nominal_panels_do_not_fabricate_an_incident_or_response():
    snapshot = trust_snapshot([],ONSET)
    assert investigation_rows(snapshot)==[]
    assert all(not r['evidence_ids'] for r in subsystem_briefings(snapshot))
    markup = mission_console(snapshot,mission_briefing(snapshot),scenario='E1')
    assert 'aria-valuenow="100"' in markup and 'No observed detections' in markup
    assert 'No recent telemetry sample' in markup
    assert 'response-preview' not in markup and 'impact-preview' not in markup


def test_missing_network_data_is_neutral_and_operator_text_is_escaped():
    snapshot = trust_snapshot([],ONSET)
    image = satellite_svg(mission_briefing(snapshot))
    svg = base64.b64decode(re.search(r'base64,([^\"]+)',image).group(1)).decode()
    assert 'LINK SECURITY · UNKNOWN' in svg
    bad = alert('R1',20,'Command channel')
    bad['description']='<script>untrusted()</script>'
    snapshot = trust_snapshot([bad],ONSET+pd.Timedelta(seconds=20))
    markup = mission_console(snapshot,mission_briefing(snapshot),scenario='<unsafe>')
    assert '<script>' not in markup and '<unsafe>' not in markup
    assert '&lt;script&gt;' in markup


def test_analyst_filters_reset_and_export_are_integrated():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'streamlit_app.py'),default_timeout=240).run()
    app.selectbox(key='detection_profile').set_value('phase_a2').run()
    app.button(key='mission_E7').click().run()
    for _ in range(5):
        app.button(key='overview_next_stage').click().run()
    assert not app.exception
    assert app.session_state['overview_replay_second']==120
    app.radio(key='overview_investigation_family').set_value('Rule-based detections').run()
    assert not app.exception
    assert app.selectbox(key='overview_investigation_alert').options
    app.radio(key='overview_investigation_family').set_value('Isolation Forest anomalies').run()
    assert not app.exception
    # Actual selected profile has no ML at +120; present an empty view, not an invented hit.
    snapshot = trust_snapshot(app.session_state['result']['security']['evidence'],ONSET+pd.Timedelta(seconds=120),correlation_policy='supported')
    if not any(a['source']=='ML' for a in snapshot['active_alerts']):
        assert any('No observed evidence in this family' in item.value for item in app.info)
    app.button(key='mission_reset').click().run()
    assert not app.exception and app.session_state['scenario']=='E1'
    assert app.radio(key='overview_investigation_family').value=='All observed evidence'
    assert len(app.tabs)==8
