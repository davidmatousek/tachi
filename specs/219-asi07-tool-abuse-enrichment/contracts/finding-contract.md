# Finding IR Contract: Category-9/10 AG-{N} Findings

**Feature**: 219 / F-3 — Heuristic A enrichment of `tool-abuse` agent for OWASP ASI07:2026 coverage
**Schema**: `schemas/finding.yaml` v1.7 (no bump — F-3 reuses existing `AG-{N}` prefix)
**F-A2 contract**: `source_attribution` referential-integrity validation per ADR-028 Decision 5

## Purpose

Document the canonical shape of `AG-{N}` findings emitted by Pattern Category 9 (Insecure Inter-Agent Communication / A2A) and Pattern Category 10 (MCP-to-MCP Trust Propagation) added in F-3 to the existing `tool-abuse` agent.

## Contract Shape

```yaml
id: "AG-{N}"                          # MUST match schema 1.7 id.pattern regex; existing AG prefix
                                      # Single-namespace ID space across all 10 categories (1-8 existing + 9-10 new)
                                      # Sequential numbering — Pattern Category does NOT influence numbering

category: "agentic"                   # Existing enum value — unchanged

component: "{DFD Process component name}"  # Inter-Agent Communication Channel, MCP relay process,
                                            # or relay-agent Process per Feature 142 multi-agent component types

threat: "{2-4 sentence description}"  # Distinguishes Category 9 (A2A surface) vs.
                                       # Category 10 (MCP-to-MCP surface) signal-class

likelihood: LOW | MEDIUM | HIGH       # OWASP factors

impact: LOW | MEDIUM | HIGH           # OWASP factors

risk_level: Critical | High | Medium | Low | Note
                                      # Computed via OWASP 3×3 matrix (severity-bands-shared.md)

mitigation: "{specific mechanism}"    # MUST name at least one concrete mechanism per below

references:                           # Required for AI categories per schema
  - "OWASP ASI07:2026"                # Always present
  - "https://cwe.mitre.org/data/definitions/{287|345}.html"  # Per category
  - <other catalog citations as applicable>

source_attribution:                   # F-A2 contract (ADR-028); REQUIRED on every Category-9/10 finding
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-{287|345}, relationship: related}
  - <optional: AML.T0060 for Cat 9 relay topologies; LLM03 for Cat 10 supply-chain reasoning>

dfd_element_type: Process             # Existing enum

# Auto-populated by orchestrator (no agent action required):
maestro_layer: "L7"                   # Agent ecosystem layer per Feature 084
agentic_pattern: communication_vulnerability | trust_exploitation | none
                                       # Per orchestrator Phase 3.6 / Feature 142
delta_status: NEW | UNCHANGED | UPDATED | RESOLVED | null
                                       # Per Feature 104 baseline-aware logic
baseline_run_id: <run_id> | null
```

## Per-Category source_attribution Invariants

### Pattern Category 9 — Insecure Inter-Agent Communication (A2A)

**Required citations** (every Category-9 finding):

```yaml
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
```

**Optional citations** (when relay-without-taint-propagation indicator fires):

```yaml
  - {taxonomy: atlas, id: AML.T0060, relationship: related}
```

**Catalog resolvability** (verified PRD-time 2026-04-25):
- ASI07 → `schemas/taxonomy/owasp.yaml:308` ✓
- CWE-287 (Improper Authentication) → `schemas/taxonomy/cwe.yaml` ✓
- AML.T0060 (Agent-in-the-Middle) → `schemas/taxonomy/mitre-atlas.yaml` ✓

### Pattern Category 10 — MCP-to-MCP Trust Propagation

**Required citations** (every Category-10 finding):

```yaml
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
```

**Optional citations** (when cross-MCP supply-chain trust-inheritance reasoning is surfaced):

```yaml
  - {taxonomy: owasp, id: LLM03, relationship: related}
```

**Catalog resolvability** (verified PRD-time 2026-04-25):
- ASI07 → `schemas/taxonomy/owasp.yaml:308` ✓
- CWE-345 (Insufficient Verification of Data Authenticity) → `schemas/taxonomy/cwe.yaml` ✓
- LLM03 (Supply Chain) → `schemas/taxonomy/owasp.yaml` ✓

