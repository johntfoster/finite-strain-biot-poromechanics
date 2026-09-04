# Spatial mass balances and nonlinear Biot coefficient

This repository contains the manuscript, minimal MOOSE application, validation
data, and agent workflow for computing a finite-deformation Biot coefficient
from a general fixed-pressure local constitutive update.  The elastic mineral
response is the verification specialization.

The physical specialization contains one deformable solid and one water phase.
The global fields are Q2 displacement, continuous Q1 water pressure, and Q2
solid partial density. Spatial solid mass balance evolves the partial density;
the local constitutive update supplies intrinsic solid density, solid volume
fraction, and any inelastic internal variables. Implicit differentiation of the
complete local residual system supplies the fixed-pressure Biot coefficient.
The elastic closure supplies analytical and centered-difference tests of this
general path. Spatial water mass balance
uses a barotropic pressure--density equation of state. The Biot transform maps
the constitutive double-prime stress to the single-prime material stress and
the total mixture stress. These local dependencies remain in the outer MOOSE
automatic-differentiation Jacobian.

The water-filled Mandel benchmark compares spatial pressure and displacement
profiles with the analytical plane-strain solution. A finite-deformation
continuation reports the departure of the Biot coefficient from its reference
value and provides two-dimensional Biot-coefficient and solid-density
snapshots. The discretization has no pressure enrichment or EG operators.

## Repository layout

- `paper/` — canonical LaTeX manuscript rooted at `paper/main.tex`
- `moose_app/` — standalone minimal MOOSE application and focused tests
- `moose/` — shared-source manifest and synchronization state
- `validation/` — analytical comparisons, curated data, and traceability
- `scripts/` — figure, extraction, provenance, and repository-validation tools
- `agent_environment/` — portable manuscript, research, and MOOSE skills
- `agent_workflows/` — Biot-specific routing, checklists, and failure triage

## Agentic work

Start every repository task with:

```sh
tools/agentctl route "describe the task"
```

The repository can be used as a complete manuscript workspace without another
checkout. `AGENTS.md` identifies `paper/main.tex` as the source of truth and
defines the manuscript build, citation, equation, and MOOSE workflows.

Shared MOOSE files are synchronized with the authoritative general simulator
repository. A successful pull records its local location in the ignored
`.agent-runtime/master_repository` file:

```sh
tools/sync_biot_moose.py check
tools/sync_biot_moose.py pull --master PATH_TO_MASTER
tools/sync_biot_moose.py push
```

An agent may edit shared MOOSE files here. `push` copies those edits to the
master only when its files still match the recorded base; divergent edits fail
without overwriting either repository.

## Reproduce

The setup skill pins MOOSE commit
`abafb58b67a6037c6723ffeb19647c84484466da` and the tested Conda package
versions. Inspect the environment without changing it:

```sh
agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh status
```

Provision missing dependencies only when authorized:

```sh
agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh setup
```

Build, run the Mandel and Q1 Jacobian tests, regenerate figures and manuscript,
and validate the package with:

```sh
make reproduce
```

Useful focused targets are `make build`, `make test`, `make mandel`, `make
figures`, `make paper`, `make validate`, and `make sync-check`.

The numerical results constitute implementation verification, analytical
benchmark comparison, and synthetic finite-deformation discrimination. They do
not constitute material-specific physical validation.
