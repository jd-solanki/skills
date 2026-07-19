---
name: aws-best-practices
description: AWS service-specific best practices and configuration rules. Use when making decisions about SSM Parameter Store, SQS consumer types, Lambda function structure, or SAM template conventions.
---

# AWS Best Practices

Service-specific configuration and lifecycle rules. Each reference covers one AWS service in depth.

- [SSM.md](SSM.md) — Parameter Store: when to create parameters, runtime vs deploy-time fetching, the bootstrap pattern, and the decision tree for secrets vs config
- [SQS.md](SQS.md) — SQS consumer types, using shared layer TypedDict types in Lambda handlers
- [LAMBDA.md](LAMBDA.md) — Lambda handler structure: SQS consumption pattern, `batchItemFailures`, `process_record()` separation, event logging, CloudWatch alarms, and Lambda/SQS naming
- [SAM.md](SAM.md) — SAM template conventions: no explicit physical resource names (auto-generate to keep deploys safe), resource grouping by topic, `Fn::ToJsonString`, `LAMBDA_ENV_VARS` pattern
