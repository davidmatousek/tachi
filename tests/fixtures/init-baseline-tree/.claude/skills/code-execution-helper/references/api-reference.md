# API Reference - TypeScript Modules

**Feature**: 026-users-david-documents (Agent Code Execution Integration)
**Source**: Feature 025 MCP Code Execution Implementation
**Last Updated**: 2025-11-18

This document provides comprehensive API reference for TypeScript modules available in the code execution environment.

---

## Table of Contents

- [Security Constraints](#security-constraints)
- [Context Variables](#context-variables)
- [Module: @ai-security/scan](#module-ai-securityscan)
- [Module: @ai-security/api](#module-ai-securityapi)
- [Module: @ai-security/health](#module-ai-securityhealth)
- [Error Handling Patterns](#error-handling-patterns)
- [Rate Limits](#rate-limits)

---

## Security Constraints

All code executed in the code execution environment is subject to strict security validation:

### Allowed Imports
- **Only `@ai-security/*` modules are permitted**
- Standard TypeScript syntax and built-in types
- No external npm packages

### Forbidden Patterns
The following patterns are **strictly prohibited** and will result in validation errors:

- `eval()` - Dynamic code evaluation
- `Function()` - Dynamic function construction
- `require()` - CommonJS imports
- `Deno.run` - Process execution
- `Deno.env` - Environment variable access
- Dynamic imports (e.g., `import(variable)`)
- `new Function()`
- `setTimeout()` with string argument
- `setInterval()` with string argument

### Resource Limits

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| **Execution Timeout** | 30 seconds | Hard limit, execution terminated |
| **Memory Usage** | 256 MB | Hard limit, execution terminated |
| **Code Size** | 100 KB | Validation error before execution |
| **Concurrent Executions** | 10 per user | Rate limit enforcement |

### Rate Limits

| Limit Type | Value | Scope |
|------------|-------|-------|
| **Executions per minute** | 10 | Per user ID |
| **Concurrent executions** | 10 | Per user ID |
| **Quota consumption** | Varies by scan type | Per user tier |

**Rate Limit Exceeded Response**:
```json
{
  "error": "RateLimitExceeded",
  "message": "Too many requests. Please try again in 45 seconds.",
  "retry_after": 45
}
```

---

## Context Variables

User code has access to the `__context__` object with the following properties:

### `__context__.userId`
- **Type**: `string`
- **Description**: Current authenticated user ID
- **Usage**: Required for quota checks, scan history retrieval
- **Example**: `"user_abc123"`

### `__context__.allowedTools`
- **Type**: `string[] | null`
- **Description**: Array of restricted tool names, or `null` for all tools allowed
- **Usage**: Tool access control (advanced use cases)
- **Example**: `["executeScan", "getHistory"]` or `null`

**Important**: API keys are NOT exposed to user code. Authentication is handled securely by the bridge server.

**Example Usage**:
```typescript
import { getUsage } from '@ai-security/api';

// Use context variables for user-specific operations
const usage = await getUsage(__context__.userId);
console.log(`User ${__context__.userId} has ${usage.quota_remaining} scans remaining`);
```

---

## Module: @ai-security/scan

Security scanning operations for code repositories and files.

### Function: `executeScan(path, options?)`

Execute a security scan on a target code repository or file.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | `string` | ✅ Yes | Absolute path to code file or repository to scan |
| `options` | `ScanOptions` | ❌ No | Scan configuration options |

**ScanOptions Interface**:
```typescript
interface ScanOptions {
  scan_type?: 'quick' | 'full';           // Default: 'full'
  agent_filters?: string[];                // Filter specific agents (e.g., ['ASI-01'])
  output_format?: 'summary' | 'detailed' | 'json';  // Default: 'detailed'
  include_context?: boolean;               // Include code context (default: true)
}
```

#### Return Type

```typescript
interface ScanResult {
  scan_id: string;
  status: 'completed' | 'in_progress' | 'failed';
  summary: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  vulnerabilities: Vulnerability[];
}

interface Vulnerability {
  id: string;
  agent_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  file_path: string;
  line_number: number;
  code_snippet: string;
  remediation: string;
}
```

#### Examples

##### Example 1: Basic Scan
```typescript
import { executeScan } from '@ai-security/scan';

const results = await executeScan('/path/to/repo');

return {
  total_vulnerabilities: results.summary.total,
  critical_count: results.summary.critical,
  scan_id: results.scan_id
};
```

##### Example 2: Quick Scan with Filtering
```typescript
import { executeScan } from '@ai-security/scan';

const results = await executeScan('/path/to/repo', {
  scan_type: 'quick',
  agent_filters: ['ASI-01', 'LLM-03']
});

// Return only critical vulnerabilities
const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

return {
  total: results.summary.total,
  critical_vulnerabilities: critical,
  token_reduction: `${Math.round((1 - critical.length / results.summary.total) * 100)}%`
};
```

**Token Savings**: Filtering critical-only can achieve ~90% token reduction (from 12,500 to ~1,250 tokens).

##### Example 3: Batch Parallel Scanning
```typescript
import { executeScan } from '@ai-security/scan';

const files = ['/src/auth.py', '/src/api.py', '/src/db.py'];

// Scan multiple files in parallel
const results = await Promise.all(
  files.map(file => executeScan(file, { scan_type: 'quick' }))
);

// Aggregate by severity
const bySeverity = results.flatMap(r => r.vulnerabilities)
  .reduce((acc, v) => {
    acc[v.severity] = (acc[v.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

return {
  files_scanned: files.length,
  vulnerabilities_by_severity: bySeverity,
  total_vulnerabilities: results.reduce((sum, r) => sum + r.summary.total, 0)
};
```

**Token Savings**: Aggregated summary instead of full results achieves ~96% reduction.

---

### Function: `getHistory(userId, limit?)`

Retrieve user's scan history with metadata and vulnerability counts.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | `string` | ✅ Yes | User ID to retrieve history for (use `__context__.userId`) |
| `limit` | `number` | ❌ No | Maximum number of scans to return (default: 10, max: 100) |

#### Return Type

```typescript
interface ScanHistory {
  total_count: number;
  scans: ScanHistoryItem[];
}

interface ScanHistoryItem {
  scan_id: string;
  status: 'completed' | 'in_progress' | 'failed';
  created_at: string;  // ISO 8601 timestamp
  total_vulnerabilities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  target_path: string;
}
```

#### Examples

##### Example 1: Recent Scans
```typescript
import { getHistory } from '@ai-security/scan';

const history = await getHistory(__context__.userId, 10);

return {
  total_scans: history.total_count,
  recent_scans: history.scans.map(s => ({
    scan_id: s.scan_id,
    date: s.created_at,
    vulnerabilities: s.total_vulnerabilities
  }))
};
```

##### Example 2: Trend Analysis
```typescript
import { getHistory } from '@ai-security/scan';

const history = await getHistory(__context__.userId, 50);

// Filter scans with critical vulnerabilities
const criticalScans = history.scans.filter(s => s.critical_count > 0);
const totalCritical = criticalScans.reduce((sum, s) => sum + s.critical_count, 0);

return {
  total_scans: history.total_count,
  scans_with_critical: criticalScans.length,
  total_critical_issues: totalCritical,
  average_critical_per_scan: Math.round(totalCritical / criticalScans.length * 10) / 10,
  most_recent_critical: criticalScans[0]?.scan_id
};
```

**Token Savings**: Aggregated statistics instead of 50 full records achieves ~96% reduction (from 20,000 to ~800 tokens).

---

## Module: @ai-security/api

User account operations including quota management and API key validation.

### Function: `getUsage(userId)`

Retrieve user usage statistics and quota information.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | `string` | ✅ Yes | User ID to get usage for (use `__context__.userId`) |

#### Return Type

```typescript
interface UserUsage {
  user_id: string;
  tier: 'free' | 'professional' | 'enterprise';
  daily_scans: number;
  monthly_scans: number;
  quota_remaining: number;
  quota_limit: number;
  reset_date: string;  // ISO 8601 timestamp
  metrics: {
    average_vulnerabilities_per_scan: number;
    most_common_severity: 'critical' | 'high' | 'medium' | 'low';
  };
}
```

#### Examples

##### Example 1: Check Quota Before Scan
```typescript
import { getUsage } from '@ai-security/api';
import { executeScan } from '@ai-security/scan';

const usage = await getUsage(__context__.userId);

if (usage.quota_remaining < 100) {
  return {
    error: 'Insufficient quota',
    remaining: usage.quota_remaining,
    required: 100,
    reset_date: usage.reset_date
  };
}

// Proceed with expensive operation
const results = await executeScan('/repo', { scan_type: 'full' });

return {
  scanned: true,
  vulnerabilities: results.summary.total,
  quota_after: usage.quota_remaining - 100
};
```

**Token Savings**: ~95% (avoided returning full scan results when quota insufficient).

##### Example 2: Usage Summary
```typescript
import { getUsage } from '@ai-security/api';

const usage = await getUsage(__context__.userId);

return {
  tier: usage.tier,
  usage_percentage: Math.round((1 - usage.quota_remaining / usage.quota_limit) * 100),
  scans_this_month: usage.monthly_scans,
  quota_remaining: usage.quota_remaining,
  reset_date: usage.reset_date
};
```

---

### Function: `validateKey(apiKey)`

Validate API key and retrieve user information.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `apiKey` | `string` | ✅ Yes | API key to validate |

#### Return Type

```typescript
interface KeyValidation {
  valid: boolean;
  user_id: string;
  tier: 'free' | 'professional' | 'enterprise';
  quota_remaining: number;
  quota_limit: number;
  reset_date: string;  // ISO 8601 timestamp
}
```

#### Example

```typescript
import { validateKey } from '@ai-security/api';

const validation = await validateKey('ask_live_abc123');

if (!validation.valid) {
  return { error: 'Invalid API key' };
}

return {
  user_id: validation.user_id,
  tier: validation.tier,
  quota_available: validation.quota_remaining > 0
};
```

**Note**: This function is primarily for administrative workflows. Most agent code should use `__context__.userId` instead of validating API keys directly.

---

## Module: @ai-security/health

Service health monitoring and status checks.

### Function: `checkStatus()`

Check AI Security Scanner service health status.

#### Parameters

None required.

#### Return Type

```typescript
interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  service_uptime: number;  // Seconds since service start
  database_connected: boolean;
  agents: {
    healthy: string[];   // Agent IDs (e.g., ['ASI-01', 'LLM-03'])
    failed: string[];
  };
  metrics: {
    average_scan_time_ms: number;
    requests_per_minute: number;
    error_rate: number;  // Percentage (0-100)
  };
}
```

#### Examples

##### Example 1: Basic Health Check
```typescript
import { checkStatus } from '@ai-security/health';

const health = await checkStatus();

return {
  is_operational: health.status === 'healthy' && health.database_connected,
  status: health.status,
  agents_healthy: health.agents.healthy.length,
  agents_total: health.agents.healthy.length + health.agents.failed.length
};
```

**Token Savings**: ~90% (essential status only instead of full health details).

##### Example 2: Detailed Status Report
```typescript
import { checkStatus } from '@ai-security/health';

const health = await checkStatus();

return {
  status: health.status,
  version: health.version,
  uptime_hours: Math.round(health.service_uptime / 3600),
  database_ok: health.database_connected,
  agent_status: {
    healthy: health.agents.healthy,
    failed: health.agents.failed
  },
  performance: {
    avg_scan_time_ms: health.metrics.average_scan_time_ms,
    error_rate: health.metrics.error_rate
  }
};
```

---

## Error Handling Patterns

All TypeScript API functions can throw errors. Always wrap tool calls in try-catch blocks.

### Common Error Types

#### ValidationError
Thrown when code violates security constraints or has syntax errors.

```typescript
{
  "error_type": "ValidationError",
  "message": "Forbidden pattern detected: eval()",
  "details": "Line 3: eval() is not allowed"
}
```

#### TimeoutError
Thrown when execution exceeds 30-second timeout.

```typescript
{
  "error_type": "TimeoutError",
  "message": "Execution exceeded 30 second timeout",
  "execution_time_ms": 30000
}
```

#### ExecutionError
Thrown when runtime errors occur in user code.

```typescript
{
  "error_type": "ExecutionError",
  "message": "TypeError: Cannot read property 'length' of undefined",
  "stack_trace": "..."
}
```

#### RateLimitError
Thrown when rate limits are exceeded.

```typescript
{
  "error_type": "RateLimitError",
  "message": "Too many requests. Please try again in 45 seconds.",
  "retry_after": 45
}
```

#### QuotaExceededError
Thrown when user has insufficient quota.

```typescript
{
  "error_type": "QuotaExceededError",
  "message": "Insufficient quota. Required: 100, Available: 50",
  "required": 100,
  "available": 50,
  "reset_date": "2025-12-01T00:00:00Z"
}
```

### Recommended Error Handling Pattern

```typescript
import { executeScan } from '@ai-security/scan';

try {
  const results = await executeScan('/path/to/repo');
  return results;
} catch (error) {
  // Graceful degradation
  return {
    error: true,
    error_type: error.error_type || 'UnknownError',
    message: error.message,
    fallback_action: 'Check logs for details or retry later'
  };
}
```

### Best Practices

1. **Always use try-catch blocks** for all tool calls
2. **Return structured error objects** with actionable information
3. **Include fallback strategies** for error scenarios
4. **Log errors** for monitoring and debugging using `console.log()`
5. **Validate inputs** before calling API functions
6. **Handle quota errors gracefully** by checking usage before expensive operations
7. **Implement retry logic** for transient errors (rate limits, timeouts)

---

## Complete Example: Token-Efficient Workflow

This example demonstrates best practices combining multiple API modules:

```typescript
import { getUsage } from '@ai-security/api';
import { executeScan } from '@ai-security/scan';
import { checkStatus } from '@ai-security/health';

// Step 1: Check service health
const health = await checkStatus();
if (health.status !== 'healthy') {
  return {
    error: 'Service unavailable',
    status: health.status,
    message: 'Please try again later'
  };
}

// Step 2: Check user quota
const usage = await getUsage(__context__.userId);
if (usage.quota_remaining < 100) {
  return {
    error: 'Insufficient quota',
    remaining: usage.quota_remaining,
    reset_date: usage.reset_date
  };
}

// Step 3: Execute scan with error handling
try {
  const results = await executeScan('/path/to/repo', { scan_type: 'full' });

  // Step 4: Filter and return only critical vulnerabilities
  const critical = results.vulnerabilities.filter(v => v.severity === 'CRITICAL');

  return {
    scan_id: results.scan_id,
    total_vulnerabilities: results.summary.total,
    critical_count: critical.length,
    critical_vulnerabilities: critical,
    quota_remaining: usage.quota_remaining - 100,
    token_savings: `~${Math.round((1 - critical.length / results.summary.total) * 100)}%`
  };
} catch (error) {
  return {
    error: true,
    error_type: error.error_type,
    message: error.message,
    quota_not_consumed: true  // Scan failed, quota preserved
  };
}
```

**Token Savings**: This workflow can achieve 90-95% token reduction compared to returning full scan results directly.

---

## Support Resources

- **Full MCP Tools Reference**: `docs/api/mcp-tools-reference.md`
- **Code Execution Examples**: `docs/api/code-execution-examples.md`
- **Troubleshooting Guide**: `docs/troubleshooting/code-execution-errors.md`
- **API Wrapper Functions**: `.claude/skills/code-execution-helper/references/api-wrapper.md`

For additional support:
- Documentation: https://docs.ai-security-scanner.com
- Email: support@ai-security-scanner.com
- Status Page: https://status.ai-security-scanner.com
