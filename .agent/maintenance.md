# Infrastructure migration — 2026-09-19

This maintenance pass changes repository infrastructure only. Manuscript source,
bibliographies, figures, submitted artifacts, and pre-existing local work are
protected. `research-project.yml` records the local authority, exact shared pin,
publication surfaces, and unfinished migration work. It uses JSON syntax, which
is valid YAML, so baseline checks need only the Python standard library.

## Commit protection

The tracked pre-commit hook defaults to manuscript-freeze mode, including in a
fresh clone. It rejects protected staged paths (including deletions and renames)
and exits before legacy disclosure/provenance generators can rewrite TeX.
The six-section commit-message checks still run. Install tracked hooks with
`tools/agentctl hooks install` after cloning.

The local setting `research.manuscriptFreeze=true` makes the freeze explicit.
Only a later task explicitly authorizing manuscript changes may end this freeze:
review the maintenance manifest and set `git config --local
research.manuscriptFreeze false` for that task. This is not permission to change
manuscripts during the current migration. Hooks protect commits, not arbitrary
filesystem writes; agents must also obey the manuscript prohibition before edits.

## Verification and remaining work

This pass checks manifest authority paths and workflow pins, protected-file
hashes, infrastructure-only hook execution, rejection of protected paths and
renames, and acceptance/rejection of synthetic process-log messages. Tests use
temporary repositories; no manuscript build or scientific simulation is run.
These checks are infrastructure evidence, not scientific validation.

The shared core is explicitly pinned to v0.2.0; the program and core repositories
are authorized infrastructure exceptions. Shared release CI and local core tests
are separate from each paper's consumer evidence.

The Codespace image is pinned by digest. Its startup checks infrastructure and
reuses/builds the existing MOOSE application as required. While manuscript freeze
is active, startup skips both the manuscript build and publication figure generation.
Scientific checks remain separately requested and reported.
