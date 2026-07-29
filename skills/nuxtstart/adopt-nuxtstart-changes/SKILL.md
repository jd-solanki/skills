---
name: adopt-nuxtstart-changes
description: Audit, pull, and reconcile NuxtStart upstream changes into a child repository.
disable-model-invocation: true
---

# Adopt NuxtStart changes

Maintain an **adoption map**: every upstream-changed path belongs to one bounded area with a recorded integration decision.

## 1. Establish the baseline

1. Read the repository instructions and inspect the current branch, worktree, history, and remotes.
2. Confirm the lowercase `nuxtstart` remote exists with `git remote get-url nuxtstart`. When it is absent, offer to add it and ask the user for permission (Repo: nuxtstart/nuxtstart).
3. Begin integration from a clean worktree. When local changes exist, show the exact paths and ask the user to commit, stash, or authorize a safe preparation step.
4. Record the pre-pull `HEAD`, then fetch with `git fetch nuxtstart --prune`.
5. Resolve the upstream default branch with `git symbolic-ref --quiet --short refs/remotes/nuxtstart/HEAD`. If that ref is absent, obtain the remote's advertised HEAD instead of guessing a branch name. Record both the remote-tracking ref and its branch name, such as `nuxtstart/main` and `main`.
6. Find the merge base with `git merge-base HEAD <upstream-ref>`. If none exists, report that an adoption baseline cannot be established and ask for one.

This step is complete when the child `HEAD`, upstream ref and SHA, merge base, and clean-worktree state are known.

## 2. Build the adoption map

Start with compact manifests rather than opening every historical commit:

```bash
git rev-list --count <merge-base>..<upstream-ref>
git diff --shortstat <merge-base> <upstream-ref>
git diff --dirstat=files,0 <merge-base> <upstream-ref>
git log --oneline --max-count=50 <merge-base>..<upstream-ref>
```

Save the complete upstream `git diff --name-status <merge-base> <upstream-ref>` output as a temporary manifest. Read it in bounded slices grouped by directory. Generate an equivalent child-side manifest from `<merge-base>` to `HEAD` only for areas that need divergence analysis.

Group every upstream-changed path into a cohesive area such as a Nuxt layer, package, configuration surface, or documentation set. For each area, inspect final upstream source, current child source, and only the history relevant to those paths. Classify its integration as:

- **Already present** — the child already implements the final upstream intent.
- **Accept upstream** — the upstream state should enter unchanged.
- **Preserve child** — an intentional child customization should win.
- **Reconcile** — both sides contain intent that the merged result must preserve.

### Scale with subagents

Delegate the audit when there are more than 25 upstream commits, more than 50 changed files, or at least three independent areas. Split any area containing more than 20 changed paths into smaller cohesive subareas. Give each subagent:

- the child `HEAD`, merge base, and upstream ref;
- one bounded area and its exact changed paths;
- a read-only task to inspect final source and path-specific history;
- the four integration classifications above;
- a required report of upstream intent, child intent, likely conflicts, and relevant checks.

Run independent area audits in parallel and in waves when they exceed the available slots. Keep Git integration and adoption-map ownership with the primary agent. Reconcile every subagent report against the manifests so no path is omitted or counted twice.

This step is complete when every upstream-changed path appears once in the adoption map and each area has an evidence-backed integration decision.

## 3. Pull the upstream state

Pull the audited branch as one inspectable merge:

```bash
git pull --no-rebase --no-ff --no-commit nuxtstart <upstream-branch>
```

`--no-rebase` merges the template history, `--no-ff` records the sync even when a fast-forward is possible, and `--no-commit` leaves a clean merge result pending for inspection.

Compare `FETCH_HEAD` with the audited upstream SHA. When upstream advanced during the audit, map the incremental paths before continuing. Apply the adoption-map decisions to the pending merge, preserving both intents for every **Reconcile** area.

If the pull produces conflicts, invoke `/resolving-merge-conflicts` (Add if missing via `npx skills@latest add mattpocock/skills --skill resolving-merge-conflicts`) and give it the adoption map as the statement of intent. Resume this skill after conflict resolution finishes.

This step is complete when the pull is integrated, every adoption-map decision is represented, and no unmerged paths remain.

## 4. Verify and report

1. Inspect the full merge against the recorded pre-pull `HEAD`.
2. Discover and run the repository's required formatting, lint, typecheck, test, and build checks in proportion to the adopted areas.
3. If the merge is still pending, commit it with a conventional message that identifies the NuxtStart sync.
4. Confirm the worktree has no unresolved merge state.
5. Report:
   - the upstream branch, SHA, and range reviewed;
   - the adoption map and any subagent assignments;
   - upstream changes accepted;
   - child customizations preserved;
   - reconciled areas and conflicts;
   - verification results.

The run is complete only when every upstream-changed path is accounted for, the audited upstream SHA is merged, verification passes, and Git reports no unresolved conflicts.
