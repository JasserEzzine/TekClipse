# TekClipse — full hosted dashboard

Simulation-only satellite security operations dashboard. This branch is prepared for Streamlit Community Cloud; it includes the complete dashboard and existing E1–E6 experiment controls.

## Deploy

1. Sign in at https://share.streamlit.io with the GitHub account that owns this repository.
2. Create an app using:
   - Repository: `JasserEzzine/TekClipse`
   - Branch: `tekclipse-cloud`
   - Main file: `streamlit_app.py`
3. In Advanced settings, choose **Python 3.14** (the version used for validation).
4. No API keys or secrets are required. Click **Deploy**.
5. Wait for dependency installation and first-run simulation initialization. Share the resulting `https://…streamlit.app` address with your friend. If viewer access is restricted, change the app's sharing settings to allow the intended viewers.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Hosted behavior

- All eight dashboard tabs, charts, scenario controls and alert exports are retained.
- A seven-day seed-42 dataset is generated once at startup, rather than committing generated data to Git.
- The initial view and automatically computed nominal detector preview cover one day to reduce interactive memory use. Visitors can select one or seven days. Larger ranges remain available in the local dashboard.
- An actual nominal preview is computed on first startup. Scenario previews train on untouched nominal data and display detector output without claiming validated detection rates or attack confirmation.
- Cloud storage is disposable; restarting or redeploying may regenerate the simulation and preview.
- Hosted processes run independently of the developer's computer. Free hosting may sleep while idle and remains subject to the provider's resource limits.

## Local validation

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run streamlit_app.py
```

The original rules, Isolation Forest implementation, injectors and evaluator are unchanged. Network and event anomaly detectors are not implemented; those sources are visualized honestly. Synthetic data is not flight telemetry. Anomaly detection is not attack confirmation.
