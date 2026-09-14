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
5. After building, verify that the open preview reloads `paper/build/main.pdf`
   when editor access or LaTeX Workshop logs are available. A successful build
   alone does not establish preview refresh. Look for a PDF change event,
   `refreshExistingViewer`, a new PDF request, and `VIEWER_PAGE_LOADED` after
   the build. If a supported editor command is available, use
   `latex-workshop.refresh-viewer` when automatic refresh fails.
   For a stale preview, inspect the VS Code renderer log for file-watcher
   errors. Linux `ENOSPC` can mean exhausted inotify watches: keep
   `**/.agent-runtime/**` excluded in workspace `files.watcherExclude`, while
   leaving `paper/build/` watched. After repairing watching, touching the
   canonical PDF can trigger a reload without rebuilding or changing content.
   If automatic refresh still fails in desktop VS Code, reopen the canonical
   preview with `code --reuse-window paper/build/main.pdf` from the repository
   root, using GUI execution approval when required by the harness. Verify a
   subsequent PDF request and `VIEWER_PAGE_LOADED` in the extension log.
   Workspace `.vscode/` settings are ignored in this repository; check the
   runtime exclusion after a fresh checkout rather than assuming it is tracked.
   If editor reload or manual refresh is still needed and cannot be performed
   through the available tools, report that remaining step explicitly.
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
