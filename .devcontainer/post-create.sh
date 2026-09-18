#!/usr/bin/env bash
# Install the pinned numerical environment and verify a fresh Codespace.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git submodule update --init --recursive
tools/agentctl hooks install
bash tools/setup_reproduction.sh
make build
make site
make paper
printf '\nReady: make test, make figures, make reproduce, or make serve.\n'
