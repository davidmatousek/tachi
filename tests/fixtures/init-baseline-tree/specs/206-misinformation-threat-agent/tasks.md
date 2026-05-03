---
description: "Task breakdown for Feature 206 — misinformation threat agent (OWASP LLM09:2025)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-23
    status: APPROVED
    notes: "Tasks.md faithfully decomposes plan.md into 62 tasks across 10 phases with full coverage — 3 user stories with correct [US#] tagging, 19 spec FRs traceable, 14 spec SCs covered (13 in Wave 5 sweep T042-T054 + SC-013 at T058), 14 out-of-scope items preserved, all 6 Triad HIGH/MEDIUM fixes explicitly annotated in Notes section (H1 AML.T0042, HIGH-1 buffer model, HIGH-2 retrospective slotting, MEDIUM-2 R8 concurrency, MEDIUM-3 FR-7 5-callsite reconciliation, MEDIUM-4 architect FR-7 edit ownership). Out-of-scope discipline rigorous (F-A3 24-file invariant preserved in T050; infrastructure-tier carve-out; F-3/F-4/F-5/F-6 separation). PRD Q1-Q5 architect-owned decisions resolved with traceability to specific task IDs. Timeline fits PRD 2-day envelope with 2026-04-29 buffer. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW. PM APPROVED. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-23
    status: APPROVED
    notes: "Tasks.md technically sound on all 6 correctness dimensions: (1) test-first discipline — T005 regex test authored before T006 schema bump; (2) T006 atomic — version + regex + examples in one commit; (3) ADR-031 dual-commit lifecycle T009→T010 (9 decisions including D8 2nd application of ADR-030 Decision 8 + D9 CWE-1039 exclusion)→T011→T022→T025 correctly sequenced; (4) F-1 5-callsite carry-over reconciliation verified — T026 reconciles orchestrator.md:296+:370, T027 reconciles dispatch-rules.md LLM list + :120 + trigger-keyword rules, T030 quintet consistency audit; (5) 24-file zero-edit invariant (22 original + F-1's 2) enumerated in T050; (6) source_attribution contract correct — T007 valid fixture cites LLM09+CWE-345 catalog-verified, T008 invalid fixture cites AML.T0042 confirmed-absent for rejection test, T014 pattern catalog cites only catalog-resolvable IDs for source_attribution, T038 regen validation. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW. APPROVED. Full review at .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-23
    status: APPROVED
    notes: "Tasks.md faithfully operationalizes plan.md into 62 atomic tasks across 10 phases with calendar-verified day assignments fitting the 2-day envelope + 2026-04-29 buffer. All 7 PRD Team-Lead fixes traceable to task IDs: HIGH-1 buffer-day budget model (T055 R5 polish at Wave 2.2 + T059 contingent R2); HIGH-2 delivery retrospective slotting (T057 Wave 2.3 PM or buffer-day); MEDIUM-1 consumers-list placement (T028 architect adjudication); MEDIUM-2 R8 concurrency hedge (Implementation Strategy); MEDIUM-3 FR-7 extended to 5-callsite (T026+T027+T030); MEDIUM-4 architect edit ownership (T026/T027 owner annotations); capacity check senior-backend-engineer 60-70% Day 1 / 40-50% Day 2 preserved. Critical path T004→T006→T010→Wave 2→3→4→5→6 correctly sequenced with no cycles. Parallelization maxima (5 Wave 1.1 / 3 Wave 3 / 13 Wave 5) aligned with capacity. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW. APPROVED. Ready for /aod.build. Full review at .aod/results/team-lead.md."
---

# Tasks: `misinformation` Threat Agent (OWASP LLM09:2025)

