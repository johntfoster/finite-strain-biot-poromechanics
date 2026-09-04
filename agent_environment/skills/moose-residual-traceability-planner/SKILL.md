---
name: moose-residual-traceability-planner
description: Plan traceable MOOSE implementation objects from the nonlinear Biot manuscript equations and solid-water reduction. Use when changing kernels, materials, boundary conditions, tests, Mandel examples, weak forms, AD properties, or validation links.
---

# MOOSE Residual Traceability Planner

Use this skill before adding or planning MOOSE implementation objects.

## Workflow

1. Read `AGENTS.md` and `VISION.md`.
2. Read the controlling manuscript or implementation-paper source for the
   requested equation, reduction, or weak form.
3. Open these repo files when they exist:
   - `validation/equation_to_moose_map.yml`
   - `validation/theory_traceability.yml`
   - `validation/acceptance.yml`
4. For each proposed object, record:
   - object family: kernel, FV kernel, material, user object, action, BC, test,
     example, or documentation
   - controlling equation label or section
   - variables and material properties consumed
   - reference/current configuration
   - AD expectations
   - FE/FV choice
   - closure, stabilization, or approximation not present in the manuscript
   - validation case that will exercise it
5. Keep kernels as residual objects that consume AD materials. Do not hide
   thermodynamics, phase behavior, or mechanics inside one monolithic kernel.

## Output

Return an implementation map before code. If making durable decisions, update
the traceability YAML files and validation matrix.
