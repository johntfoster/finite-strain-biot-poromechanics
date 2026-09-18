# Dilative plasticity, fluid exchange, and Biot-coefficient evolution

Audit date: 2026-09-17. Scope: qualitative physical interpretation in Section 6
and the conclusions. Numerical verification is retained separately from material
calibration. Sources were read in full-text PDFs before adding the citations.

## Makhnenko and Labuz (2015)

- Key: `makhnenkolabuz2015`; DOI: https://doi.org/10.1002/2014JB011287.
- Metadata: Journal of Geophysical Research: Solid Earth 120(2), 909–922;
  title and authors verified against the PDF and publisher record.
- Source: https://rockmechanics.cee.illinois.edu/files/2017/08/Dilatant-hardening-of-fluid-saturated-sandstone.pdf
- Evidence: Section 2, equations (9)–(12), relates dilation to pore-pressure
  reduction and hydraulic strengthening. Section 4.2.3, PDF page 12 (journal
  page 920), reports pressure reduction during undrained constant-mean-stress
  compression of Berea sandstone.
- Verdict: supports dilation-induced pressure reduction and strengthening;
  does not validate our finite-deformation Biot evolution or boundary-flow
  history. Their alpha is the Biot coefficient; their B is Skempton's coefficient.
  Their term dilatant hardening is not the prescribed isotropic yield hardening.

## Brantut (2020)

- Key: `brantut2020`; DOI: https://doi.org/10.1016/j.epsl.2020.116179.
- Metadata: Earth and Planetary Science Letters 538, 116179; verified against
  the author's university record https://discovery.ucl.ac.uk/id/eprint/10101554/.
- Full text: https://arxiv.org/pdf/1904.10906 (accepted manuscript).
- Evidence: PDF pages 8–9, Figure 4 and accompanying results, report fluid
  influx during recovery after slip-induced pressure drops. Section 6,
  PDF page 20, describes pressure drops reaching vapor pressure.
- Verdict: supports a dilation-driven pressure drop and subsequent fluid
  uptake, and the relevance of phase change. Localized dynamic granite
  faulting differs from our homogeneous constitutive specialization and loading.
  It does not validate the magnitude or sign of our Biot-coefficient change.

## Ingraham, Bauer, Issen, and Dewers (2017)

- Key: `ingraham2017evolution`; DOI: https://doi.org/10.1016/j.ijrmms.2017.04.004.
- Metadata: International Journal of Rock Mechanics and Mining Sciences 96,
  1–10; publisher record verifies final volume/pages; author list verified
  against the OSTI proof PDF.
- Full text: https://www.osti.gov/servlets/purl/1375031.
- Evidence: proof PDF page 8, discussion of Figure 6, reports a decrease in the
  measured Biot coefficient under hydrostatic loading and stabilization after
  shear loading in constant-shear-stress tests. Page 11 conclusions discusses
  the corresponding evolution of drained and unjacketed stiffness.
- Verdict: supports dependence on stress path and stiffness evolution. The
  high-pressure, predominantly compactive regime does not directly contradict
  a dilation-induced increase at fixed pressure and total volume. It does
  preclude treating an increase as a universal consequence of inelasticity.

## Manuscript action

Removed the detailed uncalibrated comparison of final mean coefficients from
the results and conclusions. Retained numerical error measures as implementation
verification. Added the open physical question and the need to compare volume
change, pore pressure, boundary fluid exchange, and poroelastic response along
matched paths. No numerical constitutive parameters or simulation outputs changed.

## Local PDF fingerprints

- `references/pdfs/2015-makhnenko-labuz-dilatant-hardening.pdf`: `8ed0005fb171588770725a325db88a27b14c48b8d6fce5910df793ff4e1f30a0`
- `references/pdfs/2020-brantut-dilatancy-pressure-drop.pdf`: `d0fe9fe28ebbc4e5fa5165d26e5020389525ee7f351a7248afc195974e474172`
- `references/pdfs/2017-biot-evolution-sandstone.pdf`: `bb5ceaf60a9c02b711c8853d4fe8428cba62a0ba31647fd701277b40dd30fd7f`
