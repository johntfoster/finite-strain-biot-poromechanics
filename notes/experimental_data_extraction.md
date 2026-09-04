# Experimental data extraction: Biot-coefficient evolution under high mean stress

Date: 2026-09-04. Owner: nonlinear-Biot manuscript (experimental-comparison track).
Companion: `notes/experimental_literature_review.md`.

## PDF inventory (`references/pdfs/`)

| File | Study | OA source | Status |
|------|-------|-----------|--------|
| `ingraham-2017-biot-coefficient-high-mean-stresses-sandstone.pdf` | Ingraham et al., *Int. J. Rock Mech. Min. Sci.* (2017), "Evolution of permeability and Biot coefficient at high mean stresses in high porosity sandstone", DOI 10.1016/j.ijrmms.2017.04.004 | OSTI (OA) | Downloaded, 13 pp. **CAVEAT: the OSTI copy is watermarked "WITHDRAWN"** - verify journal/DOI status before using as a calibration anchor. |
| (blocked) Makhnenko & Labuz, *Phil. Trans. R. Soc. A* (2016), DOI 10.1098/rsta.2015.0422 | Royal Society | Cloudflare challenge; not downloadable by script. Marked blocked; try institutional/manual later. |
| (paywalled) Blocher et al. (2013) DOI 10.1016/j.ijrmms.2013.08.033; Blocher et al. (2007) DOI 10.1144/sp284.6; Vajdova et al. (2004) DOI 10.1029/2003jb002942; Han et al. (2016) DOI 10.1007/s00603-016-1000-6 | publisher | Not open access; do not pirate. |

## Extracted quantitative data - Ingraham 2017 (Table 3, hydrostatic unload-reload loops)

Material: Castlegate sandstone, drained, porosity 26 +/- 0.3%. Method: Biot
coefficient from unload-reload bulk modulus `K` (jacketed) and unjacketed
modulus `Km`: alpha = 1 - K/Km. Applied mean stresses to ~275 MPa; reported
effective stresses are applied minus ~6.91 MPa.

Hydrostatic (shear < 1.5 MPa) mean-stress vs Biot-coefficient points:

| Specimen | Mean stress (MPa, applied) | alpha |
|----------|---------------------------|-------|
| 4ac21 | 22 | 0.868 |
| 4ac21 | 44 | 0.869 |
| 4ac21 | 84 | 0.812 |
| 4ac21 | 144 | 0.804 |
| 4ac22 | 32 | 0.860 |
| 4ac22 | 51 | 0.852 |
| 4ac22 | 76 | 0.849 |
| 4ac22 | 101 | 0.831 |
| 4ac22 | 121 | 0.823 |
| 4ac23 | 31 | 0.861 |
| 4ac23 | 50 | 0.847 |
| 4ac23 | 73 | 0.838 |
| 4ac23 | 100 | 0.815 |
| 4ac26 | 24 | 0.875 |
| 4ac26 | 43 | 0.848 |
| 4ac26 | 63 | 0.836 |
| 4ac27 | 35 | 0.873 |
| 4ac27 | 73 | 0.858 |
| 4ac27 | 131 | 0.853 |

Trend: nearly monotone decrease of the hydrostatic Biot coefficient from
~0.87-0.88 (20-50 MPa) to ~0.80-0.82 (120-160 MPa); near-linear in this range.
CMS (constant mean stress, deviatoric loading) data show continued decrease with
mean stress; after shear application (CSS) alpha stabilizes (shear-damage
softening keeps K/Km roughly constant). Permeability: ~20 Darcy initial to
~0.3-1.5 Darcy at 275 MPa (CMS ~1 order, CSS ~2 orders).

## Why this is a discriminating test for the manuscript formulation

A constant or small-strain elastic-only Biot coefficient cannot reproduce a
monotone alpha(mean stress) decrease of ~0.06-0.08 over inelastic (cataclastic /
compactive) loading. The repo formulation's implicit, state-dependent
`B = 1 - phi_s0 dJbar/dJ|_(p,J rho_s,H)` with inelastic pore allocation a^p is
the natural vehicle; the planned 10/20/30% hydrostatic compression continuation
is the numerical analogue of this hydrostatic load path.

## Integrity / next steps

1. **Resolve the "WITHDRAWN" status** of Ingraham 2017 (Crossref record + journal
   page) before relying on it. If withdrawn, prefer Blocher et al. (2007/2013)
   (report alpha ranges 0.97-0.65 Fletchinger, 0.92-0.48 Bentheimer, with a
   nonlinear 0-20 MPa section) or Makhnenko & Labuz (2016) - obtain via
   institutional/manual access.
2. Digitize the alpha-vs-mean-stress trend (Fig. 6) for a calibration target if
   the study is confirmed usable.
3. Keep the two OA PDFs in `references/pdfs/`; add BibTeX entries (verify before
   citing). Do not add withdrawn/paywalled content to all.bib without checking.
