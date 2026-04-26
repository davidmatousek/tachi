---
description: "Task breakdown for Feature 219 — F-3 Heuristic A enrichment of tool-abuse for OWASP ASI07:2026 (BLP-01 Tier 1 third feature; first execution of enrichment branch)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-25
    status: APPROVED
    notes: "Tasks.md faithfully decomposes plan.md into 67 atomic tasks across 9 phases with full coverage. All 21 spec SCs explicitly mapped in Wave 4 sweep T043-T058 + T062-T063 with grep-checkable predicates. All 21 spec FRs materially traceable. 3 P1 user stories tagged correctly with [US1] (Pattern Category 9 / A2A) / [US2] (Pattern Category 10 / MCP-to-MCP) / [US3] (ADR-032 + cohesive rendering). PRD Q1/Q5 honored without re-litigation; Q2/Q3/Q4 deferred to architect plan-day decisions with traceable task IDs (Q2 → T004/T013; Q3 → T005/T032/T064; Q4 → T016/T020). Heuristic A enrichment-branch first-execution narrative preserved end-to-end. Zero scope creep across 17 out-of-scope items (no new agent / no new skill dir / no schema bump / no consumers list edit / no functional orchestrator edit). Buffer Day 1 retrospective slotting (T061) + Buffer Day 2 concurrency hedge per PRD HIGH-1 / R3. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW — MEDIUM-1 is documentation hygiene (tasks.md cites only 4 FR-IDs literally vs. SC sweep's full literal coverage), LOWs stylistic. PM APPROVED. Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-25
    status: APPROVED
    notes: "Tasks.md technically sound on all 6 correctness dimensions: (1) test-first discipline preserved — T033 authors test suite before T034 regen; T005-T008 fixtures land at Wave 1.1; (2) Wave 1.1 atomic commit T009-T012 (ADR-032 Proposed + tool-abuse.md edits + fixtures); (3) ADR-032 6-stage lifecycle T009→T010→T011→T029→T030→T031 correctly sequenced; (4) 24-file zero-edit invariant verifiable in T053; (5) source_attribution contract correct — Cat-9 valid fixture cites ASI07+CWE-287 (T006), Cat-10 valid fixture cites ASI07+CWE-345 (T007), negative fixture for rejection test (T008), regen validation (T039); (6) Heuristic A enrichment-branch first-execution discipline — T010 D1-D7 surface enrichment vs new agent + additive-only + no schema bump (with ADR-031 Decision 8 cross-ref as the asymmetry F-3 does NOT invoke) + no consumers + no orchestrator + public-only + Pattern Category Disambiguation. **Strongest signal: T010 D3 surfaces ADR-031 Decision 8 regex-bump rule as the load-bearing asymmetry, elevating 'first BLP-01 detection feature with no schema bump' from prose to architectural Decision.** 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (advisory only — synthetic CWE-99999 vs F-2's real-but-absent AML.T0042 style; Phase 1 leaner than F-2 by design). APPROVED. Full review: .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-25
    status: APPROVED
    notes: "Tasks.md fits 1-day envelope (Tue 2026-04-28) with 2-day buffer per PRD §Timeline. Strongest signal: Wave 4's 16-way parallel SC sweep (T043-T058) + Wave 1.1's 6-way parallel unblock track (T006/T007/T008/T009/T013/T014) make the envelope structurally feasible despite 67 tasks. Critical path is sound (T003→T010→T012→Wave2→Wave3→Wave4) with no cycles. All PRD HIGH-1/HIGH-2 traceable to specific task IDs: HIGH-1 retrospective slotting → T061 Day 1 PM if ≥1h residual, otherwise Buffer Day 1; HIGH-2 PR title contract → T058 Wave 4 pre-merge + T063 post-merge release-please verification with F-212 recovery pattern. R3 Buffer Day 2 hedge preserved. Wave gate points enumerated; escalation paths defined for likely failure modes. Granularity check: tasks atomic enough for <30 min average / <2h max; 67 tasks across 9 phases over 1 day is more granular than F-2's 62 tasks over 2 days because enrichment-pattern testability requires more verification points. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW — MEDIUM is informational (line-count target 100-106 not bound to test assertion; hard cap ≤150 is the actual gate). LOWs stylistic. APPROVED. Ready for /aod.build. Full review: .aod/results/team-lead.md."
---

# Tasks: ASI07 Tool-Abuse Enrichment (OWASP ASI07:2026)

