# ADR-034: LLM10:2025 Unbounded Consumption Audit (Heuristic A Two-Agent Enrichment)

**Status**: Accepted
**Date**: 2026-04-27 (Proposed at Wave 1.1 commit `3adacc8`; Accepted at Wave 3 T040 — post-Wave 2 example regen + Wave 3 tester verification confirmed)
**Deciders**: Architect (tachi project)
**Feature**: [229-llm10-unbounded-consumption-verification](../../../specs/229-llm10-unbounded-consumption-verification/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean-agent + additive-only shared-reference Decision 3 — F-5 follows the additive-only edit discipline at two-agent scope), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy crosswalk — F-5 cites OWASP LLM10 / LLM03 + CWE-400 / CWE-770), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 source_attribution schema — Decision 6 F-A3 deferral; F-5 cites LLM10 in references-array only, populator wiring deferred), [ADR-030](ADR-030-output-integrity-agent.md) (F-1 — Decision 1 signal-class taxonomy in LLM tier as the precedent applied at two-agent scope here), [ADR-031](ADR-031-misinformation-agent.md) (F-2 — Decision 8 regex-alternation minor-bump rule cross-referenced as the **asymmetry** F-5 does NOT invoke), [ADR-032](ADR-032-asi07-tool-abuse-enrichment.md) (F-3 — **direct precedent** at single-agent enrichment scope; lines 84+182 forecast F-5 will not need a schema bump — fulfilled), [ADR-033](ADR-033-human-trust-exploitation-agent.md) (F-4 — Decision 2 sub-scope carve-up structural sibling; ADR-033 carved one OWASP entry across two host agents at the documentation layer; ADR-034 enriches one OWASP entry across two host agents at the pattern-catalog layer)

---

## Context

Tachi's STRIDE + AI threat-modeling pipeline ships, post-F-4 (Feature 224 merged 2026-04-26), 8 AI-tier detection agents covering input-side attacker injection (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`), downstream-execution-sanitization (`output-integrity` — LLM05:2025), factual-integrity (`misinformation` — LLM09:2025), and agent-to-human communication-axis trust exploitation (`human-trust-exploitation` — ASI09:2026 communication axis). What remains silent on the OWASP LLM Top 10 is **LLM10:2025 Unbounded Consumption** — recorded as **Partial** on the BLP-01 Coverage Matrix because the existing `denial-of-service` STRIDE-tier agent and `model-theft` AI-tier agent each cover adjacent infrastructure-availability and economic-damage surfaces but do not name the LLM-tier inference-exhaustion + cost-amplification + denial-of-wallet sub-classes explicitly.

BLP-01 (Better LLM Protection initiative, documented in `_internal/strategy/BLP-01.md`) identifies LLM10:2025 as Tier 1 priority F-5, following F-1 (Feature 201) `output-integrity`, F-2 (Feature 206) `misinformation`, F-3 (Feature 219) `tool-abuse` enrichment for ASI07:2026, and F-4 (Feature 224) `human-trust-exploitation` for ASI09:2026 communication axis. **F-5 is the second execution of the Heuristic A enrichment branch** (after F-3 single-agent scope) and the **first at two-agent scope**: rather than authoring an `llm10-unbounded-consumption` agent as a 9th AI-tier sibling, F-5 enriches BOTH the existing `denial-of-service` STRIDE-tier agent (with two new Pattern Categories — 12: LLM Inference-Request Flooding and Token Exhaustion; 13: Context-Window Exhaustion Latency-Driven Variant — Q1 SPLIT Vector A) AND the existing `model-theft` AI-tier agent (with two new Pattern Categories — 10: Cost Amplification via Recursive or Cost-Asymmetric Prompting; 11: Denial-of-Wallet via Context-Window Cost Amplification — Q1 SPLIT Vector B + broader DoW). The rationale — signal-class identity at two-agent scope, with explicit cross-agent vector decomposition for context-window exhaustion (Q1 SPLIT) — is operationalized below.

The feature ships purely additive edits to four existing files plus this public ADR: (1) `denial-of-service.md` metadata `owasp_references` += `[OWASP LLM10:2025]`, `## Purpose` 1-3 line extension naming the LLM-inference-exhaustion surface, Detection Workflow Step 5 references += `OWASP LLM10:2025`; (2) `tachi-denial-of-service/references/detection-patterns.md` appends Pattern Category 12 + Pattern Category 13 + Pattern Category Disambiguation subsection + Primary Sources extension; (3) `model-theft.md` `owasp_references` audit-confirmed (LLM10 already present — zero net change), `## Purpose` 1-3 line extension naming the cost-amplification + denial-of-wallet surface; (4) `tachi-model-theft/references/detection-patterns.md` appends Pattern Category 10 + Pattern Category 11 + Pattern Category Disambiguation subsection + Primary Sources extension; (5) ADR-034 (this file) under Proposed → Accepted dual-commit per ADR-027/028/029/030/031/032/033 precedent.

The schema `schemas/finding.yaml` is **not modified** — F-5 reuses the existing `D-{N}` and `LLM-{N}` prefixes and is the **second BLP-01 detection feature with no schema bump** (after F-3) and the **first at two-agent enrichment scope**, an asymmetry with F-1's 1.5 → 1.6 bump, F-2's 1.6 → 1.7 bump, and F-4's 1.7 → 1.8 bump. The asymmetry is recorded explicitly in Decision 4 below.

PRD 229 was approved 2026-04-27 with full Triad sign-off (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS — all HIGH/MEDIUM concerns resolved inline before sign-off). The spec (PM APPROVED), plan (PM + Architect APPROVED), and tasks (PM + Architect + Team-Lead APPROVED) all landed 2026-04-27. The Heuristic A enrichment-vs-new-agent decision at two-agent scope was inherited from SDR-001 Decision 4 + ADR-030 Decision 1 + ADR-032 (direct precedent) and re-verified by the architect at Wave 1.0 T003 in `.aod/results/wave1-architect-reverify.md`. Decisions 1 and 4 below record the inheritance and asymmetry with explicit cross-references.

### Constraints

- **24-file zero-edit invariant** (spec SC-017, FR-018 — ADR-023 lineage extended by F-1 + F-2 + F-4): F-5 MUST NOT edit any of the 12 other AI/STRIDE threat-agent files at `.claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,privilege-escalation,prompt-injection,data-poisoning,agent-autonomy,tool-abuse,output-integrity,misinformation,human-trust-exploitation}.md` or their 12 companion `detection-patterns.md` reference files. ADR-023 Decision 2 stabilized the original 22-file scope in Feature 082; F-1 added 2 (output-integrity agent + companion); F-2 added 2 (misinformation agent + companion); F-3 modified `tool-abuse.md` + companion in-place (no new files); F-4 added 2 (human-trust-exploitation agent + companion). Post-F-4 the inventory covers 28 detection files; F-5 edits 4 host files (`denial-of-service.md` + companion + `model-theft.md` + companion) and the remaining 24 stay byte-identical. The host files were ALREADY part of the in-scope detection tier per ADR-023 — F-5 follows ADR-023 Decision 3's additive-only edit discipline to preserve byte-identity on Pattern Categories 1-11 (DoS) + Pattern Categories 1-9 (model-theft) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (model-theft only — DoS companion has hybrid heading structure and lacks this section) regions.

- **Byte-identity backward compatibility** (spec SC-014, FR-015 — ADR-021 lineage): the **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. The LLM-serving topology gate (FR-015) enforces zero Cat-12/13 + Cat-10/11 emissions on architectures lacking LLM-serving indicators (declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology). The 6 baselines fall in non-qualifying topology by construction (PRD-time architect-verified at T022 via `.aod/results/wave1-llm-serving-topology-check.md`). The 7th baseline (`agentic-app` per PRD Q5 RESOLVED) is the expected mutation candidate per FR-9.

