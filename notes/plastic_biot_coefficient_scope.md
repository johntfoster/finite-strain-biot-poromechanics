> Historical design note, superseded by the current manuscript and [formulation consistency report](../validation/formulation_consistency_2026-09-14.md).

# Scope note: plastic driving stress and the implicit Biot coefficient

Status: proposal for review — not authoritative.
Date: 2026-09-04.
Owner: nonlinear-Biot manuscript + MOOSE implementation (this repository), with
the source constitutive model drawn from the sibling `nonassociated_plasticity`
theory and the phase-level driving-stress result drawn from the
`multicomponent_reactive_flow` theory.

## Confirmed decisions (from discussion)

- The **plastic demonstration lives in this paper** (extend it now), not in a
  companion repository.
- Source content: **cite the sibling `nonassociated_plasticity` theory** (the
  mechanism-resolved model) and **include the complete plastic-split derivation
  from the sibling `multicomponent_reactive_flow` theory**, attributed and
  adapted to the single-solid, single-fluid reduction.
- The inelastic demonstration uses **skeleton plasticity**: an isochoric
  true-plastic mechanism (mineral/solid-phase plastic flow) **plus** a plastic
  distension mechanism (volumetric), whose **combined** flow rules mimic a
  Drucker--Prager-type model. The mineral (intrinsic) plasticity is isochoric:
  $\det\bar{\mbf F}^{p}=1$, so intrinsic solid density changes only
  elastically.

### Resolved audit answers (author)

1. **`a^p` maps to $\phi_s$**: plastic distension is the inelastic
   porosity/volume-fraction mechanism (elastic part $a^e$ is the reversible
   pore-space response; $a^p$ locks in permanent pore-volume change).
2. **$B$-evolution channel (a)** and the demonstration uses the **combined
   Drucker--Prager-style model**: $B$ moves through the plastic-modified
   stress/confining path at fixed $p$ (the mineral being elastic-only), and the
   yield/flow is the combined two-mechanism construction.
3. **Derive it**: the deviatoric driving-stress reduction and its mapping into
   this repo's notation are to be derived in the audit (not taken as input).
4. **Plastic distension is a scalar**: $a^p$ is a single scalar internal
   variable; $\mbf A^p=(a^p)^{1/3}\mbf I$ is spherical. Under the Flory closure
   the total distension $\mbf A=a^{1/3}\mbf I$ is spherical, so the distension
   factor carries only volumetric pore-allocation, and the elastic distension
   $\mbf A^e$ is spherical as well. All deviatoric elastic and plastic content
   therefore lives in the true deformation $\bar{\mbf F}$.
5. **Observable vs. driving stress (key conceptual framing):** the observable
   stress in experiments is the drained (fixed-pressure) double-prime
   $\bs\sigma''$, not the single-prime $\bs\sigma'$; the literature maps yield
   and flow to the effective stress because in the $B=1$ limit
   $\bs\sigma'=\bs\sigma''$. When the mineral is compressible the two differ by
   $(1-B)p\mbf I$, and the implicit, plastic-state-dependent $B$ is the bridge
   between a model calibrated in drained observables and the thermodynamic
   driving picture. Observable plastic strain must also be defined: proposed
   definition is the drained-frame aggregate split $\mbf F=\mbf F^e\mbf F^p$
   with $\det\mbf F^p=a^p$ plus the deviatoric contribution inherited from the
   isochoric mechanism, rather than the internal variables only.
- The plastic driving stress is the **single-prime** stress
  $\bs\sigma'$ (fixed intrinsic density), per the dissipation analysis in the
  multicomponent theory. Going from the **double-prime** skeleton stress
  $\bs\sigma''$ (fixed pressure, the stress used in momentum) to
  $\bs\sigma'$ requires the Biot coefficient
  $\bs\sigma'=\bs\sigma''+(1-B)p\mbf I$.
- $B$ is itself a fixed-pressure constitutive tangent,
  $B=1-\phi_{s0}\,\partial\bar J/\partial J|_{p,J\rho_s,\mathcal H}$, which in
  the plastic regime is only defined by implicit differentiation of the active
  local constitutive system. Thus $B$ is required to *define* the plastic
  driving stress, and the plastic state is required to *compute* $B$: the two
  are solved together.

## Thesis of the broadened paper

The correct plastic driving stress in finite-deformation poroplasticity is the
single-prime effective stress $\bs\sigma'$, and evaluating it requires the
implicit Biot coefficient. We construct $B$ from the active local system
(return mapping + implicit tangent), and demonstrate the construction for an
elastic closure (closed-form oracle) and a Drucker--Prager-type plastic
closure built from distinct isochoric true-plastic and plastic-distension
mechanisms.

