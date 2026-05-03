---
prd_reference: docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Spec preserves all 3 PRD user stories with distinct independent-test predicates, maps PRD FR-1 through FR-7 to spec FR-001 through FR-019 with appropriate elaboration, and translates PRD SC-1 through SC-10 into 12 measurable success criteria. All 8 Triad architect-fix and team-lead-fix predicates (BLOCKING-1 CWE correction, BLOCKING-2 schema 1.5→1.6 bump, HIGH-1 orchestrator carve-out, HIGH-2 tier-grouping placement, HIGH-3 ML09 doc-only, HIGH-4 agentic_pattern exclusion, TL-H1 Outcome A/B envelopes, TL-H2 Day-1-EOD escalation gate) are preserved. Architect-owned Q1-Q5 correctly deferred to /aod.plan without being re-authored. 0 BLOCKING / 0 HIGH / 3 MEDIUM / 3 LOW concerns — all are plan-phase refinements, none block spec approval. PM APPROVES for /aod.plan. Full review at .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: `output-integrity` Threat Agent (OWASP LLM05:2025)

**Feature Branch**: `201-output-integrity-threat-agent`
**Created**: 2026-04-18
**Status**: Draft
**Input**: User description: "PRD: 201 - output-integrity-threat-agent"
**PRD**: [docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md](../../docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md)
**BLP-01 Phase**: Tier 1 — first downstream consumer of the F-A1 + F-A2 + F-B Foundation tier; first net-new threat detection agent shipped under the BLP-01 governance umbrella

## User Scenarios & Testing *(mandatory)*

### User Story 1 — LLM-Output-to-Downstream-Sink Detection (Priority: P1)

A security analyst threat-models an architecture where LLM output flows into a browser, SQL query, shell, template engine, file write, or outbound HTTP client without post-model sanitization. The analyst wants tachi to flag those components with concrete `OI-{N}` findings citing OWASP LLM05:2025 so the XSS / SQLi / SSRF / template-injection / path-traversal surface — which input-side `prompt-injection` detection does not cover — is surfaced with the same rigor as the input side.

**Why this priority**: This is the primary reason F-1 exists. Without the output-side detection signal, the LLM threat surface is asymmetric: input-side comprehensive, output-side silent. P1 because the feature has no MVP without this story.

**Independent Test**: Given an architecture containing an LLM Process whose output flows into at least one downstream execution sink (browser, SQL, shell, template, file path, outbound URL), running `/tachi.threat-model` emits ≥1 `OI-{N}` finding with `category: llm`, OWASP LLM05:2025 in `references`, and a populated `source_attribution` array. Given an architecture with no such flow, the agent emits **zero** findings — no speculation.

**Acceptance Scenarios**:

1. **Given** an architecture that includes an LLM Process whose output is rendered as HTML in a browser-facing component without declared output encoding, **when** the orchestrator dispatches `output-integrity`, **then** an `OI-N` finding emits with `category: llm`, `references` citing `OWASP LLM05:2025`, and `source_attribution` containing `{taxonomy: owasp, id: LLM05, relationship: primary}` plus `{taxonomy: cwe, id: CWE-79, relationship: related}`.
2. **Given** an architecture where an LLM-generated string is passed as a SQL fragment, shell command, or file path to a downstream Process, **when** `output-integrity` runs, **then** a finding emits with `mitigation` field naming **specific** technologies — `parameterized queries`, `allowlist-based sanitization`, `structured intermediate representations`, or `command-line arg vector construction (no shell interpolation)` — not generic "sanitize output" prose.
3. **Given** an architecture where an LLM is used to synthesize HTTP requests to external services, **when** `output-integrity` runs, **then** an SSRF finding emits on the outbound-call boundary with `references` citing `OWASP LLM05:2025` plus `{taxonomy: cwe, id: CWE-918, relationship: related}` in `source_attribution`.
4. **Given** an architecture with **no** component exhibiting an LLM-output-to-downstream-execution flow, **when** `output-integrity` runs, **then** **zero findings** emit — no speculation. The agent's behavior matches the established AI-tier convention.
5. **Given** an architecture where both input-side (prompt injection vector) and output-side (downstream sink) surfaces are present on the same LLM Process, **when** the orchestrator runs, **then** both `prompt-injection` and `output-integrity` emit findings on the same component — this is correct behavior, not duplication; the two agents cover disjoint signal classes.