## Mitigation Field Constraint

The `mitigation` field MUST name at least one specific inter-agent / MCP-trust mechanism. Generic phrasing like "secure the inter-agent channel" or "harden the MCP relay" is INSUFFICIENT.

### Acceptable mitigation mechanisms (Category 9)

- `Mutual TLS (mTLS)` — pinned client/server certificates with mutual verification
- `HMAC envelope signing with per-call nonce` — message integrity + replay prevention
- `Asymmetric envelope signature (Ed25519, ECDSA)` — message integrity with public-key verification
- `Nonce-based replay-window enforcement` — bounded message-age window with monotonic counter
- `Inter-agent taint labels` — authority propagation across relays; relay's outputs carry upstream sender's authority labels
- `Mutual JWT authentication` — peer-validated tokens (mTLS fallback when TLS infeasible)
- `Mutual API key authentication` — pre-shared secrets (mTLS fallback)

### Acceptable mitigation mechanisms (Category 10)

- `Per-hop MCP attestation` — signed capability descriptor per hop
- `Signed-capability handoff` — MCP-A signs delegated capability scope; MCP-B validates before accepting
- `MCP-trust-chain validator` — verification component that walks the multi-hop chain end-to-end before invocation
- `Supply-chain trust-chain enforcement` — cross-references with Category 6 supply-chain controls (versioned MCP server registry, signed package distribution, dependency-graph attestation)
- `Taint propagation across MCP hops` — MCP-A's taint labels propagate to MCP-B's outputs

**Rationale**: Adopters reading findings without specific mitigation guidance ("flagged-but-not-fixable") cannot apply the fix without external research. Mirrors F-2 FR-4 mitigation specificity contract.

## Validation Rules

The following invariants are enforced by F-A2 `validate_source_attribution()` at orchestrator Phase 4 (existing validator — no F-3 changes):

1. Every `source_attribution` record's `taxonomy` value is in the closed 5-value enum: `owasp | mitre-attack | mitre-atlas | nist-ai-rmf | cwe`.
2. Every `source_attribution` record's `id` resolves as a top-level `id:` key in `schemas/taxonomy/{taxonomy}.yaml`.
3. Every `source_attribution` record's `relationship` value is in the closed 3-value enum: `primary | related | derived`.

**F-3-specific invariants** (enforced by `tests/scripts/test_tool_abuse_enrichment.py`):

1. Every Category-9 finding has `{taxonomy: owasp, id: ASI07, relationship: primary}` in `source_attribution`.
2. Every Category-9 finding has `{taxonomy: cwe, id: CWE-287, relationship: related}` in `source_attribution`.
3. Every Category-10 finding has `{taxonomy: owasp, id: ASI07, relationship: primary}` in `source_attribution`.
4. Every Category-10 finding has `{taxonomy: cwe, id: CWE-345, relationship: related}` in `source_attribution`.
5. Every Category-9 finding's `mitigation` field names at least one of the acceptable Category-9 mechanisms above.
6. Every Category-10 finding's `mitigation` field names at least one of the acceptable Category-10 mechanisms above.
7. Every Category-9/10 finding's `id` matches `^AG-\d+$` (sub-pattern of schema 1.7 regex).
8. Every Category-9/10 finding's `category` is `agentic`.

## Test Fixtures

Three fixtures land in `tests/scripts/fixtures/tool_abuse_enrichment/`:

### `valid_category_9_a2a_finding.yaml`

