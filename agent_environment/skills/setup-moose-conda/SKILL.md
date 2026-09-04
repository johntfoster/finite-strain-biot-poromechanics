---
name: setup-moose-conda
description: Inspect, set up, repair, and verify the repository's MOOSE Conda toolchain and framework checkout. Use only for MOOSE builds, tests, runtime checks, or explicit toolchain preparation; do not activate for manuscript-only work.
---

# Set Up MOOSE with Conda

The setup command can bootstrap a repository-local Miniforge installation,
create the MOOSE environment, obtain the pinned framework checkout, and apply
the recorded patch series. None of these network or installation steps runs
for manuscript-only routes.

Use the bundled script. All paths in instructions and configuration are
repository-relative. Runtime resolution to an absolute path happens inside the
script after it discovers the repository root.

## Runtime layout

- Conda environment: `moose`, overridable with `MOOSE_CONDA_ENV`.
- Framework checkout: `.agent-runtime/moose`, overridable with the
  repository-relative `MOOSE_FRAMEWORK_PATH`.
- Application source: `moose_app/`.
- Shared application files are synchronized with the authoritative simulator
  repository through `tools/sync_biot_moose.py`; follow `AGENTS.md` before
  editing them.

The runtime directory is ignored by Git. A checkout elsewhere may be linked at
`.agent-runtime/moose`; do not encode its machine path in repository files.

## Workflow

1. Read `AGENTS.md`, `VISION.md`, and any narrower `AGENTS.md` in the target
   MOOSE directory.
2. Run the non-mutating diagnostic first:

   ```bash
   agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh status
   ```

3. If dependencies are missing, obtain authorization before network access or
   environment mutation, then run:

   ```bash
   agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh setup
   ```

   Never remove or recreate an existing environment automatically.
4. Verify activation, MPI, libMesh, Python dependencies, and the checkout:

   ```bash
   agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh verify
   ```

5. Execute builds or tests inside the verified environment:

   ```bash
   agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- make -j1
   agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- python .agent-runtime/moose/python/run_tests -j1
   ```

Use conservative build parallelism until a current memory check supports a
higher value. Treat a missing checkout separately from a missing environment;
do not clone or replace either silently.

## Reporting

Distinguish `status`, `verify`, and an actual `run`. Report the environment,
resolved checkout commit, package versions, commands executed, and whether a
run was complete, partial, or blocked. A sandbox-specific MPI initialization
failure is an execution-environment issue, not automatically a model failure.