**Input**: Design documents from `/specs/206-misinformation-threat-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/finding-contract.md, quickstart.md
**Branch**: `206-misinformation-threat-agent`

**Tests**: Regex unit test + fixture-driven `source_attribution` validation test REQUIRED (per SC-010 + SC-012); backward-compat byte-identity is an existing harness (existing `tests/scripts/test_backward_compatibility.py`).

**Organization**: Tasks are grouped into waves matching plan.md's 6-wave structure. Wave 1.1 schema-lock + ADR-031 Proposed is the unblock-gate; Wave 2 pattern + agent authoring proceeds after; Wave 3 orchestrator + shared edits with F-1 5-callsite carry-over reconciliation; Wave 4 example regeneration; Wave 5 ADR Accepted + PR; Wave 6 buffer day with delivery retrospective + Coverage Matrix update.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 = LLM09 factual-output detection, US2 = grounding/verification mitigation guidance, US3 = Heuristic A signal-class distinctness / ADR-031)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure feature directory and branch are correctly configured. Branch already created at start of `/aod.plan`; directories already scaffolded by setup scripts.

- [X] T001 Verify working directory clean on branch `206-misinformation-threat-agent` and `specs/206-misinformation-threat-agent/` contains spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md
- [X] T002 [P] Create directory `.claude/skills/tachi-misinformation/references/` (companion skill)
- [X] T003 [P] Create directory `tests/scripts/fixtures/misinformation/` (test fixtures)

---

## Phase 2: Foundational — Wave 1.0 & 1.1 (Blocking Prerequisites)

**Purpose**: Schema-lock commit + ADR-031 Proposed commit unblock parallel Wave 2 pattern authoring. Escalation gate fires if Heuristic A signal-class verification surfaces a subsume signal before Day 1 EOD.

**CRITICAL**: No user story work can begin until T006 (schema bump) and T010 (ADR-031 Proposed) are committed.

### Wave 1.0 — Architect Heuristic A Verification (30-60 min, Day 1 AM)

- [X] T004 Architect verifies Heuristic A signal-class intact: ADR-030 Decision 1 bounds F-1 scope to downstream-execution-sanitization (machine-victim, bytes/strings/syntax primitives); F-2 inherits factual-integrity scope carve-out (human-victim and decision-cascade-victim, factual-content primitives). Capture verification in a short decision memo saved at `.aod/results/heuristic-a-verification.md` for traceability. If a subsume-into-output-integrity signal surfaces during pattern authoring later, re-escalate per PRD R1 Day 1 gate.

### Wave 1.1 — Schema Lock + ADR-031 Proposed (parallel, Day 1 AM/PM)

- [X] T005 [P] Write regex unit test at `tests/scripts/test_misinformation.py` covering: (a) pre-1.7 IDs (`S-1`, `T-1`, `R-1`, `I-1`, `D-1`, `E-1`, `AG-1`, `LLM-1`, `AGP-1`, `OI-1`) remain valid, (b) `MI-1`, `MI-10`, `MI-99` match the 1.7 regex, (c) non-matching inputs (`MI1`, `MIA-1`, `mi-1`, empty string) are rejected. Test MUST FAIL at authoring time (before T006 regex bump).
- [X] T006 Modify `schemas/finding.yaml`: line 13 `schema_version: "1.6"` → `"1.7"`; line 18 `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"`; add an `MI-1` entry to the `examples:` list for completeness (per PRD FR-4). Verify T005 regex test now passes.
- [X] T007 [P] Author test fixture `tests/scripts/fixtures/misinformation/valid_mi_finding.yaml` — complete `MI-1` finding with valid `source_attribution` citing `owasp:LLM09` (primary) + `cwe:CWE-345` (related), populated grounding-mitigation text (e.g., "Mandatory RAG grounding with per-claim source attribution"), description distinguishing factual-emission sub-class.
- [X] T008 [P] Author test fixture `tests/scripts/fixtures/misinformation/invalid_attribution_finding.yaml` — finding with `source_attribution` citing AML.T0042 (confirmed absent from F-A1 `mitre-atlas.yaml` catalog) to validate that `validate_source_attribution` rejects the finding per F-A2 referential-integrity rule.
- [X] T009 [P] [US3] Author ADR-031 skeleton at `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` with **Status: Proposed** (per FR-018 / Q5 / plan Wave 1.1): title block, Context section (BLP-01 Tier 1 framing, factual-integrity signal-class problem statement, LLM09 Planned → Covered transition), Decisions section placeholder (populated in T010), Consequences placeholder, Cross-References placeholder, Revision History table with one initial Proposed row, no Layer 2 / commercial framing.
- [X] T010 [US3] Populate ADR-031 Decisions section in `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`: (D1) adopt new `misinformation` agent for LLM09 closure; (D2) **Heuristic A three-way scope rationale** — distinct from `prompt-injection` (input-side attacker-controlled injection; machine-attacker, input primitives); distinct from `output-integrity` (output-side execution-sink sanitization per **ADR-030 Decision 1** cross-reference — machine-victim, bytes/strings/syntax primitives); scoped to factual-integrity (grounding, verification, HITL, calibration; human-victim and decision-cascade-victim, factual-content primitives). Cite GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy. Include one-sentence acknowledgment that ADR-030 Decision 1 explicitly left factual-integrity open for F-2 (not a re-adjudication); (D3) lean-agent shape conformance per ADR-023 (single-point load, ≤150 lines, zero MAESTRO references); (D4) Pattern category scope — 5 categories per Q1 (Q1 candidates "Model-Specific Hallucination" + "Feedback-Loop Overreliance" deferred to catalog-enrichment follow-on F-2.1 or F-3/F-6 scope); (D5) 24-file zero-edit invariant (22 original + F-1's 2) preserved with grep-auditable enumeration; (D6) Proposed → Accepted dual-commit pattern per ADR-027/028/029/030; (D7) post-merge SHA fill recording squash commit; (D8) **Schema bump 1.6 → 1.7 as 2nd recorded application of ADR-030 Decision 8** regex-alternation minor-bump rule (first application was F-1's 1.5 → 1.6; F-2 preserves backward compatibility identically); (D9) **CWE-1039 deliberate-exclusion note per MEDIUM-3**: model-evasion CWE out of scope; pattern catalog focuses on factual-content primitives, not model-robustness primitives. Commit ADR-031 Proposed at Wave 1.1.
- [X] T011 [US3] Populate ADR-031 Cross-References in `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`: ADR-021 (determinism baseline), ADR-023 (lean-agent pattern), ADR-026 (minor-bump rule; extended by ADR-030 Decision 8), ADR-027 (F-A1 taxonomy enum source), ADR-028 (F-A2 `source_attribution` contract — F-2 is second producer after F-1), ADR-029 (F-B downstream consumer — `has-source-attribution` fires true on regen), **ADR-030 (F-1 precedent — Decision 1 scope bounds F-1 leaving factual-integrity for F-2; Decision 8 regex-alternation minor-bump rule F-2 invokes as 2nd application)**.
- [X] T012 [P] Pre-Wave 4 static DFD inspection check (architect MEDIUM-4 FP dry-run): grep all 6 baseline architectures for the 12 misinformation trigger keywords (`factual output`, `citation generation`, `recommendation engine`, `decision support`, `RAG`, `grounding`, `hallucination`, `advisory`, `medical`, `legal`, `financial`, `clinical`). Verify: (a) 5 non-factual baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) produce zero matches OR matches appear only in stylistic/non-factual contexts; (b) `agentic-app` post-F-1 state contains indicators suggesting regeneration candidate (factual-output extension will add matches). Record results at `specs/206-misinformation-threat-agent/dispatch-fp-check.md`. If non-factual baselines show unexpected matches: flag for architect review before Wave 3 (pre-edit to preserve byte-identity invariant SC-006).

**Checkpoint**: Schema locked at 1.7; ADR-031 Proposed committed with all 9 decisions including regex-extension 2nd application + CWE-1039 exclusion; fixtures authored; baseline dispatch FP dry-run clean. Wave 2 can now start.

**Escalation Gate**: If T004 Heuristic A verification surfaces a subsume signal or T010 not complete by Day 1 EOD (Monday 2026-04-27 23:59 local), surface user tie-break escalation before Day 2 AM. Do NOT proceed to Wave 2 without ADR-031 Proposed commit.

