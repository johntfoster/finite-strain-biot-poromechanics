# Agent Workflows

This directory carries the agent-facing workflow used by the parent
`multicomponent_reactive_flow` repository. These files route manuscript,
implementation, validation, and simulator-setup work and keep paper claims tied
to validated MOOSE interfaces.

- `decision_trees/request_router.md` -- first-pass routing.
- `decision_trees/manuscript_edit.md` -- scoped manuscript edits.
- `decision_trees/equation_number_lookup.md` -- rendered equation lookup.
- `checklists/pre_edit_scope.md` -- pre-edit scope and traceability.
- `checklists/citation_verification.md` -- source and BibTeX verification.
- `checklists/post_edit_validation.md` -- post-edit validation.
- `schemas/problem_spec.schema.json` -- structured simulation specification.
- `runbooks/moose_failure_triage.md` -- layered MOOSE diagnosis.

Do not put transient run output here. Durable workflow assets must point to the
parent equations, the exact upstream MOOSE objects, and quantitative tests.
