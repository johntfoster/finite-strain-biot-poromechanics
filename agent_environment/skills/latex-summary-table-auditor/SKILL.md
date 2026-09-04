---
name: latex-summary-table-auditor
description: Audit LaTeX manuscript summary tables against governing equations and nearby derivations. Use when the user asks about model-summary tables, unknown counts, equation-block counts, missing laws, wrong equation labels, density rows, phase-count notation, or whether a summary table accurately reflects boxed or numbered derivations.
---

# LaTeX Summary Table Auditor

Use this skill for summary tables and model-count tables.

## Workflow

1. Read `AGENTS.md`, `paper/main.tex`, and `paper/defs.tex`.
2. Locate the table, caption, label, and surrounding prose.
3. Identify the governing derivation span that the table summarizes.
4. Compare rows against governing equations, not just nearby prose:
   - unknown family
   - governing law or closure
   - count
   - phase/component index set
   - equation label
   - role description
5. Check for common mismatches:
   - using a closure where a conservation law is the governing equation
   - omitting distension or source laws
   - using bare `P_F`/`P_S` instead of manuscript macro forms
   - stale labels after local equation deletion
   - duplicated equations already presented elsewhere

## Output

Report table issues as row-level findings with source locations. If editing,
patch only the affected rows/prose and re-check labels and counts.
