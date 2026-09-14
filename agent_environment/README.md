# Compatibility layer

Reusable skills are canonical in the pinned `.agent/shared` submodule.
Entries under `agent_environment/skills/` are compatibility symlinks for older
commands. New routing uses `tools/agentctl` and `agent-profile.json`.

Paper-specific skills belong in `agent_local/skills/`. Generated harness copies
and runtime state remain ignored.