- **Zero new runtime or developer dependencies** (spec SC-016): empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `package.json`, `package-lock.json`. `pyyaml` and `pytest` remain developer-only per Feature 128 precedent. No new orchestrator phase, no new LLM-judgment pathway, no new HTTP fetch.

- **F-A2 referential-integrity contract** (spec SC-019 — ADR-028 Decision 5 lineage; F-A3 deferral per ADR-028 Decision 6): every emitted Cat 12/13 `D-{N}` finding's `references` array MUST cite `OWASP LLM10:2025 — Unbounded Consumption` and `CWE-400 Uncontrolled Resource Consumption` at minimum (CWE-770 applicable per architecture indicator). Every emitted Cat 10/11 `LLM-{N}` finding's `references` array MUST cite `OWASP LLM10:2025 — Unbounded Consumption` (LLM03:2025 applicable for cost-flow-through-third-party-models adjacency). **F-5 does NOT extend `source_attribution` populator wiring on either host agent** — the `source_attribution: []` empty-array default per finding-format-shared.md is preserved. F-A3 will own the populator wiring (one-way inheritance: F-5 → F-A3). The validator at `scripts/tachi_parsers.py:826` is regex-agnostic and does not enforce on absent populator wiring; it enforces on populated wiring. F-5 is the first BLP-01 detection feature to defer populator wiring per Decision 8 below.

- **MITRE ATT&CK T1496 prose-only invariant** (spec FR-equivalent): T1496 (Resource Hijacking) is referenced in Cat 10 + Cat 11 mitigation prose as text-only cross-reference; T1496 is NOT in `references` array because it is not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` as of PRD-time + plan-time + build-time grep checks. F-5 preserves this invariant by construction (T038 + T039 grep verification at Wave 2; T056 references-array fixture validation at Wave 3).

- **Zero MAESTRO references** in all four enriched files post-edit (spec SC-020): grep-auditable invariant per ADR-023 Decision 2. PRD-time baseline: zero MAESTRO references in all four files. F-5 preserves this invariant by construction.

- **No schema bump** (spec FR-013 / SC-018): `schemas/finding.yaml` `schema_version` remains `"1.8"` post-F-5. The `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` (post-F-4 state). F-5 reuses the existing `D` and `LLM` prefixes and is therefore the **second BLP-01 detection feature with no schema bump** (after F-3) — a deliberate asymmetry with F-1 (1.5 → 1.6), F-2 (1.6 → 1.7), and F-4 (1.7 → 1.8). Decision 4 below records the asymmetry with explicit ADR-031 Decision 8 cross-reference.

- **No consumers-list edit** (spec FR-014): `.claude/skills/tachi-shared/references/finding-format-shared.md` is byte-identical post-F-5. PRD-time + plan-time + build-time verification: `denial-of-service` already at line 12 and `model-theft` already at line 16 of the consumers list. F-5 reuses both existing consumer registrations — no new agent file means no new consumer.

- **No functional orchestrator/dispatch edit** (spec FR-019 / SC-021): `.claude/agents/tachi/orchestrator.md` is byte-identical post-F-5. `.claude/skills/tachi-orchestration/references/dispatch-rules.md` receives **zero** functional edits. The optional cosmetic Q2 annotation (extending `denial-of-service` entry to cite LLM10 for parity with `model-theft`'s existing line-73 LLM10 annotation) was decided **NO** at architect plan-day decision (recorded in `.aod/results/wave1-q2-cosmetic-annotation-decision.md`). The dispatch-tier shows zero diff against `main`.

- **LLM-serving topology gate** (spec FR-015 — correctness BLOCKER + byte-identity preservation gate): Pattern Categories 12 + 13 (DoS) + Pattern Categories 10 + 11 (model-theft) emit zero findings on architectures lacking LLM-serving indicators. The gate is enforced by anti-indicator subsections in the pattern catalog plus pattern-prose framing. The 6 non-LLM-serving baselines are guaranteed byte-identical by construction; the gate does correctness + byte-identity double-duty under SOURCE_DATE_EPOCH.

- **Q1 SPLIT cross-agent vector decomposition** (spec FR-2 + FR-3): context-window exhaustion is decomposed across two owning categories — Vector A (latency-driven availability disruption) lives in DoS Cat 13; Vector B (cost-amplification → economic damage) lives in model-theft Cat 11. Same architecture surfaces both — neither is a duplicate. The 5-row mapping table in Decision 3 below assigns each LLM10 sub-pattern to exactly one owning category.

- **Q3 severity-floor 2-condition rule** (spec FR-equivalent): Cat 11 emits at HIGH default; CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident in architecture AND (b) BOTH per-tenant token budget AND cost alerting absent. Single-tenant economic exposure with absent controls computes HIGH (not CRITICAL).

---

## Decision

We adopt the Heuristic A enrichment of the existing `denial-of-service` and `model-theft` agents for OWASP LLM10:2025 closure per the **9 numbered decisions** below. The feature ships with **zero new agent files**, **zero new skill directories**, **zero schema bumps**, **zero consumers-list edits**, **zero functional orchestrator edits**, and **zero `source_attribution` populator wiring extensions** — F-5 is structurally the second-smallest BLP-01 detection delivery to date (after F-3 single-agent scope) and the **first at two-agent enrichment scope**. Four additive file edits (`denial-of-service.md`, DoS companion, `model-theft.md`, model-theft companion), one new ADR (this file under Proposed → Accepted), one regenerated example (`agentic-app` per Q5 RESOLVED), and zero functional dispatch edits constitute the entire delivery surface. The 24-file zero-edit invariant (post-F-4 inventory: 28 detection files; F-5 edits 4 host files; 24 unchanged) and the 6-baseline byte-identity gate are preserved by construction.

### Decision 1 — Heuristic A enrichment vs. new agent at TWO-AGENT scope — signal-class identity rationale

We enrich BOTH the existing `denial-of-service` STRIDE-tier agent (with Pattern Categories 12 + 13) AND the existing `model-theft` AI-tier agent (with Pattern Categories 10 + 11) rather than authoring a new `llm10-unbounded-consumption` agent as a 9th AI-tier sibling. The rationale rests on **signal-class identity at two-agent scope**:

| Signal class — sub-pattern | Owning agent / category | Pre-existing host scope (rationale) |
|---|---|---|
| LLM inference-request flooding (per-tenant QPS exhaustion on inference endpoints) | `denial-of-service` Cat 12 | DoS Cat 9 (CWE Top 25 generic resource exhaustion) and Cat 10 (network flood) cover infrastructure-tier availability — Cat 12 extends to LLM-API-gateway-specific availability surface. Same signal class as Cat 9/10 (resource exhaustion) at a different abstraction layer (LLM-tier vs. infrastructure-tier). |
| Context-window exhaustion — latency-driven Vector A (availability disruption) | `denial-of-service` Cat 13 | Same signal class as Cat 12 (LLM-tier availability surface). Q1 SPLIT decomposition: Vector A targets per-request latency budget; intent is availability disruption. |
| Context-window exhaustion — cost-driven Vector B (economic damage) | `model-theft` Cat 11 | Q1 SPLIT decomposition: Vector B targets per-call cost; intent is economic damage. Same signal class as model-theft Cat 6 (Unbounded Inference Consumption — pre-existing per-tenant quota / cost-control / billing-attribution gaps at the abstraction level). |
| Cost amplification via recursive or cost-asymmetric prompting | `model-theft` Cat 10 | Same signal class as model-theft Cat 6 (Unbounded Inference Consumption). Cat 10 detects the specific attack vectors (recursive prompts, output-asymmetric queries, output-token caps misconfigured) below the abstraction level Cat 6 covers. |
| Denial-of-wallet (broader economic-attack class) | `model-theft` Cat 11 | The wallet is the bill, not the system uptime — denial-of-wallet is an economic attack distinct from latency-driven DoS. Same signal class as model-theft Cat 6. Cat 11 systematizes the named attack class (multi-tenant denial-of-wallet, freemium exploitation) below the abstraction level Cat 6 covers. |

**Heuristic A signal-class discipline test**: are F-5 sub-patterns more naturally adjacent to existing host-agent Pattern Categories (DoS Cat 9/10/11 / model-theft Cat 6) or to a new `llm10-unbounded-consumption` agent (separate agent file, separate trigger keyword set, separate dispatch path)? Architecture answer: ADJACENT to existing host-agent categories AT TWO-AGENT SCOPE. The five LLM10 sub-patterns naturally cleave by attacker intent (availability vs. economic damage), and that cleave aligns precisely with the existing `denial-of-service` (availability) vs. `model-theft` (cost / extraction / model-asset risk) signal-class boundary. Splitting F-5 into a new agent would (a) duplicate trigger keywords across DoS + model-theft + new agent, (b) fragment the LLM10 attack surface across three artificial agent boundaries, (c) force ID-prefix segmentation across what is structurally two emission streams (`D-{N}` for availability surface + `LLM-{N}` for economic-damage surface).

**Authority acknowledgment — inheritance, not re-adjudication**: ADR-030 Decision 1 established the **signal-class taxonomy in the LLM tier** (input-side / downstream-execution-sanitization / factual-integrity / psychology-linguistics — three-way partition formalized at F-1; F-2 inherited the partition for factual-integrity). **F-5 demonstrates the same signal-class discipline applied across two host agents simultaneously** — the LLM10 surface decomposes naturally into a DoS-host-side (availability axis) and a model-theft-host-side (economic-damage axis). This is **inheritance of the rule** at two-agent scope, not re-adjudication. ADR-032 (F-3) established the enrichment branch at single-agent scope; ADR-034 (this file) extends the precedent to two-agent scope. SDR-001 Decision 4 is the locked resolution at the BLP-01 strategy tier; this Decision 1 is the operational realization at the F-5 architectural tier.

**Forward scope marker**: F-6 / F-7 Tier 2 ML+Mobile bundles may invoke the **enrichment** branch at single-agent or multi-agent scope depending on signal-class analysis at PRD time; F-5 establishes two-agent enrichment as a viable operational pattern beyond F-3's single-agent precedent.

### Decision 2 — Additive-only edit discipline per ADR-023 Decision 3 at two-agent scope

We follow ADR-023 Decision 3's **additive-only edit discipline** at two-agent scope. F-5 is the second BLP-01 feature (after F-3) where additive-only edits to existing files are the **entire** delivery surface, and the **first at two-agent scope**.

Specifically:

- **`denial-of-service.md`**: 3 additive edits — (1) metadata YAML `owasp_references` list extension (one-token append: `OWASP LLM10:2025 — Unbounded Consumption` as 10th entry); (2) `## Purpose` section 1-3 line extension naming the LLM-inference-exhaustion surface (the pre-existing prose paragraph remains byte-identical — extension is appended, not rewritten); (3) Detection Workflow Step 5 references list extension (`OWASP LLM10:2025` exemplar mention; pre-existing references preserved byte-identically).
- **`tachi-denial-of-service/references/detection-patterns.md`**: 4 additive edits — (1) Pattern Category 12 appended after Category 11; (2) Pattern Category 13 appended after Category 12; (3) Pattern Category Disambiguation subsection appended after Category 13 (per Decision 7 below); (4) Primary Sources list extension with 1 entry (LLM10). Pre-existing Categories 1-11 + `## Overview` + `## Targeted DFD Element Types` + pre-existing Primary Sources entries remain byte-identical pre/post edit. (DoS companion has hybrid heading structure with 8 thematic groupings for Cat 1-8 + 3 named `## Pattern Category 9/10/11` headings; it does NOT have a `## Trigger Keywords` section, asymmetric to model-theft companion.)
- **`model-theft.md`**: 2 additive edits — (1) `owasp_references` audit-confirmed (LLM10 already present at PRD-time + plan-time + build-time verification — zero net change to the metadata block; audit confirmation noted in commit message); (2) `## Purpose` section 1-3 line extension naming the cost-amplification + denial-of-wallet surface (pre-existing prose paragraph remains byte-identical).
- **`tachi-model-theft/references/detection-patterns.md`**: 4 additive edits — (1) Pattern Category 10 appended after Category 9; (2) Pattern Category 11 appended after Category 10; (3) Pattern Category Disambiguation subsection appended after Category 11 (per Decision 7 below); (4) Primary Sources list extension with 1 entry (LLM10). Pre-existing Categories 1-9 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (line 19) + pre-existing Primary Sources entries remain byte-identical pre/post edit.

