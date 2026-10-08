# Phase A final technical report — 8 October 2026

Phase A preserves the working prototype and adds an auditable independent-run evaluation. The selected experimental hybrid reduces held-out E7 false-positive seconds by **48.70%**, while preserving all 351 positive seconds and all 18 source-matched events across three seeds. Precision remains low. Ablation shows that removing IF performs better on these established synthetic injections; this phase does **not** establish that ML improves the hybrid system.

Changes are local, with no automatic push. The calibrated profile is opt-in through the scientific CLI. The existing dashboard IF configuration and all Trust mathematics remain unchanged. See the [protocol](protocol.md), [team handover](handover.md) and [baseline audit](baseline.md).

## A. Baseline

Baseline commit `2b25015378564206a84d50ace8e3d0e906c46d7e`; safety branch `safety/phase-a-baseline-2026-10-08-2b25015`. Original suite: **30 passed, 0 failed, 0 skipped in 78.16 s**. The older dirty main checkout was left untouched.

The original 24 h seed 42, first 6 h train / last 18 h test protocol reproduced E7 TP 117, FP 3,068, TN 61,615, FN 0; precision 0.0367347, recall 1, F1 0.0708661, FPR 0.0474313. All 3,068 FP seconds also occur in the ML-only output; 3,067 are identical to nominal E1 and one is an injection aftereffect. Duplicate alert rows are not counted twice. Original R1–R3 had TP 63, FP 0, FN 54. Detailed per-scenario counts and source hashes: [baseline.json](baseline.json).

## B. Verified weaknesses

1. **High scientific priority:** nominal-tail ML alarms dominate FP. A 95th-percentile training threshold is not a compromise probability or calibrated deployment alarm budget. Six nominal training hours do not establish generalization across independent sessions.
2. **High correctness priority:** R1 ignored an explicit unauthorized flag on GS_PRIMARY. It is now honored and tested. Missing authorization still preserves the legacy default; this is not a complete authorization system.
3. **High evaluation priority:** sample, event and incident units were not separately measured; any-source temporal hits could receive credit for unrelated injected activity. The new metrics retain the old union labels and separately require source-matched event evidence.
4. **Remaining coverage limitations:** fixed-minute R2 misses a boundary-straddling flood; NET flags a new authorized peer because it has no authority registry; benign telemetry distribution changes elevate IF false alarms. Correlation can group unrelated nearby evidence. These are measured limitations, not reclassified labels.
5. **Measured efficiency issue:** baseline R3 spent about 1.59–1.64s iterating all 64,800 telemetry rows. It now formats only violations, with identical threshold/output behavior. The inactive legacy preprocessing helper can drop simultaneous rows; the active dashboard/research paths bypass it and preserve command/network rows.

## C. Implemented changes

New modules cover independent-run data/labels, strict scientific metrics, nominal calibration, validation-only selection, frozen experiments and report exports. The CLI remains backward compatible. Shared production changes are limited to seed configurability (default 42 preserved), valid-metric input checks, explicit R1 denial handling and output-equivalent R3 filtering. No dependency was added. The complete file-by-file rationale is in the [handover](handover.md).

