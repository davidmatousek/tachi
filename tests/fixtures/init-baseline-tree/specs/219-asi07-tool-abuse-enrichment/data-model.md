# Data Model: F-3 ASI07 Tool-Abuse Enrichment

**Feature**: 219 / F-3 — Heuristic A enrichment of `tool-abuse` agent for OWASP ASI07:2026 coverage
**Plan**: [plan.md](./plan.md)

## Entities

### 1. Pattern Category 9 — Insecure Inter-Agent Communication (A2A)

A markdown section appended to `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` after Pattern Category 8.

**Shape**:

```
## Pattern Category 9: Insecure Inter-Agent Communication (A2A)

<paragraph: scope statement — A2A channels (direct RPC, message bus, shared queue, MCP-to-MCP bridge, named pipe, IPC) without declared mutual authentication, message signing, replay protection, or taint propagation; same Heuristic A signal class as existing tool-dispatch coverage>

**Indicators**:
- Architecture includes ≥2 agent Process components connected by a communication channel
- The channel does not declare mutual authentication (mTLS, mutual JWT, mutual API key)
- Inter-agent messages are not signed (no HMAC, no envelope signature, no integrity verification)
- Messages lack timestamp binding or replay-window enforcement
- An agent acts as a message relay between two other agents without declared taint propagation
<may add 1-2 indicators per architect plan-day refinement; target 5 indicators>

**Anti-Indicators** (per Q4 architect plan-day default YES):
- Architectures with exactly one agent (no inter-agent channel) — Category 9 emits zero findings
- Architectures with declared mTLS, message signing, replay protection, AND taint propagation — Category 9 emits zero findings (all four mitigations satisfied)

**Worked Example**:
<clearly-fictional scenario: orchestrator agent dispatches workloads to specialized worker agents over plain HTTP without mTLS or message signing; threat = network-positioned attacker intercepts and tampers with orchestrator's instructions; receiving worker has no authentic-source signal and executes the modified instruction>

**Primary Source**:
- OWASP ASI07:2026 — Insecure Inter-Agent Communication

**Related Sources**:
- CWE-287 Improper Authentication
- MITRE ATLAS AML.T0060 — Agent-in-the-Middle (when relay topology with no taint propagation is detected)

**Mitigations**:
- Mutual TLS (mTLS) on every inter-agent channel
- Inter-agent message signing (HMAC or asymmetric signature) with envelope integrity verification
- Nonce-based replay prevention with replay-window enforcement
- Inter-agent taint labels (authority propagation across relays)
- Per-channel mutual authentication (mutual JWT, mutual API key) where mTLS is infeasible
```

**Constraints**:
- Indicators count: ≥4 (target 5 per architect leaning)
- Worked-example count: ≥1, clearly-fictional framing
- Primary citation: OWASP ASI07:2026 (catalog-resolvable, verified PRD-time)
- Related citations: CWE-287 (catalog-resolvable), AML.T0060 (catalog-resolvable, verified PRD-time)
- Anti-indicators: 1-2 per architect Q4 default YES — formalize multi-agent topology gate
- Pre-existing Categories 1-8 byte-identical pre/post edit (ADR-023 Decision 3)

### 2. Pattern Category 10 — MCP-to-MCP Trust Propagation

A markdown section appended to `detection-patterns.md` after Pattern Category 9.

**Shape**:

```
## Pattern Category 10: MCP-to-MCP Trust Propagation

<paragraph: scope statement — multi-hop MCP trust chains where Agent → MCP-A → MCP-B propagates without per-hop attestation, signed-capability handoff, or trust-chain validator; same Heuristic A signal class as Category 9 but distinct deployment topology>

**Indicators**:
- Architecture declares an agent that dispatches to a remote MCP server which in turn dispatches to a secondary MCP server (multi-hop MCP trust chain)
- The handoff between MCP-A and MCP-B does not declare per-hop attestation
- The agent's authority assumptions over MCP-A do not transitively constrain MCP-B
- The architecture does not declare a trust-chain validator
- Cross-MCP supply-chain assumptions are not declared (the agent treats MCP-B's outputs as authoritative without inheriting MCP-A's trust inheritance)
<may add 1-2 indicators per architect plan-day refinement; target 5 indicators>

**Anti-Indicators** (per Q4 architect plan-day default YES):
- Architectures with exactly one MCP server (no MCP-to-MCP relay) — Category 10 emits zero findings
- Architectures with declared per-hop attestation AND signed-capability handoff AND trust-chain validator — Category 10 emits zero findings (all three mitigations satisfied)

**Worked Example**:
<clearly-fictional scenario: agent dispatches to remote MCP-A server which transparently relays to secondary MCP-B server without validating MCP-A's authority over MCP-B; threat = compromised or rogue MCP-A injects responses purporting to come from MCP-B; agent has no per-hop attestation and accepts response as authoritative>

**Primary Source**:
- OWASP ASI07:2026 — Insecure Inter-Agent Communication

**Related Sources**:
- CWE-345 Insufficient Verification of Data Authenticity
- OWASP LLM03:2025 — Supply Chain (inherited from existing Category 6 supply-chain vocabulary; Pattern Category Disambiguation carves Category 6 from Category 10 — see below)

**Mitigations**:
- Per-hop MCP attestation (signed capability descriptor, per-hop authentication)
- Signed-capability handoff (MCP-A signs the capability scope it delegates to MCP-B; MCP-B validates the signature before accepting)
- MCP-trust-chain validator (verification component or contract that walks the multi-hop chain end-to-end before invocation)
- Supply-chain trust-chain enforcement (cross-reference with existing Category 6 supply-chain controls)
- Taint propagation across MCP hops (MCP-A's taint labels propagate to MCP-B's outputs)
```