**Byte-identity proof**: a structural diff of pre/post `tachi-denial-of-service/references/detection-patterns.md` returns empty for the unchanged regions (Categories 1-11 + `## Overview` + `## Targeted DFD Element Types`). A structural diff of pre/post `tachi-model-theft/references/detection-patterns.md` returns empty for the unchanged regions (Categories 1-9 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords`). T031 + T032 Wave 2 EOD validation enforces both proofs as BLOCKER gates per spec SC-008 + SC-010.

### Decision 3 — Canonical 5-row LLM10 sub-pattern → owning-agent mapping table (audit deliverable)

The LLM10 surface decomposes into 5 named sub-patterns per spec FR-1 + FR-2 + FR-3 + Q1 SPLIT decision. The canonical mapping table assigns each sub-pattern to exactly one owning agent + Pattern Category, with severity-hint annotation per Q3 RESOLVED:

| LLM10 sub-pattern | Owning agent | Owning Pattern Category | Severity hint (Q3) |
|---|---|---|---|
| Inference-request flooding (per-tenant QPS exhaustion on LLM endpoints; token-budget exhaustion via unbounded prompt-size) | `denial-of-service` | Cat 12 | MEDIUM-HIGH default (HIGH on multi-tenant LLM-serving SaaS without per-tenant QPS) |
| Context-window exhaustion — Vector A (latency-driven; per-request latency to per-tenant timeout via 32k+ token mega-history) | `denial-of-service` | Cat 13 | MEDIUM-HIGH default (HIGH on consumer-facing chatbot with adversarial conversation history) |
| Context-window exhaustion — Vector B (cost-driven; per-call cost inflation via context-window saturation) | `model-theft` | Cat 11 | HIGH default; CRITICAL floor ONLY when multi-tenant freemium AND BOTH per-tenant token budget + cost alerting absent (Q3 2-condition rule) |
| Cost amplification (recursive / cost-asymmetric prompting; output-token amplification with 100x cost-revenue ratio) | `model-theft` | Cat 10 | HIGH default |
| Denial-of-wallet (broader economic-attack class; multi-tenant freemium exploitation; cost-velocity attacks driving operator bill to ruin) | `model-theft` | Cat 11 | HIGH default; CRITICAL floor on Q3 2-condition rule |

**Audit-deliverable framing**: the table operationalizes Q1 SPLIT cross-agent vector decomposition (Vector A → DoS Cat 13; Vector B → model-theft Cat 11) and Q3 severity-floor 2-condition CRITICAL rule. The same architecture exhibiting Vector A AND Vector B emits a `D-{N}` finding (Cat 13) AND an `LLM-{N}` finding (Cat 11) — both cohesive under their respective `category: denial-of-service` and `category: llm` enums in `threats.md` and `threat-report.md`. They are not duplicates; they describe distinct attacker intents (availability disruption vs. economic damage) on the same architectural surface.

**Severity-hint annotation column**: per Q3 RESOLVED 2-condition CRITICAL floor — a Cat 11 finding emits at HIGH default; CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident in architecture (e.g., B2C consumer chatbot SaaS with freemium tier) AND (b) BOTH per-tenant token budget AND cost alerting absent. Single-tenant economic exposure with absent controls computes HIGH (not CRITICAL). The 2-condition rule is encoded in the Cat 11 worked-example narrative (Wave 2 T027) and the freemium-floor fixture (Wave 1.1 T009).

**Q1 SPLIT operational discipline**: the 5-row mapping table makes explicit that context-window exhaustion is one attack class with two distinct outcomes, and each outcome lives in exactly one owning category. The mapping table is the canonical source-of-truth — Wave 2 T024 + T025 implementation, Wave 4 T069 SC-012 verification, and code-reviewer R7 boundary-clarity check at T058 all reference this table.

### Decision 4 — No schema bump — second BLP-01 detection feature reusing existing prefixes (first at two-agent scope)

**F-5 does NOT modify `schemas/finding.yaml`. The `schema_version` remains `"1.8"` post-F-5. The `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` (post-F-4 state).**

F-5 reuses the existing `D` prefix for Cat 12/13 findings (DoS host) and the existing `LLM` prefix for Cat 10/11 findings (model-theft host). The pattern catalog already populates `D-{N}` IDs for DoS Categories 1-11 (sequential numbering across the agent's emission); Categories 12-13 extend the same single-namespace ID space without prefix segmentation. Same for model-theft `LLM-{N}` Categories 1-9 → 10-11.

**Asymmetry with F-1, F-2, and F-4 — explicit cross-reference to ADR-031 Decision 8**: ADR-031 Decision 8 recorded F-2 as the second application of the regex-alternation minor-bump rule (1.6 → 1.7 adding `MI` prefix); ADR-030 Decision 8 was the first application (1.5 → 1.6 adding `OI` prefix); ADR-033 Decision 8 was the third application (1.7 → 1.8 adding `TE` prefix). **F-5 is NOT an application of that rule. F-5 is the second asymmetry** (after F-3 ADR-032 Decision 3): the rule applies to features that introduce a **new signal-class identity** warranting a distinct ID prefix; F-5 introduces sub-classes within the existing `denial-of-service` and `model-theft` signal classes (LLM-tier inference exhaustion / cost amplification / denial-of-wallet) and therefore reuses the existing `D` and `LLM` prefixes without invoking the rule.

**Cross-reference to ADR-032 lines 84 + 182 forecast**: ADR-032 Decision 3 (F-3, lines 84 + 182) explicitly forecast that **F-5** would follow the enrichment branch like F-3 with no schema bump expected. **This Decision 4 fulfills the forecast.** The structural symmetry across F-3 (single-agent enrichment, no schema bump) and F-5 (two-agent enrichment, no schema bump) demonstrates that Heuristic A enrichment correctly avoids spurious schema bumps when signal-class identity is preserved, regardless of agent-count scope.

**Implications**: the no-schema-bump invariant at two-agent scope is the **operational signal** that Decision 1's signal-class identity claim is upheld across BOTH host agents. If F-5 had bumped the schema to add a new prefix (e.g., a hypothetical `UC` for unbounded-consumption), it would have implicitly claimed that LLM10 is a third distinct signal class from `denial-of-service` AND `model-theft` — which contradicts Decision 1.

### Decision 5 — No consumers-list edit — both agents already registered

We do NOT edit `.claude/skills/tachi-shared/references/finding-format-shared.md`. PRD-time + plan-time + build-time verification (re-confirmed at Wave 1.0 T003 in `.aod/results/wave1-architect-reverify.md`) shows `denial-of-service` already at line 12 and `model-theft` already at line 16 of the consumers list. Both registrations are reused by Categories 12-13 (DoS) and Categories 10-11 (model-theft) emissions identically to existing categories — both flow through the same shared finding-format contract.

**Contrast with F-1, F-2, F-4**: each added one new consumer (`output-integrity`, `misinformation`, `human-trust-exploitation`) at the consumers-list extension; each performed an additive edit to `finding-format-shared.md` per ADR-023 Decision 3. **F-5 has zero such edit at two-agent scope**: both host agents are already registered, and the new pattern categories ride the same registrations. This is the **second** ADR-023 Decision 3 invariant F-5 honors trivially (the first is the byte-identity invariant on Categories 1-11 (DoS) + Categories 1-9 (model-theft) in the pattern catalogs).

### Decision 6 — No functional orchestrator/dispatch edit — both agents already registered

We do NOT functionally edit `.claude/agents/tachi/orchestrator.md` or `.claude/skills/tachi-orchestration/references/dispatch-rules.md`. PRD-time + plan-time + build-time verification shows both `denial-of-service` and `model-theft` already registered across multiple callsites in both files. The dispatch trigger predicates and routing logic remain byte-identical post-F-5.

**Cosmetic Q2 annotation NOT applied** (per architect plan-day decision recorded in `.aod/results/wave1-q2-cosmetic-annotation-decision.md`): the optional one-token annotation extending `denial-of-service` entry to cite LLM10 for parity with `model-theft`'s existing line-73 LLM10 annotation was decided **NO** at plan-day. F-5 ships with **zero functional dispatch-tier touches** — `dispatch-rules.md` shows `git diff main` empty.

**Contrast with F-3's Q2 annotation**: ADR-032 Decision 5 / Feature 219 recorded the cosmetic annotation as YES at plan-day. F-5 plan-day default-NO is a deliberate difference: zero-functional-touch invariant at two-agent scope is the stronger discipline. The carve-out is unused; SC-021's zero-functional-touch claim is preserved cleanly.

### Decision 7 — Pattern Category Disambiguation (DoS Cat 9 vs. Cat 12/13 + model-theft Cat 6 vs. Cat 10/11)

We append a **Pattern Category Disambiguation** subsection to BOTH companion catalogs after the new pattern categories and before `## Primary Sources` per PRD FR-2. Each disambiguation carves the non-overlap contract between the pre-existing related pattern categories and the new LLM10 categories:

**DoS companion disambiguation** (Cat 9 vs. Cat 12 + 13):

- **Pattern Category 9** (CWE Top 25 Uncontrolled Resource Consumption and Algorithmic Complexity) detects generic uncontrolled resource consumption applicable to any HTTP service — regex-compile-on-untrusted-input (ReDoS), depth-unbounded XML or JSON parsing (billion laughs, deeply nested), archive expansion-ratio caps (zip bomb), hash-collision flooding, recursive-algorithm depth bounds. Mitigation surfaces are language- and library-level controls.
- **Pattern Categories 12 + 13** detect LLM-API-gateway-specific surfaces — per-tenant QPS on inference endpoints, max-prompt-token enforcement, per-tenant token budget, max-context-window enforcement, context-window monitoring, recursive-prompt-pattern detection. Mitigation surfaces are LLM-API-gateway-level controls.

Same architecture may legitimately surface Cat 9 + Cat 12 + Cat 13 findings; they are not duplicates and MUST NOT be merged in `threat-report.md`.

**model-theft companion disambiguation** (Cat 6 vs. Cat 10 + 11):

- **Pattern Category 6** (Unbounded Inference Consumption — pre-existing) detects per-tenant quota / cost-control / billing-attribution gaps at the **abstraction level** — generic naming of cost-control hygiene gaps applicable across model-serving deployments.
- **Pattern Category 10** detects **specific cost-amplification attack vectors** (recursive prompts, output-asymmetric queries, output-token caps misconfigured) below the abstraction level Cat 6 covers.
- **Pattern Category 11** detects the **named denial-of-wallet economic attack class** (multi-tenant freemium exploitation, cost-velocity attacks, automated tenant suspension absent) below the abstraction level Cat 6 covers.

Same architecture may legitimately surface Cat 6 + Cat 10 + Cat 11 findings; they are not duplicates.

**Q1 SPLIT cross-agent disambiguation**: Vector A latency-driven DoS lives in `denial-of-service` Cat 13; Vector B cost-driven denial-of-wallet lives in `model-theft` Cat 11 per the 5-row mapping table in Decision 3. Same architecture surfaces both — they are cross-agent siblings (each in its own `category:` enum), not duplicates.

**Why this Decision is in the public ADR**: the carves are structural invariants of the pattern catalogs. Code-reviewer R7 verification at Wave 3 T058 enforces boundary clarity in both companions' prose; Decision 7 above provides the architectural rationale that the prose and the code-review check both reference.

### Decision 8 — No `source_attribution` populator wiring extension — F-A3 deferral

**F-5 does NOT extend `source_attribution` populator wiring on either host agent.** The empty `source_attribution: []` array per finding-format-shared.md default is preserved on every Cat 12/13 + Cat 10/11 finding emitted by F-5. F-5 cites OWASP LLM10:2025 + CWE-400 / CWE-770 / LLM03 in the prose-level `references` array (existing finding-YAML field since v1.0), NOT in `source_attribution`.

**F-A3 deferral lineage** per ADR-028 Decision 6: F-A3 (the deferred populator wiring extension feature) will own the populator wiring contract for all consumers of `source_attribution`. Until F-A3 ships, only host agents that actively populate `source_attribution` (currently F-1 OI-{N}, F-2 MI-{N}, F-3 enrichment branch via existing tool-abuse populator extension, F-4 TE-{N}) emit non-empty `source_attribution`. F-5 follows the **prose-only references** path: every Cat 12/13 + Cat 10/11 finding contains `references: [OWASP LLM10:2025, CWE-400, ...]` in its YAML, and the `source_attribution` field remains `[]`.

**One-way inheritance F-5 → F-A3**: when F-A3 ships and extends `denial-of-service` + `model-theft` populator wiring to populate `source_attribution` from the new categories' `references`, the existing `references`-array contract on F-5 findings is upward-compatible with the F-A3 populator output. F-5 does NOT retroactively populate `source_attribution` on emitted findings (the regenerated example shows `source_attribution: []` until F-A3 mutates it). The validator at `scripts/tachi_parsers.py:826` is regex-agnostic and accepts empty arrays.

**Asymmetry with F-1, F-2, F-3, F-4**: each populated `source_attribution` directly. F-5 is the first BLP-01 detection feature to defer populator wiring entirely. The deferral is BY DESIGN — F-5's two-agent enrichment scope at the pattern-catalog layer plus the F-A3 deferral keeps the F-5 surface minimal (4 file edits + 1 ADR + 1 example regen) and preserves the upward-compatibility contract for F-A3.

### Decision 9 — Public ADR omits commercial framing per SDR-001 Option C

ADR-034 (this file) is the **public per-feature ADR** documenting F-5's Heuristic A enrichment pattern at two-agent scope. Per SDR-001 Option C governance contract (private companion docs at `_internal/strategy/`), the public ADR:

- **Omits commercial framing**: no Layer 2, no tachi Cloud, no enterprise-only feature references, no commercial roadmap discussion. The ADR stands on technical merits only.
- **Omits SDR-001 cross-reference**: SDR-001 lives in private `_internal/strategy/` documentation; the public ADR records inheritance of SDR-001 Decision 4 via prose without cross-referencing the document directly.
- **Omits BLP-01 internal sequencing**: F-6 / F-7 are referenced as **public roadmap items** (forward scope markers) without disclosing internal prioritization rationale or commercial drivers.

This Decision 9 mirrors ADR-030 Decision 6 (F-1), ADR-031 Decision 6 (F-2), ADR-032 Decision 6 (F-3), and ADR-033 Decision 9 (F-4) — F-5 is the fifth ADR in the BLP-01 lineage to honor Option C. The dual-commit Proposed → Accepted protocol operates within Option C constraints.

---

## Detection Calibration Note

Pattern Categories 12 + 13 (DoS) and Pattern Categories 10 + 11 (model-theft) detect via **structural-absence** patterns consistent with F-1 / F-2 / F-4 precedent. The agent looks for declared LLM-serving infrastructure (declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology) AND the absence of LLM-tier resource controls (per-tenant QPS rate limit, max-prompt-token enforcement, per-tenant token budget, max-context-window enforcement, recursive-prompt-pattern detection, cost-velocity monitoring, automated tenant suspension on budget breach). When the architecture declares LLM-serving topology but does not declare these controls, the corresponding Pattern Category fires.

**Anti-indicator gate** (FR-015 LLM-serving topology gate): when the architecture lacks LLM-serving topology indicators, F-5 emits zero Cat 12/13 + Cat 10/11 findings. The 6 non-LLM-serving baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) do not declare LLM-serving topology and are therefore byte-identical post-F-5 by construction. The 7th baseline (`agentic-app`) exhibits multi-component LLM topology established by F-3 mutation and is the expected mutation candidate per Q5 RESOLVED.

