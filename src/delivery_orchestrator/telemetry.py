"""Structured and Embedded Metric Format logging without PII."""

from __future__ import annotations

import json
import time
from typing import Any


def metric_log(
    event: str,
    *,
    metrics: dict[str, float] | None = None,
    dimensions: dict[str, str] | None = None,
    **fields: Any,
) -> None:
    """Emit CloudWatch EMF JSON; callers must not include notes or address fields."""
    metrics = metrics or {}
    dimensions = dimensions or {"Service": "DeliveryOrchestrator"}
    payload: dict[str, Any] = {
        "event": event,
        **dimensions,
        **fields,
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "IntelligentDeliveryOrchestrator",
                    "Dimensions": [list(dimensions)],
                    "Metrics": [{"Name": name, "Unit": "Count"} for name in metrics],
                }
            ],
        },
        **metrics,
    }
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True))
