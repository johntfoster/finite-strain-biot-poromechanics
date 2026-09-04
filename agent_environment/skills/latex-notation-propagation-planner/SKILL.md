---
name: latex-notation-propagation-planner
description: Plan and audit notation changes in LaTeX derivations before editing. Use when the user asks to rename symbols, change constitutive arguments, alter derivative notation, propagate a notation change everywhere, distinguish kinematic fields from constitutive variables, or avoid symbol drift across definitions, state sets, chain-rule terms, thermodynamic forces, restrictions, tables, and prose.
---

# LaTeX Notation Propagation Planner

Use this skill before any nontrivial notation edit.

## Workflow

1. Read `AGENTS.md`, `paper/main.tex`, and `paper/defs.tex`.
2. Identify the exact symbol role being changed. Separate:
   - kinematic field
   - constitutive argument
   - dummy index
   - derivative operator
   - thermodynamic force
   - closure or special-case symbol
3. Build an impact map with targeted searches:
   - definitions and first use
   - state sets and held-fixed notation
   - derivatives, inverses, and scalar specializations
   - chain-rule collections
   - Coleman-Noll restrictions
   - variational force collections
   - summary tables
   - downstream prose and references
   - locked regions
4. Preserve the user's scope. If the request says "only" or names one section,
   report out-of-scope impacts instead of editing them.
5. Do not introduce helper symbols unless the user explicitly approves.

## Output

Before editing, provide a short impact map when the blast radius is uncertain.
After editing, summarize which categories were changed and which were left
unchanged because of scope or locks.