**Cohesive emission contract**: same architecture surfacing Vector A (Cat 13 DoS) AND Vector B (Cat 11 model-theft) emits both findings — each in its own `category:` enum (`denial-of-service` for D-{N}; `llm` for LLM-{N}). They are not duplicates. The threat-report renders them adjacent under their respective categories without artificial fragmentation.

---

## Alternatives Considered

### Alternative 1 — Author new `llm10-unbounded-consumption` agent as 9th AI-tier sibling

Author `.claude/agents/tachi/llm10-unbounded-consumption.md` with companion `.claude/skills/tachi-llm10-unbounded-consumption/references/detection-patterns.md`, schema bump 1.8 → 1.9 adding new prefix (e.g., `UC` for unbounded-consumption), extend orchestrator dispatch with new registration, extend `finding-format-shared.md` consumers list with new agent.

**Why Not Chosen**: violates Heuristic A signal-class discipline per Decision 1 above. The LLM10 surface decomposes naturally into availability (DoS-host-side) and economic-damage (model-theft-host-side); splitting would (a) duplicate trigger keywords across DoS + model-theft + new agent, (b) fragment the LLM10 attack surface across three artificial agent boundaries, (c) force ID-prefix segmentation across what is structurally two emission streams. The architectural cost (~2 days of authoring) is also higher than two-agent enrichment (~1.5 day per PRD §Timeline).

