# Real-data leg: constants on the REFLEX calibration

## 1. Port validation vs the published run (07-12-2026)

| cell | h* (port/pub) | eps* = gamma (port/pub) | m (port/pub) |
|---|---|---|---|
| IG-calm | 0.435 / 0.436 | 465.4 / 465.3 | 0.0657 / 0.0662 |
| IG-normal | 0.558 / 0.558 | 268.0 / 268.0 | 0.0655 / 0.0660 |
| IG-elevated | 0.793 / 0.794 | 147.3 / 147.3 | 0.0658 / 0.0662 |
| IG-stress | 1.206 / 1.207 | 70.6 / 70.6 | 0.0663 / 0.0668 |
| IG-crisis | 1.471 / 1.472 | 34.6 / 34.5 | 0.0649 / 0.0653 |
| HY-calm | 1.182 / 1.183 | 28.3 / 28.3 | 0.0663 / 0.0667 |
| HY-normal | 1.534 / 1.535 | 16.1 / 16.2 | 0.0659 / 0.0664 |
| HY-elevated | 2.158 / 2.159 | 9.1 / 9.1 | 0.0659 / 0.0663 |
| HY-stress | 3.273 / 3.275 | 4.7 / 4.7 | 0.0652 / 0.0657 |
| HY-crisis | 4.167 / 4.169 | 2.2 / 2.2 | 0.0547 / 0.0551 |

**10/10 cells reproduce the published run.**

## 2. Extension: the paper's objects per cell

| cell | gamma_PO | exch. rate (1/2)gamma_PO | gap h_SP-h_PO (% of h0) | m |
|---|---|---|---|---|
| IG-calm | 510.6 | 255.3 | 0.0099 (2.6%) | 0.0657 |
| IG-normal | 293.8 | 146.9 | 0.0125 (2.6%) | 0.0655 |
| IG-elevated | 163.1 | 81.5 | 0.0129 (1.9%) | 0.0658 |
| IG-stress | 77.6 | 38.8 | 0.0260 (2.5%) | 0.0663 |
| IG-crisis | 37.8 | 18.9 | 0.0331 (2.7%) | 0.0649 |
| HY-calm | 30.5 | 15.3 | 0.0422 (4.1%) | 0.0663 |
| HY-normal | 17.4 | 8.7 | 0.0557 (4.2%) | 0.0659 |
| HY-elevated | 9.8 | 4.9 | 0.0687 (3.6%) | 0.0659 |
| HY-stress | 5.0 | 2.5 | 0.1184 (4.1%) | 0.0652 |
| HY-crisis | 2.3 | 1.2 | 0.1513 (4.3%) | 0.0547 |

**F = 1.6252 across the portfolio** of 10 rating x regime cells (C5.1): isotropic exploration overpays the A-optimal shape by 63% at the portfolio level.

## 3. Curvature dispersion across the bond universe

170 CUSIPs with >= 12 months of returns; per-bond annualized vol 0.001-0.148 (p5-p95).

**F = 1.0020** on the IG-normal cell: isotropic exploration overpays the A-optimal shape by 0.2% on this universe (C5.1). The modest value is itself a finding: at these anchor-dominated curvatures the real-data dispersion is small - the shaping gain concentrates in the toxic-channel term, which is structurally scaled (see the mapping's provenance caveat).

## Provenance (inherited, binding)

Only (A, k, sigma, h) are data-identified; the toxic channel is structurally scaled (documented ratios in mapping.py). Not trade-level TRACE. The port validation in section 1 is against REFLEX's own published run, not against market ground truth.
