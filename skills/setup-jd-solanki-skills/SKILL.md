---
name: setup-jd-solanki-skills
description: Setup you may require to use jd-solanki skills and tools.
disable-model-invocation: true
---

## 1. Upsert Agent Instructions

Upsert the instructions in the `<template>` below into the user's agent instructions file. The goal is to keep **one single file as the source of truth** and have the other file be a **soft symlink** pointing to it, so both `CLAUDE.md` and `AGENTS.md` always stay in sync. These also include updating outdated instruction files.

Determine what to do based on which files already exist:

- **Neither exists:** Create `AGENTS.md` as the source file, upsert the instructions into it, then create `CLAUDE.md` as a soft symlink pointing to `AGENTS.md`.
- **Only one exists:** Upsert the instructions into the existing file, then ask the user if they want to generate the second file. If they say yes, create the second file as a soft symlink pointing to the existing (source) file.
- **Both exist:** Simply upsert the instructions into the source file. If the second file is not a symlink of the source, suggest that the user symlink one file from the other source file they prefer (so the two stay in sync).

<template>
## Skill reference loading

Skills ship a main `SKILL.md` (always loaded) plus optional files in the same directory — `references/*`, `examples/*`, `SAMPLE.md`, etc. — loaded on demand. Load them deliberately: not all up-front, not blindly.

**IMPORTANT — this is a BLOCKING gate.** After invoking ANY skill, before any other tool call or task action, you MUST emit a one-line triage decision and then immediately Read the files it names:

`Triage <skill-name>: loading <files>; skipping <files> because <reason>.`

The triage line and the `Read` calls for every file listed as "loading" are ONE atomic step. Emitting the line without then Reading those files, or doing task work with a file you announced but did not Read, is a violation. If a skill lists no reference files, state `Triage <skill-name>: no reference files.` and no Reads are required.

To decide what to load:

1. **Build a menu** from the reference list in the skill's main file. If it lists none, glance at each `references/*.md` (its `load-when` line or first heading) for its topic.
2. **Classify each reference:** *core* (no condition stated) → load; *conditional* (tied to a language, task type, or context — Python vs JS, bug vs feature) → load only if this task meets the condition.
3. **Don't re-read** what's already loaded; re-evaluate only if the task changes.

When in doubt, load too few rather than too many — you can read a reference later once the task makes the condition clear.

## Context Window - Smart Zone, Delegation & Sub Agents

As the context window fills with a large number of irrelevant/unwanted tokens, it causes model's output quality to degrade.

It is strongly recommended to utilize sub agents where task is simple few steps, not relevant to main task of the current thread. Use Sub Agents to keep main context window clean, lean & relevant. See [Sub Agents](#sub-agents) section below for more details.

While working on main task, if you find out that user has given another task which is medium to large in size, which requires its own new thread utilizing multiple sub agents under it, so it is strongly recommended to ask user to start a new thread and resolve that task in new thread, and once it's done, back to current thread.

## Sub Agents

When invoking sub agents, it's important to also pass instruction to invoke task related skills along with relevant context to them. E.g. When handing a feature/task, instruct to invoke feature development related skills available in the system.

For example, when verification of a feature is required, invoke a sub agent to handle the verification task and return only the result to main agent. This way, main agent's context window remains clean and relevant to the main task. Another example can be inspecting bug in implement task, where sub agent can be invoked to handle the inspection and return only the result to main agent.
</template>

## 2. Third-Party Skills

> [!IMPORTANT]
> Only proceed with this section once **1. Upsert Agent Instructions** is fully done.

Read [`THIRD-PARTY.md`](./THIRD-PARTY.md) for a list of third-party skills, list them and suggest user that these are skills that they may want to install and use in their projects.