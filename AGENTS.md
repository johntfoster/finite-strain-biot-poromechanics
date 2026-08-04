# AGENTS.md

## Upstream foundation

This is the companion derivation, implementation, and validation repository for
the nonlinear Biot-coefficient specialization of the multicomponent reactive
flow theory. Its authoritative parent repository is:

`/home/jfoster/projects/research/reactive_transport/multicomponent_reactive_flow`

Use the parent repository's manuscript, notation, MOOSE implementation,
validation practice, and agent workflow as the foundation for all work here.
This repository must not use React/OpenClaw identity files, personal-agent
bootstrap files, or a separate theory invented for this paper.

## Project roadmap

- Read `VISION.md` at the start of repository work.
- Treat the three tracks as coupled work: derivation manuscript, MOOSE
  implementation and quantitative validation, and agent-assisted simulation
  workflow.
- The active repository layout is:
  - `paper/main.tex`, `paper/defs.tex`, `paper/sections/`, `all.bib` -- paper.
  - `moose/` -- composable input fragments, experiment decks, and the manifest
    of authoritative upstream MOOSE source used by the paper.
  - `validation/` -- acceptance criteria, equation-to-code traceability,
    reference data, and quantitative results.
  - `agent_workflows/` -- routing, edit/validation checklists, schemas, and
    MOOSE failure diagnosis inherited from the parent repository.
  - `data/` and `references/` -- immutable sources, curated data, provenance,
    and reading notes.
- Use `agent_workflows/decision_trees/request_router.md` before work that is not
  purely local. Use the narrower checklist, decision tree, schema, or runbook
  whenever its trigger matches the request.
- When a task touches more than one track, identify the immediate owner and the
  downstream track requiring follow-up.

## Manuscript source of truth

- Treat `paper/main.tex` as the canonical root of this paper. Follow its input,
  bibliography, macro, and package graph; section files are not standalone.
- Treat the parent `main.tex`, `defs.tex`, and included sections as the source of
  truth for the general multicomponent theory and accepted notation.
- Read `paper/main.tex`, `paper/defs.tex`, the parent `main.tex`, and the parent
  `defs.tex` before interpreting or changing derivations.
- Prefer exact source evidence over memory, generated PDFs, notes, or plotted
  results. Cite controlling source locations as `file:line` during audits.
- Do not introduce helper symbols when the primitive variables from the parent
  manuscript state the result clearly. In particular, use the summed Eq. (32)
  variables directly; do not introduce `A` or `M_a^0` shorthand.
- Number and descriptively label every displayed equation or identity added to
  the manuscript.
- Do not edit text between `% AGENT-LOCK-BEGIN` and `% AGENT-LOCK-END` unless
  John explicitly names that material as the target.

## Operating checklist

- At the start of every task, read `AGENTS.md` and `VISION.md`, classify the
  task as manuscript theory, MOOSE implementation, validation, agent workflow,
  or cross-track planning, and check `git status --short`.
- Before any repository edit, read `author_style_profile_2026-07-27.md`.
- If a rendered equation number is cited, resolve it through the active aux
  files before answering or editing.
- Before conceptual or derivational work, identify the exact parent-manuscript
  equations, definitions, and assumptions that control the result.
- When notation changes, propagate it through state sets, chain rules,
  constitutive restrictions, weak forms, code properties, and validation
  observables.
- Make the smallest source change that handles the request and preserve
  unrelated dirty-worktree changes.
- After manuscript edits, rebuild from `paper/main.tex`, inspect warnings, and
  visually inspect affected rendered pages.

## Technical scope and notation

- Derive the nonlinear Biot coefficient from the current multicomponent paper's
  fixed-equivalent-pressure Legendre transform and the solid/component material
  conservation constraints.
- Form intrinsic skeleton specific volume from the registered solid phases and
  components using the summed Eq. (32) storage directly:
  `J_s sum(phi_a) / sum(J_s rho_a^alpha)`.
- Distinguish intrinsic skeleton density from bulk solid partial density.
- Evaluate the inner constitutive partial at fixed equivalent pore pressure and
  declared held-fixed variables. Retain MOOSE AD on the resulting coefficient
  so the outer global Newton chain rule includes its complete state dependence.
- Use the parent paper's notation and definitions. The paper must distinguish a
  definition, a derived restriction, a constitutive closure, a calibrated
  parameter, and an independently predicted quantity.
- The Lawal--Kim workbook coefficient is computed from the measured drained and
  unjacketed moduli. A fit to those drained-modulus data is calibration, not an
  independent validation of the Biot coefficient. State that limitation
  wherever those curves are discussed.

## MOOSE implementation track

- The production source remains in the parent `moose_app/`. This repository
  records exact upstream files and revisions in `moose/source_manifest.yml` and
  contains paper-specific composable input decks and validation scripts.
- Map every MOOSE object, material property, residual, boundary condition, and
  test to a parent-manuscript equation, assumption, or special-case reduction.
- Use MOOSE automatic differentiation by default. Keep tensor kinematics,
  constraint solves, state transformations, and implicit tangents in explicit
  AD materials or user objects rather than hiding them in kernels.
- Kernels remain residual objects that consume AD material properties.
- Use Q2 Lagrange displacement and the parent repository's P1+P0 enriched
  Galerkin equivalent-pressure construction for coupled mechanics/flow solves.
- Use the validated include hierarchy and solid-reference kinematics from the
  parent repository rather than one-off input decks.
- Never use `std::pow()` with `ADReal`; use unqualified `pow()`.

## Validation track

- Every validation entry must state the governing reduction, variables,
  observables, authoritative reference, tolerance, and pass/fail status.
- Verify the implicit fixed-pressure tangent against analytic or centered
  finite-difference derivatives and verify the outer AD path with a PETSc
  Jacobian test.
- Recover the classical `B = 1 - K/K_s` limit with shrinking perturbations and
  verify intrinsic-density/specific-volume inverse consistency.
- Separate implementation verification, constitutive calibration, holdout
  prediction, and independent physical validation.
- A pressure-path MOOSE material evaluation with `solve = false` is a
  constitutive-path test, not a boundary-value simulation.
- A genuine pressure-controlled experiment must solve the mechanics and state
  variables from boundary conditions; it must not prescribe the fitted path.
- Keep source data, generated outputs, and curated reference results distinct.

## Agent-assisted simulator workflow

- Treat input templates, parameter schemas, validation checks, run recipes,
  postprocessing, and troubleshooting notes as versioned repository artifacts.
- Generate decks from composable include fragments and structured problem
  specifications whenever possible.
- Before running a generated deck, validate variables, kernels, materials,
  boundary conditions, units, mesh, executioner, outputs, and validation target.
- Diagnose failed runs in the order given by
  `agent_workflows/runbooks/moose_failure_triage.md`.

## Prose and LaTeX rules

- Apply `author_style_profile_2026-07-27.md` to manuscript text, captions,
  tables, comments, documentation, and workflow material.
- Write equation-forward prose for a continuum-mechanics and reservoir-
  simulation audience. Define symbols at first substantive use.
- Describe prior work affirmatively, then state what this paper derives or
  implements. Do not establish novelty through negative positioning.
- Preserve TeX semantics, macro context, labels, citations, and equation
  grammar. Use automatic delimiters and aligned multi-step equations.
- Never commit LaTeX build artifacts.

## Required cross-track records

Keep these files aligned when a result becomes durable:

- `validation/equation_to_moose_map.yml`
- `validation/theory_traceability.yml`
- `validation/acceptance.yml`
- `moose/source_manifest.yml`
