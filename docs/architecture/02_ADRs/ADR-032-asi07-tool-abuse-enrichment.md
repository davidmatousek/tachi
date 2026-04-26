# ADR-032: ASI07 Tool-Abuse Enrichment (OWASP Agentic ASI07:2026 Coverage)

**Status**: Accepted
**Date**: 2026-04-28 (Proposed); transitions to Accepted at PR #220 merge
**Deciders**: Architect (tachi project)
**Feature**: [219-asi07-tool-abuse-enrichment](../../../specs/219-asi07-tool-abuse-enrichment/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean-agent + additive-only shared-reference Decision 3 — F-3 follows the additive-only edit discipline in its purest form), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy crosswalk — F-3 cites OWASP ASI07/LLM03 + CWE-287/CWE-345 + AML.T0060), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 source_attribution schema — F-3 is third producer flow / first **enrichment** of an existing populator), [ADR-030](ADR-030-output-integrity-agent.md) (F-1 indirect precedent — Decision 1 signal-class taxonomy in LLM tier as a different application of the same rule applied within the AG tier by F-3), [ADR-031](ADR-031-misinformation-agent.md) (F-2 direct precedent — Decision 8 regex-alternation minor-bump rule cross-referenced as the **asymmetry** F-3 does NOT invoke; F-3 is the first BLP-01 detection feature with no schema bump)

---

## Context

Tachi's agentic-AI threat-modeling pipeline ships, post-F-2 (Feature 206 merged 2026-04-24), 7 AI-tier detection agents covering input-side attacker injection (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`), downstream-execution-sanitization (`output-integrity` — LLM05:2025), and factual-integrity (`misinformation` — LLM09:2025). What remains silent on the agentic-tier surface is the **inter-agent communication channel** signal class: A2A channels (direct RPC, message bus, shared queue, MCP-to-MCP bridge, named pipe, IPC) without declared mutual authentication, message signing, replay protection, or taint propagation; and multi-hop MCP trust chains (Agent → MCP-A → MCP-B) without per-hop attestation, signed-capability handoff, or trust-chain validator. OWASP Agentic ASI07:2026 (Insecure Inter-Agent Communication) names this threat class as one of the top 10 Agentic application risks for 2026, and the BLP-01 Coverage Matrix records ASI07:2026 as **Planned** with F-3 named as the closure feature.

BLP-01 (Better LLM Protection initiative, documented in `_internal/strategy/BLP-01.md`) identifies ASI07 as Tier 1 priority F-3, following F-1 (Feature 201) `output-integrity` and F-2 (Feature 206) `misinformation`. Whereas F-1 and F-2 introduced **net-new** AI-tier agents (LLM tier), **F-3 is the first execution of the Heuristic A enrichment branch** within the AG tier: rather than authoring an `inter-agent-communication` agent as an 8th AI-tier sibling, F-3 enriches the existing `tool-abuse` agent with two new Pattern Categories (9: A2A; 10: MCP-to-MCP). The rationale — signal-class identity with existing tool-abuse coverage (message flow between agent-or-tool endpoints) — was locked at SDR-001 Decision 4 and is operationalized here.

The feature ships purely additive edits to two existing files plus this public ADR: (1) `tool-abuse.md` metadata `owasp_references += [ASI-07]`, `## Purpose` 1-3 line extension naming the inter-agent channel surface, Detection Workflow Step 5 references += `[ASI-07, AML.T0060, CWE-287, CWE-345]`; (2) `detection-patterns.md` appends Pattern Category 9 + Pattern Category 10 + Pattern Category Disambiguation subsection + Primary Sources extension; (3) ADR-032 (this file) under Proposed → Accepted dual-commit per ADR-027/028/029/030/031 precedent. The schema `schemas/finding.yaml` is **not modified** — F-3 reuses the existing `AG-{N}` prefix and is the **first BLP-01 detection feature with no schema bump**, an asymmetry with F-1's 1.5 → 1.6 bump and F-2's 1.6 → 1.7 bump. The asymmetry is recorded explicitly in Decision 3 below.

PRD 219 was approved 2026-04-25 with full Triad sign-off (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS — all HIGH/MEDIUM concerns resolved inline before sign-off). The spec (PM APPROVED), plan (PM + Architect APPROVED), and tasks (PM + Architect + Team-Lead APPROVED) all landed 2026-04-25. The Heuristic A enrichment-vs-new-agent decision was inherited from SDR-001 Decision 4 + ADR-030 Decision 1 + ADR-031 Decision 8 (cross-referenced as the asymmetry below) and re-verified by the architect at Wave 1.0 T003 in `.aod/results/wave1-architect-reverify.md`. Decisions 1 and 3 below record the inheritance and asymmetry with explicit cross-references.

### Constraints