**Constraints**:
- Same constraints as Pattern Category 9
- Primary citation: OWASP ASI07:2026 (catalog-resolvable)
- Related citations: CWE-345 (catalog-resolvable), LLM03:2025 (catalog-resolvable, inherited supply-chain vocabulary)
- Anti-indicators: 1-2 per architect Q4 default YES — formalize multi-MCP topology gate

### 3. Pattern Category Disambiguation Subsection

A markdown subsection appended to `detection-patterns.md` after Pattern Category 10 and before `## Primary Sources` (existing line 154 baseline).

**Shape**:

```
## Pattern Category Disambiguation: Category 6 (LLM03 Supply Chain) vs. Category 10 (MCP-to-MCP Trust Propagation)

Category 10 cites OWASP LLM03:2025 as `relationship: related` per the existing Category 6 supply-chain vocabulary. This creates a **non-overlapping by design** carve formalized in ADR-032 Decision 7:

- **Category 6** fires on **upstream ingestion** of plugins / tools / MCP servers (sourcing, registration, manifest pinning, signed package distribution at registry time).
- **Category 10** fires on **runtime trust propagation** between already-registered MCP servers (per-hop attestation, signed-capability handoff, transitive authority validation at invocation time).

The same architecture may legitimately surface BOTH findings — e.g., if MCP-A is unsigned at registration (Category 6) AND MCP-A relays to MCP-B without per-hop attestation (Category 10), both are valid findings describing distinct architectural gaps. They are not duplicates and should not be merged in the threat-report's Agentic-category section.
```

**Constraint**: This subsection is required per PRD FR-2 (Pattern Category Disambiguation paragraph). Spec FR-006 codifies the carve. ADR-032 Decision 7 formalizes the non-overlap contract.

### 4. AG-{N} Finding for Categories 9 and 10

The atomic output unit emitted by the enriched `tool-abuse` agent for Pattern Categories 9 and 10. Conforms to `schemas/finding.yaml` v1.7 (existing schema; F-3 introduces no schema bump).

**Required fields** (per `schemas/finding.yaml`):

| Field | Type | Constraint |
|-------|------|------------|
| `id` | string | Matches regex `^(S\|T\|R\|I\|D\|E\|AG\|LLM\|AGP\|OI\|MI)-\d+$`; uses `AG-{N}` prefix; sequential numbering across all 10 categories |
| `category` | enum | Must be `agentic` (existing enum value — unchanged) |
| `component` | string | DFD component name (Inter-Agent Communication Channel name, MCP relay name, or relay-agent Process name) |
| `threat` | string | 2-4 sentence threat description distinguishing A2A (Cat 9) vs. MCP-to-MCP (Cat 10) signal-class |
| `likelihood` | enum | `LOW` / `MEDIUM` / `HIGH` per OWASP factors |
| `impact` | enum | `LOW` / `MEDIUM` / `HIGH` per OWASP factors |
| `risk_level` | enum | Computed via OWASP 3×3 matrix |
| `mitigation` | string | Names ≥1 specific inter-agent / MCP-trust mechanism (mTLS, HMAC + nonce, per-hop attestation, signed-capability handoff, etc.) |
| `references` | list[string] | At minimum `OWASP ASI07:2026` + applicable CWE URL |
| `dfd_element_type` | enum | `Process` (existing) |
| `source_attribution` | list[record] | Required per Categories 9/10 contract — see below |

**source_attribution invariants (Category 9)**:

