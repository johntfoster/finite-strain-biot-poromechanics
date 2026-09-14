> Historical design note, superseded by the current manuscript and [formulation consistency report](../validation/formulation_consistency_2026-09-14.md).

# Derivation / notation audit: plastic driving stress and the implicit Biot coefficient

Status: Phase-1 work in progress (Part A–D derived and source-anchored; Part E
remaining). Proposal for review.
Date: 2026-09-04.
Sources: this repo (`nonlinear_biot_ad_implementation`, sections cited as
`repo`), `multicomponent_reactive_flow` (`sections/multicomponent_solids.tex`,
cited as `MC:line`), `nonassociated_plasticity` (`main.tex`, cited as `NA:line`).

## A. Terminology conflict (must be resolved in the manuscript)

The two papers use "distension" for different objects. This is the first thing
a reader will trip on.

- This repo: `mineral distension` $\bar J = \bar\rho_{s0}/\bar\rho_s$
  (intrinsic-density ratio; the local solved volume state). Elastic closure
  gives $\bar J(p,J)$ from the mineral EOS.
- `multicomponent_reactive_flow` / `nonassociated_plasticity`: **distension
  tensor** $\mbf A_s$ is the pore-space allocation map, $\mbf F=\mbf A_s\bar{\mbf F}_s$,
  $a_s=\det\mbf A_s$; the **true deformation** $\bar{\mbf F}_s$ (with
  $\bar J_s=\det\bar{\mbf F}_s$) is the mineral's own deformation.

Clean correspondence in the closed ($\mc C_s=0$), non-reacting, no-stress-free
($\mbf A^0=\bar{\mbf F}^0=\mbf I$) single-solid/water limit:

| Theory symbol | This-repo equivalent | Meaning |
|---|---|---|
| $\bar{\mbf F}_s$, $\bar J_s=\det\bar{\mbf F}_s$ | $\bar J=\bar\rho_{s0}/\bar\rho_s=\det\bar{\mbf F}^e$ | mineral (true) volume |
| $\mbf A_s$, $a_s=\det\mbf A_s$ | $a=J/\bar J=\phi_{s0}/\phi_s$ | pore-space allocation |
| $J=a_s\bar J_s$ | $J$ | aggregate Jacobian |
| $a_s\phi_s\bar\rho_{s0}=\phi_{s0}\bar\rho_{s0}+\mc C_s$ | $\phi_s=\phi_{s0}\bar J/J$ | solid mass / volume fraction |
| $\det\bar{\mbf F}_s^p=1$ | isochoric mineral plasticity | $\bar\rho_s$ elastic-only |

Recommended manuscript wording: reserve **distension** for $\mbf A$
(pore-space allocation, whose plastic part $a^p$ maps to $\phi_s$ per the
author decision), and call $\bar J=\det\bar{\mbf F}$ the **mineral (true)
volume ratio**, or rename to avoid the collision with existing eqs. 5–6 in
`finite_deformation_biot.tex`.

## B. Kinematic elastic–plastic split (import, single-solid/water reduction)

From `MC:223`–560 (`sec:MC_solid_kinematics`):

$$
\mbf F=\mbf A\bar{\mbf F},\qquad J=a\bar J,\qquad
\mbf A=\mbf A^e\mbf A^p,\qquad
\bar{\mbf F}=\bar{\mbf F}^e\bar{\mbf F}^p,
$$
$$
\det\bar{\mbf F}^p=1\quad(\text{isochoric true-plastic}),
\qquad
\bar J=\det\bar{\mbf F}=\det\bar{\mbf F}^e .
$$

- $\bar{\mbf F}^p$, $\mbf A^p$ are plastic internal variables; $\bar{\mbf F}^0$,
  $\mbf A^0$ (stress-free maps) are dropped in the isothermal, fixed-composition
  single-solid/water reduction.
- Dependent elastic factors: $\bar{\mbf F}^e=\bar{\mbf F}(\bar{\mbf F}^p)^{-1}$,
  $\mbf A^e=\mbf A(\mbf A^p)^{-1}$.