---

### User Story 2 — Stack-Specific Mitigation Guidance (Priority: P1)

A developer reading an `OI-{N}` finding needs to address the issue in a codebase. The developer wants the `mitigation` field to name specific encodings, libraries, or patterns matched to the detected sink type so the fix can be applied without re-deriving the output-handling pattern from primary OWASP / CWE sources.

**Why this priority**: Without actionable, sink-specific mitigation text, findings are noise from a developer's perspective — flagged-but-not-fixable. Equal priority to Story 1 because developer usability gates adoption.

**Independent Test**: For each emitted `OI-{N}` finding, the `mitigation` field names at least one specific encoding mechanism, library, or defensive pattern matched to the sink type (client-side execution → HTML entity encoding / CSP / safe DOM APIs / framework-native escape helpers; server-side execution → parameterized queries / JSON string escaping / command-line arg vector / allowlist-based enum validation; SSRF → URL allowlist / scheme validation / egress firewall; template injection → escape mode / sandboxed renderer; path traversal → canonicalization / allowlist directory enforcement).

**Acceptance Scenarios**:

1. **Given** an `OI-N` finding for a client-side execution sink (XSS / DOM injection), **when** the `mitigation` field is read, **then** it names at least one specific encoding mechanism — e.g., `HTML entity encoding`, `Content Security Policy with strict directive set`, `safe DOM APIs (textContent, not innerHTML)`, or `framework-native escape helpers (React {}, Vue v-text)`.
2. **Given** an `OI-N` finding for a server-side execution sink (SQLi / command injection), **when** the `mitigation` field is read, **then** it names at least one specific defensive pattern — e.g., `parameterized SQL queries`, `JSON string escaping`, `command-line arg vector (subprocess.run(..., shell=False))`, or `allowlist-based input validation against a closed enum`.
3. **Given** any `OI-N` finding, **when** its `references` array is inspected, **then** at least one entry is `OWASP LLM05:2025` (primary), and `source_attribution` carries that citation as `relationship: primary`. CWE references — CWE-79 (XSS), CWE-89 (SQLi), CWE-918 (SSRF), CWE-94 (code injection), CWE-22 (path traversal), CWE-78 (OS command injection) — appear in `source_attribution` as `relationship: related` per applicable pattern category.
4. **Given** the agent's output across pattern categories, **when** threat descriptions are inspected, **then** they distinguish between **server-side execution** (SQLi, command injection, SSRF — runs on tachi's server / backend) and **client-side execution** (XSS, DOM injection — runs in user browser). The categorization aligns with OWASP LLM05:2025's threat-class taxonomy.

---

### User Story 3 — Heuristic A Resolution for ASI09 Scope (Priority: P1)

An adopter runs tachi on an agentic application where an LLM-bearing agent uses misleading tone, overconfident claims, false authority signaling, or manipulative persuasion against a *human* downstream consumer. The adopter wants ADR-030 to make an explicit Heuristic A determination on whether ASI09 Human-Agent Trust Exploitation is covered by `output-integrity` (Outcome A) or by a future `trust-exploitation` agent shipped as F-4 (Outcome B) so the Coverage Matrix's ASI09 status transitions from ambiguous-Planned to either Covered (A) or Planned-with-clear-owner (B).

**Why this priority**: BLP-01 §8 blocks F-4 from entering `/aod.discover` until F-1's Heuristic A determination is captured in ADR-030. Without this story, the BLP-01 Tier 1 cadence stalls — F-4 cannot advance. Equal priority to Stories 1 and 2 because it gates a downstream feature.

**Independent Test**: ADR-030 at F-1 merge contains an explicit Heuristic A determination resolving Outcome A or Outcome B with justification referencing GUIDE-threat-coverage-research §11. If Outcome A, the companion `detection-patterns.md` ships a 6th pattern category "Human-Trust Exploitation via LLM Output" with primary `OWASP ASI09:2026`. If Outcome B, the agent's `## Purpose` section explicitly forward-references `trust-exploitation` (F-4) as the future owner and ASI09 remains out of scope.

