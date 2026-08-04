# Vision

This repository develops a companion paper to the multicomponent reactive flow
theory. The paper derives and verifies the numerical evaluation of the
finite-deformation nonlinear Biot coefficient, explains the nested implicit and
automatic differentiation scheme used by MOOSE, and constructs reproducible
pressure-controlled nonreacting studies.

The parent multicomponent manuscript remains the source of truth for notation,
material conservation, the fixed-equivalent-pressure Legendre transform, solid
reference kinematics, and the nonlinear Biot stress split. This repository
specializes those equations; it does not create an independent theory.

The work has three coordinated tracks:

1. **Derivation and publication.** Derive the constrained fixed-pressure
   tangent directly from the registered solid-phase/component conservation,
   volume, EOS, and equilibrium statements. Explain the inner local implicit
   solve and the outer MOOSE AD chain rule.
2. **MOOSE implementation and validation.** Trace the implementation to the
   parent theory, verify the local tangent and global Jacobian, recover known
   small-strain limits, and construct a genuine pressure-controlled Q2/EG
   mechanics experiment.
3. **Agent-assisted simulation workflow.** Reuse the parent repository's
   composable input hierarchy, schemas, checks, and failure-triage workflow so
   future agents can assemble auditable nonlinear-Biot experiments.

Lawal and Kim's dunite data provide a pressure-dependent application. Their
reported coefficient is calculated from measured drained and unjacketed
moduli. Fitting the same drained-modulus data therefore supplies a constitutive
calibration and implementation test, not independent validation. A defensible
predictive study must use independent calibration data or a declared
train/holdout design and must solve the pressure-controlled boundary-value
problem rather than prescribe its deformation path.
