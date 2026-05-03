---
name: kb-create
description: Guided pattern and bug creation with interactive prompts and automatic quality validation. Use this skill when you need to create patterns, document solutions, add KB entries, document bug fixes, save solutions, or create knowledge base entries. Helps users create high-quality KB entries with proper structure, scoring, and categorization. Provides improvement suggestions for entries below quality thresholds.
---

# KB Create Skill

## Purpose

Guided pattern and bug creation with interactive prompts, automatic quality validation, and improvement suggestions. Ensures high-quality KB entries that meet institutional knowledge standards.

## Decision Tree: Pattern vs Bug

```
Should I create a PATTERN or BUG entry?

START: Do you have a reusable solution or specific error fix?
  ↓
Is this a specific error with an exact error message?
  → YES: Is the solution configuration/environment-specific?
    → YES: Create BUG entry
    → NO: Could be either - is it reusable across projects?
      → YES: Create PATTERN
      → NO: Create BUG
  → NO: Is this a general solution to a common problem?
    → YES: Create PATTERN
    → NO: Is it a design decision or architectural guidance?
      → YES: Create PATTERN
      → NO: Maybe not KB-worthy - consider documentation instead
```

**Pattern**: Reusable solutions, design patterns, best practices, architectural guidance
**Bug**: Specific errors with exact error messages, environment issues, configuration fixes

## Pattern Creation Workflow

### Step 1: Collect Basic Information

```
Creating new KB Pattern

Required fields (asterisk = required):

* Title (10-100 characters):
  → Example: "PostgreSQL Connection Pool Optimization"

* Category (select one):
  1. ARCH (Architecture & Design)
  2. DB (Database)
  3. API (API Design)
  4. AUTH (Authentication)
  5. SECURITY (Security)
  6. TEST (Testing)
  7. PERF (Performance)
  8. FRONTEND (Frontend)
  9. INFRA (Infrastructure)
  10. DEPLOY (Deployment)
  11. CACHE (Caching)
  12. MCP (MCP Servers)
  13. CLIENT (Client Integration)
  14. FLOW (Workflows)

  → Your choice (1-14):

* Keywords (min 5, comma-separated):
  → Example: postgresql, connection-pool, optimization, performance, scaling
  → Your keywords:
```

### Step 2: Define Problems Solved

```
* Problems this pattern solves (min 2, max 10):

  Problem 1:
  → Example: Connection pool exhaustion under high load

  Problem 2:
  → Example: Slow query performance due to connection limits

  Problem 3 (or Enter to continue):
  → Example: Connection timeout errors during peak traffic

  ... (continue until Enter on empty line)
```

### Step 3: Write Solution Content

```
Solution Content

Opening your $EDITOR for solution content...

Guidelines:
- Include code examples (min 3 for high quality)
- Explain root cause if applicable
- Provide step-by-step implementation
- Add validation checklist
- Link to related patterns

Template:

## Solution

### Root Cause
[Why does this problem occur?]

### Implementation
```language
[Code example 1]
```

[Explanation]

```language
[Code example 2]
```

### Validation Checklist
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## Related Patterns
- [PATTERN-ID]: Description

## Tags
#tag1 #tag2 #tag3
```

Save and close editor when finished.
```

### Step 4: Add Optional Metadata

```
Optional Metadata (press Enter to skip):

Author (default: Manual):
→ Your name or agent name:

Time to solve (minutes, affects quality score):
→ Example: 120

Complexity (Low/Medium/High):
→ Your choice:

Source (where this came from):
→ Example: Production incident, Code review, Architecture discussion
```

### Step 5: Quality Validation

Automatic quality scoring runs on submission:

```
Quality Score Breakdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Component Scores:
  Complexity: 25/30 pts (time_to_solve: 120 min)
  Reusability: 18/25 pts (problems: 3, keywords: 7)
  Documentation: 24/30 pts (content: 1200 chars, code blocks: 3)
  Impact: 11/15 pts (related: 2, explicit value)

