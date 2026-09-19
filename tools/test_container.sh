#!/usr/bin/env bash
# Exercise the mounted-checkout startup and ordinary tests used in Codespaces.
set -euo pipefail
exec > >(tee /ci-output/verification.log) 2>&1
git clone --no-hardlinks /opt/biot /tmp/biot-workspace
cd /tmp/biot-workspace
git remote set-url origin https://github.com/johntfoster/finite-strain-biot-poromechanics.git
bash .devcontainer/post-create.sh
cmp moose_app/nonlinear_biot_ad-opt /opt/biot/moose_app/nonlinear_biot_ad-opt
test -L .agent-runtime/moose
make test
make derivation
.agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- python3 -m unittest discover -s tools/tests
make validate
tools/agentctl check --profile manuscript
cp moose_app/.previous_test_results.json /ci-output/moose-tests.json
cp paper/build/main.log /ci-output/manuscript.log
git diff --exit-code
