# Constrained variational Biot exploration

This standalone manuscript investigates whether the scalar mineral equation
in the repository's single-solid, single-fluid finite-deformation Biot model
can serve as a variational constraint that reduces the global system.

It is an exploratory artifact.  It does not change the canonical manuscript,
MOOSE implementation, validation records, or equation-to-object map.

Build from the repository root:

```sh
latexmk -lualatex -interaction=nonstopmode -halt-on-error \
  -outdir=explorations/constrained_variational_biot/build \
  explorations/constrained_variational_biot/main.tex
```

The manuscript derives a local variational interpretation of the mineral
equation and an exact two-field reduction that follows separately from
source-free solid mass conservation.
