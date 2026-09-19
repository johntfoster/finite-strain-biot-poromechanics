# Verification evidence and reproduction

The canonical formulation is in `paper/main.tex`, with its constitutive
specialization in `paper/sections/finite_deformation_biot.tex`. The matched
logarithmic mineral equation uses elastic volume `Je = J/ap`; the coefficient
uses total volume `J`. The production update and independent tangent checks
share this convention. The global fields are Q2 displacement, continuous Q1
water pressure, and Q2 solid partial density.

The [equation map](equation_to_moose_map.yml) covers every equation label,
including subequation group labels, and every local material, kernel,
and postprocessor. Its supporting mappings distinguish analytical derivation,
limiting cases, benchmark formulas, and input conditions from assembled
equations. Run `make validate` to check both directions against the canonical manuscript
inputs, source files, and test specifications. This structural check detects
drift; the numerical verifiers below establish the tested mathematical identities.
The standalone checker is `scripts/check_equation_traceability.py`; execute it
with Python from the prepared MOOSE environment, which supplies PyYAML.

## Evidence classes

| Evidence | Current record | Command |
| --- | --- | --- |
| Governing-equation and object mapping | [Equation map](equation_to_moose_map.yml), [theory traceability](theory_traceability.yml) | `make validate` |
| Constitutive identities and symbolic reductions | [Stress-trace derivation](stress_trace_derivation_review.md) | `make derivation` |
| Implicit return, fixed-history tangent, objectivity, and increment refinement | [Material-point verification](implicit_poroplastic_verification.json) | `make plastic` |
| Assembled AD Jacobians and input regressions | [MOOSE tests](../moose_app/test/tests) | `make test` |
| Analytical Mandel comparison and elastic finite-deformation continuation | [Mandel verification](mandel_implicit_biot.yml) | `make mandel` |
| Coupled plastic storage, elastic limit, and mesh/time refinement | [Coupled verification](poroplastic_mandel_verification.json), [numerical notes](poroplastic_mandel_numerical_notes.md) | `make plastic-flow` |
| Perfect-plastic controls and hardening refinement | [Stability record](poroplastic_spatial_stability.json), [interpretation](poroplastic_spatial_stability.md) | `make stability` |
| Supplementary loading, unloading, and frozen-history checks | [Test specification](../moose_app/test/tests/poroplastic_biot/tests) | `make examples` |

The manuscript's material-point and coupled plastic examples use initial
cohesion 20 MPa and isotropic hardening modulus 100 MPa. The ordinary regression
suite also retains zero-hardening limits. The six-case stability study includes
the perfectly plastic, half-time-step, and associated-flow controls; its
positive hardening results apply to the sampled synthetic loading path.

The [acceptance specification](acceptance.yml) separates implementation
verification, analytical comparison, numerical convergence, and synthetic
finite-deformation discrimination. Material-specific physical validation
remains open. The saturated water EOS is continued into tension in the coupled
example; cavitation and desaturation are outside its scope.

## Constitutive verification

Independent checks reconstruct the physical state from the MOOSE outputs.
The intrinsic density and volume fraction are checked against solid mass
conservation and the mineral equation of state. The mineral law is also
checked against the intrinsic solid stress trace. Numerical differentiation
of the pressure Legendre potential recovers the returned single-prime stress;
differentiation of the reduced energy recovers the double-prime stress,
including its nonzero-pressure correction. The verifier checks the drained
skeleton response, the relations between effective and total stresses, and
pressure derivatives and integration at fixed plastic history using
independently solved mineral states.

The logarithm of the incremental plastic factor checks the flow rule, while
its determinant checks accumulated distention. The accumulated plastic
multiplier is independently summed over increments and used to check the
evolving cohesion. Yield admissibility, consistency during plastic flow with
hardening, and nonnegative plastic dissipation are checked separately.
Zero-hardening regressions retain verification of the perfectly plastic limit.

The same checks pass for a path with unequal principal stretches and nonzero
pore pressure. Load-increment refinement reduces the change between successive
returned plastic states on that path. The independent Jacobian comparisons
described below also verify the Newton Jacobian of the converged plastic
update. These checks apply on the smooth part of the yield surface.

Run `make plastic` to reproduce the material-point verification. The
[constitutive verification driver](scripts/check_implicit_poroplastic.py) and
[curated results](implicit_poroplastic_verification.json) record the checks
and their outcomes; `make test` includes the ordinary Jacobian regressions.

## Verification of the discrete residuals

The implementation evaluates solid and fluid accumulation rates by applying
the chain rule to field rates supplied by the MOOSE time integrator. At a
finite time step, these rates generally differ from backward differences of
the complete nonlinear accumulations. The verification therefore measures
referential solid-mass drift and fluid mass-balance drift under time-step
refinement. A separate elastic BDF2 regression checks that the same
chain-rule calculation accepts rates from another MOOSE time integrator
without modification.

### Jacobian comparisons

