# Manuscript and MOOSE formulation consistency

The current manuscript and every retained example use the scalar mineral
equation (63), `eq:verification-mineral-factors`, followed by the coefficient
(68), `eq:poroplastic-biot-correction`. Their source is
`paper/sections/finite_deformation_biot.tex`. The mineral equation uses
`Je=J/ap`; the coefficient denominator uses total `J`.

## Implementation and independent checks

`MatchedLogMineralState.h` supplies the shared scalar solve and coefficient.
The elastic material and implicit poroplastic return use that implementation.
The supplementary loading decks now use `ADImplicitPoroplasticBiotMaterial`.
The frozen-history material conserves reference solid mass and publishes the
matched mineral residual and its partial derivatives. Its independent dense
two-state tangent agrees with the closed coefficient and the loading states.

The manuscript energy was checked in its original independent-volume form as
well as its reduced pressure form. Numerical and symbolic checks cover pressure
equilibrium, energy-derived stress, the Biot transform, material mass, pressure
response, fixed-plastic-state tangents, and the equivalent volume-fraction and
porosity expressions. The implementation section explicitly distinguishes the
elastic-volume argument of the mineral solve from total volume in the
coefficient.

## Completed numerical verification

Runs and logs are retained under `.agent-runtime/formulation-update/`;
constitutive drivers also retain output in their named `.agent-runtime/`
directories.

- MOOSE harness: **17 passed, zero skipped or failed**. Both elastic and active
  plastic PETSc Jacobian tests retain relative tolerance `1e-7` and absolute
  tolerance `1e-5`.
- Full implicit plastic verification: passed mass, mineral EOS, intrinsic stress
  trace, energy-derived stress, fixed-state Biot tangent, exponential flow,
  yield, dissipation, determinant, objectivity, and increment refinement checks.
  At 400 MPa, `B=0.61559533732935`, `ap=1.0456671394274`, and companion
  `ap=1.045920874982`, reproducing the manuscript's rounded values.
- Supplementary monotonic loading, frozen-history tangent, unloading, pressure
  feedback, and loading-cycle checks completed. The two-state and closed-form
  comparisons retain their original numerical tolerances.
- Full Mandel analytical benchmark: maximum normalized pressure error
  `0.0371057831` (limit `0.04`), lateral-displacement error `0.0064886203`
  (limit `0.008`), and load error `0.0023756395` (limit `0.003`).
  Successive temporal pressure differences decrease from `0.02725015` to
  `0.01686213`.
- Publication profiles and all three finite-compression mesh/time cases
  reached 0.702 s. The final mean coefficient is `0.58219459009679`,
  with range `[0.58209924671994, 0.58224939716739]`.
  The maximum mineral residual is `2.42085e-17`; the coefficient discrepancy
  is `4.68294e-17`. Referential-mass drift decreases under time refinement.
  The exact curated coefficient-discrepancy regression was refreshed for the
  shared expression's arithmetic ordering; physical acceptance remains
  `1e-12`.

## Constitutive domain

The supplementary pressure deck now ramps pressure with compression, matching
the manuscript path. Applying full pressure at the first nearly undeformed
increment had driven the former example outside the smooth cone.

The supplementary point at 5% compression and 200 MPa also lies outside the
supported smooth-cone domain even with simultaneous loading. An independent
coaxial apex calculation gives a tensile mean stress of about -9.64 MPa.
The checker runs this input and requires MOOSE to reject it; it is recorded in
`validation/poroplastic_domain_checks.json`, not represented as a converged
point in the figure. An apex constitutive branch remains outside the manuscript
scope. The other pressure and compression paths satisfy the feedback checks.
The relative final-increment feedback increases with pressure but decreases
with compression on the supported fixed-pressure sweep; obsolete claims of
increase in both sweeps were removed.

## Cleanup and reproduction

Removed the unused scalar and tensorial prototype implementations, their
superseded feedback driver, the obsolete sandstone comparison scripts and
figures, its website page, the unused Mandel pressure PDF, and tracked raw
smoke-test CSVs. Historical research notes remain explicitly marked as
historical. Provenance no longer refers to the already absent stress-trace
appendix and covers all retained model sources, decks, checks, and figures.

`make examples` regenerates supplementary evidence. `make figures` regenerates
all ten retained figure sets and their website copies. `make reproduce` orders
the full pipeline; the shell wrapper invokes it without repeating shared
prerequisites. Smoke-test output is written under ignored runtime directories.

The 33 shared MOOSE files pass synchronization with the authoritative simulator
checkout. Its protected input-block integrity check also passes. Unrelated
worktree changes were preserved.

## Publication checks

All ten figure sets were regenerated and visually reviewed. The website PNGs
are exact copies of the corresponding repository figures. The canonical
`paper/build/main.pdf` was rebuilt and the equation, implementation, and figure
pages were visually inspected. Equations (63) and (68) retain their numbers.
There are no undefined references or overfull displays; the build retains
font-size substitution warnings from the existing math fonts.

The final repository audit passes source synchronization, curated-data checks,
physical regression limits, provenance hashes, retired-model exclusion,
figure-copy equality, manuscript numerical quotations, and manuscript build
checks. The manuscript dependency profile and Git whitespace checks also pass.
