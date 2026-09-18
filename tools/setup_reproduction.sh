#!/usr/bin/env bash
# Provision the numerical and plotting dependencies used by the paper.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
helper=.agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh
"$helper" status || true
"$helper" setup
if command -v conda >/dev/null 2>&1; then
  conda_exe="$(command -v conda)"
elif [[ -x .agent-runtime/miniforge/bin/conda ]]; then
  conda_exe=.agent-runtime/miniforge/bin/conda
elif [[ -x "$HOME/miniconda3/bin/conda" ]]; then
  conda_exe="$HOME/miniconda3/bin/conda"
else
  conda_exe="$HOME/miniforge3/bin/conda"
fi
"$conda_exe" install --yes --name "${MOOSE_CONDA_ENV:-moose}" \
  --channel conda-forge --channel https://conda.software.inl.gov/public \
  'moose-dev=2026.02.20' 'moose-libmesh=2026.02.18_f8a1758' \
  'moose-tools=2026.02.16' 'pandas=3.0.1' 'numpy=2.4.2' 'scipy=1.17.1' 'sympy=1.14.0' \
  'matplotlib=3.10.8' 'pyyaml=6.0.3'
expected_moose=abafb58b67a6037c6723ffeb19647c84484466da
actual_moose="$(git -C "${MOOSE_FRAMEWORK_PATH:-.agent-runtime/moose}" rev-parse HEAD)"
if [[ "$actual_moose" != "$expected_moose" ]]; then
  printf 'MOOSE checkout does not match the tested revision: %s\n' "$actual_moose" >&2
  exit 1
fi
"$helper" verify
"$helper" run -- python -c 'import numpy, scipy, sympy, matplotlib, yaml'
python3 tools/provision_latex.py
