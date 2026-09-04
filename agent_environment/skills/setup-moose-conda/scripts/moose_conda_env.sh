#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(git -C "${script_dir}" rev-parse --show-toplevel)"

readonly DEFAULT_ENV_NAME="moose"
readonly DEFAULT_MOOSE_PATH=".agent-runtime/moose"
readonly INL_CHANNEL="https://conda.software.inl.gov/public"
readonly MOOSE_URL="https://github.com/idaholab/moose.git"
readonly MOOSE_COMMIT="abafb58b67a6037c6723ffeb19647c84484466da"
readonly MOOSE_DEV_VERSION="2026.02.20"
readonly MOOSE_LIBMESH_VERSION="2026.02.18_f8a1758"
readonly MOOSE_TOOLS_VERSION="2026.02.16"
readonly PANDAS_VERSION="3.0.1"

env_name="${MOOSE_CONDA_ENV:-${DEFAULT_ENV_NAME}}"
moose_path="${MOOSE_FRAMEWORK_PATH:-${DEFAULT_MOOSE_PATH}}"

case "${moose_path}" in
  /*)
    printf 'ERROR MOOSE_FRAMEWORK_PATH must be repository-relative: %s\n' "${moose_path}" >&2
    exit 2
    ;;
esac

moose_dir="${repo_root}/${moose_path#./}"
local_conda="${repo_root}/.agent-runtime/miniforge/bin/conda"
conda_command=""

usage() {
  printf '%s\n' \
    "Usage: agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh {status|setup|verify|run} [-- command [args...]]" \
    "" \
    "Environment overrides:" \
    "  MOOSE_CONDA_ENV       Conda environment name (default: moose)" \
    "  MOOSE_FRAMEWORK_PATH  Repository-relative checkout (default: .agent-runtime/moose)"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'ERROR required command is unavailable: %s\n' "$1" >&2
    exit 2
  }
}

select_conda() {
  if command -v conda >/dev/null 2>&1; then
    conda_command="$(command -v conda)"
  elif [[ -x "${local_conda}" ]]; then
    conda_command="${local_conda}"
  elif [[ -x "${HOME}/miniconda3/bin/conda" ]]; then
    conda_command="${HOME}/miniconda3/bin/conda"
  elif [[ -x "${HOME}/miniforge3/bin/conda" ]]; then
    conda_command="${HOME}/miniforge3/bin/conda"
  else
    return 1
  fi
}

install_conda() {
  local system machine installer url
  system="$(uname -s)"
  machine="$(uname -m)"
  case "${system}-${machine}" in
    Linux-x86_64) installer="Miniforge3-Linux-x86_64.sh" ;;
    Linux-aarch64|Linux-arm64) installer="Miniforge3-Linux-aarch64.sh" ;;
    Darwin-x86_64) installer="Miniforge3-MacOSX-x86_64.sh" ;;
    Darwin-arm64) installer="Miniforge3-MacOSX-arm64.sh" ;;
    *) printf 'ERROR unsupported Conda bootstrap platform: %s-%s\n' "${system}" "${machine}" >&2; return 2 ;;
  esac
  mkdir -p "${repo_root}/.agent-runtime/downloads"
  url="https://github.com/conda-forge/miniforge/releases/latest/download/${installer}"
  if command -v curl >/dev/null 2>&1; then
    curl -fL "${url}" -o "${repo_root}/.agent-runtime/downloads/${installer}"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "${repo_root}/.agent-runtime/downloads/${installer}" "${url}"
  else
    printf 'ERROR curl or wget is required to bootstrap Conda\n' >&2
    return 2
  fi
  bash "${repo_root}/.agent-runtime/downloads/${installer}" -b -p "${repo_root}/.agent-runtime/miniforge"
  select_conda
}

ensure_checkout() {
  if [[ ! -d "${moose_dir}/.git" ]]; then
    require_command git
    mkdir -p "$(dirname "${moose_dir}")"
    git clone "${MOOSE_URL}" "${moose_dir}"
    git -C "${moose_dir}" checkout --detach "${MOOSE_COMMIT}"
  fi
  local patch
  for patch in "${repo_root}"/moose_app/patches/moose/*.patch; do
    [[ -e "${patch}" ]] || continue
    if git -C "${moose_dir}" apply --check "${patch}" >/dev/null 2>&1; then
      git -C "${moose_dir}" apply "${patch}"
    elif ! git -C "${moose_dir}" apply --reverse --check "${patch}" >/dev/null 2>&1; then
      printf 'ERROR MOOSE patch is neither applicable nor already applied: %s\n' "${patch#${repo_root}/}" >&2
      return 1
    fi
  done
}

environment_exists() {
  "${conda_command}" env list | awk -v target="${env_name}" '$1 == target { found = 1 } END { exit(found ? 0 : 1) }'
}

package_table() {
  "${conda_command}" list -n "${env_name}"
}

package_present() {
  local table="$1"
  local package_name="$2"
  printf '%s\n' "${table}" | awk -v target="${package_name}" '$1 == target { found = 1 } END { exit(found ? 0 : 1) }'
}

print_required_packages() {
  local table="$1"
  printf '%s\n' "${table}" | awk '$1 == "moose-libmesh" || $1 == "moose-tools" || $1 == "moose-dev" || $1 == "pandas" { print "PACKAGE " $1 " " $2 " " $3 " " $4 }'
}

check_checkout() {
  if [[ ! -d "${moose_dir}" ]]; then
    printf 'ERROR MOOSE checkout is missing: %s\n' "${moose_path}" >&2
    return 1
  fi
  if [[ ! -f "${moose_dir}/framework/moose.mk" ]]; then
    printf 'ERROR checkout lacks framework/moose.mk: %s\n' "${moose_path}" >&2
    return 1
  fi
  if ! git -C "${moose_dir}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'ERROR checkout is not a Git work tree: %s\n' "${moose_path}" >&2
    return 1
  fi
  printf 'MOOSE_PATH %s\n' "${moose_path}"
  printf 'MOOSE_COMMIT %s\n' "$(git -C "${moose_dir}" rev-parse --short=12 HEAD)"
}

status() {
  select_conda || { printf 'ERROR Conda is unavailable; run setup to bootstrap it\n' >&2; return 1; }
  printf 'CONDA_ENV %s\n' "${env_name}"
  if ! environment_exists; then
    printf 'ERROR Conda environment is missing: %s\n' "${env_name}" >&2
    return 1
  fi

  local prefix
  local table
  prefix="$("${conda_command}" run -n "${env_name}" sh -c 'printf "%s" "$CONDA_PREFIX"')"
  table="$(package_table)"
  printf 'CONDA_PREFIX %s\n' "${prefix}"
  print_required_packages "${table}"

  local missing=0
  local package_name
  for package_name in moose-libmesh moose-tools moose-dev pandas; do
    if ! package_present "${table}" "${package_name}"; then
      printf 'ERROR required package is missing: %s\n' "${package_name}" >&2
      missing=1
    fi
  done
  check_checkout || missing=1
  return "${missing}"
}

setup_environment() {
  select_conda || install_conda
  ensure_checkout
  if environment_exists; then
    "${conda_command}" install --yes --name "${env_name}" \
      --channel conda-forge --channel "${INL_CHANNEL}" \
      "moose-libmesh=${MOOSE_LIBMESH_VERSION}" "moose-tools=${MOOSE_TOOLS_VERSION}" \
      "moose-dev=${MOOSE_DEV_VERSION}" "pandas=${PANDAS_VERSION}"
  else
    "${conda_command}" create --yes --name "${env_name}" \
      --channel conda-forge --channel "${INL_CHANNEL}" \
      "moose-libmesh=${MOOSE_LIBMESH_VERSION}" "moose-tools=${MOOSE_TOOLS_VERSION}" \
      "moose-dev=${MOOSE_DEV_VERSION}" "pandas=${PANDAS_VERSION}"
  fi
  status
}

verify() {
  status
  "${conda_command}" run --no-capture-output -n "${env_name}" sh -c '
    set -eu
    test -n "${CONDA_PREFIX:-}"
    test -n "${LIBMESH_DIR:-}"
    command -v mpicxx >/dev/null
    test -x "${LIBMESH_DIR}/bin/libmesh-config"
    mpicxx --version >/dev/null
    printf "LIBMESH_VERSION %s\n" "$("${LIBMESH_DIR}/bin/libmesh-config" --version)"
    python -c "import pandas; print(\"PANDAS_VERSION\", pandas.__version__)"
  '
  printf 'VERIFIED conda activation, MPI compiler, libMesh, pandas, and framework checkout\n'
}

run_command() {
  if [[ "${1:-}" != "--" ]]; then
    printf 'ERROR run requires -- followed by a command\n' >&2
    usage >&2
    exit 2
  fi
  shift
  if [[ "$#" -eq 0 ]]; then
    printf 'ERROR no command supplied after --\n' >&2
    exit 2
  fi
  verify
  env MOOSE_DIR="${moose_dir}" "${conda_command}" run --no-capture-output -n "${env_name}" "$@"
}

case "${1:-}" in
  status)
    [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
    status
    ;;
  setup)
    [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
    setup_environment
    ;;
  verify)
    [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
    verify
    ;;
  run)
    shift
    run_command "$@"
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