---

## Phase 3: User Story 1 — Ungrounded-Factual-Output Detection (Priority: P1) MVP

**Goal**: Ship the new `misinformation` agent + companion skill pattern catalog so that running `/tachi.threat-model` on an architecture with factual-output indicators emits ≥1 `MI-{N}` finding with valid `source_attribution` and zero findings on non-factual architectures.

**Independent Test**: Run the pipeline on `examples/agentic-app/architecture.md` (post-extension with factual-output sub-component); confirm ≥1 `MI-{N}` finding in the output `threats.md` with `category: llm`, `source_attribution` citing OWASP LLM09:2025 primary + CWE-345 (and/or CWE-223) related, mitigation text naming a specific grounding/verification/HITL/calibration mechanism. Confirm zero `MI-{N}` findings on 5 non-factual baselines.

### Wave 2 — Pattern Catalog + Agent Authoring (0.5d, Day 1 PM)

- [X] T013 [US1] Author `.claude/skills/tachi-misinformation/references/detection-patterns.md` per data-model.md E2: frontmatter (`name`, `description`, `consumers: [tachi-misinformation]`, `last_updated: 2026-04-27`), `## Overview` paragraph (scope — factual-integrity signal class; three-way distinctness from prompt-injection input-side and output-integrity output-sanitization; OWASP LLM09:2025 canonical surface), `## Detection Scope` with 12 trigger keywords per Q2 architect decision (`factual output`, `citation generation`, `recommendation engine`, `decision support`, `RAG`, `grounding`, `hallucination`, `advisory`, `medical`, `legal`, `financial`, `clinical`) and `## Applicable DFD Element Types` = `Process` only per Q3.
- [X] T014 [US1] Author `## Detection Patterns` section of `detection-patterns.md` with **5 numbered categories**: (1) **Ungrounded Factual Emission** (primary `OWASP LLM09:2025`, related `CWE-345`), (2) **Citation Fabrication** (primary `OWASP LLM09:2025`, related `CWE-345`), (3) **Overreliance / Missing HITL on Decision-Critical Output** (primary `OWASP LLM09:2025`, related `CWE-223` + optional `CWE-345`), (4) **Retrieval-Grounding Gaps** (primary `OWASP LLM09:2025`, related `CWE-345`), (5) **Confidence-Calibration Absence** (primary `OWASP LLM09:2025`, related `CWE-345`). Each category MUST include 3-6 indicators + ≥1 anti-indicator per architect MEDIUM-5 + ≥1 worked example (clearly-fictional framing per NFR-6) + primary/related citations + trigger keywords + applicable DFD element types. Pattern-catalog Primary Sources list cites OWASP LLM09:2025 (catalog-resolvable), CWE-345 + CWE-223 (catalog-resolvable), **AML.T0042 Verify Attack (prose-only — catalog absent per PRD FR-5)**, NIST AI 600-1 §2.4 Hallucination (prose-only — section IDs not catalogued).
- [X] T015 [P] [US1] Author `.claude/skills/tachi-misinformation/README.md` — mirror `.claude/skills/tachi-output-integrity/README.md` shape (title + short description + `Consumers:` list + purpose header + layout overview). Keep under 50 lines.
- [X] T016 [US1] Author `.claude/agents/tachi/misinformation.md` 5-section canonical shape per data-model.md E1: YAML frontmatter (`name: misinformation`, `description`, `tools: Read, Glob, Grep`, `model: sonnet`) → metadata YAML block (`category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM09:2025]`, `output_schema: ../../../schemas/finding.yaml`; NO `agentic_pattern` field per FR-016) → `## Purpose` section (describe factual-integrity threat surface, 5 pattern categories, explicit three-way distinctness — distinct from prompt-injection input-side, distinct from output-integrity output-sanitization per ADR-030 Decision 1, scoped to factual-integrity; forward-reference `prompt-injection` and `output-integrity` as adjacent-but-distinct concerns) → `## Skill References` table (3 rows: detection-patterns, severity-bands-shared, finding-format-shared) → `## Detection Workflow` with exactly ONE `**MANDATORY**: Read` directive at section start.
- [X] T017 [US1] Complete the `## Detection Workflow` steps in `.claude/agents/tachi/misinformation.md`: step 1 (trigger keyword identification — 12 keywords), step 2 (**two-part emission gate per FR-011 — BOTH keyword match AND factual-output indicator required; purely stylistic LLM output emits zero findings**), step 3 (pattern classification across 5 categories), step 4 (severity via OWASP 3×3 distinguishing consumer-facing high-stakes HIGH/CRITICAL vs internal low-stakes MEDIUM or below), step 5 (emission with `source_attribution` + named grounding/verification/HITL/calibration mitigation), step 6 (zero-speculation on non-qualifying arch — keyword-only match emits nothing). Reference quickstart.md Step 9 for the emission shape.
- [X] T018 [P] [US1] Structural validation: `wc -l .claude/agents/tachi/misinformation.md` ≤ 150 (hard cap 180); `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/misinformation.md` = 1; `grep -i maestro .claude/agents/tachi/misinformation.md .claude/skills/tachi-misinformation/references/detection-patterns.md` returns empty. Record pass/fail at `.aod/results/wave2-structural-check.md`.

**Checkpoint**: Wave 2 complete. Agent + companion authored. Structural checks green. Ready for Wave 3 orchestrator registration.

---

## Phase 4: User Story 2 — Named Grounding / Verification Mitigation Guidance (Priority: P1)

**Goal**: Every emitted `MI-{N}` finding MUST carry `mitigation` text naming a specific grounding, verification, HITL, or calibration mechanism matched to the finding's pattern category — not generic "ground the LLM" prose.

