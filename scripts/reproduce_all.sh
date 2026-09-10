#!/usr/bin/env bash
# Reproduce all manuscript results from a clean clone.
#
# Runs, in order:
#   0. environment status
#   1. shared-source integrity check
#   2. MOOSE application build
#   3. full MOOSE test suite (Mandel + poroplastic)
#   4. poroplastic validation-data curation and verification gates
#   5. Mandel analytical + AD verification
#   6. figure regeneration
#   7. manuscript build
#   8. provenance hashes and repository validation
#
# Stops on the first failing step. Requirements are pinned by the
# setup-moose-conda skill; run its `setup` once if the environment is missing.

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${repo_root}"

env_script="agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh"

step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }

step "0. Environment status"
"${env_script}" status || true

step "1. Shared-source integrity check"
tools/sync_biot_moose.py check

step "2. Verify the closed-form derivation and build the MOOSE application"
make derivation
make build

step "3. Run all MOOSE tests (Mandel + poroplastic)"
make test

step "4. Regenerate and verify implicit poroplastic data"
make plastic

step "5. Mandel analytical + AD verification"
make mandel

step "6. Regenerate figures"
make figures

step "7. Build the manuscript"
make paper

step "8. Provenance and repository validation"
make provenance
make validate

printf '\n\033[1;32mReproduction complete.\033[0m\n'
