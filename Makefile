# Agentic-Oriented-Development-Kit - Common Commands

.PHONY: help init check update spec plan tasks analyze review-spec review-plan test coverage-audit llvm-cov

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize project (first-time setup)
	@./scripts/init.sh

check: ## Verify setup and prerequisites
	@./scripts/check.sh

update: ## Apply upstream template updates (AOD-kit → tachi); pass flags via ARGS='...'
	@./scripts/update.sh $(ARGS)

# Triad Workflow shortcuts
spec: ## Run /aod.spec
	@echo "Use /aod.spec in Claude Code"

plan: ## Run /aod.plan
	@echo "Use /aod.plan in Claude Code"

tasks: ## Run /aod.tasks
	@echo "Use /aod.tasks in Claude Code"

analyze: ## Run /aod.analyze
	@echo "Use /aod.analyze in Claude Code"

# Governance shortcuts
review-spec: ## Review spec.md with PM
	@echo "Use product-manager agent or /aod.spec for auto-review"

review-plan: ## Review plan.md with PM + Architect
	@echo "Use product-manager + architect agents or /aod.plan for auto-review"

# Rust test suite
test: ## Run the Rust test suite
	@cargo test -q

coverage-audit: ## Report the repository test surface by category
	@./scripts/coverage-audit.sh --root .

llvm-cov: ## Run cargo llvm-cov with the active toolchain's LLVM tools
	@./scripts/llvm-cov.sh

workflow-gate: ## Validate workflow action versions and checkout modernization
	@if rg "actions/checkout@v4" .github/workflows; then \
	  echo "FAIL: actions/checkout@v4 is still present in workflows"; \
	  exit 1; \
	else \
	  echo "workflow action gate passed"; \
	fi
