from __future__ import annotations

import json
from typing import Any, NoReturn

import pytest

from delivery_orchestrator.adapters import (
    ReferenceDispatchGateway,
    ReferenceNotificationGateway,
    ReferencePaymentGateway,
)
from delivery_orchestrator.errors import (
    BedrockThrottledError,
    BedrockTimeoutError,
    InvalidOrderError,
)
from delivery_orchestrator.workflow import InMemoryIdempotencyStore, LocalWorkflow
from tests.conftest import load_fixture


def test_happy_path_uses_real_local_execution(valid_order: dict[str, Any]) -> None:
    result = LocalWorkflow().run(valid_order)
    assert result["workflow_status"] == "COMPLETED"
    assert result["analysis"]["risco_alergia"] is True
    assert result["analysis"]["prioridade"] == "HIGH"
    assert result["effects"]["payment"]["status"] == "APPROVED"
    assert result["execution_mode"] == "LOCAL_DETERMINISTIC_MOCK"


def test_invalid_payment_never_reaches_cognitive_stage() -> None:
    with pytest.raises(InvalidOrderError):
        LocalWorkflow().run(load_fixture("invalid_payment.json"))


def test_payment_failure_stops_before_dispatch(valid_order: dict[str, Any]) -> None:
    result = LocalWorkflow(payment=ReferencePaymentGateway(should_decline=True)).run(valid_order)
    assert result["workflow_status"] == "PAYMENT_REJECTED"
    assert all(step["name"] != "Dispatch" for step in result["steps"])


def test_dispatch_failure_is_critical(valid_order: dict[str, Any]) -> None:
    result = LocalWorkflow(dispatch=ReferenceDispatchGateway(should_fail=True)).run(valid_order)
    assert result["workflow_status"] == "FULFILLMENT_FAILED"


def test_notification_failure_is_degraded(valid_order: dict[str, Any]) -> None:
    workflow = LocalWorkflow(notification=ReferenceNotificationGateway(should_fail=True))
    result = workflow.run(valid_order)
    assert result["workflow_status"] == "COMPLETED_WITH_WARNING"
    assert result["effects"]["notification"]["status"] == "DEGRADED"


def test_invalid_model_output_fails_contract(valid_order: dict[str, Any]) -> None:
    result = LocalWorkflow().run(valid_order, model_text="not-json")
    assert result["workflow_status"] == "FAILED_MODEL_CONTRACT"


def test_duplicate_idempotency_key_is_rejected(valid_order: dict[str, Any]) -> None:
    store = InMemoryIdempotencyStore()
    workflow = LocalWorkflow(idempotency=store)
    assert workflow.run(valid_order)["workflow_status"] == "COMPLETED"
    assert workflow.run(valid_order)["workflow_status"] == "DUPLICATE"


def _timeout(_: dict[str, Any]) -> NoReturn:
    raise BedrockTimeoutError("bounded timeout")


def _throttle(_: dict[str, Any]) -> NoReturn:
    raise BedrockThrottledError("bounded retries exhausted")


@pytest.mark.parametrize(
    ("analyzer", "expected"),
    [(_timeout, "FAILED_BEDROCK_TIMEOUT"), (_throttle, "FAILED_BEDROCK_THROTTLED")],
)
def test_bedrock_dependency_failures_are_classified(
    valid_order: dict[str, Any], analyzer: Any, expected: str
) -> None:
    assert LocalWorkflow(analyzer=analyzer).run(valid_order)["workflow_status"] == expected


def test_prompt_injection_safety_scenario() -> None:
    order = load_fixture("prompt_injection.json")
    malicious_model_output = json.dumps(
        {
            "intent": "ORDER",
            "analise_sentimento": "NEUTRAL",
            "prioridade": "NORMAL",
            "risco_alergia": False,
            "restricoes": [],
            "confidence": 1.0,
        }
    )
    result = LocalWorkflow().run(order, model_text=malicious_model_output)
    assert result["workflow_status"] == "COMPLETED"
    assert result["analysis"]["risco_alergia"] is True
    assert result["analysis"]["safety_override_applied"] is True