**Acceptance Scenarios**:

1. **Given** the public ADR-030 at the time of F-1 merge, **when** the architect's Heuristic A determination is read, **then** it explicitly resolves one of two outcomes:
   - **Outcome A (subsume)**: ASI09 falls under `output-integrity`. The companion `detection-patterns.md` ships a **sixth pattern category** "Human-Trust Exploitation via LLM Output" with at least one worked example, primary source `OWASP ASI09:2026`, and trigger keywords for human-facing LLM output paths. F-4 closes as N/A on F-1 merge.
   - **Outcome B (split)**: ASI09 stays scope-distinct. F-1's `## Purpose` section explicitly forward-references `trust-exploitation` (F-4) as the future owner, lists ASI09 as out-of-scope, and the detection-patterns ship the 5 categories without a sixth. F-4 unblocks for `/aod.discover` on F-1 merge.
2. **Given** the resolution, **when** ADR-030's Decisions section is inspected, **then** the chosen Outcome is justified with explicit reference to GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy.
3. **Given** the chosen Outcome, **when** the BLP-01 Coverage Matrix is updated post-F-1 merge, **then** ASI09:2026 transitions Planned → Covered (Outcome A) OR remains Planned with explicit "F-4 owner" annotation (Outcome B) — ambiguity resolved either way.
4. **Given** ADR-030 acceptance, **when** F-4's `/aod.discover` invocation is attempted, **then** the Heuristic A determination is already in place and the BLP-01 §8 blocking gate ("F-1 resolves F-4 scoping") is satisfied.
5. **Given** the Heuristic A determination lands in ADR-030 Proposed by Day 1 EOD (Monday 2026-04-20), **when** Day 2 pattern authoring begins, **then** the pattern catalog structure is committed (5 or 6 categories) and downstream authoring proceeds without rework. If the determination is NOT committed by Day 1 EOD, the task plan MUST surface an explicit user-tie-break escalation step before Day 2 AM.

---

### Edge Cases

