---
name: setup-jd-solanki-skills
description: Setup you may require to use jd-solanki skills and tools.
disable-model-invocation: true
---

## 1. Upsert Agent Instructions

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa) — always edit the one that's already there.

If following template block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## General Rules

- Do not manually edit files managed by CLI tools. E.g. skills-lock.json, pnpm-lock.yml, etc
- When creating .md file, if you find something can be visualized for reader's understanding do create visualization block using mermaid. This also applies to markdown supporting operations like GH issue or comments or form submissions which support markdown content
  - For GH issues & PR, also create this visualization block on top somewhere so they can easily understand via visualization
- Always use "Ponytail" skills as per context: `/ponytail`, `/ponytail-audit` & `/ponytail-review`

## Core Engineering Principles

These apply to every change you make. They are not optional style preferences.

- **Make architectural decisions for the long term. Do not accept a stopgap that only works for now and is meant to be replaced later.**
- Do not preserve backward compatibility. Remove obsolete paths instead of adding compatibility layers, fallbacks, or migrations.
- Choose the simplest implementation that fully meets the current requirements. Avoid speculative abstractions, configuration, and indirection.
- Grow the system in layers. Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
- Keep components modular and concerns clearly separated.

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

For example, when verification of a task is required, invoke a sub agent to handle the verification task and return only the result to main agent. This way, main agent's context window remains clean and relevant to the main task. Another example can be inspecting bug in implement task, where sub agent can be invoked to handle the inspection and return only the result to main agent.

## Prefer a Single Source of Truth

Do not duplicate knowledge that already has an authoritative source.

When a value, rule, configuration, or behavior is defined elsewhere, reference, import, or derive from that source instead of copying it. This applies to prose as much as to code — issues, PR descriptions, docs, and comments.

Examples:

* **Node.js version:** Do not hard-code the version in documentation, scripts, or CI if the repository already defines it in `.node-version`, `.nvmrc`, or another canonical runtime configuration. Reference or read from that source instead.
* **pnpm version:** Do not repeat the pnpm version across documentation or tooling when it is already defined in `package.json`, such as through the `packageManager` field. Reference or derive it from there.
* Import a shared constant instead of redefining the same value in multiple modules.
* Read configuration from its canonical source instead of maintaining parallel copies.
* **Repository content quoted in prose:** When an issue, PR description, or doc refers to something that lives in the repository — a list in `README.md`, a set of supported options, a config schema — point the reader at that location instead of pasting the content. The pasted copy goes stale the moment the source changes, and readers then trust the wrong one. Write "see the supported providers list in `README.md`" instead of reproducing the list.

Before adding duplicated information, check whether a canonical source already exists. If it does, use that source.

Apply DRY to duplicated **knowledge**, not merely similar-looking code. Do not introduce abstractions solely to eliminate harmless code repetition when doing so would reduce clarity or increase coupling.
```

Include this as well if user is using context7:

```markdown
<!-- context7 -->
# Context7

Use the `ctx7` CLI to fetch current documentation whenever the user asks about a library, framework, SDK, API, CLI tool, or cloud service -- even well-known ones like Vue, Nuxt, Prisma, Express, Tailwind, Django, or Spring Boot. This includes API syntax, configuration, version migration, library-specific debugging, setup instructions, and CLI tool usage. Use even when you think you know the answer -- your training data may not reflect recent changes. Prefer this over web search for library docs.

Do not use for: refactoring, writing scripts from scratch, debugging business logic, code review, or general programming concepts.

### Steps

1. Resolve library: `pnpm dlx ctx7@latest library <name> "<user's question>"` — use the official library name with proper punctuation (e.g., "Next.js" not "nextjs", "Customer.io" not "customerio", "Three.js" not "threejs")
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question)
3. Fetch docs: `pnpm dlx ctx7@latest docs <libraryId> "<user's question>"`
4. Answer using the fetched documentation

You MUST call `library` first to get a valid ID unless the user provides one directly in `/org/project` format. Use the user's full question as the query -- specific and detailed queries return better results than vague single words. Do not run more than 3 commands per question. Do not include sensitive information (API keys, passwords, credentials) in queries.

For version-specific docs, use `/org/project/version` from the `library` output (e.g., `/vercel/next.js/v14.3.0`).

If a command fails with a quota error, inform the user and suggest `pnpm dlx ctx7@latest login` or setting `CONTEXT7_API_KEY` env var for higher limits. Do not silently fall back to training data.
Run Context7 CLI requests outside Codex's default sandbox. If a Context7 CLI command fails with DNS or network errors such as ENOTFOUND, host resolution failures, or fetch failed, rerun it outside the sandbox instead of retrying inside the sandbox.
<!-- context7 -->
```

## 2. Third-Party Skills

> [!IMPORTANT]
> Only proceed with this section once **1. Upsert Agent Instructions** is fully done.

Read [`THIRD-PARTY.md`](./THIRD-PARTY.md) for a list of third-party skills, list them and suggest user that these are skills that they may want to install and use in their projects.