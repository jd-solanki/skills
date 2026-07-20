# Bruno GraphQL Reference

## GraphQL request template

```
meta {
  name: Filter Products by SKUs
  type: graphql
  seq: 1
}

post {
  url: {{baseUrl}}/shop-api
  body: graphql
  auth: bearer
}

auth:bearer {
  token: {{apiToken}}
}

body:graphql {
  query GetProductsBySkus($skus: [String!]!) {
    customProductVariants(options: { filter: { sku: { in: $skus } } }) {
      items {
        sku
        featuredAsset {
          preview
        }
      }
    }
  }
}

body:graphql:vars {
  {
    "skus": ["HAR326-4", "GPW-6"]
  }
}
```

## Key rules

- `meta.type: graphql` — not `http`
- The method block declares `body: graphql` (usually `post {}`)
- The query goes in a `body:graphql { ... }` block; the variables go in a separate
  `body:graphql:vars { ... }` block as a JSON object — never inline them in the query
- `body:graphql:vars` must be valid JSON
- Auth is the same as HTTP — `auth: bearer` in the method block plus an
  `auth:bearer {}` block; `auth: inherit` also works
- No separate `body:<type>` for the payload — the `graphql` body type covers both
  the query and its variables blocks