```yaml
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}      # REQUIRED
  - {taxonomy: cwe, id: CWE-287, relationship: related}      # REQUIRED
  - {taxonomy: atlas, id: AML.T0060, relationship: related}  # OPTIONAL — when relay-without-taint-propagation indicator fires
```

**source_attribution invariants (Category 10)**:

```yaml
source_attribution:
  - {taxonomy: owasp, id: ASI07, relationship: primary}      # REQUIRED
  - {taxonomy: cwe, id: CWE-345, relationship: related}      # REQUIRED
  - {taxonomy: owasp, id: LLM03, relationship: related}      # OPTIONAL — when cross-MCP supply-chain trust-inheritance reasoning is surfaced in description
```

**Validation**: F-A2 `validate_source_attribution()` at orchestrator Phase 4 must return no errors on every Category-9/10 finding. Catalog resolvability verified PRD-time:
- ASI07 → `schemas/taxonomy/owasp.yaml:308` ✓
- LLM03 → `schemas/taxonomy/owasp.yaml` ✓
- CWE-287 → `schemas/taxonomy/cwe.yaml` ✓
- CWE-345 → `schemas/taxonomy/cwe.yaml` ✓
- AML.T0060 → `schemas/taxonomy/mitre-atlas.yaml` ✓ (distinct from F-2's confirmed-absent AML.T0042)

### 5. Multi-Agent / Multi-MCP Topology Gate (FR-011)

A detection-workflow invariant enforced by the enriched `tool-abuse` agent on Pattern Categories 9 and 10. Predicates over the architecture DFD:

| Pattern Category | Topology Predicate | Emission Behavior |
|------------------|--------------------|-------------------|
| 1-8 (existing) | Trigger keyword match on Process | Existing logic — emit findings per pattern |
| 9 (A2A) | (≥2 agent Process components) AND (communication channel between them) | Emit findings only when predicate is TRUE; emit zero findings when FALSE |
| 10 (MCP-to-MCP) | Multi-hop MCP trust chain (Agent → MCP-A → MCP-B) | Emit findings only when predicate is TRUE; emit zero findings when FALSE |

**Invariants**:
- Single-agent architectures: Categories 9 + 10 emit ZERO findings (Categories 1-8 fire as today)
- Single-MCP architectures: Category 10 emits ZERO findings (Categories 5-8 fire as today on the single MCP server)
- The gate is enforced in agent prose (Detection Workflow Step 5 references list extension) plus pattern-catalog Anti-Indicators sections per Q4 architect default YES
- Byte-identity guarantee on 5 non-multi-agent baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) under `SOURCE_DATE_EPOCH=1700000000` follows from the gate's zero-emission default on these baselines (SC-010 BLOCKER)

### 6. Tool-Abuse Agent Metadata (Existing — Modified Additively)

YAML frontmatter at `.claude/agents/tachi/tool-abuse.md` lines 12-19. Pre-edit:

```yaml
category: agentic
threat_class: AG
dfd_targets: [Process]
owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025]
output_schema: ../../../schemas/finding.yaml
```

Post-F-3 edit (additive — `ASI-07` appended):

```yaml
category: agentic
threat_class: AG
dfd_targets: [Process]
owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]
output_schema: ../../../schemas/finding.yaml
```

**Constraint**: Pre-existing entries byte-identical (grep-checkable per SC-001). No other metadata fields modified. `category`, `threat_class`, `dfd_targets`, `output_schema` unchanged.

### 7. ADR-032 (Public Per-Feature Architecture Decision Record)

A new file at `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`. Conforms to ADR-027/028/029/030/031 dual-commit Proposed → Accepted pattern.

**Required body sections**:

| Section | Content |
|---------|---------|
| Status | `Proposed` initially; transitions to `Accepted` at PR merge |
| Date | Initial Proposed date + Accepted date; SHA fill post-merge |
| Decision 1 | Heuristic A enrichment vs. new agent — signal-class identity rationale |
| Decision 2 | Additive-only edit discipline per ADR-023 Decision 3 — byte-identity proof on Categories 1-8 |
| Decision 3 | No schema bump — reuses `AG-{N}` prefix; first BLP-01 detection feature with no schema bump |
| Decision 4 | No consumers-list edit — `tool-abuse` already at `finding-format-shared.md:18` |
| Decision 5 | No functional orchestrator/dispatch-rules edit — `tool-abuse` already fully registered (cosmetic Q2 annotation per architect plan-day decision is documentation-only) |
| Decision 6 | Public ADR omits commercial framing per SDR-001 Option C governance contract |
| Decision 7 | Pattern Category Disambiguation — Category 6 (LLM03 supply-chain) vs. Category 10 (MCP-to-MCP trust propagation) non-overlap carve |
| Cross-references | ADR-021, ADR-023, ADR-027, ADR-028, ADR-030 Decision 1 (signal-class taxonomy in LLM tier as different application of same rule), ADR-031 Decision 8 (regex-alternation minor-bump rule as the **asymmetry** F-3 does NOT invoke) |
| Revision History | Table tracking Proposed date / Accepted date / post-merge SHA |
| 24-file zero-edit invariant | Grep-auditable enumeration of the 24 unchanged detection-tier files |

