# Microservice Architecture

## Recommended Directory Structure

Each microservice follows this layout:

```
<microservice>/
├── .vscode/                   # workspace settings
├── lambdas/
│   └── <lambda_name>/         # one directory per Lambda function
│       └── lambda_function.py
├── layers/
│   └── common_layer/          # layer root — packaged and attached to Lambdas
│       └── common_layer/      # Python package — defines import namespace (see below)
│           └── utils.py
├── scripts/                   # local dev and deployment helpers (not deployed)
├── template.yml               # main SAM/CloudFormation template for this microservice
└── templates/                 # reusable nested-stack templates referenced by template.yml
    └── some-nested-stack.yml
```

### Why `common_layer/common_layer`?

The outer `common_layer/` is the layer root — the directory that gets zipped and attached to Lambda functions. The inner `common_layer/` is the Python package that defines the import namespace.

This means imports are source-qualified:

```python
from common_layer.utils import resolve_product_category   # clear: from common_layer
from utils import resolve_product_category                 # ambiguous: which layer?
```

When a function uses multiple layers, namespace-qualified imports make it immediately clear which layer a symbol comes from — no collision risk between same-named modules across layers.

## Shared Microservice

A `shared/` microservice provides utilities and reusable SAM templates to all other microservices. No business logic lives here — only cross-cutting infrastructure.

```
shared/
├── layers/
│   └── shared_layer/          # utils available to every microservice
│       └── shared_layer/      # Python package (same namespace scoping as above)
│           ├── sqs/
│           │   └── types.py   # SQSEvent, SQSBatchResponse, SQSRecord, SQSBatchItemFailure
│           └── utils/
├── templates/                 # reusable SAM nested-stack templates
│   ├── lambda-cloudwatch-alarm.yml
│   └── queue-triggered-lambda.yml
└── scripts/
```

## Layer Hierarchy

| Layer | Scope | Use for |
|---|---|---|
| `shared_layer` (in `shared/`) | All microservices | Cross-cutting utilities: SQS types, encoders, string helpers |
| `common_layer` (per microservice) | One microservice | Business logic helpers shared within that service only |

Prefer `shared_layer` functions before adding to `common_layer`. Only promote to `shared_layer` when a utility is genuinely cross-microservice.

## Key Conventions

- `template.yml` (root) is the microservice's main SAM template. `templates/` holds reusable nested stacks (alarms, queue+lambda pairs) that `template.yml` references.
- `scripts/` holds local helpers (seed data, invoke shortcuts) — never deployed to AWS.
