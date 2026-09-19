# Plastic history and the reversible Biot coefficient

Review date: 2026-09-19. Manuscript and bibliography unchanged.

## Question and conclusion

The claim under review is that the construction explicitly demonstrates how
permanent pore-volume change modifies subsequent reversible pressure coupling.
The manuscript defines the derivative with the plastic configuration fixed in
`paper/sections/finite_deformation_biot.tex:611`, gives its closed form at
line 629, and demonstrates unloading at fixed plastic state in
`paper/sections/poroplastic_results.tex:29`.

The broad claim that plasticity can change a Biot coefficient has direct
precedents. More significantly, Gajo (2011) contains the same mineral-volume
closure and reversible coefficient under the matched logarithmic constitutive
choices and zero plastic mineral-volume change. The reduction below is our
comparison of his equations; it is not a scalar equation explicitly displayed
in his paper. The inspected sources therefore support a contribution centered
on the scalar construction, its mathematical analysis, physical interpretation,
and verified numerical demonstrations. They do not support priority for the
underlying plastic-history dependence.

This is a focused review, not an exhaustive priority survey. In particular,
equivalence of the volumetric closure does not establish equivalence of the
complete plastic flow rules, hardening laws, dissipation arguments, or numerical
algorithms.

## Gajo (2011): direct constitutive precedent

