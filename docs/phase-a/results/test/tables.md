# Measured independent-run results

Aggregated within each case across independent seeds. Different scenarios reuse nominal sessions: do not treat their pooled seconds as independent trials. Blank/undefined ratios have no denominator. Episodes are contiguous false-positive seconds, not raw alert rows.

| Case | Method | TP | FP | TN | FN | Precision | Recall | F1 | FPR | FP seconds/h | False episodes/h | Event recall | Event delay s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E1 | Rules only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | ML original | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| E1 | ML calibrated | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| E1 | Network only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | System only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | Original hybrid | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| E1 | Full-day uncalibrated hybrid | 0 | 12829 | 246371 | 0 | 0 | undefined | 0 | 0.0494946 | 178.181 | 23.6528 | undefined | undefined |
| E1 | Improved hybrid | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| E1 | Without ML | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| E1 | Without network | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| E1 | Without rules | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| E2 | Rules only | 3 | 0 | 259197 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E2 | ML original | 0 | 14128 | 245069 | 3 | 0 | 0 | 0 | 0.0545068 | 196.222 | 27.8056 | 0 | undefined |
| E2 | ML calibrated | 0 | 7249 | 251948 | 3 | 0 | 0 | 0 | 0.0279671 | 100.681 | 18.1806 | 0 | undefined |
| E2 | Network only | 0 | 0 | 259197 | 3 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E2 | System only | 0 | 0 | 259197 | 3 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E2 | Original hybrid | 3 | 14128 | 245069 | 0 | 0.000212299 | 1 | 0.000424508 | 0.0545068 | 196.222 | 27.8056 | 1 | 0 |
| E2 | Full-day uncalibrated hybrid | 3 | 12829 | 246368 | 0 | 0.000233791 | 1 | 0.000467472 | 0.0494952 | 178.181 | 23.6528 | 1 | 0 |
| E2 | Improved hybrid | 3 | 7249 | 251948 | 0 | 0.000413679 | 1 | 0.000827016 | 0.0279671 | 100.681 | 18.1806 | 1 | 0 |
| E2 | Without ML | 3 | 0 | 259197 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E2 | Without network | 3 | 7249 | 251948 | 0 | 0.000413679 | 1 | 0.000827016 | 0.0279671 | 100.681 | 18.1806 | 1 | 0 |
| E2 | Without rules | 0 | 7249 | 251948 | 3 | 0 | 0 | 0 | 0.0279671 | 100.681 | 18.1806 | 0 | undefined |
| E3 | Rules only | 3 | 0 | 259023 | 174 | 1 | 0.0169492 | 0.0333333 | 0 | 0 | 0 | 1 | 18 |
| E3 | ML original | 5 | 14123 | 244900 | 172 | 0.000353907 | 0.0282486 | 0.000699056 | 0.0545241 | 196.153 | 27.75 | 0 | undefined |
| E3 | ML calibrated | 0 | 7249 | 251774 | 177 | 0 | 0 | 0 | 0.0279859 | 100.681 | 18.1806 | 0 | undefined |
| E3 | Network only | 0 | 0 | 259023 | 177 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E3 | System only | 0 | 0 | 259023 | 177 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E3 | Original hybrid | 8 | 14123 | 244900 | 169 | 0.000566131 | 0.0451977 | 0.00111826 | 0.0545241 | 196.153 | 27.75 | 1 | 18 |
| E3 | Full-day uncalibrated hybrid | 3 | 12829 | 246194 | 174 | 0.000233791 | 0.0169492 | 0.000461219 | 0.0495284 | 178.181 | 23.6528 | 1 | 18 |
| E3 | Improved hybrid | 3 | 7249 | 251774 | 174 | 0.000413679 | 0.0169492 | 0.000807646 | 0.0279859 | 100.681 | 18.1806 | 1 | 18 |
| E3 | Without ML | 3 | 0 | 259023 | 174 | 1 | 0.0169492 | 0.0333333 | 0 | 0 | 0 | 1 | 18 |
| E3 | Without network | 3 | 7249 | 251774 | 174 | 0.000413679 | 0.0169492 | 0.000807646 | 0.0279859 | 100.681 | 18.1806 | 1 | 18 |
| E3 | Without rules | 0 | 7249 | 251774 | 177 | 0 | 0 | 0 | 0.0279859 | 100.681 | 18.1806 | 0 | undefined |
| E4 | Rules only | 0 | 0 | 258840 | 360 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E4 | ML original | 5 | 14123 | 244717 | 355 | 0.000353907 | 0.0138889 | 0.000690226 | 0.0545627 | 196.153 | 27.75 | 0 | undefined |
| E4 | ML calibrated | 0 | 7249 | 251591 | 360 | 0 | 0 | 0 | 0.0280057 | 100.681 | 18.1806 | 0 | undefined |
| E4 | Network only | 360 | 0 | 258840 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E4 | System only | 0 | 0 | 258840 | 360 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E4 | Original hybrid | 360 | 14123 | 244717 | 0 | 0.0248567 | 1 | 0.0485077 | 0.0545627 | 196.153 | 27.75 | 1 | 0 |
| E4 | Full-day uncalibrated hybrid | 360 | 12829 | 246011 | 0 | 0.0272955 | 1 | 0.0531405 | 0.0495634 | 178.181 | 23.6528 | 1 | 0 |
| E4 | Improved hybrid | 360 | 7249 | 251591 | 0 | 0.0473124 | 1 | 0.0903501 | 0.0280057 | 100.681 | 18.1806 | 1 | 0 |
| E4 | Without ML | 360 | 0 | 258840 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E4 | Without network | 0 | 7249 | 251591 | 360 | 0 | 0 | 0 | 0.0280057 | 100.681 | 18.1806 | 0 | undefined |
| E4 | Without rules | 360 | 7249 | 251591 | 0 | 0.0473124 | 1 | 0.0903501 | 0.0280057 | 100.681 | 18.1806 | 1 | 0 |
| E5 | Rules only | 543 | 0 | 258657 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E5 | ML original | 64 | 14123 | 244534 | 479 | 0.00451117 | 0.117864 | 0.00868975 | 0.0546013 | 196.153 | 27.75 | 1 | 14 |
| E5 | ML calibrated | 12 | 7249 | 251408 | 531 | 0.00165266 | 0.0220994 | 0.00307535 | 0.0280255 | 100.681 | 18.1806 | 1 | 19.3333 |
| E5 | Network only | 0 | 0 | 258657 | 543 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E5 | System only | 0 | 0 | 258657 | 543 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E5 | Original hybrid | 543 | 14123 | 244534 | 0 | 0.0370244 | 1 | 0.0714051 | 0.0546013 | 196.153 | 27.75 | 1 | 0 |
| E5 | Full-day uncalibrated hybrid | 543 | 12829 | 245828 | 0 | 0.0406072 | 1 | 0.0780453 | 0.0495985 | 178.181 | 23.6528 | 1 | 0 |
| E5 | Improved hybrid | 543 | 7249 | 251408 | 0 | 0.0696869 | 1 | 0.130294 | 0.0280255 | 100.681 | 18.1806 | 1 | 0 |
| E5 | Without ML | 543 | 0 | 258657 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E5 | Without network | 543 | 7249 | 251408 | 0 | 0.0696869 | 1 | 0.130294 | 0.0280255 | 100.681 | 18.1806 | 1 | 0 |
| E5 | Without rules | 12 | 7249 | 251408 | 531 | 0.00165266 | 0.0220994 | 0.00307535 | 0.0280255 | 100.681 | 18.1806 | 1 | 19.3333 |
| E6 | Rules only | 543 | 0 | 258657 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0.666667 | 0 |
| E6 | ML original | 64 | 14123 | 244534 | 479 | 0.00451117 | 0.117864 | 0.00868975 | 0.0546013 | 196.153 | 27.75 | 0.333333 | 14 |
| E6 | ML calibrated | 12 | 7249 | 251408 | 531 | 0.00165266 | 0.0220994 | 0.00307535 | 0.0280255 | 100.681 | 18.1806 | 0.333333 | 19.3333 |
| E6 | Network only | 360 | 0 | 258657 | 183 | 1 | 0.662983 | 0.797342 | 0 | 0 | 0 | 0.333333 | 0 |
| E6 | System only | 0 | 0 | 258657 | 543 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| E6 | Original hybrid | 543 | 14123 | 244534 | 0 | 0.0370244 | 1 | 0.0714051 | 0.0546013 | 196.153 | 27.75 | 1 | 0 |
| E6 | Full-day uncalibrated hybrid | 543 | 12829 | 245828 | 0 | 0.0406072 | 1 | 0.0780453 | 0.0495985 | 178.181 | 23.6528 | 1 | 0 |
| E6 | Improved hybrid | 543 | 7249 | 251408 | 0 | 0.0696869 | 1 | 0.130294 | 0.0280255 | 100.681 | 18.1806 | 1 | 0 |
| E6 | Without ML | 543 | 0 | 258657 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| E6 | Without network | 543 | 7249 | 251408 | 0 | 0.0696869 | 1 | 0.130294 | 0.0280255 | 100.681 | 18.1806 | 0.666667 | 0 |
| E6 | Without rules | 360 | 7249 | 251408 | 183 | 0.0473124 | 0.662983 | 0.0883219 | 0.0280255 | 100.681 | 18.1806 | 0.666667 | 9.66667 |
| E7 | Rules only | 189 | 0 | 258849 | 162 | 1 | 0.538462 | 0.7 | 0 | 0 | 0 | 0.5 | 3.33333 |
| E7 | ML original | 138 | 14141 | 244708 | 213 | 0.00966454 | 0.393162 | 0.0188653 | 0.0546303 | 196.403 | 27.8611 | 0.166667 | 6.66667 |
| E7 | ML calibrated | 160 | 7254 | 251595 | 191 | 0.0215808 | 0.45584 | 0.0412106 | 0.0280241 | 100.75 | 18.2361 | 0.166667 | 5.33333 |
| E7 | Network only | 348 | 0 | 258849 | 3 | 1 | 0.991453 | 0.995708 | 0 | 0 | 0 | 0.166667 | 0 |
| E7 | System only | 6 | 0 | 258849 | 345 | 1 | 0.017094 | 0.0336134 | 0 | 0 | 0 | 0.333333 | 0 |
| E7 | Original hybrid | 351 | 14141 | 244708 | 0 | 0.0242203 | 1 | 0.047295 | 0.0546303 | 196.403 | 27.8611 | 1 | 1.66667 |
| E7 | Full-day uncalibrated hybrid | 351 | 12853 | 245996 | 0 | 0.0265829 | 1 | 0.051789 | 0.0496544 | 178.514 | 23.6806 | 1 | 1.66667 |
| E7 | Improved hybrid | 351 | 7254 | 251595 | 0 | 0.0461538 | 1 | 0.0882353 | 0.0280241 | 100.75 | 18.2361 | 1 | 1.66667 |
| E7 | Without ML | 351 | 0 | 258849 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1.66667 |
| E7 | Without network | 189 | 7254 | 251595 | 162 | 0.025393 | 0.538462 | 0.0484988 | 0.0280241 | 100.75 | 18.2361 | 0.833333 | 2 |
| E7 | Without rules | 348 | 7254 | 251595 | 3 | 0.0457774 | 0.991453 | 0.0875141 | 0.0280241 | 100.75 | 18.2361 | 0.666667 | 1.33333 |
| benign_command_burst | Rules only | 0 | 3 | 259197 | 0 | 0 | undefined | 0 | 1.15741e-05 | 0.0416667 | 0.0416667 | undefined | undefined |
| benign_command_burst | ML original | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| benign_command_burst | ML calibrated | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_command_burst | Network only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_command_burst | System only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_command_burst | Original hybrid | 0 | 14131 | 245069 | 0 | 0 | undefined | 0 | 0.0545177 | 196.264 | 27.8472 | undefined | undefined |
| benign_command_burst | Full-day uncalibrated hybrid | 0 | 12832 | 246368 | 0 | 0 | undefined | 0 | 0.0495062 | 178.222 | 23.6944 | undefined | undefined |
| benign_command_burst | Improved hybrid | 0 | 7252 | 251948 | 0 | 0 | undefined | 0 | 0.0279784 | 100.722 | 18.2222 | undefined | undefined |
| benign_command_burst | Without ML | 0 | 3 | 259197 | 0 | 0 | undefined | 0 | 1.15741e-05 | 0.0416667 | 0.0416667 | undefined | undefined |
| benign_command_burst | Without network | 0 | 7252 | 251948 | 0 | 0 | undefined | 0 | 0.0279784 | 100.722 | 18.2222 | undefined | undefined |
| benign_command_burst | Without rules | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_authorized_peer | Rules only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_authorized_peer | ML original | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| benign_authorized_peer | ML calibrated | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_authorized_peer | Network only | 0 | 270 | 258930 | 0 | 0 | undefined | 0 | 0.00104167 | 3.75 | 0.0416667 | undefined | undefined |
| benign_authorized_peer | System only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_authorized_peer | Original hybrid | 0 | 14398 | 244802 | 0 | 0 | undefined | 0 | 0.0555478 | 199.972 | 27.8472 | undefined | undefined |
| benign_authorized_peer | Full-day uncalibrated hybrid | 0 | 13099 | 246101 | 0 | 0 | undefined | 0 | 0.0505363 | 181.931 | 23.6944 | undefined | undefined |
| benign_authorized_peer | Improved hybrid | 0 | 7519 | 251681 | 0 | 0 | undefined | 0 | 0.0290085 | 104.431 | 18.2222 | undefined | undefined |
| benign_authorized_peer | Without ML | 0 | 270 | 258930 | 0 | 0 | undefined | 0 | 0.00104167 | 3.75 | 0.0416667 | undefined | undefined |
| benign_authorized_peer | Without network | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_authorized_peer | Without rules | 0 | 7519 | 251681 | 0 | 0 | undefined | 0 | 0.0290085 | 104.431 | 18.2222 | undefined | undefined |
| benign_load | Rules only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | ML original | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| benign_load | ML calibrated | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_load | Network only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | System only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | Original hybrid | 0 | 14128 | 245072 | 0 | 0 | undefined | 0 | 0.0545062 | 196.222 | 27.8056 | undefined | undefined |
| benign_load | Full-day uncalibrated hybrid | 0 | 12829 | 246371 | 0 | 0 | undefined | 0 | 0.0494946 | 178.181 | 23.6528 | undefined | undefined |
| benign_load | Improved hybrid | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_load | Without ML | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_load | Without network | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_load | Without rules | 0 | 7249 | 251951 | 0 | 0 | undefined | 0 | 0.0279668 | 100.681 | 18.1806 | undefined | undefined |
| benign_telemetry | Rules only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | ML original | 0 | 25762 | 233438 | 0 | 0 | undefined | 0 | 0.0993904 | 357.806 | 15.6667 | undefined | undefined |
| benign_telemetry | ML calibrated | 0 | 24159 | 235041 | 0 | 0 | undefined | 0 | 0.093206 | 335.542 | 17.6944 | undefined | undefined |
| benign_telemetry | Network only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | System only | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | Original hybrid | 0 | 25762 | 233438 | 0 | 0 | undefined | 0 | 0.0993904 | 357.806 | 15.6667 | undefined | undefined |
| benign_telemetry | Full-day uncalibrated hybrid | 0 | 28003 | 231197 | 0 | 0 | undefined | 0 | 0.108036 | 388.931 | 16.3056 | undefined | undefined |
| benign_telemetry | Improved hybrid | 0 | 24159 | 235041 | 0 | 0 | undefined | 0 | 0.093206 | 335.542 | 17.6944 | undefined | undefined |
| benign_telemetry | Without ML | 0 | 0 | 259200 | 0 | undefined | undefined | undefined | 0 | 0 | 0 | undefined | undefined |
| benign_telemetry | Without network | 0 | 24159 | 235041 | 0 | 0 | undefined | 0 | 0.093206 | 335.542 | 17.6944 | undefined | undefined |
| benign_telemetry | Without rules | 0 | 24159 | 235041 | 0 | 0 | undefined | 0 | 0.093206 | 335.542 | 17.6944 | undefined | undefined |
| attack_primary_unauthorized | Rules only | 3 | 0 | 259197 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_primary_unauthorized | ML original | 0 | 14128 | 245069 | 3 | 0 | 0 | 0 | 0.0545068 | 196.222 | 27.8056 | 0 | undefined |
| attack_primary_unauthorized | ML calibrated | 0 | 7249 | 251948 | 3 | 0 | 0 | 0 | 0.0279671 | 100.681 | 18.1806 | 0 | undefined |
| attack_primary_unauthorized | Network only | 0 | 0 | 259197 | 3 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_primary_unauthorized | System only | 0 | 0 | 259197 | 3 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_primary_unauthorized | Original hybrid | 0 | 14128 | 245069 | 3 | 0 | 0 | 0 | 0.0545068 | 196.222 | 27.8056 | 0 | undefined |
| attack_primary_unauthorized | Full-day uncalibrated hybrid | 3 | 12829 | 246368 | 0 | 0.000233791 | 1 | 0.000467472 | 0.0494952 | 178.181 | 23.6528 | 1 | 0 |
| attack_primary_unauthorized | Improved hybrid | 3 | 7249 | 251948 | 0 | 0.000413679 | 1 | 0.000827016 | 0.0279671 | 100.681 | 18.1806 | 1 | 0 |
| attack_primary_unauthorized | Without ML | 3 | 0 | 259197 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_primary_unauthorized | Without network | 3 | 7249 | 251948 | 0 | 0.000413679 | 1 | 0.000827016 | 0.0279671 | 100.681 | 18.1806 | 1 | 0 |
| attack_primary_unauthorized | Without rules | 0 | 7249 | 251948 | 3 | 0 | 0 | 0 | 0.0279671 | 100.681 | 18.1806 | 0 | undefined |
| attack_boundary_flood | Rules only | 0 | 0 | 259164 | 36 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | ML original | 0 | 14128 | 245036 | 36 | 0 | 0 | 0 | 0.0545137 | 196.222 | 27.8056 | 0 | undefined |
| attack_boundary_flood | ML calibrated | 0 | 7249 | 251915 | 36 | 0 | 0 | 0 | 0.0279707 | 100.681 | 18.1806 | 0 | undefined |
| attack_boundary_flood | Network only | 0 | 0 | 259164 | 36 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | System only | 0 | 0 | 259164 | 36 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | Original hybrid | 0 | 14128 | 245036 | 36 | 0 | 0 | 0 | 0.0545137 | 196.222 | 27.8056 | 0 | undefined |
| attack_boundary_flood | Full-day uncalibrated hybrid | 0 | 12829 | 246335 | 36 | 0 | 0 | 0 | 0.0495015 | 178.181 | 23.6528 | 0 | undefined |
| attack_boundary_flood | Improved hybrid | 0 | 7249 | 251915 | 36 | 0 | 0 | 0 | 0.0279707 | 100.681 | 18.1806 | 0 | undefined |
| attack_boundary_flood | Without ML | 0 | 0 | 259164 | 36 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_boundary_flood | Without network | 0 | 7249 | 251915 | 36 | 0 | 0 | 0 | 0.0279707 | 100.681 | 18.1806 | 0 | undefined |
| attack_boundary_flood | Without rules | 0 | 7249 | 251915 | 36 | 0 | 0 | 0 | 0.0279707 | 100.681 | 18.1806 | 0 | undefined |
| attack_low_network | Rules only | 0 | 0 | 258930 | 270 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_low_network | ML original | 0 | 14128 | 244802 | 270 | 0 | 0 | 0 | 0.054563 | 196.222 | 27.8056 | 0 | undefined |
| attack_low_network | ML calibrated | 0 | 7249 | 251681 | 270 | 0 | 0 | 0 | 0.027996 | 100.681 | 18.1806 | 0 | undefined |
| attack_low_network | Network only | 3 | 0 | 258930 | 267 | 1 | 0.0111111 | 0.021978 | 0 | 0 | 0 | 1 | 0 |
| attack_low_network | System only | 0 | 0 | 258930 | 270 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_low_network | Original hybrid | 3 | 14128 | 244802 | 267 | 0.000212299 | 0.0111111 | 0.000416638 | 0.054563 | 196.222 | 27.8056 | 1 | 0 |
| attack_low_network | Full-day uncalibrated hybrid | 3 | 12829 | 246101 | 267 | 0.000233791 | 0.0111111 | 0.000457945 | 0.0495462 | 178.181 | 23.6528 | 1 | 0 |
| attack_low_network | Improved hybrid | 3 | 7249 | 251681 | 267 | 0.000413679 | 0.0111111 | 0.00079766 | 0.027996 | 100.681 | 18.1806 | 1 | 0 |
| attack_low_network | Without ML | 3 | 0 | 258930 | 267 | 1 | 0.0111111 | 0.021978 | 0 | 0 | 0 | 1 | 0 |
| attack_low_network | Without network | 0 | 7249 | 251681 | 270 | 0 | 0 | 0 | 0.027996 | 100.681 | 18.1806 | 0 | undefined |
| attack_low_network | Without rules | 3 | 7249 | 251681 | 267 | 0.000413679 | 0.0111111 | 0.00079766 | 0.027996 | 100.681 | 18.1806 | 1 | 0 |
| attack_short_thermal | Rules only | 45 | 0 | 259155 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_short_thermal | ML original | 24 | 14138 | 245017 | 21 | 0.00169468 | 0.533333 | 0.00337862 | 0.0545542 | 196.361 | 27.8333 | 1 | 3.66667 |
| attack_short_thermal | ML calibrated | 5 | 7249 | 251906 | 40 | 0.000689275 | 0.111111 | 0.00137005 | 0.0279717 | 100.681 | 18.1806 | 0.666667 | 7.5 |
| attack_short_thermal | Network only | 0 | 0 | 259155 | 45 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_short_thermal | System only | 0 | 0 | 259155 | 45 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_short_thermal | Original hybrid | 45 | 14138 | 245017 | 0 | 0.00317281 | 1 | 0.00632556 | 0.0545542 | 196.361 | 27.8333 | 1 | 0 |
| attack_short_thermal | Full-day uncalibrated hybrid | 45 | 12831 | 246324 | 0 | 0.00349487 | 1 | 0.00696541 | 0.0495109 | 178.208 | 23.6806 | 1 | 0 |
| attack_short_thermal | Improved hybrid | 45 | 7249 | 251906 | 0 | 0.00616945 | 1 | 0.0122633 | 0.0279717 | 100.681 | 18.1806 | 1 | 0 |
| attack_short_thermal | Without ML | 45 | 0 | 259155 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_short_thermal | Without network | 45 | 7249 | 251906 | 0 | 0.00616945 | 1 | 0.0122633 | 0.0279717 | 100.681 | 18.1806 | 1 | 0 |
| attack_short_thermal | Without rules | 5 | 7249 | 251906 | 40 | 0.000689275 | 0.111111 | 0.00137005 | 0.0279717 | 100.681 | 18.1806 | 0.666667 | 7.5 |
| attack_reordered | Rules only | 48 | 0 | 258885 | 267 | 1 | 0.152381 | 0.264463 | 0 | 0 | 0 | 0.666667 | 0 |
| attack_reordered | ML original | 24 | 14138 | 244747 | 291 | 0.00169468 | 0.0761905 | 0.0033156 | 0.0546111 | 196.361 | 27.8333 | 0.333333 | 3.66667 |
| attack_reordered | ML calibrated | 5 | 7249 | 251636 | 310 | 0.000689275 | 0.015873 | 0.00132118 | 0.0280008 | 100.681 | 18.1806 | 0.222222 | 7.5 |
| attack_reordered | Network only | 270 | 0 | 258885 | 45 | 1 | 0.857143 | 0.923077 | 0 | 0 | 0 | 0.333333 | 0 |
| attack_reordered | System only | 0 | 0 | 258885 | 315 | undefined | 0 | 0 | 0 | 0 | 0 | 0 | undefined |
| attack_reordered | Original hybrid | 315 | 14138 | 244747 | 0 | 0.0217948 | 1 | 0.0426598 | 0.0546111 | 196.361 | 27.8333 | 0.666667 | 0 |
| attack_reordered | Full-day uncalibrated hybrid | 315 | 12831 | 246054 | 0 | 0.0239617 | 1 | 0.0468019 | 0.0495625 | 178.208 | 23.6806 | 1 | 0 |
| attack_reordered | Improved hybrid | 315 | 7249 | 251636 | 0 | 0.0416446 | 1 | 0.0799594 | 0.0280008 | 100.681 | 18.1806 | 1 | 0 |
| attack_reordered | Without ML | 315 | 0 | 258885 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| attack_reordered | Without network | 48 | 7249 | 251636 | 267 | 0.00657805 | 0.152381 | 0.0126117 | 0.0280008 | 100.681 | 18.1806 | 0.666667 | 0 |
| attack_reordered | Without rules | 275 | 7249 | 251636 | 40 | 0.0365497 | 0.873016 | 0.070162 | 0.0280008 | 100.681 | 18.1806 | 0.555556 | 3 |
