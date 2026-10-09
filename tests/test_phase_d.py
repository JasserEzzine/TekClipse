from copy import deepcopy
from pathlib import Path
import json

import pandas as pd
import pytest

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.data.coordinated import ONSET
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import explain_alerts, detect_system_alerts
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.security.evidence import operational_rows, build_findings, csv_export, utc, safe_review
from tekclipse.security.store import EvidenceStore
from tekclipse.security.defense import outcomes, active_policies, evaluate_record
from tekclipse.security.report import incident_report, report_html, sparta_mapping


@pytest.fixture(scope='module')
def nominal():
    return generate_synthetic_dataset(13,persist=False)


def prepared(nominal, scenario='E7', profile='phase_a2'):
    data,_ = get_scenario(scenario)(nominal)
    alerts = detect_rule_alerts(data['commands'],data['telemetry'],r2_mode='rolling' if profile=='phase_a2' else 'fixed')
    alerts += detect_network_alerts(data['network'],fit_network_baseline(nominal['network']))
    alerts += detect_system_alerts(data['system_events'])
    features = nominal['telemetry'].copy()
    evidence = explain_alerts(alerts,data,features,features)
    raw = operational_rows({k:f[f.timestamp.between(ONSET-pd.Timedelta(seconds=180),ONSET+pd.Timedelta(seconds=180))] for k,f in data.items()}, 'run-'+scenario+profile)
    context = dict(run_id='run-'+scenario+profile, scenario=scenario,profile=profile)
    findings = build_findings(evidence,raw,context['run_id'],scenario,profile)
    return context,raw,findings,evidence


def review(store, prepared, second):
    context,raw,findings,evidence = prepared
    snapshot=trust_snapshot(evidence,ONSET+pd.Timedelta(seconds=second),correlation_policy='supported')
    store.record_review(context,raw,findings,snapshot)
    return snapshot


def test_persistence_idempotency_and_replay_rewind(nominal,tmp_path):
    p=prepared(nominal)
    store=EvidenceStore(tmp_path/'evidence.sqlite')
    later=review(store,p,180)
    before=deepcopy(p)
    early=review(store,p,20)
    review(store,p,20)
    reopened=EvidenceStore(store.path)
    rows=reopened.findings(p[0]['run_id'],early['at'])
    assert {f['detector'] for f in rows}=={'R1'}
    assert all(r['timestamp']<=early['at'] for r in reopened.raw(p[0]['run_id'],early['at']))
    assert len(reopened.findings(p[0]['run_id'],later['at']))==len(p[2])
    assert p==before


def test_evidence_provenance_and_source_filters(nominal,tmp_path):
    p=prepared(nominal); store=EvidenceStore(tmp_path/'e.sqlite'); snap=review(store,p,86)
    rows=store.findings(p[0]['run_id'],snap['at'],source='203.0.113.27',detector='NET',severity='HIGH',scenario='E7',incident='INC-001')
    assert rows and all('203.0.113.27' in r['source_ids'] for r in rows)
    assert store.findings(p[0]['run_id'],snap['at'],source='invented')==[]
    index={r['record_id']:r for r in p[1]}
    for finding in p[2]:
        assert all(index[r]['timestamp']<=finding['timestamp'] for r in finding['record_ids'])
    r1=next(r for r in p[2] if r['detector']=='R1')
    assert r1['source_ids']==['UNKNOWN_1'] and not r1['target_ids']
    assert index[r1['record_ids'][0]]['observation']['authorized'] is False


def test_legacy_flood_description_excludes_future_counts(nominal):
    p=prepared(nominal,'E3','original')
    finding=next(f for f in p[2] if f['detector']=='R2')
    assert len(finding['record_ids'])==11
    assert '11 command records observed' in finding['evidence']
    assert 'commands/min' not in finding['evidence']
    snapshot=trust_snapshot(p[3],finding['timestamp'])
    original=deepcopy(snapshot)
    safe=safe_review(snapshot,p[2])
    assert snapshot==original and safe['score']==snapshot['score']
    assert next(a for a in safe['active_alerts'] if a['source']=='R2')['description']==finding['evidence']


