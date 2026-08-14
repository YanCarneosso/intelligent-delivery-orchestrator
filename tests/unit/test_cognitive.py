from __future__ import annotations

import json
from typing import Any

import pytest

from delivery_orchestrator.cognitive import (
    build_bedrock_request,
    extract_model_text,
    normalize_analysis,
    parse_model_text,
)
from delivery_orchestrator.errors import InvalidModelOutputError
from delivery_orchestrator.safety import detect_safety_signals
from tests.conftest import load_fixture


def _unsafe_false_output() -> str:
    return json.dumps(
        {
            "intent": "ORDER",
            "analise_sentimento": "NEUTRAL",
            "prioridade": "NORMAL",
            "risco_alergia": False,
            "restricoes": [],
            "confidence": 0.99,
        }
    )


def test_bedrock_request_minimizes_pii(valid_order: dict[str, Any]) -> None:
    safety = detect_safety_signals(valid_order["notes"])
    request = build_bedrock_request(valid_order, safety)
    serialized = json.dumps(request)
    assert "postal_code" not in serialized
    assert "payment_method" not in serialized
    assert "delivery_instructions" not in serialized
    assert request["schemaVersion"] == "messages-v1"


def test_prompt_treats_notes_as_untrusted(valid_order: dict[str, Any]) -> None:
    request = build_bedrock_request(valid_order, detect_safety_signals(valid_order["notes"]))
    user_text = request["messages"][0]["content"][0]["text"]
    assert "<UNTRUSTED_ORDER_NOTES>" in user_text
    assert "JSON_CONTRACT=" in user_text


def test_markdown_wrapped_json_is_rejected() -> None:
    response = load_fixture("bedrock_invalid_response.json")
    with pytest.raises(InvalidModelOutputError, match="bare JSON"):
        parse_model_text(extract_model_text(response))


def test_prompt_injection_cannot_clear_detected_allergy() -> None:
    order = load_fixture("prompt_injection.json")
    result = normalize_analysis(_unsafe_false_output(), detect_safety_signals(order["notes"]))
    assert result["risco_alergia"] is True
    assert result["prioridade"] == "HIGH"
    assert result["safety_override_applied"] is True
    assert "AMENDOIM" in result["restricoes"]


def test_model_can_add_a_restriction() -> None:
    model_output = json.loads(_unsafe_false_output())
    model_output["restricoes"] = ["VEGAN"]
    result = normalize_analysis(
        json.dumps(model_output), detect_safety_signals("Entregar na portaria")
    )
    assert result["restricoes"] == ["VEGAN"]


def test_extract_model_text_from_projected_response() -> None:
    assert extract_model_text({"bedrock": {"modelText": "{}"}}) == "{}"


def test_extract_model_text_rejects_wrong_shape() -> None:
    with pytest.raises(InvalidModelOutputError, match="did not contain"):
        extract_model_text({"bedrock": {"unexpected": True}})
