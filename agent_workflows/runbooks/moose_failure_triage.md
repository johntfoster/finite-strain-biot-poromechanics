# MOOSE Failure Triage Runbook

Diagnose in layers and stop at the first layer explaining the failure.

1. **Input syntax:** blocks, parameters, paths, registrations, and include order.
2. **Missing objects:** confirm required parent MOOSE objects exist; do not
   invent input syntax for planned objects.
3. **Variable/material consistency:** AD properties, units, solid-reference
   measures, phase/component indices, Q2 displacement, and P1+P0 EG pressure.
4. **Solver/executioner:** tolerances, scaling, preconditioning, time step, and
   nonlinear/linear convergence.
5. **Discretization/stabilization:** FE spaces, EG volume/facet/BC operators,
   mesh compatibility, and any added stabilization.
6. **Model assumptions:** closures, boundary/initial conditions, held-fixed
   variables, and validation target.

Report the first failing layer, exact symptom, controlling file/object, narrow
fix, and affected track.
