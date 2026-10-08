# Phase A.2 — detection reliability and scientific hardening

Phase A.2 fixes the rolling command-flood blind spot, adds explicit network-flow authorization, makes correlation more conservative, and connects the dashboard to the scientific detector configurations. A nominal-noise training/calibration change reduces E7 false-positive seconds by **62.34% relative to Phase A**, with **18/18 source-matched events retained**. Isolation Forest still adds no coverage on standard E7. Its incremental coverage on new operational deviations is limited and inconsistent.

This is a synthetic prototype evaluation, not production or flight validation. No dependencies were added, no trust weights were changed, and no push was performed. Original Phase A artifacts and all original test files are preserved byte-for-byte. See [baseline audit](baseline.md), [selection decisions](validation-decisions.md), [complete measurements](metrics.md), [handover and exact commands](handover.md), and [verification record](verification.json).

## Evidence and experimental boundaries

The unchanged Phase A protocol supplies E1–E7 and all nine robustness cases on frozen seeds **301/302/303**: 48 cases. Each Phase A comparator was recomputed and checked against its archived hybrid measurements and dataset fingerprints. The historical original comparator comes from the previously verified archive, not a newly relabeled experiment.

New experiments use nominal training seed **501**, calibration **502**, validation **503/504**, and test **601/602/603**. Test roles and operational variant magnitudes were fixed before validation. The final matrix adds E1/E7 controls and five new operational/nominal variants on each new test seed: 21 additional cases, **69 total**. These cases were run twice; all common confusion/event/incident/trust measurements and data fingerprints matched exactly. The second run additionally records paired nominal counterfactuals for ML attribution.

Selection evolved during validation, transparently documented in [validation-decisions.md](validation-decisions.md). Round 1's 21-feature, seven-mean and nine-relationship candidates failed the initial coverage requirement. Round 2's contextual residual candidate detected more operational anomalies but produced unacceptable benign-regime false alarms. Round 3 explicitly required lower aggregate benign false alarms and retained E5/E7 ML events, while assessing operational novelty separately. **This is validation-based engineering, not a claimed first-attempt preregistered success.** Final test results did not change the selected model, thresholds, ground truth or variant parameters.

All runs contain 86,400 one-second samples. Confusion counts classify a second with any emitted alert; event recall requires a compatible detector inside the exact event window. A three-seed row pools 259,200 seconds / 72 simulated hours. Delays average detected events only; missed events are not assigned zero delay. Episode rates supplement raw counts. Incident groups have no defensible TN universe, so incident TN/FPR remain undefined.

## Before/after E7

These rows use the identical 301/302/303 datasets and labels (351 positive and 258,849 negative seconds).

| Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP seconds/hour | False episodes/hour | Source-matched events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Historical original | 351 | 14,141 | 244,708 | 0 | 2.42% | 100% | 4.73% | 5.46% | 196.40 | 27.86 | 18/18 |
| Phase A calibrated | 351 | 7,254 | 251,595 | 0 | 4.62% | 100% | 8.82% | 2.80% | 100.75 | 18.24 | 18/18 |
| Phase A.2 hardened | 351 | 2,732 | 256,117 | 0 | 11.39% | 100% | 20.44% | 1.06% | 37.94 | 7.50 | 18/18 |
| Phase A.2 without ML | 351 | 0 | 258,849 | 0 | 100% | 100% | 100% | 0% | 0 | 0 | 18/18 |

The Phase A.2 reduction is 62.34% versus Phase A and 80.68% versus historical original. The earlier **48.70%** number remains Phase A versus historical original. Hybrid mean event delay remains **1.67 seconds**, and the first supported E7 multi-domain association remains **25 seconds** after the first malicious event. Perfect no-ML results apply to these known simulator injections only.

[metrics.md](metrics.md) contains the full before/after TP/FP/TN/FN, precision, recall, F1, FPR, both false-alarm rates, event recall and delay for every scenario and robustness case. [aggregate-metrics.csv](aggregate-metrics.csv) also includes rules, ML, network, no-ML/no-network/no-rules ablations and changes applied one at a time. [results/metrics.csv](results/metrics.csv) retains every individual seed; [results/incidents.csv](results/incidents.csv) keeps association metrics separate.

## What changed

### R2: rolling 60-second policy

The Phase A.2 profile counts commands in **(t−60 seconds, t]** and alerts when the count first exceeds ten. Sorting is followed by a linear deque scan. Simultaneous commands all count; expiry and arrivals at the same instant are evaluated together. Input order does not affect the result. One alert is emitted per continuous above-threshold episode; separate floods produce separate alerts. Authorization does not exempt a rate anomaly.

