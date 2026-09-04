# Plan: nonlinear Biot implicit-AD paper

## Objective

Finish and publish a reproducible paper on the finite-deformation Biot
coefficient computed from the fixed-pressure tangent of solved solid-mass and
mineral-EOS equations.

## Governing problem

- One deformable solid and one water phase.
- Finite-deformation equations on the solid reference configuration.
- Q2 displacement and continuous Q1 water pressure.
- Q2 solid intrinsic-density-ratio and solid-volume-fraction states.
- Solid mass conservation and the mineral EOS solved as residual equations.
- A local implicit fixed-pressure tangent retained in the outer MOOSE AD graph.
- No pressure enrichment, EG facet term, or pressure stabilization.

## Verification sequence

1. Verify the local implicit tangent against its analytical expression and a
   centered fixed-pressure difference.
2. Verify the outer displacement-pressure-solid-state AD path with the pure-Q1
   PETSc Jacobian test.
3. Compare Mandel water-pressure profiles at several times with the analytical
   series.
4. Compare horizontal and vertical displacement profiles with the analytical
   solution.
5. Verify solid-mass and mineral-EOS residuals and pressure/load convergence.
6. Continue to finite deformation and report spatial Biot-coefficient and
   solid-density contours.
7. Rebuild the manuscript and reproduce every reported figure from curated
   source data.

## Repository workflow

- The Biot repository owns the manuscript and agent environment.
- The general simulator repository owns the shared MOOSE implementation.
- `tools/sync_biot_moose.py` provides conflict-detecting pull, push, and check
  operations so code edits made in either workspace appear in both.
- A clean public clone validates the exported hashes without requiring the
  master checkout.
