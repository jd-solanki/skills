---
name: project-context
description: This repository's words, rules, reasons and fences. Invoke before the first code action in a session, and again when a task enters a new domain.
---

# Project context

## What earns a line here

- A **word** — a term whose meaning this project fixes.
- A **rule** — a convention no linter or type checker enforces.
- A **reason** — why this shape was chosen, when the code cannot show it.
- A **fence** — the trap, where it bites (`file:line`), and why the fence stands.

**The test: could I learn this by reading the code?** Then link the path under
**Where it lives**. Leave the prose out.

Git holds the history and the skills CLI holds the install state. Both are sources of
truth already; point at them.

Past ~150 lines, a file is two domains, or it is restating code. Split it or cut it.

`/audit-project-context` enforces all of the above.

## References

Load `glossary.md` every session. Load a domain file when your task enters it.

A row may name any path in the repository. Living inside this folder is not what makes
a file loadable; this table is.

| Reference | Load when |
| --- | --- |
| `glossary.md` | always |
| `domains/layout.md` | adding, moving, renaming or linking a skill |
| `domains/authoring.md` | writing or editing the text inside a skill, and committing it |
| `docs/context-engineering.md` | changing the shape of `/setup-project-context`, `/audit-project-context`, or the layout they build |
