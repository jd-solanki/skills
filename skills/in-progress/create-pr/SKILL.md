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
reviewer can act on. It asks someone for their time, and the body is your half of
the trade: what changed, why it changed, and why they can trust it.

It opens as a **draft**. Marking it ready for review is the author's call, never
yours.

## What every PR body answers

Three lines. The reviewer decides "do I trust this?" from them.

1. **Why** - what was true before, and why it had to change.
2. **What changed** - what the diff does, in plain words. Not a list of files.
3. **How you know** - the check you ran, and what it printed.

For a bug that is: the old behaviour, the cause, the fix. For a feature: the gap,
the new behaviour, the proof it works. Same three slots either way.

## Read the diff, don't imagine it

`git diff <base>...HEAD` and `git log <base>..HEAD` before you write a word.

Every claim in the body traces back to a line you read. A body that describes a
change the diff does not contain costs the reviewer more than an empty body: they
have to find the lie before they can start reviewing.

## Red before green

Your change needs one check that would have failed without it.

Fixing a bug, that check is the reproduction from the ticket. Adding a feature, it
is the test that calls the new behaviour. Run it against the old code first and
watch it fail - **red**. Then run it against your change and watch it pass -
**green**. A test that never failed proves nothing; it may be passing for reasons
that have nothing to do with your work.

Name that test in the body so the reviewer can run it themselves.

Nothing here can be tested, because it is docs, config, or a rename? Say what you
did instead: the page you loaded, the command you ran, the output you compared.

## Report what you ran, not what should pass

"Ran `pnpm test src/upload.test.ts`, 14 passed, 0 failed" is a fact a reviewer can
check. "Tests should pass" is a wish.

Only facts go in the body. Did not run it? Write that down. An honest gap is
cheap; a confident claim that turns out false costs the reviewer their afternoon
and costs you their trust.

## The title becomes history

Your title is the line the squashed merge commit carries, so write it for
`git log`. `git log --oneline -20` tells you whether the repo uses conventional
commits.

## Link the ticket

`Closes #123` in the body, so merging closes the ticket. Reference the ticket by
ID rather than pasting a link: some trackers put private detail in the URL.

No ticket exists? A one-line PR body that repeats what a ticket would have said is
fine. Do not open a ticket just to link it.

## Length

One change per PR. A refactor and a fix in the same diff make the reviewer grade
two things at once, and they will do both worse.

## Process

### 1. Check where you are

You need a branch that is not the default one, and a clean tree with your work
committed. On the default branch, or holding uncommitted changes? Say so and stop.
Committing is `/git-commit`.

**Done when:** you know the base branch, the current branch, and that nothing is
uncommitted.

### 2. Read the change

The diff, the log, and the ticket it closes.

**Done when:** you can answer the three questions from what you read, without
guessing at intent.

### 3. Run the check

Run the tests that cover the change, and paste real output. Red before green for
a bug fix.

**Done when:** you have a command and its result to put in the body, or a written
reason you have neither.

### 4. Draft the body

Title, then the three answers. Only the parts that carry something.

### 5. Clean it up

Run the draft through `/writing-for-humans` skill: the title, the evidence, the secrets
check, and the humanizer pass. One extra tell in a pull request: a bullet per file
that only restates the filename. Cut those.

### 6. Show it, then open it

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
style, and it wins. Fill its sections and put the three answers inside them.
Sections that do not apply to this change come out rather than getting padded.

## Boundaries

Opens the pull request. Reviewing it, merging it, and marking it ready for review
belong to a person.
