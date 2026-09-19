# Finite-strain pressure coupling: literature comparison

Search date: 2026-09-18. Original-PDF verification: 2026-09-19.

## Question and finding

The claim tested was whether the mineral-pressure contribution
`(K/K_s) p Jbar` in `eq:matched-logarithmic-double-prime-stress` had no
precedent in finite-strain porous-medium energies and stresses. The claim is
not supported: Gajo (2010) gives this term explicitly in equation (3.47),
and includes coupling work in the energy in equations (3.37)–(3.39).
The paper should emphasize its derivation, stress interpretation, closed-form
evaluation, poroplastic update, and verification without claiming priority
for the elastic coupling term or for coupled finite-strain energies generally.

## Sources and support audit

| Source | Evidence inspected | Verdict and role |
| --- | --- | --- |
| Gajo (2010), DOI [10.1098/rspa.2010.0018](https://doi.org/10.1098/rspa.2010.0018) | Local published PDF, pp. 3063–3065, 3073–3074, 3076–3078, and 3082–3083; original equation typography visually checked. Title-page metadata agrees with the BibTeX entry and prior Crossref verification. | Contradicts absence of the term; direct elastic constitutive precedent. Added as `gajo2010`. |
| Sun, Ostien, and Salinger (2013), DOI [10.1002/nag.2161](https://doi.org/10.1002/nag.2161) | Local full PDF, equations (5)–(9), PDF pages 4–5. | Supports a narrower comparison: this implementation assumes a pressure-independent effective first Piola stress and uses the modulus-ratio Biot coefficient. Its phase stress already contains a `K/K_s` pressure contribution. Retained existing implementation citation. |
| Kazemian et al. (2025), DOI [10.1016/j.ijsolstr.2025.113436](https://doi.org/10.1016/j.ijsolstr.2025.113436) | Published PDF, section 2, journal page 3, equations (6)–(9). | Related explicit alternative: a quadratic Hencky/porosity energy gives total Kirchhoff stress with a constant `b p` contribution. Different constitutive choice and stress-volume scaling; not evidence that coupling energy is generally absent. No manuscript citation added. |
| MacMinn, Dufresne, and Wettlaufer (2016), DOI [10.1103/PhysRevApplied.5.044020](https://doi.org/10.1103/PhysRevApplied.5.044020) | Local full preprint, sections II–III. | Related-only for this question: incompressible constituents exclude the finite-mineral-compressibility mechanism. Retained as large-deformation context. |
| Gajo (2011), DOI [10.1016/j.ijsolstr.2011.02.021](https://doi.org/10.1016/j.ijsolstr.2011.02.021) | Publisher metadata and abstract only. | Candidate-unverified for detailed plastic equivalence. The existence of this finite-strain hyperelastoplastic paper precludes treating a general extension to plasticity as an established priority claim. No equation-level claim or new citation added. |

The direct source for the Gajo full-text extraction is the
[author-uploaded publication](https://www.researchgate.net/publication/243685858_A_general_approach_to_isothermal_hyperelastic_modelling_of_saturated_porous_media_at_finite_strains_with_compressible_constituents).
Initial publisher and institutional retrieval attempts returned HTTP 403.
That access limitation was resolved on 2026-09-19 using the user-supplied
published PDF, retrieved from Hamilton and stored as
[the local Gajo source](../pdfs/gajo-2010-compressible-constituents.pdf).
The 27-page PDF was ingested with the repository research-store script;
extracted text and retrieval state remain under `.agent-runtime/research/`.
The source and received copies have SHA-256
`68d3bb7d6f726a41b7d76e8c13271d4bb5a886047445792b20dbccb0d0f47217`.
The duplicate root filename was moved to the same reference path on Hamilton.

### Original-PDF audit of the contribution revision

- **Metadata and variables: supports.** The title page confirms the author,
  title, year, journal, volume, pages, and DOI in `gajo2010`. Equations
  (2.6)–(2.7), journal p. 3065 (PDF p. 5), confirm `J_s=Jbar` and
  `1-n_0=phi_s0`, including the current-volume fraction relation.
- **Scalar closure: supports.** Equations (3.27), (3.32), and both parts of
  (3.34), journal pp. 3073–3074 (PDF pp. 13–14), match every source relation
  transcribed in the new appendix. The trace is divided by three, and the
  contact-stress relation is divided by the reference solid fraction.
  The pressure relation contains the total mineral ratio `J_s`, not the
  pressure factor `J_(s-f)`. Elimination and reverse reconstruction are valid.
- **Finite pressure factor: supports.** Equations (3.47)–(3.48), journal
  p. 3077 (PDF p. 17), confirm the total Kirchhoff stress and
  `alpha=1-K J_s/(J K_s)`. Dividing by total `J` gives the appendix's
  mean Cauchy stress. Gajo's double-prime stress in this passage is the
  drained stress; it is not the manuscript's current-pressure energy derivative.
- **Rate coupling: supports.** The original typography on journal
  pp. 3082–3083 (PDF pp. 22–23) distinguishes Greek `alpha` from Roman `a`:
  `alpha=1-K J_s t/(J K_s)` and `a=K t/[K_s(1-n_0)]` in (5.4).
  The ratio `[alpha+r(1-a)]/[1+r(1-a)]` in (5.12) and (5.14) reduces
  to the manuscript's `B` when `t=1` and `r=p J_s/K_s`.
  These equations include additional fluid/volume factors multiplying that
  dimensionless ratio; the manuscript correctly identifies the coupling
  factor rather than equating `B` with the whole rate-matrix entry.
- **Energy and assumptions: supports within the stated specialization.**
  Equation (3.39), journal p. 3076 (PDF p. 16), confirms the sign and
  factors in the coupled energy comparison below. Pages 3063–3064 and
  Sec. 3(c) require separated volumetric/isochoric energies, logarithmic
  mineral response, and equivalent isotropic mineral strains under isotropic
  macroscopic effective loading and pore pressure. The appendix now states
  these assumptions explicitly. Plastic equivalence remains outside this audit.
- **Rate-form interpretation and novelty: appropriately scoped.** The remark
  on journal p. 3078 (PDF p. 18) concerns `alpha` for general skeleton
  energies. Section 5 expresses its tangent quantities in the current state.
  The manuscript's distinction between finite pressure change and local
  tangent response is consistent with these equations. The explicit scalar
  construction and reconstruction are defensible contribution statements;
  the PDF does not establish first-in-literature priority for that reduction.

No sign, scaling, or algebraic correction was needed in the new appendix.
Independent symbolic checks reconfirmed the scalar elimination, pressure
sensitivity, rate-factor reduction, and mapped elastic volumetric energy.
The full-PDF check supersedes the previous extraction-only verification.

The Kazemian PDF was acquired from the
[University of Glasgow repository](https://eprints.gla.ac.uk/356644/1/356644.pdf)
and saved as `references/pdfs/kazemian-2025-column-solid-compressibility.pdf`.
Local sources were ingested with the repository research-store script.

## Algebraic comparison

The following mapping and simplifications are our comparison, rather than
claims quoted from the source. For virgin elasticity, map Gajo's `J_s` to
`Jbar`, `p_w` to `p`, and `1-n_0` to `phi_s0`. His mean total Kirchhoff
stress becomes

`K ln J + (K/K_s) p Jbar - J p`.

This is exactly the manuscript's total mean Kirchhoff stress when `J^e=J`.
His factor relative to the drained stress is `1-K Jbar/(J K_s)`. It is a
secant pressure factor. The manuscript's fixed-pressure volume derivative is

`B = 1 - K Jbar / {J [K_s + (1-K/(phi_s0 K_s)) p Jbar]}`.

These are distinct decompositions of the same elastic total stress. The
double-prime stress in the manuscript is the derivative of the reduced solid
energy at fixed pressure, so it retains the compensating pressure correction.
Gajo's rate formulation contains the same elastic tangent coefficient. The original PDF confirms the symbols previously obscured by text
extraction. Use the source names
`alpha=1-K Jbar/(J K_s)`, `a=K/(phi_s0 K_s)`, and `r=p Jbar/K_s`.
For his logarithmic specialization the stiffness factor `t` is one.
The rate coupling factor in equations (5.12) and (5.14) is
`[alpha+r(1-a)]/[1+r(1-a)]`. Substitution gives exactly the manuscript's
`B` above; an independent SymPy simplification returned zero for the
difference. Equations (5.3) and (5.7) also recover this factor as the
derivative of reference pore volume with respect to `J` at fixed pressure.
Thus the difference from the secant pressure factor does not establish
novelty of the elastic closed-form tangent. Plastic equivalence remains a
separate question requiring the 2011 full text.

For an explicit energy check, use temporary comparison variables only in this
note: `x=ln J`, `z=ln Jbar`, `q=phi_s0`, `c=1-K/(q K_s)`, and
`y=ln J_(s-f)=-p Jbar/K_s`. The shared mineral relation gives
`z=K x/(q K_s)+c y`. The manuscript volumetric energy is

`K (x-z)^2/(2c) + q K_s z^2/2`.

After separating the pore-fluid energy, the source's logarithmic
specialization has solid terms

`K (x-y)^2/2 + q K_s y^2/2 + K (x-y)y`.

Substitution reduces both to `K x^2/2 + (q K_s-K)y^2/2`.
SymPy simplification returned zero for their difference. A separate symbolic
check of the equilibrated total Cauchy pressure derivative returned `-B`.
These checks establish the mapped elastic volumetric agreement; they do not
compare plastic internal variables or return mappings.

## Search scope and limits

Searches combined finite strain, compressible constituents, effective stress,
stored energy, logarithmic poroelasticity, and mineral-pressure coupling.
The reference chain led from recent logarithmic consolidation to earlier
compressible-constituent formulations. De Buhan and Dormieux (1998) and
Ehlers (2018) were also identified, but full PDF access was unsuccessful;
no equation-level verdict rests on those candidates. No exhaustive absence
or first-in-literature claim is made.

Google Scholar exact-title lookups for Gajo (2010) and Kazemian et al. (2025)
were inaccessible on the audit date. Citation counts are unavailable and
were not inferred from search ordering or substituted from another database.
Gajo was selected for direct equation support, not a citation-count ranking.

## Manuscript action

The title now names both poroelasticity and poroplasticity. The abstract,
introduction, constitutive discussion, elastic and plastic results, and
conclusions explain the role of mineral-pressure coupling. The introduction
and stress discussion credit the elastic precedent. The finite-deformation
profiles describe the complete model response, not a numerical experiment
isolating removal of the pressure correction. No constitutive equations,
implementation files, numerical data, or figures were changed for this review.

## Implicit mineral closure and historical review

Eliminating Gajo's mineral factors from equations (3.27), (3.32), and
(3.34) gives, with `q=1-n0=phi_s0`,

`ln J_(s-f) = -p Jbar/K_s`,

`ln J_(s-m) = K [ln J-ln J_(s-f)]/(q K_s)`,

`ln Jbar = ln J_(s-m)+ln J_(s-f)`.

Consequently,

`K_s ln Jbar + [1-K/(q K_s)] p Jbar - (K/q) ln J = 0`.

This is precisely manuscript equation `eq:verification-mineral-factors`
(rendered as 62 on the audit date) for virgin elasticity. The rate coupling
coefficient is algebraic in the current state; it does not eliminate this
implicit constitutive closure. This is our elimination, not a claim that
Gajo displays this exact residual verbatim. His primary macroscopic variables
include fluid mass, so his overall closure also uses saturation and the
fluid equation of state.

Following Gajo's historical review led to Biot (1972), *Theory of Finite
Deformations of Porous Solids*, Indiana University Mathematics Journal
21(7), 597–620, DOI 10.1512/iumj.1972.21.21048. The publisher PDF was
saved as `references/pdfs/biot-1972-finite-deformations.pdf` from
https://www.iumj.indiana.edu/IUMJ/FTDLOAD/1972/21/21048/pdf .
The scan has no usable text layer; pages 597–600 were visually inspected.
Equations (2.5), (2.10), (2.14), and (2.20) support the introduction's
statement that deformation and fluid mass are potential arguments and that
stress and fluid potential follow by differentiation. Crossref metadata and
the scanned title page were checked. Added as `biot1972`.

Coussy, Dormieux, and Detournay (1998), Armero (1999), and Gajo (2011)
were identified in the reference chain, but accessible metadata or abstracts
do not establish their detailed constitutive equivalence. Attempts at
institutional full-text retrieval failed. No technical comparison or claim
of plastic priority is based on them. The expanded review therefore follows
the verified Biot potential, Drumheller constituent/distention description,
Gajo compressible-constituent energy, and existing computational references.
