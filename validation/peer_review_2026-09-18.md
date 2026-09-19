# Internal peer review: manuscript, implementation, and reproducibility website

Reviewed 2026-09-18 at repository revision
`35ab1883ef43f4dcb54716ee94e59d58c064c693`. This is an agent-conducted internal
review, not an external journal review. The worktree was clean at the start.
The paper repository owns all three reviewed tracks. Scientific sources were
not edited during the initial review. The responses below record the subsequent authorized manuscript, implementation,
and reproducibility changes.

**Initial recommendation: revise before submission.** The closed-form derivative
and energy-to-stress construction are supported by the inspected equations and
focused numerical checks. Finding 1 has since been addressed by clarifying
double-prime calibration and the pressure-feedback comparison, with new
verification checks. Findings 2--4 are addressed below through an optional
virgin-state diagnostic, a complete reproduction recipe, and execution-time
provenance. Verification of the revised heavy studies is recorded separately
from the original review.

## 1. Addressed: explain drained calibration and qualify the comparison

Original review locations: `paper/sections/poroplastic_results.tex:54`,
`paper/sections/finite_deformation_biot.tex:678`,
`moose_app/src/materials/ADImplicitPoroplasticBiotMaterial.C:144`, and
`docs/poroplastic.html:54`.

The original review placed too much weight on algebraic cancellation of the
explicit coefficient in the simplified single-prime stress. That cancellation
does not undermine the constitutive role of the Biot coefficient. Zero-pressure
laboratory calibration supplies the drained double-prime skeleton response.
The coupled energy and mineral law extend that response to nonzero pressure;
the effective-stress relations then supply the driving and total stresses.

The narrower issue is the comparison: it retains the consistent double-prime
law and substitutes only `B_el` in the transformation. At a common candidate
state this adds `(B - B_el) p J I` to the driving stress. It is a constitutive
sensitivity experiment, rather than a second material derived from the same
coupled energy.

Implemented response: the constitutive section now explains the calibration
sequence and derives the fixed-history pressure tangents and pressure integral.
The abstract, introduction, results, conclusion, figure labels, and website
identify the precise substitution. The production constitutive equations are
unchanged. The independent material-point verifier now checks drained stress,
finite-pressure double-prime stress, both transformations, the pressure tangent,
and pressure integration against returned MOOSE states. These checks are mapped
to the manuscript and included in publication acceptance.

Response verification: the full material-point publication driver passed and
regenerated its verification record without changing the numerical history or
feedback data. All five focused poroplastic regression tests passed, including
the zero-hardening and hardening active AD Jacobians. The largest normalized
new stress error was `1.68e-10`, the pressure-tangent error `7.61e-9`, and the
pressure-integral error `3.46e-12`, all below `2e-7`. Figure labels were
regenerated for the manuscript and website. Repository audits, the five
website tests, manuscript workflow checks, and shared-source integrity passed.

## 2. Addressed (original severity: moderate): an optional virgin-state diagnostic restricts production states

Original review locations: `moose_app/src/materials/ADImplicitPoroplasticBiotMaterial.C:137`
and `moose_app/include/utils/MatchedLogMineralState.h:27`.

In the reviewed revision, every constitutive evaluation solved the virgin
mineral problem with total `J`, even when
`use_elastic_coefficient_in_trial` was false. A valid plastic
mineral root at `J/ap` does not guarantee a virgin root at `J`, particularly
under tensile pore pressure. The diagnostic can therefore abort the production
constitutive evaluation before the actual plastic state is returned.

A direct double-precision instantiation of the repository's mineral helper
reproduces the distinction with `K=1 GPa`, `Ks=2.5 GPa`, `phi0=0.9`, `J=2`,
`ap=2`, and `p=-1.35 GPa`:

| Quantity | Result |
| --- | --- |
| Plastic mineral volume | 1.6313407573 |
| Plastic solid fraction | 0.7341033408 |
| Scalar stability denominator | 1.2764944320 GPa |
| Plastic Biot coefficient | 0.3610074920 |
| Virgin mineral solve | Aborts: no stable tensile root |

