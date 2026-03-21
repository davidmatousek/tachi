# Architecture Documentation - tachi

**Last Updated**: 2026-03-21
**Owner**: Architect
**Status**: Template

---

## Overview

This directory contains all technical architecture documentation for tachi.

---

## Structure

### 00_Tech_Stack/
Technology choices and justifications
- `README.md` - Tech stack overview with {{TEMPLATE_VARIABLES}}

### 01_system_design/
High-level system design and component diagrams
- `README.md` - System architecture overview (auto-scaffolded from plan.md by `/aod.project-plan` after Architect sign-off)
- `upstream-sync-architecture.md` - Repo topology and sync flow between private, public template, and adopter projects
- Component interaction diagrams
- Data flow diagrams

### 02_ADRs/ (Architecture Decision Records)
Significant technical decisions with context and trade-offs
- `ADR-000-template.md` - ADR template and example
- `ADR-001-atomic-state-persistence.md` - Write-then-rename for orchestrator state (Feature 022)
- `ADR-002-prompt-segmentation.md` - On-demand reference file loading for context efficiency (Feature 030)
- `ADR-005-serialization-trade-off.md` - Serialization trade-off for parallel Triad reviews (Feature 047)
- `ADR-006-non-fatal-observability-operations.md` - Non-fatal error handling for observability and circuit-breaker functions (Feature 054)
- `ADR-007-stack-pack-dual-surface-injection.md` - Dual-surface injection pattern for stack pack context loading (Feature 058)
- `ADR-008-opt-out-flag-for-default-quality-gates.md` - Opt-out flag (`--no-simplify`) for default-on quality gate steps in commands (Feature 065)
- `ADR-009-template-variable-expansion-scope.md` - Expanding `tachi` placeholder to all user-facing template files (Feature 061)
- `ADR-010-minimal-return-architecture.md` - Minimal return architecture for subagent→main token efficiency (Feature 073)
- `ADR-011-multi-flag-opt-out-and-step-insertion-pattern.md` - Multi-flag opt-out pattern and step insertion convention for `/aod.build` (Feature 080)
- `ADR-NNN-decision-title.md` - Individual ADRs

### 03_patterns/
Reusable design patterns and best practices
- `README.md` - Pattern catalog
- Pattern documentation by category

### 04_deployment_environments/
Environment-specific configurations and documentation
- `README.md` - Environment overview
- `development.md` - Local development setup
- `staging.md` - Staging environment
- `production.md` - Production environment

---

## Key Principles

1. **Document Decisions**: Use ADRs for significant technical choices
2. **Keep Current**: Update docs alongside code changes
3. **Auto-Scaffold**: `01_system_design/README.md` is auto-generated from plan.md during `/aod.project-plan` approval (Feature 089)
4. **Template Variables**: Use `{{TEMPLATE_VARIABLES}}` for project-specific values
5. **Version Control**: All architecture docs in git

---

## Quick Links

- [Tech Stack](00_Tech_Stack/README.md)
- [System Design](01_system_design/README.md)
- [ADRs](02_ADRs/ADR-000-template.md)
- [Patterns](03_patterns/README.md)
- [Environments](04_deployment_environments/README.md)

---

**Maintained By**: Architect
