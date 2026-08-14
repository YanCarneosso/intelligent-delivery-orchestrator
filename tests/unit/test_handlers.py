from __future__ import annotations

import json
from typing import Any

from delivery_orchestrator.handlers.dispatch import handler as dispatch_handler
from delivery_orchestrator.handlers.input_validation import handler as validation_handler
from delivery_orchestrator.handlers.normalize import handler as normalize_handler
from delivery_orchestrator.handlers.notification import handler as notification_handler
from delivery_orchestrator.handlers.payment import handler as payment_handler


def test_validation_handler(valid_order: dict[str, Any], capsys: Any) -> None:
    result = validation_handler(valid_order, None)
    assert result["order"]["order_id"] == valid_order["order_id"]
    log = json.loads(capsys.readouterr().out)
    assert log["OrdersValidated"] == 1
    assert "notes" not in log


def test_normalize_handler_applies_override(valid_order: dict[str, Any], capsys: Any) -> None:
    prepared = validation_handler(valid_order, None)
    capsys.readouterr()
    prepared["bedrock"] = {
        "modelText": json.dumps(
            {
                "intent": "ORDER",
                "analise_sentimento": "NEUTRAL",
                "prioridade": "NORMAL",
                "risco_alergia": False,
                "restricoes": [],
                "confidence": 0.8,
            }
        )
    }
    result = normalize_handler(prepared, None)
    assert result["risco_alergia"] is True
    assert result["safety_override_applied"] is True
    assert json.loads(capsys.readouterr().out)["AllergyRiskOrders"] == 1


def test_reference_effect_handlers_are_explicit(valid_order: dict[str, Any], capsys: Any) -> None:
    event = {"order": valid_order, "analysis": {}}
    payment = payment_handler(event, None)
    dispatch = dispatch_handler(event, None)
    notification = notification_handler(event, None)
    capsys.readouterr()
    assert payment["adapter"] == "REFERENCE_NON_CHARGING"
    assert dispatch["adapter"] == "REFERENCE_NON_DISPATCHING"
    assert notification["adapter"] == "REFERENCE_NON_SENDING"
