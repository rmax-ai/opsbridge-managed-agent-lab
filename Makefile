.PHONY: bootstrap-cloud bootstrap-self-hosted seed-demo-data run-ui run-api clean

bootstrap-cloud: ## Provision cloud Managed Agents environment
	python -m src.opsbridge.managed_agents.provision --profile cloud

bootstrap-self-hosted: ## Provision self-hosted sandbox profile
	python -m src.opsbridge.managed_agents.provision --profile self-hosted

seed-demo-data: ## Seed OpsHub MCP server with incident data
	python -m mcp_server.seed

run-mcp-server: ## Start the synthetic OpsHub MCP server
	uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001

run-api: ## Start the FastAPI backend
	uvicorn src.opsbridge.api.main:app --host 0.0.0.0 --port 8000 --reload

run-ui: ## Start the Streamlit UI
	streamlit run app/ui/streamlit_app.py --server.port 8501

setup: ## Install dependencies
	pip install -e ".[dev]"

clean: ## Remove generated files
	rm -rf data/*.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

test: ## Run all tests
	python -m pytest tests/ -v -x --tb=short

test-evals: ## Run governance evaluation tests
	python -m pytest tests/evals/ -v -x --tb=short

lint: ## Lint and type-check
	ruff check src/ tests/
	ruff format --check src/ tests/

format: ## Format code
	ruff format src/ tests/
	ruff check --fix src/ tests/

demo-full: ## Run the full demo (bootstrap + seed + services)
	$(MAKE) bootstrap-cloud
	$(MAKE) seed-demo-data
	@echo "Start MCP server, API, and UI in separate terminals:"
	@echo "  make run-mcp-server"
	@echo "  make run-api"
	@echo "  make run-ui"
