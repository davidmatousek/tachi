---
name: code-execution-helper
description: Guide for using code execution capabilities to perform parallel batch processing, conditional filtering, and data aggregation. This skill should be used when agents need to analyze multiple files efficiently, validate large result sets, aggregate data from multiple sources, or reduce token consumption through execution-based filtering. Provides reusable templates for quota-aware workflows, error handling patterns, and token-efficient data processing.
---

# Code Execution Helper

This skill provides guidance for using code execution capabilities efficiently in Claude Code workflow agents. Code execution enables agents to perform parallel batch processing, conditional filtering, and data aggregation while dramatically reducing token consumption.

## About Code Execution

Code execution allows agents to run TypeScript code in a sandboxed Deno runtime, enabling operations that would otherwise require loading massive amounts of data into context. By processing data in the execution environment and returning only filtered or aggregated results, agents can achieve 30-95% token reduction for high-value use cases.

### Key Benefits

1. **Parallel batch processing** - Scan 10+ files simultaneously instead of sequentially
2. **Conditional filtering** - Return only relevant data (e.g., CRITICAL vulnerabilities only)
3. **Data aggregation** - Summarize patterns across multiple sources
4. **Token efficiency** - Process large datasets without context window limits
5. **Quota awareness** - Check API limits before execution to prevent failures

### When to Use Code Execution

Use code execution when tasks meet these criteria:

- **Multiple operations**: More than 5 files, API calls, or validation checks
- **Large datasets**: Results exceed 10,000 tokens if loaded into context
- **Conditional logic**: Need to filter, aggregate, or transform data before returning
- **Parallel processing**: Operations can run simultaneously for faster execution
- **Token efficiency**: Reducing context usage is important for the workflow

### When NOT to Use Code Execution

Avoid code execution for:

- **Single operations**: One file scan, one API call, simple queries
- **Small datasets**: Results under 2,000 tokens
- **Direct responses**: User needs raw data without filtering
- **Simple queries**: Questions answerable with existing tools
- **Debugging code execution itself**: Use direct tools to avoid recursion

## Decision Criteria

To determine whether to use code execution, apply these thresholds:

1. **File count**: Use execution for 6+ files, direct tools for 5 or fewer
2. **Result size**: Use execution if unfiltered results exceed 10,000 tokens
3. **Validation checks**: Use execution for 3+ acceptance criteria in parallel
4. **API calls**: Use execution for 4+ parallel requests
5. **Filtering needed**: Use execution if returning <20% of raw data

## Available Capabilities

### Parallel Batch Scanning

Analyze multiple files simultaneously using the security scanner:

- Scan 10-50 files in parallel (limited by quota and rate limits)
- Aggregate vulnerability patterns across files
- Filter by severity before returning results
- Token reduction: 85-95% for large codebases

**Example use cases**:
- Debugger analyzing error patterns across 10+ API files
- Code reviewer scanning changed files in large PRs
- Security analyst identifying vulnerabilities across modules

### Quota-Aware Workflows

Check API quota before execution to prevent failures:

- Verify available quota matches operation needs
- Return graceful error if quota insufficient
- Track quota consumption across agent workflows
- Prevent partial execution failures

**Example use cases**:
- Tester validating 5 acceptance criteria (check quota first)
- Web researcher aggregating data from multiple sources
- AOD orchestrator coordinating multi-agent workflows

### Conditional Filtering

Process data in execution environment and return only relevant results:

- Filter by severity (CRITICAL/HIGH only)
- Return pass/fail boolean instead of full results
- Provide detailed output only when failures occur
- Summarize patterns instead of listing all instances

**Example use cases**:
- Tester validating scan results (return boolean, not 20,000 token dataset)
- Code reviewer showing only security-relevant changes
- Senior backend engineer identifying N+1 queries (return recommendations only)

### Error Handling

Implement fallback strategies when code execution fails:

- Catch execution errors and fall back to direct tools
- Handle timeout errors by reducing batch size
- Validate syntax before execution to prevent failures
- Log errors for debugging while maintaining functionality

**Example use cases**:
- All agents when code execution unavailable or fails
- Backward compatibility when Feature 025 disabled
- Graceful degradation under rate limiting

## API Abstraction Layer

All code execution examples must use the API abstraction layer defined in `references/api-wrapper.md`. This wrapper provides:

- **Type-safe function signatures** for all MCP tools
- **Consistent error handling** across agents
- **Simplified imports** (no direct `@ai-security/*` dependencies)
- **Future-proof API** (changes to MCP tools isolated to wrapper)

**IMPORTANT**: Never use direct `@ai-security/*` imports in code execution examples. Always use wrapper functions: `scanFile()`, `checkQuota()`, `getHealth()`, `getScanHistory()`.