- Mass: $J\phi_s\bar\rho_s=\phi_{s0}\bar\rho_{s0}$ (closed); true conservation
  $\bar J\bar\rho_s=\bar\rho_{s0}$; hence
  $\phi_s=\phi_{s0}/a=\phi_{s0}\bar J/J$ (`MC:340`–360). Distension rate
  $\dot a/a=\nabla_{\mbf x}\!\cdot\!\mbf v+\dot{\bar\rho}_s/\bar\rho_s$
  (`MC:365`).
- Density rate: $\dot{\bar\rho}_s/\bar\rho_s
  =-\operatorname{tr}[\dot{\bar{\mbf F}}^e(\bar{\mbf F}^e)^{-1}]$ (isochoric
  plastic, no stress-free map) (`MC:380`).

Consequence for the repo: the local volume state $\bar J$ remains the **elastic**
true determinant $\det\bar{\mbf F}^e$; isochoric plasticity does not add a
scalar volume variable, but the **elastic true deformation becomes tensorial**
(deviatoric elastic mineral strain), which the repo's current isotropic elastic
closure does not contain (see Part E, decision R1/R2).

**Author decision (recorded):** the plastic distension is a **scalar** $a^p$,
so $\mbf A^p=(a^p)^{1/3}\mbf I$ is spherical. Under the Flory closure the total
distension $\mbf A=a^{1/3}\mbf I$ is spherical, hence $\mbf A^e$ is spherical as
well; the distension factor carries only volumetric pore-allocation and all
deviatoric elastic/plastic content lives in the true deformation $\bar{\mbf F}$.
The distension flow rule then reduces to a scalar (volumetric) law driven by
the spherical part of $\bs\sigma'$.

## C. Dissipation and the plastic driving stresses (import)

From `MC:3325`–3980 (`residual inequality`, `plastic-flow closures`): the
residual dissipation carries two solid plastic powers

$$
\frac{1}{\theta}\Big[
\bs\sigma':\mbf A^e\dot{\mbf A}^p(\mbf A^p)^{-1}(\mbf A^e)^{-1}
+\operatorname{tr}\big[\mbf S\,\dot{\bar{\mbf F}}^p(\bar{\mbf F}^p)^{-1}\big]
\Big],
$$
with the deviatoric true-plastic driving stress (`MC:3331`)
$$
\mbf S
=(\bar{\mbf F}^e)^{-1}\mbf A^{-1}
\Big(\operatorname{dev}\bs\sigma'\Big)\mbf A\,\bar{\mbf F}^e,
\qquad \operatorname{tr}\mbf S=0 .
$$

Key results:
1. **Distension power is driven by $\bs\sigma'$** (single-prime, fixed intrinsic
   density); **true-plastic power by $\operatorname{dev}\bs\sigma'$** through
   $\mbf S$.
2. Associated flow rules with nonnegative mobilities (`MC:3912`):
   $\dot{\bar{\mbf F}}^p(\bar{\mbf F}^p)^{-1}=\Lambda_{\bar{\mbf F}}\mbf S^T$
   (isochoric since $\operatorname{tr}\mbf S=0$), and
   $\dot{\mbf A}^p(\mbf A^p)^{-1}=\Lambda_{\mbf A}(\mbf A^e)^T\bs\sigma'(\mbf A^e)^{-T}$,
   plus hardening $\dot{\mbf p}=\mbf g(\cdot)$.
3. Coupled/non-associated laws are admissible when the combined power stays
   nonnegative; compressive dilation makes the distension power negative and is
   supported by positive true-plastic dissipation; a shared rate constraint and
   stress-dependent dissipation yield normality in generalized-force space that
   projects as a non-associated pressure-dependent rule after reduction to
   true-stress space (`MC:3973`, Collins–Houlsby). This is the bridge to the
   `nonassociated_plasticity` Drucker–Prager correspondence (`NA:584`–770).

## D. Placement of $B$ and $\bs\sigma'$ in this repo (derived)

