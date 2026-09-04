# Portable agent environment

`tools/agentctl` is the repository-local entry point for skill discovery and
dependency routing. It discovers the repository root through Git and records
generated environments below `.agent-runtime/`.

The canonical skills live in `agent_environment/skills/`. Common commands are:

```sh
tools/agentctl skills
tools/agentctl profiles
tools/agentctl route "resolve equation 16"
tools/agentctl activate codex "edit the manuscript" --dry-run
tools/agentctl check --profile manuscript
```

The manuscript root is `paper/main.tex`, its generated output belongs in
`paper/build/`, and research retrieval state belongs in
`.agent-runtime/research/`.
