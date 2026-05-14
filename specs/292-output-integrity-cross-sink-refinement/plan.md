---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 2M / 4L. Plan faithfully extends PM-signed PRD/spec. All 12 PRD FRs, 7 NFRs, 12 SCs (with conditional SC-015 path noted), 5 user stories, 3 gap closures trace into plan content. Q1-Q5 resolutions all preserve adopter signal for vector-DB tenant scoping / package-manager / cross-agent boundary. F-260 community-merge precedent honored verbatim (T+0 offer, T+5d nudge, T+7d SLA breach, maintainer-authored fallback with Co-Authored-By + CHANGELOG attribution). 24+2 file zero-edit invariant anchors scope correctly. Constitution Check gates correctly evaluated; Principle VII docs-only exception appropriate. M/L findings flow into /aod.tasks. Full review at .aod/results/product-manager-plan.md."
  architect_signoff:
    agent: architect
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 2M / 3L. Plan technically sound; all 10 evaluation criteria pass on substance. Q1-Q5 correctly resolved per BLP-01 lineage. ADR-045 template faithfully mirrors ADR-032's 7-decision template with ADR-031 D8 asymmetry note codified. No-schema-bump invariant correctly framed as operational signal of signal-class identity preservation per ADR-032 D3 / ADR-034 D6 / ADR-035 D6 lineage. Cross-link no-emission contract codifies FR-007 testably and avoids F-248 over-scoped byte-comparison trap. Finding-emission contract preserves F-1 / ADR-030 D1 populator contract end-to-end (no F-5/F-6/F-A3-deferral regression). Concerns confined to documentation hygiene (BLP-01 count mismatch, invariant labeling, minor doc gaps) — flow into /aod.tasks. Full review at .aod/results/architect-plan.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Output-Integrity Cross-Sink Refinement

