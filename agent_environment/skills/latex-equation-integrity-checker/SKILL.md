---
name: latex-equation-integrity-checker
description: Resolve and validate rendered LaTeX equation references before answering or editing. Use when the user cites equation numbers, bare numbers in manuscript context, labels, boxed displays, stale numbering, aux-file conflicts, overfull display fixes, or asks to inspect, explain, box, remove, or revise a numbered equation.
---

# LaTeX Equation Integrity Checker

Use this skill before relying on rendered equation numbers.

## Workflow

1. Read `AGENTS.md`. For manuscript interpretation, also read `paper/main.tex`
   and `paper/defs.tex`.
2. Prefer `paper/build/main.aux` over other auxiliary files.
3. Use the existing resolver when available:

```bash
python3 agent_environment/skills/takeme/scripts/takeme_resolve.py --repo . --target "<number>"
```

4. Open the resolved source span and confirm:
   - label
   - rendered number
   - environment type
   - locked-region status
   - nearby references
   - display width or style risks
5. If aux files disagree, treat root `main.aux` as stale unless a fresh build
   proves otherwise.
6. After label-sensitive or display-sensitive edits, compile twice from
   `paper/main.tex` when build validation is needed.

## Report

Report the resolved label, source location, and any integrity risks. If editing,
make the narrowest source change and then re-check the affected label/display.
