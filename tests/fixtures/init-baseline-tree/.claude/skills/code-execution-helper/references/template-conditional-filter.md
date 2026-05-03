# Template: Conditional Filtering

**Feature**: 026-users-david-documents
**Created**: 2025-11-18
**Purpose**: Enable intelligent filtering of scan results to return only relevant data, maximizing token efficiency

---

## Use Case

Use this template when you need to scan files but only return results matching specific criteria. This pattern dramatically reduces token consumption by filtering data before it enters the context window.

**Optimal For**:
- **Tester agent**: Validate specific conditions (e.g., "at least 1 CRITICAL found")
- **Code reviewer**: Return only security issues in changed files
- **Security analyst**: Filter by severity, vulnerability type, or file patterns
- **Debugger**: Find specific error patterns across multiple files

**When to Use**:
- Need specific subset of scan results (severity, keyword, pattern)
- Boolean validation (pass/fail without details)
- Aggregated statistics instead of full data
- Results filtered by file path, line range, or vulnerability type

---

## Pattern

Execute scan using `scanFile()` wrapper, apply filter criteria using JavaScript array methods, return only matching subset.

**Key Components**:
1. **Scan execution** - `scanFile()` from api-wrapper.md
2. **Filter criteria** - Severity, keyword, regex, count threshold, file pattern
3. **Array filtering** - `filter()`, `some()`, `every()`, `find()`
4. **Conditional returns** - Return different detail levels based on filter matches
5. **Aggregation** - Count, sum, group by before returning

---

## Complete Example

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

// Execute scan
const results = await scanFile('/path/to/repo');

// Filter 1: Only CRITICAL severity vulnerabilities
const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

// Filter 2: Only vulnerabilities in auth-related files
const authIssues = critical.filter(v =>
  v.file_path.includes('/auth') ||
  v.file_path.includes('/authentication') ||
  v.file_path.includes('/login')
);

// Filter 3: Only specific vulnerability patterns
const authPatterns = authIssues.filter(v =>
  v.title.includes('injection') ||
  v.title.includes('authentication') ||
  v.title.includes('authorization')
);

// Return filtered subset with minimal details
return {
  scan_id: results.scan_id,
  total_vulnerabilities: results.summary.total,
  critical_count: results.summary.critical,
  auth_critical_count: authPatterns.length,
  findings: authPatterns.map(v => ({
    file: v.file_path,
    line: v.line_number,
    title: v.title,
    severity: v.severity
  }))
};
```

---

## Input

**Required**:
- File or repository path to scan
- Filter criteria (severity, keywords, patterns, etc.)

**Optional**:
- Multiple filter conditions (chain filters)
- Output detail level (summary, titles only, full details)
- Aggregation type (count, group by, unique)

**Example Filter Criteria**:
```typescript
// Severity filter
const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

// Keyword filter
const sqlInjection = results.vulnerabilities.filter(v =>
  v.title.toLowerCase().includes('sql injection')
);

// Regex filter
const sensitiveFiles = results.vulnerabilities.filter(v =>
  /\/(config|secrets|\.env)\//.test(v.file_path)
);

// Count threshold filter
const highRiskFiles = results.vulnerabilities
  .reduce((acc, v) => {
    acc[v.file_path] = (acc[v.file_path] || 0) + 1;
    return acc;
  }, {});
const filesWithMany = Object.entries(highRiskFiles)
  .filter(([_, count]) => count >= 3);