PETSc forms a finite-difference approximation of the residual Jacobian and
compares it with the Jacobian assembled from MOOSE AD derivatives, including
constitutive rates entering fluid storage. The relative and absolute
Frobenius-norm differences must remain below `1e-7` and `1e-5`, respectively.
The finite-difference scale parameter is `1e-9` in the unit-scaled diagnostic.

The comparisons cover three settings:

- The elastic coupled-field test includes momentum, solid mass, fluid storage,
  and Darcy flow.
- The active-plastic test uses algebraic residuals containing the returned
  stress invariants, plastic distention, and Biot coefficient at nonzero
  pressure and unequal principal stretches. Each finite-difference
  perturbation repeats the return mapping, testing the derivative of the
  converged local update carried into the outer Newton Jacobian.
- The coupled poroplastic test includes all four field residuals during
  compression and the subsequent hold. A temporal predictor moves the initial
  Newton guess away from the elastic–plastic switching surface, and every
  assembled Jacobian is compared on that path using the same tolerances.

At the switching surface itself, perturbations can produce either an elastic
response or plastic flow, so a single smooth Jacobian does not describe both
sides. The predictor permits comparisons within a smooth branch; the test
does not establish differentiability at the switch.

### Storage and integrated mass balance

An independent check perturbs total volume, pressure, solid partial density,
and plastic distention at sampled quadrature points, solves the scalar
mineral equation independently, and differences the complete water
accumulation. This verifies the plastic storage contribution separately from
the assembled Jacobian.

Integrated Darcy outflow and the pressure-boundary reaction are compared with
water-mass change. The reaction sums only nodes carrying pressure degrees of
freedom. Time-step refinement measures mass drift introduced by the chain-rule
time discretization.

Run the ordinary input regressions with `make test` and the full coupled
storage, Jacobian, and refinement study with `make plastic-flow`. The
[MOOSE test specifications](../moose_app/test/tests),
[coupled verification driver](scripts/check_poroplastic_mandel.py), and
[numerical notes](poroplastic_mandel_numerical_notes.md) provide the executable
checks and their results.

## Artifact provenance

Input decks and verification drivers are source. Solver output and logs belong
under ignored `.agent-runtime/` directories. Curated CSV and JSON/YAML records
in this directory contain accepted results. Publication plots live in
`figures/`, with identical PNG copies under `docs/assets/img/`.

Run `make reproduce` to regenerate all evidence, figures, and the canonical
manuscript before refreshing [content hashes](provenance.yml) and running the
repository audit. This includes the extended studies; the ordinary MOOSE test
suite marks those two tests as heavy. Do not interpret that default omission as
a completed refinement or stability run. Current source hashes and acceptance
criteria are checked by `make validate`; the companion site also checks every
local link and packaged source file.

The supplementary smooth-cone domain rejection is retained in
[poroplastic_domain_checks.json](poroplastic_domain_checks.json). It is an
expected constitutive-domain rejection, not a converged data point.

## Review response, 2026-09-18

Execution provenance for new publication runs is recorded by the simulation
drivers before execution, with observed package versions, framework commit,
application hash, and completed output hashes. `make provenance` packages those
observations separately from `required_environment`; it does not identify the
environment of historical runs. Missing historical observations are marked
`not_recorded`. Cache reuse retains the observations from the original run.

The optional virgin coefficient is evaluated after the production plastic
return. If its state is inadmissible, the coefficient is NaN and
`plastic_elastic_biot_coefficient_available` is zero. Setting
`compute_elastic_coefficient=false` disables this diagnostic. A companion law
selected with `use_elastic_coefficient_in_trial=true` still requires an
admissible virgin state. `check_comparator_domain.py` verifies these cases,
using `initial_plastic_distention=2` to initialize isotropic history and its
matching accumulated multiplier. Ordinary calculations retain the default
unit initial distention.

The [review response](peer_review_2026-09-18.md) records the focused regression
and publication checks for these changes.

The subsequent [consistency review](consistency_review_2026-09-18.md) checks
the current manuscript against the implementation and companion website,
including complete equation coverage and refreshed publication evidence.

## Submission verification before the review, 2026-09-18

The pinned local toolchain passed all 21 ordinary MOOSE regressions. The two
heavy studies were run separately through the full publication drivers:
`make plastic-flow` passed storage, Jacobian, elastic-limit, and mesh/time
comparisons, and `make stability` passed all six cases. The derivation checks,
material-point examples, supplementary loading paths, analytical Mandel
benchmark, and finite-deformation continuation also passed their existing
acceptance criteria.

All publication figures were regenerated from the resulting curated data, and
the canonical manuscript compiled to 30 pages. The repository audit, 13 tool
tests, 33-file shared-source integrity check, and manuscript environment check
passed. The website build checked 298 local links and 25 repository Markdown
links. The container image and manuscript build were also tested independently.

A fresh eight-core GitHub Codespace built the pinned MOOSE framework and
application, then passed `make test plastic figures paper provenance validate`.
Its ordinary suite reported 21 passed, two heavy tests skipped, and zero failed;
the skipped studies are covered by the full local runs above. This check used
a newly installed Conda environment and the checked-in container configuration.
