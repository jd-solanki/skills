---
name: review-pr
description: >
  Review a PR or branch in rounds until a round finds nothing new. Each round runs two fresh
  reviewer subagents in parallel — correctness and simplicity — then one implementer subagent; the
  next round's reviewers verify the last round's fixes. Use when the user asks to review a PR,
  review a branch, or review until clean.
---

Loop rounds until **dry**: both reviewers return no finding *and* confirm every fix from the round
before.

## Loop

1. **Pin the range.** `git diff <merge-base>` — no second ref, so earlier rounds' uncommitted fixes
   stay in scope. Pin the spec too (PR body, or the issue it closes); a reviewer with no spec
   reports style.
2. **Both reviewers → join → implementer → join.** Dispatch the two in one message, then let each
   agent's completion notification arrive on its own; `sleep` buys nothing. Silent between them;
   report once the round closes.
3. **Carry paths, not text.** Each reviewer writes its own ledger to the session scratchpad —
   `round-[N]-correctness.md`, `round-[N]-simplicity.md` — and returns one summary line. Hand the
   next agent the paths to read. The axis in the filename is load-bearing: next round's reviewer
   verifies the fixes on its own axis. Ledgers never enter your context, so nothing is retyped,
   nothing is dropped, and nothing is re-escaped.
4. **Dry, or round 3 → report.** The ceiling is a backstop, not dryness — say which ended the loop.
   `$ARGUMENTS` raises it.

## Roles

| Job | Who | Constraint |
|---|---|---|
| Find | two reviewer subagents, fresh each round, one per axis | read-only in the repo |
| Fix | implementer subagent, reads both ledgers | never verifies its own work |
| Carry | you | dispatch both, join both, pass ledger paths |

A reviewer reads before it prescribes, and refutes its own findings before it writes them down.
Every Fix names a file the reviewer opened.

## Reviewer brief

Fill the slots and send it twice in one message, once per axis section below.

```xml
<role>
  [axis] reviewer for round [N]. You wrote none of this code and ran no earlier round.
  Do the whole review yourself.
</role>

<constraints>
  Read-only in the repo: change no file under [path], and run no git commit, push, checkout,
  reset or stash. Earlier rounds are uncommitted; a stray write destroys them. Your single
  write is your own ledger.
</constraints>

<context>
  Directory: [path] — stay inside it.
  Range: [range]
  Spec: [path]
  Repo docs the range touches: CLAUDE.md, CONTRIBUTING.md, and the /project-context
  references whose load-when matches the range
</context>

<prior-rounds>
  Your axis's earlier ledgers, in order. Read every one before you read the code: [ledger paths]
  Verify those fixes first; report one only if wrong, incomplete, or newly broken.
  Then go where earlier rounds did not: [untouched surfaces]
</prior-rounds>

<axis>
  [paste the matching axis section, verbatim]
</axis>

<your-job>
  1. Report the class, not the instance. Grep the finding's shape across the range; every site is
     one finding.
  2. Refute each finding — open the file and make it fail. Cannot? Drop it. Taste with no cost, and
     trade-offs the spec names, are not findings.
  3. Open every file the Fix touches, plus the callers and the docs it cites, before you write the
     Fix. A Fix for a file you never opened is a guess. Drop the finding or go read.
  4. Rank by severity.
</your-job>

<output>
  Write exactly this to [axis ledger path]:

    ## Verdict
    <one sentence: safe to merge on your axis, or not, and why>

    ## Round [N-1] fixes
    <one line each: correct | wrong or incomplete + what. Expand only on a problem.>

    ## Findings

    ### [prefix]1 — <title>
    - **Severity:** blocker | major | minor
    - **Where:** <every site>
    - **Problem:** <one or two concrete sentences>
    - **Failure:** <input or state that breaks it; for simplicity, the cost paid>
    - **Fix:** <specific enough to need no further investigation>

    ## Not exercised
    <every surface you could not check, and why. "Nothing." only if you exercised all of them.>

  Then return one line and nothing else:
  <verdict> | N findings: B blocker, M major, m minor | round [N-1] fixes: X confirmed, Y broken

  "None." is a valid Findings section. The implementer acts on your ledger literally.
</output>
```

### Correctness axis

```
Invoke /code-review and /coding, obey each triage gate. Number your findings C1, C2 and on.

/coding IS the coding standards for /code-review's Standards axis. Name it as the standards
source: this repo ships no CODING_STANDARDS.md, so without that pointer the axis falls back to
a generic smell baseline and every round invents its own checklist.

Correctness outranks style. Scan for bugs, edge cases, regressions, race conditions, security,
performance, accessibility, API and design, maintainability, tests, backward compatibility and
missing validation. Challenge assumptions.

Trace the flow in source against the pinned dependency versions.

A range that touches a page or a component is reviewed in a browser as well as in source.
Load it, drive it, report what you saw. Stacking context, focus order, accessible names and
anything that streams are invisible to a source read, and a surface reviewed only in source
still reads as reviewed. The run skill launches the app and Playwright CLI drives it;
development mode pre-fills the credentials, so a signed-in page costs you nothing.
Every surface you could not exercise goes in "Not exercised" by name.
```

### Simplicity axis

```
Invoke /ponytail-review and /simplify, obey each triage gate. Number your findings S1, S2 and on.
/simplify applies fixes — override it, report only.
Name what to cut and what replaces it.
```

## Implementer brief

```xml
<role>
  Implementer for round [N].
  Invoke ponytail with args ultra: deletion before addition, shortest change that fully fixes.
  Invoke /coding too. It is the standards the reviewers judged this range against, and the
  standards next round's reviewers judge your fixes against. Write to the bar you will be read at.
</role>

<constraints>
  Directory: [path] — stay inside it. Earlier rounds are uncommitted: no git checkout, reset,
  stash, commit or push. Leave changes in the working tree.
  `git add -N` every file you create, the moment you create it. `git diff` hides an untracked
  file, so the range is missing it and next round's reviewer reads a file that is not there.
</constraints>

<task>
  Read both ledgers — [correctness ledger path], [simplicity ledger path] — before your first
  edit. Apply every finding from both.
  A reviewer already refuted each against source, so implement rather than re-litigate.
  Two findings on one site are one change: satisfy both, and correctness wins any conflict.
  A Fix that proves wrong at the keyboard: fix the real problem, say so.
  Run the repo's checks (scripts in root package.json) until green. Weaken no test or type.
</task>

<output>
  Return exactly this:

    ## Applied
    - <finding id> — <what changed, which file; deviation from the Fix and why>

    ## Checks
    - <command>: pass | fail — <error, verbatim and short>

    ## Notes
    <a wrong Fix, an unpassable check, work not done. Otherwise "None.">
</output>
```

## Traps

- **`/simplify` writes.** Keep the simplicity axis's report-only override when you edit it.
- **`Checks: pass` is a claim, not evidence.** Run them yourself — 3 of 15 fixes came back wrong in
  the reference run, 2 of them new bugs the review introduced.
- **A two-ref diff hides the round.** `git diff <base> HEAD` skips every uncommitted fix, and an
  untracked file is missing from the range whichever refs you pin. Check `git status` against the
  range before you dispatch.
- **A rendered surface skips itself.** Stated as a condition, the browser pass is the step the
  reviewer drops under load. The reference run reached round 3 before anyone loaded the page, and
  that one browser turn found the worst bug in the PR. "Not exercised" is what makes the skip
  visible.
- **A ledger inside the repo dirties `git status`,** which the implementer reads. The session
  scratchpad needs no `.gitignore` entry.