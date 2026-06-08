# Testing Strategy - {{PROJECT_NAME}}

**Last Updated**: {{CURRENT_DATE}}
**Owner**: Architect + Team Lead
**Status**: Template

---

## Overview

This document provides guidance on testing strategy for {{PROJECT_NAME}}. It does NOT scaffold specific test files (project-specific), but provides recommendations and patterns.

## Coverage Visibility

- Run `make coverage-audit` to classify the current test surface with the Rust-backed audit binary.
- The audit now includes Rust-native test modules under `crates/*/tests` and `src-tauri/tests` alongside the remaining legacy Python tests.
- Run `make llvm-cov` to generate the workspace coverage report with LLVM tools resolved from the active toolchain.
- See `coverage-summary.md` for the current counts, category meanings, and smoke-vs-e2e boundary.
- See `2026-06-04-rust-native-coverage-audit.md` for the Rust-native migration target and current workspace skeleton baseline.

---

## Testing Philosophy

**Goal**: Ship confidently with automated quality gates

**Principles**:
1. **Test the right things**: Focus on user-facing behavior, not implementation
2. **Fast feedback**: Unit tests run in milliseconds, integration in seconds
3. **Reliable tests**: Tests should pass/fail consistently
4. **Maintainable tests**: Tests should be easy to understand and update

---

## Testing Pyramid

```
          /\
         /E2E\          <- Few (Critical user flows)
        /------\
       /  API   \       <- Some (API contracts, integration)
      /----------\
     /   Unit     \     <- Many (Business logic, utilities)
    /--------------\
```

### Unit Tests (70%)
- **What**: Individual functions, components, utilities
- **Speed**: <10ms per test
- **Scope**: Single unit in isolation
- **Mocking**: Mock external dependencies only when a real dependency is impractical

### Integration Tests (20%)
- **What**: Multiple units working together (API + database)
- **Speed**: <100ms per test
- **Scope**: API endpoints, database operations
- **Mocking**: Minimize; prefer real test fixtures and local services

### E2E Tests (10%)
- **What**: Complete user workflows
- **Speed**: <5s per test
- **Scope**: Frontend → Backend → Database
- **Mocking**: None (test production-like environment)

---

## Recommended Testing Frameworks by Project Type

### Rust Projects

- **Unit/Integration**: `cargo test`, `cargo nextest` when faster isolation is useful
- **Coverage**: `cargo llvm-cov`
- **CLI smoke**: shell wrappers around `cargo run` or installed binaries

**Example Setup**
```bash
cargo test
cargo nextest run
make llvm-cov
```

### Frontend Testing

