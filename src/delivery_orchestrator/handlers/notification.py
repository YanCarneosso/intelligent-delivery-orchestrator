"""Reference non-sending notification adapter Lambda."""

from __future__ import annotations

from typing import Any

from ..adapters import ReferenceNotificationGateway
from ..telemetry import metric_log


def handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    del context
    order = event["order"]
    result = ReferenceNotificationGateway().notify(order, event["analysis"])
    metric_log(
        "notification_reference_succeeded",
        metrics={"NotificationsSucceeded": 1},
        order_id=order["order_id"],
        correlation_id=order["correlation_id"],
    )
    return result
