---
prd:
  number: 219
  topic: asi07-tool-abuse-enrichment
  created: 2026-04-25
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-25, status: APPROVED, notes: "PRD grounded in BLP-01 §7 F-3 spec and Issue #219; 3 user stories preserved with job-story restructuring; 11 success criteria covering DoD bullets; HIGH-1 retrospective slotting + HIGH-2 PR title contract addressed inline; Q1 + Q5 resolved at PRD time; Pattern Category Disambiguation paragraph added to FR-2 (M2 fix); SC-10 wording softened to accommodate Q2 annotation-only edit (architect LOW-2 fix). Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-25, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 2 MEDIUM / 2 LOW. Heuristic A enrichment correctly chosen for ASI07 — signal-class identity with existing tool-abuse coverage. All PRD-time invariants independently verified (schema v1.7, 7 dispatch callsites, 5 catalog citations including ASI07/CWE-287/CWE-345/AML.T0060/LLM03, ADR-032 numbering, zero MAESTRO refs). Pattern Categories 9+10 indicators carve surface correctly. MEDIUM-1 Q1 single-category resolution: addressed inline. MEDIUM-2 Category 6 vs 10 non-overlap: addressed via Pattern Category Disambiguation subsection in FR-2. LOW-1 CWE-300 consideration + LOW-2 brittle line numbers: deferred to architect plan-day adjudication. ADR-032 6-decision scope appropriately public. Q1/Q2/Q3/Q4 architect-tractable at plan time. Full review: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-25, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. Calendar verified (cal 4 2026 confirms 04-25 Sat / 04-27 Mon / 04-28 Tue / 04-29 Wed / 04-30 Thu). All 7 PRD on-disk claims verified (98-line tool-abuse, 163-line detection-patterns, schema v1.7, 7 dispatch callsites, ADR-032 next-available). F-3 surface 5/5 dimensions smaller than F-2 — 1-day envelope realistic with 2-day buffer. HIGH-1 retrospective slotting: addressed via Buffer Day 1 retrospective slot + DoD bullet 12. HIGH-2 PR title contract: addressed via Release Discipline subsection + R6 risk. MEDIUM-4 Q5: resolved inline (Tue 2026-04-28). MEDIUM-1 effort-S asymmetry: deferred to architect plan-day AC-to-test mapping. Ready for /aod.plan. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 219
  story_id: null
---

# F-3 — ASI07 Insecure Inter-Agent Communication: Product Requirements Document

**Status**: Approved
**Created**: 2026-04-25
**Spec**: TBD (will land at `specs/219-asi07-tool-abuse-enrichment/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 1 — third Tier 1 feature (parallel-eligible with F-4 and F-5; follows F-1 + F-2)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner

Enrich the existing `tool-abuse` AI-tier threat agent with two new pattern categories — **Insecure Inter-Agent Communication (A2A)** and **MCP-to-MCP Trust Propagation** — closing the OWASP ASI07:2026 detection gap via Heuristic A consolidation into the existing tool-dispatch signal class. **No new agent**, **no schema bump**, **no consumers-list edit** — F-3 is the leanest BLP-01 Tier 1 feature on the wire because the host agent is already correctly registered.

### Problem Statement

Tachi ships 13 detection agents post-F-2 (12 original + `output-integrity` from F-1 + `misinformation` from F-2). The agentic threat tier is covered by two agents: `agent-autonomy` (ASI-01 unchecked autonomy) and `tool-abuse` (ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025). Together they cover 5 of the 10 OWASP Agentic Top 10:2026 entries. Among the remaining 5, **ASI07 Insecure Inter-Agent Communication** is a Tier 1 priority — it captures the attack surface introduced when two or more agents communicate (A2A direct RPC, message bus, shared queue, MCP-to-MCP bridge) without mutual authentication, message signing, replay protection, or trust-chain attestation.

A security analyst threat-modeling a multi-agent application today (e.g., the canonical MAESTRO CDSS reference, `examples/agentic-app/`, or any orchestrator + worker-agent topology) gets **no signal from tachi** that the inter-agent channel itself is an attack surface. Tachi flags single-agent tool dispatch (Categories 1–4), MCP server poisoning (Categories 5–6), instruction-hijack (Category 7), and MCP-server cross-tool exfiltration (Category 8) — but the **bridge** between two agents and the **multi-hop trust chain** between two MCP servers are silently uncovered. Per the BLP-01 Coverage Matrix audit, ASI07:2026 is **Planned (Gap)** today.

Per **Heuristic A (signal-class taxonomy)** in `GUIDE-threat-coverage-research §11`, ASI07 is **same signal class as tool dispatch** — message flow between agent-or-tool endpoints. The detection signal is structurally identical to the surface that `tool-abuse` already covers: a process invokes another endpoint and the channel between them carries security-relevant assumptions. The Heuristic A worked example for ASI07 explicitly recommended **enrichment of `tool-abuse`** rather than authoring a new agent, on the rationale that splitting message-flow detection across two agents would fragment findings without distinguishing the signal class. SDR-001 Decision 4 locked this resolution **without contingency** — F-3 is the operationalization of that decision.

### Proposed Solution

Apply **ADR-023 Decision 3 (additive-only edit discipline)** to enrich the existing `tool-abuse` agent and its companion `detection-patterns.md` with two new Pattern Categories. Net change is **purely additive** to two existing files plus one new ADR — no new agent file, no new skill directory, no schema bump, no orchestrator dispatch table edits, no `finding-format-shared.md` consumers list edit.

1. **`.claude/agents/tachi/tool-abuse.md`** — two-line additive edits:
   - `owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025]` → append `ASI-07` (verified at PRD time: `tool-abuse.md:17`).
   - `## Purpose` paragraph extended with 1-3 lines naming the A2A / MCP-to-MCP surface alongside the existing tool-dispatch surface. Existing prose is byte-identical; new lines append.
   - Detection Workflow Step 5 `references` exemplar list (currently `ASI-02, ASI-04, MCP-03, MCP-05, OWASP LLM06:2025, MITRE ATLAS AML.T0058/T0061/T0062, CWE-77, CWE-89`) extended with `ASI-07` and `MITRE ATLAS AML.T0060` and `CWE-287` and `CWE-345`.
   - Agent file line count remains ≤150 (PRD-time baseline: 98 lines; budget for additions: ≤52 lines, expected delta: ≤8 lines).

2. **`.claude/skills/tachi-tool-abuse/references/detection-patterns.md`** — append two new Pattern Category sections after existing Category 8 (file currently ends at line 163; Categories 1–8 byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category 9: Insecure Inter-Agent Communication (A2A)** — covers A2A channels (direct RPC, message bus, shared queue, MCP-to-MCP bridge) without mutual authentication, message signing, replay protection, or agent-in-the-middle taint propagation. Indicators ≥4. Primary sources: OWASP ASI07:2026 (primary), CWE-287 (related), MITRE ATLAS AML.T0060 (related). Worked example: orchestrator dispatches to worker-agent over plain HTTP without mTLS or message signing. Mitigations: mutual TLS, inter-agent message signing, nonce-based replay prevention, per-hop attestation, inter-agent taint labels.
   - **Pattern Category 10: MCP-to-MCP Trust Propagation** — covers multi-hop MCP trust chains where Agent → MCP-A → MCP-B propagates without cross-trust attestation, signed-capability handoff, or per-hop authentication. Indicators ≥4. Primary sources: OWASP ASI07:2026 (primary), OWASP LLM03:2025 (supply-chain, related), CWE-345 (related). Worked example: agent dispatches to remote MCP-A which transparently relays to MCP-B without validating MCP-A's authority over MCP-B. Mitigations: per-hop MCP attestation, signed-capability handoff, MCP-trust-chain validator, taint propagation across MCP hops.
   - Primary Sources list (currently at line 154) extended with `OWASP ASI07:2026 — Insecure Inter-Agent Communication` and `MITRE ATLAS AML.T0060 — Agent-in-the-Middle` (both catalog-resolvable per PRD-time verification of `schemas/taxonomy/owasp.yaml:308` and `schemas/taxonomy/mitre-atlas.yaml`).

3. **`docs/architecture/02_ADRs/ADR-NNN-asi07-tool-abuse-enrichment.md`** — public per-feature ADR documenting (a) the Heuristic A consolidation into `tool-abuse`, (b) the explicit non-creation of a new agent and the rationale (signal-class distinctness from misinformation/output-integrity but signal-class identity with existing tool-abuse coverage), (c) the additive-only edit discipline per ADR-023 Decision 3, (d) zero-MAESTRO-reference invariant proof on the enriched files, (e) the cross-reference back to SDR-001 Decision 4. Authored under the Proposed → Accepted dual-commit pattern that ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 established as the BLP-01 default protocol. ADR number assigned at plan time (next available is ADR-032).

4. **Example regeneration** on a multi-agent example architecture — the canonical candidate is `examples/agentic-app/` (regenerated by F-1 already; multi-agent topology with inter-agent channels exists per Feature 142 `Inter-agent Communication Channel` component type). At least one new `AG-{N}` finding produced citing OWASP ASI07:2026, demonstrating Pattern Category 9 OR 10 firing on the canonical example. The 5 non-multi-agent baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant — those baselines do not exhibit multi-agent inter-agent channels, so no new findings emit, so threat artifacts are unchanged).

