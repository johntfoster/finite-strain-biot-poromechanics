> Historical research note. Current equations, code, and verified results are maintained in `paper/main.tex`, `moose_app/`, and `validation/`.

# Plasticity demonstration scope: implicit Biot coefficient, not rock calibration

Status: author decision (recorded 2026-09-07). Owner: nonlinear-Biot manuscript
+ MOOSE implementation (this repository).
Purpose: stop the plasticity work from drifting into full constitutive modeling.
The paper illustrates the utility of the *implicit* (fixed-pressure,
history-dependent) Biot coefficient.  It does not need to predict a sandstone.

## Status of actions taken (2026-09-07, autonomous session)

- Note recorded (this file).- Paper prose adjusted to the demonstration framing (evidence-safe, no new
  fabricated results): abstract now states the material-level inelastic
  demonstration and that neither the elastic tests nor that demonstration
  independently validate a specific constitutive law; introduction's fourth
  objective notes the demonstration is at the material level and does not
  reproduce a rock's drained behavior; Sec. 4.7 scope states reproducing the
  sandstone hydrostatics is a constitutive-validation task beyond the
  demonstration; conclusions reframe the next stage as the coupled,
  momentum-active demonstration with the (1-B)p feedback and separate
  rock-scale physical validation as a later stage requiring the additional
  drained-stiffness ingredient.  Files: paper/main.tex, introduction.tex,
  mandel_verification.tex, conclusions.tex.  `\(...\)` delimiters verified
  balanced in all four files.
- MOOSE implementation of V2/V3/V4 NOT started: requires the missing `moose`
  conda environment (provisioning needs authorization) and the C++ milestones
  documented above.  V1 and the Delta-B sweep already exist and were not
  changed.
- Full LaTeX build verification blocked by a missing provisioned TeX
  distribution (authblk.sty and other packages absent from the system TeX);
  requires `tools/provision_latex.py` (authorization) or a fuller TeX tree.

## Decision

1. Physical sandstone calibration (Castlegate / Ingraham 2017) is OUT of scope
   for this paper.  The compactive (cap) branch, the porosity-dependent drained
   modulus K(phi), and the volume-strain-path identification of a hardening law
   are deferred to a separate constitutive-modeling extension.  The manuscript
   already labels that comparison "a target, not a validation"
   (`paper/sections/mandel_verification.tex`, Sec. 4.6) and separates
   implementation verification from constitutive/physical validation
   (Sec. 4.7).  Keep that honesty; do not promote the comparison to a
   prediction.
2. The inelastic chapter exists to support three claims from the scope note
   (`notes/plastic_biot_coefficient_scope.md`):
   (1) plastic work is driven by (deviatoric) single-prime stress and the
   distension conjugate; (2) B is an implicit, history-dependent fixed-pressure
   tangent that cannot be replaced by an elastic modulus ratio once plasticity
   is active; (3) a concrete inelastic local system and an FE demonstration
   computing B elastically and plastically from the same implicit path.
   Claims (2)-(3) are supported by a *mechanism demonstration* plus
   code-level verification of the machinery - not by matching a rock.
3. Literature position: the poroplasticity literature almost universally
   assumes a constant Biot/effective-stress coefficient (Terzaghi B=1 or
   constant alpha), so no standard numerical benchmark with an *evolving* B
   exists.  That absence is part of the paper's novelty and justifies the
   demonstration + verification approach.

## Demonstration + verification package (the plan)

- V1. E-1 elastic collapse: inactive branch reproduces the elastic coefficient
  exactly (Delta B = 0).  EXISTING gate; keep
  (`moose_app/test/tests/poroplastic_biot/poroplastic_delta_b_elastic.i`).
- V2. General-path oracle: B obtained by AD-implicit differentiation of the
  *active* plastic local system at fixed (p, J rho_s, H) compared against the
  reduced closed form B = 1 - (1 - B_el)/a^p.  This proves the demonstration B
  is a genuine fixed-pressure tangent of the active system, not an imposed
  formula.  STATUS: CODE MILESTONE - requires the full Sec-3 local-system
  Newton / route B (the current material computes only the reduced aggregate
  closed form); DEFERRED.
