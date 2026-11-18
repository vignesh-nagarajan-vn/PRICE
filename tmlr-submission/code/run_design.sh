#!/bin/bash
# Sensitivity of the certified search to its own design parameters (30 seeds, monotone and slope-bound classes).
set -u
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
R=../results
run() {  # name, extra JSON
  "$PY" -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --extra "$2" --procs "${PROCS:-6}" \
      --out "$R/design_$1.json" >> "$R/run_design.log" 2>&1
}
run ncap50   '{"n_cap": 50000}'
run ncap200  '{"n_cap": 200000}'
run ratio125 '{"rho": 1.25}'
run ratio200 '{"rho": 2.0}'
run step0025 '{"step": 0.0025}'
run step010  '{"step": 0.01}'
run n032     '{"n0": 32}'
run n0128    '{"n0": 128}'
run alpha01  '{"alpha": 0.01}'
run alpha10  '{"alpha": 0.1}'
echo "design runs done: $(date)" >> "$R/run_design.log"
