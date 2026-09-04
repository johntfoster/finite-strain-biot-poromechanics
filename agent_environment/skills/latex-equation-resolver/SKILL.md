---
name: latex-equation-resolver
description: Resolve rendered LaTeX equation numbers back to source labels and locations before answering or editing. Use in LaTeX repositories when the user refers to an equation as "equation", "eq", "(XXX)", "XXX", "number XXX", or similar numeric shorthand in the context of a paper, manuscript, derivation, notation, citation, proof, or TeX edit.
---

# LaTeX Equation Resolver

## Core Rule

When the user refers to an equation by rendered number rather than label, resolve
that number through the LaTeX build artifacts before answering or editing.

Treat these as equation-number references when the surrounding context is a
paper/manuscript/edit/derivation:

- `equation 12`, `eq 12`, `Eq. 12`
- `(12)`, `(3.7)`, `(A.4)`
- a bare number like `12` when the user is clearly discussing paper equations

Do not guess from nearby source order. Rendered equation numbers may differ from
source order because of counters, appendices, subequations, unnumbered displays,
or stale build output.

## Workflow

1. Identify the manuscript root. Prefer repository guidance such as `AGENTS.md`;
   otherwise find the root by reading TeX inputs from the likely main file.
2. Inspect build artifacts from the latest compile. Prefer aux files in the
   configured output directory, then root-level `.aux` files. Common locations:
   `paper/build/main.aux`, then other generated auxiliary files.
3. Run `scripts/resolve_equation.py` with the requested rendered number and the
   repository root.
4. Verify the returned label in the TeX source rooted at the manuscript root.
   Read the surrounding equation environment before making claims or edits.
5. If editing, modify the source equation corresponding to the resolved label,
   not the generated aux/log/PDF artifacts.

If aux data is missing or stale, compile or ask for/perform the repo's normal
LaTeX build workflow, then resolve again. If compilation is not possible, state
that the mapping is unavailable or potentially stale.

## Helper

Use the bundled script:

```bash
python3 agent_environment/skills/latex-equation-resolver/scripts/resolve_equation.py 12 .
python3 agent_environment/skills/latex-equation-resolver/scripts/resolve_equation.py "(3.7)" .
```

The script reads `.aux` files and reports labels whose `\newlabel` rendered
number matches the requested equation number. It also tries to locate the label
in source files and prints candidate `file:line` locations.

## Ambiguity Rules

- If exactly one label matches, use it.
- If multiple labels match, show the candidates and inspect source context before
  deciding.
- If no label matches, check whether the build output is stale, whether the
  number includes a section/appendix prefix, and whether the user may have meant
  a page, theorem, figure, or table number.
- If the user provides both a rendered number and a label, trust the label only
  after confirming the label's rendered number when build artifacts are
  available.

## Reporting

When answering, include the resolved label and source location when useful:

```text
Equation (12) resolves to `eq:biot_pressure_storage` at paper/sections/finite_deformation_biot.tex:120.
```

For manuscript mechanics claims, cite the TeX source location, not the aux file.
