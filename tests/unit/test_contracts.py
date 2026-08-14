from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from delivery_orchestrator.contracts import (
    validate_cognitive_output,
    validate_order,
    validate_schema_files,
)
from delivery_orchestrator.errors import InvalidModelOutputError, InvalidOrderError
from tests.conftest import load_fixture


def valid_analysis() -> dict[str, Any]:
    return {
        "intent": "ORDER",
        "analise_sentimento": "NEUTRAL",
        "prioridade": "NORMAL",
        "risco_alergia": False,
        "restricoes": [],
        "confidence": 0.9,
    }


def test_schema_documents_are_valid() -> None:
    validate_schema_files()


def test_valid_order_contract(valid_order: dict[str, Any]) -> None:
    assert validate_order(valid_order)["order_id"] == "ORD-0001"


def test_invalid_payment_is_rejected_before_inference() -> None:
    with pytest.raises(InvalidOrderError, match="CHEQUE"):
        validate_order(load_fixture("invalid_payment.json"))


def test_missing_required_field_is_rejected() -> None:
    with pytest.raises(InvalidOrderError, match="address"):
        validate_order(load_fixture("missing_required_field.json"))


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda value: value.update({"unexpected": True}), "Additional properties"),
        (lambda value: value["product"].update({"quantity": "one"}), "not of type 'integer'"),
        (lambda value: value.update({"order_id": "bad"}), "does not match"),
        (lambda value: value.update({"notes": "x" * 2001}), "too long"),
    ],
)
def test_negative_order_contract_cases(
    valid_order: dict[str, Any], mutation: Any, expected: str
) -> None:
    candidate = deepcopy(valid_order)
    mutation(candidate)
    with pytest.raises(InvalidOrderError, match=expected):
        validate_order(candidate)


def test_valid_cognitive_contract() -> None:
    assert validate_cognitive_output(valid_analysis())["confidence"] == 0.9


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.pop("confidence"),
        lambda value: value.update({"confidence": 1.1}),
        lambda value: value.update({"prioridade": "CRITICAL"}),
        lambda value: value.update({"risco_alergia": "false"}),
        lambda value: value.update({"extra": "untrusted"}),
        lambda value: value.update({"restricoes": ["not-normalized"]}),
    ],
)
def test_invalid_cognitive_contract_cases(mutation: Any) -> None:
    candidate = valid_analysis()
    mutation(candidate)
    with pytest.raises(InvalidModelOutputError):
        validate_cognitive_output(candidate)
