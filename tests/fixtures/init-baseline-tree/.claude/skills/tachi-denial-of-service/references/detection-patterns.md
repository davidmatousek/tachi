---
name: denial-of-service-detection-patterns
description: Externalized detection pattern catalog for STRIDE denial of service — resource exhaustion, algorithmic complexity, connection pool exhaustion, cascade failures, network flood and amplification
consumers: [tachi-denial-of-service]
last_updated: 2026-04-11
---

# Denial of Service Detection Patterns

## Overview

Detection vocabulary for the STRIDE Denial of Service threat category. Loaded at detection start by the `tachi-denial-of-service` agent via a single `**MANDATORY**: Read` directive. Covers availability degradation against Processes, Data Stores, and Data Flows — including resource exhaustion, algorithmic complexity attacks (ReDoS, billion laughs, zip bombs), database and storage saturation, connection pool exhaustion, dependency cascade failures, application-layer flooding, infrastructure-layer flood and amplification, plus the CWE Top 25 2024 algorithmic-complexity vectors and MITRE ATT&CK T1498/T1499 network and endpoint DoS techniques.

## Targeted DFD Element Types

- **Process**: API endpoints, background workers, data processing pipelines, authentication services, webhook receivers
- **Data Store**: Databases, caches, message queues, file storage, search indexes
- **Data Flow**: Network connections, API calls, message bus channels, file upload streams, WebSocket connections

## Resource Exhaustion

- Endpoints accepting unbounded input sizes (request body, file uploads, query parameters)
- Missing request size limits on API gateways or reverse proxies
- Memory-intensive operations triggered by unauthenticated requests
- CPU-intensive computations (regex, compression, encryption) on user-controlled input
- Thread pool exhaustion from long-running synchronous operations

## Algorithmic Complexity Attacks

- Regular expressions vulnerable to ReDoS (catastrophic backtracking)
- Hash collision attacks on hash table implementations
- XML parsing vulnerable to billion laughs (entity expansion) or quadratic blowup
- JSON parsing without depth or size limits
- Recursive algorithms on user-controlled data without depth bounds

## Database and Storage Saturation

- Queries without result limits allowing full table scans
- Missing pagination on list endpoints enabling massive result sets
- Write-heavy endpoints without rate limiting enabling storage flooding
- Missing TTL on cache entries enabling memory exhaustion
- Log volume from user-triggerable events filling disk storage

## Connection and Pool Exhaustion

- Database connection pools without timeouts or maximum size limits
- HTTP client connections without read/write timeouts
- WebSocket connections without idle timeout or per-client limits
- File descriptor exhaustion from unclosed connections or handles
- Thread pool starvation from blocking I/O on async paths

## Dependency and Cascade Failures

- Missing circuit breakers on calls to external services
- Retry storms from aggressive retry policies without backoff
- Synchronous dependency chains where one slow service blocks all upstream callers
- Missing fallback behavior when optional dependencies are unavailable
- Health check endpoints that call downstream services (creating cascading failures)

## Application-Layer Attacks

- HTTP flood attacks targeting computationally expensive endpoints (search, report generation, export)
- Slowloris-style attacks holding connections open with partial HTTP requests
- API abuse through high-frequency polling of expensive queries without caching
- GraphQL complexity attacks using deeply nested or aliased queries to amplify server workload
- Multipart upload abuse sending many small concurrent uploads to exhaust file descriptor limits

## Infrastructure-Layer Attacks

- DNS amplification targeting service discovery endpoints
- SYN flood attacks exhausting TCP connection tables on load balancers
- TLS renegotiation attacks consuming CPU on TLS termination endpoints
- Missing DDoS protection at CDN or API gateway layer for public-facing services
- UDP/ICMP flood attacks saturating network bandwidth before reaching application layer

## Flooding and Abuse