**Branch**: `292-output-integrity-cross-sink-refinement` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/292-output-integrity-cross-sink-refinement/spec.md`

## Summary

This is a **Heuristic A enrichment branch at single-agent scope** — a docs-heavy refinement of the shipped F-1 `output-integrity` agent (PRD #201, v4.21.0, ADR-030) that closes three pattern-catalog gaps surfaced by a first-time community contributor. The implementation appends new pattern content to `.claude/skills/tachi-output-integrity/references/detection-patterns.md`, adds ≤10 lines of navigational cross-link prose to `.claude/agents/tachi/output-integrity.md`, optionally introduces one new example baseline (`examples/multi-tenant-rag-app/`), authors ADR-045 documenting the architectural decisions, and ships a CHANGELOG entry preserving @armorer-labs's authorship per the F-260 community-merge precedent.

**Technical approach**: Additive-only markdown edits (no schema changes, no new agent files, no API surface changes). The agent's existing both-signal detection logic (trigger-keyword AND downstream-sink-indicator) is reused — new pattern surfaces inherit the enforcement. Byte-identical regression protection on 5 non-qualifying baselines under `SOURCE_DATE_EPOCH=1700000000`. ADR-045 follows the ADR-032 7-decision structure with Proposed → Accepted dual-commit governance.

## Technical Context

**Language/Version**: Markdown (CommonMark) + YAML 1.2 — no source code in this feature
**Primary Dependencies**: tachi v4.35.0 baseline (current main)
**Storage**: Git filesystem; ADR slot ADR-045
**Testing**: `tests/scripts/test_backward_compatibility.py` (existing pytest harness with `SOURCE_DATE_EPOCH=1700000000`) + manual byte-identical baseline regeneration + grep-auditable structural invariants
**Target Platform**: tachi running inside Claude Code (per scope.md)
**Project Type**: Single project (tachi self-modification)
**Performance Goals**: N/A (docs-only refinement; no runtime impact)
**Constraints**:
- `.claude/agents/tachi/output-integrity.md` total diff ≤10 lines (FR-009)
- `.claude/skills/tachi-output-integrity/references/detection-patterns.md` additive-only (existing Cat 1–5 byte-identical)
- 24+2 file zero-edit invariant: no edits to tool-abuse / data-poisoning / other threat-agent files or their companion skill references
- No `schemas/finding.yaml` schema bump
- 5 non-qualifying baselines (`web-app/`, `microservices/`, `ascii-web-api/`, `mermaid-agentic-app/`, `free-text-microservice/`) reproduce byte-identical under `SOURCE_DATE_EPOCH=1700000000`
- 22 frozen tier files + 11 frozen companion files + all post-F-1/F-2/F-3/F-4/F-5/F-6 hosts unchanged
**Scale/Scope**:
- ~150 lines of new content in `detection-patterns.md` (Cat 6 + Gap 3 subsection + Memory-Promotion Rules schema example)
- ≤10 lines of cross-link prose in `output-integrity.md` Purpose section
- 1 new ADR (ADR-045, ~200 lines following ADR-032 7-decision template)
- 1 optional new baseline (`examples/multi-tenant-rag-app/` — 1 architecture description + regenerated artifacts)
- 1 CHANGELOG entry + 2 discussion thread comments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applicability | Compliance | Gate Status |
|---|---|---|---|
| I. General-Purpose Architecture | N/A (tachi is security-domain-specific by design; see `.claude/rules/scope.md`) | N/A | ✅ Pass |
| II. API-First Design | N/A (no API surface; markdown-only refinement) | N/A | ✅ Pass |
| III. Backward Compatibility (NON-NEGOTIABLE) | **APPLIES** — 5 non-qualifying baselines must reproduce byte-identical under `SOURCE_DATE_EPOCH=1700000000`; agent's existing detection workflow unchanged; finding-id prefix `OI-{N}` preserved | FR-011 + SC-004 + SC-011 + ADR-021 byte-identity gate | ✅ Pass |
| IV. Concurrency & Data Integrity | N/A (no shared state, no locks, no database) | N/A | ✅ Pass |
| V. Privacy & Data Isolation | N/A (no user data; tachi is local-first per scope.md) | N/A | ✅ Pass |
| VI. Testing Excellence | **APPLIES** — existing pytest backward-compatibility harness covers the byte-identical regression; new pattern surface gets a worked example serving as an inline test fixture | SC-001 + SC-002 + SC-003 + SC-004 verifiable via existing harness | ✅ Pass |
| VII. Definition of Done (NON-NEGOTIABLE) | **APPLIES** — 3-step validation: (1) merged to main + release-please bump, (2) all backward-compat tests pass + `/security` re-scan clean, (3) user-validated via discussion #179 closure comment + adopter feedback window | Plan-level DoD checklist below; per-task DoD inherited from `docs/standards/DEFINITION_OF_DONE.md` | ✅ Pass (exception: docs-only changes may not require production deployment per Constitution VII Exceptions; we treat squash-merge to main + release-please bump as the "production deployment" equivalent) |
| VIII. Observability & Root Cause Analysis | **APPLIES (lightly)** — Five Whys methodology used in PRD H1/H2 inline resolution; no runtime observability impact | PRD review captures architect + team-lead Five Whys analyses | ✅ Pass |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | **APPLIES** — feature branch `292-output-integrity-cross-sink-refinement` + Conventional Commits + PR review + `Co-Authored-By:` trailer for @armorer-labs (if path b accepted) | SC-013 enforces `feat(292):` PR title for release-please | ✅ Pass |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | **APPLIES** — PRD signed off 2026-05-14 (PM + Architect + Team-Lead all APPROVED_WITH_CONCERNS); spec.md PM-signed; plan.md requires PM + Architect dual sign-off; tasks.md requires triple sign-off; ADR-045 authored documenting architectural decisions per "Architect documents all architectural decisions in docs/architecture/02_ADRs/" mandate at line 394 | This plan's dual sign-off section + FR-016 + SC-014 + ADR-045 authorship | ✅ Pass |

**Gate Result**: All applicable gates PASS. No violations to track in Complexity Tracking.

## Architectural Decisions Resolved (PRD Q1–Q5)

The five Architect-owned open questions from PRD #292 are resolved here per the Architect's leans (BLP-01 lineage defaults). Each resolution is captured as a decision in ADR-045.

### Q1: Vector-Filter Pattern Placement → **Cat 6 (new top-level pattern category)**

**Decision**: Add a new top-level Pattern Category 6 ("Vector / Search-DSL Injection") to `detection-patterns.md`, NOT extend Cat 2 as a sub-class.

**Rationale**:
- The Architect's decision criterion in the PRD: "If the Architect's CWE pinning yields a CWE distinct from CWE-89 (e.g., a vector-DB-specific CWE), Cat 6 is justified."
- FR-3 pins **CWE-943** (Improper Neutralization of Special Elements in Data Query Logic) as primary — this is the canonical parent CWE for non-SQL query-language injection, distinct from CWE-89 (SQL-specific). The decision criterion is satisfied.
- A new top-level Cat 6 enables clean future expansion to additional structured-query languages (GraphQL injection, NoSQL operator injection, LDAP, XQuery, XPath, DQL — all CWE-943 family).
- Industry framing supports separate category: OWASP LLM08:2025 "Vector and Embedding Weaknesses" is its own OWASP class (distinct from LLM05:2025 Improper Output Handling at the framework taxonomy level), reinforcing the cleaner category boundary.

**Alternatives considered**:
- Cat 2 sub-class — rejected because vector-filter injection deserves its own CWE pinning (CWE-943, not CWE-89) and the OWASP framework anchor differs (LLM08 vs LLM05).

**Resolves**: PRD FR-1, spec FR-001, PM finding M-1 indirectly (Cat 6 is the BLP-01-lineage-aligned default).

### Q2: New Multi-Tenant RAG Baseline → **Add `examples/multi-tenant-rag-app/`**

**Decision**: Add a new example baseline at `examples/multi-tenant-rag-app/` exercising the Cat 6 vector-filter pattern.

**Rationale**:
- Architect's decision criterion: "If the Architect anticipates Gap 1 patterns to be re-exercised across multiple future refinements, adding the baseline now pays compounding regression-protection dividends."
- Multi-tenant RAG is an emerging high-frequency adopter architecture (per web research: Microsoft Azure secure RAG, AWS Bedrock+OpenSearch JWT, Mavik Labs 2026, Pinecone Pool model). Future refinements will likely extend to more vector-DB engines (Weaviate, Milvus, Chroma) — the baseline serves as the regression-protection anchor for those extensions.
- The baseline doubles as adopter documentation: a worked architecture showing both the failure mode (LLM-synthesized filter omits tenant clause) AND the recommended mitigation (server-side filter composition / namespace-per-tenant).
- Cost: +0.5 day per the PRD timeline (Day 2 PM), buffered by Buffer-1 / Buffer-2 if worst-case path materializes.

**Alternatives considered**:
- Skip baseline — rejected because the existing `agentic-app/` baseline doesn't exercise vector-DB patterns; regression protection on Cat 6 emissions would rely solely on the inline worked example in `detection-patterns.md`, which is weaker than a regenerable baseline.

**Resolves**: PRD FR-12, spec FR-012 conditional → confirmed; PM finding M-3 → introduces SC-015 (added below in Phase 0).

### Q3: ADR Authorship → **Author ADR-045**

**Decision**: Author ADR-045 documenting the F-292 architectural decisions (Q1 Cat 6 placement, Q2 baseline addition, Q3 ADR authorship itself, Q4 Memory-Promotion Rules inline placement, Q5 parallel-non-blocking handoff).

**Rationale**:
- Constitution Principle X line 394: "Architect documents all architectural decisions in docs/architecture/02_ADRs/" — this is a NON-NEGOTIABLE constitutional mandate, not a stylistic preference.
- BLP-01 lineage: F-3 (ADR-032), F-5 (ADR-034), F-6 (ADR-035), F-7 (ADR-036), F-241 (ADR-037) — ALL six BLP-01 enrichment-branch features authored ADRs. **No BLP-01 precedent skips an ADR on a Heuristic A enrichment refinement.**
- F-292 is the eighth Heuristic A enrichment execution; departure from the established lineage would itself require an ADR or a Principle X exception note — heavier ceremony than just authoring the ADR.
- ADR-045 captures durable institutional knowledge that pays compounding dividends across future Heuristic A enrichments (more vector-DB engines, more package-manager surfaces, more cross-agent handoffs).

**Alternatives considered**:
- No-ADR exception — rejected because (a) BLP-01 lineage has zero precedent for skipping, (b) the exception itself would require an ADR or Principle X cross-cite, and (c) the docs-only nature does not exempt the change from architectural-decision documentation.

**ADR slot allocation**: ADR-045 (next available after ADR-043 reserved for BLP-03 cosign-vs-minisign and ADR-044 used by Dual-Frame Public Positioning).

**ADR structure**: 7 numbered decisions mirroring ADR-032 (same-agent enrichment is structural sub-case of single-agent enrichment):
- D1: Heuristic A enrichment vs new agent — signal-class identity inheritance from ADR-030 D1 + ADR-032 D1
- D2: Additive-only edit discipline per ADR-023 D3
- D3: No schema bump — operational signal of signal-class identity preservation
- D4: No consumers-list edit (host already registered)
- D5: No functional orchestrator/dispatch edit (host already registered)
- D6: Public ADR omits commercial framing per SDR-001 Option C
- D7: Pattern Category Disambiguation (Cat 6 boundary carve from Cat 2 + cross-link prose disambiguation from tool-abuse / data-poisoning)

**Governance protocol**: Proposed → Accepted dual-commit (Proposed at planning lock; Accepted at pre-PR with `<pending-post-merge-fill>` placeholder on `Accepted-commit-SHA`; post-merge SHA fill at delivery).

**Resolves**: PRD NFR-6, spec FR-016 + SC-014, PM finding M-1 (resolved in favor of "MUST author" with explicit BLP-01 lineage rationale; no-ADR exception path not invoked).

### Q4: Memory-Promotion Rules Placement → **Inline in `detection-patterns.md` Gap 3 subsection**

**Decision**: Co-locate the Memory-Promotion Rules worked schema example inside the Cross-Agent Handoff Sinks subsection of `detection-patterns.md`, NOT as a separate skill-reference file.

**Rationale**:
- Single-use surface today — Memory-Promotion Rules is referenced only by the Gap 3 cross-link prose; no current `tool-abuse` or `data-poisoning` skill reference imports it.
- Reader ergonomics — co-location keeps the navigational pointer AND the mitigation pattern in one place, reducing the analyst's context-switching when reviewing the boundary.
- The worked schema example is ≤20 lines of JSON-schema-style YAML — doesn't warrant a separate file at this scope.
- Future-proofing: if reuse from adjacent agents is anticipated in a follow-on refinement, the Memory-Promotion Rules block can be lifted to a separate skill-reference file at that point. The current inline placement is reversible.

**Alternatives considered**:
- Separate skill-reference file at `.claude/skills/tachi-output-integrity/references/memory-promotion-rules.md` — rejected because it implies multi-consumer surface that doesn't exist today; pre-mature abstraction per CLAUDE.md guidance.

**Resolves**: PRD Q4, spec FR-008 placement.

### Q5: Contributor-Handoff Timing → **Parallel non-blocking with 7-day SLA**

**Decision**: Maintainer track proceeds in parallel with @armorer-labs handoff offer; switch tracks on response or fall back to maintainer-authored at 7-day SLA breach.

**Rationale**:
- F-260 precedent: @north-echo opened PR within ~10h of maintainer invite reply. The 7-day SLA is generous and matches the contributor-collisions feedback policy.
- F-260 retrospective: contributor declined the follow-on offer — empirical support for the maintainer-authored fallback being a realistic path.
- Capacity: per Team-Lead M-3 in PRD review, maintainer 5-hour attention budget for path (a) is confirmable but not pre-confirmed; default explicitly to (b) if not available is the safe operational stance.
- Authorship preservation: NFR-5 preserves @armorer-labs's authorship via CHANGELOG + `Co-Authored-By:` trailer regardless of which path is taken — the choice is about PR-authorship form, not attribution itself.

**Operational playbook**:
- T-0 (PRD/spec/plan locked, 2026-05-14): post the discussion #179 reply with the two-choice offer
- T+48h (2026-05-16 Sat — best-effort by Fri evening Day 1 PM per timeline): reply posted
- T+7d (2026-05-21 Thu): SLA breach checkpoint — if no contributor response, switch to (b) maintainer-authored
- Per PM finding L-3 + Architect L3 follow-up notification: post a "still proceeding on maintainer track, attribution preserved" comment at T+5d (Tue 2026-05-19) as a courtesy nudge before the SLA breach, so the contributor is not ghosted

**Resolves**: PRD Q5, spec FR-015, PM finding L-3.

## Project Structure

### Documentation (this feature)

```
specs/292-output-integrity-cross-sink-refinement/
├── plan.md              # This file (/aod.project-plan output)
├── spec.md              # Feature specification (/aod.spec output, PM-signed)
├── research.md          # Phase 0 research (KB + codebase + architecture + web)
├── data-model.md        # Phase 1 design artifact: pattern catalog structure additions
├── quickstart.md        # Phase 1 design artifact: verification recipe
├── contracts/
│   ├── finding-emission-contract.md   # OI-{N} emission preservation contract
│   ├── cross-link-no-emission-contract.md  # FR-007 testable invariant
│   └── adr-045-template.md            # ADR-045 structure template (7 decisions)
├── checklists/
│   └── requirements.md  # Spec quality checklist (created at spec stage)
└── tasks.md             # Task breakdown (/aod.tasks output — created next sub-step)
```

### Source Code (repository root)

This feature does not introduce new source code modules. The implementation modifies existing markdown and YAML files in place, with the addition of one new directory if the optional baseline is included.

```
# Files modified (additive-only edits)
.claude/skills/tachi-output-integrity/references/
└── detection-patterns.md   # Append Cat 6 + Cross-Agent Handoff Sinks subsection + Memory-Promotion Rules schema example

