# Round-2 Reviewer 2: continuum reduction, boundary-value problem, and prototype plan

**Recommendation: minor revision.**

The revision resolves the substantive system-level concerns from the first
round.  In particular, the manuscript now makes the right distinction between
the pointwise constitutive condensation of \(\bar J\) and the continuum
elimination of \(\rho_s\).  Equations (1)--(2) state the compatible
source-free solid-mass consequence correctly, and the reduced storage
\(m_f=(J-\phi_{s0}\bar J)\bar\rho_f\) follows directly.  The momentum and
fluid-mass weak residuals also have the correct integration-by-parts signs for
the displayed strong equations and a referential mass flux.  The discrete
caveat at `main.tex:306--316` is important and correct: substituting
\(\rho_{s0}/J(\mathbf u_h)\) is not algebraically the same as retaining an
independently interpolated Q2 solid-density field.

The following limited changes would make the proposed two-field boundary-value
problem and prototype plan reproducible.

1. **State the boundary partitions and prescribed data explicitly.**  At
   `main.tex:261--298`, say that \(\Gamma_u\dot\cup\Gamma_t=\partial\Omega_0\)
   and \(\Gamma_p\dot\cup\Gamma_w=\partial\Omega_0\), up to measure-zero
   intersections, and give the data: \(\mathbf u=\bar{\mathbf u}\) on
   \(\Gamma_u\), \(\mathbf P_{\rm tot}\mathbf N_0=\bar{\mathbf t}\) on
   \(\Gamma_t\), \(p=\bar p\) on \(\Gamma_p\), and
   \(\mathbf W_f\cdot\mathbf N_0=\bar w_f\) on \(\Gamma_w\), where
   \(\mathbf N_0\) is outward.  This will remove any ambiguity in the
   sign of the final boundary term in (16) and establish that traction and
   flux data are referential quantities.

2. **Complete the initial-data statement for the time-dependent two-field
   problem.**  The compatible solid datum is stated well at `main.tex:91--108`.
   The reduced fluid equation nevertheless requires an initial pressure (or
   equivalently initial referential fluid mass), consistent with the mineral
   root and the imposed initial deformation.  Add a compact statement before
   (14), for example: prescribe \(\mathbf u(\mathbf X,0)\) as compatible
   with the mechanical data and prescribe \(p(\mathbf X,0)=p_0(\mathbf X)\);
   obtain \(\bar J(\mathbf X,0)\) from (3) on the selected positive-curvature
   branch.  It should also say that the reduced solid density is then
   \(\rho_{s0}/J(\mathbf X,0)\), rather than independent input.

3. **Narrow the one inertial sentence or supply its missing model.**  The
   reduced equations are quasistatic, but `main.tex:331--333` says that the
   same variation enters an action with inertia.  In a mixture this requires
   an explicitly selected kinetic energy and momentum approximation (including
   whether fluid relative inertia is neglected).  Since neither is part of the
   paper, replace that statement with a forward-looking scope limitation, or
   provide those ingredients.  This avoids suggesting that (14)--(18) already
   define a dynamic Hamilton principle.

4. **Turn the prototype paragraph into a minimally auditable verification
   set.**  The existing requirements at `main.tex:306--316` are strong.  Add
   (i) a quadrature-point check of \(R=0\) and
   \(K_s+\alpha p\bar J>0\), (ii) a global fluid balance check whose boundary
   flux sign follows the stated \(\bar w_f\) convention, (iii) spatial as well
   as temporal refinement against the three-field solution, and (iv) a
   small-strain/drained reference check recovering \(B=1-K/K_s\).  The paper
   should characterize Q2--Q1 as a candidate pair to be tested for this
   reduced nonlinear storage problem, rather than imply that it inherits a
   stability result from the Q2--Q1--Q2 formulation.

None of these points changes the central conclusion.  With the specified
boundary/initial data and verification additions, the note provides a sound
continuum blueprint for a source-free elastic two-field prototype while
correctly declining to claim discrete equivalence or a poroplastic result.
