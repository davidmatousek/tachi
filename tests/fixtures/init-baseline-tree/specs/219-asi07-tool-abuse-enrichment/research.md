# Research Summary: F-3 ASI07 Tool-Abuse Enrichment

**Feature**: 219 / F-3 — Heuristic A enrichment of `tool-abuse` agent for OWASP ASI07:2026 coverage
**Date**: 2026-04-25
**PRD**: [docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md](../../docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md)

## Knowledge Base Findings

The institutional-knowledge index does not carry an entry specific to Heuristic A enrichment yet — F-3 is the **first execution** of the enrichment branch. Prior BLP-01 KB entries cover the **new-agent** branch of Heuristic A only:

- F-1 (Feature 201) `output-integrity` agent — established the lean-agent shape conformance for ADR-023 detection-variant agents and the additive-edit discipline for orchestrator dispatch wiring.
- F-2 (Feature 206) `misinformation` agent — established the **second-execution-deep** validation of the new-agent shape; the F-2 retrospective documented the regex-alternation minor-bump rule (ADR-030 Decision 8 extension) and the three-signal-class taxonomy within the LLM tier.

**Key lesson F-3 inherits from F-1 + F-2**: Pattern catalogs MUST cite only catalog-resolvable taxonomy IDs in `source_attribution` (`schemas/taxonomy/{owasp,cwe,mitre-atlas,nist-ai-rmf}.yaml`). F-1 verified this on `OI-{N}` findings; F-2 verified it on `MI-{N}` findings; F-3 extends the contract to enrichment of an existing producer (`AG-{N}`).

**Zero-MAESTRO-reference invariant (ADR-023 Decision 2)**: F-3 grep-verified at PRD time on both target files — `tool-abuse.md` and `detection-patterns.md` carry **0** MAESTRO references. Additive edits MUST preserve this invariant.

## Codebase Analysis

### Existing target files (PRD-time baselines)

| File | Lines | State | F-3 Edit Posture |
|------|-------|-------|------------------|
| `.claude/agents/tachi/tool-abuse.md` | 98 | 5 OWASP refs, 8 CWE/ATLAS refs in Step 5, `## Purpose` paragraph | Additive — append ASI-07 to metadata, append AML.T0060/CWE-287/CWE-345 to Step 5, extend `## Purpose` 1-3 lines |
| `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` | 163 | 8 Pattern Categories (1-8), Primary Sources at line 154 | Additive — append Categories 9 + 10 after Category 8, extend Primary Sources |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | n/a | `tool-abuse` already at line 18 in consumers list | **NO EDIT** — already present |
| `schemas/finding.yaml` | n/a | `schema_version: "1.7"`, `id.pattern` includes `AG` | **NO EDIT** — no schema bump |

### F-3-specific structural advantages over F-1 and F-2

| Dimension | F-1 (output-integrity) | F-2 (misinformation) | F-3 (tool-abuse enrichment) |
|-----------|------------------------|----------------------|------------------------------|
| New agent file | YES | YES | **NO** |
| New skill directory | YES | YES | **NO** |
| Schema version bump | 1.4 → 1.5 | 1.6 → 1.7 | **NO** (stays 1.7) |
| New ID prefix | OI | MI | **NO** (reuses AG) |
| `finding-format-shared.md` consumers edit | YES | YES | **NO** (`tool-abuse` already present) |
| Orchestrator dispatch edits | YES | YES | **NO** (cosmetic annotation carve-out only) |
| Pattern categories added | 5 | 5 | **2** |

**F-3 is structurally the smallest BLP-01 detection delivery** — 2 additive-edit surfaces vs. F-1/F-2's 6+ surfaces.

### Naming conventions to follow

- ADR file naming: `ADR-NNN-feature-slug.md` (lowercase, kebab-case). PRD-time verified next-available number is **032**.
- Pattern Category headers: `## Pattern Category N: <Name>` (matches existing 1-8 in `detection-patterns.md`).
- Indicator bullets: `-` prefix, indicators ≥4 per category (matches existing 5-7 indicators per category).
- Worked example: prose paragraph + threat description + agent reasoning trace.
- Mitigations: bulleted list of named mechanisms (mTLS, HMAC signing, etc.).

