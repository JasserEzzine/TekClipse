"""Read-only operator views of existing causal snapshots. No detection logic."""
from __future__ import annotations

import pandas as pd
from tekclipse.data.coordinated import ONSET, STAGES

from tekclipse.pipeline.mission_impact import mission_impacts
from tekclipse.pipeline.response import ACTIONS, recommended_responses
from tekclipse.pipeline.subsystems import subsystem_statuses
from tekclipse.dashboard.mission_state import SOURCE_NAMES
from tekclipse.dashboard.mission_visuals import label, badge

FAMILIES = {'R1':'Rule-based detections', 'R2':'Rule-based detections', 'R3':'Rule-based detections',
            'ML':'Isolation Forest anomalies', 'NET':'Network anomalies', 'SYS':'Subsystem events'}
INTERPRETATIONS = {
    'R1':'Command authorization policy violation; verify the origin and operator intent.',
    'R2':'Command-rate policy violation; authorization alone does not make a burst harmless.',
    'R3':'Telemetry hard-limit violation; this does not establish its cause.',
    'NET':'Deviation from the network baseline or authorization context; investigate the actual evidence.',
    'ML':'Statistical deviation from nominal telemetry. Isolation Forest does not classify a confirmed cyberattack.',
    'SYS':'Recognized simulated subsystem event; review the log and surrounding evidence.',
}


def investigation_rows(snapshot):
    permitted = set(recommended_responses(snapshot))
    rows = []
    for alert in sorted(snapshot['active_alerts'], key=lambda a:(pd.Timestamp(a['observed_at']), a['id']), reverse=True):
        associated = [i['id'] for i in snapshot['incidents'] if alert['id'] in i['contributing_alerts']]
        actions = [a for a in ACTIONS.get(alert['source'], []) if a in permitted]
        rows.append(dict(id=alert['id'], observed_at=alert['observed_at'], detector=alert['source'],
                         family=FAMILIES.get(alert['source'], 'Other evidence'), severity=alert['severity'],
                         evidence=alert['description'], subsystem=', '.join(alert.get('subsystems', [])) or 'Unmapped',
                         incidents=', '.join(associated) or 'No association',
                         interpretation=INTERPRETATIONS.get(alert['source'], 'Review the source record.'),
                         action='; '.join(actions) if actions else 'No action recommended by the current response policy.'))
    return rows


def subsystem_briefings(snapshot):
    impacts = mission_impacts(snapshot)
    permitted = set(recommended_responses(snapshot))
    result = []
    for state in subsystem_statuses(snapshot):
        alerts = [a for a in snapshot['active_alerts'] if state['subsystem'] in a.get('subsystems', [])]
        ids = {a['id'] for a in alerts}
        impact = [i['potential_consequence'] for i in impacts if ids.intersection(i['evidence_ids'])]
        actions = sorted({action for a in alerts for action in ACTIONS.get(a['source'], []) if action in permitted})
        result.append(dict(**state, evidence_ids=sorted(ids),
                           incidents=[i['id'] for i in snapshot['incidents'] if ids.intersection(i['contributing_alerts'])],
                           impact=impact[0] if impact else 'No supported mission impact mapped.',
                           action=actions[0] if actions else 'Continue observation; no response required by the current policy.'))
    return result


def replay_stages(history):
    """Only supplied, already-revealed snapshots; never infer missing detections."""
    stages, previous = [], None
    for snapshot in sorted(history, key=lambda s:pd.Timestamp(s['at'])):
        at = pd.Timestamp(snapshot['at'])
        fresh = [a for a in snapshot['active_alerts'] if (previous is None or pd.Timestamp(a['observed_at']) > previous) and pd.Timestamp(a['observed_at']) <= at]
        families = sorted({a['source'] for a in fresh})
        impacts = mission_impacts(snapshot)
        checkpoints = [second for second, _ in STAGES] + [180]
        offset = (at - ONSET).total_seconds()
        stage_number = max(0, sum(second <= offset for second in checkpoints)-1)
        stages.append(dict(number=stage_number, at=snapshot['at'], score=snapshot['score'], status=snapshot['status'],
                           change=0 if not stages else snapshot['score']-stages[-1]['score'],
                           sources=families, evidence_ids=[a['id'] for a in fresh],
                           summary='; '.join(SOURCE_NAMES.get(s,s) for s in families) or 'No new detector evidence',
                           incidents=[i['id'] for i in snapshot['incidents']],
                           implication=impacts[0]['potential_consequence'] if impacts else 'No evidence-based mission impact is mapped.',
                           contributors=snapshot['contributors']))
        previous = at
    return stages


def subsystem_panel(snapshot):
    cards = []
    for index, row in enumerate(subsystem_briefings(snapshot), 1):
        cards.append(f'''<article class="subsystem-card" data-subsystem="{label(row['subsystem'])}" data-status="{row['status']}">
        <div class="subsystem-card-head"><span class="subsystem-index">{index:02d}</span>{badge(row['status'])}</div>
        <h4>{label(row['subsystem'])}</h4><p>{row['evidence_count']} active records · {label(row['reason'])}</p>
        <div class="subsystem-impact">{label(row['impact'])}</div><details><summary>Evidence &amp; operator guidance</summary>
        <p>{label(', '.join(row['evidence_ids']) or 'No mapped alert IDs')}</p>
        <p>Incidents: {label(', '.join(row['incidents']) or 'None')}</p><p>{label(row['action'])}</p></details></article>''')
    return '<section class="subsystem-workspace" aria-label="Five satellite subsystems"><div class="workspace-heading"><div><span class="mission-kicker">ASSET WATCH / SAT-01</span><h3>Five subsystems. One evidence trail.</h3></div><p>Security status, not a diagnosis of physical equipment failure.</p></div><div class="subsystem-cards">'+''.join(cards)+'</div></section>'


