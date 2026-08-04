# Lawal and Kim (2026) source record

- Article: Ummu-kulthum Lawal and Kiseok Kim, “Poromechanical and Crack
  Evolution of Olivine-Rich Rock During Serpentinization,” *Geophysical
  Research Letters* 53(10), e2025GL120883.
- Article DOI: <https://doi.org/10.1029/2025GL120883>
- Article license: CC BY 4.0.
- Dataset: <https://doi.org/10.5281/zenodo.20089570>
- Dataset license: CC BY 4.0.
- Raw workbook MD5: `c995782d56ef24e72a0df32999d49c12`.
- Raw Figure 3 MD5: `a8b16259f9f1689d5e40ab04037a4a8b`.

Figure 3c is not manually digitized here because the public workbook contains
the exact plotted source cells. The extraction script retains the workbook row
for every point. The workbook contains one SP30 modulus/alpha row without a
pressure coordinate; Excel omits it from Figure 3c, and the tidy extraction does
the same.

## Source inconsistency to preserve in the audit

The Figure 3b annotation reports \(K_s'=65.5\) GPa for SP14. The workbook cell
used by the Figure 3c formulas is 65.0 GPa; the published alpha cells satisfy
\(\alpha=1-K/65.0\) to roundoff. The reproduction therefore uses 65.0 GPa when
matching Figure 3c and reports a sensitivity calculation using 65.5 GPa.