Total Score: 78/100

Decision: ✅ ACCEPTED (Score ≥60)

Pattern created: docs/kb/patterns/DB-005-postgresql-connection-pool.md
Pattern ID: DB-005
```

### Step 6: Handle Quality Result

**ACCEPTED (Score ≥60)**:
```
✅ Pattern Created Successfully!

Pattern: DB-005
Title: PostgreSQL Connection Pool Optimization
Category: DB
Quality Score: 78/100
File: docs/kb/patterns/DB-005-postgresql-connection-pool.md

Your pattern meets quality standards and is ready to use.

Next steps:
1. Pattern automatically indexed (git pre-commit hook)
2. Searchable via: make kb-search QUERY="connection pool"
3. Viewable in: docs/kb/INDEX.md

Would you like to:
- View the pattern? (v)
- Create another pattern? (c)
- Exit? (e)
```

**REVIEW (Score 40-59)**:
```
⚠️ Pattern Created - Needs Review

Pattern: DB-005
Quality Score: 52/100
Decision: REVIEW (usable but needs improvements)

Improvement Suggestions:
1. Add more code examples (current: 1, target: 3+)
2. Increase keyword count (current: 4, target: 8+)
3. Add validation checklist (0 items found)
4. Include related patterns (0 references)
5. Expand problem descriptions (avg: 15 words, target: 30+)

Your pattern is saved but consider improving it.

Would you like to:
- Edit the pattern now? (e)
- Accept as-is? (a)
- Delete and retry? (d)
```

**REJECTED (Score <40)**:
```
❌ Pattern Rejected - Quality Too Low

Pattern: DB-005
Quality Score: 32/100
Decision: REJECTED (below minimum threshold)

Critical Issues:
1. Too few keywords (3, minimum: 5)
2. No code examples (minimum: 1)
3. Content too short (250 chars, target: 500+)
4. Only 1 problem described (minimum: 2)
5. Time to solve too low (15 min, target: 30+ for quality score)

Your pattern was NOT saved.

To improve:
1. Add more specific keywords related to the solution
2. Include at least 1 code example showing implementation
3. Expand solution explanation with more detail
4. Describe at least 2 distinct problems this solves
5. Ensure pattern is substantive (not trivial fixes)

Would you like to:
- Retry with improvements? (r)
- Exit? (e)
```

## Bug Creation Workflow

### Step 1: Bug Information

```
Creating new KB Bug Entry

* Title (concise error description):
  → Example: "PostgreSQL Connection Refused - ECONNREFUSED"

* Error Messages (exact text, min 1):

  Error 1:
  → Example: "Error: connect ECONNREFUSED 127.0.0.1:5432"

  Error 2 (or Enter to continue):
  → Example: "Error: Could not connect to PostgreSQL database"

  ... (continue until Enter on empty line)
```

### Step 2: Symptoms and Context

```
* Symptoms (observable behavior, min 1):

  Symptom 1:
  → Example: "API returns 500 errors on startup"

  Symptom 2 (or Enter to continue):
  → Example: "Health check endpoint fails with database error"

  ... (continue until Enter on empty line)

* Technologies involved (comma-separated):
  → Example: postgresql, docker, nodejs, express
  → Your technologies:
```

### Step 3: Root Cause

```
* Root Cause (20-500 characters):
  → Example: "PostgreSQL container not started before application container. Docker Compose service dependency missing."

  → Your root cause:
```

### Step 4: Fix Classification

```
* Fix Type:
  1. Configuration (environment variables, config files)
  2. Code (logic bugs, missing functionality)
  3. Environment (dependencies, system setup)
  4. Infrastructure (networking, resources, deployment)

  → Your choice (1-4):

* Difficulty:
  1. Easy (< 30 minutes, clear fix)
  2. Medium (30-120 minutes, some investigation)
  3. Hard (> 120 minutes, complex debugging)

  → Your choice (1-3):
