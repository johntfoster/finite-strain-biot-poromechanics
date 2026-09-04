# MOOSE implementation plan: Drucker-Prager-type poroplasticity with implicit B

Status: plan for the rate-independent backward-Euler AD return-mapping prototype
(option (i), committed in manuscript Sec. 2.5-2.6 and Sec. 3).
Date: 2026-09-04.  Owner: nonlinear-Biot MOOSE app (`moose_app/`), Biot-side
patch until imported through the shared-source master.
Authoritative theory: manuscript `finite_deformation_biot.tex` Sec. 2.4-2.6 and
`implicit_ad_implementation.tex` Sec. 3; model spec `plastic_biot_model_spec.md`
(Sec. 1b, 3, 3b, 5); validated equations map in `validation/equation_to_moose_map.yml`.

## 0. Registration and shared-source facts (verified)

- The application is `NonlinearBiotADApp` (binary `nonlinear_biot_ad-opt`), but
  `registerAll` registers objects under the label `MulticomponentReactiveFlowApp`
  (`Registry::registerObjectsTo(factory, {"MulticomponentReactiveFlowApp"})`) and
  `registerKnownLabel` lists both.  Shared-style sources in this repo therefore
  call `registerMooseObject("MulticomponentReactiveFlowApp", Class)`.
- New `moose_app/` sources build automatically (wildcard); they are not in
  `moose/sync_manifest.json` until deliberately shared.  Keep the new material
  Biot-side for now; sharing is a separate `tools/sync_biot_moose.py` step.
- Do not weaken or redefine existing tests (AGENTS.md).  The elastic Mandel
  results are the E-1 collapse oracle and must be reproduced by the new material
  in its inactive-yield limit.

## 1. Existing architecture (what the prototype plugs into)

- `ADLocalElasticMineralBiotMaterial`: value/residual *provider*.  At the
  quadrature point it computes intrinsic-density ratio (mineral EOS),
  phi_s, and publishes the local material-mass and mineral-EOS residuals plus
  their partial derivatives wrt the state and wrt J (fixed referential solid
  mass).  Registration app label as above.
- `ADConstrainedSkeletonBiotMaterial`
  (`DerivativeMaterialInterface<Material>`): generic fixed-pressure tangent
  assembler.  It does NOT Newton-solve R(y)=0; it assumes the state y is already
  determined (algebraically, by providers) and solves only the linearized
  tangent `R_y * dy/dJ = -R_J` by AD Gaussian elimination
  (`solveImplicitTangent`), then publishes
  `B = 1 - (d/dJ)(J*phi/accumulation)/v0` (repo eq. 35-37 equivalents).
- Supporting: `ADSolidReferenceKinematics` (J_s), `ADBinarySolidSpatialMassMaterial`,
  drained/volumetric skeleton stress materials feeding sigma'' and its
  volumetric part; kernels consume AD material properties (momentum, mass
  storage, Darcy flux).
- Consequence: the elastic case has no true implicit unknown.  Poroplasticity
  introduces one (the integrated plastic increment Delta_gamma; plus Fbar^p/a^p
  updates and hardening), so the fixed-pressure local solve must become a real
  Newton on R(y)=0 before the tangent is taken.

## 2. Design choice (route A, recommended for the prototype)

Self-contained AD poroplastic material that performs the return mapping
internally, following the MOOSE `ADSingleVariableReturnMappingSolution` pattern
(rate-independent backward-Euler: elastic predictor, trial f; if f<=0 the step
is elastic and Delta_gamma=0; else Newton on the scalar discrete-consistency
residual f(sigma'(Delta_gamma), p, H_{n+1})=0 in AD types).  It declares, as AD
properties with full AD dependency, the single-prime driving stress
sigma' = sigma'' + (1-B) p I (manuscript eq:single-prime-...), the implicit
B of the active local system, a^p, and diagnostics (yield f, Delta_gamma).

- E-1 collapse requirement: with yield inactive (Delta_gamma=0, a^p=1) the
  material must reproduce, to the existing Mandel tolerances, the B and sigma''
  of `ADLocalElasticMineralBiotMaterial` + `ADConstrainedSkeletonBiotMaterial`.
  A dedicated poroplastic Mandel deck with a very high yield limit (or a
  single-element unit test) is compared against the existing reference CSVs
  (`mandel_pressure_profiles.csv`, `mandel_displacement_profiles.csv`).
- The route keeps `ADConstrainedSkeletonBiotMaterial` untouched for the elastic
  verification path; the poroplastic deck routes momentum/storage through the
  new material's properties.

Route B (defer): extend the generic assembler to iterate Newton on an augmented
R(y)=0 (add plastic residual providers and state-derivative lists).  More
intrusive and harder to validate; only pursue if route A cannot express the
active-set tangent cleanly.

## 3. Local state and residuals (mapping to manuscript equations)

Active-set local system at fixed (p, J*rho_s, H_n), state y = (rho_bar_s, a^p,
Delta_gamma, [Fbar^p or reduced equivalent], [hardening]):
  (i)   mineral-EOS / pressure equilibrium (elastic mineral, existing);
  (ii)  solid material mass (existing);
  (iii) volumetric scalar flow eta-dot = beta gamma-dot, i.e.
        ln(a^p/a^p_n) = beta*Delta_gamma  (reconstruction eq:reconstruct-pore-allocation);
  (iv)  discrete consistency f(sigma'(Delta_gamma),p,H_{n+1}) = 0 on the active
        set (eq:discrete-consistency), with Kuhn-Tucker eq:kuhn-tucker selecting
        active/inactive.
The driving invariants p', q' come from the single-prime Kirchhoff/Mandel
measures (eq:single-prime-kirchhoff-stress .. eq:finite-plastic-stress-invariants);
q''=q', p' = p''-(1-B)p in the observable form (eq:dp-yield-observable).
B follows from the fixed-pressure tangent of this converged system (repo eq. 37).

## 4. Objects to add (first prototype, Biot-side)

- `moose_app/include/materials/ADDruckerPragerPoroplasticBiotMaterial.h`
- `moose_app/src/materials/ADDruckerPragerPoroplasticBiotMaterial.C`
  (registerMooseObject("MulticomponentReactiveFlowApp", ...)).
- Test deck under `moose_app/test/tests/poroplastic_biot/`: a drained/undrained
  uniform compression case and an inactive-yield collapse case against the
  existing elastic reference; jacobian test analogous to
  `implicit_biot_q2_q1_jacobian.i`.
- Params (spec defaults): friction slope M (e.g. 1.2), dilation beta (e.g.
  0.4), cohesion 0; drained K, G and mineral K_s, phi_s0 as in the Mandel deck.

## 5. Gates this plan addresses

- E-1 (elastic collapse): the inactive-yield unit/Mandel comparison above gives
  the missing numeric verification.
- E-4 (DP translation into MOOSE): object/residual map above.

## 6. Out of scope for the prototype (later)

10/20/30% platen-compression continuation studies and the Delta-B-vs-elastic
figure; provenance/records update; sharing the new source through the master.
