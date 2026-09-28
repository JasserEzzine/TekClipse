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
    }
    for scenario, rules in expected.items():
        next(
            button for button in app.button if button.key == "run_" + scenario
        ).click().run()
        assert not app.exception, [e.value for e in app.exception]
        result = app.session_state["result"]
        assert result["scenario"] == scenario
        assert set(result["alerts"].source) - {"ML"} == rules

    # Check populated alert visualizations and post-injection telemetry shading.
    for key in ["nav_ALERTS", "nav_TELEMETRY", "nav_OVERVIEW"]:
        next(button for button in app.button if button.key == key).click().run()
        assert not app.exception, [e.value for e in app.exception]
