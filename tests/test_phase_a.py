"""Independent correctness checks for evaluation and narrowly justified fixes."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.evaluation.validated import labeled_metrics
from tekclipse.evaluation.scientific_metrics import measure, measure_incidents
from tekclipse.evaluation.study_data import validate_roles, make_case, fingerprint
from tekclipse.pipeline.calibration import feature_frame
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.correlation import correlate_alerts
from tekclipse.pipeline.trust import trust_snapshot

ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/'docs/phase-a/protocol.json').read_text())


def test_metric_rejects_ambiguous_units_and_inconsistent_intervals():
    timeline = pd.date_range('2026-01-01', periods=6, freq='s', tz='UTC')
    truth = [False, False, True, True, False, False]
    assert not labeled_metrics(timeline[::2], truth[::2], [], [])["available"]
    assert not labeled_metrics(timeline.tz_localize(None), truth, [], [])["available"]
    assert not labeled_metrics(timeline, truth, [], [])["available"]
    assert not labeled_metrics(timeline, truth, [], [(timeline[2],timeline[3]), (timeline[3],timeline[3])])["available"]
    assert not labeled_metrics(timeline, truth, [], [(timeline[2],timeline[4])])["available"]


def test_sample_event_and_episode_units_are_not_interchanged():
    timeline = pd.date_range('2026-01-01', periods=8, freq='s', tz='UTC')
    event = dict(id='command', start=timeline[3].isoformat(), end=timeline[5].isoformat(), domain='Commands', detectors=['R2'])
    alerts = [dict(timestamp=timeline[i], source='ML') for i in (0,1,4,4,7)]
    result = measure(timeline, [event], alerts)
    assert (result['seconds']['tp'],result['seconds']['fp'],result['seconds']['tn'],result['seconds']['fn']) == (1,3,2,2)
    assert result['seconds']['false_alarm_episodes'] == 2
    assert result['events']['detected'] == 0  # A temporal ML hit cannot detect a command event.
    alerts.append(dict(timestamp=timeline[5],source='R2'))
    result = measure(timeline, [event], alerts)
    assert result['events']['recall'] == 1
    assert result['events']['mean_detection_delay_seconds'] == 2
    nominal = measure(timeline, [], [])
    assert nominal['seconds']['precision'] is None
    assert nominal['seconds']['recall'] is None
    assert nominal['seconds']['f1'] is None
    assert nominal['events']['recall'] is None


def test_seed_roles_disjoint_and_default_generation_preserved(tmp_path):
    config = protocol()
    validate_roles(config)
    with pytest.raises(ValueError):
        validate_roles(dict(config, test_seeds=[config['training_seed']]))
    original = generate_synthetic_dataset(1,persist=False)
    explicit = generate_synthetic_dataset(1,persist=False,seed=42)
    independent = generate_synthetic_dataset(1,tmp_path,seed=101)
    for name in original:
        pd.testing.assert_frame_equal(original[name],explicit[name])
    assert fingerprint(original) != fingerprint(independent)
    assert json.loads((tmp_path/'manifest.json').read_text())['seed'] == 101
    assert fingerprint(independent) == fingerprint(generate_synthetic_dataset(1,persist=False,seed=101))
    for seed in (-1, True, 1.5):
        with pytest.raises(ValueError):
            generate_synthetic_dataset(1,persist=False,seed=seed)


def test_features_are_causal_restart_per_run_and_reject_invalid_data():
    tel = generate_synthetic_dataset(1,persist=False)['telemetry']
    features = feature_frame(tel)
    other = tel.copy()
    other.loc[100:,'temperature_c'] += 200
    pd.testing.assert_frame_equal(features.iloc[:100],feature_frame(other).iloc[:100])
    tail = feature_frame(tel.iloc[100:].reset_index(drop=True))
    assert tail.temperature_c_rolling_mean_60s.iloc[0] == tel.temperature_c.iloc[100]
    assert tail.temperature_c_rolling_std_60s.iloc[0] == 0
    for value in (np.nan,np.inf):
        broken = tel.copy()
        broken.loc[0,'temperature_c'] = value
        with pytest.raises(ValueError):
            feature_frame(broken)
    with pytest.raises(ValueError):
        feature_frame(tel.iloc[::2])


def test_r1_honors_explicit_denial_for_primary_and_other_sources():
    rows = [dict(timestamp='2026-01-01T00:00Z',source=source,type='REBOOT',authorized=authorized)
            for source,authorized in [('GS_PRIMARY',False),('GS_BACKUP',False),('NEW',False),('UNKNOWN_1',True),('GS_PRIMARY',True)]]
    alerts = [a for a in detect_rule_alerts(rows) if a['source']=='R1']
    assert len(alerts) == 4
    assert 'GS_PRIMARY' in alerts[0]['description']


def test_r2_fixed_minute_boundary_and_threshold_are_explicit():
    start = pd.Timestamp('2026-01-01T00:00Z')
    def commands(times):
        return pd.DataFrame(dict(timestamp=times, source='GS_PRIMARY', type='UPLOAD', authorized=True))
    for count,expected in [(10,0),(11,1)]:
        times=pd.date_range(start,periods=count,freq='s')
        assert sum(a['source']=='R2' for a in detect_rule_alerts(commands(times))) == expected
    straddled = pd.date_range(start+pd.Timedelta(seconds=54),periods=12,freq='s')
    assert not detect_rule_alerts(commands(straddled))  # Documented fixed-bin coverage limit.


def test_r3_strict_boundaries_and_sparse_formatting_match_reference():
    tel = pd.DataFrame(dict(timestamp=pd.date_range('2026-01-01',periods=7,freq='s',tz='UTC'),
                            temperature_c=[85,85.01,40,40,40,40,np.nan],
                            voltage_v=[28,28,26,25.99,30,30.01,28]))
    expected=[]
    for _,row in tel.iterrows():
        if row.temperature_c>85 or row.voltage_v<26 or row.voltage_v>30:
            expected.append(dict(timestamp=row.timestamp,source='R3',severity='WARNING',
                                 description=f'Hard limit exceeded: temp={row.temperature_c}C, voltage={row.voltage_v}V',score=.8))
    assert detect_rule_alerts([],tel) == expected


def test_standard_labels_preserved_and_variants_do_not_mutate_nominal():
    nominal=generate_synthetic_dataset(13,persist=False,seed=203)
    before=fingerprint(nominal)
    config=protocol()
    for name in config['scenarios']+config['variants']:
        data,events,_=make_case(nominal,name,config,203)
        if name.startswith('benign'):
            assert not events
        elif name!='E1':
            assert events
        assert fingerprint(nominal)==before
    assert fingerprint(make_case(nominal,'benign_telemetry',config,203)[0]) == fingerprint(make_case(nominal,'benign_telemetry',config,203)[0])


def test_authorized_novel_peer_still_alarms_without_authority_registry():
    config=protocol()
    nominal=generate_synthetic_dataset(13,persist=False,seed=203)
    data,events,_=make_case(nominal,'benign_authorized_peer',config,203)
    alerts=detect_network_alerts(data['network'],fit_network_baseline(nominal['network']))
    assert not events
    assert len(alerts)==config['variant_duration_seconds']
    assert all('Previously unseen src_ip' in a['description'] for a in alerts)


def test_incident_association_requires_supported_distinct_domains_and_no_tn():
    t=pd.Timestamp('2026-01-01T12:00Z')
    evidence=[dict(id=str(i),timestamp=(t+pd.Timedelta(seconds=i)).isoformat(),
                   observed_at=(t+pd.Timedelta(seconds=i)).isoformat(),source=source,severity='CRITICAL')
              for i,source in enumerate(['R1','NET'])]
    events=[dict(id=str(i),start=a['timestamp'],end=a['timestamp'],domain=domain,detectors=[a['source']])
            for i,(a,domain) in enumerate(zip(evidence,['Commands','Network']))]
    incidents=correlate_alerts(evidence)
    result=measure_incidents(incidents,evidence,events,True)
    assert result['reference_recall']==1 and result['first_supported_association_delay_seconds']==1
    assert result['true_negatives'] is None
    assert measure_incidents(incidents,evidence,events,False)['unmatched_groups']==1
    snapshot=trust_snapshot(evidence,t+pd.Timedelta(seconds=1))
    assert snapshot['score']==100-sum(c['penalty'] for c in snapshot['contributors'])
    assert trust_snapshot(evidence*5,t+pd.Timedelta(seconds=1))['score']==snapshot['score']


def test_calibration_fits_only_training_and_uses_separate_nominal_quantile(monkeypatch):
    from tekclipse.pipeline import calibration
    fitted = []

    class Model:
        def decision_function(self, frame):
            return -frame.temperature_c.to_numpy()

    def fit(frame, **kwargs):
        fitted.append(frame.copy())
        return Model(), frame.temperature_c.to_numpy()

    monkeypatch.setattr(calibration, 'build_model', fit)
    training = generate_synthetic_dataset(2,persist=False,seed=101)['telemetry']
    nominal_cal = generate_synthetic_dataset(2,persist=False,seed=202)['telemetry']
    config = dict(protocol(), original_train_hours=1)
    result = calibration.fit_profiles(training,nominal_cal,config)
    assert [len(frame) for frame in fitted] == [3600,7200]
    assert not any('label' in frame.columns for frame in fitted)
    assert result['thresholds']['calibrated'] == np.quantile(nominal_cal.temperature_c,config['calibration_quantile'])
    assert result['thresholds']['original'] == np.quantile(training.temperature_c.iloc[:3600],.95)


def test_csv_sqlite_alert_persistence_and_optional_parquet(tmp_path):
    import importlib.util
    import sqlite3
    from tekclipse.pipeline.alerts import persist_alerts
    alert = dict(timestamp='2026-01-01T12:00:00+00:00',source='R1',severity='CRITICAL',description='test',score=.99)
    persist_alerts([alert],tmp_path)
    assert pd.read_csv(tmp_path/'alerts.csv').source.tolist()==['R1']
    with sqlite3.connect(tmp_path/'alerts.db') as connection:
        assert connection.execute('SELECT source, score FROM alerts').fetchone()==('R1',.99)
    data = generate_synthetic_dataset(1,tmp_path/'data',seed=301)
    if importlib.util.find_spec('pyarrow') is not None:
        for name, frame in data.items():
            pd.testing.assert_frame_equal(frame,pd.read_parquet(tmp_path/'data'/f'{name}.parquet'))


def test_selection_does_not_hide_loss_by_counting_a_different_event():
    from tekclipse.evaluation.scientific import acceptance
    def result(fp, identifiers):
        return dict(seconds=dict(fp=fp),events=dict(details=[dict(id=i,detected=True) for i in identifiers]))
    case=dict(case='E7',comparisons={
        'Original hybrid':result(10,['command','thermal']),
        'Improved hybrid':result(1,['command','network']),
        'ML original':result(10,['thermal']),
        'ML calibrated':result(1,['thermal']),
    })
    assert not acceptance([case])['accepted']
    case['comparisons']['Improved hybrid']=result(1,['command','thermal','network'])
    assert acceptance([case])['accepted']
    case['comparisons']['ML calibrated']=result(1,[])
    assert not acceptance([case])['accepted']
