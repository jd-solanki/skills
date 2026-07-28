# Lambda Best Practices

## SQS Consumer — Handler Structure

**Imports:**

```python
import json
from typing import Any

# Assuming shared_layer is a Lambda Layer containing shared types and utilities
from shared_layer.log import log_prefix_scope, setup_logger
from shared_layer.sqs.types import SQSBatchItemFailure, SQSBatchResponse, SQSEvent
from shared_layer.utils.encoders import DecimalEncoder
from shared_layer.utils.string import decode_json_strings
```

**Handler signature — always type with shared layer types:**

```python
def lambda_handler(event: SQSEvent, context: Any) -> SQSBatchResponse:
```

## Logging — `setup_logger()`

Call `setup_logger()` once at module level. Never hand-roll handler wiring in a Lambda — the setup lives in one shared module so a format change is a one-place edit:

```python
logger = setup_logger()  # module level, above the handler
```

Copy [shared_layer/log.py](shared_layer/log.py) into your shared layer. It replaces the handler AWS pre-installs (which duplicates every line) with a single stdout handler formatted `[LEVEL] message`, and takes an optional `level="DEBUG"`.

### `log_prefix_scope()` — tag a block of lines

A batch handler interleaves lines from many records, so a bare message can't be traced back to the record that emitted it. Wrap the per-record work in `log_prefix_scope(label, value)` and every line inside carries that identifier:

```python
def process_record(record: Record) -> None:
    with log_prefix_scope("sku", record.get("sku")):
        logger.info("Processing product")
        # -> [INFO] [sku:ABC-123] Processing product
```

`label` is rendered verbatim — keep it snake_case. An empty or missing `value` yields no prefix, so `.get()` on an absent key degrades to an unprefixed line rather than raising. The scope restores the previous prefix on exit, so one record's identifier never leaks into the next iteration.

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
- `DecimalEncoder` safely serializes any `Decimal` values

Copy both into your shared layer: [shared_layer/utils/string.py](shared_layer/utils/string.py) and [shared_layer/utils/encoders.py](shared_layer/utils/encoders.py).

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
from typing import TypedDict

# You don't necessarily need to create `Record` type, it's just for example and mostly you'll reuse existing type for `record` parameter
class Record(TypedDict): ...

def process_record(record: Record) -> None:
    # domain logic only — no SQS-specific code here
    order_id = record["orderId"]
    ...
```

This keeps the two concerns independently testable.

## CloudWatch Alarm

Every Lambda must have a CloudWatch alarm that fires on errors. Use the reusable SAM nested-stack template in your shared templates directory — copy [templates/lambda-cloudwatch-alarm.yml](templates/lambda-cloudwatch-alarm.yml) there if the project doesn't have one yet:

```yaml
MyFunctionErrorAlarm:
  Type: AWS::Serverless::Application
  Properties:
    Location: ../../shared/templates/lambda-cloudwatch-alarm.yml
    Parameters:
      FunctionName: !Ref MyFunction
      AlarmSNSTopicArn: !Ref ErrorAlarmSNSTopicArn
```

The template creates an `Errors >= 1` alarm over a single 10-minute evaluation period.

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
