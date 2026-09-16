---
name: setup-project-context
description: One-time bootstrap of this repo's agent context — CONTRIBUTING.md, a /project-context router skill, and one reference file per domain — drafted from the code when no context exists yet.
disable-model-invocation: true
---

# Setup Project Context

Project context is **upstream** of the code:

```text
project context & decisions → codebase → human docs
```

The owner decides in the context. The code implements the decision. Human docs explain
the result.

This skill runs once, in a repo with no `skills/internal/project-context/`. The context
should have come first, so the code is the only draft left: mine it, and the owner
answers only what the code cannot say. `/audit-project-context` owns every later
change.

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

Correctness alone does not earn context. Keep a fact only when omitting it could plausibly cause an
agent to make a costly wrong decision before nearby code or tests expose the mistake. Otherwise,
leave it beside the implementation or list only its path under **Where it lives**.

Write the enduring invariant: the intended outcome, ownership boundary, state transition, safety
property, or failure policy. Prefer that over current symbols, files, call sequences, or wiring. A
sentence that becomes false after an ordinary rename, move, or implementation refactor is usually
too low-level. Library and vendor names belong only when the owner has selected the name itself as a
durable architectural constraint.

A domain file carries a header and five sections, nothing else. The header is `load-when:`,
plus `confidence:` when the domain is not settled.

- **Words** — terms used only inside this domain.
- **Rules** — conventions no linter or type checker enforces.
- **Reasons** — why this shape was chosen, when the code cannot show it.
- **Fences** — the trap, where it bites (`file:line`), and why the fence stands.
- **Where it lives** — paths. Everything you were about to explain goes here instead.

## How solid a domain is

A domain file states how far its reader should trust it, with a `confidence:` line in the
header: one of three words, then a short clause naming what is still moving.

| `confidence:` | Write it when the owner can defend |
| ------------- | ---------------------------------- |
| `settled`     | this shape, in review              |
| `provisional` | the direction, but not the detail  |
| `exploratory` | neither — they are still guessing  |

`settled` is the default, so only a shaky file carries the line. Write the word the owner
says in the interview, never the one the prose sounds like.

The router file tells the reader what to **do** with each word. Never repeat that here.

The router template tells later work when the word moves.

## 1. Survey

If `skills/internal/project-context/` exists, stop. Tell the user the context already
exists and `/audit-project-context` keeps it. This skill does not run twice.

Read what is already there: `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`,
`CONTEXT.md`, `docs/`, `package.json` and `skills/`. Run `git remote -v`.

**Done when** you can name every agent-facing doc in the repo and say which tier it
belongs in.

## 2. Mine

The slowest step and the one that carries the skill. Empty files are the failure mode.

Everything mined is a **draft**. The code shows what exists, never whether it was
intended. A draft becomes context only when the owner confirms it in step 4.

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
- Name the file and heading with the repository's glossary terms. A name must tell an
  agent what work loads it; generic containers such as `lifecycle`, `management` or
  `platform` earn their place only when the glossary gives them a project-specific meaning.
- Preserve a module's boundary when it owns a cohesive product domain. A task that crosses
  domains loads multiple files; crossing them is not a reason to merge them under an umbrella.
- Two domains that always load together are one domain.
- A domain earns a file once it holds at least one fence or one non-obvious reason.
  Below that bar it is an empty heading pretending to be context.
- A file heading past ~150 lines is two domains.

For example, a Nuxt project may have `layer-auth` owning identity and access,
`layer-payments` owning Orders and payment collection, and `layer-email` owning email
delivery. Write `identity-and-access.md`, `payments.md` and `email-delivery.md`. A checkout
task that emails a receipt loads all three. Do not hide their ownership in a
`customer-lifecycle.md` umbrella.

**Done when** the user has approved the list.

## 4. Interview

The code shows the *what*. Only the owner holds the *why*, and only the owner turns a
draft into a decision. Take one domain at a time. Skip every question the code already
answers.

A draft the owner rejects is not context. Ask whether the mining misread the code, or
the code breaks the owner's decision. Record the second kind for the report.

Drop any fence whose reason nobody can state. An unexplained fence teaches the next
agent to guess.

Apply both admission tests before proposing text: would omission permit a costly mistake, and would
the sentence survive an implementation refactor? Record the candidates you drop so the owner can
distinguish deliberate pruning from an incomplete survey.

Ask each domain's `confidence:` word outright. The owner says it; never infer it from how
sure the prose sounds.

**Done when** every surviving fence carries a reason in the human's own words, and every
domain has a confidence word the owner chose.

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

Add the `## Project context` section from `TEMPLATES.md`. If the file already has that
section, replace it in place. Other skills own other sections in this file; leave theirs
alone.

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
- Every draft where the code breaks the owner's decision, with its `file:line`: code to
  fix.
- How many lines `AGENTS.md` lost.