```

### Step 5: Fix Steps

```
Fix Steps

Opening your $EDITOR for detailed fix steps...

Guidelines:
- Provide step-by-step instructions
- Include exact commands or code changes
- Explain why the fix works
- Add verification steps

Template:

## Fix Steps

### Immediate Fix

1. Stop the application:
```bash
docker-compose down
```

2. Update docker-compose.yml to add dependency:
```yaml
services:
  app:
    depends_on:
      - db
    # ... rest of config
```

3. Restart with correct order:
```bash
docker-compose up -d
```

### Verification

```bash
# Check PostgreSQL is running
docker-compose ps

# Check application connects successfully
curl http://localhost:3000/health
```

### Prevention

Add health check to docker-compose.yml to ensure DB is ready before app starts.

Save and close editor when finished.
```

### Step 6: Bug Entry Created

```
✅ Bug Entry Created Successfully!

Bug ID: BUG-003
Title: PostgreSQL Connection Refused - ECONNREFUSED
File: docs/kb/bugs/BUG-003-postgresql-connection-refused.md

Your bug fix is documented and searchable.

Search examples:
- make kb-search QUERY="ECONNREFUSED"
- make kb-search QUERY="PostgreSQL connection"
- make kb-search QUERY="docker database startup"

Would you like to:
- View the bug entry? (v)
- Create another bug entry? (c)
- Exit? (e)
```

## Quality Scoring Guide

### High Quality Patterns (Score ≥60)

**Characteristics**:
- Time to solve: ≥60 minutes (indicates substantive problem)
- Keywords: 8+ specific, relevant terms
- Code examples: 3+ working examples with explanations
- Validation checklist: 5+ concrete verification steps
- Problems solved: 3+ distinct, well-described issues
- Content length: 1000+ characters
- Related patterns: 2+ cross-references
- Impact: Explicit business/technical value described

**Example**: Architecture pattern for multi-tenant API design with complete implementation, security considerations, and scaling strategies.

### Medium Quality Patterns (Score 40-59)

**Characteristics**:
- Time to solve: 30-60 minutes
- Keywords: 5-7 terms
- Code examples: 1-2 examples
- Validation checklist: 2-4 items
- Problems solved: 2-3 issues
- Content length: 500-1000 characters
- Related patterns: 1 cross-reference
- Impact: Implied but not explicit

**Example**: Database query optimization pattern with index suggestions and query rewriting examples.

### Low Quality Patterns (Score <40)

**Characteristics**:
- Time to solve: <30 minutes (trivial fix)
- Keywords: <5 terms
- Code examples: 0-1 basic examples
- Validation checklist: 0-1 items
- Problems solved: 1 issue
- Content length: <500 characters
- Related patterns: None
- Impact: Not described

**Example**: "Change variable name from X to Y" - too simple for KB entry.

## Interactive Prompts Example

Full session creating a high-quality pattern:

```
$ make kb-pattern

Creating new KB Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

* Title: JWT Token Refresh Implementation

* Category (1-14): 4
  → Selected: AUTH

* Keywords (min 5): jwt, authentication, token-refresh, oauth, security, session-management, api-client

* Problems this pattern solves:

  Problem 1: JWT tokens expire after 1 hour causing 401 errors
  Problem 2: Users forced to re-login frequently
  Problem 3: API calls fail mid-session without graceful handling

  Problem 4 (Enter to continue):

* Author: senior-backend-engineer

* Time to solve (minutes): 90

* Complexity: Medium

Opening editor for solution content...
[Editor opens with template]

Validating pattern...

Quality Score: 82/100 ✅ ACCEPTED

Pattern created: docs/kb/patterns/AUTH-006-jwt-token-refresh.md

✅ Success! Your high-quality pattern is ready to use.

Next: make kb-search QUERY="JWT refresh"
```

## Error Prevention

### Duplicate Detection

Before creating pattern, checks for similar entries:

```
⚠️ Potential Duplicate Detected