The enriched agent activates **as it does today** when any DFD `Process` element matches existing tool-abuse trigger keywords (orchestrator, MCP server, tool server, plugin, agent). The new Pattern Categories 9 and 10 fire when the architecture additionally exhibits **inter-agent channel indicators** (e.g., two or more agent Process components connected by a communication channel; declared MCP-to-MCP relay; agent acts as message router between other agents). When no inter-agent channel is present, Categories 9 and 10 emit **zero findings** — the existing emission-gate discipline of `tool-abuse` is preserved.

**Three things the solution is deliberately NOT:**

1. It is **not** a new agent. ASI07's signal class — message flow between agent-or-tool endpoints — is structurally identical to the surface `tool-abuse` already covers. Splitting it into a hypothetical `inter-agent-communication` agent would fragment the agentic-category section of `threats.md` without semantic gain. Per Heuristic A, the consolidation rule applies. SDR-001 Decision 4 locked this without contingency — F-3 cannot ship as a new agent without re-opening that decision, which would force re-adjudication of every prior Heuristic A consolidation (LLM05 → output-integrity, LLM09 → misinformation) on the same grounds.
2. It is **not** a new finding ID prefix. Findings emit `category: agentic` (existing enum value) with sequential `AG-{N}` IDs (existing prefix; verified present in `schemas/finding.yaml` regex post-F-2 `id.pattern`). **No schema bump** — `finding.yaml` stays at v1.7. This is the first BLP-01 detection feature that does not require a schema version increment, because the Heuristic A consolidation pattern reuses the existing host-agent's ID space.
3. It is **not** an orchestrator-dispatch change. `tool-abuse` is already registered across 7 callsites in `dispatch-rules.md` and `orchestrator.md` (PRD-time grep-verified). The existing AG dispatch path invokes `tool-abuse` for every multi-agent component without modification. No `finding-format-shared.md` `consumers:` list edit is needed — `tool-abuse` is already in the consumers list. **F-3 is the first BLP-01 detection feature with zero functional orchestrator-tier touches** — the leanest delivery surface in the initiative. (A one-token cosmetic annotation update to `dispatch-rules.md` extending `tool-abuse (MCP-03)` to `tool-abuse (MCP-03, ASI-07)` is permitted per Q2 architect adjudication at plan time — documentation-only, no functional dispatch change.)

### Success Criteria

- **SC-1** — `.claude/agents/tachi/tool-abuse.md` `owasp_references` list extended to include `ASI-07`; existing entries (`ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025`) preserved byte-identically (grep-checkable). Agent file line count remains **≤150 lines** (AI tier cap per ADR-023). PRD-time baseline: 98 lines; expected post-edit count: 100–106 lines.
- **SC-2** — `.claude/agents/tachi/tool-abuse.md` `## Purpose` section gains a 1-3 line extension naming the A2A / MCP-to-MCP surface alongside the existing tool-dispatch coverage. The pre-existing prose paragraphs remain byte-identical (the edit is additive, not a rewrite).
- **SC-3** — `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` gains **Pattern Category 9 "Insecure Inter-Agent Communication (A2A)"** and **Pattern Category 10 "MCP-to-MCP Trust Propagation"** appended after existing Category 8. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one primary-source citation (`OWASP ASI07:2026` minimum), (d) named mitigations. Pre-existing Categories 1–8 and `## Overview` / `## Targeted DFD Element Types` / `## Trigger Keywords` sections remain **byte-identical** pre/post edit per ADR-023 Decision 3.
- **SC-4** — Primary Sources list (line 154 baseline) extended with `OWASP ASI07:2026 — Insecure Inter-Agent Communication` and `MITRE ATLAS AML.T0060 — Agent-in-the-Middle`. Existing Primary Sources entries preserved byte-identically.
- **SC-5** — Public per-feature **ADR-NNN** (ADR-032 expected) committed under `docs/architecture/02_ADRs/` documenting (a) the Heuristic A consolidation rationale, (b) the additive-only edit discipline conformance, (c) the explicit non-creation of a new agent, (d) zero-MAESTRO-reference invariant proof, (e) cross-reference to SDR-001 Decision 4 in the private companion ADR/SDR set without leaking strategic content into the public ADR. Authored under the Proposed → Accepted dual-commit pattern.
- **SC-6** — Agent invocation on a multi-agent example architecture produces **at least 1 new `AG-{N}` finding** attributable to Pattern Category 9 OR 10. The canonical example target is `examples/agentic-app/` (extended in Feature 142 with `Inter-agent Communication Channel` component type). Architect adjudicates the final example target at plan time.
- **SC-7** — All **5 non-multi-agent example PDFs** regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The 5 baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`. Zero-impact-when-absent invariant: those baselines do not exhibit multi-agent inter-agent channels, so Categories 9 and 10 emit zero findings, so all downstream artifacts (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic specs, PDF) are unchanged. **The 6th baseline (`agentic-app`)** is the expected mutation candidate per SC-6.
- **SC-8** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared.
- **SC-9** — **Schema invariant preserved** — `schemas/finding.yaml` `schema_version` remains **`"1.7"`** (PRD-time verified post-F-2). `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$` — no new prefix; `AG` already enumerated. **F-3 is the first BLP-01 detection feature with no schema bump.**
- **SC-10** — **24-file zero-edit invariant preserved on every detection-tier file other than the host agent + companion** (extended count post-F-1 + F-2: 26 detection files). F-3's edits are scoped to the **2 host-agent files** (`tool-abuse.md` + `detection-patterns.md`) — every other detection-tier file (12 other agent files + 12 other companion `detection-patterns.md` files + new `output-integrity.md` + new `misinformation.md` + their two companions = 24 files) remains byte-identical. **No `finding-format-shared.md` consumers list edit is needed** — `tool-abuse` is verified present in the consumers list (PRD-time grep-verified at `.claude/skills/tachi-shared/references/finding-format-shared.md`). **No functional orchestrator/dispatch-rules edit is needed** — `tool-abuse` is fully registered (PRD-time verified across 7 callsites in `dispatch-rules.md` and `orchestrator.md`). **Annotation carve-out**: a cosmetic one-token annotation update to `dispatch-rules.md` line ~92 (extending `tool-abuse (MCP-03)` to `tool-abuse (MCP-03, ASI-07)`) is permitted contingent on architect adjudication of Q2 at plan time — this is documentation-only, no functional dispatch change, and does not invalidate the zero-functional-touch claim. F-3 is structurally the smallest BLP-01 detection delivery to date.
- **SC-11** — **Source attribution** populated on every emitted Category-9/10 `AG-{N}` finding using the F-A2 `source_attribution` schema field. Each Category-9 finding cites: `{taxonomy: owasp, id: ASI07, relationship: primary}`, `{taxonomy: cwe, id: CWE-287, relationship: related}` (Improper Authentication — primary CWE for unauthenticated A2A channels; verified present in `schemas/taxonomy/cwe.yaml`), and where applicable `{taxonomy: atlas, id: AML.T0060, relationship: related}` (Agent-in-the-Middle; verified present in `schemas/taxonomy/mitre-atlas.yaml`). Each Category-10 finding cites: `{taxonomy: owasp, id: ASI07, relationship: primary}`, `{taxonomy: cwe, id: CWE-345, relationship: related}` (Insufficient Verification of Data Authenticity — primary CWE for trust-chain validation gaps; verified present), and `{taxonomy: owasp, id: LLM03, relationship: related}` for the supply-chain-trust adjacency (verified present in `schemas/taxonomy/owasp.yaml`). **F-3 is the third net-new producer of `source_attribution`** (after F-1 OI-{N} and F-2 MI-{N}); the existing `tool-abuse` AG-{N} findings already populate `source_attribution` from prior wiring, so F-3 extends an existing populator rather than adding a new one — the **referential-integrity contract is now proven across two agent classes (LLM new + AG enrichment)** in addition to the two-agent-new validation from F-1 + F-2.

### Timeline

Target window: **2026-04-28 (Tuesday) → 2026-04-29 (Wednesday)** with a **2026-04-30 (Thursday) buffer**. Calendar verified at PRD time (`cal 4 2026`): 2026-04-25 = Saturday (today), 2026-04-27 = Monday, 2026-04-28 = Tuesday, 2026-04-29 = Wednesday, 2026-04-30 = Thursday. F-3 starts Tuesday because Monday is conventionally reserved for PRD-day work (this PRD ships Saturday) and to allow plan-day Monday prior to build-day Tuesday.

**Single-envelope sizing** — F-3 is **simpler than F-2** because:
- No new agent file (only an additive edit to existing).
- No new skill directory (only an additive edit to existing companion).
- No schema bump (no new ID prefix).
- No `finding-format-shared.md` edit (`tool-abuse` already in consumers list).
- No orchestrator/dispatch-rules edit (`tool-abuse` already fully registered).
- Two new Pattern Categories vs. F-2's five (smaller pattern-authoring surface).
- Heuristic A consolidation is locked in SDR-001 Decision 4 (no scope adjudication at build time).

- **Realistic envelope**: **1 working day**, 0.5 days aspirational. 2 pattern categories appended; 1-3 line `## Purpose` extension; metadata one-liner edit. ADR-032 Proposed → Accepted dual-commit. Delivery 2026-04-28.
- **Buffer**: 2026-04-29 Wednesday reserved for regeneration friction and ADR Accepted transition. 2026-04-30 Thursday is a second buffer day reserved for F-3 + F-4 + F-5 multi-feature concurrency hedge (see Risks below).

