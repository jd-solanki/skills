# AGENTS.md

## Two skill folders

- `skills/` is what this repo publishes. Edit these.
- `.agents/skills/` is what is installed here from elsewhere, to use while working.
  Someone else owns those; leave them alone.

## Layout

Every published skill lives at `skills/<category>/<skill-name>/SKILL.md`. Reference
files sit beside it in the same folder, because the skills CLI installs the folder.

`in-progress` is the incubator, borrowed from `mattpocock/skills`. A skill leaves it
once it has been used on real work and stopped changing.

`coding` and `engineering` are easy to confuse. `coding` is about the code itself.
`engineering` is about everything around it.

## Adding a skill

New or still moving? It starts in `skills/in-progress/`. Settled? Pick the category
it belongs to.

Write it with `/writing-for-agents` skill, in `.agents/skills/`. Read its
`SKILL-MECHANICS.md` for frontmatter and the model-invoked versus user-invoked
choice.

## The instruction block this repo ships

**Read** `skills/scaffolding/setup-jd-solanki-skills/SKILL.md`. It holds the block that gets written into other people's repos: skill reference loading, sub-agent delegation,
single source of truth. Those rules apply here too.

Read it there. Copying it into this file would give one repo two copies of it, and
the block's own rule says not to.

## Commit Guidelines

- Use feat, fix, etc instead of docs as this repo is for skills and using docs doesn't make sense
- Use skills as scope like `feat(my-skill): ...`
