# Nonlinear Biot request router

1. Read `AGENTS.md` and `VISION.md`.
2. Check `git status --short`.
3. For manuscript work, read `paper/main.tex`, `paper/defs.tex`, and the
   relevant included section.
4. For MOOSE work, run `tools/sync_biot_moose.py check`, read the setup skill,
   and identify the controlling manuscript equation and validation gate.

| Request | Route |
| --- | --- |
| Interpret or revise manuscript text | manuscript source and narrative skill |
| Rendered equation number | equation resolver, then source |
| Citation or attributed equation | citation verifier and local source PDF |
| Derivation or tangent audit | derivation auditor and implicit-AD section |
| MOOSE material or kernel change | residual traceability and synchronization contract |
| Mandel result or figure | analytical verifier, result provenance, and plotting script |
| Build or reproduce | LaTeX or MOOSE setup skill, then repository validation |

Do not route this repository through SPE, black-oil, reaction, phase-transfer,
or enriched-Galerkin workflows.