Day 1 AM: senior-backend-engineer applies the additive edits to `tool-abuse.md` + `detection-patterns.md` and authors ADR-032 Proposed commit. Day 1 PM: regenerate `examples/agentic-app/`, byte-identity verification on 5 non-multi-agent baselines, ADR-032 Accepted transition.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's vision — automated threat modeling extending STRIDE with AI-specific threat agents for agentic applications — implies *complete* coverage of the agentic threat surface, not just the agent-itself surface. F-1 / F-2 closed the LLM-output factual and sanitization surfaces; F-3 closes the **inter-agent channel** surface — a structurally distinct attack surface that emerges only when an architecture contains 2+ agents communicating. An adopter evaluating "does tachi cover the *multi-agent* threat surface?" today must answer "no, inter-agent channels are silently uncovered"; post-F-3 the answer is "yes — single-agent tool dispatch, MCP server poisoning, and inter-agent communication are all modeled, with findings rendered cohesively in the same Agentic-category section."

The value proposition is especially strong for adopters running **multi-agent orchestrator + worker-agent topologies** or **multi-MCP fleets** (clinical decision support with multiple specialized agents, agentic RAG with retrieval + synthesis + verification agents, MCP-bridged agent ecosystems). Post-F-3 those adopters get architecture-context-aware findings on the channel itself, not just the endpoints.

### BLP-01 Initiative Fit

**Reference**: `BLP-01 threat coverage` — F-3 is the **third Tier 1 feature** in the BLP-01 initiative (F-1 shipped 2026-04-19 as Feature 201; F-2 shipped 2026-04-24 as Feature 206). F-3 is parallel-eligible with F-4 (ASI09 Human-Agent Trust Exploitation) and F-5 (LLM10 Unbounded Consumption); F-4 was unblocked by ADR-030 Outcome B at F-1 close.

F-3's place in the BLP-01 chain:

```
F-A1 (Feature 180, delivered 2026-04-17) — taxonomy catalogs + crosswalk
  │
F-A2 (Feature 189, delivered 2026-04-17) — source_attribution schema contract
  │
F-B  (Feature 194, delivered 2026-04-18) — coverage attestation PDF section
  │
F-1 (Feature 201, delivered 2026-04-19) — output-integrity agent (LLM05)
  │
F-2 (Feature 206, delivered 2026-04-24) — misinformation agent (LLM09)
  │
F-3 (this PRD, #219) ◄────── THIRD TIER 1 FEATURE (parallel-eligible with F-4, F-5)
  │  Enrichment of tool-abuse with ASI07 — Heuristic A consolidation; no new agent
  │
F-4 (ASI09 Human-Agent Trust Exploitation, parallel-eligible)
F-5 (LLM10 Unbounded Consumption, parallel-eligible)
  │
F-6, F-7 (Tier 2 ML + Mobile bundles)
F-8 (Tier 3 Web/API attestation; ships last)
```

**F-3 does NOT gate any other feature.** Its delivery closes ASI07 on the Coverage Matrix and demonstrates the **Heuristic A enrichment pattern** — net-new validation that the consolidation rule produces a working, leaner delivery (vs. the new-agent pattern proven in F-1 + F-2). The pattern becomes available for future Heuristic A consolidations beyond BLP-01 Tier 1.

**F-3 is the first feature to validate Heuristic A consolidation in production.** SDR-001 Decision 4 specified the rule but no prior feature operationalized it (F-1 considered subsumption of LLM05 into existing agents and chose new-agent under Outcome A; F-2 was a clear new-agent decision). F-3 is the first execution of the **enrichment branch** of Heuristic A — the precedent set here governs every future Heuristic A consolidation.

### Recent ADR Lineage

- **ADR-023** (Threat Agent Skill References Pattern, Accepted 2026-04-11): Decision 3 (additive-only shared-reference edits) is the operational pattern for both file edits in F-3. Decision 2 (zero MAESTRO references) preserved on the enriched files. SC-1 + SC-3 + SC-10 trace to this ADR.
- **ADR-021** (SOURCE_DATE_EPOCH determinism, Accepted earlier): SC-7 byte-identity gate on the 5 non-multi-agent baselines uses this harness.
- **ADR-027** (Taxonomy Crosswalk Schema, Accepted 2026-04-17): F-3 cites OWASP ASI07 from `schemas/taxonomy/owasp.yaml` (verified at PRD time). The 5-value taxonomy enum is the source of `taxonomy: owasp` in F-3's `source_attribution` records.
- **ADR-028** (Source Attribution Schema Extension, Accepted 2026-04-17): SC-11 is direct consumption of this contract — Category-9/10 findings emit `source_attribution: [{taxonomy: owasp, id: ASI07, relationship: primary}, {taxonomy: cwe, id: CWE-287/345, relationship: related}, ...]`.
- **ADR-029** (Coverage Attestation Report Section, Accepted 2026-04-18): F-3's findings will surface in F-B's per-finding attribution table and per-framework coverage matrix when `examples/agentic-app/` is included in a security-report PDF run.
- **ADR-030** (Output Integrity Agent, Accepted 2026-04-19): F-3's ADR-032 cross-references ADR-030's Heuristic A signal-class analysis — ADR-030 Decision 1 established the three-signal-class taxonomy (input / output-sanitization / factual-integrity) within the LLM tier; F-3 demonstrates the **enrichment branch** of Heuristic A within the AG tier, which is a different application of the same rule.
- **ADR-031** (Misinformation Agent, Accepted 2026-04-24): F-3's ADR-032 cross-references ADR-031's regex-alternation minor-bump rule (ADR-030 Decision 8 extension). F-3's distinguishing technical fact: **F-3 does not invoke the rule** — no regex bump, no schema increment. The cross-reference is to document the asymmetry: F-1 and F-2 needed it; F-3 does not, because Heuristic A consolidation reuses the existing host-agent's ID space.
- **Feature 201/206 precedent** (F-1 + F-2 — first two net-new agents authored under ADR-023 from authoring): F-3 mirrors the **dispatch-registration validation** but inverts the **edit pattern** — the first two BLP-01 features added agents; F-3 enriches one. The **two-execution-deep validation** of the lean-agent shape (per F-2 retrospective) becomes the **structural-compatibility validation** for enrichment when the host agent is already lean+skill-references compliant.

### Roadmap Fit

- **Phase**: BLP-01 Tier 1 (AI/Agentic gaps, depth + breadth)
- **Week**: Week of 2026-04-27 — immediate follow-on to Feature 206 (F-2) delivery
- **Dependencies**:
  - F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17 (verified: OWASP ASI07 entry present at `schemas/taxonomy/owasp.yaml:308`; CWE-287 + CWE-345 present in `schemas/taxonomy/cwe.yaml`; AML.T0060 present in `schemas/taxonomy/mitre-atlas.yaml`)
  - F-A2 (Feature 189) — **SATISFIED** as of 2026-04-17 (verified: `schemas/finding.yaml` v1.7 carries `source_attribution`; existing `tool-abuse` findings already populate the field)
  - F-B (Feature 194) — **SATISFIED** as of 2026-04-18 (verified: `templates/tachi/security-report/coverage-attestation.typ` exists; `has-source-attribution` boolean wired)
  - F-1 (Feature 201) — **SATISFIED** as of 2026-04-19 (no architectural dependency; informational precedent only)
  - F-2 (Feature 206) — **SATISFIED** as of 2026-04-24 (no architectural dependency; informational precedent only — F-3 is parallel-eligible with F-2 per BLP-01 §7 dependency declaration but ships sequentially in practice for build-cadence reasons)

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Security Analyst Modeling a Multi-Agent Architecture**

- **Role**: Application security engineer or external consultant performing threat modeling on a multi-agent system (orchestrator + worker agents, agentic RAG with retrieval + synthesis + verification agents, MCP-bridged agent ecosystems, clinical decision support with multiple specialized agents)
- **Goal**: Surface the inter-agent channel threat surface — A2A unauthenticated peer connections, message tampering between agents, replay attacks, agent-in-the-middle relay, MCP-to-MCP cross-trust violations — with concrete mitigations rooted in OWASP ASI07:2026 vocabulary
- **Pain Point Today**: Tachi reports findings on **agents themselves** (tool-abuse on each agent's tool dispatch, agent-autonomy on each agent's privilege boundary) and on **MCP server endpoints** (Categories 5–8). The **bridge between agents** and the **multi-hop trust chain** are silently uncovered. The analyst must hand-author the inter-agent threat model, citing OWASP ASI07:2026 manually, with no architectural-context-aware finding generation. In multi-agent or multi-MCP architectures this gap is significant — the channel surface area scales quadratically with agent count.
- **Value Delivered**: Per-channel `AG-{N}` findings (Pattern Category 9 or 10) with named mitigations (mutual TLS, inter-agent message signing, nonce-based replay prevention, per-hop MCP attestation, signed-capability handoff, MCP-trust-chain validator, inter-agent taint labels) emitted automatically when the architecture exhibits multi-agent or multi-MCP inter-channel topology. Coverage Matrix shows ASI07:2026 as Covered.

### Secondary Persona: **Developer Building a Multi-Agent Orchestrator**

- **Role**: Backend or full-stack developer wiring an orchestrator agent that dispatches to worker agents, or building an agentic RAG pipeline with multiple specialized agents
- **Goal**: Address tachi findings without researching the inter-agent communication mitigation pattern library from primary OWASP / CWE / ATLAS sources
- **Pain Point Today**: Generic advice ("authenticate inter-agent calls") doesn't translate to a concrete architectural change. Developers want named mechanisms: "mutual TLS on the worker-agent invocation channel", "HMAC message signing with per-call nonce", "MCP-attestation handshake before relay", "agent-in-the-middle taint propagation flag".
- **Value Delivered**: Each Category-9/10 finding's `mitigation` field names specific inter-agent / MCP-trust mechanisms matched to the detected pattern category. Category 9 (A2A) findings name mTLS, message signing, replay protection, taint propagation. Category 10 (MCP-to-MCP) findings name per-hop attestation, signed-capability handoff, trust-chain validator, supply-chain controls.