- **24-file zero-edit invariant** (spec SC-013, FR-015 — ADR-023 lineage extended by F-1 + F-2): F-3 MUST NOT edit any of the 12 other AI/STRIDE threat-agent files at `.claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,agent-autonomy,output-integrity,misinformation}.md` or their 12 companion `detection-patterns.md` reference files at `.claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,agent-autonomy,output-integrity,misinformation}/references/`. ADR-023 Decision 2 stabilized the original 22-file scope in Feature 082; F-1 added 2 (output-integrity agent + companion); F-2 added 2 (misinformation agent + companion). Post-F-2 the invariant covers 26 detection files; F-3 edits 2 host files (`tool-abuse.md` + companion `detection-patterns.md`) and the remaining 24 stay byte-identical. The host files were ALREADY part of the 22-file invariant per ADR-023 — F-3 follows ADR-023 Decision 3's additive-only edit discipline to preserve byte-identity on Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` regions.
- **Byte-identity backward compatibility** (spec SC-010, FR-009 — ADR-021 lineage): the 5 non-multi-agent example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. The multi-agent / multi-MCP topology gate (FR-011) enforces zero Category-9/10 emissions on architectures lacking ≥2 agent Process components connected by a channel (Cat 9) or a multi-hop MCP trust chain (Cat 10). The 5 baselines fall in non-qualifying topology by construction (PRD-time architect-verified), preserving byte-identity. The 6th baseline (`agentic-app` per PRD Q3 PM default; architect plan-day decision recorded in `.aod/results/wave1-q3-example-target-decision.md`) is the expected mutation candidate per FR-9.
- **Zero new runtime or developer dependencies** (spec SC-012): empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `package.json`, `package-lock.json`. `pyyaml` and `pytest` remain developer-only per Feature 128 precedent. No new orchestrator phase, no new LLM-judgment pathway, no new HTTP fetch.
- **F-A2 referential-integrity contract** (spec SC-015 — ADR-028 Decision 5 lineage): every emitted Category-9 / Category-10 `AG-{N}` finding's `source_attribution` array MUST resolve every `(taxonomy, id)` pair against `schemas/taxonomy/{taxonomy}.yaml`. F-3 is the **third net-new producer flow** the validator at `scripts/tachi_parsers.py:826` enforces against (after F-1 OI-{N} + F-2 MI-{N}) and the **first enrichment of an existing populator** — Categories 1-8 already populate `source_attribution` from prior wiring; Categories 9-10 extend the same agent's emission. All 5 catalog citations (ASI07, CWE-287, CWE-345, AML.T0060, LLM03) are catalog-resolvable as of PRD time and re-verified at Wave 1.0 (`.aod/results/wave1-architect-reverify.md`).
- **Zero MAESTRO references** in `tool-abuse.md` and `detection-patterns.md` post-edit (spec FR-010 / SC-016): grep-auditable invariant per ADR-023 Decision 2. PRD-time baseline: zero MAESTRO references in both files. F-3 preserves this invariant by construction.
- **No schema bump** (spec FR-013 / SC-014): `schemas/finding.yaml` `schema_version` remains `"1.7"` post-F-3. The `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$` (post-F-2 state). F-3 reuses the existing `AG` prefix and is therefore the **first BLP-01 detection feature with no schema bump** — a deliberate asymmetry with F-1 (1.5 → 1.6) and F-2 (1.6 → 1.7). Decision 3 below records the asymmetry with explicit ADR-031 Decision 8 cross-reference.
- **No consumers-list edit** (spec FR-014): `.claude/skills/tachi-shared/references/finding-format-shared.md` is byte-identical post-F-3. PRD-time verification: `tool-abuse` is already at line 18 in the consumers list. F-3 reuses the existing consumer registration.
- **No functional orchestrator/dispatch edit** (spec FR-016 / SC-017): `.claude/agents/tachi/orchestrator.md` is byte-identical post-F-3. `.claude/skills/tachi-orchestration/references/dispatch-rules.md` receives an optional cosmetic single-token annotation (`tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`) per PRD Q2 architect plan-day decision (recorded YES in `.aod/results/wave1-q2-cosmetic-annotation-decision.md`); the annotation is documentation-only and does not invalidate the zero-functional-touch claim.
- **Multi-agent / multi-MCP topology gate** (spec FR-011 — zero-speculation discipline inherited from F-1 + F-2): Pattern Category 9 emits findings only when ≥2 agent Process components are connected by a communication channel; Pattern Category 10 emits findings only when an architecture exhibits a multi-hop MCP trust chain (Agent → MCP-A → MCP-B). Single-agent and single-MCP architectures emit zero new Category-9/10 findings — Categories 1-8 fire as they do today. The gate is enforced by anti-indicator subsections in the pattern catalog (per Q4 architect plan-day default YES) plus pattern-prose framing.

---

## Decision

We adopt the Heuristic A enrichment of the existing `tool-abuse` agent for OWASP ASI07:2026 closure per the 7 numbered decisions below. The feature ships with **zero new agent files**, **zero new skill directories**, **zero schema bumps**, **zero consumers-list edits**, and **zero functional orchestrator edits** — F-3 is structurally the smallest BLP-01 detection delivery to date. Two additive file edits (`tool-abuse.md`, `detection-patterns.md`), one new ADR (this file under Proposed → Accepted), one regenerated example (`agentic-app` per Q3 PM default), and one optional cosmetic annotation (`dispatch-rules.md` per Q2 architect plan-day decision) constitute the entire delivery surface. The 24-file zero-edit invariant (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2 host files; 24 unchanged) and the 5-baseline byte-identity gate are preserved by construction. Six of the seven decisions operationalize architectural questions raised in the PRD + spec + plan for F-3 specifically; Decision 1 records the Heuristic A enrichment-vs-new-agent inheritance; Decision 3 records F-3 as the first detection feature with no schema bump (asymmetry with F-1 + F-2).

### Decision 1 — Heuristic A enrichment vs. new agent — signal-class identity rationale

We enrich the existing `tool-abuse` agent rather than authoring a new `inter-agent-communication` agent as an 8th AI-tier sibling. The rationale rests on **signal-class identity**:

| Signal class | F-3 scope (new) | Existing tool-abuse scope (Categories 1-8) |
|---|---|---|
| Primitive type | Message flow between agent-or-tool endpoints | Message flow between agent-or-tool endpoints |
| Trigger surface | DFD Process components matching tool-abuse keywords (orchestrator, MCP server, agent, plugin, tool server) — same trigger logic | DFD Process components matching tool-abuse keywords — identical |
| Detection vocabulary | Indicators centered on absence of mutual auth / signing / replay protection / per-hop attestation / trust-chain validator on inter-agent or inter-MCP channels | Indicators centered on tool invocation, capability escalation, parameter injection, tool poisoning, MCP server poisoning |
| Mitigation taxonomy | mTLS, HMAC + nonce, per-hop attestation, signed-capability handoff, MCP-trust-chain validator, taint propagation | Allowlist enforcement, parameter schema validation, tool chain policy engines, MCP attestation, supply-chain controls |

