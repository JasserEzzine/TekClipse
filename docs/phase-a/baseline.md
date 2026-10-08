# Phase A audit baseline — 8 October 2026

Stage 1 completed before detector changes. Baseline commit: `2b25015378564206a84d50ace8e3d0e906c46d7e`; local safety branch: `safety/phase-a-baseline-2026-10-08-2b25015`. The cloud checkout was clean. The dirty older main checkout was left untouched. Original tests: **30 passed, 0 failed, 0 skipped in 78.16 seconds**.

## Reproduction

`python scripts/run_experiment.py --scenario E7 --hours 24` reproduced the historical result exactly. `python scripts/audit_phase_a_baseline.py --output results/phase-a-baseline.json` provides the component breakdown for E1–E7. The recorded pre-change output is [baseline.json](baseline.json), including original source/test hashes and measured timing.

Seed 42, 24 hours at 1 Hz, first six hours nominal training, remaining 64,800 seconds scored. IF: 100 trees, model seed 42, contamination .05, threshold at training-score quantile .95, 21 raw/rolling telemetry features. Inclusive ground-truth windows are unioned; multiple alerts in one second count once. R2 is evaluated at the eleventh command, not its legacy minute timestamp. Rolling features restart at the split. Attack aftereffects outside the injected window remain false positives.

| E7 method | TP | FP | TN | FN | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Rules | 63 | 0 | 64683 | 54 | 1 | .538462 | .7 | 0 |
| IF | 58 | 3068 | 61615 | 59 | .018554 | .495726 | .035769 | .047431 |
| Hybrid | 117 | 3068 | 61615 | 0 | .036735 | 1 | .070866 | .047431 |

All 3,068 hybrid FP seconds originate in IF. 3,067 occur at the same seconds in E1; one additional second follows the E7 injection. Rules, network and explicit subsystem events contribute no FP seconds here. This is predominantly nominal calibration error, not duplicate alert inflation. A training 95th-percentile threshold deliberately flags the nominal tail; contamination is not an attack prior. See the [official IF definition](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html). The first six hours also cover fewer operational phases than a full day.

## Architecture and correctness findings

- `data/generator.py`: fixed seed 42 and relative 1 January schedule. Correlated orbital/pass patterns; no independent-run seed API yet. No research paper PDF, DOCX or TeX was found in either project checkout; paper targets cannot be verified.
- `data/injection.py`, `data/coordinated.py`: E1–E7 injection definitions and explicit union intervals. E3 labels a 59-second burst interval despite sparse command arrivals. One R2 alert gives sample recall 1/59 but event recall 1/1; neither should be substituted for the other.
- `evaluation/validated.py`: valid deduplicated second counts for complete 1 Hz input, but helper itself does not reject irregular timelines, timezone ambiguity, inconsistent or overlapping event intervals. No separate source-matched event metric, false-alarm episode rate, network comparison or incident evaluation. Global any-source temporal hits can credit unrelated detectors. `evaluation/runner.py` is a legacy preview, correctly marked unavailable; its old low-level metrics return zero for undefined ratios and must not be used for final research results.
- `pipeline/rules.py`: R1 trusts GS_PRIMARY even when explicitly unauthorized (correctness bug). Missing authorization defaults to True; UNKNOWN_1 always alarms. R2 uses fixed UTC minute bins, >10 total commands regardless of authority/type; a boundary-straddling burst can be missed. R3 uses strict >85 C / <26 V / >30 V; iterating every nominal telemetry row costs ~1.59–1.64s per 18-hour frame in this run.
- `pipeline/model.py`, `features.py`: IF uses raw telemetry and trailing 60-sample means/std. No future samples, but no explicit missing/nonfinite input policy. Model defaults and dashboard threshold are hardcoded rather than a scientific protocol. The same-run temporal holdout is not an independent session test; preview overlaps nominal training and is clearly disclosed.
- `pipeline/network.py`: per-second counts summed, limits 1.5× nominal .999 quantile, rise threshold 6× .999 difference (minimum500), category novelty. Unseen authorized peers still alarm because there is no authority registry. Normal pass variation is covered in seed 42. This is novelty, not proof of hostile traffic.
- `pipeline/correlation.py`: non-ML seeds, bounded forward 180-second grouping, each ID consumed once, at least two domains; R3 and ML are one domain. Temporal proximity can associate unrelated events. This is not an independent raw detector. Score caps repeated families. Incident identifiers are recomputed per snapshot.
- `pipeline/trust.py`: active trailing180s, maximum severity per family, capped deduction, one capped association deduction. R3+ML and correlation deliberately add policy weights; these are not independent probabilities. Repeated rows do not increase family penalties. Existing tests verify causality, expiry and reset. No demonstrated mathematics bug: preserve it.
- Explanations, subsystem mapping, mission impact, recommendations, eight dashboard tabs, CSV/SQLite and optional Parquet remain covered by original tests. Dashboard executes IF scoring twice per run; defer optimization unless separately justified.

## Ranked decisions before Stage 2

| Priority | Change/hypothesis | Benefit | Risk / effort |
|---|---|---|---|
| P0 | Independent run seeds, strict metric validation, explicit source-matched event ledger | Defensible comparisons; reveals temporal-hit credit | Low / moderate |
| P0 | Full-day nominal IF fit + separate nominal calibration at .999 quantile | Reduce nominal tail alarms; quantify lost IF sensitivity | Moderate / moderate; experimental profile only |
| P0 | Honor explicit unauthorized GS_PRIMARY | Fix missed unauthorized commands | Low / small; focused boundary regression |
| P1 | Evaluate ablations, benign changes and attack variants | Expose scope and false associations | Low / moderate |
| P1 | Filter R3 rows before formatting alerts, with exact output parity | Remove measured nominal row-loop bottleneck | Low / small |

Predeclared experiment: train seed101; calibration seed202; validation seed203; final test seeds301/302/303. Each independent run is24 h; standard scenarios unchanged. Original profile fits first 6 h of training run at .95 training quantile. Candidate fits full 24 h and calibrates .999 quantile on a separate nominal run. Also measure full-day fit with .95 training quantile to separate the two changes. .999 is an exploratory engineering choice, **not a recovered paper target**. Keep candidate only if validation reduces hybrid FP seconds without losing source-matched attack-event coverage on established E2–E7; report standalone IF recall trade-offs. Freeze all choices before generating final test runs. Never tune on final test results.

No UI redesign, no trust-formula change, no scenario rewriting, no automatic push. Calibrated evaluation remains explicitly separate from the established dashboard preview until its operational policy can be reviewed.
