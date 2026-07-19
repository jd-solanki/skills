# Webhook Ingestion Architecture

Always follow this flow for any new webhook source:

```
Source → API GW (direct SQS integration) → SQS FIFO (+ DLQ) → Routing Lambda → per-type SQS → Handler Lambda
```

**Key rules:**
- API GW writes **directly to SQS** — no ingest lambda. A lambda between API GW and the first queue adds a failure point and cold-start risk; if it crashes the payload is lost. Direct integration is atomic.
- API GW returns `200` immediately via `IntegrationResponses` — source never waits on processing
- First SQS queue is FIFO — preserves event order per `MessageGroupId`
- Attach a DLQ to every queue — failed messages are redriven without replaying the source
- Routing lambda fans out by **payload type** — one queue per webhook type in the microservice that owns it
- Each handler queue has one responsibility: process that webhook type end-to-end (including any downstream SQS sends to other microservice queues)

See [REFERENCE.md](REFERENCE.md) for mermaid diagrams, API GW → SQS integration snippet, FIFO key selection, DLQ config, and the microservices variant.

## Example Flow

```
Stripe → API GW /webhooks/stripe → Routing FIFO Queue → routing_lambda → target_queue_per_event_type
```

API GW uses `Type: AWS` integration targeting `sqs:path/{AccountId}/{QueueName}` with an IAM role. No lambda at the ingestion step.

## Queue Naming Convention

Handler queues are named by **source webhook + webhook type only** — never include the consumer service name:

```
<Source>Webhook<WebhookType>HandlerQueue
```

Examples for Stripe webhooks:
- `StripeWebhookPaymentIntentHandlerQueue`
- `StripeWebhookSubscriptionHandlerQueue`
- `StripeWebhookInvoiceHandlerQueue`

The routing lambda fans out by **(type × destination service)** — one queue per combination. Each queue lives inside the destination service's own stack, so the stack prefix provides service context. The queue logical name stays clean and type-scoped.

## Adding a New Payload Type

1. In each destination service stack, create a queue named `<Source>Webhook<Type>HandlerQueue` (FIFO if ordering matters) + DLQ
2. Export the queue URL from each service stack and pass it as an env var to the routing lambda
3. Add a route branch in the routing lambda that sends to all destination queues for that type
4. Create a handler lambda in each service stack, subscribed to its queue — one responsibility per handler
5. Grant the routing lambda `sqs:SendMessage` on each new queue

## Queue Selection

| Scenario | Queue type |
|---|---|
| Order matters (subscription lifecycle, inventory) | FIFO |
| High-throughput, order irrelevant | Standard |
| Cross-microservice fan-out | FIFO per microservice |