**Heuristic A signal-class discipline test**: are F-3 Categories 9/10 detection vocabulary, CWE mapping, and mitigation taxonomy more naturally adjacent to existing `tool-abuse` Categories 1-8 (same agent, append) or to a new `inter-agent-communication` agent (separate agent file, separate trigger keyword set, separate dispatch path)? Architecture answer: ADJACENT to existing tool-abuse Categories 1-8. Splitting F-3 into a new agent would (a) duplicate the trigger-keyword set (orchestrator / MCP server / agent / plugin), (b) fragment the Agentic-category section of `threat-report.md` into two artificial sub-sections without semantic gain, (c) force the dispatch tier to maintain two registrations for the same DFD Process trigger predicate, and (d) break ID-prefix cohesion (Categories 1-8 emit `AG-{N}`; new agent would need a separate prefix or share `AG-{N}` redundantly).

**Authority acknowledgment — inheritance, not re-adjudication**: ADR-030 Decision 1 established the **signal-class taxonomy in the LLM tier** (input-side / downstream-execution-sanitization / factual-integrity / psychology-linguistics — three-way partition formalized at F-1; F-2 inherited the partition for factual-integrity). **F-3 demonstrates the same signal-class discipline applied within the AG tier**: A2A inter-agent communication and MCP-to-MCP trust propagation are sibling sub-classes of the message-flow-between-agent-or-tool-endpoints signal class that `tool-abuse` already owns; they are not a new top-level signal class warranting a new agent. This is **inheritance of the rule**, not re-adjudication — the rule is applied at the AG tier in the **enrichment** mode rather than the **new-agent** mode. SDR-001 Decision 4 is the locked resolution at the BLP-01 strategy tier; this Decision 1 is the operational realization at the F-3 architectural tier.

**Forward scope marker**: ASI06 (Intent Manipulation), ASI08 (Repudiation enrichment), and ASI09 (Trust Exploitation, F-4) own distinct signal classes that may invoke the **new-agent** branch of Heuristic A rather than the enrichment branch. F-3 does not pre-design those features; it establishes the **enrichment** branch as a viable operational pattern alongside the new-agent branch already validated by F-1 + F-2. The enrichment branch precedent is captured in the F-3 delivery retrospective (`specs/219-asi07-tool-abuse-enrichment/delivery.md`) for F-6/F-7 Tier 2 ML+Mobile bundles which may also use enrichment.

### Decision 2 — Additive-only edit discipline per ADR-023 Decision 3

We follow ADR-023 Decision 3's **additive-only edit discipline** in its purest form — F-3 is the first BLP-01 feature where additive-only edits to existing files are the **entire** delivery surface (vs. F-1 and F-2 which were primarily new-file authoring with one shared-reference additive edit each).

Specifically:

- **`tool-abuse.md`**: 3 additive edits — (1) metadata YAML `owasp_references` list extension (one-token append); (2) `## Purpose` section 1-3 line extension naming the inter-agent channel surface (the pre-existing prose paragraph remains byte-identical — extension is appended, not rewritten); (3) Detection Workflow Step 5 references list extension (4 IDs appended: `ASI-07`, `MITRE ATLAS AML.T0060`, `CWE-287`, `CWE-345`; pre-existing references preserved byte-identically).
- **`detection-patterns.md`**: 4 additive edits — (1) Pattern Category 9 appended after Category 8; (2) Pattern Category 10 appended after Category 9; (3) Pattern Category Disambiguation subsection appended after Category 10 (per Decision 7 below); (4) Primary Sources list extension with 2 entries (ASI07 + AML.T0060). Pre-existing Categories 1-8, `## Overview`, `## Targeted DFD Element Types`, `## Trigger Keywords`, and pre-existing Primary Sources entries remain byte-identical pre/post edit.

