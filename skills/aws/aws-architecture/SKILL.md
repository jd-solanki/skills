---
name: aws-architecture
description: AWS serverless architecture patterns for webhooks, event routing, SQS/Lambda pipelines, and microservices. Use when designing webhook ingestion, adding SQS queues, wiring Lambda consumers, deciding between FIFO vs standard queues, reviewing event-driven architecture, or structuring Python Lambda microservice directories.
---

# AWS Architecture

Serverless architecture patterns for AWS.

- [Webhook Ingestion Architecture](webhooks/WEBHOOK_ARCHITECTURE.md) — Webhook pipeline: API GW → SQS FIFO → Routing Lambda → per-type SQS → Handler Lambda. Includes queue naming, payload routing, DLQ strategy, and reference diagrams.
- [Microservice Architecture](microservices/MICROSERVICE_ARCHITECTURE.md) — Recommended directory layout and layer sharing strategy for Python Lambda microservices.
