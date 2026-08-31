---
name: review-roadmap
description: Review a roadmap through three lenses — feasibility, limitations, and improvements — and report what each one found.
argument-hint: "[roadmap file path]"
disable-model-invocation: true
---

Dispatch three subagents in one message, one per lens. Give each the roadmap path
and its lens, and have it use `/research` when a claim needs an outside source.

| Lens | Looks for |
| --- | --- |
| Feasibility | Can this be built as written? Holes, unstated assumptions, steps resting on something that does not exist yet. |
| Limitations | What the design cannot do. Bottlenecks, ceilings, costs it defers to later. |
| Improvements | A better shape. Simpler paths, code already in the repo to reuse, tools/services to utilize, steps to drop. |

Every step of the roadmap gets a verdict from every lens.

Report three sections, one per lens, in that order. Each finding names the roadmap
step it lands on.
