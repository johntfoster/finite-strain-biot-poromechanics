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
make paper
printf '\nReady: make test, make figures, make reproduce, or make serve.\n'
