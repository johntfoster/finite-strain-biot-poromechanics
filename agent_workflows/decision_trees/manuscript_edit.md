# Manuscript Edit Decision Tree

## Scope

1. Identify the narrowest requested section, paragraph, equation, label, table,
   or symbol.
2. Treat `only`, `just`, and explicit file/equation limits as hard boundaries.
3. Do not edit `% AGENT-LOCK-BEGIN` to `% AGENT-LOCK-END` without explicit
   authorization.

## Before editing

Run `../checklists/pre_edit_scope.md`. For notation changes, map definitions,
state sets, held-fixed variables, chain-rule terms, stress/storage equations,
MOOSE properties, validation observables, and limiting reductions.

## Edit rules

- Preserve the notation established in `paper/main.tex` and `paper/defs.tex`.
- Do not introduce helper symbols when primitive variables suffice.
- Number and descriptively label new displays.
- Keep equations grammatical and use aligned steps for multiple equalities.
- Use automatic delimiters.
- Distinguish derived results, closures, calibrated quantities, and predictions.

## After editing

Run `../checklists/post_edit_validation.md`, rebuild from `paper/main.tex`, and
inspect the affected rendered pages.
