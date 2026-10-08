# Incremental satellite security upgrade

> Historical report from the earlier security upgrade. Phase A adds independent-run evaluation, ablations and measured batch resource usage; see [the Phase A report](phase-a/report.md). The original benchmark below is retained for traceability.

This extends the existing Streamlit dashboard and five-column alert schema. No new runtime dependencies, services or device connections were added. The original eight tabs, charts, data generator, storage backends, R1–R3 and Isolation Forest remain. E1–E6 injection function bodies are unchanged; E4 now also produces network alerts.

## Added files

| File | Responsibility |
|---|---|
| `tekclipse/pipeline/network.py` | Nominal envelope, per-second totals/spikes and peer/protocol novelty |
| `tekclipse/pipeline/correlation.py` | Bounded temporal groups, independent source domains, incident evidence IDs |
| `tekclipse/pipeline/trust.py` | Capped, severity-weighted operational indicator and causal review snapshots |
| `tekclipse/data/coordinated.py` | Deterministic non-mutating E7 and explicit E1–E7 injected intervals |
| `tekclipse/pipeline/explain.py` | SYS checks, threshold/feature context, actual R2 observation time |
| `tekclipse/dashboard/security_charts.py` | Plotly attack episodes and trust progression |
| `tekclipse/pipeline/response.py` | Display-only operator guidance |
| `tekclipse/pipeline/subsystems.py` | Five evidence-derived subsystem flags |
| `tekclipse/evaluation/validated.py` | Explicit-label held-out rules/ML/hybrid comparison |
| `tekclipse/dashboard/security_panel.py` | Additive security briefing and guided replay |
| `tests/test_network_detection.py` | Nominal pass behavior, E4 coverage, novelty, empty baseline |
| `tests/test_correlation_trust.py` | Independent domains, bounded windows, capped deductions, causality |
| `tests/test_e7.py` | Determinism, no input mutation, command/thermal stages, short-data rejection |
| `tests/test_explanations.py` | R2 observation timing, thermal explanation, nominal event handling |
| `tests/test_security_views.py` | Chart serialization, response guidance and subsystem mapping |
| `tests/test_validated_evaluation.py` | Known confusion matrix, duplicate predictions, absent labels, latency and held-out E4 |
| `docs/security-upgrade.md` | This implementation/verification record |

## Modified files

- `config.yaml`: E7 enabled and configurable 180-second correlation window.
- `tekclipse/data/injection.py`: register E7; existing injectors untouched.
- `tekclipse/dashboard/data_service.py`: attach NET/SYS, explainable evidence and incidents to existing previews; cache separate held-out evaluation; include new detector/injector sources in preview freshness checks.
- `tekclipse/dashboard/app.py`: integrate briefing, replay, E7 button, source filter and optional held-out evaluation without removing pages/charts.
- `tekclipse/dashboard/charts.py`: show actual NET/SYS radar counts.
- `tekclipse/evaluation/runner.py`: keep legacy preview API, explicitly suppress invalid onset-only metrics. Existing keys remain with unavailable `NaN` values.
- `scripts/run_experiment.py`: E1–E7 CLI now runs the labeled held-out evaluation and saves JSON; supports `--hours`.
- `tests/test_dashboard_app.py`: exercise all eight tabs, seven scenario buttons, new detector integration, held-out button and guided replay progression.
- `README.md`: current architecture, formulas, evaluation definitions, limitations and timed demo instructions.
- `requirements.txt`: patch the existing urllib3 dependency to 2.8.0 after the final audit found three advisories in 2.7.0; no new dependency added.

## Verification

The pre-change suite passed (12 tests). Focused regression checks ran after each major component. The final integrated suite passed all 25 tests in 96.16 seconds, including actual Streamlit AppTest scenario, evaluation and replay interactions. Static Python security analysis and the tracked-content secret scan reported no findings. The patched pinned dependencies had no known advisories in the final audit and passed the compatibility check. A source comparison confirmed unchanged E1–E6 function bodies and no modifications to original rules/model/generator/storage. The nominal Overview was also checked in a headless browser.

The E7 replay test requires a nominal indicator of at least 95, a strictly falling score over its five major observed stages, and a final CRITICAL score. This is a deterministic demo policy check, not scientific validation of the score.

CLI smoke check: `python scripts/run_experiment.py --scenario E7 --hours 24`. Results are saved to ignored `results/E7-held-out.json`. On the tested seed-42 24-hour run, the hybrid detector labeled all 117 injected positive seconds and also flagged 3,068 nominal seconds; its precision was approximately 0.0367. Reporting those false positives is essential: a successful scripted demonstration is not evidence of accurate real-world cybersecurity detection. Re-run for measured outputs after any data/model change.

## Run and demonstrate

```powershell
cd C:\Users\msi\Bureau\TekClipse-cloud
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit. The older `TekClipse` working directory is preserved separately; these changes live in `TekClipse-cloud` on branch `tekclipse-cloud`.

Use Overview → **Judge demo / 2–3 minutes** → **Start nominal E1**, then **Launch E7 guided replay**. Advance through the stages, show the falling trust indicator and correlated incident, and finish with the evidence and **Recommended Operator Response**. Use Scenarios → **Run E7** for a completed review or **Evaluate selected scenario** for the separate benchmark.

## Limits

- Fixed nominal network envelope; legitimate new peers/protocols can produce false positives.
- Correlation is bounded time association, not entity-aware causal attribution. ML/R3 are one domain.
- No calibrated attack probability, autonomous response, flight model or real spacecraft integration.
- E7 includes observable synthetic events; detection on operational logs remains unvalidated.
- Trust/subsystem status is a historical trailing-window view. Evidence aging does not establish recovery.
- Evaluation labels are generated injection intervals. One-second any-source hits can be coincidental; E7 interval coverage does not establish coverage of every stage.
- Methods have different source coverage. No controlled ablation, real-data validation or monitoring-overhead measurement is claimed.
- Cold training takes time; use one-day mode and warm up before a timed presentation. Per-process detector serialization and existing caching remain in place.
