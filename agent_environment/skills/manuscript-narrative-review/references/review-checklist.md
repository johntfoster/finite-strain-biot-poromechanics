# Review Checklist

Use this checklist after reading the repository's governing manuscript files.

## Audience And Voice

- Assume readers know continuum mechanics, thermodynamics, and reservoir or compositional flow.
- Do not assume readers know this manuscript's variational construction, prior chat history, discarded formulations, or the author's intent outside the source.
- Remove phrases that sound like development notes: "we now just", "as discussed earlier" when the source has no explicit anchor, "this is useful because we wanted", "the above mess", "our previous choice", or similar chat-local language.
- Replace defensive prose with direct academic claims: state what the equation expresses, which assumption is being imposed, and what consequence follows.

## Explanatory Shape

- Start from the local physical or mathematical role of a term before naming formal machinery.
- When a multiplier, affinity, pressure, flux, or closure appears, say what constraint, balance, or thermodynamic force it belongs to.
- Bridge unfamiliar variational objects to familiar reservoir-simulation ideas only when the manuscript already supports the comparison or the user requested it.
- Keep special-case reductions explicit about assumptions and lost or retained thermodynamic structure.

## Definitions And Redundancy

- Keep primitive symbol definitions close to first substantive use; immediate post-display definitions are acceptable if unambiguous.
- Prefer references to canonical earlier equations over duplicate local displays.
- Remove a redundant display only after checking labels, references, tables, and surrounding prose.
- If a local summary table or paragraph claims to count governing equations or unknowns, compare it against the actual nearby derivation rather than relying on prose.

## LaTeX Style

- Treat displays as grammatical parts of the sentence and punctuate accordingly.
- Avoid numbered one-line chained equalities; use aligned steps when a result genuinely needs multiple equalities.
- Preserve established notation, macro usage, and algebraic grouping from canonical equations.
- Do not introduce helper variables or shorthand unless the user explicitly approves them.
- Do not edit protected `% AGENT-LOCK` regions unless explicitly instructed.

## Validation Prompts

Before finishing, ask:

- Did this edit change only prose unless a narrow redundancy removal was justified?
- Are definitions now near enough to first use without interrupting the mathematical flow?
- Does the passage stand alone for the intended reader?
- Did any label, equation number, citation, or table entry need a build or source check?
