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

## B, step 2 - compactive (plastic) porosity-loss interpretation (DONE, calibrated)

Author directive (2026-09-04): "fit the plasticity model also."  The published
paper provides the needed plastic anchor that alpha(P) alone does not: initial
porosity 26 +/- 0.3% and Table 1 POST-TEST porosity (permanent compaction)
- hydrostatic 4ac21 (failure at ~180 MPa applied / ~173 MPa effective) -> 14%,
  CMS/CSS specimens -> 12-16%, unjacketed 4ac37 -> 22% (near zero effective
  stress, so near-initial).

Hypothesis tested: the measured drained stiffening K(P) (5.9 -> ~12 GPa) is
CARRIED BY plastic porosity loss, i.e., drained tangent K = K(porosity), and the
porosity is set by compactive (cap) plastic flow a^p < 1.  Anchor a
porosity-modulus law to the two independent endpoints and check consistency
against every intermediate unload K:

```
K(phi)  = 31880 exp(-6.47 phi)  MPa   (K0=5.9 GPa at phi0=0.26; ~12.9 GPa at phi=0.14)
Km(phi) = 80652 exp(-1.745 phi) MPa   (Km 52 -> 63 GPa; much weaker porosity sensitivity)
```

Result: the porosity-only law reproduces the measured alpha(P)
(alpha = 1 - K(phi)/Km(phi), RMS ~0.006, same as the direct K(P)/Km(P) fit),
and the inferred porosity path is smooth and monotone along the hydrostatic
path (0.245 at 15 MPa eff -> 0.153 at 137 MPa eff), ending at 0.140 at the
failure point - i.e. EXACTLY the independently measured post-test porosity
(0.14 for the hydrostatic specimen 4ac21).

Compactive pore allocation (phi_s = phi_s0/a^p with phi_s0 = 0.74):
  a^p: 1.0 -> ~0.97 (15 MPa eff) -> ~0.92 (70) -> ~0.87 (137).
Fitting the repo cap form a^p = exp(-(P_eff - P_y)/K_pl):
  yield onset P_y ~ 0-10 MPa effective (compactive from the start),
  plastic modulus K_pl ~ 1.0-1.15 GPa.
These are physical for high-porosity Castlegate (cataclastic/compactive flow
beginning at low mean stress) and land close to the earlier placeholders
(P_c ~ 80-100 MPa was too high; the alpha data place onset much lower).

Interpretation and honesty notes:
- The compactive (a^p < 1) branch lowers B = 1 - (1-B_el)/a^p, i.e. the
  Castlegate direction, complementing the dilative single-element demo
  (a^p > 1, Delta B > 0) already in the manuscript.
- NOT unique: a reversible stress-stiffening law at fixed porosity could also
  reproduce K(P); but the porosity-loss version is anchored by the independent
  post-test porosity and yields a physically smooth phi(P).  State this when
  the comparison is written up.
- Still missing for a uniquely identified hardening law: the volume-strain PATH
  (Fig. 3d), i.e., porosity vs stress between the endpoints.  If needed,
  digitize Fig. 3d for the hydrostatic specimen.

## Remaining B steps (revised)

1. (Author decision) Formalize the compactive-cap calibration as a script +
   overlay figure (elastic-fit vs compactive/porosity model vs data, with the
   inferred phi(P) or a^p(P) panel), then implement the compactive (cap)
   branch + hydrostatic driver in the MOOSE material
   (`ADDruckerPragerPoroplasticBiotMaterial` currently carries only the
   dilative cone; the volumetric surface f_v = p - p_y, compaction eta-dot <= 0
   is in the manuscript theory, Sec. 2.4, but not yet in code).
2. Any final comparison figure must state data provenance (published copy,
   Table 1 + Table 3) and label the elastic vs compactive contributions.
   Produce the PGF variant (lualatex conventions) only when the figure enters
   the manuscript.
