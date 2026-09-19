# Manuscript, implementation, and website consistency review

This review uses the current working tree, including the uncommitted review
response and subsequent manuscript edits. The canonical source is
`paper/main.tex`. The equation inventory follows its inputs and macro file.
It covers 131 equation labels, including three subequation group labels,
and 19 application materials, kernels, and postprocessors.

## Corrections

The [equation map](equation_to_moose_map.yml) still referenced two deleted
equations: `eq:single-prime-pressure-tangent` and
`eq:total-stress-pressure-integral`. The pressure checks now cite the current
single-prime stress and total-stress pressure tangent. Pressure integration
remains an independent verification of that tangent, rather than a separate
numbered manuscript equation.

The map previously omitted most supporting derivations, the analytical Mandel
appendix, and several stress and plastic-flow relations. Explicit supporting
mappings now identify their sources and roles. Derivations and limiting cases
are distinguished from equations assembled by MOOSE; analytical series belong
to the reference calculation. All five consumers of the shared mineral helper
are listed. `scripts/check_equation_traceability.py`, included in
`make validate`, rejects missing equation or object coverage, deleted labels,
missing source paths, and unknown test names. Regression tests exercise those
failure cases. This is a structural guard against drift, not a proof of the
equations.

The mineral helper cited obsolete rendered equation numbers. It now uses
stable manuscript labels. The generic flux kernel description cited an
equation from the general simulator; it now identifies the water weak residual
used here while retaining its general flux description. These documentation
changes were pushed through the shared-source synchronization tool. No C++
arithmetic or solver tolerances were changed in this review.

The symbolic verifier also cited a deleted compatibility equation and old
rendered numbers. Its comments now identify current labels and distinguish
supplementary compatibility identities. Its historical check identifiers and
mathematical assertions are preserved.

The website described the kinematics material as publishing `J F^-T`; its
actual property is `J F^-1`. Both affected pages now agree with the source.
The catalog also describes the prescribed-gradient material's AD stretch and
rotation options and identifies the algebraic kernel as a constitutive test
probe. Production local constraints are solved inside materials. The catalog
explains equation coverage and the inactive general-simulator options.
The Mandel page also called the observed errors acceptance limits. It now
distinguishes the measured pressure, displacement, and load errors from the
actual 4.0%, 0.8%, and 0.3% limits and states their normalization.

The website recipe regression extended its search into later explanatory
sections and counted their repeated commands. It now examines only the
numbered recipe section, preserving the comparison with `make reproduce`.

## Mathematical correspondence

| Manuscript source | Implementation and interpretation |
| --- | --- |
| `paper/sections/finite_deformation_biot.tex:562` | `MatchedLogMineralState.h` solves the mineral residual in log volume, using elastic `Je=J/ap`, and restores AD derivatives after bracketing. |
| `paper/sections/finite_deformation_biot.tex:623` | The same helper evaluates the coefficient using total `J`; `ADConstrainedSkeletonBiotMaterial` independently verifies the fixed-pressure, fixed-history tangent. |
| `paper/sections/finite_deformation_biot.tex:704` | The elastic stress material and implicit plastic return use the equivalent pressure correction `K alpha p^2 z^2/(Ks D)`, with mineral volume `z` and `D=Ks+alpha p z`. Adding `(1-B)p J` gives the single-prime Kirchhoff stress. |
| `paper/sections/finite_deformation_biot.tex:921` | The return solves six symmetric logarithmic plastic increments and yield consistency; hardening uses the current multiplier. The implicit-function solve retains current-state derivatives with previous history fixed. |
| `paper/sections/implicit_ad_implementation.tex:121` | The solid mass material supplies `Jdot rho + J rhodot` in normalized density units to the AD time kernel. |
| `paper/sections/implicit_ad_implementation.tex:117` | Water storage differentiates `J(1-phi_s)rho_f(p)`; the Darcy material and flux kernel give the negative weak-divergence contribution. Natural fluid boundaries have zero flux. |
| `paper/sections/implicit_ad_implementation.tex:155` | The plastic pore-volume material includes `beta Delta_gamma/dt` in the mineral-volume rate and combines it with the solved partial-density rate. |
| `paper/sections/mandel_analytical_appendix.tex:47` | `check_mandel_implicit_biot.py` uses the matching linearized storage, derived parameters, characteristic roots, pressure series, and displacement series, specialized to the reported unit width. |

In the code expression above, `alpha=1-K/(phi_s0 Ks)`. Substitution of the
closed coefficient converts the manuscript's pressure correction directly
to this expression; no approximation is involved.

The finite-step chain-rule mass drift remains explicitly documented and is
measured by refinement. The plastic material's constant-reference-mass state
and the independently evolved partial density coincide in the mass-conserving
limit; the reported residuals quantify the discrete departure. The vertical
Mandel displacement is prescribed from the analytical solution, and the
manuscript correctly distinguishes that boundary-condition check from the
independent horizontal-displacement comparison.

## Verification record

The current application was rebuilt with the pinned MOOSE framework and Conda
packages. Verification completed with the existing scientific tolerances:

- All 20 repository tooling tests passed. The standard MOOSE suite passed
  all 22 ordinary tests; its two heavy studies were run separately in full.
- The derivation checks passed for 48 elastic and 36 fixed-plastic states,
  together with all 21 symbolic checks.
- The publication material-point and supplementary example drivers passed
  and refreshed their curated records.
- The full elastic Mandel benchmark and all four publication cases passed.
  The pressure and independent side-displacement errors remain 3.71% and
  0.649%. The execution provenance now records these fresh runs.
- The full coupled poroplastic study passed, including all five refinement
  cases, elastic recovery, 807 active storage samples, and all 53 assembled
  Jacobian comparisons. The maximum relative Jacobian error is 2.22086e-8
  and the absolute error is 2.71333e-6, below 1e-7 and 1e-5.
- All six spatial-stability histories completed and passed. The hardening
  cases retain positive sampled acoustic determinants. The maximum temporal
  coefficient-contrast difference is 3.85e-6, below 5e-6.

The regenerated elastic record changes its maximum Biot-identity residual
from 4.6829394935328e-17 to 4.6945015734244e-17. The curated-data fingerprint
was refreshed; its comparison tolerance and the independent 1e-12 acceptance
limit are unchanged. The detailed stability notes were also refreshed from
the new data. The manuscript now specifies the 40 × 4 mesh and 0.0025 s step
for its reported acoustic minimum of 0.03797 GPa^2.

All publication figures were regenerated for the manuscript and website.
The canonical 30-page PDF rebuilt successfully. The affected equation and
figure pages were visually inspected; no clipping, undefined references, or
overfull displays were found. Existing small-font substitutions remain.
The packaged website passed 309 local-link checks and all 34 repository
Markdown-link checks. All 12 repository audit groups passed, including source
and execution provenance, formulation consistency, and equation traceability.
The manuscript environment check, synchronization of all 33 shared MOOSE
files, and whitespace checks also passed.

## Scope

This review checks local manuscript, application, numerical evidence, and
website packaging. It does not constitute material-specific physical
validation or a fresh citation-by-citation source-PDF review. It does not
deploy the website or establish the state of the live hosted site. The
uncommitted changes present at the start were retained.
