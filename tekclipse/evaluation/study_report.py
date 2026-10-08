"""Portable CSV/Markdown tables; JSON retains full event and incident evidence."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def csv_table(path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def ratio(a, b):
    return a/b if b else None


def aggregate(cases):
    groups = defaultdict(list)
    for case in cases:
        for method, metrics in case['comparisons'].items():
            groups[(case['case'], method)].append(metrics)
    rows = []
    for (case, method), metrics in groups.items():
        total = {k:sum(m['seconds'][k] for m in metrics) for k in
                 ('tp','fp','tn','fn','evaluated_seconds','false_alarm_episodes')}
        events = sum(m['events']['total'] for m in metrics)
        detected = sum(m['events']['detected'] for m in metrics)
        delays = [e['delay_seconds'] for m in metrics for e in m['events']['details'] if e['detected']]
        tp, fp, tn, fn = (total[k] for k in ('tp','fp','tn','fn'))
        hours = total['evaluated_seconds']/3600
        rows.append(dict(case=case, method=method, runs=len(metrics), **total,
                         precision=ratio(tp,tp+fp), recall=ratio(tp,tp+fn),
                         f1=ratio(2*tp,2*tp+fp+fn), fpr=ratio(fp,fp+tn),
                         false_positive_seconds_per_hour=fp/hours,
                         false_alarm_episodes_per_hour=total['false_alarm_episodes']/hours,
                         labeled_events=events, detected_events=detected,
                         event_recall=ratio(detected,events),
                         mean_event_delay_seconds=ratio(sum(delays),len(delays))))
    return rows


def export_tables(cases, output):
    output = Path(output)
    rows, incidents, runtime = [], [], []
    for case in cases:
        for method, metrics in case['comparisons'].items():
            rows.append(dict(seed=case['seed'], case=case['case'], method=method,
                             **{k:v for k,v in metrics['seconds'].items() if k!='available'},
                             event_total=metrics['events']['total'], event_detected=metrics['events']['detected'],
                             event_recall=metrics['events']['recall'],
                             event_delay_seconds=metrics['events']['mean_detection_delay_seconds']))
        for method, security in case['security'].items():
            incidents.append(dict(seed=case['seed'], case=case['case'], method=method, **security['incidents']))
        runtime.append(dict(seed=case['seed'], case=case['case'], **case['processing']))
    csv_table(output/'per-run.csv', rows)
    csv_table(output/'incidents.csv', incidents)
    csv_table(output/'processing.csv', runtime)
    summary = aggregate(cases)
    csv_table(output/'comparison.csv', summary)
    csv_table(output/'confusion-matrices.csv', [{k:r[k] for k in ('case','method','tp','fp','tn','fn')} for r in summary])
    csv_table(output/'ablation.csv', [r for r in summary if r['method'] in ('Improved hybrid','Without ML','Without network','Without rules')])
    lines = ['# Measured independent-run results', '',
             'Aggregated within each case across independent seeds. Different scenarios reuse nominal sessions: do not treat their pooled seconds as independent trials. Blank/undefined ratios have no denominator. Episodes are contiguous false-positive seconds, not raw alert rows.', '',
             '| Case | Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP seconds/h | False episodes/h | Event recall | Event delay s |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    def value(item):
        return 'undefined' if item is None else f'{item:.6g}' if isinstance(item,float) else str(item)
    for row in summary:
        lines.append('| '+' | '.join(value(row[k]) for k in ('case','method','tp','fp','tn','fn','precision','recall','f1','fpr','false_positive_seconds_per_hour','false_alarm_episodes_per_hour','event_recall','mean_event_delay_seconds'))+' |')
    (output/'tables.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
