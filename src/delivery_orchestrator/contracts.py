"""JSON contract loading and validation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .errors import InvalidModelOutputError, InvalidOrderError


def _project_root() -> Path:
    configured = os.getenv("PROJECT_ROOT")
    if configured:
        return Path(configured)
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "schemas").is_dir():
            return parent
    return Path("/var/task")


def load_schema(name: str) -> dict[str, Any]:
    """Load a version-controlled schema from the deployment package."""
    packaged_path = Path(__file__).parent / "assets" / name
    path = packaged_path if packaged_path.is_file() else _project_root() / "schemas" / name
    with path.open(encoding="utf-8") as schema_file:
        schema: dict[str, Any] = json.load(schema_file)
    Draft202012Validator.check_schema(schema)
    return schema


def _format_error(error: ValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"{location}: {error.message}"


def validate_order(order: Any) -> dict[str, Any]:
    """Validate caller input and return it with a precise type boundary."""
    validator = Draft202012Validator(load_schema("order.schema.json"))
    errors = sorted(validator.iter_errors(order), key=lambda item: list(item.absolute_path))
    if errors:
        raise InvalidOrderError("; ".join(_format_error(error) for error in errors))
    if not isinstance(order, dict):  # Defensive type narrowing after schema validation.
        raise InvalidOrderError("$: order must be an object")
    return order


def validate_cognitive_output(output: Any) -> dict[str, Any]:
    """Reject arbitrary LLM output before it reaches business rules."""
    validator = Draft202012Validator(load_schema("cognitive-output.schema.json"))
    errors = sorted(validator.iter_errors(output), key=lambda item: list(item.absolute_path))
    if errors:
        raise InvalidModelOutputError("; ".join(_format_error(error) for error in errors))
    if not isinstance(output, dict):
        raise InvalidModelOutputError("$: model output must be an object")
    return output


def validate_schema_files() -> None:
    """Validate both schema documents themselves; used by CI."""
    for name in ("order.schema.json", "cognitive-output.schema.json"):
        try:
            Draft202012Validator.check_schema(load_schema(name))
        except SchemaError as error:
            raise RuntimeError(f"invalid schema {name}: {error.message}") from error
