# Data Model: Output-Integrity Cross-Sink Refinement

**Feature**: F-292
**Phase**: 1 (Design)
**Date**: 2026-05-14

This feature is a docs-heavy refinement, not a data-bearing application. The "data model" describes the **structural shape of the markdown content additions** to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` and `.claude/agents/tachi/output-integrity.md`, plus the **schema shape of the Memory-Promotion Rules worked example** that appears inline.

---

## 1. Pattern Category 6 (New Top-Level Category)

**Insertion point**: `.claude/skills/tachi-output-integrity/references/detection-patterns.md` immediately after the existing Cat 5 final paragraph (line 151 EOF area).

**Structure** (mirrors Cat 1–5 verbatim — same shape, same heading depth, same field order):

```markdown
### 6. Vector / Search-DSL Injection

> *Intro paragraph (1–2 lines):* LLM-synthesized filters for vector databases (Qdrant, Pinecone) and structured search DSLs (Elasticsearch, hybrid search) gate tenant/RBAC scoping. When the LLM emits filter clauses without server-side composition, the resulting query can bypass the tenant-scoping clause — functionally equivalent to SQL injection against a tenant boundary.

- **Primary citation**: OWASP LLM08:2025 Vector and Embedding Weaknesses; OWASP LLM05:2025 Improper Output Handling (cross-anchor)
- **Related citations**: CWE-943 (Improper Neutralization of Special Elements in Data Query Logic — primary CWE); CWE-89 (SQL Injection — taxonomic neighbor); CWE-94 (Code Injection — when filter is templated as expression)
- **Trigger keywords**: `qdrant`, `pinecone`, `metadata filter`, `must_not`, `must` (in vector-filter context), `tenant_id`, `namespace`, `embedding query`, `hybrid search`, `elasticsearch DSL`, `vector index`, `RAG retrieval filter`
- **Applicable DFD element types**: Process
- **Indicators**:
  - ◆ LLM Process emits filter/query content into a vector-DB or structured-search query interface
  - ◆ Multi-tenancy signal present (`tenant_id` payload field, namespace per tenant, RBAC scoping)
  - ◆ Filter composition happens at the LLM-output layer, not the application/middleware layer
  - ◆ Architecture lacks server-side filter pinning or base-filter override-prevention

> **Distinguishing prose (per PM M-2 resolution)**: This is an **output-handling** signal — the LLM's *filter SYNTHESIS* goes wrong. It is distinct from `data-poisoning` corpus-side signals where the *corpus CONTENT* goes wrong. Both findings can co-emit on the same multi-tenant RAG architecture without contradiction. See `.claude/agents/tachi/data-poisoning.md` for the corpus-content surface.

#### Worked Example

**Finding**: `OI-{N} Multi-tenant RAG metadata filter omits tenant_id clause (vector-DB injection)`

**Architecture**: An LLM Process synthesizes a Pinecone metadata filter from user input. The application sends the filter directly to Pinecone without server-side composition. The filter is supposed to include `tenant_id == "{requesting_tenant}"` but the LLM-synthesized filter only contains the user's query terms, omitting the tenant clause entirely. As a result, the query returns documents from all tenants whose `tenant_id` is *not* explicitly excluded — functionally equivalent to SQL injection across tenant boundaries.

