"""Evidence-qualified SPARTA mapping and portable incident reports."""
import html
import json

from tekclipse.security.defense import outcomes


def sparta_mapping(finding, raw):
    records = [r for r in raw if r['record_id'] in finding['record_ids']]
    if finding['scenario'] in {'E3','E7'} and finding['detector']=='R2' and len(records)>10 and all(r['observation'].get('authorized') is True for r in records):
        return [dict(technique_id='EX-0013.01', name='Flooding: Valid Commands',
                     scenario=finding['scenario'], evidence_id=finding['event_id'],
                     qualification='Behavior-level analogy, moderate confidence. Rate violation with authorized simulated commands; resource exhaustion and malicious intent are not established.',
                     reason='Observed command count exceeds the implemented R2 rate policy.',
                     reference='https://sparta.aerospace.org/technique/EX-0013/01/', verified='2026-10-09')]
    return []


def incident_report(store, run_id, exercise_id, at, *, incident_id=None, event_id=None):
    snapshot = store.review(run_id, at)
    incident = next((i for i in snapshot['incidents'] if i['id']==incident_id),None)
    if incident_id and not incident:
        raise ValueError('No such incident at this review')
    findings = store.findings(run_id, at)
    if incident:
        findings = [f for f in findings if f['alert_id'] in incident['contributing_alerts']]
    elif event_id:
        findings = [f for f in findings if f['event_id']==event_id]
    if not findings:
        raise ValueError('No observed evidence for this report')
    raw = store.raw(run_id, at)
    ids = {r for f in findings for r in f['record_ids']}
    evidence_ids = {f['event_id'] for f in findings}
    context_actions = store.actions(exercise_id,at)
    actions = [a for a in context_actions if a['event_id'] in evidence_ids]
    for finding in findings:
        finding['operator_response'] = [a['action_id'] for a in actions if a['event_id']==finding['event_id']]
        if finding['operator_response']:
            finding['status'] = 'Reviewed with simulated response; original finding retained'
    return dict(schema_version=1, report_type='Correlated incident' if incident else 'Finding investigation',
                incident_id=incident_id, incident=incident, run_id=run_id, exercise_id=exercise_id,
                simulated_review_utc=snapshot['at'], scenario=findings[0]['scenario'], profile=findings[0]['profile'],
                timeline=sorted(findings,key=lambda f:f['timestamp']),
                source_records=[r for r in raw if r['record_id'] in ids],
                detectors=sorted({f['detector'] for f in findings}),
                subsystems=sorted({s for f in findings for s in f['subsystems']}),
                trust=dict(score=snapshot['score'], status=snapshot['status'], deductions=snapshot['contributors'],
                           scope='Full current review window, not a per-incident score; original observations, unchanged by counterfactual responses.'),
                sparta=[m for f in findings for m in sparta_mapping(f,raw)],
                response_actions=actions, exercise_policy_context=context_actions,
                post_response_evaluation=outcomes(raw,context_actions,at),
                uncertainties=['Synthetic simulation; no real attacker identity, firewall or spacecraft control.',
                               'Temporal association is not causality. Sources may be spoofed; no authenticated cross-stream session identifiers.',
                               'Network findings aggregate a second of traffic, not an attribution to each listed peer.',
                               'ML and telemetry anomalies do not prove cyberattack. Unmapped findings lack supported SPARTA technique evidence.',
                               'Admission outcomes and resubmission probes are counterfactual, not reconstructed physical effects.',
                               'Incident IDs are local to a run and review time. Evidence journal covers the documented mission review interval.'])


def report_html(report):
    def esc(value):
        return html.escape(str(value), quote=True)
    first = {}
    for finding in report['timeline']:
        first.setdefault(finding['detector'],finding)
    rows = ''.join('<tr>'+''.join('<td>'+esc(f[k])+'</td>' for k in ('timestamp','detector','severity','evidence'))+'</tr>' for f in first.values())
    actions = ''.join('<li>'+esc(f"{a['timestamp']} · {a['operation']} {a['policy']} / {a['target']}: {a['result']}. Probe {a['probe_before']['outcome']} → {a['probe_after']['outcome']}. Reason: {a['reason']}")+'</li>' for a in report['response_actions'])
    limits = ''.join('<li>'+esc(limit)+'</li>' for limit in report['uncertainties'])
    mappings = ''.join('<li>'+esc(m['technique_id']+' · '+m['name']+' — '+m['qualification']+' Reference: '+m['reference'])+'</li>' for m in report['sparta'])
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>TekClipse incident investigation</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;color:#182c40}td,th{padding:10px;border-bottom:1px solid #ccc;text-align:left}table{width:100%;border-collapse:collapse}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{color:#174b68}</style>'
            '<h1>TekClipse · Incident investigation</h1><p>SIMULATED MISSION — RESEARCH DEMONSTRATOR</p>'
            f'<p>{esc(report["scenario"])} · {esc(report["profile"])} · {esc(report["simulated_review_utc"])}</p>'
            f'<h2>{esc(report["incident_id"] or "Finding report · no correlated incident")}</h2>'
            f'<p>Operational Trust: {report["trust"]["score"]}/100 — policy indicator, not compromise probability.</p>'
            f'<p>{len(report["timeline"])} recorded findings · {len(report["source_records"])} supporting raw records. Subsystems: {esc(", ".join(report["subsystems"]) or "Unmapped")}.</p>'
            '<h2>First observed finding from each detector</h2><table><thead><tr><th>UTC</th><th>Detector</th><th>Severity</th><th>Evidence</th></tr></thead><tbody>'+rows+'</tbody></table>'
            '<h2>Simulated response</h2><ul>'+(actions or '<li>No associated response at this review.</li>')+'</ul>'
            '<h2>Qualified SPARTA mapping</h2><ul>'+(mappings or '<li>Unmapped: insufficient supported technique evidence.</li>')+'</ul>'
            '<h2>Uncertainties</h2><ul>'+limits+'</ul>'
            '<details><summary>Complete timeline, source records, deductions and response audit</summary><pre>'+esc(json.dumps(report,indent=2,ensure_ascii=False))+'</pre></details></html>')
