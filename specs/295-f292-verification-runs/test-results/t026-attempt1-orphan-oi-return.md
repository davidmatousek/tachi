# T026 attempt-1 orphaned output-integrity agent return (evidence artifact)

**Provenance**: During T012 attempt 1 (2026-07-03), the tachi-orchestrator dispatched its 11 threat agents
with background execution and ended its turn before their completion — the parent instance could never
collect the results (tooling failure; attempt 1 concluded unusable). The child agents kept running and
their results were later delivered to the orchestrating session directly. They were NOT used in any
compiled artifact (attempt 2 was a fresh, fully synchronous run). This file preserves the attempt-1
`tachi-output-integrity` agent's verbatim finding block as **corroborating evidence** for the T013 gate
defect analysis: the OI agent's native output for this architecture uses the `OI-` finding-ID prefix and
cites CWE-943 — both of which are absent from the attempt-2 compiled artifacts.

**Agent**: tachi-output-integrity (attempt-1 dispatch, task a-c045d422a21aaef9 lineage)
**Architecture analyzed**: examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/architecture.md
**Emission-gate summary returned by the agent**: LLM Query Synthesizer → Emit finding (Cat 6 keywords +
execution sink via Retriever→Pinecone); LLM Answer Generator → zero findings (no execution sink);
Anthropic LLM API → categorically ineligible (External Entity); Auth Gateway → not an LLM invoker.

## Verbatim finding block (as returned)

```yaml
id: "OI-1"
category: llm
component: "LLM Query Synthesizer"
threat: "The LLM Query Synthesizer instructs the Anthropic LLM API to emit a Pinecone metadata filter as JSON (intended form: {\"$and\": [{\"tenant_id\": {\"$eq\": \"{requesting_tenant}\"}}, {<<query terms>>}]}), then trusts the LLM-emitted filter as authoritative and forwards it unmodified through the RAG Retriever, which performs no validation, schema/allowlist enforcement, or server-side recomposition before it reaches Pinecone's shared multi-tenant index (Pool model, no namespace-per-tenant separation). If the LLM omits the tenant_id clause -- whether from ordinary model inconsistency or adversarial prompt-injection pressure originating in retrieved corpus content -- the trust assumption that LLM-synthesized query filters are inherently authoritative is violated, and Pinecone returns matching documents from ALL tenants rather than the requesting tenant alone. Execution context is server-side: the malformed filter is executed directly by Pinecone under the service account's cross-tenant reach, functionally equivalent to SQL injection across a tenant boundary but occurring at the vector-search-DSL layer instead of the relational-SQL layer."
likelihood: HIGH
impact: HIGH
risk_level: Critical
mitigation: "Compose the tenant_id clause server-side -- in the RAG Retriever or a dedicated middleware layer, never in the LLM Query Synthesizer -- treating the LLM-emitted filter as an untrusted proposal for the query-terms portion only, never as the source of the tenant clause (pre-retrieval filtering / server-side filter composition). Pin an unbypassable base filter: middleware AND-composes {\"tenant_id\": {\"$eq\": \"<jwt-derived-tenant>\"}} against the LLM-emitted filter and raises SecurityError if the LLM-emitted filter attempts to override the pin -- e.g. via a contradictory tenant_id clause or a nullifying $not wrapper (Mavik Labs 2026 / Authzed base-filter pattern). Migrate off the Pool model to namespace-per-tenant (Pinecone Silo model -- the strongest control per OWASP LLM08:2025): select the Pinecone namespace from the JWT-validated tenant_id before the query runs, so the LLM-emitted filter can never cross a tenant boundary regardless of its content. Layer allowlisted clause keys as defense-in-depth: parse the LLM-emitted filter and reject any clause key outside a closed allowlist, sourcing tenant context exclusively from the validated JWT -- never from request parameters or LLM output."
references:
  - "OWASP LLM08:2025"
  - "OWASP LLM05:2025"
  - "CWE-943"
  - "CWE-89"
source_attribution:
  - taxonomy: owasp
    id: LLM08
    relationship: primary
  - taxonomy: owasp
    id: LLM05
    relationship: related
  - taxonomy: cwe
    id: CWE-943
    relationship: related
  - taxonomy: cwe
    id: CWE-89
    relationship: related
dfd_element_type: "Process"
```

**Note on Cat 6 citation structure**: the agent applied Cat 6's own citation structure (LLM08:2025 primary,
LLM05:2025 related cross-anchor) per the detection-patterns.md Cat 6 definition, with CWE-943 as the
required CWE anchor — matching the spec FR-009 expectation "CWE-943 primary" at the CWE-taxonomy level.