**Mitigation** (at least one required; defense-in-depth recommends all three):
- **Pre-retrieval filtering / server-side filter composition**: Application composes the tenant_id clause server-side before the filter reaches Pinecone. The LLM-emitted filter is wrapped, not interpreted as authoritative.
- **Base filter that cannot be overridden** (Mavik Labs 2026 / Authzed pattern): Middleware injects the tenant_id pin; the LLM-emitted filter is composed with `AND` against the pin and raises `SecurityError` if the LLM-emitted filter attempts to override the pin.
- **Namespace-per-tenant** (Pinecone Silo model — strongest control per OWASP): Each tenant has a dedicated Pinecone namespace; the LLM-emitted filter never crosses tenant boundaries because the namespace is fixed at the application layer before the query runs.
- **Allowlisted clause keys**: The LLM-emitted filter is parsed and rejected if any clause key is not in the application's allowlist. Tenant context is extracted from validated JWT, never from request parameters.
```

**Total Cat 6 content estimate**: ~50 lines of markdown.

---

## 2. Cat 2 Trigger-Keyword List Extension (Gap 2 — Package Manager / CI Workflow)

**Modification point**: Existing Cat 2 (Server-Side Execution Sinks) Trigger Keywords line in `detection-patterns.md`.

**Operation**: Append to the existing trigger-keyword list (additive-only edit; pre-existing keywords preserved byte-identical).

**Keywords added**:
```
npm install, pip install, apt install, brew install, gh workflow, actions/, uses:, package-lock, requirements.txt
```

**Worked Example Added under Cat 2** (after existing SQLi / OS Command / Code worked example):

```markdown
##### Sub-example: Package-Manager / CI-Workflow Injection (AI Coding Assistant)

**Finding**: `OI-{N} AI coding assistant emits attacker-controlled package name into npm install (supply-chain execution sink)`

**Architecture**: An LLM Process generates an install script or GitHub Actions workflow YAML from user input. The output contains `npm install <attacker-controlled-name>` or a `uses: malicious/action@<commit>` step. The CI runner or developer machine executes the LLM output without validation.

**Real-world urgency** (2026 incident record):
- **SANDWORM_MODE** (Sep 2025 → Apr 2026): self-propagating npm worm injecting prompt-injection blocks into AI assistant tool descriptions; affected 170+ npm packages, 404 malicious versions on a single day
- **LiteLLM PyPI compromise** (Mar 2026): `pip install litellm` for ~4 hours silently exfiltrated env vars, AWS creds, SSH keys via `.pth` payload
- **Agentic Workflow Injection (AWI)** (arXiv 2605.07135): formalized attack pattern in GitHub Actions

**Mitigation** (at least one required; defense-in-depth recommends all three):
- **Allowlist of registries and scopes** (NVIDIA / Nesbitt 2026 guidance): agent can only resolve names from a fixed registry list (your private registry + a handful of vetted public packages); arbitrary npm / PyPI names are rejected before resolution
- **Sandbox isolation** (canonical 2026 isolation trio): microVM (Firecracker), gVisor user-space kernel, or hardened container; install phase fetches/verifies; execution phase runs in sandbox
- **Sigstore-backed signature verification**: `npm audit signatures` or PyPI equivalent gates the install on cryptographic provenance; rejected installs fail closed
```

**Total Cat 2 extension estimate**: ~25 lines of additional markdown (sub-example + mitigation block).

---

## 3. Cross-Agent Handoff Sinks Subsection (Gap 3 — Navigational, No New Emission)

**Insertion point**: `detection-patterns.md` immediately after Cat 6 (NEW), before EOF.

**Structure**:

```markdown
## Cross-Agent Handoff Sinks (Navigational — NO emission from `output-integrity`)

> **Boundary phrase**: LLM output is **harmless as text, dangerous as tool argument or memory entry.** The `output-integrity` agent does NOT emit findings on tool-call-argument or durable-memory-write flows — those flows are owned by adjacent agents.

### When LLM output flows into a tool-call argument

Cross-link target: `.claude/agents/tachi/tool-abuse.md` (Pattern Categories 9 "Insecure Inter-Agent Communication" and 10 "MCP-to-MCP Trust Propagation").

The `tool-abuse` agent owns the surface where LLM-synthesized strings become parameters of downstream tool invocations (MCP calls, function-calling middleware, plugin APIs). The signal class is **command/parameter injection across an agent-to-agent communication channel**, distinct from the encoding/sanitization signal class owned here.

### When LLM output flows into a durable memory write

Cross-link target: `.claude/agents/tachi/data-poisoning.md` (LLM03 / LLM04 / OWASP ASI06 Memory & Context Poisoning).

