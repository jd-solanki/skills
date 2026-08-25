# AGENTS.md

## Two skill folders

- `skills/` is what this repo publishes. Edit these.
- `.agents/skills/` is what is installed here from elsewhere, to use while working.
  Someone else owns those; leave them alone.

## Layout

Every published skill lives at `skills/<category>/<skill-name>/SKILL.md`. Reference
files sit beside it in the same folder, because the skills CLI installs the folder.

| Category | Holds |
|---|---|
| `automation` | releases and changelogs |
| `aws` | AWS architecture and practice |
| `bruno` | the Bruno API client |
| `coding` | how code should look: naming, comments, structure |
| `engineering` | how work gets done: git, tickets, pull requests |
| `nuxtstart` | the Nuxtstart template |
| `scaffolding` | starting a project, or configuring this repo |
| `third-party` | skills other people wrote, vendored here |
| `in-progress` | written, not settled, not recommended yet |

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

## Why the folders exist

For people reading the repo. **The skills CLI does not read them.**

`npx skills@latest add jd-solanki/skills` walks the tree for `SKILL.md` files and
prints one flat list. Grouping in the install picker comes from a `.claude-plugin/`
manifest that names each skill path, and this repo does not ship one yet.

So moving a skill between categories changes nothing for whoever installs it. Do
not expect it to.

## The instruction block this repo ships

`skills/scaffolding/setup-jd-solanki-skills/SKILL.md` holds the block that gets
written into other people's repos: skill reference loading, sub-agent delegation,
single source of truth. Those rules apply here too.

Read it there. Copying it into this file would give one repo two copies of it, and
the block's own rule says not to.