- V3. Load-unload loop: plastically load a drained point, then unload; report
  the unload coefficient and show it equals the implicit B at the current
  plastic state (the fixed-pressure tangent) and differs from the virgin
  elastic B_el.  This checks the literature's operational definition of alpha
  as an unload-reload tangent (Brown-Korringa; Rice-Cleary; Ingraham).
  STATUS: CODE MILESTONE - requires a stateful incremental return mapping with
  stored plastic history (F^p_n / a^p_n).  The current
  `ADDruckerPragerPoroplasticBiotMaterial` is documented as valid only for
  first loading from a virgin plastic state; DEFERRED.
- V4. B-feedback contrast: same loading path evaluated with the implicit
  inelastic B versus B frozen at B_el (or B=1), quantifying the shift in yield
  onset / returned state through sigma' = sigma'' + (1-B) p I.  NOTE: the
  (1-B) p term vanishes at pore pressure p = 0, so the contrast requires
  p != 0.  STATUS: CODE MILESTONE, NOT a deck change.  The current
  `ADDruckerPragerPoroplasticBiotMaterial` consumes B as an input property
  (default `solid_biot_coefficient`, set constant in the decks) and
  `ADPoroplasticBiotCoefficientMaterial` only post-computes
  B = 1 - (1 - B_el)/a^p for reporting; there is no B feedback into the driving
  stress.  Feeding the corrected B back into the DP material's
  `biot_coefficient_name` would create a cyclic AD-material dependency
  (poroplastic_biot_coefficient depends on plastic_pore_allocation, which the
  DP material produces only after consuming B).  A genuine B-feedback
  demonstration therefore requires ONE material that solves the coupled
  state + B system self-consistently at the quadrature point (the "M3 B
  feedback" milestone noted in the DP material header).  This is the
  "utility" number of the paper and the central follow-up code task.
- D. Directional mechanism demonstration: existing single-element
  poroplastic_delta_b sweep (Delta B vs compression) remains the synthetic
  discrimination figure.

## Constraints discovered (2026-09-07), recorded for the implementation plan

- The `moose` Conda environment is MISSING on this machine and the built
  binary cannot run (libs not found).  Provision via
  `agent_environment/skills/setup-moose-conda` (network + environment
  mutation; requires authorization) before any build/test/run.
- `.agent-runtime/moose` framework checkout is absent.
- `ADDruckerPragerPoroplasticBiotMaterial` header documents: prototype valid
  for first loading from virgin plastic state only (F^p_n = I); coupling of the
  plastic state back into the constrained Biot coefficient is a follow-up
  milestone.  V3 therefore cannot be run without that milestone.
- B-feedback (the (1-B) p I term in the driving stress) is absent whenever the
  pore pressure p = 0, as in all current drained decks.  V4 needs p != 0.
- Pre-existing dirty worktree (deleted dotfiles, untracked build artifacts,
  freshly registered `.github/skills/` symlinks): preserve unrelated changes.
- V2, V3, and V4 are all C++ milestones requiring the MOOSE environment; none
  is expressible as a deck change against the current prototype.
- `latexmk` is missing on this machine (lualatex/bibtex are present); verify
  manuscript edits with a manual multi-pass lualatex/bibtex run or provision
  LaTeX (`tools/provision_latex.py`, needs authorization) before a canonical
  `latexmk` build.

## Literature anchors (citations to add, all under references/)

- Rice & Cleary (1976), Rev. Geophys. 14(2) 227-241 - basic poroelastic
  diffusion; modulus-ratio structure of alpha.
- Brown & Korringa (1975), Geophysics 40(4) 608-616 - alpha from drained and
  unjacketed moduli; the definition used here.
- Garg & Nur (1973), J. Geophys. Res. - effective stress laws for *inelastic*
  porous rock: the elastic effective-stress coefficient need not govern
  inelastic behavior; the theoretical justification for demonstrating rather
  than re-deriving a plastic model.
- Detournay & Cheng (1993), "Fundamentals of poroelasticity", Comprehensive
  Rock Engineering vol. 2 ch. 5 - standard poroelastic reference.
- Ingraham et al. (2017) already cited: alpha measured as an unload-loop
  tangent at high mean stress; the motivation and the operational definition.

## Paper consequences (to apply when the demonstrations are in hand)

- Sec. 4.5 single-element poroplastic demonstration: retain, but frame as the
  mechanism demonstration that B is implicit/history-dependent and cannot be
  replaced by an elastic ratio; do not over-claim constitutive generality.
- Sec. 4.6 sandstone comparison: remains "a target, not a validation";
  optionally add the Garg-Nur frame (inelastic effective-stress coefficient
  need not be the elastic one).
- Sec. 4.7 scope: state the separation - the inelastic evidence is a
  demonstration of the implicit-B machinery plus implementation verification;
  physical/constitutive validation of a specific rock is out of scope.
- Abstract/introduction: align the claim with demonstration (B-feedback
  changes a predicted plastic observable), not with predictive rock modeling.


## Implementation status after authorized session (2026-09-07)

- Environment provisioned and verified: `moose` conda env (moose-dev
  2026.02.20, moose-libmesh 2026.02.18_f8a1758, moose-tools 2026.02.16),
  framework at `.agent-runtime/moose` commit abafb58b67a6.  `make` builds;
  the full poroplastic harness suite (5 tests) passes.
- V4 IMPLEMENTED (this supersedes the "deferred" note above):
  `ADDruckerPragerPoroplasticBiotMaterial` gained `biot_feedback` (default
  false = prior behavior; the 4 legacy tests still pass), solving
  B = 1 - (1 - B_el)/a^p consistently with the return map by fixed point when
  pore pressure is nonzero, and reporting a frozen-elastic (B = B_el)
  reference pass.  App-local (not in moose/sync_manifest.json); no shared-file
  push needed.
- Demonstration evidence: `moose_app/test/tests/poroplastic_biot/
  poroplastic_b_feedback.i` (registered test poroplastic_b_feedback);
  `scripts/sweep_poroplastic_b_feedback.py` -> `validation/
  poroplastic_b_feedback.csv`; `scripts/plot_poroplastic_b_feedback.py` ->
  `figures/poroplastic_b_feedback.{png,pgf}` (wired into `make figures`).
- Representative numbers (20% compression, ideal DP M = 1.5, beta = 0.6):
  150 MPa pore pressure -> B_used = 0.3753 > B_el = 0.3640, a^p = 1.0182 <
  a_p_ref = 1.0186; 400 MPa -> B_used 0.4528 vs B_el 0.4245 and the
  frozen-elastic reference over-predicts Delta_gamma by ~5%.  At fixed
  200 MPa, the elastic-implicit split widens with compression to ~30% relative
  difference near 35% compression and the Delta_gamma over-prediction reaches
  ~3%.  Fixed point self-consistency holds to machine precision
  (B_used = 1 - (1 - B_el)/a_p exactly in every row).
- Records updated: equation_to_moose_map.yml (new poroplastic_biot_feedback
  mapping), theory_traceability.yml (evidence + synthetic_discrimination),
  acceptance.yml (poroplastic_b_feedback), provenance.yml (34 artifacts,
  including the previously omitted poroplastic/sandstone figures and CSVs).
- Paper updated with real results: new subsection
  `sec:poroplastic-b-feedback` + `fig:poroplastic-b-feedback` in
  mandel_verification.tex; abstract, introduction, and conclusions state the
  feedback demonstration and its magnitude.  `scripts/validate_repository.py`
  passes all audits (portability, q2_q1_scope, sync, curated data,
  finite-deformation results, provenance, manuscript).
- LaTeX full build NOT run here: the system TeX lacks required packages
  (authblk, placeins, cleveref, pgf) and installing them needs sudo
  (`tools/provision_latex.py`); run `make paper` on a full-TeX machine or
  after provisioning.  Static delimiter balance was checked on all edited
  TeX (the naive mismatch was an artifact of treating `\%` as a comment).
- Still deferred (documented C++ milestones, not implemented): V2
  (general-path oracle = B by implicit differentiation of the active plastic
  local system with stored history) and V3 (stateful incremental load-unload
  return mapping with stored F^p/a^p).  Both require stored plastic history;
  the first-loading prototype remains the documented scope of the current
  material.  The B-feedback demonstration (V4) - the paper's central
  "utility" claim - is implemented and verified.


## V2 implemented and verified (2026-09-07, pure AD, no finite differences)

- V2 (general-path oracle) is now IMPLEMENTED and PASSES.  It uses pure
  automatic differentiation (no finite differences), mirroring the elastic
  general-vs-oracle tangent test.
- New app-local residual provider `ADPlasticStateBiotMaterial` (header + C in
  moose_app/) publishes the route-A solid volume fraction
  phi_s = phi_s0*r/(ratio*a^p) with a^p read FROZEN (non-AD, history held
  fixed), plus the material-mass and mineral-EOS local residuals and their
  partial derivatives.  `ADDruckerPragerPoroplasticBiotMaterial` now also
  publishes a plain-value a^p output (`plastic_pore_allocation_value`).
- The existing generic `ADConstrainedSkeletonBiotMaterial` assembles the AD
  dense tangent of the active plastic local system from those residuals and
  returns B_general = 1 - phi_s0 d(Jbar/a^p)/dJ |_{p,J rho_s,a^p}.
- Verification: deck `poroplastic_general_path.i` (registered test
  poroplastic_general_path) plus `validation/scripts/
  check_poroplastic_general_path.py` (6-case drained compression sweep,
  5-30%).  |B_general - B_reduced| <= 3.3e-16 (machine precision) at every
  compression, with B_reduced = 1 - (1 - B_el)/a^p the existing reduced
  closed form.  Curated: validation/poroplastic_general_path.csv.  The full
  poroplastic harness suite (6 tests) passes; all repository audits pass.
- This establishes, by pure AD, that the reduced poroplastic coefficient IS
  the fixed-history, fixed-pressure tangent of the active plastic local
  system - not an imposed formula.
- V3 (stateful incremental load-unload return mapping with stored F^p/a^p)
  remains the outstanding documented C++ milestone.


## V3 implemented and verified (2026-09-07)

- V3 (frozen-history unload-branch coefficient) is now IMPLEMENTED and PASSES,
  using the pure-AD general-path machinery established in V2.  Scope note: it
  demonstrates the literature unload/reload-tangent reading of alpha after
  monotonic plastic loading; it does not yet contain a transient plasticity
  engine that detects elastic reversal internally (that stateful tensorial
  return mapping with F^e = F (F^p)^-1 trial remains the outstanding
  documented milestone).
- Deck: `poroplastic_unload_tangent.i` (registered test
  poroplastic_unload_tangent): single element at a reduced compression with the
  plastic pore allocation frozen at its peak (a^p = 1.047205 after loading to
  20%); B_unload from the AD general path + reduced oracle + virgin B_el.
- Driver: `validation/scripts/check_poroplastic_load_unload.py` (reads the V2
  monotonic branch from validation/poroplastic_general_path.csv, runs the
  frozen unload deck at 5/10/15/20% compression, pure-AD cross-check
  |B_general - (1 - (1 - B_el)/a^p)| ~ 1e-9 (CSV precision)).  Curated:
  validation/poroplastic_load_unload.csv.  Figure:
  figures/poroplastic_load_unload.{png,pgf} (scripts/
  plot_poroplastic_load_unload.py, wired into `make figures`).
- Result: on the unload branch B_unload exceeds the virgin elastic B_el at
  every compression (e.g., at 10% after unloading from 20%: B_unload = 0.5052
  vs B_el = 0.4818 vs monotonic-load 0.4934) - the coefficient measured on the
  unloading branch is the fixed-history, fixed-pressure tangent at the plastic
  state, not the virgin elastic value.  All seven poroplastic harness tests
  pass; all repository audits pass.
- Records: equation_to_moose_map.yml (poroplastic_unload_branch),
  theory_traceability.yml, acceptance.yml, provenance.yml updated.
- Outstanding documented milestone: a fully stateful incremental load-unload
  return mapping with stored F^p/a^p (immediate elastic reversal on load
  reduction), which the current first-loading reduced prototype does not
  implement.


## Paper: sandstone section removed; V2/V3 results added (2026-09-07)

- Removed subsection "Drained sandstone hydrostatics as a compactive target"
  (the compactive target; author confirmed it adds nothing).  Ingraham et al.
  remains cited as motivation in Sec. 4.5 (single-point demonstration).
- Added subsection "Verification of the poroplastic coefficient"
  (`sec:poroplastic-verification`, becomes the new Sec. 4.7) reporting, with
  real numbers:
  * V2 general-path oracle: B_general (pure-AD dense solve of the active
    plastic local system with a^p frozen) equals B = 1 - (1 - B_el)/a^p to
    machine precision (max 3.3e-16) over 5-30% drained compression; at 20%:
    a^p = 1.0472, B_el = 0.32467, B = 0.35511.
  * V3 unloading branch: after loading to 20% and freezing a^p = 1.0472, the
    unload coefficient at 10% is 0.50518 vs virgin elastic 0.48182 and
    monotonic-load 0.49341 (history-dependent fixed-pressure tangent);
    Fig. fig:poroplastic-load-unload (figures/poroplastic_load_unload.pgf).
- Updated prose: "Scope and reproducibility" no longer references the removed
  sandstone section; conclusions now close on the V2/V3 verification and
  separate rock-scale physical validation.  audit_manuscript passes.

## PLAN: full tensorial stateful return mapping (outstanding milestone)

Goal: replace the reduced first-loading prototype with a genuine
multiplicative-plasticity integration so that loading then unloading gives
immediate elastic reversal (state frozen), and reloading re-yields - the
capability V3 currently approximates by prescribing the frozen allocation.

Model (manuscript Sec. 2.4-2.6): F = F^e F^p with F^p = (a^p)^{1/3} Fbar^p,
det Fbar^p = 1; isochoric true-plastic rate driven by the Mandel-type
deviatoric stress, scalar pore allocation driven by the mean; ideal
(constant-strength) Drucker-Prager surface, backward-Euler radial return.

Staged implementation:
1. Stateful material `ADTensorialPoroplasticBiotMaterial` (app-local):
   carry F^p (RankTwoTensor) and a^p across steps via MOOSE stateful
   properties; each step form F^e_tr = F (F^p_old)^-1 and evaluate the drained
   double-prime skeleton + mineral response on F^e_tr (J^e = det F^e_tr),
   replicating the repo skeleton-stress closed form on the trial deformation;
   reconstruct single-prime Kirchhoff tau' = tau'' + (1-B)p J I; yield test
   on q - M p; if active, radial return on the deviatoric (Mandel-type)
   stress with isochoric update Fbar^p_new (exponential/radial in the trial
   direction) and scalar a^p_new = a^p_old * exp(beta Delta_gamma); if the
   trial is inside the surface, freeze F^p and a^p (elastic unload).
2. Time-ramped deformation material + transient single-element deck: load
   (compress), unload, reload; report a^p, F^p, returned stress, and the
   fixed-history coefficient B along the loop.
3. Verification gates (no weakening):
   a. First-loading gate: monotonic compression reproduces the reduced
      single-load results (delta_b: a^p ~ 1.0229 at 10%, B_pl ~ 0.4934), i.e.
      incremental ideal-plastic update is path-independent on the proportional
      path.
   b. Elastic-unload gate: reducing compression after plastic loading leaves
      a^p and F^p frozen and the stress retraces the elastic branch.
   c. Reload gate: re-compression above the stored yield point re-activates
      plastic flow from the stored state.
   d. Jacobian/regression: existing 7 poroplastic tests still pass.
4. Add a load-unload figure/numbers from the stateful engine to the paper
   (superseding the frozen-history V3 demonstration), update records
   (equation_to_moose_map, theory_traceability, acceptance, provenance), and
   rebuild the manuscript.

Honest status: the reduced-prototype demonstrations (V1-V4) are implemented
and verified; the full tensorial engine is implemented and verified (below).

## Tensorial engine implemented and verified (2026-09-07)

`ADTensorialPoroplasticBiotMaterial` (app-local:
`moose_app/include/materials/...`, `moose_app/src/materials/...`) is now a
genuine stateful multiplicative material:
- stores F^p (RankTwoTensor) and a^p (Real) across steps (stateful
  properties; `initQpStatefulProperties` sets F^p = I, a^p = 1);
- each step forms F^e_tr = F (F^p_old)^-1 and evaluates the drained
  double-prime skeleton + mineral response on F^e_tr, reconstructing the
  single-prime Kirchhoff stress tau' = tau'' + (1 - B_used) p J I with
  B_used = 1 - (1 - B_el)/a^p_old;
- ideal Drucker-Prager yield test on (q, p) of the full tensorial trial;
  when active, a radial return updates F^p with the exact symmetric
  matrix-exponential F^p_new = exp(W) F^p_old (W = dg((3/2) dev(tau_tr)/q_tr
  + (beta/3) I)); when the trial is inside the surface F^p and a^p freeze
  (immediate elastic reversal).  Entirely AD; no finite differences.

Verification gates (all PASS, run data in the summaries below):
- (E-1) elastic limit M = 100: a^p stays 1.0, Delta_gamma = 0, and B equals
  the elastic coefficient 0.324666 at 20% compression.
- (path independence) peak a^p at 20% compression converges under step
  refinement: dt = 0.1 gives 1.031709, dt = 0.02 gives 1.031888 (~ 1.0319).
- (elastic unload) after loading to 20% then unloading to 10%, a^p is frozen
  at 1.031888 and Delta_gamma = 0 across the whole unload branch; B recovers
  along the elastic branch.
- (reload) re-compression above the stored yield point re-yields at the peak.
- (regression) all 8 poroplastic harness tests pass
  (`poroplastic_tensorial_load_unload` added as RunApp).

Artifacts added: `moose_app/test/tests/poroplastic_biot/tensorial_load_unload.i`
(+ test entry), `validation/tensorial_load_unload.csv` (curated by
`validation/scripts/check_tensorial_load_unload.py`, RESULT: PASS),
`figures/tensorial_load_unload.{png,pgf}` (`scripts/plot_tensorial_load_unload.py`),
Makefile `figures` target, and records (`equation_to_moose_map.yml`
`poroplastic_tensorial_stateful`, `theory_traceability.yml`,
`acceptance.yml` `poroplastic_tensorial_load_unload`, provenance regenerated;
`validate_repository.py` PASS).

## Coefficient convention alignment and example rewiring (2026-09-07)

The stateful engine now reports the coefficient with the route-A convention
used everywhere in the paper and verified by the general-path oracle:
B = 1 - (1 - B_el(J))/a^p with B_el evaluated at the TOTAL deformation J
(matching ADLocalElasticMineralBiotMaterial / the reduced closed form), not at
the elastic trial J^e.  Added outputs `plastic_elastic_biot_coefficient`
(B_el at total J) and the frozen-elastic reference option
`use_elastic_coefficient_in_trial` (isolates the coefficient feedback at
nonzero pore pressure).  Default path and all prior gates are unchanged
(peak a^p = 1.031888 at 20% under load-unload; E-1 collapse B = B_el).

All the other examples were rewired through the canonical stateful engine
(canonical parameters M = 0.6, beta = 0.4, matching the load-unload demo):
- delta_b compression demonstration -> transient monotonic stateful decks
  `poroplastic_delta_b{,elastic,_20,_30}.i` plus `poroplastic_delta_b_sweep.i`
  (0-35%, exact-sampled), curated by
  `validation/scripts/curate_poroplastic_delta_b.py` into
  `validation/poroplastic_delta_b.csv` (RESULT: PASS).  Canonical curve
  (5%,10%,20%,30%): a^p = 1.0074, 1.0151, 1.0319, 1.0506; B_el = 0.5451,
  0.4818, 0.3247, 0.1169; B_pl = 0.5484, 0.4895, 0.3455, 0.1595;
  Delta B = 0.0033, 0.0077, 0.0209, 0.0425.  Elastic collapse (M = 100):
  a^p = 1, Delta_gamma = 0, B = B_el = 0.324666 at 20%.
- b_feedback (nonzero pore pressure) -> `poroplastic_b_feedback.i` (stateful
  transient at 20% compression) with a frozen-elastic (B = B_el) reference
  pass; `validation/scripts/check_poroplastic_b_feedback.py` (RESULT: PASS)
  curates `validation/poroplastic_b_feedback.csv`: corrected coefficient B
  exceeds B_el and the coupled a^p falls below the reference; e.g. at 20% and
  150 MPa, B = 0.4007 vs B_el = 0.3640 and a^p = 1.0612 vs 1.0632
  (over-prediction 1.1%); at 400 MPa the over-prediction reaches 3.3%.
- general_path oracle -> `poroplastic_general_path.i` feeds the frozen a^p
  accumulated by the stateful engine at each compression (read from
  `validation/poroplastic_delta_b.csv`); the AD dense tangent
  B_general = B_reduced to machine precision (~1.4e-16) and B_reduced equals
  the stateful coefficient to ~1e-9 (`check_poroplastic_general_path.py`,
  RESULT: PASS).  At 20%: a^p = 1.0319, B_el = 0.32467, B = 0.34553.
- unload_tangent -> `poroplastic_unload_tangent.i` freezes the canonical peak
  a^p = 1.031877 (20%); `check_poroplastic_load_unload.py` (RESULT: PASS)
  curates `validation/poroplastic_load_unload.csv`: unload to 10% gives
  B_unload = 0.4978, above the virgin elastic 0.4818 and the monotonic-loading
  0.4895 at the same compression.

Harness: 9 poroplastic tests pass (delta_b elastic/10/20/30/sweep,
b_feedback, general_path, unload_tangent, tensorial_load_unload); figures
regenerated (poroplastic_delta_b, poroplastic_b_feedback,
poroplastic_load_unload, tensorial_load_unload); records
(equation_to_moose_map, theory_traceability, acceptance) rewritten to the
canonical engine and frozen-canonical oracles; provenance regenerated;
`validate_repository.py` PASS.

## Manuscript updated to the canonical stateful engine (2026-09-07)

`paper/sections/mandel_verification.tex` was rewritten to present the
canonical stateful multiplicative engine (M = 0.6, beta = 0.4):
- sec:poroplastic-demonstration now describes the stored aggregate plastic
  factor F^p (elastic trial on F^e = F (F^p_n)^-1, radial return updating
  F^p, a^p = det F^p), the monotonic delta-B ramp with canonical numbers
  (Delta B from 0.003 at 5% to 0.043 at 30%), and adds
  `fig:tensorial-load-unload` (stateful load-unload-reload: a^p frozen with
  Delta_gamma = 0 on unload, re-yield on reload).  Elastic-collapse (M large)
  check retained.
- sec:poroplastic-b-feedback now reports the corrected coefficient carried in
  the single-prime reconstruction with a frozen-elastic (B = B_el) reference
  pass: at 150 MPa and 20%, B = 0.4006 > B_el = 0.3640, a^p = 1.0612 below
  the reference 1.0632; at 400 MPa B = 0.4953 vs 0.4245 with ~3.3%
  over-prediction; caption updated.
- sec:poroplastic-verification now reports the general-path oracle with a^p
  frozen at the stateful values (1.0074 to 1.0506 over 5-30%), B_general =
  B_reduced to 1.4e-16 and equal to the stateful coefficient to 1e-9 (at 20%:
  a^p = 1.0319, B = 0.34553), and the unload branch with frozen peak a^p =
  1.0319 (unload to 10% gives B = 0.4978 vs elastic 0.48182 and monotonic
  0.48954).
- `paper/main.tex` abstract and `paper/sections/conclusions.tex` updated:
  delta-B "up to 0.043 at 30%" and feedback over-prediction "about three
  percent at 400 MPa / 20%".

`validate_repository.py` (incl. audit_manuscript) PASS after regenerating
provenance.  LaTeX build remains blocked in this environment (latexmk and
texlive packages pgf/cleveref/placeins/authblk missing; needs a system TeX
install) - the manuscript edits are validated by the delimiter/label/reference
audit and by figure inspection, not by a compiled PDF.
