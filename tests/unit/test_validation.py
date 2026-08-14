from __future__ import annotations

import json
from typing import Any

from delivery_orchestrator.validation import prepare_order


def test_prepare_order_preserves_supplied_correlation_id(valid_order: dict[str, Any]) -> None:
    prepared = prepare_order(valid_order)
    assert prepared["order"]["correlation_id"] == valid_order["correlation_id"]


def test_prepare_order_builds_bedrock_body(valid_order: dict[str, Any]) -> None:
    prepared = prepare_order(valid_order)
    body = prepared["bedrock_request"]
    assert body["inferenceConfig"]["temperature"] == 0
    json.dumps(body)


def test_prepare_order_detects_safety_before_model(valid_order: dict[str, Any]) -> None:
    prepared = prepare_order(valid_order)
    assert prepared["safety"]["allergy_risk"] is True
    assert "CEBOLA" in prepared["safety"]["restrictions"]