**Input**: Design documents from `/specs/219-asi07-tool-abuse-enrichment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/finding-contract.md, quickstart.md
**Branch**: `219-asi07-tool-abuse-enrichment`

**Tests**: Structural-diff test on Categories 1-8 byte-identity + line-count test on `tool-abuse.md` + MAESTRO grep test + F-A2 referential-integrity validation on Category-9/10 fixtures REQUIRED (per SC-006, SC-002, SC-016, SC-015); backward-compat byte-identity is an existing harness (existing `tests/scripts/test_backward_compatibility.py`).

**Organization**: Tasks are grouped into waves matching plan.md's 4-wave structure. Wave 1 ADR-032 Proposed + `tool-abuse.md` additive edits is the unblock-gate; Wave 2 pattern catalog authoring (Categories 9 + 10 + Disambiguation + Primary Sources) proceeds after; Wave 3 example regeneration on multi-agent target + backward-compat verification; Wave 4 ADR-032 Accepted + PR ready + delivery retrospective + Coverage Matrix update.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 = A2A inter-agent channel detection / Pattern Category 9; US2 = MCP-to-MCP trust propagation detection / Pattern Category 10; US3 = Cohesive Agentic-category rendering with Heuristic A enrichment pattern / ADR-032)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure feature directory and branch are correctly configured. Branch already created at start of `/aod.plan`; directories already scaffolded by `/aod.spec` and `/aod.project-plan`. Draft PR #220 already opened with `feat(219):` Conventional Commits title.

- [X] T001 Verify working directory clean on branch `219-asi07-tool-abuse-enrichment` and `specs/219-asi07-tool-abuse-enrichment/` contains spec.md, plan.md, research.md, data-model.md, contracts/finding-contract.md, quickstart.md
- [X] T002 [P] Create directory `tests/scripts/fixtures/tool_abuse_enrichment/` (test fixtures for Category-9/10 source_attribution validation)

---

## Phase 2: Foundational — Wave 1.0 & 1.1 (Blocking Prerequisites)

**Purpose**: Architect re-verification of catalog citations + Heuristic A scope intact + ADR-032 Proposed commit + `tool-abuse.md` additive edits unblock Wave 2 pattern catalog authoring. Escalation gate fires if Heuristic A enrichment-vs-new-agent decision is challenged or any of the 5 catalog citations no longer resolve.

**CRITICAL**: No user story work can begin until T009 (ADR-032 Proposed) and T012 (`tool-abuse.md` edits) are committed.

### Wave 1.0 — Architect Re-Verification (15-30 min, Day 1 AM)

- [X] T003 Architect re-verifies plan-day prerequisites: (a) all 5 catalog citations still resolve in `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml` (re-runs grep checks against ASI07, LLM03, CWE-287, CWE-345, AML.T0060); (b) Heuristic A enrichment-vs-new-agent decision intact (SDR-001 Decision 4 locked; ADR-030 Decision 1 + ADR-031 Decision 8 cross-refs valid); (c) `.claude/agents/tachi/tool-abuse.md` line count is still 98 (no concurrent edit landed since PRD time); (d) `tool-abuse` still at line 18 in `finding-format-shared.md` consumers list. Capture verification in a short decision memo at `.aod/results/wave1-architect-reverify.md`. If any verification fails, escalate before T009 commit.
- [X] T004 Architect plan-day decision on PRD Q2 (cosmetic dispatch-rules annotation): record YES/NO at `.aod/results/wave1-q2-cosmetic-annotation-decision.md`. PRD architect leaning YES (adds Coverage Matrix traceability without modifying dispatch logic; documentation-only ~30-second edit). If YES, T012 includes the one-token annotation update to `dispatch-rules.md`.
- [X] T005 Architect plan-day decision on PRD Q3 (example regeneration target): record `agentic-app` extend vs. `maestro-reference` vs. new minimal multi-agent fixture at `.aod/results/wave1-q3-example-target-decision.md`. PM default per PRD: extend `examples/agentic-app/` (Feature 142 already added `Inter-agent Communication Channel` component type — sufficient multi-agent topology by construction). Architect may invoke fallback if Wave 3 structural inspection reveals insufficient inter-agent channel signal.

### Wave 1.1 — ADR-032 Proposed + `tool-abuse.md` Additive Edits + Fixtures (parallel, Day 1 AM/PM)

- [X] T006 [P] [US1] [US2] Author test fixture `tests/scripts/fixtures/tool_abuse_enrichment/valid_category_9_a2a_finding.yaml` per contracts/finding-contract.md — complete `AG-{N}` Category-9 finding with valid `source_attribution` citing `owasp:ASI07` (primary) + `cwe:CWE-287` (related) + optional `atlas:AML.T0060` (related), populated mitigation text naming mTLS + HMAC + nonce + taint propagation, description distinguishing A2A channel sub-class.
- [X] T007 [P] [US1] [US2] Author test fixture `tests/scripts/fixtures/tool_abuse_enrichment/valid_category_10_mcp_to_mcp_finding.yaml` per contracts/finding-contract.md — complete Category-10 finding with valid `source_attribution` citing `owasp:ASI07` (primary) + `cwe:CWE-345` (related) + optional `owasp:LLM03` (related), populated mitigation text naming per-hop MCP attestation + signed-capability handoff + MCP-trust-chain validator, description distinguishing MCP-to-MCP trust propagation sub-class.
- [X] T008 [P] Author negative-test fixture `tests/scripts/fixtures/tool_abuse_enrichment/invalid_attribution_finding.yaml` — Category-9/10 finding with `source_attribution` citing an absent CWE ID (e.g., `CWE-99999`) to validate that F-A2 `validate_source_attribution` rejects the finding per referential-integrity rule.
- [X] T009 [US3] Author ADR-032 skeleton at `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` with **Status: Proposed** (per FR-019 / plan Wave 1.1): title block, Context section (BLP-01 Tier 1 framing, Heuristic A enrichment branch problem statement, ASI07:2026 Planned → Covered transition, signal-class identity with existing tool-abuse coverage), Decisions section placeholder (populated in T010), Consequences placeholder, Cross-References placeholder, Revision History table with one initial Proposed row, no Layer 2 / commercial framing per SDR-001 Option C.
- [X] T010 [US3] Populate ADR-032 Decisions section with **6-7 numbered Decisions**: (D1) **Heuristic A enrichment vs. new agent** — signal-class identity rationale (message flow between agent-or-tool endpoints; consolidating into existing `tool-abuse` agent prevents Agentic-category section fragmentation; SDR-001 Decision 4 cross-reference; explicit acknowledgment that ADR-030 Decision 1 established the signal-class taxonomy in LLM tier and F-3 demonstrates the same rule applied within AG tier); (D2) **Additive-only edit discipline per ADR-023 Decision 3** — byte-identity proof on Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords`; (D3) **No schema bump** — reuses existing `AG-{N}` prefix; first BLP-01 detection feature with no schema bump (cross-references ADR-031 Decision 8 as the **asymmetry**: regex-alternation minor-bump rule applies to F-1/F-2 but NOT F-3); (D4) **No consumers-list edit** — `tool-abuse` already at `finding-format-shared.md:18` (PRD-time verified); (D5) **No functional orchestrator/dispatch-rules edit** — `tool-abuse` already fully registered (cosmetic Q2 annotation per architect plan-day decision is documentation-only); (D6) **Public-only governance** per SDR-001 Option C contract — public ADR omits commercial framing and SDR-001 cross-reference; (D7) **Pattern Category Disambiguation** — Category 6 (LLM03 supply-chain — upstream ingestion at registration time) vs. Category 10 (runtime trust propagation between already-registered MCP servers at invocation time) — explicit non-overlap carve. Commit ADR-032 Proposed at Wave 1.1.
- [X] T011 [US3] Populate ADR-032 Cross-References section: **ADR-021** (byte-identity baseline harness — SOURCE_DATE_EPOCH determinism), **ADR-023** (lean+skill-references pattern; Decision 3 additive-only shared-reference edits — F-3 follows in purest form), **ADR-027** (F-A1 taxonomy crosswalk — ASI07 + CWE-287 + CWE-345 + AML.T0060 + LLM03 catalog-resolvable), **ADR-028** (F-A2 source_attribution schema extension — F-3 is third producer flow / first enrichment of existing populator), **ADR-030** (F-1 indirect precedent — Decision 1 signal-class taxonomy in LLM tier as different application of same rule applied to AG tier), **ADR-031** (F-2 direct precedent — Decision 8 regex-alternation minor-bump rule cross-referenced as the **asymmetry** F-3 does NOT invoke). Plus 24-file zero-edit invariant proof with grep-auditable enumeration of the 24 unchanged detection-tier files.
- [X] T012 [US1] [US2] Modify `.claude/agents/tachi/tool-abuse.md` with 3 additive edits: **(Edit 1)** metadata YAML line 17 `owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025]` → `[ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]`. **(Edit 2)** `## Purpose` section (line 23-25) — append 1-3 lines naming the inter-agent channel surface (A2A and MCP-to-MCP) alongside the existing tool-dispatch surface. Architect adjudicates final prose; suggested phrasing: "This agent additionally covers the inter-agent channel surface — A2A communication between agent Process components (direct RPC, message bus, shared queue, MCP-to-MCP bridge) and multi-hop MCP trust chains — per OWASP ASI07:2026. Pattern Categories 9 (Insecure Inter-Agent Communication) and 10 (MCP-to-MCP Trust Propagation) detect channel-level threats distinct from single-agent tool dispatch." Pre-existing prose paragraph remains byte-identical. **(Edit 3)** Detection Workflow Step 5 references list (line 43) `(ASI-02, ASI-04, MCP-03, MCP-05, OWASP LLM06:2025, MITRE ATLAS AML.T0058/T0061/T0062, CWE-77, CWE-89)` — append `ASI-07`, `MITRE ATLAS AML.T0060`, `CWE-287`, `CWE-345`. Pre-existing references preserved byte-identically.
- [X] T013 [P] Apply Q2 cosmetic dispatch-rules annotation contingent on T004 decision: if Q2=YES, modify `.claude/skills/tachi-orchestration/references/dispatch-rules.md` extending `tool-abuse (MCP-03)` annotation to `tool-abuse (MCP-03, ASI-07)` (single-token edit, ~30 seconds). If Q2=NO, skip — F-3 ships with zero functional dispatch-tier touches. Documentation-only either way.
- [X] T014 [P] Pre-Wave 3 multi-agent topology dry-run (architect plan-day check): grep all 6 baseline architectures (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `agentic-app`) for multi-agent / multi-MCP indicators (`Inter-agent Communication Channel` component type per Feature 142, ≥2 agent Process components, MCP-to-MCP relay declarations). Verify: (a) 5 non-multi-agent baselines do not exhibit multi-agent inter-agent channels (zero matches expected) ⇒ guarantees byte-identity per topology gate; (b) `agentic-app` exhibits multi-agent topology post-Feature-142 ⇒ confirms Q3 PM default extension target. Record results at `specs/219-asi07-tool-abuse-enrichment/multi-agent-topology-check.md`. If 5 non-multi-agent baselines unexpectedly match: flag for architect Wave 3 review (pre-edit to preserve SC-010 byte-identity invariant).

