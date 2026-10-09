# Phase D — cybersecurity defense and incident investigation

Phase D adds a persistent evidence journal, source investigation, reversible simulation admission policies and incident reports to the existing Streamlit application. It does not change the detector pipeline, attack injections, scientific profiles or Trust mathematics. All responses are manual and simulated.

## Audit and preservation

Baseline: `f4eef4a` on `tekclipse-cloud`; checkpoint `safety/phase-d-baseline-f4eef4a`. Phase A, A.2 and C reports, handovers, protocols and verification artifacts informed the implementation. The baseline suite passed 72 tests with no failures or skips in 273.72 seconds. [baseline-inventory.json](baseline-inventory.json) fingerprints 125 original tests, detector/data/evaluation/storage files, scientific archives, configuration, requirements and data service files.

The actual entry point is `streamlit_app.py`, which executes `tekclipse/dashboard/app.py`. The eight original tabs, E1–E7, seven E7 advances, original/Phase A/Phase A.2 profiles, five subsystems, orbit schematic, telemetry/command/network/event analysis, evaluation CLIs and old exports remain. No historical benchmark artifacts are regenerated or overwritten. The old dirty main checkout is separate and untouched.

### What the existing records support

| Record | Existing fields | Interpretation and new linkage |
|---|---|---|
| Detector finding | Local alert ID, detector, severity, timestamp, observed_at, description, subsystems | New run-scoped event ID; detector severity retained verbatim |
| Command | timestamp, type, source, authorized | Logical station identifiers such as GS_PRIMARY, GS_BACKUP, UNKNOWN_1; no invented IP |
| Network | timestamp, src_ip, dst_ip, protocol, packets, bytes, connection_count, traffic_rate | Actual simulated IPs; NET aggregates all rows in a second, so every associated peer is not necessarily suspicious |
| System event | timestamp, event_type, source, details | Logical component, not attacker identity; matched by time/type/component |
| Telemetry | timestamp and seven measurements | Sample and available trailing feature inputs; no attacker source inferred |
| Incident | Local INC ID, time range, detected_at, sources, contributing alert IDs, score/severity/explanation | Recomputed by existing correlation at the current review time; temporal association only |

There are no authenticated sessions or shared causal identifiers linking ground commands, network flows and spacecraft effects. No new station or attacker identifier was needed. Raw-record identifiers address deterministic rows in a bounded run; they are evidence locators, not identities. R1 links matching timestamp/source/type/authorization predicates; indistinguishable duplicates remain ambiguous. R2 links the commands observed within the applicable fixed/rolling window. ML links available current/trailing 60-second telemetry inputs, not causal feature attribution.

## Evidence journal

`results/security-evidence.sqlite` uses new SQLite tables and the existing results-directory helper. Original CSV/SQLite/Parquet operational data, alerts database and JSON outputs are untouched. Findings, supporting raw operational records, review-time incident/trust snapshots, exercises and response actions are separate tables. Inserts are idempotent for observations and reviews; actions append under a transaction. Run IDs include dataset token, scenario, profile, duration and existing scientific signature. Row/event IDs are deterministic within that context. No destructive migration is required.

The dashboard journal covers **11:57–12:03 UTC on 1 January 2026**, with up to 60 seconds of preceding raw feature context. It records actual findings through the selected review time; it does not fabricate a historical full-run alert archive. The record builder can represent every supported detector family. Original analytical tabs still expose the complete stored run. The journal persists on the server filesystem; ephemeral hosting can discard it unless durable storage is provisioned.

The event feed filters by start timestamp, detector, severity, recorded source, scenario and current incident. The selected review clock is the inclusive end bound. Scenario filtering is intentionally scoped to the current run, avoiding accidental mixing of seeds/profiles. Tables show at most 200 findings; filtered CSV/JSON exports include all matches. CSV escapes spreadsheet formula prefixes; JSON preserves exact evidence strings. Findings retain their original observation status and separately list response audit IDs; applying a restriction never marks an alert disproven or an incident resolved.

Incident IDs are local to a run and review time. They are not stable global attacker/case identifiers: a later correlation window may regroup evidence. Persisted snapshots and reports carry the review context to make this explicit.

