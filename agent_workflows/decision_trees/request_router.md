# Agent Request Router

Use this tree before repository work. It does not replace `AGENTS.md`,
`VISION.md`, `paper/main.tex`, or `paper/defs.tex`.

## Startup

1. Read `AGENTS.md` and `VISION.md`.
2. Classify the immediate owner as `theory-manuscript`,
   `moose-implementation`, `validation`, `agent-workflow`, or
   `cross-track-planning`.
3. For notation, equations, labels, or references, read this paper's
   `paper/main.tex` and `paper/defs.tex` and the parent manuscript's `main.tex`
   and `defs.tex`.

## Route

| Request | Primary route | Required companion |
| --- | --- | --- |
| Interpret a definition or equation | Source-based manuscript answer | Parent and local TeX sources |
| Change manuscript prose or equations | Manuscript edit | `manuscript_edit.md` |
| Rendered equation number | Equation lookup | `equation_number_lookup.md` |
| Symbol or notation change | Propagation plan | `../checklists/pre_edit_scope.md` |
| Citation, DOI, source support | Citation verification | `../checklists/citation_verification.md` |
| MOOSE object or weak form | Implementation traceability | `validation/theory_traceability.yml` |
| Validation or pressure experiment | Acceptance matrix | `validation/acceptance.yml` |
| Input-deck generation | Structured problem specification | `../schemas/problem_spec.schema.json` |
| Failed MOOSE run | Layered failure triage | `../runbooks/moose_failure_triage.md` |

For implementation or validation, map each object and observable to a parent
manuscript equation, assumption, or reduction. For underspecified simulation
setups, ask only questions that change equations, closures, boundary or initial
conditions, or the validation target.
