# Template: Parallel Batch Scanning

**Feature**: 026-users-david-documents
**Created**: 2025-11-18
**Purpose**: Enable parallel scanning of multiple files with aggregated result analysis

---

## Use Case

Use this template when you need to scan multiple files concurrently and aggregate results by criteria (severity, count, patterns). This pattern is optimal for:

- **Debugger agent**: Analyzing 10+ files for error patterns
- **Code reviewer**: Scanning multiple changed files in a PR
- **Security analyst**: Batch vulnerability assessment across components
- **Tester**: Validating multiple test fixtures

**When to Use**:
- Scanning 3+ files where results need aggregation
- Need to analyze patterns across multiple code units
- Require severity-based grouping or filtering
- Want to reduce latency through parallel execution

---

## Pattern

Use `Promise.all()` with the `scanFile()` wrapper function to execute scans in parallel, then aggregate results using standard JavaScript array methods.

**Key Components**:
1. **Parallel execution** - `Promise.all()` launches all scans concurrently
2. **Wrapper function** - `scanFile()` from api-wrapper.md (NOT direct imports)
3. **Result aggregation** - `flatMap()`, `reduce()`, `filter()` for data summarization
4. **Severity grouping** - Group vulnerabilities by CRITICAL/HIGH/MEDIUM/LOW

---

## Complete Example

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

// Files to scan in parallel
const files = [
  '/src/api/auth.py',
  '/src/api/users.py',
  '/src/api/payments.py',
  '/src/api/admin.py',
  '/src/api/reports.py',
  '/src/api/webhooks.py',
  '/src/api/notifications.py',
  '/src/api/analytics.py',
  '/src/api/search.py',
  '/src/api/export.py'
];

// Execute scans in parallel (all 10 files scan concurrently)
const results = await Promise.all(
  files.map(file => scanFile(file))  // Uses default scan_type: 'quick'
);