**Checkpoint**: ADR-032 Proposed committed; `tool-abuse.md` 3 additive edits applied; fixtures authored; multi-agent topology dry-run clean. Wave 2 can now start.

**Escalation Gate**: If T003 architect re-verification surfaces a catalog drift OR Heuristic A enrichment decision is challenged OR T012 not complete by Day 1 AM (Tuesday 2026-04-28 12:00 local), surface user tie-break escalation before Day 1 PM. Do NOT proceed to Wave 2 without ADR-032 Proposed + `tool-abuse.md` edits committed.

---

## Phase 3: User Story 1 — Inter-Agent Channel Detection / A2A (Priority: P1) MVP

**Goal**: Ship Pattern Category 9 (Insecure Inter-Agent Communication / A2A) appended to `detection-patterns.md` so that running `/tachi.threat-model` on a multi-agent architecture emits ≥1 new `AG-{N}` finding citing OWASP ASI07:2026 + CWE-287 (and where applicable AML.T0060) + named A2A mitigations (mTLS / HMAC + nonce / replay-window / taint propagation).

**Independent Test**: Run the pipeline on `examples/agentic-app/architecture.md` (multi-agent topology established by Feature 142); confirm ≥1 new Category-9 `AG-{N}` finding in the output `threats.md` with `category: agentic`, `source_attribution` citing OWASP ASI07:2026 primary + CWE-287 related, mitigation text naming a specific A2A mechanism. Confirm zero Category-9 findings on 5 non-multi-agent baselines (single-agent topology gate per FR-011).

### Wave 2 — Pattern Category 9 Authoring (parallel with US2 T017, ~0.2d, Day 1 AM/PM)

- [X] T015 [US1] Append **Pattern Category 9 — Insecure Inter-Agent Communication (A2A)** to `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` after existing Pattern Category 8 (currently ends before line 154 `## Primary Sources`) per data-model.md E1: scope paragraph (A2A channels — direct RPC, message bus, shared queue, MCP-to-MCP bridge, named pipe, IPC — without declared mutual authentication, message signing, replay protection, or taint propagation; same Heuristic A signal class as existing tool-dispatch coverage); ≥4 indicators (target 5) covering ≥2 agent Process components connected by communication channel, no mutual authentication declared, no message signing, no replay protection, agent-in-the-middle relay without taint propagation. Architect may add 1-2 indicators at authoring time per plan-day refinement.
- [X] T016 [US1] Add **Anti-Indicator section** to Pattern Category 9 per Q4 architect plan-day default YES: enumerate at least one anti-indicator (single-agent topology — no inter-agent channel — emits zero Category-9 findings; declared mTLS + message signing + replay protection + taint propagation satisfies all four mitigations and emits zero Category-9 findings). Formalizes multi-agent topology gate (FR-011) for grep-auditability. Anti-indicator predicates MUST be testable. Mirrors F-2 MEDIUM-5 anti-indicator discipline.
- [X] T017 [US1] Add **Worked Example** to Pattern Category 9: clearly-fictional scenario per spec NFR-equivalent (no real institutional names) — orchestrator agent dispatches workloads to specialized worker agents over plain HTTP without mTLS or message signing. Threat description: a network-positioned attacker (or sibling worker on same compute substrate) intercepts and tampers with the orchestrator's instructions; receiving worker has no authentic-source signal and executes the modified instruction. Mitigation summary: mutual TLS + HMAC envelope signing with per-call nonce + inter-agent taint labels.
- [X] T018 [US1] Add **Primary/Related Citations** + **Mitigations** to Pattern Category 9: Primary `OWASP ASI07:2026 — Insecure Inter-Agent Communication`; Related `CWE-287 Improper Authentication`; Related (where applicable) `MITRE ATLAS AML.T0060 — Agent-in-the-Middle` (when relay-without-taint-propagation indicator fires). Mitigation list: Mutual TLS (mTLS) on every inter-agent channel; Inter-agent message signing (HMAC or asymmetric signature) with envelope integrity verification; Nonce-based replay prevention with replay-window enforcement; Inter-agent taint labels for authority propagation across relays; Per-channel mutual authentication (mutual JWT, mutual API key) where mTLS is infeasible.

**Checkpoint**: Pattern Category 9 fully authored. Multi-agent topology gate codified. Ready for US2 Pattern Category 10 authoring (parallel completion).

---

## Phase 4: User Story 2 — MCP-to-MCP Trust Propagation Detection (Priority: P1)

**Goal**: Ship Pattern Category 10 (MCP-to-MCP Trust Propagation) appended to `detection-patterns.md` so that running `/tachi.threat-model` on a multi-MCP architecture emits ≥1 new `AG-{N}` finding citing OWASP ASI07:2026 + CWE-345 (and where applicable LLM03) + named MCP-trust mitigations (per-hop attestation / signed-capability handoff / MCP-trust-chain validator).

**Independent Test**: Run the pipeline on `examples/agentic-app/architecture.md` (or architect-chosen multi-MCP target); confirm ≥1 new Category-10 `AG-{N}` finding in the output `threats.md` with `category: agentic`, `source_attribution` citing OWASP ASI07:2026 primary + CWE-345 related, mitigation text naming a specific MCP-trust mechanism. Confirm zero Category-10 findings on 5 non-multi-agent baselines (single-MCP topology gate per FR-011).

