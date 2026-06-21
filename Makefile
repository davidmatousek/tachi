# Agentic-Oriented-Development-Kit - Common Commands

.PHONY: help init check update spec plan tasks analyze review-spec review-plan test coverage-audit llvm-cov workflow-gate docs-version-gate docs-archive-version-gate release-gate publish-gate

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
	@if rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|::set-output" .github/workflows; then \
	  echo "FAIL: stale GitHub Actions or CodeQL pins are still present in workflows"; \
	  exit 1; \
	else \
	  echo "workflow action gate passed"; \
	fi

docs-version-gate: ## Validate docs and examples workflow-version hygiene
	@if rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|codeql/upload-sarif@v3|::set-output|Node 20" \
	  docs/testing/README.md \
	  docs/guides/DEVELOPER_GUIDE_TACHI.md \
	  docs/devops/README.md \
	  docs/devops/CI_CD_GUIDE.md \
	  docs/standards/PRECOMMIT_HOOKS.md \
	  docs/standards/GIT_WORKFLOW.md \
	  docs/architecture/00_Tech_Stack/README.md \
	  docs/architecture/01_system_design/README.md \
	  examples; then \
	  echo "FAIL: stale workflow-version references are still present in maintained docs or examples"; \
	  exit 1; \
	else \
	  echo "docs/version gate passed"; \
	fi

docs-archive-version-gate: ## Validate archived docs workflow-version hygiene
	@./scripts/docs-archive-version-gate.sh

release-gate: ## Validate release artifact parity and checksum matrix
	@cargo test -p tachi-tauri --test release_artifacts -- --nocapture

publish-gate: ## Run end-to-end publish-readiness gates locally
	@$(MAKE) check
	@$(MAKE) workflow-gate
	@$(MAKE) docs-version-gate
	@$(MAKE) docs-archive-version-gate
	@$(MAKE) release-gate
	@$(MAKE) test
	@cargo clippy --all-targets -- -D warnings
	@$(MAKE) coverage-audit
	@$(MAKE) llvm-cov
