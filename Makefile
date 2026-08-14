PYTHON ?= python3
VENV ?= .venv
VENV_BIN := $(VENV)/bin
AWS_REGION ?= us-east-1
STACK_NAME ?= intelligent-delivery-orchestrator-dev
ENVIRONMENT ?= dev

.PHONY: setup test test-all demo benchmark lint format format-check typecheck validate security ci build deploy integration-test cloud-demo destroy clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/python -m pip install -e ".[dev,aws]"

test:
	$(VENV_BIN)/python -m pytest -m "not integration"

test-all:
	$(VENV_BIN)/python -m pytest

demo:
	$(VENV_BIN)/python -m delivery_orchestrator.cli

benchmark:
	$(VENV_BIN)/python scripts/benchmark.py --iterations 500

lint:
	$(VENV_BIN)/python -m ruff check .

format:
	$(VENV_BIN)/python -m ruff format .

format-check:
	$(VENV_BIN)/python -m ruff format --check .

typecheck:
	$(VENV_BIN)/python -m mypy

validate:
	$(VENV_BIN)/python scripts/validate_repository.py

security:
	$(VENV_BIN)/python scripts/secret_scan.py

ci: lint format-check typecheck validate security test

build:
	sam build

deploy: build
	sam deploy --stack-name $(STACK_NAME) --region $(AWS_REGION) --resolve-s3 --capabilities CAPABILITY_IAM --parameter-overrides Environment=$(ENVIRONMENT) --no-confirm-changeset

integration-test:
	RUN_AWS_INTEGRATION=1 $(VENV_BIN)/python scripts/integration_test.py

cloud-demo:
	$(VENV_BIN)/python scripts/integration_test.py --show-result

destroy:
	sam delete --stack-name $(STACK_NAME) --region $(AWS_REGION) --no-prompts

clean:
	$(VENV_BIN)/python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('.aws-sam','.pytest_cache','.mypy_cache','.ruff_cache','htmlcov')]"