### Wave 2 — Pattern Category 10 + Disambiguation + Primary Sources (parallel with US1, ~0.2d, Day 1 AM/PM)

- [X] T019 [US2] Append **Pattern Category 10 — MCP-to-MCP Trust Propagation** to `detection-patterns.md` after Pattern Category 9 per data-model.md E2: scope paragraph (multi-hop MCP trust chains — Agent → MCP-A → MCP-B — propagating without per-hop attestation, signed-capability handoff, or trust-chain validator; same Heuristic A signal class as Category 9 but distinct deployment topology); ≥4 indicators (target 5) covering multi-hop MCP trust chain declared, no per-hop attestation, transitive authority assumption gaps, no trust-chain validator, undeclared cross-MCP supply-chain assumptions.
- [X] T020 [US2] Add **Anti-Indicator section** to Pattern Category 10 per Q4 architect plan-day default YES: enumerate at least one anti-indicator (single-MCP architectures — no MCP-to-MCP relay — emit zero Category-10 findings; declared per-hop MCP attestation + signed-capability handoff + MCP-trust-chain validator satisfies all three mitigations and emits zero Category-10 findings). Formalizes multi-MCP topology gate (FR-011).
- [X] T021 [US2] Add **Worked Example** to Pattern Category 10: clearly-fictional scenario — agent dispatches to remote MCP-A server which transparently relays to secondary MCP-B server without validating MCP-A's authority over MCP-B. Threat description: a compromised or rogue MCP-A injects responses purporting to come from MCP-B; agent has no per-hop attestation and accepts response as authoritative. Mitigation summary: per-hop MCP attestation with signed capability descriptors + signed-capability handoff (MCP-A signs delegated scope; MCP-B validates before accepting) + MCP-trust-chain validator that walks the multi-hop chain end-to-end before invocation.
- [X] T022 [US2] Add **Primary/Related Citations** + **Mitigations** to Pattern Category 10: Primary `OWASP ASI07:2026 — Insecure Inter-Agent Communication`; Related `CWE-345 Insufficient Verification of Data Authenticity`; Related (where applicable) `OWASP LLM03:2025 — Supply Chain` (inherited from existing Category 6 supply-chain vocabulary). Mitigation list: Per-hop MCP attestation (signed capability descriptor, per-hop authentication); Signed-capability handoff (MCP-A signs the capability scope it delegates to MCP-B; MCP-B validates the signature before accepting the delegation); MCP-trust-chain validator (verification component or contract that walks the multi-hop chain end-to-end before invocation); Supply-chain trust-chain enforcement (cross-reference with existing Category 6 supply-chain controls — versioned MCP server registry, signed package distribution, dependency-graph attestation); Taint propagation across MCP hops (MCP-A's taint labels propagate to MCP-B's outputs).
- [X] T023 [US2] [US3] Append **Pattern Category Disambiguation** subsection to `detection-patterns.md` after Pattern Category 10 and before existing `## Primary Sources` per PRD FR-2 / ADR-032 Decision 7 / data-model.md E3: explicit non-overlap carve between Category 6 (LLM03 supply-chain — upstream ingestion of plugins/tools/MCP servers at registration time) and Category 10 (runtime trust propagation between already-registered MCP servers at invocation time). Document that the same architecture may legitimately surface BOTH findings describing distinct architectural gaps; they are not duplicates and MUST NOT be merged in `threat-report.md` Agentic-category section.
- [X] T024 [P] [US1] [US2] Extend `## Primary Sources` list in `detection-patterns.md` (existing line 154 baseline) with two additive entries: `OWASP ASI07:2026 — Insecure Inter-Agent Communication` and `MITRE ATLAS AML.T0060 — Agent-in-the-Middle`. Pre-existing entries (`OWASP LLM03:2025`, `OWASP LLM06:2025`, MCP specification, MITRE ATLAS, CWE-89, CWE-77, Anthropic Tool Use Security Considerations) preserved byte-identically.

### Wave 2 EOD — Byte-Identity + MAESTRO Validation (Day 1 PM)

- [X] T025 [P] Structural-diff validation: run `git diff main -- .claude/skills/tachi-tool-abuse/references/detection-patterns.md`; verify the diff shows ONLY appended content after Pattern Category 8 — no `<` removal lines or `>` addition lines within Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` regions (additive-only invariant per ADR-023 Decision 3 / SC-006 BLOCKER). Record pass/fail at `.aod/results/wave2-byte-identity-check.md`.
- [X] T026 [P] MAESTRO grep validation: run `grep -i 'maestro' .claude/agents/tachi/tool-abuse.md .claude/skills/tachi-tool-abuse/references/detection-patterns.md`; expect empty output (zero matches per SC-016 BLOCKER / ADR-023 Decision 2). Record pass/fail at `.aod/results/wave2-maestro-grep-check.md`.
- [X] T027 [P] Line-count validation on `.claude/agents/tachi/tool-abuse.md`: run `wc -l .claude/agents/tachi/tool-abuse.md`; expect ≤150 (target 100-106 post-edit; PRD-time baseline 98 per SC-002 BLOCKER). Record at `.aod/results/wave2-line-count-check.md`.
- [X] T028 [P] Single MANDATORY Read directive preserved: run `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/tool-abuse.md`; expect 1 (unchanged). Record at `.aod/results/wave2-mandatory-read-check.md`.

**Checkpoint**: Wave 2 complete. Pattern Categories 9 + 10 + Disambiguation authored; Primary Sources extended; byte-identity preserved on Categories 1-8 + Overview + DFD targets + triggers; MAESTRO grep clean; line count ≤150; MANDATORY Read directive preserved. Ready for Wave 3 example regeneration.

---

## Phase 5: User Story 3 — Cohesive Agentic-Category Rendering with Heuristic A Enrichment Pattern (Priority: P1)

**Goal**: ADR-032 Accepted at F-3 merge contains explicit Heuristic A enrichment-vs-new-agent rationale + 6-7 numbered Decisions + cross-references; regenerated example architecture renders Categories 1-8 findings AND Categories 9-10 findings adjacent in the same `category: agentic` section of `threats.md` and `threat-report.md`; BLP-01 Coverage Matrix transitions ASI07:2026 Planned → Covered with F-3 named as closure feature.

**Independent Test**: ADR-032 at F-3 merge: (a) Status: Accepted, (b) Decisions section has all 6-7 Decisions populated (D1 enrichment vs. new agent / D2 additive-only edit discipline / D3 no schema bump / D4 no consumers edit / D5 no functional orchestrator edit / D6 public-only governance / D7 Pattern Category Disambiguation), (c) Cross-References include ADR-021/023/027/028/030 Decision 1/031 Decision 8 (asymmetry), (d) zero MAESTRO references in Decision sections, (e) Revision History tracks Proposed → Accepted with dates, (f) tool-abuse.md `## Purpose` section explicitly names the inter-agent channel surface as adjacent-but-distinct from single-agent tool dispatch.

### Wave 1.1 — ADR-032 Proposed (T009-T011 above)

