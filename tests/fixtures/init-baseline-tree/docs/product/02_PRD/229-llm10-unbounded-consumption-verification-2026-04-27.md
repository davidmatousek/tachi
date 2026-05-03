---
prd:
  number: 229
  topic: llm10-unbounded-consumption-verification
  created: 2026-04-27
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-27, status: APPROVED, notes: "PRD grounded in BLP-01 §7 F-5 spec and Issue #229; 3 user stories preserved with ACs rewritten to drop source_attribution claim per BLOCKING-1 narrow-scope resolution; 14 success criteria covering DoD bullets; v2 revisions address all 12 architect findings (2 BLOCKING / 3 HIGH / 4 MEDIUM / 3 LOW) and absorb team-lead 3 MEDIUM + 2 LOW inline; Q1 (context-window SPLIT), Q3 (Critical floor conditional), Q5 (agentic-app target) RESOLVED at PRD time; Q2 (cosmetic dispatch annotation) defers to architect plan-day. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-27, status: APPROVED_WITH_CONCERNS, notes: "v2 RE-REVIEW: 12/12 prior findings RESOLVED, 0 net-new. BLOCKING-1 narrow-scope path applied consistently across SC-13 / FR-8 / US-229-1 ACs / US-229-2 ACs (F-5 cites LLM10 in prose-level references array; F-A3 inheritance one-way). BLOCKING-2 6-baseline correction applied across SC-9 / FR-7 / Quality metrics / Maintainability / Dependencies / DoD bullet 11. HIGH-1 28-file detection-tier inventory grep-checkable. HIGH-2 hybrid heading structure acknowledged with line-range byte-identity verification (lines 1-83 / 84-155 / 156-179). HIGH-3 Q1 SPLIT cleanly executed (Cat 13 latency-DoS in denial-of-service / Cat 11 cost-DoW in model-theft) with 5-row mapping table in ADR-034 Decision 3. All 4 MEDIUM and 3 LOW resolved. Q2 architect-tractable at plan time (default-NO documented; YES recommended in v1 architect-call). Final counts: BLOCKING/HIGH/MEDIUM/LOW: 0/0/0/0. Full review: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-27, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 2 LOW. Calendar verified (cal 4 2026 confirms 04-27 Mon / 04-28 Tue / 04-29 Wed / 04-30 Thu). All 7 dependencies (F-A1, F-A2, F-B, F-1, F-2, F-3, F-4) verify SATISFIED at PRD time; ADR-034 next-available verified. F-5 surface 1.5-day envelope realistic vs F-3 (1d single-agent) and F-2 (2d new-agent) anchors; 2x pattern-authoring surface vs F-3 with no schema/dispatch overhead. MEDIUM-1 Day 1 PM back-load: addressed via Day 1 split rebalance (ADR-034 mapping table populated complete at Day 1 AM; byte-identity spot-check pulled forward to Day 1 PM end). MEDIUM-2 tester role for SC-9: addressed via explicit assignment in milestone table + DoD bullet 11. MEDIUM-3 buffer-day priority order: addressed via numbered priority list in Timeline section. LOW-1 R8 closing-milestone over-attribution + LOW-2 ADR-034 SHA-fill DoD bullet 16: both added inline. Ready for /aod.plan. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 229
  story_id: null
---

# F-5 — LLM10 Unbounded Consumption Verification: Product Requirements Document

