# SAM Template Best Practices

## Prefer SAM Shorthand Over Raw CloudFormation

Use `AWS::Serverless::Function`, `AWS::Serverless::Api`, etc. instead of their raw CloudFormation equivalents. SAM shorthand handles event source mappings, IAM role generation, and deployment preferences in a fraction of the YAML.

```yaml
# Prefer this
MyFunction:
  Type: AWS::Serverless::Function

# Over this
MyFunction:
  Type: AWS::Lambda::Function
```

Only drop to raw CloudFormation when SAM shorthand doesn't expose the property you need.

## Don't Set Explicit Physical Resource Names

Let CloudFormation auto-generate physical names. Do **not** set `QueueName`, `FunctionName`, `TableName`, `BucketName`, `RoleName`, `TopicName`, etc. unless an external system genuinely requires a fixed, known name (and even then, prefer exporting the generated name as a stack Output).

**Why — explicit names break updates that require replacement.** When you change an immutable property of a named resource, CloudFormation must replace it. Its update strategy is *create-the-new-one-before-deleting-the-old-one*, so for a brief window two resources would need the same physical name. Names must be unique, so the create fails with `already exists` and the whole stack update rolls back:

```yaml
# Bad — a fixed name turns any future replacement into a failed deploy
MyQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: my-service-orders   # collides with itself during replace

# Good — CloudFormation generates a unique name; replacements are seamless
MyQueue:
  Type: AWS::SQS::Queue
  Properties: {}                   # reference elsewhere via !Ref / !GetAtt
```

Auto-generated names are also what make **logical-ID renames** safe: renaming a resource (or splitting one into several) deletes the old logical ID and creates new ones — with auto-naming there is no collision, so the deploy succeeds.

**Corollary — don't add naming parameters that nothing consumes.** A `StackName`/`NamePrefix` parameter threaded into a nested template but never referenced by any resource is dead config: it implies control over naming that doesn't exist, and tempts the next person to "fix" it by adding an explicit name. If a parameter doesn't feed a real property, delete it. Distinctness between multiple instances of a reusable nested template already comes from each being its own nested stack — not from a name parameter.

## Resource Grouping — Group by Topic, Not by Type

Do not scatter related resources across type-based sections. Group all resources for a feature under a single VSCode region block, placed at the **end** of the `Resources:` map.

VSCode region comments collapse in the editor — you can fold an entire feature's resources into one line and scan the template quickly without scrolling through dozens of unrelated resources:

```yaml
Resources:
  # ... existing resources above ...

  # region Stripe Order Webhook
  StripeOrderWebhookDLQ:
    Type: AWS::Serverless::Application
    ...
  StripeOrderWebhookQueue:
    Type: AWS::SQS::Queue
    ...
  StripeOrderWebhookFunction:
    Type: AWS::Serverless::Function
    ...
  StripeOrderWebhookFunctionErrorAlarm:
    Type: AWS::Serverless::Application
    ...
  # endregion
```

Each new feature section goes at the end of `Resources:` — additions are easy to find and diff.

## Fn::ToJsonString — Readable JSON in SAM Templates

When a SAM resource property or template parameter expects a JSON string, avoid manually encoding it — it's fragile and unreadable:

```yaml
# Hard to read, breaks on any whitespace or quoting error
SomeProperty: !Sub '{"QueueUrl": "${MyQueue}", "Region": "${AWS::Region}"}'
```

Use `Fn::ToJsonString` instead. Write the value as plain YAML; SAM serializes it to a valid JSON string at deploy time:

```yaml
# Clean, readable, fully referable
SomeProperty: !ToJsonString
  QueueUrl: !Ref MyQueue
  Region: !Ref AWS::Region
```

`Fn::ToJsonString` is provided by the `AWS::LanguageExtensions` transform. Declare it **before** `AWS::Serverless-2016-10-31` in the `Transform` list — order matters:

```yaml
Transform:
  - AWS::LanguageExtensions
  - AWS::Serverless-2016-10-31
```

## Shared Templates

Reusable nested-stack templates live in a shared templates directory. Always check there before writing a new resource inline.

| Template | Use |
|---|---|
| `lambda-cloudwatch-alarm.yml` | CloudWatch `Errors >= 1` alarm for a Lambda |
| `queue-triggered-lambda.yml` | Full FIFO SQS + DLQ + Lambda + alarm stack |

### Passing Lambda Env Vars to Generic Templates

Generic nested-stack templates (like `queue-triggered-lambda.yml`) are intentionally parameter-free regarding Lambda env vars — they shouldn't grow a new parameter for every variable each Lambda needs. Instead, pass all env vars as a single JSON blob using `Fn::ToJsonString`.

In the parent template:

```yaml
MyStack:
  Type: AWS::Serverless::Application
  Properties:
    Location: ../../shared/templates/queue-triggered-lambda.yml
    Parameters:
      LambdaEnvironmentVariables: !ToJsonString
        MY_QUEUE_URL: !Ref SomeQueue
        SOME_CONFIG: !Ref SomeParam
```

The nested template forwards the blob as a single env var without inspecting it:

```yaml
# inside queue-triggered-lambda.yml
Environment:
  Variables:
    LAMBDA_ENV_VARS: !Ref LambdaEnvironmentVariables
```

In the Lambda, unpack with a helper that falls back to named env vars:

```python
_env_vars = json.loads(os.environ.get("LAMBDA_ENV_VARS", "{}"))

def _env(key: str) -> str:
    return _env_vars.get(key) or os.environ[key]
```

This keeps the nested template generic: one `LambdaEnvironmentVariables` parameter covers every Lambda regardless of how many env vars it needs.