- Missing rate limiting on public-facing endpoints
- Missing rate limiting differentiation between authenticated and anonymous traffic
- Account creation or password reset endpoints without CAPTCHA or proof-of-work
- Webhook receivers without sender verification enabling forged flood attacks
- Missing IP-based throttling for unauthenticated endpoints

## Pattern Category 9: Uncontrolled Resource Consumption and Algorithmic Complexity (CWE Top 25 2024)

CWE-400 Uncontrolled Resource Consumption rose into the CWE Top 25 Most Dangerous Software Weaknesses 2024 driven primarily by ReDoS (CWE-1333) and broader algorithmic-complexity exploitation (CWE-407). The pre-existing Algorithmic Complexity Attacks list covers a small subset; this category systematizes the broader pattern: any component that compiles patterns from untrusted input, parses structured formats without depth limits, processes archives or media without expansion ratio caps, or performs sort/search/traversal on user-controllable collections is exposed to single-request exhaustion that bypasses network-layer DoS controls entirely. These attacks are especially insidious because a single well-crafted request consumes minutes of CPU, defeating per-request rate limiting and SYN-flood protections.

**Indicators**:

- DFD element compiles or evaluates regular expressions sourced from untrusted input — user-supplied patterns, patterns templated with user input, or third-party rule files loaded at runtime without complexity analysis
- Component parses structured formats (XML, JSON, YAML, Protobuf, MessagePack) without declared depth limits, entity-expansion limits, or anchor-resolution caps — vulnerable to billion-laughs, XML quadratic blowup, YAML alias bombs, and JSON deeply-nested object attacks
- Image, PDF, video, or archive processing component accepts files without size limits AND without content-ratio (compression-bomb / zip-bomb) limits — a 10KB upload that decompresses to 10GB exhausts memory or disk
- Graph traversal, sort, search, or reduce operation runs on a user-controllable collection size without an enforced upper bound — pathological inputs that trigger O(n²) or worse worst-case complexity
- Hash-table-backed data structure populated from user input without hash randomization or per-bucket size caps — vulnerable to hash collision flooding (CWE-407)
- Cryptographic operations (key derivation, signing, verification) performed on user-controlled work factors without server-side caps — bcrypt cost, scrypt N parameter, PBKDF2 iterations supplied by client

**Primary source**:

- CWE-400: Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-770: Allocation of Resources Without Limits or Throttling: https://cwe.mitre.org/data/definitions/770.html
- CWE-1333: Inefficient Regular Expression Complexity (ReDoS): https://cwe.mitre.org/data/definitions/1333.html
- CWE-407: Inefficient Algorithmic Complexity: https://cwe.mitre.org/data/definitions/407.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html

**Example**: A SaaS log-search service accepts user-supplied regular expressions for filtering historical events. The frontend forwards the pattern unchanged to a Go backend that calls `regexp.MatchString(userPattern, line)` against millions of stored events. An attacker submits the pattern `^(a+)+$` against a corpus containing a single line of 30 `a` characters followed by a `b`. The Go regex engine (RE2-based, normally ReDoS-safe) is fine for this input, but the service has a fallback path that uses a PCRE-backed regex library for "compatibility mode" exposed through a header — the attacker sets the header. PCRE backtracks for ten minutes on the single matching attempt, pinning a CPU core; the attacker submits 100 parallel requests and the entire search-fleet stalls. No network-layer rate limiter triggers because the request count is small, and no application-layer cap on regex compile/run time exists.

## Pattern Category 10: Network Flood, Reflection, and Amplification (ATT&CK T1498/T1499)

MITRE ATT&CK T1498 (Network Denial of Service) and T1499 (Endpoint Denial of Service) provide canonical taxonomy for network-layer and edge-layer DoS that is more granular than the pre-existing Infrastructure-Layer Attacks list. T1498.001 (Direct Network Flood) and T1498.002 (Reflection Amplification) target bandwidth and stateful network appliances; T1499.001 (OS Exhaustion Flood), T1499.002 (Service Exhaustion Flood), T1499.003 (Application Exhaustion Flood), and T1499.004 (Application or System Exploitation) target the host and application layers. This category enables architecture-level detection of edge-protection gaps that allow these techniques to reach the application at all — the right place to stop them is at the perimeter, before they consume backend capacity.

