"""Derive pooled measurements without averaging precision across runs."""
import argparse
import json
from pathlib import Path

import pandas as pd


def summarize(input_path, output):
    report = json.loads(Path(input_path).read_text(encoding='utf-8'))
    groups = {}
    for case in report['cases']:
        cohort = 'regression 301-303' if case['seed'] < 400 else 'independent 601-603'
        for method, metrics in case['comparisons'].items():
            groups.setdefault((cohort, case['case'], method), []).append(metrics)
    rows = []
    for (cohort, case, method), measured in groups.items():
        tp, fp, tn, fn = [sum(m['seconds'][k] for m in measured) for k in ('tp','fp','tn','fn')]
        seconds = sum(m['seconds']['evaluated_seconds'] for m in measured)
        episodes = sum(m['seconds']['false_alarm_episodes'] for m in measured)
        events = [e for m in measured for e in m['events']['details']]
        delays = [e['delay_seconds'] for e in events if e['detected']]
        rows.append(dict(cohort=cohort, case=case, method=method, runs=len(measured), tp=tp, fp=fp, tn=tn, fn=fn,
                         precision=tp/(tp+fp) if tp+fp else None,
                         recall=tp/(tp+fn) if tp+fn else None,
                         f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
                         fpr=fp/(fp+tn) if fp+tn else None,
                         fp_seconds_per_hour=fp/(seconds/3600), false_alarm_episodes=episodes,
                         episodes_per_hour=episodes/(seconds/3600), events_detected=len(delays), events_total=len(events),
                         event_recall=len(delays)/len(events) if events else None,
                         mean_event_delay_seconds=sum(delays)/len(delays) if delays else None))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output/'aggregate-metrics.csv', index=False)
    text = ['# Full pooled before/after measurements', '',
            'Each row pools three independent 24-hour runs (259,200 seconds). Rates use 72 simulated hours. Confusion counts classify seconds; events require the matching detector family inside the exact event interval. A dash means an undefined denominator or no detected event. Delays average detected events only. Full component and ablation rows are in [aggregate-metrics.csv](aggregate-metrics.csv); individual seeds are in [results/metrics.csv](results/metrics.csv).', '',
            '| Cohort / case | Profile | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP s/h | Episodes/h | Events | Event recall | Delay s |',
            '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    def fmt(v):
        return '-' if v is None else f'{v:.4f}' if isinstance(v, float) else str(v)
    for row in rows:
        if row['method'] not in {'Phase A hybrid','Phase A.2 hybrid'}:
            continue
        values = [row['cohort']+' / '+row['case'], row['method'], *[row[k] for k in ('tp','fp','tn','fn','precision','recall','f1','fpr','fp_seconds_per_hour','episodes_per_hour')],
                  f"{row['events_detected']}/{row['events_total']}",row['event_recall'],row['mean_event_delay_seconds']]
        text.append('| '+' | '.join(map(fmt, values))+' |')
    (output/'metrics.md').write_text('\n'.join(text)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('docs/phase-a2/results/test.json'))
    parser.add_argument('--output', type=Path, default=Path('docs/phase-a2'))
    args = parser.parse_args()
    summarize(args.input, args.output)