The boundary flood at 09:00:54–09:01:05 changes from **0/3 to 3/3 detected events**, first observed after **10 seconds**. Its second-level TP/FN become 3/33 over the three 12-second windows: an episode alert is not a continuous alarm at every attack second. E3 retains 3/3 events and 18-second mean delay; E6/E7 event coverage is preserved. Exactly ten commands, commands exactly 60 seconds apart, duplicates, simultaneous expiry/arrival, unsorted input and separated bursts have direct tests and a brute-force transition comparison.

The declared benign authorized burst still generates **one R2 alert per run**: three false-positive seconds across 72 hours under the benign experiment labels. That is the explicit rate-policy trade-off. The original API/default preview and Phase A profile retain fixed-minute R2 for historical compatibility; select **Phase A.2 hardened** to use the correction.

### Isolation Forest: representative nominal noise, no alert suppression

The accepted profile retains the original 21 telemetry features and Isolation Forest (100 trees, contamination .05, seed 42). It fits on a complete nominal day containing alternating 90-minute blocks of ordinary and additional nominal sensor noise: temperature SD .5 C and CPU SD 1 percentage point. Calibration uses a separate similarly augmented nominal day and its **.99 score quantile**, giving threshold **0.029328459963379617**. Inference telemetry is never modified. All raw scores above threshold produce an ML alert: no persistence gate, clipping, cooldown or hidden observations.

The verified weakness was narrow noise representativeness: rolling standard-deviation features changed substantially under the declared benign-noise variant. Reducing to rolling means alone lost thermal coverage. Contextual residuals exposed some operational changes but also flagged harmless unseen offsets; that candidate is retained as rejected evidence. Contamination is unchanged; the explicit independent quantile determines the operating point. Additional scaling was not introduced without supporting evidence. Temporal means remain causal, with the existing first-sample warm-up behavior retained and included in all denominators.

On 301/302/303 nominal E1, false-positive seconds fall **7,249 → 2,732**. On benign telemetry noise they fall **24,159 → 6,148 (74.55%)**, while false-alarm episodes fall **1,274 → 1,029**; the episode reduction is much smaller than the seconds reduction. On new unseen benign thermal/power regimes, false positives fall **9,690 → 4,029** and **10,976 → 3,875**. These remaining alarms are not excused by the operating-regime explanation.

Retaining standard event recall does not preserve sample coverage or latency. E7 ML-only true-positive seconds fall **160 → 46**, and thermal-event delay rises **5.33 → 19.00 seconds**. E5 ML-only true-positive seconds rise **12 → 17**, but mean event delay worsens **19.33 → 29.67 seconds**. Both retain 3/3 compatible thermal events. Deterministic R3 still provides immediate coverage of hard-limit violations.

### Explicit network authorization

The selected profile registers two example flows: `10.0.0.99 → 10.1.0.5 / TCP` and `10.0.0.99 → 10.1.0.6 / UDP`. All three fields must match. Optional UTC validity bounds are supported and tested. A registered match exempts only novelty against the learned categories; packet, byte, traffic-volume and adjacent-second spike checks continue unchanged. A changed protocol or unregistered destination still alarms. Repeated observations never update authorization.

The Phase A authorized-peer variant produces **270 → 0 NET false-positive seconds** over three runs. Total hybrid FP are **7,519 → 2,732**, combining this correction with the ML change. E4 and E7 network coverage is retained. The low-intensity network case still detects only its first rise: **3 TP / 267 FN seconds**, although event recall is 3/3. This is a remaining duration/sensitivity limitation, not full low-intensity coverage.

The registry is explicit simulated operator context, not authenticated identity or proof that an IP cannot be spoofed. It does not support ports because the input schema has none. The unchanged learned baseline still represents expected categories; authorization is a separate explicit exemption and grants no blanket trust. Current example registrations have no expiration; operators must edit the profile configuration to change that assumption.

### Conservative correlation and unchanged trust math

The hardened correlation policy deduplicates identical IDs, rejects conflicting reuse of an ID, and separates evidence with different explicit asset IDs. It requires **two non-ML domains** to establish an incident; ML is contextual and cannot establish an extra domain or inflate severity. ML and R3 remain one telemetry domain. The existing incident schema is retained, with explicit temporal-association language.

The simulator represents one satellite and does not provide causal session/link identifiers. Two unrelated non-ML events on that asset within 180 seconds can still be associated; no causal claim is made. In the frozen matrix the existing and hardened policies both have zero unmatched incident groups, so **no measured matrix-level incident precision gain is claimed**. Targeted adversarial tests demonstrate the corrected duplicate/background-ML cases. E6, E7 and the reordered sequence each retain 3/3 reference incidents, with 0, 25 and 30-second supported-association delays respectively.

Trust deductions, severity weights, caps, boundaries and status thresholds are unchanged. The selected correlation policy is passed consistently into all snapshots and history points. For example, seeds 302/303 have trust 11 instead of 9 at E7 +120 seconds because ML has not yet fired; the two-point difference is the existing ML deduction, not a formula change. Both profiles reach 9 by +160 seconds. Trust is a prototype policy indicator, not a probability of compromise; expiry-driven recovery is not verified remediation.

