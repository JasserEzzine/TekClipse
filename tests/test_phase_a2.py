"""Phase A.2 contracts; all historical tests remain untouched."""
import numpy as np
import pandas as pd
import pytest

from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import detect_network_alerts, fit_network_baseline
from tekclipse.pipeline.correlation import correlate_alerts
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.research_features import fit_relationships, research_features
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario

START = pd.Timestamp('2026-01-01T12:00:00Z')


def commands(seconds):
    return pd.DataFrame(dict(timestamp=[START + pd.Timedelta(seconds=s) for s in seconds],
                             source='GS_PRIMARY', type='UPLOAD', authorized=True))


def floods(seconds):
    return [a for a in detect_rule_alerts(commands(seconds), r2_mode='rolling') if a['source'] == 'R2']


@pytest.mark.parametrize('seconds,count,first', [
    (list(range(11)), 1, 10), (list(range(54, 65)), 1, 64),
    (list(range(10)), 0, None), ([0]*10 + [60], 0, None),
    ([0]*10 + [59.999], 1, 59.999), ([0]*11, 1, 0),
    (list(range(300)), 1, 10), (list(range(11)) + list(range(120, 131)), 2, 10),
    (list(reversed(range(54, 65))), 1, 64),
    ([0]*11 + [60]*11, 1, 0), ([0]*11 + [61]*11, 2, 0),
])
def test_rolling_boundaries_simultaneity_and_episodes(seconds, count, first):
    alerts = floods(seconds)
    assert len(alerts) == count
    if count:
        assert alerts[0]['timestamp'] == START + pd.Timedelta(seconds=first)
        assert alerts[0]['window_kind'] == 'rolling60'
        assert alerts[0]['severity'] == 'CRITICAL'


@pytest.mark.parametrize('scenario', ['E3', 'E6', 'E7'])
def test_rolling_standard_command_scenarios(scenario):
    data, _ = get_scenario(scenario)(generate_synthetic_dataset(13, persist=False, seed=503))
    alerts = detect_rule_alerts(data['commands'], data['telemetry'], r2_mode='rolling')
    assert any(a['source'] == ('R1' if scenario == 'E6' else 'R2') for a in alerts)


def test_explicit_network_flow_registration_does_not_hide_volume_or_other_flows():
    nominal = generate_synthetic_dataset(1, persist=False, seed=501)['network']
    baseline = fit_network_baseline(nominal)
    changed = nominal.copy()
    changed['src_ip'] = '10.0.0.99'
    registry = [dict(src_ip='10.0.0.99', dst_ip=dst, protocol=protocol)
                for dst, protocol in [('10.1.0.5', 'TCP'), ('10.1.0.6', 'UDP')]]
    assert len(detect_network_alerts(changed, baseline)) == len(changed)
    assert detect_network_alerts(changed, baseline, authorized_flows=registry) == []
    changed.loc[0, 'protocol'] = 'UNREGISTERED'
    assert len(detect_network_alerts(changed, baseline, authorized_flows=registry)) == 1
    changed.loc[1, 'traffic_rate'] = baseline['limits']['traffic_rate'] * 2
    assert len(detect_network_alerts(changed, baseline, authorized_flows=registry)) >= 2
    expired = [dict(f, valid_until='2025-12-31T23:59:59Z') for f in registry]
    assert len(detect_network_alerts(changed, baseline, authorized_flows=expired)) == len(changed)
    assert baseline['categories']['src_ip'] == sorted(nominal.src_ip.unique().tolist())


def evidence(source, index, asset='SAT01'):
    return dict(id=f'A{index}', source=source, timestamp=START.isoformat(), observed_at=START.isoformat(),
                severity='WARNING' if source == 'ML' else 'CRITICAL', asset_id=asset)


def test_correlation_requires_independent_non_ml_domains_and_unique_evidence():
    command, ml, net = evidence('R1', 1), evidence('ML', 2), evidence('NET', 3)
    assert correlate_alerts([command, ml])
    assert correlate_alerts([command, ml], policy='supported') == []
    incident = correlate_alerts([command, ml, net, net], policy='supported')[0]
    assert incident['contributing_alerts'] == ['A1', 'A2', 'A3']
    assert incident['sources'] == ['Commands', 'Network']
    assert incident['severity'] == 'HIGH'
    assert correlate_alerts([command, evidence('NET', 3, 'SAT02')], policy='supported') == []
    with pytest.raises(ValueError, match='Conflicting'):
        correlate_alerts([net, dict(net, severity='WARNING')], policy='supported')


