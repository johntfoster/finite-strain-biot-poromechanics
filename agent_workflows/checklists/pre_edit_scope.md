# Pre-Edit Scope Checklist

## Common

- Identify the immediate track owner and narrowest requested scope.
- Read `AGENTS.md`, `VISION.md`, and `author_style_profile_2026-07-27.md`.
- Check `git status --short`; preserve unrelated work.
- Identify downstream tracks without editing them unless authorized.

## Manuscript

- Read `paper/main.tex` and `paper/defs.tex`.
- Resolve rendered equation numbers through current aux files.
- Inspect labels, references, displayed equations, and locked regions.
- Map notation changes through derivatives, state sets, restrictions, weak
  forms, code properties, and validation quantities.

## Implementation

- Run `tools/sync_biot_moose.py check` and map each object to a manuscript
  equation or solid-water reduction.
- Classify it as kernel, material, user object, action, BC, test, deck,
  postprocessor, or documentation.
- Record added closures, linearizations, variables, and weak-form assumptions.

## Validation

- State the physical regime, governing reduction, variables, observables,
  authoritative reference, tolerance, and output files.
- Classify the evidence as unit/regression verification, manufactured solution,
  calibration, holdout prediction, or independent physical validation.
