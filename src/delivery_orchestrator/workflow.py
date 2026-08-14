"""Deterministic local executable specification of the cloud workflow."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from .adapters import (
    DispatchGateway,
    NotificationGateway,
    PaymentGateway,
    ReferenceDispatchGateway,
    ReferenceNotificationGateway,
    ReferencePaymentGateway,
)
from .cognitive import normalize_analysis
from .errors import (
    BedrockThrottledError,
    BedrockTimeoutError,
    DispatchError,
    InvalidModelOutputError,
    NotificationError,
    PaymentDeclinedError,
)
from .local_analyzer import analyze_locally
from .safety import SafetySignal
from .validation import prepare_order


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str
    detail: str = ""


class InMemoryIdempotencyStore:
    """Process-local equivalent of the DynamoDB conditional claim."""

    def __init__(self) -> None:
        self._claims: set[str] = set()

    def claim(self, key: str) -> bool:
        if key in self._claims:
            return False
        self._claims.add(key)
        return True


class LocalWorkflow:
    """Run the same safety and decision policy with explicitly local adapters."""

    def __init__(
        self,
        *,
        payment: PaymentGateway | None = None,
        dispatch: DispatchGateway | None = None,
        notification: NotificationGateway | None = None,
        idempotency: InMemoryIdempotencyStore | None = None,
        analyzer: Callable[[dict[str, Any]], str] = analyze_locally,
    ) -> None:
        self.payment = payment or ReferencePaymentGateway()
        self.dispatch = dispatch or ReferenceDispatchGateway()
        self.notification = notification or ReferenceNotificationGateway()
        self.idempotency = idempotency or InMemoryIdempotencyStore()
        self.analyzer = analyzer

    def run(
        self,
        raw_order: dict[str, Any],
        *,
        model_text: str | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        steps: list[StepResult] = []
        prepared = prepare_order(raw_order)
        order = prepared["order"]
        steps.append(StepResult("Schema validation", "PASS"))

        if not self.idempotency.claim(str(order["idempotency_key"])):
            steps.append(StepResult("Idempotency claim", "FAIL", "duplicate key"))
            return self._result("DUPLICATE", order, steps, started)
        steps.append(StepResult("Idempotency claim", "PASS"))

        safety = SafetySignal(
            allergy_risk=prepared["safety"]["allergy_risk"],
            restrictions=tuple(prepared["safety"]["restrictions"]),
            matched_terms=tuple(prepared["safety"]["matched_terms"]),
        )
        try:
            cognitive_text = model_text if model_text is not None else self.analyzer(order)
        except BedrockTimeoutError as error:
            steps.append(StepResult("Cognitive analysis", "FAIL", str(error)))
            return self._result("FAILED_BEDROCK_TIMEOUT", order, steps, started)
        except BedrockThrottledError as error:
            steps.append(StepResult("Cognitive analysis", "FAIL", str(error)))
            return self._result("FAILED_BEDROCK_THROTTLED", order, steps, started)
        try:
            analysis = normalize_analysis(cognitive_text, safety)
        except InvalidModelOutputError as error:
            steps.append(StepResult("Cognitive analysis", "FAIL", str(error)))
            return self._result("FAILED_MODEL_CONTRACT", order, steps, started)
        steps.append(StepResult("Cognitive analysis", "PASS", "LOCAL_MOCK"))

        try:
            payment = self.payment.authorize(order)
        except PaymentDeclinedError as error:
            steps.append(StepResult("Payment", "FAIL", str(error)))
            return self._result("PAYMENT_REJECTED", order, steps, started, analysis=analysis)
        steps.append(StepResult("Payment", "APPROVED"))

        try:
            dispatch = self.dispatch.dispatch(order)
        except DispatchError as error:
            steps.append(StepResult("Dispatch", "FAIL", str(error)))
            return self._result("FULFILLMENT_FAILED", order, steps, started, analysis=analysis)
        steps.append(StepResult("Dispatch", "SUCCESS"))

        degraded = False
        try:
            notification = self.notification.notify(order, analysis)
            steps.append(StepResult("Notification", "SUCCESS"))
        except NotificationError as error:
            notification = {"status": "DEGRADED", "adapter": "REFERENCE_NON_SENDING"}
            degraded = True
            steps.append(StepResult("Notification", "DEGRADED", str(error)))

        return self._result(
            "COMPLETED_WITH_WARNING" if degraded else "COMPLETED",
            order,
            steps,
            started,
            analysis=analysis,
            effects={"payment": payment, "dispatch": dispatch, "notification": notification},
        )

    @staticmethod
    def _result(
        status: str,
        order: dict[str, Any],
        steps: list[StepResult],
        started: float,
        *,
        analysis: dict[str, Any] | None = None,
        effects: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "order_id": order["order_id"],
            "workflow_status": status,
            "execution_mode": "LOCAL_DETERMINISTIC_MOCK",
            "analysis": analysis,
            "effects": effects or {},
            "steps": [asdict(step) for step in steps],
            "measured_duration_ms": round((time.perf_counter() - started) * 1000, 3),
        }
