# Experimental data extraction: Biot-coefficient evolution under high mean stress

Date: 2026-09-04. Owner: nonlinear-Biot manuscript (experimental-comparison track).
Companion: `notes/experimental_literature_review.md`.

## PDF inventory (`references/pdfs/`)

| File | Study | OA source | Status |
|------|-------|-----------|--------|
| `ingraham-2017-biot-coefficient-high-mean-stresses-sandstone-published.pdf` | Ingraham et al., *Int. J. Rock Mech. Min. Sci.* 96 (2017) 1-10, "Evolution of permeability and Biot coefficient at high mean stresses in high porosity sandstone", DOI 10.1016/j.ijrmms.2017.04.004 | Elsevier (published; obtained via the author's added copy) | **AUTHORITATIVE**, 10 pp., full Table 3. Confirmed legitimate (Crossref clean, no retraction). Use this for calibration. |
| `ingraham-2017-biot-coefficient-high-mean-stresses-sandstone.pdf` | same study | OSTI (OA, watermarked) | 13 pp. Retained for cross-check only; the OSTI watermark "WITHDRAWN" refers to the OSTI record, not the article. Superseded by the published copy above. |
| (blocked) Makhnenko & Labuz, *Phil. Trans. R. Soc. A* (2016), DOI 10.1098/rsta.2015.0422 | Royal Society | Cloudflare challenge; not downloadable by script. Marked blocked; try institutional/manual later. |
| (paywalled) Blocher et al. (2013) DOI 10.1016/j.ijrmms.2013.08.033; Blocher et al. (2007) DOI 10.1144/sp284.6; Vajdova et al. (2004) DOI 10.1029/2003jb002942; Han et al. (2016) DOI 10.1007/s00603-016-1000-6 | publisher | Not open access; do not pirate. |



## Extracted quantitative data - Ingraham 2017 (published Table 3)

Material: Castlegate sandstone, drained, porosity 26 +/- 0.3%, water-saturated,
pore pressure ~6.89 MPa held during drained unload-reload loops. Method:
`alpha = 1 - K/Km`, with `K` the drained (jacketed) bulk modulus from unload-loop
tangents and `Km` the unjacketed bulk modulus from the single unjacketed test
(4ac37); the same empirical `Km(P)` curve is substituted into every specimen.
Listed mean stress is applied (confining); effective mean stress is applied
minus 6.89 MPa. Hydrostatic rows are those with a blank shear cell (applied
shear < 1.5 MPa).

| Specimen | P_applied | P_eff | K (MPa) | Km (MPa) | alpha |
|----------|-----------|-------|---------|----------|-------|
| 4ac21 | 22 | 15.1 | 6856 | 52278 | 0.868 |
| 4ac21 | 44 | 37.1 | 7802 | 53796 | 0.854 |
| 4ac21 | 94 | 87.1 | 10716 | 57246 | 0.812 |
| 4ac21 | 144 | 137.1 | 11864 | 60696 | 0.804 |
| 4ac22 | 32 | 25.1 | 7162 | 52950 | 0.864 |
| 4ac22 | 51 | 44.1 | 7991 | 54265 | 0.852 |
| 4ac22 | 76 | 69.1 | 8938 | 55995 | 0.840 |
| 4ac22 | 101 | 94.1 | 9730 | 57717 | 0.831 |
| 4ac22 | 121 | 114.1 | 10489 | 59093 | 0.822 |
| 4ac23 | 50 | 43.1 | 8246 | 54210 | 0.847 |
| 4ac23 | 100 | 93.1 | 10610 | 57660 | 0.815 |
| 4ac25 | 33 | 26.1 | 7342 | 53037 | 0.861 |
| 4ac25 | 73 | 66.1 | 9025 | 55810 | 0.838 |
| 4ac26 | 24 | 17.1 | 6541 | 52436 | 0.875 |
| 4ac26 | 43 | 36.1 | 8148 | 53713 | 0.848 |
| 4ac26 | 63 | 56.1 | 8998 | 55107 | 0.836 |
| 4ac27 | 35 | 28.1 | 6723 | 53140 | 0.873 |
| 4ac27 | 73 | 66.1 | 7899 | 55797 | 0.858 |

Unjacketed test 4ac37 `Km` vs applied mean stress (MPa): (51, 53410),
(76, 57769), (100, 56420), (125, 60953), (150, 59077), (177, 63781).

Trend: near-monotone decrease of the hydrostatic Biot coefficient from
~0.87-0.88 (20-50 MPa applied) to ~0.80 (120-160 MPa applied). CSS (constant
shear stress, shear > 12 MPa) rows show alpha stabilizing (~0.85-0.86) after
shear application. Permeability: ~20 Darcy initial to ~0.3-1.5 Darcy at 275 MPa
(CMS ~1 order, CSS ~2 orders).

## Calibration finding (B, step 1) - elastic stiffening explains alpha(P)

Fits from the authoritative table (effective mean stress P_eff in MPa, moduli in
MPa; linear least squares / quadratic):

```
Km(P_eff) = 51230 + 69.0 P_eff          (52.3 -> 63.0 GPa over 15 -> 170 MPa)
K(P_eff)  = 5920 + 50.6 P_eff - 0.0602 P_eff^2   (5.9 -> ~12 GPa; drained)
alpha_el(P_eff) = 1 - K(P_eff)/Km(P_eff)
```

Result: `alpha_el(P_eff)` reproduces the measured hydrostatic alpha over the
whole range with **RMS residual 0.008** (mean |resid| 0.006), i.e., equal to the
specimen-to-specimen scatter (std ~0.009 in the 15-40 MPa cluster). The drained
bulk modulus stiffens (5.9 -> ~12 GPa) faster than the unjacketed modulus
(52 -> 63 GPa), so alpha drops ~0.87 -> ~0.80 even with **no inelastic/compactive
contribution**. This matches the authors' own reading ("the Biot parameter
decreases because the bulk modulus stiffens faster than does the unjacketed bulk
modulus").

Interpretation for the manuscript (honesty constraint): the measured hydrostatic
alpha(P) decline is an *elastic tangent-stiffening* signature, not evidence for
the repo's poroplastic pore-allocation channel. A constant-modulus finite
deformation elastic law (the repo `B_el(J)` with fixed K0, Ks) cannot reproduce
Castlegate because its drained modulus does not stiffen with pressure. Matching
this data requires a pressure-/state-dependent drained bulk modulus (nonlinear
elastic stiffening), which is a separate constitutive ingredient from the
`a^p` poroplastic mechanism. The poroplastic `B` feedback is instead the
candidate for the deviatoric / genuinely inelastic channel (single-element
demonstration), and any manuscript comparison figure must be labeled so it does
not imply the hydrostatic alpha(P) data validate the plastic mechanism.

## Why the hydrostatic path is (and is not) discriminating

It discriminates the *elastic pressure dependence* of the drained modulus, which
the current repo model does not include. It does NOT isolate the inelastic pore
allocation `a^p`: over drained hydrostatic unload loops the measured alpha is an
elastic tangent quantity, and the compactive (cap) branch, if any, must be fit
to the *permanent* volume strain (Fig. 3d) rather than to alpha(P). This is the
main correction to the earlier "discriminating test" framing in this note.

## Integrity / next steps

1. DONE: "WITHDRAWN" status resolved - the published Elsevier copy is in
   `references/pdfs/`, Crossref clean, no retraction. Authoritative data above.
2. B step 1 (DONE, quantified): elastic K(P)/Km(P) stiffening explains the
   hydrostatic alpha(P) decline within scatter; see
   `notes/sandstone_comparison_feasibility.md`.
3. Next: decide whether the repo model should add a pressure-stiffening drained
   elastic law (to be comparable to Castlegate hydrostatics) as a distinct,
   labeled constitutive ingredient, separate from the poroplastic `a^p`
   demonstration; fit the compactive cap (if pursued) to permanent volume strain
   (Fig. 3d), not to alpha(P).
4. BibTeX: `ingraham2017evolution` already in `all.bib` and cited; keep.
   Do not add withdrawn/paywalled content.
