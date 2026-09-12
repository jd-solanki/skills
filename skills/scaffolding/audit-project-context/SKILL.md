---
name: audit-project-context
description: Trim this repo's /project-context back to what the code cannot say. Run it at the end of a pull request.
argument-hint: "[base ref, defaults to the merge-base with the default branch]"
disable-model-invocation: true
---

# Audit Project Context

A week of work leaves real knowledge and restatement side by side in
`/project-context`. Both arrived the same way. Only reading the code tells them apart.

Built by `/setup-project-context`. Trimmed by this.

## Separation of duties

Dispatch a fresh sub-agent for the audit itself. It wrote none of these lines, so it
owes none of them anything. You dispatch, join, and report.

Hand it the diff range and the paths. It reports; you present.

## The law

`/project-context` `SKILL.md` carries the rules under **What earns a line here**. Read
them from there. This skill enforces them and does not restate them.

## 1. Pin the range

`git diff <base>...HEAD -- skills/internal/project-context/ CONTRIBUTING.md`

Three dots, so the comparison runs against the merge-base. `$ARGUMENTS` sets the base;
without it, use the merge-base with the default branch.

An empty diff ends the run. Say so and stop.

## 2. Judge every added line against the code

**Open the code before you judge the line.** A line that reads like real knowledge and
a line that restates a function body look identical in prose. Only the file tells you
which one you have.

For each added line, find what it describes and read it. Then it is one of three:

- **Keep** — the code cannot say it. A word the project fixes, a rule no tool
  enforces, a reason, or a fence.
- **Cut to a link** — the code says it. Delete the prose. Add the path under **Where
  it lives** if it is missing.
- **Cut** — it is a changelog entry, a feature checklist, or a rule another domain
  file already owns.

**Done when** every added line carries a verdict and the `file:line` that settled it.
A verdict with no location is a guess, and a guess keeps garbage.

## 3. Check the shape

- Every fence names where it bites and why the fence stands. A fence with no reason
  teaches the next agent to guess; cut it, or ask the user for the reason.
- Every domain file sits under ~150 lines. Past that, split it or cut the restatement.
- A term that appears in `glossary.md` but is used inside one domain only moves to that
  domain's **Words**.
- The routing table lists every file in `domains/`, and every row's `load-when`
  names tasks rather than topics.
- Each reason that rests on a decision or an investigation links it under `docs/`.

## 4. Apply and report

Make the cuts. Then say:

- How many lines went, per file.
- The three biggest cuts, each with the `file:line` that proved it was restatement.
- Every fence still missing a reason. These are the user's to answer, and they are the
  only thing here that blocks.
