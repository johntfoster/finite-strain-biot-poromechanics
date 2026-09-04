---
name: latex-display-math-normalizer
description: Scan and normalize displayed mathematics in LaTeX manuscripts. Use when an agent is asked to find or fix display equation style issues such as chained one-line equalities, overlong numbered equations, fragile align structures, accidental numbering shifts, helper-definition numbering, inconsistent equation/align/gather usage, labels in awkward positions, or manuscript-wide display-math cleanup in .tex source.
---

# LaTeX Display Math Normalizer

## Overview

Use this skill to inspect and edit display equations for readable, stable, manuscript-consistent LaTeX. It targets style and structural problems, not mathematical correctness, though nearby math must still be read before changing displays.

## Workflow

1. Read repository-specific authoring instructions first, especially rules about display environments, numbering, locked regions, build paths, and generated artifacts.
2. Identify the canonical root file and included section files. Do not treat section files as standalone if the manuscript has a root such as `main.tex`.
3. Run `scripts/scan_display_math.py` on the target files or manuscript sections.
4. Inspect each flagged display in source context before editing. Avoid mechanical rewrites across locked regions or macro-heavy environments you have not understood.
5. Normalize only the issue requested unless the user asks for a manuscript-wide cleanup.
6. After editing, validate references and numbering with the manuscript's preferred build workflow when available. For display-structure edits, two builds may be necessary to settle references.

## Normalization Rules

- Replace one-line chained multiple-equals numbered displays with an `align` or `aligned` structure that vertically aligns the equality signs.
- Follow the repository's `AGENTS.md` numbering policy. In this repository,
  agent-introduced helper displays are numbered and descriptively labeled unless
  the author explicitly requests otherwise.
- Prefer `equation` for one numbered result, `align` for multiple aligned numbered relations, and `equation` plus `aligned` for one numbered multi-line derivation.
- Put `\label{...}` in a stable position associated with the numbered line it names.
- Avoid adding new numbered displays inside sections where rendered equation numbers are actively being discussed unless the user wants renumbering.
- Do not collapse multi-line derivations into dense one-line expressions when readability or reviewability would suffer.
- Preserve source comments, local spacing conventions, and surrounding prose unless they are part of the requested cleanup.

## Common Findings

- Chained equalities: `A = B = C = D` in a single numbered display.
- Overlong display lines that are likely to overflow or become unreadable in PDF.
- Numbered helper equations introduced only to define notation for the next line.
- `align` environments with every line numbered when only one line needs a reference.
- Labels placed before the mathematical object they name or on an unnumbered line.
- Manual spacing or line breaks that hide the logical structure of a derivation.

## Helper Script

Use:

```bash
python3 agent_environment/skills/latex-display-math-normalizer/scripts/scan_display_math.py --root . --files paper/sections/target.tex
```

The script flags likely style issues and prints line spans. Confirm each candidate manually before editing.
