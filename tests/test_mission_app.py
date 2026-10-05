from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tekclipse.dashboard import data_service
from tekclipse.dashboard.mission_state import mission_briefing
from tekclipse.data.coordinated import ONSET
from tekclipse.pipeline.trust import trust_snapshot
import pandas as pd


def test_visible_demo_controls_preserve_algorithms_and_reset_all_review_state():
    entry = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    with patch.object(
        data_service, "build_model", wraps=data_service.build_model
    ) as training:
        app = AppTest.from_file(str(entry), default_timeout=240).run()
        app.button(key="mission_E7").click().run()
        assert not app.exception
        calls = training.call_count
        preview = app.session_state["result"]
        assert app.session_state["overview_replay_second"] == 0
        for expected in [20, 45, 86, 100, 120, 160, 180]:
            app.button(key="overview_next_stage").click().run()
            assert not app.exception
            assert app.session_state["overview_replay_second"] == expected
            snapshot = trust_snapshot(
                preview["security"]["evidence"],
                ONSET + pd.Timedelta(seconds=expected),
                preview["security"]["window_seconds"],
            )
            shown = next(m.value for m in app.metric if m.label == "Trust score")
            assert shown == f"{snapshot['score']}/100"
        assert training.call_count == calls  # No model training on replay clicks.
        end = mission_briefing(snapshot)
        assert end["impacts"] and end["recommendations"]
        app.session_state["validated_evaluation"] = {"scenario": "E7"}
        app.button(key="mission_reset").click().run()
        assert not app.exception
        assert app.session_state["result"]["scenario"] == "E1"
        assert "overview_replay_second" not in app.session_state
        assert "validated_evaluation" not in app.session_state
        nominal = trust_snapshot(
            app.session_state["result"]["security"]["evidence"],
            ONSET + pd.Timedelta(seconds=160),
        )
        assert not nominal["incidents"]
        assert not mission_briefing(nominal)["impacts"]
        assert nominal["score"] >= 95
        app.button(key="mission_E1").click().run()
        assert not app.exception and app.session_state["result"]["scenario"] == "E1"