**JavaScript/TypeScript Projects**:
- **Unit/Integration**: [Vitest](https://vitest.dev/) or [Jest](https://jestjs.io/)
- **Component**: [React Testing Library](https://testing-library.com/react) or [Vue Test Utils](https://test-utils.vuejs.org/)
- **E2E**: [Playwright](https://playwright.dev/) or [Cypress](https://www.cypress.io/)

### Go Projects

- **Unit/Integration**: Built-in `testing` package
- **API Testing**: [httptest](https://pkg.go.dev/net/http/httptest)

---

## Coverage Targets

### Minimum Coverage (Definition of Done)
- **Unit Tests**: 80% line coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user workflows

### What to Test

**DO Test** ✅:
- Business logic (calculations, validations)
- API endpoints (request/response)
- Database operations (queries, mutations)
- Error handling (edge cases)
- Critical user flows (E2E)

**DON'T Test** ❌:
- Third-party libraries (assume they work)
- Framework internals (React, Vue, etc.)
- Trivial getters/setters
- Auto-generated code
- Configuration files

---

## Testing Patterns

### Rust Unit Test Pattern

```rust
#[test]
fn calculate_total_adds_item_values() {
    let items = vec![(10, 2), (5, 3)];

    let total = calculate_total(&items);

    assert_eq!(total, 35);
}
```

### Rust Integration Test Pattern

```rust
#[test]
fn command_handles_missing_input() {
    let result = run_command("--input", "");

    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("input is required"));
}
```

### E2E Test Pattern

```typescript
import { test, expect } from '@playwright/test';

test('user can create and complete a task', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.fill('[data-testid="task-input"]', 'Buy groceries');
  await page.click('[data-testid="add-task-button"]');
  await expect(page.locator('[data-testid="task-list"]')).toContainText('Buy groceries');
  await page.click('[data-testid="task-checkbox"]');
  await expect(page.locator('[data-testid="completed-tasks"]')).toContainText('Buy groceries');
});
```

---

## Test Data Management

### Use Test Fixtures

Keep fixtures small, deterministic, and close to the code they exercise.

### Database Testing

- **Approach 1**: In-memory database (SQLite for PostgreSQL-compatible)
- **Approach 2**: Test database with migrations (Docker container)
- **Approach 3**: Transaction rollback (each test in transaction, rollback after)

---

## CI Integration

### Run Tests in CI/CD

**GitHub Actions Example**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          profile: minimal
      - run: cargo test
      - run: make llvm-cov
```

### Quality Gates

- **Minimum Coverage**: 80%
- **No Failing Tests**: All tests must pass
- **Performance**: Test suite completes in <5 minutes

---

## Best Practices

### DO ✅
- Write tests alongside feature code
- Use descriptive test names
- Test error cases and edge cases
- Keep tests simple and focused
- Use fixtures where they reduce setup noise
- Run tests before committing

### DON'T ❌
- Skip tests to "move faster" (technical debt compounds)
- Test implementation details (test behavior, not internals)
- Share state between tests (each test should be independent)
- Use production data in tests
- Ignore flaky tests (fix or remove them)
- Write tests that depend on execution order

---

## Common Testing Mistakes

### Mistake 1: Testing Implementation Instead of Behavior

```rust
// ❌ BAD: Tests implementation detail
#[test]
fn calls_helper_function() {
    assert!(helper_was_called());
}

// ✅ GOOD: Tests behavior
#[test]
fn displays_user_data_after_loading() {
    assert_eq!(rendered_user_name(), "John Doe");
}
```

### Mistake 2: Shared Test State

```rust
// ❌ BAD: Shared state
static mut USER_ID: Option<u32> = None;

// ✅ GOOD: Each test sets up its own data
#[test]
fn updates_user() {
    let user_id = create_user();
    update_user(user_id);
}
```

---

## Resources

### Documentation
- [The Rust Book](https://doc.rust-lang.org/book/)
- [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)
- [cargo llvm-cov](https://github.com/taiki-e/cargo-llvm-cov)
- [Playwright](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)

### Learning
- [Effective Testing](https://effectivetesting.dev/)
- [Test Desiderata](https://kentbeck.github.io/TestDesiderata/) by Kent Beck

---

## Getting Started Checklist

- [ ] Choose testing framework for your stack
- [ ] Set up test runner in your manifest or workspace config
- [ ] Create test directory structure (`tests/` or equivalent)
- [ ] Write first unit test
- [ ] Configure coverage reporting
- [ ] Add tests to CI/CD pipeline
- [ ] Set coverage threshold (80%)
- [ ] Document testing patterns in this file

---

## Test Artifact Archiving

### Convention

Test artifacts produced during development are archived alongside feature specifications at delivery time.

**Standard archive location**: `specs/{NNN}-*/test-results/`

This directory is created automatically by the `/aod.deliver` workflow when test artifacts are confirmed for archival.

### Delivery Workflow Integration

When you run `/aod.deliver`, the skill auto-detects test result files in these locations:

1. `.aod/test-results/` — AOD convention directory
2. `test-results/` — project root
3. `coverage/` — project root
4. `junit*.xml`, `test-report.*`, `coverage.*` — project root files

If files are found, you confirm which to archive. If none are found, you can provide custom paths or skip.

### Supported Formats

| Format | Metric Extraction | Notes |
|--------|-------------------|-------|
| JUnit XML | Automatic (test counts, failures, errors) | Parsed via `xmllint --xpath` |
| LCOV (.info/.lcov) | Automatic (line coverage %) | Parsed via `grep`/`bc` |
| JSON | Manual review | Archived as-is |
| Plain text | Manual review | Archived as-is |
| HTML | Manual review | Archived as-is (test reports, coverage reports) |
| PNG/screenshots | Manual review | Archived as-is (UI test evidence) |

### Size Guidance

- **Individual files**: Keep under 10 MB each
- **Total per feature**: Keep under 50 MB
- **Videos**: Do NOT commit video recordings to git — link externally instead (e.g., cloud storage URL in the delivery document)
- The delivery workflow warns on large files but does not block archival

### Sensitive Data

Review test artifacts for sensitive data before archival:
- API keys and tokens from test fixtures
- PII from test data
- Database credentials from integration test configs

Sanitize or exclude files containing sensitive data. The delivery workflow displays a reminder before archival.

### Example Archive Structure

```
specs/042-user-auth/
├── spec.md
├── plan.md
├── tasks.md
├── delivery.md
└── test-results/
    ├── junit-results.xml      # Unit test results
    ├── e2e-results.xml        # E2E test results
    └── lcov.info              # Coverage report
```

---

**Template Instructions**: This is guidance, not scaffolding. Customize based on your project's testing needs. Add project-specific patterns as you develop them.

**Maintained By**: Architect + Team Lead
**Review Trigger**: When testing patterns change or new frameworks adopted
