# Mission-control presentation upgrade

## Baseline and scope

Baseline commit: `9de3447`, branch `tekclipse-cloud`. Before implementation, the complete suite returned **25 passed, 0 failed, 0 skipped in 102.10 seconds**. The review covered all eight pages, CSS, E1–E7, existing detection/correlation/trust/subsystem/response logic, evaluation, storage and README. The existing AppTest exercised every tab and scenario.

This is an additive presentation and mission-context layer. The original detectors, alert scoring, correlation and trust mathematics are unchanged. Source comparisons against the baseline verified the protected modules, original tests, detection/data-loading/evaluation functions, orbital schematic and ML gauge. No tests were removed or weakened.

## Added and polished

- A ground-to-space schematic with Earth, ground station, communication-security link and SAT-01. Its antenna/OBC/thermal/power colors follow existing subsystem state.
- A dominant real trust value, exact deductions, observed-stage sparkline and probability disclaimer.
- Five subsystem cards, a timestamp-ordered attack chain and a prominent correlated-incident card.
- Traceable deterministic mission-impact mappings. Only active evidence produces potential consequences; no new detector or physical prediction is introduced.
- Existing recommendations presented as operator decision support, with full recommendations retained in the analyst briefing.
- Visible E1/E7/reset buttons, compact replay controls, original judge helper retained.
- Responsive mission CSS, consistent chart typography, calmer semantic colors, larger controls, reduced-motion support and local fonts. The sidebar starts collapsed and remains available.
- All original metrics, trust formula, plots, evidence tables and JSON export remain in **Analyst briefing**. The original orbit, ML gauge, activity charts and judge helper remain below. All eight tabs stay operational.

## Ground/link and time semantics

`SAT-01` is an explicit simulated-spacecraft display name. “LINK DATA ACTIVE” reflects recent stored network rows, not a measured physical link. Scheduled contact is determined independently from the latest contact-acquired/closed event, and may be **OUT OF PASS**. Raw 1 Hz telemetry near the replay is retained in the cached chart payload so the hero does not accidentally reveal future values from an aggregate bin.

The header uses stored simulation UTC/elapsed mission time. The existing wall clock remains in the sidebar, separately labeled. Security colors express observed evidence, not flight qualification or confirmed physical health. Full-scenario analyst charts remain available and may show later data; the hero uses only evidence available at its selected time.

E7 remains unchanged: command +20s → network +45s → command burst observable +86s → thermal limit +100s → subsystem event +120s → final review +160s. Other evidence, such as ML, appears only at its actual detected time. The association node uses first multi-source association time, while its color/severity reflects the current review assessment. Ties show a triggering observation before its association.

## Validation and performance

Final complete suite: **30 passed, 0 failed, 0 skipped in 94.00 seconds**. The five new tests cover mission-impact provenance/non-mutation, causal chain order, real data availability/contact distinction, SVG validity/escaping, and actual UI replay/reset with a model-training spy. E1, E2, E3, E4, E5, E6 and E7 all pass the preserved original integration checks.

Real Edge browser verification visited all eight tabs, advanced all seven E7 review steps, inspected impact/recommendation visibility, reset and ran E1 again. No browser page errors or horizontal document/console overflow were found at **1920×1080** or **1366×768**. Smaller screens use vertical scrolling for the details. Actual screenshots and the raw verification report are in [assets](assets/README.md).

The recorded one-day browser run took **12.43 seconds** for an uncached E7 launch; subsequent stage transitions took **0.81–1.07 seconds**, median **0.92 seconds**, on the development machine. These are UI timings, not detector accuracy, real-time spacecraft guarantees or a controlled hardware benchmark. First startup and model fitting still require time. Warm up E7 before presenting. A test confirms stage changes do not retrain Isolation Forest. The new presentation retains only a small 361-second raw review window and uses lightweight SVG/CSS; it adds no runtime dependency.

## Files

Added:

| File | Purpose |
|---|---|
| `tekclipse/pipeline/mission_impact.py` | Traceable deterministic potential-consequence mapping |
| `tekclipse/dashboard/mission_state.py` | Causal chain, ground/space mapping and data-availability presentation model |
| `tekclipse/dashboard/mission_visuals.py` | Original SVG schematic, trust, incident, impact and response components |
| `tekclipse/dashboard/mission.css` | Responsive mission-control styling and reduced-motion rules |
| `tests/test_mission_presentation.py` | Four tests for new pure presentation/impact logic |
| `tests/test_mission_app.py` | Full staged UI/reset test and no-retraining check |
| `scripts/check_mission_ui.py` | Optional Edge browser verification and actual screenshots |
| `docs/mission-control.md` | This report |
| `docs/assets/README.md`, `verification.json`, six PNGs | Media provenance, measured checks and actual captures |

Modified: `README.md`; `streamlit_app.py` (initial sidebar state); `tekclipse/dashboard/app.py` (integration/controls/reset); `data_service.py` (bounded exact review samples only); `security_panel.py` (new hero plus preserved analyst content); `charts.py` (shared visual styling and HIGH severity color only).

## Template and asset decision

No external dashboard template was present or imported. The existing project palette/components were extended directly. All new vector artwork and CSS are original project code. The existing Inter, JetBrains Mono and Orbitron fonts retain SIL OFL 1.1 notices; [asset provenance](assets/README.md) records their source projects and exact use.

## Run and 2–3 minute jury flow

```powershell
cd C:\Users\msi\Bureau\TekClipse-cloud
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

1. **0:00–0:30:** Overview → **Start nominal E1**. Introduce SAT-01, synthetic link/telemetry and calculated trust.
2. **0:30–1:30:** **Launch E7 attack**, then **Next attack stage** through command, network, burst, thermal and subsystem evidence. Follow the spacecraft colors and timestamped chain.
3. **1:30–2:00:** Show the correlated incident and actual deductions. In the recorded one-day data, trust moves 100 → 80 → 58 → 46 → 23 → 9; those numbers are computed, not scripted display values.
4. **2:00–2:30:** Open **Mission impact reasoning**. Connect observed cyber evidence to a potential operational consequence. Show **Operator Decision Support** and its simulation-only label.
5. **2:30–3:00:** Open **Analyst briefing** if asked for evidence, formulas, the original timeline or full recommendations. **Reset demo**, then **Start nominal E1**; no stale E7 chain, impact or recommendation remains.

## Issues found and resolved

- Streamlit sanitized inline SVG, leaving a blank spacecraft area. The new component now uses an escaped self-contained SVG image, preserving sanitization and adding no script execution.
- During hot reload, imported presentation helpers could remain from the prior preview process. Final browser verification used a fresh local process.
- Browser resizing could scroll the focused slider into view during a screenshot. Capture now blurs focus and resets scrolling; separate complete console captures preserve the full story.
- The optional browser checker originally used Python assertions. It now raises explicit verification errors so checks remain active under optimized Python and pass the repository's static-analysis policy.

No remaining application regression was observed in the completed tests. Real satellite data, causal attack attribution, calibrated compromise probability, RF/flight dynamics and physical-failure prediction remain outside scope. The measured false positives and evaluation limitations documented in the main README remain unchanged.
