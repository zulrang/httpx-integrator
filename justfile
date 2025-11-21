
RED := '\033[0;31m'
GREEN := '\033[0;32m'
YELLOW := '\033[0;33m'
BLUE := '\033[0;34m'
MAGENTA := '\033[0;35m'
CYAN := '\033[0;36m'
RESET := '\033[0m'

check-docker:
	@docker --version 2>/dev/null || (echo "{{ RED }}Docker is not installed. Please install Docker (or start Docker Desktop in Windows){{ RESET }}" && exit 1)
	@echo "{{ GREEN }}Docker is installed{{ RESET }}"


check: check-docker lint type test

test:
	@echo "{{ YELLOW }}Running tests...{{ RESET }}"
	@uv run pytest -n auto tests
	@echo "{{ GREEN }}Tests passed{{ RESET }}"
lint:
	@echo "{{ YELLOW }}Linting code...{{ RESET }}"
	@uv run ruff format src tests
	@uv run ruff check --fix src tests
	@echo "{{ GREEN }}Code linted{{ RESET }}"

type:
	@echo "{{ YELLOW }}Type checking code...{{ RESET }}"
	@uv run mypy src
	@echo "{{ GREEN }}Code type checked{{ RESET }}"