### Alternative 2 — Single-agent enrichment of `denial-of-service` only (defer cost-amplification + denial-of-wallet to F-A3 or beyond)

Ship F-5 with narrower scope: enrich `denial-of-service` with Cat 12 + Cat 13 only; defer Cat 10 + Cat 11 model-theft enrichment to a follow-on feature.

**Why Not Chosen**: leaves LLM10:2025 Coverage Matrix in a Partial state because cost-amplification + denial-of-wallet are core LLM10 sub-patterns that the OWASP framework names explicitly. Partial coverage would be harder to reason about than Planned. Two-agent enrichment costs only marginally more than single-agent (the marginal cost is 2 additional Pattern Categories on a second host); splitting creates a follow-on feature with its own governance overhead.

### Alternative 3 — Schema bump 1.8 → 1.9 to add `UC` prefix for unbounded-consumption findings

Bump schema to add a new prefix segregating LLM10 findings from existing `D-{N}` and `LLM-{N}` findings.

**Why Not Chosen**: violates Decision 4 above. The `UC` prefix would imply that LLM10 sub-patterns are a distinct signal class from both `denial-of-service` AND `model-theft` — but they are sub-classes within the existing host-agent signal classes per Decision 1. The minor-bump rule (ADR-031 Decision 8) applies to features introducing new signal-class identities; Decision 4 records F-5 as the second asymmetry (after F-3). The no-schema-bump invariant at two-agent scope is the structural signal that Decision 1's identity claim is upheld.