def test_unauthorized_rejection_probe_and_reversal(nominal,tmp_path):
    p=prepared(nominal,'E2'); store=EvidenceStore(tmp_path/'e.sqlite'); snap=review(store,p,0)
    exercise=store.exercise(p[0]['run_id']); r1=next(f for f in p[2] if f['detector']=='R1')
    action=store.act(exercise,snap['at'],event_id=r1['event_id'],policy='reject_unauthorized',target='command-channel',reason='Validate R1 authorization rejection')
    assert action['probe_before']['outcome']=='ALLOW' and action['probe_after']['outcome']=='DENY'
    restored=store.act(exercise,snap['at'],event_id=r1['event_id'],reverses=action['action_id'],reason='Restore after rehearsal')
    assert restored['probe_before']['outcome']=='DENY' and restored['probe_after']['outcome']=='ALLOW'
    assert not active_policies(store.actions(exercise,snap['at']),snap['at'])
    assert len(EvidenceStore(store.path).actions(exercise,snap['at']))==2


def test_station_quarantine_enforces_later_commands_and_expires(nominal,tmp_path):
    p=prepared(nominal,'E3'); store=EvidenceStore(tmp_path/'e.sqlite'); snap=review(store,p,20)
    exercise=store.exercise(p[0]['run_id']); r2=next(f for f in p[2] if f['detector']=='R2')
    action=store.act(exercise,snap['at'],event_id=r2['event_id'],policy='quarantine_station',target='GS_PRIMARY',reason='Contain observed rate violation')
    later=review(store,p,58); actions=store.actions(exercise,later['at'])
    evaluated=outcomes(store.raw(p[0]['run_id'],later['at']),actions,later['at'])
    denied=[r for r in evaluated if r['outcome']=='DENY']
    assert len(denied)>=19 and all(r['source']=='GS_PRIMARY' and r['stream']=='commands' for r in denied)
    assert not active_policies(actions,action['expires_at'])
    raw=next(r for r in p[1] if r['record_id']==denied[0]['record_id'])
    assert evaluate_record(raw,actions,at=action['expires_at'])['outcome']=='ALLOW'
    assert trust_snapshot(p[3],later['at'],correlation_policy='supported')==later


def test_network_denylist_affects_only_selected_peer_then_restores(nominal,tmp_path):
    p=prepared(nominal); store=EvidenceStore(tmp_path/'e.sqlite'); snap=review(store,p,45)
    exercise=store.exercise(p[0]['run_id']); f=next(f for f in p[2] if f['detector']=='NET')
    a=store.act(exercise,snap['at'],event_id=f['event_id'],policy='block_network',target='203.0.113.27',reason='Investigate unregistered peer')
    later=review(store,p,86); evaluated=outcomes(p[1],store.actions(exercise,later['at']),later['at'])
    assert sum(r['outcome']=='DENY' for r in evaluated)==41
    assert all(r['outcome']=='ALLOW' for r in evaluated if r['source']!='203.0.113.27')
    restore=store.act(exercise,later['at'],event_id=f['event_id'],reverses=a['action_id'],reason='Restore access')
    assert restore['probe_after']['outcome']=='ALLOW'
    action_list=store.actions(exercise,later['at'])
    sample=next(r for r in p[1] if r['stream']=='network' and r['observation']['src_ip']=='203.0.113.27')
    assert evaluate_record(sample,action_list,at=ONSET+pd.Timedelta(seconds=87))['outcome']=='ALLOW'
    # Earlier admissions still reflect the original restriction after reversal.
    assert evaluate_record(sample,action_list,at=ONSET+pd.Timedelta(seconds=60))['outcome']=='DENY'