def test_trust_penalties_unchanged_and_no_ml_correlation_bonus():
    alerts = [evidence('R1', 1), evidence('ML', 2)]
    hardened = trust_snapshot(alerts, START, correlation_policy='supported')
    assert hardened['score'] == 78  # 20 + round(3 * .75), unchanged formula
    assert trust_snapshot(alerts, START)['score'] == 68
    duplicated = trust_snapshot(alerts + alerts, START, correlation_policy='supported')
    assert duplicated['score'] == hardened['score']
    assert trust_snapshot(alerts, START + pd.Timedelta(seconds=181), correlation_policy='supported')['score'] == 100


def test_research_features_are_nominal_fitted_causal_and_deterministic():
    tel = generate_synthetic_dataset(1, persist=False, seed=501)['telemetry']
    relationships = fit_relationships(tel)
    full = research_features(tel, 'relationships9', relationships)
    assert len(full.select_dtypes(include='number').columns) == 9
    changed = tel.copy()
    changed.loc[100:, 'power_w'] += 8
    other = research_features(changed, 'relationships9', relationships)
    pd.testing.assert_frame_equal(full.iloc[:100], other.iloc[:100])
    pd.testing.assert_frame_equal(full, research_features(tel, 'relationships9', relationships))
    assert np.isfinite(full.select_dtypes(include='number')).all().all()


def test_rolling_matches_brute_force_threshold_transitions():
    rng = np.random.default_rng(920)
    seconds = np.sort(rng.integers(0, 1200, 220))
    # Evaluate all arrivals/expirations, including simultaneous expiry + arrival.
    instants = sorted(set(seconds) | set(seconds + 60))
    expected, active = [], False
    for instant in instants:
        anomalous = ((seconds > instant-60) & (seconds <= instant)).sum() > 10
        if anomalous and not active:
            expected.append(START + pd.Timedelta(seconds=int(instant)))
        active = anomalous
    assert [a['timestamp'] for a in floods(seconds)] == expected


def test_selected_profile_and_cli_dashboard_share_scoring_without_refitting(monkeypatch):
    import json
    from pathlib import Path
    from tekclipse.pipeline.profiles import fit_profile, infer_profile, CONFIG_PATH
    from tekclipse.evaluation.profile_evaluation import evaluate_profile
    from tekclipse.dashboard import data_service
    from tekclipse.evaluation.scientific_metrics import measure
    from tekclipse.evaluation.study_data import standard_events

    selection = json.loads((Path(__file__).resolve().parents[1]/'docs/phase-a2/selection.json').read_text())
    bundle = fit_profile('phase_a2')
    assert bundle['metadata']['config']['feature_mode'] == selection['selected']['mode']
    assert bundle['threshold'] == pytest.approx(selection['selected']['threshold'], abs=1e-12)
    nominal = generate_synthetic_dataset(24, persist=False, seed=42)
    data, _ = get_scenario('E7')(nominal)
    # Inference must use the already-fitted independent bundle.
    monkeypatch.setattr(bundle['model'], 'fit', lambda *a, **k: pytest.fail('Unexpected refit'))
    inferred = infer_profile(bundle, data, explain=False)
    cli = evaluate_profile(nominal, 'E7', bundle)
    assert cli['comparisons']['Hybrid'] == measure(pd.DatetimeIndex(data['telemetry'].timestamp), standard_events('E7'), inferred['evidence'])['seconds']
    monkeypatch.setattr(data_service, 'scientific_bundle', lambda *args: bundle)
    preview = data_service._scientific_preview(nominal, 'E7', 'phase_a2', 'test', 0)
    observed = [dict(a) for a in preview['security']['evidence']]
    assert measure(pd.DatetimeIndex(data['telemetry'].timestamp), standard_events('E7'), observed)['seconds'] == cli['comparisons']['Hybrid']
    assert preview['profile_metadata'] == cli['profile_metadata']
    assert preview['security']['correlation_policy'] == 'supported'
    with pytest.raises(ValueError, match='nominal'):
        data_service.save_nominal_preview(24, 'test', dict(preview, scenario='E1'))
    signature = data_service._detector_signature()
    # Verify the JSON configuration actually participates in cache invalidation.
    original_read = Path.read_bytes
    monkeypatch.setattr(Path, 'read_bytes', lambda path: original_read(path)+b' ' if path == CONFIG_PATH else original_read(path))
    assert data_service._detector_signature() != signature