### Alternative 4 — Inline pattern catalog in agent files (no companion-skill edits)

Author Pattern Categories 12-13 directly inside `denial-of-service.md` and Categories 10-11 directly inside `model-theft.md` rather than externalizing them to the existing companion `detection-patterns.md` files.

**Why Not Chosen**: violates the ADR-023 lean-agent shape. Categories with ≥4 indicators each, ≥1 worked example each, anti-indicator subsections, and citation lists would consume 80-120 lines per host agent, pushing both `denial-of-service.md` and `model-theft.md` past their respective ≤120 / ≤150 line caps. The lean + skill-references pattern is the tachi standard; F-5 conforms by routing pattern catalog content to the companion files.

### Alternative 5 — Decompose Q1 SPLIT into a single owning category (merge Cat 13 Vector A and Cat 11 Vector B into one host)

Resolve Q1 SPLIT cross-agent vector decomposition by assigning BOTH context-window vectors to a single owning category (either DoS Cat 13 covers both Vector A + Vector B, or model-theft Cat 11 covers both).

**Why Not Chosen**: violates signal-class identity per Decision 1. Vector A targets availability disruption (per-request latency); Vector B targets economic damage (per-call cost). The two outcomes have different attacker intents, different mitigation surfaces (latency budgets + truncation policy vs. token budgets + cost-velocity monitoring), and different host agents owning the relevant abstraction layer. Merging would create a single category with disjoint indicator sets and disjoint mitigation taxonomies — semantically incoherent.

---

## Consequences

### Positive