```

---

## Output

### Example 1: Severity Filter (CRITICAL only)

```typescript
{
  scan_id: "scan_abc123",
  total_vulnerabilities: 45,
  critical_count: 3,
  critical_details: [
    {
      file: "/src/auth/login.py",
      line: 42,
      title: "SQL Injection in login handler",
      severity: "CRITICAL"
    },
    {
      file: "/src/api/users.py",
      line: 128,
      title: "Command injection in user export",
      severity: "CRITICAL"
    },
    {
      file: "/src/payments/process.py",
      line: 67,
      title: "Insecure deserialization",
      severity: "CRITICAL"
    }
  ]
}
```

**Token Efficiency**: ~500 tokens vs ~12,500 tokens (full 45 vulnerabilities)

---

### Example 2: Boolean Validation

```typescript
{
  validation_passed: false,
  reason: "Found 2 CRITICAL vulnerabilities in auth module",
  critical_count: 2,
  acceptance_criteria: "0 CRITICAL vulnerabilities",
  scan_id: "scan_abc123"
}
```

**Token Efficiency**: ~100 tokens vs ~12,500 tokens (97% reduction)

---

### Example 3: Aggregated Statistics

```typescript
{
  scan_id: "scan_abc123",
  file_summary: {
    total_files_scanned: 42,
    files_with_critical: 3,
    files_with_high: 8,
    files_with_any_issues: 15,
    clean_files: 27
  },
  top_issues: [
    { type: "SQL Injection", count: 5 },
    { type: "XSS", count: 3 },
    { type: "Path Traversal", count: 2 }
  ]
}
```

**Token Efficiency**: ~250 tokens vs ~12,500 tokens (98% reduction)

---

## Token Savings

**Benchmark** (45 vulnerabilities total):
- **Before** (full results): ~12,500 tokens (45 vulns × ~280 tokens each)
- **After** (CRITICAL only, 3 vulns): ~840 tokens (3 vulns × ~280 tokens)
- **After** (boolean validation): ~100 tokens (minimal response)
- **After** (aggregated stats): ~250 tokens (summary only)
- **Reduction**: 90-98% depending on filter selectivity

**Scaling by Selectivity**:
- 10% match (5/50 vulns): ~86% reduction (14,000 → 2,000 tokens)
- 5% match (2/40 vulns): ~93% reduction (11,200 → 800 tokens)
- 1% match (1/100 vulns): ~97% reduction (28,000 → 840 tokens)

---

## Integration

### In Agent Prompts

```markdown
## Code Execution Capabilities

### Conditional Filtering for Validation

When validating scan results, filter to only relevant data:

**Example**: Check if any CRITICAL vulnerabilities exist in auth module

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const results = await scanFile('/repo');
const criticalAuth = results.vulnerabilities.filter(v =>
  v.severity === 'CRITICAL' &&
  v.file_path.includes('/auth')
);

return {
  validation_passed: criticalAuth.length === 0,
  critical_count: criticalAuth.length
};
```

**Benefits**: 97% token reduction, clear pass/fail result
```

---

## Advanced Variations

### Variation 1: Multi-Condition Filter

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const results = await scanFile('/path/to/repo');

// Complex filter: CRITICAL or HIGH severity, in specific files, with specific patterns
const filtered = results.vulnerabilities.filter(v =>
  (v.severity === 'CRITICAL' || v.severity === 'HIGH') &&
  (v.file_path.includes('/api/') || v.file_path.includes('/auth/')) &&
  (v.title.includes('injection') || v.title.includes('deserialization'))
);

return {
  total_scanned: results.summary.total,
  matched_criteria: filtered.length,
  findings: filtered.map(v => ({
    severity: v.severity,
    file: v.file_path,
    issue: v.title,
    line: v.line_number
  }))
};
```

---

### Variation 2: Conditional Detail Level

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const results = await scanFile('/path/to/repo');

const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

// Return different detail levels based on findings
if (critical.length === 0) {
  // Pass: Minimal response
  return {
    status: 'PASS',
    message: 'No critical vulnerabilities found',
    total_issues: results.summary.total
  };
} else if (critical.length <= 3) {
  // Few issues: Return details
  return {
    status: 'FAIL',
    critical_count: critical.length,
    details: critical.map(v => ({
      file: v.file_path,
      line: v.line_number,
      title: v.title,
      remediation: v.remediation
    }))
  };
} else {
  // Many issues: Return summary only
  return {
    status: 'FAIL',
    critical_count: critical.length,
    message: 'Multiple critical issues found',
    files_affected: [...new Set(critical.map(v => v.file_path))],
    recommendation: 'Run detailed scan for full list'
  };
}
```

---

### Variation 3: Keyword and Regex Filtering

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const results = await scanFile('/path/to/repo');

// Filter by keywords
const keywords = ['sql injection', 'xss', 'command injection', 'path traversal'];
const keywordMatches = results.vulnerabilities.filter(v =>
  keywords.some(k => v.title.toLowerCase().includes(k))
);

// Filter by regex pattern
const sensitiveFilePattern = /\/(config|secrets|\.env|keys|passwords)\//;
const sensitiveFileIssues = keywordMatches.filter(v =>
  sensitiveFilePattern.test(v.file_path)
);

// Group by vulnerability type
const grouped = sensitiveFileIssues.reduce((acc, v) => {
  const type = v.title.split(' ')[0];  // Extract first word as type
  if (!acc[type]) acc[type] = [];
  acc[type].push({
    file: v.file_path,
    line: v.line_number
  });
  return acc;
}, {});