**Indicators**:

- DFD ingress is direct internet-facing without a declared upstream DDoS protection layer (CDN with shield service, cloud-provider DDoS scrubbing, dedicated WAF with rate-limiting rules) — the ingress component is the first to see attacker traffic
- Externally reachable UDP service (DNS, NTP, memcached, SNMP, CoAP, QUIC over UDP) that responds with packets larger than the request — vulnerable to being weaponized as a reflection/amplification source against third parties, AND vulnerable to direct flood attack
- Authentication endpoint, search endpoint, report-generation endpoint, or other expensive endpoint reachable from the internet without rate limiting, CAPTCHA, or proof-of-work at the edge — Application Exhaustion Flood (T1499.003) target
- HTTP server has no declared connection concurrency cap, no slow-loris timeout (`Slowloris` and `R-U-Dead-Yet` style attacks), no per-IP connection limit, and no maximum request header / body read deadline — Service Exhaustion Flood (T1499.002) target
- Edge layer does not perform geo-blocking, ASN reputation filtering, or known-bot fingerprinting before forwarding requests to the backend — high-volume traffic from known bot networks reaches the application directly
- Stateful network appliances (load balancer, firewall, NAT gateway) lack declared connection-table size limits or eviction policy — exhausting the table is the OS Exhaustion Flood (T1499.001) primitive

**Primary source**:

- MITRE ATT&CK T1498: Network Denial of Service: https://attack.mitre.org/techniques/T1498/
- MITRE ATT&CK T1498.001: Direct Network Flood: https://attack.mitre.org/techniques/T1498/001/
- MITRE ATT&CK T1498.002: Reflection Amplification: https://attack.mitre.org/techniques/T1498/002/
- MITRE ATT&CK T1499: Endpoint Denial of Service: https://attack.mitre.org/techniques/T1499/
- MITRE ATT&CK T1499.003: Application Exhaustion Flood: https://attack.mitre.org/techniques/T1499/003/
- NIST SP 800-61r2 Computer Security Incident Handling Guide: https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final
- US-CERT TA14-017A UDP-Based Amplification Attacks: https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks

**Example**: A regional fintech exposes an API gateway directly on a public ELB without an upstream CDN or DDoS scrubbing service. The gateway routes `/api/v1/search` to a backend that executes a parameterized SQL query joining four tables; the endpoint is rate-limited per-API-key but the rate-limiter is bypassed by setting an `X-Forwarded-For` header the gateway trusts. A botnet of 5,000 residential proxies sends 200 requests/sec each to the search endpoint with rotating `X-Forwarded-For` values; the gateway logs each as a unique client, the rate-limiter never trips, and the backend SQL pool is exhausted within 90 seconds. Legitimate traffic gets `503 Service Unavailable`. The attack is canonical T1499.003 Application Exhaustion Flood — and the only effective control would have been an upstream bot-fingerprinting WAF that the architecture description does not mention.

## Pattern Category 11: Cascade Failures and Noisy Neighbor in Microservice Architectures (OWASP A04:2021)

OWASP A04:2021 Insecure Design introduced design-level resilience gaps as a Top 10 category in 2021, recognizing that most production outages are not network DoS — they are self-inflicted cascade failures triggered by a single component degradation. The pre-existing Dependency and Cascade Failures list covers the basic patterns; this category formalizes the architecture-level resilience review for microservice topologies. Without bulkheads, timeout budgets, retry budgets, and graceful-degradation paths, a single slow downstream dependency cascades through every synchronous caller until the entire fleet is stalled, often without any external attacker — the noisy-neighbor variant (one tenant exhausting shared resources) achieves the same effect with no malice at all.

