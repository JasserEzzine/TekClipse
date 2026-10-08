# Measured independent-run results

Aggregated within each case across independent seeds. Different scenarios reuse nominal sessions: do not treat their pooled seconds as independent trials. Blank/undefined ratios have no denominator. Episodes are contiguous false-positive seconds, not raw alert rows.

| Case | Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP seconds/h | False episodes/h | Event recall | Event delay s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E1 | Rules only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | ML original | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| E1 | ML calibrated | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| E1 | Network only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | System only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | Original hybrid | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| E1 | Full-day uncalibrated hybrid | 0 | 4145 | 82255 | 0 | 0 | undefined | 0 | 0.0479745 | 172.708 | 24.2083 | undefined | undefined |
| E1 | Improved hybrid | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| E1 | Without ML | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | Without network | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| E1 | Without rules | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| E2 | Rules only | 1 | 0 | 86399 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E2 | ML original | 0 | 4550 | 81849 | 1 | 0 | 0 | 0 | 0.0526626 | 189.583 | 27.5833 | 0 | undefined |
| E2 | ML calibrated | 0 | 2348 | 84051 | 1 | 0 | 0 | 0 | 0.0271762 | 97.8333 | 16.125 | 0 | undefined |
| E2 | Network only | 0 | 0 | 86399 | 1 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E2 | System only | 0 | 0 | 86399 | 1 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E2 | Original hybrid | 1 | 4550 | 81849 | 0 | 0.000219732 | 1 | 0.000439367 | 0.0526626 | 189.583 | 27.5833 | 1 | 0 |
| E2 | Full-day uncalibrated hybrid | 1 | 4145 | 82254 | 0 | 0.000241196 | 1 | 0.000482276 | 0.0479751 | 172.708 | 24.2083 | 1 | 0 |
| E2 | Improved hybrid | 1 | 2348 | 84051 | 0 | 0.000425713 | 1 | 0.000851064 | 0.0271762 | 97.8333 | 16.125 | 1 | 0 |
| E2 | Without ML | 1 | 0 | 86399 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E2 | Without network | 1 | 2348 | 84051 | 0 | 0.000425713 | 1 | 0.000851064 | 0.0271762 | 97.8333 | 16.125 | 1 | 0 |
| E2 | Without rules | 0 | 2348 | 84051 | 1 | 0 | 0 | 0 | 0.0271762 | 97.8333 | 16.125 | 0 | undefined |
| E3 | Rules only | 1 | 0 | 86341 | 58 | 1 | 0.0169492 | 0.0333333 | 0 | 0 | 0 | 1 | 18 |
| E3 | ML original | 0 | 4550 | 81791 | 59 | 0 | 0 | 0 | 0.052698 | 189.583 | 27.5833 | 0 | undefined |
| E3 | ML calibrated | 0 | 2348 | 83993 | 59 | 0 | 0 | 0 | 0.0271945 | 97.8333 | 16.125 | 0 | undefined |
| E3 | Network only | 0 | 0 | 86341 | 59 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E3 | System only | 0 | 0 | 86341 | 59 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E3 | Original hybrid | 1 | 4550 | 81791 | 58 | 0.000219732 | 0.0169492 | 0.000433839 | 0.052698 | 189.583 | 27.5833 | 1 | 18 |
| E3 | Full-day uncalibrated hybrid | 1 | 4145 | 82196 | 58 | 0.000241196 | 0.0169492 | 0.000475624 | 0.0480073 | 172.708 | 24.2083 | 1 | 18 |
| E3 | Improved hybrid | 1 | 2348 | 83993 | 58 | 0.000425713 | 0.0169492 | 0.000830565 | 0.0271945 | 97.8333 | 16.125 | 1 | 18 |
| E3 | Without ML | 1 | 0 | 86341 | 58 | 1 | 0.0169492 | 0.0333333 | 0 | 0 | 0 | 1 | 18 |
| E3 | Without network | 1 | 2348 | 83993 | 58 | 0.000425713 | 0.0169492 | 0.000830565 | 0.0271945 | 97.8333 | 16.125 | 1 | 18 |
| E3 | Without rules | 0 | 2348 | 83993 | 59 | 0 | 0 | 0 | 0.0271945 | 97.8333 | 16.125 | 0 | undefined |
| E4 | Rules only | 0 | 0 | 86280 | 120 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E4 | ML original | 0 | 4550 | 81730 | 120 | 0 | 0 | 0 | 0.0527353 | 189.583 | 27.5833 | 0 | undefined |
| E4 | ML calibrated | 0 | 2348 | 83932 | 120 | 0 | 0 | 0 | 0.0272137 | 97.8333 | 16.125 | 0 | undefined |
| E4 | Network only | 120 | 0 | 86280 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E4 | System only | 0 | 0 | 86280 | 120 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E4 | Original hybrid | 120 | 4550 | 81730 | 0 | 0.0256959 | 1 | 0.0501044 | 0.0527353 | 189.583 | 27.5833 | 1 | 0 |
| E4 | Full-day uncalibrated hybrid | 120 | 4145 | 82135 | 0 | 0.028136 | 1 | 0.054732 | 0.0480413 | 172.708 | 24.2083 | 1 | 0 |
| E4 | Improved hybrid | 120 | 2348 | 83932 | 0 | 0.0486224 | 1 | 0.0927357 | 0.0272137 | 97.8333 | 16.125 | 1 | 0 |
| E4 | Without ML | 120 | 0 | 86280 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E4 | Without network | 0 | 2348 | 83932 | 120 | 0 | 0 | 0 | 0.0272137 | 97.8333 | 16.125 | 0 | undefined |
| E4 | Without rules | 120 | 2348 | 83932 | 0 | 0.0486224 | 1 | 0.0927357 | 0.0272137 | 97.8333 | 16.125 | 1 | 0 |
| E5 | Rules only | 181 | 0 | 86219 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E5 | ML original | 27 | 4550 | 81669 | 154 | 0.00589906 | 0.149171 | 0.0113493 | 0.0527726 | 189.583 | 27.5833 | 1 | 22 |
| E5 | ML calibrated | 3 | 2348 | 83871 | 178 | 0.00127605 | 0.0165746 | 0.00236967 | 0.027233 | 97.8333 | 16.125 | 1 | 23 |
| E5 | Network only | 0 | 0 | 86219 | 181 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E5 | System only | 0 | 0 | 86219 | 181 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E5 | Original hybrid | 181 | 4550 | 81669 | 0 | 0.0382583 | 1 | 0.0736971 | 0.0527726 | 189.583 | 27.5833 | 1 | 0 |
| E5 | Full-day uncalibrated hybrid | 181 | 4145 | 82074 | 0 | 0.04184 | 1 | 0.0803195 | 0.0480753 | 172.708 | 24.2083 | 1 | 0 |
| E5 | Improved hybrid | 181 | 2348 | 83871 | 0 | 0.0715698 | 1 | 0.133579 | 0.027233 | 97.8333 | 16.125 | 1 | 0 |
| E5 | Without ML | 181 | 0 | 86219 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E5 | Without network | 181 | 2348 | 83871 | 0 | 0.0715698 | 1 | 0.133579 | 0.027233 | 97.8333 | 16.125 | 1 | 0 |
| E5 | Without rules | 3 | 2348 | 83871 | 178 | 0.00127605 | 0.0165746 | 0.00236967 | 0.027233 | 97.8333 | 16.125 | 1 | 23 |
| E6 | Rules only | 181 | 0 | 86219 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0.666667 | 0 |
| E6 | ML original | 27 | 4550 | 81669 | 154 | 0.00589906 | 0.149171 | 0.0113493 | 0.0527726 | 189.583 | 27.5833 | 0.333333 | 22 |
| E6 | ML calibrated | 3 | 2348 | 83871 | 178 | 0.00127605 | 0.0165746 | 0.00236967 | 0.027233 | 97.8333 | 16.125 | 0.333333 | 23 |
| E6 | Network only | 120 | 0 | 86219 | 61 | 1 | 0.662983 | 0.797342 | 0 | 0 | 0 | 0.333333 | 0 |
| E6 | System only | 0 | 0 | 86219 | 181 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E6 | Original hybrid | 181 | 4550 | 81669 | 0 | 0.0382583 | 1 | 0.0736971 | 0.0527726 | 189.583 | 27.5833 | 1 | 0 |
| E6 | Full-day uncalibrated hybrid | 181 | 4145 | 82074 | 0 | 0.04184 | 1 | 0.0803195 | 0.0480753 | 172.708 | 24.2083 | 1 | 0 |
| E6 | Improved hybrid | 181 | 2348 | 83871 | 0 | 0.0715698 | 1 | 0.133579 | 0.027233 | 97.8333 | 16.125 | 1 | 0 |
| E6 | Without ML | 181 | 0 | 86219 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E6 | Without network | 181 | 2348 | 83871 | 0 | 0.0715698 | 1 | 0.133579 | 0.027233 | 97.8333 | 16.125 | 0.666667 | 0 |
| E6 | Without rules | 120 | 2348 | 83871 | 61 | 0.0486224 | 0.662983 | 0.0906002 | 0.027233 | 97.8333 | 16.125 | 0.666667 | 11.5 |
| E7 | Rules only | 63 | 0 | 86283 | 54 | 1 | 0.538462 | 0.7 | 0 | 0 | 0 | 0.5 | 3.33333 |
| E7 | ML original | 36 | 4550 | 81733 | 81 | 0.00784998 | 0.307692 | 0.0153094 | 0.0527334 | 189.583 | 27.5833 | 0.166667 | 9 |
| E7 | ML calibrated | 53 | 2348 | 83935 | 64 | 0.0220741 | 0.452991 | 0.0420969 | 0.0272128 | 97.8333 | 16.125 | 0.166667 | 7 |
| E7 | Network only | 116 | 0 | 86283 | 1 | 1 | 0.991453 | 0.995708 | 0 | 0 | 0 | 0.166667 | 0 |
| E7 | System only | 2 | 0 | 86283 | 115 | 1 | 0.017094 | 0.0336134 | 0 | 0 | 0 | 0.333333 | 0 |
| E7 | Original hybrid | 117 | 4550 | 81733 | 0 | 0.0250696 | 1 | 0.048913 | 0.0527334 | 189.583 | 27.5833 | 1 | 1.66667 |
| E7 | Full-day uncalibrated hybrid | 117 | 4145 | 82138 | 0 | 0.0274519 | 1 | 0.0534369 | 0.0480396 | 172.708 | 24.2083 | 1 | 1.66667 |
| E7 | Improved hybrid | 117 | 2348 | 83935 | 0 | 0.0474645 | 1 | 0.0906274 | 0.0272128 | 97.8333 | 16.125 | 1 | 1.66667 |
| E7 | Without ML | 117 | 0 | 86283 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1.66667 |
| E7 | Without network | 63 | 2348 | 83935 | 54 | 0.0261302 | 0.538462 | 0.0498418 | 0.0272128 | 97.8333 | 16.125 | 0.833333 | 2 |
| E7 | Without rules | 116 | 2348 | 83935 | 1 | 0.0470779 | 0.991453 | 0.0898876 | 0.0272128 | 97.8333 | 16.125 | 0.666667 | 1.75 |
| benign_command_burst | Rules only | 0 | 1 | 86399 | 0 | 0 | undefined | 0 | 1.15741e-05 | 0.0416667 | 0.0416667 | undefined | undefined |
| benign_command_burst | ML original | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| benign_command_burst | ML calibrated | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_command_burst | Network only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_command_burst | System only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_command_burst | Original hybrid | 0 | 4551 | 81849 | 0 | 0 | undefined | 0 | 0.0526736 | 189.625 | 27.625 | undefined | undefined |
| benign_command_burst | Full-day uncalibrated hybrid | 0 | 4146 | 82254 | 0 | 0 | undefined | 0 | 0.0479861 | 172.75 | 24.25 | undefined | undefined |
| benign_command_burst | Improved hybrid | 0 | 2349 | 84051 | 0 | 0 | undefined | 0 | 0.0271875 | 97.875 | 16.1667 | undefined | undefined |
| benign_command_burst | Without ML | 0 | 1 | 86399 | 0 | 0 | undefined | 0 | 1.15741e-05 | 0.0416667 | 0.0416667 | undefined | undefined |
| benign_command_burst | Without network | 0 | 2349 | 84051 | 0 | 0 | undefined | 0 | 0.0271875 | 97.875 | 16.1667 | undefined | undefined |
| benign_command_burst | Without rules | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_authorized_peer | Rules only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_authorized_peer | ML original | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| benign_authorized_peer | ML calibrated | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_authorized_peer | Network only | 0 | 90 | 86310 | 0 | 0 | undefined | 0 | 0.00104167 | 3.75 | 0.0416667 | undefined | undefined |
| benign_authorized_peer | System only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_authorized_peer | Original hybrid | 0 | 4640 | 81760 | 0 | 0 | undefined | 0 | 0.0537037 | 193.333 | 27.625 | undefined | undefined |
| benign_authorized_peer | Full-day uncalibrated hybrid | 0 | 4235 | 82165 | 0 | 0 | undefined | 0 | 0.0490162 | 176.458 | 24.25 | undefined | undefined |
| benign_authorized_peer | Improved hybrid | 0 | 2438 | 83962 | 0 | 0 | undefined | 0 | 0.0282176 | 101.583 | 16.1667 | undefined | undefined |
| benign_authorized_peer | Without ML | 0 | 90 | 86310 | 0 | 0 | undefined | 0 | 0.00104167 | 3.75 | 0.0416667 | undefined | undefined |
| benign_authorized_peer | Without network | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_authorized_peer | Without rules | 0 | 2438 | 83962 | 0 | 0 | undefined | 0 | 0.0282176 | 101.583 | 16.1667 | undefined | undefined |
| benign_load | Rules only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | ML original | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| benign_load | ML calibrated | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_load | Network only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | System only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | Original hybrid | 0 | 4550 | 81850 | 0 | 0 | undefined | 0 | 0.052662 | 189.583 | 27.5833 | undefined | undefined |
| benign_load | Full-day uncalibrated hybrid | 0 | 4145 | 82255 | 0 | 0 | undefined | 0 | 0.0479745 | 172.708 | 24.2083 | undefined | undefined |
| benign_load | Improved hybrid | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_load | Without ML | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | Without network | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_load | Without rules | 0 | 2348 | 84052 | 0 | 0 | undefined | 0 | 0.0271759 | 97.8333 | 16.125 | undefined | undefined |
| benign_telemetry | Rules only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | ML original | 0 | 8624 | 77776 | 0 | 0 | undefined | 0 | 0.0998148 | 359.333 | 14.625 | undefined | undefined |
| benign_telemetry | ML calibrated | 0 | 7960 | 78440 | 0 | 0 | undefined | 0 | 0.0921296 | 331.667 | 15.7917 | undefined | undefined |
| benign_telemetry | Network only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | System only | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | Original hybrid | 0 | 8624 | 77776 | 0 | 0 | undefined | 0 | 0.0998148 | 359.333 | 14.625 | undefined | undefined |
| benign_telemetry | Full-day uncalibrated hybrid | 0 | 9258 | 77142 | 0 | 0 | undefined | 0 | 0.107153 | 385.75 | 17.25 | undefined | undefined |
| benign_telemetry | Improved hybrid | 0 | 7960 | 78440 | 0 | 0 | undefined | 0 | 0.0921296 | 331.667 | 15.7917 | undefined | undefined |
| benign_telemetry | Without ML | 0 | 0 | 86400 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | Without network | 0 | 7960 | 78440 | 0 | 0 | undefined | 0 | 0.0921296 | 331.667 | 15.7917 | undefined | undefined |
| benign_telemetry | Without rules | 0 | 7960 | 78440 | 0 | 0 | undefined | 0 | 0.0921296 | 331.667 | 15.7917 | undefined | undefined |
| attack_primary_unauthorized | Rules only | 1 | 0 | 86399 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_primary_unauthorized | ML original | 0 | 4550 | 81849 | 1 | 0 | 0 | 0 | 0.0526626 | 189.583 | 27.5833 | 0 | undefined |
| attack_primary_unauthorized | ML calibrated | 0 | 2348 | 84051 | 1 | 0 | 0 | 0 | 0.0271762 | 97.8333 | 16.125 | 0 | undefined |
| attack_primary_unauthorized | Network only | 0 | 0 | 86399 | 1 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_primary_unauthorized | System only | 0 | 0 | 86399 | 1 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_primary_unauthorized | Original hybrid | 0 | 4550 | 81849 | 1 | 0 | 0 | 0 | 0.0526626 | 189.583 | 27.5833 | 0 | undefined |
| attack_primary_unauthorized | Full-day uncalibrated hybrid | 1 | 4145 | 82254 | 0 | 0.000241196 | 1 | 0.000482276 | 0.0479751 | 172.708 | 24.2083 | 1 | 0 |
| attack_primary_unauthorized | Improved hybrid | 1 | 2348 | 84051 | 0 | 0.000425713 | 1 | 0.000851064 | 0.0271762 | 97.8333 | 16.125 | 1 | 0 |
| attack_primary_unauthorized | Without ML | 1 | 0 | 86399 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_primary_unauthorized | Without network | 1 | 2348 | 84051 | 0 | 0.000425713 | 1 | 0.000851064 | 0.0271762 | 97.8333 | 16.125 | 1 | 0 |
| attack_primary_unauthorized | Without rules | 0 | 2348 | 84051 | 1 | 0 | 0 | 0 | 0.0271762 | 97.8333 | 16.125 | 0 | undefined |
| attack_boundary_flood | Rules only | 0 | 0 | 86388 | 12 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | ML original | 0 | 4550 | 81838 | 12 | 0 | 0 | 0 | 0.0526694 | 189.583 | 27.5833 | 0 | undefined |
| attack_boundary_flood | ML calibrated | 0 | 2348 | 84040 | 12 | 0 | 0 | 0 | 0.0271797 | 97.8333 | 16.125 | 0 | undefined |
| attack_boundary_flood | Network only | 0 | 0 | 86388 | 12 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | System only | 0 | 0 | 86388 | 12 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | Original hybrid | 0 | 4550 | 81838 | 12 | 0 | 0 | 0 | 0.0526694 | 189.583 | 27.5833 | 0 | undefined |
| attack_boundary_flood | Full-day uncalibrated hybrid | 0 | 4145 | 82243 | 12 | 0 | 0 | 0 | 0.0479812 | 172.708 | 24.2083 | 0 | undefined |
| attack_boundary_flood | Improved hybrid | 0 | 2348 | 84040 | 12 | 0 | 0 | 0 | 0.0271797 | 97.8333 | 16.125 | 0 | undefined |
| attack_boundary_flood | Without ML | 0 | 0 | 86388 | 12 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | Without network | 0 | 2348 | 84040 | 12 | 0 | 0 | 0 | 0.0271797 | 97.8333 | 16.125 | 0 | undefined |
| attack_boundary_flood | Without rules | 0 | 2348 | 84040 | 12 | 0 | 0 | 0 | 0.0271797 | 97.8333 | 16.125 | 0 | undefined |
| attack_low_network | Rules only | 0 | 0 | 86310 | 90 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_low_network | ML original | 0 | 4550 | 81760 | 90 | 0 | 0 | 0 | 0.052717 | 189.583 | 27.5833 | 0 | undefined |
| attack_low_network | ML calibrated | 0 | 2348 | 83962 | 90 | 0 | 0 | 0 | 0.0272043 | 97.8333 | 16.125 | 0 | undefined |
| attack_low_network | Network only | 1 | 0 | 86310 | 89 | 1 | 0.0111111 | 0.021978 | 0 | 0 | 0 | 1 | 0 |
| attack_low_network | System only | 0 | 0 | 86310 | 90 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_low_network | Original hybrid | 1 | 4550 | 81760 | 89 | 0.000219732 | 0.0111111 | 0.000430942 | 0.052717 | 189.583 | 27.5833 | 1 | 0 |
| attack_low_network | Full-day uncalibrated hybrid | 1 | 4145 | 82165 | 89 | 0.000241196 | 0.0111111 | 0.000472144 | 0.0480246 | 172.708 | 24.2083 | 1 | 0 |
| attack_low_network | Improved hybrid | 1 | 2348 | 83962 | 89 | 0.000425713 | 0.0111111 | 0.000820008 | 0.0272043 | 97.8333 | 16.125 | 1 | 0 |
| attack_low_network | Without ML | 1 | 0 | 86310 | 89 | 1 | 0.0111111 | 0.021978 | 0 | 0 | 0 | 1 | 0 |
| attack_low_network | Without network | 0 | 2348 | 83962 | 90 | 0 | 0 | 0 | 0.0272043 | 97.8333 | 16.125 | 0 | undefined |
| attack_low_network | Without rules | 1 | 2348 | 83962 | 89 | 0.000425713 | 0.0111111 | 0.000820008 | 0.0272043 | 97.8333 | 16.125 | 1 | 0 |
| attack_short_thermal | Rules only | 15 | 0 | 86385 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_short_thermal | ML original | 7 | 4552 | 81833 | 8 | 0.00153542 | 0.466667 | 0.00306078 | 0.0526943 | 189.667 | 27.625 | 1 | 4 |
| attack_short_thermal | ML calibrated | 0 | 2348 | 84037 | 15 | 0 | 0 | 0 | 0.0271806 | 97.8333 | 16.125 | 0 | undefined |
| attack_short_thermal | Network only | 0 | 0 | 86385 | 15 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_short_thermal | System only | 0 | 0 | 86385 | 15 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_short_thermal | Original hybrid | 15 | 4552 | 81833 | 0 | 0.00328443 | 1 | 0.00654736 | 0.0526943 | 189.667 | 27.625 | 1 | 0 |
| attack_short_thermal | Full-day uncalibrated hybrid | 15 | 4145 | 82240 | 0 | 0.00360577 | 1 | 0.00718563 | 0.0479829 | 172.708 | 24.2083 | 1 | 0 |
| attack_short_thermal | Improved hybrid | 15 | 2348 | 84037 | 0 | 0.00634786 | 1 | 0.0126156 | 0.0271806 | 97.8333 | 16.125 | 1 | 0 |
| attack_short_thermal | Without ML | 15 | 0 | 86385 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_short_thermal | Without network | 15 | 2348 | 84037 | 0 | 0.00634786 | 1 | 0.0126156 | 0.0271806 | 97.8333 | 16.125 | 1 | 0 |
| attack_short_thermal | Without rules | 0 | 2348 | 84037 | 15 | 0 | 0 | 0 | 0.0271806 | 97.8333 | 16.125 | 0 | undefined |
| attack_reordered | Rules only | 16 | 0 | 86295 | 89 | 1 | 0.152381 | 0.264463 | 0 | 0 | 0 | 0.666667 | 0 |
| attack_reordered | ML original | 7 | 4552 | 81743 | 98 | 0.00153542 | 0.0666667 | 0.00300172 | 0.0527493 | 189.667 | 27.625 | 0.333333 | 4 |
| attack_reordered | ML calibrated | 0 | 2348 | 83947 | 105 | 0 | 0 | 0 | 0.027209 | 97.8333 | 16.125 | 0 | undefined |
| attack_reordered | Network only | 90 | 0 | 86295 | 15 | 1 | 0.857143 | 0.923077 | 0 | 0 | 0 | 0.333333 | 0 |
| attack_reordered | System only | 0 | 0 | 86295 | 105 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_reordered | Original hybrid | 105 | 4552 | 81743 | 0 | 0.0225467 | 1 | 0.0440991 | 0.0527493 | 189.667 | 27.625 | 0.666667 | 0 |
| attack_reordered | Full-day uncalibrated hybrid | 105 | 4145 | 82150 | 0 | 0.0247059 | 1 | 0.0482204 | 0.0480329 | 172.708 | 24.2083 | 1 | 0 |
| attack_reordered | Improved hybrid | 105 | 2348 | 83947 | 0 | 0.0428047 | 1 | 0.0820954 | 0.027209 | 97.8333 | 16.125 | 1 | 0 |
| attack_reordered | Without ML | 105 | 0 | 86295 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_reordered | Without network | 16 | 2348 | 83947 | 89 | 0.00676819 | 0.152381 | 0.0129607 | 0.027209 | 97.8333 | 16.125 | 0.666667 | 0 |
| attack_reordered | Without rules | 90 | 2348 | 83947 | 15 | 0.0369155 | 0.857143 | 0.0707825 | 0.027209 | 97.8333 | 16.125 | 0.333333 | 0 |
