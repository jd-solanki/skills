# Bruno Auth Reference

## How secrets flow: .env → environment → request

**Step 1 — `.env`** (gitignored, never committed) at the collection root:
```
HUBSPOT_TOKEN=pat-xxx-yyy
DDI_WEBHOOK_TOKEN=s3cr3t
```

**Step 2 — `environments/<env>.bru`** — map process env to Bruno variables:
```
vars {
  baseUrl: https://api.example.com
  apiToken: {{process.env.HUBSPOT_TOKEN}}
  ddiWebhookToken: {{process.env.DDI_WEBHOOK_TOKEN}}
}
```
> The values are `{{process.env.*}}` references, so the file holds no secret — the
> real value stays in `.env`. A leading `~` disables a variable.

**Step 3 — individual request** — reference the variable:
```
auth:bearer {
  token: {{apiToken}}
}
```

---

## Auth types

Name the mode in the method block (`auth: bearer`), then add the matching block.

### Bearer Token
```
auth:bearer {
  token: {{apiToken}}
}
```

### API Key (header or query)
```
auth:apikey {
  key: x-api-key
  value: {{apiKey}}
  placement: header
}
```
> `placement: header` or `query`. If your Bruno version lacks `auth:apikey`, put
> the key straight into `headers { x-api-key: {{apiKey}} }` — the server only ever
> sees a header either way.

### Basic Auth
```
auth:basic {
  username: {{clientId}}
  password: {{clientSecret}}
}
```
> **Important:** with basic auth + a JSON body Bruno does not auto-inject
> `Content-Type`. Add it explicitly in `headers { Content-Type: application/json }`.

### Inherit (from collection or folder)
Set the method block's `auth: inherit` — inherits `collection.bru`'s auth.

### No auth
Set the method block's `auth: none` and omit the auth block.

### OAuth 2.0, AWS SigV4, Digest, WSSE, NTLM
Supported as `auth:oauth2`, `auth:awsv4`, `auth:digest`, `auth:wsse`, `auth:ntlm`
blocks. Fetch `https://docs.usebruno.com/auth/overview` for current keys, or
configure once via the Bruno UI and read back the generated `.bru`.

---

## Getting a token and sharing it across requests

Capture a value into a session-wide runtime variable with `vars:post-response`:
```
vars:post-response {
  ACCESS_TOKEN: $res.body.access_token
}
```
Then reference `{{ACCESS_TOKEN}}` in any later request:
```
auth:bearer {
  token: {{ACCESS_TOKEN}}
}
```
> Do NOT add `ACCESS_TOKEN` to `environments/<env>.bru`. If it references
> `{{process.env.*}}` there, the runtime capture cannot override it and the token
> will never update.

For scripted capture instead of the declarative block, use a post-response
script: `script:post-response { bru.setVar("ACCESS_TOKEN", res.body.access_token); }`
