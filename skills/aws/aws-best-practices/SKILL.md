---
name: aws-best-practices
description: AWS service-specific best practices and configuration rules. Use when making decisions about RDS environment isolation, SSM Parameter Store, SQS consumer types, Lambda function structure, or SAM template conventions.
---

# AWS Best Practices

Service-specific configuration and lifecycle rules. Each reference covers one AWS service in depth.

- [RDS.md](RDS.md) — RDS/Aurora: one host per environment, why prod must not share an instance with staging, staging fidelity (engine flavour and version), and sizing staging down instead of sharing
- [SSM.md](SSM.md) — Parameter Store: when to create parameters, runtime vs deploy-time fetching, the bootstrap pattern, and the decision tree for secrets vs config
- [SQS.md](SQS.md) — SQS consumer types, using shared layer TypedDict types in Lambda handlers
- [LAMBDA.md](LAMBDA.md) — Lambda handler structure: SQS consumption pattern, `batchItemFailures`, `process_record()` separation, `setup_logger()` / `log_prefix_scope()`, event logging, CloudWatch alarms, and Lambda/SQS naming
- [SAM.md](SAM.md) — SAM template conventions: no explicit physical resource names (auto-generate to keep deploys safe), resource grouping by topic, `Fn::ToJsonString`, `LAMBDA_ENV_VARS` pattern
- [templates/](templates/) — copy-paste nested-stack templates referenced above: `lambda-cloudwatch-alarm.yml`, `dlq.yml`, `queue-triggered-lambda.yml`
- [shared_layer/](shared_layer/) — copy-paste shared-layer modules referenced above: `log.py`, `utils/string.py`, `utils/encoders.py`
