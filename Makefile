# Agentic-Oriented-Development-Kit - Common Commands

.PHONY: help init check spec plan tasks analyze review-spec review-plan test

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize project (first-time setup)
	@./scripts/init.sh

check: ## Verify setup and prerequisites
	@./scripts/check.sh

# Triad Workflow shortcuts
spec: ## Run /triad.specify
	@echo "Use /triad.specify in Claude Code"

plan: ## Run /triad.plan
	@echo "Use /triad.plan in Claude Code"

tasks: ## Run /triad.tasks
	@echo "Use /triad.tasks in Claude Code"

analyze: ## Run /triad.analyze
	@echo "Use /triad.analyze in Claude Code"

# Governance shortcuts
review-spec: ## Review spec.md with PM
	@echo "Use product-manager agent or /triad.specify for auto-review"

review-plan: ## Review plan.md with PM + Architect
	@echo "Use product-manager + architect agents or /triad.plan for auto-review"

# Python test suite
test: ## Run the Python test suite
	@pytest tests/scripts/ --cov=scripts --cov-report=term-missing