## Functional response semantics

| Manual policy | Evidence requirement | Actual simulation effect |
|---|---|---|
| Reject unauthorized commands | R1 with matching raw commands | Later commands with UNKNOWN_1 or explicit unauthorized status return DENY |
| Quarantine command station | R1/R2 and an observed logical source | Later commands from that station return DENY, including otherwise authorized commands |
| Block network source | NET and a source IP in its contributing records | Later network rows from that source return DENY; other sources continue to return ALLOW |
| Restore access | Active restriction with original evidence ID | Append a reversal; later evaluations no longer apply that restriction |

The new evaluator's unrestricted baseline is **ALLOW**. This is an explicit simulation assumption, not proof that an originally stored command executed successfully. Historical observations and Trust Score remain unchanged. Later observed rows are evaluated under the policies effective at their timestamps. Reversals preserve earlier admission decisions. Restrictions expire after 300 simulated seconds or manual restoration; the short UI review interval makes manual restoration the practical demo path. No automatic response exists.

Each action records a unique ID, exercise/run, simulated operator, simulated time, wall-clock recording time, policy/target, reason, evidence, result, expiry and reversal reference. An explicit resubmission probe reuses an already observed payload at review time plus one microsecond. Its before/after decision demonstrates enforcement immediately, even when E2 has no later unauthorized command. It is labeled synthetic and never enters the detector or raw-observation ledger. Subsequent admission outcomes are reproducible from the persisted observations and audit, and are included in reports.

Each browser session gets a separate exercise. Scenario/profile/duration changes and Reset start new response context; old audit rows remain stored. Rewinding hides later actions and evidence. Mutation before an existing later action is rejected; advance back or start a fresh exercise. Manual duplicate restrictions, unsupported targets, future findings and findings from another run are rejected. SQLite serializes action validation and insertion. This is a local research journal, not tamper-proof forensic storage or an authenticated multi-user SOC.

## Investigation and reports

The Overview and scenario briefing expose **Open cyber defense workspace**. The original satellite overview, posture, counts, Trust gauge and subsystem cards remain visible. The workspace adds a structured feed, provenance card, raw-record drilldown, source/incident-related findings, incident cards, qualified SPARTA mapping, response controls, before/after outcomes, audit and exports. Missing source information is explicitly unknown. Related evidence means shared recorded source or temporal incident, never established actor identity.

JSON and standalone escaped HTML reports include context, incident (when one exists), chronological findings/raw records, detectors/subsystems, current Trust deductions, mappings, relevant actions, other exercise policy context, subsequent evaluation and limitations. A standalone E2/E3 finding report does not invent an incident. Trust deductions describe the whole active review window, not a newly calculated per-incident score.

The legacy fixed-minute R2 detector can describe the completed minute's total before every command has occurred. New causal presentation copies replace that text with the actual observed count at threshold crossing. The original detector record and scientific metrics stay intact. The new mission narration, journal and exports therefore do not reveal a future command count. Full-scenario analytical tabs remain explicitly retrospective.

## SPARTA verification

