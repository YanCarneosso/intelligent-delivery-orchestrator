"""Reference non-charging payment adapter Lambda."""

from __future__ import annotations

from typing import Any

from ..adapters import ReferencePaymentGateway
from ..telemetry import metric_log


def handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    del context
    order = event["order"]
    result = ReferencePaymentGateway().authorize(order)
    metric_log(
        "payment_reference_approved",
        metrics={"PaymentsApproved": 1},
        order_id=order["order_id"],
        correlation_id=order["correlation_id"],
    )
    return result
