# Glossary

This repository publishes skills. It also installs other people's skills to use while
working on them, so almost every word here exists to keep those two apart.

**Skill**:
A folder holding a `SKILL.md` and the reference files beside it. The folder is the
unit: the skills CLI installs the whole of it, so a reference file only travels if it
sits inside.
_Avoid_: command, prompt, plugin

**Published skill**:
A skill this repository owns and ships, under `skills/`. The only kind that is edited
here.
_Avoid_: local skill, our skill

**Installed skill**:
A skill written elsewhere and installed into this repository under `.agents/skills/`
so it can be used while working. Someone else owns it.
_Avoid_: vendored, third-party copy

**Fork**:
An installed skill that has been copied into `skills/` and changed. It stops being
someone else's the moment it is edited, because upstream can no longer be re-pulled
cleanly.
_Avoid_: vendored, patched

**Category**:
The folder between `skills/` and a skill's own folder — `coding`, `engineering`,
`scaffolding`, and the rest. It is part of the path the tooling depends on, not a
label.
_Avoid_: group, section, namespace

**Incubator**:
`skills/in-progress/`, where a skill lives while it is still changing. A skill leaves
once it has been used on real work and stopped moving.
_Avoid_: draft, wip, staging

**The block**:
The instruction text this repository writes into other people's `CLAUDE.md` or
`AGENTS.md`. It has exactly one home, named in `domains/authoring.md`.
_Avoid_: the template, the preamble
