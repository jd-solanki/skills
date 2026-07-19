---
name: bruno
description: Create and manage Bruno API collections in the Bru Lang (.bru) format — adding a request, creating an environment, writing pre/post scripts, or scaffolding a collection. Triggers: "add Bruno request", "Bruno collection", "write a .bru", "Bru Lang".
disable-model-invocation: true
---

# Bruno

## Quick start — fetch docs first

Use **WebFetch** directly (context7 does not index Bruno docs).

This project uses the **Bru Lang** (`.bru`) format, NOT OpenCollection YAML. The
Bruno desktop app and VS Code extension fully support `.bru` and validate a
collection by the presence of a `bruno.json` at its root; OpenCollection's
`opencollection.yml` alone is not reliably recognised (see usebruno/bruno#7379).

| Topic | URL |
|---|---|
| Bru Lang overview | `https://docs.usebruno.com/bru-lang/overview` |
| Tag reference (request blocks) | `https://docs.usebruno.com/bru-lang/tag-reference` |
| Language design | `https://docs.usebruno.com/bru-lang/language` |
| Samples | `https://docs.usebruno.com/bru-lang/samples` |
| Variables | `https://docs.usebruno.com/variables/overview` |
| Auth | `https://docs.usebruno.com/auth/overview` |
| Secrets / .env | `https://docs.usebruno.com/secrets-management/dotenv-file` |
| Full doc index | `https://docs.usebruno.com/llms.txt` |

Read existing requests before writing new ones: `find api -name "*.bru" | head -10`

## Project layout

Group requests by resource under an `api/` directory whose tree **mirrors the
API's URL path**, so a URL maps predictably to a file. Name each request
`<verb>-<noun>.bru`.

`POST /api/webhook/orders` → `bruno/api/webhook/create-order.bru`

```
bruno/
├── bruno.json                       # Collection config (JSON) — the file the app validates
├── collection.bru                   # Collection-level settings (headers/auth/scripts/vars)
├── .env.example                     # var names only, no values (.env is gitignored)
├── environments/
│   └── <env>.bru
└── api/                             # mirrors the URL path under /api
    └── <resource>/
        ├── create-<noun>.bru
        ├── get-<noun>.bru
        └── delete-<noun>.bru
```

**`bruno.json`:**
```json
{
  "version": "1",
  "name": "<collection-name>",
  "type": "collection",
  "ignore": ["node_modules", ".git", ".env"]
}
```

**`collection.bru`** (collection-level settings; keep minimal unless there are
shared headers/auth/scripts):
```
meta {
  type: collection
}
```

## Request templates

**GET with path param** (see [AUTH.md](AUTH.md) for auth options):
```
meta {
  name: Get Deal by ID
  type: http
  seq: 1
}

get {
  url: {{baseUrl}}/crm/v3/objects/deals/:dealId
  auth: bearer
}

params:path {
  dealId: 60074085675
}

auth:bearer {
  token: {{hubspotToken}}
}
```

**POST with JSON body + API key + assertions**:
```
meta {
  name: Create Order
  type: http
  seq: 1
}

post {
  url: {{baseUrl}}/api/webhook/orders
  body: json
  auth: apikey
}

headers {
  Content-Type: application/json
}

auth:apikey {
  key: x-api-key
  value: {{apiKey}}
  placement: header
}

body:json {
  {
    "orderNumber": "W60523"
  }
}

assert {
  $res.status: 200
  $res.body.orderNumber: W60523
}
```

→ GraphQL requests: see [GRAPHQL.md](GRAPHQL.md)
→ All auth types: see [AUTH.md](AUTH.md)
→ Variable types & when to use: see [VARIABLES.md](VARIABLES.md)

## Body types

The method block declares `body: <type>`, and the body lives in its own
`body:<type> { ... }` block.

| Use case | method `body:` | Block |
|---|---|---|
| JSON payload | `json` | `body:json { <raw json> }` |
| URL-encoded form | `form-urlencoded` | `body:form-urlencoded { key: value }` |
| Multipart / file | `multipart-form` | `body:multipart-form { key: value }` / `file: @file(path/to/f) @contentType(type)` |
| Plain text | `text` | `body:text { ... }` |
| XML | `xml` | `body:xml { ... }` |

## Assertions & tests

Prefer the declarative `assert {}` block for status/body checks — no operator
means equals:
```
assert {
  $res.status: 200
  $res.body.ingested: true
  ~$res.body.note: skipped        # a leading ~ disables an assertion
}
```
For JavaScript assertions, use a `tests {}` block:
```
tests {
  function onResponse(request, response) {
    expect(response.status).to.equal(200);
  }
}
```

## Key rules

- **No `enabled:` field** — a leading `~` DISABLES a line (header, param, var,
  assert). Everything else is enabled.
- Auth is per-request: name the mode in the method block (`auth: bearer`) and add
  the matching `auth:<type> {}` block. For API keys use `auth:apikey { key /
  value / placement }`, or just put the key in `headers {}`.
- Environments are `.bru` files under `environments/`. Bruno reads them when the
  collection is OPENED; it does NOT hot-detect files written to disk while it is
  open — re-open the collection (or create the env via the UI) to pick up a new one.
- Cross-request values: `vars:post-response { TOKEN: $res.body.token }` sets a
  session-wide runtime var for later requests. Do NOT put it in the environment.
- File names: `<verb>-<noun>.bru` in kebab-case; `seq` = next number in the folder.
