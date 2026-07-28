"""Shared logging configuration for Lambda functions.

Public API is two names:

- `setup_logger()` — the standard CloudWatch format, called once at import.
- `log_prefix_scope()` — tag every log line in a block with a value
  (e.g. a customer or order number).

Typical use::

    from shared_layer.log import setup_logger, log_prefix_scope

    logger = setup_logger()

    def process_record(*, record):
        data = json.loads(record["body"])
        with log_prefix_scope("customer_number", data.get("Customer Number")):
            logger.info("Processing customer dashboard stat")
            # -> [INFO] [customer_number:C12345] Processing customer dashboard stat
"""

import contextlib
import contextvars
import logging
import sys
from collections.abc import Iterator
from typing import Literal

# The level names `logging.setLevel` accepts. Stdlib exposes these only as
# untyped int constants, so we name them here to get editor autocomplete.
type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Holds the active prefix. A ContextVar (not a plain global) keeps the value
# isolated per execution context, which is what `log_prefix_scope` relies on.
_log_prefix: contextvars.ContextVar[str] = contextvars.ContextVar(
    "log_prefix", default=""
)


class _PrefixFilter(logging.Filter):
    """Supplies the `%(prefix)s` field that the formatter renders."""

    def filter(self, record: logging.LogRecord) -> bool:
        prefix = _log_prefix.get()
        record.prefix = f"[{prefix}] " if prefix else ""
        return True


def setup_logger(*, level: LogLevel = "INFO") -> logging.Logger:
    """Configure and return the root logger with the shared format.

    Replaces the handler AWS pre-installs with a single stdout handler that
    renders an optional prefix (see `log_prefix_scope`). Safe to call at
    module import time.
    """
    logger = logging.getLogger()
    logger.handlers = []

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(prefix)s%(message)s"))
    handler.addFilter(_PrefixFilter())
    logger.addHandler(handler)

    logger.setLevel(level)
    return logger


@contextlib.contextmanager
def log_prefix_scope(label: str, value: str | None) -> Iterator[None]:
    """Prefix every log line emitted inside this block with `[label:value]`.

    `label` is rendered verbatim and should be snake_case (the caller's
    responsibility) so log lines read like `[customer_number:0004801]`. An
    empty/whitespace `value` yields no prefix at all. The previous prefix is
    restored on exit, so one record's prefix never leaks into the next when a
    handler loops over a batch.
    """
    clean = (value or "").strip()
    token = _log_prefix.set(f"{label}:{clean}" if clean else "")
    try:
        yield
    finally:
        _log_prefix.reset(token)
