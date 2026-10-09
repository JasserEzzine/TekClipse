# Phase D — three reproducible jury demonstrations

Start the app using [handover.md](handover.md). In the sidebar select **one day** and **Phase A.2 hardened (experimental)**. Display data uses seed 42; these demonstrations are not the archived scientific benchmark. Source identifiers and IPs belong to the simulation.

## A · Unauthorized command (about one minute)

1. Open **SCENARIOS E1–E7**, click **Run E2**, then return to **OVERVIEW**.
2. Enable **Open cyber defense workspace**. Set **Defense review / seconds after 12:00 UTC** to **0** and press Enter.
3. In the security event log choose **Detector → R1**. Inspect `UNKNOWN_1`, `REBOOT`, and `authorized: false` in **Supporting raw records and related findings**. No IP or real attacker identity is known.
4. Choose **Reject unauthorized commands / command-channel**. Enter an operator reason such as `Rehearse rejection of the unauthorized command` and press Enter.
5. Click **Apply simulated restriction**. The explicit resubmission probe changes **ALLOW → DENY**. Explain that it reuses the observed payload in a new hypothetical admission test; the stored E2 command is not rewritten and no later unauthorized observation is invented.
6. Show the audit and export its JSON. Click **Restore normal access** to see **DENY → ALLOW**. Download a finding report if needed; E2 need not have a correlated incident.

## B · Command flood (about ninety seconds)

1. Open **SCENARIOS E1–E7 → Run E3**, then **OVERVIEW**. Enable the cyber defense workspace.
2. Set the defense review to **20** seconds; press Enter. Select **Detector → R2**. The hardened rolling rate policy has already crossed its threshold. Inspect the actual command records and `GS_PRIMARY` source.
3. Choose **Quarantine command station / GS_PRIMARY**, enter `Contain observed command-rate violation`, and apply the restriction.
4. Set the review to **58** seconds. The recorded UPLOAD sequence continues in the original observations, but **19 later commands** are denied by the counterfactual admission evaluator for this seed/profile. Network rows and unrelated sources remain allowed. This is a functional admission decision, not removal of historical commands or proof of physical mitigation.
5. Show the qualified **SPARTA EX-0013.01** mapping. Valid-command volume supports the analogy; malicious intent and resource exhaustion are unproven.
6. Enter a restoration reason and click **Restore normal access**. The resubmission becomes ALLOW; prior denied admission decisions remain in the audit/report. Export the finding report with its timeline, mapping and response outcomes.

## C · Coordinated E7 attack (two to three minutes)

1. Click **Reset demo** to show nominal E1 and explain the policy Trust Score. Click **Launch E7 attack**. It begins at +000.
2. Enable the cyber defense workspace. Advance to **+020**: inspect R1 and UNKNOWN_1. Advance to **+045**: choose **Detector → NET**, **Source identifier → 203.0.113.27**.
3. Explain that NET aggregates all flows in the second. The supporting list includes co-occurring nominal traffic; the source choice is manual. Choose **Block network source / 203.0.113.27**, enter a reason, and apply it.
4. Advance the remaining stages: **+086, +100, +120, +160, +180**. That is seven total advances. The timeline and five subsystems follow actual findings. At +180, **115 subsequent network rows** from the chosen peer are denied under the simulation policy. Original evidence and the observed Trust Score remain **9** for this specific run; no remediation-driven score increase is invented.
5. Choose **Report scope → INC-001**. Review the multi-source incident, provenance, Trust deductions, qualified R2 mapping, network restriction and uncertainties. Download both JSON and HTML reports.
6. Explain: rules flag policy violations, NET identifies baseline/authorization deviations, and Isolation Forest provides statistical evidence. Temporal correlation does not prove one attacker caused all effects. Restore access or Reset to E1; old audit evidence remains stored.

If a filter produces no findings, clear it or advance to the appropriate review time. If a scientific profile produces no ML alert at a stage, report its actual result. Normal events are not attacks; no real station, firewall or satellite is controlled by these demonstrations.