See Phase 2 T009, T010, T011 — ADR-032 Proposed authoring happens at Wave 1.1 to unblock Wave 2.

### Wave 4 — ADR-032 Accepted Transition (Day 1 PM / Buffer Day 1)

- [X] T029 [US3] Transition ADR-032 `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` Status: Proposed → Accepted. Add Revision History row: `| 2026-04-28 | Proposed → Accepted | PR #220 pending merge | provisional |` (update date and PR number at authoring time).
- [X] T030 [US3] Verify ADR-032 body completeness: all 6-7 Decisions (D1-D7) populated; Consequences section populated; Cross-References section lists ADR-021/023/027/028/030 Decision 1/031 Decision 8 per T011; Revision History tracks Proposed → Accepted; zero MAESTRO references in Decision sections (`grep -i 'maestro'` on the ADR file returns empty); zero commercial framing per SDR-001 Option C. Record checklist pass/fail at `.aod/results/adr-032-completeness-check.md`.

### Post-Merge (Wave 4 or later)

- [ ] T031 [US3] After PR squash-merge: update ADR-032 Revision History with `| YYYY-MM-DD | Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed |` (ADR-027/028/029/030/031 precedent). Mirrors F-2 T025 same-day-as-merge SHA-fill pattern.

**Checkpoint**: Heuristic A enrichment rationale locked in public ADR-032 with 6-7 Decisions + cross-refs; ASI07 coverage surface documented; SHA-fill records the squash commit.

---

## Phase 6: Wave 3 — Example Regeneration + Backward-Compatibility Verification + Tests (Day 1 PM, ~0.3d)

**Purpose**: Regenerate the multi-agent example target with Categories 9-10 active to confirm dispatch produces ≥1 new `AG-{N}` finding per category; verify cohesive Agentic-category rendering; verify 5 non-multi-agent baselines remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-010 BLOCKER) — topology gate ensures zero-impact-when-absent. Q3 fallback decision point: if `agentic-app` cumulative-state cost exceeds convention-preservation benefit, invoke Q3 fallback to `maestro-reference` or new minimal multi-agent fixture (consuming Buffer Day 1 capacity per PRD R1).

