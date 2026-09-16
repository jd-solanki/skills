# Layout

## Rules

- A published skill lives at `skills/<category>/<skill-name>/SKILL.md`. Reference files
  sit beside it in the same folder.
- A new skill, or one still moving, starts in `skills/in-progress/`. It leaves once it
  has been used on real work and stopped changing.
- `coding` is about the code itself. `engineering` is about everything around it.
- A fork goes in the category it belongs to, never in `third-party/`. `third-party/` is
  for copies kept unchanged.
- `skills/internal/` is for skills that serve this repository only and are never
  published for installation elsewhere.
- A published skill is used here through a symlink in an agent skills directory.
  `/link-skills` makes them.

## Reasons

- Reference files sit beside `SKILL.md` because the skills CLI installs the **folder**.
  A reference kept anywhere else does not travel with the skill.
- `in-progress` is an incubator borrowed from `mattpocock/skills`. It lets a skill ship
  and be used before it has settled, without claiming it is stable.
- A fork lives in its real category because we maintain it now. Filing it under
  `third-party/` would claim upstream still does. Attribution goes in `README.md`
  rather than inside the skill, so it does not load on every invocation.

## Fences

- **`.agents/skills/` is not ours.** Those skills are installed from elsewhere and are
  overwritten on the next install, so an edit made there is lost without warning. Edit
  `skills/` and re-link.
- **`.claude/skills/` mixes two kinds of symlink.** Some point into `../../skills/`
  and are ours to edit; some point into `../../.agents/skills/` and are not. Run
  `ls -la .claude/skills/` and read the target before editing through a link.
- **`/link-skills` hardcodes `skills/<category>/<name>`.** A skill placed directly
  under `skills/` cannot be linked, because the relative depth it builds is wrong.
  `skills/productivity/link-skills/SKILL.md:8`
- **`CLAUDE.md` is a symlink to `AGENTS.md`.** Both agents read one file, so a tool
  that refuses to write through a symlink must be pointed at `AGENTS.md` instead.

## Where it lives

`skills/`, `.agents/skills/`, `.claude/skills/`, `skills-lock.json`,
`skills/productivity/link-skills/SKILL.md`, `AGENTS.md`
