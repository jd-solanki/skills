# Contributing

## What this is

A library of AI agent skills, published for installation into other repositories
through the skills CLI. Most are written for my own projects first and generalised
once they have survived real work.

## Status

Working and installed in real projects. `skills/in-progress/` is the incubator: a
skill there is still moving and may change shape without notice. Everything outside it
has been used on real work and settled.

The context-engineering system — `/setup-project-context`, `/audit-project-context`,
and the two forks that depend on them — is written but has not yet been run on a real
repository. Treat it as unproven until it has.

## Conventions

Every rule about this repo lives in `/project-context`. Invoke it.

## How to contribute

- Work lands straight on `main`. One commit per skill.
- Commits: use `/git-commit`.
- Write a skill with `/writing-for-agents`.
