# Finding IR Contract: F-5 LLM10 Unbounded Consumption (Cat 12/13 D-{N} + Cat 10/11 LLM-{N})

**Feature**: 229 / F-5
**Phase**: 1 (Design & Contracts)
**Schema**: `schemas/finding.yaml` v1.8 (unchanged in F-5)

## Purpose

Document the shape of new Pattern Category 12/13 (`D-{N}`, denial-of-service host) and Pattern Category 10/11 (`LLM-{N}`, model-theft host) findings emitted by the enriched agents. F-5 reuses the existing `D-{N}` and `LLM-{N}` ID prefixes; no schema bump.

## Cat 12/13 (DoS) Finding Schema

```yaml
id: "D-{N}"                              # existing prefix; single-namespace across Cat 1-13
category: "denial-of-service"            # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"
                                         # Cat 12 example: "LLM Inference-Request Flooding: /v1/completions endpoint without per-tenant QPS rate limit"
                                         # Cat 13 example: "Context-Window Exhaustion (Latency-Driven): adversarial 32k-token mega-history payload drives p99 latency to per-tenant timeout"
severity: "medium" | "high"              # Q3 RESOLVED: Cat 12 + Cat 13 default MEDIUM-HIGH
component: "{DFD Process | Data Store | Data Flow component name}"
description: |
  {2-4 sentence threat description}
  - For Cat 12: distinguish LLM-tier inference exhaustion from generic infrastructure DoS
  - For Cat 13: distinguish Vector A (latency-driven availability disruption) from Vector B (cost-DoW which lives in model-theft Cat 11)
mitigation: |
  {LLM-API-gateway / token-budget / context-window mechanism}
  - Cat 12 example: "Per-tenant queries-per-second rate limit at the API gateway with prompt-size cap (max-prompt-token enforcement) and per-tenant token budget per request with hard-cap"
  - Cat 13 example: "Max-context-window enforcement at the API gateway with automatic 413-response on overflow, plus per-conversation truncation policy with sliding-window limit"
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"          # REQUIRED on every Cat 12/13 finding
  - "CWE-400 Uncontrolled Resource Consumption"         # REQUIRED on every Cat 12/13 finding
  - "CWE-770 Allocation of Resources Without Limits or Throttling"  # APPLICABLE per architecture indicator (Cat 12; rare for Cat 13)
source_attribution: []                   # NOT POPULATED by F-5 — deferred to F-A3 per ADR-028 Decision 6
maestro_layer: "L7"                      # assigned downstream by orchestrator Phase 1
agentic_pattern: "none"                  # DoS findings carry agentic_pattern: "none" by default
delta_status: null                       # assigned downstream if baseline present
```

## Cat 10/11 (model-theft) Finding Schema

```yaml
id: "LLM-{N}"                            # existing prefix; single-namespace across Cat 1-11
category: "llm"                          # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"
                                         # Cat 10 example: "Cost Amplification via Recursive Prompting: 10-token prompt triggers 32k-token response on RAG advisory assistant"
                                         # Cat 11 example: "Denial-of-Wallet via Context-Window Cost Amplification: multi-tenant LLM SaaS without per-tenant token budget"
severity: "high" | "critical"            # Q3 RESOLVED: Cat 10 HIGH default; Cat 11 HIGH default with CRITICAL floor on 2-condition rule
component: "{DFD Process | Data Store component name}"
description: |
  {2-4 sentence threat description}
  - For Cat 10: distinguish cost-amplification specific attack vectors from model-theft Cat 6 (per-tenant quota / cost-control / billing-attribution gaps at the abstraction level)
  - For Cat 11: distinguish denial-of-wallet (the wallet is the bill, not the system uptime) from Vector A latency-DoS (which lives in DoS Cat 13)
mitigation: |
  {output-token cap / recursive-prompt depth limit / per-tenant token budget / cost-velocity monitoring mechanism}
  - Cat 10 example: "Per-query output-token cap tuned to realistic response-length p99, plus recursive-prompt depth limit at the inference-runtime layer (cf. MITRE ATT&CK T1496 Resource Hijacking)"
  - Cat 11 example: "Per-tenant token budget with hard-cap at the API gateway, plus denial-of-wallet anomaly detection via cost-velocity monitoring with automated tenant suspension on budget breach (cf. MITRE ATT&CK T1496 Resource Hijacking)"
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"          # REQUIRED on every Cat 10/11 finding
  - "OWASP LLM03:2025 — Supply Chain"                    # APPLICABLE for cost-flow-through-third-party-models adjacency
  # NOTE: T1496 NOT in references (not catalog-resolvable per plan-time grep on schemas/taxonomy/mitre-attack.yaml); named in mitigation prose only
source_attribution: []                   # NOT POPULATED by F-5 — deferred to F-A3 per ADR-028 Decision 6
maestro_layer: "L7"                      # assigned downstream by orchestrator Phase 1
agentic_pattern: "none"                  # model-theft findings carry agentic_pattern: "none" by default
delta_status: null                       # assigned downstream if baseline present
```