**Indicators**:

- Synchronous RPC chain across 3 or more services declared without per-hop timeouts, total request budget, retry budget, or circuit breaker — the slowest service in the chain dictates total latency and a single failure point cascades upstream
- Shared database, cache, message queue, or downstream service across multiple components without per-component connection pools, per-tenant quotas, or noisy-neighbor isolation — one component's burst saturates the shared resource for all
- Queue-based workflow with unbounded queue depth, no backpressure mechanism, no poison-message dead-letter handling, and no consumer concurrency cap — producer outpaces consumer indefinitely until memory or disk exhaust
- Critical-path dependency on a single component with no declared fallback, no graceful-degradation mode, and no cached/stale-but-acceptable response strategy — outage of that one component takes the whole product down
- Health-check endpoint that calls downstream services and returns degraded if any are slow — load balancers depool the service, intensifying load on remaining replicas (the canonical thundering-herd cascade)
- Auto-scaling policy reacts to a metric correlated with the failure being defended against (e.g., scaling on request count when the failure is downstream timeout), causing the scale-out itself to amplify the cascade
- Retry policy uses fixed delay or exponential backoff without jitter — synchronized retries collide at the recovering service, creating retry storms that prevent recovery (false-positive risk: HIGH because resilience patterns are rarely declared at architecture level; flag for review rather than auto-finding)

**Primary source**:

- OWASP Top 10 2021 — A04: Insecure Design: https://owasp.org/Top10/A04_2021-Insecure_Design/
- OWASP Cheat Sheet — Denial of Service: https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
- AWS Builders' Library — Avoiding fallback in distributed systems: https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/
- Google SRE Book — Handling Overload (Chapter 21): https://sre.google/sre-book/handling-overload/
- Release It! (Michael Nygard) — Stability Patterns (bulkhead, circuit breaker, timeout)

**Example**: An e-commerce platform's checkout flow calls a synchronous chain: `web-tier` → `cart-service` → `inventory-service` → `pricing-service` → `tax-service` → `payment-gateway`. Each hop has an individual 30-second timeout but the chain has no total budget. During a Black Friday sale, the third-party tax-service degrades from 50ms p99 to 8 seconds p99. Every checkout request now blocks for ~8 seconds at the tax hop; the upstream pricing-service exhausts its connection pool to tax-service; cart-service exhausts its connection pool to pricing-service; the entire checkout fleet stalls within 2 minutes despite tax-service still being technically up. There is no circuit breaker on tax-service, no per-hop budget, no fallback to cached tax estimates, and the architecture description never mentions any of these patterns — the cascade was inevitable from the design.

## Pattern Category 12: LLM Inference-Request Flooding and Token Exhaustion (OWASP LLM10:2025)

OWASP LLM10:2025 (Unbounded Consumption) introduced LLM-tier resource exhaustion as a Top-10 LLM threat in 2025, recognizing that inference compute, prompt-token budget, and context-window are scarce resources distinct from generic infrastructure DoS. The pre-existing Pattern Categories 9 (CWE Top 25 algorithmic complexity), 10 (network flood), and 11 (cascade failures) cover infrastructure availability — this category systematizes the LLM-API-gateway flooding and token-budget exhaustion subclass. An attacker with valid API access (free-tier, low-tier subscription, or compromised credential) can exhaust the operator's per-tenant inference compute capacity and inflate per-call cost without triggering classic network-layer rate limits. Same Heuristic A signal class as the cost-amplification and denial-of-wallet variants in `model-theft` Pattern Categories 10 + 11.

**Indicators**:

