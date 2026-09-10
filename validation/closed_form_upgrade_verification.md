# Closed-form matched-logarithmic Biot implementation

The main derivation is in `paper/sections/finite_deformation_biot.tex`, with
stress-trace compatibility detailed in `paper/sections/stress_trace_biot_appendix.tex`.
The production coefficient is

```text
B = 1 - K barJ / {J [Ks + (1 - K/(phi_s0 Ks)) p barJ]}.
Ks ln(barJ) + (1 - K/(phi_s0 Ks)) p barJ - (K/phi_s0) ln(J/a_p) = 0.
```

The coefficient contains states only. The mineral state remains implicit.
The total-volume derivative fixes the current plastic configuration; the
outer AD derivative includes the active return mapping. The elastic and plastic
materials share `moose_app/include/utils/MatchedLogMineralState.h`. The general
AD-valued two-state tangent remains an independent diagnostic.

## Verification evidence

The completed run is retained under `.agent-runtime/matched-log-upgrade/`.
Curated evidence is in `validation/mandel_implicit_biot.yml` and
`validation/implicit_poroplastic_verification.json`; provenance hashes identify
the source and publication artifacts.

- Application build: passed with the repository MOOSE environment.
- Full MOOSE harness: 15 passed, zero skipped or failed (`tests-final.log`).
- Elastic and active-plastic PETSc Jacobian comparisons: passed the original
  relative `1e-7` and absolute `1e-5` thresholds. The active-plastic comparison
  gave relative `6.70891e-8` and absolute `5.70914e-8` differences.
- Independent mathematical verification: 48 elastic and 36 fixed-plastic-state
  checks passed, with maximum normalized discrepancy `2.21e-12`. Fifteen symbolic
  identities passed, including elimination of the two-state tangent.
- Full plastic history, pressure feedback, nonaxisymmetric deformation,
  superposed rotation, and increment refinement: passed unchanged physical
  acceptance tolerances. Mass, EOS, stress-trace EOS, energy-derived stress,
  fixed-state tangent, exponential flow, determinant, yield, dissipation,
  and objectivity were checked independently.
- Full Mandel analytical comparison and spatial/time refinement: passed.
  Maximum pressure error was `0.0371058` (limit `0.04`), side-displacement
  error `0.00648862` (limit `0.008`), and load error `0.00237564`
  (limit `0.003`). Successive temporal pressure differences decreased from
  `0.0272501` to `0.0168621`.
- Publication profile run and three ten-percent compression continuation runs:
  completed. Halving the time step reduced maximum referential-mass drift
  from `5.57267e-5` to `2.78519e-5`. The final average coefficient is
  `0.58219459`, compared with reference `0.6`.

## Constitutive-domain and regression changes

The original plastic history used `phi_s0=0.9`. With the new mineral law,
its full compression path reached pore closure: at `J=0.808`, the solid
fraction was already `0.99971776`, and the next increment violated the
strict `phi_s<1` condition. The synthetic plastic benchmark now uses
`phi_s0=0.8` with the same complete compression/unloading/reloading path,
moduli, pressure range, and acceptance tolerances. The active-plastic
Jacobian probe uses the same reference fraction. The Mandel material retains
`phi_s0=0.9`.

The dimensionless elastic Jacobian deck previously had
`K=phi_s0 Ks`, outside the new model's strict positive-storage reference
domain. Its reference fraction is now `0.5` instead of `0.25`, with the
specific-volume reference changed consistently. Its moduli and reference
coefficient are unchanged. This exercises nonzero mineral pressure coupling.

Two historical plastic tests consumed an elastic material whose constitutive
law changed in this work. They now receive their original analytical inputs
explicitly through parsed materials, preserving their original plastic
models and assertions. These legacy tests remain separate from the active
matched-logarithmic plastic verification.

The Mandel analytical storage and prescribed platen history were regenerated
from the matched law. Figure extraction now uses the actual Biot material
output rather than reconstructing an obsolete constitutive expression.
Golden publication values were updated for the new model. The roundoff-level
Biot diagnostic is checked against its new recorded value (`4.77014e-17`),
and the constitutive acceptance limit remains `1e-12`. All physical and
Jacobian acceptance tolerances are unchanged.

## Reproduction and scope

`make derivation` runs the mathematical checks. `make test` runs the complete
MOOSE harness. `make plastic` regenerates plastic evidence; `make mandel`
runs the analytical benchmark, publication profiles, and finite-deformation
sensitivity cases and curates their results. `make figures` regenerates the
manuscript and website figures. `make paper`, `make provenance`, and
`make validate` complete the publication checks.

The implementation verifies active constitutive plasticity and a coupled
elastic boundary-value problem. Active coupled poroplastic flow and physical
material calibration remain outside the demonstrated scope.