def test_actions_reject_future_wrong_run_unsupported_target_and_rewind(nominal,tmp_path):
    p=prepared(nominal); store=EvidenceStore(tmp_path/'e.sqlite'); snap=review(store,p,180)
    exercise=store.exercise(p[0]['run_id']); f=next(f for f in p[2] if f['detector']=='R1')
    for at,target in [(ONSET,'command-channel'),(snap['at'],'invented')]:
        with pytest.raises(ValueError):
            store.act(exercise,at,event_id=f['event_id'],policy='reject_unauthorized',target=target,reason='Test')
    other=store.exercise('different-run')
    with pytest.raises(ValueError):
        store.act(other,snap['at'],event_id=f['event_id'],policy='reject_unauthorized',target='command-channel',reason='Test')
    a=store.act(exercise,snap['at'],event_id=f['event_id'],policy='reject_unauthorized',target='command-channel',reason='Test')
    with pytest.raises(ValueError,match='already active'):
        store.act(exercise,snap['at'],event_id=f['event_id'],policy='reject_unauthorized',target='command-channel',reason='Test')
    with pytest.raises(ValueError,match='before the latest action'):
        store.act(exercise,ONSET+pd.Timedelta(seconds=20),event_id=f['event_id'],reverses=a['action_id'],reason='Test')
    assert store.actions(exercise,ONSET+pd.Timedelta(seconds=86))==[]


def test_incident_export_causal_trust_mapping_and_html_escape(nominal,tmp_path):
    p=prepared(nominal); store=EvidenceStore(tmp_path/'e.sqlite'); review(store,p,180); early=review(store,p,45)
    exercise=store.exercise(p[0]['run_id'])
    document=incident_report(store,p[0]['run_id'],exercise,early['at'],incident_id='INC-001')
    assert set(document['detectors'])=={'R1','NET'} and not document['sparta']
    assert all(r['timestamp']<=early['at'] for r in document['source_records']+document['timeline'])
    assert document['trust']['score']==early['score']
    late=review(store,p,86)
    document=incident_report(store,p[0]['run_id'],exercise,late['at'],incident_id='INC-001')
    assert {m['technique_id'] for m in document['sparta']}=={'EX-0013.01'}
    document['timeline'][0]['evidence']='<script>alert(1)</script>'
    markup=report_html(document)
    assert '<script>' not in markup and '&lt;script&gt;' in markup
    rows=[dict(event_id='=malicious()',source_ids=['203.0.113.27'])]
    assert "'=malicious()" in csv_export(rows)
    assert json.loads(json.dumps(document))==document


@pytest.mark.parametrize('scenario',['E1','E2','E3','E4','E5','E6','E7'])
def test_existing_scenarios_remain_representable(nominal,scenario):
    p=prepared(nominal,scenario)
    assert len(p[2])==len(p[3])
    assert len({r['event_id'] for r in p[2]})==len(p[2])
    assert all(r['record_ids'] for r in p[2])
    if scenario in {'E1','E5'}:
        assert not any(sparta_mapping(f,p[1]) for f in p[2])


def test_protocol_share_is_generator_row_count_not_aggregation_bug(nominal):
    network=nominal['network']
    assert network.protocol.value_counts().to_dict()=={'TCP':23400,'UDP':23400}
    e4=get_scenario('E4')(nominal)[0]['network'].protocol.value_counts()
    e7=get_scenario('E7')(nominal)[0]['network'].protocol.value_counts()
    assert e4['TCP']==23520 and e4['UDP']==23400
    assert e7['TCP']==23400 and e7['UDP']==23516


def test_event_heatmap_uses_date_categories_and_time_legend_clears_slider(nominal):
    from tekclipse.dashboard.charts import event_charts, style
    import plotly.graph_objects as go
    data=dict(events=nominal['system_events'],event_grid=pd.DataFrame(index=['2026-01-01']))
    heat,feed=event_charts(data)
    assert heat.layout.yaxis.type=='category'
    assert heat.layout.xaxis.dtick==1 and not feed.layout.showlegend
    chart=style(go.Figure(),'Timeline',350,True)
    assert chart.layout.margin.b>=150 and chart.layout.legend.y<=-0.6
