# SQS Best Practices

## Consumer Types — Use TypedDicts

Always type SQS Lambda handlers with TypedDicts. Never pass raw `dict` through the handler boundary — typed records catch missing keys early and make handler signatures self-documenting.

Define the following types in your shared layer so every SQS consumer uses the same definitions:

```python
from typing import TypedDict


class SQSRecord(TypedDict):
    messageId: str
    body: str
    receiptHandle: str


class SQSEvent(TypedDict):
    Records: list[SQSRecord]


class SQSBatchItemFailure(TypedDict):
    itemIdentifier: str


class SQSBatchResponse(TypedDict):
    batchItemFailures: list[SQSBatchItemFailure]
```

| Type | Use |
|---|---|
| `SQSEvent` | `event` parameter of the Lambda handler |
| `SQSRecord` | Individual record from `event["Records"]` |
| `SQSBatchItemFailure` | One failed message identifier in a partial batch response |
| `SQSBatchResponse` | Return type of the handler — contains `batchItemFailures` list |

See [LAMBDA.md](LAMBDA.md) for the full handler pattern including `batchItemFailures` and `process_record()`.

**TIP**: If you are following microservice architecture, place these types in the shared layer of your `shared/` microservice so all other microservices can import them. See [MICROSERVICE_ARCHITECTURE.md](MICROSERVICE_ARCHITECTURE.md) for details.