### Tertiary Persona: **Adopter of the Canonical MAESTRO CDSS Reference**

- **Role**: Tachi adopter who runs the canonical MAESTRO Clinical Decision Support System reference (or `examples/agentic-app/` extended with multi-agent topology per Feature 142) as a teaching example or compliance template
- **Goal**: See the canonical reference produce findings that span the full agentic threat surface (single-agent + inter-agent), demonstrating that tachi's coverage is structurally complete
- **Pain Point Today**: The MAESTRO reference architecture introduced an `Inter-agent Communication Channel` component type in Feature 142, but no detection agent currently fires on that channel — the architecture renders the channel and tachi remains silent on its security implications. The pedagogical asymmetry undermines the reference's role as a complete-coverage teaching example.
- **Value Delivered**: Post-F-3 the canonical reference architecture produces `AG-{N}` findings on every inter-agent channel that lacks declared authentication, signing, or replay protection. The Agentic-category section of `threats.md` and `threat-report.md` shows tool-dispatch findings AND inter-agent findings in the same section, demonstrating Heuristic A consolidation as a working pattern.

### Quaternary Persona: **Tachi Maintainer Validating the Heuristic A Enrichment Pattern**

- **Role**: Maintainer evaluating whether Heuristic A consolidation produces a maintainable delivery pattern (vs. the new-agent pattern validated by F-1 + F-2)
- **Goal**: Ship the first execution of Heuristic A enrichment branch and confirm that (a) the additive-only edit discipline holds across two file types simultaneously (agent metadata + companion pattern catalog), (b) the byte-identity invariant on Categories 1–8 is grep-checkable, (c) the agent-line-count cap (≤150) is preserved with margin, (d) the enrichment does not introduce false positives on the 5 non-multi-agent baselines.
- **Pain Point Today**: SDR-001 Decision 4 specifies Heuristic A enrichment as a delivery pattern but no prior feature has operationalized it. The two-execution-deep validation that F-2 retrospective established for the lean-agent shape applies only to the new-agent pattern; the enrichment pattern is one-execution-deep at most after F-3.
- **Value Delivered**: F-3 establishes the enrichment-pattern precedent — additive-only edits to two files (agent metadata + companion catalog) with byte-identity preservation on existing content, no schema bump, no consumers list edit, no orchestrator touch. Post-F-3 the pattern is available for any future Heuristic A consolidation (e.g., a hypothetical ASI06 enrichment of `agent-autonomy`). F-3's success criteria specifically name the byte-identity grep checks (SC-1, SC-3, SC-4) so the maintainer has a programmatic gate, not just a code-review gate.

---

## 📖 User Stories

All three user stories are preserved from GitHub Issue #219 (which sourced them from BLP-01 §7, F-3). Job-story restructuring applied to align with the F-2 PRD (206) precedent; acceptance criteria preserved where they specify testable predicates.

### US-219-1: Inter-Agent Channel Detection (A2A)

**When** a security analyst threat-models an architecture that includes two or more agent Process components connected by a communication channel (direct RPC, message bus, shared queue, MCP-to-MCP bridge),
**I want** tachi to flag unauthenticated, unsigned, or replay-vulnerable channels with concrete `AG-{N}` findings citing OWASP ASI07:2026,
**So I can** catch inter-agent spoofing, tampering, and replay surfaces before they reach runtime.

**Acceptance Criteria**:

- **Given** an architecture with two or more agent Process components connected by a communication channel with no declared mutual authentication, **when** the orchestrator dispatches `tool-abuse`, **then** an `AG-N` finding emits with `category: agentic`, `references` citing `OWASP ASI07:2026`, and `source_attribution` containing `{taxonomy: owasp, id: ASI07, relationship: primary}` plus `{taxonomy: cwe, id: CWE-287, relationship: related}`.
- **Given** inter-agent messages that are not signed, not timestamped, or not replay-protected, **when** `tool-abuse` runs, **then** distinct `AG-{N}` findings surface the message-integrity gap with named mitigations (HMAC message signing with per-call nonce, timestamp binding, replay-window enforcement).
- **Given** an agent that acts as a message relay between two other agents without declared taint propagation, **when** `tool-abuse` runs, **then** a finding highlights the agent-in-the-middle surface and (where catalog-resolvable) cites `MITRE ATLAS AML.T0060` in `source_attribution`.
- **Given** an architecture with **only one agent** (no inter-agent channel present), **when** `tool-abuse` runs, **then** Pattern Category 9 emits **zero findings** — the existing tool-abuse Categories 1–8 fire as they do today; the new Category 9 is gated on multi-agent topology and does not speculate on hypothetical second agents.

**Priority**: P0
**Effort**: S

### US-219-2: MCP-to-MCP Trust Propagation Detection

**When** a developer operates a multi-MCP agent fleet where Agent → MCP-A → MCP-B forms a trust chain,
**I want** tachi to surface MCP-to-MCP trust-propagation risks distinct from single-agent MCP poisoning,
**So I can** harden the cross-MCP trust boundary with concrete per-hop attestation and signed-capability handoff mechanisms.

**Acceptance Criteria**:

- **Given** an architecture where an agent dispatches to a remote MCP server which in turn dispatches to a secondary MCP server without declared trust-chain attestation, **when** `tool-abuse` runs, **then** an `AG-{N}` finding emits with primary citation `OWASP ASI07:2026` and the related `OWASP LLM03:2025` upstream-trust reasoning surfaced in the threat description (LLM03 inherited from the existing supply-chain vocabulary in Category 6).
- **Given** an `AG-{N}` finding for the MCP-to-MCP trust propagation category, **when** the `mitigation` field is read, **then** it names at least one concrete control: per-hop MCP attestation, signed-capability handoff, MCP-trust-chain validator, supply-chain trust-chain enforcement.
- **Given** any Category-10 finding, **when** its `references` array is inspected, **then** at least one entry is `OWASP ASI07:2026` (primary), and `source_attribution` carries that as `relationship: primary`. CWE-345 (Insufficient Verification of Data Authenticity) is `relationship: related`. LLM03:2025 may be cited as `relationship: related` per the existing Category 6 supply-chain vocabulary.
- **Given** an architecture with **only one MCP server** (no MCP-to-MCP relay), **when** `tool-abuse` runs, **then** Pattern Category 10 emits **zero findings** — single-MCP architectures continue to receive Categories 5–8 findings as they do today.

**Priority**: P0
**Effort**: S

### US-219-3: Cohesive Agentic-Category Rendering

**When** an adopter of a multi-agent canonical example (MAESTRO CDSS reference, `examples/agentic-app/` per Feature 142, or any extended multi-agent topology) runs `/tachi.threat-model`,
**I want** existing tool-abuse findings (Categories 1–8) plus the new ASI07 findings (Categories 9–10) rendered cohesively in the same Agentic-category section,
**So that** the report does not fragment agentic threats across two artificial categories that would emerge if ASI07 were a new agent.

**Acceptance Criteria**:

- **Given** a regenerated example architecture exercising both single-agent tool dispatch AND inter-agent communication channels, **when** the AI-category section of `threat-report.md` is read, **then** all `AG-{N}` findings render in the same `category: agentic` section regardless of which Pattern Category (1–10) produced them. The ID prefix `AG-{N}` is **single-namespace** — sequential numbering across all 10 categories.
- **Given** ADR-NNN (ADR-032) at the time of F-3 merge, **when** its Decision section is read, **then** it explicitly resolves the Heuristic A consolidation rationale: (a) ASI07 signal class is identical to existing tool-abuse coverage (message flow between agent-or-tool endpoints), (b) creating a new agent would fragment the Agentic-category section without semantic gain, (c) the additive-only edit discipline preserves byte-identity on existing categories per ADR-023 Decision 3, (d) cross-references SDR-001 Decision 4 in private companion documentation without leaking strategic content.
- **Given** the BLP-01 Coverage Matrix post-F-3 merge, **when** ASI07:2026 row is inspected, **then** it transitions **Planned → Covered** with F-3 (Feature 219) named as the closure feature.
- **Given** the Coverage Matrix post-F-3 merge, **when** the OWASP Agentic Top 10:2026 framework row is summed, **then** ASI07 joins ASI-01 / ASI-02 / ASI-04 / MCP-03 / MCP-05 as the sixth Agentic Top 10 entry covered (out of 10), with F-4 (ASI09) and post-Tier-1 features tracking the remaining 4.

**Priority**: P0
**Effort**: S (Heuristic A consolidation is locked in SDR-001 Decision 4; ADR-032 records the rationale but does not re-adjudicate)

---

## ⚙️ Functional Requirements

### FR-1 — Additive Metadata Edit to `tool-abuse.md`

