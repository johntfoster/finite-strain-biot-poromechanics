# Rendered Equation Number Lookup

1. Prefer `paper/build/main.aux` when it exists.
2. Treat other aux files as potentially stale.
3. Resolve the rendered number to a label and source line.
4. Open the surrounding source and check locked-region markers.
5. Inspect references to the label before editing.
6. Rebuild twice when numbering or references matter.

Parent-manuscript equation numbers must be resolved in the parent repository's
active build, not inferred from this paper's numbering.
