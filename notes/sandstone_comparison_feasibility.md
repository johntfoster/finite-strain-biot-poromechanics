# Sandstone comparison: A (feasibility) result and B (calibration) plan

Date: 2026-09-04. Owner: nonlinear-Biot manuscript (experimental-comparison
track).  Status: A completed (uncalibrated feasibility); B planned (see below).
Data source: Ingraham et al. 2017 (Castle-gate sandstone), from the OSTI copy
in `references/pdfs/` (watermarked manuscript; verify against the published
version before any final comparison figure).

## A - Feasibility model and overlay

Script: `scripts/poroplastic_sandstone_feasibility.py`.
Overlay figure: `figures/sandstone_feasibility_overlay.png`.

Model (single material point, drained hydrostatic, all idealizations stated in
the script docstring):
- Castle-gate-approximate parameters: phi0 = 0.74 (26% porosity), drained bulk
  K0 = 7.5 GPa, grain modulus K_s = 55 GPa (so small-strain B0 = 1 - K0/K_s
  ~ 0.86, matching the measured ~0.87).
- Drained hydrostatic relation P_eff = -K0 ln(J); repo finite-deformation
  elastic B_el(J); idealized compactive cap for P_eff > P_c with pore
  allocation a^p = exp(-(P_eff-P_c)/K_pl) and B_pl = 1 - (1 - B_el)/a^p
  (placeholder P_c = 80 MPa, K_pl = 1.5 GPa).

Result (uncalibrated): B declines from ~0.864 at low stress to ~0.84
(elastic-only) / ~0.84 (with cap) at ~140 MPa and ~0.79 / ~0.76 at ~270 MPa.
Overlay on the extracted Ingraham hydrostatic points (B ~ 0.80-0.88 over
~15-140 MPa effective, large specimen scatter): the model reproduces the
monotone decrease and lies within the data band but is not yet discriminating,
because (i) the data scatter is ~ +/-0.03, (ii) the drained bulk modulus K in
the experiment stiffens strongly with mean stress (Table 3: ~6.9 -> 11.9 GPa
over 22 -> 144 MPa), which is NOT yet in the model (constant K0), and (iii) the
reliable data range ends near ~160 MPa effective.

## B - Calibration plan (from Ingraham 2017)

Parameters / targets:
- phi0 = 0.74  (26 +/- 0.3% porosity).
- Grain/unjacketed modulus K_s ~ K_m: Table 3 unjacketed values ~52-64 GPa over
  the load path; take K_s ~ 55 GPa (or use the measured per-load K_m).
- Small-strain Biot limit B0 ~ 0.87-0.88 -> drained K0 = (1-B0) K_s ~ 7-8 GPa.
- Pressure-dependent drained bulk: fit K(P) from Table 3 "Bulk Modulus" vs mean
  stress (~6.9 at 22 MPa to ~11.9 GPa at 144 MPa).  This stiffening is the
  PRIMARY driver of the measured B decline and must enter the model (replace
  the constant-K0 hydrostatic closure with a K(P) closure, self-consistently in
  B_el).
- Compactive (cap) onset P_c and plastic modulus K_pl: fit to the hydrostatic
  volume-strain departure from the elastic K(P) trend; placeholders P_c ~
  80-100 MPa, K_pl ~ 1-3 GPa.  In the current cone-DP MOOSE material pure
  hydrostatic loading cannot activate yield, so reproducing the compactive part
  requires the volumetric/cap mechanism (the manuscript's second yield surface)
  in MOOSE.
- Verification targets: B0 ~ 0.87; B(137 MPa eff) in the ~0.80-0.85 cluster;
  monotone decline; porosity reduction from a^p if compactive.

Steps:
1. Add K(P) drained stiffening to the feasibility model and refit K0, K_s so
   B(P) tracks the elastic decline; quantify how much of the measured decline
   is elastic stiffening vs inelastic.
2. Add the compactive/cap mechanism (a^p < 1) and fit P_c, K_pl to the
   hydrostatic volume-strain data (endpoints only in the watermarked copy:
   e.g., final volume strains ~0.057 for the most compacted hydrostatic
   specimen; obtain the published stress-strain tables if available).
3. Implement the same compactive branch + hydrostatic driver in the MOOSE
   material and reproduce the feasibility overlay from the actual solver.
4. Produce a labeled model-vs-data figure for the manuscript.

Caveats (honesty): the freely available copy is watermarked and has no full
hydrostatic stress-strain table; a defensible calibration needs the published
version (and ideally independent measurements of drained K(P) and porosity
loss).  Keep any comparison figure clearly labeled with the data provenance.
