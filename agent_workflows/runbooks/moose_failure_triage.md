# MOOSE Failure Triage Runbook

Diagnose in layers and stop at the first layer explaining the failure.

1. **Input syntax:** blocks, parameters, paths, registrations, and include order.
2. **Missing objects:** confirm the object exists in `moose_app/` and is listed
   in `moose/sync_manifest.json`; do not invent input syntax.
3. **Variable/material consistency:** AD properties, units, solid-reference
   measures, Q2 displacement, continuous Q1 water pressure, and the two solved
   solid constitutive states.
4. **Solver/executioner:** tolerances, scaling, preconditioning, time step, and
   nonlinear/linear convergence.
5. **Discretization:** Q2/Q1 FE spaces, mesh compatibility, quadrature, and
   boundary conditions. The Mandel deck has no EG enrichment or facet operator.
6. **Model assumptions:** closures, boundary/initial conditions, held-fixed
   variables, and validation target.

Report the first failing layer, exact symptom, controlling file/object, narrow
fix, and affected track.