The `data-poisoning` agent owns the surface where LLM-synthesized content gets persisted to a durable knowledge store (RAG corpus, agent memory, knowledge base) that future agent decisions will consult. The signal class is **persistent integrity violation of agent durable state**, distinct from the encoding/sanitization signal at the output-handling moment.

### Mitigation Pattern: Memory-Promotion Rules

The recommended mitigation when LLM output may flow into a durable memory store is **structured allowlist gating before promotion**. The pattern names three required fields:

- `promotable_keys`: allowlist enum of which memory-store keys the agent may write
- `value_schema`: reference to a JSON-schema validating the shape of permitted values
- `tenant_scope`: pin binding the write to the requesting tenant's namespace

#### Worked schema example (YAML)

```yaml
# Memory-Promotion Rules — agent durable-write gate
memory_promotion_rules:
  promotable_keys:
    enum:
      - user_preferences.theme
      - user_preferences.timezone
      - session_summary
    description: |
      The agent may only write to these three keys. Any write to a key
      not in this list raises PromotionDeniedError and is logged.
  value_schema:
    $ref: "schemas/agent-memory-value.yaml"
    description: |
      Every promoted value must validate against this schema. Schema
      rejects malformed or unexpected payloads. See A-MEMGUARD framework
      (arXiv 2510.02373) for the canonical "staging buffer with validation"
      pattern that this allowlist implements.
  tenant_scope:
    binding: "request.tenant_id"
    description: |
      The write is namespaced to the requesting tenant's memory store.
      Cross-tenant memory writes are rejected. AWS Bedrock AgentCore
      Memory exposes `scope` dicts implementing this pattern.
  optional_layered_controls:
    staging_buffer:
      enabled: true
      description: |
        Writes go to a staging buffer first; promotion to live store
        requires schema validation + (optional) human approval.
    human_approval_gate:
      enabled: false
      description: |
        Per A-MEMGUARD, additive control for modifications that affect
        future session behavior. Disabled by default; enable for
        high-trust memory categories.
```

**Distinguishing prose**: This mitigation pattern lives in `output-integrity`'s navigational surface, but the durable-memory-write *detection* is owned by `data-poisoning`. Adopters implementing the rules should consult `data-poisoning` for the detection-side workflow and `output-integrity` for the output-handling-side framing.

**Industry anchors**:
- OWASP ASI06 Memory & Context Poisoning (NOT OWASP LLM04 — LLM04 is training-time data poisoning, distinct surface)
- OWASP Agent Memory Guard project
- A-MEMGUARD (arXiv 2510.02373) — "staging buffer with validation"
- MemoryGraft (arXiv 2512.16962) — persistent memory poisoning attack
- MINJA Memory Injection Attack (arXiv 2601.05504, >95% success rate without schema validation)
- AWS Bedrock AgentCore Memory; Vertex AI Memory Bank IAM Conditions
```

**Total Gap 3 subsection estimate**: ~75 lines of markdown (boundary prose + two cross-link subsections + Memory-Promotion Rules worked example + industry anchors).

---

## 4. Output-Integrity Agent Purpose Section Cross-Link Prose

**Insertion point**: `.claude/agents/tachi/output-integrity.md` Purpose section, after line 27 (end of main scope prose), before the existing "Out of scope" forward-reference to F-4 trust-exploitation.

**Operation**: Append ≤10 lines of navigational prose. Total agent-file diff MUST be ≤10 lines (FR-009 / SC-005).

**Content**:

```markdown
**Cross-agent handoff scope (navigational, no emission)**: When LLM output flows into a tool-call argument (MCP call, function-calling middleware, plugin API), the detection surface is owned by `tool-abuse` ([`.claude/agents/tachi/tool-abuse.md`](tool-abuse.md), Pattern Categories 9–10). When LLM output flows into a durable memory write (RAG corpus, agent memory, knowledge base), the detection surface is owned by `data-poisoning` ([`.claude/agents/tachi/data-poisoning.md`](data-poisoning.md), OWASP ASI06 Memory & Context Poisoning). This agent does NOT detect those handoff cases — it owns the encoding/sanitization signal class only, per ADR-030 Decision 2. See the Cross-Agent Handoff Sinks subsection in [`detection-patterns.md`](../../skills/tachi-output-integrity/references/detection-patterns.md) for the boundary framing and the Memory-Promotion Rules mitigation pattern.
```

**Line count**: 6 lines of prose (well under the ≤10 line FR-009 cap), allowing 4 lines of headroom for paragraph break or formatting.

---

## 5. ADR-045 Structure (New File)

**Path**: `docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md`

**Header**:
```markdown
# ADR-045: Output-Integrity Cross-Sink Refinement (F-292)

