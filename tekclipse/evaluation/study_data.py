"""Independent simulator runs and explicit source-aware injection ledgers."""
from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd

from tekclipse.data.coordinated import ONSET, ground_truth_intervals
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.scientific_metrics import truth_mask


def fingerprint(data):
    digest = hashlib.sha256()
    for name, frame in sorted(data.items()):
        digest.update(name.encode())
        digest.update(pd.util.hash_pandas_object(frame, index=False).to_numpy().tobytes())
    return digest.hexdigest()


def validate_roles(config):
    roles = [config['training_seed'], config['calibration_seed'],
             *config['validation_seeds'], *config['test_seeds']]
    if len(roles) != len(set(roles)):
        raise ValueError('Training, calibration, validation and test seeds must be disjoint')
    if any(isinstance(s, bool) or not isinstance(s, int) or s < 0 for s in roles):
        raise ValueError('Run seeds must be nonnegative integers')
    if config['hours'] < 13 or not 0 < config['original_train_hours'] < config['hours']:
        raise ValueError('Runs must cover all unchanged scenario injections')
    if not 0 < config['original_quantile'] < config['calibration_quantile'] < 1:
        raise ValueError('Quantiles must satisfy 0 < original < calibrated < 1')
    if not config['validation_seeds'] or not config['test_seeds']:
        raise ValueError('Independent validation and test runs are required')


def event(identifier, start, end, domain, detectors):
    return dict(id=identifier, start=start.isoformat(), end=end.isoformat(),
                domain=domain, detectors=list(detectors))


def standard_events(scenario):
    specifications = {
        'E1': [], 'E2': [('unauthorized', 0, 0, 'Commands', ['R1'])],
        'E3': [('flood', 0, 58, 'Commands', ['R2'])],
        'E4': [('network', 0, 119, 'Network', ['NET'])],
        'E5': [('thermal', 0, 180, 'Telemetry', ['R3', 'ML'])],
        'E7': [('unauthorized', 20, 20, 'Commands', ['R1']),
               ('network', 45, 160, 'Network', ['NET']),
               ('flood', 76, 87, 'Commands', ['R2']),
               ('thermal', 100, 160, 'Telemetry', ['R3', 'ML']),
               ('watchdog', 120, 120, 'System events', ['SYS']),
               ('degraded', 135, 135, 'System events', ['SYS'])],
    }
    if scenario == 'E6':
        return standard_events('E2') + standard_events('E4') + standard_events('E5')
    return [event(f'{scenario}:{name}', ONSET+pd.Timedelta(seconds=a),
                  ONSET+pd.Timedelta(seconds=b), domain, detectors)
            for name, a, b, domain, detectors in specifications[scenario]]


def make_case(nominal, name, config, seed):
    if name in config['scenarios']:
        data, _ = get_scenario(name)(nominal)
        events = standard_events(name)
        timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
        legacy = np.zeros(len(timeline), bool)
        for a, b in ground_truth_intervals(name):
            legacy |= (timeline >= a) & (timeline <= b)
        if not np.array_equal(legacy, truth_mask(timeline, events)):
            raise ValueError('Source ledger must preserve the established union labels')
        return data, events, name in {'E6', 'E7'}
    data = {k: v.copy(deep=True) for k, v in nominal.items()}
    start = nominal['telemetry'].timestamp.min() + pd.Timedelta(seconds=config['variant_start_seconds'])
    end = start + pd.Timedelta(seconds=config['variant_duration_seconds']-1)
    events = []

    def add_commands(times, authorized=True):
        rows = pd.DataFrame(dict(timestamp=times, type='UPLOAD', source='GS_PRIMARY', authorized=authorized))
        data['commands'] = pd.concat([data['commands'], rows], ignore_index=True).sort_values('timestamp', kind='stable').reset_index(drop=True)

    if name == 'benign_command_burst':
        add_commands(pd.date_range(start, periods=config['benign_burst_commands'], freq='s'))
    elif name == 'benign_authorized_peer':
        mask = data['network'].timestamp.between(start, end)
        data['network'].loc[mask, 'src_ip'] = config['benign_peer']
        # Authority is experiment ground truth, not an input available to NET.
    elif name == 'benign_load':
        for field in ('packets', 'bytes', 'traffic_rate'):
            values = data['network'][field] * config['benign_load_multiplier']
            data['network'][field] = values.astype(int) if field != 'traffic_rate' else values
    elif name == 'benign_telemetry':
        rng = np.random.default_rng(seed + 10000)
        for field, deviation in [('temperature_c', config['benign_temperature_noise_sd']),
                                 ('cpu_percent', config['benign_cpu_noise_sd'])]:
            data['telemetry'][field] += rng.normal(0, deviation, len(data['telemetry']))
    elif name == 'attack_primary_unauthorized':
        add_commands([start], authorized=False)
        events.append(event(name, start, start, 'Commands', ['R1']))
    elif name == 'attack_boundary_flood':
        start = start.floor('min') + pd.Timedelta(seconds=54)
        end = start + pd.Timedelta(seconds=11)
        add_commands(pd.date_range(start, end, freq='s'))
        events.append(event(name, start, end, 'Commands', ['R2']))
    elif name == 'attack_low_network':
        mask = data['network'].timestamp.between(start, end)
        for field in ('packets', 'bytes', 'traffic_rate'):
            data['network'].loc[mask, field] *= config['attack_network_multiplier']
        events.append(event(name, start, end, 'Network', ['NET']))
    elif name == 'attack_short_thermal':
        end = start + pd.Timedelta(seconds=config['short_thermal_seconds']-1)
        mask = data['telemetry'].timestamp.between(start, end)
        data['telemetry'].loc[mask, 'temperature_c'] = config['attack_temperature_c']
        events.append(event(name, start, end, 'Telemetry', ['R3', 'ML']))
    elif name == 'attack_reordered':
        # Telemetry precedes network and command, independently of unchanged E7.
        end = start + pd.Timedelta(seconds=config['short_thermal_seconds']-1)
        data['telemetry'].loc[data['telemetry'].timestamp.between(start, end), 'temperature_c'] = config['attack_temperature_c']
        events.append(event(name+':thermal', start, end, 'Telemetry', ['R3', 'ML']))
        network_start = start + pd.Timedelta(seconds=30)
        network_end = network_start + pd.Timedelta(seconds=config['variant_duration_seconds']-1)
        data['network'].loc[data['network'].timestamp.between(network_start, network_end), 'src_ip'] = '203.0.113.99'
        events.append(event(name+':network', network_start, network_end, 'Network', ['NET']))
        command_start = start + pd.Timedelta(seconds=60)
        add_commands([command_start], authorized=False)
        events.append(event(name+':command', command_start, command_start, 'Commands', ['R1']))
    else:
        raise ValueError(f'Unknown study case: {name}')
    return data, events, name == 'attack_reordered'
