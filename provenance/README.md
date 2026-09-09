# Manuscript provenance

`ai-use.yml` records the author-directed AI workflow. Generate the public and
LaTeX disclosures with `python3 tools/update_ai_disclosure.py`.

The versioned hooks regenerate and stage those disclosures before each commit
and require the six-section process-log body defined in `AGENTS.md`. Install
them in a fresh clone or worktree with:

```sh
tools/agentctl hooks install
```

The hooks validate the repository-derived disclosure and commit-message
structure. An agent or author must still gather and synthesize the relevant
cross-machine session histories; hooks cannot safely reconstruct those chats.

`manuscript-export.json` lists the source, validation, and agent-workflow paths
that belong to the public reproducibility repository.
