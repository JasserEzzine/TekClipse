from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tekclipse.pipeline import profiles
from tekclipse.security.store import EvidenceStore


def test_defense_workflow_enforcement_reversal_profile_reset_and_no_refit(tmp_path,monkeypatch):
    database=tmp_path/'journal.sqlite'
    monkeypatch.setenv('TEKCLIPSE_EVIDENCE_DB',str(database))
    with patch.object(profiles,'build_model',wraps=profiles.build_model) as training:
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'streamlit_app.py'),default_timeout=240).run()
        app.selectbox(key='detection_profile').set_value('phase_a2').run()
        calls=training.call_count
        next(b for b in app.button if str(b.key).startswith('nav_SCENARIOS')).click().run()
        app.button(key='run_E3').click().run()
        app.button(key='nav_OVERVIEW').click().run()
        app.toggle(key='defense_open').set_value(True).run()
        app.number_input(key='defense_review_second').set_value(20).run()
        assert not app.exception,[e.value for e in app.exception]
        app.selectbox(key='defense_overview_detector').set_value('R2').run()
        app.selectbox(key='defense_overview_policy').set_value('Quarantine command station / GS_PRIMARY').run()
        app.text_input(key='defense_overview_reason').set_value('Rehearse temporary command containment').run()
        app.button(key='defense_overview_apply').click().run()
        assert not app.exception,[e.value for e in app.exception]
        exercise=app.session_state['defense_exercise']
        store=EvidenceStore(database)
        assert store.actions(exercise,'2026-01-01T12:00:20Z')[-1]['probe_after']['outcome']=='DENY'
        app.number_input(key='defense_review_second').set_value(58).run()
        assert any('denied by simulation policy: 19' in item.value for item in app.markdown)
        app.button(key='defense_overview_restore').click().run()
        assert not app.exception
        assert store.actions(exercise,'2026-01-01T12:00:58Z')[-1]['probe_after']['outcome']=='ALLOW'
        app.button(key='mission_E7').click().run()
        assert not app.toggle(key='defense_open').value
        app.toggle(key='defense_open').set_value(True).run()
        app.button(key='overview_next_stage').click().run()
        assert not app.exception
        assert app.session_state['defense_exercise']!=exercise
        rows=store.findings(app.session_state['defense_run'],'2026-01-01T12:00:20Z')
        assert all(f['detector']!='NET' for f in rows)
        assert training.call_count==calls
        app.selectbox(key='detection_profile').set_value('original').run()
        assert not app.exception and app.session_state['scenario']=='E1'
        assert not app.toggle(key='defense_open').value
        assert len(app.tabs)==8
