# JMPS submission package

The submission release freezes the manuscript, source, curated numerical
records, and companion website at one Git revision. It is a preparation
snapshot; creating the release does not submit the article to the journal.

Run `make paper validate`, then `python3 tools/package_submission.py --tag TAG`
from the committed checkout. The packager requires a clean worktree, verifies
content hashes, includes the pinned workflow submodule, and writes checksums
and a Git bundle under `.agent-runtime/submission/TAG/`. The bundle preserves
commit history; `source.zip` can be browsed and its website built without Git.
For numerical reproduction, clone `repository.bundle`, set the public origin,
and initialize the pinned workflow submodule as described in the main README.

Upload the canonical manuscript PDF, `manuscript-source.zip`, and the
[highlights](highlights.txt) as the corresponding article files. The
[cover letter](cover-letter.txt) describes the work and reproducibility record.
The source archive includes PGF figures and requires LuaLaTeX; check the PDF
produced by the submission system against `paper/build/main.pdf`. If the portal
cannot render PGF, use the provided PDF for initial review and supply the source
archive as an additional file.

The release includes curated data and historical execution records. Raw
working directories are mutable and are not represented as immutable original
runs. Heavy numerical studies are documented in the validation records and
are excluded from routine container CI. Ordinary test logs and the exact
container digest belong with the release evidence.

Before completing the journal's submission form, verify author details,
funding, competing interests, CRediT roles, exclusivity, article type, and any
reviewer suggestions. Consult the current
[JMPS author guide](https://www.sciencedirect.com/journal/journal-of-the-mechanics-and-physics-of-solids/publish/guide-for-authors)
for portal-specific requirements. The guide was inaccessible to automated
retrieval during package preparation; no journal-compliance certification is
implied. A persistent archival DOI can be added after repository deposit;
none is invented by this package.
