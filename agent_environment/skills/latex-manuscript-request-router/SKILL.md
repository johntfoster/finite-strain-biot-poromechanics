---
name: latex-manuscript-request-router
description: Route LaTeX manuscript and repository requests for the nonlinear Biot implicit-AD paper. Use for manuscript interpretation, scoped edits, derivation audits, rendered-equation lookup, citation checks, display cleanup, MOOSE implementation planning, validation planning, or cross-track work.
---

# LaTeX Manuscript Request Router

Use this skill as the first routing layer for repository tasks that are not
obviously a one-line shell command.

## Workflow

1. Read the repository `AGENTS.md` and `VISION.md`.
2. If the task is manuscript-related, also read `paper/main.tex` and `paper/defs.tex`.
3. Open `agent_workflows/decision_trees/request_router.md` when it exists.
4. Classify the immediate owner:
   - `biot-manuscript`
   - `moose-implementation`
   - `validation`
   - `agent-workflow`
   - `cross-track-planning`
5. Select the narrower workflow:
   - rendered equation number -> equation resolver or equation-integrity skill
   - source edit -> manuscript edit decision tree
   - notation change -> notation propagation planner
   - summary table -> summary table auditor
   - MOOSE object plan -> MOOSE residual traceability planner

## Output

For planning or interpretive responses, state the selected route and the source
files that control the answer. For edit requests, route quickly and then make
the scoped edit; do not stop at classification unless the user asked for a plan.
