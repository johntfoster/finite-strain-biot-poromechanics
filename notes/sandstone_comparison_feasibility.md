# Sandstone comparison: A (feasibility) result and B (calibration) status

Date: 2026-09-04. Owner: nonlinear-Biot manuscript (experimental-comparison
track).  Data source: Ingraham et al. 2017, Castlegate sandstone, the PUBLISHED
copy in `references/pdfs/ingraham-2017-biot-coefficient-high-mean-stresses-
sandstone-published.pdf` (Elsevier, IJRMSS 96 (2017) 1-10,
doi:10.1016/j.ijrmms.2017.04.004).  This resolves the earlier caveat that only a
watermarked OSTI copy was available.

## B, step 1 - calibrated elastic pressure-stiffening model (DONE)

Script: `scripts/poroplastic_sandstone_feasibility.py`.
Figure: `figures/sandstone_feasibility_overlay.png`.
Extraction detail: `notes/experimental_data_extraction.md` (authoritative
published Table 3 hydrostatic rows).

Fit (P_eff in MPa = applied - 6.89; moduli in MPa), computed in the script from
the authoritative table:

```
Km(P_eff) = 51230 + 69.0  P_eff                    (unjacketed)
K(P_eff)  =  5925 + 50.63 P_eff - 0.0602 P_eff^2   (drained tangent)
alpha_el(P_eff) = 1 - K(P_eff)/Km(P_eff)
```

Result:
- alpha0 (P_eff -> 0) = 0.884, consistent with the measured low-stress
  cluster (~0.86-0.88).
- The elastic stiffening model reproduces the measured hydrostatic alpha
  decline (~0.87 -> ~0.80 over 15 -> 140 MPa effective) with RMS residual 0.008,
  equal to the specimen scatter (~0.009).  No inelastic/compactive contribution
  is required to explain alpha(P) on the drained hydrostatic path.
- The constant-modulus repo elastic coefficient (B_el(J), fixed K0/Ks, drained
  modulus does not stiffen) is nearly flat (B ~ 0.884 -> 0.881) and misses the
  data with RMS 0.041 (about 5x worse).

Conclusion (honesty, for the manuscript):
1. The measured Castlegate hydrostatic alpha(P) decline is an ELASTIC
   tangent-stiffening signature: the drained bulk modulus stiffens (5.9 ->
   ~12 GPa) faster than the unjacketed modulus (52 -> 63 GPa).  This matches the
   authors' own interpretation in the paper.
2. The repository's constant-modulus finite-deformation elastic B_el(J) cannot
   capture this, and the poroplastic pore-allocation a^p mechanism is NOT the
   right tool for the pure hydrostatic alpha(P) path (an unload-loop alpha is an
   elastic tangent quantity).  Matching Castlegate requires a pressure/state-
   dependent drained bulk modulus as a separate, labeled constitutive
   ingredient.
3. The poroplastic B feedback remains the candidate for the genuinely
   inelastic / deviatoric channel (single-element demonstration), not for this
   hydrostatic data set.

## A - earlier feasibility model (superseded)

The previous committed model used a constant drained K0 plus an idealized
compactive cap (a^p < 1).  It was uncalibrated, lay inside the broad data band,
and was not discriminating.  That model has been REPLACED by the calibrated
elastic stiffening model above (B step 1); the constant-modulus curve in the new
figure plays the role of the "no stiffening" reference.

## Remaining B steps (revised)

1. Decide, with the author, whether to add a pressure-stiffening drained
   elastic law to the MOOSE model so the hydrostatic comparison becomes a true
   model-vs-data check (a distinct ingredient from the poroplastic a^p
   mechanism).  Until then, do NOT claim the poroplastic single-element model
   reproduces the Ingraham hydrostatic alpha(P) data.
2. If the compactive (cap) branch is pursued for Castlegate, fit it to the
   PERMANENT volume strain (Fig. 3d / volume-strain data), not to alpha(P);
   placeholders P_c, K_pl are not anchored by the hydrostatic alpha data.
3. Any final comparison figure must state data provenance (published copy,
   Table 3) and label elastic-stiffening vs inelastic mechanisms separately.
   Produce the PGF variant (lualatex conventions) only when the figure enters
   the manuscript.