return {
  total_vulnerabilities: results.summary.total,
  sensitive_file_issues: sensitiveFileIssues.length,
  by_type: grouped
};
```

---

### Variation 4: Threshold-Based Filtering

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

const results = await scanFile('/path/to/repo');

// Count vulnerabilities per file
const fileCounts = results.vulnerabilities.reduce((acc, v) => {
  acc[v.file_path] = (acc[v.file_path] || 0) + 1;
  return acc;
}, {});

// Filter files with 3+ vulnerabilities
const THRESHOLD = 3;
const highRiskFiles = Object.entries(fileCounts)
  .filter(([_, count]) => count >= THRESHOLD)
  .map(([path, count]) => ({ path, count }))
  .sort((a, b) => b.count - a.count);

return {
  total_files_scanned: Object.keys(fileCounts).length,
  high_risk_files: highRiskFiles.length,
  threshold: THRESHOLD,
  details: highRiskFiles.slice(0, 5).map(f => ({
    file: f.path,
    vulnerability_count: f.count
  }))
};
```

---

### Variation 5: Changed Files Only (Code Review)

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

// Changed files in PR (from git diff)
const changedFiles = [
  '/src/api/users.py',
  '/src/auth/login.py',
  '/src/models/user.py'
];

// Scan entire repo
const results = await scanFile('/path/to/repo');

// Filter to only vulnerabilities in changed files
const changedFileIssues = results.vulnerabilities.filter(v =>
  changedFiles.some(changed => v.file_path.includes(changed))
);

// Group by file
const byFile = changedFileIssues.reduce((acc, v) => {
  if (!acc[v.file_path]) acc[v.file_path] = [];
  acc[v.file_path].push({
    severity: v.severity,
    line: v.line_number,
    title: v.title
  });
  return acc;
}, {});

return {
  changed_files: changedFiles.length,
  files_with_new_issues: Object.keys(byFile).length,
  new_issues_count: changedFileIssues.length,
  by_file: byFile
};
```

---

## Error Handling

### Graceful Degradation Pattern

```typescript
import { scanFile } from '@code-execution-helper/api-wrapper';

try {
  // Execute scan
  const results = await scanFile('/path/to/repo');

  // Apply filters
  const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

  return {
    success: true,
    critical_count: critical.length,
    findings: critical
  };

} catch (error) {
  // Handle scan failure
  if (error.error_type === 'TimeoutError') {
    console.warn('Scan timeout - trying quick scan instead');

    // Fallback: Quick scan with aggressive filtering
    const quickResults = await scanFile('/path/to/repo', {
      scan_type: 'quick',
      severity_filter: ['CRITICAL']
    });

    return {
      success: true,
      mode: 'quick_scan_fallback',
      critical_count: quickResults.summary.critical
    };
  }

  // Cannot recover - return error
  return {
    success: false,
    error: error.error_type || 'UnknownError',
    message: error.message
  };
}
```

---

## Fallback Strategy

If code execution fails, use direct tool with manual filtering:

```typescript
// Primary: Code execution with filtering (preferred)
try {
  const result = await execute_code(`
    import { scanFile } from '@code-execution-helper/api-wrapper';
    const results = await scanFile('/path');
    const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');
    return { critical_count: critical.length, findings: critical };
  `);
  return result;

} catch (error) {
  // Fallback: Standard tool with post-processing
  console.warn('⚠️ Code execution unavailable. Using standard approach - may use more tokens.');

  const results = await execute_security_scan('/path');

  // Manual filtering in agent context (uses more tokens)
  const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

  return {
    mode: 'fallback',
    critical_count: critical.length,
    findings: critical
  };
}
```

---

## Performance Characteristics

| Filter Selectivity | Input Vulns | Output Vulns | Token Reduction |
|-------------------|-------------|--------------|-----------------|
| Very selective (1%) | 100 | 1 | 97% |
| Selective (5%) | 100 | 5 | 93% |
| Moderate (20%) | 100 | 20 | 75% |
| Permissive (50%) | 100 | 50 | 40% |

**Recommendation**: Combine multiple filters to achieve <10% selectivity for maximum token savings.

---

## Related Templates

- **template-parallel-batch.md**: Combine with parallel scanning for multi-file filtering
- **template-quota-aware.md**: Use filtering to reduce quota consumption
- **template-error-handling.md**: Add error handling to filter operations

---

**Status**: ✅ Production Ready - Use in all agent validation and filtering workflows
**Last Updated**: 2025-11-18
**Maintained By**: Jimmy (Prompt Engineering Agent)