.claude/agents/tachi/
└── output-integrity.md     # ≤10 line cross-link prose in Purpose section

docs/architecture/02_ADRs/
└── ADR-045-output-integrity-cross-sink-refinement.md   # NEW (~200 lines, 7 decisions)

# Files added (optional, per Q2 = Add)
examples/multi-tenant-rag-app/
├── architecture.md         # Mermaid architecture description (LLM Process → Pinecone filter → multi-tenant query)
├── threats.md              # Regenerated SARIF + Markdown output
├── threat-report.md        # Regenerated narrative
├── risk-scores.md          # Regenerated risk scoring
└── (other auto-regenerated artifacts)

examples/
└── README.md               # Add one row to standardized examples table (per Architect M4)

# Files added (delivery-time)
CHANGELOG.md                # Append F-292 attribution entry (auto-generated by release-please from squash-merge title)

# Files modified at PRD stage (already committed in this feature branch)
docs/product/02_PRD/
├── INDEX.md                # PRD #292 row
├── _backlog/BACKLOG.md     # F-292 entry
└── 292-output-integrity-cross-sink-refinement-2026-05-14.md   # The PRD itself
```

**Structure Decision**: tachi follows a single-project structure (no front-end / back-end split). This feature is a docs-heavy refinement of existing files, plus one new ADR file and one optional new example baseline directory. No new source-code modules, no new test files (existing pytest backward-compat harness covers regression), no new schema files.

## Implementation Phases

### Phase 0: Outline & Research

**Status**: Research already conducted at spec stage and aggregated in `research.md`. Architectural decisions resolved above. No outstanding `NEEDS CLARIFICATION` markers.

**Phase 0 outputs (already created)**:
- `research.md` — aggregated findings from KB / codebase / architecture / web research streams
- `.aod/results/spec-research-kb.md` — KB detail
- `.aod/results/spec-research-codebase.md` — codebase detail
- `.aod/results/spec-research-architecture.md` — architecture constraints + ADR slot availability
- `.aod/results/spec-research-web.md` — OWASP / CWE / industry / academic references

**PM-finding resolutions** (M-1, M-2, M-3, L-1, L-2, L-3) flow into plan as follows:
- **M-1 (Q3 ADR commitment tension)** → resolved above in "Q3: ADR Authorship → Author ADR-045"; no-ADR exception path not invoked
- **M-2 (R2 output-handling vs poisoning corpus framing)** → Phase 1 contract `cross-link-no-emission-contract.md` will require the Cat 6 worked example to include a 1–2 sentence distinguishing-prose block ("output-handling = filter SYNTHESIS goes wrong; data-poisoning = corpus CONTENT goes wrong"), preempting the documentation-quality risk
- **M-3 (Conditional baseline SC-015)** → since Q2 = Add, add **SC-015** to spec.md frontmatter at PM re-sign-off: "If `examples/multi-tenant-rag-app/` baseline is added per FR-012, the baseline emits at least one `output-integrity` finding under the new Cat 6 pattern surface AND reproduces byte-identical under `SOURCE_DATE_EPOCH=1700000000`, AND is listed in `examples/README.md` (per Architect M4)." → To be added when /aod.tasks generates tasks.md; the SC is implicit via FR-012 + SC-001 today
- **L-1 (F-4 trust-exploitation in FR-010 catch-all)** → tasks.md will include a verification step explicitly grepping `git diff --name-only` for `.claude/agents/tachi/human-trust-exploitation.md` and the F-4 skill references (catch-all already covers this; the explicit step strengthens verifiability)
- **L-2 (Architect M2 byte-identical scope tension)** → resolved: SC-003 scope restricted to `output-integrity`-tagged finding subset (avoids F-248-style over-scoped byte-comparison trap from KB Entry 1); whole-pipeline byte-identity is owned by SC-004 on the 5 non-qualifying baselines where output-integrity emits zero today and zero after
- **L-3 (Architect L3 follow-up notification at Q5 SLA breach)** → resolved above in "Q5 operational playbook" — courtesy nudge at T+5d before SLA breach

### Phase 1: Design & Contracts

**Prerequisites**: research.md complete ✓; architectural decisions resolved ✓.

**Phase 1 outputs (to be generated in this sub-step)**:

1. **`data-model.md`** — Pattern catalog structure additions
   - Cat 6 structure (intro, citations, trigger keywords, applicable DFD types, indicators, worked example with Pinecone + Qdrant)
   - Cross-Agent Handoff Sinks subsection structure (boundary phrase, two cross-link targets, no-emission invariant, Memory-Promotion Rules schema example)
   - Memory-Promotion Rules inline schema example (~20 lines YAML)
   - Output-integrity agent Purpose section cross-link prose (≤10 lines)

2. **`contracts/finding-emission-contract.md`** — `OI-{N}` emission preservation
   - Schema invariance contract (no `schemas/finding.yaml` modification; `OI-{N}` prefix reuse)
   - Source-attribution populator contract preservation (F-1 contract inherited, every Cat 6 finding carries populated `source_attribution`)
   - Severity range (Cat 6 findings target high-severity bracket per LLM08:2025 baseline)

3. **`contracts/cross-link-no-emission-contract.md`** — FR-007 testable invariant
   - Cross-link prose does NOT cause `output-integrity` agent to emit findings on tool-arg or memory-write flows
   - Verification: re-run `agentic-app/` baseline; diff OI-tagged finding subset before/after; expect zero new emissions and byte-identical OI-scoped output under `SOURCE_DATE_EPOCH=1700000000`
   - Distinguishing-prose requirement (PM M-2 resolution): Cat 6 worked example must include 1–2 sentence distinguishing output-handling-vs-poisoning framing

4. **`contracts/adr-045-template.md`** — ADR-045 structure
   - 7 decisions mirroring ADR-032 (with content adapted to F-292's same-agent enrichment at finer-grained scope)
   - Cross-reference matrix: ADR-021 + ADR-023 + ADR-027 + ADR-028 + ADR-030 + ADR-032 + ADR-034 + ADR-035
   - Proposed → Accepted dual-commit protocol

5. **`quickstart.md`** — Verification recipe
   - How to verify FR-001 (Cat 6 exists with vector-filter pattern)
   - How to verify FR-004 (package-manager keywords present)
   - How to verify FR-006 (Cross-Agent Handoff Sinks subsection exists with cross-links)
   - How to verify FR-007 (no new OI emissions from cross-link prose alone)
   - How to verify FR-011 (no schema bump)
   - How to verify SC-001 / SC-002 / SC-003 / SC-004 / SC-010 / SC-011 / SC-012 / SC-013 / SC-014

6. **Agent context update**: Run `.aod/scripts/bash/update-agent-context.sh claude` to add F-292 to the agent's context window if any new technology was introduced. For this docs-heavy refinement, no new technology is introduced — the script run is a no-op or appends a one-line F-292 reference.

**Re-evaluate Constitution Check post-design**: After Phase 1 artifacts are generated, re-confirm the gates above. Expected outcome: all gates still PASS (no new violations introduced; Phase 1 artifacts are documentation contracts, not code).

## Definition of Done (Plan-Level)

Per Constitution Principle VII, this plan inherits the 3-step validation (with the docs-only exception clause from Principle VII Exceptions).

| Step | Validation | This Feature |
|---|---|---|
| 1. Pushed to Production | Squash-merge to main + release-please bump to next minor version | SC-013 (`feat(292):` Conventional-Commit PR title + 30-second release-please trigger per project memory `feedback_aod_deliver_release_gate.md`) |
| 2. Tested | All automated tests pass (`tests/scripts/test_backward_compatibility.py` byte-identical regression + `/security` re-scan zero new findings) | SC-003 + SC-004 + SC-012 |
| 3. User Validated | discussion #179 closure comment within 24h of merge + adopter feedback window | SC-007 + SC-008 |

## Risks & Mitigations (Plan-Level Carry-Forward from PRD)

| PRD Risk | Plan-Level Mitigation |
|---|---|
| R1 (Cross-link prose triggers unintended emissions) | Phase 1 contract `cross-link-no-emission-contract.md` codifies the testable invariant; FR-007 + SC-003 verify on re-run of `agentic-app/` |
| R2 (Vector-filter / data-poisoning corpus framing overlap) | PM M-2 resolution: Cat 6 worked example includes distinguishing-prose block |
| R3 (Authorship handoff stalls) | Q5 operational playbook with T+5d courtesy nudge + T+7d SLA breach + maintainer-authored fallback with `Co-Authored-By:` trailer |
| R4 (Schema-bump scope creep) | FR-011 hard constraint + SC-011 binary check + Edge case 7 preempts; ADR-045 D3 codifies the no-schema-bump invariant as the operational signal of signal-class identity preservation |
| R5 (Discussion #179 closure SLA slips) | FR-014 "best-effort, next-business-day acceptable" framing |

## Complexity Tracking

*No Constitution Check violations to track. All applicable gates PASS without exceptions.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _(none)_ | _(N/A)_ | _(N/A)_ |
