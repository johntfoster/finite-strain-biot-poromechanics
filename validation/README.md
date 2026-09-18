# Verification evidence and reproduction

The canonical formulation is in `paper/main.tex`, with its constitutive
specialization in `paper/sections/finite_deformation_biot.tex`. The matched
logarithmic mineral equation uses elastic volume `Je = J/ap`; the coefficient
uses total volume `J`. The production update and independent tangent checks
share this convention. The global fields are Q2 displacement, continuous Q1
water pressure, and Q2 solid partial density.

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

## Submission verification, 2026-09-18

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
