# Phase C — satellite security mission control

Phase C improves the existing Streamlit application rather than introducing a separate frontend. The mission overview, evidence investigation, subsystem guidance and progressive E7 review all consume the existing causal security snapshots. Detection, calibration, correlation, trust mathematics, scenario injections and storage are unchanged.

## Audit and implementation plan

The audit started on clean `tekclipse-cloud` commit `5dd1d1f`. The safety branch is `safety/phase-c-baseline-5dd1d1f`. The actual hosted entry point is `streamlit_app.py`; it prepares an actual nominal preview and executes `tekclipse/dashboard/app.py`. The local dashboard entry remains available. Both use the same data service. Phase A/A.2 reports, handovers, protocols and verification records were reviewed before editing.

The baseline full suite passed **65 tests, 0 failed, 0 skipped in 177.22 seconds**. An inventory records hashes of 107 existing tests, detector/data/evaluation/storage files, scientific artifacts, the data service, configuration and dependencies. The existing browser checker captured E1/E7 before images at 1920×1080 and 1366×768.

The existing application already had a useful satellite SVG, radial trust indicator, causal replay, impact/recommendation logic and eight analyst tabs. The identified presentation limitations were abbreviated subsystem names, limited per-stage investigation detail, buried evidence drill-down, a tall overview and a weak top-level distinction between current observations and historical scientific results.

The implementation order was: improve overview hierarchy; retain and clarify trust; add actual stage history and subsystem guidance; add investigation and scoped exports; then verify profiles, responsiveness and preservation. No approval or dependency was needed for this additive presentation work.

## Implemented experience

- A restrained navy mission-control theme, a precise title and question, and the visible **SIMULATED MISSION — RESEARCH DEMONSTRATOR** banner. The scenario, detection profile and stored seed are always named above the original eight tabs.
- Current review UTC, policy posture, active alert and incident counts, and the latest relevant evidence. Non-ML evidence is prioritized for the latest actionable observation; if absent, the latest statistical observation is shown. This is not an invented severity classifier.
- The existing trust gauge now exposes an accessible meter value, real deductions and checkpoint history. The score remains `100 − active policy deductions`, with its existing caps/floor. The indicator is explicitly not a compromise probability.
- The existing ground/link/satellite vector graphic remains. Ground-station command coloring and the command-security label use the existing Command channel state; the link uses Communications evidence. Missing network samples with no mapped anomaly produce a neutral UNKNOWN link rather than a nominal green connection. Scheduled RF contact remains distinct from the presence of network records. No physical outage or orbital position is invented.
- A compact strip and dedicated cards use the five exact subsystem names: Communications, Thermal, Power, On-board computer, Command channel. Cards expose alert IDs, actual associated incidents, supported potential impact and existing policy recommendations. No new response action or physical failure classification is introduced.
- An E7 investigation timeline shows only supplied, already-revealed snapshots. Each row contains the actual stage number, UTC, new detector families, new evidence count and actual trust score. The current review is highlighted with its score change, incidents and supported implication. A custom slider time stays within its existing stage; it does not create a new attack stage. Missing detections remain absent.
- An expandable analyst workspace distinguishes rule detections, network anomalies, Isolation Forest anomalies and subsystem events. Operators can inspect an alert's ID, observation time, severity, description, mapped subsystem, incident association, interpretation and existing recommended action. CSV export contains all currently matching observed records; the table deliberately limits its display to 100 records. Existing JSON and full-scenario exports remain available.
- A compact research section explains synthetic data, separate training/calibration/validation/test roles, remaining false positives, limited ML value, policy-based trust, lack of satellite integration and lack of flight qualification. Any historical numbers explicitly name profile, scenario, seeds and scope.

## Data provenance

| Presentation | Source and boundary |
|---|---|
| Active scenario/profile | Existing session state and `PROFILE_LABELS`; original preview remains default |
| Review time, posture, trust, deductions | Existing `trust_snapshot`, using the selected profile's correlation policy |
| Alert/incident counts | Current snapshot's active alerts and incidents, trailing 180 seconds |
| Latest relevant evidence | Latest observed non-ML alert, falling back to latest ML; actual source/time/description |
| Gauge/history and stage score changes | Existing review snapshots; no new scoring implementation |
| Satellite subsystem colors | Existing `subsystem_statuses`; absence of recent network data separately yields a neutral link |
| Telemetry samples / data availability | Existing exact review samples at or before the review time, with a two-second freshness limit |
| Scheduled contact | Existing contact-acquired/contact-closed system events at or before review time |
| Subsystem guidance | Existing `mission_impacts` and `recommended_responses`, intersected with mapped evidence IDs |
| Analyst records / CSV | Current snapshot only, filtered by actual detector family; no future-stage records |
| Historical research notes | Preserved Phase A.2 report, explicitly labeled as independent frozen experiments |
| Original orbit | Existing illustrative Plotly orbit; still labeled as nonphysical geometry |

