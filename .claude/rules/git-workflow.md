# Git Workflow

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

All development must use feature branches. Never commit to main directly.

**Auto-create branches**: When a workflow command (e.g., `/aod.plan`, `/aod.spec`) detects you are on `main`, automatically create the feature branch and switch to it. Do NOT ask the user for confirmation — feature branches are mandatory, not a choice.

---

## Branch Naming

**Format**: `NNN-descriptive-name`
- **NNN**: GitHub Issue number, zero-padded to 3 digits (e.g., `001`, `002`, `012`)
- **descriptive-name**: Kebab-case description (e.g., `initial-feature`, `user-auth`)

**Examples**:
- `001-initial-feature`
- `012-database-migration`
- `045-api-authentication`

---

## Commit Standards

- Write clear, descriptive commit messages
- Use conventional commits format when possible (feat:, fix:, docs:, etc.)
- Keep commits atomic and focused on single changes
- Reference GitHub Issue numbers in commit messages (e.g., "feat(021): add dark mode")

---

## PR Policies

**Always use feature branches**: `git checkout -b NNN-feature-name`
- Never commit to main directly
- Create PR for review before merge
- Link PR to feature spec (`specs/NNN-feature-name/spec.md`)
- Ensure CI/CD passes before merge
- Require at least one approval (if team workflow)
