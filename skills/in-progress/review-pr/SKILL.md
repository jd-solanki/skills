---
name: review-pr
description: Review PR
argument-hint: "[#22]"
disable-model-invocation: true
---

Review PR using review-implementer subagents max 3 round, both subagents stays separate. Recreate subagent after each round to get fresh context for reviewer subagent.

- Prioritize correctness over style. Look for bugs, edge cases, regressions, race conditions, security, performance, accessibility, API/design issues, maintainability, tests, backward compatibility, missing validation, etc. Challenge assumptions. Only report real issues with evidence, severity, and a suggested fix. Ignore trivial formatting/nitpicks.

- Use following skills for review subagent's 2 further nested subagents for parallel review via skills, Spawn one subagent for correctness using `/code-review` & `/coding` skills and other for simplicity using `/ponytail-review` & `/simplify` skills
- Use `/ponytail ultra` skill for implementer subagents