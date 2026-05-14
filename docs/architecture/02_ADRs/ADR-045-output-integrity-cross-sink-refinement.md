# ADR-045: Output-Integrity Cross-Sink Refinement (F-292)

**Status**: Accepted
**Date**: 2026-05-14 (Proposed) → 2026-05-14 (Accepted, provisional pre-PR; final commit-SHA filled post-merge)
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Feature**: F-292 (PRD #292)
**Lineage**: Heuristic A enrichment branch, same-agent enrichment within F-1 `output-integrity` (8th BLP-01 execution)
**Cross-references**: ADR-021, ADR-023, ADR-027, ADR-028, ADR-030, ADR-032, ADR-034, ADR-035

## Context

A first-time community contributor surfaced three concrete coverage gaps in the shipped `output-integrity` agent through a gap-analysis comment on discussion #179 (2026-05-12). The maintainer review (2026-05-14) confirmed the gaps and produced PRD #292.

The three gaps are:

1. **Vector / Search-DSL Injection**: The agent emits no finding when an LLM Process synthesizes a vector-DB metadata filter (Qdrant, Pinecone) into a multi-tenant query interface where the filter could omit the tenant-scoping clause. OWASP LLM08:2025 (Vector and Embedding Weaknesses) names "missing tenant isolation in multi-tenant RAG systems" as a canonical industry vulnerability; the agent's catalog had no pattern surface for it.

2. **Package-Manager / CI-Workflow Sinks**: The agent catches generic shell injection but emits no finding when an LLM Process emits `npm install <attacker-controlled-name>` or GitHub Actions YAML into an execution sink. The 2026 incident record (SANDWORM_MODE npm worm; LiteLLM PyPI compromise) and academic literature (arXiv 2605.07135 Agentic Workflow Injection) establish this as an active attack surface.

3. **Cross-Agent Handoff Boundary**: When LLM output flows into a tool-call argument or durable memory write, three different agents emit overlapping findings (`output-integrity` on encoding/sanitization, `tool-abuse` on tool-arg injection, `data-poisoning` on durable-memory writes). The catalog had no navigational subsection making the handoff boundary explicit.

F-292 is the **8th Heuristic A enrichment execution** at the finer-grained scope of *same-agent* enrichment (vs F-3 / ADR-032's single-agent-scope). The three gap closures all fall within the encoding/sanitization signal class established by F-1 / ADR-030, so the right architectural form is enrichment of the existing agent — not a new AI-tier agent.

This ADR codifies the seven architectural decisions that govern that enrichment, mirroring the ADR-032 7-decision template.

## Decisions

### D1: Heuristic A enrichment vs new agent — same-agent enrichment within `output-integrity`

**Decision**: F-292 enriches the existing `output-integrity` agent (host of F-1 / ADR-030) by appending one new Pattern Category 6, extending one existing trigger-keyword list, and adding one navigational subsection. We do NOT create a new AI-tier threat agent for vector-filter / search-DSL injection.

**Rationale (inheritance from ADR-030 D1 + ADR-032 D1)**: The three gap closures all fall within the **encoding/sanitization signal class** (machine-victim output handling, LLM05:2025) — same signal class as F-1. The signal-class taxonomy from ADR-030 D1 is inherited; ADR-032 D1's enrichment-vs-new-agent rationale is applied at finer-grained scope (same-agent, not just single-agent).

**Counter-argument absorption**: An alternative form — new agent for vector-filter / search-DSL injection — is rejected because vector-filter injection IS an output-handling signal (filter *SYNTHESIS* goes wrong, distinct from corpus *CONTENT* goes wrong which is `data-poisoning`'s surface). A new agent would fragment the encoding/sanitization signal class and force adopters to reconcile two agents on the same architectural surface.

### D2: Additive-only edit discipline per ADR-023 D3

**Decision**: All edits to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` are additive — Cat 1–5 byte-identical pre/post; Cat 6 appended after Cat 5; Cross-Agent Handoff Sinks subsection appended after Cat 6. The `.claude/agents/tachi/output-integrity.md` edit is ≤10 lines of navigational prose appended to the Purpose section.

**Verification**: structural diff on Cat 1–5 sections of `detection-patterns.md` returns empty; `git diff` on `output-integrity.md` returns ≤10 changed lines.

### D3: No schema bump — operational signal of signal-class identity preservation

**Decision**: `schemas/finding.yaml` is byte-identical pre/post merge. `schema_version: "1.8"` UNCHANGED. The `OI-{N}` prefix is reused for Cat 6 findings.

**Rationale**: The no-schema-bump status is the *operational signal* that the signal-class identity claim is upheld. If F-292 introduced a schema bump (e.g., a new `OQ-{N}` prefix for "output query injection"), it would implicitly claim cross-sink refinement is a distinct signal class — contradicting the D1 enrichment rationale. ADR-032 D3 precedent applies verbatim; ADR-034 D6 and ADR-035 D6 reinforced this lineage on the F-5 and F-6 enrichments.

**Edge case carved out by spec Edge Case 7**: A reviewer arguing for a new `OQ-{N}` prefix is referred to this decision and to ADR-030 D8. The schema-bump cost would cascade to populator wiring, taxonomy crosswalks, and source-attribution contracts — expressly out of scope.

### D4: No consumers-list edit

**Decision**: `.claude/skills/tachi-shared/references/finding-format-shared.md` consumers list is unchanged. `output-integrity` is already registered there from F-1 / ADR-030.

### D5: No functional orchestrator/dispatch edit

**Decision**: `.claude/agents/tachi/orchestrator.md` and dispatch-rules documentation are unchanged. `output-integrity` is already wired into orchestrator Phase 1 classification from F-1 / ADR-030; same-agent enrichment within an already-dispatched agent requires no dispatch-routing update.

### D6: Public ADR omits commercial framing per SDR-001 Option C

**Decision**: ADR-045 stands on technical merits only. No commercial / strategic / source-attribution-system cross-references. No mention of the internal initiative codename or the dual-frame public-positioning ADR by name in this public ADR.

**Rationale**: The technical-merits-only frame keeps ADR-045 directly useful to external adopters (the primary ADR audience) and consistent with the public-positioning discipline applied across the BLP-01 enrichment-branch ADR series.

### D7: Pattern Category Disambiguation — Cat 6 boundary + cross-link prose

**Decision**: ADR-045 codifies two disambiguation invariants:

**Invariant A (Cat 6 vs Cat 2 boundary)**: Cat 6 (Vector / Search-DSL Injection) is distinguished from Cat 2 (Server-Side Execution Sinks) by:

- **Primary CWE**: CWE-943 (Improper Neutralization of Special Elements in Data Query Logic) is the Cat 6 primary anchor; CWE-89 (SQL Injection) remains the Cat 2 primary. CWE-943 is the canonical parent for non-SQL query-language injection and is the architectural reason Cat 6 deserves its own category rather than a Cat 2 sub-class.
- **Primary OWASP class**: LLM08:2025 (Vector and Embedding Weaknesses) is the Cat 6 primary anchor; LLM05:2025 (Improper Output Handling) is referenced as a cross-anchor. Cat 2 uses LLM05:2025 as primary.
- **Architectural tell**: vector-DB / structured-search filter context for Cat 6; generic SQL/cmd/code execution sink for Cat 2.

**Invariant B (Cross-Agent Handoff Sinks navigational pointer)**: The Cross-Agent Handoff Sinks subsection does NOT extend `output-integrity`'s emission surface. It is a navigational pointer to `tool-abuse` (tool-argument handoff, owned via Pattern Categories 9–10) and `data-poisoning` (durable-memory-write handoff, owned via OWASP ASI06 Memory & Context Poisoning). `output-integrity` emits zero findings on those flows; the subsection's only function is reader navigation.

**Two-facet disjoint-tells inheritance from ADR-035 D4**: The same architecture surfacing both an `output-integrity` Cat 6 finding AND a `data-poisoning` corpus-poisoning finding is NOT a contradiction — the two facets have disjoint architectural tells (filter SYNTHESIS goes wrong for output-integrity; corpus CONTENT goes wrong for data-poisoning). The Cat 6 worked example includes a distinguishing-prose block making this co-emission explicit, and the cross-agent subsection adds a navigational pointer to the `data-poisoning` agent for the corpus-side surface.

## Consequences

- Eighth Heuristic A enrichment execution validates the pattern at finer-grained scope (same-agent within F-1's host).
- Future vector-DB engine additions (Weaviate, Milvus, Chroma) have a clean Cat 6 extension path — append to the trigger-keyword list and add a worked sub-example.
- Future package-manager surface extensions (e.g., new registries, new CI providers) have a clean Cat 2 keyword-list extension path.
- Future cross-agent-handoff documentation additions can reuse the Cross-Agent Handoff Sinks subsection structure (boundary phrase → two-agent cross-links → mitigation pattern with worked schema example).
- The Memory-Promotion Rules worked schema example becomes institutional knowledge for any future agent introducing a durable-write surface; if a future feature lifts the example into a separate skill-reference file at reuse time, the inline placement here is fully reversible.
- ADR-045 sets the precedent for same-agent enrichment ADRs going forward (ADR-046+ may follow this template at the same scope).

## Cross-Reference Matrix

| ADR | Relevance |
|---|---|
| ADR-021 | SOURCE_DATE_EPOCH determinism — byte-identity gate for SC-003 (OI-scoped) / SC-004 (5 non-qualifying baselines) |
| ADR-023 | Lean-agent + additive-only shared-reference discipline — D2 inheritance |
| ADR-027 | F-A1 taxonomy crosswalk — F-292 reuses OWASP LLM05/LLM08 + CWE-943 references |
| ADR-028 | F-A2 source_attribution contract — F-292 inherits F-1 populator (D1 cross-ref) |
| ADR-030 | F-1 direct precedent — F-292 enriches the same agent (D1 inheritance) |
| ADR-032 | F-3 single-agent enrichment-branch precedent — closest structural sibling (7-decision template source) |
| ADR-034 | F-5 two-agent enrichment-branch precedent — informational reference |
| ADR-035 | F-6 three-agent enrichment-branch precedent (ML Top 10 bundle); D4 two-facet disjoint-tells pattern (D7 inheritance) |

## ADRs Cited as Asymmetry (NOT Invoked)

- **ADR-031 Decision 8 (regex-alternation minor-bump rule)** — F-292 explicitly does NOT invoke this. The no-schema-bump status is the operational signal of signal-class identity preservation (D3 rationale). Invoking ADR-031 D8 would imply a new finding-id prefix is needed, which contradicts D1 and D3.

## Alternatives Considered

- **New agent for vector-filter / search-DSL injection** (rejected, see D1 counter-argument absorption above).
- **Cat 2 sub-class extension instead of new Cat 6** (rejected): vector-filter injection has a distinct primary CWE (CWE-943, not CWE-89) and a distinct primary OWASP class (LLM08, not LLM05). The category boundary at CWE-pinning + OWASP-class level argues for a clean Cat 6, not a Cat 2 sub-class. Future structured-query-language additions (GraphQL injection, NoSQL operator injection, LDAP, XQuery, XPath, DQL — all CWE-943 family) inherit Cat 6 cleanly.
- **Skip the optional multi-tenant RAG example baseline** (rejected): The existing `agentic-app/` baseline does not exercise vector-DB patterns; without a dedicated baseline, regression protection on Cat 6 emissions relies solely on the inline worked example. Adding `examples/multi-tenant-rag-app/` doubles as adopter documentation and pays compounding regression-protection dividends as future vector-DB engines are added.
- **Skip the ADR (no-ADR exception path)** (rejected): Constitution Principle X mandates ADR authorship for architectural decisions. BLP-01 lineage has zero precedent for skipping; the exception itself would require an ADR or Principle X cross-cite — heavier ceremony than just authoring this ADR.
- **Separate skill-reference file for Memory-Promotion Rules** (rejected at this scope): Single-use surface today — only the Cross-Agent Handoff Sinks subsection references the worked schema example. Co-location keeps the navigational pointer AND the mitigation pattern in one place. If reuse from adjacent agents is anticipated in a follow-on refinement, the Memory-Promotion Rules block can be lifted to a separate skill-reference file at that point — fully reversible.

## Implementation Notes

- **Plan**: `specs/292-output-integrity-cross-sink-refinement/plan.md`
- **Tasks**: `specs/292-output-integrity-cross-sink-refinement/tasks.md`
- **Pattern catalog additions**: `.claude/skills/tachi-output-integrity/references/detection-patterns.md` (Cat 6 ~50 lines; Cat 2 keyword extension + sub-example ~25 lines; Cross-Agent Handoff Sinks subsection ~75 lines)
- **Agent file cross-link**: `.claude/agents/tachi/output-integrity.md` Purpose section, ≤10 line diff
- **Optional baseline**: `examples/multi-tenant-rag-app/architecture.md` plus auto-regenerated artifacts

## Verification Steps

| Spec Anchor | Acceptance Test |
|---|---|
| SC-003 (cross-link no-emission) | Re-run `tachi.threat-model` on `examples/agentic-app/`; diff OI-scoped finding subset pre/post under `SOURCE_DATE_EPOCH=1700000000`; expect byte-identical |
| SC-004 (5 non-qualifying baselines byte-identical) | `pytest tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000`; all 5 baseline tests PASS |
| SC-010 (24+2 file zero-edit invariant) | `git diff main --name-only` lists only the four targeted file surfaces |
| SC-011 (no schema bump) | `git diff main -- schemas/finding.yaml` returns empty |
| SC-012 (security re-scan zero new findings) | `/security` skill on modified file surface; zero new findings |
| SC-014 (ADR-045 Accepted before squash-merge) | grep `^\*\*Status\*\*: Accepted$` in this file before `gh pr ready` |

## Provenance / Attribution Note

The three gap surfaces codified in this ADR were identified by community contributor `@armorer-labs` in a gap-analysis comment on discussion #179 (2026-05-12). The contribution chain follows the F-260 community-merge precedent: discussion → maintainer gap-analysis → PRD → spec → plan → tasks → ADR → implementation → CHANGELOG attribution. Authorship is preserved end-to-end via either contributor-authored PR (path a, F-260 precedent) or maintainer-authored PR with `Co-Authored-By:` commit trailer and explicit CHANGELOG attribution line (path b, default fallback at 7-day SLA breach).
