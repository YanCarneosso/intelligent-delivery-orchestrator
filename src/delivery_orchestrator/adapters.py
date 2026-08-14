"""Deterministic reference adapters for external side effects.

These adapters deliberately do not claim to charge money, contact a courier, or send a
message. Production providers must replace them behind the same narrow interfaces.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Protocol

from .errors import DispatchError, NotificationError, PaymentDeclinedError


class PaymentGateway(Protocol):
    def authorize(self, order: dict[str, Any]) -> dict[str, str]: ...


class DispatchGateway(Protocol):
    def dispatch(self, order: dict[str, Any]) -> dict[str, str]: ...


class NotificationGateway(Protocol):
    def notify(self, order: dict[str, Any], analysis: dict[str, Any]) -> dict[str, str]: ...


def _reference(prefix: str, order_id: str) -> str:
    digest = hashlib.sha256(order_id.encode()).hexdigest()[:12].upper()
    return f"{prefix}-{digest}"


@dataclass
class ReferencePaymentGateway:
    """Non-charging adapter used for local evaluation and the reference AWS stack."""

    should_decline: bool = False

    def authorize(self, order: dict[str, Any]) -> dict[str, str]:
        if self.should_decline:
            raise PaymentDeclinedError("reference payment adapter declined the order")
        return {
            "status": "APPROVED",
            "authorization_id": _reference("AUTH", str(order["order_id"])),
            "adapter": "REFERENCE_NON_CHARGING",
        }


@dataclass
class ReferenceDispatchGateway:
    """Non-dispatching logistics adapter with deterministic receipts."""

    should_fail: bool = False

    def dispatch(self, order: dict[str, Any]) -> dict[str, str]:
        if self.should_fail:
            raise DispatchError("reference dispatch adapter failed")
        return {
            "status": "SUCCESS",
            "dispatch_id": _reference("DSP", str(order["order_id"])),
            "adapter": "REFERENCE_NON_DISPATCHING",
        }


@dataclass
class ReferenceNotificationGateway:
    """Non-sending notification adapter with deterministic receipts."""

    should_fail: bool = False

    def notify(self, order: dict[str, Any], analysis: dict[str, Any]) -> dict[str, str]:
        del analysis
        if self.should_fail:
            raise NotificationError("reference notification adapter failed")
        return {
            "status": "SUCCESS",
            "notification_id": _reference("NTF", str(order["order_id"])),
            "adapter": "REFERENCE_NON_SENDING",
        }