The initial `.999` calibration lost the original ML event detections and was rejected for promotion. A recorded validation grid selected `.975`, preserving each original ML-detected event on validation while reducing false positives. Positive-second recall and delay still change. No choices were retuned after final test seeds were used. See [selection history](protocol.md#selection-history-and-frozen-decision).

## D. Held-out before/after comparison

Train seed 101; nominal calibration 202; validation 203; frozen test 301/302/303. Each test session is 24 h. These are independent runs and **not the historical 18 h temporal holdout**, so compare methods within this table. E7 totals cover 259,200 seconds, 351 positive and 258,849 negative. Ratios are 0–1, not percentages.

| Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | False episodes/h | Mean event delay s |
|---|---|---|---|---|---|---|---|---|---|---|
| Rules only | 189 | 0 | 258849 | 162 | 1 | 0.538462 | 0.7 | 0 | 0 | 3.33333 |
| ML original | 138 | 14141 | 244708 | 213 | 0.00966454 | 0.393162 | 0.0188653 | 0.0546303 | 27.8611 | 6.66667 |
| ML calibrated | 160 | 7254 | 251595 | 191 | 0.0215808 | 0.45584 | 0.0412106 | 0.0280241 | 18.2361 | 5.33333 |
| Network only | 348 | 0 | 258849 | 3 | 1 | 0.991453 | 0.995708 | 0 | 0 | 0 |
| Original hybrid | 351 | 14141 | 244708 | 0 | 0.0242203 | 1 | 0.047295 | 0.0546303 | 27.8611 | 1.66667 |
| Full-day uncalibrated hybrid | 351 | 12853 | 245996 | 0 | 0.0265829 | 1 | 0.051789 | 0.0496544 | 23.6806 | 1.66667 |
| Improved hybrid | 351 | 7254 | 251595 | 0 | 0.0461538 | 1 | 0.0882353 | 0.0280241 | 18.2361 | 1.66667 |

FP seconds per simulated hour: original **196.403**, selected **100.75**. False-alarm episodes are contiguous FP seconds and are reported separately; aggregation never erases raw FP seconds. The sample detection recall is 100% for E7. Source-matched event recall is 18/18 with mean delay 1.66667 s (R2 needs 10 s; other E7 events are observed at onset). Missed events have undefined delay, never zero.

Standalone ML trade-offs (event totals include all source events, so only compatible thermal events are in ML scope):

| Case | Method | TP seconds | FP seconds | Detected/all events | Mean matched delay s |
|---|---|---|---|---|---|
| E5 | ML original | 64 | 14123 | 3/3 | 14 |
| E5 | ML calibrated | 12 | 7249 | 3/3 | 19.3333 |
| E6 | ML original | 64 | 14123 | 3/9 | 14 |
| E6 | ML calibrated | 12 | 7249 | 3/9 | 19.3333 |
| E7 | ML original | 138 | 14141 | 3/18 | 6.66667 |
| E7 | ML calibrated | 160 | 7254 | 3/18 | 5.33333 |

Use the [per-run CSV](results/test/per-run.csv) and [aggregate tables](results/test/tables.md) to see individual seeds and every method. No ML-superiority claim is supported.

## E. Ablation and correlation

| Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | False episodes/h | Mean event delay s |
|---|---|---|---|---|---|---|---|---|---|---|
| Improved hybrid | 351 | 7254 | 251595 | 0 | 0.0461538 | 1 | 0.0882353 | 0.0280241 | 18.2361 | 1.66667 |
| Without ML | 351 | 0 | 258849 | 0 | 1 | 1 | 1 | 0 | 0 | 1.66667 |
| Without network | 189 | 7254 | 251595 | 162 | 0.025393 | 0.538462 | 0.0484988 | 0.0280241 | 18.2361 | 2 |
| Without rules | 348 | 7254 | 251595 | 3 | 0.0457774 | 0.991453 | 0.0875141 | 0.0280241 | 18.2361 | 1.33333 |

Without ML, the standard E7 labels are still fully covered and FP seconds disappear. Rules supply command/hard-limit detections, NET supplies the network interval, and SYS supplies explicit subsystem events. These injections favor deterministic coverage; they do not prove that rules detect unknown real attacks. The remaining IF complexity is justified as a research comparison/telemetry novelty indicator, **not by demonstrated incremental attack coverage in this dataset**. No existing detector was removed.

Correlation is evaluated separately; a matched group needs labeled evidence from at least two domains. There is no invented incident TN or FPR:

| Case | Method | Reference incidents | Detected references | Emitted groups | Unmatched groups | Extra matched fragments |
|---|---|---|---|---|---|---|
| E1 | Original hybrid | 0 | 0 | 0 | 0 | 0 |
| E1 | Improved hybrid | 0 | 0 | 0 | 0 | 0 |
| E6 | Original hybrid | 3 | 3 | 3 | 0 | 0 |
| E6 | Improved hybrid | 3 | 3 | 3 | 0 | 0 |
| E7 | Original hybrid | 3 | 3 | 3 | 0 | 0 |
| E7 | Improved hybrid | 3 | 3 | 3 | 0 | 0 |
| benign_command_burst | Original hybrid | 0 | 0 | 0 | 0 | 0 |
| benign_command_burst | Improved hybrid | 0 | 0 | 0 | 0 | 0 |
| benign_authorized_peer | Original hybrid | 0 | 0 | 0 | 0 | 0 |
| benign_authorized_peer | Improved hybrid | 0 | 0 | 0 | 0 | 0 |
| attack_reordered | Original hybrid | 3 | 3 | 3 | 0 | 0 |
| attack_reordered | Improved hybrid | 3 | 3 | 3 | 0 | 0 |

Source-supported association delay is reported in `results/test/incidents.csv`: E7 reaches supported two-domain association after 25 s on every seed/profile (network at +45 s minus first command at +20 s). Temporal association is not cause or attribution. A preceding false ML alert cannot make the supported-association delay negative. A matched incident may still contain unrelated evidence; the metric requires two supported domains, not that every contributing alert is correct.

## F. Robustness

All figures below pool each named variant over the same three seeds (72 h exposure per case). The standard injectors were not changed. Variants independently change timing, duration, intensity or ordering; benign variations have no attack labels.

| Variant | TP | FP | FN | Precision | Second recall | Event recall | False episodes/h |
|---|---|---|---|---|---|---|---|
| benign_command_burst | 0 | 7252 | 0 | 0 | undefined | undefined | 18.2222 |
| benign_authorized_peer | 0 | 7519 | 0 | 0 | undefined | undefined | 18.2222 |
| benign_load | 0 | 7249 | 0 | 0 | undefined | undefined | 18.1806 |
| benign_telemetry | 0 | 24159 | 0 | 0 | undefined | undefined | 17.6944 |
| attack_primary_unauthorized | 3 | 7249 | 0 | 0.000413679 | 1 | 1 | 18.1806 |
| attack_boundary_flood | 0 | 7249 | 36 | 0 | 0 | 0 | 18.1806 |
| attack_low_network | 3 | 7249 | 267 | 0.000413679 | 0.0111111 | 1 | 18.1806 |
| attack_short_thermal | 45 | 7249 | 0 | 0.00616945 | 1 | 1 | 18.1806 |
| attack_reordered | 315 | 7249 | 0 | 0.0416446 | 1 | 1 | 18.1806 |

The explicit-denial fix detects the primary-source unauthorized command. The boundary flood remains missed. A lower-intensity known-peer network attack may trigger only at its initial rise rather than throughout its duration. Benign new peers/command bursts remain false alarms. Noise variation remains a substantial generalization weakness: false-positive seconds rise from 7,249 to 24,159, even though the episode rate falls slightly because alarms persist longer. Counting episodes alone would hide that deterioration. None was tuned away on the final test.

## G. Performance and resources

Final test execution took **625.61s** for 48 case-runs, including comparisons, explanations and reporting. Fit/calibration took **1.184s**. Sampled whole-process peak RSS was **306.95 MiB**, increment **142.98MiB** from the process starting measurement. Sampling every 20 ms can miss brief peaks. This is not incremental spacecraft-monitoring overhead.

Across test cases, median candidate IF scoring/alert formatting was **0.5542s per 24 h batch**; median correlation call was **0.0222s**. The separate three-repeat E7 benchmark measured median complete input→alerts time **0.7164s**, and input→explanation/correlation **4.6155s**. Original-profile comparison was **0.9858s** and **8.9021s**, respectively; both use the current output-equivalent R3 optimization. Fewer ML alerts reduce explanation work.

These are development-machine batch measurements under concurrent verification load, not streaming latency, real-time guarantees or a controlled speedup study. Simulation-clock event/association delay is a separate metric. UI replay uses cached detector results and does not retrain on stage changes. Environment: Python 3.14.4, Windows 11, 6 physical/12 logical CPUs, 31.7 GiB RAM. Full versions, measurements and RSS method: [runtime](results/runtime.json), [end-to-end benchmark](results/end-to-end-benchmark.json).

## H. Scenario and Trust validation

| Case | Original TP | Selected TP | Original FP | Selected FP | Selected events | Mean event delay s |
|---|---|---|---|---|---|---|
| E1 | 0 | 0 | 14128 | 7249 | 0/0 | undefined |
| E2 | 3 | 3 | 14128 | 7249 | 3/3 | 0 |
| E3 | 8 | 3 | 14123 | 7249 | 3/3 | 18 |
| E4 | 360 | 360 | 14123 | 7249 | 3/3 | 0 |
| E5 | 543 | 543 | 14123 | 7249 | 3/3 | 0 |
| E6 | 543 | 543 | 14123 | 7249 | 9/9 | 0 |
| E7 | 351 | 351 | 14141 | 7254 | 18/18 | 1.66667 |

E1 is known nominal, but detector false positives remain. E2–E7 all retain source-matched hybrid event coverage. E3's lower candidate TP count removes chance ML hits inside its command window; the real flood event remains detected. Actual E7 snapshots for both profiles, contributors and all five subsystems are stored per seed in `results/test.json`.

In test seeds 302/303, background ML evidence makes the original profile reach Trust 47 at +45 s; the selected profile is at 58. That early third-domain evidence also affects incident severity. This is a change in detector inputs, not a rewritten Trust equation or proof of actual compromise. The selected profile follows 100→80→58→46→23→9 across all three seeds.

The unchanged dashboard's real-browser replay showed 100→80→58→46→23→9→9→9 at 0/20/45/86/100/120/160/180s; reset restored E1 with no stale chain, impact or recommendation. Trust family caps, severity weights and correlation penalty are unchanged. **Operational Trust is an explainable prototype indicator, not a probability of compromise.**

## I. Regression and verification

Final complete suite: **43 passed, 0 failed, 0 skipped in 81.32 s**. All 30 original tests remain byte-for-byte unchanged; 13 new tests cover metric validity, source-matched events, independent seeds, causal rolling windows, calibration isolation, rule boundaries, benign novelty, incident semantics, Trust consistency, CSV/SQLite/Parquet storage and selection safeguards. All eight tabs, E1–E7, replay/reset, recommendations, diagrams and existing CLI passed.

Real Edge checks passed at 1920×1080 and 1366×768; actual E1/E7 screenshots were inspected. No page exceptions or horizontal overflow were found. The initial browser-check reset failure was whitespace/timing in the checker; it now waits for the requested score and normalizes whitespace without dropping any assertion. See [browser verification](browser-verification.json).

Dependency compatibility passed; dependency audit reported no known advisories; static analysis and source/document secret scans reported no remaining findings. Algorithm-qualified public hash strings distinguish provenance from credentials. No new API, external service or runtime dependency was introduced. No real satellite integration or deployment was tested or claimed.

## J. Reproduction and KPI definitions

```powershell
cd C:\Users\msi\Bureau\TekClipse-cloud
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_experiment.py --scientific --output results/phase-a
python scripts/benchmark_phase_a.py --study results/phase-a --repeats 3
python -m streamlit run streamlit_app.py
```

Outputs include per-run comparisons, confusion matrices, ablation/incident tables, runtime, fingerprints and frozen validation. A second clean-output test execution uses the same frozen artifact; its semantic results digest excludes nondeterministic timing. Both complete 48-case executions produced identical semantic results and dataset fingerprints. Reproducibility verification is recorded in [reproducibility.json](results/reproducibility.json). Archived provenance digests have explicit algorithm prefixes; raw CLI outputs keep machine-comparison values.

| KPI | Definition/method | Actual selected result | Dataset and limit |
|---|---|---|---|
| Sample recall | TP/(TP+FN) | 1 | E7 three-seed union labels; not source attribution |
| Precision | TP/(TP+FP) | 0.0461538 | E7; low despite calibration |
| F1 | 2TP/(2TP+FP+FN) | 0.0882353 | E7 at the frozen threshold |
| FPR | FP/(FP+TN) | 0.0280241 | E7 negative seconds |
| False alarms | Contiguous FP-second episodes / exposure hours | 18.1806/h | E1, 72 h; also 100.681 FP seconds/h |
| Event coverage | Source-matched injected events detected | 18/18 E7; established E2–E7 covered | Narrow synthetic scenarios; boundary variant missed |
| Detection delay | First matching observation minus event onset | 1.66667 s mean | E7 detected events only; not wall time |
| Processing | Whole 24 h input batch→alerts median | 0.7164s | Three E7 repeats; in-memory development machine |
| Memory | Sampled whole evaluation process RSS | 306.95 MiB peak | 20 ms sampling; includes evaluation |

Original paper targets were unavailable and are not invented. No KPI is described as meeting an unverified challenge target.

## K. Remaining limitations and risks

- Calibration reduces false alarms but does not make this a production detector. Standalone ML sensitivity and delay vary; synthetic independent seeds still share one generator and orbit/pass schedule. Model initialization remains fixed at seed 42; uncertainty over model seeds and other hyperparameters was not measured.
- Standard injections are few and favor rules. The without-ML result is negative evidence against claiming hybrid superiority. General attack coverage, attribution and real mission safety are unvalidated.
- Fixed-bin flood coverage, benign bursts/peers, distribution drift and temporal false associations remain unresolved. Alert storms after a genuinely changing nominal regime need future operating-policy work.
- The experiment measures batch latency and sampled process memory, not live ingestion latency or isolated deployed CPU overhead. Timing depends on hardware/load.
- The paper, its numerical targets and real satellite data were unavailable. No final PDF or presentation was fabricated; these documented results/CSV tables are inputs for the team's technical report.

## L. Team handover

Read the [handover](handover.md), reproduce one scenario and recompute its confusion row before using these results with the jury. AI assistance supported implementation, experiments and documentation; the team must independently review and defend them. Explain both improvements and failures. Do not substitute event recall for sample recall, false episodes for FP seconds, or prototype Trust for probability of compromise.
