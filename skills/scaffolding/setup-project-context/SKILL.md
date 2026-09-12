---
name: setup-project-context
description: Build and maintain this repo's agent context — CONTRIBUTING.md, a /project-context router skill, and one reference file per domain. Re-run it after the repo has drifted.
disable-model-invocation: true
---

# Setup Project Context

Upsert. First run builds the context. Later runs rebuild it once a repo has drifted
far enough that mining and interviewing pay off again.

Everyday upkeep belongs to `/audit-project-context`, which runs at the end of a pull
request and trims what the week's work added.

## The shape it builds

| Tier | File | Loads |
| --- | --- | --- |
| 1 | `AGENTS.md` / `CLAUDE.md` | every turn — behaviour and the gate |
| 2 | `CONTRIBUTING.md` | every session — what the project is, its status, how to contribute |
| 2 | `skills/internal/project-context/SKILL.md` | every session — the rules and the table |
| 2 | `glossary.md` | every session — the words used across domains |
| 3 | `domains/<domain>.md` | only when the task enters that domain |
| — | `docs/` | by link only — the decisions and investigations behind a reason |
| — | `README.md` | humans only — pointers out |

Context splits by **domain**, never by document type. A task about environments reads
one file, not four.

## The rule every file obeys

**A doc earns a line only if the code cannot say it.**

A domain file carries five sections and nothing else:

- **Words** — terms used only inside this domain.
- **Rules** — conventions no linter or type checker enforces.
- **Reasons** — why this shape was chosen, when the code cannot show it.
- **Fences** — the trap, where it bites (`file:line`), and why the fence stands.
- **Where it lives** — paths. Everything you were about to explain goes here instead.

## 1. Survey

Read what is already there: `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`,
`CONTEXT.md`, `docs/`, `package.json`, `skills/`, and any existing
`skills/internal/project-context/`. Run `git remote -v`.

**Done when** you can name every agent-facing doc in the repo and say which tier it
belongs in.

## 2. Mine

The slowest step and the one that carries the skill. Empty files are the failure mode.

Dig in every seam:

- `git log` — reverts, and commits that undo an earlier choice.
- `rg -n 'TODO|HACK|FIXME|workaround|deliberately|intentionally|on purpose'`
- Skipped and disabled tests: `.skip`, `xit`, `it.todo`, `test.todo`.
- Commented-out code, dead flags, config that departs from the default.
- Closed issues and merged pull requests, through `gh`, when the remote is GitHub.

Every candidate fence gets a `file:line`.

**Done when** every candidate carries a location. A fence with no location is a guess.

## 3. Propose the domains

**This skill ships no domain list.** Every repo has its own. Read the repo, propose a
list with one line each, and wait for approval.

- A domain is a subject a task is **about**, not a folder.
- Two domains that always load together are one domain.
- A domain earns a file once it holds at least one fence or one non-obvious reason.
  Below that bar it is an empty heading pretending to be context.
- A file heading past ~150 lines is two domains.

**Done when** the user has approved the list.

## 4. Interview

The code shows the *what*. Only the human holds the *why*. Take one domain at a time
and ask.

Drop any fence whose reason nobody can state. An unexplained fence teaches the next
agent to guess.

**Done when** every surviving fence carries a reason in the human's own words.

## 5. Write

Read [`TEMPLATES.md`](./TEMPLATES.md), then write:

- `CONTRIBUTING.md`
- `skills/internal/project-context/SKILL.md`
- `skills/internal/project-context/glossary.md`
- `skills/internal/project-context/domains/<domain>.md`, one per domain
- `README.md`, cut back to pointers

Rehome the scattered docs. **Move the text. Never copy it.** A root `CONTEXT.md`
becomes `glossary.md`; a term used inside one domain only goes to that domain's
**Words** instead. `docs/agents/*` becomes domain files, and the folder goes.

`docs/` keeps `adr/` and `research/`. Those hold the **record**: what was decided and
what was found, each fixed to the moment it happened. A record is never pruned, which
is the opposite of a domain file's rule, and that is why the two stay apart. A domain
file's **Reasons** section links the decision or the investigation behind it, and that
link is the only way an agent gets there.

Retire `docs/design/`. A design doc is a proposal. Once the thing is built, the
decision is an ADR and the rules are a domain file, so a third copy only goes stale.
Move each one to whichever of the two it really is.

**Done when** every line of the old files is moved into exactly one domain file,
replaced by a link, or deleted with the reason said out loud to the user.

## 6. Drain

`AGENTS.md` / `CLAUDE.md` keeps behaviour. Everything about *this* project moves into
a domain file.

Edit the file that already exists. If `CLAUDE.md` exists, edit it. Else edit
`AGENTS.md`. If neither exists, ask which to create.

Upsert the gate block from `TEMPLATES.md` between its `<!-- project-context -->`
markers. Other skills own other blocks in this file; leave theirs alone.

**Done when** every remaining section either holds true in an unrelated repo, or is
the gate.

## 7. Link

Invoke `/link-skills project-context`. Read `SKILL.md` back through every new symlink
to confirm it resolves.

## 8. Report

Say plainly:

- Which domains were written, and how many fences each holds.
- Which domains came out thin, so the user knows where the context is still weak.
- Which fences were dropped, and why.
- How many lines `AGENTS.md` lost.
