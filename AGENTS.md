# AGENTS.md

## Portable agent environment

- Treat this file as the sole universal entry point for agent work.
- Resolve every operational path from the repository root. Never record a user
  home directory, machine-specific checkout, or required sibling-repository
  path in a tracked file.
- At the first relevant query, run `tools/agentctl route "<query>"` and use the
  smallest applicable skill and dependency profile.
- Keep generated environments, caches, builds, and run output below ignored
  runtime directories. Commit only source, instructions, tests, reference data,
  and intentional publication artifacts.

## Agent skill registration

- The canonical skills live in `agent_environment/skills/<name>/SKILL.md` and
  are the single source of truth. Each harness discovery directory holds
  one-way relative symlinks back to that source, so registered skills never
  drift from the canonical files.
- `agent_environment/dependencies.json` maps every harness to its discovery
  directory: copilot -> `.github/skills`, codex -> `.codex/skills`, claude ->
  `.claude/skills`, opencode -> `.opencode/skills`.
- Register every canonical skill for a harness before relying on it there, and
  re-register when switching harnesses (for example between Copilot and Codex)
  or after a fresh checkout, because symlinks are not preserved by clone or
  archive. From the repository root:

  ```sh
  # DIR is the harness discovery directory, for example:
  #   .github/skills  (Copilot)   .codex/skills  (Codex)
  DIR=.github/skills
  mkdir -p "$DIR"
  for skill in agent_environment/skills/*/; do
    name="$(basename "$skill")"
    ln -sfn "../../agent_environment/skills/$name" "$DIR/$name"
  done
  ```

- `ln -sfn` is idempotent and keeps the link one-way to the canonical source.
  Do not copy skill content into a discovery directory and never make a harness
  directory canonical.
- After first registration, reload the harness (for Copilot, reload the VS Code
  window) so discovery observes the links.

## Project scope

- Read `VISION.md` at the start of repository work.
- This repository owns the nonlinear-Biot manuscript, its figures, references,
  validation records, manuscript tools, and agent skills.
- The shared nonlinear-Biot MOOSE files are synchronized with the authoritative
  general simulator repository. The manuscript and paper-specific workflow are
  not downstream mirrors.
- Classify work as manuscript, MOOSE implementation, validation, publication,
  or cross-track work. State the immediate owner when a request crosses tracks.

## Manuscript source of truth

- Treat `paper/main.tex` as the canonical root and `paper/defs.tex` as its macro
  file. Interpret `paper/sections/*.tex` only through that root.
- Read `paper/main.tex` and `paper/defs.tex` before interpreting equations,
  notation, labels, citations, or section-local prose.
- Read `author_style_profile_2026-07-27.md` before editing prose, captions,
  tables, documentation, or workflow instructions.
- Prefer exact source evidence over memory, PDFs, generated files, or notes.
  Cite manuscript findings as `file:line`.
- If the user cites a rendered equation number, resolve it through
  `paper/build/main.aux`; rebuild first when the auxiliary data are stale.
- Verify external-paper equation and citation claims against the source PDF.
  Store PDFs in `references/pdfs/`, notes in `references/notes/`, and generated
  retrieval state in `.agent-runtime/research/`.

## Manuscript editing rules

- Preserve TeX semantics, macro context, math mode, environment nesting,
  labels, references, citations, and local definitions.
- Number and descriptively label every displayed equation introduced by an
  agent. Keep displays grammatical and punctuated.
- Use `align` for multi-step equalities. Do not write several equality steps on
  one numbered line.
- Do not put multi-line aligned subenvironments inside one visible delimiter.
  Continue delimiters across `align` rows with matching invisible delimiters.
- Use automatic delimiter sizing; do not introduce manual `\big`, `\Big`, or
  related sizing commands.
- Do not introduce helper variables or shorthand unless the user approves the
  new notation or it is essential to the requested result.
- Treat text between `% AGENT-LOCK-BEGIN` and `% AGENT-LOCK-END` as protected
  unless the user explicitly names it as an edit target.
- Write for readers versed in continuum mechanics and poromechanics. State the
  physical purpose, equation, local definitions, consequence, and limiting
  interpretation in that order when practical.
- State contributions positively. Remove drafting-history language and
  rhetorical claims based on what another formulation lacks.
