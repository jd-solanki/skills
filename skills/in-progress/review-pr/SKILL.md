---
name: review-pr
description: >
  Review a PR or branch in rounds until a round finds nothing new. Each round runs a fresh reviewer
  subagent (correctness and simplicity in parallel) and a separate implementer subagent; the next
  round's reviewer verifies the last round's fixes. Use when the user asks to review a PR, review a
  branch, or review until clean.
---

Loop rounds until **dry**: the reviewer returns no finding *and* confirms every fix from the round
before.

## Loop

1. **Pin the range.** `git diff <merge-base>` — no second ref, so earlier rounds' uncommitted fixes
   stay in scope. Pin the spec too (PR body, or the issue it closes); a reviewer with no spec
   reports style.
2. **Reviewer → join → implementer → join.** Silent between them; report once the round closes.
3. **Carry paths, not text.** The reviewer writes its ledger to the session scratchpad and returns
   one summary line. Hand the next agent the paths to read. Ledgers never enter your context, so
   nothing is retyped, nothing is dropped, and nothing is re-escaped.
4. **Dry, or round 3 → report.** The ceiling is a backstop, not dryness — say which ended the loop.
   `$ARGUMENTS` raises it.

## Roles

| Job | Who | Constraint |
|---|---|---|
| Find | reviewer subagent, fresh each round | read-only in the repo |
| Fix | implementer subagent | never verifies its own work |
| Carry | you | dispatch, join, pass ledger paths |

The prior ledger is the fresh reviewer's **oracle**: read before the code.

## Reviewer brief

Fill the slots, send as one prompt.

```xml
<role>
  Review coordinator for round [N]. You wrote none of this code and ran no earlier round.
</role>

<constraints>
  Read-only in the repo: you and your sub-agents change no file under [path], and run no
  git commit, push, checkout, reset or stash. Earlier rounds are uncommitted; a stray write
  destroys them. Your single write is the ledger; sub-agents write nothing at all.
  Repeat this in each sub-agent's brief.
</constraints>

<context>
  Directory: [path] — stay inside it.
  Range: [range]
  Spec: [path]
  Repo docs the range touches: CLAUDE.md, CONTEXT.md, docs/agents/*.md
</context>

<prior-rounds>
  Already found and fixed, in order. Read every one before you read the code: [ledger paths]
  Verify those fixes first; report one only if wrong, incomplete, or newly broken.
  Then go where earlier rounds did not: [untouched surfaces]
</prior-rounds>

<sub-agents>
  Spawn exactly two in one message, then wait for both.

  <correctness>
    Invoke /code-review and /coding, obey each triage gate.

    /coding IS the coding standards for /code-review's Standards axis. Name it as the standards
    source: this repo ships no CODING_STANDARDS.md, so without that pointer the axis falls back to
    a generic smell baseline and every round invents its own checklist.

    Correctness outranks style. Scan for bugs, edge cases, regressions, race conditions, security,
    performance, accessibility, API and design, maintainability, tests, backward compatibility and
    missing validation. Challenge assumptions.

    Trace the flow in source against the pinned dependency versions. If the range touches a
    rendered surface, load the page and look — stacking-context and accessible-name defects are
    invisible to a source read. The run skill launches the app; Playwright CLI drives it.
  </correctness>

  <simplicity>
    Invoke /ponytail-review and /simplify, obey each triage gate.
    /simplify applies fixes — override it, report only.
    Name what to cut and what replaces it.
  </simplicity>
</sub-agents>

<your-job>
  1. Merge, dedupe, keep the sharper statement.
  2. Report the class, not the instance. Grep the finding's shape across the range; every site is
     one finding.
  3. Refute each finding — open the file and make it fail. Cannot? Drop it. Taste with no cost, and
     trade-offs the spec names, are not findings.
  4. Rank by severity.
</your-job>

<output>
  Write exactly this to [ledger path]:

    ## Verdict
    <one sentence: safe to merge, or not, and why>

    ## Round [N-1] fixes
    <one line each: correct | wrong or incomplete + what. Expand only on a problem.>

    ## Findings

    ### F1 — <title>
    - **Severity:** blocker | major | minor
    - **Axis:** correctness | simplicity
    - **Where:** <every site>
    - **Problem:** <one or two concrete sentences>
    - **Failure:** <input or state that breaks it; for simplicity, the cost paid>
    - **Fix:** <specific enough to need no further investigation>

  Then return one line and nothing else:
  <verdict> | N findings: B blocker, M major, m minor | round [N-1] fixes: X confirmed, Y broken

  "None." is a valid Findings section. The implementer acts on your ledger literally.
</output>
```

## Implementer brief

```xml
<role>
  Implementer for round [N].
  Invoke ponytail with args ultra: deletion before addition, shortest change that fully fixes.
</role>

<constraints>
  Directory: [path] — stay inside it. Earlier rounds are uncommitted: no git checkout, reset,
  stash, commit or push. Leave changes in the working tree.
</constraints>

<task>
  Read the ledger at [ledger path]. Apply every finding.
  A reviewer already confirmed each against source, so implement rather than re-litigate.
  A Fix that proves wrong at the keyboard: fix the real problem, say so.
  Run the repo's checks (scripts in root package.json) until green. Weaken no test or type.
</task>

<output>
  Return exactly this:

    ## Applied
    - F1 — <what changed, which file; deviation from the Fix and why>

    ## Checks
    - <command>: pass | fail — <error, verbatim and short>

    ## Notes
    <a wrong Fix, an unpassable check, work not done. Otherwise "None.">
</output>
```

## Traps

- **`/simplify` writes.** Keep the reviewer brief's override when you edit it.
- **`Checks: pass` is a claim, not evidence.** Run them yourself — 3 of 15 fixes came back wrong in
  the reference run, 2 of them new bugs the review introduced.
- **A two-ref diff hides the round.** `git diff <base> HEAD` skips every uncommitted fix.
- **A ledger inside the repo dirties `git status`,** which the implementer reads. The session
  scratchpad needs no `.gitignore` entry.