**Constraints**:
- Zero MAESTRO references in Decision sections (mirrors agent file invariant per ADR-023 Decision 2)
- Zero commercial framing per SDR-001 Option C — public ADR stands on technical merits only
- ADR number reconfirmed at plan time (PRD-time verified: ADR-031 highest existing → ADR-032 next-available)

## State Transitions

### F-3 Build State Machine

```
[PRD Approved] → [Spec Approved] → [Plan Approved] → [Tasks Approved] → [Build Wave 1.0]
                                                                              │
                                                                              ▼
[Wave 1.0: Catalog re-verify] → [Wave 1.1: ADR-032 Proposed + tool-abuse.md edits + fixtures]
                                                                              │
                                                                              ▼
[Wave 2: Categories 9 + 10 + Disambiguation + Primary Sources extension] ── [Wave 2 EOD: byte-identity validation]
                                                                              │
                                                                              ▼
[Wave 3: Multi-agent example regen + 5-baseline byte-identity + tests pass]
                                                                              │
                                                                              ▼
[Wave 4: Code review + ADR-032 Accepted + PR ready + merge + Coverage Matrix update + delivery retro]
                                                                              │
                                                                              ▼
                                                             [Buffer Day 2: concurrency hedge]
                                                                              │
                                                                              ▼
                                                                      [F-3 Closed]
```

### ADR-032 Lifecycle

```
[NOT EXIST] → [Wave 1.1: Proposed commit (Status=Proposed, no merge SHA)]
                                                  │
                                                  ▼
                                  [Wave 4: Accepted transition (Status=Accepted, provisional merge date)]
                                                  │
                                                  ▼
                                  [Post-merge: SHA fill on Revision History table]
                                                  │
                                                  ▼
                                              [Final Accepted]
```

### Finding Emission Per Architecture Topology

| Architecture | Categories 1-8 Emission | Category 9 Emission | Category 10 Emission |
|--------------|-------------------------|---------------------|----------------------|
| Single-agent (no MCP) | Per existing logic | ZERO (topology gate) | ZERO (topology gate) |
| Single-agent + single-MCP | Per existing logic | ZERO (topology gate) | ZERO (topology gate) |
| Multi-agent + single-MCP | Per existing logic | ≥1 finding (gate satisfied) | ZERO (topology gate) |
| Single-agent + multi-MCP | Per existing logic | ZERO (topology gate) | ≥1 finding (gate satisfied) |
| Multi-agent + multi-MCP | Per existing logic | ≥1 finding (gate satisfied) | ≥1 finding (gate satisfied) |

**5 non-multi-agent baselines fall in row 1 or row 2 → ZERO Category-9/10 emissions → byte-identical PDFs under `SOURCE_DATE_EPOCH=1700000000` (SC-010 BLOCKER).**

## Validation Rules

1. Every emitted Category-9/10 `AG-{N}` finding MUST pass F-A2 `validate_source_attribution()` at orchestrator Phase 4.
2. Every Category-9 finding MUST cite `{taxonomy: owasp, id: ASI07, relationship: primary}` AND `{taxonomy: cwe, id: CWE-287, relationship: related}`.
3. Every Category-10 finding MUST cite `{taxonomy: owasp, id: ASI07, relationship: primary}` AND `{taxonomy: cwe, id: CWE-345, relationship: related}`.
4. AML.T0060 (Category 9) and LLM03 (Category 10) are OPTIONAL related citations — present when the topology indicators warrant.
5. The `mitigation` field MUST name at least one specific inter-agent / MCP-trust mechanism — NOT generic "secure the inter-agent channel".
6. The `id` MUST match `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$` regex (existing schema 1.7 pattern; AG enumerated).
7. The agent-file post-edit `wc -l` MUST return ≤150.
8. `grep -i maestro` on `tool-abuse.md` AND `detection-patterns.md` MUST return empty (zero MAESTRO references).
9. Categories 1-8 byte-identical pre/post edit (structural diff returns empty for unchanged regions).
10. 5 non-multi-agent baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` (`test_backward_compatibility.py` passes).