A. Gajo, *Finite strain hyperelastoplastic modelling of saturated porous media
with compressible constituents*, International Journal of Solids and Structures
48, 1738–1753. DOI: [10.1016/j.ijsolstr.2011.02.021](https://doi.org/10.1016/j.ijsolstr.2011.02.021).

Full text: user-supplied published PDF,
`references/pdfs/gajo-2011-finite-strain-hyperelastoplastic.pdf`, 16 pages.
SHA-256: `0cf3c3f25e9a518894865672fab45af23db3519ab4daaaeb13850ff339fdbfcc`.
The retrieved file matches the source hash. The extraction reports an extra
trailing page; use printed journal pages for citations. Original PDF pages 5
and 6 were visually checked, including equations (35)–(39) and (47)–(51).

Evidence:

- Section 4, p. 1742, discusses dependence of stored energy on plastic volume
  and plastic fluid-mass variables and the resulting elastoplastic coupling.
- Equations (34)–(38), p. 1742, prescribe logarithmic mineral elasticity and
  split elastic mineral volume into pressure and contact-stress factors.
- Equations (47)–(51), p. 1743, specialize to a logarithmic skeleton law and
  give a current-state pressure multiplier valid in elastic and plastic states.
- Appendix C.1, p. 1748, imposes zero plastic mineral-volume change, so total
  mineral volume equals elastic mineral volume. Skeleton plastic volume can
  still evolve. This is the relevant specialization for our comparison.
- Equation (65), p. 1744, and Appendix B, p. 1747, give rate couplings with
  the same dimensionless pressure-coupling fraction encountered in the 2010
  elastic paper. Those matrix entries also contain fluid and configuration
  factors; the entire entry must not be identified with our scalar B.

For the reduction, identify Gajo's solid reference fraction `1-n0` with
`phi_s0`, total mineral Jacobian `Js` with `bar J`, skeleton plastic Jacobian
`Jp` with `a^p`, and elastic skeleton Jacobian `Je` with `J/a^p`.
Set his plastic mineral Jacobian to unity as in Appendix C.1. His equations
(35), (37), and (38), with the definition of effective mean Kirchhoff stress
immediately below (38), imply

```text
Ks ln(bar J) = K'_vol/phi_s0 - p bar J.
```

Equation (39), specialized with (47), gives

```text
K'_vol = K ln(Je/Js-f^e)
       = K ln(Je) + (K/Ks) p bar J.
```

Substitution therefore gives exactly the manuscript mineral residual:

```text
Ks ln(bar J) + [1 - K/(phi_s0 Ks)] p bar J
             - (K/phi_s0) ln(J/a^p) = 0.
```

Gajo's mean Cauchy stress follows from (48) and (51):

```text
sigma_m = (K/J) ln(J/a^p) - [1 - K bar J/(J Ks)] p.
```

His alpha in (51) is the finite pressure multiplier relative to the displayed
skeleton stress. Because mineral volume depends on pressure, alpha is not our
reversible pressure derivative at nonzero pressure. Differentiate the mineral
residual at fixed total deformation and plastic state, then differentiate this
mean stress. The result is precisely

```text
B = - partial sigma_m / partial p |_(F,Fp)
  = 1 - K bar J / {J [Ks + (1-K/(phi_s0 Ks)) p bar J]}.
```

Thus our reversible coefficient, including its dependence on plastic history,
is recoverable from Gajo (2011). Its absence as a standalone displayed formula
would not establish a new constitutive mechanism.

As an additional consequence of this shared closure, holding K, Ks, phi_s0,
J, and p fixed gives

```text
partial B / partial ln(a^p) |_(J,p)
 = K^2 Ks bar J
   / {phi_s0 J [Ks + (1-K/(phi_s0 Ks)) p bar J]^3} > 0
```

on the positive-residual-slope branch. The equality and sign are our algebraic
deduction under the stated assumptions. They should not be attributed as a
theorem stated by Gajo. This result explains the manuscript's matched-volume,
matched-pressure history comparison and provides a useful way to present it.
Symbolic checks verified the residual reduction, pressure derivative, and
plastic-distention sensitivity.

Support verdict: **supports** prior existence of the specialized constitutive
dependence, by explicit reduction. Role: direct theoretical precedent.
Action: supplement Gajo (2010) with Gajo (2011) when manuscript revisions are
authorized; do not claim the plastic-history dependence as a first derivation.

## Suvorov and Selvadurai (2019): active plastic tangent

A. P. Suvorov and A. P. S. Selvadurai, *The Biot coefficient for an
elasto-plastic material*, International Journal of Engineering Science 145,
103166. DOI: [10.1016/j.ijengsci.2019.103166](https://doi.org/10.1016/j.ijengsci.2019.103166).

Published full text downloaded from the
[author's university](https://www.mcgill.ca/civil/files/civil/315.pdf), saved as
`references/pdfs/suvorov-selvadurai-2019-biot-elastoplastic.pdf` and indexed.
Original PDF p. 6 was visually checked.

Section 2 eliminates the plastic-strain increment using consistency before
identifying the pressure coefficient: equations (2.14)–(2.17), pp. 3–4.
Section 3 derives a closed expression depending on plastic-zone size,
equation (3.21), p. 6. Figure 2, p. 7, plots the coefficient increasing toward
unity as the plastic region spreads. Equation (3.26) relates it to the drained
elastoplastic tangent modulus. The conclusions, pp. 12–13, restrict the
demonstrations to monotonic loading and identify unloading residual effects
as requiring an additional analysis. The analytical geometry neglects evolving
porosity; the authors discuss the consequence for larger strains on p. 13.

Support verdict: **supports** an explicit analytical and numerical precedent
for evolution during plastic loading; **related-only** to the narrower claim
about the reversible coefficient measured with plastic variables frozen.
Role: essential comparison. Their active plastic tangent and our reversible
tangent are different derivatives, even though both are called Biot
coefficients. This distinction is scientifically useful but does not remove
the direct Gajo (2011) precedent.

The ancestry identified in this paper includes Rice (1977) for pressure in
inelastic constitutive laws and Chu and Hashin (1971) for the composite-sphere
plasticity solution. These are leads, not independently verified priority
sources in this review. Rice's author-hosted page reports proceedings pages
295–297, whereas some later citations give 360–363; resolve that discrepancy
before adding a bibliography entry.

## Other inspected evidence and related mechanisms

| Source | Full-text evidence | Verdict and role |
| --- | --- | --- |
| Gajo (2010), DOI [10.1098/rspa.2010.0018](https://doi.org/10.1098/rspa.2010.0018) | Local published PDF; earlier detailed audit in `finite-strain-pressure-coupling-literature-2026-09-18.md`. Equations (3.32), (3.34), (3.47), and section 5 support the elastic reduction. | Supports elastic constitutive ancestry. Use alongside the 2011 extension. |
| Ingraham et al. (2017), *Evolution of permeability and Biot coefficient at high mean stresses in high porosity sandstone* | Local published PDF; section 4.3, Figure 6 and Table 3. Unload–reload measurements give changing modulus ratios and inferred Biot coefficients; shear loading affects their evolution. | Supports experimental variability of reversible coupling with loading and structural change. Does not isolate our fixed-J, fixed-p plastic-distention mechanism. |
| Meschke and Grasberger (2003), *Numerical Modeling of Coupled Hygromechanical Degradation of Cementitious Materials* | [Institution-hosted full text](https://www.mm.bme.hu/edu/msc/kapcsoltf/hf2/h3.pdf), saved as `meschke-grasberger-2003-hygromechanical.pdf`. Coupling-coefficient section, equation (29), PDF pp. 4–5: the coefficient depends on saturation and the evolving drained stiffness tensor in an elastoplastic-damage model. | Supports a separate established route from irreversible damage to changed reversible coupling. Linearized kinematics and damage differ from our logarithmic mineral closure. |
| Makhnenko and Labuz (2016), DOI [10.1098/rsta.2015.0422](https://doi.org/10.1098/rsta.2015.0422) | [Published full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5014295/), sections 2 and 4. Poroelastic parameters vary with stress; a calibrated elastoplastic model describes dilatant hardening. | Related experimental and physical context. Dilatant hardening alone is not evidence for our specific reversible-coefficient evolution law. |

The Meschke–Grasberger PDF appears to retain proof pagination and a provisional
DOI ending in `(1)`; do not copy that DOI into the bibliography without checking
the final publication record. Its references identify Shao (1998) and Bary
et al. (2000) as earlier damage-coupling work; those full texts were not audited
and remain candidate-unverified. Gajo's introduction also identifies Borja
(2006) as finite-deformation work with nonconstant coefficients; no priority
verdict on that work is assigned here.

## Search limits and recommended positioning

Searches covered exact Gajo titles and DOI, plastic strain/history/distention
with Biot-coefficient evolution, reversible versus plastic tangents,
elastoplastic coupling, and damage. References were followed from the inspected
2011, 2019, and 2003 papers. Google Scholar exact-title requests for Gajo (2011)
and Suvorov–Selvadurai (2019) returned HTTP 403 on the review date. No Scholar
counts are reported, and no priority judgment rests on citation counts.

An appropriate positive contribution statement is:

> We reduce the coupled mineral and skeleton response to a scalar mineral
> equation of state and obtain its reversible Biot coefficient by implicit
> differentiation. The construction makes the influence of permanent
> pore-volume change explicit, establishes the branch on which the mineral
> response is locally unique, and demonstrates how plastic history changes
> pressure coupling during unloading and subsequent loading.

This states what the paper establishes without claiming that a new physical
dependence first appears here. The mathematical reduction and physical
demonstrations can be valuable contributions even when their constitutive
ancestry is acknowledged. The quantitative importance and journal-level
significance should be argued from those results rather than from an
unsupported claim of precedence.