Subsystem NORMAL means no mapped active evidence, not certified health. Mission consequences remain possible effects rather than predicted failures. Correlated groups remain temporal associations, not proven common cause or attacker attribution. The existing full-scenario Telemetry/Network/Events/Alerts tabs remain retrospective data-analysis views; the mission briefing, new investigation and replay timeline are time-limited. Those two scopes should not be confused during a demonstration.

## Preserved implementation and performance

All eight tabs remain: Overview, Telemetry, Commands, Network, Events, Alerts, Scenarios E1–E7, About. All E1–E7 injectors, rules R1–R3, Isolation Forest, network detection, correlation, all three profiles, trust formula, mission impact, recommendations, existing exports, CSV/SQLite/optional Parquet storage and scientific CLIs remain present. Profile changes clear the additional investigator selection keys along with the existing replay/evaluation state. Reset retains the chosen profile and restores E1.

The presentation uses the already-computed review history rather than invoking detectors for the timeline. It adds no ML fitting, data generation, network service, dependency or scientific evaluation to replay clicks. The investigator derives descriptions from existing alert records. Existing regression tests check that replay does not refit models and that dashboard/CLI scientific configurations agree. Whole-run browser timings are recorded, not presented as detector latency or a controlled speed comparison.

The new CSS lives in `operations.css`, loaded after the existing theme. New widgets use scoped classes, while a few deliberate app-level rules tighten spacing and typography. Reduced-motion behavior remains supported. The diagram is repo-native SVG with escaped labels, without scripts or external image services.

## Verification and actual captures

The final suite passed **72 tests, 0 failed, 0 skipped in 204.36 seconds** (204.328 seconds in the JUnit record). All 107 protected baseline files retain their original hashes. Real-browser checks passed for all eight tabs, all three profiles, seven E7 advances and reset. The filtered CSV contained 63 rule records, with no future evidence. Layout checks found no horizontal overflow at **1920×1080, 1366×768, 768×1024 and 390×844**.

Final security checks reported **0 Bandit findings and 0 scan errors** across `tekclipse`, `scripts` and `streamlit_app.py`, and **0 detect-secrets findings** across current Git-tracked files including staged additions. The credential check was not a repository-history scan. No runtime dependencies were added. These checks do not establish that every possible vulnerability is absent.

Exact final counts, unchanged-file checks, browser sizes, stage trust values, export checks and security scans are in [verification.json](verification.json). The full test run initially caught a legacy control-order regression from a new selectbox; the family filter was changed to radio buttons and the original test was retained unchanged. Browser tooling also needed consistent assertion timeouts and a fresh server after module edits; no detector or scientific result was changed to address those checks.

Before and after images are actual browser captures, not generated mockups:

- [Before E7, 1366×768](screenshots/before-e7-1366.png)
- [After E7, 1366×768](screenshots/after-e7-1366.png)
- [After E7, 1920×1080](screenshots/after-e7-1920.png)
- [E7 investigation timeline](screenshots/investigation.png)
- [Five-subsystem panel](screenshots/subsystems.png)
- [Analyst evidence](screenshots/analyst.png)
- [Tablet, 768×1024](screenshots/tablet-768.png)
- [Phone, 390×844](screenshots/mobile-390.png)

The main overview is designed for desktop/laptop presentation; tablet and phone layouts stack panels and require vertical scrolling. Long evidence descriptions and tables remain in expandable investigation views. No comprehensive assistive-technology audit or real spacecraft validation is claimed. The known scientific limitations and false alarms of Phase A.2 are unchanged.

## Files

Modified: `tekclipse/dashboard/app.py`, `mission_visuals.py`, `security_panel.py`, and `README.md`.

Added: `tekclipse/dashboard/investigation.py`, `operations.css`, `tests/test_phase_c.py`, `scripts/check_phase_c_ui.py`, and this `docs/phase-c/` package. Existing tests and scientific artifacts are retained unchanged. No push or deployment is automatic.
