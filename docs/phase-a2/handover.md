# Phase A.2 handover

Worktree: `C:\Users\msi\Bureau\TekClipse-cloud`, branch `tekclipse-cloud`. Safety baseline: `safety/phase-a2-baseline-e1f8b64`. The older dirty `TekClipse` main checkout and separate README worktree were left untouched. Changes are local; no push or deployment is part of this handover.

## Run the app

From the cloud worktree with the pinned dependencies installed:

```powershell
python -m streamlit run streamlit_app.py
```

Open the sidebar with the arrow at the upper left. Choose **Phase A.2 hardened (experimental)** under **Detection profile**, and use the one-day range for comparability with the scientific tests. The main view also names the active profile. Start E1, launch E7, advance each stage, and inspect the trust deductions. Reset restores E1 while keeping your chosen profile. Selecting another profile clears old replay and evaluation results.

Default **Original preview** preserves the established demo. **Phase A calibrated** exposes the previous scientific configuration. The hardened profile uses rolling R2, noise-representative nominal IF calibration, the explicit authorized-flow registry and conservative correlation. The published seed-301/302/303 E7 measurements do not describe the default preview or display seed 42.

## Reproduce

```powershell
# All original and new regression tests
python -m pytest -q -rA

# Existing CLI, default historical behavior
python scripts/run_experiment.py --scenario E7 --hours 24

# The same scientific profile used by the dashboard, on display seed 42
python scripts/run_experiment.py --scenario E7 --hours 24 --profile phase_a2
python scripts/run_experiment.py --scenario E7 --hours 24 --profile phase_a

# Validation only: rerun final candidate grid on seeds 503/504
# Writes docs/phase-a2/selection.json; use a clean checkout/copy to retain archives.
python scripts/select_phase_a2.py

# Freeze selected profiles, then evaluate all 69 cases in a NEW output directory
# Existing test artifacts are protected from overwrite.
python scripts/benchmark_phase_a2.py --output results/phase-a2-reproduction

# Derive pooled tables from the new result (does not alter the archived report)
python scripts/summarize_phase_a2.py --input results/phase-a2-reproduction/test.json --output results/phase-a2-reproduction/summary

# Original independent Phase A protocol remains available
python scripts/run_experiment.py --scientific --output results/phase-a-reproduction
```

`selection.json` records validation candidates, eligibility, thresholds and fingerprints. The benchmark checks that the configured feature mode/quantile and fitted threshold equal the selected candidate, writes `frozen.json` before generating tests, and checks every old regression dataset and Phase A hybrid result against the original archive. Detector/profile configuration is shared through `tekclipse/pipeline/detection_profiles.json` and `profiles.py`.

Runtime and source hashes can differ across environments or presentation-only edits; confusion/event/incident measurements and dataset fingerprints are the reproducibility targets. The archived two runs matched those measurements on all 69 cases. The second run adds a nominal-counterfactual check without changing the underlying labels or prior measurements. Model state is deterministically recreated from nominal seeds instead of loading an untrusted serialized model.

Optional browser verification uses the already installed Playwright developer tool and Edge; it is not a new runtime dependency:

```powershell
# In one terminal
python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8505

# In another terminal
python scripts/check_mission_ui.py --url http://127.0.0.1:8505 --profile original --output .audit/browser-original
python scripts/check_mission_ui.py --url http://127.0.0.1:8505 --profile phase_a --output .audit/browser-phase-a
python scripts/check_mission_ui.py --url http://127.0.0.1:8505 --profile phase_a2 --output .audit/browser-phase-a2
```

## Files changed

Modified implementation files:

- `tekclipse/pipeline/rules.py`: explicit rolling R2 with continuous-episode deduplication; legacy path preserved.
- `tekclipse/pipeline/explain.py`: rolling observation-time explanation while retaining legacy bin handling.
- `tekclipse/pipeline/network.py`: exact explicit flow authorization, optional validity dates; volume checks retained.
- `tekclipse/pipeline/correlation.py`: optional supported policy, deduplication/conflict checks and asset separation.
- `tekclipse/pipeline/trust.py`: correlation-policy argument; existing weights and formula preserved.
- `tekclipse/dashboard/data_service.py`: shared scientific bundles/evaluation, profile-aware caches and signature, safe original-only saved preview.
- `tekclipse/dashboard/app.py`: explicit profile selector/label, profile metadata and state invalidation.
- `tekclipse/dashboard/security_panel.py`: selected policy consistently applied to snapshots and histories.
- `scripts/run_experiment.py`: additive `--profile` option; old commands retained.
- `scripts/check_mission_ui.py`: actual browser verification for each selectable profile.
- `.gitignore`: permits the new scientific archive while generated runtime data remains ignored.
- `README.md`: Phase A.2 explanation, results and profile usage.

New implementation and tests:

- `tekclipse/pipeline/detection_profiles.json`: explicit Phase A and Phase A.2 configurations and registrations.
- `tekclipse/pipeline/profiles.py`: shared nominal-only fit and inference pipeline.
- `tekclipse/pipeline/research_features.py`: feature candidates and seeded nominal-noise augmentation; rejected candidates remain research evidence, not active defaults.
- `tekclipse/evaluation/profile_evaluation.py`: identical scientific evaluation for dashboard and CLI.
- `tekclipse/evaluation/phase_a2_data.py`: independent operational and benign variants, kept separate from E1–E7.
- `scripts/select_phase_a2.py`: validation-only model/quantile selection.
- `scripts/benchmark_phase_a2.py`: frozen 69-case comparison and paired ML counterfactuals.
- `scripts/summarize_phase_a2.py`: reproducible pooled tables.
- `tests/test_phase_a2.py`: boundaries, policy, authorization, causal features, shared configuration and inference tests.
- `tests/test_phase_a2_app.py`: profile switch/reset/evaluation/replay integration, including no refit on replay.
- `docs/phase-a2/`: baseline/protocol/selection evidence, rejected rounds, full reports, CSV/JSON measurements, verification and browser evidence.

All 13 historical test files and all 30 Phase A artifact files retain their baseline SHA-256 hashes. No original test assertion was weakened. No existing storage, scenario, tab, subsystem, impact or response feature was removed.

## Limits to explain

Do not claim that reduced false alarms prove broader attack detection. Standard E7 remains perfectly detected by the deterministic checks without ML. The hardened ML adds only 3/9 independent operational events, compared with 6/9 for Phase A, and misses moderate thermal drift. Training augmentation covers declared sensor-noise variability, not real spacecraft diversity. Trust is an explainable policy score; correlation and ML do not establish attribution or a probability of compromise.