- **File**: `.claude/agents/tachi/tool-abuse.md`
- **Edit 1** (one-line append): `owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025]` → `owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]`. Verified at PRD time: `tool-abuse.md:17`.
- **Edit 2** (Detection Workflow Step 5 references list extension): existing list `(ASI-02, ASI-04, MCP-03, MCP-05, OWASP LLM06:2025, MITRE ATLAS AML.T0058/T0061/T0062, CWE-77, CWE-89)` — append `ASI-07`, `MITRE ATLAS AML.T0060`, `CWE-287`, `CWE-345`. Verified at PRD time: `tool-abuse.md:43`.
- **Edit 3** (`## Purpose` extension — additive paragraph or 1-3 sentences appended within the existing `## Purpose` section): name the A2A / MCP-to-MCP surface alongside the existing tool-dispatch surface. Suggested phrasing (architect-finalized at plan time): "This agent additionally covers the **inter-agent channel surface** — A2A communication between agent Process components (direct RPC, message bus, shared queue, MCP-to-MCP bridge) and multi-hop MCP trust chains — per OWASP ASI07:2026. Pattern Categories 9 (Insecure Inter-Agent Communication) and 10 (MCP-to-MCP Trust Propagation) detect channel-level threats distinct from single-agent tool dispatch."
- **Length cap**: agent file MUST remain ≤150 lines (AI tier cap per ADR-023). PRD-time baseline: 98 lines. Expected post-edit: 100–106 lines.
- **MAESTRO references**: **ZERO** (ADR-023 Decision 2 invariant). Grep-checkable.
- **Byte-identity preservation**: every line not directly modified by Edit 1, 2, or 3 remains byte-identical.

### FR-2 — Additive Pattern Categories 9 and 10 in `detection-patterns.md`

- **File**: `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`
- **Edit posture**: append-only after existing `## Pattern Category 8: MCP Server Poisoning and Cross-Tool Exfiltration` (currently ends before line 154 `## Primary Sources`). Categories 1–8 byte-identical pre/post edit per ADR-023 Decision 3.
- **Section shape (mirror Categories 1–8)**: each new Category specifies (a) name with header, (b) primary OWASP/CWE source, (c) **≥4 indicators** (3-6 bullet points), (d) at least one worked example, (e) named mitigations.

#### Pattern Category 9: Insecure Inter-Agent Communication (A2A)

- **Primary**: `OWASP ASI07:2026 — Insecure Inter-Agent Communication`
- **Related**: `CWE-287 Improper Authentication`, `MITRE ATLAS AML.T0060 — Agent-in-the-Middle`
- **Indicators** (≥4, architect may add at plan time):
  - Architecture includes ≥2 agent Process components connected by a communication channel (direct RPC, message bus, shared queue, MCP-to-MCP bridge, named pipe, IPC).
  - The channel does not declare mutual authentication (mTLS, mutual JWT, mutual API key).
  - Inter-agent messages are not signed (no HMAC, no envelope signature, no envelope-level integrity verification).
  - Messages lack timestamp binding or replay-window enforcement (no nonce, no monotonic message counter, no replay-cache lookup).
  - An agent acts as a message relay between two other agents without declared taint propagation (the relay's outputs do not carry the upstream sender's authority labels).
- **Worked example**: An orchestrator agent dispatches workloads to specialized worker agents over plain HTTP without mTLS or message signing. Threat: a network-positioned attacker (or a sibling worker on the same compute) intercepts and tampers with the orchestrator's instructions; receiving worker has no authentic-source signal and executes the modified instruction.
- **Mitigations**:
  - Mutual TLS (mTLS) on every inter-agent channel.
  - Inter-agent message signing (HMAC or asymmetric signature) with envelope integrity verification.
  - Nonce-based replay prevention with replay-window enforcement.
  - Inter-agent taint labels (authority propagation across relays).
  - Per-channel mutual authentication (mutual JWT, mutual API key) where mTLS is infeasible.

#### Pattern Category 10: MCP-to-MCP Trust Propagation

- **Primary**: `OWASP ASI07:2026 — Insecure Inter-Agent Communication`
- **Related**: `CWE-345 Insufficient Verification of Data Authenticity`, `OWASP LLM03:2025 — Supply Chain` (inherited from existing Category 6 supply-chain vocabulary)
- **Indicators** (≥4, architect may add at plan time):
  - Architecture declares an agent that dispatches to a remote MCP server which in turn dispatches to a secondary MCP server (or to additional remote MCP servers) — i.e., a multi-hop MCP trust chain.
  - The handoff between MCP-A and MCP-B does not declare per-hop attestation (no signed capability descriptor, no per-hop authentication, no MCP-server identity validation at each hop).
  - The agent's authority assumptions over MCP-A do not transitively constrain MCP-B (MCP-A can transparently relay to any downstream MCP without honoring the agent's original capability scope).
  - The architecture does not declare a trust-chain validator (a component or contract that verifies the integrity of the multi-hop chain before invocation).
  - Cross-MCP supply-chain assumptions are not declared (the agent treats MCP-B's outputs as authoritative without inheriting MCP-A's trust inheritance).
- **Worked example**: An agent dispatches to a remote MCP-A server which transparently relays the request to a secondary MCP-B server without validating MCP-A's authority over MCP-B. Threat: a compromised or rogue MCP-A injects responses purporting to come from MCP-B; the agent has no per-hop attestation and accepts the response as authoritative.
- **Mitigations**:
  - Per-hop MCP attestation (signed capability descriptor, per-hop authentication).
  - Signed-capability handoff (MCP-A signs the capability scope it delegates to MCP-B; MCP-B validates the signature before accepting the delegation).
  - MCP-trust-chain validator (a verification component or contract that walks the multi-hop chain end-to-end before invocation).
  - Supply-chain trust-chain enforcement (cross-reference with existing Category 6 supply-chain controls — versioned MCP server registry, signed package distribution, dependency-graph attestation).
  - Taint propagation across MCP hops (MCP-A's taint labels propagate to MCP-B's outputs).

#### Pattern Category Disambiguation: Category 6 (LLM03 Supply Chain) vs. Category 10 (MCP-to-MCP Trust Propagation)

Category 10 cites OWASP LLM03:2025 as `relationship: related` per the existing Category 6 supply-chain vocabulary. This creates a **non-overlapping by design** carve that ADR-032 will formalize:

- **Category 6** fires on **upstream ingestion** of plugins / tools / MCP servers (sourcing, registration, manifest pinning, signed package distribution at registry time).
- **Category 10** fires on **runtime trust propagation** between already-registered MCP servers (per-hop attestation, signed-capability handoff, transitive authority validation at invocation time).

The same architecture may legitimately surface BOTH findings — e.g., if MCP-A is unsigned at registration (Category 6) AND MCP-A relays to MCP-B without per-hop attestation (Category 10), both are valid findings describing distinct architectural gaps. They are not duplicates and should not be merged in the threat-report's Agentic-category section. Architect to formalize this carve in ADR-032 (likely as Decision 7 — Pattern Category Disambiguation).

### FR-3 — Primary Sources List Extension in `detection-patterns.md`

- **File**: `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`
- **Edit**: extend the `## Primary Sources` list (currently at line 154) with two additive entries:
  - `OWASP ASI07:2026 — Insecure Inter-Agent Communication` (catalog-resolvable per `schemas/taxonomy/owasp.yaml:308`)
  - `MITRE ATLAS AML.T0060 — Agent-in-the-Middle` (catalog-resolvable per `schemas/taxonomy/mitre-atlas.yaml`; verified at PRD time)
- **Existing entries preserved byte-identically**: `OWASP ASI-02 / ASI-04 / MCP-03 / MCP-05 / LLM06:2025`, `MITRE ATLAS AML.T0058/T0061/T0062`, `CWE-77`, `CWE-89`, etc.

### FR-4 — Public Per-Feature ADR (ADR-032 expected)

- **File**: `docs/architecture/02_ADRs/ADR-NNN-asi07-tool-abuse-enrichment.md` (NNN expected to be 032; team-lead confirms numbering at plan time per established convention)
- **Authoring pattern**: dual-commit Proposed → Accepted per ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 precedent.
- **Decision content** (architect-owned at plan time):
  - **Decision 1**: Adopt Heuristic A enrichment (vs. new agent) for ASI07. Rationale: signal-class identity with existing tool-abuse coverage; creating a new agent would fragment the Agentic-category section without semantic gain.
  - **Decision 2**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing Categories 1–8 byte-identical pre/post edit (grep-checkable).
  - **Decision 3**: No schema bump. `schemas/finding.yaml` remains at v1.7. Reuses existing `AG-{N}` ID prefix.
  - **Decision 4**: No consumers-list edit. `tool-abuse` already at `finding-format-shared.md:16` (verified at PRD time).
  - **Decision 5**: No orchestrator/dispatch-rules edit. `tool-abuse` already fully registered (verified across 7 callsites at PRD time).
  - **Decision 6**: Public ADR omits commercial framing per Option C governance contract from SDR-001. The cross-reference to SDR-001 Decision 4 lives in private companion docs only.
- **Cross-references** (public-safe): ADR-023 (lean+skill-references pattern, additive-only edits), ADR-021 (byte-identity baseline harness), ADR-027 (taxonomy crosswalk), ADR-028 (source attribution schema), ADR-030 (Heuristic A within LLM tier), ADR-031 (regex minor-bump rule — referenced as the asymmetry: F-3 does not need it).
- **Zero-MAESTRO-reference invariant**: ADR-032 itself contains zero MAESTRO references in its Decision sections, mirroring the agent file invariant.

### FR-5 — Example Regeneration Target