```yaml
id: "AG-9"
category: "agentic"
component: "Inter-Agent Communication Channel: Orchestrator-to-Worker"
threat: "An orchestrator agent dispatches workloads to specialized worker agents over plain HTTP without mutual TLS or message signing. A network-positioned attacker on the same compute substrate intercepts and tampers with the orchestrator's instructions; the receiving worker has no authentic-source signal and executes the modified instruction."
likelihood: HIGH
impact: HIGH
risk_level: Critical
mitigation: "Mutual TLS (mTLS) on every inter-agent channel + HMAC envelope signing with per-call nonce + inter-agent taint labels for authority propagation across relays."
references:
  - "OWASP ASI07:2026"
  - "https://cwe.mitre.org/data/definitions/287.html"
  - "https://atlas.mitre.org/techniques/AML.T0060"
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
  - {taxonomy: atlas, id: AML.T0060, relationship: related}
dfd_element_type: "Process"
```

### `valid_category_10_mcp_to_mcp_finding.yaml`

```yaml
id: "AG-10"
category: "agentic"
component: "MCP Relay: MCP-A → MCP-B"
threat: "An agent dispatches to a remote MCP-A server which transparently relays the request to a secondary MCP-B server without validating MCP-A's authority over MCP-B. A compromised or rogue MCP-A injects responses purporting to come from MCP-B; the agent has no per-hop attestation and accepts the response as authoritative."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Per-hop MCP attestation with signed capability descriptors + signed-capability handoff (MCP-A signs the delegated scope; MCP-B validates the signature before accepting) + MCP-trust-chain validator that walks the multi-hop chain end-to-end before invocation."
references:
  - "OWASP ASI07:2026"
  - "https://cwe.mitre.org/data/definitions/345.html"
  - "OWASP LLM03:2025"
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
  - {taxonomy: owasp, id: LLM03, relationship: related}
dfd_element_type: "Process"
```

### `invalid_attribution_finding.yaml`

```yaml
# Negative-test fixture: source_attribution cites an absent taxonomy ID
# F-A2 validate_source_attribution MUST reject this fixture at parse time
id: "AG-99"
category: "agentic"
component: "Test fixture (negative)"
threat: "Negative-test fixture for F-A2 referential-integrity validation."
likelihood: LOW
impact: LOW
risk_level: Note
mitigation: "Test fixture only — never emitted by production agent."
references:
  - "OWASP ASI07:2026"
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}
  - {taxonomy: cwe, id: CWE-99999, relationship: related}  # CWE-99999 absent from catalog → MUST fail validation
dfd_element_type: "Process"
```

## Producer Inventory After F-3

F-3 establishes that `source_attribution` is now populated by:

| Producer | Class | ID Prefix | Source PRD | Validates F-A2 contract on |
|----------|-------|-----------|------------|----------------------------|
| `output-integrity` | New AI agent (LLM tier) | OI-{N} | F-1 (Feature 201) | First independent producer flow |
| `misinformation` | New AI agent (LLM tier) | MI-{N} | F-2 (Feature 206) | Second independent producer flow |
| `tool-abuse` Categories 9-10 | Enrichment of existing AI agent (AG tier) | AG-{N} | F-3 (Feature 219) | Third producer flow — first **enrichment** of existing agent |
| `tool-abuse` Categories 1-8 | Existing AI agent | AG-{N} | Pre-F-3 wiring | Existing populator (extended in prior wiring) |

**F-3 validates the F-A2 contract across two agent classes** (LLM new — F-1 OI + F-2 MI — plus AG enrichment — F-3) in addition to the two-agent-new validation already established by F-1 + F-2.

## References

- `schemas/finding.yaml` v1.7 — finding IR schema (no edit in F-3)
- `schemas/taxonomy/owasp.yaml` — ASI07, LLM03 catalog entries (read-only)
- `schemas/taxonomy/cwe.yaml` — CWE-287, CWE-345 catalog entries (read-only)
- `schemas/taxonomy/mitre-atlas.yaml` — AML.T0060 catalog entry (read-only)
- ADR-028 — `source_attribution` schema extension (Decision 5: parser-tier referential integrity)
- ADR-031 Decision 8 — regex-alternation minor-bump rule (F-3 does NOT invoke; cross-referenced as the asymmetry)
- F-1 contract (precedent): `specs/201-output-integrity-threat-agent/contracts/finding-contract.md`
- F-2 contract (precedent): `specs/206-misinformation-threat-agent/contracts/finding-contract.md`