- **LLM10:2025 Unbounded Consumption threat surface closed.** F-5 ships the first detection-tier coverage of OWASP LLM10:2025, advancing OWASP LLM Top 10:2025 framework coverage from 9/10 (post-F-4) to **10/10** (post-F-5 — full LLM Top 10 closure milestone). Combined with F-4's ASI09 closure: **20/20 OWASP AI top-10 entries** covered by tachi.
- **Heuristic A enrichment branch validated at two-agent scope.** F-3 validated the enrichment branch at single-agent scope; F-5 extends the precedent to two-agent scope, demonstrating that signal-class discipline (Decision 1) generalizes across agent-count regardless. Future BLP-01 features (F-6 / F-7 Tier 2 ML+Mobile bundles) can cite F-5 as the two-agent enrichment precedent.
- **Second BLP-01 detection feature with no schema bump (after F-3); first at two-agent scope.** Decision 4 above records the asymmetry. F-5 demonstrates that Heuristic A enrichment correctly avoids spurious schema bumps at any agent-count scope when signal-class identity is preserved. The structural symmetry across F-3 (single-agent) and F-5 (two-agent) is the operational signal that Decision 1's identity claim is upheld.
- **First BLP-01 detection feature to defer `source_attribution` populator wiring entirely (F-A3 inheritance, one-way).** Decision 8 above records the deferral. F-5 establishes the prose-only references-array contract for enrichment features that defer populator wiring; F-A3 inherits the contract upward without F-5 retroactive mutation.
- **Q1 SPLIT cross-agent vector decomposition operationalized.** First BLP-01 sub-pattern with cross-agent vector decomposition. The 5-row mapping table in Decision 3 is the canonical source-of-truth for context-window exhaustion (Vector A → DoS Cat 13; Vector B → model-theft Cat 11) and other cross-host sub-pattern boundaries.
- **Q3 severity-floor 2-condition CRITICAL rule encoded.** The 2-condition rule (multi-tenant freemium AND BOTH per-tenant token budget + cost alerting absent) is encoded in the Cat 11 worked-example narrative + freemium-floor fixture. Single-tenant economic exposure with absent controls computes HIGH (not CRITICAL) — preserves the precise severity contract.
- **Smallest BLP-01 detection delivery surface at two-agent scope.** Zero new agent files, zero new skill directories, zero schema bumps, zero consumers-list edits, zero functional orchestrator edits, zero `source_attribution` populator wiring extensions. F-5 ships in ~1.5 working days per PRD §Timeline, demonstrating that two-agent enrichment can deliver an OWASP LLM Top 10 closure at structurally minimal surface.
- **Zero regression on the 24-file detection tier.** ADR-023 stabilization + F-1 + F-2 + F-3 + F-4 extensions all hold. The 24 frozen detection-tier files (12 other agents + 12 other companions) remain byte-identical at F-5 merge. F-5 is an enrichment of two in-scope files plus their companions, not a refactor or scope expansion.
- **SC-014 byte-identity preserved by construction across 6 baselines.** The 6 non-LLM-serving baselines do not qualify for the LLM-serving topology gate (FR-015 — no declared inference endpoint, no LLM API gateway, no per-tenant API key, no token-counting middleware, no cost-attribution layer). All 6 baselines emit zero Cat 12/13 + Cat 10/11 findings → all 6 PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`.
- **Cohesive category rendering on the regenerated example.** Cat 1-13 (DoS) findings render adjacent in the same `category: denial-of-service` section of `threats.md` and `threat-report.md`, with sequential `D-{N}` IDs. Cat 1-11 (model-theft) findings render adjacent in the same `category: llm` section with sequential `LLM-{N}` IDs. No fragmentation across artificial sub-sections that would emerge if LLM10 were a new agent.
- **OWASP LLM Top 10:2025 framework coverage 10/10 milestone.** Combined with F-4's ASI09 closure: **20/20 OWASP AI top-10 entries** (10 LLM Top 10 + 10 Agentic Top 10) — full closure of both OWASP AI top-10 frameworks.
- **Zero new runtime or developer dependencies.** Empty diffs on all dependency manifests. Consistent with Features 128 / 180 / 189 / 194 / 201 / 206 / 219 / 224.
- **Determinism preserved.** No new orchestrator phase, no new LLM-judgment step, no new HTTP fetch. The agent's pattern matching is a pure function of architecture input + companion `detection-patterns.md` rules. ADR-021 byte-identity harness consumes no new knobs.

### Negative / risks

- **Q1 SPLIT cross-agent vector decomposition requires prose precision across two companion files.** Cat 13 (DoS) and Cat 11 (model-theft) cover different vectors of context-window exhaustion; the cross-agent boundary must be clear to adopters reading either catalog. **Mitigation**: explicit Q1 SPLIT scope notes in Cat 13 (Wave 2 T015) and Cat 11 (Wave 2 T025) that point to the 5-row mapping table in Decision 3 above; code-reviewer R7 verification at Wave 3 T058 enforces boundary clarity.
- **Q3 severity-floor 2-condition CRITICAL rule requires worked-example precision.** The 2-condition rule must be encoded clearly enough that pipeline runs produce the correct severity (HIGH default vs. CRITICAL floor) on diverse architecture inputs. **Mitigation**: Cat 11 worked-example narrative (Wave 2 T027) explicitly states the 2-condition rule; freemium-floor fixture (Wave 1.1 T009) demonstrates the floor case.
- **`agentic-app` regeneration may surface unexpectedly clean LLM-serving topology if Feature 224's mutation removed key indicators.** F-5 Q5 default (extend `agentic-app`) relies on the multi-component LLM topology established by F-3 mutation. If Wave 2 T043 confirmation reveals insufficient LLM-serving signal, fallback to architecture extension consumes 0.5 day of Buffer Day capacity per PRD R1. **Mitigation**: T022 LLM-serving topology dry-run (Wave 1.1) validates `agentic-app` post-F-4 architecture pre-edit; T043 confirmation gate reviews actual signal.
- **F-A3 inheritance one-way contract requires future feature discipline.** Decision 8 defers `source_attribution` populator wiring entirely. When F-A3 ships, it must extend `denial-of-service` + `model-theft` populator wiring to populate `source_attribution` from the new categories' `references` without retroactively mutating F-5 findings. **Mitigation**: F-A3 PRD will explicitly cite Decision 8 above and the upward-compatibility contract; ADR-028 Decision 6 records the F-A3 scope boundary.

### Neutral

- **No new `category` enum value.** F-5 reuses `category: denial-of-service` (DoS host) and `category: llm` (model-theft host) — both existing enum values. Cat 12/13/10/11 findings flow through the same `category:` code paths in downstream consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) — zero infrastructure-tier edits.
- **Schema 1.8 is unchanged.** Future BLP-01 enrichment features that follow F-5's two-agent branch can cite this no-schema-bump precedent at multi-agent scope. Future new-agent features (F-6 / F-7 Tier 2 if they invoke the new-agent branch) follow the regex-alternation minor-bump rule per ADR-030 Decision 8 + ADR-031 Decision 8 + ADR-033 Decision 8.
- **F-5 ships solo or as the first of multiple parallel-eligible Tier 1 features in the 2026-04-29 → 2026-04-30 window** per agent-assignments.md §1 capacity check. R3 multi-feature concurrency hedge (Buffer Day reserved) absorbs any F-6 / F-7 sequencing collisions; F-5 has the second-smallest edit surface (after F-3) and ships before F-6 / F-7 to minimize rebase friction.
- **MAESTRO Layer 7 inheritance** per ADR-020 lineage. Both `D-{N}` and `LLM-{N}` findings inherit L7 Application layer via orchestrator Phase 1 keyword classification (existing categories already inherit L7). The agents do not author their own layer field; this is correct per ADR-020 Decision and ADR-023 Decision 2.
- **Forward-compatibility for F-A3 populator wiring.** F-A3 will extend `denial-of-service` + `model-theft` populator wiring to populate `source_attribution` from references. F-5 does NOT pre-design F-A3 beyond the Decision 8 deferral and the upward-compatibility contract.

---

## Cross-References

- **ADR-021**: Determinism baseline (SOURCE_DATE_EPOCH). F-5's Wave 3 regeneration gate (T054) uses `SOURCE_DATE_EPOCH=1700000000` to verify 6-baseline byte-identity. The agent's pattern matching is deterministic (pure function of architecture input + pattern catalog); no new determinism knobs introduced.
- **ADR-023**: Lean-agent + additive-only shared-reference Decision 3. F-5 follows the additive-only edit discipline at two-agent scope per Decision 2 above. The 24-file zero-edit invariant (post-F-4 inventory: 28 detection files; F-5 edits 4 host files; 24 unchanged) is preserved by construction. Decision 3 byte-identity enforcement on the existing `denial-of-service.md` + `model-theft.md` host files plus their two companions is the core architectural compliance signal at Wave 2 EOD T031 + T032.
- **ADR-027**: F-A1 taxonomy crosswalk (`schemas/taxonomy/owasp.yaml` LLM10 + LLM03 entries; `schemas/taxonomy/cwe.yaml` CWE-400 + CWE-770 entries). F-5's `references`-array citations resolve against all 4 catalog anchors. F-5 is read-only against the F-A1 catalog; no edits to `schemas/taxonomy/`. T1496 (Resource Hijacking) is NOT catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` and is therefore prose-only on Cat 10/11 mitigations (NOT in references).
- **ADR-028**: F-A2 `source_attribution` schema — **Decision 6 F-A3 deferral**: F-5 cites LLM10 + CWE-400 / CWE-770 / LLM03 in references-array only; populator wiring deferred to F-A3 per Decision 8 above. F-5 is the first BLP-01 detection feature to defer populator wiring entirely. The validator at `scripts/tachi_parsers.py:826` is regex-agnostic and accepts empty arrays.
- **ADR-030**: F-1 — **Decision 1 signal-class taxonomy in LLM tier** as the precedent applied at two-agent scope here. F-5 demonstrates the same signal-class discipline applied across two host agents simultaneously (DoS for availability axis + model-theft for economic-damage axis). This is **inheritance of the rule** at two-agent scope, not re-adjudication.
- **ADR-031**: F-2 — **Decision 8 regex-alternation minor-bump rule** (ADR-031 records F-2 as the second application — 1.6 → 1.7 adding `MI` prefix). **F-5 cross-references Decision 8 as the asymmetry**: F-5 is NOT an application of the rule. F-5 is the second BLP-01 detection feature with no schema bump (after F-3) because the existing `D` and `LLM` prefixes are already correct for the Heuristic A enrichment-branch signal classes. Decision 4 above records the asymmetry with explicit ADR-031 Decision 8 cross-reference.
- **ADR-032**: F-3 — **direct precedent at single-agent enrichment scope**. **Lines 84 + 182 forecast** that F-5 would follow the enrichment branch with no schema bump expected — this Decision 4 fulfills the forecast. The structural symmetry across F-3 (single-agent enrichment, no schema bump) and F-5 (two-agent enrichment, no schema bump) is the operational signal that Decision 1's identity claim is upheld at any agent-count scope.
- **ADR-033**: F-4 — **Decision 2 sub-scope carve-up structural sibling**. ADR-033 carved one OWASP entry (ASI09:2026) across two host agents (`human-trust-exploitation` for communication axis + `agent-autonomy` for autonomy axis) at the documentation layer (no agent-tier-source code edits — only cross-references and metadata). ADR-034 enriches one OWASP entry (LLM10:2025) across two host agents (`denial-of-service` for availability axis + `model-theft` for economic-damage axis) at the pattern-catalog layer (additive Pattern Category authoring on each companion). Both ADRs operationalize one-OWASP-entry-across-two-host-agents partition in different layers. Sibling structural pattern.

### 24-file zero-edit invariant — grep-auditable enumeration

The T073 pre-merge grep audit verifies the following 24 files have zero diff against `main`:

**12 other AI/STRIDE threat-agent files** (all in `.claude/agents/tachi/`):

```
spoofing.md
tampering.md
repudiation.md
info-disclosure.md
privilege-escalation.md
prompt-injection.md
data-poisoning.md
agent-autonomy.md
tool-abuse.md
output-integrity.md
misinformation.md
human-trust-exploitation.md
```

**12 companion `detection-patterns.md` files** (all under `.claude/skills/tachi-{name}/references/`):

```
tachi-spoofing/references/detection-patterns.md
tachi-tampering/references/detection-patterns.md
tachi-repudiation/references/detection-patterns.md
tachi-info-disclosure/references/detection-patterns.md
tachi-privilege-escalation/references/detection-patterns.md
tachi-prompt-injection/references/detection-patterns.md
tachi-data-poisoning/references/detection-patterns.md
tachi-agent-autonomy/references/detection-patterns.md
tachi-tool-abuse/references/detection-patterns.md
tachi-output-integrity/references/detection-patterns.md
tachi-misinformation/references/detection-patterns.md
tachi-human-trust-exploitation/references/detection-patterns.md
```

The infrastructure-tier consumers (`risk-scorer.md`, `control-analyzer.md`, `threat-report.md`, `threat-infographic.md`, `report-assembler.md`), `orchestrator.md`, and `finding-format-shared.md` are also expected to show zero diff per spec FR-016 / FR-017 / FR-019 / SC-016 / SC-017 / SC-021. `dispatch-rules.md` shows zero diff (Q2 default-NO at architect plan-day decision). `schemas/finding.yaml` shows zero diff per spec SC-018 / Decision 4.

---

## References

