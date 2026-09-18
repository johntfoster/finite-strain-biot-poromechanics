# Spatial mass balances and nonlinear Biot coefficient

This repository contains the manuscript, minimal MOOSE application, validation
data, and agent workflow for computing a finite-deformation Biot coefficient
from matched logarithmic skeleton and mineral stress laws. Implicit
differentiation gives a closed-form coefficient in terms of the current states.
An implicit poroplastic material retains active history and pressure coupling.
The closed-form derivation, verification results, and benchmark parameter
adjustments are recorded in [the formulation consistency report](validation/formulation_consistency_2026-09-14.md).

The physical specialization contains one deformable solid and one water phase.
The global fields are Q2 displacement, continuous Q1 water pressure, and Q2
solid partial density. Spatial solid mass balance evolves the partial density;
the local constitutive update supplies intrinsic solid density, solid volume
fraction, and any inelastic internal variables. A scalar solve determines the
mineral volume, and the closed-form expression supplies the fixed-pressure Biot
coefficient. A general two-state implicit tangent and centered differences of
perturbed mineral solves independently verify that coefficient. Spatial water mass balance
uses a barotropic pressure--density equation of state. The Biot transform maps
the constitutive double-prime stress to the single-prime material stress and
the total mixture stress. These local dependencies remain in the outer MOOSE
automatic-differentiation Jacobian.

The water-filled Mandel benchmark compares spatial pressure and displacement
profiles with the analytical plane-strain solution. A finite-deformation
continuation reports the departure of the Biot coefficient from its reference
value and provides two-dimensional Biot-coefficient and solid-density
snapshots. The discretization has no pressure enrichment or EG operators.

The plastic demonstration uses `ADImplicitPoroplasticBiotMaterial`. Its current
plastic state remains active in the outer AD calculation, while the derivative
defining B fixes that state. Run `make plastic` to verify the physical identities
and regenerate the material-point data. Supplementary loading and frozen-history
examples use the same mineral equation and coefficient; run `make examples`
to regenerate their independent checks and data.

## Launch and reproduce

[Open in GitHub Codespaces](https://codespaces.new/johntfoster/nonlinear_biot_ad_implementation)
opens the checked-in development container. Select an 8-core machine with
64 GB storage or larger. The first setup downloads the pinned MOOSE framework
and Conda packages, installs the plotting and LaTeX dependencies, and builds
the application and paper. Wait for the post-create command to finish. Initial
compilation can take tens of minutes. Codespaces usage is charged under your
GitHub plan; stop the Codespace when finished.

```sh
make test       # standard MOOSE tests, including active AD Jacobians
make figures    # regenerate publication figures from curated data
make paper      # paper/build/main.pdf
make serve      # companion site on forwarded port 8000
```

[Companion website](https://johntfoster.github.io/nonlinear_biot_ad_implementation/)
includes the complete [object and example catalog](https://johntfoster.github.io/nonlinear_biot_ad_implementation/moose-catalog.html#examples).
Every input links to the local materials and kernels it selects, its included
base inputs, and its test specification. Website source files are packaged
from the same checkout as the pages by `make site`.

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

The setup script pins MOOSE commit
`abafb58b67a6037c6723ffeb19647c84484466da` and the tested Conda package
versions. Inspect the environment without changing it:

```sh
.agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh status
```

For a local installation, clone with the workflow submodule and provision the
complete reproduction environment:

```sh
git submodule update --init --recursive
make setup
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

## Example entry points

| Calculation | Input | Reproduction target |
| --- | --- | --- |
| Elastic Mandel | [Q2/Q1 input](moose_app/test/tests/mandel_implicit_biot/mandel_water_q2_q1.i) | `make mandel` |
| Implicit plastic material point | [Material path](moose_app/test/tests/implicit_poroplastic/material_path.i) | `make plastic` |
| Coupled poroplastic compression | [Compression input](moose_app/test/tests/poroplastic_mandel/compression.i) | `make plastic-flow` |
| Perfect-plastic controls and hardening refinement | [Stability driver](validation/scripts/check_poroplastic_spatial_stability.py) | `make stability` |
| Supplementary loading and tangent checks | [Test group](moose_app/test/tests/poroplastic_biot/tests) | `make examples` |

`make reproduce` runs all publication drivers, including the extended stability
matrix, before rebuilding figures, the manuscript, provenance, and validation.
The extended coupled calculations can take hours. `POROPLASTIC_MPI_RANKS` controls
their MPI parallelism; choose a count no larger than the allocated CPU count.
The ordinary test harness leaves the two heavy tests to these explicit drivers.

For a local website preview, run `make serve` from the repository root and open
`http://localhost:8000`. GitHub Actions builds the same artifact and deploys it
to Pages on pushes to `main`; pull requests run the site checks without deploying.

Code is licensed under Apache 2.0; manuscript, documentation, and original data
are licensed under CC BY 4.0. See [licenses and third-party notices](LICENSES.md).
