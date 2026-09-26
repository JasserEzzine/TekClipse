# TEKCLIPSE — Satellite Security Operations Prototype

A lightweight multi-source anomaly detection prototype for a simulated satellite environment, designed as a Phase 2 feasibility demonstrator for the IASTAM 6.0 Track 5 challenge.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B) ![Phase](https://img.shields.io/badge/Phase-2-feasibility-00C2FF)

## ⚠ Disclaimer

This project is a simulation-only prototype. It does not represent a flight-certified system. Alerts mean deviation from a learned nominal profile, not confirmed cyber compromise.

## Problem (P9)

Can the satellite still be trusted in an operational environment with multiple telemetry, command, network, and event streams? This demonstrator explores that question with deterministic synthetic data and lightweight anomaly detection so the team can test detection logic and dashboard UX before a more advanced Phase 3 system.

## Architecture

```text
TekClipse
├── config.yaml
├── requirements.txt
├── README.md
├── scripts/
│   ├── generate_data.py
│   └── run_experiment.py
├── tekclipse/
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   ├── generator.py
│   │   └── injection.py
│   ├── dashboard/
│   │   └── app.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── runner.py
│   ├── pipeline/
│   │   ├── alerts.py
│   │   ├── features.py
│   │   ├── model.py
│   │   ├── preprocess.py
│   │   └── rules.py
│   ├── storage/
│   │   └── db.py
│   └── data/
│       └── generated/
├── tests/
│   └── test_basic.py
└── results/
    ├── results.json
    └── summary.md
```

## Quick Start

```bash
# 1) Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Generate synthetic data
python scripts/generate_data.py --hours 24

# 4) Run the experiment suite
python scripts/run_experiment.py --scenario E1
python scripts/run_experiment.py --scenario E2
python scripts/run_experiment.py --scenario E3
python scripts/run_experiment.py --scenario E4
python scripts/run_experiment.py --scenario E5
python scripts/run_experiment.py --scenario E6

# 5) Launch the SOC dashboard
streamlit run tekclipse/dashboard/app.py
```

## Data

All data is synthetic and generated deterministically with seed 42. Telemetry is produced at 1 Hz and includes temperature, CPU, RAM, battery, voltage, power, and signal strength. Commands are generated roughly every 5 minutes with authorized sources. Network records contain packet, byte, and rate metrics. System events include auth and process activity.

This is appropriate for a Phase 2 demonstrator because it gives a realistic operational profile without depending on a proprietary or unavailable satellite dataset. The goal is to evaluate feasibility, not to claim flight-grade realism.

## Detection

### Rules

| Rule | Description | Severity |
|---|---|---|
| R1 | Unauthorized command source or non-authorized command activity | CRITICAL |
| R2 | More than 10 commands per minute | CRITICAL |
| R3 | Hard limits: temperature > 85 C or voltage outside 26–30 V | WARNING |

### Isolation Forest

The model uses a practical Isolation Forest baseline:

- `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)`
- fit on nominal data only
- train/test split uses the first 70% nominal data for training and the remaining 30% plus injected anomalies for testing
- score is `-decision_function`
- alert threshold is derived from the contamination quantile of nominal train scores

This is intentionally described as a baseline and not as an optimal detector. The project does not claim military-grade detection performance.

## Scenarios

| Scenario | Description | Status |
|---|---|---|
| E1 | Nominal baseline | IMPLEMENTED and runnable |
| E2 | Unauthorized source sends REBOOT | Runnable via injection |
| E3 | Command flood (30 commands / 60 s) | Runnable via injection |
| E4 | Network spike (traffic rate x10, 2 min) | Runnable via injection |
| E5 | Telemetry manipulation (temperature step to 120 C) | Runnable via injection |
| E6 | Combined E2 + E4 + E5 | Runnable via injection |

## Evaluation

Metrics are computed with real values from actual runs:

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2PR / (P + R)
- FPR = FP / (FP + TN)
- Latency = first_alert − onset
- CPU/RAM overhead = psutil-based process usage

### Actual measured results from the workspace run

| Scenario | Precision | Recall | F1 | FPR | Latency(ms) |
|---|---:|---:|---:|---:|---:|
| E1 | 0.000 | 0.000 | 0.000 | 0.000 | [TO BE MEASURED] |
| E2 | 1.000 | 1.000 | 1.000 | 0.000 | 0.0 |
| E3 | 1.000 | 1.000 | 1.000 | 0.000 | 0.0 |
| E4 | 0.000 | 0.000 | 0.000 | 0.000 | [TO BE MEASURED] |
| E5 | 0.006 | 1.000 | 0.011 | 1.000 | 0.0 |
| E6 | 0.005 | 1.000 | 0.011 | 1.000 | 0.0 |

These values are honest and imperfect; they reflect the baseline architecture rather than tuned results.

## Configuration Reference

The project reads settings from [config.yaml](config.yaml). Key sections include:

- simulation: seed, hours, Hz, train/test split, data directory
- scenarios: enabled scenario names and injection windows
- telemetry: min/max ranges for each simulated measurement
- commands: rate, valid sources, command types, threshold
- network: nominal rate and spike multiplier
- system: auth failure rate
- rules: hard limits and R1/R2 thresholds
- model: Isolation Forest config
- ui: dark-mode SOC palette values

## Project Structure

```text
tekclipse/
├── __init__.py
├── config.py
├── data/
│   ├── generator.py
│   └── injection.py
├── dashboard/
│   └── app.py
├── evaluation/
│   ├── metrics.py
│   └── runner.py
├── pipeline/
│   ├── alerts.py
│   ├── features.py
│   ├── model.py
│   ├── preprocess.py
│   └── rules.py
├── storage/
│   └── db.py
└── data/generated/
```

## Limitations

- Synthetic data only; not derived from flight hardware or production telemetry
- Limited scenario set compared to real mission systems
- No hardware-in-the-loop validation or operator decision loop
- Baseline anomaly detector is intentionally simple and not optimized for real-world deployment

## Phase 3 Roadmap

- integrate richer attack models and realistic mission contexts
- add operator feedback and human-in-the-loop triage
- expand timeline and network feature sets
- add confidence scoring and explainable alerts
- use real telemetry ingestion and model validation pipelines

## Team and Institution

TekClipse — TEK-UP University, Tunis (IEEE TEK-UP Student Branch)

IASTAM 6.0 Technical Challenge 2026 — Track 5 Cybersecurity
