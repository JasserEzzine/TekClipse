from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from tekclipse.pipeline import profiles
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.data.coordinated import ONSET


@pytest.mark.parametrize('profile', ['phase_a', 'phase_a2'])
def test_scientific_profiles_reset_switch_and_replay_without_refitting(profile):
    entry = Path(__file__).resolve().parents[1]/'streamlit_app.py'
    with patch.object(profiles, 'build_model', wraps=profiles.build_model) as training:
        app = AppTest.from_file(str(entry), default_timeout=240).run()
        assert not app.exception
        assert app.selectbox(key='detection_profile').value == 'original'
        app.selectbox(key='detection_profile').set_value(profile).run()
        assert not app.exception
        assert app.session_state['result']['profile'] == profile
        assert app.session_state['scenario'] == 'E1'
        calls = training.call_count
        assert len(app.tabs) == 8
        app.button(key='mission_E7').click().run()
        result = app.session_state['result']
        assert result['profile'] == profile
        assert app.session_state['overview_replay_second'] == 0
        for second in [20,45,86,100,120,160,180]:
            app.button(key='overview_next_stage').click().run()
            assert not app.exception
            assert app.session_state['overview_replay_second'] == second
            snapshot = trust_snapshot(result['security']['evidence'], ONSET+pd.Timedelta(seconds=second),
                                      correlation_policy=result['security']['correlation_policy'])
            assert next(m.value for m in app.metric if m.label == 'Trust score') == f"{snapshot['score']}/100"
        assert training.call_count == calls
        app.session_state['validated_evaluation'] = {'stale':'E7'}
        # Changing the profile clears both results and every scenario review state.
        app.selectbox(key='detection_profile').set_value('original').run()
        assert not app.exception
        assert app.session_state['scenario'] == 'E1'
        assert 'validated_evaluation' not in app.session_state
        assert 'overview_replay_second' not in app.session_state
        app.selectbox(key='detection_profile').set_value(profile).run()
        app.button(key='mission_E7').click().run()
        app.button(key='mission_reset').click().run()
        assert not app.exception
        assert app.session_state['result']['profile'] == profile
        assert app.session_state['result']['scenario'] == 'E1'
        assert 'overview_replay_second' not in app.session_state
        assert training.call_count == calls
        next(b for b in app.button if str(b.key).startswith('nav_SCENARIOS')).click().run()
        app.button(key='evaluate_selected').click().run()
        assert not app.exception
        evaluation = app.session_state['validated_evaluation']
        assert evaluation['available']
        assert evaluation['profile_metadata'] == app.session_state['result']['profile_metadata']
