"""Same scientific model and measurements for CLI and dashboard evaluation."""
import pandas as pd

from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.scientific_metrics import measure
from tekclipse.evaluation.study_data import standard_events
from tekclipse.pipeline.profiles import infer_profile


def evaluate_profile(nominal, scenario, bundle):
    data, _ = get_scenario(scenario)(nominal)
    inferred = infer_profile(bundle, data, explain=False)
    timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
    events = standard_events(scenario)
    parts = inferred['components']
    methods = {'Rules only':parts['rules'], 'ML only':parts['ml'], 'Network only':parts['network'],
               'Without ML':parts['rules']+parts['network']+parts['system'], 'Hybrid':inferred['evidence']}
    measured = {name:measure(timeline, events, alerts) for name,alerts in methods.items()}
    metadata = bundle['metadata']
    return dict(available=True, comparisons={k:v['seconds'] for k,v in measured.items()},
                source_matched_events={k:v['events'] for k,v in measured.items()},
                method=f"{metadata['label']}: shared scientific configuration; independent display seed 42, not the official frozen test set. Prototype synthetic evaluation.",
                train_end=f"independent seed {metadata['config']['training_seed']} (24 h); calibration seed {metadata['config']['calibration_seed']}",
                test_start=timeline.min().isoformat(), test_end=timeline.max().isoformat(),
                profile_metadata=metadata)
