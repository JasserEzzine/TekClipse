from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_cloud_app_tabs_and_all_scenario_buttons():
    entry = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(str(entry), default_timeout=240).run()
    assert not app.exception, [e.value for e in app.exception]
    assert len(app.tabs) == 8
    assert app.selectbox[0].value == 1
    assert app.session_state["result"] is not None
    for key in [
        "nav_TELEMETRY",
        "nav_COMMANDS",
        "nav_NETWORK",
        "nav_EVENTS",
        "nav_ALERTS",
        "nav_ABOUT",
    ]:
        next(button for button in app.button if button.key == key).click().run()
        assert not app.exception, [e.value for e in app.exception]

    next(
        button for button in app.button if str(button.key).startswith("nav_SCENARIOS")
    ).click().run()
    expected = {
        "E1": set(),
        "E2": {"R1"},
        "E3": {"R2"},
        "E4": set(),
        "E5": {"R3"},
        "E6": {"R1", "R3"},
        "E7": {"R1", "R2", "R3"},
    }
    for scenario, rules in expected.items():
        next(
            button for button in app.button if button.key == "run_" + scenario
        ).click().run()
        assert not app.exception, [e.value for e in app.exception]
        result = app.session_state["result"]
        assert result["scenario"] == scenario
        assert set(result["alerts"].source) & {"R1", "R2", "R3"} == rules
        if scenario in {"E4", "E6", "E7"}:
            assert "NET" in set(result["alerts"].source)
        if scenario == "E7":
            assert "SYS" in set(result["alerts"].source)
            assert any(
                i["severity"] == "CRITICAL" for i in result["security"]["incidents"]
            )

    next(
        button for button in app.button if button.key == "evaluate_selected"
    ).click().run()
    assert not app.exception, [e.value for e in app.exception]
    assert app.session_state["validated_evaluation"]["available"]

    # Check populated alert visualizations and post-injection telemetry shading.
    for key in ["nav_ALERTS", "nav_TELEMETRY", "nav_OVERVIEW"]:
        next(button for button in app.button if button.key == key).click().run()
        assert not app.exception, [e.value for e in app.exception]

    next(button for button in app.button if button.key == "demo_E1").click().run()
    assert app.session_state["result"]["scenario"] == "E1"
    next(button for button in app.button if button.key == "demo_E7").click().run()
    assert app.session_state["overview_replay_second"] == 0
    scores = [
        int(next(m.value for m in app.metric if m.label == "Trust score").split("/")[0])
    ]
    for _ in range(5):
        next(
            button for button in app.button if button.key == "overview_next_stage"
        ).click().run()
        assert not app.exception, [e.value for e in app.exception]
        scores.append(
            int(
                next(m.value for m in app.metric if m.label == "Trust score").split(
                    "/"
                )[0]
            )
        )
    assert scores[0] >= 95
    assert all(a > b for a, b in zip(scores, scores[1:])), scores
    assert scores[-1] < 50