## Invariants

### Required Invariants (BLOCKER-level)

1. **`references` array — Cat 12/13**: every `D-{N}` finding MUST contain at minimum `OWASP LLM10:2025 — Unbounded Consumption` AND `CWE-400 Uncontrolled Resource Consumption`.
2. **`references` array — Cat 10/11**: every `LLM-{N}` finding MUST contain at minimum `OWASP LLM10:2025 — Unbounded Consumption`.
3. **T1496 prose-only**: `MITRE ATT&CK T1496 Resource Hijacking` MUST be named in `mitigation` narrative on Cat 10/11 findings as a text-only cross-reference. T1496 MUST NOT appear in `references` (not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml`).
4. **`mitigation` field**: MUST name at least one specific LLM-API-gateway / token-budget / context-window / cost-control mechanism. Generic "rate-limit your endpoints" or "monitor your bill" are insufficient.
5. **`id` regex**: MUST match schema 1.8 `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"`. F-5 reuses existing `D` and `LLM` prefixes; no bump.
6. **LLM-serving topology gate (FR-015)**: Cat 12/13 + Cat 10/11 emit zero findings on architectures lacking LLM-serving indicators (declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology). Architectures with no LLM-serving topology preserve byte-identity on the 6 baselines.
7. **Cat 11 severity floor (Q3 RESOLVED)**: severity computation MUST encode the 2-condition CRITICAL floor. HIGH default; CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident in the architecture AND (b) both per-tenant token budget AND cost alerting absent. Single-tenant economic exposure with absent controls computes HIGH (not CRITICAL).
8. **`source_attribution` not populated**: F-5 MUST NOT extend `source_attribution` populator wiring on either host agent. The `source_attribution: []` empty-array default per finding-format-shared.md is preserved. F-A3 will own the populator wiring.

### Optional Invariants (per applicability)

9. **CWE-770 inclusion (Cat 12)**: included in `references` where the architecture indicator specifically signals "Allocation of Resources Without Limits or Throttling" (e.g., per-tenant token budget hard-cap absent). Optional for Cat 13.
10. **LLM03 inclusion (Cat 10/11)**: included in `references` where the architecture indicator specifically signals supply-chain trust-inheritance (e.g., cost-flow-through-third-party-models, OpenAI/Anthropic upstream provider with no upstream cost reconciliation).

## Examples

### Example 1: Cat 12 (Inference-Request Flooding) on Multi-Tenant SaaS

```yaml
id: D-3                                  # next sequential D-{N} ID
category: denial-of-service
title: "LLM Inference-Request Flooding: /v1/completions endpoint without per-tenant QPS rate limit"
severity: high                           # MEDIUM-HIGH default; HIGH applied for high-likelihood multi-tenant freemium
component: "LLM Inference Service (Process)"
description: |
  The /v1/completions endpoint is exposed without per-tenant queries-per-second
  rate limiting at the API gateway. An attacker registers free-tier accounts
  and floods the endpoint with concurrent requests, exhausting inference compute
  capacity and causing latency degradation for paying tenants. Tenant isolation
  breaks down at the inference-compute layer; denial-of-wallet exposure compounds
  with the availability degradation.
mitigation: |
  Per-tenant queries-per-second rate limit at the API gateway. Prompt-size cap
  (max-prompt-token enforcement) at request ingestion. Per-tenant token budget
  per request with hard-cap enforcement. Token-counting middleware between
  request ingestion and model invocation, with anomaly alerting on per-tenant
  token-velocity spikes.
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"
  - "CWE-400 Uncontrolled Resource Consumption"
  - "CWE-770 Allocation of Resources Without Limits or Throttling"
source_attribution: []
maestro_layer: L7
agentic_pattern: none
```

### Example 2: Cat 11 (Denial-of-Wallet — Critical Floor)

```yaml
id: LLM-7                                # next sequential LLM-{N} ID
category: llm
title: "Denial-of-Wallet via Context-Window Cost Amplification: multi-tenant freemium chatbot without per-tenant token budget"
severity: critical                       # CRITICAL FLOOR per Q3 2-condition rule:
                                         # (a) multi-tenant freemium structure structurally evident in architecture AND
                                         # (b) both per-tenant token budget AND cost alerting absent
component: "Consumer Chatbot Service (Process)"
description: |
  The B2C consumer chatbot SaaS allows freemium users to consume inference
  compute without per-tenant token budget. An attacker registers thousands of
  freemium accounts and runs cost-amplification queries (Cat 10 pattern) at
  scale, plus drives context-window to model max per call (Vector B), inflating
  per-call cost. The operator's monthly inference bill exceeds revenue by 10x;
  the freemium tier becomes economically untenable.
mitigation: |
  Per-tenant token budget with hard-cap enforcement at the API gateway.
  Per-tenant context-window cost reconciliation. Cost-per-query p99 alerting
  tied to per-tenant billing attribution. Denial-of-wallet anomaly detection
  via cost-velocity monitoring with anomaly alerting on percentile-velocity
  spikes. Automated tenant suspension on budget breach (no manual approval
  delay). Per-tenant billing attribution computed at-query-time (not
  end-of-month). cf. MITRE ATT&CK T1496 Resource Hijacking.
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"
  - "OWASP LLM03:2025 — Supply Chain"
source_attribution: []
maestro_layer: L7
agentic_pattern: none
```

### Example 3: Cat 13 (Context-Window Exhaustion — Latency-DoS)

```yaml
id: D-4                                  # next sequential D-{N} ID
category: denial-of-service
title: "Context-Window Exhaustion (Latency-Driven): adversarial conversation history drives p99 latency to per-tenant timeout"
severity: high                           # MEDIUM-HIGH default; HIGH applied for high-likelihood multi-tenant
component: "Consumer Chatbot Service (Process)"
description: |
  The chatbot allows users to send arbitrarily long conversation history. An
  attacker constructs a 32k-token mega-history payload that drives context-window
  usage to 99% of model max, causing per-request latency to spike to per-tenant
  timeout. Legitimate users on the same inference cluster experience degraded
  latency; attacker's intent is availability disruption (Vector A). Same
  architecture additionally surfaces model-theft Cat 11 (Vector B cost-DoW) —
  both findings emit on the same architecture, neither is a duplicate.
mitigation: |
  Max-context-window enforcement at the API gateway, with automatic 413-response
  on overflow. Per-conversation truncation policy with sliding-window limit on
  appended message history. Recursive-prompt-pattern detection at the API gateway.
  Context-window monitoring with anomaly alerting on percentage-of-max usage
  spikes. Per-tenant context-window cap distinct from per-request context-window cap.
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"
  - "CWE-400 Uncontrolled Resource Consumption"
source_attribution: []
maestro_layer: L7
agentic_pattern: none
```

## Validation Procedure

1. Every Cat 12/13 + Cat 10/11 finding's `references` array contains the required entries (LLM10 minimum; CWE-400 also for Cat 12/13).
2. Every Cat 10/11 `mitigation` narrative contains the literal string "T1496" or "Resource Hijacking" as text-only mention.
3. T1496 does NOT appear in `references` — `grep -F "T1496" {finding.references}` returns empty.
4. All cited IDs in `references` resolve against `schemas/taxonomy/{owasp,cwe}.yaml` — referential integrity check passes.
5. `mitigation` field word count > 30 (named-mechanism check; generic guidance fails this gate).
6. Cat 11 finding severity is HIGH unless 2-condition critical-floor predicate matches (multi-tenant freemium architectural indicators + absent token budget + absent cost alerting).
7. F-A2 referential validator — when F-A3 ships and populator wiring lands — passes by construction because catalog references in F-5 are correct.

## References

- Schema: `schemas/finding.yaml` v1.8 (unchanged)
- Finding format shared: `.claude/skills/tachi-shared/references/finding-format-shared.md`
- ADR-028 Decision 6 (F-A3 deferral): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- F-3 finding contract (precedent): `specs/219-asi07-tool-abuse-enrichment/contracts/finding-contract.md`
