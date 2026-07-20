# Bruno Variables Reference

## All types & precedence

Highest priority wins when the same name exists in multiple scopes.

| Priority | Type | Scope | Set via | Persists? |
|---|---|---|---|---|
| 1 (highest) | **Runtime** | Session-wide | `bru.setVar(k, v)` in a script, or a `vars:post-response` block | No — lost on restart |
| 2 | **Request** | Single request | `vars:pre-request` block in the request `.bru` | In the `.bru` |
| 3 | **Folder** | Folder | Bruno UI / `folder.bru` | In the folder file |
| 4 | **Environment** | Active environment | `environments/<env>.bru` | In the `.bru` |
| 5 | **Collection** | Collection-wide | `collection.bru` | In `collection.bru` |
| 6 (lowest) | **Global** | Workspace | `bru.setGlobalEnvVar(k, v)` | Yes — app storage |
| — | **Process Env** | OS-level | `.env` file via `{{process.env.VAR}}` | Read-only |
| — | **Prompt** | One request run | `{{?Prompt label}}` syntax | Never stored |

## When to use each

**Runtime** — dynamically obtained values like OAuth tokens. Available to all
requests in the same session:
```
vars:post-response {
  ACCESS_TOKEN: $res.body.access_token
}
```
Then reference as `{{ACCESS_TOKEN}}` in any request.

**Environment** — static per-environment config (base URLs, feature flags, API
versions), in `environments/<env>.bru`:
```
vars {
  baseUrl: https://api.prod.example.com
}
```

**Process Env** — sensitive credentials loaded from `.env` (gitignored, never
committed). Reference them from an environment `.bru`:
```
vars {
  apiToken: {{process.env.API_TOKEN}}
}
```
```ini
# .env
API_TOKEN=pat-abc-123
```
Ship `.env.example` with var names and placeholder values so teammates know what
to set.

**Prompt** — one-off interactive input, never stored anywhere: `{{?Enter order ID}}`

**Collection / Folder** — shared defaults in `collection.bru` / `folder.bru`; low
priority so requests can override them.

**Global** — workspace-wide defaults. Avoid — prefer environment variables which
are scoped and version-controlled.

## Rules

- **A leading `~` disables a variable** (`~token: secret`). There is no `enabled:`
  field and no `type:` field — a var is just `name: value`.
- Keep real secrets in `.env` and reference them with `{{process.env.VAR}}`, so no
  secret value is ever written into a committed `.bru`.
- Do NOT put dynamically-obtained tokens in `environments/<env>.bru`. A runtime
  capture **cannot override** a `process.env.*` binding — the token will never
  update after `get-token` runs.
- `.env` is gitignored; always ship `.env.example` alongside it.
- Process env vars are **read-only** — use runtime or env vars for writable state.

## bru JS API

```javascript
// Runtime — session-wide, lost on Bruno restart
bru.setVar("key", value)
bru.getVar("key")
bru.hasVar("key")
bru.deleteVar("key")

// Environment — active environment file
// ⚠️ v4: setEnvVar/deleteEnvVar persist to environments/<env>.bru BY DEFAULT
// (pre-v4 they were in-memory unless you passed { persist: true }).
bru.setEnvVar("key", value)                    // writes back to environments/<env>.bru
bru.deleteEnvVar("key")                         // removes from environments/<env>.bru
bru.getEnvVar("key")
bru.hasEnvVar("key")

// Global — workspace-wide, persisted in app storage
bru.setGlobalEnvVar("key", value)
bru.getGlobalEnvVar("key")

// Read-only OS environment
bru.getProcessEnv("KEY")
```

## v4 migration: do not persist secrets via env vars

As of Bruno v4, `setEnvVar()`, `deleteEnvVar()`, and `setGlobalEnvVar()` write
their changes to disk by default — so a token written through them lands in
`environments/<env>.bru` and can be committed to git.

- For **dynamically obtained secrets** (OAuth tokens, API keys): use `bru.setVar`
  / `bru.deleteVar` (runtime scope) — these stay in memory and are never written
  to disk. This is already the pattern in [SKILL.md](SKILL.md) / [AUTH.md](AUTH.md).
- Only use `setEnvVar`/`setGlobalEnvVar` for non-sensitive values you actually
  want saved across sessions.