Your pattern "PostgreSQL Connection Pool" is similar to:

1. DB-005: PostgreSQL Pool Optimization (similarity: 85%)
   Keywords overlap: postgresql, connection-pool, optimization
   Problems overlap: 2/3 problems match

Do you want to:
- View existing pattern? (v)
- Continue creating new pattern? (c)
- Cancel? (x)
```

### Missing Required Fields

```
❌ Validation Error

Missing required fields:
- Keywords (provided: 3, minimum: 5)
- Problems (provided: 1, minimum: 2)

Please provide:
- 2 more keywords
- 1 more problem description
```

### Invalid Category

```
❌ Invalid Category

"DATABASE" is not a valid category.

Valid categories:
  1. ARCH    8. FRONTEND
  2. DB      9. INFRA
  3. API    10. DEPLOY
  4. AUTH   11. CACHE
  5. SECURITY 12. MCP
  6. TEST   13. CLIENT
  7. PERF   14. FLOW

Choose number 1-14:
```

## Integration

### Uses
- **Bash**: Execute `make kb-pattern` and `make kb-bug` commands
- **Write**: Create new pattern/bug files
- **Read**: Load templates and examples
- **Edit**: Modify patterns after creation
- **Grep**: Check for duplicates

### Creates
- **docs/kb/patterns/[CATEGORY-NNN]-[slug].md**: Pattern files
- **docs/kb/bugs/BUG-NNN-[slug].md**: Bug fix files

### Updates
- **docs/kb/INDEX.md**: Auto-updated via git hooks
- **.kb-metadata.json**: Cache updated after pattern creation

## Related Skills

- **kb-query**: Search existing patterns before creating duplicates
- **root-cause-analyzer**: Use KB to document 5 Whys analysis results
- **debugger**: Create bug entries after fixing issues

## Tips for High-Quality Patterns

### Choose Meaningful Titles
- Good: "JWT Token Refresh with Retry Logic"
- Bad: "Fix authentication"

### Select Specific Keywords
- Good: jwt, token-refresh, retry, exponential-backoff, oauth
- Bad: auth, fix, code, update, change

### Describe Complete Problems
- Good: "JWT tokens expire after 1 hour causing 401 errors mid-session, requiring users to re-login and lose workflow context"
- Bad: "Auth doesn't work"

### Include Working Code Examples
- Good: Complete, runnable code snippets with explanations
- Bad: Pseudo-code without context

### Add Concrete Validation Steps
- Good: Checklist with specific commands/tests to verify
- Bad: "Make sure it works"

### Link Related Patterns
- Creates knowledge graph
- Helps discovery of related solutions
- Shows pattern evolution

### Explain Root Cause
- Helps understand why problem occurs
- Enables prevention, not just fixes
- Valuable for learning

## Success Criteria

- Pattern creation completes in <5 minutes (interactive mode)
- Quality validation provides actionable feedback
- Improvement suggestions are specific and helpful
- Duplicate detection prevents redundancy
- Interactive prompts guide users to high-quality entries
- Created patterns are immediately searchable

## Workflow Summary

1. **Determine type**: Pattern (reusable) vs Bug (specific error)
2. **Collect information**: Interactive prompts for all required fields
3. **Write content**: Editor opens with template and guidelines
4. **Validate quality**: Automatic scoring with breakdown
5. **Handle result**: Accept/Review/Reject with improvement suggestions
6. **Follow up**: View, edit, or create another entry

## Command Reference

```bash
# Interactive pattern creation
make kb-pattern

# Pattern creation from JSON (for automation)
make kb-pattern JSON=pattern-data.json

# Interactive bug entry creation
make kb-bug

# Bug entry from JSON
make kb-bug JSON=bug-data.json

# Check pattern quality without creating
make kb-validate-pattern FILE=path/to/pattern.md

# View quality scoring guide
make kb-help
```