## What ML demonstrably adds

New deviations are labeled **operational anomalies, not cyberattacks**: a 12 C drift ramped over 300 seconds and held to 600 seconds; +8 W power with unchanged CPU/RAM; −.15 V voltage with unchanged battery. All remain inside R3 limits and plausible within this simplified numerical generator. Benign +1.5 C and +3 W full-run offsets remain negative labels. The generator has useful algebraic relationships but is not a physical spacecraft model; these magnitudes do not establish real mission danger.

| New operational case, seeds 601/602/603 | Phase A incremental ML coverage | Phase A.2 incremental ML coverage | Without ML |
|---|---:|---:|---:|
| Moderate thermal drift | 0/3 | 0/3 | 0/3 |
| Power/CPU/RAM relationship | 3/3 | 2/3 | 0/3 |
| Voltage/battery relationship | 3/3 | 1/3 | 0/3 |

Coverage here requires at least one newly flagged second relative to the **same seed's untouched nominal counterpart**, not merely an incidental ML alarm in the injected window. This catches a misleading result: Phase A appears to detect one thermal-drift event under ordinary event matching, but that alarm already occurred in its nominal twin and supplies no incremental sensitivity. The raw event metrics remain unchanged in the full tables; the counterfactual check is an additional, explicitly stricter measurement.

Phase A.2 adds **3/9 operational events beyond deterministic checks** (22 newly flagged seconds), compared with Phase A's 6/9 (51 newly flagged seconds). Its power hits occur after 10 and 0 seconds; the voltage hit after 1 second. It misses all thermal drifts and most sustained anomaly seconds. Validation had 0/6 operational hits for this selected candidate; test coverage is therefore inconsistent, not a demonstrated robust generalization capability. Do not retune on these outcomes.

The defensible positioning is **experimental supporting anomaly evidence**. ML remains implemented and selectable, contributes limited sensitivity to some sub-rule relationships, and does not establish maliciousness. On known E7 injections it adds false alarms without incremental event coverage. The lower-FP candidate trades away some operational sensitivity; this negative result is part of the deliverable.

## Dashboard and validation

The original preview remains the default. The sidebar offers **Original preview**, **Phase A calibrated**, and **Phase A.2 hardened**, and the active profile is also printed in the main view. Scientific profile metadata exposes fit/calibration seeds, threshold, feature columns, configuration digest and explicit authorized flows. The separate displayed-data evaluation uses the same fitted bundle as the preview and the CLI. Display seed 42 is independent of scientific training, but is not the official published test set. Original preview evaluation retains its historical six-hour split, explicitly labeled separately.

Scientific models are fitted only from fixed nominal generator runs, before any displayed attack injection. Model/data caches include profile identity and a signature of configuration and relevant source files. Changing profile or duration clears stale scenario/evaluation/replay state; Reset keeps the selected profile and restores E1. Replay clicks do not refit. Longer previews remain available, but the interface labels them outside the validated 24-hour experiment range. No major visual layout was changed.

The final full suite has **65 passed, 0 failed, 0 skipped** (109.66 seconds): all 43 historical tests plus 22 new cases. The [verification record](verification.json) contains CLI/security checks and real-browser reports. Browser checks use installed Edge at **1920×1080 and 1366×768**, exercise all eight tabs, all seven E7 advances, mission impact, recommendations, original orbit iframe and Reset. Local screenshots are actual captures, not mockups. Early browser-checker failures were an import-path omission, an outdated sidebar test selector, and tab-click/render synchronization; these were corrected without weakening UI assertions. No application failure was concealed.

## Remaining limits and jury explanation

Residual false alarms remain material (37.94 per simulated hour on E7), ML novelty coverage is inconsistent, and three test seeds cannot support broad reliability claims. Noise augmentation covers a declared simulator regime rather than arbitrary real-world sensor drift. New peer authorization is static and simulated. Fixed-minute behavior remains available in the original and Phase A compatibility profiles. Correlation remains temporal association. The low-intensity network case has poor per-second recall. Longer-duration scientific previews and real spacecraft data are not validated.

For the jury: “TekClipse combines explicit command and telemetry rules, statistical network checks and an experimental Isolation Forest. We corrected a command burst that could cross a clock-minute boundary, made known legitimate network flows explicit, and reduced false alarms using independent nominal training and calibration. We kept the original demo profile and made the scientific profile selectable. The hardened profile detects all staged E7 events in our frozen synthetic tests, but the deterministic checks already cover those attacks. ML only adds limited coverage of some operational deviations and still produces false alarms. The trust indicator explains our policy deductions; it does not estimate a probability that a satellite is compromised.”
