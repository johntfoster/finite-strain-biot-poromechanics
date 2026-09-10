# Constitutive and manuscript audit

The manuscript will retain plasticity. The verified contribution is the implicit
fixed-pressure Biot tangent and its dependence on the current constitutive state.
An active plastic update must preserve that dependence in the outer Jacobian.
The source inspection and additional MOOSE probes below precede the rewrite.

## Findings in the existing implementation

- `moose_app/src/materials/ADPlasticStateBiotMaterial.C:131` inserts plastic
  distention into the partial-density identity. With its declared intrinsic
  density, this violates `rho_s = phi_s * rhobar_s` when `a_p != 1`.
  An instrumented run of `poroplastic_general_path.i` gives a physical mass
  ratio of 0.985088712164, while the published residual is approximately
  1.1e-16 and the coefficient comparison is zero. The density reconstructed
  from mass is 1.015137 times the EOS density. Agreement between the two
  coefficient implementations therefore does not verify physical consistency.
- `moose_app/src/materials/ADTensorialPoroplasticBiotMaterial.C:173` evaluates
  the coefficient base at total J while evaluating elastic stress at elastic J.
  The trial uses the previous plastic distention, and the reported coefficient
  uses its current value. These are different constitutive states.
- The same material's matrix exponential at line 223 is not the exponential
  of a general symmetric three-dimensional tensor. The load-unload probe gives
  a nonzero error in `log(a_p_new/a_p_old) = beta * Delta_gamma`. Its radial
  stress correction is not followed by reconstruction from the updated elastic
  deformation. An algebraically zero yield function is insufficient evidence
  of a consistent return.
- Current plastic factors are converted to plain values before coefficient
  evaluation. Their active outer AD dependence is lost.
- `validation/scripts/check_poroplastic_b_feedback.py` defines a physical
  `check` function but never calls it; `add_case` returns the supplied literal
  `True`. Its PASS message is not an acceptance check on the stated trends.
- The Mandel implementation uses two local states (normalized intrinsic density
  and solid volume fraction), whereas the manuscript describes one. Residual
  derivatives are written analytically and evaluated with AD scalars. The
  dense tangent solve retains outer AD dependence.
- The manuscript equates thermodynamic pore pressure with mean intrinsic grain
  stress. Foster and Xu distinguish these quantities. The asserted consequence
  that the single-prime stress is deviatoric must be removed.

The original checks have not been weakened or adjusted to conceal these findings.
Probe inputs and raw results are in `.agent-runtime/research/plastic-consistency/`.
The full Mandel verifier passes, as do the existing PETSc Jacobian comparison
and eleven baseline MOOSE application tests. These results support their tested
elastic scope; they do not resolve the plastic findings above.

## Constitutive construction to verify

Use Drumheller's distention gradient A, distention a = det A, and true-deformation
Jacobian Jbar. Preserve F = A Fbar and J = a Jbar. For the selected isotropic
plastic specialization, use F = Fe Fp with det Fp = a_p and isochoric true
plastic flow. Mineral compression depends on Je = J/a_p. Preserve the physical
partial-density identity without an additional plastic multiplier.

Define B from the constrained mineral-volume derivative at fixed pressure,
referential solid mass, and current plastic state. The plastic state remains
active in the outer derivative of the converged constitutive update. These two
operations must be distinguished in the theory and numerical description.

Retain the isotropic skeleton and logarithmic mineral EOS, with a free energy
that generates both. Use the intermediate-configuration Mandel stress as the
plastic work conjugate; its invariants coincide with those of the single-prime
Kirchhoff stress for this isotropic response. Drucker-Prager yield and the
nonassociated dilation rule are constitutive choices. Solve the exponential
increment and yield consistency together, recomputing stress and B at the
updated state. Restrict claims to the admissible smooth cone branch exercised
by verification; do not claim apex, hardening, or general anisotropic response.

## Implementation map before source edits

| Object | Equations and state | Configuration and AD | Verification |
| --- | --- | --- | --- |
| Constitutive material | mass identity, mineral EOS, implicit B, multiplicative flow, yield consistency | Solid reference; symmetric increment in plastic intermediate configuration; current state and local solve retain outer AD | independent density/mass identity, fixed-state centered B derivative, reconstructed stress, yield and flow residuals, active constitutive Jacobian |
| Existing constrained tangent material | R_y y_J = -R_J | AD-valued local dense solve; fixed p, mass and plastic state | analytical and centered derivatives |
| Prescribed-deformation helper | F and J | AD inputs for derivative tests | material Jacobian comparison |
| Material-point driver | load, unload, reload and prescribed pore pressure | homogeneous deformation; no coupled-flow claim | history persistence, return residuals, refinement and feedback comparison |
| Manuscript and figures | verified constitutive response and separate Mandel benchmark | same data in scripts, publication figures and website | source traceability, build and visual inspection |

The existing prototypes and their failed physical assumptions will not be used
as evidence for the corrected model. Independent acceptance tests must measure
the physical identities, rather than encode a desired direction of change in B.

## Verified revision

`ADImplicitPoroplasticBiotMaterial` now implements the current manuscript model.
It is app-local and preserves the archived prototype sources and tests.
The physical mass relation, the EOS evaluated at elastic J, the energy-derived
single-prime stress, the exponential flow increment and yield consistency are
verified independently in `validation/scripts/check_implicit_poroplastic.py`.
The unequal-principal-stretch and superposed-rotation paths also pass. The
active outer AD test passes the original relative tolerance of 1e-7 and
absolute tolerance of 1e-5 after expressing its algebraic probe in consistent
dimensionless stress units; physical units had caused poorly scaled PETSc
finite-difference perturbations. No tolerance was relaxed.

The corrected drained path produces a coefficient below the virgin elastic
value at equal total deformation. The pressure comparison therefore increases
plastic dilation relative to the virgin-coefficient substitution. The manuscript
and new figures report this verified direction of change.

The axisymmetric proportional path has a fixed flow direction and its endpoint
is increment independent to output precision. A separate path with unequal
principal stretches supplies the nontrivial refinement check. These distinct
limits are recorded in `validation/implicit_poroplastic_verification.json`.
The local Newton solver rejects nonfinite residuals and does not implement a
cone-apex branch. Coupled active fluid storage and physical calibration remain
outside the verified scope.
