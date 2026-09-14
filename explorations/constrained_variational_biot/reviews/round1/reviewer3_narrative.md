# Reviewer 3: narrative, scope, and presentation review

## Recommendation: major revision

This is a worthwhile and sharply scoped exploratory technical note. Its central distinction--local constitutive condensation of \(\bar J\) versus global elimination of \(\rho_s\)--is useful, clearly motivated, and likely valuable for directing a two-field prototype. In its present form, however, it is not yet a self-contained paper suitable for acceptance: the central stress identity is asserted across a derivative that is not defined consistently, the claimed energy behind the matched logarithmic residual is not displayed, and the weak/dissipative formulation is incomplete. These are repairable, but they are substantive rather than editorial changes.

The current five-page PDF has a professional, legible layout: no overfull-box, undefined-reference, or citation warnings were reported in the build log, and the title, equations, page breaks, and bibliography render cleanly. It is best described as an exploratory **technical note** until the derivations below are supplied; with those additions it could become a concise stand-alone methods paper.

## Major findings

1. **The derivation of the total stress in (11)--(12) is presently inconsistent.** At fixed \(p\) and stationary \(\bar J\), differentiating the displayed potential \(G=W_s-p(J-\phi_{s0}\bar J)\) gives the first line of (11), namely \(W_{s,\mathbf F}|_{\bar J}-pJ\mathbf F^{-T}\) (lines 165--180). The manuscript then identifies that expression with \(\mathbf P^{\prime\prime}-BpJ\mathbf F^{-T}\), while defining \(\mathbf P^{\prime\prime}\) as a derivative of a “fixed-pressure solid energy” (lines 181--183). Those are different derivative prescriptions: the \(B\) factor arises only after the fixed-pressure \(\bar J(\mathbf F,p)\) dependence and the appropriate Legendre transformation have been made explicit. As written, neither (5) alone nor stationarity changes the coefficient of \(-pJ\mathbf F^{-T}\). **Required revision:** define the double- and single-prime energies and stresses precisely, derive the fixed-pressure chain rule, and show every step connecting (11) to (12). Alternatively, revise the potential and terminology so that its envelope derivative genuinely produces the stated total stress.

2. **The claimed stationary energy is not self-contained.** The manuscript writes an unspecified \(W_s(\mathbf F,\bar J)\), then says that its stationarity condition is equivalent to the specific matched-logarithmic residual (3) (lines 139--163). No expression for the relevant volumetric energy, nor even the proportionality linking \(\partial W_s/\partial\bar J+\phi_{s0}p\) to \(R\), is given. Thus the reader cannot verify the central “energy-consistent” claim or whether \(D>0\) is a true second-variation stability condition rather than only an implicit-function condition. **Required revision:** display the relevant energy (or state and prove the exact derivative identity), identify the fixed variables, and distinguish nonzero residual derivative from positive curvature of the local potential.

3. **The proposed two-field reduction needs a more exact statement of its assumptions and boundary/initial data.** Equation (1) follows pointwise for a material solid under source-free mass balance, but the reduction does not intrinsically require a *uniform* reference mass: a prescribed spatial \(\rho_{s0}(\mathbf X)\) still gives \(\rho_s=\rho_{s0}(\mathbf X)/J\). Conversely, the text says an “independent solid-density initial condition” restores a field (lines 199--256), although such initial data ordinarily specify \(\rho_{s0}\), not an additional evolution equation. **Required revision:** distinguish source terms/reactions from spatially varying but prescribed reference density; state the compatible initial condition and what boundary data are retained after eliminating the solid-mass residual. State explicitly whether plastic-volume evolution is excluded or retained as a local internal-variable update, since \(J^e=J/a^p\) was introduced on lines 98--100.

4. **The strong, weak, and dissipative statements do not yet form a complete variational system.** The strong momentum equation includes a gravity term (15; lines 221--229), but the stated weak residual omits its body-force contribution and all boundary terms (lines 242--253). It is reasonable to omit boundaries in an exploratory note, but then the body term must also be omitted from the strong equation or the weak form must include it. The symbols \(\rho\) and \(\mathbf g\) are not defined. Likewise, the phrase “pressure-driven virtual power” is not displayed (lines 275--290), so the reader cannot check that variation of (21) yields (17), including its sign and reference/current pull-backs. **Required revision:** give one consistent weak statement with body and boundary data, define total density and flux conventions, and display the Onsager functional or virtual-power term whose \(\mathbf W_f\) variation yields Darcy’s law.

5. **The scope claim requires stronger literature positioning and more careful wording.** The introduction appropriately cites Foster--Xu and general mixture/variational sources (lines 49--76), but the manuscript does not explain what is newly derived here relative to those works or to standard mixed/Onsager poromechanics. “Exact reduction” can be read as a novel variational reduction even though it is the direct substitution of integrated solid mass balance (lines 196--204). **Required revision:** add a short paragraph that identifies this as a specialization and reformulation of the existing single-solid model, specifies what the paper contributes (the separation of local and global elimination), and avoids implying a new global reduction from the mineral constraint.

## Minor findings

1. Define the configuration of \(\Omega_0\), the regularity/admissibility of \(\boldsymbol\chi\), and the sign convention for pore pressure before the first weak form (lines 81--96 and 242--253).

2. Define “true mineral mass balance” and distinguish the reference mineral density \(\bar\rho_{s0}\) from partial density more explicitly (lines 83--96). This will help readers unfamiliar with the constituent-volume convention.

3. Do not call \(D>0\) by itself the “stable mineral response” (lines 110--118 and 303--305). Call it the selected regular branch until the energy curvature result requested above is proved.

4. Give units or a brief convention for \(\kappa\), \(\mathbf W_f\), and the referential flux pull-back (lines 212--235). This is needed to assess (17) and the dissipation density (21).

5. The bibliography is readable, but the DOI strings render as plain text in the PDF rather than demonstrated active links. Use the defined `\doi{}` macro or a bibliography style that produces clickable DOI links.

## Required revisions before a favorable decision

1. Repair and fully show the energy/Legendre/chain-rule derivation of the stress transformation.
2. Supply the matched-logarithmic energy or an equivalent verified derivative identity, and separate regularity from stability.
3. State the exact reduction hypotheses, including initial and boundary data, and correct the unnecessary uniform-reference-density restriction.
4. Present a consistent weak mechanics statement and an explicit dissipative variational functional for Darcy flow.
5. Tighten scope and novelty language, add focused literature positioning, and correct the minor notation, definition, and DOI-link issues above.