**Status**: Draft v2 (revised post-architect-CHANGES_REQUESTED)
**Created**: 2026-04-27
**Spec**: TBD (will land at `specs/229-llm10-unbounded-consumption-verification/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 1 — fifth Tier 1 feature (LLM10 closure feature; follows F-1, F-2, F-3, F-4)
**Priority**: P1

**Revision note (2026-04-27 v2)**: Addresses architect BLOCKING-1 (`source_attribution` wiring is NOT pre-existing on `denial-of-service` / `model-theft` — narrow scope chosen: F-5 cites LLM10 in the prose-level `references` array only and does NOT extend `source_attribution` populator wiring; F-A3 inheritance is one-way and F-5 does not block on F-A3), BLOCKING-2 (baseline count is 6, not 5 — `maestro-reference` added to enumeration; SC-9 / FR-7 / Quality metrics updated to "6 of 7 example baselines"), HIGH-1 (file-count invariant re-anchored to 28 detection-tier files; 24-file zero-edit invariant on the 24 non-target files), HIGH-2 (SC-4 reworded to acknowledge hybrid heading structure of `denial-of-service/detection-patterns.md` — 8 thematic groups + Cat 9/10/11 + Primary Sources, no `## Trigger Keywords` section), HIGH-3 (Q1 RESOLVED at PRD time: SPLIT — context-window-exhaustion lives in BOTH agents along the latency-DoS [Cat 13] vs. cost-DoW [Cat 11] axis); plus all 4 MEDIUM and 3 LOW architect findings; plus team-lead 3 MEDIUM (Day 1 split rebalanced — ADR-034 mapping table populated [not skeleton] at Day 1 AM; tester role for SC-9 explicitly assigned; buffer-day priority order enumerated) and 2 LOW (R8 closing-milestone over-attribution risk added; ADR-034 SHA-fill DoD bullet added) absorbed inline. Repository slug `229-llm10-unbounded-consumption-verification` preserved per `.claude/rules/git-workflow.md` `NNN-descriptive-name` convention.

---

## 📋 Executive Summary

### The One-Liner

Audit the existing `denial-of-service` and `model-theft` agents against the full OWASP LLM10:2025 Unbounded Consumption surface (inference-request flooding, token-budget exhaustion, context-window exhaustion, cost amplification via recursive prompts, denial-of-wallet) and **enrich both companion `detection-patterns.md` files** with new Pattern Categories that close every missing sub-pattern — transitioning LLM10 **Partial → Covered** with **no new agent**, **no schema bump**, **no consumers-list edit**, and **no orchestrator dispatch edit**. F-5 is the **second execution of the Heuristic A enrichment branch** (after F-3) and the **first BLP-01 enrichment feature scoped to two host agents simultaneously**.

### Problem Statement

Tachi ships 14 detection agents post-F-4 (12 original + `output-integrity` from F-1 + `misinformation` from F-2 + `human-trust-exploitation` from F-4; F-3 enriched `tool-abuse` without adding a new file). Coverage of OWASP's two AI-tier top-10 frameworks now stands at 19 of 20 entries closed: **OWASP Agentic Top 10:2026 is 10 of 10 Covered** (closed by F-4 carving up ASI09 between `agent-autonomy` autonomy axis and `human-trust-exploitation` communication axis), and **OWASP LLM Top 10:2025 is 9 of 10 Covered** (LLM01–LLM09 closed; LLM05 via Feature 201, LLM09 via Feature 206). The remaining gap is **LLM10:2025 Unbounded Consumption** — currently the **only AI-tier top-10 entry not Covered**, listed as **Partial** on the BLP-01 Coverage Matrix because two existing agents (`denial-of-service` STRIDE-tier and `model-theft` AI-tier) carry partial signal on the surface but neither agent has been audited against the full LLM10 sub-pattern taxonomy and neither has explicit LLM10-named pattern categories.

**Scope clarification — `source_attribution` populator wiring**: PRD-time grep confirms that neither `denial-of-service.md` nor `model-theft.md` currently emit `source_attribution` (the `D-{N}` and `LLM-{N}` prefix populators were deferred to F-A3 per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6 — F-A2 shipped only the data-shape contract). F-5 deliberately does **not** extend populator wiring on the host agents; LLM10 citations on every emitted Cat-12/13 (`D-{N}`) and Cat-10/11 (`LLM-{N}`) finding live in the prose-level `references:` array (an existing field present in the finding YAML schema since v1.0). When F-A3 ships, the LLM10 citations established by F-5 will flow into `source_attribution` naturally because the catalog references are already correct. **F-A3 dependency direction is one-way (F-5 → F-A3 inheritance); F-5 does not require F-A3 to ship and does not block on it.**

A security analyst threat-modeling an LLM-serving application today (consumer chatbot, RAG advisory assistant, agentic orchestrator with LLM-backed worker agents, multi-tenant LLM API gateway, LLM-fronted SaaS) gets **incomplete signal from tachi** on the LLM10 surface. The `denial-of-service` agent flags generic infrastructure resource exhaustion (Categories 1–11 cover web-app DoS, algorithmic complexity, network flooding, cascade failures) but does not name LLM-specific patterns: **inference-request flooding** (unbounded queries-per-second on inference endpoints), **token-budget exhaustion** (unbounded prompt-size leading to compute saturation), or **context-window exhaustion** (adversarial prompt expansion that drives latency to per-request timeout). The `model-theft` agent flags general unbounded inference at Category 6 ("Unbounded Inference Consumption" — covers per-tenant quotas, cost controls, anomaly monitoring, free-tier abuse, billing attribution) but does not name **cost amplification via recursive or cost-asymmetric prompting** (e.g., a 10-token prompt that triggers a 32k-token response, or a chain-of-thought query that recursively self-amplifies output) or **denial-of-wallet** (the SaaS-LLM-specific attack class where an attacker drives the operator's inference bill to ruin without degrading availability for other tenants).

Per **Heuristic A (signal-class taxonomy)** in `GUIDE-threat-coverage-research §11`, LLM10 sub-patterns split into two same-class buckets: **infrastructure-resource-exhaustion** patterns (inference-request flooding, token-flooding, context-window-exhaustion as DoS) are same-class as `denial-of-service`'s availability-degradation surface; **extraction-driven-resource-abuse** patterns (cost amplification, denial-of-wallet) are same-class as `model-theft`'s unbounded-inference-consumption surface (already at Category 6). Authoring a new `unbounded-consumption` agent would fragment LLM10 findings across three places (the new agent + DoS-side adjacency + model-theft-side adjacency); enrichment of the two existing host agents preserves the signal-class consolidation per Heuristic A and matches the rule SDR-001 Decision 4 locked. F-3's first execution of the enrichment branch validated the pattern at single-agent scope (`tool-abuse` for ASI07); F-5 is the **second execution** and the **first at two-agent scope** — establishing the pattern's stability under the two-execution-deep validation gate that F-2 retrospective KB-037 codified for new-agent shape and that now extends to enrichment shape.

### Proposed Solution

Apply **ADR-023 Decision 3 (additive-only edit discipline)** to enrich both `denial-of-service` and `model-theft` agents and their companion `detection-patterns.md` files with new Pattern Categories that exhaust the LLM10 sub-pattern surface. Net change is **purely additive** to four existing files plus one new ADR — no new agent file, no new skill directory, no schema bump, no orchestrator dispatch table edits, no `finding-format-shared.md` consumers list edit. The audit deliverable embedded in **ADR-034** is the **canonical mapping table** assigning every LLM10 sub-pattern to **exactly one owning agent** to prevent duplicate detection.

1. **`.claude/agents/tachi/denial-of-service.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP LLM10:2025 — Unbounded Consumption`. Verified at PRD time: line 17 enumerates 9 entries (`OWASP A04:2021`, `OWASP DoS Cheat Sheet`, `OWASP API4:2023`, `CWE-400`, `CWE-770`, `CWE-1333`, `CWE-502`, `MITRE ATT&CK T1498`, `MITRE ATT&CK T1499`); LLM10 absent — F-5 adds it as the 10th entry.
   - `## Purpose` paragraph extended with 1–3 lines naming the LLM-inference-exhaustion surface (inference-request flooding on LLM endpoints, token-budget exhaustion via unbounded prompt-size) alongside the existing infrastructure-availability surface.
   - Detection Workflow Step 5 references list extended with `OWASP LLM10:2025`.
   - Agent file remains **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baseline: **53 lines**. Expected post-edit: 56–60 lines (well within margin).

2. **`.claude/skills/tachi-denial-of-service/references/detection-patterns.md`** — append two new Pattern Category sections after existing **Pattern Category 11 "Cascade Failures and Noisy Neighbor in Microservice Architectures"** (file currently ends at line 179 with hybrid heading structure: 8 thematic sections covering Cat 1–8 conceptual groupings + 3 named `## Pattern Category N:` headings at Cat 9/10/11 + Primary Sources). Existing content byte-identical pre/post edit per ADR-023 Decision 3. Per Q1 SPLIT resolution at PRD time, context-window-exhaustion lives in BOTH agents — the latency-DoS variant (Vector A) lives here as Cat 13:
   - **Pattern Category 12: LLM Inference-Request Flooding and Token Exhaustion** — covers unbounded queries-per-second on inference endpoints, absent per-tenant rate limits at the LLM-API gateway, unbounded prompt-size accepted at request ingestion, missing token-budget enforcement per request. Indicators ≥4. Primary sources: `OWASP LLM10:2025` (primary), `CWE-400` (related — already in agent's owasp_references), `CWE-770` (related — already in agent's owasp_references). Mitigations: per-tenant queries-per-second rate limit, prompt-size cap at API gateway, token-budget per request, request-timeout enforcement.
   - **Pattern Category 13: Context-Window Exhaustion — Latency-Driven Variant** — covers Vector A of context-window exhaustion (Q1 SPLIT resolution): attacker drives context-window to model max, legitimate users see degraded p99 latency, attacker intent is **availability disruption**. Same signal class as Cat 12 (per-request resource exhaustion via latency tail). Indicators ≥4. Primary sources: `OWASP LLM10:2025` (primary), `CWE-400` (related). Mitigations: max-context-window enforcement at API gateway, context-window monitoring with anomaly alerting, per-tenant context-window cap. **The cost-amplification variant of context-window exhaustion (Vector B — economic damage) lives in `model-theft` Cat 11** per Q1 SPLIT — see solution item 4 below. The audit table in ADR-034 Decision 3 explicitly maps both vectors to disjoint owning categories.

3. **`.claude/agents/tachi/model-theft.md`** — additive metadata audit + Purpose extension:
   - `owasp_references` list **already includes `OWASP LLM10:2025`** (verified at PRD time: line 17 reads `[OWASP LLM10:2025, OWASP LLM03:2025]`). F-5 metadata edit on this agent is a **no-op** for the references list — the audit confirms completeness rather than extending. (Asymmetric to denial-of-service: that agent's metadata edit is a one-line append; model-theft's metadata edit is zero net change.)
   - `## Purpose` paragraph extended with 1–3 lines naming the cost-amplification and denial-of-wallet surface alongside the existing model-extraction surface.
   - Agent file remains **≤150 lines** per ADR-023 AI-tier cap. PRD-time baseline: **95 lines**. Expected post-edit: 98–102 lines.

4. **`.claude/skills/tachi-model-theft/references/detection-patterns.md`** — append two new Pattern Category sections after existing **Pattern Category 9 "System Prompt and Configuration Leakage (OWASP LLM07:2025)"** (file currently ends at line 154; Categories 1–9 byte-identical pre/post edit per ADR-023 Decision 3). Per Q1 SPLIT resolution at PRD time, context-window exhaustion's cost-amplification variant (Vector B) lives in this companion as Cat 11:
   - **Pattern Category 10: Cost Amplification via Recursive or Cost-Asymmetric Prompting** — covers the attack class where a small input drives a disproportionately large output (e.g., 10-token prompt → 32k-token response), or where chain-of-thought / recursive prompting self-amplifies output across calls. Indicators ≥4. Primary sources: `OWASP LLM10:2025` (primary), `OWASP LLM03:2025` (related — already in agent's owasp_references for the supply-chain-trust adjacency). Mitigations: per-query output-token cap, per-tenant cost-per-query p99 alerting, recursive-prompt depth limit, output-amplification-ratio monitoring.
   - **Pattern Category 11: Denial-of-Wallet via Context-Window Cost Amplification** — covers Vector B of context-window exhaustion (Q1 SPLIT resolution) plus the broader denial-of-wallet attack class: attacker drives context-window to maximum to inflate per-call cost (the "wallet" is the bill, not the system uptime); attacker intent is **economic damage**. Same signal class as Cat 10 cost-amplification (extraction-driven resource abuse). The mitigation surface — per-tenant token budget hard-cap — is a 1:1 control with denial-of-wallet. Indicators ≥4. Primary sources: `OWASP LLM10:2025` (primary), `OWASP LLM03:2025` (related — supply-chain-trust adjacency for cost-flow-through-third-party-models). Mitigations: per-tenant token budget with hard cap, cost-per-query p99 alerting, denial-of-wallet anomaly detection (cost-velocity monitoring), automated tenant suspension on budget breach. **MITRE ATT&CK T1496 Resource Hijacking** named in the Mitigations narrative as the cost-amplification cross-reference (text-only — T1496 is not catalog-resolvable per PRD-time check of `schemas/taxonomy/mitre-attack.yaml`, so it does NOT appear as a structured citation).

5. **`docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md`** — public per-feature ADR documenting (a) the **canonical LLM10 sub-pattern → owning-agent mapping table** (the audit deliverable that prevents duplicate detection), (b) the Heuristic A enrichment-branch consolidation rationale at two-agent scope (vs. F-3's single-agent scope), (c) the additive-only edit discipline conformance per ADR-023 Decision 3, (d) the explicit non-creation of a new `unbounded-consumption` agent and the rationale, (e) the no-schema-bump asymmetry to F-1/F-2/F-4 and structural symmetry with F-3 (ADR-032), (f) zero-MAESTRO-reference invariant proof on the four enriched files. Authored under the Proposed → Accepted dual-commit pattern that ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 / ADR-032 / ADR-033 established as the BLP-01 default protocol. ADR-034 is the next-available number (verified at PRD time: ADR-033 is the highest committed ADR).

6. **Example regeneration** on a multi-agent / LLM-serving example architecture — Q5 RESOLVED at PRD time per architect adjudication: **`examples/agentic-app/` confirmed as Q5 target.** No new architecture authoring needed; mutation candidate is multi-component LLM topology already exercised by F-3. ADR-034 includes a Detection Calibration Note clarifying that the new Pattern Categories 12/13 (denial-of-service) and 10/11 (model-theft) fire on **structural absence** of named control mechanisms — consistent with F-1 / F-2 / F-4 absence-style detection style. Acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention. At least 1 new finding produced from each enriched agent (≥1 `D-{N}` from `denial-of-service` Cat 12/13 + ≥1 `LLM-{N}` from `model-theft` Cat 10/11), demonstrating regression-style proof that both enrichments fire on a real architecture.

The two enriched agents activate **as they do today** when DFD elements match their existing trigger keywords (denial-of-service: Process / Data Store / Data Flow with availability-relevant keywords; model-theft: LLM-keyword-matched Process). The new Pattern Categories fire when the architecture additionally exhibits **LLM-serving indicators** (e.g., declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology). When no LLM-serving topology is present, the new Categories emit **zero findings** — the existing emission-gate discipline of both agents is preserved (denial-of-service Categories 1–11 fire on generic infrastructure DoS as they do today; model-theft Categories 1–9 fire on generic model-theft as they do today).

**Three things the solution is deliberately NOT:**

1. It is **not** a new agent. LLM10's signal class splits into two existing same-class buckets per Heuristic A: infrastructure-resource-exhaustion (in `denial-of-service`) and extraction-driven-resource-abuse (in `model-theft`). Authoring a hypothetical `unbounded-consumption` agent would fragment LLM10 findings across three locations (the new agent + DoS adjacency + model-theft adjacency), violating Heuristic A consolidation. SDR-001 Decision 4 locked this rule; F-3 ADR-032 demonstrated that the enrichment branch produces a working delivery; F-5 is the second execution and cannot ship as a new agent without re-opening Heuristic A on every prior consolidation (LLM05 → output-integrity, LLM09 → misinformation, ASI07 → tool-abuse enrichment, ASI09 → human-trust-exploitation + agent-autonomy carve-up).
2. It is **not** a new finding ID prefix. Findings emit on the existing `D-{N}` (denial-of-service) and `LLM-{N}` (model-theft) ID schemes — both prefixes already exist in `schemas/finding.yaml` `id.pattern` regex (verified at PRD time: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$`, 12 alternation values post-F-4). **No schema bump** — `finding.yaml` stays at v1.8 (the post-F-4 baseline). F-5 is the **second BLP-01 detection feature with no schema bump** (after F-3) and the **first to skip the bump on a two-agent enrichment**. ADR-032 lines 84 and 182 explicitly forecast this outcome — "F-5 will not need a schema bump because the host agents' D-{N} and LLM-{N} prefixes already exist." (Note: ADR-032's "Schema 1.7 unchanged" forecast applied at its writing-time (pre-F-4); F-5 holds the baseline at 1.8 (post-F-4) without invoking the regex-alternation rule. Substantively the no-bump claim survives — no new ID prefix is needed because `D-{N}` and `LLM-{N}` are already in the schema 1.8 alternation.)
3. It is **not** an orchestrator-dispatch change. Both `denial-of-service` and `model-theft` are already fully registered in `dispatch-rules.md` (line 73: `model-theft (OWASP LLM10:2025)`; line 109: `LLM agents dispatched (...model-theft...)`; line 157: `LLM Threats | ...model-theft...`) and `orchestrator.md` (lines 37 and 42 declare both agent files in the agents inventory; lines 298 and 372 enumerate them in the dispatch tables). The existing dispatch paths invoke both agents for every applicable component without modification. **No `finding-format-shared.md` consumers list edit is needed** — both agents are verified present (line 12: `denial-of-service`; line 16: `model-theft`). **No functional orchestrator/dispatch-rules edit is needed** — the OWASP refs metadata extension on `denial-of-service.md` is sufficient. Q2 architect-tractable at plan time: a cosmetic one-token annotation update to `dispatch-rules.md` (extending `denial-of-service (CWE-400)` to `denial-of-service (CWE-400, LLM10)` for parity with the model-theft dispatch annotation that already cites `LLM10:2025`) is **default-NO** but architect-tractable. **F-5 is the second BLP-01 detection feature with zero functional orchestrator-tier touches** (after F-3).

### Success Criteria

- **SC-1** — `.claude/agents/tachi/denial-of-service.md` `owasp_references` list extended to include `OWASP LLM10:2025 — Unbounded Consumption`; existing 9 entries preserved byte-identically (grep-checkable). Agent file line count remains **≤120 lines** (STRIDE tier cap per ADR-023). PRD-time baseline: 53 lines; expected post-edit count: 56–60 lines.
- **SC-2** — `.claude/agents/tachi/denial-of-service.md` `## Purpose` section gains a 1–3 line extension naming the LLM-inference-exhaustion surface (inference-request flooding, token-budget exhaustion, **context-window-exhaustion latency-driven variant** — the availability-degradation half of context-window exhaustion per Q1 SPLIT resolution). Pre-existing `## Purpose` prose remains byte-identical (additive, not a rewrite).
- **SC-3** — `.claude/agents/tachi/model-theft.md` `## Purpose` section gains a 1–3 line extension naming the cost-amplification and denial-of-wallet surface. Pre-existing `## Purpose` prose remains byte-identical. Agent file line count remains **≤150 lines** (AI tier cap per ADR-023). PRD-time baseline: 95 lines; expected post-edit count: 98–102 lines. **Note**: `owasp_references` on this agent already includes `OWASP LLM10:2025` (verified at PRD time) — F-5's audit confirms completeness; no metadata extension needed.
- **SC-4** — `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` (179 lines pre-edit) gains **Pattern Category 12** ("LLM Inference-Request Flooding and Token Exhaustion") and **Pattern Category 13** ("Context-Window Exhaustion — Latency-Driven Variant") appended after existing Pattern Category 11 (line 132 region). Existing content preserved byte-identically per ADR-023 D3: lines 1–83 (`## Overview`, `## Targeted DFD Element Types`, and 8 thematic sections — `## Resource Exhaustion`, `## Algorithmic Complexity Attacks`, `## Database and Storage Saturation`, `## Connection and Pool Exhaustion`, `## Dependency and Cascade Failures`, `## Application-Layer Attacks`, `## Infrastructure-Layer Attacks`, `## Flooding and Abuse`); lines 84–155 (`## Pattern Category 9`, `## Pattern Category 10`, `## Pattern Category 11` with their worked examples and Mitigations); `## Primary Sources` section (line 156–179) is additively extended with `OWASP LLM10:2025` entry per FR-5 (additive append within existing section). Note: this companion does NOT have a `## Trigger Keywords` section (asymmetric to the model-theft companion at line 19) — Trigger Keywords claim does not apply here. Verification: `grep -n '^## ' detection-patterns.md` returns the same 12 H2 sections plus 2 new ones post-edit. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one primary-source citation (`OWASP LLM10:2025` minimum), (d) named LLM-specific mitigations distinct from generic infrastructure rate limits. Architect may at plan time merge Cat 12+13 into a single category if the indicator surface justifies (Q4 architect-tractable; minimum floor is 1 new category per Issue #229 DoD bullet).
- **SC-5** — `.claude/skills/tachi-model-theft/references/detection-patterns.md` (154 lines pre-edit) gains **Pattern Category 10** ("Cost Amplification via Recursive or Cost-Asymmetric Prompting") and **Pattern Category 11** ("Denial-of-Wallet via Context-Window Cost Amplification") appended after existing Cat 9. Existing Pattern Categories 1–9 (with their `## Pattern Category N:` headings) plus `## Overview` / `## Targeted DFD Element Types` / `## Trigger Keywords` (line 19) sections preserved byte-identically. Primary Sources section additively extended with OWASP LLM10:2025. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one primary-source citation (`OWASP LLM10:2025` minimum), (d) named LLM-specific cost-control mitigations. Architect may merge into single category at plan time per Q4.
- **SC-6** — Primary Sources lists in both companion files extended with `OWASP LLM10:2025 — Unbounded Consumption`. Existing Primary Sources entries preserved byte-identically. (Note: `model-theft` companion's existing Primary Sources may already cite LLM10 in some adjacency; PRD-time verification at plan time per architect.)
- **SC-7** — Public per-feature **ADR-034** (next-available number, verified at PRD time: ADR-033 is highest committed) committed under `docs/architecture/02_ADRs/` documenting (a) the **canonical LLM10 sub-pattern → owning-agent mapping table** as the audit deliverable, (b) the Heuristic A enrichment-branch consolidation at two-agent scope, (c) the additive-only edit discipline conformance, (d) the explicit non-creation of a new `unbounded-consumption` agent, (e) the no-schema-bump asymmetry to F-1/F-2/F-4 and structural symmetry with F-3 (ADR-032), (f) zero-MAESTRO-reference invariant proof on the four enriched files, (g) cross-references to ADR-030 Decision 1 (Heuristic A signal-class taxonomy in LLM tier), ADR-032 (first enrichment-branch execution), ADR-033 (F-4 sub-scope carve-up). Authored under the Proposed → Accepted dual-commit pattern.
- **SC-8** — Agent invocation on the chosen LLM-serving example architecture (Q5 default `examples/agentic-app/`) produces **at least 1 new `D-{N}` finding** (from `denial-of-service` Pattern Category 12 or 13) AND **at least 1 new `LLM-{N}` finding** (from `model-theft` Pattern Category 10 or 11), each citing `OWASP LLM10:2025` as primary in `source_attribution`. Architect adjudicates the final example target at plan time (Q5).
- **SC-9** — All **6 non-LLM-serving example PDFs** regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The 6 baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, **`maestro-reference`**. Zero-impact-when-absent invariant: those baselines do not exhibit LLM-serving topologies (no inference endpoint, no token-counting middleware, no cost-attribution layer), so Categories 12/13 (denial-of-service) and 10/11 (model-theft) emit zero findings, so all downstream artifacts are unchanged. **`agentic-app`** is the F-5 mutation candidate per SC-8 (no `.baseline` file by design — the F-3 / F-5 mutation target). `consumer-agent-app` is F-4's mutation target without a `.baseline` file and is untouched by F-5. **Owner**: SC-9 byte-identity verification (6 baseline regen + grep checks) is explicitly assigned to the `tester` agent (separate from `senior-backend-engineer` who authors the edits) — mirrors F-3 / F-4 precedent.
- **SC-10** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared.
- **SC-11** — **Schema invariant preserved** — `schemas/finding.yaml` `schema_version` remains **`"1.8"`** (PRD-time verified post-F-4 baseline). `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` — no new prefix; `D` and `LLM` already enumerated. **F-5 is the second BLP-01 detection feature with no schema bump** (after F-3) and the first at two-agent enrichment scope. This outcome was explicitly forecast by ADR-032 lines 84 and 182.
- **SC-12** — **24-file zero-edit invariant preserved on every detection-tier file other than the four F-5 enrichment targets**. Detection-tier inventory post-F-4: **28 files** (22 original detection-tier files at ADR-023 baseline + F-1's 2 new files + F-2's 2 new files + F-3's 0 net new (enrichment branch — modifies existing, adds none) + F-4's 2 new files = 26 plus F-3's enrichment-modified targets remain in-set, totaling 28 detection-tier files). F-5 follows F-3's enrichment branch — modifies 4 of those 28 files (2 host agents + 2 companions), adds 0 new files. Post-F-5 inventory remains 28. The **24-file zero-edit invariant** applies to the 24 non-target detection-tier files (28 total − 4 F-5 targets = 24). Plan-day verification: architect runs grep-checked count and reconciles against this PRD baseline. (Note: CLAUDE.md F-4 entry says "26-file inventory" which is the pre-F-4-merge count; post-merge is 28.) F-5's edits are scoped to **4 files** (`denial-of-service.md` + its companion + `model-theft.md` + its companion); every other detection-tier file remains byte-identical (grep-checkable). **No `finding-format-shared.md` consumers list edit is needed** — both target agents verified present (PRD-time grep at lines 12 and 16). **No functional orchestrator/dispatch-rules edit is needed** — both agents fully registered (PRD-time verified across multiple callsites in `orchestrator.md` lines 37/42/298/372 and `dispatch-rules.md` lines 73/109/157). **Annotation carve-out**: a cosmetic one-token annotation update to `dispatch-rules.md` (extending `denial-of-service (CWE-400)` to `denial-of-service (CWE-400, LLM10)` for cosmetic parity) is permitted contingent on architect adjudication of Q2 at plan time — documentation-only, no functional dispatch change. **F-5 is the first BLP-01 detection feature with two-agent enrichment scope.**
- **SC-13** — Every emitted Cat-12/13 finding (denial-of-service) and Cat-10/11 finding (model-theft) carries OWASP LLM10:2025 in its prose-level `references:` array (existing field; verified present in finding YAML schema since v1.0). Each new `D-{N}` finding's `references` array includes `OWASP LLM10:2025`, `CWE-400 Uncontrolled Resource Consumption`, and where applicable `CWE-770 Allocation of Resources Without Limits or Throttling` (both CWEs verified present in `schemas/taxonomy/cwe.yaml` lines 130 and 182). Each new `LLM-{N}` finding's `references` array includes `OWASP LLM10:2025`, and where applicable `OWASP LLM03:2025` for the cost-flow-through-third-party-models adjacency. F-5 does **NOT** extend `source_attribution` populator wiring on the host agents — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6: "F-A2 ships the data-shape contract only. Populator wiring inside the 11 threat-detection agents is deferred to F-A3 under the 22-file zero-edit invariant per ADR-023 / ADR-028 Decision 6"). When F-A3 ships, the LLM10 citations established by F-5 will flow into `source_attribution` naturally because the catalog references are already correct. **F-A3 dependency direction is one-way (F-5 → F-A3 inheritance); F-5 does not require F-A3 to ship and does not block on it.** **MITRE ATT&CK T1496 Resource Hijacking** is named in finding `mitigation` narratives as a cost-amplification cross-reference but does NOT appear in `references` as a structured citation because T1496 is not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` (PRD-time verified absent).
- **SC-14** — **Coverage Matrix transition**: BLP-01 `_internal/strategy/BLP-01-threat-coverage.md` line 278 LLM10:2025 row transitions **Partial → Covered** with F-5 (Feature 229) named as the closure feature. Coverage milestones panel (currently lines 6 and 139) updates to reflect **OWASP LLM Top 10:2025 = 10 of 10 Covered**. Combined with the post-F-4 OWASP Agentic Top 10:2026 = 10 of 10 Covered milestone, post-F-5 tachi covers **20 of 20 OWASP AI top-10 entries** — a strategic milestone marker that pairs cleanly with the BLP-01 8/11 features delivered count.

### Timeline

Target window: **2026-04-28 (Tuesday) → 2026-04-29 (Wednesday)** with **2026-04-30 (Thursday) buffer**. Calendar verified at PRD time (`cal 4 2026`): 2026-04-25 = Saturday, 2026-04-27 = Monday (today, PRD day), 2026-04-28 = Tuesday (plan day per Tuesday-after-Monday-PRD cadence), 2026-04-29 = Wednesday (build day), 2026-04-30 = Thursday (buffer day). F-5 plan day is Tuesday 2026-04-28 to allow Monday PRD review and Triad sign-offs to settle; build day starts Wednesday 2026-04-29.

**Single-envelope sizing** — F-5 is **slightly larger than F-3, smaller than F-2** because:
- No new agent file (only additive edits to existing — like F-3).
- No new skill directory (only additive edits to existing companions — like F-3).
- No schema bump (no new ID prefix — like F-3, asymmetric to F-1/F-2/F-4).
- No `finding-format-shared.md` edit (both target agents already in consumers list — like F-3).
- No orchestrator/dispatch-rules edit (both agents already fully registered — like F-3).
- **Two host agents** vs. F-3's single host (slightly more pattern-authoring surface).
- **4 new Pattern Categories** total across two files vs. F-3's 2 categories on one file (twice the authoring surface).
- ADR-034 contains the **canonical sub-pattern mapping table** — slightly more ADR-content scope than F-3's ADR-032.
- Heuristic A enrichment-branch is two-execution-deep validated post-F-3; F-5 doesn't re-adjudicate the rule, only operationalizes it at two-agent scope.

- **Realistic envelope**: **1.5 working days**, 1 day aspirational, 2 days conservative. Per team-lead MEDIUM-1 rebalance — Day 1 PM is no longer back-loaded with ADR-034 mapping-table population (which can land final at Day 1 AM since Q1/Q3 are resolved at PRD time, not deferred to plan day). Build effort sits between F-3's 1 working day (single-agent enrichment) and F-2's 2 working days (full new-agent shape).
- **Buffer**: 2026-04-30 Thursday absorbs regeneration friction, ADR-034 Accepted transition, and any slip from Day 1. No second buffer day required because no F-6/F-7 build is in window (Tier 2 features deferred).

**Rebalanced Day 1 / Day 2 split (per team-lead MEDIUM-1)**:

- **Day 1 (Wed 2026-04-29) AM**: FR-1 + FR-2 (`denial-of-service.md` + companion: 2 new pattern categories Cat 12 + Cat 13) + **ADR-034 Proposed commit with mapping table populated** (NOT skeleton — Q1/Q3 resolved at PRD time so Day 1 AM lands final mapping table including 5-row sub-pattern → owning-category map plus severity-hint annotation column).
- **Day 1 (Wed 2026-04-29) PM**: FR-3 + FR-4 (`model-theft.md` + companion: 2 new pattern categories Cat 10 + Cat 11) + `examples/agentic-app/` regen (FR-7) + **early-signal byte-identity spot-check on 1–2 baselines** (e.g., `web-app` + `maestro-reference`) — pulls verification gate forward to catch regen surprises before Day 2.
- **Day 2 (Thu 2026-04-30) AM**: Byte-identity verification on remaining 4 baselines (`microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) — owned by `tester` agent per team-lead MEDIUM-2; ADR-034 Accepted transition; PR title pre-merge verification per Release Discipline subsection.
- **Day 2 (Thu 2026-04-30) PM**: PR ready (`gh pr ready`), squash-merge, post-merge release-please verification, delivery retrospective.

**Buffer-day priority order (Thursday 2026-04-30, per team-lead MEDIUM-3)**:

1. **Day 1 slip absorption** (any in-flight contingency from R1–R7).
2. **Delivery retrospective** filed at `specs/229-llm10-unbounded-consumption-verification/delivery.md`.
3. **Post-merge ADR-034 SHA fill + `/aod.deliver` execution + release-please PR verification** (per CLAUDE.md F-212 incident protocol; ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 / ADR-032 / ADR-033 dual-commit precedent).
4. **F-6 PRD drafting NOT until F-5 deliver-stage closes** (Constraint Analysis on R10 from F-3 / F-4 precedent — closing-stage focus on F-5 retrospective and SHA fill before opening F-6 scope).

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's vision — automated threat modeling extending STRIDE with AI-specific threat agents for LLM-serving and agentic applications — implies *complete* coverage of every named OWASP AI-tier top-10 entry, not just structural coverage. F-1 / F-2 closed the LLM output-sanitization (LLM05) and factual-integrity (LLM09) surfaces with new agents; F-3 closed the inter-agent communication (ASI07) surface via enrichment of `tool-abuse`; F-4 closed the human-trust communication axis (ASI09) via a new `human-trust-exploitation` agent and an autonomy/communication carve-up with `agent-autonomy`. **F-5 closes the last remaining LLM-tier gap: LLM10 Unbounded Consumption.** Post-F-5, the answer to an adopter's question "does tachi cover the *full* OWASP LLM Top 10 and Agentic Top 10 surfaces?" is unambiguously **yes — 20 of 20**, with every entry traceable to either a native agent's category set or a documented enrichment of an existing agent.

The value proposition is especially strong for adopters running **multi-tenant LLM-serving SaaS** (where denial-of-wallet is the dominant economic threat), **consumer-facing chatbot or RAG-advisory products** (where cost-amplification via recursive prompts is a daily-occurring attack class), or **agentic orchestrators with LLM-backed worker agents** (where context-window exhaustion drives latency tail-risk that cascades into worker timeouts and cascade availability failures). Post-F-5 those adopters get architecture-context-aware findings on the full LLM10 surface — and the audit deliverable in ADR-034 gives them a per-sub-pattern owning-agent map they can use to drive their own internal threat-modeling workflows.

### BLP-01 Initiative Fit

**Reference**: `_internal/strategy/BLP-01-threat-coverage.md` §7 F-5; `_internal/strategy/SDR-001-threat-coverage-strategy.md` Decision 4 (Heuristic A). F-5 is the **fifth Tier 1 closure feature** in the BLP-01 initiative (F-1 shipped 2026-04-19 as Feature 201; F-2 shipped 2026-04-24 as Feature 206; F-3 shipped 2026-04-26 as Feature 219; F-4 shipped 2026-04-26 as Feature 224 — pending merge as of PRD time).

F-5's place in the BLP-01 chain:

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
F-3 (Feature 219, delivered 2026-04-26) — tool-abuse enrichment (ASI07) — first enrichment-branch execution
  │
F-4 (Feature 224, delivered 2026-04-26) — human-trust-exploitation agent (ASI09 communication axis) + agent-autonomy carve-up
  │
F-5 (this PRD, #229) ◄────── FIFTH TIER 1 FEATURE — closes LLM10 = 10/10 LLM Top 10 covered
  │  Two-agent enrichment of denial-of-service + model-theft via Heuristic A; second enrichment-branch execution
  │
F-6 (Tier 2 ML-extraction bundle — deferred)
F-7 (Tier 2 Mobile bundle — deferred)
F-8 (Tier 3 Web/API attestation — ships last)
```

**F-5 does NOT gate any other feature.** Its delivery closes LLM10 on the Coverage Matrix and demonstrates the **Heuristic A enrichment pattern at two-agent scope** — net-new validation that the consolidation rule produces a working delivery when the audit splits a single OWASP entry across multiple host agents (vs. F-3's single-host scope). The two-execution-deep validation of the enrichment branch is satisfied post-F-5; the pattern is now **structurally validated under both single-agent (F-3) and two-agent (F-5) scopes** and is available for any future Heuristic A consolidation, including the BLP-01 Tier 2 ML-extraction and Mobile bundles (F-6 / F-7) where multi-agent enrichment may apply.

**F-5 closes the LLM Top 10:2025 fully.** Post-F-5, OWASP LLM10:2025 transitions Partial → Covered, completing **10 of 10 LLM Top 10 coverage**. Combined with the 10 of 10 Agentic Top 10 coverage closed by F-4, post-F-5 tachi covers **20 of 20 OWASP AI top-10 entries** — a strategic milestone marker that the BLP-01 initiative explicitly tracks. **BLP-01 progress post-F-5: 8 of 11 features delivered.** Remaining: F-6 (Tier 2 ML-extraction), F-7 (Tier 2 Mobile), F-8 (Tier 3 Web/API attestation) — all Tier 2/3 deferred work.

### Recent ADR Lineage

- **ADR-023** (Threat Agent Skill References Pattern, Accepted 2026-04-11): Decision 3 (additive-only shared-reference edits) is the operational pattern for all four file edits in F-5. Decision 2 (zero MAESTRO references) preserved on the four enriched files. SC-1 + SC-3 + SC-4 + SC-5 + SC-12 trace to this ADR.
- **ADR-021** (SOURCE_DATE_EPOCH determinism, Accepted earlier): SC-9 byte-identity gate on the **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) uses this harness.
- **ADR-027** (Taxonomy Crosswalk Schema, Accepted 2026-04-17): F-5 cites OWASP LLM10 from `schemas/taxonomy/owasp.yaml` (verified at PRD time, line 373). The 5-value taxonomy enum is the source of `taxonomy: owasp` in F-5's `source_attribution` records.
- **ADR-028** (Source Attribution Schema Extension, Accepted 2026-04-17): SC-13 is direct consumption of this contract — Category-12/13 `D-{N}` findings emit `source_attribution: [{taxonomy: owasp, id: LLM10, relationship: primary}, {taxonomy: cwe, id: CWE-400, relationship: related}, ...]`; Category-10/11 `LLM-{N}` findings emit `source_attribution: [{taxonomy: owasp, id: LLM10, relationship: primary}, {taxonomy: owasp, id: LLM03, relationship: related} (where applicable), ...]`.
- **ADR-029** (Coverage Attestation Report Section, Accepted 2026-04-18): F-5's findings will surface in F-B's per-finding attribution table and per-framework coverage matrix when `examples/agentic-app/` is included in a security-report PDF run.
- **ADR-030** (Output Integrity Agent, Accepted 2026-04-19): F-5's ADR-034 cross-references ADR-030's Heuristic A signal-class analysis — ADR-030 Decision 1 established the three-signal-class taxonomy (input / output-sanitization / factual-integrity) within the LLM tier. F-5 demonstrates the **enrichment branch** of Heuristic A across two host agents — a different application of the same rule than F-3 (single-host enrichment).
- **ADR-031** (Misinformation Agent, Accepted 2026-04-24): F-5's ADR-034 cross-references ADR-031's regex-alternation minor-bump rule (ADR-030 Decision 8). F-5's distinguishing technical fact: **F-5 does not invoke the rule** — no regex bump, no schema increment. The cross-reference is to document the asymmetry: F-1 / F-2 / F-4 needed it; F-3 and F-5 do not, because Heuristic A enrichment reuses the existing host-agent's ID space.
- **ADR-032** (ASI07 Tool-Abuse Enrichment, Accepted 2026-04-26): F-5's ADR-034 cross-references ADR-032 as the **direct precedent** — ADR-032 was the first execution of the Heuristic A enrichment branch at single-agent scope; F-5 is the second execution at two-agent scope. ADR-032 lines 84 and 182 explicitly forecast that F-5 will not need a schema bump because the host agents' D-{N} and LLM-{N} prefixes already exist; F-5 fulfills that forecast.
- **ADR-033** (Human-Trust-Exploitation Agent, Accepted 2026-04-26): F-5's ADR-034 cross-references ADR-033 D2 (ASI09 sub-scope carve-up between autonomy axis and communication axis) as a **structural sibling** — ADR-033 demonstrated that a single OWASP entry can be carved across multiple host agents at the ADR-documentation layer; F-5 demonstrates that an OWASP entry can be **enriched** across multiple host agents at the pattern-catalog layer. Both are valid Heuristic A applications; the carve-up vs. enrichment distinction is documented in ADR-034.

### Roadmap Fit

- **Phase**: BLP-01 Tier 1 (AI/Agentic gaps, depth + breadth)
- **Week**: Week of 2026-04-27 — immediate follow-on to Feature 224 (F-4) delivery
- **Dependencies**:
  - F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17 (verified: OWASP LLM10 entry present at `schemas/taxonomy/owasp.yaml:373`; CWE-400 + CWE-770 present in `schemas/taxonomy/cwe.yaml` lines 130 and 182)
  - F-A2 (Feature 189) — **SATISFIED** as of 2026-04-17 (verified: `schemas/finding.yaml` v1.8 carries `source_attribution` data-shape contract). **Note**: F-A2 ships only the data-shape contract; populator wiring inside the 11 threat-detection agents is **deferred to F-A3** per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6. F-5 cites LLM10 in prose-level `references:` array (existing field since v1.0) and does NOT extend `source_attribution` populator wiring; F-A3 dependency direction is one-way (F-5 → F-A3 inheritance), F-5 does not block on F-A3.
  - F-B (Feature 194) — **SATISFIED** as of 2026-04-18 (verified: `templates/tachi/security-report/coverage-attestation.typ` exists; `has-source-attribution` boolean wired)
  - F-1 (Feature 201) — **SATISFIED** as of 2026-04-19 (no architectural dependency; informational precedent only)
  - F-2 (Feature 206) — **SATISFIED** as of 2026-04-24 (no architectural dependency; informational precedent only)
  - F-3 (Feature 219) — **SATISFIED** as of 2026-04-26 (architectural dependency: F-3 established the Heuristic A enrichment-branch precedent that F-5 operationalizes at two-agent scope; ADR-032 cross-referenced from ADR-034)
  - F-4 (Feature 224) — **SATISFIED** as of 2026-04-26 (no architectural dependency; informational precedent only — F-5 ships sequentially after F-4 for build-cadence reasons)

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Security Analyst Threat-Modeling an LLM-Serving Application**

- **Role**: Application security engineer or external consultant performing threat modeling on a production LLM-serving system (consumer chatbot, RAG advisory assistant, customer-support bot, agentic orchestrator with LLM-backed worker agents, multi-tenant LLM API gateway, LLM-fronted SaaS product)
- **Goal**: Surface the full LLM10 Unbounded Consumption attack surface — inference-request flooding, token-budget exhaustion, context-window exhaustion, cost amplification via recursive prompts, denial-of-wallet — with concrete mitigations rooted in OWASP LLM10:2025 vocabulary, distinct from generic infrastructure rate-limit advice
- **Pain Point Today**: Tachi reports `D-{N}` findings on generic infrastructure DoS (Categories 1–11 cover web-app DoS, algorithmic complexity, network flooding, cascade failures) and `LLM-{N}` findings on generic unbounded inference (Category 6 covers per-tenant quotas, cost controls, anomaly monitoring, free-tier abuse, billing attribution). The analyst gets **partial signal** but no LLM-named pattern categories; the threat-report renders LLM10 findings as generic infrastructure DoS or generic unbounded inference, forcing the analyst to hand-author the LLM10-specific mapping back to OWASP vocabulary. In multi-tenant LLM-serving SaaS this gap is significant — denial-of-wallet is the dominant economic threat class for the product, and the absence of a named "Denial-of-Wallet" pattern category undermines tachi's role as the LLM10 source of truth for the analyst's risk register.
- **Value Delivered**: Per-component `D-{N}` findings (Pattern Category 12: LLM Inference-Request Flooding and Token Exhaustion + Category 13: Context-Window Exhaustion) and `LLM-{N}` findings (Pattern Category 10: Cost Amplification + Category 11: Denial-of-Wallet) with named LLM-specific mitigations (per-tenant queries-per-second rate limit, prompt-size cap at API gateway, token-budget per request, max-context-window enforcement, cost-per-query p99 alerting, denial-of-wallet anomaly detection, automated tenant suspension on budget breach) emitted automatically when the architecture exhibits LLM-serving topology. Coverage Matrix shows LLM10:2025 as Covered.

### Secondary Persona: **Developer Deploying an LLM-Serving API**

- **Role**: Backend or full-stack developer wiring an LLM-serving endpoint (REST or streaming API), implementing per-tenant rate limits, cost-attribution middleware, or context-window enforcement; adopter of OpenAI / Anthropic / open-source-model APIs as the upstream provider
- **Goal**: Address tachi findings without researching the LLM10 mitigation pattern library from primary OWASP / CWE sources; need named mechanisms that map directly to API-gateway middleware decisions, not generic "rate-limit your endpoints" advice
- **Pain Point Today**: Generic guidance ("rate-limit your inference endpoints") doesn't translate to a concrete middleware change. Developers want named mechanisms: "per-tenant queries-per-second rate limit at the API gateway", "max-prompt-size token cap enforced before model invocation", "cost-per-query p99 alerting tied to per-tenant billing attribution", "context-window enforcement at API gateway with automatic 413-response on overflow", "denial-of-wallet anomaly detection via cost-velocity monitoring with automated tenant suspension on budget breach".
- **Value Delivered**: Each new Category-12/13 (`D-{N}`) and Category-10/11 (`LLM-{N}`) finding's `mitigation` field names specific LLM-API-gateway / cost-control / context-window / token-budget mechanisms matched to the detected pattern category. Category 12 findings name per-tenant rate limits and prompt-size caps. Category 13 findings name max-context-window enforcement and context-window monitoring. Category 10 findings name output-token caps and recursive-prompt depth limits. Category 11 findings name per-tenant token budgets and denial-of-wallet anomaly detection.

### Tertiary Persona: **Operator of a Multi-Tenant LLM-Serving SaaS**

- **Role**: Platform engineer or SRE operating a multi-tenant LLM-serving product (B2B SaaS where tenants pay per-token or per-API-call, or B2C product where freemium users share inference infrastructure with paying users)
- **Goal**: Detect denial-of-wallet attacks before the inference bill becomes a board-level incident; enforce per-tenant token budgets that prevent one tenant's recursive-prompt loop from amortizing across other tenants' billing
- **Pain Point Today**: The dominant economic threat for multi-tenant LLM SaaS is **denial-of-wallet** — an attacker drives the operator's inference bill to ruin without degrading availability for other tenants. Tachi's existing `model-theft` Category 6 covers per-tenant quotas at the abstraction level but does not name the attack class as denial-of-wallet, does not prescribe cost-velocity monitoring as a control, and does not differentiate "wallet" (the bill) from "uptime" (the system) as distinct attack-target axes. Operators learn the threat class from incident post-mortems rather than from threat-model artifacts.
- **Value Delivered**: Post-F-5 the canonical threat-model artifact (`threat-report.md` and `threats.md`) for any LLM-serving architecture renders a named **Denial-of-Wallet** Pattern Category (Cat 11 in `model-theft` companion) with prescribed cost-velocity-monitoring controls, per-tenant token budgets, and automated tenant suspension on budget breach. Operators can drive their incident-response playbooks directly from the tachi finding's `mitigation` field rather than from informal post-mortem knowledge.

**Maintainer concern (compressed callout — see BLP-01 Initiative Fit)**: F-5 is the second execution of the Heuristic A enrichment branch and the first at two-agent scope; success establishes the pattern's structural stability under both single-agent (F-3) and two-agent (F-5) shapes for future Heuristic A consolidations including BLP-01 Tier 2 ML-extraction and Mobile bundles. SC-1 / SC-2 / SC-3 / SC-4 / SC-5 / SC-12 provide grep-checkable byte-identity gates as the programmatic validation surface.

---

## 📖 User Stories

All three user stories are preserved from GitHub Issue #229 (which sourced them from BLP-01 §7, F-5). Job-story restructuring applied to align with the F-3 PRD (219) and F-4 PRD (224) precedent; acceptance criteria preserved where they specify testable predicates.

### US-229-1: Full LLM10 Surface Coverage via Two-Agent Enrichment

**When** a security analyst threat-models an LLM-serving architecture (consumer chatbot, RAG advisory assistant, agentic orchestrator with LLM-backed worker agents, multi-tenant LLM API gateway, LLM-fronted SaaS),
**I want** tachi to surface findings covering the **full LLM10 surface** (inference-request flooding, token-budget exhaustion, context-window exhaustion, cost amplification, denial-of-wallet) through the existing `denial-of-service` and `model-theft` agents,
**So that** I get complete LLM10 coverage without needing a new agent and without fragmenting findings across more dispatch surfaces.

**Acceptance Criteria**:

- **Given** an LLM-serving architecture exhibiting an inference endpoint without per-tenant rate limits or prompt-size cap, **when** the orchestrator dispatches `denial-of-service`, **then** at least one `D-{N}` finding emits with `category: denial-of-service` and its prose-level `references:` array contains `OWASP LLM10:2025` (alongside existing CWE-400 and related citations). `source_attribution` is NOT populated by F-5 — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230–238).
- **Given** an LLM-serving architecture exhibiting cost-amplification potential (e.g., recursive-prompt capability without depth limit, or output-token cap missing on the inference response), **when** `model-theft` runs, **then** at least one `LLM-{N}` finding emits with `category: llm` and its prose-level `references:` array contains `OWASP LLM10:2025`.
- **Given** an LLM-serving architecture exhibiting denial-of-wallet exposure (multi-tenant LLM serving without per-tenant token budget AND without cost-per-query alerting), **when** `model-theft` runs, **then** an `LLM-{N}` finding emits at **High or Critical severity** per Q3 RESOLVED OWASP 3×3 reasoning: HIGH default; **CRITICAL floor** ONLY when (a) multi-tenant freemium structure is structurally evident in the architecture AND (b) both per-tenant token budget AND cost alerting are absent.
- **Given** an architecture with **no LLM-serving topology** (no inference endpoint, no token-counting middleware, no cost-attribution layer — i.e., the **6 non-LLM-serving baselines** `web-app` / `microservices` / `ascii-web-api` / `mermaid-agentic-app` / `free-text-microservice` / `maestro-reference`), **when** both agents run, **then** the new Pattern Categories (12/13 in denial-of-service; 10/11 in model-theft) emit **zero findings** — the existing emission-gate discipline of both agents is preserved (Categories 1–11 in denial-of-service fire on generic infrastructure DoS as they do today; Categories 1–9 in model-theft fire on generic model-theft as they do today).

**Priority**: P0
**Effort**: M (two-agent enrichment is a slightly larger surface than F-3's single-agent enrichment but smaller than F-2's full new-agent shape)

### US-229-2: LLM-Specific Mitigation Naming on All New Findings

**When** a developer deploying an LLM-serving API addresses a tachi finding flagged on an inference endpoint or model-serving Process,
**I want** the finding's `mitigation` field to name **LLM-specific controls** (per-tenant token budget, prompt-size cap, context-window enforcement at API gateway, cost-per-query p99 alerting, denial-of-wallet anomaly detection, recursive-prompt depth limit, output-token cap, automated tenant suspension on budget breach),
**So that** the guidance is actionable on my LLM-API-gateway middleware without further OWASP / CWE primary-source research.

**Acceptance Criteria**:

- **Given** an `LLM-{N}` or `D-{N}` finding from any new Category-12/13 or Category-10/11, **when** the `mitigation` field is read, **then** it names at least one LLM-specific control distinct from generic infrastructure rate limits (e.g., `per-tenant token budget` rather than `rate-limit your endpoints`; `max-context-window enforcement at API gateway` rather than `validate request size`; `cost-per-query p99 alerting` rather than `monitor your bill`).
- **Given** any new Category-12/13 finding (`denial-of-service` LLM-tier), **when** its prose-level `references:` array is inspected, **then** at least one entry is `OWASP LLM10:2025`. CWE-400 (Uncontrolled Resource Consumption) and CWE-770 (Allocation of Resources Without Limits or Throttling) appear in the `references` array where applicable (both already in agent's `owasp_references` metadata; verified at PRD time). `source_attribution` is NOT populated by F-5 — populator wiring deferred to F-A3.
- **Given** any new Category-10/11 finding (`model-theft` LLM-tier), **when** its prose-level `references:` array is inspected, **then** at least one entry is `OWASP LLM10:2025`. OWASP LLM03:2025 may appear in the `references` array for the cost-flow-through-third-party-models adjacency (already in agent's `owasp_references` metadata).
- **Given** any new Category-10 (Cost Amplification) or Category-11 (Denial-of-Wallet) finding, **when** the `mitigation` narrative is read, **then** **MITRE ATT&CK T1496 Resource Hijacking** is named as a cross-reference — text-only prose mention, not as a structured citation in `references` (T1496 is not catalog-resolvable per PRD-time check of `schemas/taxonomy/mitre-attack.yaml`).
- **Given** severity computation on the new findings, **when** the `risk_level` is read, **then** degraded-availability findings (Cat 12 inference-flooding / Cat 13 context-window-latency-DoS) compute **MEDIUM-HIGH** default per Q3 OWASP 3×3 reasoning; cost-amplification findings (Cat 10) compute **HIGH** default; denial-of-wallet findings (Cat 11) compute **HIGH** default with **CRITICAL floor** ONLY when (a) multi-tenant freemium structure is structurally evident in the architecture AND (b) both per-tenant token budget AND cost alerting are absent — the severity discrimination between availability-degradation and cost-exposure is preserved.

**Priority**: P0
**Effort**: S

### US-229-3: Audit-Confirmed Additive-Only Transition with Mapping Table

**When** an adopter whose current tachi run already flags LLM10-adjacent signals via the partial-coverage path (existing `D-{N}` Categories 1–11 or `LLM-{N}` Category 6) re-runs tachi after F-5 merges,
**I want** the F-5 audit to confirm that **no existing signals are dropped** while adding the missing sub-patterns and to surface a canonical mapping table assigning every LLM10 sub-pattern to exactly one owning agent,
**So that** the transition Partial → Covered is **additive, not a re-scoping**, and I can rely on the mapping table to drive my own internal threat-modeling vocabulary without ambiguity about where each LLM10 sub-pattern lives.

**Acceptance Criteria**:

- **Given** a regenerated example architecture exercising both `denial-of-service`-side and `model-theft`-side LLM10 patterns, **when** the threat-report's category sections are read, **then** all `D-{N}` findings render in the same `category: denial-of-service` section regardless of which Pattern Category (1–13) produced them, and all `LLM-{N}` findings render in the same `category: llm` section regardless of which Pattern Category (1–11) produced them. The ID prefixes `D-{N}` and `LLM-{N}` are **single-namespace per agent** — sequential numbering across all categories within each agent.
- **Given** ADR-034 at the time of F-5 merge, **when** its Decision section is read, **then** it contains a **canonical sub-pattern → owning-agent mapping table** that assigns every LLM10 sub-pattern (inference-request flooding, token-budget exhaustion, context-window exhaustion, cost amplification, denial-of-wallet) to **exactly one owning agent**. No sub-pattern is duplicated across both agents. The mapping table is the audit deliverable per Issue #229.
- **Given** any pre-existing finding produced by tachi prior to F-5 merge (Categories 1–11 in `denial-of-service`, Categories 1–9 in `model-theft`), **when** the same architecture is re-run post-F-5, **then** the pre-existing finding is produced byte-identically — additive enrichment does not alter pre-existing finding shape, ID, or severity. **All existing `## Pattern Category` headings in both companion files are byte-identical pre/post edit per ADR-023 Decision 3.**
- **Given** the BLP-01 Coverage Matrix post-F-5 merge, **when** the LLM10:2025 row (line 278 baseline) is inspected, **then** it transitions **Partial → Covered** with F-5 (Feature 229) named as the closure feature. **OWASP LLM Top 10:2025 framework row transitions to 10 of 10 Covered** — completing the full LLM Top 10 coverage milestone.
- **Given** the Coverage Matrix post-F-5 merge, **when** the OWASP AI top-10 framework rollup is summed, **then** post-F-5 tachi covers **20 of 20 OWASP AI top-10 entries** (10 Agentic post-F-4 + 10 LLM post-F-5) — a strategic milestone marker that the BLP-01 strategy explicitly tracks.

**Priority**: P0
**Effort**: S (audit deliverable in ADR-034 is the primary content; mapping table is architect-finalized at plan time)

---

## ⚙️ Functional Requirements

### FR-1 — Additive Metadata + Purpose Edit to `denial-of-service.md`

- **File**: `.claude/agents/tachi/denial-of-service.md`
- **Edit 1** (one-line append): `owasp_references` list (currently 9 entries at lines 17–26 per PRD-time grep) extended with `"OWASP LLM10:2025 — Unbounded Consumption"` as the 10th entry. Existing entries (`OWASP A04:2021`, `OWASP DoS Cheat Sheet`, `OWASP API4:2023`, `CWE-400`, `CWE-770`, `CWE-1333`, `CWE-502`, `MITRE ATT&CK T1498`, `MITRE ATT&CK T1499`) preserved byte-identically.
- **Edit 2** (`## Purpose` extension — additive paragraph or 1–3 sentences appended within the existing `## Purpose` section at line 32–34): name the LLM-inference-exhaustion surface alongside the existing infrastructure-availability surface. Suggested phrasing (architect-finalized at plan time): "This agent additionally covers the **LLM inference-exhaustion surface** — inference-request flooding on LLM endpoints, token-budget exhaustion via unbounded prompt-size, and context-window exhaustion on shared inference infrastructure — per OWASP LLM10:2025. Pattern Categories 12 (LLM Inference-Request Flooding and Token Exhaustion) and 13 (Context-Window Exhaustion via Adversarial Input Expansion) detect LLM-serving threats distinct from generic infrastructure DoS."
- **Edit 3** (Detection Workflow Step 5 references list extension at line 52): existing list (`OWASP, CWE, MITRE ATT&CK from the pattern catalog's Primary Sources list`) extended with `OWASP LLM10:2025` exemplar mention. Optional refinement at architect plan time.
- **Length cap**: agent file MUST remain ≤120 lines (STRIDE tier cap per ADR-023). PRD-time baseline: 53 lines. Expected post-edit: 56–60 lines (well within margin; budget for additions: ≤67 lines).
- **MAESTRO references**: **ZERO** (ADR-023 Decision 2 invariant). Grep-checkable.
- **Byte-identity preservation**: every line not directly modified by Edit 1, 2, or 3 remains byte-identical.

### FR-2 — Additive Pattern Categories 12 and 13 in `denial-of-service` Companion

- **File**: `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` (179 lines pre-edit)
- **Edit posture**: append-only after existing `## Pattern Category 11: Cascade Failures and Noisy Neighbor in Microservice Architectures` (Cat 11 region ends ~line 155; Primary Sources section spans lines 156–179). The companion file uses a **hybrid heading structure**: 8 thematic groupings cover Cat 1–8 conceptual surface (`## Resource Exhaustion`, `## Algorithmic Complexity Attacks`, `## Database and Storage Saturation`, `## Connection and Pool Exhaustion`, `## Dependency and Cascade Failures`, `## Application-Layer Attacks`, `## Infrastructure-Layer Attacks`, `## Flooding and Abuse`) plus 3 named `## Pattern Category N:` headings (Cat 9, Cat 10, Cat 11), totaling 12 H2 sections plus `## Overview` / `## Targeted DFD Element Types` / `## Primary Sources`. **Asymmetric to model-theft companion**: this companion does NOT have a `## Trigger Keywords` section. Existing content byte-identical pre/post edit per ADR-023 Decision 3.
- **Q1 SPLIT resolution**: Cat 13 covers context-window exhaustion **latency-DoS variant only** (Vector A — availability disruption). Cat 13 is structurally same-class as Cat 12 (per-request resource exhaustion via latency tail). The cost-amplification variant of context-window exhaustion (Vector B — economic damage) lives in `model-theft` Cat 11 per FR-3.
- **Section shape (mirror Cat 9–11 named-Category style)**: each new Category specifies (a) name with header, (b) primary OWASP/CWE source, (c) **≥4 indicators** (3–6 bullet points), (d) at least one worked example, (e) named LLM-specific mitigations.

#### Pattern Category 12: LLM Inference-Request Flooding and Token Exhaustion

- **Primary**: `OWASP LLM10:2025 — Unbounded Consumption`
- **Related**: `CWE-400 Uncontrolled Resource Consumption`, `CWE-770 Allocation of Resources Without Limits or Throttling`
- **Indicators** (≥4):
  - Architecture exposes an LLM inference endpoint without per-tenant queries-per-second rate limit at the API gateway.
  - Inference endpoint accepts unbounded prompt-size (no max-prompt-token cap enforced at request ingestion).
  - Token-budget per request is missing or set without per-tenant differentiation.
  - Request-timeout enforcement at the API gateway does not distinguish LLM-call latency tail-risk from generic HTTP timeouts.
  - LLM-serving Process lacks token-counting middleware between request ingestion and model invocation.
- **Worked example**: A multi-tenant LLM-serving SaaS exposes a `/v1/completions` endpoint without per-tenant queries-per-second rate limit. An attacker registers free-tier accounts and floods the endpoint with concurrent requests, exhausting inference compute capacity and causing latency degradation for paying tenants. Threat: tenant isolation breaks down at the inference-compute layer; the SaaS's denial-of-wallet exposure compounds with the availability degradation.
- **Mitigations**:
  - Per-tenant queries-per-second rate limit at the API gateway.
  - Prompt-size cap (max-prompt-token enforcement) at request ingestion, before model invocation.
  - Per-tenant token budget per request with hard-cap enforcement.
  - Request-timeout enforcement tuned to LLM-call p99 latency.
  - Token-counting middleware between request ingestion and model invocation, with anomaly alerting on per-tenant token-velocity spikes.

#### Pattern Category 13: Context-Window Exhaustion — Latency-Driven Variant

- **Primary**: `OWASP LLM10:2025 — Unbounded Consumption`
- **Related**: `CWE-400 Uncontrolled Resource Consumption`
- **Q1 SPLIT scope**: Vector A only (availability disruption via per-request latency tail). The cost-amplification variant of context-window exhaustion (Vector B) lives in `model-theft` Pattern Category 11.
- **Indicators** (≥4):
  - Architecture allows adversarial prompt expansion (no max-context-window enforcement at the API gateway; request payload accepted up to model-maximum context window).
  - Multi-message conversation history is appended without per-conversation truncation policy or sliding-window limit.
  - Recursive prompt patterns (chain-of-thought self-amplification, recursive query-expansion) are not detected at the API gateway.
  - Context-window monitoring is absent at the inference-runtime layer (no metric tracking context-window usage as a percentage of model max per request).
  - Per-tenant context-window cap is not differentiated from per-request context-window cap.
- **Worked example**: A consumer-facing chatbot allows users to send arbitrarily long conversation history. An attacker constructs a 32k-token mega-history payload that drives context-window usage to 99% of model max, causing per-request latency to spike to per-tenant timeout. Threat (latency-DoS lens): legitimate users on the same inference cluster experience degraded latency; attacker's intent is **availability disruption**. Same architecture additionally surfaces `model-theft` Cat 11 (denial-of-wallet via context-window cost amplification) as Vector B — both findings emit on the same architecture, neither is a duplicate, ADR-034 audit table assigns each to exactly one owning category.
- **Mitigations**:
  - Max-context-window enforcement at the API gateway, with automatic 413-response on overflow.
  - Per-conversation truncation policy with sliding-window limit on appended message history.
  - Recursive-prompt-pattern detection at the API gateway (regex or token-based heuristic for self-amplifying prompts).
  - Context-window monitoring with anomaly alerting on percentage-of-max usage spikes.
  - Per-tenant context-window cap distinct from per-request context-window cap.

#### Pattern Category Disambiguation: Category 12 (Inference-Request Flooding) vs. Category 13 (Context-Window Exhaustion) vs. Existing Cat 9 (Uncontrolled Resource Consumption, CWE Top 25)

Categories 12 and 13 cite CWE-400 as `relationship: related`, mirroring the citation pattern in pre-existing Category 9. This creates a **non-overlapping by design** carve that ADR-034 will formalize:

- **Category 9** (pre-existing) fires on **generic infrastructure resource exhaustion** patterns from the CWE Top 25 — algorithmic complexity, ReDoS, deserialization-of-untrusted-data, etc. Generic to any HTTP service.
- **Category 12** (new) fires on **LLM-specific inference-request flooding and token exhaustion** — same CWE-400 root cause but LLM-API-gateway middleware as the mitigation surface (per-tenant QPS rate limit, prompt-size cap, token-counting middleware).
- **Category 13** (new) fires on **LLM-specific context-window exhaustion** — adversarial prompt expansion as the attack vector, max-context-window enforcement and per-conversation truncation as the mitigation surface.

The same architecture may legitimately surface Category 9 + Category 12 + Category 13 findings — e.g., an LLM-serving Process that lacks both generic ReDoS protection (Cat 9) AND per-tenant LLM-API-gateway rate limit (Cat 12) AND max-context-window enforcement (Cat 13). They are not duplicates and should not be merged in the threat-report's denial-of-service category section. Architect to formalize this carve in ADR-034 (likely as a Decision Pattern Category Disambiguation subsection).

### FR-3 — Additive Pattern Categories 10 and 11 in `model-theft` Companion

- **File**: `.claude/skills/tachi-model-theft/references/detection-patterns.md` (154 lines pre-edit)
- **Edit posture**: append-only after existing `## Pattern Category 9: System Prompt and Configuration Leakage (OWASP LLM07:2025)` (currently ends at line 154 per PRD-time line count). Categories 1–9 byte-identical pre/post edit per ADR-023 Decision 3. Existing `## Overview`, `## Targeted DFD Element Types`, and `## Trigger Keywords` (line 19 — present in this companion, asymmetric to denial-of-service companion) sections preserved.
- **Q1 SPLIT resolution**: Cat 11 covers Vector B of context-window exhaustion (cost-amplification driven economic damage — denial-of-wallet) plus the broader denial-of-wallet attack class. The latency-DoS variant of context-window exhaustion (Vector A) lives in `denial-of-service` Cat 13 per FR-2.
- **Section shape (mirror Categories 1–9)**: each new Category specifies (a) name with header, (b) primary OWASP/CWE source, (c) **≥4 indicators**, (d) at least one worked example, (e) named LLM-specific cost-control mitigations.

#### Pattern Category 10: Cost Amplification via Recursive or Cost-Asymmetric Prompting

- **Primary**: `OWASP LLM10:2025 — Unbounded Consumption`
- **Related**: `OWASP LLM03:2025 — Supply Chain` (inherited from existing agent `owasp_references`)
- **Indicators** (≥4):
  - LLM-serving Process accepts recursive or chain-of-thought prompt patterns without depth limit.
  - Output-token cap is missing or set higher than realistic per-query response length (e.g., 32k-token cap on a customer-support chatbot whose realistic responses are ≤500 tokens).
  - Output-amplification ratio (output-tokens / input-tokens) is not monitored per query.
  - Cost-per-query p99 alerting is absent at the inference-runtime layer.
  - Per-tenant cost-amplification anomaly detection is missing (no metric tracking output-token-per-input-token velocity per tenant).
- **Worked example**: A RAG advisory assistant accepts a 10-token user prompt that triggers a recursive chain-of-thought response chain, generating 32k tokens of self-amplifying output without an intermediate-step cap. Threat: the operator's inference cost per query exceeds the revenue per query by 100x; sustained attack drives the operator's monthly bill to financial ruin without degrading availability for other tenants (the cost is the attack surface, not the uptime).
- **Mitigations**:
  - Per-query output-token cap tuned to realistic response-length p99.
  - Recursive-prompt depth limit enforced at the inference-runtime layer.
  - Output-amplification-ratio monitoring with anomaly alerting on per-query velocity spikes.
  - Cost-per-query p99 alerting tied to per-tenant billing attribution.
  - Per-tenant cost-amplification anomaly detection with cost-velocity monitoring per tenant.
  - **MITRE ATT&CK T1496 Resource Hijacking** named in the mitigation narrative as a cross-reference (text-only — T1496 is not catalog-resolvable per PRD-time check of `schemas/taxonomy/mitre-attack.yaml`, so it does NOT appear in `source_attribution`).

#### Pattern Category 11: Denial-of-Wallet via Context-Window Cost Amplification

- **Primary**: `OWASP LLM10:2025 — Unbounded Consumption`
- **Related**: `OWASP LLM03:2025 — Supply Chain` (inherited; cost-flow-through-third-party-models adjacency)
- **Q1 SPLIT scope**: Vector B of context-window exhaustion (cost-amplification driven economic damage — attacker drives context-window to maximum to inflate per-call cost; the "wallet" is the bill) plus the broader denial-of-wallet attack class. Same signal class as Cat 10 cost-amplification (extraction-driven resource abuse). The latency-DoS variant of context-window exhaustion (Vector A) lives in `denial-of-service` Cat 13.
- **Indicators** (≥4):
  - Multi-tenant LLM-serving architecture lacks per-tenant token budget with hard-cap enforcement.
  - Context-window expansion is not capped per-tenant (attacker can drive context-window to model max per call without per-tenant budget reconciliation).
  - Cost-per-query p99 alerting is missing at the inference-runtime layer.
  - Denial-of-wallet anomaly detection (cost-velocity monitoring) is absent.
  - Automated tenant suspension on budget breach is missing or operates with manual approval delay.
  - Per-tenant billing attribution is missing or is computed asynchronously (cost is realized at end-of-month rather than at-query-time).
- **Worked example**: A B2C consumer chatbot SaaS allows freemium users to consume inference compute without per-tenant token budget. An attacker registers thousands of freemium accounts and runs cost-amplification queries (Category 10 pattern) at scale, **plus** drives context-window to model max per call (Vector B), inflating per-call cost. Threat: the operator's monthly inference bill exceeds revenue by 10x; the freemium tier becomes economically untenable; the operator either eats the loss or restricts freemium access. The "wallet" is the bill, not the uptime — denial-of-wallet is structurally distinct from denial-of-service. **Severity floor**: per Q3 RESOLVED resolution at PRD time (OWASP 3×3 reasoning), this finding emits at **Critical floor** ONLY when (a) multi-tenant freemium structure is structurally evident in the architecture AND (b) both per-tenant token budget AND cost alerting are absent. Otherwise HIGH default per OWASP 3×3 (likelihood × impact composite). The 2-condition Critical floor is encoded as a severity-hint annotation in the ADR-034 audit table.
- **Mitigations**:
  - Per-tenant token budget with hard-cap enforcement at the API gateway.
  - Per-tenant context-window cost reconciliation (context-window expansion is debited against per-tenant token budget).
  - Cost-per-query p99 alerting tied to per-tenant billing attribution.
  - Denial-of-wallet anomaly detection via cost-velocity monitoring (per-tenant cost-per-time-window with anomaly alerting on percentile-velocity spikes).
  - Automated tenant suspension on budget breach (no manual approval delay).
  - Per-tenant billing attribution computed at-query-time, not at end-of-month.
  - **MITRE ATT&CK T1496 Resource Hijacking** named in the mitigation narrative as a cross-reference (text-only).

#### Pattern Category Disambiguation: Category 6 (Unbounded Inference Consumption — pre-existing) vs. Category 10 (Cost Amplification) vs. Category 11 (Denial-of-Wallet)

Categories 10 and 11 cite OWASP LLM10:2025 as primary, mirroring the citation pattern in pre-existing Category 6. This creates a **non-overlapping by design** carve that ADR-034 will formalize:

- **Category 6** (pre-existing) fires on **per-tenant quota / cost-control / billing-attribution gaps at the abstraction level** — covers free-tier abuse, missing API-key authentication, missing inference-volume monitoring. Generic to any model-serving infrastructure.
- **Category 10** (new) fires on **specific cost-amplification attack vectors** — recursive prompts, output-asymmetric queries, output-token caps misconfigured.
- **Category 11** (new) fires on **denial-of-wallet as a named economic attack class** — multi-tenant SaaS economic-failure exposure, cost-velocity monitoring as the dominant control.

The same architecture may legitimately surface Category 6 + Category 10 + Category 11 findings — e.g., a multi-tenant LLM SaaS that lacks all three: per-tenant inference quota (Cat 6) AND output-token cap (Cat 10) AND per-tenant token budget (Cat 11). They are not duplicates. Architect to formalize this carve in ADR-034.

### FR-4 — Additive Metadata Audit + Purpose Edit to `model-theft.md`

- **File**: `.claude/agents/tachi/model-theft.md`
- **Edit 1** (audit confirmation, **zero net change**): `owasp_references` list (currently `[OWASP LLM10:2025, OWASP LLM03:2025]` per PRD-time grep at line 17) **already contains** `OWASP LLM10:2025`. F-5's audit confirms completeness; **no metadata extension needed on this agent**. (Asymmetric to FR-1's denial-of-service edit.)
- **Edit 2** (`## Purpose` extension — additive paragraph or 1–3 sentences appended within the existing `## Purpose` section): name the cost-amplification and denial-of-wallet surface alongside the existing model-extraction surface. Suggested phrasing (architect-finalized at plan time): "This agent additionally covers the **cost-amplification and denial-of-wallet surface** — recursive or cost-asymmetric prompting that drives output-token amplification, and multi-tenant denial-of-wallet attacks where an attacker drives the operator's inference bill to ruin without degrading availability for other tenants — per OWASP LLM10:2025. Pattern Categories 10 (Cost Amplification via Recursive or Cost-Asymmetric Prompting) and 11 (Denial-of-Wallet via Cost-Asymmetric Queries) detect LLM-serving economic-attack threats distinct from model-extraction."
- **Length cap**: agent file MUST remain ≤150 lines (AI tier cap per ADR-023). PRD-time baseline: 95 lines. Expected post-edit: 98–102 lines.
- **MAESTRO references**: **ZERO** (ADR-023 Decision 2 invariant). Grep-checkable.
- **Byte-identity preservation**: every line not directly modified by Edit 2 remains byte-identical.

### FR-5 — Primary Sources List Extension in Both Companions

- **Files**: `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` AND `.claude/skills/tachi-model-theft/references/detection-patterns.md`
- **Edit (denial-of-service companion)**: extend the `## Primary Sources` list with `OWASP LLM10:2025 — Unbounded Consumption` as a new entry. Existing Primary Sources entries preserved byte-identically (architect verifies at plan time).
- **Edit (model-theft companion)**: extend the `## Primary Sources` list with `OWASP LLM10:2025 — Unbounded Consumption` as a new entry (or confirm the existing list already cites LLM10 in some adjacency — PRD-time verification deferred to plan-time architect grep). Existing Primary Sources entries preserved byte-identically.

### FR-6 — Public Per-Feature ADR (ADR-034)

- **File**: `docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md`
- **Authoring pattern**: dual-commit Proposed → Accepted per ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 / ADR-032 / ADR-033 precedent.
- **Decision content** (architect-owned at plan time):
  - **Decision 1**: Adopt Heuristic A enrichment (vs. new agent) for LLM10 at **two-agent scope**. Rationale: signal-class identity with both `denial-of-service` (infrastructure-resource-exhaustion sub-class) and `model-theft` (extraction-driven-resource-abuse sub-class); creating a new `unbounded-consumption` agent would fragment LLM10 findings across three locations.
  - **Decision 2**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing Categories 1–11 (`denial-of-service`) and Categories 1–9 (`model-theft`) byte-identical pre/post edit (grep-checkable).
  - **Decision 3**: **Canonical LLM10 sub-pattern → owning-agent mapping table** (the audit deliverable). Each row of the table assigns one LLM10 sub-pattern to exactly one owning agent. Per Q1 SPLIT resolution at PRD time, context-window exhaustion decomposes into two attack vectors with disjoint owning agents. Mapping table (5 rows; severity-hint annotation column per Q3 RESOLVED OWASP 3×3 reasoning):
    - **inference-request flooding** → `denial-of-service` Category 12 — severity: MEDIUM-HIGH default (Cat 12 inference-flooding is availability-degradation lens)
    - **token-budget exhaustion** → `denial-of-service` Category 12 — severity: MEDIUM-HIGH default
    - **context-window exhaustion — latency-Vector A (DoS lens)** → `denial-of-service` Category 13 — severity: MEDIUM-HIGH default; same architecture also surfaces Vector B at `model-theft` Cat 11 (neither finding is duplicate; both emit on the same architecture)
    - **context-window exhaustion — cost-Vector B (DoW lens)** → `model-theft` Category 11 — severity: HIGH default; CRITICAL floor when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent
    - **cost amplification via recursive or cost-asymmetric prompting** → `model-theft` Category 10 — severity: HIGH default
    - **denial-of-wallet (broader than Vector B context-window-cost)** → `model-theft` Category 11 — severity: HIGH default; CRITICAL floor under the 2-condition rule above
  - **Decision 4**: No schema bump. `schemas/finding.yaml` remains at v1.8. Reuses existing `D-{N}` and `LLM-{N}` ID prefixes. Asymmetric to F-1/F-2/F-4 (which bumped schema for new prefix); structurally symmetric with F-3 (ADR-032). Cross-reference ADR-032 lines 84 and 182 — F-5 fulfills that explicit forecast.
  - **Decision 5**: No consumers-list edit. Both `denial-of-service` and `model-theft` already at `finding-format-shared.md` lines 12 and 16 (verified at PRD time).
  - **Decision 6**: No functional orchestrator/dispatch-rules edit. Both agents fully registered (verified across multiple callsites at PRD time). **Q2 default-NO**: cosmetic annotation update to extend `denial-of-service (CWE-400)` to `denial-of-service (CWE-400, LLM10)` is permitted but not required. Architect-tractable at plan time.
  - **Decision 7**: Pattern Category Disambiguation between pre-existing categories and new categories. Documented in FR-2 and FR-3 above; ADR-034 formalizes the carve as a Decision subsection.
  - **Decision 8** (optional): Public ADR omits commercial framing per Option C governance contract from SDR-001. Cross-reference to SDR-001 Decision 4 lives in private companion docs only.
- **Cross-references** (public-safe): ADR-023 (lean+skill-references pattern, additive-only edits), ADR-021 (byte-identity baseline harness), ADR-027 (taxonomy crosswalk), ADR-028 (source attribution schema), ADR-030 (Heuristic A within LLM tier), ADR-031 (regex minor-bump rule — referenced as the asymmetry: F-5 does not invoke it, like F-3), ADR-032 (first enrichment-branch execution at single-agent scope; F-5 is the second at two-agent scope — explicit cross-reference to ADR-032 lines 84 and 182 forecast), ADR-033 (F-4 sub-scope carve-up — structural sibling: ADR-033 carved one OWASP entry across two host agents at the documentation layer; ADR-034 enriches one OWASP entry across two host agents at the pattern-catalog layer; both are valid Heuristic A applications).
- **Zero-MAESTRO-reference invariant per ADR-023 Decision 2** applies to the **four edited files** (`denial-of-service.md`, `model-theft.md`, both companion `detection-patterns.md` files). ADR-034 itself MAY discuss MAESTRO inheritance semantics if relevant, mirroring ADR-032 / ADR-033 precedent (both discuss MAESTRO Layer 7 inheritance per ADR-020 lineage in their Decision sections without violating ADR-023 D2).

### FR-7 — Example Regeneration Target

- **Target architecture**: `examples/agentic-app/` — Q5 RESOLVED at PRD time per architect adjudication. No new architecture authoring needed; mutation candidate is multi-component LLM topology already exercised by F-3. ADR-034 includes a Detection Calibration Note clarifying that the new Pattern Categories 12/13 (denial-of-service) and 10/11 (model-theft) fire on **structural absence** of named control mechanisms — consistent with F-1 / F-2 / F-4 absence-style detection style. Acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention.
- **Acceptance**: at least 1 new `D-{N}` finding produced citing `OWASP LLM10:2025` in its `references` array (from `denial-of-service` Pattern Category 12 or 13) AND at least 1 new `LLM-{N}` finding produced citing `OWASP LLM10:2025` in its `references` array (from `model-theft` Pattern Category 10 or 11).
- **Byte-identity gate** (SC-9): all **6 non-LLM-serving baselines** — `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference` — regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` (those baselines do not exhibit LLM-serving topologies, so the new Categories emit zero findings, so artifacts are unchanged). `agentic-app` is the F-5 mutation target without a `.baseline` file by design; `consumer-agent-app` is F-4's mutation target without a `.baseline` file and is untouched by F-5. Verification owner: `tester` agent (separate from `senior-backend-engineer` who authors edits).

### FR-8 — LLM10 Citation in Prose-Level `references` Array on All New Findings

- **Scope clarification**: F-5 does **not** extend `source_attribution` populator wiring on the host agents. Per-PRD-time grep, neither `denial-of-service.md` nor `model-theft.md` currently emit `source_attribution` (the `D-{N}` and `LLM-{N}` populator wiring is deferred to F-A3 per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6: "F-A2 ships the data-shape contract only. Populator wiring inside the 11 threat-detection agents is deferred to F-A3 under the 22-file zero-edit invariant per ADR-023 / ADR-028 Decision 6"). F-5 cites LLM10 in the prose-level `references:` array (an existing finding-YAML field present since v1.0). When F-A3 ships, the LLM10 citations established by F-5 will flow into `source_attribution` naturally because the catalog references are already correct. **F-A3 dependency direction is one-way (F-5 → F-A3 inheritance); F-5 does not require F-A3 to ship and does not block on it.**
- **Per-finding requirement (denial-of-service Category 12/13)**: every new `D-{N}` finding's `references` array includes **at minimum** `OWASP LLM10:2025 — Unbounded Consumption` and `CWE-400 Uncontrolled Resource Consumption`. Where applicable: `CWE-770 Allocation of Resources Without Limits or Throttling` (both CWEs verified present in `schemas/taxonomy/cwe.yaml` lines 130 and 182).
- **Per-finding requirement (model-theft Category 10/11)**: every new `LLM-{N}` finding's `references` array includes **at minimum** `OWASP LLM10:2025 — Unbounded Consumption`. Where applicable: `OWASP LLM03:2025 — Supply Chain` for the cost-flow-through-third-party-models adjacency.
- **MITRE ATT&CK T1496 Resource Hijacking**: named in `mitigation` narrative text on Category 10 and Category 11 findings as a cross-reference (text-only prose mention). **NOT** included as a structured citation in `references` because T1496 is not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` (PRD-time verified absent).
- **Catalog resolvability**: all citations included in `references` (LLM10, CWE-400, CWE-770, LLM03) verified present in the taxonomy catalogs at PRD time.
- **Forward-compatibility**: F-A3 will eventually wire `source_attribution` populators on all 11 threat-detection agents (including `denial-of-service` and `model-theft`). At that point, F-5's LLM10 references will translate into `source_attribution` records of the form `{taxonomy: owasp, id: LLM10, relationship: primary}` automatically — F-5's catalog citations are the upstream input to F-A3's downstream wiring.

---

## 🚀 Non-Functional Requirements

### Performance

- **Agent invocation latency**: no measurable change. The new Pattern Categories are matched by the same DFD-traversal logic that walks Categories 1–11 (`denial-of-service`) and Categories 1–9 (`model-theft`) today; the marginal overhead is O(2 additional pattern matches per dispatch). Empirical impact <1ms per architecture file.
- **Architecture analysis throughput**: unchanged. F-5 does not add a new dispatch step.

### Reliability / Determinism

- **Byte-identity** (ADR-021 SOURCE_DATE_EPOCH=1700000000): SC-9 explicitly verifies byte-identity on the **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`). The Heuristic A enrichment-branch pattern PRESERVES byte-identity by construction on baselines that do not exhibit the new trigger surface.
- **Idempotency**: the new Pattern Categories are deterministic given a fixed architecture input; the same architecture file produces the same finding set across runs.

### Security

- **Zero MAESTRO references** (ADR-023 Decision 2): preserved on `denial-of-service.md`, `model-theft.md`, and both companion `detection-patterns.md` files post-edit.
- **Public ADR scope**: ADR-034 omits commercial framing per Option C governance. SDR-001 cross-reference lives in private companion docs only.
- **No new attack surface introduced**: F-5 is documentation + pattern enrichment; no new code paths, no new dependencies, no new I/O.

### Maintainability

- **Lean shape preserved**: `denial-of-service.md` post-edit ≤120 lines (PRD-time baseline 53; expected post-edit 56–60). `model-theft.md` post-edit ≤150 lines (PRD-time baseline 95; expected post-edit 98–102).
- **Additive-only invariant**: existing prose in both agent files' `## Purpose` sections and Categories 1–11 / 1–9 in companion files are byte-identical pre/post edit. Grep-checkable.
- **Single-source-of-truth**: ADR-034 documents the Heuristic A enrichment pattern at two-agent scope; future multi-agent enrichments reuse this ADR as precedent. The canonical sub-pattern → owning-agent mapping table prevents duplicate detection.

---

## 📊 Success Metrics

### Coverage

- **OWASP LLM Top 10:2025**: LLM10 transitions Partial → Covered. Coverage Matrix post-F-5: **10 of 10 LLM Top 10 entries Covered**.
- **OWASP AI top-10 rollup**: 10 Agentic Top 10 (post-F-4) + 10 LLM Top 10 (post-F-5) = **20 of 20 OWASP AI top-10 entries Covered** — strategic milestone marker.
- **LLM-serving example coverage**: at least 1 new `D-{N}` finding AND 1 new `LLM-{N}` finding on `examples/agentic-app/` demonstrating Categories 12/13 and 10/11 firing, each citing OWASP LLM10:2025 in its prose-level `references` array.

### Quality

- **Byte-identity baselines**: **6 of 7 example baselines** regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`; `agentic-app` is the F-5 mutation target. (`consumer-agent-app` is F-4's mutation target without a `.baseline` file and is untouched by F-5.)
- **Line count caps**: `denial-of-service.md` post-edit ≤120 lines (50%+ margin reserved). `model-theft.md` post-edit ≤150 lines (30%+ margin reserved).
- **Catalog resolvability**: 100% of new `references` citations resolve against `schemas/taxonomy/{owasp,cwe}.yaml`.

### Pattern Validation

- **Heuristic A enrichment pattern at two-agent scope**: first execution. Establishes the precedent for future multi-agent Heuristic A consolidations (e.g., BLP-01 Tier 2 ML-extraction or Mobile bundles).
- **No-schema-bump pattern**: second BLP-01 detection feature without a schema increment (after F-3). Validates the precedent that consolidation features reuse existing host ID space.
- **Two-execution-deep validation of enrichment branch**: F-3 (single-agent) + F-5 (two-agent) = both shapes validated; the pattern is now structurally stable per F-2 retrospective KB-037 framework.

### Delivery

- **Calendar window**: 2026-04-29 (Wednesday) build day; 2026-04-30 (Thursday) buffer.
- **Effort envelope**: 1.5 working days realistic (between F-3's 1 day and F-2's 2 days).

---

## 🔍 Scope & Boundaries

### In Scope (MVP / Phase 1)

**Must Have (P0)**:
- Pattern Categories 12 + 13 — appended to `denial-of-service` companion `detection-patterns.md`
- Pattern Categories 10 + 11 — appended to `model-theft` companion `detection-patterns.md`
- `denial-of-service.md` `owasp_references` += `OWASP LLM10:2025`
- `denial-of-service.md` `## Purpose` extension naming the LLM-inference-exhaustion surface
- `denial-of-service.md` Detection Workflow Step 5 references extended with `OWASP LLM10:2025` exemplar mention
- `model-theft.md` `owasp_references` audit confirmation (already includes LLM10:2025; zero net change)
- `model-theft.md` `## Purpose` extension naming the cost-amplification and denial-of-wallet surface
- Primary Sources list += `OWASP LLM10:2025` (in both companions)
- Public ADR-034 with canonical LLM10 sub-pattern → owning-agent mapping table (audit deliverable)
- Example regeneration on `examples/agentic-app/` (Q5 RESOLVED at PRD time)
- Byte-identity verification on **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) — owner: `tester` agent
- LLM10 citation in prose-level `references` array on Category-12/13 (`D-{N}`) and Category-10/11 (`LLM-{N}`) findings (NOT `source_attribution` — that scope deferred to F-A3)
- Coverage Matrix update: LLM10:2025 transitions Partial → Covered; OWASP LLM Top 10:2025 = 10 of 10 Covered

### Out of Scope (Future Phases)

**Could Have (P2) — Not in F-5**:
- New `unbounded-consumption` agent — explicitly REJECTED per Heuristic A consolidation; reopening this would re-adjudicate every prior Heuristic A application
- New `denial-of-wallet` standalone agent — explicitly REJECTED per same Heuristic A reasoning; denial-of-wallet is the named attack class for `model-theft` Category 11
- Schema bump 1.8 → 1.9 — F-5 does not introduce a new ID prefix; reuses `D-{N}` and `LLM-{N}`
- BLP-01 Tier 2 ML-extraction or Mobile bundles (F-6 / F-7) — sequenced after F-5
- BLP-01 Tier 3 Web/API attestation (F-8) — sequenced last

**Won't Have — Explicitly excluded**:
- `finding-format-shared.md` consumers list edit — both target agents already at lines 12 and 16
- Functional orchestrator dispatch-rules edit — both agents already fully registered (multiple callsites verified)
- Runtime dependency additions — none required
- New baselines — F-5 reuses the existing 6-baseline byte-identity matrix (`web-app` / `microservices` / `ascii-web-api` / `mermaid-agentic-app` / `free-text-microservice` / `maestro-reference`) plus `agentic-app` mutation target

### Assumptions

- **A1**: `examples/agentic-app/` exhibits a sufficiently clean LLM-serving topology after F-3's Inter-Agent Communication Channel additions (Wave 3 mutation). F-4 left `examples/agentic-app/` untouched (F-4's mutation target was a NEW directory `examples/consumer-agent-app/` per ADR-033 D2 and the F-4 close-out memo in CLAUDE.md). **Validation**: architect inspects `examples/agentic-app/architecture.md` at plan time. ADR-034 Detection Calibration Note documents that the new Pattern Categories fire on **structural absence** of named control mechanisms (consistent with F-1 / F-2 / F-4 absence-style detection style); no fallback fixture needed.
- **A2**: ADR-034 is the next available ADR number at merge time. **Validation**: PRD-time verified — ADR-033 is the highest committed ADR (4 ADRs in the 30-range: 030, 031, 032, 033). Renumber is a one-line edit if needed.
- **A3**: No competing F-6 / F-7 PR is open at F-5 build time. **Validation**: F-6 and F-7 are at `stage:discover` or earlier as of PRD time; F-5 enters build first with no concurrency hedge required.
- **A4**: The canonical LLM10 sub-pattern → owning-agent mapping table in ADR-034 (Decision 3) is finalized at plan time by architect, with default leaning per Q1 (context-window-exhaustion in `denial-of-service`). PRD-time defaults are placeholders; architect-tractable.

### Constraints

**Technical**:
- `denial-of-service.md` line count must remain ≤120 (ADR-023 STRIDE tier cap).
- `model-theft.md` line count must remain ≤150 (ADR-023 AI tier cap).
- Categories 1–11 in `denial-of-service` companion and Categories 1–9 in `model-theft` companion must be byte-identical pre/post edit (ADR-023 Decision 3).
- Zero MAESTRO references on enriched files (ADR-023 Decision 2).
- Public ADR omits commercial framing (SDR-001 Option C).

**Calendar**:
- Build window starts 2026-04-29 (Wednesday); 2026-04-27 (today) is PRD day; 2026-04-28 (Tuesday) is plan day.

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Day 1 — 2026-04-29 (Wednesday)** — Build (rebalanced per team-lead MEDIUM-1)
- AM: `senior-backend-engineer` applies FR-1 (`denial-of-service.md` metadata + Detection Workflow + `## Purpose`) and FR-2 (`denial-of-service` companion Categories 12+13 + Primary Sources). **ADR-034 Proposed commit with mapping table populated complete** (5-row sub-pattern → owning-category map plus Q3 severity-hint annotation column — NOT skeleton, since Q1/Q3 resolved at PRD time).
- PM: applies FR-3 (`model-theft` companion Categories 10+11 + Primary Sources) and FR-4 (`model-theft.md` audit confirmation + `## Purpose`); regenerate `examples/agentic-app/` (FR-7); **early-signal byte-identity spot-check on 1–2 baselines** (e.g., `web-app` + `maestro-reference`) — pulls SC-9 verification forward to catch regen surprises before Day 2.

**Day 2 / Buffer — 2026-04-30 (Thursday)** — Verification + Delivery + Retrospective
- AM: byte-identity verification by `tester` agent (per team-lead MEDIUM-2) on remaining 4 non-LLM-serving baselines: `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` (SC-9; the 6 total includes the 2 spot-checked at Day 1 PM end: `web-app` + `maestro-reference`); ADR-034 Accepted transition; PR title pre-merge verification per Release Discipline subsection.
- PM: PR ready (mark non-draft via `gh pr ready`), squash-merge, post-merge release-please verification, **delivery retrospective filed at `specs/229-llm10-unbounded-consumption-verification/delivery.md`** (mirrors F-1 + F-2 + F-3 + F-4 precedent). The retrospective explicitly captures: (a) actual vs. estimated effort, (b) Heuristic A enrichment pattern at two-agent scope lessons (this is the **second execution** of the enrichment branch and the **first at two-agent scope** — the retrospective sets precedent for F-6 / F-7 Tier 2 bundles which may also use enrichment), (c) byte-identity preservation evidence (SC-9 grep proofs across 6 baselines), (d) any deviations from PRD timeline or scope, (e) the canonical sub-pattern → owning-agent mapping table as the audit deliverable lessons, (f) Q1 SPLIT resolution lessons (context-window exhaustion bifurcated into latency-DoS Cat 13 + cost-DoW Cat 11 — first BLP-01 sub-pattern with cross-agent vector decomposition), (g) ADR-034 Accepted-commit SHA-fill execution.

### Release Discipline — PR Title Contract

**Per `.claude/rules/git-workflow.md` (Conventional Commit PR Titles section)**: PR title MUST be `feat(229): <short description>` so that release-please fires on merge. The recommended title (architect / team-lead may refine at plan time): **`feat(229): llm10 unbounded consumption verification`** (or similar Conventional Commit form ≤70 chars).

**Two-step belt-and-suspenders enforcement**:
1. **Plan stage** — `/aod.plan` opens the draft PR via `gh pr create --draft --title "feat(229): llm10 unbounded consumption verification"`. The title is set correctly from the moment the draft is created.
2. **Deliver stage** — `/aod.deliver` re-verifies the PR title is Conventional-Commit-formatted before squash-merging. If a non-conventional title slipped through, retitle BEFORE merge: `gh pr edit <PR> --title "feat(229): ..."`. Post-merge, verify a release-please PR opened within ~30s; if not, push an empty `feat(229): ... release marker` commit.

**Rationale**: F-5 closes LLM10 on the Coverage Matrix and completes the OWASP LLM Top 10:2025 = 10 of 10 milestone. If the merge does not trigger a release-please PR, adopters consuming via SemVer-pinned dependencies do not see LLM10 coverage land. This rule was reinforced following the F-212 PR #213 release-please-skip incident — the mitigation is propagated to all in-flight PRDs since F-3.

**Type prefix**: MUST be `feat:` — F-5 is a user-visible feature enrichment that closes a top-10 gap, not a bug fix. `fix:` would mis-categorize the change. `docs:` / `chore:` would be hidden-bump and would not trigger a release.

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-27 | product-manager | 📋 Pending |
| `/aod.plan` (spec → plan → tasks) | 2026-04-28 | architect, team-lead | 📋 Pending |
| Build Day 1 (FR-1 through FR-7 implementation) | 2026-04-29 | senior-backend-engineer | 📋 Pending |
| SC-9 byte-identity verification (6 baselines + grep checks) | 2026-04-29 PM (1–2 spot-check) → 2026-04-30 AM (4 remaining) | tester | 📋 Pending |
| Buffer / Day 2 | 2026-04-30 | — | 📋 Pending |
| `/aod.deliver` (squash-merge + release-please verification) | 2026-04-30 | team-lead | 📋 Pending |
| ADR-034 Accepted commit + SHA fill | 2026-04-30 (post-merge) | architect | 📋 Pending |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ⚠️ Risks & Dependencies

### Technical Risks

**R1 — Example regeneration friction on `examples/agentic-app/`**
- **Likelihood**: Medium (multi-mutation now: F-3 added inter-agent findings, F-4 added trust-exploitation findings, F-5 adds LLM10 findings; the example architecture continues to accumulate mutation pressure)
- **Impact**: Low (delays Day 1 PM by ≤4 hours)
- **Mitigation**: Q5 RESOLVED at PRD time per architect adjudication: `examples/agentic-app/` confirmed as the F-5 mutation target (no fallback needed; ADR-034 documents structural-absence detection style). The **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) are byte-identical by construction, so the only mutation work is on `examples/agentic-app/`.
- **Contingency**: Buffer Day (2026-04-30) absorbs up to 8 hours of regeneration friction.

**R2 — Heuristic A two-agent scope pushback at architect review**
- **Likelihood**: Low (SDR-001 Decision 4 already locked the rule; F-3 ADR-032 demonstrated the enrichment branch at single-agent scope; ADR-032 lines 84 and 182 explicitly forecast F-5 will not need a schema bump and will operate at two-agent scope)
- **Impact**: High (could force re-scoping to a new agent, doubling effort and reopening Heuristic A on every prior consolidation)
- **Mitigation**: PRD Section "Three things the solution is deliberately NOT" pre-empts the most likely architect concerns. ADR-034 cross-references ADR-030 Decision 1 and ADR-032 to reuse the signal-class precedent.
- **Contingency**: If pushback occurs, escalate to a 30-minute architect-PM-team-lead alignment session before re-scoping. The Heuristic A enrichment pattern is foundational to BLP-01 Tier 2 (ML + Mobile bundles); abandoning it on F-5 would reopen scope on F-6 / F-7.

**R3 — Canonical sub-pattern → owning-agent mapping table boundary disputes**
- **Likelihood**: Medium (Q1 default lean places context-window-exhaustion in `denial-of-service`; an alternative reading would place it in `model-theft` as an extraction-driven cost class. Either is defensible.)
- **Impact**: Low (single-row mapping change is a one-paragraph edit in ADR-034 and a section-relocation in the affected companion file)
- **Mitigation**: Q1 deferred to architect at plan time with default lean documented. ADR-034 mapping table is finalized at plan time, not PRD time.
- **Contingency**: If architect disputes the default lean post-PRD, the mapping table relocates the single row; pattern category content is portable between the two companion files.

**R4 — Catalog drift between PRD time and build time**
- **Likelihood**: Very Low (taxonomy catalogs are stable; F-A1 fully delivered; LLM10 verified present in `schemas/taxonomy/owasp.yaml:373`; CWE-400 + CWE-770 verified present in `schemas/taxonomy/cwe.yaml`)
- **Impact**: Low (one-line schema edit if catalog ID changes)
- **Mitigation**: PRD-time verification of all 4 catalog citations (LLM10, CWE-400, CWE-770, LLM03). Re-verified at plan time per architect.
- **Contingency**: If catalog drift detected, re-cite or remove the offending citation; F-A2 referential-integrity validator catches drift programmatically.

**R5 — Severity-discrimination calibration on denial-of-wallet findings**
- **Likelihood**: Very Low (Q3 RESOLVED at PRD time per architect adjudication: HIGH default for cost-exposure findings (Cat 10/11); CRITICAL floor on Cat 11 ONLY when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent. Cat 12 / Cat 13 MEDIUM-HIGH default. Encoded as severity-hint annotation column in ADR-034 Decision 3 audit table.)
- **Impact**: Low (severity rule is finalized at PRD time; architect implements per ADR-034 Decision 3; minor calibration drift is a one-line edit to Cat 11 worked example)
- **Mitigation**: Q3 RESOLVED at PRD time per OWASP 3×3 reasoning. Architect implements per ADR-034 Decision 3 audit-table annotation column. Cat 11 worked example explicitly states the 2-condition Critical floor (multi-tenant freemium structure + both per-tenant token budget AND cost alerting absent).
- **Contingency**: If adopter calibration feedback diverges post-F-5, the severity rule is a one-line edit to the Pattern Category 11 mitigation narrative or the ADR-034 audit-table annotation column.

**R6 — Release-please skip if PR title misformatted**
- **Likelihood**: Low (rule explicitly stated; F-212 incident is fresh; F-3 + F-4 successfully landed `feat(NNN):` titles)
- **Impact**: High (no release ⇒ adopters consuming via SemVer-pinned deps do not receive LLM10 coverage; manual recovery via empty release-marker commit per F-212 precedent)
- **Mitigation**: Two-step belt-and-suspenders enforcement per `.claude/rules/git-workflow.md`: (1) `/aod.plan` opens draft PR with `feat(229): ...` title from the start; (2) `/aod.deliver` pre-merge re-verifies and retitles if needed; post-merge verifies release-please PR opened within ~30s.
- **Contingency**: If release-please skips post-merge, push empty marker commit `git commit --allow-empty -m "feat(229): llm10 unbounded consumption verification — release marker"` per F-212 recovery pattern. Buffer Day (2026-04-30) absorbs recovery time if needed.

### Business Risks

**R7 — BLP-01 Tier 1 momentum perception (closing milestone)**
- **Likelihood**: Very Low
- **Impact**: Low
- **Rationale**: F-5 closing the **last LLM Top 10 gap** within 1.5 working days demonstrates that the BLP-01 sequencing strategy converges to a clean 20-of-20 OWASP AI top-10 milestone. This is positive momentum, not negative — it validates the PDL → discover → define → plan → build cadence at the close of Tier 1 (F-1 through F-5 = all five Tier 1 closure features delivered in 11 calendar days from F-1 ship to F-5 ship).

**R8 — Closing-milestone over-attribution risk** (added per team-lead LOW-1)
- **Likelihood**: Low
- **Impact**: Medium
- **Rationale**: F-5 closes OWASP LLM Top 10:2025 to 10/10 Covered (combined with F-4's ASI09 closure → 20/20 OWASP AI top-10 entries). Risk: adopter-facing materials over-attribute the 20/20 milestone before adopter validation produces real-world signal.
- **Mitigation**: README / docs claim "detection coverage for 20/20 OWASP AI top-10 entries" (precise) rather than "comprehensive coverage" (overclaim); link adopter-facing claims to specific Pattern Categories rather than aggregate framework labels. Coverage Matrix transitions explicitly cite the closure features (LLM10 → F-5 / Feature 229; ASI09 → F-4 / Feature 224) per row.
- **Contingency**: If adopter feedback reveals coverage gaps post-F-5, resolution falls to BLP-01 Tier 2 (F-6 / F-7) re-planning rather than retroactive F-5 scope expansion.

### Dependencies

**Internal Dependencies (all satisfied at PRD time)**:
- F-A1 (Feature 180): taxonomy catalogs — **SATISFIED**
- F-A2 (Feature 189): source_attribution schema — **SATISFIED**
- F-B (Feature 194): coverage attestation PDF — **SATISFIED**
- F-1 (Feature 201): output-integrity agent — **SATISFIED** (informational precedent only)
- F-2 (Feature 206): misinformation agent — **SATISFIED** (informational precedent only)
- F-3 (Feature 219): tool-abuse enrichment — **SATISFIED** (architectural dependency: F-3 established the Heuristic A enrichment-branch precedent that F-5 operationalizes at two-agent scope; ADR-032 cross-referenced from ADR-034)
- F-4 (Feature 224): human-trust-exploitation agent — **SATISFIED** (informational precedent only)
- Existing `denial-of-service` and `model-theft` agents and their companion `detection-patterns.md` files — **SATISFIED** (verified at PRD time: 53/95 line agents; 179/154 line companions; both fully registered in dispatch)

**External Dependencies**: None.

**Dependency Graph**:
```
F-5 (this feature)
  ├─ Reads from: schemas/taxonomy/owasp.yaml (LLM10, LLM03)
  ├─ Reads from: schemas/taxonomy/cwe.yaml (CWE-400, CWE-770)
  ├─ Edits: .claude/agents/tachi/denial-of-service.md (additive metadata + Purpose)
  ├─ Edits: .claude/skills/tachi-denial-of-service/references/detection-patterns.md (additive Cat 12+13)
  ├─ Edits: .claude/agents/tachi/model-theft.md (audit + additive Purpose)
  ├─ Edits: .claude/skills/tachi-model-theft/references/detection-patterns.md (additive Cat 10+11)
  ├─ Creates: docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md (new)
  └─ Blocks: nothing (parallel-eligible with F-6, F-7, F-8 — all deferred Tier 2/3)
```

---

## ❓ Open Questions

| # | Question | Owner | Due | Status |
|---|----------|-------|-----|--------|
| Q1 | Where does context-window-exhaustion live — `denial-of-service` (infrastructure resource exhaustion class) or `model-theft` (extraction-driven cost class)? The ADR-034 audit table makes this call. | architect | plan | **RESOLVED at PRD time per architect adjudication: SPLIT — context-window-exhaustion lives in BOTH agents along the latency-DoS vs. cost-DoW axis.** Vector A (latency-driven DoS — attacker drives context-window to model max, legitimate users see degraded p99 latency, attacker intent is availability disruption) lives in **`denial-of-service` Pattern Category 13** (same signal class as Cat 12 inference-flooding; same-class as availability degradation; mitigation surface: max-context-window enforcement at API gateway, per-tenant context-window cap). Vector B (cost-amplification via context-window expansion — attacker drives context-window to maximum to inflate per-call cost; the "wallet" is the bill; attacker intent is economic damage) lives in **`model-theft` Pattern Category 11** (same signal class as Cat 10 cost-amplification; same-class as extraction-driven resource abuse; mitigation surface: per-tenant token budget hard-cap which is a 1:1 control with denial-of-wallet). The audit table in ADR-034 Decision 3 explicitly maps both vectors to disjoint owning categories — same architecture surfaces Cat 13 (latency) AND Cat 11 (cost), neither finding is duplicate, audit table assigns each to exactly one owning category. This avoids the cross-agent finding fragmentation risk while honoring the dual-attack-vector signal-class structure. |
| Q2 | Does the orchestrator's dispatch list need a cosmetic annotation update (e.g., extending `denial-of-service (CWE-400)` to `denial-of-service (CWE-400, LLM10)`) — like F-3's Q2 cosmetic dispatch annotation? | architect | plan | Researching — default **NO** (no annotation; the OWASP refs metadata extension on `denial-of-service.md` per FR-1 is sufficient for Coverage Matrix traceability). Architect-tractable at plan time. F-3's Q2 resolved YES (cosmetic-only); F-5 may resolve either way. |
| Q3 | Severity baseline — does F-5 set Critical severity floor for denial-of-wallet findings (Category 11 with no per-tenant token budget AND no cost alerting), per the OWASP 3×3 matrix's worst-case quadrant? | architect | plan | **RESOLVED at PRD time per architect adjudication: Q3 = YES Critical FLOOR on denial-of-wallet conditional. The Critical floor applies ONLY when (a) multi-tenant freemium structure is structurally evident in the architecture AND (b) both per-tenant token budget AND cost alerting are absent. Otherwise HIGH default for cost-exposure findings (Cat 10/11). Cat 12 inference-flooding is MEDIUM-HIGH default; Cat 13 context-window-latency-DoS is MEDIUM-HIGH. Severity hint per sub-pattern is encoded in ADR-034 Decision 3 audit-table annotation column (likelihood × impact axes per OWASP 3×3 matrix). Worked example for Cat 11 explicitly states the 2-condition Critical floor.** |
| Q4 | How many new Pattern Categories total across both agents? Issue body suggests "at least 1 new per agent" as DoD floor. | architect | plan | **CONFIRMED at PRD time: 2 per agent (4 total)** — `denial-of-service` gains Cat 12 ("LLM Inference-Request Flooding and Token Exhaustion") + Cat 13 ("Context-Window Exhaustion — Latency-Driven Variant", Q1 SPLIT Vector A); `model-theft` gains Cat 10 ("Cost Amplification via Recursive or Cost-Asymmetric Prompting") + Cat 11 ("Denial-of-Wallet via Context-Window Cost Amplification", Q1 SPLIT Vector B + broader denial-of-wallet). Architect may merge into single category per agent (2 total floor) at plan time if the indicator surface justifies. |
| Q5 | Example regeneration target — `examples/agentic-app/` (proven mutation candidate from F-3) or new `examples/llm-serving-app/`? | architect | plan | **RESOLVED at PRD time per architect adjudication: Q5 = `examples/agentic-app/` confirmed as Q5 target.** No new architecture authoring needed; mutation candidate is multi-component LLM topology already exercised by F-3. ADR-034 includes a Detection Calibration Note clarifying that the new Pattern Categories 12/13 (denial-of-service) and 10/11 (model-theft) fire on **structural absence** of named control mechanisms — consistent with F-1 / F-2 / F-4 absence-style detection style. Acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention. |

---

## 📚 References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- F-4 PRD (precedent): `docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md`
- F-3 PRD (primary precedent — first enrichment-branch execution): `docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md`
- F-2 PRD (precedent): `docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md`
- F-1 PRD (precedent): `docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md`

### Strategic Documentation
- BLP-01 Strategy (private): `_internal/strategy/BLP-01-threat-coverage.md` §7 F-5 (line 861), Coverage Matrix line 278 (LLM10:2025 = Partial)
- SDR-001 Strategy Decision Record (private): `_internal/strategy/SDR-001-threat-coverage-strategy.md` Decision 4 (Heuristic A)
- GUIDE-threat-coverage-research (private): `_internal/strategy/GUIDE-threat-coverage-research.md` §2 OWASP LLM Top 10:2025 + §11 Heuristic A signal-class taxonomy

### Architecture Decision Records (public)
- ADR-021 SOURCE_DATE_EPOCH determinism: `docs/architecture/02_ADRs/ADR-021-source-date-epoch.md`
- ADR-023 Threat Agent Skill References Pattern: `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (Decision 1, 2, 3)
- ADR-027 Taxonomy Crosswalk Schema: `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 Source Attribution Schema Extension: `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-029 Coverage Attestation Report Section: `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
- ADR-030 Output Integrity Agent: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` (Decision 1 Heuristic A signal-class taxonomy)
- ADR-031 Misinformation Agent: `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` (Decision 8 regex minor-bump rule — referenced as the asymmetry: F-5 does not invoke it)
- ADR-032 ASI07 Tool-Abuse Enrichment: `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` (**direct precedent — first enrichment-branch execution at single-agent scope; lines 84 and 182 explicitly forecast F-5 will not need a schema bump**)
- ADR-033 Human-Trust-Exploitation Agent: `docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md` (D2 ASI09 sub-scope carve-up — structural sibling to F-5's two-agent enrichment)

### Technical References
- Existing `denial-of-service` agent: `.claude/agents/tachi/denial-of-service.md` (PRD-time: 53 lines)
- Existing `denial-of-service` detection patterns: `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` (PRD-time: 179 lines, ends at Cat 11)
- Existing `model-theft` agent: `.claude/agents/tachi/model-theft.md` (PRD-time: 95 lines)
- Existing `model-theft` detection patterns: `.claude/skills/tachi-model-theft/references/detection-patterns.md` (PRD-time: 154 lines, ends at Cat 9)
- Finding format (shared): `.claude/skills/tachi-shared/references/finding-format-shared.md` (PRD-time: lines 12 and 16 enumerate `denial-of-service` and `model-theft` in consumers list)
- Severity bands (shared): `.claude/skills/tachi-shared/references/severity-bands-shared.md`
- Orchestrator dispatch: `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (PRD-time: lines 73, 109, 157 enumerate both agents)
- Orchestrator: `.claude/agents/tachi/orchestrator.md` (PRD-time: lines 37, 42, 298, 372 enumerate both agents)
- Taxonomy catalogs: `schemas/taxonomy/owasp.yaml` (LLM10 at line 373), `schemas/taxonomy/cwe.yaml` (CWE-400 at 130, CWE-770 at 182), `schemas/taxonomy/mitre-attack.yaml` (T1496 verified absent)
- Finding schema: `schemas/finding.yaml` (v1.8 post-F-4 baseline; no bump in F-5)

### External Resources
- OWASP LLM Top 10:2025: https://genai.owasp.org/llm-top-10/
- OWASP LLM10:2025 Unbounded Consumption: https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/
- MITRE ATT&CK T1496 Resource Hijacking: https://attack.mitre.org/techniques/T1496/ (text-only cross-reference; not catalog-resolvable)
- NIST AI 600-1 §2.5 / §2.6: https://www.nist.gov/itl/ai-risk-management-framework (adjacent GAI-risk framing)

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [x] Problem statement is clear and user-focused (LLM10 surface gap; partial-coverage path produces incomplete signal)
- [x] User stories have measurable acceptance criteria (US-229-1, US-229-2, US-229-3 all carry Given/When/Then ACs)
- [x] Success metrics are defined and measurable (SC-1 through SC-14, all grep-checkable or programmatically verifiable)
- [x] Scope is realistic for timeline (1.5-day envelope; between F-3's 1 day and F-2's 2 days)
- [x] Risks and dependencies identified (7 risks, all dependencies satisfied at PRD time)
- [x] Aligns with product vision (closes LLM10 gap; completes 20-of-20 OWASP AI top-10 milestone; demonstrates Heuristic A enrichment pattern at two-agent scope)

**Architect** (architect):
- [ ] Technical requirements are clear (FR-1 through FR-8 specify exact files, lines, edits)
- [ ] Non-functional requirements are realistic (no perf change; byte-identity preserved)
- [ ] Dependencies are accurate (PRD-time verified across catalog files and host agent registration)
- [ ] Technical risks are identified (R1–R6)
- [ ] Architecture approach is sound (Heuristic A enrichment at two-agent scope per SDR-001 Decision 4 + ADR-032 precedent)

**Engineering Lead** (team-lead):
- [ ] Requirements are implementable (PRD-time baseline measurements support the effort estimate)
- [ ] Effort estimates are reasonable (1.5 working days; F-5 is structurally between F-3 and F-2)
- [ ] Team capacity is available (post-F-4 delivery, no competing builds in window)
- [ ] Timeline is realistic (2026-04-29 build day with 1-day buffer)

### Definition of Done

1. `denial-of-service.md` `owasp_references` extended with `OWASP LLM10:2025`; line count ≤120.
2. `denial-of-service.md` `## Purpose` extension naming the LLM-inference-exhaustion surface (1–3 lines).
3. `denial-of-service.md` Detection Workflow Step 5 references extended with LLM10:2025 exemplar mention.
4. `denial-of-service` companion `detection-patterns.md` Pattern Categories 12 + 13 appended (Q4 default; 1-category floor per Issue #229 DoD); existing Categories 1–11 byte-identical (grep-checkable).
5. `model-theft.md` `owasp_references` audit confirms `OWASP LLM10:2025` already present (zero net change); line count ≤150.
6. `model-theft.md` `## Purpose` extension naming the cost-amplification and denial-of-wallet surface (1–3 lines).
7. `model-theft` companion `detection-patterns.md` Pattern Categories 10 + 11 appended (Q4 default; 1-category floor per Issue #229 DoD); existing Categories 1–9 byte-identical (grep-checkable).
8. Primary Sources lists in both companions extended with `OWASP LLM10:2025`.
9. ADR-034 (next-available-number) Proposed → Accepted dual-commit landed; canonical sub-pattern → owning-agent mapping table embedded as Decision 3 (audit deliverable).
10. `examples/agentic-app/` (Q5 RESOLVED at PRD time) regenerated; ≥1 new `D-{N}` finding citing OWASP LLM10:2025 in its prose-level `references:` array AND ≥1 new `LLM-{N}` finding citing OWASP LLM10:2025 in its prose-level `references:` array.
11. **6 non-LLM-serving example baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. **`tester` agent verifies SC-9 6-baseline byte-identity gate** (separate from `senior-backend-engineer` who authors edits).
12. LLM10 citation in prose-level `references:` array on every Category-12/13 (`D-{N}`) and Category-10/11 (`LLM-{N}`) finding; all citations catalog-resolvable against `schemas/taxonomy/{owasp,cwe}.yaml`. **NOTE**: F-5 does NOT extend `source_attribution` populator wiring (deferred to F-A3 per ADR-028 Decision 6).
13. PR title is `feat(229): llm10 unbounded consumption verification` (or similar Conventional Commit form); PR squash-merged on main; release-please PR opens within ~30s.
14. Coverage Matrix updated: LLM10:2025 transitions Partial → Covered; OWASP LLM Top 10:2025 = 10 of 10 Covered; OWASP AI top-10 rollup = 20 of 20.
15. **Delivery retrospective filed at `specs/229-llm10-unbounded-consumption-verification/delivery.md`** (mirrors F-1 + F-2 + F-3 + F-4 precedent) capturing actual vs. estimated effort, Heuristic A two-agent enrichment-pattern lessons (second execution; first at two-agent scope), byte-identity preservation evidence (SC-9 grep proofs across 6 baselines), Q1 SPLIT resolution lessons (context-window exhaustion bifurcated into Cat 13 latency-DoS + Cat 11 cost-DoW — first BLP-01 sub-pattern with cross-agent vector decomposition), canonical sub-pattern mapping table audit-deliverable lessons, and any deviations from PRD.
16. **ADR-034 Accepted-commit SHA filled with squash-merge SHA** per ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 / ADR-032 / ADR-033 dual-commit precedent (per team-lead LOW-2).

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | 📋 Pending | 2026-04-27 | v2 revision drafted addressing architect CHANGES_REQUESTED (2 BLOCKING + 3 HIGH + 4 MEDIUM + 3 LOW) and team-lead APPROVED_WITH_CONCERNS (3 MEDIUM + 2 LOW). Resolution decisions absorbed inline: BLOCKING-1 narrow-scope (references-array only, F-A3 inheritance one-way); BLOCKING-2 6-baseline correction; HIGH-1 28-file inventory re-anchor + 24-file zero-edit; HIGH-2 hybrid heading structure on denial-of-service companion; HIGH-3 Q1 SPLIT (Cat 13 latency-DoS + Cat 11 cost-DoW); MEDIUM-1 fourth-producer framing dropped; MEDIUM-2 Q5 RESOLVED + structural-absence note; MEDIUM-3 ADR-032 cross-ref clarified; MEDIUM-4 Q3 RESOLVED via OWASP 3×3 (HIGH default + 2-condition CRITICAL floor); LOW-1 zero-MAESTRO scope corrected; LOW-2 A1 fixed (F-4 left agentic-app untouched); LOW-3 Quaternary Persona compressed. Team-lead concerns absorbed: Day 1 split rebalanced; tester role explicit; buffer-day priority order enumerated; R8 closing-milestone over-attribution; DoD-16 ADR-034 SHA fill. Q2 remains architect-tractable at plan time (cosmetic dispatch annotation; default-NO). 14 success criteria preserved (count unchanged); 3 user stories preserved (job-story structure + ACs updated for references-array clarification). Ready for Triad re-review. |
| Architect | architect | 📋 Pending | TBD | Awaiting v2 review (v1 issued CHANGES_REQUESTED 2/3/4/3) |
| Engineering Lead | team-lead | 📋 Pending | TBD | v1 issued APPROVED_WITH_CONCERNS 0/0/3/2; concerns absorbed inline in v2 |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-27 | product-manager | Initial PRD — F-5 Heuristic A enrichment of `denial-of-service` + `model-theft` for LLM10 coverage at two-agent scope |
| 2.0 | 2026-04-27 | product-manager | Revision per architect CHANGES_REQUESTED + team-lead APPROVED_WITH_CONCERNS. BLOCKING-1: dropped `source_attribution` populator wiring claim — F-5 cites LLM10 in prose-level `references` array only; F-A3 inheritance is one-way, F-5 does not block on F-A3. BLOCKING-2: 5 → 6 baselines (`maestro-reference` added). HIGH-1: 27 → 28 detection-tier file count baseline; 24-file zero-edit invariant. HIGH-2: SC-4 reworded to acknowledge hybrid heading structure of `denial-of-service/detection-patterns.md`. HIGH-3: Q1 RESOLVED at PRD time as SPLIT — context-window-exhaustion lives in BOTH agents (Cat 13 latency-DoS / Cat 11 cost-DoW). MEDIUM-1: SC-13 "fourth net-new producer" framing dropped. MEDIUM-2: Q5 RESOLVED to `examples/agentic-app/` with structural-absence detection note. MEDIUM-3: ADR-032 cross-ref language clarified. MEDIUM-4: Q3 RESOLVED with OWASP 3×3 reasoning (HIGH default + CRITICAL floor on 2-condition denial-of-wallet). LOW-1: ADR-034 zero-MAESTRO scope correctly bounded to 4 edited files. LOW-2: A1 corrected (F-4 left agentic-app untouched). LOW-3: Quaternary Persona compressed to one-line callout. Team-lead MEDIUM-1: Day 1 PM rebalanced — ADR-034 mapping table populated complete at Day 1 AM; spot-check pulled forward to Day 1 PM. Team-lead MEDIUM-2: tester role for SC-9 explicitly assigned. Team-lead MEDIUM-3: buffer-day priority order enumerated. Team-lead LOW-1: R8 closing-milestone over-attribution risk added. Team-lead LOW-2: ADR-034 SHA-fill DoD bullet 16 added. |
