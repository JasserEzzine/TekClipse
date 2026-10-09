# Phase D — run and operate

Use the `tekclipse-cloud` worktree, which contains the Phase D upgrade:

```powershell
cd C:\Users\msi\Bureau\TekClipse-cloud
python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8513
```

Open http://127.0.0.1:8513 locally. Dependencies remain in `requirements.txt`. The original default profile remains available; select **Phase A.2 hardened (experimental)** in the sidebar and use one day for the recommended demonstrations. See [demo.md](demo.md) for precise E2/E3/E7 steps.

The eight existing tabs remain. **Overview → Open cyber defense workspace** reveals the journal, investigation, response and report workflow. E7 uses its existing stage controls/slider. Other scenarios expose **Defense review / seconds after 12:00 UTC** as an exact integer input (0–180). This is a historical simulation review clock, not wall time.

## Evidence and response

Select a detector/source/severity/incident filter, then a real finding. Read the source records before choosing a restriction. A NET finding can contain innocent co-occurring flows: select the exact source you intend to investigate. Unknown source means unknown; no IP address is invented for command stations.

Enter an operator reason before **Apply simulated restriction**. Read the explicit payload resubmission test and advance review to see subsequent observed records evaluated under the policy. Original alerts and Trust are preserved. Use **Restore normal access** with a reason to append a reversal. Restrictions also expire after 300 simulated seconds, beyond most of the short demo window.

**Report scope** selects the current finding or its associated incident. JSON/HTML include provenance, deductions, mappings, actions, outcomes and uncertainties. **Export security log** exports the entire filtered set, even when the table shows only 200 rows. **Export response audit** saves the exercise's revealed actions.

## Persistence and recovery

- The journal is `results/security-evidence.sqlite`, separate from original operational and alert stores. Back up this file while the app is stopped for a consistent simple backup. It is ignored by Git.
- `TEKCLIPSE_EVIDENCE_DB` may specify a different local journal path for testing. Tests use temporary databases. Do not point it at an unrelated application's database.
- Journal data persists across reruns/restarts on durable local storage. Hosting with ephemeral disks cannot guarantee persistence; this phase does not provision hosting.
- **Reset demo**, a new scenario or a profile/duration change clears active response context but preserves old audit rows. **Start fresh response exercise** clears only the current response exercise. It does not delete evidence or historical audit.
- A rewind hides later evidence/actions and refuses a new mutation before the latest saved action. Advance to that action time, or start a fresh exercise to explore another branch.
- Exports should be saved before resetting for a jury handout. Prior exercise actions remain in SQLite but there is no cross-session audit browser or authenticated user management in this phase.
- Restart Streamlit after Python module edits. If a localhost port is occupied, choose another port. Do not terminate unrelated services or regenerate benchmark data to repair a presentation issue.

## Verify

```powershell
python -m pytest -q --junitxml=.audit/phase-d-recheck.xml
python scripts/check_phase_d_ui.py --url http://127.0.0.1:8513 --output .audit/phase-d-browser-recheck
python scripts/check_phase_c_ui.py --url http://127.0.0.1:8513 --output .audit/phase-d-preserved-replay
python scripts/check_mission_ui.py --url http://127.0.0.1:8513 --profile phase_a2 --output .audit/phase-d-eight-tabs
```

Browser checks use the existing optional Playwright developer installation and Edge. No new production dependency is needed. Read [report.md](report.md) and [verification.json](verification.json) for the measured results. The user authorized publishing the verified branch to GitHub; no separate hosting deployment is included.