The official Aerospace SPARTA pages verified **EX-0013.01 — Flooding: Valid Commands** and **IA-0007.02 — Malicious Commanding via Valid GS** on 9 October 2026. The first describes excessive legitimate command traffic; the second assumes a compromised mission ground system. Sources: [EX-0013.01](https://sparta.aerospace.org/technique/EX-0013/01/), [IA-0007.02](https://sparta.aerospace.org/technique/IA-0007/02/).

Only EX-0013.01 is emitted, for E3/E7 R2 evidence with more than ten observed authorized commands. This is a moderate-confidence behavior analogy, qualified because resource exhaustion and intent are not established. R1 alone does not support ground-system compromise; NET novelty does not prove exploitation or DoS; ML/R3/SYS deviations do not prove a cyber technique. These remain unmapped. Source pages are external references, not runtime dependencies; no external call occurs when applying a response.

## Chart review and protocol proportions

The nominal generator uses `protocol = TCP if t is even else UDP`; whole-hour datasets therefore contain exactly equal row counts. The pie chart correctly counts rows, not bytes, packets or unique connections. E4 adds 120 TCP rows; E7 adds 116 UDP rows. Focused tests verify those counts. No proportions or generator parameters were altered.

The Network tab now explains this assumption. The protocol pie keeps labels inside slices and gives exact row counts on hover; flow axes state daily byte/packet totals, and rate units are explicit. Common chart margins and axis auto-margins leave more room for tick labels and horizontal legends. Visual review caught a legend overlapping the time-range slider, so time charts now reserve a separate lower legend area. The event heatmap uses categorical UTC dates rather than displaying misleading fractional-time ticks around a single date. The system-event feed removes the redundant legend because event types are already on its y-axis. Existing underlying samples and controls remain available.

## Verification and limitations

Exact final test counts, browser checks, preservation hashes and scans are recorded in [verification.json](verification.json). Actual screenshots and browser demo exports accompany this report. The response checks exercise later records as well as probes; they do not merely assert badge changes.

Final regression: **90 passed, 0 failed, 0 skipped in 126.19 seconds** (JUnit: 126.169 seconds). All 125 protected files retain their baseline hashes. Real Edge checks passed all eight tabs, all three profiles, seven E7 advances per profile, reset and the preserved 63-record filtered CSV export. The defense workflow passed E2 rejection/restoration, E3 denial of 19 later commands/restoration, and E7 denial of 115 later peer flows with incident export and unchanged Trust 9. No horizontal overflow was found at **1920×1080, 1366×768, 768×1024 or 390×844**.

Security checks: **0 Bandit findings, 0 Bandit scan errors, and 0 detect-secrets findings** in current tracked/staged files. The credential scan does not cover repository history. Staged whitespace checks and documentation links passed. These checks are bounded verification, not a guarantee against every possible vulnerability.

Actual captures: [Overview](screenshots/overview-1366.png), [security logs](screenshots/security-logs.png), [source investigation](screenshots/incident-investigation.png), [incident card](screenshots/incident-card.png), [simulated response](screenshots/simulated-response.png), [phone layout](screenshots/overview-390.png), [network chart](screenshots/network-chart.png), [corrected event heatmap](screenshots/events-chart.png). These were captured after rerender completion, without editing the images. Examples downloaded from the browser: [E2 action audit](examples/e2-actions.json), [E3 finding report](examples/e3-report.json), [E7 incident JSON](examples/e7-incident.json), [E7 incident HTML](examples/e7-incident.html).

Resolved browser issues included a retained frontend toggle value after scenario changes, asynchronous stage/download rendering, and checker selectors/UTF-8 handling. The application now explicitly resets widget values; the checker waits for the completed render before exporting or capturing. Original tests and assertions were preserved.

Remaining limits: synthetic data and logical identities; aggregate NET attribution ambiguity; detector false positives and limited ML value from A.2; no physical spacecraft consequence simulation; a bounded mission journal; local filesystem durability; no authenticated operator roles or tamper-resistant audit; phone views require vertical scrolling. Restrictions can deny legitimate traffic from a selected source. Restoring a restriction does not certify mission safety, undo a real command or improve the historical Trust Score. No real-world or flight qualification is claimed.

## Important code changes

- New `tekclipse/security/evidence.py`: record provenance, causal filtering, safe narration and CSV export.
- New `tekclipse/security/store.py`: additive SQLite journal and transactional action audit.
- New `tekclipse/security/defense.py`: admission, expiry, reversal and explicit probe evaluation.
- New `tekclipse/security/report.py`: qualified SPARTA mapping and JSON/HTML incident report data.
- New `tekclipse/dashboard/defense_service.py` and `defense_panel.py`: cached evidence preparation and integrated workflow. Evidence preparation consumes existing detector output; it never invokes model fitting or a new detection run.
- Modified dashboard app/security panel, chart styling and scoped CSS; README documents launch and Phase D.
- New focused pure/app tests and `scripts/check_phase_d_ui.py` for reproducible real-browser demonstrations. Original tests remain unchanged.

No runtime dependency, real firewall operation or external messaging integration was added. On 9 October 2026 the user explicitly requested a GitHub push after verification; publication is authorized on `tekclipse-cloud`. No separate hosting deployment is performed.