Contributions that this adds beyond the current paper (elastic verification of
a general implicit-AD architecture):
1. State the dissipation argument that plastic work is driven by (deviatoric)
   $\bs\sigma'$ and by the distension-conjugate pair, and that the Biot
   transform $\sigma'=\sigma''+(1-B)p\mbf I$ is what makes the poroplastic
   yield/flow problem well-posed when the mineral is compressible.
2. Show $B$ as an implicit, history-dependent quantity that cannot be replaced
   by an elastic modulus ratio once plasticity is active.
3. Give a concrete inelastic local system (two-mechanism return mapping) and a
   finite-element demonstration computing $B$ elastically and plastically from
   the same implicit path.

## Notation used here (this repository)

- $\mbf F$, $J=\det\mbf F$: aggregate skeleton deformation and Jacobian.
- $\bar J=\bar\rho_{s0}/\bar\rho_s$: mineral distension (intrinsic-density
  ratio).
- $p$: common intrinsic pressure (water and solid), $\bar p_s=\bar p_f=p$.
- $\phi_s=\rho_s/\bar\rho_s$, $\phi_f=1-\phi_s$: solid/fluid volume fractions;
  $\phi_{s0}$ reference solid volume fraction; $J\rho_s$ referential solid mass.
- $\bs\sigma''$: drained skeleton stress, fixed-$p$ (double prime); enters
  momentum as $\bs\sigma=\bs\sigma''-Bp\mbf I$.
- $\bs\sigma'=\bs\sigma''+(1-B)p\mbf I$: single-prime effective stress, fixed
  intrinsic density; the plastic driving stress.
- $\mathcal H_n$: previous constitutive history.

## Source model to import (sibling `nonassociated_plasticity`)

Kinematics $\mbf F=\mbf A\bar{\mbf F}$ with elastic--plastic splits
$\mbf A=\mbf A^e\mbf A^p$ and $\bar{\mbf F}=\bar{\mbf F}^e\bar{\mbf F}^p$;
isochoric true-plastic flow $\det\bar{\mbf F}^{p}=1$; all plastic volume change
assigned to the distension factor $\mbf A^p$. Under the Flory closure
$\mbf A=a^{1/3}\mbf I$ with $a=\det\mbf A$ and $a^p=\det\mbf A^p$.

- Deviatoric (isochoric) mechanism: associated flow on a deviatoric yield
  surface $f_d=0$, driven by the deviatoric part of $\bs\sigma'$ mapped through
  the distension and elastic true-deformation factors (Drumheller
  construction).
- Volumetric mechanism: plastic distension $\dot a^p$ governed by its own yield
  condition and consistency.
- Combined response: the two associated mechanisms give an overall flow rule
  not normal to either surface — apparent non-associativity that reproduces
  Drucker--Prager yield with a distinct plastic potential (friction from the
  isochoric mechanism, dilation from the distension mechanism).

Mapping questions to resolve in the derivation audit (single-phase theory
$\rightarrow$ two-phase poromechanics):
1. Relation between the kinematic distension factor $\mbf A$ of the sibling and
   the porous measures here: which object carries the plastic volume change
   ($a^p \leftrightarrow \phi_s$ / porosity, or a separate mesoscale volume)?
2. With isochoric mineral plasticity, $\bar\rho_s$ remains on the elastic
   mineral EOS. Confirm the two channels by which $B$ then evolves:
   (a) the plastic/hardening part of the skeleton stress alters the
   confining/contact term that drives $\bar J$ at fixed $p$;
   (b) the plastic distension mechanism changes porosity / the volume assigned
   to the solid, changing $\phi_s$ and hence the storage/accumulation terms.
   Decide which channel the demonstration must isolate or whether both appear.
3. How the aggregate single-prime stress used in the yield function is formed
   from the intrinsic phase stress (volume-fraction weighting) and how the
   deviatoric driving stress (Drumheller map) reduces in the single-solid,
   single-fluid setting.
4. How the yield function and plastic potential are written in invariants of
   $\bs\sigma'$ so that the implementation consumes $B$ (via
   $\sigma'=\sigma''+(1-B)p\mbf I$).

## Coupled local system and implicit $B$

Local state $\mbf y=(\bar\rho_s,\ \mbf F^{p}\text{-equivalent},\ a^p,\ \text{hardening vars})$;
local residual system
$\mbf R(\mbf y;J,p,J\rho_s,\mathcal H_n)=\mbf0$ containing: the intrinsic
pressure equilibrium / mineral EOS; the active deviatoric yield + consistency;
the active distension yield + consistency; and the flow rules. $B$ is then
$B=1-\phi_{s0}\,\partial\bar J/\partial J|_{p,J\rho_s,\mathcal H_n}$ with the
derivative obtained from the converged implicit solve
$\partial\mbf y/\partial J=-(\partial\mbf R/\partial\mbf y)^{-1}\partial\mbf R/\partial J$
on the active set. $\bs\sigma'$ for the yield/flow is reconstructed with this
$B$, closing the loop.

