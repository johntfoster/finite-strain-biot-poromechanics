---
name: manuscript-narrative-review
description: Review and revise the nonlinear Biot LaTeX manuscript for a rigorous, self-contained academic narrative without disrupting equation flow. Use for prose cleanup, equation-adjacent exposition, removal of development-note phrasing, redundancy review, or narrative consistency.
---

# Manuscript Narrative Review

## Purpose

Revise manuscript prose so the paper reads as a self-contained theoretical article for technically prepared readers who are not already initiated into this variational formulation. Keep the mathematical derivation intact unless a displayed equation or definition is demonstrably redundant and can be removed without breaking references, notation, or logical flow.

## Required Context

For the nonlinear Biot manuscript, follow the repository instructions first:

1. Read `AGENTS.md` and `VISION.md`.
2. For manuscript edits, read `paper/main.tex` and `paper/defs.tex`.
3. Inspect the relevant `paper/sections/*.tex` source through the `paper/main.tex` compilation graph.
4. If rendered equation numbers, labels, citations, or display structure are involved, use the appropriate LaTeX skills and current build artifacts before editing.

Use [review-checklist.md](references/review-checklist.md) for the detailed prose and redundancy checklist.

## Workflow

1. Classify the request scope: whole manuscript, section, subsection, paragraph, or local display.
2. Read enough source before editing to identify the local purpose of the passage, the definitions already available, and the controlling equations.
3. Mark protected regions (`% AGENT-LOCK-BEGIN` to `% AGENT-LOCK-END`) as off limits unless the user explicitly unlocks them.
4. Edit prose first. Prefer sentence-level and paragraph-level revisions over derivation rewrites.
5. Preserve equation environments, labels, numbering, references, and algebraic grouping unless the user asks for math changes or the redundancy check justifies a narrow removal.
6. After edits, reread the touched source and nearby displays to catch accidental environment, punctuation, or label drift.
7. Validate with `git diff --check` and, when labels/equations/citations/display formatting changed, rebuild through the repository's LaTeX build workflow.

## Prose Targets

Make the manuscript:

- self-contained for a continuum-mechanics and reservoir-simulation audience;
- precise about what each symbol, field, multiplier, force, or closure does;
- explicit about why a variational or thermodynamic step is being introduced;
- written as final academic prose, not as notes to the author, TODO commentary, or a defense of earlier drafting decisions;
- locally explanatory before theorem-heavy or jargon-heavy phrasing;
- consistent with the manuscript's established notation and source-of-truth equations.

Avoid adding broad theory, new named symbols, or extra derivation scaffolding merely to make a paragraph smoother. If a concept can be clarified in prose, do that before adding mathematics.

## Equation And Definition Discipline

Mostly leave equations alone. A prose review may remove or collapse a displayed equation or definition only when all of these are true:

- the same result is already stated nearby or in a canonical earlier equation;
- no later `\ref`, `\eqref`, label, table, or prose sentence relies on the local display;
- the surrounding argument remains readable after replacing the display with prose or a reference to the canonical equation;
- the edit does not change the derivation's algebraic content, assumptions, or variable set.

Definitions may appear immediately after a display if they are close and unambiguous. Do not force every symbol definition before the display when the local narrative is clearer with a post-display definition.

## Reporting

For edit tasks, report:

- the scope edited;
- the main narrative drift corrected;
- any equation or definition removed, retained, or intentionally left alone;
- the validation performed and any validation not run.

For review-only tasks, lead with concrete issues and source locations, then suggest focused edits.