- **Target architecture**: `examples/agentic-app/` (extended in Feature 142 with `Inter-agent Communication Channel` component type; F-1 already regenerated this example with new `OI-{N}` findings).
- **Acceptance**: at least 1 new `AG-{N}` finding produced citing `OWASP ASI07:2026`, attributable to Pattern Category 9 OR 10. Architect adjudicates the final example target at plan time. Fallback candidate: a newly-introduced minimal multi-agent fixture if `examples/agentic-app/` does not exhibit a sufficiently clean inter-agent channel signal.
- **Byte-identity gate** (SC-7): `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` (those baselines do not exhibit multi-agent inter-agent channels, so Categories 9 and 10 emit zero findings, so artifacts are unchanged).

### FR-6 — Source Attribution Population on Category-9/10 Findings

- **Per-finding requirement**: every Category-9 finding emits `source_attribution` containing **at minimum** `{taxonomy: owasp, id: ASI07, relationship: primary}` and `{taxonomy: cwe, id: CWE-287, relationship: related}`. Where applicable: `{taxonomy: atlas, id: AML.T0060, relationship: related}`.
- **Per-finding requirement**: every Category-10 finding emits `source_attribution` containing **at minimum** `{taxonomy: owasp, id: ASI07, relationship: primary}` and `{taxonomy: cwe, id: CWE-345, relationship: related}`. Where applicable: `{taxonomy: owasp, id: LLM03, relationship: related}`.
- **Catalog resolvability**: all five citations (ASI07, CWE-287, CWE-345, AML.T0060, LLM03) verified present in the taxonomy catalogs at PRD time. F-A2 referential-integrity validator passes by construction.
- **Existing AG findings** (Categories 1–8): existing `tool-abuse` findings already populate `source_attribution` from prior wiring — F-3 extends an existing populator rather than adding a new one. The post-F-3 referential-integrity contract is proven across **two-execution-deep** (F-1 + F-2) for new agents AND **one-execution-deep** (F-3) for enrichment; this is sufficient to lift the contract from "validated on new agents" to "validated on both new agents and enrichments."

---

## 🚀 Non-Functional Requirements

### Performance

- **Agent invocation latency**: no measurable change. The new Pattern Categories 9 and 10 are matched by the same DFD-traversal logic that walks Categories 1–8 today; the marginal overhead is O(2 additional pattern matches per AG dispatch). Empirical impact <1ms per architecture file.
- **Architecture analysis throughput**: unchanged. F-3 does not add a new dispatch step.

### Reliability / Determinism

- **Byte-identity** (ADR-021 SOURCE_DATE_EPOCH=1700000000): SC-7 explicitly verifies byte-identity on the 5 non-multi-agent baselines. The Heuristic A consolidation pattern PRESERVES byte-identity by construction on baselines that do not exhibit the new trigger surface.
- **Idempotency**: Categories 9 and 10 are deterministic given a fixed architecture input; the same architecture file produces the same finding set across runs.

### Security

- **Zero MAESTRO references** (ADR-023 Decision 2): preserved on `tool-abuse.md` and `detection-patterns.md` post-edit.
- **Public ADR scope**: ADR-032 omits commercial framing per Option C governance. SDR-001 cross-reference lives in private companion docs only.
- **No new attack surface introduced**: F-3 is documentation + pattern enrichment; no new code paths, no new dependencies, no new I/O.

### Maintainability

- **Lean shape preserved**: `tool-abuse.md` post-edit ≤150 lines (PRD-time baseline 98; expected post-edit 100–106).
- **Additive-only invariant**: existing prose in `tool-abuse.md` `## Purpose` and Categories 1–8 in `detection-patterns.md` are byte-identical pre/post edit. Grep-checkable.
- **Single-source-of-truth**: ADR-032 documents the Heuristic A enrichment pattern; future ASI06 / ASI08 / similar consolidations reuse this ADR as precedent.

---

## 📊 Success Metrics

### Coverage

- **OWASP Agentic Top 10:2026**: ASI07 transitions Planned → Covered. Coverage Matrix post-F-3: 6 of 10 ASI items covered (ASI-01 / ASI-02 / ASI-04 / ASI-07 / MCP-03 / MCP-05).
- **Multi-agent example coverage**: at least 1 new `AG-{N}` finding on `examples/agentic-app/` (or chosen fallback) demonstrating Category 9 or 10 firing.

### Quality

- **Byte-identity baselines**: 5 of 6 example baselines regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. The 6th (`agentic-app`) is the expected mutation candidate.
- **Line count cap**: `tool-abuse.md` post-edit ≤150 lines (95% margin reserved for future enrichment).
- **Catalog resolvability**: 100% of Category-9/10 `source_attribution` citations resolve against `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml`.

### Pattern Validation

- **Heuristic A enrichment pattern**: first execution. Establishes the precedent for future Heuristic A consolidations.
- **No-schema-bump pattern**: first BLP-01 detection feature without a schema increment. Establishes the precedent that consolidation features reuse the host's ID space.

### Delivery

- **Calendar window**: 2026-04-28 (Tuesday) build day; 2026-04-29 (Wednesday) buffer; 2026-04-30 (Thursday) reserved for multi-feature concurrency hedge.
- **Effort envelope**: 1 working day realistic, 0.5 days aspirational.

---

## 🔍 Scope & Boundaries

### In Scope (MVP / Phase 1)

**Must Have (P0)**:
- ✅ Pattern Category 9: Insecure Inter-Agent Communication (A2A) — appended to `detection-patterns.md`
- ✅ Pattern Category 10: MCP-to-MCP Trust Propagation — appended to `detection-patterns.md`
- ✅ `tool-abuse.md` `owasp_references` += `ASI-07`
- ✅ `tool-abuse.md` `## Purpose` extension naming the A2A / MCP-to-MCP surface
- ✅ `tool-abuse.md` Detection Workflow Step 5 references += `ASI-07`, `AML.T0060`, `CWE-287`, `CWE-345`
- ✅ Primary Sources list += `OWASP ASI07:2026`, `MITRE ATLAS AML.T0060`
- ✅ Public ADR-032 (Heuristic A enrichment for ASI07)
- ✅ Example regeneration on `examples/agentic-app/` (or architect-chosen fallback)
- ✅ Byte-identity verification on 5 non-multi-agent baselines
- ✅ Source attribution population on Category-9/10 findings

### Out of Scope (Future Phases)

**Could Have (P2) — Not in F-3**:
- 🔮 ASI06 (Intent Manipulation) enrichment — different signal class; needs its own Heuristic A adjudication
- 🔮 ASI08 (Repudiation) enrichment — STRIDE-tier with potential AG cross-cite; out-of-scope for BLP-01 Tier 1
- 🔮 MCP-04 / MCP-06 (additional MCP Top 10 items) — out-of-scope; current `tool-abuse` already covers MCP-03 / MCP-05; remaining MCP items defer to a future MCP-bundle feature
- 🔮 New `inter-agent-communication` agent — explicitly REJECTED per Heuristic A consolidation; reopening this would re-adjudicate every prior consolidation

**Won't Have — Explicitly excluded**:
- ❌ Schema bump 1.7 → 1.8 — F-3 does not introduce a new ID prefix; reuses `AG-{N}`
- ❌ `finding-format-shared.md` consumers list edit — `tool-abuse` already at line 16
- ❌ Orchestrator dispatch-rules edit — `tool-abuse` already fully registered (7 callsites verified)
- ❌ Runtime dependency additions — none required

### Assumptions

- **A1**: `examples/agentic-app/` exhibits a sufficiently clean multi-agent topology after Feature 142's `Inter-agent Communication Channel` component type addition. **Validation**: architect inspects the example architecture at plan time; if insufficient, architect chooses a fallback (newly-introduced minimal multi-agent fixture, or extension of `agentic-app` itself).
- **A2**: ADR-032 is the next available ADR number at merge time. **Validation**: team-lead checks `docs/architecture/02_ADRs/` directory and assigns the actual number at plan time. Renumber is a one-line edit if needed.
- **A3**: No competing F-4 / F-5 PR is open at F-3 build time. **Validation**: team-lead checks `gh pr list` and BACKLOG.md at build start; if competing, sequence F-3 first (smaller surface, lower-conflict footprint).

### Constraints

**Technical**:
- `tool-abuse.md` line count must remain ≤150 (ADR-023 AI tier cap).
- Categories 1–8 in `detection-patterns.md` must be byte-identical pre/post edit (ADR-023 Decision 3).
- Zero MAESTRO references on enriched files (ADR-023 Decision 2).
- Public ADR omits commercial framing (SDR-001 Option C).

**Calendar**:
- Build window starts 2026-04-28 (Tuesday); 2026-04-25 (today) is PRD day.

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Day 1 — 2026-04-28 (Tuesday)** — Build
- AM: senior-backend-engineer applies FR-1 (`tool-abuse.md` metadata + Detection Workflow + `## Purpose`) and FR-2/FR-3 (`detection-patterns.md` Categories 9 + 10 + Primary Sources). ADR-032 Proposed commit.
- PM: regenerate `examples/agentic-app/` (FR-5); byte-identity verification on 5 non-multi-agent baselines (SC-7); ADR-032 Accepted transition; PR open as draft.

**Buffer — 2026-04-29 (Wednesday)** — Slack day + Delivery retrospective
- Reserved for regeneration friction (fixture drift on the chosen example), ADR-032 review polish, or PR review feedback turnaround.
- **Delivery retrospective filed at `specs/219-asi07-tool-abuse-enrichment/delivery.md`** (mirrors F-1 + F-2 precedent at `specs/201-...` and `specs/206-...`). Authored same-day-as-delivery if Day 1 PM merge has ≥1 hour residual capacity; otherwise authored on this Buffer Day 1 as the primary buffer-day activity. The retrospective explicitly captures: (a) actual vs. estimated effort, (b) Heuristic A enrichment pattern lessons (this is the **first execution** of the enrichment branch — the retrospective sets precedent for F-6 / F-7 Tier 2 ML+Mobile bundles which may also use enrichment), (c) byte-identity preservation evidence (SC-7 grep proofs), (d) any deviations from PRD timeline or scope.

