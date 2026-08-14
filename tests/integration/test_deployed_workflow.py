"""Opt-in deployed-AWS smoke test.

Run through scripts/integration_test.py; excluded from the default local test command because it
requires credentials, a deployed stack, model access, and incurs AWS charges.
"""

from __future__ import annotations

import os

import pytest


@pytest.mark.integration
def test_integration_environment_is_explicit() -> None:
    if os.getenv("RUN_AWS_INTEGRATION") != "1":
        pytest.skip("set RUN_AWS_INTEGRATION=1 and use scripts/integration_test.py")
    assert os.environ.get("STATE_MACHINE_ARN"), "STATE_MACHINE_ARN is required"