**Independent Test**: For each `MI-{N}` finding in regenerated `examples/agentic-app/threats.md`, inspect the `mitigation` field: it names at least one of the required pattern-specific mechanisms per US-2 acceptance scenarios (mandatory RAG grounding / retrieval-strength metric / confidence-calibration layer for ungrounded factual emission; output-time citation verification / strict citation-token decoder constraint for citation fabrication; HITL review queue / risk-threshold escalation / AI-provenance disclosure for overreliance; declared retrieval-strength metric / versioned retrieval corpus with staleness policy for retrieval-grounding gaps; calibration layer + ECE monitor / refusal pattern for confidence-calibration absence).

### Wave 2 (parallel with US1) — Example Findings + Mitigation Text

- [X] T019 [US2] Author `## Example Findings` section of `.claude/agents/tachi/misinformation.md` with **2-3 worked `MI-{N}` example findings** demonstrating (a) ungrounded factual emission on medical summarizer with `mandatory RAG grounding with per-claim source attribution` mitigation, (b) citation fabrication on legal-research agent with `output-time citation verification against retrieved source URIs` mitigation, optionally (c) overreliance on financial-advisory agent with `human-in-the-loop review queue on decision-critical output` mitigation. Each example MUST populate `source_attribution` correctly per contracts/finding-contract.md I4 mapping table (LLM09 primary + CWE-345 and/or CWE-223 related).
- [X] T020 [US2] In `detection-patterns.md` pattern categories (authored in T014), each category MUST include at least one worked example whose mitigation text names a specific grounding/verification/HITL/calibration mechanism (not generic). Reviewer checkpoint per FR-017: **each worked example's `description` field MUST explicitly distinguish factual-emission / citation-integrity / decision-overreliance sub-classes** — surface this as an explicit acceptance predicate. **NFR-6 compliance check**: all worked examples use clearly-fictional framing ("a hypothetical clinical-decision-support system...", "a generic legal-research tool...", "a synthetic financial-advisory component..."); no real institutional names, no real clinician / lawyer / advisor identities, no real regulatory-citation examples.
- [X] T021 [P] [US2] Sanity grep: `grep -iE '(ground the llm|verify the output|add hitl|sanitize)' .claude/skills/tachi-misinformation/references/detection-patterns.md .claude/agents/tachi/misinformation.md` MUST NOT return a line where those generic phrases appear without a specific mechanism named in the same sentence or adjacent line. Record pass/fail at `.aod/results/wave2-mitigation-specificity-check.md`.

**Checkpoint**: Mitigation specificity verified. FR-017 three-sub-class distinction explicit. NFR-6 clearly-fictional framing verified. Ready for Wave 3.

---

## Phase 5: User Story 3 — Factual-Integrity as a First-Class Distinct Threat Class (Priority: P1)

**Goal**: ADR-031 Accepted at F-2 merge contains explicit Heuristic A three-way signal-class determination; regenerated example architecture renders `LLM-{N}`, `OI-{N}`, and `MI-{N}` findings adjacent (not synthesized) in the `category: llm` section of `threat-report.md`; BLP-01 Coverage Matrix transitions LLM09:2025 Planned → Covered with F-2 named as closure feature.

**Independent Test**: ADR-031 at F-2 merge: (a) Status: Accepted, (b) Decisions section has D2 explicitly resolving three-way scope boundaries (distinct from prompt-injection / distinct from output-integrity per ADR-030 Decision 1 cross-reference / scoped to factual-integrity), (c) Decisions section references GUIDE-threat-coverage-research §11, (d) D8 cross-references ADR-030 Decision 8 regex-alternation minor-bump rule as 2nd application, (e) D9 CWE-1039 deliberate-exclusion note present, (f) Revision History shows Proposed → Accepted transition with dates, (g) agent's `## Purpose` section explicitly forward-references `prompt-injection` and `output-integrity` as adjacent-but-distinct concerns.

### Wave 1.1 — ADR-031 Proposed authoring (T009-T011 above)

See Phase 2 T009, T010, T011 — ADR-031 Proposed authoring happens at Wave 1.1 to unblock Wave 2.

### Wave 5 — ADR-031 Accepted Transition (Day 2 PM)

- [X] T022 [US3] Transition ADR-031 `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` Status: Proposed → Accepted. Add Revision History row: `| 2026-04-28 | Proposed → Accepted | PR #NNN pending merge | provisional |` (update date and PR number at authoring time).
- [X] T023 [US3] Verify ADR-031 body completeness: all 9 Decisions (D1-D9) populated (including D8 ADR-030 Decision 8 2nd application + D9 CWE-1039 exclusion); Consequences section populated; Cross-References section lists ADR-021/023/026/027/028/029/030 per T011; Revision History tracks Proposed → Accepted. Record checklist pass/fail at `.aod/results/adr-031-completeness-check.md`.
- [X] T024 [US3] Verify agent `## Purpose` section in `.claude/agents/tachi/misinformation.md` explicitly distinguishes three signal classes: (a) not input-side attacker-induced wrong output (that's `prompt-injection`), (b) not output-side crossing-unsanitized-boundary (that's `output-integrity` per ADR-030 Decision 1), (c) scoped to architecture-level grounding/verification/HITL/calibration absence. Forward-references to `prompt-injection` and `output-integrity` as adjacent-but-distinct concerns are present.

### Post-Merge (Wave 6 or later)

- [X] T025 [US3] After PR squash-merge: update ADR-031 Revision History with `| YYYY-MM-DD | Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed |` (ADR-027/028/029/030 precedent). **Completed 2026-04-24: SHA-fill row added recording squash commit `b703e52be2fa` (full: `b703e52be2fac041dd9b5ffc23b1f5b610e8a262`) merged at `2026-04-24T13:51:00Z`. Provisional Accepted-date preserved per ADR-030 precedent.**

**Checkpoint**: Heuristic A three-way signal-class discipline locked in public ADR; LLM09 coverage surface documented.

---

## Phase 6: Wave 3 — Orchestrator Registration + F-1 Carry-Over Reconciliation + Shared-Reference Additive Edits (Day 2 AM, 0.3d)

