---
name: root-cause-analyzer
description: Implements 5 Whys root cause analysis methodology for systematic debugging and problem resolution. Use this skill when you need to find root cause, run 5 whys analysis, analyze recurring problems, or perform systematic debugging. Guides developers through structured analysis, documents findings in institutional knowledge system, and prevents recurring issues.
---

# Root Cause Analyzer Skill

## Purpose

Systematically identifies root causes of complex problems using the 5 Whys methodology from docs/5-WHYS-METHODOLOGY.md. Documents findings in docs/development-learnings/ and updates Knowledge Base (docs/kb/) using `make kb-pattern`. Implements FR-009 from the feature specification.

## Knowledge Base Integration

**IMPORTANT**: Before starting root cause analysis, check the Knowledge Base for existing patterns.

### Pre-Analysis KB Check

```python
from scripts.kb.search import kb_search, kb_get_pattern

# Search for similar issues
results = kb_search(
    query="[error message or symptom]",
    category="[ARCH/DB/API/TEST/etc]",
    min_quality_score=60,
    limit=5
)

if results:
    print(f"Found {len(results)} existing patterns!")
    # Review top pattern
    pattern = kb_get_pattern(results[0].id)
    if pattern:
        # Apply existing solution instead of re-analyzing
        print("Applying existing root cause analysis from KB")
else:
    print("No existing patterns found. Proceeding with new 5 Whys analysis")
```

### When to Check KB

1. **Before starting 5 Whys**: Search for error messages, symptoms, or similar problems
2. **During analysis**: Browse relevant categories (ARCH, DB, API, TEST, ERROR) for design patterns
3. **After finding root cause**: Search again to see if this is a known systemic issue
4. **Before documenting**: Check if similar pattern exists to avoid duplication

### What to Search For

- **Exact error messages**: Copy error text into search query
- **Symptom keywords**: "timeout", "connection pool", "race condition", etc.
- **Technology + problem**: "postgresql connection pool exhausted"
- **Pattern category**: Use category filter to narrow results

### If Pattern Found

1. Review the existing pattern's 5 Whys analysis
2. Check if root cause matches current issue
3. Apply existing solution if applicable
4. Update pattern usage count if applied
5. Add cross-reference in your documentation

### If No Pattern Found

1. Proceed with new 5 Whys analysis
2. After solving, create new KB pattern (if >30 min analysis)
3. Link related patterns using `related_patterns` field
4. Use `make kb-pattern` to create properly formatted pattern

See: [KB-USAGE-GUIDE.md](../../KB-USAGE-GUIDE.md) for detailed search workflow and API reference.

## How It Works

### Step 1: Problem Statement

Guide user to define a clear, specific problem:

```
🔍 Root Cause Analysis

Let's identify the root cause using 5 Whys methodology.

First, describe the problem:
- What happened? (specific, observable event)
- When did it happen? (timestamp, frequency)
- What was the expected behavior?
- What was the actual behavior?

Example:
"Authentication tests fail randomly. Expected: tests pass consistently.
Actual: tests pass 60% of time, fail 40% with timeout errors."
```

### Step 2: Conduct 5 Whys

Ask "Why?" recursively until reaching root cause:

```
## 5 Whys Analysis

Problem: Authentication tests fail randomly (40% failure rate)

### Why #1: Why do the tests fail?
Possible answers:
A. Database connection times out
B. Test data setup incomplete
C. Race condition in test execution

Selected: A (Database connection times out)
Evidence: Error logs show "Connection timeout after 5000ms"

### Why #2: Why does the database connection timeout?
Possible answers:
A. Database is overloaded
B. Connection pool exhausted
C. Network latency high

Selected: B (Connection pool exhausted)
Evidence: Pool size = 5, concurrent tests = 12

### Why #3: Why is the connection pool exhausted?
Possible answers:
A. Pool size too small
B. Connections not released properly
C. Tests running in parallel without coordination

Selected: C (Tests run in parallel without coordination)
Evidence: All tests share single pool, no mutex

### Why #4: Why do tests run in parallel without coordination?
Possible answers:
A. Test runner configured for parallel execution
B. No database connection management strategy
C. Tests written assuming serial execution

Selected: B (No database connection management)
Evidence: No connection cleanup in test setup/teardown

### Why #5: Why is there no connection management?
Possible answers:
A. Missing from initial test setup
B. Developers unaware of need
C. No testing guidelines documented

Selected: A (Missing from initial test setup)
Evidence: Original test template didn't include cleanup

ROOT CAUSE: Test template lacks database connection cleanup patterns,
causing parallel tests to exhaust connection pool.
```

