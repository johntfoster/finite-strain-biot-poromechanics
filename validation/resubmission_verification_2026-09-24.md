# Repository verification before resubmission

Date: 2026-09-24. Status: local resubmission verification passed.

The audit uses `paper/main.tex` and `paper/defs.tex` as the mathematical
authority. The separately requested pore-volume explanation and weak-form layout changes
in `paper/sections/implicit_ad_implementation.tex` are preserved.

## Implementation and equation coverage

The equation checker covers 153 equation identifiers, 19 registered application
objects, and 33 traceability groups. Every remaining object is selected by a
retained input. A regression now rejects mapped objects without an input.

| Kernel | Manuscript identifiers | Implemented contribution and scope |
| --- | --- | --- |
| `ReferenceMomentum` | `eq:momentum-weak-residual`, `eq:reference-momentum-balance` | Reference test gradient contracted with total first Piola stress; quasistatic, zero body force. Prescribed displacement and natural traction conditions complete the boundary problem. |
| `ReferenceFluidMass` | `eq:fluid-pressure-weak-residual`, `eq:conservative-fluid-mass-step`, `eq:reference-darcy-flux` | Test times the backward difference of complete reference water mass, minus the reference test gradient dotted with Darcy mass flux. Previous mass is stateful; current mineral and plastic dependencies retain AD derivatives. |
| `ADMaterialPropertyResidual` | `eq:verification-mineral-factors`, `eq:poroplastic-biot-correction`, `eq:single-prime-kirchhoff-stress`, `eq:distension` | Algebraic probes of returned constitutive quantities in Jacobian tests. These probes are verification equations, not additional physical balance laws. |

The reference fluid mass is `rho_f(p) * J * (1 - phi_s)`, with
`phi_s = phi_s0 * Jbar / J`. The Darcy material supplies
`-rho_f * J * F_inverse * (permeability / viscosity) * F_inverse_transpose * Grad(p)`.
Thus the kernel integrates reference quantities without adding another Jacobian.
Density units are mass per volume; reference mass flux has units of mass per area
per time. The total first Piola stress has units of force per reference area.

`ADReferenceSolidMomentum`, `ADReferenceComponentFluxTerm`, and
`ADReferenceMaterialStorageRateTerm` had no retained input consumers. Their six
source/header files were removed from this paper and its synchronized export
list. Their general-simulator implementations were preserved. The reduced
manifest was synchronized with `tools/sync_biot_moose.py push`; all 33 retained
shared files pass integrity checks. Existing unrelated master changes were
preserved. The export records its actual master revision independently of the
older scientific dependency pin; no dependency pin was advanced.

The website catalog now lists the conservative kernels under Kernels and
explains that continuous plastic storage rates are diagnostics. Repository
instructions and vision now describe two solved fields and pointwise solid
density elimination. Supplementary constitutive inputs, independent tangent
oracles, reference data, and figure formats remain because they have documented
verification or publication consumers.

## Completed checks

- MOOSE toolchain status and verification: passed with framework
  `abafb58b67a6037c6723ffeb19647c84484466da`.
- Rebuilt application: 23 ordinary MOOSE tests passed, zero failed. The two
  heavy studies were checked separately, as reported below.
- Repository tooling: 34 tests passed, including unused-object rejection.
- Equation traceability: 153 equation identifiers, 19 registered objects, and
  33 traceability groups passed.
- Shared-source integrity: all 33 retained files passed.
- Manuscript dependency profile and submission export manifest: passed;
  the export manifest covers 34 repository-relative paths.
- Repository validation: all 13 audits passed after refreshing provenance.
- Local website: 320 local links and 46 repository Markdown links passed;
  source copies agree with the worktree.
- Canonical manuscript: `paper/build/main.pdf` is up to date, with no LaTeX
  warnings. Pages 18 and 19 and every publication-figure page passed visual
  inspection. Temporary manuscript review renders were removed.

The optional publication-profile requirement `git-filter-repo` is absent.
It is used by manuscript-history extraction, not the submission packager;
no history extraction was requested.

## Numerical reproduction and publication artifacts

The interrupted session completed the symbolic checks, ordinary MOOSE suite,
and material-point verification, including nonaxisymmetric refinement and
rotation/objectivity. Recovery established that the old simulation processes
were absent before restarting incomplete studies. Completed plastic runs were
reused only when command, input, executable, and source signatures matched.
Independent stability cases used distinct output names while the canonical
coordinator waited; that coordinator subsequently performed all acceptance
checks. Meshes, time steps, constitutive equations, and tolerances were unchanged.
Logs and recovery records are under `.agent-runtime/resubmission-verification/`.

| Gate | Result |
| --- | --- |
| Elastic and plastic nonzero initial states | Passed sealed-mass, pressure, and prescribed-history checks. |
| Analytical Mandel benchmark | Passed; maximum pressure, horizontal-displacement, and load errors are 3.7075%, 0.64625%, and 0.23663%, below the 4.0%, 0.8%, and 0.3% limits. |
| Elastic publication profiles and finite compression | Passed all runs and comparisons; final mean Biot coefficient 0.582194547, relative departure 0.029675755. |
| Coupled plastic storage and Jacobian | Passed; normalized discrete-storage error 6.62e-12, 49 Jacobian comparisons with maximum relative difference 5.54e-8. |
| Coupled plastic refinement and elastic recovery | Passed; maximum reaction mass defect below 2.0e-12, finest reconstructed Darcy mismatch 0.3363%, normalized elastic-recovery error below 1.2e-13. |
| Six-case stability study | Passed unchanged acoustic, transverse-variation, conservation, and refinement criteria; maximum fine-grid temporal field difference 2.48731e-6 and maximum reaction mass defect 4.04652e-12. |
| Supplementary examples | All five drivers passed. |

All seven figure generators completed. The eight manuscript figures and four
supplementary figure sets were regenerated and visually inspected. Every PNG
agrees byte for byte with its website copy. The regenerated image data reproduce
the existing plotted results; updated execution records identify the fresh runs.
The website's rounded benchmark errors and finite-compression coefficient agree
with the new records. Detailed stability values were refreshed, and three rounded
bounds in the plastic numerical notes were made conservative with respect to the
measured residuals. Acceptance tolerances were not changed.

The application is dynamically linked, so the launcher hash alone does not
identify its implementation. The rebuilt library
`moose_app/lib/libnonlinear_biot_ad-opt.so.0.0.0` has SHA-256
`5efd2d67d0c6721ba5ddfbd8b2eca68a941c75a953f01ac3d1f1db2a0aa65f52`.
The library and every application source/header hash were verified unchanged
through the resumed simulations. Symbol inspection confirmed that the three
retired kernel classes are absent.

## Publication scope

This report records local scientific and artifact verification. Delivery uses
the existing Pages workflow after commit and push, followed by a byte comparison
of every public website file against the build from that revision. Deployment
verification is separate from the local results reported here.

The persistent infrastructure maintenance freeze remains unchanged. No release,
journal submission, or separate manuscript-history extraction is part of this
audit. The synthetic calculations do not establish material-specific experimental
validation or a global constitutive stability proof.
