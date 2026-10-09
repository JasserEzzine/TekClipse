"""Manual investigation -> admission policy -> audit -> report workflow."""
import html
import json

import pandas as pd
import streamlit as st

from tekclipse.dashboard.defense_service import load_evidence
from tekclipse.security.evidence import csv_export, filter_findings
from tekclipse.security.defense import available_policies, active_policies, outcomes, POLICIES
from tekclipse.security.report import incident_report, report_html, sparta_mapping


def choose(label, options, key):
    if st.session_state.get(key) not in options:
        st.session_state[key] = options[0]
    return st.selectbox(label,options,key=key)


def render_defense(snapshot, result, prefix, *, journal=None):
    store, context, raw, findings, exercise = journal or load_evidence(result)
    at, run_id = snapshot['at'], context['run_id']
    store.record_review(context,raw,findings,snapshot)
    if not st.session_state.get('defense_open'):
        return
    key = 'defense_'+prefix
    observed = store.findings(run_id,at)
    recorded_actions = store.actions(exercise,at)
    for row in observed:
        row['operator_response'] = [a['action_id'] for a in recorded_actions if a['event_id']==row['event_id']]
        if row['operator_response']:
            row['status'] = 'Reviewed with simulated response; original finding retained'
    raw = store.raw(run_id,at)
    st.html('<section class="defense-heading"><span class="mission-kicker">CYBER DEFENSE / MANUAL SIMULATION</span><h2>Evidence → Investigation → Response → Report</h2><p>Review what happened, test a restriction, and preserve the audit trail.</p></section>')
    st.caption(f"{context['scenario']} / {context['profile']} · Reviewed through {at} · Exercise {exercise[-8:]} · Manual actions only")
    st.caption('Persistent evidence journal: 11:57–12:03 UTC on 1 January 2026. Future records remain hidden. Original full-run analytical tabs remain available.')
    with st.container(border=True):
        st.markdown('### 1 · Security event log')
        a,b,c = st.columns(3)
        with a:
            detector = choose('Detector', ['All']+sorted({r['detector'] for r in observed}),key+'_detector')
            source = choose('Source identifier', ['All']+sorted({s for r in observed for s in r['source_ids']}),key+'_source')
        with b:
            severity = choose('Severity', ['All']+sorted({r['severity'] for r in observed}),key+'_severity')
            incident = choose('Incident association', ['All']+[i['id'] for i in snapshot['incidents']],key+'_incident')
        with c:
            scenario = choose('Scenario scope',['All',context['scenario']],key+'_scenario')
            start = st.text_input('From UTC (inclusive)',context['mission_start'],key=key+'_start')
        try:
            visible = filter_findings(observed,at=at,start=start,**{k:None if v=='All' else v for k,v in dict(detector=detector,source=source,severity=severity,incident=incident,scenario=scenario).items()})
        except (ValueError,TypeError):
            st.error('Enter a valid UTC start timestamp.'); return
        st.caption(f'{len(visible)} matching findings · detector-assigned severity, not certainty of an attack · table shows latest 200')
        if visible:
            frame = pd.DataFrame(visible)[['event_id','timestamp','detector','severity','source_ids','incident_ids','evidence']]
            st.dataframe(frame.head(200),hide_index=True,width='stretch')
        a,b = st.columns(2)
        a.download_button('Export security log / CSV',csv_export(visible),'tekclipse-security-log.csv','text/csv',key=key+'_csv')
        b.download_button('Export security log / JSON',json.dumps(visible,indent=2),'tekclipse-security-log.json','application/json',key=key+'_json')
    if not visible:
        st.info('No findings match this review and filter. Normal operational records are not labeled attacks.'); return
    selected = choose('Finding to investigate',[f['event_id'] for f in visible],key+'_finding')
    finding = next(f for f in visible if f['event_id']==selected)
    records = [r for r in raw if r['record_id'] in finding['record_ids']]
    e = lambda value:html.escape(str(value),quote=True)
    st.html(f'<article class="defense-evidence"><span class="mission-kicker">2 / INVESTIGATION · {e(finding["detector"])} · {e(finding["alert_id"])}</span><h3>{e(finding["category"])}</h3><span class="defense-severity">{e(finding["severity"])}</span><p>{e(finding["evidence"])}</p><dl><dt>Observed UTC</dt><dd>{e(finding["timestamp"])}</dd><dt>Source</dt><dd>{e(", ".join(finding["source_ids"]) or "Unknown — no source identity in this stream")}</dd><dt>Target / subsystem</dt><dd>{e(", ".join(finding["target_ids"]+finding["subsystems"]) or "Unmapped")} · SAT-01 simulation context</dd><dt>Provenance</dt><dd>{e(finding["provenance"])}</dd></dl><p>Known: the recorded detector condition. Unknown: actor identity, intent, physical effects and cross-stream causality.</p></article>')
    with st.expander('Supporting raw records and related findings'):
        st.json(records)
        related = [f for f in observed if f['event_id']!=selected and (set(f['source_ids']) & set(finding['source_ids']) or set(f['incident_ids']) & set(finding['incident_ids']))]
        st.caption('Related by shared recorded source or current temporal incident, not proven common actor.')
        st.dataframe(pd.DataFrame(related).head(100),hide_index=True,width='stretch')
    for inc in snapshot['incidents']:
        if inc['id'] in finding['incident_ids']:
            st.html(f'<article class="defense-incident"><b>{e(inc["id"])} · {e(inc["severity"])} temporal incident</b><p>{e(inc["explanation"])}</p><small>{len(inc["contributing_alerts"])} contributing alerts · {e(inc["detected_at"])}</small></article>')
    mappings = sparta_mapping(finding,raw)
    for mapping in mappings:
        st.markdown(f'**SPARTA [{mapping["technique_id"]} · {mapping["name"]}]({mapping["reference"]})**')
        st.write(mapping['qualification'])
    if not mappings:
        st.caption('SPARTA: unmapped. This evidence does not establish a supported technique. Unauthorized origin alone does not prove ground-station compromise.')
    with st.container(border=True):
        st.markdown('### 3 · Simulated defensive response')
        st.caption('Restrictions affect subsequent simulation admission for 300 simulated seconds or until restored. No real firewall or spacecraft command. Original detections and Trust Score stay unchanged.')
        choices = available_policies(finding,raw)
        reason = st.text_input('Operator reason',key=key+'_reason',max_chars=1000)
        if choices:
            labels = {POLICIES[p]+' / '+t:(p,t) for p,t in choices}
            choice = choose('Simulation policy / target',list(labels),key+'_policy')
            if st.button('Apply simulated restriction',key=key+'_apply',type='primary',disabled=not reason.strip()):
                try:
                    policy,target = labels[choice]
                    store.act(exercise,at,event_id=selected,policy=policy,target=target,reason=reason)
                except ValueError as error:
                    st.error(str(error))
        else:
            st.info('No supported source restriction for this finding. Investigate telemetry/model context; no arbitrary target is inferred.')
        actions = store.actions(exercise,at)
        active = active_policies(actions,at)
        if active:
            restrictions = {a['action_id']:a for a in active}
            reversal = choose('Restriction to restore',list(restrictions),key+'_restore_id')
            if st.button('Restore normal access',key=key+'_restore',disabled=not reason.strip()):
                try:
                    store.act(exercise,at,event_id=restrictions[reversal]['event_id'],reverses=reversal,reason=reason)
                    actions = store.actions(exercise,at)
                except ValueError as error:
                    st.error(str(error))
        if actions:
            latest = actions[-1]
            st.html(f'<div class="defense-response"><b>{e(latest["result"])}</b><p>Explicit resubmission test: <strong>{e(latest["probe_before"]["outcome"])} → {e(latest["probe_after"]["outcome"])}</strong></p><small>Reuses an observed payload at review +1 microsecond; not a newly observed command or detection.</small></div>')
            evaluated = outcomes(raw,actions,at)
            denied = sum(r['outcome']=='DENY' for r in evaluated)
            st.markdown(f'**Subsequent observed records evaluated: {len(evaluated)} · denied by simulation policy: {denied}**')
            st.caption('Advance the review clock to evaluate later recorded traffic/commands. These are counterfactual admission results, not altered historical data.')
            with st.expander('Response audit and subsequent evaluation',expanded=True):
                st.dataframe(pd.DataFrame(actions)[['action_id','timestamp','actor','operation','policy','target','reason','result','reverses']],hide_index=True,width='stretch')
                st.dataframe(pd.DataFrame(evaluated).tail(100),hide_index=True,width='stretch')
                st.download_button('Export response audit / JSON',json.dumps(actions,indent=2),'tekclipse-response-audit.json','application/json',key=key+'_audit')
        else:
            st.info('No response actions at this review. Automatic response is disabled.')
        if st.button('Start fresh response exercise',key=key+'_fresh'):
            st.session_state['defense_exercise'] = store.exercise(run_id)
            st.rerun()
    st.markdown('### 4 · Export investigation report')
    report_scope = choose('Report scope',['Selected finding']+finding['incident_ids'],key+'_report_scope')
    report = incident_report(store,run_id,exercise,at,event_id=selected,incident_id=None if report_scope=='Selected finding' else report_scope)
    a,b = st.columns(2)
    a.download_button('Download incident report / JSON',json.dumps(report,indent=2),'tekclipse-incident-report.json','application/json',key=key+'_report_json')
    b.download_button('Download incident report / HTML',report_html(report),'tekclipse-incident-report.html','text/html',key=key+'_report_html')