### Step 3: Validation

Verify root cause with counterfactual test:

```
## Root Cause Validation

Question: "If we fix the root cause (add connection cleanup to test
template), will the problem go away?"

Answer: YES
- Adding cleanup will ensure connections released after each test
- This prevents pool exhaustion
- Tests can run in parallel without interference

This confirms we've reached the root cause (not just a symptom).
```

### Step 4: Document Findings

Create learning pattern file:

```markdown
# docs/development-learnings/TEST-003-parallel-test-connection-pool.md

## Problem Statement

Authentication tests failing randomly with 40% failure rate due to
database connection timeouts.

## Root Cause

Test template lacks database connection cleanup patterns, causing
parallel tests to exhaust connection pool (5 connections for 12
concurrent tests).

## 5 Whys Analysis

[Full analysis from above]

## Solutions Proposed

1. **Immediate Fix** (Owner: Developer, Deadline: 2025-10-18)
   - Add connection cleanup to all test files
   - Success Metric: 0% test failures in 100 runs

2. **Preventive Action** (Owner: Team Lead, Deadline: 2025-10-20)
   - Update test template with connection cleanup pattern
   - Document in docs/testing/TESTING-GUIDE.md
   - Success Metric: All new tests include cleanup

3. **Long-term** (Owner: DevOps, Deadline: 2025-10-25)
   - Increase connection pool size for test environment
   - Implement connection pool monitoring
   - Success Metric: Pool utilization <70%

## Related Patterns

- Similar to TEST-001 (fixture cleanup issue)
- Related to DB-002 (connection pool tuning)
```

### Step 5: Update Institutional Knowledge

Add to Knowledge Base using `make kb-pattern`:

```markdown
### TEST-003: Parallel Test Connection Pool Exhaustion

**Symptom**: Random test failures with timeout errors
**Root Cause**: Missing connection cleanup in test template
**Solution**: Add connection cleanup to test setup/teardown
**Prevention**: Update test templates, document in TESTING-GUIDE.md
**Usage Count**: 1
**Last Updated**: 2025-10-17
**Related**: TEST-001, DB-002
```

### Step 6: Create Action Items

Use TodoWrite to track solutions:

```
TODO Items Created:

1. [HIGH] Add connection cleanup to authentication tests (TEST-003)
   Owner: Developer
   Deadline: 2025-10-18

2. [MEDIUM] Update test template with cleanup pattern (TEST-003)
   Owner: Team Lead
   Deadline: 2025-10-20

3. [LOW] Increase test DB connection pool and monitor (TEST-003)
   Owner: DevOps
   Deadline: 2025-10-25
```

## Examples

### Example 1: New Pattern Discovered

**User Query**: "Why does this keep happening? Our API returns 500 errors sporadically."

**Skill Actions**:
1. Guide user through problem statement
2. Conduct 5 Whys - discover missing error handling
3. Validate root cause
4. Create docs/development-learnings/API-004-missing-error-handler.md
5. Update Knowledge Base using `make kb-pattern` or `make kb-bug` with new pattern
6. Create TodoWrite items for fixes

