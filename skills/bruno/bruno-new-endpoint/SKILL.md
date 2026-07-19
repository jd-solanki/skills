---
name: bruno-new-endpoint
description: Create a new Bruno API endpoint file from API documentation
disable-model-invocation: true
---

# New Endpoint

Infer the target API and operation from the conversation context. If not clear, ask: "Which API and endpoint should I create a Bruno request for?"

1. Use WebFetch (or context7) to fetch API documentation — extract endpoint path, HTTP method, required headers, request body schema, and auth type.
2. Find existing Bruno request `.bru` files in the project and read a few to understand local conventions (variable naming, auth style, `seq` numbering).
3. Place the request so the tree under `bruno/api/` **mirrors the endpoint's URL path**, grouped by resource, and name the file `<verb>-<noun>.bru`. For example `POST /api/webhook/orders` → `bruno/api/webhook/create-order.bru`.
4. Invoke the `/bruno` skill to create the `.bru` file. Include realistic placeholder values in the request body.
