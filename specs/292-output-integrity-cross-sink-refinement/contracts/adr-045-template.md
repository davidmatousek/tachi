# Contract: ADR-045 Template Structure

**Feature**: F-292
**Phase**: 1 (Design)
**Date**: 2026-05-14

This contract specifies the structure of `docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md` — the architectural-decision record authored per Constitution Principle X mandate + BLP-01 lineage default + Q3 resolution in plan.md.

---

## 1. ADR Slot Allocation

**Allocated slot**: ADR-045

**Rationale**:
- ADR-043: RESERVED for BLP-03 cosign-vs-minisign (per project memory `project_blp03_signed_updates.md`)
- ADR-044: USED by Dual-Frame Public Positioning (2026-05-07)
- ADR-045: NEXT AVAILABLE

**Cross-verification on plan day** (per Architect L1 in PRD review): re-confirm slot 043 is still reserved before commit.

---

## 2. ADR Status Lifecycle (Proposed → Accepted Dual-Commit)

**Per ADR-027 / ADR-028 / ADR-030 / ADR-031 / ADR-032 / ADR-033 / ADR-034 / ADR-035 lineage**:

| Phase | Status field | Date field | Accepted-commit-SHA field |
|---|---|---|---|
| At planning lock (T+0) | `Proposed` | 2026-05-14 (today) | `<pending-post-merge-fill>` |
| At pre-PR (Wave 5) | `Accepted` | 2026-05-{N} (provisional, day of PR) | `<pending-post-merge-fill>` |
| Post-squash-merge | `Accepted` | (same as Wave 5) | actual SHA (filled in delivery T034-equivalent) |

**Two-commit governance** (per ADR-027 D8 lineage):
1. Commit 1 (planning lock): introduces ADR-045 with `Status: Proposed`
2. Commit 2 (pre-PR Wave 5): flips `Status: Proposed → Accepted`, sets provisional accepted-date, leaves `Accepted-commit-SHA: <pending-post-merge-fill>` placeholder
3. Post-merge: tasks.md final wave fills the actual SHA in a follow-up commit (per the F-282 close-out pattern: `f6441dd docs(282): T034 — flip ADR-042 status Proposed → Accepted`)

---

## 3. Required Structure (Mirrors ADR-032's 7-Decision Template)

### Header (mandatory)

```markdown
# ADR-045: Output-Integrity Cross-Sink Refinement (F-292)

**Status**: Proposed
**Date**: 2026-05-14
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Feature**: F-292 (PRD #292)
**Lineage**: Heuristic A enrichment branch, same-agent enrichment within F-1 `output-integrity` (8th BLP-01 execution)
**Cross-references**: ADR-021, ADR-023, ADR-027, ADR-028, ADR-030, ADR-032, ADR-034, ADR-035
```

### Context (mandatory)

Brief statement (≤300 words) covering:
- The community gap-surfacing chain: @armorer-labs discussion #179 comment (2026-05-12) → maintainer gap-analysis (2026-05-14) → PRD #292
- The three pattern-catalog gaps in shipped F-1 (Cat 6 vector-filter, Cat 2 package-manager keyword extension, Cat 3 cross-agent handoff prose + Memory-Promotion Rules)
- F-292's position as the 8th Heuristic A enrichment execution at single-agent scope (same-agent enrichment is finer-grained than F-3's ADR-032 single-agent-scope)

### Decisions (7 numbered, mirroring ADR-032)

#### D1: Heuristic A enrichment vs new agent — same-agent enrichment within `output-integrity`

**Decision**: F-292 enriches the existing `output-integrity` agent (host of F-1 / ADR-030) by appending one new Pattern Category 6, extending one existing trigger-keyword list, and adding one navigational subsection. We do NOT create a new AI-tier threat agent.

**Rationale (inheritance from ADR-030 D1 + ADR-032 D1)**: The three gap closures all fall within the **encoding/sanitization signal class** (machine-victim output handling, LLM05:2025) — same signal class as F-1. The signal-class taxonomy from ADR-030 D1 is inherited; ADR-032 D1's enrichment-vs-new-agent rationale is applied at finer-grained scope (same-agent, not just single-agent).