- [X] T032 [US1] [US2] Q3 fallback decision confirmation point: architect re-verifies `examples/agentic-app/` post-Feature-142 architecture and confirms extend-in-place vs. fallback to `maestro-reference` or new minimal multi-agent fixture per T005 plan-day decision. PM default per Q3: extend `agentic-app` (Feature 142 already added `Inter-agent Communication Channel` component type — sufficient multi-agent topology by construction). Record decision at `.aod/results/wave3-regen-target-confirmation.md`.
- [X] T033 [US1] [US2] Author `tests/scripts/test_tool_abuse_enrichment.py`: structural-diff test on Categories 1-8 byte-identity (parses pre/post `detection-patterns.md` and asserts unchanged regions empty diff per SC-006); line-count test on `tool-abuse.md` (≤150 per SC-002); MAESTRO grep test on both target files (per SC-016); F-A2 referential-integrity validation on Category-9/10 fixtures (T006 + T007 pass; T008 negative fixture rejected); single MANDATORY Read directive preserved (per SC plan validation). Test MUST FAIL on baseline state (pre-Wave 1.1) and pass post-edits.
- [X] T034 [US1] [US2] Run `/tachi.threat-model examples/agentic-app/architecture.md` with `SOURCE_DATE_EPOCH=1700000000`. Expect ≥1 new Category-9 `AG-{N}` finding (A2A — orchestrator → worker-agent topology) AND/OR ≥1 new Category-10 `AG-{N}` finding (MCP-to-MCP trust propagation if architecture exhibits multi-MCP relay) plus preservation of existing Categories 1-8 `AG-{N}` findings, F-1 `OI-{N}` findings, F-2 `MI-{N}` findings, existing `LLM-{N}` findings. Verify cohesive Agentic-category rendering in `threats.md` (single `category: agentic` section, no fragmentation across artificial categories).
- [X] T035 [US1] [US2] Run `/tachi.risk-score` on the regenerated `agentic-app`. Verify risk-scorer processes Category-9/10 `AG-{N}` findings through `category: agentic` code paths without edit (FR-017).
- [X] T036 [US1] [US2] Run `/tachi.compensating-controls` on the regenerated `agentic-app`. Verify control-analyzer processes Category-9/10 `AG-{N}` findings through `category: agentic` code paths.
- [X] T037 [US1] [US2] Run `/tachi.infographic all` on the regenerated `agentic-app`. Regenerate all infographic JPEGs + specs.
- [X] T038 [US1] [US2] Run `/tachi.security-report` on the regenerated `agentic-app`. Regenerate `security-report.pdf` and `security-report.pdf.baseline`.
- [X] T039 [P] [US1] [US2] F-A2 referential-integrity validation on regenerated findings: run `pytest tests/scripts/test_tool_abuse_enrichment.py::test_validate_source_attribution_on_regen -v`. Confirm `validate_source_attribution` returns no errors on every Category-9/10 finding (SC-015 BLOCKER); confirm valid fixtures (T006 + T007) pass and negative fixture (T008) is rejected.
- [X] T040 [P] [US1] [US2] Backward-compat byte-identity (BLOCKER per SC-010): run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v`. Expect 5/5 pass on `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` (single-agent / single-MCP / stylistic-multi-agent topologies — multi-agent / multi-MCP topology gate per FR-011 guarantees zero Category-9/10 findings). If any baseline fails: escalate per PRD R1 with architect + team-lead approval.
- [X] T041 [P] [US3] Cohesive Agentic-category rendering verification (SC-019): grep regenerated `examples/agentic-app/threat-report.md` for `category: agentic` section. Confirm all `AG-{N}` finding IDs (Categories 1-10) appear adjacent with sequential numbering (single-namespace ID space across all 10 categories). Confirm no artificial fragmentation across "tool-abuse" vs. "asi07-inter-agent-communication" or similar sub-section headings. Record pass/fail at `.aod/results/wave3-cohesive-rendering-check.md`.
- [X] T042 [P] [US1] [US2] [US3] Git-stage regenerated artifacts for commit: `examples/agentic-app/architecture.md` (if architect chose to extend with explicit multi-MCP relay topology beyond Feature 142's `Inter-agent Communication Channel`), `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/` (if applicable), `attack-chains.md` (if applicable), `threat-*.jpg` infographics + specs, `security-report.pdf`, `security-report.pdf.baseline`.

**Checkpoint**: Wave 3 complete. Regenerated example shows Categories 9-10 findings + cohesive Agentic-category rendering; 5 non-multi-agent baselines byte-identical; all pytest green; F-A2 contract validated 3rd time (after F-1 OI-{N} + F-2 MI-{N}, now extended to AG enrichment).

---

## Phase 7: Wave 4 — Pre-Merge Validation + PR Ready (Day 1 PM / Buffer Day 1)

**Purpose**: Final validation against all 21 spec SCs + quickstart.md 18 steps before marking PR #220 ready for review. Code review double-check per PRD R7 (Pattern Category Disambiguation prose clarity) + R8 (anti-indicator predicates testable).

- [X] T043 [P] SC-001 + SC-004: verify `tool-abuse.md` `owasp_references` includes `ASI-07`; Detection Workflow Step 5 references list extended with `ASI-07`, `AML.T0060`, `CWE-287`, `CWE-345`; pre-existing entries byte-identical
- [X] T044 [P] SC-002 + SC-016: verify `wc -l .claude/agents/tachi/tool-abuse.md` ≤150; `grep -i maestro` on tool-abuse.md + detection-patterns.md returns empty
- [X] T045 [P] SC-003: verify `## Purpose` section 1-3 line extension; pre-existing prose byte-identical (structural diff returns empty for unchanged region)
- [X] T046 [P] SC-005: verify `detection-patterns.md` Pattern Categories 9 + 10 present with ≥4 indicators each, ≥1 worked example each, named mitigations, anti-indicator sections
- [X] T047 [P] SC-006: confirm T025 byte-identity result — Categories 1-8 + Overview + DFD targets + Triggers byte-identical pre/post edit
- [X] T048 [P] SC-007: verify `## Primary Sources` extended with `OWASP ASI07:2026` + `MITRE ATLAS AML.T0060`; existing entries byte-identical
- [X] T049 [P] SC-008: confirm ADR-032 Accepted at merge with all 6-7 decisions + cross-refs + Revision History per T030
- [X] T050 [P] SC-009 + SC-011: confirm regenerated `agentic-app` emits ≥1 new Category-9/10 `AG-{N}` finding with grounded mitigations + OWASP ASI07:2026 citation per T034 result
- [X] T051 [P] SC-010: confirm T040 backward-compat byte-identity pass on 5 non-multi-agent baselines
- [X] T052 [P] SC-012: verify empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` via `git diff main --stat`
- [X] T053 SC-013: 24-file zero-edit grep audit per quickstart.md Step 8 — `git diff main --stat` returns zero lines on the 12 other threat-agent files + 12 other companion `detection-patterns.md` files; orchestrator.md + finding-format-shared.md zero diff; infrastructure-tier consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) zero diff
- [X] T054 [P] SC-014: verify `schemas/finding.yaml` `git diff main` returns empty (no schema bump; first BLP-01 detection feature with no schema bump)
- [X] T055 [P] SC-015: confirm F-A2 validation passes on regenerated findings per T039 (fixture-driven + regen-based)
- [X] T056 [P] SC-017: verify `orchestrator.md` zero diff; `dispatch-rules.md` zero functional diff (cosmetic Q2 annotation if applied is single-token, contingent on T013 result)
- [X] T057 [P] SC-019: cohesive Agentic-category rendering per T041 result
- [X] T058 [P] SC-020: verify PR #220 title matches `feat(219):` Conventional Commits format; pre-merge re-verification via `gh pr view 220 --json title -q .title`
- [X] T059 **R7 + R8 code-review double-check**: senior-backend-engineer + code-reviewer review (a) pattern-catalog Pattern Category Disambiguation subsection for Cat 6 vs. Cat 10 boundary clarity (per PRD R7); (b) anti-indicator subsections in Categories 9 + 10 for testable-predicate framing (per PRD R8); (c) worked-example clearly-fictional framing — no real institutional/clinician/lawyer/advisor identities. Record pass/fail at `.aod/results/wave4-r7-r8-review.md`. **Per PRD HIGH-1 buffer-day budget model**: this review is consumed at Wave 4 PM, NOT buffer.
- [X] T060 Mark PR #220 ready for review via `gh pr ready 220`. PR body links to PRD, spec, plan, tasks, ADR-032. Request triple review (PM + Architect + Team-Lead) as part of PR process.

**Checkpoint**: All 21 SCs green; R7 + R8 code-review compliance verified; PR ready. Wave 4 buffer day available if R1 (regeneration friction) materializes or delivery-retrospective authoring deferred.

---

## Phase 8: Wave 4 — Delivery Retrospective + Coverage Matrix Update (Day 1 PM / Buffer Day 1 Wednesday 2026-04-29)

**Purpose**: Delivery retrospective slotting per PRD HIGH-1 / DoD bullet 12 / SC-021; BLP-01 Coverage Matrix update per SC-018; release-please post-merge verification per SC-020 / R6.

- [X] T061 **Delivery retrospective slotting per PRD HIGH-1 / SC-021**: if Day 1 PM merge completes with ≥1 hour residual capacity, author `specs/219-asi07-tool-abuse-enrichment/delivery.md` Day 1 PM (mirrors F-1 + F-2 same-day-as-delivery pattern). Otherwise author 2026-04-29 Wednesday (Buffer Day 1) as primary buffer-day activity. Retrospective covers: estimated vs. actual duration, **first execution of Heuristic A enrichment branch** lessons (precedent for F-6/F-7 Tier 2 ML+Mobile bundles which may also use enrichment), patterns validated (lean+skill-references additive-only edit discipline now two-tier-deep — Wave 2 for new agents F-1+F-2, Wave 1.1+2 for enrichment F-3), byte-identity preservation evidence (T025 + T040 grep proofs), 5/5-dimension reduction in edit surface vs. F-2 (no new agent / no new skill dir / no schema bump / no consumers list edit / no orchestrator edit), any deviations from PRD timeline or scope.
- [ ] T062 **SC-018 BLP-01 Coverage Matrix update**: after PR squash-merge, update `_internal/strategy/BLP-01-threat-coverage.md`: ASI07:2026 row transitions Planned → Covered with F-3 (Feature 219) named as closure feature. OWASP Agentic Top 10:2026 framework coverage advances from 5/10 (post-F-2) to 6/10 (post-F-3) — ASI07 joins ASI-01, ASI-02, ASI-04, MCP-03, MCP-05. Post-merge documentation commit (private — `_internal/` does not enter public git history per F-2 precedent).
- [ ] T063 **Release-please post-merge verification per SC-020 / R6**: within ~30s after merge, run `gh pr list --state open --search "release-please" --limit 3` to confirm release-please PR opened. If empty, push empty release-marker commit per F-212 incident recovery pattern: `git commit --allow-empty -m "feat(219): asi07 inter-agent communication enrichment — release marker" && git push origin main`. Record outcome at `.aod/results/wave4-release-please-verification.md`.
- [ ] T064 Contingent R1 buffer-day work (ONLY if regeneration friction on `agentic-app` materializes): if T034 surfaces issues with extending `agentic-app` for Categories 9-10 emission, invoke Q3 fallback to `maestro-reference` or new minimal multi-agent fixture (~0.5 day consumption) per PRD R1. If R1 does NOT materialize, buffer-day capacity redirects to T061 delivery retrospective authoring.

**Checkpoint**: Wave 4 complete. F-3 closes ASI07:2026 on BLP-01 Coverage Matrix; delivery retrospective filed; release-please confirmed firing.

---

## Phase 9: Polish & Cross-Cutting

**Purpose**: Final hygiene + documentation updates.

- [X] T065 [P] Update `CLAUDE.md` Recent Changes section with Feature 219 entry (similar to Features 201/206/212 entries). Include: F-3 Heuristic A enrichment of `tool-abuse` for ASI07:2026 closure, ADR-032 lineage with ADR-030 Decision 1 (signal-class taxonomy in LLM tier — different application of same rule applied to AG tier) + ADR-031 Decision 8 cross-refs (regex-alternation rule cross-referenced as the asymmetry F-3 does NOT invoke), BLP-01 Tier 1 framing (3rd Tier 1 feature after F-1 + F-2; first execution of enrichment branch), zero schema bump (first BLP-01 detection feature with no schema bump), 24-file zero-edit invariant preservation (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2 host files; the remaining 24 stay byte-identical), F-3 is third net-new producer flow of `source_attribution` (after F-1 OI-{N} + F-2 MI-{N}; first **enrichment** of existing populator).
- [X] T066 [P] Run quickstart.md Step 17 + Step 18 end-to-end (Coverage Matrix update + delivery retrospective) and verify per-step pass/fail. Record at `.aod/results/quickstart-smoke.md`.
- [X] T067 [P] Verify `examples/README.md` entry — F-3 does NOT add a new example (extends `agentic-app` per Q3 PM default); update only if Q3 fallback to `maestro-reference` or new minimal multi-agent fixture was invoked at T032 (same convention as Features 084/142/145/201/206).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational / Wave 1.0 + 1.1)**: T003 → T004 + T005 (architect plan-day decisions); T006 / T007 / T008 / T009 / T013 / T014 parallel; T009 → T010 → T011 (ADR-032 Proposed commit); T012 sequential after T010 (depends on Heuristic A scope locked); T013 contingent on T004 result
- **Phase 3 (US1 Wave 2)**: Depends on T012 (`tool-abuse.md` edits) + T010 (ADR-032 Proposed with Heuristic A D1/D2 scope rationale)
- **Phase 4 (US2 Wave 2)**: Depends on T015-T018 (Pattern Category 9 authored — Pattern Category 10 reuses scope-paragraph pattern). Can run in parallel with Phase 3 continuation.
- **Phase 5 (US3 Wave 4)**: Depends on Phase 6 (Wave 3 regeneration with cohesive rendering) + Phase 7 PR pre-merge validation
- **Phase 6 (Wave 3)**: Depends on Phase 3 + Phase 4 (Pattern Categories 9 + 10 authored; Wave 2 byte-identity + MAESTRO grep + line-count green)
- **Phase 7 (Wave 4 Pre-Merge)**: Depends on Phase 6 (Wave 3 complete)
- **Phase 8 (Wave 4 Retrospective + Coverage Matrix)**: Depends on Phase 7 PR merge
- **Phase 9 (Polish)**: After PR opened (can run pre-merge)

### Wave Gate Points

- **Wave 1.1 Gate**: T010 + T012 committed → unblocks Wave 2 (escalation gate fires if not by Day 1 12:00 local)
- **Wave 2 Gate**: T015-T024 complete → T025 byte-identity green + T026 MAESTRO grep clean + T027 line-count ≤150 + T028 MANDATORY Read = 1 → unblocks Wave 3
- **Wave 3 Gate**: T032-T042 complete → Q3 confirmation + ≥1 Category-9/10 finding surfaced + cohesive rendering + 5-baseline byte-identity + F-A2 validation green → unblocks Wave 4
- **Wave 4 Gate**: T043-T060 all green (21 SC checks + R7/R8 review) → T060 PR ready → unblocks merge
- **Post-merge Gate**: T031 SHA-fill + T062 Coverage Matrix update + T063 release-please verification → delivery closed

### Parallel Opportunities

- **Wave 1.1 parallel track**: T006 (Cat-9 fixture) ∥ T007 (Cat-10 fixture) ∥ T008 (negative fixture) ∥ T009 (ADR-032 skeleton) ∥ T013 (Q2 cosmetic annotation if applicable) ∥ T014 (multi-agent topology dry-run) — 6 parallel tasks
- **Wave 2 parallel track**: T015-T018 (Cat-9 authoring) ∥ T019-T022 (Cat-10 authoring) — two parallel author tracks. T023 (Disambiguation) sequential after T019. T024 (Primary Sources) parallel with T023.
- **Wave 2 EOD parallel track**: T025 (byte-identity) ∥ T026 (MAESTRO grep) ∥ T027 (line-count) ∥ T028 (MANDATORY Read) — 4 parallel verifications
- **Wave 3 parallel track**: T039 (F-A2 fixture validation) ∥ T040 (backward-compat) ∥ T041 (cohesive rendering) ∥ T042 (git-stage) — 4 parallel verifications
- **Wave 4 parallel track**: T043-T058 all parallel SC checks (16 independent verifications on different file surfaces); T059 sequential R7/R8 review before T060 PR ready

---

## Implementation Strategy

### MVP Path (Baseline — 1-day envelope per PRD §Timeline)

**Day 1 (Tuesday 2026-04-28)**:
- Morning (~0.4d): T003 architect re-verify → T004/T005 plan-day decisions → T006/T007/T008 fixtures ∥ T009 ADR-032 skeleton ∥ T013 Q2 annotation (if applicable) ∥ T014 multi-agent topology dry-run → T010 ADR-032 Decisions populated → T011 cross-refs → T012 `tool-abuse.md` 3 edits (Wave 1)
- Mid-day (~0.4d): T015-T018 Pattern Category 9 authoring ∥ T019-T024 Pattern Category 10 + Disambiguation + Primary Sources authoring (Wave 2)
- Wave 2 EOD: T025/T026/T027/T028 byte-identity + MAESTRO grep + line-count + MANDATORY Read validation
- Afternoon (~0.3d): T032 Q3 confirmation → T033 test authoring → T034 `/tachi.threat-model` regen → T035-T038 downstream pipeline → T039/T040/T041/T042 verifications (Wave 3)
- Late afternoon: T029-T030 ADR-032 Accepted transition → T043-T058 SC validation sweep → T059 R7/R8 review → T060 PR ready (Wave 4 pre-merge)
- End of day: T061 delivery retrospective (if ≥1h residual) → T065-T067 polish
- Post-merge: T031 ADR-032 SHA fill + T062 BLP-01 Coverage Matrix update + T063 release-please verification

**Buffer Day 1 (Wednesday 2026-04-29)** — per PRD HIGH-1 buffer-day budget model:
- Primary: T061 delivery retrospective (if not authored Day 1 PM)
- Contingent: T064 R1 regeneration friction absorption (if `agentic-app` extension surfaces issues — Q3 fallback to `maestro-reference` or new minimal multi-agent fixture; ~0.5 day consumption)
- If all else green: absorbed into review lag / merge cycle

**Buffer Day 2 (Thursday 2026-04-30)** — per PRD R3 multi-feature concurrency hedge:
- Reserved for F-3 + F-4 + F-5 sequencing collisions if F-4 (ASI09) or F-5 (LLM10) enters build concurrently. F-3 has smallest edit surface; sequencing F-3 first minimizes rebase friction. If R3 does NOT materialize, Buffer Day 2 capacity redirects to additional polish or remains unused.

### Escalation Paths

- **Wave 1.0 catalog drift escalation**: if T003 architect re-verification surfaces a catalog drift on any of ASI07/CWE-287/CWE-345/AML.T0060/LLM03 (e.g., upstream rename, ID change, removal), escalate before Wave 1.1 commit. F-A2 referential-integrity validator catches drift programmatically.
- **Wave 1.0 Heuristic A challenge escalation**: if architect challenges Heuristic A enrichment-vs-new-agent decision at T003, escalate per PRD R2 with 30-minute architect-PM-team-lead alignment session. SDR-001 Decision 4 is the locked resolution; ADR-030 Decision 1 + ADR-031 Decision 8 reinforce the signal-class taxonomy. Reopening would force re-adjudication of every prior Heuristic A consolidation (F-1 LLM05 → output-integrity, F-2 LLM09 → misinformation).
- **Wave 1.1 line-count escalation**: if T012 `tool-abuse.md` edits push line count >150 (target 100-106; PRD-time baseline 98), trim `## Purpose` extension to 1 line; move worked-example references to companion catalog if needed. Hard ceiling 180 (ADR-023).
- **Wave 2 byte-identity violation escalation**: if T025 structural diff reveals unintended edits to Categories 1-8 / Overview / DFD targets / Triggers, hard revert to baseline content; ADR-023 Decision 3 violation must be 100% pre-merge (SC-006 BLOCKER).
- **Wave 3 backward-compat regression escalation**: if T040 reveals byte-identity break on any of the 5 non-multi-agent baselines, investigate dispatch-tier change; F-3 should produce zero new findings on these baselines via topology gate. Likely cause: cross-feature edit drift; team-lead approves resolution path.
- **Wave 3 zero-Category-9/10 emission escalation**: if T034 reveals zero new ASI07-citing findings on regenerated `agentic-app`, architect re-evaluates example target via Q3 fallback (T032 decision point). Invoke `maestro-reference` extension or new minimal multi-agent fixture if `agentic-app` does not exhibit a sufficiently clean inter-agent channel signal post-Feature-142.
- **Wave 3 F-A2 validation failure escalation**: if T039 reveals referential-integrity errors on Category-9/10 findings, verify catalog citations match `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml`; remove offending citation. AML.T0060 + LLM03 are optional related citations — if catalog drift detected, demote to prose-only and re-emit findings without the absent citation.
- **Wave 4 PR title escalation**: if T058 reveals PR title not Conventional Commits format, retitle via `gh pr edit 220 --title "feat(219): asi07-tool-abuse-enrichment"` before merge. Pre-existing draft PR #220 already has correct title from `/aod.plan` per PRD §Release Discipline subsection.
- **Post-merge release-please skip escalation**: if T063 reveals no release-please PR opens within ~30s, push empty `feat(219): asi07 enrichment — release marker` commit per F-212 incident recovery pattern. Buffer Day 1 absorbs recovery time if needed.

