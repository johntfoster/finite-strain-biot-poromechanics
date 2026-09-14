#!/usr/bin/env bash
# Reproduce all retained examples, figures, and manuscript results.
# Make orders the validation stages and runs shared prerequisites once.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${repo_root}"
exec make reproduce