**Status**: Proposed → Accepted (dual-commit governance per ADR-027 lineage)
**Date**: 2026-05-14 (Proposed) → 2026-05-{N} (Accepted, post-merge SHA fill)
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Feature**: F-292 (PRD #292)
**Lineage**: Heuristic A enrichment branch, same-agent enrichment (8th BLP-01 execution)
**Cross-references**: ADR-021, ADR-023, ADR-027, ADR-028, ADR-030, ADR-032, ADR-034, ADR-035

## Context

(Brief statement of the gap surfacing via @armorer-labs discussion #179 comment, the three pattern-catalog gaps, and why F-292 is the eighth Heuristic A enrichment execution at single-agent scope.)

## Decisions

### D1: Heuristic A enrichment vs new agent — same-agent enrichment within `output-integrity`

(Inheritance from ADR-030 D1 + ADR-032 D1 signal-class taxonomy.)

### D2: Additive-only edit discipline per ADR-023 D3

(Pre-existing Cat 1–5 byte-identical; Cat 6 appended after Cat 5; cross-link subsection appended after Cat 6.)

### D3: No schema bump — operational signal of signal-class identity preservation

(F-292 reuses `OI-{N}` prefix; no `schemas/finding.yaml` modification; schema-version unchanged.)

### D4: No consumers-list edit

(`output-integrity` already registered in `tachi-shared/references/finding-format-shared.md` consumers list.)

### D5: No functional orchestrator/dispatch edit

(`output-integrity` already in orchestrator.md and dispatch-rules.md.)

### D6: Public ADR omits commercial framing per SDR-001 Option C

(F-292 ADR stands on technical merits only; no commercial / strategic cross-references.)

### D7: Pattern Category Disambiguation — Cat 6 boundary carve + cross-link prose

(Cat 6 boundary from Cat 2 distinguished via CWE-943 primary vs CWE-89 primary; Cross-Agent Handoff Sinks subsection makes navigational pointer to tool-abuse + data-poisoning explicit.)

## Consequences

(Enrichment-branch precedent reinforced; eighth execution of Heuristic A at finer-grained scope; future vector-DB engines and package-manager surfaces have a clean extension path.)

## Cross-Reference Matrix

| ADR | Relevance |
|---|---|
| ADR-021 | SOURCE_DATE_EPOCH determinism — byte-identity gate |
| ADR-023 | Lean-agent + additive-only shared-reference discipline |
| ADR-027 | F-A1 taxonomy crosswalk — F-292 reuses LLM05 + LLM08 + CWE-943 |
| ADR-028 | F-A2 source_attribution contract — F-292 inherits populator from F-1 |
| ADR-030 | F-1 direct precedent — F-292 enriches the same agent |
| ADR-032 | F-3 single-agent enrichment-branch precedent — closest structural sibling |
| ADR-034 | F-5 two-agent enrichment-branch precedent |
| ADR-035 | F-6 three-agent enrichment-branch precedent (ML Top 10 bundle) |
```

**Total ADR-045 estimate**: ~200 lines following the ADR-032 7-decision template structure.

---

## 6. Multi-Tenant RAG Baseline (Conditional, Q2 = Add)

**Path**: `examples/multi-tenant-rag-app/`

**Files**:
```
examples/multi-tenant-rag-app/
├── architecture.md       # Mermaid description of LLM Process → Pinecone metadata filter → multi-tenant query
├── README.md             # Adopter-facing description of the example
├── threats.md            # Auto-generated SARIF + Markdown by tachi.threat-model
├── threat-report.md      # Auto-generated narrative
├── risk-scores.md        # Auto-generated risk scoring
└── (other auto-regenerated artifacts as produced by the tachi pipeline)
```

**Architecture invariants**:
- LLM Process emits Pinecone `metadata` filter into a multi-tenant query interface
- `tenant_id` field present in metadata schema (signaling multi-tenancy)
- Filter composition happens at the LLM-output layer (the architectural failure mode)
- The application sends the filter directly to Pinecone without server-side composition (the trigger)

**Expected emissions**:
- At least one `OI-{N}` finding under the new Cat 6 surface (per FR-012 + SC-001 + SC-015 conditional)
- Possible additional findings from existing Cat 2–5 categories (acceptable; the baseline is not constrained to a single emission)
- Possible `data-poisoning` findings on the corpus-side (acceptable; distinguishing-prose requirement preempts reader confusion per PM M-2)

**Verification**: Reproduces byte-identical under `SOURCE_DATE_EPOCH=1700000000`; listed in `examples/README.md` standardized examples table (per Architect M4).

---

## 7. CHANGELOG Entry

**Path**: `CHANGELOG.md` (release-please-generated section for the next minor release)

**Attribution form** (per F-260 precedent):
```markdown
### Features

* **292:** output-integrity cross-sink refinement ([#{PR}](https://github.com/davidmatousek/tachi/issues/{PR})) ({SHA7}))
```

**Maintainer-authored path additions** (if Q5 → b):
- Commit trailer: `Co-Authored-By: @armorer-labs <handle@github>` (if contributor agrees)
- Explicit attribution line under the entry: `Surfaced by @armorer-labs in discussion #179.`

---

## 8. Discussion #179 Thread Replies

**Two replies in the contribution chain**:

1. **48-hour two-choice offer** (T-0 + 48h, posted 2026-05-14 to 2026-05-16):
   - Path (a) — contributor authors PR with maintainer steerage (F-260 precedent)
   - Path (b) — maintainer authors PR with explicit CHANGELOG + commit-trailer attribution
   - 7-day response SLA (calendar days)
   - Default fallback to (b) at SLA breach

2. **24-hour delivery comment** (T-0 + 7d + 24h, posted at PR merge):
   - PR link
   - `detection-patterns.md` anchor for each gap closure (Cat 6 / Cat 2 keyword extension / Cross-Agent Handoff Sinks subsection)
   - CHANGELOG section link
   - Attribution line
   - Best-effort 24h SLA; next-business-day acceptable

3. **(Conditional) T+5d courtesy nudge** (per PM L-3 / Architect L3 resolution):
   - Posted 2026-05-19 if no contributor response yet
   - States the maintainer track is proceeding and attribution is preserved regardless

---

## Summary

This data model is entirely composed of **markdown content shapes and YAML schema shapes** — no relational data, no API entities, no database schemas. The "model" is the structural contract that the implementation must produce:
- 1 new Pattern Category 6 (~50 lines markdown in `detection-patterns.md`)
- 1 Cat 2 keyword-list extension (~25 lines markdown sub-example)
- 1 new Cross-Agent Handoff Sinks subsection (~75 lines markdown including YAML schema example)
- ≤10 lines cross-link prose in `output-integrity.md`
- 1 new ADR-045 file (~200 lines)
- 1 optional new baseline (`examples/multi-tenant-rag-app/`)
- 1 CHANGELOG entry
- 2–3 discussion thread replies

Total markdown / YAML / file additions estimate: ~600 lines (excluding the auto-regenerated baseline artifacts).
