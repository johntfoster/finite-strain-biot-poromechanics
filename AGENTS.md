# AGENTS.md — Nonlinear Biot AD implementation paper

## Scope

This repository contains a standalone computational paper and reproducible
nonreacting pressure-path study for the nonlinear Biot coefficient. The theory
and MOOSE implementation are traced to the read-only source repository:

`/home/jfoster/projects/research/reactive_transport/multicomponent_reactive_flow`

The experimental comparison is Lawal and Kim (2026), especially Figure 3c and
the public Zenodo poromechanical workbook (DOI 10.5281/zenodo.20089570).

## Every session

Read `SOUL.md`, `USER.md`, `TASKS.md`, `VISION.md`, `THEORY.md`, and `CODE.md`.
Check `memory/` for the most recent results. Work only in this repository unless
the user explicitly authorizes a source-code change upstream.

## Non-negotiable technical rules

1. Use the notation and definitions in the current multicomponent paper.
2. Form the nonlinear coefficient from the summed solid-phase/component version
   of Eq. (32); do not introduce `A` or `M_a^0` as code-facing shorthand.
3. The inner derivative is the constitutive partial at fixed equivalent pore
   pressure; the outer MOOSE AD derivative must remain active for Newton.
4. Distinguish intrinsic skeleton density from bulk solid partial density.
5. Use Q2 Lagrange displacement and P1+P0 enriched Galerkin pressure when a
   coupled mechanics/flow solve is performed.
6. Every MOOSE object and input block must trace to a numbered paper equation.
7. Do not claim agreement from a plotted curve alone. Report data provenance,
   units, objective functions, error metrics, and acceptance tolerances.
8. Preserve the nonreacting scope of the Lawal–Kim pressure-path comparison.
9. Never use `std::pow()` with `ADReal`; use unqualified `pow()`.

## Verification gates

- Reproduce the published Figure 3c values from the authors' workbook.
- Verify all extracted Biot values from `1-K/K_s'` to roundoff.
- Verify the implicit tangent against centered finite differences.
- Verify the global PETSc Jacobian with state-dependent Biot coupling.
- Recover `B=1-K/K_s` in the small-strain limit.
- Run the pressure-path study for HT14, SP14, and SP30 and report RMSE, maximum
  absolute error, and bias against the published data.
- Build the manuscript and inspect the resulting PDF before completion.