## Manuscript impact (this repository)

- Reframe §2/§3 so the inelastic local system (return mapping + active-set
  implicit tangent) is the subject; present elasticity as the inactive-mechanism
  limit (may replace the bolted-on fixed-pressure Legendre potential `W''`, eq.
  29, with an emergent elastic limit).
- Add a section on the correct plastic driving stress in poroplasticity
  (single-prime $\bs\sigma'$, Drumheller isochoric mechanism, distension
  volumetric mechanism, apparent non-associativity / Drucker--Prager
  correspondence) citing `multicomponent_reactive_flow` (driving-stress
  derivation), Drumheller, Collins--Houlsby, and `nonassociated_plasticity`
  (mechanism-resolved model).
- Extend §3 with the concrete two-mechanism plastic material and the implicit
  $B$ path; extend validation with an elastic oracle and a plastic $B$
  demonstration showing $B$ evolving with plastic strain and showing that a
  $\sigma''$-driven (or $B=1$ Terzaghi) yield mis-predicts the flow.

## MOOSE implementation impact (this repository, sync contract)

- New/updated materials implementing the two-mechanism return mapping with AD,
  consuming $\bs\sigma''$/$p$ and returning $\bs\sigma'$, plastic state, and
  the implicit $B$; kernels unchanged in principle (weak-form residual objects
  consume AD material properties).
- Update `validation/equation_to_moose_map.yml`,
  `validation/theory_traceability.yml`, and the sync manifest/state.
- New verification: local implicit-tangent checks (analytical/centered
  difference) for the plastic active set; PETSc Jacobian comparison; an
  elastic--plastic boundary-value problem (e.g., yield-inducing extension of the
  Mandel/compression continuation) with a Drucker--Prager-type response.

## Cross-track ownership

- Manuscript (theory reframe, driving stress, $B$ implicit, plastic
  demonstration): this repo.
- Source constitutive model: sibling `nonassociated_plasticity` (mechanism
  split) and `multicomponent_reactive_flow` (phase-level driving stress and the
  complete plastic-split derivation). No changes are assumed in the siblings;
  this repo cites them and includes the attributed, reduced derivation.
- MOOSE implementation + validation: this repo.

## Derivation blocks to import (anchors in `multicomponent_reactive_flow`,
`paper/main.tex` is not the root there; `sections/multicomponent_solids.tex`)

1. Kinematic elastic--plastic split and solid state variables,
   `multicomponent_solids.tex:223`--560 (F = A F̄; A^e/A^p and F̄^e/F̄^p;
   isochoric true-plastic flow; Drumheller construction).
2. Free-energy/Coleman--Noll restriction and the residual inequality fixing
   the plastic driving stress, `multicomponent_solids.tex:3325`--3400.
3. Plastic-flow closures (separate dissipative powers, mobilities,
   shared-rate/coupled options), `multicomponent_solids.tex:3909`--3980.
4. Solid-phase and overall momentum from the Biot--Terzaghi effective-stress
   split (single vs. double prime), `multicomponent_solids.tex:4936` ff.
5. Scalar distension simplifications, `multicomponent_solids.tex:5856` ff.

## Phased plan (proposal)

1. Derivation/notation audit: map $\sigma'/\sigma''/B/\bar J/\phi$ and the
   sibling $\mbf A,\bar{\mbf F}$ split through the current §2--§3 and the
   theory paper; resolve the four mapping questions above.
2. Write the scoping into the manuscript (outline + notation) without touching
   verified content yet; rebuild and re-run all audits.
3. Implement the plastic material + implicit $B$ in MOOSE; local tangent and
   Jacobian verification.
4. Elastic + plastic demonstrations and figures; update provenance and
   validation records.
5. Narrative and prose review of the extended paper (plasticity lives in this
   paper per decision).

## Open decisions for the author

- Confirm the $B$-evolution channel(s) in mapping question 2 (plastic/hardening
  contact term at fixed $p$ vs. plastic-distension porosity change, or both).
- Confirm the demonstration vehicle (Mandel-family extension vs. new
  boundary-value problem).
- Confirm which `multicomponent_reactive_flow` blocks are included as an
  attributed reduction vs. cited-only, to keep the single-solid/water paper
  self-contained without reproducing the general multicomponent derivation.