- LLM inference endpoint without per-tenant queries-per-second (QPS) rate limit at the API gateway — every authenticated client shares one global rate budget, enabling a single tenant to starve the inference fleet
- Prompt size accepted unbounded (no max-prompt-token enforcement) — an attacker submits 4k-, 8k-, 16k-, or larger prompts that exceed the operator's intended cost-per-call envelope and inflate per-request inference time
- Per-tenant token budget per request not enforced — a single request can request the model's max output (4k, 16k, 32k tokens) regardless of tenant tier, creating per-call cost asymmetry between attackers and the operator
- Token-counting middleware absent or computed asynchronously — the API gateway accepts the request without checking projected cost, and only learns total token usage after-the-fact via billing reconciliation
- Request-timeout configured for typical (non-LLM) request latency — the inference call's latency tail (p99 > 30s for context-window-heavy requests) is not distinguished from infrastructure-tier slow paths, so legitimate slow LLM requests are killed alongside attacks

**Primary source**:

- OWASP LLM10:2025 — Unbounded Consumption: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- CWE-400: Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-770: Allocation of Resources Without Limits or Throttling: https://cwe.mitre.org/data/definitions/770.html

**Example**: A multi-tenant LLM-serving SaaS exposes a `/v1/completions` endpoint without per-tenant QPS rate limit. An attacker registers free-tier accounts and floods the endpoint with concurrent requests, exhausting inference compute capacity and causing latency degradation for paying tenants. Tenant isolation breaks down at the inference-compute layer; the SaaS's denial-of-wallet exposure compounds with the availability degradation. **Mitigation**: per-tenant QPS rate limit at the API gateway + prompt-size cap (max-prompt-token enforcement) + per-tenant token budget per request with hard-cap + token-counting middleware with anomaly alerting on per-tenant token-velocity spikes.

## Pattern Category 13: Context-Window Exhaustion — Latency-Driven Variant (OWASP LLM10:2025; Q1 SPLIT Vector A)

Context-window exhaustion is a single attack class with two distinct outcomes — Vector A drives availability disruption (this category), Vector B drives economic damage (model-theft Pattern Category 11). Vector A targets the inference-server's per-request latency budget: an adversarially long conversation history or prompt expansion drives per-request latency to per-tenant timeout. Attacker intent is availability disruption — same signal class as Cat 12 (LLM-tier resource exhaustion).

**Q1 SPLIT scope note**: Cat 13 covers Vector A (latency-driven availability disruption) only. Vector B (cost-amplification → economic damage) lives in `model-theft` Pattern Category 11 per F-5 FR-3. Same architecture surfaces both — neither is a duplicate. ADR-034 Decision 3 audit table assigns each vector to exactly one owning category. Cohesive emission (`D-{N}` for Vector A in `category: denial-of-service` section + `LLM-{N}` for Vector B in `category: llm` section) preserves single-namespace category rendering across `threats.md`.

**Indicators**:

- LLM inference endpoint accepts adversarially long prompts (prompt expansion via injection or recursive embedding) without max-context-window enforcement at API gateway — the model's max-context-window becomes the per-request DoS surface
- Multi-message conversation history accepted unbounded (no per-conversation truncation policy) — an attacker constructs a 32k+ token mega-history payload that drives context usage to 99% of model max, spiking per-request latency
- Recursive prompt patterns not detected — adversarial templates that cause the model to re-engage its own output (chain-of-thought, recursive tool-call, self-reflection prompts) inflate context-window usage in unexpected ways
- Context-window monitoring absent — no anomaly alerting on percentage-of-max usage spikes per request or per-tenant
- Per-tenant context-window cap not differentiated from per-request cap — a single tenant can monopolize inference latency by sending consecutive max-context requests, even if per-request limits exist

**Primary source**:

- OWASP LLM10:2025 — Unbounded Consumption: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- CWE-400: Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html

**Example**: A consumer-facing chatbot allows users to send arbitrarily long conversation history. An attacker constructs a 32k-token mega-history payload that drives context-window usage to 99% of model max, causing per-request latency to spike to the per-tenant timeout. Legitimate users on the same inference cluster experience degraded latency (Vector A — availability disruption). The same architecture additionally surfaces `model-theft` Pattern Category 11 (denial-of-wallet via context-window cost amplification) as Vector B — both findings emit on the same architecture, neither is a duplicate. **Mitigation**: max-context-window enforcement at the API gateway with automatic 413-response on overflow + per-conversation truncation policy with sliding-window limit + recursive-prompt-pattern detection + context-window monitoring with anomaly alerting on percentage-of-max usage spikes + per-tenant context-window cap distinct from per-request cap.

