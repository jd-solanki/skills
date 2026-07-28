---
name: aws-architecture
description: AWS architecture patterns for webhooks, event routing, SQS/Lambda pipelines, microservices, and long-running server deployment with CI/CD. Use when designing webhook ingestion, adding SQS queues, wiring Lambda consumers, deciding between FIFO vs standard queues, reviewing event-driven architecture, structuring Python Lambda microservice directories, choosing between serverless and a long-running server, or deploying a containerized server to ECS Express Mode with push-to-deploy CI/CD.
---

# AWS Architecture

Architecture patterns for AWS — serverless and long-running.

- [Webhook Ingestion Architecture](webhooks/WEBHOOK_ARCHITECTURE.md) — Webhook pipeline: API GW → SQS FIFO → Routing Lambda → per-type SQS → Handler Lambda. Includes queue naming, payload routing, DLQ strategy, and reference diagrams.
- [Microservice Architecture](microservices/MICROSERVICE_ARCHITECTURE.md) — Recommended directory layout and layer sharing strategy for Python Lambda microservices.
- [Long-Running Server Deployment](deployment/DEPLOYMENT_ARCHITECTURE.md) — Deploy pipeline: push → test → image to ECR → migrate → ECS Express Mode (Fargate + ALB), with durable infrastructure in a stack the pipeline never runs. Includes why not serverless or EC2, disposable compute, keyless OIDC, reversible-before-irreversible ordering, and expand/contract migrations.
