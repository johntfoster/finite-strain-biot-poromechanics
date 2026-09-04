# Poroplastic Biot-coefficient correction: results (M3, route A)

Date: 2026-09-04. Owner: nonlinear-Biot manuscript / MOOSE (todo M3 + Delta-B seed).
Commit: this results set accompanies the M3 route-A implementation.

## Model

`v = Jbar/a^p` at fixed referential partial density and fixed history gives the
fixed-pressure tangent
  B = 1 - phi_s0 dv/dJ = 1 - (1 - B_el)/a^p,
where B_el is the elastic constrained Biot coefficient (single-solid elastic
closure).  App-local material `ADPoroplasticBiotCoefficientMaterial`; shared
local-system materials untouched.

## Verified single-element results (drained, prescribed uniaxial-strain compression)

Decks in `moose_app/test/tests/poroplastic_biot/poroplastic_delta_b*.i`
(active M=0.2, beta=0.4; inactive M=100).  Run with
`./nonlinear_biot_ad-opt -i <deck>`.

| Axial stretch (compression) | a^p | B_el | B_pl | Delta B |
|---|---|---|---|---|
| 1.0 / inactive (E-1) | 1.0000 | 0.4818 | 0.4818 | 0.0000 |
| 0.9 (10%) | 1.0229 | 0.4818 | 0.4934 | +0.0116 |
| 0.8 (20%) | 1.0472 | 0.3247 | 0.3551 | +0.0304 |
| 0.7 (30%) | 1.0736 | 0.1169 | 0.1775 | +0.0606 |

Checks:
- B_pl = 1 - (1 - B_el)/a^p exactly (e.g. 30%: 1-(1-0.11694)/1.07363 = 0.17749).
- E-1: inactive branch reproduces the elastic coefficient exactly (Delta B = 0).
- a^p = exp(beta*Delta_gamma) with Delta_gamma = 0.0566/0.1153/0.1776 at 10/20/30%.

## Interpretation and next steps

- Plastic pore allocation (dilation branch, a^p > 1) raises B toward 1, and the
  gap Delta B grows with compression (0.012 -> 0.030 -> 0.061).  This is the
  mechanism the constant-B / elastic-only formulations cannot produce.
- Next: (a) plot Delta-B vs compression (figure); (b) connect to the Ingraham
  2017 hydrostatic alpha-vs-mean-stress data (references/pdfs, local) once the
  loading path (hydrostatic, not uniaxial strain) and parameter mapping are
  aligned; (c) full momentum/Mandel wiring for the inelastic demonstration.
