# Reviewer 2: reduction, balances, and discretization

## Recommendation

**Major revision.** The manuscript identifies a useful continuous reduction,
but it has not yet established that the proposed two-field problem is the same
problem as the repository's three-field finite-element formulation, nor has it
defined the claimed poroplastic extension.

## Major findings

1. **The reduction requires a compatible initial referential solid mass, not
   only a source-free balance.** The step from the local balance to
   `rho_s = rho_s0/J` is valid when
   \(J\rho_s\vert_{t=0}=\rho_{s0}\) is prescribed pointwise (uniformly for
   the specialization), and remains so only while the solid balance has zero
   sources. The draft states the integrated identity at
   `main.tex:85--94`, then treats it as automatic at `main.tex:199--204`.
   It should state the initial compatibility condition explicitly, distinguish
   a spatially varying but time-independent referential mass from the uniform
   case, and say that the two-field model no longer admits an independent
   initial condition for \(\rho_s\). The repository makes the same conditional
   statement: its balance is source-free at
   `paper/sections/finite_deformation_biot.tex:44--51` and the uniform-reference
   identity is introduced separately at `paper/sections/finite_deformation_biot.tex:53--60`.

2. **“Exact” is defensible at the continuum level, but not yet at the stated
   finite-element level.** The current implementation solves a Q2 field for
   \(\rho_s/\rho_{s0}\) (`paper/sections/implicit_ad_implementation.tex:92--101`)
   and forms its residual from \(\dot J\rho_s+J\dot\rho_s\)
   (`paper/sections/implicit_ad_implementation.tex:88--90`). By contrast,
   replacing that Q2 field with \(1/J(\mbf u_h)\) produces a nonlinear
   quadrature-point quantity that is generally not in Q2. Thus the two discrete
   algebraic systems are not simply related by elimination. The manuscript must
   replace “exact reduction” at `main.tex:196`, `main.tex:254`, and
   `main.tex:310--313` with a continuum-qualified claim, or prove discrete
   equivalence for a specified storage/time discretization. It should also give
   a discrete mass-conservation check. This is material because the existing
   implementation deliberately uses the chain-rule rate supplied by the time
   integrator, which is stated not generally to equal a backward difference of
   the complete product (`paper/sections/implicit_ad_implementation.tex:103--108`).

3. **The manuscript mixes elastic-PDE and poroplastic-PDE claims without a
   complete local evolution problem.** Equation (4) uses
   \(J^e=J/a^p\) at fixed stored \(a^p\) (`main.tex:98--107`), while the
   two-field weak system has only \((\mbf u,p)\) (`main.tex:221--253`). This
   is a valid field count only if plastic variables are explicitly local history
   variables, with a return map and a consistent outer tangent. In particular,
   \(\dot m_f\) must include the pressure-, deformation-, and plastic-state
   dependence of \(\bar J(J/a^p,p)\); it is not sufficient merely to say that
   \(\bar J\) depends on deformation and pressure (`main.tex:237--240`). The
   repository expressly limits its coupled boundary-value verification to the
   elastic specialization (`paper/sections/implicit_ad_implementation.tex:45--48`)
   and says coupled poroplastic flow still requires verification of plastic
   contributions to storage (`paper/sections/implicit_ad_implementation.tex:110--117`).
   The revision should either restrict the proposed PDE to the elastic model or
   derive the local plastic update, storage rate, and consistent tangent.

4. **Boundary data and body force are not carried consistently into the reduced
   formulation.** The strong momentum equation retains \(J\rho\mbf g\) at
   `main.tex:221--229`, but \(\rho\) is undefined there. The source model
   identifies it as total mixture density (`paper/sections/finite_deformation_biot.tex:158--166`).
   The subsequent weak form omits both this term and all boundary terms
   (`main.tex:242--252`). A derivation intended to define a boundary-value
   problem must state the displacement/traction partition and pressure/normal
   mass-flux partition, then show how each term transforms. “Boundary terms
   omitted” is adequate only after those data and the zero-body-force assumption
   are stated in the governing problem.

5. **The finite-element implications need a stability and verification plan.**
   The asserted two-field prototype is not established merely by writing Q2/Q1
   weak residuals. The existing Q2 displacement/Q1 pressure choice is reported
   with no pressure stabilization in a three-field solve
   (`paper/sections/implicit_ad_implementation.tex:93--101`), whose test deck
   also states that solid partial density is globally solved
   (`moose_app/test/tests/mandel_implicit_biot/mandel_water_q2_q1.i:1--3`).
   Eliminating it changes the block Jacobian and possibly the relevant
   inf--sup/storage behavior. The paper should specify proposed spaces and
   quadrature evaluation of \(J^{-1}\), derive the two-field consistent
   Jacobian, and require comparison with the three-field solution, mass drift,
   mesh refinement, and a Jacobian check before claiming robustness.

## Minor findings

1. The local mineral-state formula in `main.tex:208` is correct only after the
   same compatible referential-mass specialization used in `main.tex:88--93`.
   State that dependency directly at the reduced-state equation rather than
   leaving it implicit.

2. The stable-branch condition is written as \(D=\partial R/\partial\bar J>0\)
   at `main.tex:111--118`, while the repository commonly uses the equivalent
   numerator condition \(K_s+\alpha p\bar J>0\)
   (`paper/sections/finite_deformation_biot.tex:579--594`). A one-line
   equivalence would make the constraint domain easier to compare.

3. The phrase “independent solid-density initial condition” at `main.tex:254--256`
   is imprecise: a general source-free problem can have a prescribed spatial
   referential-mass distribution. The restricted two-field model removes the
   freedom to prescribe a density independently of that distribution and the
   initial deformation.

## Required revisions

1. State the exact continuum assumptions: material reference motion, zero
   solid source, compatible initial \(J\rho_s\), and the admissible initial
   referential-mass distribution.
2. Separate continuum equivalence from discrete approximation; either prove the
   selected fully discrete reduction or remove assertions of discrete exactness
   and provide a validation protocol.
3. Restrict the PDE derivation to elasticity, or add the full local poroplastic
   update and its contributions to stress, storage, and the Newton tangent.
4. Define total density and give complete boundary/body-force weak forms.
5. Add a concrete two-field finite-element design and verification matrix
   against the present Q2--Q1--Q2 formulation.