**Counter-argument absorption**: Outcome A — new agent for vector-filter / search-DSL injection — is rejected because vector-filter injection IS an output-handling signal (filter SYNTHESIS goes wrong, distinct from corpus CONTENT goes wrong which is `data-poisoning`'s surface). A new agent would fragment the encoding/sanitization signal class.

#### D2: Additive-only edit discipline per ADR-023 D3

**Decision**: All edits to `detection-patterns.md` are additive — Cat 1–5 byte-identical pre/post; Cat 6 appended after Cat 5; Cross-Agent Handoff Sinks subsection appended after Cat 6.

**Verification**: structural diff on Cat 1–5 sections returns empty.

#### D3: No schema bump — operational signal of signal-class identity preservation

**Decision**: `schemas/finding.yaml` is byte-identical pre/post merge. `schema_version: "1.8"` UNCHANGED. `OI-{N}` prefix reused for Cat 6 findings.

**Rationale**: The no-schema-bump status is the *operational signal* that the signal-class identity claim is upheld. If F-292 had a schema bump, it would implicitly claim cross-sink refinement is a distinct signal class — contradicting the D1 enrichment rationale. ADR-032 D3 precedent applies verbatim.

#### D4: No consumers-list edit

**Decision**: `tachi-shared/references/finding-format-shared.md` consumers list is unchanged. `output-integrity` is already registered there from F-1 / ADR-030.

#### D5: No functional orchestrator/dispatch edit

**Decision**: `orchestrator.md` and `dispatch-rules.md` are unchanged. `output-integrity` is already wired into orchestrator Phase 1 classification from F-1 / ADR-030.

#### D6: Public ADR omits commercial framing per SDR-001 Option C

**Decision**: ADR-045 stands on technical merits only. No commercial / strategic / source-attribution-system cross-references. No mention of BLP-01 or SDR-001 by name in this public ADR (per project memory `project_blp01_threat_coverage.md` `_internal/` gitignore convention).

#### D7: Pattern Category Disambiguation — Cat 6 boundary + cross-link prose

**Decision**: ADR-045 codifies two disambiguation invariants:

**Invariant A (Cat 6 vs Cat 2 boundary)**: Cat 6 (Vector / Search-DSL Injection) is distinguished from Cat 2 (Server-Side Execution Sinks) by:
- Primary CWE: CWE-943 (Cat 6) vs CWE-89 (Cat 2)
- Primary OWASP class: LLM08:2025 (Cat 6) vs LLM05:2025 (Cat 2)
- Architectural-tell: vector-DB / structured-search filter context (Cat 6) vs generic SQL/cmd/code execution (Cat 2)

**Invariant B (Cross-Agent Handoff Sinks navigational pointer)**: The Cross-Agent Handoff Sinks subsection does NOT extend `output-integrity`'s emission surface. It is a navigational pointer to `tool-abuse` (tool-argument handoff, owned via Pattern Categories 9–10) and `data-poisoning` (durable-memory-write handoff, owned via OWASP ASI06). `output-integrity` does NOT emit on those flows.

**Two-facet disjoint-tells inheritance from ADR-035 D4**: The same architecture surfacing both `output-integrity` Cat 6 AND `data-poisoning` corpus-poisoning findings is NOT a contradiction — the two facets have disjoint architectural tells (filter SYNTHESIS vs corpus CONTENT). The disambiguation subsection on `detection-patterns.md` codifies this for adopter readers.

### Consequences (mandatory)

- Eighth Heuristic A enrichment execution validates the pattern at finer-grained scope (same-agent within F-1)
- Future vector-DB engine additions (Weaviate, Milvus, Chroma) have a clean Cat 6 extension path
- Future package-manager surface extensions have a clean Cat 2 keyword-list extension path
- Future cross-agent-handoff documentation additions reuse the Gap 3 subsection structure
- ADR-045 sets the precedent for same-agent enrichment ADRs going forward (ADR-046+ may follow this template)

### Cross-Reference Matrix (mandatory)

```markdown
| ADR | Relevance |
|---|---|
| ADR-021 | SOURCE_DATE_EPOCH determinism — byte-identity gate for SC-003 / SC-004 |
| ADR-023 | Lean-agent + additive-only shared-reference discipline — D2 inheritance |
| ADR-027 | F-A1 taxonomy crosswalk — F-292 reuses OWASP LLM05/LLM08 + CWE-943 references |
| ADR-028 | F-A2 source_attribution contract — F-292 inherits F-1 populator (D1 cross-ref) |
| ADR-030 | F-1 direct precedent — F-292 enriches the same agent (D1 inheritance) |
| ADR-032 | F-3 single-agent enrichment-branch precedent — closest structural sibling (7-decision template source) |
| ADR-034 | F-5 two-agent enrichment-branch precedent — informational reference |
| ADR-035 | F-6 three-agent enrichment-branch precedent (ML Top 10 bundle); D4 two-facet disjoint-tells pattern (D7 inheritance) |
```

### ADRs Cited as Asymmetry (NOT Invoke) (mandatory)

```markdown
- ADR-031 Decision 8 (regex-alternation minor-bump rule) — F-292 explicitly does NOT invoke this; the no-schema-bump status is the operational signal of signal-class identity preservation (D3 rationale).
```

---

## 4. Optional Sections (May Include)

- **Alternatives Considered** (for D1): brief paragraph explaining why "new agent for vector-filter / search-DSL injection" was rejected
- **Implementation Notes**: pointer to `specs/292-output-integrity-cross-sink-refinement/plan.md` and `tasks.md` for build-stage details
- **Verification Steps**: enumerate the SC-003 / SC-004 / SC-010 / SC-011 / SC-012 / SC-014 acceptance tests
- **Provenance / Attribution Note**: explicit credit to @armorer-labs's gap-surfacing per the F-260 community-merge precedent

---

## 5. Length Estimate

Following the ADR-032 template structure (7 decisions, context, consequences, cross-reference matrix, asymmetry note, alternatives, implementation notes): **~180–220 lines** of markdown.

This is the typical envelope for BLP-01 enrichment-branch ADRs (ADR-032 is 174 lines, ADR-034 is 195 lines, ADR-035 is 218 lines).

---

## 6. Acceptance Tests

| Contract Invariant | Acceptance Test | Spec Anchor |
|---|---|---|
| ADR-045 file exists at next-available slot | `ls docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md` | FR-016 |
| Status field set to Proposed at planning lock | grep `^**Status**: Proposed$` in file | Proposed → Accepted dual-commit protocol |
| Status field flipped to Accepted at pre-PR Wave 5 | grep `^**Status**: Accepted$` in file before squash-merge | FR-016 + SC-014 |
| `Accepted-commit-SHA` placeholder pre-merge | grep `<pending-post-merge-fill>` in file | Proposed → Accepted dual-commit protocol |
| `Accepted-commit-SHA` filled post-merge | grep actual SHA (7 chars) in file after delivery | Delivery step (T034-equivalent) |
| 7 decisions present | grep `^### D[1-7]:` count == 7 | ADR-032 template inheritance |
| Cross-reference matrix lists all 8 ADRs | grep ADR-021/023/027/028/030/032/034/035 references | ADR-032 template inheritance |
| No mention of BLP-01 or SDR-001 by name | grep -i "BLP-01\|SDR-001" returns empty | D6 (SDR-001 Option C compliance) |
