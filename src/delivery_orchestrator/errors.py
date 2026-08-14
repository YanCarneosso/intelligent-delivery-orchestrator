"""Typed errors surfaced to the workflow boundary."""


class OrchestratorError(Exception):
    """Base error for expected orchestration failures."""


class InvalidOrderError(OrchestratorError):
    """The caller supplied an order that violates the input contract."""


class InvalidModelOutputError(OrchestratorError):
    """The model response is not safe to consume."""


class BedrockTimeoutError(OrchestratorError):
    """The cognitive dependency exceeded its bounded timeout."""


class BedrockThrottledError(OrchestratorError):
    """The cognitive dependency remained throttled after bounded retries."""


class PaymentDeclinedError(OrchestratorError):
    """The deterministic payment adapter declined the transaction."""


class DispatchError(OrchestratorError):
    """The logistics adapter could not dispatch the order."""


class NotificationError(OrchestratorError):
    """The notification adapter failed; fulfillment may still continue."""