**Purpose**: Register the new agent in orchestrator dispatch (FR-004), reconcile F-1 carry-over callsites (5 reconciliation points), and extend the shared-reference consumers list (FR-005). All edits MUST be additive; ADR-023 Decision 3 byte-identity on `## ` headings is enforced on the shared-reference edit. Edit owner: architect per PRD MEDIUM-4.

- [X] T026 Modify `.claude/agents/tachi/orchestrator.md`: (a) insert `  - misinformation` after the `output-integrity` entry in the AI-tier dispatch list; (b) **F-1 carry-over reconciliation at line 296**: update sequential-mode text from `(prompt-injection then data-poisoning then model-theft)` → `(prompt-injection then data-poisoning then model-theft then output-integrity then misinformation)` extending the pre-F-1 three-agent text to the full five-agent quintet; (c) **F-1 carry-over reconciliation at line 370**: update LLM Threats row from `prompt-injection, data-poisoning, model-theft` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`. Zero changes to STRIDE tier or infrastructure tier.
- [X] T027 Modify `.claude/skills/tachi-orchestration/references/dispatch-rules.md`: (a) extend the LLM dispatch quartet (post-F-1; lines 71-74) to **quintet** by adding `- \`misinformation\` (OWASP LLM09:2025)` after the `output-integrity` line with FR-011-style two-part emission activation rule (requires BOTH LLM keyword match AND factual-output indicator); (b) **F-1 carry-over reconciliation at line 120**: update table row agent list from `prompt-injection, data-poisoning, model-theft` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`; (c) extend trigger-keyword rules section with misinformation's 12-keyword set per Q2. **SCOPE EXTENDED per MEDIUM-3** (see `.aod/results/medium-3-quintet-mismatch-2026-04-23.md`): T030 audit surfaced 7 additional F-1 carry-over callsites beyond the 5 originally enumerated; architect re-dispatch reconciled dispatch-rules.md:106/110/147/153/160/371 + orchestrator.md:578 to post-F-2 quintet + updated agent cardinalities (5 AI → 7 AI, 11 detection → 13 detection).
- [X] T028 [P] Modify `.claude/skills/tachi-shared/references/finding-format-shared.md`: in the frontmatter `consumers:` list (post-F-1 state), insert `- misinformation` on a new line between `  - output-integrity` and `  - risk-scorer` (tier-grouping placement per FR-5). ZERO changes to any body `## ` heading.
- [X] T029 Structural-diff validation on `finding-format-shared.md`: run `git diff main -- .claude/skills/tachi-shared/references/finding-format-shared.md | grep -E '^[+-]## '`. MUST return empty (no `## ` heading changes per ADR-023 Decision 3). Record pass/fail at `.aod/results/wave3-structural-diff-check.md`.
- [X] T030 Quintet-consistency grep audit (5-callsite F-1 carry-over verification per MEDIUM-3): verify all 5 callsites reference the five-agent quintet (`prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`) consistently. Callsites: (1) `orchestrator.md:296` sequential-mode text, (2) `orchestrator.md:370` LLM Threats row, (3) `dispatch-rules.md` LLM dispatch list (lines 71-74 extended), (4) `dispatch-rules.md:120` table row, (5) `dispatch-rules.md` trigger-keyword rules section. Record quintet-consistency results at `.aod/results/wave3-quintet-consistency-check.md`. **EXTENSION**: Part B audit revealed 7 additional callsites (dispatch-rules.md:106/110/147/153/160/371 + orchestrator.md:578); MEDIUM-3 escalation path applied; all 12 now at quintet. Anti-grep 0/6 confirms zero stale F-0/F-1 text remains in the 2 edited files.

**Checkpoint**: Orchestrator registered with F-1 carry-over reconciled across 5 callsites; shared reference extended; quintet consistency verified. Ready for Wave 4 example regeneration.

---

## Phase 7: Wave 4 — Example Regeneration + Backward-Compatibility Verification (Day 2 PM, 0.5d)

**Purpose**: Regenerate `examples/agentic-app/` with the new agent active and a factual-output sub-component added; verify ≥1 `MI-{N}` finding + three-signal-class discipline (adjacent LLM-{N}, OI-{N}, MI-{N}); verify 5 non-factual baselines remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-006 BLOCKER). Q4 decision confirmation point: if `agentic-app` cumulative-state cost exceeds convention-preservation benefit, invoke Q4 fallback to new `advisory-app` consuming 0.5-day buffer per PRD R2.