---

## Notes

- [P] tasks = different files / independent commands / no dependencies on incomplete tasks
- [Story] label maps task to user story (US1 = Pattern Category 9 / A2A inter-agent channel detection; US2 = Pattern Category 10 / MCP-to-MCP trust propagation detection; US3 = Cohesive Agentic-category rendering with Heuristic A enrichment / ADR-032)
- Commit boundaries: Wave 1.1 ADR-032 Proposed commit + `tool-abuse.md` 3 edits + fixtures is atomic; subsequent waves commit at wave-gate checkpoints
- ADR-032 Proposed commit at T010 unblocks Wave 2; ADR-032 Accepted transition at T029-T030 happens pre-PR ready
- 24-file zero-edit invariant (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2 host files; 24 unchanged) is enforced by T053 grep audit — verify this as final pre-merge check
- Post-merge: T031 SHA-fill is the last task in the per-feature sequence (updates Revision History with the squash commit short SHA); T062 Coverage Matrix update + T063 release-please verification follow
- All PRD Triad-fix predicates traceable:
  - **PRD MEDIUM-1 (Q1 single-category resolution)** → RESOLVED at PRD time; T015 Pattern Category 9 ships single-category indicator set; T010 D1 supporting evidence in ADR-032
  - **PRD MEDIUM-2 (Pattern Category Disambiguation FR-2 paragraph)** → T023 Pattern Category Disambiguation subsection; T010 D7 Pattern Category Disambiguation Decision in ADR-032; T059 R7 code-review boundary clarity check
  - **PRD HIGH-1 (Buffer Day 1 retrospective slotting + DoD bullet 12)** → T059 R7/R8 review consumed at Wave 4 PM (NOT buffer); T061 delivery retrospective slotting (Day 1 PM if ≥1h residual; otherwise Buffer Day 1)
  - **PRD HIGH-2 (PR title contract / Release Discipline)** → T058 SC-020 PR title verification; T063 release-please post-merge verification + recovery via empty release-marker commit per F-212 precedent
  - **PRD MEDIUM-1 team-lead (effort-S asymmetry)** → All 21 spec SCs covered in Wave 4 sweep (T043-T058); architect plan-day AC-to-test mapping at T033 test authoring
  - **PRD MEDIUM-4 team-lead (Q5 build-day calendar)** → RESOLVED at PRD time; Implementation Strategy notes 2026-04-28 Tuesday Day 1 build per established Tuesday-after-Monday-plan cadence
  - **PRD R3 multi-feature concurrency hedge** → Buffer Day 2 reserved per Implementation Strategy; F-3 ships first (smallest surface) to minimize rebase friction
  - **Q2 architect plan-day decision (cosmetic dispatch annotation)** → T004 plan-day decision recorded; T013 conditional execution
  - **Q3 architect plan-day decision (example regeneration target)** → T005 plan-day decision; T032 confirmation point; T064 contingent R1 fallback if needed
  - **Q4 architect plan-day decision (anti-indicator section)** → T016 (Cat-9) + T020 (Cat-10) anti-indicator sections per Q4 default YES
  - **Spec FR-021 / SC-020 (Conventional Commits PR title)** → Draft PR #220 already opened with `feat(219):` title at `/aod.plan` stage; T058 pre-merge re-verification; T063 post-merge release-please verification
  - **Spec SC-021 / DoD bullet 12 (delivery retrospective)** → T061 Wave 4 PM or Buffer Day 1 authoring
  - **First-execution Heuristic A enrichment branch precedent** → T010 D1 ADR-032 Decision; T061 retrospective lessons captured for F-6/F-7 Tier 2 ML+Mobile bundles
  - **F-A2 third-producer-flow validation** → T039 referential-integrity validation on Category-9/10 fixtures + regen findings; F-3 is third producer flow after F-1 OI-{N} + F-2 MI-{N}; first **enrichment** of existing populator (Categories 1-8 already populate via prior wiring)
