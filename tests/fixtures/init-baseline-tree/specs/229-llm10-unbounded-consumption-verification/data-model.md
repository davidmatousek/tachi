# Data Model: F-5 LLM10 Unbounded Consumption Enrichment

**Feature**: 229 / F-5
**Phase**: 1 (Design & Contracts)

## Purpose

Document the entity shapes for new Pattern Categories 12/13 (DoS host) + 10/11 (model-theft host), the LLM-serving topology gate predicates, the Q3 severity-floor conditional, and the Q1 SPLIT cross-agent vector decomposition for context-window exhaustion.

## Pattern Category Entity (4 instances)

```yaml
PatternCategory:
  id: "Cat 12" | "Cat 13" | "Cat 10" | "Cat 11"
  host_agent: "denial-of-service" | "model-theft"
  host_companion: ".claude/skills/tachi-{denial-of-service,model-theft}/references/detection-patterns.md"
  finding_id_prefix: "D" | "LLM"
  category_enum: "denial-of-service" | "llm"
  primary_source: "OWASP LLM10:2025 — Unbounded Consumption"
  related_sources:
    Cat 12: ["CWE-400", "CWE-770"]
    Cat 13: ["CWE-400"]
    Cat 10: ["OWASP LLM03:2025"]                # inherited from agent owasp_references
    Cat 11: ["OWASP LLM03:2025"]                # inherited from agent owasp_references
  prose_only_references:
    Cat 10: ["MITRE ATT&CK T1496 Resource Hijacking"]
    Cat 11: ["MITRE ATT&CK T1496 Resource Hijacking"]
  indicator_count: ">=4 (target 5)"
  worked_example_count: ">=1"
  default_severity:
    Cat 12: "MEDIUM-HIGH"
    Cat 13: "MEDIUM-HIGH"
    Cat 10: "HIGH"
    Cat 11: "HIGH (CRITICAL floor on 2-condition rule)"
  q1_split_role:
    Cat 13: "Vector A — latency-driven DoS (availability disruption)"
    Cat 11: "Vector B — cost-driven DoW (economic damage) + broader denial-of-wallet"
```

## LLM-Serving Topology Gate Predicate

The new Pattern Categories enforce a two-part emission gate:

```python
def emit_finding(component, architecture):
    # Part 1: dispatch trigger (existing)
    if not matches_existing_trigger_keywords(component):
        return None  # agent self-gates dispatch

    # Part 2: LLM-serving topology indicator (new — FR-015)
    if not has_llm_serving_indicators(architecture):
        return None  # zero new Cat 12/13 + Cat 10/11 findings on non-LLM-serving topologies

    # Per-category indicator evaluation
    if matches_pattern_category_indicators(component, architecture):
        return build_finding(...)

    return None
```

**LLM-serving indicators** (any one of):
- Declared inference endpoint (e.g., `/v1/completions`, `/inference`, `/chat`, `/generate`)
- LLM API gateway component (named in DFD)
- Per-tenant API key authentication on inference endpoint
- Token-counting middleware between request ingestion and model invocation
- Cost-attribution layer (per-tenant cost reconciliation, billing API)
- Multi-tenant LLM-serving topology (≥2 tenants share inference compute)

**Zero-impact-when-absent invariant** (SC-014): the 6 non-LLM-serving baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) lack all 6 LLM-serving indicators → topology gate fails → zero new findings → byte-identical PDFs under `SOURCE_DATE_EPOCH=1700000000`.

## Q3 Severity-Floor Conditional Predicate (Cat 11)

```python
def cat_11_severity(component, architecture):
    # 2-condition CRITICAL floor per Q3 RESOLVED at PRD time
    is_multi_tenant_freemium = (
        architecture.has_multi_tenant_indicator and
        architecture.has_freemium_indicator
    )
    both_controls_absent = (
        not architecture.has_per_tenant_token_budget and
        not architecture.has_cost_alerting
    )

    if is_multi_tenant_freemium and both_controls_absent:
        return "critical"  # CRITICAL floor — narrowly-defined trigger
    return "high"  # HIGH default — preserves severity discrimination
```

**Multi-tenant freemium indicators** (both required for the 1st condition):
- Multi-tenant: ≥2 tenants share inference compute (architectural indicator: `multi-tenant`, `B2B SaaS`, `B2C platform`, `tenant isolation`, freemium tier with paying tier)
- Freemium: free-tier user class structurally evident (architectural indicator: `freemium`, `free-tier`, `unauthenticated user`, `anonymous user`, `trial`)

**Absent controls** (both required for the 2nd condition):
- Per-tenant token budget: not declared in DFD; or DFD names budget without hard-cap enforcement
- Cost alerting: cost-per-query p99 alerting / cost-velocity monitoring / denial-of-wallet anomaly detection NONE declared

If only one condition matches (e.g., multi-tenant freemium WITH per-tenant token budget AND cost alerting both present, OR single-tenant WITH both controls absent), severity is HIGH (not CRITICAL).

## Q1 SPLIT — Cross-Agent Vector Decomposition

Context-window exhaustion has two attack vectors with disjoint owning categories. ADR-034 Decision 3 5-row mapping table assigns each vector to exactly one owning category:

