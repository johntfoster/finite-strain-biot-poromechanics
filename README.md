# Implicit AD nonlinear Biot coefficient

Standalone paper and reproducibility repository for the MOOSE implementation of
a constrained finite-deformation Biot coefficient and a nonreacting replication
of the pressure-dependent dunite measurements of Lawal and Kim (2026).

## Repository layout

- `paper/` — manuscript and sections
- `data/raw/` — immutable public source data and checksums
- `data/processed/` — tidy Figure 3c data and fitted curves
- `scripts/` — extraction, fitting, plotting, and validation
- `moose/` — experiment decks and upstream source manifest
- `validation/` — quantitative acceptance records
- `references/` — bibliographic and source-provenance notes

## Reproduce the data extraction

```bash
python3 scripts/extract_lawal_kim_figure3c.py \
  data/raw/GRL_Poromechanical_Measurements.xlsx \
  data/processed/lawal_kim_figure3c.csv
python3 scripts/verify_lawal_kim_figure3c.py data/processed/lawal_kim_figure3c.csv
```

## Build the manuscript

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error \
  -outdir=paper/build paper/main.tex
```

The published article is open access under CC BY 4.0. The underlying workbook
is cited by its version DOI, `10.5281/zenodo.20089570`.

## Complete validation

With the MOOSE conda environment active, the complete data, constitutive-fit,
implicit-AD MOOSE, figure, and manuscript workflow is:

```bash
make reproduce
```

For a quick audit of the committed artifacts without rerunning MOOSE:

```bash
make validate
```