The plastic mineral volume is below `e`, and its pore volume and scalar
tangent satisfy the manuscript's stated restrictions. This is a constitutive
domain probe, not a demonstrated loading path or a physically calibrated
water-tension experiment. It does not establish that the published paths fail.
The helper was compiled with minimal adapters for error reporting and raw
double values; the mineral-solving code itself was unchanged.

Requested revision: separate comparator availability from production-state
admissibility. Compute the comparator when requested and represent an
unavailable comparator explicitly. Retain strict rejection when the chosen
companion stress law actually requires it. Add a focused regression covering
this distinction.

Implemented response: the production return now solves only its current
plastic mineral state. The optional virgin coefficient is evaluated after
convergence; an unavailable value is NaN with an explicit zero availability
property. The numerical implementation section and website explain the
separate domains. `compute_elastic_coefficient=false` disables this diagnostic. The
companion stress law retains its requirement for an admissible virgin state,
including when the optional diagnostic is disabled. Initial isotropic plastic
distention can be prescribed for fixed-history verification, with the
accumulated multiplier initialized consistently.

Response verification: the five-case MOOSE regression passes the reported
tensile-domain probe, diagnostic disabling at a valid state, an available
comparator, closed virgin pores with a valid plastic state, and rejection when
the companion law requires the unavailable comparator. Production coefficients
are checked independently in each accepted state. The material-point
publication driver and 21 focused MOOSE regressions passed, including the
active AD Jacobian checks.

## 3. Addressed (original severity: moderate): the numbered website recipe does not reproduce all results

Original review locations: `docs/reproduction.html:67`, `docs/reproduction.html:86`,
`Makefile:79`, and `moose_app/test/tests/poroplastic_mandel/tests:11`.

The reviewed numbered steps ran the standard tests, material-point calculations,
supplementary examples, and elastic Mandel study, then regenerated all figures.
They omitted `make plastic-flow`, `make stability`, and `make derivation`.
The standard harness marks the full coupled refinement and stability drivers
as heavy, so those tests do not fill the gap. A reader following the numbered
recipe can render the coupled publication figures from checked-in data without
reproducing those simulations.

The canonical-target table correctly includes the missing targets, and a
later section supplies the plastic-flow command. The defect is the inconsistent
claim that the numbered sequence describes the complete pipeline.

Requested revision: make the numbered steps match `make reproduce`, including
the full coupled and stability calculations before plotting. State the expected
long runtime next to those commands. Clearly distinguish rendering curated
data from regenerating numerical evidence.

Implemented response: the numbered recipe now includes derivation verification,
full coupled refinement, and all six stability cases before plotting. It states
the expected runtime and distinguishes plotting curated results from rerunning
simulations. A regression compares the numbered commands with the canonical
`make reproduce` dependency sequence. All six website unit tests passed.

## 4. Addressed (original severity: minor): provenance records prescribed rather than observed package versions

Original review location: `scripts/update_validation_provenance.py:152`.

The reviewed provenance generator wrote literal package versions and a literal
framework commit into its `environment` record. It did not interrogate the
environment that produced the results. Content hashes establish file identity,
but do not establish which executable dependencies generated those files.
Running the target after an environment change can therefore record the tested
versions as though they were the execution environment.

Requested revision: distinguish the required environment from the observed
run environment. Capture actual package versions, framework revision, and
application identity at simulation time, and carry that record into curated
results. The currently inspected MOOSE environment matches the pinned framework
and primary MOOSE packages; this finding concerns the recording mechanism.

Implemented response: publication drivers now observe actual Python and package
versions, Conda package builds, framework revision, and executable identity
before execution, then attach output hashes after successful completion.
Cached runs retain their original observations. The provenance generator
packages these records separately from `required_environment`; missing
historical observations are explicitly `not_recorded`. The supplementary
example target uses a wrapper around the same five drivers to capture the
same evidence. The elastic Mandel driver captures observations on future
runs; its historical publication results have not been relabeled.

Response verification: two provenance tests pass, covering observed metadata,
missing metadata, portable paths, executable changes during execution, and
preservation of historical observations during a content-hash refresh. The
material-point publication driver and all supplementary examples passed and
produced execution records. The coupled and six-case stability publication
drivers subsequently passed and recorded their observed environments as well.