```yaml
context_window_exhaustion:
  vector_a_latency_dos:
    owner: "denial-of-service"
    pattern_category: "Cat 13"
    finding_prefix: "D-{N}"
    attacker_intent: "availability disruption (legitimate users see degraded p99 latency)"
    same_class_as: "Cat 12 inference-flooding (per-request resource exhaustion via latency tail)"
    mitigation_surface:
      - "max-context-window enforcement at API gateway with automatic 413-response on overflow"
      - "per-conversation truncation policy with sliding-window limit"
      - "context-window monitoring with anomaly alerting on percentage-of-max usage spikes"
      - "per-tenant context-window cap"
  vector_b_cost_dow:
    owner: "model-theft"
    pattern_category: "Cat 11"
    finding_prefix: "LLM-{N}"
    attacker_intent: "economic damage (the wallet is the bill, not the system uptime)"
    same_class_as: "Cat 10 cost-amplification (extraction-driven resource abuse)"
    mitigation_surface:
      - "per-tenant token budget with hard-cap enforcement at API gateway"
      - "per-tenant context-window cost reconciliation"
      - "denial-of-wallet anomaly detection via cost-velocity monitoring"
      - "automated tenant suspension on budget breach (no manual approval delay)"
```

**Cross-agent emission contract**: same architecture exhibiting context-window-exhaustion exposure surfaces BOTH findings (Cat 13 D-{N} for Vector A latency-DoS AND Cat 11 LLM-{N} for Vector B cost-DoW). Neither is duplicate. ADR-034 Decision 3 audit table assigns each vector to exactly one owning category.

## Pattern Category Disambiguation

### DoS Cat 9 vs. Cat 12/13 (FR-005 / ADR-034 Decision 7)

```yaml
disambiguation_dos_cat9_vs_cat12_13:
  cat_9:
    fires_on: "generic infrastructure resource exhaustion (CWE Top 25 — algorithmic complexity, ReDoS, deserialization-of-untrusted-data, etc.)"
    mitigation_surface: "generic to any HTTP service"
    cwe_root_cause: "CWE-400"
  cat_12:
    fires_on: "LLM-specific inference-request flooding and token exhaustion"
    mitigation_surface: "LLM-API-gateway middleware (per-tenant QPS rate limit, prompt-size cap, token-counting middleware)"
    cwe_root_cause: "CWE-400 (same as Cat 9) + CWE-770"
  cat_13:
    fires_on: "LLM-specific context-window exhaustion (adversarial prompt expansion)"
    mitigation_surface: "max-context-window enforcement, per-conversation truncation policy"
    cwe_root_cause: "CWE-400 (same as Cat 9)"
  non_overlap_contract: "same architecture may legitimately surface Cat 9 + Cat 12 + Cat 13 — same CWE-400 root cause but distinct mitigation surfaces. They are not duplicates and MUST NOT be merged in the threat-report's denial-of-service category section."
```

### model-theft Cat 6 vs. Cat 10/11 (FR-008 / ADR-034 Decision 7)

```yaml
disambiguation_modeltheft_cat6_vs_cat10_11:
  cat_6:
    fires_on: "per-tenant quota / cost-control / billing-attribution gaps at the abstraction level (free-tier abuse, missing API-key authentication, missing inference-volume monitoring)"
    mitigation_surface: "generic to any model-serving infrastructure"
    primary_source: "OWASP LLM10:2025 (already cited in pre-existing Cat 6)"
  cat_10:
    fires_on: "specific cost-amplification attack vectors (recursive prompts, output-asymmetric queries, output-token caps misconfigured)"
    mitigation_surface: "per-query output-token cap, recursive-prompt depth limit, output-amplification-ratio monitoring"
    primary_source: "OWASP LLM10:2025"
    prose_only_reference: "MITRE ATT&CK T1496 Resource Hijacking"
  cat_11:
    fires_on: "denial-of-wallet as a named economic attack class (multi-tenant SaaS economic-failure exposure, cost-velocity monitoring as the dominant control)"
    mitigation_surface: "per-tenant token budget with hard-cap, denial-of-wallet anomaly detection, automated tenant suspension"
    primary_source: "OWASP LLM10:2025"
    prose_only_reference: "MITRE ATT&CK T1496 Resource Hijacking"
    severity_floor: "Q3 RESOLVED 2-condition CRITICAL floor"
  non_overlap_contract: "same architecture may legitimately surface Cat 6 + Cat 10 + Cat 11 — Cat 6 is abstraction-level (per-tenant quotas as a general control class); Cat 10 + Cat 11 are specific named attack vectors. They are not duplicates."
```

## Detection Calibration Note

ADR-034 includes a Detection Calibration Note clarifying that the new Pattern Categories 12/13 (DoS) and 10/11 (model-theft) fire on **structural absence** of named control mechanisms — consistent with F-1 / F-2 / F-4 absence-style detection style. Acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention.

**Examples of structural-absence indicators**:
- "inference endpoint" declared in DFD WITHOUT a "per-tenant rate limit" / "per-tenant QPS limit" component → Cat 12 fires
- "consumer chatbot" declared in DFD WITHOUT a "max-context-window enforcement" / "context-window cap" component → Cat 13 fires
- "RAG advisory" / "recursive prompt" declared WITHOUT "output-token cap" / "recursive-prompt depth limit" component → Cat 10 fires
- "multi-tenant LLM SaaS" / "freemium" declared WITHOUT "per-tenant token budget" AND WITHOUT "cost-per-query alerting" → Cat 11 fires (CRITICAL floor)

**Implicit-but-undeclared controls**: an architecture that has the controls implemented in code but does not surface them in the DFD will surface a finding (acceptable FP per tachi convention; mitigated by the analyst marking the finding as "false positive — control implemented" in the threat-report annotation).

## References

- Schema: `schemas/finding.yaml` v1.8
- Plan: `plan.md`
- Spec: `spec.md`
- Research: `research.md`
- F-3 data-model precedent: `specs/219-asi07-tool-abuse-enrichment/data-model.md`
- ADR-034 (to be authored): `docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md`
