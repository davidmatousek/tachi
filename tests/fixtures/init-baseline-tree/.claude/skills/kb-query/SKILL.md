---
name: kb-query
description: Interactive Knowledge Base search with natural language queries. Use this skill when you need to search KB, find patterns, search knowledge base, look for solutions, find bug fixes, or query institutional knowledge. Searches patterns and bug fixes with relevance ranking, quality scoring, and fuzzy matching for typo tolerance. Helps users find solutions quickly without manual browsing.
---

# KB Query Skill

## Purpose

Interactive Knowledge Base search with natural language queries, providing fast access to institutional knowledge through relevance-ranked results with quality scoring.

## How It Works

### Step 1: Accept Query

User provides search query or problem description:

```
User: "Search KB for database connection pool issues"
```

### Step 2: Execute Search

Run KB search with intelligent parameters:

```bash
# Basic search
make kb-search QUERY="database connection pool"

# With category filter
make kb-search QUERY="JWT authentication" CATEGORY=AUTH

# With quality threshold
make kb-search QUERY="performance optimization" MIN_SCORE=70

# All parameters
make kb-search QUERY="redis cache" CATEGORY=CACHE MIN_SCORE=60 LIMIT=10
```

### Step 3: Display Results

Show top results with relevance and quality scores:

```
Search Results for "database connection pool"

Found 3 patterns:

1. DB-005: PostgreSQL Connection Pool Optimization
   Category: DB | Quality: 85/100 | Relevance: 9.2/10
   Keywords: postgresql, connection-pool, optimization, performance
   Problems solved:
   - Connection pool exhaustion under load
   - Slow query performance due to connection limits

2. PERF-002: Connection Pool Tuning Guide
   Category: PERF | Quality: 78/100 | Relevance: 8.5/10
   Keywords: connection-pool, tuning, performance, scalability
   Problems solved:
   - Optimizing pool size for workload
   - Monitoring pool utilization

3. DB-002: Database Connection Retry Logic
   Category: DB | Quality: 72/100 | Relevance: 7.1/10
   Keywords: database, connection, retry, error-handling
   Problems solved:
   - Transient connection failures
   - Graceful degradation on DB issues
```

### Step 4: Offer Actions

Interactive follow-up options:

```
Actions:
1. View full content of a pattern (enter 1-3)
2. Search with different parameters
3. Browse by category
4. Exit

Your choice:
```

### Step 5: View Full Content (if requested)

Display complete pattern details:

```bash
# Read full pattern file
cat docs/kb/patterns/DB-005-postgresql-connection-pool.md
```

Show structured content:

