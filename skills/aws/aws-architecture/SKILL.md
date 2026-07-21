---
name: aws-architecture
description: AWS architecture patterns for webhooks, event routing, SQS/Lambda pipelines, microservices, and long-running server deployment with CI/CD. Use when designing webhook ingestion, adding SQS queues, wiring Lambda consumers, deciding between FIFO vs standard queues, reviewing event-driven architecture, structuring Python Lambda microservice directories, or deploying a long-running server to EC2 with push-to-deploy CI/CD (GitHub Actions, SSM, UserData/bootstrap, migrations, rollback).
---

# AWS Architecture

Architecture patterns for AWS — serverless and long-running.

- [Webhook Ingestion Architecture](webhooks/WEBHOOK_ARCHITECTURE.md) — Webhook pipeline: API GW → SQS FIFO → Routing Lambda → per-type SQS → Handler Lambda. Includes queue naming, payload routing, DLQ strategy, and reference diagrams.
- [Microservice Architecture](microservices/MICROSERVICE_ARCHITECTURE.md) — Recommended directory layout and layer sharing strategy for Python Lambda microservices.
- [Long-Running Server Deployment](deployment/DEPLOYMENT_ARCHITECTURE.md) — Long-running server on EC2 (any runtime) with push-to-deploy CI/CD: two lifecycles (provision vs deploy), disposable box / durable data, thin-loader UserData over idempotent bootstrap, reversible-before-irreversible pipeline order, keyless OIDC, expand/contract migration rollback, and the GitHub Actions workflows (app-cd, infra-cd, rollback, reconfigure-box).
