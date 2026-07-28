import decimal
import json
from datetime import datetime
from typing import Any


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal values from DynamoDB.

    Note: This preserves numeric types (int or float) instead of converting to string
    """

    def default(self, o: Any) -> Any:  # noqa: ANN401
        if isinstance(o, decimal.Decimal):
            # Convert Decimal to int if it's a whole number, otherwise float
            return int(o) if o % 1 == 0 else float(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