**Buffer — 2026-04-30 (Thursday)** — Multi-feature concurrency hedge
- Reserved for F-3 + F-4 + F-5 sequencing collisions if F-4 or F-5 enters build concurrently. Mitigation: F-3 ships first (smallest surface, no shared edits with F-4/F-5).

### Release Discipline — PR Title Contract

**Per `.claude/rules/git-workflow.md` (Conventional Commit PR Titles section)**: PR title MUST be `feat(219): <short description>` so that release-please fires on merge. The recommended title (architect / team-lead may refine at plan time): **`feat(219): asi07 inter-agent communication tool-abuse enrichment`** (or similar Conventional Commit form ≤70 chars).

**Two-step belt-and-suspenders enforcement**:
1. **Plan stage** — `/aod.plan` opens the draft PR via `gh pr create --draft --title "feat(219): asi07 inter-agent communication tool-abuse enrichment"`. The title is set correctly from the moment the draft is created.
2. **Deliver stage** — `/aod.deliver` re-verifies the PR title is Conventional-Commit-formatted before squash-merging. If a non-conventional title slipped through, retitle BEFORE merge: `gh pr edit <PR> --title "feat(219): ..."`. Post-merge, verify a release-please PR opened within ~30s; if not, push an empty `feat(219): ... release marker` commit.

**Rationale**: F-3 closes ASI07 on the Coverage Matrix. If the merge does not trigger a release-please PR, adopters consuming via SemVer-pinned dependencies do not see ASI07 coverage land. This rule was reinforced today (2026-04-25) following the F-212 PR #213 release-please-skip incident — the mitigation is propagated to all in-flight PRDs starting with F-3.

**Type prefix**: MUST be `feat:` — F-3 is a user-visible feature enrichment, not a bug fix. `fix:` would mis-categorize the change. `docs:` / `chore:` would be hidden-bump and would not trigger a release.

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-25 | product-manager | 🟡 In Review |
| `/aod.plan` (spec → plan → tasks) | 2026-04-27 | architect, team-lead | 📋 Pending |
| Build Day 1 | 2026-04-28 | senior-backend-engineer | 📋 Pending |
| Buffer Day 1 | 2026-04-29 | — | 📋 Pending |
| Buffer Day 2 | 2026-04-30 | — | 📋 Pending |
| `/aod.deliver` (squash-merge + release) | 2026-04-29 (PM) or 2026-04-30 | team-lead | 📋 Pending |
| ADR-032 Accepted commit | 2026-04-29 (post-merge) | architect | 📋 Pending |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ⚠️ Risks & Dependencies

### Technical Risks

**R1 — Example regeneration friction on `examples/agentic-app/`**
- **Likelihood**: Medium
- **Impact**: Low (delays Day 1 PM by ≤4 hours)
- **Mitigation**: Architect inspects the example architecture at plan time and chooses fallback if insufficient. The 5 non-multi-agent baselines are byte-identical by construction, so the only mutation work is on the chosen multi-agent example.
- **Contingency**: Buffer Day 1 (2026-04-29) absorbs up to 8 hours of regeneration friction.

**R2 — Heuristic A consolidation pushback at architect review**
- **Likelihood**: Low (SDR-001 Decision 4 already locked the resolution; ADR-030 + ADR-031 reinforced the signal-class taxonomy)
- **Impact**: High (could force re-scoping to a new agent, doubling effort)
- **Mitigation**: PRD Section "Three things the solution is deliberately NOT" pre-empts the most likely architect concerns. ADR-032 cross-references ADR-030 Decision 1 to reuse the signal-class precedent.
- **Contingency**: If pushback occurs, escalate to a 30-minute architect-PM-team-lead alignment session before re-scoping. The Heuristic A enrichment pattern is foundational to BLP-01 Tier 2 (ML + Mobile bundles); abandoning it on F-3 would reopen scope on F-6 / F-7.

**R3 — Multi-feature concurrency conflicts (F-3 + F-4 + F-5)**
- **Likelihood**: Low (F-4 and F-5 are at `stage:discover` or earlier as of PRD time; F-3 enters build first)
- **Impact**: Medium (additive-edit conflicts on `tool-abuse.md`, `finding-format-shared.md`, `dispatch-rules.md`)
- **Mitigation**: F-3 has the **smallest** edit surface among Tier 1 features (2 host files only; no `finding-format-shared.md` edit; no orchestrator edit). F-4 (ASI09 — likely new agent) and F-5 (LLM10 — likely new agent or `tool-abuse` enrichment) WILL touch `finding-format-shared.md` and the orchestrator. Sequencing F-3 first minimizes rebase friction.
- **Contingency**: Buffer Day 2 (2026-04-30) absorbs concurrency-rebase work.

**R4 — Catalog drift between PRD time and build time**
- **Likelihood**: Very Low (taxonomy catalogs are stable; F-A1 fully delivered)
- **Impact**: Low (one-line schema edit if catalog ID changes)
- **Mitigation**: PRD-time verification of all 5 catalog citations (ASI07, CWE-287, CWE-345, AML.T0060, LLM03). Re-verified at plan time per architect.
- **Contingency**: If catalog drift detected, re-cite or remove the offending citation; F-A2 referential-integrity validator catches drift programmatically.

**R6 — Release-please skip if PR title misformatted**
- **Likelihood**: Low (rule explicitly stated; F-212 incident is fresh)
- **Impact**: High (no release ⇒ adopters consuming via SemVer-pinned deps do not receive ASI07 coverage; manual recovery via empty release-marker commit per F-212 precedent)
- **Mitigation**: Two-step belt-and-suspenders enforcement per `.claude/rules/git-workflow.md`: (1) `/aod.plan` opens draft PR with `feat(219): ...` title from the start; (2) `/aod.deliver` pre-merge re-verifies and retitles if needed; post-merge verifies release-please PR opened within ~30s.
- **Contingency**: If release-please skips post-merge, push empty marker commit `git commit --allow-empty -m "feat(219): asi07 inter-agent communication enrichment — release marker"` per F-212 recovery pattern. Buffer Day 1 (2026-04-29) absorbs recovery time if needed.

### Business Risks

**R5 — BLP-01 momentum perception**
- **Likelihood**: Very Low
- **Impact**: Low
- **Rationale**: F-3 closing within 1 working day demonstrates that the Heuristic A enrichment pattern produces a leaner, faster delivery than the new-agent pattern. This is positive momentum, not negative — it validates the BLP-01 sequencing strategy.

### Dependencies

**Internal Dependencies (all satisfied at PRD time)**:
- F-A1 (Feature 180): taxonomy catalogs — **SATISFIED**
- F-A2 (Feature 189): source_attribution schema — **SATISFIED**
- F-B (Feature 194): coverage attestation PDF — **SATISFIED**
- F-1 (Feature 201): output-integrity agent — **SATISFIED** (informational precedent only)
- F-2 (Feature 206): misinformation agent — **SATISFIED** (informational precedent only)
- Existing `tool-abuse` agent and companion `detection-patterns.md` — **SATISFIED**

**External Dependencies**: None.

**Dependency Graph**:
```
F-3 (this feature)
  ├─ Reads from: schemas/taxonomy/owasp.yaml (ASI07)
  ├─ Reads from: schemas/taxonomy/cwe.yaml (CWE-287, CWE-345)
  ├─ Reads from: schemas/taxonomy/mitre-atlas.yaml (AML.T0060)
  ├─ Edits: .claude/agents/tachi/tool-abuse.md (additive)
  ├─ Edits: .claude/skills/tachi-tool-abuse/references/detection-patterns.md (additive)
  ├─ Creates: docs/architecture/02_ADRs/ADR-NNN-asi07-tool-abuse-enrichment.md (new)
  └─ Blocks: nothing (parallel-eligible with F-4, F-5)
```

---

## ❓ Open Questions

| # | Question | Owner | Due | Status |
|---|----------|-------|-----|--------|
| Q1 | Does Pattern Category 9 need to distinguish "channel-without-auth" from "channel-with-broken-auth"? Currently single category covers both. | architect | plan | **Resolved (architect, 2026-04-25)**: single category covers both. Indicator 2 ("does not declare mutual authentication") naturally encompasses both no-auth-declared and broken-auth-declared. The threat is the same (relying party accepts spoofed/tampered/replayed messages); the mitigation is the same (implement strong mutual auth). Splitting would mirror F-2's pre-PRD scoping over-fragmentation. ADR-032 Decision 1 supporting evidence to document this. |
| Q2 | Should `dispatch-rules.md` `tool-abuse (MCP-03)` annotation be extended to `tool-abuse (MCP-03, ASI-07)` for parity? Cosmetic; no functional change. Architect adjudicates. | architect | plan | Researching — strong leaning YES per architect review (annotation-only, adds Coverage Matrix traceability without modifying dispatch logic). PRD SC-10 wording already softened to accommodate. |
| Q3 | Is `examples/agentic-app/` the right example target post-Feature 142, or should F-3 introduce a new minimal multi-agent fixture? | architect | plan | Researching — `examples/maestro-reference/` is a third candidate per architect note (tertiary persona explicitly mentions canonical MAESTRO CDSS reference). Architect to evaluate all three at plan time. |
| Q4 | Does Pattern Category 10 require explicit anti-indicators (e.g., "single-MCP architectures emit no Category-10 findings")? Mirrors F-2 anti-indicator discipline (M5). | architect | plan | Researching — strong leaning YES per architect review. The acceptance criteria already specify "single-MCP architectures emit zero Category-10 findings" (US-219-2 AC-4); formalize as explicit anti-indicator section in `detection-patterns.md` Category 10. |
| Q5 | Build-day sequencing — does F-3 ship 2026-04-28 (Tuesday) or compress to 2026-04-27 (Monday) given 1-day envelope? | team-lead | plan | **Resolved (team-lead, 2026-04-25)**: F-3 ships **2026-04-28 Tuesday**. Monday is plan day per the established Tuesday-after-Monday-plan cadence (F-2 used the same pattern: PRD Thu, plan Fri/Sat, build Mon/Tue). Compressing build into the same day as plan would violate "plan complete before build starts" sequencing that F-1 and F-2 both honored. |

