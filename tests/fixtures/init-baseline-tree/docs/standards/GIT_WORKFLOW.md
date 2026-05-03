# Git Workflow Best Practices

**Document Type:** Core Principle Guide
**Category:** Development Workflow, Version Control
**Last Updated:** 2025-11-19
**Applies To:** All tachi development work

---

## Overview

This document defines the git workflow standards for tachi development. These practices ensure safe collaboration, maintain code quality, and support multi-agent development workflows.

**Constitutional Reference:** Principle IX - Git Workflow & Feature Branching (NON-NEGOTIABLE)

---

## Core Principles

### 1. Feature Branch Workflow (MANDATORY)

**Rule:** ALL development MUST occur on feature branches. Direct commits to `main` are STRICTLY PROHIBITED.

**Rationale:**
- Prevents accidental corruption of production-ready code
- Enables code review and quality gates
- Maintains clean development history
- Supports parallel multi-agent development

**Branch Naming Convention:**

The branch number **NNN** is the **GitHub Issue number**, zero-padded to 3 digits (e.g., GitHub Issue #1 becomes `001`, Issue #42 becomes `042`). NNN is **not** an independently generated Feature ID — it always corresponds directly to a GitHub Issue.

```
NNN-<description>

Examples:
✅ 001-task-locking-api        (GitHub Issue #1)
✅ 042-vector-search-optimization  (GitHub Issue #42)
✅ 089-mcp-timeout-handling    (GitHub Issue #89)

❌ feature/task-locking      (missing Issue number)
❌ fix_bug                    (use hyphens, not underscores)
❌ my-work                    (not descriptive)
```

**Branch Lifecycle:**
```bash
# 1. Create branch from main
git checkout main
git pull origin main
git checkout -b 001-task-locking-api

# 2. Work on feature
git add .
git commit -m "feat(api): implement task locking endpoint"

# 3. Push and create PR
git push origin 001-task-locking-api
# Create PR via GitHub UI

# 4. After merge, delete branch
git checkout main
git pull origin main
git branch -d 001-task-locking-api
```

---

## Commit Standards

### Conventional Commits Format

All commits MUST follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature or capability | `feat(api): add task locking endpoint` |
| `fix` | Bug fix | `fix(mcp): handle connection timeout` |
| `docs` | Documentation only | `docs(readme): update installation steps` |
| `style` | Code formatting (no logic change) | `style(api): format with prettier` |
| `refactor` | Code restructuring (no behavior change) | `refactor(db): extract query builder` |
| `perf` | Performance improvement | `perf(search): add query result caching` |
| `test` | Adding or updating tests | `test(api): add concurrency tests` |
| `chore` | Build, dependencies, tooling | `chore: update dependencies` |

### Scopes

Scopes match system architecture:

- `api` - REST API endpoints
- `mcp` - MCP server and tools
- `database` - Database schema and operations
- `auth` - Authentication/authorization
- `ui` - Frontend components
- `infra` - Infrastructure/deployment
- `test` - Testing infrastructure
- `docs` - Documentation

### Commit Message Examples

**Good Examples:**

```bash
# Feature with explanation
feat(api): add task locking endpoint

Implements POST /api/tasks/:id/claim with optimistic locking.
Uses locked_until timestamp to prevent race conditions.
Supports configurable lock timeout per project.

Closes #42

---

# Bug fix with root cause
fix(mcp): handle connection timeout gracefully

Falls back to local .aod/ files when MCP server
unreachable after 5s timeout. Adds health check endpoint
at /mcp/health for monitoring.

Root cause: No timeout configured on fetch() calls.
Solution: Add AbortController with 5s timeout.

Fixes #89

---

# Performance improvement
perf(search): optimize vector search with caching

Implements query result caching with 5-minute TTL.
Reduces 95th percentile search latency from 2.5s to 0.8s.

Benchmarks:
- Before: p50=1.2s, p95=2.5s, p99=4.1s
- After:  p50=0.3s, p95=0.8s, p99=1.2s

Refs #156
```

**Bad Examples:**

```bash
# Too vague
fix: fixed bug

# Missing scope
feat: add new feature

# Imperative not followed
fixed: fixes the timeout issue

# No explanation
refactor(api): changes
```

### Commit Best Practices

1. **Atomic Commits**: One logical change per commit
2. **Descriptive Subjects**: 50 characters or less, imperative mood ("add" not "added")
3. **Rich Bodies**: Explain "why" not "what" (code shows what)
4. **Issue References**: Use `Closes #123`, `Fixes #456`, or `Refs #789`
5. **Co-authorship**: Include agent/reviewer contributions
   ```
   Co-Authored-By: architect <agent@tachi>
   ```

---

## Pull Request Requirements

### PR Title Format

Follow conventional commit format:

```
<type>(<scope>): <description>

Examples:
✅ feat(api): implement task locking with optimistic concurrency control
✅ fix(mcp): gracefully handle server connection timeouts
✅ docs(contributing): add git workflow guidelines
```

### PR Description Template

```markdown
## Objective
[Brief description of what this PR accomplishes]

## Changes
- Bullet point summary of changes
- Highlight key architectural decisions
- Reference constitutional principles if applicable

## Testing
- [ ] Unit tests added (80% coverage minimum)
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Performance impact assessed

## Constitution Compliance
- [ ] Aligns with Principle I: General-Purpose Architecture
- [ ] Aligns with Principle II: API-First Design
- [ ] Aligns with Principle VI: Testing Excellence
- [ ] Aligns with Principle VII: Definition of Done

## Validation Checklist
- [ ] All automated tests pass (CI/CD pipeline)
- [ ] Code review approved (minimum 1 reviewer)
- [ ] No breaking API changes (or migration plan documented)
- [ ] Security scan passes (no vulnerabilities)
- [ ] Documentation updated (if applicable)
- [ ] Performance targets met (API <500ms, search <2s)

## Related Issues
Closes #123
Related to #456

## Screenshots/Demos
[Include if UI changes or significant feature]
```

### PR Size Guidelines

- **Optimal:** 200-500 lines of changes
- **Maximum:** 800 lines (larger PRs should be split)
- **Exception:** Large refactors or data migrations (document rationale)

**Strategy for Large Features:**
1. Break into smaller, independent PRs
2. Use feature flags to hide incomplete work
3. Link PRs together (e.g., "Part 1 of 3")

---

## Code Review Process

### Before Requesting Review

- [ ] All tests pass locally
- [ ] Lint checks pass (`make lint` or equivalent)
- [ ] No secrets or credentials in commits
- [ ] Sync with main: `git merge origin/main`
- [ ] Documentation updated
- [ ] Self-review completed

### Review Checklist for Reviewers

**Functional Review:**
- [ ] Code solves the stated problem
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is comprehensive
- [ ] Tests cover new functionality

**Constitutional Review:**
- [ ] Follows core principles (I-IX)
- [ ] Maintains backward compatibility (Principle III)
- [ ] API-first approach (Principle II)
- [ ] Proper concurrency handling (Principle IV)

**Quality Review:**
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity
- [ ] Consistent with existing patterns
- [ ] Proper variable/function naming
- [ ] Comments explain "why" not "what"

**Security Review:**
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Secrets managed properly
- [ ] Authentication/authorization correct

**Performance Review:**
- [ ] No N+1 queries
- [ ] Proper indexing (database queries)
- [ ] API response times meet targets (<500ms)
- [ ] Vector search meets targets (<2s)

### Review Response Time

- **Simple PRs** (<100 lines): Within 24 hours
- **Standard PRs** (100-500 lines): Within 48 hours
- **Complex PRs** (>500 lines): Within 72 hours
- **Urgent PRs** (hotfixes): Within 4 hours

---

## Git Safety Protocols

### Commands to NEVER Use (Without Explicit Approval)

| Prohibited Command | Why It's Dangerous | Safe Alternative |
|-------------------|-------------------|------------------|
| `git push -f origin main` | Overwrites production history | Merge instead; never force-push to main |
| `git reset --hard` | Loses all uncommitted work | Use `git stash` or create checkpoint branch |
| `git clean -fd` | Permanently deletes untracked files | Review with `git status` first, delete selectively |
| `git rebase main` (on shared branch) | Rewrites history others depend on | Use `git merge` on shared branches |
| `git commit --no-verify` | Bypasses safety hooks | Fix issues instead of skipping validation |

### Safe Git Practices

1. **Before Destructive Operations:**
   ```bash
   # Always check what you're about to change
   git status
   git diff HEAD
   git log --oneline -5
   ```

2. **Use `--force-with-lease` for Local Cleanup:**
   ```bash
   # Only force-push if no one else has pushed
   git push origin feature/001 --force-with-lease
   ```

3. **Create Checkpoint Branches:**
   ```bash
   # Before risky operations, create a checkpoint
   git branch checkpoint-before-rebase
   git rebase -i HEAD~5
   # If something goes wrong, recover with:
   git reset --hard checkpoint-before-rebase
   ```

4. **Verify Before Pushing:**
   ```bash
   # Always verify what you're pushing
   git log origin/main..HEAD
   git diff origin/main..HEAD
   ```

---

## Branch Protection Rules

### Main Branch Protection (Required)

Configure in GitHub repository settings:

- ✅ **Require pull request reviews before merging**
  - Minimum 1 approval for standard changes
  - Minimum 2 approvals for core architecture changes

- ✅ **Require status checks to pass**
  - All CI/CD workflows must succeed
  - Code coverage threshold met (80% minimum)

- ✅ **Require branches to be up to date before merging**
  - Prevent merging outdated branches

- ✅ **Require conversation resolution before merging**
  - All review comments must be addressed

- ✅ **Restrict who can push to matching branches**
  - Only maintainers can push directly (emergency only)

- ✅ **Require signed commits** (recommended)
  - Ensures commit authenticity

### CODEOWNERS Configuration

Create `.github/CODEOWNERS` to enforce architecture reviews:

```
# tachi CODEOWNERS

# Core API
/backend/api/ @architect @code-reviewer

# Database & concurrency
/backend/database/ @architect

# MCP Server
/backend/mcp/ @architect

# Frontend
/frontend/ @code-reviewer

# Infrastructure
/deployment/ @architect

# Tests
/tests/ @tester

# Documentation
/docs/ @architect
*.md @code-reviewer

# Constitution & governance
.aod/ @architect
CONTRIBUTING.md @architect
```

---

## Multi-Agent Collaboration

### Agent Assignment in PRs

```yaml
# Example PR with agent assignments
title: "feat(tasks): implement concurrent task claiming"
assignees:
  - frontend-developer      # Implementation lead
  - architect        # Design review
  - code-reviewer    # Quality check
  - tester           # QA sign-off

labels:
  - type/feature
  - component/api
  - priority/high
  - agent/frontend-developer
```

### Parallel Development with Git Worktrees

For parallel agent sessions working on different features:

```bash
# Main session working on feature 001
git worktree add ../work-001 001-task-locking

# Parallel session working on feature 002
git worktree add ../work-002 002-vector-search

# Each session works independently
# Merge back when complete
```

---

## CI/CD Integration

### Automated Checks (Required)

All PRs MUST pass these automated checks:

1. **Linting**: Code style and formatting
2. **Type Checking**: TypeScript/Python type validation
3. **Unit Tests**: Business logic tests (80% coverage)
4. **Integration Tests**: API and database tests
5. **Security Scan**: Dependency vulnerabilities
6. **Performance Tests**: Response time benchmarks
7. **Constitution Compliance**: Automated principle verification

### Pipeline Configuration Example

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint
        run: make lint
      - name: Type check
        run: make typecheck
      - name: Tests
        run: make test
      - name: Coverage
        run: make coverage-check
      - name: Security scan
        run: make security-scan
```

---

## Common Scenarios

### Scenario 1: Creating a New Feature

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b 042-knowledge-search

# 3. Make changes and commit
git add backend/api/knowledge.py
git commit -m "feat(api): add knowledge search endpoint

Implements GET /api/knowledge/search with vector similarity.
Returns top 10 results with relevance scores.

Refs #42"

# 4. Push and create PR
git push origin 042-knowledge-search
# Create PR via GitHub UI
```

### Scenario 2: Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b 089-mcp-timeout-fix

# 2. Fix bug and add test
git add backend/mcp/client.py tests/test_mcp_timeout.py
git commit -m "fix(mcp): handle connection timeout gracefully

Root cause: No timeout on fetch() calls to MCP server.
Solution: Add AbortController with 5s timeout and fallback.

Before: Hung indefinitely on network issues
After: Falls back to local files after 5s

Fixes #89"

# 3. Push and create PR
git push origin 089-mcp-timeout-fix
```

### Scenario 3: Updating Documentation

```bash
# 1. Create docs branch
git checkout -b 123-update-api-docs

# 2. Update docs
git add docs/api/endpoints.md
git commit -m "docs(api): update task locking endpoint documentation

Add examples for POST /api/tasks/:id/claim.
Document lock timeout configuration.
Clarify error responses for lock conflicts.

Closes #123"

# 3. Push (docs changes typically fast-tracked)
git push origin 123-update-api-docs
```

### Scenario 4: Syncing with Main

```bash
# If your branch is behind main
git checkout 001-task-locking
git merge origin/main

# Resolve any conflicts
git add .
git commit -m "merge: sync with main"
git push origin 001-task-locking
```

---

## Troubleshooting

### Problem: Merge Conflicts

```bash
# 1. Fetch latest main
git fetch origin main

# 2. Merge main into your branch
git merge origin/main

# 3. Resolve conflicts (edit files)
# 4. Mark as resolved
git add <conflicted-files>

# 5. Complete merge
git commit -m "merge: resolve conflicts with main"
```

### Problem: Accidentally Committed to Main

```bash
# 1. Create a new branch from current state
git branch emergency-save

# 2. Reset main to match remote
git checkout main
git reset --hard origin/main

# 3. Apply changes via proper branch
git checkout -b proper-feature-branch
git cherry-pick emergency-save
git push origin proper-feature-branch

# 4. Create PR
```

### Problem: Need to Undo Last Commit

```bash
# If commit not pushed yet
git reset --soft HEAD~1  # Keeps changes staged
# or
git reset HEAD~1         # Unstages changes

# If commit already pushed
git revert HEAD          # Creates new commit that undoes
git push origin <branch>
```

---

## Quick Reference

### Common Commands

```bash
# Start new feature (NNN = GitHub Issue number, zero-padded to 3 digits)
git checkout -b NNN-feature-name

# Check status
git status

# Stage changes
git add <files>

# Commit with message
git commit -m "type(scope): description"

# Push branch
git push origin <branch-name>

# Update from main
git merge origin/main

# Delete local branch
git branch -d <branch-name>

# Delete remote branch
git push origin --delete <branch-name>
```

### Commit Message Template

```
type(scope): subject (max 50 chars)

Body: Explain "why" not "what"
- What problem does this solve?
- What was the approach?
- Any important context?

Closes #123
Co-Authored-By: Agent <agent@tachi>
```

---

## References

- **Constitution**: `.aod/memory/constitution.md` - Principle IX
- **Contributing Guide**: `CONTRIBUTING.md` - Development workflow
- **Claude Code Docs**: Common workflows and git integration
- **Conventional Commits**: https://www.conventionalcommits.org/
- **GitHub Flow**: https://guides.github.com/introduction/flow/

---

*This workflow guide is part of the tachi core principles. All development work must adhere to these standards.*
