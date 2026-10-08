# Phase A.2 baseline audit

Work started from clean `tekclipse-cloud` commit `e1f8b64`. A local safety branch, `safety/phase-a2-baseline-e1f8b64`, preserves that state. The unrelated main and README worktrees were not edited. Nothing is pushed automatically.

Before changing algorithms, all **43 tests passed, 0 failed, 0 skipped** (64.91 seconds). The archived 48-case Phase A semantic digest was verified. E7 seeds 301, 302 and 303 were rerun using the Phase A pipeline; all comparisons, trust/security snapshots and data fingerprints matched the archive. `baseline.json` contains this evidence and SHA-256 inventories of all 13 historical test files and all 30 Phase A artifact files.

Verified weaknesses:

- Fixed-minute R2 misses twelve commands spanning 09:00:54–09:01:05. Authorization does not resolve this rate-policy question.
- Phase A E7 has 7,254 false-positive seconds across three days, all from ML. The no-ML hybrid has TP 351 / FP 0 / FN 0 on these known injections.
- Training on one narrow nominal sensor-noise distribution makes rolling standard deviations sensitive to the declared benign noise variant. This produces 24,159 false-positive seconds across the three Phase A robustness runs.
- A new legitimate peer creates 90 network novelty alarms per run because no authorization registry was available to the detector.
- Legacy correlation allows a background ML deviation to establish a second domain, even without two independently actionable sources; duplicate IDs can also appear in incident evidence.
- Scientific calibration was unavailable as an explicit dashboard profile, creating a configuration gap for jury demonstrations.

The original Phase A test intentionally asserts the old fixed-minute behavior. To keep that test and historical reproduction intact, the corrected R2 path is explicit: `r2_mode="rolling"`, selected by the Phase A.2 profile. The default legacy API and original preview remain fixed-minute. This is a disclosed compatibility mode, not a claim that every existing entry point now uses rolling R2.
