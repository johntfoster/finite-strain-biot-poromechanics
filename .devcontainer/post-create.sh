#!/usr/bin/env bash
# Attach the tested image environment to the editable Codespaces checkout.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p .agent-runtime
exec > >(tee .agent-runtime/codespace-setup.log) 2>&1
git submodule update --init --recursive
tools/agentctl hooks install
if [[ -n "${BIOT_IMAGE_ROOT:-}" && -d "$BIOT_IMAGE_ROOT/.agent-runtime/moose" ]]; then
  if [[ ! -e .agent-runtime/moose ]]; then
    ln -s "$BIOT_IMAGE_ROOT/.agent-runtime/moose" .agent-runtime/moose
  fi
else
  bash tools/setup_reproduction.sh
fi
make build BUILD_JOBS=2
make site
if python3 -c 'import json; from pathlib import Path; raise SystemExit(not json.loads(Path("research-project.yml").read_text())["maintenance"]["manuscript_edits"])'; then
  make paper
else
  printf '\nManuscript freeze: skipping paper and publication-figure generation.\n'
fi
python3 .agent/shared/tools/research_project.py check
printf '\nReady: make test, make figures, make reproduce, or make serve.\n'
