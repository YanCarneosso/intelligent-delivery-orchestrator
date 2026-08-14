"""Pre-inference input validation boundary."""

from __future__ import annotations

import uuid
from typing import Any

from .cognitive import build_bedrock_request
from .contracts import validate_order
from .safety import detect_safety_signals


def prepare_order(raw_order: Any) -> dict[str, Any]:
    """Validate, correlate, detect safety signals, and prepare a minimized prompt."""
    order = dict(validate_order(raw_order))
    correlation_id = order.get("correlation_id", str(uuid.uuid4()))
    order["correlation_id"] = correlation_id
    safety = detect_safety_signals(order["notes"])
    return {
        "order": order,
        "safety": {
            "allergy_risk": safety.allergy_risk,
            "restrictions": list(safety.restrictions),
            "matched_terms": list(safety.matched_terms),
        },
        "bedrock_request": build_bedrock_request(order, safety),
    }
