---
name: commit
description: Create requested Git commits with a sanitized cross-session development narrative and the repository Git hooks. Use for every request to commit, checkpoint, or record changes in Git, including a commit requested alongside other work. Reading existing commits alone does not authorize a new commit.
---

# Commit

This is the repository's commit workflow. The agent synthesizes the chat
history; Git hooks update the AI disclosure and validate the message. Hooks
cannot recover or summarize conversations themselves.

## Prepare the change and narrative

1. Read `AGENTS.md` and check `git status --short`, the staged diff, and
   `git log -1 --format=fuller`. Complete the authorized work and its focused
   checks before committing. Preserve unrelated changes and respect the
   requested commit scope. Do not push or rewrite history without authorization.
2. Use the previous commit's timestamp as the history-window boundary. Read
   relevant messages from this conversation and available Codex, Copilot,
   OpenClaw, or other harness session stores. Prefer repository/worktree matches;
   include sessions that began earlier but contain messages in this window.
   Deduplicate inherited transcripts. Use available remote-session access only
   within existing authorization. Do not inspect credential stores.
3. Synthesize decisions, reasons, alternatives, failed approaches, and remaining
   work from all recoverable relevant sessions. Distinguish prior verification
   records from checks run now. Describe carried-over work using its diff and
   evidence. Explicitly identify unavailable histories rather than inventing
   them. Keep raw extracts under `.agent-runtime/commit/` and out of Git.
4. Write the message body first, with substantive content under these headings
   in this exact order: `Summary`, `What changed & why`, `Alternatives considered`,
   `Dead ends & backtracks`, `Open questions`, `Next steps`. Then prepend a concise
   header describing the same final change. Sanitize credentials, personal
   details, and private conversation content; record technical reasoning, not
   a transcript. Use repository-relative paths in the narrative.
5. Save the exact message in `.agent-runtime/commit/message.txt`. Stage only the
   intended source, instructions, tests, reference data, and publication assets.
   Inspect `git diff --cached`, including newly added files. Keep manuscript
   revisions in Git, with `paper/build/main.pdf` as the sole manuscript preview.

## Commit through the hooks

From the repository root, run:

```sh
agent_environment/skills/commit/scripts/commit.sh .agent-runtime/commit/message.txt
```

The helper validates the narrative and staged whitespace before committing,
installs the tracked hooks, checks their executable permissions, and invokes
ordinary `git commit --file`. Git runs `pre-commit`, `prepare-commit-msg`, and
`commit-msg`; the pre-commit hook may stage updated disclosure files.

Never use `--no-verify`, disable hooks, or fall through to a commit after a
failed check. Resolve a failure within the authorized scope and rerun; explain
any blocker that remains. Existing commit authorization also covers ordinary
hook installation and scoped staging, subject to the environment's permissions.

After success, inspect `git show --stat --oneline HEAD` and `git status --short`.
Report the commit hash, validation outcome, and any intentionally uncommitted
work. A request to prepare a message or review a diff stops before committing.