- [X] T031 Q4 fallback decision point: architect reviews `agentic-app` post-F-1 architecture and confirms extend-in-place vs fallback to new `advisory-app`. PM default: extend `agentic-app`. Record decision at `.aod/results/wave4-regen-target-decision.md`. **DECIDED**: EXTEND agentic-app (cumulative-state cost low post-F-1). Sub-component: Clinical Advisory Sub-Agent per `.aod/results/wave4-factual-output-subcomponent-design.md`.
- [X] T032 Extend `examples/agentic-app/architecture.md` with a factual-output sub-component (e.g., LLM-backed advisory sub-agent emitting medical/legal/financial summaries or decision recommendations) structurally satisfying at least 2 of the 12 factual-output trigger keywords plus ≥1 factual-output indicator. Preserve existing F-1 `OI-{N}` component surface; do not regress `LLM-{N}` prompt-injection surface. **APPLIED**: 9 insertions (1 node + 6 flows + 1 table row + 1 bullet), 0 deletions. Keywords matched: clinical, advisory, medical, grounding, \bRAG\b (5 of 12).
- [X] T033 Run `/tachi.threat-model examples/agentic-app/architecture.md` with `SOURCE_DATE_EPOCH=1700000000`. Expect ≥1 new `MI-{N}` finding on the factual-output sub-component plus preservation of F-1 `OI-{N}` + existing `LLM-{N}` findings. Verify three-signal-class discipline in rendered `threats.md` AI-category section (findings adjacent, not synthesized). **COMPLETE**: 3 MI findings (MI-1/2/3 on Clinical Advisory Sub-Agent covering FR-017 Categories 1, 3, 4). 83 total findings. Three-signal-class verified (Section 4.1 MI, 4.2 OI, cross-section LLM). Schema 1.7 applied. Output at `examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/` (gitignored local).
- [X] T034 Run `/tachi.risk-score` on the regenerated `agentic-app` threats. Verify risk-scorer processes `MI-{N}` findings through `category: llm` code paths without edit (FR-014).
- [X] T035 Run `/tachi.compensating-controls` on the regenerated `agentic-app`. Verify control-analyzer processes `MI-{N}` findings through `category: llm` code paths.
- [X] T036 Run `/tachi.infographic all` on the regenerated `agentic-app`. Regenerate all 6 infographic JPEGs + specs.
- [X] T037 Run `/tachi.security-report` on the regenerated `agentic-app`. Regenerate `security-report.pdf` and `security-report.pdf.baseline`.
- [X] T038 [P] F-A2 referential-integrity validation: run `pytest tests/scripts/test_misinformation.py` — all tests pass including a fixture-driven test invoking `validate_source_attribution` on the regenerated `MI-{N}` findings (MUST confirm AML.T0042 absence from `source_attribution` on all emitted findings per FR-5).
- [X] T039 [P] Backward-compat byte-identity: run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v`. Expect 5/5 pass on `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` (factual-output indicators not present — two-part emission gate guarantees zero `MI-{N}` findings). If any baseline fails: escalate per PRD R6 with architect + team-lead approval.
- [X] T040 [P] Three-signal-class discipline verification (SC-014): grep regenerated `examples/agentic-app/threat-report.md` category: llm section. Confirm `LLM-{N}`, `OI-{N}`, and `MI-{N}` finding IDs appear adjacent (not synthesized into unified prose) and each carries its own `source_attribution` primary (LLM01, LLM05, LLM09 respectively). Record pass/fail at `.aod/results/wave4-three-signal-class-check.md`.
- [X] T041 [P] Git-stage regenerated artifacts for commit: `examples/agentic-app/architecture.md` (extended), `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md` (if applicable), `threat-*.jpg` × 6 + corresponding specs, `security-report.pdf`, `security-report.pdf.baseline`.

**Checkpoint**: Wave 4 complete. Regenerated example shows MI findings + three-signal-class discipline; 5 baselines byte-identical; all pytest green.

---

## Phase 8: Wave 5 — Pre-Merge Validation + PR (Day 2 PM, 0.3d)

**Purpose**: Final validation against all 14 spec SCs + quickstart.md 12 steps before opening PR. Code review double-check per R5 NFR-6 compliance (healthcare/legal/finance clearly-fictional framing).

- [X] T042 [P] SC-001: verify `misinformation.md` ≤150 lines; 1 `**MANDATORY**: Read`; under `## Detection Workflow` heading
- [X] T043 [P] SC-002: verify `detection-patterns.md` has ≥5 pattern categories, each with worked example + anti-indicator + primary/related citations + trigger keywords + DFD element types
- [X] T044 [P] SC-003: verify `finding-format-shared.md` edit is additive-only per T029 result
- [X] T045 SC-004: confirm `/tachi.threat-model` on regenerated `agentic-app` emits ≥1 `MI-{N}`; non-qualifying baselines emit zero (two-part emission gate)
- [X] T046 SC-005: confirm ADR-031 Accepted at merge with all 9 decisions (D1-D9) + cross-refs + Revision History per T023
- [X] T047 [P] SC-006: confirm T039 backward-compat byte-identity pass on 5 non-factual baselines
- [X] T048 [P] SC-007: confirm regenerated `agentic-app` MI findings carry grounding/verification mitigations + OWASP LLM09:2025 citation + `source_attribution`
- [X] T049 [P] SC-008: verify empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` via `git diff main --stat`
- [X] T050 SC-009: 24-file zero-edit grep audit — `git diff main --stat` returns zero lines on the 12 threat agent files + 12 companion `detection-patterns.md` files enumerated in quickstart.md Step 7 (22 original + F-1's 2)
- [X] T051 [P] SC-010: confirm F-A2 validation passes on regenerated findings per T038 (fixture-driven + regen-based)
- [X] T052 [P] SC-011: verify zero MAESTRO references per T018 `grep -i maestro` check
- [X] T053 [P] SC-012: verify schema_version `"1.7"` + regex extends to `MI` per T006; regex unit test passes
- [X] T054 [P] SC-014: three-signal-class discipline per T040 result
- [X] T055 **R5 code-review double-check (per HIGH-1 buffer-day budget model — consumed at Wave 2.2 PM, NOT buffer)**: senior-backend-engineer + code-reviewer review pattern-catalog worked examples for NFR-6 clearly-fictional framing compliance. Record pass/fail at `.aod/results/wave5-nfr6-compliance-check.md`.
- [X] T056 Open PR from `206-misinformation-threat-agent` → `main` with title `feat(206): misinformation threat agent (OWASP LLM09:2025)` and body linking to PRD, spec, plan, tasks, ADR-031. Request triple review (PM + Architect + Team-Lead) as part of PR process. **Draft PR #207 opened 2026-04-24 at https://github.com/davidmatousek/tachi/pull/207.**

**Checkpoint**: All 14 SCs green; NFR-6 compliance verified; PR opened. Wave 6 buffer day available if R2 (regeneration friction) materializes or delivery-retrospective authoring deferred.

---

## Phase 9: Wave 6 — Delivery Retrospective + Coverage Matrix Update (Day 2 PM or 2026-04-29 Wednesday Buffer)

**Purpose**: Delivery retrospective slotting per HIGH-2; BLP-01 Coverage Matrix update per SC-013; contingent buffer-day work if R2 materializes.

- [X] T057 **Delivery retrospective slotting per HIGH-2**: if PR merge completes Wave 2.3 PM with ≥1 hour residual capacity, author `specs/206-misinformation-threat-agent/delivery.md` Wave 2.3 PM (mirrors F-1 same-day-as-delivery pattern). Otherwise author 2026-04-29 Wednesday (buffer day) as primary buffer-day activity. Retrospective covers: estimated vs actual duration, surprises encountered, patterns validated (now two-execution-deep post-F-2: F-1 + F-2), lessons learned for F-3/F-4/F-5 authoring. **Authored pre-merge 2026-04-24 at `specs/206-misinformation-threat-agent/delivery.md` — merge metadata fill at post-squash (T025 companion).**
- [X] T058 **SC-013 BLP-01 Coverage Matrix update**: after PR squash-merge, update `_internal/strategy/BLP-01-threat-coverage.md`: LLM09:2025 row transitions Planned → Covered with F-2 (Feature 206) named as closure feature. Post-merge documentation commit. **Completed 2026-04-24 (private, gitignored — `_internal/` does not enter public git history): (1) LLM09:2025 row Planned → Covered, named F-2 Feature 206 2026-04-24; (2) OWASP LLM Top 10 2025 posture line updated from "Partial — gap remaining at LLM09" to "9 of 10 Covered"; (3) F-2 dependency-tree row Proposed → ✅ Delivered with PR #207 link.**
- [X] T059 Contingent R2 buffer-day work (ONLY if regeneration friction on `agentic-app` materializes): extend buffer-day capacity to absorb regeneration friction OR invoke Q4 fallback to new `examples/advisory-app/` (~0.5 day consumption) per PRD HIGH-1 buffer-day budget model. If R2 does NOT materialize, buffer-day capacity redirects to T057 delivery retrospective authoring. **NOT FIRED: R2 contingency did not materialize. Wave 4 `agentic-app` regen produced byte-identical output on all 5 non-factual baselines (T039 13 pass / 1 documented skip); no Q4 fallback required; buffer-day redirected to T057 authoring per PRD HIGH-1 budget model. Closed 2026-04-24.**

---

## Phase 10: Polish & Cross-Cutting

**Purpose**: Final hygiene + documentation updates.

- [X] T060 [P] Update `CLAUDE.md` Recent Changes section with Feature 206 entry (similar to Features 180/189/194/201 entries). Include: new misinformation agent, ADR-031 lineage with ADR-030 Decision 1 + Decision 8 cross-refs, BLP-01 Tier 1 framing (2nd Tier 1 feature after F-1), schema 1.6 → 1.7 minor bump as 2nd recorded application of Decision 8 regex-alternation rule, three-signal-class discipline demonstrated, 24-file zero-edit invariant preservation (22 original + F-1's 2), F-2 is second net-new `source_attribution` producer.
- [X] T061 [P] Run quickstart.md Step 12 end-to-end smoke test (LLM09:2025 Coverage Matrix transition verification). Record pass/fail at `.aod/results/quickstart-smoke.md`.
- [X] T062 [P] Verify `examples/README.md` entry — F-2 does NOT add a new example (extends `agentic-app`); update only if R2 fallback to `advisory-app` was invoked at T031 (same convention as Features 084/142/145/201).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational / Wave 1.0 + 1.1)**: T004 → T005 → T006 (T006 blocks all Wave 2 pattern authoring); T007, T008 parallel; T009 → T010 → T011 (ADR-031 Proposed commit); T012 independent (dispatch FP dry-run)
- **Phase 3 (US1 Wave 2)**: Depends on T006 (schema lock) + T010 (ADR-031 Proposed with Heuristic A D2)
- **Phase 4 (US2 Wave 2)**: Depends on T014 (pattern categories authored) + T016 (agent file skeleton). Can run in parallel with Phase 3 continuation.
- **Phase 5 (US3 Wave 5)**: Depends on Phase 7 (Wave 4 regeneration with three-signal-class discipline) + Phase 8 PR pre-merge
- **Phase 6 (Wave 3)**: Depends on Phase 3 + Phase 4 (agent + companion authored)
- **Phase 7 (Wave 4)**: Depends on Phase 6 (orchestrator registration with F-1 carry-over reconciled) + T031 Q4 decision point
- **Phase 8 (Wave 5 Pre-Merge)**: Depends on Phase 7 (Wave 4 complete)
- **Phase 9 (Wave 6 Retrospective + Coverage Matrix)**: Depends on Phase 8 PR merge
- **Phase 10 (Polish)**: After PR opened (can run pre-merge)

### Wave Gate Points

- **Wave 1.1 Gate**: T010 committed → unblocks Wave 2 (escalation gate fires if not by Day 1 EOD)
- **Wave 2 Gate**: T013-T018 complete → structural checks green → unblocks Wave 3
- **Wave 3 Gate**: T026-T030 complete → structural-diff green + 5-callsite quintet consistency green → unblocks Wave 4
- **Wave 4 Gate**: T031-T041 complete → Q4 decision + byte-identity pass + MI findings surfaced + three-signal-class verified → unblocks Wave 5
- **Wave 5 Gate**: T042-T055 all green (14 SC checks + NFR-6 compliance) → unblocks T056 PR open
- **Wave 6 Gate**: T057 (retrospective) or T058 (Coverage Matrix) → delivery closed

### Parallel Opportunities

- **Wave 1.1 parallel track**: T005 (regex test) ∥ T007 (valid fixture) ∥ T008 (invalid fixture) ∥ T009 (ADR skeleton) ∥ T012 (dispatch FP dry-run) — 5 parallel tasks
- **Wave 2 parallel track**: T013 (pattern scope) ∥ T015 (README) — parallel with T016 (agent skeleton). T014 sequential after T013.
- **Wave 3 parallel track**: T026 (orchestrator edit) ∥ T027 (dispatch rules) ∥ T028 (shared consumers) — 3 parallel file edits (different files). T029/T030 sequential after T028.
- **Wave 4 parallel track**: T038 (F-A2 validation) ∥ T039 (backward-compat) ∥ T040 (three-signal-class check) ∥ T041 (git-stage) — 4 parallel verifications
- **Wave 5 parallel track**: T042-T054 all parallel SC checks (13 independent verifications on different file surfaces); T055 sequential NFR-6 double-check before T056 PR open

---

## Implementation Strategy

### MVP Path (Baseline — 2-day envelope)

**Day 1 (Monday 2026-04-27)**:
- Morning: T004 Heuristic A verification → T006 schema bump → T010 ADR-031 Proposed commit (critical path)
- Parallel morning/afternoon: T005 regex test ∥ T007/T008 fixtures ∥ T009 ADR skeleton ∥ T012 dispatch FP dry-run
- Afternoon: T013-T018 pattern catalog + agent file + structural checks (Wave 2)
- End of day: T019-T021 mitigation text + example findings + specificity check (continuation of Wave 2)

**Day 2 (Tuesday 2026-04-28)**:
- Morning: T026-T030 orchestrator registration + F-1 5-callsite carry-over reconciliation + shared-reference edits + quintet consistency verification (Wave 3)
- Morning/Early-PM: T031 Q4 decision → T032-T041 example regeneration + three-signal-class verification (Wave 4)
- PM: T022-T024 ADR-031 Accepted transition (Wave 5 start)
- PM: T042-T055 SC validation sweep + NFR-6 compliance (Wave 5)
- PM: T056 PR open → T057 delivery retrospective (if ≥1h residual) → T060-T062 polish
- Post-merge: T025 ADR-031 SHA fill + T058 BLP-01 Coverage Matrix update (Wave 6)

**Buffer Day (Wednesday 2026-04-29)** — per HIGH-1 buffer-day budget model:
- Primary: T057 delivery retrospective (if not authored Wave 2.3 PM)
- Contingent: T059 R2 regeneration friction absorption OR Q4 fallback to `advisory-app` (~0.5 day)
- If all else green: absorbed into review lag / merge cycle

### Escalation Paths

- **Wave 1.0 Heuristic A escalation**: if T004 surfaces a subsume-into-output-integrity signal OR T010 not complete by Day 1 EOD (Monday 2026-04-27 23:59 local), user tie-break before Day 2 AM (R1 mitigation)
- **Non-factual baseline trigger match (T012)**: if 5 non-factual baselines unexpectedly match misinformation trigger keywords, architect reviews before Wave 3 (pre-edit to preserve SC-006 byte-identity)
- **F-A2 validation failure (T038)**: if validate_source_attribution rejects an MI finding, pattern worked examples likely cite AML.T0042 or out-of-catalog CWE — revise per FR-7 (LLM09 primary + CWE-345/CWE-223 related only)
- **Regeneration surface drift (T039, R2)**: if backward-compat byte-identity breaks on non-factual baseline, pause PR and root-cause; invoke Q4 fallback to `advisory-app` if `agentic-app` cumulative-state cost too high (0.5 day buffer consumption)
- **5-callsite quintet consistency (T030)**: if grep audit reveals pre-F-1 three-agent text still present at any of the 5 callsites, re-apply T026/T027 edits before Wave 4

---

## Notes

- [P] tasks = different files / independent commands / no dependencies on incomplete tasks
- [Story] label maps task to user story (US1 = LLM09 factual-output detection, US2 = grounding/verification mitigation guidance, US3 = Heuristic A three-way distinctness / ADR-031)
- Commit boundaries: Wave 1.1 schema-lock commit is atomic (T006 + T009 + T010); subsequent waves commit at wave-gate checkpoints
- ADR-031 Proposed commit at T010 unblocks Wave 2; ADR-031 Accepted transition at T022 happens pre-PR open
- 24-file zero-edit invariant (22 original + F-1's 2) is enforced by T050 grep audit — verify this as the final pre-merge check
- Post-merge: T025 SHA-fill is the last task in the per-feature sequence (updates Revision History with the squash commit short SHA)
- All PRD Triad-fix predicates traceable:
  - **H1 (AML.T0042 absent)** → T008 invalid fixture uses AML.T0042 to validate referential-integrity rejection; T014 pattern-catalog prose-only citation; T038 regen-time validation
  - **HIGH-1 (buffer-day budget model)** → T055 R5 NFR-6 double-check consumed at Wave 2.2 PM (not buffer); T059 contingent R2 absorption
  - **HIGH-2 (delivery retrospective slotting)** → T057 Wave 2.3 PM or buffer-day authoring
  - **MEDIUM-2 (R8 concurrency hedge)** → Implementation Strategy notes F-2 ships solo; serialization if F-3/F-5 enter build concurrently
  - **MEDIUM-3 (FR-7 three-callsite F-1 reconciliation → extended to 5-callsite quintet)** → T026 (orchestrator.md:296 + :370) + T027 (dispatch-rules.md:120 + LLM list) + T027 trigger-keyword rules section = 5 callsites; T030 consistency grep audit
  - **MEDIUM-4 (architect FR-7 edit ownership)** → T026 + T027 architect-owned edits
  - **M1 (ADR-030 Decision 1 cross-ref in FR-6)** → T010 D2 explicit cross-reference; T011 Cross-References entry
  - **ADR-030 Decision 8 2nd application** → T010 D8 explicit 2nd-recorded-application statement
  - **MEDIUM-5 (anti-indicator discipline in pattern catalog)** → T014 anti-indicator per pattern category
  - **M3 CWE-1039 deliberate-exclusion note** → T010 D9 explicit exclusion statement
  - **NFR-6 clearly-fictional framing** → T020 worked-example review; T055 code-review double-check
  - **Q1 (5 categories)** → T014 five numbered categories; T010 D4 codification
  - **Q2 (12 trigger keywords)** → T013 Detection Scope; T027 dispatch-rules trigger-keyword rules
  - **Q3 (Process only)** → T013 Applicable DFD Element Types; T016 agent metadata
  - **Q4 (extend agentic-app / fallback advisory-app)** → T031 decision point; T032 extension; T059 contingent fallback
  - **Q5 (ADR-031 Proposed Day 1 Wave 1.1)** → T009/T010 Wave 1.1 sequencing