Repo relations (`finite_deformation_biot.tex`, eqs. 14–16):
$$
\bs\sigma=\bs\sigma''-Bp\mbf I,
\qquad
\bs\sigma'=\bs\sigma''+(1-B)p\mbf I,
$$
$B=1-\phi_{s0}\,\partial\bar J/\partial J|_{p,J\rho_s,\mathcal H}$. The yield
and flow are written in $\bs\sigma'$ (deviatoric part for the isochoric
mechanism via $\mbf S$, full $\bs\sigma'$ for the distension mechanism). Since
$\bs\sigma'$ needs $B$, and $B$ needs the plastic state (active tangent), the
local problem is the coupled implicit system:

- State $\mbf y=(\bar\rho_s,\ \bar{\mbf F}^p\text{ or }\bar{\mbf F}^e,\ a^p,\ \mbf p,\ \ldots)$.
- Residuals $\mbf R(\mbf y;J,p,J\rho_s,\mathcal H_n)=\mbf0$: (i) intrinsic
  pressure equilibrium / mineral EOS; (ii) active isochoric yield +
  consistency; (iii) active distension yield + consistency; (iv) flow rules /
  hardening.
- Implicit tangent
  $\partial\mbf y/\partial J|_{p,J\rho_s,\mathcal H_n}
  =-\big(\partial\mbf R/\partial\mbf y\big)^{-1}\partial\mbf R/\partial J$
  on the active set (repo eqs. 34–36), then
  $B=1-\phi_{s0}\,\partial\bar J/\partial J|_{p,J\rho_s,\mathcal H_n}$, and
  $\bs\sigma'=\bs\sigma''+(1-B)p\mbf I$ reconstructs the driving stress.

Elastic limit recovery (audit check): with $\bar{\mbf F}^p=\mbf I$,
$a^p=1$, $\mbf p$ frozen, the system must collapse to the repo's elastic local
residual (eq. 38) and closed form (eq. 28). This is the "elastic as the
inactive-mechanism limit" that can replace the bolted-on Legendre potential
(eq. 29). Derivation of the exact collapse is part of Part E-1.

### D.1 Observable vs. driving picture (author observation, to frame the
theory)

Two conjugate pairs coexist: the **observable** pair
$(\bs\sigma'',\ \mbf F^p_{\rm agg})$ where $\bs\sigma''$ is the drained
(fixed-pressure) stress a drained experiment measures and $\mbf F^p_{\rm agg}$
is the observable (aggregate) plastic strain, and the **driving** pair
$(\bs\sigma',\ \{\bar{\mbf F}^p,a^p\})$ from the dissipation analysis. In the
$B=1$ limit $\bs\sigma'=\bs\sigma''$, which is why the literature's effective
stress calibrations work. When $B\neq1$ the implicit, plastic-state-dependent
$B$ maps between them, e.g.
$\frac13\operatorname{tr}\bs\sigma'=\frac13\operatorname{tr}\bs\sigma''+(1-B)p$.
Observable plastic strain is proposed as the drained-frame aggregate split
$\mbf F=\mbf F^e\mbf F^p$ (drained elastic response defines $\mbf F^e$), with
$\det\mbf F^p=a^p$ (volumetric, porosity) plus the deviatoric part inherited
from the isochoric mechanism; relating it to the internal variables is an
$B$-mediated map. Task: reframe §2.4 and the demonstration around this
two-picture statement and state the observable-plastic-strain definition.

## E. Imported results (E-2, E-3 now done) and remaining work

### E-2. Biot–Terzaghi momentum and the $\sigma''\to\sigma'$ reconstruction
(`MC:4936` ff., `sec:MC_phase_overall_momentum_biot`)

- Single-solid/water reduction (drop electrical terms, set $\bar p_E\to p$):
  the solid momentum uses $\bs\sigma''+\phi(1-\bar B)p\mbf I$; the aggregate
  roll-up gives $\bs\sigma'=\bs\sigma''+\big(1-\sum_s\phi_s(1-\bar B_s)\big)p\mbf I$
  with $B=1-\sum_s\phi_s(1-\bar B_s)$; single-solid limit $B=1-\phi(1-\bar B)$.
- Direct statement to quote: *"Plastic flow remains conjugate to
  $\bs\sigma_s'$. A constitutive model calibrated with the fixed-pressure
  stress $\bs\sigma_s''$ must first use [the phase Biot split] to reconstruct
  $\bs\sigma_s'$."*
- Reconciliation task (for E-6): show the repo's
  $B=1-\phi_{s0}\,\partial\bar J/\partial J|_{p,J\rho_s,\mathcal H}$ is the
  single-solid specialization of $B=1-\phi(1-\bar B)$, i.e. map
  $\phi_{s0}\,\partial\bar J/\partial J|_p \leftrightarrow \phi(1-\bar B)$.

### E-3. Scalar-distension simplifications (imported; validates the author
decision) (`MC:5856` ff., `sec:MC_scalar_distension_simplifications`)

