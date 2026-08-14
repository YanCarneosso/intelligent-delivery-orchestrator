"""Reference non-dispatching logistics adapter Lambda."""

from __future__ import annotations

from typing import Any

from ..adapters import ReferenceDispatchGateway
from ..telemetry import metric_log


def handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    del context
    order = event["order"]
    result = ReferenceDispatchGateway().dispatch(order)
    metric_log(
        "dispatch_reference_succeeded",
        metrics={"DispatchesSucceeded": 1},
        order_id=order["order_id"],
        correlation_id=order["correlation_id"],
    )
    return result
