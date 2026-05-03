---
name: tachi-denial-of-service
description: "STRIDE denial of service threat agent that detects availability degradation threats against Processes, Data Stores, and Data Flows, covering resource exhaustion, algorithmic complexity attacks, connection pool exhaustion, and cascading dependency failures."
---

## Metadata

```yaml
category: stride
threat_class: D
dfd_targets: [Process, Data Store, Data Flow]
owasp_references:
  - "OWASP Application Denial of Service Cheat Sheet"
  - "OWASP API Security 2023 API4 — Unrestricted Resource Consumption"
  - "CWE-400: Uncontrolled Resource Consumption"
  - "CWE-770: Allocation of Resources Without Limits or Throttling"
  - "CWE-502: Deserialization of Untrusted Data"
  - "MITRE ATT&CK T1498: Network Denial of Service"
  - "MITRE ATT&CK T1499: Endpoint Denial of Service"
output_schema: ../../../schemas/finding.yaml
```

# Denial of Service Threat Agent

## Purpose

Detects threats where an attacker degrades or eliminates system availability — through resource exhaustion, flooding, algorithmic complexity exploitation, or cascading dependency failures. Denial of service undermines availability guarantees, causing service outages, degraded performance, or data loss from overwhelmed storage. This agent targets Processes (where compute or memory exhaustion halts operations), Data Stores (where storage saturation or lock contention blocks access), and Data Flows (where bandwidth saturation or connection pool exhaustion prevents communication).

## Detection Scope

### Targeted DFD Element Types

- **Process**: API endpoints, background workers, data processing pipelines, authentication services, webhook receivers
- **Data Store**: Databases, caches, message queues, file storage, search indexes
- **Data Flow**: Network connections, API calls, message bus channels, file upload streams, WebSocket connections

### Patterns and Indicators

**Resource Exhaustion**
- Endpoints accepting unbounded input sizes (request body, file uploads, query parameters)
- Missing request size limits on API gateways or reverse proxies
- Memory-intensive operations triggered by unauthenticated requests
- CPU-intensive computations (regex, compression, encryption) on user-controlled input
- Thread pool exhaustion from long-running synchronous operations

**Algorithmic Complexity Attacks**
- Regular expressions vulnerable to ReDoS (catastrophic backtracking)
- Hash collision attacks on hash table implementations
- XML parsing vulnerable to billion laughs (entity expansion) or quadratic blowup
- JSON parsing without depth or size limits
- Recursive algorithms on user-controlled data without depth bounds

**Database and Storage Saturation**
- Queries without result limits allowing full table scans
- Missing pagination on list endpoints enabling massive result sets
- Write-heavy endpoints without rate limiting enabling storage flooding
- Missing TTL on cache entries enabling memory exhaustion
- Log volume from user-triggerable events filling disk storage

**Connection and Pool Exhaustion**
- Database connection pools without timeouts or maximum size limits
- HTTP client connections without read/write timeouts
- WebSocket connections without idle timeout or per-client limits
- File descriptor exhaustion from unclosed connections or handles
- Thread pool starvation from blocking I/O on async paths

**Dependency and Cascade Failures**
- Missing circuit breakers on calls to external services
- Retry storms from aggressive retry policies without backoff
- Synchronous dependency chains where one slow service blocks all upstream callers
- Missing fallback behavior when optional dependencies are unavailable
- Health check endpoints that call downstream services (creating cascading failures)

**Application-Layer Attacks**
- HTTP flood attacks targeting computationally expensive endpoints (search, report generation, export)
- Slowloris-style attacks holding connections open with partial HTTP requests
- API abuse through high-frequency polling of expensive queries without caching
- GraphQL complexity attacks using deeply nested or aliased queries to amplify server workload
- Multipart upload abuse sending many small concurrent uploads to exhaust file descriptor limits

**Infrastructure-Layer Attacks**
- DNS amplification targeting service discovery endpoints
- SYN flood attacks exhausting TCP connection tables on load balancers
- TLS renegotiation attacks consuming CPU on TLS termination endpoints
- Missing DDoS protection at CDN or API gateway layer for public-facing services
- UDP/ICMP flood attacks saturating network bandwidth before reaching application layer

**Flooding and Abuse**
- Missing rate limiting on public-facing endpoints
- Missing rate limiting differentiation between authenticated and anonymous traffic
- Account creation or password reset endpoints without CAPTCHA or proof-of-work
- Webhook receivers without sender verification enabling forged flood attacks
- Missing IP-based throttling for unauthenticated endpoints

## Finding Template

Each finding produced by this agent conforms to `../../../schemas/finding.yaml` with the following field guidance:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Sequential identifier with D prefix | `D-1` |
| `category` | Always `denial-of-service` | `denial-of-service` |
| `component` | Name of the Process, Data Store, or Data Flow under analysis | `LLM Agent Orchestrator` |
| `threat` | Specific availability threat description — what resource is exhausted, how, and what service impact results | `Attacker sends concurrent requests with maximum-length prompts to the LLM Agent Orchestrator because no per-client rate limit or request size cap is enforced, exhausting memory and compute budget and blocking legitimate orchestration requests` |
| `likelihood` | Assessed using OWASP factors: ease of exploit (often low-skill), attacker tooling availability, exposure surface | `HIGH` |
| `impact` | Assessed using OWASP factors: availability loss duration, blast radius (single service vs system-wide), data loss potential | `HIGH` |
| `risk_level` | Computed from OWASP 3x3 matrix (likelihood x impact) | `Critical` |
| `mitigation` | Actionable countermeasure — specific limit, timeout, circuit breaker, or scaling mechanism | `Enforce per-client rate limit of 10 requests/minute on the orchestrator endpoint; cap prompt input at 4096 tokens; configure request timeout at 30 seconds with circuit breaker after 5 consecutive failures; set memory limit at 1GB per worker with OOM-kill restart policy` |
| `references` | OWASP, CWE, MITRE ATT&CK, or CVE identifiers supporting the finding | `["CWE-400", "ATT&CK T1499"]` |
| `dfd_element_type` | DFD classification of the target component | `Process`, `Data Store`, or `Data Flow` |

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- OWASP Application Denial of Service Cheat Sheet
- OWASP API Security Top 10 2023 — API4: Unrestricted Resource Consumption
- OWASP Rate Limiting Cheat Sheet
- CWE-400: Uncontrolled Resource Consumption
- CWE-770: Allocation of Resources Without Limits or Throttling
- CWE-776: Improper Restriction of Recursive Entity References in DTDs (XML Entity Expansion)
- CWE-1333: Inefficient Regular Expression Complexity
- CWE-502: Deserialization of Untrusted Data
- MITRE ATT&CK T1498: Network Denial of Service
- MITRE ATT&CK T1499: Endpoint Denial of Service
- MITRE ATT&CK T1499.003: Application Exhaustion Flood
- MITRE ATT&CK T1499.004: Application or System Exploitation
- NIST SP 800-53 SC-5: Denial of Service Protection