## Pattern Category Disambiguation

Pattern Categories 12 + 13 (LLM-tier inference-resource exhaustion) and the pre-existing Pattern Category 9 (CWE Top 25 generic infrastructure resource exhaustion) share the CWE-400 root cause but address distinct mitigation surfaces:

- **Pattern Category 9** detects generic uncontrolled resource consumption applicable to any HTTP service — regex-compile-on-untrusted-input (ReDoS), depth-unbounded XML or JSON parsing (billion laughs, deeply nested), archive expansion-ratio caps (zip bomb), hash-collision flooding, recursive-algorithm depth bounds. Mitigation surfaces are language- and library-level controls.
- **Pattern Categories 12 + 13** detect LLM-API-gateway-specific surfaces — per-tenant QPS on inference endpoints, max-prompt-token enforcement, per-tenant token budget, max-context-window enforcement, context-window monitoring, recursive-prompt-pattern detection. Mitigation surfaces are LLM-API-gateway-level controls.

Same architecture may legitimately surface Pattern Category 9 + Pattern Category 12 + Pattern Category 13 findings; they are not duplicates and MUST NOT be merged in `threat-report.md`. Architect formalizes this carve in ADR-034 Decision 7. Vector A latency-driven DoS lives here in Cat 13; Vector B cost-driven denial-of-wallet lives in `model-theft` Pattern Category 11 per Q1 SPLIT cross-agent vector decomposition.

## Primary Sources

- OWASP Top 10 2021 — A04: Insecure Design: https://owasp.org/Top10/A04_2021-Insecure_Design/
- OWASP Application Denial of Service Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
- OWASP API Security Top 10 2023 — API4: Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OWASP Rate Limiting Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Rate_Limiting_Cheat_Sheet.html
- OWASP LLM10:2025 — Unbounded Consumption: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- CWE-400: Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-407: Inefficient Algorithmic Complexity: https://cwe.mitre.org/data/definitions/407.html
- CWE-502: Deserialization of Untrusted Data: https://cwe.mitre.org/data/definitions/502.html
- CWE-770: Allocation of Resources Without Limits or Throttling: https://cwe.mitre.org/data/definitions/770.html
- CWE-776: Improper Restriction of Recursive Entity References in DTDs (XML Entity Expansion): https://cwe.mitre.org/data/definitions/776.html
- CWE-1333: Inefficient Regular Expression Complexity: https://cwe.mitre.org/data/definitions/1333.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
- MITRE ATT&CK T1498: Network Denial of Service: https://attack.mitre.org/techniques/T1498/
- MITRE ATT&CK T1498.001: Direct Network Flood: https://attack.mitre.org/techniques/T1498/001/
- MITRE ATT&CK T1498.002: Reflection Amplification: https://attack.mitre.org/techniques/T1498/002/
- MITRE ATT&CK T1499: Endpoint Denial of Service: https://attack.mitre.org/techniques/T1499/
- MITRE ATT&CK T1499.003: Application Exhaustion Flood: https://attack.mitre.org/techniques/T1499/003/
- MITRE ATT&CK T1499.004: Application or System Exploitation: https://attack.mitre.org/techniques/T1499/004/
- NIST SP 800-53 SC-5: Denial of Service Protection
- NIST SP 800-61r2 Computer Security Incident Handling Guide: https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final
- US-CERT TA14-017A UDP-Based Amplification Attacks: https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks
- AWS Builders' Library — Avoiding fallback in distributed systems: https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/
- Google SRE Book — Handling Overload: https://sre.google/sre-book/handling-overload/