- Render every bibliography DOI as a clickable link to
  `https://dx.doi.org/<doi>` in the compiled PDF (see the `\doi` macro in
  `paper/defs.tex`). Never emit a plain-text, non-hyperlinked DOI.
- A plotted quantity, figure set, or figure filename is consumed in three
  places at once: the generating script under `scripts/`, the manuscript
  figures under `figures/` and `paper/`, and the website under `docs/`.
  Change all three together in one coordinated edit; never update only the
  script or only the figure.

## Manuscript build

- After every manuscript-source edit, use the `latex-workshop-recompile` skill
  and build from the repository root:

  ```sh
  latexmk -lualatex -interaction=nonstopmode -halt-on-error \
    -outdir=paper/build paper/main.tex
  ```

- Inspect warnings and visually inspect affected pages, especially displays
  near page boundaries.
- Keep all generated LaTeX output in `paper/build/`. Never commit auxiliary
  files or generated PDFs from that directory.

## Shared MOOSE source contract

- `moose/sync_manifest.json` lists every MOOSE source, header, Mandel deck,
  verification driver, and framework patch shared with the authoritative
  simulator repository. `moose/sync_state.json` records their common hashes.
- Before editing a shared file, run:

  ```sh
  tools/sync_biot_moose.py check
  ```

- Agentic work may edit a shared MOOSE file in this repository. Before
  reporting the edit complete, run:

  ```sh
  tools/sync_biot_moose.py push
  ```

  The push fails if the master copy changed from the recorded base. Resolve
  that conflict explicitly; never overwrite either side silently.
- After changing shared files in the master repository, refresh this repository
  with `tools/sync_biot_moose.py pull`.
- The local master location is supplied with `--master`, the
  `BIOT_MOOSE_MASTER_ROOT` environment variable, or the ignored
  `.agent-runtime/master_repository` pointer written by a successful pull.
  A public clone remains reproducible without that checkout; synchronization
  requires access to both repositories.
- External contributions made without the master checkout remain Biot-side
  patches until they are imported, tested, and re-exported through the master.

## MOOSE implementation

- Before building or running `moose_app/`, use
  `agent_environment/skills/setup-moose-conda/SKILL.md`. Run its non-mutating
  diagnostic before setup, build, or test operations.
- The formulation uses Q2 displacement, continuous Q1 water pressure, and the
  solved solid intrinsic-density and volume-fraction states. The Mandel problem
  has no pressure enrichment, reconstructed EG pressure material, EG facet
  operator, or pressure stabilization.
- Solve solid mass conservation and the mineral EOS as residual equations.
  Compute the fixed-pressure implicit state tangent in
  `ADConstrainedSkeletonBiotMaterial` while preserving its outer MOOSE AD
  dependence.
- Keep kernels as weak-form residual objects that consume AD material
  properties. Keep constitutive constraints, tensor kinematics, and implicit
  tangents in materials.
- Map every MOOSE object and validation test to the equations and assumptions in
  `validation/equation_to_moose_map.yml` and
  `validation/theory_traceability.yml`.
- Never weaken, skip, or redefine a verification test to obtain a pass.
- Preserve unrelated dirty-worktree changes in both repositories.

## Validation

- Keep implementation verification, analytical Mandel comparison, numerical
  convergence, finite-deformation discrimination, and physical validation
  explicitly separated.
- The required implementation checks are the local implicit-tangent analytical
  and centered-difference comparisons, the PETSc Jacobian comparison, solid
  mass and mineral-EOS residuals, and pressure/displacement comparison with the
  analytical Mandel solution.
- Water pressure and displacement comparisons are spatial profiles at several
  times. Biot-coefficient and density contour figures use two-dimensional
  spatial snapshots.
- Source inputs, analytical reference data, generated run output, curated
  results, and publication figures are distinct artifact classes.

## Repository checks

- Check `git status --short` before editing and preserve unrelated work.
- Use repository-relative paths in instructions, scripts, manifests, and
  configuration.
- Run `tools/agentctl check --profile manuscript` for manuscript tooling and
  `tools/sync_biot_moose.py check` for shared-source integrity.
- For source edits, run the smallest focused test first, then broader validation
  in proportion to risk.
