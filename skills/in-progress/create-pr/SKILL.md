---
name: create-pr
description: Open one pull request as a draft, with a body the reviewer can act on.
argument-hint: "[what the PR does]"
disable-model-invocation: true
---

# Create PR

Read `/writing-for-humans` skill first. It carries the title, the shape, the evidence
rules, and the de-slopping pass. This skill adds only what a pull request needs on
top.

The work is already written and committed. This turns it into a pull request a
reviewer can act on. It opens as a **draft**. Marking it ready for review is the
author's call, never yours.

## The body carries what the diff can't

The diff is already open in the reviewer's tab. Anything they can read there is not
your job to restate: bullets that say "adds X", "moves Y", "renames Z" pad the body
without giving the reviewer something new. The body earns its space on the two
things the diff cannot show:

1. **Why** — what was true before, and what forced the change. The trigger, the
   report, the deadline, the security note.
2. **Notes** — the things a careful reader still cannot infer from the diff after
   reading it. Invariants that hold across the change, a decision that looks
   arbitrary but was deliberate, a gotcha that will trip the next person, a
   constraint from outside the repo.

That is the whole body. If a Note fails the test "could the reviewer figure this
out from the diff alone?" it goes; if there are no surviving Notes, the section
comes out. **Why** stays regardless — the reason a change happened is never in the
diff.

Section names read like a human wrote them: `## Why`, `## Notes`. Anything like
`## What changed`, `## How you know`, `## Verification`, `## Things a reviewer
cannot read off the diff` sounds AI-authored and confuses a human reader who
opens the PR expecting a colleague's writing.

## Read the diff, don't imagine it

`git diff <base>...HEAD` and `git log <base>..HEAD` before you write a word.

Every claim in the body traces back to a line you read. A body that describes a
change the diff does not contain costs the reviewer more than an empty body:
they have to find the lie before they can start reviewing.

Reading the diff also settles which Notes are real. If a bullet you drafted for
Notes turns out to sit in plain view of the diff, it fails the test and comes out.

## The title becomes history

Your title is the line the squashed merge commit carries, so write it for
`git log`.

## Link the ticket

`Closes #123` at the bottom of the body, so merging closes the ticket. Reference
the ticket by ID rather than pasting a link: some trackers put private detail in
the URL.

No ticket exists? A one-line PR body — just the **Why** — is fine. Do not open a
ticket just to link it.

## Length

One change per PR. A refactor and a fix in the same diff make the reviewer grade
two things at once, and they will do both worse.

## Process

### 1. Check where you are

You need a branch that is not the default one, and a clean tree with your work
committed. On the default branch, or holding uncommitted changes? Say so and
stop. Committing is `/git-commit`.

**Done when:** you know the base branch, the current branch, and that nothing is
uncommitted.

### 2. Read the change

The diff, the log, and the ticket it closes.

**Done when:** you can state the trigger for the change, and every Note you plan
to include, from what you read.

### 3. Draft the body

Title, then **Why**, then **Notes** if any survive the diff-alone test, then the
ticket line. Skip empty sections rather than filling them.

### 4. Clean it up

Run the draft through `/writing-for-humans`: the title, the evidence, the secrets
check, and the humanizer pass. Two extra tells in a pull request:

- A bullet per file that only restates the filename.
- A section titled with the check the reviewer is being asked to do rather than
  the thing they are being told (`What changed`, `How you know`, `Verification`).
  Rename to a human heading, or if the section only restated the diff, cut it.

### 5. Show it, then open it

Print the title and body. On the go-ahead, push the branch and open the pull
request **as a draft**:

```shell
gh pr create --draft --base <base> --title "<title>" --body "<body>"
```

Return the link, and say plainly that it is a draft waiting for them to mark it
ready for review.

Labels go on after it exists (`gh pr edit <n> --add-label ...`), and only labels
the repo already has.

## Where it goes

GitHub through the `gh` CLI is the fallback. Before you settle for it, check
`git remote -v`: GitLab takes `glab`, where the draft flag is `--draft` on
`glab mr create`.

A repo pull request template at `.github/pull_request_template.md` is the house
style, and it wins. Fill its sections; sections that do not apply to this change
come out rather than getting padded.

## Boundaries

Opens the pull request. Reviewing it, merging it, and marking it ready for review
belong to a person.