- Spherical factors $\mbf A^e=(a^e)^{1/3}\mbf I$, $\mbf A^p=(a^p)^{1/3}\mbf I$;
  $a=a^ea^pa^0$; $\mbf F=a^{1/3}\bar{\mbf F}_s$, $J=a\bar J_s$.
- Isotropic distension factors cancel from the stress push-forward:
  $\bs\sigma_s'=\rho_s\,\partial\psi_s/\partial\bar{\mbf F}_s^e\,(\bar{\mbf F}_s^e)^T$
  (the single-prime stress is entirely the true-deformation conjugate).
- Scalar distension conjugate (trace restriction):
  $\frac13\operatorname{tr}\bs\sigma_s'=\rho_s\,\partial\psi_s/\partial a_s^e\,a_s^e$,
  with double-prime form
  $\frac13\operatorname{tr}\bs\sigma_s''
  =\rho_s\,\partial\psi_s/\partial a_s^e\,a_s^e-\phi_s(1-\bar B_s)\bar p_E$.
- Scalar plastic-distension power
  $\sum_s\frac13\operatorname{tr}(\bs\sigma_s')\,\dot a_s^p/a_s^p$, and the
  associated flow rule
  $\dot a_s^p/a_s^p=\Lambda_{\mbf A}(\mc X_s,\mbf p_s)\,\frac13\operatorname{tr}\bs\sigma_s'$.
  Scalar plastic distension = hydrostatic compaction/dilation with the mean
  single-prime stress as its conjugate force (the volumetric/cap mechanism of
  the combined Drucker–Prager-type model).

### Remaining work

E-1. Derive the elastic-limit collapse (Part D) in repo notation; confirm it
reproduces repo eqs. 27–28 and the fixed-pressure `W''` (eq. 29) as a limit;
reconcile repo $B$ with the MC single-solid $B=1-\phi(1-\bar B)$.
E-4. Reproduce the Drucker–Prager correspondence from `nonassociated_plasticity`
(`NA:421`–874: independent mechanisms and consistency `NA:487`–570; coupled DP
`NA:584`–770; finite-deformation extension `NA:874`–970) to state the combined
model used by the demonstration, in $\frac13\operatorname{tr}\bs\sigma'$
(volumetric/distension) and $\operatorname{dev}\bs\sigma'$/$S$ (isochoric)
invariants.
E-5. Structural route (working assumption, author can override): present the
general split (R1, full $\bar{\mbf F}^e$ stored energy) in the theory; use the
reduced-aggregate route (R2) for implementation/demonstration with the repo's
$W_0(K,G)$ deviatoric elasticity and the scalar $a^p\to\phi_s$ plastic variable.
E-6. Produce the manuscript edit list (notation pass; new inelastic section;
revised local system with scalar $a^p$ and isochoric mechanism; plastic $B$
demonstration showing a $\sigma''$-driven or $B=1$ yield mis-predicts flow),
the MOOSE object map, and the validation plan (elastic oracle + plastic $B$).
