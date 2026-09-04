# Experimental literature: discriminating datasets for the implicit-B poroplastic formulation

Status: initial literature scan (OpenAlex/Crossref, 2026-09-04). Owner: nonlinear-Biot
manuscript. Purpose: identify candidate published experimental datasets that the
finite-deformation, implicit-Biot poroplastic formulation could match and that simpler
formulations (small strain, constant or elastic-only Biot coefficient, no inelastic
pore allocation a^p) plausibly cannot.

## The formulation's discriminating physics (what we need experiments to expose)

1. Biot coefficient `B = 1 - phi_s0 dJbar/dJ|_{p,J rho_s,H}` is a fixed-pressure
   tangent that **evolves with finite strain and with inelastic pore volume** (the
   plastic pore-allocation scalar `a^p`). So: measurements showing `B` (or Skempton
   `B_s`, or drained/undrained bulk moduli) changing with mean stress / permanent
   porosity loss are direct targets.
2. Drucker-Prager-type single-prime driving stress: experiments on pressure-sensitive
   (dilatant/compactive) porous solids where the *effective-stress partitioning*
   itself changes on the plastic branch.
3. Coupled storage: undrained pore-pressure response during inelastic compaction.

## Candidate datasets (OpenAlex/Crossref verified DOIs)

| # | Study | Measured quantities | Why discriminating for this formulation | DOI |
|---|-------|--------------------|----------------------------------------|-----|
| 1 | Evolution of permeability and Biot coefficient at high mean stresses in high-porosity sandstone (2017) | `B` (and permeability) vs mean stress into the compactive regime | Directly reports Biot coefficient **evolving at high mean stress** (inelastic pore collapse) - needs a deformation/state-dependent `B`, not a constant or small-strain elastic `B`. Strongest single candidate. | 10.1016/j.ijrmms.2017.04.004 |
| 2 | Direct and indirect laboratory measurements of poroelastic properties of two consolidated sandstones (2013) | `B`, Skempton `B_s`, drained/undrained moduli (direct vs indirect) | Gives both elastic-derived and wave-derived `B`; stress dependence and method discrepancy are exactly the kind of feature an implicit, tangent-based `B` can rationalize. | 10.1016/j.ijrmms.2013.08.033 |
| 3 | Investigation of the undrained poroelastic response of sandstones to confining pressure: experiment + simulation (2007) | Undrained response / Skempton `B_s` vs confining pressure | Skempton `B_s` varying with confining pressure implies the poroelastic coupling stiffens with compaction - needs `B` that changes with state. | 10.1144/sp284.6 |
| 4 | Elastic and inelastic deformation of fluid-saturated rock (2016, review/theory) | Synthesis of drained/undrained moduli incl. inelastic deformation | Authoritative framing that elastic-only poroelasticity misses inelastic pore-volume coupling; good citation anchor for the paper's motivation. | 10.1098/rsta.2015.0422 |
| 5 | Permeability evolution during localized deformation in Bentheim sandstone (2004) | Porosity/permeability loss in compaction bands | Demonstrates large permanent pore-volume change (an `a^p`-type mechanism). Caveat: strain localization - best used as a mechanism citation, not a clean homogeneous match. | 10.1029/2003jb002942 |
| 6 | Experimental investigation on mechanical behavior and permeability evolution of a porous limestone under compression (2016) | Stress-strain + permeability under pore collapse | Pore-collapse compaction with permanent volume loss and evolving transport - matches inelastic `a^p` coupling; localization caveat applies. | 10.1007/s00603-016-1000-6 |

## Supporting / foundational (memory-based - verify before citing)

- Skempton, A. W. (1954). The pore-pressure coefficients A and B. Geotechnique 4(4). [defines B_s - foundational for undrained checks]
- Biot, M. A. & Willis, D. G. (1957). The elastic coefficients of the theory of consolidation. J. Appl. Mech. 24. [already cited in the manuscript]
- David, Menendez & Zhu (2001). Mechanical compaction, microstructures and permeability evolution in sandstones. PEPI. [compactive permeability loss - mechanism anchor]
- Wong, Baud & Klein (1997). Localized failure modes in a compactant porous rock. GRL 24. [cap/dilatancy framework]
- Baud, Vajdova & Wong (2000). Shear-enhanced compaction and strain localization in porous sandstone. JGR. [shear-enhanced compaction: needs pressure-dependent cap + pore allocation]

These memory entries have no verified DOI in this scan; use canonical-reference-finder /
latex-citation-verifier before adding to all.bib.

## Recommended next steps

1. Fetch PDFs for candidates #1-#3 and #6 into references/pdfs/ (canonical-reference-finder)
   and extract the quantitative curves (mean stress vs B; confining pressure vs B_s;
   drained/undrained moduli; porosity loss).
2. Best first quantitative match target: study #1 (Biot coefficient vs mean stress in
   the compactive regime) - a single homogeneous compression curve the implicit-B
   poroplastic model can be calibrated against (the planned 10/20/30% compression
   continuation is the natural numerical analogue).
3. Assess undrained variants (#2, #3) for the Skempton-B evolution test.