## Strengths and scope

The manuscript distinguishes fixed-plastic-state derivatives from the outer
derivative of the active return. Its energy construction, scalar-root domain,
and synthetic constitutive choices are explicit. It acknowledges chain-rule
mass drift, cavitation limitations, and the distinction between verification
and physical validation. These qualifications should be retained.

The implementation separates material calculations from weak residuals and
provides independent constitutive, storage, and assembled-Jacobian checks.
The coupled simulation cache includes executable and source signatures. The
website packages its linked source files and checks local links and anchors.

The extensive virtual-work exposition in the constitutive section could be
shortened or partly moved to an appendix to bring the central coefficient and
its implications forward. This is an editorial suggestion, not a mathematical
defect.

## Verification after the review changes

- The five comparator-domain cases passed, including a valid plastic state
  with no admissible virgin root and strict companion-law rejection.
- The focused MOOSE suite reported 21 passed and zero failed. The full
  material-point publication driver and all five supplementary drivers passed.
- The full coupled publication driver passed storage, all 53 assembled
  Jacobian comparisons, five refinement cases, elastic recovery, and field
  checks. Its largest Jacobian relative difference was `2.22086e-8` against
  `1e-7`; the absolute difference was `2.71333e-6` against `1e-5`.
  Regenerated history and contour values differ from the prior publication
  data only at roundoff scale (largest relative difference with a unit floor:
  `3.68e-13` and `2.78e-15`, respectively).
- The first full coupled invocation was terminated during its final mesh run.
  Restarting with signature-matched completed caches reran that incomplete
  case and passed the complete driver. No tolerance was changed.
- All six stability cases passed the existing checks. The three hardening
  cases retain positive sampled acoustic determinants, and the largest
  time-step field difference is `3.84763e-6`, below `5e-6`. Their current
  numerical summaries and execution observations are curated in the stability
  record. The three zero-hardening controls retain the diagnosed instability.
- All publication figures were regenerated. The numerical conclusions and
  rounded manuscript values remain supported by the refreshed results.
- The eight website/provenance unit tests, shared-source check, and manuscript
  environment check passed. The manuscript compiled successfully, with only
  the existing font-size substitutions; the added implementation paragraph
  was visually inspected on page 14 without clipping.

The final repository audit passed all eleven groups, including current
coupled/stability source hashes and provenance. The website build checked
305 local links and 26 repository Markdown links. The elastic Mandel
publication calculations were not repeated for this response; their missing
historical execution observations remain explicitly `not_recorded`.

## Original review verification record and limits

- `tools/agentctl check --profile manuscript`: passed.
- MOOSE environment `status` and `verify`: passed; framework
  `abafb58b67a6037c6723ffeb19647c84484466da`, moose-dev `2026.02.20`,
  moose-libmesh `2026.02.18_f8a1758`, moose-tools `2026.02.16`.
- `python3 validation/scripts/check_stress_trace_derivation.py`: passed over
  48 elastic and 36 fixed-plastic states; maximum reported normalized error
  approximately `2.21e-12`.
- `python3 scripts/validate_repository.py`: all repository audit groups passed.
- `python3 scripts/build_site.py`: passed, checking 298 local website links
  and 25 repository Markdown links before this report was added.
- Website packaging unit tests: 5 passed.
- `make paper`: canonical PDF was already current. Existing log reports font
  size substitutions. Feedback discussion and figure pages were visually
  inspected; no clipping was observed on those pages.
- Standard MOOSE regression suite, run from `moose_app/` using the verified
  environment and `python ../.agent-runtime/moose/python/run_tests --no-color
  -j1`: 21 passed, 2 heavy tests skipped, 0 failed, in 125.8 seconds.
- The two heavy publication studies were not rerun in this review. Their
  curated records and acceptance checks were inspected; a fresh full
  `make reproduce` is not claimed.

This review did not perform a clean-machine installation, browser interaction
testing of the deployed website, or a full citation-by-citation source-PDF
audit. It establishes the findings above from local source, selected rendered
pages, and the stated executable checks. Temporary page images and extracts
were removed after inspection. No external reviewers were contacted and no
publication or deployment was performed.