---

## 📚 References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- F-2 PRD (precedent): `docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md`
- F-1 PRD (precedent): `docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md`

### Strategic Documentation
- BLP-01 Strategy (private): `_internal/strategy/BLP-01-threat-coverage.md` §7 F-3
- SDR-001 Strategy Decision Record (private): `_internal/strategy/SDR-001-threat-coverage-strategy.md` Decision 4 (Heuristic A)
- GUIDE-threat-coverage-research (private): `_internal/strategy/GUIDE-threat-coverage-research.md` §2 OWASP Agentic Top 10:2026 + §11 Heuristic A signal-class taxonomy

### Architecture Decision Records (public)
- ADR-021 SOURCE_DATE_EPOCH determinism: `docs/architecture/02_ADRs/ADR-021-source-date-epoch.md`
- ADR-023 Threat Agent Skill References Pattern: `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (Decision 1, 2, 3)
- ADR-027 Taxonomy Crosswalk Schema: `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 Source Attribution Schema Extension: `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-029 Coverage Attestation Report Section: `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
- ADR-030 Output Integrity Agent: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` (Decision 1 Heuristic A signal-class taxonomy)
- ADR-031 Misinformation Agent: `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` (Decision 2 Heuristic A inheritance; Decision 8 regex minor-bump rule — referenced as the asymmetry: F-3 does not invoke it)

### Technical References
- Existing `tool-abuse` agent: `.claude/agents/tachi/tool-abuse.md`
- Existing `tool-abuse` detection patterns: `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`
- Finding format (shared): `.claude/skills/tachi-shared/references/finding-format-shared.md`
- Severity bands (shared): `.claude/skills/tachi-shared/references/severity-bands-shared.md`
- Taxonomy catalogs: `schemas/taxonomy/owasp.yaml`, `schemas/taxonomy/cwe.yaml`, `schemas/taxonomy/mitre-atlas.yaml`
- Finding schema: `schemas/finding.yaml` (v1.7, no bump in F-3)

### External Resources
- OWASP Agentic Top 10:2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP LLM Top 10:2025: https://genai.owasp.org/llm-top-10/
- MITRE ATLAS: https://atlas.mitre.org/
- Feature 142 (`Inter-agent Communication Channel` component type): see project history; canonical `examples/agentic-app/` extension

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [x] Problem statement is clear and user-focused (multi-agent threat surface gap)
- [x] User stories have measurable acceptance criteria (US-219-1, US-219-2, US-219-3 all carry Given/When/Then ACs)
- [x] Success metrics are defined and measurable (SC-1 through SC-11, all grep-checkable or programmatically verifiable)
- [x] Scope is realistic for timeline (1-day envelope; smaller surface than F-1/F-2)
- [x] Risks and dependencies identified (5 risks, all dependencies satisfied at PRD time)
- [x] Aligns with product vision (closes ASI07 gap; demonstrates Heuristic A enrichment pattern)

**Architect** (architect):
- [ ] Technical requirements are clear (FR-1 through FR-6 specify exact files, lines, edits)
- [ ] Non-functional requirements are realistic (no perf change; byte-identity preserved)
- [ ] Dependencies are accurate (PRD-time verified across catalog files and host agent registration)
- [ ] Technical risks are identified (R1–R5)
- [ ] Architecture approach is sound (Heuristic A consolidation per SDR-001 Decision 4)

**Engineering Lead** (team-lead):
- [ ] Requirements are implementable (PRD-time baseline measurements support the effort estimate)
- [ ] Effort estimates are reasonable (1 working day; F-3 is structurally smaller than F-2)
- [ ] Team capacity is available (post-F-2 delivery, no competing builds in window)
- [ ] Timeline is realistic (2026-04-28 build day with 2-day buffer)

### Definition of Done

1. `tool-abuse.md` `owasp_references` extended with `ASI-07`; line count ≤150.
2. `tool-abuse.md` `## Purpose` extension naming the A2A / MCP-to-MCP surface (1-3 lines).
3. `tool-abuse.md` Detection Workflow Step 5 references extended with `ASI-07`, `AML.T0060`, `CWE-287`, `CWE-345`.
4. `detection-patterns.md` Pattern Categories 9 + 10 appended; existing Categories 1–8 byte-identical (grep-checkable).
5. `detection-patterns.md` Primary Sources extended with `OWASP ASI07:2026` and `MITRE ATLAS AML.T0060`.
6. ADR-032 (or next-available-number) Proposed → Accepted dual-commit landed.
7. `examples/agentic-app/` (or architect-chosen multi-agent example) regenerated; ≥1 new `AG-{N}` finding citing OWASP ASI07:2026.
8. 5 non-multi-agent example baselines regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`.
9. `source_attribution` populated on every Category-9/10 finding with catalog-resolvable IDs; F-A2 referential-integrity validator passes.
10. PR title is `feat(219): asi07 inter-agent communication tool-abuse enrichment` (or similar Conventional Commit form); PR squash-merged on main; release-please PR opens within ~30s.
11. Coverage Matrix updated: ASI07:2026 transitions Planned → Covered.
12. **Delivery retrospective filed at `specs/219-asi07-tool-abuse-enrichment/delivery.md`** (mirrors F-1 + F-2 precedent) capturing actual vs. estimated effort, Heuristic A enrichment-pattern lessons (first execution), byte-identity preservation evidence, and any deviations from PRD. Authored same-day-as-delivery if capacity permits; otherwise on Buffer Day 1 (2026-04-29 Wed).

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ APPROVED | 2026-04-25 | PRD grounded in BLP-01 §7 F-3 spec and Issue #219; 3 user stories preserved with job-story restructuring; 11 success criteria covering DoD bullets; HIGH-1 retrospective slotting + HIGH-2 PR title contract addressed inline; Q1 + Q5 resolved at PRD time; Pattern Category Disambiguation paragraph added to FR-2 (M2 fix); SC-10 wording softened to accommodate Q2 annotation-only edit (architect LOW-2 fix). Ready for /aod.plan. |
| Architect | architect | 🟡 APPROVED_WITH_CONCERNS | 2026-04-25 | 0 BLOCKING / 0 HIGH / 2 MEDIUM / 2 LOW. Heuristic A enrichment correctly chosen for ASI07 — signal-class identity with existing tool-abuse coverage. All PRD-time invariants independently verified (schema v1.7, 7 dispatch callsites, 5 catalog citations including ASI07/CWE-287/CWE-345/AML.T0060/LLM03, ADR-032 numbering, zero MAESTRO refs). Pattern Categories 9+10 indicators carve surface correctly with 5 each. MEDIUM-1 Q1 channel-without-auth vs broken-auth: resolved inline as single category. MEDIUM-2 Category 6 vs 10 non-overlap: addressed via Pattern Category Disambiguation subsection in FR-2. LOW-1 CWE-300 consideration: deferred to architect plan-day adjudication. LOW-2 line-number references: addressed by softening SC-10 wording. ADR-032 6-decision scope appropriately public. Q1/Q2/Q3/Q4 architect-tractable at plan time. Full review: .aod/results/architect.md. |
| Engineering Lead | team-lead | 🟡 APPROVED_WITH_CONCERNS | 2026-04-25 | 0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. Calendar verified (cal 4 2026 confirms 04-25 Sat / 04-27 Mon / 04-28 Tue / 04-29 Wed / 04-30 Thu). All 7 PRD on-disk claims verified (98-line tool-abuse, 163-line detection-patterns, schema v1.7, 7 dispatch callsites, ADR-032 next-available). F-3 surface 5/5 dimensions smaller than F-2 (no new agent / no new skill dir / no schema bump / no consumers list edit / no orchestrator edit) — 1-day envelope realistic with 2-day buffer. HIGH-1 retrospective slotting: addressed via Buffer Day 1 retrospective slot + DoD bullet 12. HIGH-2 PR title contract: addressed via "Release Discipline — PR Title Contract" subsection + R6 risk. MEDIUM-4 Q5: resolved inline (Tue 2026-04-28). MEDIUM-1 effort-S asymmetry: deferred to architect plan-day AC-to-test mapping. R3 multi-feature concurrency: Buffer Day 2 hedge adequate. Capacity 12h Triad / 8h engineer / 3 days — sustainable. Ready for /aod.plan. Full review: .aod/results/team-lead.md. |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-25 | product-manager | Initial PRD — F-3 Heuristic A enrichment of `tool-abuse` for ASI07 coverage |
