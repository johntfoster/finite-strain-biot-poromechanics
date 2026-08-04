# Implicit AD nonlinear Biot coefficient

Companion derivation, MOOSE implementation, and reproducibility repository for
the nonlinear-Biot specialization of the theory in
`multicomponent_reactive_flow`. The repository uses that paper's notation,
solid-reference equations, MOOSE workflow, validation conventions, and
agent-assisted input-deck architecture.

The existing Lawal--Kim curves are a calibration to their measured drained
moduli. They verify data handling and the constrained implicit-AD constitutive
path; they are not an independent prediction of the plotted Biot coefficient.

## Repository layout

- `paper/` — manuscript and sections
- `data/raw/` — immutable public source data and checksums
- `data/processed/` — tidy Figure 3c data and fitted curves
- `scripts/` — extraction, fitting, plotting, and validation
- `moose/` — experiment decks and upstream source manifest
- `validation/` — quantitative acceptance records
- `references/` — bibliographic and source-provenance notes
- `agent_workflows/` — request routing, scoped-edit and validation checklists,
  problem schema, and MOOSE failure triage inherited from the parent repository
- `validation/equation_to_moose_map.yml` and
  `validation/theory_traceability.yml` — paper/theory/code/test traceability

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
