> Historical design note, superseded by the current manuscript and [formulation consistency report](../validation/formulation_consistency_2026-09-14.md).

# Constitutive model specification: Drucker-Prager-type poroplasticity with the implicit Biot coefficient

Status: draft spec, to be closed (E-1/E-4) before code.
Date: 2026-09-04.
Purpose: single input for (a) the manuscript theory rewrite and (b) the MOOSE
implementation + 10/20/30% compression / Delta-B study.

## 1. Objective and demonstration

Add an inelastic (poroplastic) closure to the single-solid/water repo whose
plastic response is an isochoric true-plastic mechanism + a scalar plastic pore
allocation a^p that together realize a Drucker-Prager-type surface following
`nonassociated_plasticity`. Demonstrate: 10%, 20%, 30% finite-deformation
compressions; report the plastic Biot coefficient B vs. the elastic model and
plot the difference (Delta B) vs. compression (and/or vs. plastic strain).

## 1b. Canonical plastic notation (SYNCED with manuscript Sec. 2.4-2.6)

Use these symbols ONLY (no plastic multipliers; the rates ARE the unknowns):
- gamma-dot >= 0: isochoric (true-plastic / shear) plastic rate; in the coupled
  Drucker-Prager model it is the single rate (there is no lambda).
- eta-dot := adot^p/a^p: volumetric (pore-allocation) plastic rate
  (>0 dilation, <0 compaction).
- Independent mechanisms (Sec. 2.4): isochoric rate gamma-dot (surface
  f_d = q - q_y, gamma-dot >= 0, gamma-dot f_d = 0); volumetric rate eta-dot
  (surface f_v = p - p_y, compaction branch eta-dot <= 0).
- Coupled DP (shared rate constraint eta-dot = beta gamma-dot):
  f = q - M p <= 0, M = mu + beta; flow L^p = Fdot^p(F^p)^-1 =
  gamma-dot[(3/2) S/q + (beta/3) I]; dissipation D^p = mu p gamma-dot.
- Kuhn-Tucker: gamma-dot >= 0, f <= 0, gamma-dot f = 0; consistency dot f = 0
  when gamma-dot > 0. Time-discrete: solve for Delta-gamma = int gamma-dot dt
  via the discrete consistency f(state(Delta-gamma)) = 0 (return mapping),
  embedded in the Sec-3 local residual system (elastic limit Delta-gamma = 0).

## 2. Stress/measure conventions to reconcile (critical)

- Repo: Cauchy stress tension-positive; water pressure p positive in
  compression; sigma'' = drained skeleton stress (fixed p, tension-positive),
  total sigma = sigma'' - B p I; sigma' = sigma'' + (1-B) p I (fixed rho-bar_s).
- Sibling `nonassociated_plasticity`: compression-positive p = -(1/3) tr sigma,
  q = sqrt(3/2) ||dev sigma||, Kirchhoff at finite strain, Mandel-type
  true-plastic stress; p >= 0, gamma-dot >= 0; cohesionless, no back stress.
- Translation: define the poroplastic driving invariants from sigma' with the
  repo's tension-positive convention. Let p' := -(1/3) tr sigma' (compression
  positive mean driving pressure) and s' := dev sigma', q' := sqrt(3/2)||s'||.
  Recover p'' := -(1/3) tr sigma'' = p' - (1-B)p, so a yield written in sigma'
  becomes one in sigma'' plus an explicit B-correction (the two-picture point).
- Volumetric plastic mechanism is driven by p' (mean sigma'), isochoric
  deviatoric mechanism by s'/q'.

## 3. The DP-type construction (from `nonassociated_plasticity`, carried over)

Rates (no separate plastic multipliers; see Sec. 1b):
  isochoric rate gamma-dot >= 0;  volumetric rate eta-dot := dot a^p/a^p
  (eta-dot > 0 dilation, < 0 compaction);  det Fbar^p = 1;  a = a^e a^p.
  dot Fbar^p (Fbar^p)^-1 = gamma-dot N',  N' = (3/2) s'/q'.
Coupled DP (shared rate constraint eta-dot = beta gamma-dot):
  f = q' - M p' <= 0,  M = mu + beta,  mu >= 0.