- **LLM Process with no downstream sink**: a component matches a trigger keyword (e.g., name contains "LLM") but its output returns only to the calling agent with no downstream execution surface. Pattern indicators require **both** a trigger keyword AND a structural indicator of a downstream sink — keyword alone MUST NOT emit a finding (US-1 zero-speculation criterion).
- **`mermaid-agentic-app` baseline break risk**: the example is in the 6-baseline backward-compatibility set and contains LLM-related components. Plan stage MUST verify whether its architecture matches output-integrity triggers; if yes, coordinate a re-baseline with the byte-identity test or carve it out similarly to `agentic-app`.
- **F-A2 referential validation failure**: if an `OI-{N}` finding cites a CWE ID not present in `schemas/taxonomy/cwe.yaml` (e.g., CWE-73, CWE-1336), `validate_source_attribution` rejects the finding at parse time. Pattern catalog worked examples MUST cite only IDs verified present.
- **Template injection CWE substitution**: CWE-1336 (specific template-injection CWE) is absent from `schemas/taxonomy/cwe.yaml`; CWE-94 (code injection, in-catalog parent) substitutes. Path traversal CWE-73 is also absent; CWE-22 alone covers the surface.
- **ML09 bundling scope**: OWASP ML09:2023 (predictive-ML output tampering) shares the output-side signal class per BLP-01 §4 but differs semantically. ML09 closure is **documentation-only**: recorded in ADR-030 rationale + Coverage Matrix transition; `source_attribution` carries only LLM05 + CWE citations, never ML09 (ML09 is not in the closed 5-value taxonomy enum).
- **Heuristic A Outcome A 6th-pattern research lag**: if Outcome A is chosen but Human-Trust pattern indicators were not pre-researched, Day 2 pattern authoring slips. Mitigation: if Outcome A is the architect's leaning at Day 1 AM, parallel research proceeds Day 1 PM.
- **Orchestrator dispatch-order drift**: adding `output-integrity` to `orchestrator.md` and `dispatch-rules.md` could inadvertently shift finding-emission order on the regenerated example, breaking byte-identity. Plan stage verifies insertion position and runs structured pre-vs-post diff on the regenerated example.
- **Both input and output signals on one LLM Process**: both `prompt-injection` and `output-integrity` fire; this is correct behavior (disjoint signal classes), not duplication.
- **`source_attribution` on existing 22 agents**: the 22 detection-tier files do NOT populate `source_attribution` in F-1 scope; that is F-A3. F-1 is the first net-new producer at the new agent boundary only.
- **ADR-030 Proposed commit timing**: per PRD Q5 architect leaning, ADR-030 lands as Proposed at Day 1 Wave 1.1 schema-lock commit to unblock parallel pattern authoring. Accepted transition at PR merge with provisional merge-date; post-merge SHA fill records squash commit.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST ship a new lean AI-tier threat agent at `.claude/agents/tachi/output-integrity.md` conforming to the ADR-023 detection-variant shape: YAML frontmatter → metadata YAML (`category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM05:2025, OWASP ML09:2023]`, `output_schema: ../../../schemas/finding.yaml`) → `## Purpose` → `## Skill References` table → `## Detection Workflow` with exactly **one** `**MANDATORY**: Read` directive at section start → optional `## Example Findings`. Line count MUST be ≤150 with a hard ceiling of 180.
- **FR-002**: The system MUST ship a new companion skill directory at `.claude/skills/tachi-output-integrity/` containing `README.md` (consumers + purpose header) and `references/detection-patterns.md` (frontmatter with `consumers: [tachi-output-integrity]` + `last_updated` date; `## Overview` paragraph; `## Detection Scope` with Trigger Keywords + Applicable DFD Element Types; `## Detection Patterns` with ≥5 pattern categories).
- **FR-003**: The pattern catalog MUST include **at minimum** these five categories, each carrying (a) ≥1 worked example, (b) ≥1 primary-source citation (OWASP LLM05:2025 at minimum), (c) trigger keywords, (d) applicable DFD element types: (1) Client-Side Execution Sinks (XSS / DOM Injection), (2) Server-Side Execution Sinks (SQLi / Command Injection), (3) SSRF from LLM-Synthesized URLs, (4) Template / Expression Injection, (5) Path Traversal + Unsafe File Writes. A **conditional sixth category** "Human-Trust Exploitation via LLM Output" ships only if ADR-030's Heuristic A determination resolves Outcome A.
- **FR-004**: The system MUST register the new agent in orchestrator dispatch via two additive edits: (a) `.claude/agents/tachi/orchestrator.md` — add `output-integrity.md` to the hardcoded AI-tier dispatch list; (b) `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — extend the LLM dispatch trio (`prompt-injection`, `data-poisoning`, `model-theft`) to a quartet by adding `output-integrity` with its trigger-keyword activation rules. No new LLM keywords are required; output-integrity shares the existing LLM keyword set.
- **FR-005**: The system MUST extend `.claude/skills/tachi-shared/references/finding-format-shared.md` frontmatter `consumers:` list by adding `output-integrity` between `tool-abuse` and `risk-scorer` (tier-grouping placement: appended to AI tier). All existing `## ` headings MUST remain byte-identical pre/post edit; the body diff outside the frontmatter consumer list MUST be empty.
- **FR-006**: The system MUST bump `schemas/finding.yaml` from schema version 1.5 to 1.6 (minor, additive) by extending the `id.pattern` regex from `^(S|T|R|I|D|E|AG|LLM|AGP)-\d+$` to include the `OI` prefix. The `category` enum MUST remain unchanged. The bump follows the ADR-026 minor-bump rule for additive regex extensions.
- **FR-007**: Every emitted `OI-{N}` finding MUST include a non-empty `source_attribution` array per the F-A2 schema. Minimum: `{taxonomy: owasp, id: LLM05, relationship: primary}` on every finding. Per pattern category, additional entries as `relationship: related` using only CWE IDs verified present in `schemas/taxonomy/cwe.yaml`: CWE-79 (client-side), CWE-89 / CWE-78 / CWE-94 (server-side), CWE-918 (SSRF), CWE-94 (template injection, substituting for absent CWE-1336), CWE-22 (path traversal, substituting for absent CWE-73).
- **FR-008**: The system MUST ship a public per-feature ADR at `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` under the Proposed → Accepted dual-commit pattern (ADR-027 / ADR-028 / ADR-029 precedent). ADR-030 body MUST include: (a) the new-agent decision, (b) the Heuristic A scope resolution for ASI09 with explicit reference to GUIDE-threat-coverage-research §11, (c) lean-agent shape conformance per ADR-023 (single-point load, ≤150 lines, zero MAESTRO references), (d) LLM05 + ML09 bundling rationale per BLP-01 §4, (e) cross-references to ADR-021 / ADR-023 / ADR-026 / ADR-027 / ADR-028 / ADR-029, (f) 22-file zero-edit invariant preserved with grep-auditable enumeration, (g) Revision History table tracking Proposed → Accepted dates, (h) no Layer 2 / tachi Cloud / commercial framing — public ADR stands on technical merits.
- **FR-009**: The system MUST regenerate one example architecture that exercises the new flow (PM default: `examples/agentic-app/`; alternative: extend a different example, architect decides at plan time). The regenerated example MUST surface ≥1 `OI-{N}` finding with concrete mitigations, OWASP LLM05:2025 citation, and populated `source_attribution`.
- **FR-010**: The agent file and its companion `detection-patterns.md` MUST contain **zero MAESTRO references** — grep-checkable invariant across both files. MAESTRO layer classification remains orchestrator-owned per ADR-023 Decision 2.
- **FR-011**: The agent's detection workflow MUST require **both** a trigger keyword match AND a structural indicator of a downstream execution sink before emitting a finding — keyword match alone MUST NOT produce a finding. Architectures with no qualifying Process emit zero findings (no speculation).
- **FR-012**: Orchestrator Phase 4 `validate_source_attribution` MUST resolve every `source_attribution` record on every `OI-{N}` finding without error. Pattern catalog worked examples MUST cite only taxonomy IDs present in the F-A1 catalogs (`schemas/taxonomy/owasp.yaml`, `schemas/taxonomy/cwe.yaml`).
- **FR-013**: The system MUST NOT edit any of the 22 existing detection-tier files — the 11 threat agent files at `.claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md` or their 11 companion `detection-patterns.md` references. Grep-auditable zero-edit invariant extends the ADR-023 lineage.
- **FR-014**: The system MUST NOT edit infrastructure-tier consumer agents (`risk-scorer`, `control-analyzer`, `threat-report`, `threat-infographic`, `report-assembler`). These read `category: llm` (existing enum value); `OI-{N}` findings flow through them without consumer-side changes.
- **FR-015**: The system MUST NOT add new runtime dependencies — `pyproject.toml`, `requirements*.txt`, `package.json` diffs MUST be empty. No new developer dependencies either (`pyyaml`, `pytest` already declared per Feature 128).
- **FR-016**: The agent MUST NOT declare `agentic_pattern` in its metadata YAML. The `agentic_pattern` field is set downstream by orchestrator Phase 3.6 per ADR-026; `OI-{N}` findings will receive `agentic_pattern: none` (single-agent output surface, not multi-agent pattern).
- **FR-017**: The agent's threat descriptions MUST distinguish between **server-side execution** (SQLi, command injection, SSRF, template injection — runs on backend) and **client-side execution** (XSS, DOM injection — runs in user browser). The pattern category taxonomy aligns with OWASP LLM05:2025 threat-class taxonomy.
- **FR-018**: ML09:2023 Output Integrity Attack bundling MUST be **documentation-only**, NOT pattern-level. ADR-030 records the bundling rationale per BLP-01 §4; the Coverage Matrix transitions ML09 to Covered citing F-1 as the closure path. Pattern categories detect LLM05 surfaces only. `source_attribution` does NOT carry ML09 (not in the closed 5-value taxonomy enum).
- **FR-019**: ADR-030 MUST land as Proposed at Day 1 Wave 1.1 schema-lock commit to unblock parallel pattern-catalog authoring; MUST transition Accepted at PR merge with provisional merge-date; MUST post-merge SHA fill recording the squash commit (ADR-027 / ADR-028 / ADR-029 precedent).

