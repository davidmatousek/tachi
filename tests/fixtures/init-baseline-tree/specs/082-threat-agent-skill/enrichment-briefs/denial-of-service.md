# Enrichment Brief — denial-of-service

**Agent type**: STRIDE
**Primary threat category**: Denial of Service (Availability)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Uncontrolled Resource Consumption and Algorithmic Complexity

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/data/definitions/400.html`
- **Source item**: CWE-400 Uncontrolled Resource Consumption; related CWE-770 Allocation of Resources Without Limits or Throttling; related CWE-1333 Inefficient Regular Expression Complexity (ReDoS)
- **Why this category**: CWE-400 rose into the 2024 Top 25 primarily driven by ReDoS and algorithmic-complexity attacks; inline patterns cover only network-layer DoS and miss algorithmic vectors entirely.
- **Proposed detection signal**:
  - DFD element compiles or applies regular expressions from untrusted input (user-supplied patterns or patterns templated with user input)
  - Component parses structured formats (XML, JSON, YAML, Protobuf) with unbounded nesting depth or expansion (billion-laughs, yaml anchors)
  - Image/PDF/archive processing component accepts files without size or content-ratio (zip bomb) limits
  - Graph traversal, sort, or search operation on user-controllable collection size without bound
- **False-positive risk**: Low — presence of untrusted regex compilation or unbounded parse is a concrete signal
- **Taxonomy alignment**: STRIDE Denial of Service; CWE-400 (Top 25 2024), CWE-770, CWE-1333

### Category 2 — Network Denial of Service (Flood, Reflection, Amplification)

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1498/`
- **Source item**: T1498 Network Denial of Service (.001 Direct Network Flood, .002 Reflection Amplification); related T1499 Endpoint Denial of Service (.001 OS Exhaustion Flood, .002 Service Exhaustion Flood, .003 Application Exhaustion Flood, .004 Application or System Exploitation)
- **Why this category**: ATT&CK provides canonical taxonomy for network-layer DoS that is more granular than current inline coverage; enables architecture-level detection of edge-protection gaps.
- **Proposed detection signal**:
  - DFD ingress is direct internet-facing without declared DDoS protection (CDN, WAF, scrubbing service, cloud-provider shield)
  - Externally reachable UDP service (risk of reflection/amplification)
  - Authentication or expensive endpoint reachable without rate limiting or CAPTCHA at edge
  - No declared connection concurrency cap or slow-loris protection on HTTP server
- **False-positive risk**: Medium — rate limiting is often declared outside architecture descriptions
- **Taxonomy alignment**: STRIDE Denial of Service; ATT&CK TA0040 Impact tactic

### Category 3 — Cascade Failures and Noisy Neighbor in Microservice Architectures

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A04_2021-Insecure_Design/`
- **Source item**: A04:2021 Insecure Design (the new-in-2021 category covering design-level security flaws including missing resilience)
- **Why this category**: Microservice designs without bulkheads, timeouts, or circuit breakers cascade single-point failures into service-wide outages. Current inline patterns treat DoS as an external-only attacker model and miss design-level resilience gaps.
- **Proposed detection signal**:
  - Synchronous RPC chain across 3+ services declared without timeout, retry budget, or circuit breaker
  - Shared database or cache across components without connection-pool isolation (noisy neighbor)
  - Queue-based workflow with unbounded depth (no backpressure or poison-message handling)
  - Critical path dependency on a single component with no fallback or graceful degradation declared
- **False-positive risk**: High — resilience patterns are rarely declared at architecture level; flag for review rather than auto-finding
- **Taxonomy alignment**: STRIDE Denial of Service; OWASP A04:2021

## Source Verification Notes

- CWE-400 moved into CWE Top 25 2024 driven by ReDoS prominence — verify exact rank during Phase 3.2 extraction.
- CWE-1333 (ReDoS) is specific to regular expressions; CWE-407 Algorithmic Complexity is the broader parent.
- ATT&CK T1498 and T1499 are distinct techniques (network-layer vs. endpoint-layer); cite the one that matches detection focus.
- OWASP A04:2021 Insecure Design is broad and covers more than DoS resilience; use specifically for resilience-gap patterns.
- Checked but NOT used: Chaos Engineering / resilience4j / Hystrix docs — these are controls references, not detection-pattern sources.
