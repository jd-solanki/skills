# Lambda Best Practices

## SQS Consumer — Handler Structure

**Imports:**

```python
import json
import logging
import sys
from typing import Any

# Assuming shared_layer is a Lambda Layer containing shared types and utilities
from shared_layer.sqs.types import SQSBatchItemFailure, SQSBatchResponse, SQSEvent
from shared_layer.utils.encoders import DecimalEncoder
from shared_layer.utils.string import decode_json_strings
```

**Logger setup — do this once at module level:**

```python
logger = logging.getLogger()
logger.handlers = []  # prevent duplicate log lines from default handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Handler signature — always type with shared layer types:**

```python
def lambda_handler(event: SQSEvent, context: Any) -> SQSBatchResponse:
```

## Event Logging

Log the incoming event at the top of every Lambda handler to enable CloudWatch debugging:

```python
logger.info(
    json.dumps(
        {"message": "Event", "event": decode_json_strings(event)},
        cls=DecimalEncoder,
    )
)
```

- `decode_json_strings` makes nested JSON strings readable in CloudWatch logs — SQS `body` fields often contain JSON-encoded strings that show up as escaped noise without it
- `DecimalEncoder` safely serializes DynamoDB `Decimal` values

Add `decode_json_strings` to your `shared_layer/utils/string.py`:

```python
import json
from typing import Any


def decode_json_strings(obj: Any) -> Any:
    if isinstance(obj, str):
        try:
            return decode_json_strings(json.loads(obj))
        except (ValueError, TypeError):
            return obj
    elif isinstance(obj, dict):
        return {k: decode_json_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decode_json_strings(item) for item in obj]
    return obj
```

## batchItemFailures — Always Implement

Return a `SQSBatchResponse` with partial failures so only failed messages are retried — never return `None` or raise from the handler:

```python
def lambda_handler(event: SQSEvent, context: Any) -> SQSBatchResponse:
    logger.info(
        json.dumps(
            {"message": "Event", "event": decode_json_strings(event)},
            cls=DecimalEncoder,
        )
    )
    failed_items: list[SQSBatchItemFailure] = []
    for record in event.get("Records", []):
        message_id = record["messageId"]
        try:
            body = json.loads(record["body"])
            process_record(body)
        except Exception:
            logger.exception("Failed to process messageId=%s", message_id)
            failed_items.append(SQSBatchItemFailure(itemIdentifier=message_id))
    return SQSBatchResponse(batchItemFailures=failed_items)
```

## process_record() — Separate Domain Logic

Extract domain logic into a dedicated `process_record()` function. The handler loop owns SQS mechanics (parsing, error capture, retry signalling); `process_record()` owns the domain logic and knows nothing about SQS:

```python
def process_record(record: dict) -> None:
    # domain logic only — no SQS-specific code here
    order_id = record["orderId"]
    ...
```

This keeps the two concerns independently testable.

## CloudWatch Alarm

Every Lambda must have a CloudWatch alarm that fires on errors. Use the reusable SAM nested-stack template in your shared templates directory:

```yaml
MyFunctionErrorAlarm:
  Type: AWS::Serverless::Application
  Properties:
    Location: ../../shared/templates/lambda-cloudwatch-alarm.yml
    Parameters:
      FunctionName: !Ref MyFunction
```

The template creates an `Errors >= 1` alarm over a 1-minute evaluation period.

## Lambda / SQS Naming Convention

When a Lambda is the sole consumer of an SQS queue, give them a shared PascalCase base name:

```
<Feature>Function            — the Lambda
<Feature>Queue               — its SQS queue
<Feature>DLQ                 — the dead-letter queue
<Feature>FunctionErrorAlarm  — the CloudWatch alarm
```

**Example** — Stripe order webhook handler:

- `StripeOrderWebhookFunction`
- `StripeOrderWebhookQueue`
- `StripeOrderWebhookDLQ`
- `StripeOrderWebhookFunctionErrorAlarm`

The shared base makes the Lambda ↔ queue relationship immediately visible in the template without cross-referencing resource names.