```markdown
# DB-005: PostgreSQL Connection Pool Optimization

## Metadata
- Category: DB
- Quality Score: 85/100
- Created: 2025-10-15
- Author: senior-backend-engineer
- Time to solve: 120 minutes
- Complexity: Medium

## Problems This Solves
1. Connection pool exhaustion under load
2. Slow query performance due to connection limits
3. Connection timeout errors during peak traffic

## Solution

### Root Cause
Connection pool size (default: 10) insufficient for concurrent load (50+ requests/sec).

### Implementation
```javascript
// PostgreSQL pool configuration
const pool = new Pool({
  max: 50,              // Increase from default 10
  min: 10,              // Maintain minimum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});

// Add pool monitoring
pool.on('error', (err, client) => {
  console.error('Pool error:', err);
});
```

### Validation Checklist
- [ ] Pool size matches concurrent request load
- [ ] Idle timeout configured to prevent stale connections
- [ ] Connection timeout set for fail-fast behavior
- [ ] Pool monitoring/alerting enabled
- [ ] Load testing confirms no exhaustion

## Related Patterns
- PERF-002: Connection Pool Tuning Guide
- DB-002: Database Connection Retry Logic
- INFRA-003: Database Scaling Strategies

## Tags
#postgresql #connection-pool #optimization #performance #database
```

## Search Parameters

### Query (Required)
Natural language search terms:
- Error messages: "ECONNREFUSED"
- Problem descriptions: "slow database queries"
- Technology + issue: "JWT token expired"
- Keywords: "authentication", "caching", "optimization"

### Category (Optional)
Filter by specific category:
- **ARCH**: Architecture and design patterns
- **DB**: Database patterns
- **API**: API design and integration
- **AUTH**: Authentication and authorization
- **SECURITY**: Security best practices
- **TEST**: Testing patterns
- **PERF**: Performance optimization
- **FRONTEND**: Frontend patterns
- **INFRA**: Infrastructure patterns
- **DEPLOY**: Deployment patterns
- **CACHE**: Caching strategies
- **MCP**: MCP server patterns
- **CLIENT**: Client integration patterns
- **FLOW**: Workflow and process patterns

### MIN_SCORE (Optional)
Minimum quality score (0-100):
- **80+**: Exceptional quality (comprehensive, validated)
- **60-79**: High quality (production-ready)
- **40-59**: Medium quality (usable, may need improvements)
- **<40**: Low quality (review before use)

Default: 60 (high quality only)

### LIMIT (Optional)
Maximum results to return (default: 5)

### Fuzzy Matching
Automatically enabled for typo tolerance:
- "databse" → "database"
- "authentiction" → "authentication"
- "conection" → "connection"

## Examples

### Example 1: Database Error Search

**Query**: "ECONNREFUSED connecting to PostgreSQL"

**Command**:
```bash
make kb-search QUERY="ECONNREFUSED PostgreSQL" CATEGORY=DB
```

**Results**:
```
Found 2 results:

1. BUG-002: PostgreSQL Connection Refused
   Type: Bug Fix | Relevance: 9.5/10
   Error: ECONNREFUSED, Could not connect to PostgreSQL
   Technologies: postgresql, docker, networking
   Fix Type: Configuration | Difficulty: Easy

2. DB-002: Database Connection Retry Logic
   Category: DB | Quality: 72/100 | Relevance: 6.8/10
   Keywords: database, connection, retry, error-handling
```

**Action**: View BUG-002 for exact fix steps

### Example 2: Architecture Pattern Discovery

**Query**: "How to structure API endpoints for multi-tenant app"

**Command**:
```bash
make kb-search QUERY="multi-tenant API architecture" CATEGORY=ARCH MIN_SCORE=70
```

**Results**:
```
Found 3 patterns:

1. ARCH-004: Multi-Tenant API Design Patterns
   Category: ARCH | Quality: 88/100 | Relevance: 9.7/10

2. API-007: Tenant Isolation Strategies
   Category: API | Quality: 82/100 | Relevance: 8.9/10

3. DB-011: Multi-Tenant Database Schema Design
   Category: DB | Quality: 76/100 | Relevance: 7.5/10
```

**Action**: View ARCH-004 for comprehensive design approach

### Example 3: No Results Found

**Query**: "quantum blockchain AI optimization"

**Command**:
```bash
make kb-search QUERY="quantum blockchain AI" MIN_SCORE=60
```

**Results**:
```
No results found for "quantum blockchain AI"

Suggestions:
1. Try broader search terms
2. Remove technical jargon
3. Search by specific error message
4. Browse categories: make kb-help
5. Create new pattern: make kb-pattern

Would you like to:
- Retry search with different terms? (r)
- Browse by category? (b)
- Create new pattern? (c)
- Exit? (e)
```

### Example 4: Category Browse

**Query**: "Show all authentication patterns"

**Command**:
```bash
make kb-search QUERY="*" CATEGORY=AUTH
```

**Results**:
```
All AUTH patterns (7 total):

1. AUTH-001: JWT Token Authentication
   Quality: 92/100 | Problems: 3 | Code examples: 5

2. AUTH-003: OAuth 2.0 Implementation
   Quality: 88/100 | Problems: 4 | Code examples: 7

3. AUTH-005: Session Management Best Practices
   Quality: 85/100 | Problems: 3 | Code examples: 4

... (4 more patterns)
```

## Error Handling

### No Results
```
No results found for "your query"

This might mean:
- Pattern doesn't exist yet - create one with `make kb-pattern`
- Query too specific - try broader terms
- Typo in category name - available: ARCH, DB, API, AUTH, etc.
```

### KB Not Indexed
```
Error: KB index not found

Run: make kb-index

This will scan all patterns and build the search index.
```

### Invalid Category
```
Error: Invalid category "DATABAS"

Valid categories:
ARCH, DB, API, AUTH, SECURITY, TEST, PERF, FRONTEND,
INFRA, DEPLOY, CACHE, MCP, CLIENT, FLOW

Example: make kb-search QUERY="your query" CATEGORY=DB
```

## Integration

### Uses
- **Bash**: Execute `make kb-search` commands
- **Read**: Display full pattern content
- **Grep**: Find related patterns by keyword
- **Glob**: Browse patterns by category

### References
- **docs/kb/KB.md**: KB quick start guide
- **docs/kb/INDEX.md**: Organized pattern index
- **docs/agents/KB-USAGE-GUIDE.md**: Search workflow and API reference

## Related Skills

- **kb-create**: Create new patterns after search fails
- **root-cause-analyzer**: Use KB results during 5 Whys analysis
- **debugger**: Search KB before debugging

## Workflow Summary

1. **Accept user query** (natural language or keywords)
2. **Execute KB search** with appropriate parameters
3. **Display top 3-5 results** with scores and metadata
4. **Offer interactive actions**:
   - View full content
   - Refine search
   - Browse categories
   - Create new pattern (if no results)
5. **Follow up** based on user choice

## Tips for Effective Searching

### Use Specific Keywords
- Good: "JWT token expired 401"
- Bad: "authentication doesn't work"

### Include Technology Names
- Good: "PostgreSQL connection pool exhaustion"
- Bad: "database is slow"

### Copy Exact Error Messages
- Good: "ECONNREFUSED"
- Bad: "connection error"

### Filter by Category
- Narrows results to relevant domain
- Faster than browsing all patterns

### Adjust Quality Threshold
- Start with MIN_SCORE=60 (default)
- Lower to 40 for broader results
- Raise to 80 for only best patterns

## Success Criteria

- Search completes in <3 seconds
- Relevance ranking surfaces best match first
- Quality scores help assess pattern reliability
- Fuzzy matching handles typos gracefully
- Interactive actions provide clear next steps
- Error messages are actionable and helpful
