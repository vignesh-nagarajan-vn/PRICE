# Horizon stability of the tail-average metric

Every reported final error is a 300-step tail average over the deployed path. This audit re-measures each cell at five horizons and reports the spread; a last-iterate metric fails it (the anchor-off cells limit-cycle).

## E7 ablation grid (base T = 4500)

| cell (D,A,G) | T=4498 | T=4499 | T=4500 | T=4501 | T=4502 | spread |
|---|---|---|---|---|---|---|
| D1A1G1 | 0.0436 | 0.0436 | 0.0437 | 0.0437 | 0.0438 | 0.0003 |
| D1A1G0 | 0.0436 | 0.0436 | 0.0437 | 0.0437 | 0.0438 | 0.0003 |
| D1A0G1 | 0.1862 | 0.1867 | 0.1845 | 0.1844 | 0.1844 | 0.0023 |
| D1A0G0 | 0.1215 | 0.1215 | 0.1216 | 0.1216 | 0.1216 | 0.0000 |
| D0A1G1 | 0.0178 | 0.0170 | 0.0182 | 0.0212 | 0.0197 | 0.0042 |
| D0A1G0 | 0.0178 | 0.0170 | 0.0182 | 0.0212 | 0.0197 | 0.0042 |
| D0A0G1 | 0.2838 | 0.2838 | 0.2825 | 0.2795 | 0.2816 | 0.0043 |
| D0A0G0 | 0.0934 | 0.0928 | 0.0939 | 0.0965 | 0.0949 | 0.0037 |

## E4 SafeD cell (base T = 4000)

| T | 3998 | 4000 | 4002 | spread |
|---|---|---|---|---|
| err | 0.0391 | 0.0389 | 0.0387 | 0.0004 |

## E8 pricing agent (base T = 2500)

| T | 2498 | 2500 | 2502 | spread |
|---|---|---|---|---|
| err | 0.1483 | 0.1534 | 0.1473 | 0.0062 |

**Worst spread across all cells: 0.0062 (tolerance 0.01): PASS.**