### Key Entities

- **`output-integrity` agent** (`.claude/agents/tachi/output-integrity.md`) — new lean AI-tier threat detection agent. Inputs: DFD architecture description. Outputs: ordered list of `OI-{N}` findings per F-A2 schema.
- **`tachi-output-integrity` skill** (`.claude/skills/tachi-output-integrity/`) — companion skill directory hosting the pattern catalog. Contains `README.md` + `references/detection-patterns.md`.
- **`OI-{N}` finding** — new finding-ID prefix for output-integrity findings. Emitted with `category: llm` (existing enum); same shape as existing findings plus a populated `source_attribution` array.
- **ADR-030** (`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`) — public per-feature ADR with Heuristic A scope resolution for ASI09 and LLM05 + ML09 bundling rationale.
- **Pattern category** — one entry in `detection-patterns.md` with name, primary OWASP/CWE citation, indicators (3-6 bullets), and at least one worked example.
- **Trigger keyword set** — 8-12 keywords (architect finalizes at plan) matching LLM-output-to-downstream-sink flow in DFD component names/descriptions.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `.claude/agents/tachi/output-integrity.md` exists, is **≤150 lines** (AI tier cap; hard ceiling 180), and passes the ADR-023 structural-diff check: exactly **one** `**MANDATORY**: Read` directive under a `## Detection Workflow` section heading. Verified via `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/output-integrity.md` returning `1` and `wc -l` returning ≤150.
- **SC-002**: Companion `.claude/skills/tachi-output-integrity/references/detection-patterns.md` ships with **≥5 pattern categories** covering client-side execution, server-side execution, SSRF, template/expression injection, and path traversal. Each category carries (a) ≥1 worked example, (b) ≥1 primary-source citation (OWASP LLM05:2025 at minimum), (c) trigger keywords, (d) applicable DFD element types. A conditional sixth category ships if and only if ADR-030 resolves Heuristic A Outcome A.
- **SC-003**: `.claude/skills/tachi-shared/references/finding-format-shared.md` frontmatter `consumers:` list is extended to include `output-integrity` between `tool-abuse` and `risk-scorer`. A structural diff of `## ` headings pre/post edit returns **empty**; the body diff outside the consumer list addition returns **empty**.
- **SC-004**: Orchestrator dispatch invokes the new agent when at least one `Process` component in the architecture matches the trigger-keyword set AND exhibits a structural downstream-sink indicator. Verified by **≥1 new `OI-{N}` finding produced** on the regenerated example architecture. Architectures with no qualifying Process emit **zero** `OI-{N}` findings.
- **SC-005**: Public ADR-030 is committed at `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` documenting the new-agent decision, Heuristic A scope resolution, lean-agent shape conformance, LLM05 + ML09 bundling rationale, 22-file zero-edit invariant proof with grep-auditable enumeration, and ADR cross-references. Authored under the dual-commit Proposed → Accepted pattern. The Heuristic A determination is captured BEFORE F-4 enters `/aod.discover` per BLP-01 §8 blocking gate.
- **SC-006**: All 5 non-agentic example PDF baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant). If `mermaid-agentic-app` matches the new agent's triggers and byte-identity cannot be preserved, the plan stage MUST surface a re-baseline decision with explicit architect + team-lead approval.
- **SC-007**: Example regeneration lands on an architecture exercising the new flow (PM default: `examples/agentic-app/`; architect may override at plan time with documented rationale). The regenerated example surfaces ≥1 `OI-{N}` finding with concrete mitigations and OWASP LLM05:2025 citation.
- **SC-008**: Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies.
- **SC-009**: **22-file zero-edit invariant preserved** on the existing detection tier. Grep-auditable: zero edits to the 11 threat agent files under `.claude/agents/tachi/` (excluding the new `output-integrity.md`) or their 11 companion `detection-patterns.md` reference files. **Carve-out**: orchestrator-tier files (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`) are expected to receive minimal additive edits per FR-004.
- **SC-010**: Every emitted `OI-{N}` finding passes F-A2 referential-integrity validation (`validate_source_attribution` returns no errors). Every finding carries at minimum `{taxonomy: owasp, id: LLM05, relationship: primary}` plus applicable CWE entries (CWE-22 / CWE-78 / CWE-79 / CWE-89 / CWE-94 / CWE-918) as `relationship: related`. F-1 is the first net-new producer of `source_attribution` in the tachi codebase post-F-A2, validating the contract end-to-end on a production-path finding flow independent of F-A3.
- **SC-011**: The agent file and its companion `detection-patterns.md` contain **zero MAESTRO references** — verified via `grep -i 'maestro' .claude/agents/tachi/output-integrity.md .claude/skills/tachi-output-integrity/references/detection-patterns.md` returning no matches.
- **SC-012**: `schemas/finding.yaml` line 13 contains `schema_version: "1.6"` and line 18 `id.pattern` regex matches `OI-\d+` (verifiable by a regex unit test). Existing finding IDs conforming to pre-1.6 prefixes remain valid against the 1.6 regex.

---

## Out of Scope (Explicit)

The following items are explicitly out of scope for F-1. Each carries a forward-reference per PRD §Out of Scope:

1. **Wiring the existing 22 detection-tier files to populate `source_attribution`** → F-A3 (separate Tier 1 follow-on).
2. **`trust-exploitation` agent for ASI09 (Outcome B path)** → F-4, gated on F-1 Heuristic A resolution.
3. **`misinformation` agent for LLM09** → F-2, parallel-eligible separate PRD.
4. **`tool-abuse` enrichment for ASI07 inter-agent communication** → F-3, parallel-eligible.
5. **`denial-of-service` + `model-theft` enrichment for LLM10** → F-5, parallel-eligible.
6. **OWASP ML Top 10 bundle (9 items beyond ML09)** → F-6 Tier 2.
7. **OWASP Mobile Top 10 bundle** → F-7 Tier 2.
8. **Web/API attestation** → F-8 Tier 3.
9. **Cross-feature attack-chain reasoning** — Feature 141 cross-layer attack chains already covers this; `OI-{N}` findings flow through Phase 3.5 chain correlation automatically with zero F-1 scope.
10. **Section 4b "Findings by Agentic Pattern" entry** — F-1 findings emit `agentic_pattern: none`; Section 4b is untouched.
11. **Coverage Matrix update in `BLP-01-threat-coverage.md`** — private `_internal/strategy/` document; updated post-merge in a separate documentation commit. Public coverage view renders automatically via F-B's per-framework matrix once `OI-{N}` findings carry `source_attribution`.

---

## Assumptions

- The architect resolves Heuristic A (Outcome A subsume / Outcome B split) at Day 1 Wave 1.0 and commits ADR-030 Proposed at Day 1 Wave 1.1 schema-lock. If the ruling drifts past Day 1 EOD (Monday 2026-04-20), `/aod.tasks` surfaces an explicit user-tie-break escalation step before Day 2 AM.
- `examples/agentic-app/` is the regeneration target (PM default per Q4 architect leaning). Architect may override at plan time with documented rationale if cumulative-state cost exceeds convention-preservation benefit.
- Trigger keyword set is curated to 8-12 keywords at plan time (architect-owned per PRD Q2 leaning; starting set of 7 in PRD FR-1).
- DFD target set is `Process` only (architect-owned per Q3 leaning; precedent-preserving across 11 existing AI agents).
- The `mermaid-agentic-app` baseline either does NOT match output-integrity triggers (byte-identity preserved) or is a candidate for coordinated re-baseline if it does. Plan stage verifies.
- F-A1, F-A2, F-B dependencies are satisfied at PRD time (verified: `schemas/taxonomy/`, `schemas/finding.yaml` v1.5 with `source_attribution`, `templates/tachi/security-report/coverage-attestation.typ`).
- PM + Architect + Team-Lead PRD sign-offs are in place (APPROVED / APPROVED_WITH_CONCERNS / APPROVED_WITH_CONCERNS per PRD frontmatter).