**Byte-identity proof**: a structural diff of pre/post `detection-patterns.md` returns empty for the unchanged regions (Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords`). A structural diff of pre/post `tool-abuse.md` returns empty for the pre-existing `## Purpose` prose, the pre-existing metadata fields other than `owasp_references`, and the pre-existing Detection Workflow Step 5 references. T025 Wave 2 EOD validation enforces both proofs as BLOCKER gates per spec SC-006.

ADR-023 Decision 3's `## `-heading byte-identity enforcement on shared-reference edits applies vacuously here — F-3 does not edit `finding-format-shared.md` (per Decision 4 below). The Decision 3 discipline is exercised in its purest form on `detection-patterns.md` itself: every existing `## Pattern Category N` heading and the `## Primary Sources` heading remain byte-identical; only **content under** `## Pattern Category 8` ends and **new content begins** at `## Pattern Category 9`.

### Decision 3 — No schema bump — first BLP-01 detection feature reusing existing prefix

**F-3 does NOT modify `schemas/finding.yaml`. The `schema_version` remains `"1.7"` post-F-3. The `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$` (post-F-2 state).**

F-3 reuses the existing `AG` prefix for Categories 9 and 10 findings. The pattern catalog already populates `AG-{N}` IDs for Categories 1-8 (sequential numbering across the agent's emission); Categories 9-10 extend the same single-namespace ID space without prefix segmentation. The same architecture exercising both pre-existing tool-abuse coverage AND new ASI07 coverage emits a contiguous `AG-1`, `AG-2`, ..., `AG-N` sequence with no Pattern Category-driven discontinuity.

**Asymmetry with F-1 and F-2 — explicit cross-reference to ADR-031 Decision 8**: ADR-031 Decision 8 recorded F-2 as the second application of the regex-alternation minor-bump rule (1.6 → 1.7 adding `MI` prefix); ADR-030 Decision 8 was the first application (1.5 → 1.6 adding `OI` prefix). **F-3 is NOT an application of that rule. F-3 is the asymmetry**: the rule applies to features that introduce a **new signal-class identity** warranting a distinct ID prefix (F-1's downstream-execution-sanitization vs. existing input-side; F-2's factual-integrity vs. existing input-side and downstream); F-3 introduces sub-classes within the existing `tool-abuse` signal class (inter-agent and inter-MCP message flow) and therefore reuses the existing `AG` prefix without invoking the rule.

**This asymmetry is structurally important**: it demonstrates that the Heuristic A signal-class discipline (recorded by ADR-030 Decision 1, operationalized for the LLM tier by F-1 + F-2) generalizes correctly to the AG tier in the **enrichment** mode. If F-3 had bumped the schema to add a new prefix, it would have implicitly claimed that ASI07 is a distinct signal class from tool-abuse — which contradicts Decision 1 above. The no-schema-bump invariant is therefore not just a cost-minimization; it is the **operational signal** that Decision 1's signal-class identity claim is upheld.

**Implications for future BLP-01 features**:

- **F-4** (`trust-exploitation` for ASI09) is forward-referenced by ADR-030 Decision 2 Outcome B as a **new agent** with a distinct ID prefix (e.g., `TE-{N}`), invoking the regex-alternation minor-bump rule for the third application (1.7 → 1.8). F-4 follows the **new-agent** branch.
- **F-5** (LLM10 Unbounded Consumption coverage via `denial-of-service` + `model-theft` enrichment) follows the **enrichment** branch like F-3 — no schema bump expected.
- **F-6/F-7** Tier 2 (ML/Mobile bundles) may use either branch depending on signal-class analysis at PRD time; F-3 establishes the enrichment branch as a viable operational pattern that future features can cite.

### Decision 4 — No consumers-list edit — `tool-abuse` already registered

We do NOT edit `.claude/skills/tachi-shared/references/finding-format-shared.md`. PRD-time verification (re-confirmed at Wave 1.0 T003 in `.aod/results/wave1-architect-reverify.md`) shows `tool-abuse` already at line 18 of the consumers list. The consumer registration is reused by Categories 9-10 emissions identically to Categories 1-8 emissions — both flow through the same shared finding-format contract.

**Contrast with F-1 + F-2**: F-1 added one new consumer (`output-integrity`) at the consumers-list extension; F-2 added one new consumer (`misinformation`). Both performed an additive edit to `finding-format-shared.md` per ADR-023 Decision 3. **F-3 has zero such edit**: the host agent is already registered, and the new pattern categories ride the same registration. This is the **second** ADR-023 Decision 3 invariant F-3 honors trivially (the first was the byte-identity invariant on Categories 1-8 in the pattern catalog).

### Decision 5 — No functional orchestrator/dispatch edit — `tool-abuse` already registered

We do NOT functionally edit `.claude/agents/tachi/orchestrator.md` or `.claude/skills/tachi-orchestration/references/dispatch-rules.md`. PRD-time verification shows `tool-abuse` already registered across multiple callsites in both files (orchestrator.md cross-references; dispatch-rules.md lines 92 / 107 / 122 / 147). The dispatch trigger predicates and routing logic remain byte-identical post-F-3.

**Cosmetic annotation carve-out** (per PRD Q2 architect plan-day decision recorded in `.aod/results/wave1-q2-cosmetic-annotation-decision.md`): `dispatch-rules.md` line 92 receives a single-token annotation extending `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`. This is **documentation-only** — surfaces ASI-07 alongside MCP-03 on the `tool-abuse` row for Coverage Matrix traceability. The annotation does not alter registration, dispatch keywords, or trigger routing. The pre-existing dispatch behavior is byte-identical. SC-017's zero-functional-touch claim is preserved; the cosmetic annotation is an explicit carve-out.

**Contrast with F-2's 5-callsite quintet reconciliation**: ADR-031 Decision 5 / Feature 206 recorded a 5-callsite F-1 carry-over reconciliation extending the post-F-1 quartet to the full five-agent quintet (`prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`) across orchestrator.md and dispatch-rules.md. **F-3 has no such reconciliation**: `tool-abuse` is a single-agent registration that already exists; F-3 does not extend any group enumeration. This is the **third** ADR-023 Decision 3 invariant F-3 honors trivially: zero functional dispatch edits.

### Decision 6 — Public ADR omits commercial framing per SDR-001 Option C

ADR-032 (this file) is the **public per-feature ADR** documenting F-3's Heuristic A enrichment pattern. Per SDR-001 Option C governance contract (private companion docs at `_internal/strategy/`), the public ADR:

- **Omits commercial framing**: no Layer 2, no tachi Cloud, no enterprise-only feature references, no commercial roadmap discussion. The ADR stands on technical merits only.
- **Omits SDR-001 cross-reference**: SDR-001 lives in private `_internal/strategy/` documentation; the public ADR records inheritance of SDR-001 Decision 4 via prose ("the rationale was locked at SDR-001 Decision 4") without cross-referencing the document directly.
- **Omits BLP-01 internal sequencing**: F-4 / F-5 / F-6 / F-7 are referenced as **public roadmap items** (forward scope markers) without disclosing internal prioritization rationale or commercial drivers.

This Decision 6 mirrors ADR-030 Decision 6 (F-1 ADR) and ADR-031 Decision 6 (F-2 ADR) — F-3 is the third ADR in the BLP-01 lineage to honor Option C. The dual-commit Proposed → Accepted protocol (Decision below) operates within Option C constraints.

### Decision 7 — Pattern Category Disambiguation — Category 6 (LLM03) vs. Category 10 (MCP-to-MCP)

We append a **Pattern Category Disambiguation** subsection to `detection-patterns.md` after Pattern Category 10 and before `## Primary Sources` per PRD FR-2. The subsection carves the non-overlap contract between Pattern Category 6 (LLM03 Supply Chain) and Pattern Category 10 (MCP-to-MCP Trust Propagation) — both cite OWASP LLM03:2025 in `source_attribution` (Category 10 cites it as `relationship: related` per inherited supply-chain vocabulary), but the temporal and architectural locus differs:

- **Pattern Category 6** fires on **upstream ingestion** of plugins / tools / MCP servers — sourcing, registration, manifest pinning, signed package distribution at **registry time**. The threat is that an attacker compromises the upstream supply chain (manifest registry, plugin marketplace, MCP server publisher) and injects malicious tool definitions before the agent's first invocation.
- **Pattern Category 10** fires on **runtime trust propagation** between already-registered MCP servers — per-hop attestation, signed-capability handoff, transitive authority validation at **invocation time**. The threat is that an attacker compromises a trusted MCP-A intermediary (or the trust-chain logic itself) and manipulates the multi-hop relay to MCP-B during an active session.

**Co-emission contract**: an architecture exhibiting BOTH MCP-A unsigned at registration (Category 6) AND MCP-A relays to MCP-B without per-hop attestation (Category 10) MUST emit BOTH findings. They are not duplicates and MUST NOT be merged in the threat-report's Agentic-category section. The same architecture may legitimately surface both findings describing distinct architectural gaps. Per spec FR-006 (e), Category 10 cites LLM03 as `relationship: related` (optional, when cross-MCP supply-chain trust-inheritance reasoning is surfaced); Category 6 cites LLM03 as `relationship: primary`. The dual citation is by design — distinct relationship semantics over the same OWASP framework anchor.

**Why this Decision is in the public ADR**: the carve is a structural invariant of the pattern catalog. Code-reviewer R7 verification at Wave 4 T059 enforces boundary clarity in the prose; Decision 7 above provides the architectural rationale that the prose and the code-review check both reference.

---

## Alternatives Considered

### Alternative 1 — Author new `inter-agent-communication` agent as 8th AI-tier sibling

Author `.claude/agents/tachi/inter-agent-communication.md` with companion `.claude/skills/tachi-inter-agent-communication/references/detection-patterns.md`, schema bump 1.7 → 1.8 adding new prefix (e.g., `IA` or `AC`), extend orchestrator dispatch with new registration, extend `finding-format-shared.md` consumers list with new agent.

**Why Not Chosen**: violates Heuristic A signal-class discipline per Decision 1 above. The inter-agent communication signal class is identical to existing tool-abuse coverage (message flow between agent-or-tool endpoints); splitting would (a) fragment the Agentic-category section, (b) duplicate the trigger-keyword set, (c) force ID-prefix segmentation across what is structurally a single emission stream. The architectural cost (~1 day of authoring) is also higher than enrichment (~0.4 day).

### Alternative 2 — Defer ASI07 coverage to a post-Tier-1 feature

Ship F-3 with narrower scope (Pattern Category 9 only, deferring Category 10 to a follow-on) or defer entirely to post-Tier-1.

**Why Not Chosen**: ASI07:2026 is an OWASP Agentic Top 10 risk; partial coverage would leave the Coverage Matrix in a Planned-with-partial-F-3 state harder to reason about than Planned. Categories 9 and 10 share a Heuristic A signal class (message flow); authoring both costs only marginally more than authoring one (the marginal cost is per-category trigger keywords and worked examples, not architectural scope). Splitting creates two follow-on features rather than one, doubling governance overhead.

### Alternative 3 — Schema bump 1.7 → 1.8 to add `IA` prefix for inter-agent findings

Bump schema to add a new prefix segregating Categories 9-10 findings from Categories 1-8 findings within the same agent's emission stream.

**Why Not Chosen**: violates Decision 3 above. The `IA` prefix would imply that Categories 9-10 are a distinct signal class from Categories 1-8 — but they are sub-classes within the same `tool-abuse` signal class per Decision 1. The minor-bump rule (ADR-031 Decision 8) applies to features introducing new signal-class identities; Decision 3 records F-3 as the asymmetry — it is the first detection feature with no schema bump because the ID-prefix shape is already correct for the signal class.

### Alternative 4 — Inline pattern catalog in agent file (no companion-skill edit)

Author Pattern Categories 9-10 directly inside `tool-abuse.md` rather than externalizing them to the existing companion `detection-patterns.md`.

**Why Not Chosen**: violates the ADR-023 lean-agent shape. Categories 9-10 with ≥4 indicators each, ≥1 worked example each, anti-indicator subsections (per Q4), and citation lists would consume 80-120 lines, pushing `tool-abuse.md` past the 150-line cap. The lean + skill-references pattern is the tachi standard; F-3 conforms by routing pattern catalog content to the companion file (which is unbounded by line cap).

### Alternative 5 — Move Categories 5-8 (existing MCP coverage) to a new `mcp-security` agent and re-scope `tool-abuse` to non-MCP content only

Refactor existing tool-abuse Categories 5-8 (which cover MCP poisoning, MCP supply chain, MCP cross-tool exfiltration) out of `tool-abuse.md` into a dedicated `mcp-security` agent, then add F-3 Categories 9-10 (MCP-to-MCP trust propagation) to the new agent.

**Why Not Chosen**: out-of-scope for F-3 and contradicts the additive-only edit discipline per Decision 2. Refactoring existing Categories 5-8 would violate the byte-identity invariant (SC-006 BLOCKER), reopen the 24-file zero-edit invariant, and introduce migration complexity (existing `AG-{N}` findings would need re-prefixing or category-enum changes). The tool-abuse agent's MCP coverage is a stable invariant; F-3 enriches it rather than fragmenting it.

---

## Consequences

### Positive

- **ASI07:2026 inter-agent communication threat surface closed.** F-3 ships the first detection-tier coverage of OWASP Agentic ASI07:2026, advancing OWASP Agentic Top 10:2026 framework coverage from 5/10 (post-F-2) to 6/10 (post-F-3 — ASI07 joins ASI-01 / ASI-02 / ASI-04 / MCP-03 / MCP-05). The 2 pattern categories (9 + 10) cover the full ASI07 sub-class taxonomy: A2A inter-agent communication AND MCP-to-MCP trust propagation.
- **Heuristic A enrichment branch validated as a viable operational pattern.** F-1 and F-2 validated the **new-agent** branch (LLM tier); F-3 validates the **enrichment** branch (AG tier) as the asymmetric counterpart. Future BLP-01 features (F-5 LLM10 enrichment, F-6/F-7 Tier 2 bundles) can cite F-3 as the enrichment-branch precedent. The signal-class discipline (Decision 1) generalizes from LLM tier to AG tier without modification.
- **F-A2 contract proven against three independent producer flows + one enrichment flow.** F-1 was the first net-new producer (LLM tier OI-{N}); F-2 was the second (LLM tier MI-{N}); F-3 is the third (AG tier Categories 9-10) AND the **first enrichment of an existing populator** — Categories 1-8 already populated `source_attribution` from prior wiring; Categories 9-10 extend the same agent's emission. The F-A2 referential-integrity validator works correctly on enrichment flows in addition to net-new flows.
- **First BLP-01 detection feature with no schema bump.** Decision 3 above records the asymmetry. F-3 demonstrates that Heuristic A enrichment correctly avoids spurious schema bumps when signal-class identity is preserved. The asymmetry is structurally important: the no-schema-bump invariant is the **operational signal** that Decision 1's signal-class identity claim is upheld.
- **Smallest BLP-01 detection delivery surface to date.** Zero new agent files, zero new skill directories, zero schema bumps, zero consumers-list edits, zero functional orchestrator edits. F-3 ships in ~1 working day per PRD §Timeline, demonstrating that enrichment can deliver a top-10 OWASP framework closure faster than new-agent paths (F-1 + F-2 each consumed ~2 days).
- **Zero regression on the 24-file detection tier.** ADR-023 stabilization + F-1 + F-2 extensions all hold. The 24 frozen detection-tier files (12 other agents + 12 other companions) remain byte-identical at F-3 merge. F-3 is an enrichment of an in-scope file, not a refactor or scope expansion.
- **SC-010 byte-identity preserved by construction.** The 5 non-multi-agent baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) do not qualify for the multi-agent / multi-MCP topology gate (FR-011 — no ≥2 agents on shared channel; no multi-hop MCP trust chain). All 5 baselines emit zero Category-9/10 findings → all 5 PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`.
- **Cohesive Agentic-category rendering on the regenerated example.** Categories 1-8 findings AND Categories 9-10 findings render adjacent in the same `category: agentic` section of `threats.md` and `threat-report.md`, with sequential `AG-{N}` IDs. No fragmentation across artificial sub-sections that would emerge if ASI07 were a new agent.
- **Zero new runtime or developer dependencies.** Empty diffs on all dependency manifests. `pyyaml` and `pytest` remain developer-only. Consistent with Features 128 / 180 / 189 / 194 / 201 / 206.
- **Determinism preserved.** No new orchestrator phase, no new LLM-judgment step, no new HTTP fetch. The agent's pattern matching is a pure function of the architecture input + the companion `detection-patterns.md` rules. ADR-021 byte-identity harness consumes no new knobs.

### Negative / risks

- **Categories 9 and 10 share trigger keywords with Categories 1-8.** The `tool-abuse` agent dispatches on existing trigger keywords (orchestrator, MCP server, tool server, plugin, agent); Categories 9-10 fire on the same dispatch but additionally require the multi-agent / multi-MCP topology gate. If the topology gate enforcement is loose, false positives could fire on single-agent architectures. **Mitigation**: anti-indicator subsections in Categories 9 + 10 (per Q4 architect plan-day default YES) explicitly enumerate the zero-emission conditions (single-agent topology → zero Cat-9; single-MCP topology → zero Cat-10). Wave 3 T040 backward-compat byte-identity test on 5 non-multi-agent baselines (BLOCKER per SC-010) catches any topology-gate leak by construction.
- **Pattern Category Disambiguation (Decision 7) requires prose precision.** Categories 6 and 10 both cite LLM03; the temporal (registry-time vs. invocation-time) and architectural-locus distinction must be clear to adopters reading the catalog. Loose prose could lead to merged findings or misinterpreted relationships. **Mitigation**: Decision 7 above provides the architectural rationale; the catalog Disambiguation subsection (FR-2) operationalizes it; code-reviewer R7 verification at Wave 4 T059 enforces boundary clarity. Anti-indicator subsections for Category 10 explicitly differentiate "MCP server registered without signature" (Cat 6) from "MCP-to-MCP relay without per-hop attestation" (Cat 10).
- **`agentic-app` regeneration may surface a clean inter-agent channel signal only after Feature 142.** F-3's Q3 default (extend `agentic-app`) relies on Feature 142's `Inter-agent Communication Channel` component type to provide a multi-agent topology in the regenerated example. If Wave 3 T032 confirmation reveals insufficient signal, Q3 fallback to `maestro-reference` or new minimal multi-agent fixture consumes 0.5 day of Buffer Day 1 capacity per PRD R1. **Mitigation**: T014 multi-agent topology dry-run validates `agentic-app` post-Feature-142 architecture pre-edit; T032 confirmation gate reviews actual signal.

### Neutral

- **No new `category` enum value.** F-3 reuses `category: agentic` (existing enum value — unchanged). Categories 9-10 findings flow through the same `category: agentic` code paths in downstream consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) — zero infrastructure-tier edits.
- **Schema 1.7 is unchanged.** Future BLP-01 enrichment features that follow F-3's branch (F-5 LLM10 via existing `denial-of-service` + `model-theft` agents) can cite this no-schema-bump precedent. Future new-agent features (F-4 ASI09 `trust-exploitation`) follow the regex-alternation minor-bump rule per ADR-030 Decision 8 + ADR-031 Decision 8.
- **F-3 ships solo or as the first of multiple parallel-eligible Tier 1 features in the 2026-04-28 → 2026-04-30 window** per agent-assignments.md §1 capacity check. R3 multi-feature concurrency hedge (Buffer Day 2 reserved) absorbs any F-4 / F-5 sequencing collisions; F-3 has the smallest edit surface and ships first to minimize rebase friction.
- **MAESTRO Layer 7 inheritance** per ADR-020 lineage. `AG-{N}` findings inherit L7 Agent Ecosystem layer via orchestrator Phase 1 keyword classification (existing Categories 1-8 already inherit L7). The agent does not author its own layer field; this is correct per ADR-020 Decision and ADR-023 Decision 2.
- **Forward-compatibility for F-4 `trust-exploitation`.** F-4 will be a separate AI-tier agent with its own ID prefix (e.g., `TE-{N}`) requiring a third Decision-8-style regex alternation addition (1.7 → 1.8). F-3 does not pre-design F-4 beyond the public roadmap forward-reference establishing ASI09 as a distinct signal class.

---

## Cross-References

- **ADR-021**: Determinism baseline (SOURCE_DATE_EPOCH). F-3's Wave 3 regeneration gate (T040) uses `SOURCE_DATE_EPOCH=1700000000` to verify 5-baseline byte-identity. The agent's pattern matching is deterministic (pure function of architecture input + pattern catalog); no new determinism knobs introduced.
- **ADR-023**: Lean-agent + additive-only shared-reference Decision 3. F-3 follows the additive-only edit discipline in its purest form per Decision 2 above. The 24-file zero-edit invariant (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2 host files; 24 unchanged) is preserved by construction. Decision 3 byte-identity enforcement on the existing `tool-abuse.md` and `detection-patterns.md` host files is the core architectural compliance signal at Wave 2 EOD T025.
- **ADR-027**: F-A1 taxonomy crosswalk (`schemas/taxonomy/owasp.yaml` ASI07 + LLM03 entries; `schemas/taxonomy/cwe.yaml` CWE-287 + CWE-345 entries; `schemas/taxonomy/mitre-atlas.yaml` AML.T0060 entry). F-3's `source_attribution` citations resolve against all 5 catalog anchors. F-3 is read-only against the F-A1 catalog; no edits to `schemas/taxonomy/`. ADR-027 Decision 3's 5-value taxonomy enum and Decision 5's closed-domain constraint both apply to F-3's attribution emissions.
- **ADR-028**: F-A2 `source_attribution` contract — F-3 is the **third net-new producer flow** of `source_attribution` data after F-1 (OI-{N}) + F-2 (MI-{N}), AND the **first enrichment of an existing populator** — Categories 1-8 already populate `source_attribution` from prior wiring; Categories 9-10 extend the same agent's emission. Every Category-9 finding carries `{taxonomy: owasp, id: ASI07, relationship: primary}` plus `{taxonomy: cwe, id: CWE-287, relationship: related}` plus optional `{taxonomy: atlas, id: AML.T0060, relationship: related}`. Every Category-10 finding carries `{taxonomy: owasp, id: ASI07, relationship: primary}` plus `{taxonomy: cwe, id: CWE-345, relationship: related}` plus optional `{taxonomy: owasp, id: LLM03, relationship: related}`. F-A2's referential-integrity validator at `scripts/tachi_parsers.py:826` enforces the contract on every emission.
- **ADR-030**: F-1 indirect precedent — **Decision 1 signal-class taxonomy in LLM tier** (input-side / downstream-execution-sanitization / factual-integrity / psychology-linguistics — three-way partition formalized at F-1; F-2 inherited the partition for factual-integrity). F-3 demonstrates the same signal-class discipline applied within the AG tier, in the **enrichment** mode rather than the new-agent mode. The cross-reference is **inheritance of the rule** (LLM-tier → AG-tier), not re-adjudication. Decision 1 above records the inheritance with explicit ADR-030 cross-reference.
- **ADR-031**: F-2 direct precedent — **Decision 8 regex-alternation minor-bump rule** (ADR-031 records F-2 as the second application — 1.6 → 1.7 adding `MI` prefix). **F-3 cross-references Decision 8 as the asymmetry**: F-3 is NOT an application of the rule. F-3 is the first BLP-01 detection feature with no schema bump because the existing `AG` prefix is already correct for the Heuristic A enrichment-branch signal class. Decision 3 above records the asymmetry with explicit ADR-031 Decision 8 cross-reference. The asymmetry is structurally important: it is the operational signal that Decision 1's signal-class identity claim is upheld.

### 24-file zero-edit invariant — grep-auditable enumeration

The T053 pre-merge grep audit verifies the following 24 files have zero diff against `main`:

**12 other AI/STRIDE threat-agent files** (all in `.claude/agents/tachi/`):

```
spoofing.md
tampering.md
repudiation.md
info-disclosure.md
denial-of-service.md
privilege-escalation.md
prompt-injection.md
data-poisoning.md
model-theft.md
agent-autonomy.md
output-integrity.md
misinformation.md
```

**12 companion `detection-patterns.md` files** (all under `.claude/skills/tachi-{name}/references/`):

```
tachi-spoofing/references/detection-patterns.md
tachi-tampering/references/detection-patterns.md
tachi-repudiation/references/detection-patterns.md
tachi-info-disclosure/references/detection-patterns.md
tachi-denial-of-service/references/detection-patterns.md
tachi-privilege-escalation/references/detection-patterns.md
tachi-prompt-injection/references/detection-patterns.md
tachi-data-poisoning/references/detection-patterns.md
tachi-model-theft/references/detection-patterns.md
tachi-agent-autonomy/references/detection-patterns.md
tachi-output-integrity/references/detection-patterns.md
tachi-misinformation/references/detection-patterns.md
```

The infrastructure-tier consumers (`risk-scorer.md`, `control-analyzer.md`, `threat-report.md`, `threat-infographic.md`, `report-assembler.md`), `orchestrator.md`, and `finding-format-shared.md` are also expected to show zero diff per spec FR-014 / FR-016 / FR-017 / SC-013 / SC-017. `dispatch-rules.md` shows zero functional diff (cosmetic Q2 single-token annotation if applied is documentation-only). `schemas/finding.yaml` shows zero diff per spec SC-014 / Decision 3.

---

## References

- Spec: [`specs/219-asi07-tool-abuse-enrichment/spec.md`](../../../specs/219-asi07-tool-abuse-enrichment/spec.md) — 3 user stories (US-219-1/2/3), 21 FRs, 21 SCs
- Plan: [`specs/219-asi07-tool-abuse-enrichment/plan.md`](../../../specs/219-asi07-tool-abuse-enrichment/plan.md) — 4-wave structure (1.0 / 1.1 / 2 / 3 / 4), Q1-Q5 architect decisions resolved, zero F-1/F-2 carry-over reconciliation
- Tasks: [`specs/219-asi07-tool-abuse-enrichment/tasks.md`](../../../specs/219-asi07-tool-abuse-enrichment/tasks.md) — 67 tasks across 9 phases, triple sign-off APPROVED 2026-04-25
- Wave 1.0 architect re-verification memo: [`.aod/results/wave1-architect-reverify.md`](../../../.aod/results/wave1-architect-reverify.md) — catalog citation re-verify + Heuristic A scope intact + line count + consumers list verification
- Wave 1.0 Q2 decision memo: [`.aod/results/wave1-q2-cosmetic-annotation-decision.md`](../../../.aod/results/wave1-q2-cosmetic-annotation-decision.md) — cosmetic dispatch-rules annotation YES per architect leaning
- Wave 1.0 Q3 decision memo: [`.aod/results/wave1-q3-example-target-decision.md`](../../../.aod/results/wave1-q3-example-target-decision.md) — example regeneration target = `agentic-app` extension per PM default
- PRD: [`docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md`](../../product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md)
- Schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) — schema_version "1.7" (UNCHANGED per Decision 3)
- F-A1 catalog YAMLs: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml) (ASI07, LLM03), [`schemas/taxonomy/cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) (CWE-287, CWE-345), [`schemas/taxonomy/mitre-atlas.yaml`](../../../schemas/taxonomy/mitre-atlas.yaml) (AML.T0060) — all read-only
- F-A2 parser + validator: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` + `validate_source_attribution` (unchanged; regex-agnostic — accepts any prefix matching `id.pattern`)
- Feature 082 (ADR-023 lean-agent stabilization): [`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`](ADR-023-threat-agent-skill-references-pattern.md)
- Feature 142 (multi-agent component types — `Inter-agent Communication Channel`): [`specs/142-maestro-phase-2/`](../../../specs/142-maestro-phase-2/) — establishes the multi-agent topology baseline that F-3 leverages in `agentic-app`
- Feature 201 (F-1 indirect precedent — first net-new AI-tier agent under ADR-023; new-agent branch of Heuristic A): [`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`](ADR-030-output-integrity-agent.md)
- Feature 206 (F-2 direct precedent — second net-new AI-tier agent; new-agent branch second-execution validation): [`docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`](ADR-031-misinformation-agent.md)

---

## Revision History

| Date | Status | SHA | Author | Note |
|------|--------|-----|--------|------|
| 2026-04-28 | Proposed | provisional | architect (Feature 219) | Initial proposal — Wave 1.1 unblock-gate commit. Records 7 numbered decisions covering the Heuristic A enrichment of `tool-abuse` for ASI07:2026 closure (D1 enrichment-vs-new-agent inheritance from ADR-030 Decision 1 within the AG tier; signal-class identity rationale with detection vocabulary / CWE mapping / mitigation taxonomy disjointness from a hypothetical new agent), additive-only edit discipline per ADR-023 Decision 3 in its purest form (D2 byte-identity proof on Categories 1-8 + Overview + DFD targets + Triggers regions of `detection-patterns.md`; pre-existing `## Purpose` prose preserved on `tool-abuse.md`), no schema bump (D3 first BLP-01 detection feature reusing existing `AG` prefix; cross-references ADR-031 Decision 8 as the **asymmetry** F-3 does NOT invoke), no consumers-list edit (D4 `tool-abuse` already at finding-format-shared.md:18), no functional orchestrator/dispatch edit (D5 cosmetic Q2 annotation per architect plan-day decision is documentation-only), public-only governance per SDR-001 Option C contract (D6 omits commercial framing and SDR-001 cross-reference), and Pattern Category Disambiguation Cat 6 vs Cat 10 non-overlap carve (D7 temporal locus distinction — registry-time supply chain vs. invocation-time trust propagation; co-emission contract for distinct architectural gaps). Heuristic A enrichment-branch first-execution narrative captured for F-6/F-7 Tier 2 ML+Mobile bundles. ADR-030 Decision 1 + ADR-031 Decision 8 cross-references explicit at Decisions 1 + 3. Authored at Day 1 Wave 1.1 after T003 catalog re-verification + T004/T005 plan-day decisions; serves as the unblock-gate signal that unblocks parallel Wave 2 authoring of Pattern Categories 9 + 10 + Disambiguation + Primary Sources extension. Status transitions to Accepted at Wave 4 T029 with provisional merge-date; post-merge SHA fill at T031 per Decision 6 dual-commit governance protocol. |
| 2026-04-25 | Accepted | `<pending-squash-sha>` | architect (Feature 219) | Initial Accepted (F-3 Wave 4) — ASI07 tool-abuse enrichment via Heuristic A; ADR-032 Decisions D1-D7 captured; cross-references ADR-021/023/027/028/030 D1/031 D8; 24-file zero-edit invariant verified; first BLP-01 detection feature with no schema bump (asymmetry to ADR-031 D8). |
