"""Lambda handler for the pre-inference validation boundary."""

from __future__ import annotations

from typing import Any

from ..telemetry import metric_log
from ..validation import prepare_order


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context
    prepared = prepare_order(event)
    metric_log(
        "order_validated",
        metrics={"OrdersValidated": 1},
        order_id=prepared["order"]["order_id"],
        correlation_id=prepared["order"]["correlation_id"],
    )
    return prepared