**Result**:
```
✅ Root Cause Analysis Complete

Pattern: API-004-missing-error-handler
Category: Error Handling (ERR-xxx)

Root Cause Found:
Database query errors not caught, causing unhandled exceptions to
propagate as 500 errors.

Solutions Created (3):
1. Add try/catch to all database queries [HIGH]
2. Implement global error handler [MEDIUM]
3. Add error monitoring and alerting [LOW]

Documentation:
- Created: docs/development-learnings/API-004-missing-error-handler.md
- Updated: Knowledge Base (docs/kb/) (added API-004)

This pattern is NEW - added to institutional knowledge system.

Next Steps:
1. Review action items in TodoWrite
2. Implement fixes in priority order
3. Verify solution with testing
```

### Example 2: Existing Pattern Match

**User Query**: "Find root cause of this OAuth timeout issue"

**Skill Actions**:
1. Conduct 5 Whys
2. Discover root cause: token refresh logic missing
3. search Knowledge Base using `make kb-search QUERY="..."`
4. Find existing pattern AUTH-003 (similar issue)
5. Update usage count
6. Provide existing solution

**Result**:
```
✅ Root Cause: Known Pattern Match

Pattern: AUTH-003 (OAuth Token Refresh)
Usage Count: 4 (incremented from 3)

This is a KNOWN ISSUE! Pattern already documented.

Root Cause:
OAuth tokens expire after 1 hour but refresh logic not implemented.

Existing Solution (from AUTH-003):
1. Implement token refresh interceptor in API client
2. Store refresh token securely
3. Auto-refresh on 401 responses

Reference:
docs/development-learnings/AUTH-003-token-refresh.md

Previous Occurrences:
- 2025-09-15: Initial discovery
- 2025-09-22: Same issue in admin panel
- 2025-10-01: Same issue in mobile app
- 2025-10-17: Current occurrence (you)

Prevention:
Add to project onboarding checklist - verify OAuth refresh implemented.
```

## Integration

### Uses

- **Read**: Load docs/5-WHYS-METHODOLOGY.md template
- **Write**: Create pattern files in docs/development-learnings/
- **Grep**: search Knowledge Base using `make kb-search QUERY="..."` for existing patterns
- **Glob**: Find related pattern files
- **TodoWrite**: Create action items for solutions

### Updates

- **docs/development-learnings/**: New pattern files
- **docs/kb/ (Knowledge Base)**: Pattern index and usage counts

### References

- **docs/5-WHYS-METHODOLOGY.md**: Complete methodology guide
- **docs/kb/ (Knowledge Base)**: Pattern index with 21+ patterns
- **docs/development-learnings/**: 21+ documented patterns

## Workflow Template

```markdown
# 5 Whys Root Cause Analysis: [Problem Name]

**Date**: [YYYY-MM-DD]
**Duration**: [X minutes]
**Analyst**: Claude Code (root-cause-analyzer skill)

## Problem Statement

[Specific, measurable problem description]

## 5 Whys Analysis

### Why #1: [Question]
- **Answer**: [Selected answer]
- **Evidence**: [Data/facts]

[Continue for Why #2-5]

### Root Cause
[Final answer - the systemic issue]

## Validation

**Test**: "If we fix this, will problem go away?"
**Answer**: [YES/NO with reasoning]

## Solutions Proposed

1. [Solution 1]
   - **Owner**: [Name]
   - **Deadline**: [Date]
   - **Success Metric**: [How we'll know it worked]

## Related Patterns

[Links to similar patterns]

## Prevention Strategy

[How to prevent this in the future]
```

## Related Skills

- **security-pattern-scanner**: If root cause analysis reveals security vulnerabilities, use this skill to scan for similar patterns across the codebase

## Constitutional Compliance

- **Observability & Root Cause**: Implements Principle VI mandatory root cause analysis
- **Institutional Knowledge**: Builds organizational learning (SC-010: 90%+ capture rate)
- **Problem Prevention**: Documents patterns to prevent recurrence (SC-014: 50%+ duplicate prevention)
- **Systematic Approach**: 5 Whys methodology ensures thorough analysis
