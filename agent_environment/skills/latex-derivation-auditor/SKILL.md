---
name: latex-derivation-auditor
description: Audit highly mathematical LaTeX derivations for notation, dependency, chain-rule, constitutive-state, balance-law, and downstream force consistency. Use when an agent is asked to inspect or revise a derivation, propagate a notation or constitutive change through a manuscript, check whether equations follow from prior definitions, audit Coleman-Noll/variational/thermodynamic arguments, or explain mathematical inconsistencies in .tex source rooted at a main LaTeX file.
---

# LaTeX Derivation Auditor

## Overview

Use this skill to audit mathematical consistency in LaTeX manuscripts where equations are coupled across definitions, assumptions, balances, constitutive restrictions, and derived forces. Treat the TeX source as the authority, but use build artifacts only for diagnostics or rendered-number lookup when needed.

## Workflow

1. Read the repository's agent or authoring instructions first when present, especially `AGENTS.md`, `VISION.md`, or equivalent manuscript guidance.
2. Use `paper/main.tex` as the canonical LaTeX root. Follow `\input`, `\include`, macro files, theorem/equation packages, and bibliography declarations from that root.
3. Inspect `paper/defs.tex`, local definitions near the target section, and labels/cross-references before judging math.
4. If the user cites rendered equation numbers, resolve those numbers to labels/source lines before auditing. Prefer an existing equation resolver skill or active build `.aux` files.
5. Run `scripts/scan_derivation_surface.py` on the target files to collect equation environments, labels, references, state-set phrases, derivatives, and common propagation-sensitive symbols.
6. Build a dependency map from the source:
   - primitive variables and fields
   - derived variables
   - constitutive arguments
   - balance-law inputs
   - multipliers, forces, fluxes, source terms, and dissipation terms
   - assumptions that remove or simplify terms
7. Audit propagation in both directions:
   - upstream: every symbol in the target equation has a prior definition or local meaning
   - downstream: every changed constitutive argument, split, or assumption is reflected in chain-rule terms, force definitions, residual inequalities, stresses, fluxes, and special-case reductions
8. Report findings with `file:line` source locations. Separate confirmed inconsistencies from plausible concerns that need author judgment.

## Editing Rules

- Reuse the manuscript's existing notation unless a new symbol clearly reduces real complexity.
- Do not infer global notation from one displayed equation. Check root-level macros and nearby prose.
- Preserve protected or locked regions unless the user explicitly names them as edit targets.
- Prefer narrow patches for local derivation errors and broader propagation only when the user asks for a global notation or constitutive change.
- Follow the repository's `AGENTS.md` numbering policy for helper definitions;
  in this repository every agent-introduced display is numbered and labeled
  unless the author explicitly requests otherwise.
- After editing displayed equations, validate with the manuscript's preferred build path. If no build is available, state that only source-level validation was performed.

## Audit Checklist

- Definitions: every nonstandard symbol, index set, operator, and macro has a source-grounded meaning.
- State sets: constitutive dependencies match the chain-rule variables used later.
- Kinematics: independent fields are not accidentally replaced by constitutive arguments, and vice versa.
- Thermodynamics: entropy inequalities, residual dissipation, affinities, potentials, and flux-force pairs retain the same sign and variable conventions.
- Variational steps: variations, integration by parts, boundary terms, and multiplier terms are carried through without dropping active terms.
- Special cases: assumptions used to simplify equations are stated before the simplification and do not imply stronger conditions than written.
- Numbering and references: added equations do not accidentally shift rendered references when numbering stability matters.

## Helper Script

Use:

```bash
python3 agent_environment/skills/latex-derivation-auditor/scripts/scan_derivation_surface.py --root . --files paper/sections/target.tex
```

The script is a surface scanner, not a proof checker. Use its output to focus source inspection; do not treat matches as mathematical findings until the surrounding TeX has been read.