## Progressive Disclosure: Templates and References

This skill uses progressive disclosure to manage context efficiently:

1. **SKILL.md** (this file) - Overview, decision criteria, when to use
2. **references/api-wrapper.md** - API abstraction layer with wrapper functions
3. **references/api-reference.md** - TypeScript API module specifications
4. **references/template-parallel-batch.md** - Parallel batch scanning template
5. **references/template-quota-aware.md** - Quota-aware workflow template
6. **references/template-conditional-filter.md** - Conditional filtering template
7. **references/template-error-handling.md** - Error handling and fallback template

To access templates, read the relevant reference file when implementing specific patterns. This keeps the skill lean while providing detailed guidance when needed.

## Integration Patterns by Agent

### Full Integration (3-5 examples per agent)

Agents with high-value code execution use cases:

- **Debugger** - Parallel file analysis, cross-file pattern detection
- **Tester** - Validation filtering, batch acceptance criteria checks
- **Code Reviewer** - Diff-aware scanning, severity-based filtering
- **Senior Backend Engineer** - Query pattern analysis, performance optimization
- **Architect** - Technology validation, compatibility testing
- **Web Researcher** - Multi-source aggregation, data processing

### Medium Integration (1-2 examples + skill reference)

Agents with focused code execution use cases:

- **Security Analyst** - Parallel vulnerability scanning, severity filtering
- **Code Monkey** - Component scanning, batch validation
- **DevOps** - Health check aggregation, configuration validation
- **AOD Orchestrator** - Quota checking, agent coordination

### Minimal Integration (documentation only)

Agents with limited code execution use cases:

- **Head Honcho** - Documentation awareness only
- **UX/UI Designer** - Documentation awareness only
- **Jimmy** - Documentation awareness only

## Workflow Guidance

### Step 1: Determine if Code Execution is Appropriate

Apply decision criteria (see "Decision Criteria" section above):

- Count operations (files, API calls, validations)
- Estimate token usage without filtering
- Identify filtering or aggregation needs
- Check for parallel processing opportunities

### Step 2: Choose the Right Template

Based on the use case:

- **Parallel processing** → `template-parallel-batch.md`
- **Quota checking** → `template-quota-aware.md`
- **Filtering/aggregation** → `template-conditional-filter.md`
- **Error handling** → `template-error-handling.md`

### Step 3: Use API Wrapper Functions

Always use wrapper functions from `api-wrapper.md`:

- `scanFile(filePath: string)` - Scan single file
- `checkQuota()` - Check available API quota
- `getHealth()` - Check system health
- `getScanHistory()` - Retrieve scan history

### Step 4: Implement Fallback Strategy

Every code execution block must include:

- Error handling (try/catch)
- Fallback to direct tools if execution fails
- Timeout handling (reduce batch size if needed)
- Graceful error messages to user

### Step 5: Document Token Savings

When using code execution, explain to the user:

- What operation was performed
- How many tokens were saved (vs loading full results)
- What filtering or aggregation was applied
- What the output represents

## Example: Parallel Batch Scanning

This example demonstrates scanning multiple files in parallel and aggregating results:

```typescript
// Scan 10 API files in parallel and return aggregated error patterns
const { scanFile } = await import('./references/api-wrapper.md');

const files = [
  'src/api/auth.ts',
  'src/api/users.ts',
  'src/api/posts.ts',
  // ... 7 more files
];

// Scan all files in parallel
const results = await Promise.all(
  files.map(file => scanFile(file))
);

// Aggregate CRITICAL/HIGH vulnerabilities only
const criticalIssues = results
  .flatMap(r => r.vulnerabilities)
  .filter(v => v.severity === 'CRITICAL' || v.severity === 'HIGH')
  .slice(0, 10); // Return top 10 only

// Return summary
return {
  totalFiles: files.length,
  totalVulnerabilities: results.reduce((sum, r) => sum + r.vulnerabilities.length, 0),
  criticalIssues,
  tokenSavings: '95% (500 tokens vs 10,000 tokens for full results)'
};
```

**Token savings**: This approach uses ~500 tokens instead of ~10,000 tokens (95% reduction) by filtering to critical issues only.

## Example: Quota-Aware Workflow

This example demonstrates checking quota before execution:

```typescript
// Check quota before scanning 5 files
const { checkQuota, scanFile } = await import('./references/api-wrapper.md');

// Check available quota
const quota = await checkQuota();

if (quota.remaining < 5) {
  return {
    error: 'Insufficient quota',
    available: quota.remaining,
    needed: 5,
    message: 'Need 5 scans but only ' + quota.remaining + ' available. Try again later.'
  };
}

// Quota sufficient, proceed with scans
const files = ['auth.ts', 'users.ts', 'posts.ts', 'comments.ts', 'api.ts'];
const results = await Promise.all(files.map(scanFile));

return { success: true, scanned: files.length, results };
```

