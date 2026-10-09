# Phase C — jury demonstration handover

## Launch

Use the cloud worktree, not the older main checkout:

```powershell
cd C:\Users\msi\Bureau\TekClipse-cloud
python -m streamlit run streamlit_app.py
```

The pinned environment is in `requirements.txt` if setting up a new machine. The first startup may prepare stored simulation data and an actual detector preview. Allow that to finish before presenting. No API keys or real satellite credentials are needed.

For a separate local rehearsal port:

```powershell
python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8507
```

The sidebar arrow at the top left opens simulation range and detection profile controls. Use **one day** and **Phase A.2 hardened (experimental)** for the recommended scientific demonstration. The application still defaults to Original preview. All three profiles remain selectable; the chosen profile is visible above the tabs. Changing it resets the scenario and investigation to E1 rather than mixing results from different models.

## Recommended sequence

1. **Start nominal E1.** Point to SAT-01, the four monitored streams and the simulation banner. Explain that NORMAL means no sufficiently penalized current evidence under the implemented policy; it is not a safety certification.
2. **Explain the overview.** Read the simulated review UTC, active alert count, incident count and latest relevant evidence. Distinguish data availability from the scheduled RF pass. The spacecraft diagram is illustrative, not a measured location or a physical communications model.
3. **Launch E7 attack.** This starts at +000 seconds. Use **Next attack stage** seven times: +020, +045, +086, +100, +120, +160 and +180 seconds. You can also use the existing slider for a custom review time.
4. **Follow the real evidence.** Watch commands, network anomalies, telemetry limits and subsystem events appear when observed. Scroll to **Follow the evidence** for stage UTC, actual detector sources, new records, score and current incidents. The highlighted row is the current review. No future-stage event is revealed there.
5. **Explain trust.** Start at 100 and show the listed active deductions. Families are capped; severity weights and an existing correlation deduction determine the score. This is a policy-based indicator, not a probability of compromise. For seed 42 under Phase A.2, the prior verified demonstration shows 11 at +120 and 9 at +160; read the actual value rather than promising a particular dramatic drop.
6. **Show all five subsystems.** Communications, Thermal, Power, On-board computer and Command channel use existing evidence mappings. Open a card's evidence/guidance detail. Point out that an unaffected Power card stays nominal and that possible mission impact is not proven equipment failure.
7. **Investigate an alert.** Expand **Security analyst / investigate observed evidence**, choose an evidence family and an alert. Explain its source, timestamp, supporting description, subsystem and incident association. Export the observed CSV if useful. The existing analyst briefing retains the full trust snapshot JSON export and complete recommendations.
8. **Discuss limitations.** Open **Research validation / what this console can and cannot establish**. Isolation Forest finds statistical deviations, including false alarms. Deterministic checks already cover known E7 events; the hardened ML added only 3/9 independent operational deviations in the separate scientific experiment. Correlation does not prove common cause or identify an attacker.
9. **Reset demo.** Confirm E1 returns, the replay timeline disappears and stale attack effects/recommendations are gone. The selected profile remains active. No real spacecraft command is executed by any control or recommendation.

The first screen answers the mission question using current policy evidence. The deeper analyst tabs remain available for full stored-scenario analysis, which is a different scope from the time-limited replay. Never describe archived benchmark precision/recall as live measurements of the displayed seed-42 run.

## Recover from a demo issue

- Use **Reset demo** for unwanted replay/investigation state.
- Check the profile and one-day range if results differ from the intended rehearsal. Profile changes intentionally restore E1.
- If startup is still fitting/loading, wait for the status indicator. Avoid repeatedly clicking scenario buttons while a run is in progress.
- After editing Python presentation modules, restart the Streamlit server before collecting final screenshots; a server can retain imported modules between reruns. A browser refresh alone is not a reliable source reload.
- If the port is occupied, launch on a different localhost port using the command above. Do not kill unrelated Python processes.
- Generated data stays in its existing ignored data directory. Do not delete storage or change detector thresholds to make the screen look nominal.
- If a statistical alert is absent at a stage, show the actual detector result and explain its limits. Do not replace it with a scripted alert or score.

## Verify

```powershell
python -m pytest -q -rA
python scripts/check_mission_ui.py --url http://127.0.0.1:8507 --profile original --output .audit/phase-c-original
python scripts/check_mission_ui.py --url http://127.0.0.1:8507 --profile phase_a --output .audit/phase-c-phase-a
python scripts/check_mission_ui.py --url http://127.0.0.1:8507 --profile phase_a2 --output .audit/phase-c-hardened
python scripts/check_phase_c_ui.py --url http://127.0.0.1:8507 --output .audit/phase-c-investigation
```

Browser checks require the existing optional Playwright developer installation and Edge. They are not new runtime dependencies. Read [report.md](report.md) and [verification.json](verification.json) for actual measurements, screenshots and remaining limitations. No automatic GitHub push or hosting deployment is included.
