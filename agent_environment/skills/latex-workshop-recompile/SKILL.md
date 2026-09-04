---
name: latex-workshop-recompile
description: Recompile LaTeX manuscripts with the repository's configured recipe when a build or validation is needed. Use an editor build command only when the active harness exposes one; otherwise run the equivalent repository command directly.
---

# LaTeX Workshop Recompile

## Workflow

1. Read the repository instructions first and build the canonical
   `paper/main.tex` root from the repository root.
2. Inspect repository build configuration, including `.vscode/settings.json`
   when present, for the root file, output directory, tools, and recipe.
3. Use an editor or harness build command only when it is directly exposed.
   Do not probe for harness-specific command dispatch.
4. Otherwise run `latexmk -lualatex -interaction=nonstopmode -halt-on-error
   -outdir=paper/build paper/main.tex` from the repository root.
5. Mention editor-preview synchronization only when it is relevant to the
   requested result, and never imply that a shell build refreshed an editor
   preview.
6. For equation-number, citation, aux, or cross-reference validation, build at
   least twice or follow the workspace recipe when it already includes multiple
   passes and bibliography.
7. Report the build path, root file, and only the actionable diagnostics. Report
   preview-refresh status only when preview synchronization is relevant.

## Fallback Notes

- If LuaLaTeX cache writes fail, use `.agent-runtime/tex-cache/var` and
  `.agent-runtime/tex-cache/cache`; keep both ignored by Git.
- Treat `paper/build/` outputs, `.aux`, `.log`, `.out`, `.bbl`, `.blg`, `.fls`,
  `.fdb_latexmk`, `.synctex.gz`, and PDFs as generated artifacts. Do not commit
  them.
- If the first pass reports changed labels or undefined references introduced by
  the current edit, rerun before deciding the manuscript is still broken.