**Benefit**: Prevents partial execution failures by validating quota upfront.

## Example: Conditional Filtering

This example demonstrates returning different detail levels based on findings:

```typescript
// Scan and return detailed results only if CRITICAL found
const { scanFile } = await import('./references/api-wrapper.md');

const result = await scanFile('src/api/auth.ts');

const critical = result.vulnerabilities.filter(v => v.severity === 'CRITICAL');

if (critical.length > 0) {
  // CRITICAL found - return detailed analysis
  return {
    status: 'FAIL',
    critical: critical.map(v => ({
      type: v.type,
      line: v.line,
      description: v.description,
      remediation: v.remediation
    })),
    tokenSavings: '90% (detailed output only when needed)'
  };
} else {
  // No CRITICAL - return summary only
  return {
    status: 'PASS',
    summary: `Scan complete. ${result.vulnerabilities.length} total issues, none CRITICAL.`,
    tokenSavings: '95% (summary instead of full results)'
  };
}
```

**Token savings**: This approach uses ~500 tokens when passing (vs ~5,000 for full results), and ~2,000 tokens when failing (vs ~10,000 for unfiltered output).

## Rate Limits and Constraints

Code execution operates under these constraints:

- **Rate limit**: 10 executions per minute per user (20/minute requested for power users)
- **Timeout**: 30 seconds maximum execution time
- **Quota**: API calls (executeScan) consume user quota independently
- **Sandboxing**: Deno runtime with security constraints (network access limited)
- **Allowed imports**: Only TypeScript API modules from Feature 025 are available

To stay within limits:

- Batch operations into single execution when possible
- Check quota before large operations
- Reduce batch size if timeout occurs
- Implement exponential backoff for rate limit errors

## Troubleshooting

### Code Execution Fails

**Symptom**: Execution error returned instead of results

**Solutions**:
1. Check syntax using Deno syntax validation
2. Verify wrapper function imports are correct
3. Reduce batch size if timeout occurred
4. Fall back to direct tools
5. Check rate limit status (10/minute)

### Quota Insufficient

**Symptom**: API calls fail with quota error even though execution succeeds

**Solutions**:
1. Use quota-aware workflow template
2. Check quota before execution with `checkQuota()`
3. Return graceful error message to user
4. Suggest user try again later or upgrade quota

### Token Savings Not Achieved

**Symptom**: Code execution used but token count still high

**Solutions**:
1. Verify filtering logic is applied before returning
2. Return summary statistics instead of raw data
3. Use conditional detail levels (detailed only when needed)
4. Limit result count (e.g., top 10 instead of all 500)

### Syntax Errors

**Symptom**: TypeScript syntax validation fails

**Solutions**:
1. Use wrapper functions from `api-wrapper.md` (no direct imports)
2. Validate TypeScript syntax with Deno before execution
3. Check for typos in function names
4. Verify all async functions use `await`

## Token Reduction Benchmarks

Expected token savings by use case:

- **Parallel batch scanning** (10+ files): 85-95% reduction
- **Validation filtering** (boolean results): 90-98% reduction
- **Diff-aware scanning** (large PRs): 85-92% reduction
- **Conditional filtering** (severity-based): 80-95% reduction
- **Data aggregation** (multi-source): 70-85% reduction
- **Quota-aware workflows**: 5-10% overhead (worth it to prevent failures)

These benchmarks assume proper filtering and aggregation are implemented. Raw data dumps from code execution provide zero token savings.

## Best Practices

1. **Always filter before returning** - Process data in execution environment, return only what user needs
2. **Check quota for batch operations** - Prevent partial execution failures
3. **Implement fallback strategies** - Maintain backward compatibility
4. **Document token savings** - Explain efficiency gains to users
5. **Use wrapper functions** - Never import `@ai-security/*` directly
6. **Limit result counts** - Return top N instead of all results
7. **Conditional detail levels** - Detailed output only when necessary
8. **Validate syntax first** - Catch errors before execution
9. **Respect rate limits** - Batch operations to stay under 10/minute
10. **Measure and iterate** - Track actual token savings and optimize

## Further Reading

For detailed implementation guidance, read these reference files as needed:

- `references/api-wrapper.md` - API abstraction layer (required reading)
- `references/api-reference.md` - TypeScript API specifications
- `references/template-parallel-batch.md` - Parallel processing patterns
- `references/template-quota-aware.md` - Quota management strategies
- `references/template-conditional-filter.md` - Filtering and aggregation techniques
- `references/template-error-handling.md` - Error handling and fallback strategy
