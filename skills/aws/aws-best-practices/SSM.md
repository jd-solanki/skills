# SSM Parameter Store — Best Practices

## Rule 1: Never create SSM parameters via CloudFormation / SAM

`AWS::SSM::Parameter` in a SAM/CloudFormation template is an anti-pattern for any value you'll later populate with a real value.

**Why it bites you:**

CloudFormation has no `ignore_changes` equivalent. If you create a parameter with a placeholder and then set the real value out-of-band, the next `sam deploy` sees the template still says `"PLACEHOLDER"` and resets it — clobbering your real secret.

Additional hard blocker: CloudFormation only supports `String` and `StringList` parameter types. You **cannot** create a `SecureString` via CloudFormation. For anything sensitive, the in-template approach is not even available without a custom resource.

**What the template should do instead:**

Grant `ssm:GetParameter` permission and pass the parameter *name* (not value) as an env var:

```yaml
# IAM — grant read access
- Effect: Allow
  Action: ssm:GetParameter
  Resource:
    - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/myapp/prod/api-credentials"

# Lambda env var — name only, not the value
Environment:
  Variables:
    API_CREDENTIALS_PARAMETER_NAME: /myapp/prod/api-credentials
```

The parameter itself must exist before first deploy, created by a bootstrap step (see Rule 3).

---

## Rule 2: Prefer runtime fetching over deploy-time resolution in Lambda

Two tempting but problematic patterns:

```yaml
# Pattern A — SSM parameter type (deploy-time)
Parameters:
  DbHost:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /myapp/prod/db-host

# Pattern B — dynamic reference (deploy-time)
Environment:
  Variables:
    DB_PASSWORD: '{{resolve:ssm-secure:/myapp/prod/db-password}}'
```

Both bake the value into the Lambda config **at deploy time**. If the secret rotates (API key, DB password, third-party token), the running function holds the stale value until you redeploy.

**Lambda-specific nuance:** Lambda caches environment variables for the lifetime of the execution environment (minutes to hours). A rotated secret won't reach your function until a cold start after redeploy — you may not even notice until failures start.

**Prefer runtime fetching instead:**

```python
import boto3
import json
import os

ssm = boto3.client("ssm")

def get_credentials():
    response = ssm.get_parameter(
        Name=os.environ["API_CREDENTIALS_PARAMETER_NAME"],
        WithDecryption=True
    )
    return json.loads(response["Parameter"]["Value"])
```

For high-frequency invocations, cache the value in a module-level variable with a TTL rather than fetching on every call. The **AWS Parameters and Secrets Lambda Extension** handles this automatically (caches and refreshes without a redeploy) and is the preferred approach for production workloads.

**When deploy-time resolution is acceptable:** non-sensitive, environment-stable config (region names, feature flags, stack names) that never rotates and doesn't need to change without a redeploy.

---

## Rule 3: Scalable pattern — separate parameter lifecycle from the app stack

Config values and secrets change on a different cadence than your application code. Coupling them into the same stack ties two independent concerns together.

**The scalable approach:**

```
Bootstrap step (runs once, before first sam deploy)
  └── aws ssm put-parameter --name /myapp/prod/api-credentials \
        --value '{"client_id":"...","client_secret":"..."}' \
        --type SecureString

App stack (sam deploy — every release)
  └── assumes parameter already exists, only reads it at runtime
```

Options for owning the parameter's lifecycle:

| Owner | When to use |
|---|---|
| CI pre-deploy script (`aws ssm put-parameter --overwrite`) | Simple; good for per-environment secrets managed in CI |
| Separate bootstrap/foundation stack | Parameters shared across multiple app stacks; clearer dependency |
| Secrets Manager (with SSM reference) | Secrets that need rotation policies or cross-account access |
| Manual + documented runbook | One-time credentials that never rotate; lowest overhead |

**Chicken-and-egg on first deploy:** document required parameters in a `BOOTSTRAP.md` or in the SAM template's `Parameters` section description. The IAM `ssm:GetParameter` deny will fail loudly at Lambda invocation time if the parameter is missing — this is acceptable and surfaceable via CloudWatch alarms.

---

## Decision tree

```
Is it a secret / credential?
├── Yes → SecureString, created outside the stack, fetched at runtime
│         Consider Secrets Manager if rotation is needed
└── No → Is it environment-stable config that never rotates?
          ├── Yes → deploy-time resolution is fine (SSM parameter type or {{resolve:}})
          └── No (rotates or changes independently) → runtime fetch, module-level cache
```