- Spec: [`specs/229-llm10-unbounded-consumption-verification/spec.md`](../../../specs/229-llm10-unbounded-consumption-verification/spec.md) — 3 user stories (US-229-1/2/3), 22 FRs, 22 SCs
- Plan: [`specs/229-llm10-unbounded-consumption-verification/plan.md`](../../../specs/229-llm10-unbounded-consumption-verification/plan.md) — 4-wave structure (1.0 / 1.1 / 2 / 3 / 4), Q1-Q5 architect decisions resolved, 1.5-day envelope
- Tasks: [`specs/229-llm10-unbounded-consumption-verification/tasks.md`](../../../specs/229-llm10-unbounded-consumption-verification/tasks.md) — 85 tasks across 10 phases, triple sign-off APPROVED 2026-04-27
- Wave 1.0 architect re-verification memo: [`.aod/results/wave1-architect-reverify.md`](../../../.aod/results/wave1-architect-reverify.md) — catalog citation re-verify + Heuristic A two-agent scope intact + line count + consumers list verification
- Wave 1.0 Q2 decision memo: [`.aod/results/wave1-q2-cosmetic-annotation-decision.md`](../../../.aod/results/wave1-q2-cosmetic-annotation-decision.md) — cosmetic dispatch-rules annotation NO per architect plan-day default
- PRD: [`docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md`](../../product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md)
- Schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) — schema_version "1.8" (UNCHANGED per Decision 4)
- F-A1 catalog YAMLs: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml) (LLM10 line 373, LLM03 in catalog header), [`schemas/taxonomy/cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) (CWE-400 line 130, CWE-770 line 182) — all read-only
- F-A2 parser + validator: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` + `validate_source_attribution` (unchanged; regex-agnostic — accepts empty arrays)
- Feature 082 (ADR-023 lean-agent stabilization): [`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`](ADR-023-threat-agent-skill-references-pattern.md)
- Feature 201 (F-1 indirect precedent — first net-new AI-tier agent under ADR-023): [`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`](ADR-030-output-integrity-agent.md)
- Feature 206 (F-2 indirect precedent — second net-new AI-tier agent; minor-bump rule second application): [`docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`](ADR-031-misinformation-agent.md)
- Feature 219 (F-3 direct precedent — first enrichment-branch execution at single-agent scope): [`docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`](ADR-032-asi07-tool-abuse-enrichment.md)
- Feature 224 (F-4 structural sibling — sub-scope carve-up of one OWASP entry across two host agents): [`docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md`](ADR-033-human-trust-exploitation-agent.md)

---

## Revision History

| Date | Status | SHA | Author | Note |
|------|--------|-----|--------|------|
| 2026-04-27 | Proposed | `3adacc8` | architect (Feature 229) | Initial proposal — Wave 1.1 unblock-gate commit. Records 9 numbered decisions covering the Heuristic A enrichment of `denial-of-service` + `model-theft` for LLM10:2025 closure at **two-agent scope** (D1 enrichment-vs-new-agent inheritance from ADR-030 Decision 1 applied at two-agent scope; signal-class identity rationale with detection vocabulary / mitigation taxonomy disjointness from a hypothetical new agent), additive-only edit discipline per ADR-023 Decision 3 at two-agent scope (D2 byte-identity proof on Cat 1-11 (DoS) + Cat 1-9 (model-theft) + Overview + DFD targets + Triggers regions of both companion catalogs; pre-existing `## Purpose` prose preserved on both host agents), **canonical 5-row LLM10 sub-pattern → owning-agent mapping table populated COMPLETE** (D3 audit deliverable per Q3 severity-hint annotation column; Q1 SPLIT cross-agent vector decomposition operationalized with Vector A → DoS Cat 13 / Vector B → model-theft Cat 11), no schema bump (D4 second BLP-01 detection feature reusing existing `D` and `LLM` prefixes; cross-references ADR-031 Decision 8 as the **asymmetry** F-5 does NOT invoke; cross-references ADR-032 lines 84+182 forecast as **fulfilled**), no consumers-list edit (D5 both agents already at finding-format-shared.md lines 12 + 16), no functional orchestrator/dispatch edit (D6 cosmetic Q2 annotation NO at architect plan-day default — zero functional dispatch-tier touches), Pattern Category Disambiguation across two companion catalogs (D7 DoS Cat 9 vs Cat 12/13 + model-theft Cat 6 vs Cat 10/11 non-overlap carves; Q1 SPLIT cross-agent disambiguation), no `source_attribution` populator wiring extension (D8 F-A3 deferral; F-5 cites LLM10 in references-array only; first BLP-01 detection feature to defer populator wiring; one-way inheritance F-5 → F-A3), and public-only governance per SDR-001 Option C (D9 omits commercial framing; fifth ADR in BLP-01 lineage to honor Option C). Heuristic A enrichment-branch second-execution at two-agent scope narrative captured for F-6/F-7 Tier 2 ML+Mobile bundles. ADR-030 D1 + ADR-031 D8 + ADR-032 (direct precedent + lines 84+182 forecast fulfilled) + ADR-033 D2 (sub-scope carve-up structural sibling) cross-references explicit at Decisions 1 + 4. Authored at Day 1 Wave 1.1 after T003 catalog re-verification + T004 plan-day Q2 default-NO decision; serves as the unblock-gate signal that unblocks parallel Wave 2 authoring of Pattern Categories 10 + 11 + Disambiguation + Primary Sources extension on model-theft companion. Status transitions to Accepted at Wave 3 T040 with provisional merge-date; post-merge SHA fill at T042 per Decision 9 dual-commit governance protocol. |
| 2026-04-27 | Accepted | `e086d31` | architect (Feature 229 — Wave 3 T040) | Status transition Proposed → Accepted following successful Wave 2 example regeneration on `examples/agentic-app/` (T045 emitted 4 NEW findings — D-10 Cat 12, D-11 Cat 13, LLM-15 Cat 10, LLM-16 Cat 11 — all citing OWASP LLM10:2025 with correct cohesive category rendering and references-array contract honored per T050/T051), Wave 3 tester verification (T054 6/6 byte-identity baselines pass + T055 26/26 enrichment tests green + T056 per-fixture references contract honored), architect full re-confirmation (T057 references-array contract validated across all 27 D/LLM findings — both STRIDE 10-column and AI/LLM 11-column table formats; T1496 prose-only confirmed across full corpus with 0 references-column violations), and code-review APPROVED (T058 0 Critical / 0 High / 0 Medium / 1 Low). Q1 SPLIT cross-agent vector decomposition operationally validated (D-11 Vector A latency / LLM-16 Vector B cost in correlation group CG-8 of regenerated threat-report.md Theme 5). Q3 RESOLVED severity-floor 2-condition correctly applied at LLM-16 (HIGH default — single-application architecture; CRITICAL 2-condition floor not met). T1496 prose-only on Cat 10/11 with explicit "(NOT in references array — not catalog-resolvable per ADR-034 Decision 6)" annotation in both LLM-15 + LLM-16 narratives. Heuristic A second-execution at two-agent scope precedent established for F-6/F-7 Tier 2 ML+Mobile bundles. Test infrastructure update at `tests/scripts/test_backward_compatibility.py` carves out F-5 hosts (denial-of-service.md + model-theft.md + 2 companion patterns) from F-142 zero-edit invariant per ADR-034 Decision 2; mirrors F-3 (PR #220) precedent at multi-host scope. SHA backfilled at T042 post-squash-merge to `e086d31` (full SHA `e086d31e4bead0dd7cb3de3fd63e4a120da59133`); release-please PR #226 (v4.24.0) opened cleanly within ~30s of squash-merge per T081 verification — no F-212 empty-marker fallback invoked. |
