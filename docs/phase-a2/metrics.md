# Full pooled before/after measurements

Each row pools three independent 24-hour runs (259,200 seconds). Rates use 72 simulated hours. Confusion counts classify seconds; events require the matching detector family inside the exact event interval. A dash means an undefined denominator or no detected event. Delays average detected events only. Full component and ablation rows are in [aggregate-metrics.csv](aggregate-metrics.csv); individual seeds are in [results/metrics.csv](results/metrics.csv).

| Cohort / case | Profile | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP s/h | Episodes/h | Events | Event recall | Delay s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| regression 301-303 / E1 | Phase A hybrid | 0 | 7249 | 251951 | 0 | 0.0000 | - | 0.0000 | 0.0280 | 100.6806 | 18.1806 | 0/0 | - | - |
| regression 301-303 / E1 | Phase A.2 hybrid | 0 | 2732 | 256468 | 0 | 0.0000 | - | 0.0000 | 0.0105 | 37.9444 | 7.5000 | 0/0 | - | - |
| regression 301-303 / E2 | Phase A hybrid | 3 | 7249 | 251948 | 0 | 0.0004 | 1.0000 | 0.0008 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E2 | Phase A.2 hybrid | 3 | 2732 | 256465 | 0 | 0.0011 | 1.0000 | 0.0022 | 0.0105 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E3 | Phase A hybrid | 3 | 7249 | 251774 | 174 | 0.0004 | 0.0169 | 0.0008 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 18.0000 |
| regression 301-303 / E3 | Phase A.2 hybrid | 3 | 2732 | 256291 | 174 | 0.0011 | 0.0169 | 0.0021 | 0.0105 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 18.0000 |
| regression 301-303 / E4 | Phase A hybrid | 360 | 7249 | 251591 | 0 | 0.0473 | 1.0000 | 0.0904 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E4 | Phase A.2 hybrid | 360 | 2732 | 256108 | 0 | 0.1164 | 1.0000 | 0.2086 | 0.0106 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E5 | Phase A hybrid | 543 | 7249 | 251408 | 0 | 0.0697 | 1.0000 | 0.1303 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E5 | Phase A.2 hybrid | 543 | 2732 | 255925 | 0 | 0.1658 | 1.0000 | 0.2844 | 0.0106 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / E6 | Phase A hybrid | 543 | 7249 | 251408 | 0 | 0.0697 | 1.0000 | 0.1303 | 0.0280 | 100.6806 | 18.1806 | 9/9 | 1.0000 | 0.0000 |
| regression 301-303 / E6 | Phase A.2 hybrid | 543 | 2732 | 255925 | 0 | 0.1658 | 1.0000 | 0.2844 | 0.0106 | 37.9444 | 7.5000 | 9/9 | 1.0000 | 0.0000 |
| regression 301-303 / E7 | Phase A hybrid | 351 | 7254 | 251595 | 0 | 0.0462 | 1.0000 | 0.0882 | 0.0280 | 100.7500 | 18.2361 | 18/18 | 1.0000 | 1.6667 |
| regression 301-303 / E7 | Phase A.2 hybrid | 351 | 2732 | 256117 | 0 | 0.1139 | 1.0000 | 0.2044 | 0.0106 | 37.9444 | 7.5000 | 18/18 | 1.0000 | 1.6667 |
| regression 301-303 / benign_command_burst | Phase A hybrid | 0 | 7252 | 251948 | 0 | 0.0000 | - | 0.0000 | 0.0280 | 100.7222 | 18.2222 | 0/0 | - | - |
| regression 301-303 / benign_command_burst | Phase A.2 hybrid | 0 | 2735 | 256465 | 0 | 0.0000 | - | 0.0000 | 0.0106 | 37.9861 | 7.5417 | 0/0 | - | - |
| regression 301-303 / benign_authorized_peer | Phase A hybrid | 0 | 7519 | 251681 | 0 | 0.0000 | - | 0.0000 | 0.0290 | 104.4306 | 18.2222 | 0/0 | - | - |
| regression 301-303 / benign_authorized_peer | Phase A.2 hybrid | 0 | 2732 | 256468 | 0 | 0.0000 | - | 0.0000 | 0.0105 | 37.9444 | 7.5000 | 0/0 | - | - |
| regression 301-303 / benign_load | Phase A hybrid | 0 | 7249 | 251951 | 0 | 0.0000 | - | 0.0000 | 0.0280 | 100.6806 | 18.1806 | 0/0 | - | - |
| regression 301-303 / benign_load | Phase A.2 hybrid | 0 | 2732 | 256468 | 0 | 0.0000 | - | 0.0000 | 0.0105 | 37.9444 | 7.5000 | 0/0 | - | - |
| regression 301-303 / benign_telemetry | Phase A hybrid | 0 | 24159 | 235041 | 0 | 0.0000 | - | 0.0000 | 0.0932 | 335.5417 | 17.6944 | 0/0 | - | - |
| regression 301-303 / benign_telemetry | Phase A.2 hybrid | 0 | 6148 | 253052 | 0 | 0.0000 | - | 0.0000 | 0.0237 | 85.3889 | 14.2917 | 0/0 | - | - |
| regression 301-303 / attack_primary_unauthorized | Phase A hybrid | 3 | 7249 | 251948 | 0 | 0.0004 | 1.0000 | 0.0008 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_primary_unauthorized | Phase A.2 hybrid | 3 | 2732 | 256465 | 0 | 0.0011 | 1.0000 | 0.0022 | 0.0105 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_boundary_flood | Phase A hybrid | 0 | 7249 | 251915 | 36 | 0.0000 | 0.0000 | 0.0000 | 0.0280 | 100.6806 | 18.1806 | 0/3 | 0.0000 | - |
| regression 301-303 / attack_boundary_flood | Phase A.2 hybrid | 3 | 2732 | 256432 | 33 | 0.0011 | 0.0833 | 0.0022 | 0.0105 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 10.0000 |
| regression 301-303 / attack_low_network | Phase A hybrid | 3 | 7249 | 251681 | 267 | 0.0004 | 0.0111 | 0.0008 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_low_network | Phase A.2 hybrid | 3 | 2732 | 256198 | 267 | 0.0011 | 0.0111 | 0.0020 | 0.0106 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_short_thermal | Phase A hybrid | 45 | 7249 | 251906 | 0 | 0.0062 | 1.0000 | 0.0123 | 0.0280 | 100.6806 | 18.1806 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_short_thermal | Phase A.2 hybrid | 45 | 2732 | 256423 | 0 | 0.0162 | 1.0000 | 0.0319 | 0.0105 | 37.9444 | 7.5000 | 3/3 | 1.0000 | 0.0000 |
| regression 301-303 / attack_reordered | Phase A hybrid | 315 | 7249 | 251636 | 0 | 0.0416 | 1.0000 | 0.0800 | 0.0280 | 100.6806 | 18.1806 | 9/9 | 1.0000 | 0.0000 |
| regression 301-303 / attack_reordered | Phase A.2 hybrid | 315 | 2732 | 256153 | 0 | 0.1034 | 1.0000 | 0.1874 | 0.0106 | 37.9444 | 7.5000 | 9/9 | 1.0000 | 0.0000 |
| independent 601-603 / E1 | Phase A hybrid | 0 | 7398 | 251802 | 0 | 0.0000 | - | 0.0000 | 0.0285 | 102.7500 | 17.4722 | 0/0 | - | - |
| independent 601-603 / E1 | Phase A.2 hybrid | 0 | 2712 | 256488 | 0 | 0.0000 | - | 0.0000 | 0.0105 | 37.6667 | 7.6944 | 0/0 | - | - |
| independent 601-603 / E7 | Phase A hybrid | 351 | 7398 | 251451 | 0 | 0.0453 | 1.0000 | 0.0867 | 0.0286 | 102.7500 | 17.4722 | 18/18 | 1.0000 | 1.6667 |
| independent 601-603 / E7 | Phase A.2 hybrid | 351 | 2712 | 256137 | 0 | 0.1146 | 1.0000 | 0.2056 | 0.0105 | 37.6667 | 7.6944 | 18/18 | 1.0000 | 1.6667 |
| independent 601-603 / nominal_thermal_regime | Phase A hybrid | 0 | 9690 | 249510 | 0 | 0.0000 | - | 0.0000 | 0.0374 | 134.5833 | 17.7361 | 0/0 | - | - |
| independent 601-603 / nominal_thermal_regime | Phase A.2 hybrid | 0 | 4029 | 255171 | 0 | 0.0000 | - | 0.0000 | 0.0155 | 55.9583 | 11.0139 | 0/0 | - | - |
| independent 601-603 / nominal_power_regime | Phase A hybrid | 0 | 10976 | 248224 | 0 | 0.0000 | - | 0.0000 | 0.0423 | 152.4444 | 20.5833 | 0/0 | - | - |
| independent 601-603 / nominal_power_regime | Phase A.2 hybrid | 0 | 3875 | 255325 | 0 | 0.0000 | - | 0.0000 | 0.0149 | 53.8194 | 11.0694 | 0/0 | - | - |
| independent 601-603 / operational_thermal_drift | Phase A hybrid | 1 | 7397 | 250003 | 1799 | 0.0001 | 0.0006 | 0.0002 | 0.0287 | 102.7361 | 17.4583 | 1/3 | 0.3333 | 3.0000 |
| independent 601-603 / operational_thermal_drift | Phase A.2 hybrid | 0 | 2712 | 254688 | 1800 | 0.0000 | 0.0000 | 0.0000 | 0.0105 | 37.6667 | 7.6944 | 0/3 | 0.0000 | - |
| independent 601-603 / operational_power_relationship | Phase A hybrid | 29 | 7397 | 250003 | 1771 | 0.0039 | 0.0161 | 0.0063 | 0.0287 | 102.7361 | 17.4583 | 3/3 | 1.0000 | 0.3333 |
| independent 601-603 / operational_power_relationship | Phase A.2 hybrid | 12 | 2712 | 254688 | 1788 | 0.0044 | 0.0067 | 0.0053 | 0.0105 | 37.6667 | 7.6944 | 2/3 | 0.6667 | 5.0000 |
| independent 601-603 / operational_voltage_relationship | Phase A hybrid | 24 | 7397 | 250003 | 1776 | 0.0032 | 0.0133 | 0.0052 | 0.0287 | 102.7361 | 17.4583 | 3/3 | 1.0000 | 1.3333 |
| independent 601-603 / operational_voltage_relationship | Phase A.2 hybrid | 10 | 2712 | 254688 | 1790 | 0.0037 | 0.0056 | 0.0044 | 0.0105 | 37.6667 | 7.6944 | 1/3 | 0.3333 | 1.0000 |
