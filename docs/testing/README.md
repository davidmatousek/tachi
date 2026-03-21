# Testing Strategy - tachi

**Last Updated**: 2026-03-21
**Owner**: Architect + Team Lead
**Status**: Template

---

## Overview

This document provides guidance on testing strategy for tachi. It does NOT scaffold specific test files (project-specific), but provides recommendations and patterns.

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
- **Mocking**: Mock external dependencies

### Integration Tests (20%)
- **What**: Multiple units working together (API + database)
- **Speed**: <100ms per test
- **Scope**: API endpoints, database operations
- **Mocking**: Minimize (use real database in test mode)

### E2E Tests (10%)
- **What**: Complete user workflows
- **Speed**: <5s per test
- **Scope**: Frontend → Backend → Database
- **Mocking**: None (test production-like environment)

---

## Recommended Testing Frameworks by Project Type

### Frontend Testing

**JavaScript/TypeScript Projects**:
- **Unit/Integration**: [Vitest](https://vitest.dev/) or [Jest](https://jestjs.io/)
- **Component**: [React Testing Library](https://testing-library.com/react) or [Vue Test Utils](https://test-utils.vuejs.org/)
- **E2E**: [Playwright](https://playwright.dev/) or [Cypress](https://www.cypress.io/)

**Example Setup (Vitest + React Testing Library)**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### Backend Testing

**Node.js Projects**:
- **Unit/Integration**: [Vitest](https://vitest.dev/) or [Jest](https://jestjs.io/)
- **API Testing**: [Supertest](https://github.com/ladjs/supertest)

**Python Projects**:
- **Unit/Integration**: [pytest](https://pytest.org/)
- **API Testing**: [httpx](https://www.python-httpx.org/)

**Go Projects**:
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

### Unit Test Pattern

```typescript
// Example: Testing a calculation function
import { describe, it, expect } from 'vitest';
import { calculateTotal } from './utils';

describe('calculateTotal', () => {
  it('calculates total for multiple items', () => {
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 3 }
    ];

    expect(calculateTotal(items)).toBe(35);
  });

  it('returns 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('handles negative quantities', () => {
    const items = [{ price: 10, quantity: -1 }];

    expect(() => calculateTotal(items)).toThrow('Quantity must be positive');
  });
});
```

### Integration Test Pattern (API)

```typescript
// Example: Testing an API endpoint
import { describe, it, expect, beforeEach } from 'vitest';
import { app } from '../src/app';
import { cleanDatabase, seedTestData } from './helpers';

describe('POST /api/tasks', () => {
  beforeEach(async () => {
    await cleanDatabase();
    await seedTestData();
  });

  it('creates a new task', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/tasks',
      payload: {
        title: 'Test Task',
        description: 'Test Description'
      }
    });

    expect(response.statusCode).toBe(201);
    expect(response.json()).toMatchObject({
      title: 'Test Task',
      description: 'Test Description'
    });
  });

  it('validates required fields', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/tasks',
      payload: {} // Missing required fields
    });

    expect(response.statusCode).toBe(400);
    expect(response.json().error).toContain('title is required');
  });
});
```

### E2E Test Pattern (Playwright)

```typescript
// Example: Testing user workflow
import { test, expect } from '@playwright/test';

test('user can create and complete a task', async ({ page }) => {
  // Navigate to application
  await page.goto('http://localhost:3000');

  // Create task
  await page.fill('[data-testid="task-input"]', 'Buy groceries');
  await page.click('[data-testid="add-task-button"]');

  // Verify task appears
  await expect(page.locator('[data-testid="task-list"]')).toContainText('Buy groceries');

  // Complete task
  await page.click('[data-testid="task-checkbox"]');

  // Verify task marked complete
  await expect(page.locator('[data-testid="completed-tasks"]')).toContainText('Buy groceries');
});
```

---

## Test Data Management

### Use Test Fixtures
```typescript
// tests/fixtures/tasks.ts
export const testTasks = [
  {
    id: '1',
    title: 'Test Task 1',
    status: 'pending'
  },
  {
    id: '2',
    title: 'Test Task 2',
    status: 'completed'
  }
];
```

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
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Quality Gates
- **Minimum Coverage**: 80%
- **No Failing Tests**: All tests must pass
- **Performance**: Test suite completes in <5 minutes

---

## Best Practices

### DO ✅
- Write tests alongside feature code
- Use descriptive test names (`it('returns 404 for non-existent task')`)
- Test error cases and edge cases
- Keep tests simple and focused
- Use test data builders/fixtures
- Mock external APIs and services
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
```typescript
// ❌ BAD: Tests implementation
it('calls fetchUserData function', () => {
  const spy = vi.spyOn(api, 'fetchUserData');
  renderComponent();
  expect(spy).toHaveBeenCalled();
});

// ✅ GOOD: Tests behavior
it('displays user data after loading', async () => {
  renderComponent();
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### Mistake 2: Shared Test State
```typescript
// ❌ BAD: Shared state
let userId;

it('creates user', () => {
  userId = createUser();
});

it('updates user', () => {
  updateUser(userId); // Depends on previous test
});

// ✅ GOOD: Independent tests
it('updates user', () => {
  const userId = createUser(); // Each test sets up own data
  updateUser(userId);
});
```

---

## Resources

### Documentation
- [Vitest](https://vitest.dev/)
- [Jest](https://jestjs.io/)
- [Playwright](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [Pytest](https://pytest.org/)

### Learning
- [Testing JavaScript](https://testingjavascript.com/) by Kent C. Dodds
- [Effective Testing](https://effectivetesting.dev/)
- [Test Desiderata](https://kentbeck.github.io/TestDesiderata/) by Kent Beck

---

## Getting Started Checklist

- [ ] Choose testing framework for your stack
- [ ] Set up test runner in package.json
- [ ] Create test directory structure (`tests/` or `__tests__/`)
- [ ] Write first unit test
- [ ] Configure coverage reporting
- [ ] Add tests to CI/CD pipeline
- [ ] Set coverage threshold (80%)
- [ ] Document testing patterns in this file

---

**Template Instructions**: This is guidance, not scaffolding. Customize based on your project's testing needs. Add project-specific patterns as you develop them.

**Maintained By**: Architect + Team Lead
**Review Trigger**: When testing patterns change or new frameworks adopted