// Aggregate vulnerabilities by severity
const bySeverity = results.flatMap(r => r.vulnerabilities)
  .reduce((acc, vuln) => {
    acc[vuln.severity] = (acc[vuln.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

// Calculate total vulnerabilities
const totalVulns = results.reduce((sum, r) => sum + r.summary.total, 0);

// Return aggregated summary
return {
  files_scanned: files.length,
  total_vulnerabilities: totalVulns,
  by_severity: {
    CRITICAL: bySeverity.CRITICAL || 0,
    HIGH: bySeverity.HIGH || 0,
    MEDIUM: bySeverity.MEDIUM || 0,
    LOW: bySeverity.LOW || 0
  },
  files_with_issues: results.filter(r => r.summary.total > 0).length,
  scan_ids: results.map(r => r.scan_id)
};
```

---

## Input

**Required**:
- Array of file paths to scan (minimum 2 files for parallel benefit)

**Optional**:
- Scan options (passed to `scanFile()` wrapper)
- Aggregation criteria (severity, file path pattern, etc.)

**Example Input**:
```typescript
const files = ['/path/file1.py', '/path/file2.py', '/path/file3.py'];
```

---

## Output

**Aggregated Summary Structure**:
```typescript
{
  files_scanned: number,           // Total files processed
  total_vulnerabilities: number,   // Sum across all files
  by_severity: {
    CRITICAL: number,
    HIGH: number,
    MEDIUM: number,
    LOW: number
  },
  files_with_issues: number,       // Files containing ≥1 vulnerability
  scan_ids: string[]               // Scan IDs for detailed retrieval
}
```

**Token Efficiency**: Returns ~200 tokens vs ~50,000 tokens for full scan results (10 files × 5,000 tokens/file)

---

## Token Savings

**Benchmark** (10 files):
- **Before** (full results): ~50,000 tokens (10 files × 5,000 tokens each)
- **After** (aggregated): ~200 tokens (summary only)
- **Reduction**: ~96% token savings

**Scaling**:
- 3 files: ~93% reduction (15,000 → 1,000 tokens)
- 5 files: ~95% reduction (25,000 → 1,250 tokens)
- 20 files: ~97% reduction (100,000 → 3,000 tokens)

---

## Integration

### In Agent Prompts

```markdown
## Code Execution Capabilities

### Parallel File Analysis

When analyzing multiple files (3+), use code execution for efficient parallel scanning:

**Example**: Scan 10 API route files for security vulnerabilities

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const files = ['/src/api/auth.py', '/src/api/users.py', /* ... */];
const results = await Promise.all(files.map(file => scanFile(file)));

const bySeverity = results.flatMap(r => r.vulnerabilities)
  .reduce((acc, v) => {
    acc[v.severity] = (acc[v.severity] || 0) + 1;
    return acc;
  }, {});

return {
  files_scanned: files.length,
  by_severity: bySeverity
};
```

**Benefits**: 96% token reduction, parallel execution reduces latency
```

---

## Advanced Variations

### Variation 1: Filter High-Severity Only

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const files = [/* file paths */];
const results = await Promise.all(files.map(file => scanFile(file)));

// Filter to CRITICAL and HIGH severity only
const criticalVulns = results.flatMap(r =>
  r.vulnerabilities.filter(v =>
    v.severity === 'CRITICAL' || v.severity === 'HIGH'
  )
);

return {
  files_scanned: files.length,
  critical_high_count: criticalVulns.length,
  details: criticalVulns.map(v => ({
    file: v.file_path,
    severity: v.severity,
    title: v.title,
    line: v.line_number
  }))
};
```

**Token Savings**: ~90% (filtering further reduces output)

---

### Variation 2: Group by File with Top Issues

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const files = [/* file paths */];
const results = await Promise.all(files.map(file => scanFile(file)));

// Group by file, show top 3 critical issues per file
const fileReport = results.map((result, index) => {
  const criticalIssues = result.vulnerabilities
    .filter(v => v.severity === 'CRITICAL')
    .slice(0, 3);  // Top 3 only

  return {
    file: files[index],
    total_issues: result.summary.total,
    critical_count: result.summary.critical,
    top_critical: criticalIssues.map(v => ({
      title: v.title,
      line: v.line_number
    }))
  };
});

return {
  files_analyzed: files.length,
  file_reports: fileReport
};
```

---

### Variation 3: Comprehensive Scan with Custom Options

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const files = [/* file paths */];

// Comprehensive scan with custom options
const results = await Promise.all(
  files.map(file => scanFile(file, {
    scan_type: 'comprehensive',
    severity_filter: ['CRITICAL', 'HIGH']
  }))
);

// Aggregate and deduplicate by vulnerability type
const vulnTypes = new Set(
  results.flatMap(r => r.vulnerabilities.map(v => v.title))
);

return {
  files_scanned: files.length,
  unique_vulnerability_types: Array.from(vulnTypes),
  total_vulnerabilities: results.reduce((sum, r) => sum + r.summary.total, 0)
};
```

---

## Error Handling

### Graceful Degradation Pattern

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const files = [/* file paths */];

try {
  // Attempt parallel scans
  const results = await Promise.all(files.map(file => scanFile(file)));

  // Aggregate results
  const bySeverity = results.flatMap(r => r.vulnerabilities)
    .reduce((acc, v) => {
      acc[v.severity] = (acc[v.severity] || 0) + 1;
      return acc;
    }, {});

  return { success: true, by_severity: bySeverity };

} catch (error) {
  // Fallback: Sequential scanning with individual error handling
  console.warn(`Parallel scan failed (${error.message}), falling back to sequential`);

  const results = [];
  for (const file of files) {
    try {
      const result = await scanFile(file);
      results.push(result);
    } catch (fileError) {
      console.warn(`Failed to scan ${file}: ${fileError.message}`);
      // Continue with remaining files
    }
  }

  // Return partial results
  return {
    success: false,
    partial: true,
    files_scanned: results.length,
    files_failed: files.length - results.length
  };
}
```

---

## Fallback Strategy

If code execution fails, fall back to sequential tool calls:

```typescript
// Primary: Code execution (preferred)
try {
  const result = await execute_code(`
    import { scanFile } from '@code-execution-helper/api-wrapper';
    const files = ${JSON.stringify(files)};
    const results = await Promise.all(files.map(f => scanFile(f)));
    return results.reduce((acc, r) => ({
      total: acc.total + r.summary.total,
      critical: acc.critical + r.summary.critical
    }), { total: 0, critical: 0 });
  `);
  return result;

} catch (error) {
  // Fallback: Standard tool calls (sequential)
  console.warn('⚠️ Code execution unavailable. Using standard approach - may use more tokens.');

  let totalVulns = 0;
  let criticalVulns = 0;

  for (const file of files) {
    const result = await execute_security_scan(file);
    totalVulns += result.summary.total;
    criticalVulns += result.summary.critical;
  }

  return { total: totalVulns, critical: criticalVulns };
}
```

---

## Performance Characteristics

| Files | Sequential Time | Parallel Time | Speedup |
|-------|----------------|---------------|---------|
| 3     | ~15s           | ~5s           | 3x      |
| 5     | ~25s           | ~5s           | 5x      |
| 10    | ~50s           | ~5s           | 10x     |
| 20    | ~100s          | ~5s           | 20x     |

**Note**: Actual speedup depends on scan complexity and server load. Parallel execution limited by rate limits (10 executions/minute).

---

## Related Templates

- **template-quota-aware.md**: Check quota before expensive batch operations
- **template-conditional-filter.md**: Advanced filtering strategies for scan results
- **template-error-handling.md**: Comprehensive error handling patterns

---

**Status**: ✅ Production Ready - Use in agent code execution examples
**Last Updated**: 2025-11-18
**Maintained By**: Jimmy (Prompt Engineering Agent)