Kuhn-Tucker: gamma-dot >= 0, f <= 0, gamma-dot f = 0; dot f = 0 when
gamma-dot > 0.
Plastic power: D^p = q' gamma-dot - p' beta gamma-dot = mu p' gamma-dot >= 0
(requires p' >= 0 during active compressive loading).
Non-associated: flow slope beta in volume, yield slope M = mu + beta.
Observable picture: with p'' = p' - (1-B)p and q'' (deviatoric sigma''), the
same yield reads q' = q'' and p' = p'' + (1-B)p, so f = q'' - M p'' - M(1-B)p;
i.e. an explicit B-correction to a sigma''-formulated Drucker-Prager surface.

## 3b. Finite-deformation driving stress (Kirchhoff/Mandel) and the a^p update (author correction)

The plastic driving stress is NOT the small-strain Cauchy sigma' invariants; at
finite deformation it is a Kirchhoff/Mandel-type measure (brought from the
multicomponent derivation):

- Single-prime intrinsic stress (Kirchhoff-type current-configuration):
  sigma'_s = rho_s dpsi_s/dFbar^e (Fbar^e)^T  (fixed intrinsic density).
- Isochoric mechanism driving stress (Mandel-type):
  S = (Fbar^e)^{-1} dev(sigma'_s) Fbar^e,  tr S = 0.
- Scalar pore-allocation mechanism driven by mean (1/3)tr sigma'_s.
- Invariants: p = -(1/3)tr sigma'_s (compressive), q = sqrt(3/2)||S||.
- DP: f = q - M p <= 0, M = mu+beta; flow rules (single rate gamma-dot):
    dot Fbar^p (Fbar^p)^{-1} = gamma-dot (3/2) S/q  (isochoric, det Fbar^p = 1),
    eta-dot = dot a^p/a^p = beta gamma-dot           (scalar pore allocation)
  D^p = mu p gamma-dot >= 0. Non-associated when mu > 0.
- a^p update is REQUIRED and is exactly the volumetric mechanism:
  eta-dot = dot a^p/a^p = beta gamma-dot, with a = a^e a^p, phi_s = phi_s0/a.
- Small-strain reduction: Fbar^e -> I, S -> dev(sigma'), sigma'_s -> sigma'
  (= sigma'' + (1-B)p I aggregate), recovering f = q' - M p' <= 0 and the
  observable form f = q'' - M[p''-(1-B)p] <= 0.
- Structural consequence: forming q requires the elastic true deformation
  Fbar^e, so the inelastic local state must include Fbar^e (or its deviatoric
  elastic part) in addition to a^p and hardening - i.e., the pure "R2 aggregate
  scalar" route is insufficient for the driving stress; the code must carry the
  elastic true-deformation needed by S. This must be reflected in the local
  system (state y) and in the MOOSE material design.

## 3c. Two-surface derivation then single Drucker-Prager projection; system Biot
coefficient (author refinement)

- Present the FULL two-mechanism derivation from dissipation first (Drumheller /
  multicomponent): two nonnegative plastic powers
    D^p_d = tr[ S Fdotbar^p (Fbar^p)^-1 ] >= 0   (isochoric, driven by Mandel S)
    D^p_v = (1/3) tr(sigma'_s) adot^p/a^p >= 0   (volumetric, driven by mean sigma'_s)
  with each mechanism having its own associated yield surface and advancing at
  its own rate (gamma-dot for the isochoric, eta-dot for the volumetric;
  constant-strength forms: f_d = q - q_y, f_v = p - p_y); independent response
  stays at the corner and compacts.
- THEN show the coupled projection to ONE Drucker-Prager surface
  f = q - M p <= 0, M = mu + beta, single rate gamma-dot, total observable flow
  L^p = gamma-dot[(3/2) S/q + (beta/3) I] (so eta-dot = beta gamma-dot),
  dissipation mu p gamma-dot, non-associated when
  mu > 0. This makes clear where the deviatoric (S) and volumetric (mean sigma'_s)
  driving stresses come from.
- The two internal fields are NOT separately observable; reconstruct after:
  a^p = det F^p (eta-dot = adot^p/a^p = tr L^p = beta gamma-dot),
  Fbar^p = (a^p)^(-1/3) F^p.
- Biot coefficient: do NOT carry a separate "reacting" phase coefficient; use the
  system coefficient B = 1 - phi_s0 dJbar/dJ |_{p,J rho_s,H} (repo eq. 15), which
  the phase form of the multicomponent theory reduces to automatically in the
  single-solid limit. In code B comes from implicit differentiation of the active
  local system.
- Local state consequence (unchanged): forming q requires Fbar^e; local state
  y = (rho-bar_s, Fbar^e-content, a^p, gamma/hardening).

## 4. Reduced aggregate implementation route (R2)

Keep aggregate variables and the repo elasticity:
- Deviatoric elastic response from the drained skeleton W0 (shear G):
  deviatoric sigma'' from deviatoric elastic strain via the repo material.
- Mineral (intrinsic) response elastic-only, volumetric (bulk K_s): rho-bar_s
  (Jbar = det Fbar^e) set by pressure equilibrium (mineral EOS) including the
  skeleton confining term; det Fbar^p = 1 leaves rho-bar_s elastic.
- Volumetric plastic mechanism = scalar a^p; phi_s = phi_s0/a, a = J/Jbar;
  elastic pore allocation a^e = a/a^p (spherical).
Elastic limit: yield off (gamma-dot = 0), a^p frozen at 1; must reproduce the
existing elastic closure exactly (repo eqs. 27-28) - E-1 gate.

## 5. Local system and the implicit B (repo architecture, Sec. 3)

Local state y = (rho-bar_s, a^p, gamma ~ accumulated plastic strain; optional
hardening var). At quadrature point inputs (J, p, J rho_s, history H_n):
Residuals R(y; ...) = 0:
  (i) pressure equilibrium / mineral EOS (elastic-only mineral);
  (ii) isochoric yield-consistency on active set (f = q' - M p' <= 0);
  (iii) volumetric scalar flow eta-dot = beta gamma-dot (a^p allocation) + consistency;
  (iv) flow rule update for Fbar^p (or reduced equivalent) and a^p.
Return mapping selects active set. Then:
  dy/dJ at fixed (p, J rho_s, H) = -(dR/dy)^-1 dR/dJ  (repo eq. 35),
  dJbar/dJ = dJbar/dy . dy/dJ   (eq. 36),
  B = 1 - phi_s0 dJbar/dJ |_{p, J rho_s, H}   (eq. 37).
sigma' reconstructed as sigma'' + (1-B) p I with this B closes the yield.

## 6. Parameter set and compression study

Elastic/Mandel baseline (repo Table): K = 1.0 GPa, G = 0.75 GPa,
K_s = 2.5 GPa, phi_f0 = 0.1, etc.; B0 = 0.6.
DP parameters to choose (cohesionless): friction slope M (= mu+beta) and
dilation slope beta (beta <= M); propose M in [1.0, 1.5], beta in [0, M]
(calibration values to confirm). Apply 10/20/30% platen compression
(displacement-driven, drained/undrained conditions per the existing
continuation), record B_plastic vs B_elastic(J) profiles and report
Delta B = B_plastic - B_elastic as a function of compression and/or plastic
volume strain; also report where sigma''-driven (beta=0,B-frozen) yield
diverges.

## 7. Gates (status)

E-4 (DP translation): CLOSED - written into manuscript Sec. 2.4
(`finite_deformation_biot.tex`): aggregate split F=F^e F^p (eq. inelastic-aggregate), observable plastic strain = F^p (det = a^p), driving invariants p',q' from sigma', DP yield f = q' - M p' (M = mu+beta), flow normal to q'-beta p' with single rate gamma-dot, dissipation mu p' gamma-dot, observable form f = q'' - M[p''-(1-B)p] <= 0. Sign convention: repo tension-positive; p',p'' compressive-positive means; deviatoric parts coincide (q''=q').
E-1 (elastic collapse): PARTIAL - structurally, gamma-dot=0 => F^p=I, a^p=1 gives F=F^e and the aggregate elastic machinery (sigma'' from W0 at F^e + elastic mineral Jbar) reproduces the repo elastic closure provided the mineral-pressure "contact" and W0 volumetric terms are evaluated on the elastic aggregate deformation F^e (=F when plastic inactive). Remaining to verify on code: exact numeric reduction to repo eqs. 27-28 under this contact choice, and the local residual set for the yield-active case (state y = (rho-bar_s, a^p, gamma), consistency, active-set tangent).

Then: manuscript rewrite (constructed in Sec. 2.4; continue to Sec. 3 local-system specialization + abstract/scope numbers after runs), then delegate MOOSE implementation (qwen3-coder-next) + runs + Delta-B figure, update equation_to_moose_map/theory_traceability/provenance, commit.
