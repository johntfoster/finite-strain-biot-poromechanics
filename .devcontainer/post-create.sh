#!/usr/bin/env bash
# Install the pinned numerical environment and verify a fresh Codespace.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p .agent-runtime
exec > >(tee .agent-runtime/codespace-setup.log) 2>&1
git submodule update --init --recursive
tools/agentctl hooks install
bash tools/setup_reproduction.sh
make build BUILD_JOBS=4
make site
make paper
printf '\nReady: make test, make figures, make reproduce, or make serve.\n'