def replay_panel(history):
    stages = replay_stages(history)
    if not stages:
        return ''
    current = stages[-1]
    steps = ''.join(f'''<div class="stage-step {'stage-current' if s is current else ''}" data-stage-time="{label(s['at'])}">
        <span class="stage-number">{s['number']:02d}</span><div><time>{pd.Timestamp(s['at']):%H:%M:%S} UTC</time><b>{label(s['summary'])}</b><small>{label(' / '.join(s['sources']) or 'No new source')} · {len(s['evidence_ids'])} new records</small></div><strong>{s['score']}<small>/100</small></strong></div>''' for s in stages)
    return f'''<section class="replay-investigation" aria-label="Observed replay investigation"><div class="workspace-heading"><div><span class="mission-kicker">E7 / INCIDENT INVESTIGATION</span><h3>Follow the evidence.</h3></div><p>Only observations revealed through {pd.Timestamp(current['at']):%H:%M:%S} UTC</p></div>
    <div class="replay-grid"><div class="stage-list">{steps}</div><article class="stage-detail"><span class="mission-kicker">CURRENT REVIEW · STAGE {current['number']:02d}</span><h3>{label(current['summary'])}</h3>
    <div class="stage-score"><b>{current['score']}<small>/100</small></b><span>{current['change']:+d} since previous review<br>{badge(current['status'])}</span></div>
    <p>{len(current['evidence_ids'])} new evidence records. Detectors: {label(', '.join(current['sources']) or 'None at this review')}.</p>
    <p>Associated incidents: <b>{label(', '.join(current['incidents']) or 'None')}</b></p><p>{label(current['implication'])}</p>
    <small>A missing expected alert stays missing. A stage advances the review clock; it does not force a detection or score.</small></article></div></section>'''


def render_investigation(snapshot, prefix):
    import streamlit as st
    with st.expander('Security analyst / investigate observed evidence', expanded=False):
        rows = investigation_rows(snapshot)
        family = st.radio('Evidence family', ['All observed evidence', *dict.fromkeys(FAMILIES.values())], key=prefix+'_investigation_family',horizontal=True)
        visible = rows if family == 'All observed evidence' else [r for r in rows if r['family'] == family]
        if visible:
            ids = [r['id'] for r in visible]
            selected = st.selectbox('Alert to investigate', ids, key=prefix+'_investigation_alert')
            row = next(r for r in visible if r['id'] == selected)
            st.html(f'''<article class="analyst-evidence"><div class="workspace-heading"><span class="mission-kicker">{label(row['family'])} / {label(row['id'])}</span>{badge(row['severity'])}</div>
            <h3>{label(SOURCE_NAMES.get(row['detector'],row['detector']))}</h3><p class="evidence-description">{label(row['evidence'])}</p>
            <dl><dt>Observed UTC</dt><dd>{label(row['observed_at'])}</dd><dt>Detector</dt><dd>{label(row['detector'])}</dd><dt>Asset / subsystem</dt><dd>SAT-01 (simulated) / {label(row['subsystem'])}</dd><dt>Incident association</dt><dd>{label(row['incidents'])}</dd></dl>
            <p>{label(row['interpretation'])}</p><div class="analyst-action"><span class="mission-kicker">OPERATOR GUIDANCE</span>{label(row['action'])}</div></article>''')
            st.dataframe(pd.DataFrame(visible)[['id','observed_at','detector','severity','subsystem','incidents']].head(100),hide_index=True,width='stretch')
            st.caption(f'Showing up to 100 of {len(visible)} currently observed records. Export includes every matching record.')
            st.download_button('Export observed investigation / CSV', pd.DataFrame(visible).to_csv(index=False),
                               file_name='tekclipse-observed-investigation.csv',mime='text/csv',key=prefix+'_investigation_csv')
        else:
            st.info('No observed evidence in this family at the current review time.')
        st.caption('Correlation is temporal association, not attacker attribution. Recommendations are display-only; no spacecraft action is executed.')


def render_research_notes():
    import streamlit as st
    with st.expander('Research validation / what this console can and cannot establish', expanded=False):
        st.markdown('**Synthetic mission, independent evaluation.** Scientific profiles fit and calibrate on separate nominal runs. Model selection uses validation seeds; published results use frozen test seeds. The displayed simulation uses seed 42 and is not that benchmark.')
        st.markdown('**Rules and ML answer different questions.** Rules flag explicit policy/limit violations. Isolation Forest flags statistical deviations, including false positives; it is not a confirmed attack classifier. Deterministic checks already cover standard E7. Phase A.2 adds only 3/9 independent operational anomaly events, versus 6/9 for Phase A.')
        st.caption('Historical scope: E7, seeds 301/302/303, three 24-hour runs. Phase A.2 has 2,732 false-positive seconds and 18/18 source-matched events. These are archived research results, not measurements of the current view.')
        st.markdown('**Trust is policy-based, not a probability of compromise.** Subsystem flags reflect mapped evidence, and mission effects are possible consequences. No real satellite integration, physical failure diagnosis, flight qualification or real-world detection accuracy is claimed.')
