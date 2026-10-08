# Phase A technical handover

## Explain the contribution plainly

TekClipse observes **synthetic** telemetry, commands, network activity and system events. Rules catch explicit policy/limit violations; Isolation Forest measures deviations from nominal telemetry; network checks detect volume changes and unfamiliar categories. Correlation links nearby evidence. Operational Trust summarizes that evidence using an explainable policy. None of these establishes a real attack, its cause, or spacecraft failure.

Phase A adds a reproducible scientific evaluation, fixes an authorization edge case, and tests a calibrated IF profile. It does not redesign the dashboard or replace the existing detection architecture.

## What changed and why

| File | Change | How to defend it |
|---|---|---|
| `.gitignore`, `README.md`, `docs/` | Retain the measured evidence archive, document reproduction and distinguish historical reports | Raw working outputs stay ignored; the reviewed Phase A results remain versioned and inspectable. |
| `data/generator.py` | Optional explicit seed; default 42 unchanged | Independent runs require distinct noise/command/event realizations. Manifest records the actual seed. |
| `pipeline/rules.py` | R1 honors explicit denial for GS_PRIMARY | Source name cannot override an explicit unauthorized flag. The added regression supplies that exact input. |
| `pipeline/rules.py` | R3 selects violating rows before formatting | Same strict thresholds, order and messages; avoids a measured loop through every nominal sample. |
| `evaluation/validated.py` | Enforces UTC-aware complete1 Hz timeline and consistent disjoint intervals | Prevents misleading denominators and double-counted intervals. Existing valid results stay identical. |
| `pipeline/calibration.py` | Optional full-day nominal fit and separate calibration | Training determines the model; independent nominal scores determine threshold values. Missing/nonfinite input is rejected. |
| `evaluation/study_data.py` | Role checks, fingerprints, event ledger and separate variants | Ground truth remains explicit and source-aware. Established scenarios are unchanged. |
| `evaluation/scientific_metrics.py` | Separate seconds, events, incidents and false-alarm episodes | A sample count is not a count of attacks. No negative incident universe is invented. |
| `evaluation/calibration_study.py` | Reproducible validation-only threshold grid | Selection sees validation labels but never test labels. Rejected alternatives remain documented. |
| `evaluation/scientific.py`, `study_report.py` | Frozen study, ablations, timing/RSS and exports | The same held-out data and denominators are used for all methods. Test reruns reject changed provenance. |
| `scripts/run_experiment.py` | Opt-in `--scientific` mode | Original CLI remains valid; the protocol controls the new mode. |
| `scripts/audit_phase_a_baseline.py` | Historical reproduction and component FP diagnosis | Shows where the old numbers came from rather than replacing them. |
| `scripts/benchmark_phase_a.py` | Repeated complete-batch wall-clock timings | Separates simulated delay from processing through alerts and explanation/correlation. |
| `scripts/check_mission_ui.py` | Await reset state; normalize whitespace in score comparison | `100\n/100` and `100/100` are the same displayed score. All original assertions remain. |
| `tests/test_phase_a.py` | Additional correctness/regression tests | Tests cover invalid metrics, seeds, leakage, boundaries, authorization, storage and selection. Original tests are untouched. |

## Important answers for the jury

**Why were the original false positives so high?** The historical E7 hybrid has 3,068 FP seconds; 3,067 also occur in nominal E1. Its95th-percentile training threshold flags the nominal tail. These are predominantly IF calibration errors, not duplicate alert rows. The calibrated experiment trades sensitivity for fewer nominal alarms; it is not a proof that IF is better than rules.

**Why not simply use a very high threshold?** The first `.999` candidate reduced nominal validation FP to 94 but lost the ML detections of thermal injections. We recorded and rejected it. A validation grid selected `.975` to preserve each previously detected ML event. That still changes positive-second recall and delay; the tables disclose both. Never quote only the reduced FP count.

**Does event recall mean every attacked second was flagged?** No. R2 emits once when the count exceeds 10 in a fixed minute. E3 therefore can be detected as an event while having only 1/59 sample recall. NET/telemetry detectors may emit every anomalous second. Both units are useful and must remain separate.

**Is the final test independent?** Its seeds are distinct from training, calibration and validation. However, all data comes from one synthetic model with shared pass patterns. This supports limited simulation repeatability, not broad real-world generalization.

**Does the new calibration replace the dashboard model?** No. It is an explicit scientific CLI profile. The established UI keeps its original preview threshold and training behavior. The R1 correctness fix and R3 efficiency change apply to the shared rule implementation. Do not describe new scientific metrics as current dashboard-preview metrics.

**Is Trust a compromise probability?** No. It deducts capped family weights and a capped correlation weight over a trailing window. Repeated samples do not amplify a family penalty. Telemetry rule/ML evidence and correlation can all contribute by policy; these are not independent probabilities. The mathematics is unchanged.

**What still fails?** A burst crossing a minute boundary can evade fixed-bin R2. A benign authorized burst can trigger it. NET has no authority registry, so a legitimate new peer can alarm. Higher benign telemetry noise changes the distribution and raises IF false alarms. Source-matched coverage is narrower than an any-source temporal hit. Correlation can associate unrelated nearby evidence. Read the held-out tables and final report before making any quantitative claim.

## Review and reproduce as a team

1. Read [baseline](baseline.md), [protocol](protocol.md) and [results](report.md), including negative results.
2. Run the exact reproduction command in the protocol with the pinned requirements. Inspect `test/comparison.csv`, `test/ablation.csv`, `test/incidents.csv` and the source-level event ledger in `test.json`.
3. Recalculate one row by hand: precision=TP/(TP+FP), recall=TP/(TP+FN). Check that TP+FP+TN+FN equals the evaluated seconds.
4. Inspect a flood's eleventh command and explain why simulated detection delay differs from wall-clock processing time.
5. Read R1/R2/R3 and the small metric/calibration helpers; practice explaining the threshold trade-off without claiming calibrated probabilities.
6. Run E1→E7→each stage→reset. Compare the displayed trust deductions with `trust_snapshot`, remembering that preview and scientific profiles are separate.

AI assistance was used to inspect code, implement the controlled changes, design experiments, execute checks and draft documentation. The team must independently review, rerun and understand the code/results before submission. This document is a technical handover, not a final presentation or a substitute for team ownership. No original paper content or research targets have been invented.

No changes are automatically pushed in Phase A. The local safety branch preserves the baseline; the final change remains reviewable before any publication.