## Architecture Constraints

### Active ADRs F-3 inherits from

- **ADR-021** SOURCE_DATE_EPOCH determinism — byte-identity baseline harness (5 non-multi-agent baselines must regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`).
- **ADR-023** Threat Agent Skill References Pattern:
  - **Decision 1**: lean-agent shape (≤150 lines AI tier cap).
  - **Decision 2**: zero MAESTRO references on agent files and companion catalogs.
  - **Decision 3**: additive-only edit discipline on shared references — existing prose remains byte-identical pre/post edit.
- **ADR-027** Taxonomy Crosswalk Schema — F-3 cites OWASP ASI07, CWE-287, CWE-345, AML.T0060, LLM03 from F-A1 catalogs.
- **ADR-028** Source Attribution Schema Extension — F-3 extends an **existing** populator (`tool-abuse` already populates `source_attribution` on AG-{N} findings).
- **ADR-030** Output Integrity Agent — Decision 1 established the three-signal-class taxonomy in the LLM tier; F-3 cross-references this as the precedent for signal-class consolidation logic, applied here within the AG tier.
- **ADR-031** Misinformation Agent — F-3 cross-references **as the asymmetry** (F-1 and F-2 invoked the regex-alternation minor-bump rule; F-3 does NOT — Heuristic A consolidation reuses the existing host's ID space).

### Public-ADR governance constraint

ADR-032 omits commercial framing per Option C governance contract (SDR-001). All BLP-01 strategy cross-references live in private companion docs only. The public ADR stands on technical merits.

### Catalog state at PRD time (verified 2026-04-25)

| Taxonomy | ID | Catalog Path | Status |
|----------|-----|--------------|--------|
| OWASP | ASI07 | `schemas/taxonomy/owasp.yaml:308` | Present |
| OWASP | LLM03 | `schemas/taxonomy/owasp.yaml` | Present |
| MITRE ATLAS | AML.T0060 (Agent-in-the-Middle) | `schemas/taxonomy/mitre-atlas.yaml` | Present |
| CWE | CWE-287 (Improper Authentication) | `schemas/taxonomy/cwe.yaml` | Present |
| CWE | CWE-345 (Insufficient Verification of Data Authenticity) | `schemas/taxonomy/cwe.yaml` | Present |

All 5 citations are catalog-resolvable; F-A2 referential-integrity validator passes by construction on every Category-9/10 finding.

### tool-abuse dispatch registration state (PRD-time grep-verified)

`tool-abuse` is registered across multiple callsites in `dispatch-rules.md` and `orchestrator.md` — F-3 does not touch the dispatch path. The architect identified one optional cosmetic annotation update (`tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`) which is **documentation-only, no functional dispatch change** — adjudicated at plan time per PRD Q2 (architect leaning YES).

## Industry Research

### OWASP ASI07:2026 — Insecure Inter-Agent Communication

The OWASP Agentic Top 10:2026 entry covers attack surfaces introduced when two or more agents communicate without:
- Mutual authentication (mTLS, mutual JWT, mutual API key)
- Message signing (HMAC, asymmetric signature, envelope integrity)
- Replay protection (nonce, monotonic message counter, replay-window enforcement)
- Trust-chain attestation (per-hop validation, signed-capability handoff)
- Taint propagation (authority labels carried across relays)

Two structurally distinct sub-patterns emerge:
1. **A2A direct communication** — direct RPC, message bus, shared queue between two agents.
2. **MCP-to-MCP trust propagation** — multi-hop chains where Agent → MCP-A → MCP-B propagates without per-hop attestation.

### Best practices F-3 codifies

- **Mutual TLS (mTLS)** as the strongest guarantee for inter-agent peer authentication.
- **HMAC message signing with per-call nonce** for envelope integrity + replay protection.
- **Signed-capability handoff** for MCP-to-MCP chains — MCP-A signs the capability scope it delegates to MCP-B; MCP-B validates the signature before accepting.
- **MCP-trust-chain validator** as a verification component or contract that walks the multi-hop chain end-to-end before invocation.
- **Inter-agent taint labels** for authority propagation across message relays (the relay's outputs carry the upstream sender's authority labels).

### MITRE ATLAS AML.T0060 (Agent-in-the-Middle)

Adjacent technique covering attacker-positioned interception of inter-agent messages — relevant where the architecture exhibits a relay agent without declared taint propagation. Cited in Category 9 `source_attribution` as `relationship: related`.

### CWE-287 Improper Authentication / CWE-345 Insufficient Verification of Data Authenticity

Primary CWE references for the two sub-patterns:
- **CWE-287** — A2A channels without mutual authentication (Category 9).
- **CWE-345** — multi-hop trust chains without signed-capability validation (Category 10).

## Recommendations for Spec

1. **Preserve PRD's three-user-story structure** (US-219-1, US-219-2, US-219-3) with P1 priority on all three — A2A detection, MCP-to-MCP detection, and cohesive Agentic-category rendering are co-equal MVP signals.
2. **Translate PRD's 11 success criteria** to spec SCs with grep-checkable predicates — line counts, byte-identity proofs, catalog-resolvability gates, schema-invariant gates.
3. **Codify the two-part emission gate** — Categories 9 and 10 fire only when (a) AG dispatch trigger keywords match AND (b) inter-agent channel indicators are structurally present. Architectures with one agent or one MCP server emit zero new findings.
4. **Codify the byte-identity invariants** — Categories 1-8 in `detection-patterns.md` byte-identical pre/post edit; existing `## Purpose` prose in `tool-abuse.md` byte-identical pre/post edit; 5 non-multi-agent baselines byte-identical PDFs under `SOURCE_DATE_EPOCH=1700000000`.
5. **Codify the lean-shape envelope** — `tool-abuse.md` post-edit ≤150 lines (PRD-time baseline 98; expected 100-106).
6. **Codify the source-attribution contract** — every Category-9 finding emits ASI07 primary + CWE-287 related + (where applicable) AML.T0060 related; every Category-10 finding emits ASI07 primary + CWE-345 related + (where applicable) LLM03 related.
7. **Document the Heuristic A enrichment-pattern precedent** as the first execution — establishes the precedent for future ASI06/ASI08 enrichments and Tier 2 ML/Mobile bundles.
8. **Defer architect-tractable questions** (Q1, Q2, Q3, Q4) to Assumptions section with documented PM/architect leaning — avoid re-adjudicating what the PRD already resolved (Q1, Q5).
9. **Do NOT lock the example regeneration target in spec** — PRD Q3 leaves `examples/agentic-app/` vs `examples/maestro-reference/` vs new minimal fixture as architect's plan-day decision. Spec carries Assumption stating PM leaning + architect override authority.
10. **Avoid implementation-detail leakage** — the spec describes WHAT (testable predicates: line counts, byte-identity, catalog-resolvability) not HOW (specific edit positions, exact prose, ADR sectioning). Plan stage owns HOW.

## References

- F-2 spec (immediate precedent): `specs/206-misinformation-threat-agent/spec.md` — model spec shape on this.
- F-1 spec: `specs/201-output-integrity-threat-agent/spec.md` — first BLP-01 detection feature spec.
- ADR-030 Decision 1 (signal-class taxonomy in LLM tier): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- ADR-031 Decision 2 (Heuristic A inheritance for misinformation): `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`
- Existing `tool-abuse` agent: `.claude/agents/tachi/tool-abuse.md` (98 lines)
- Existing detection patterns: `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` (163 lines, 8 categories)
- Schema: `schemas/finding.yaml` (v1.7, AG prefix already enumerated, no bump in F-3)
