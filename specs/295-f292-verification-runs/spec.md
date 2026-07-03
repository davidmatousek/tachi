---
prd_reference: docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-03
    status: APPROVED
    notes: "All 13 PRD ACs trace to scenarios/FRs; 7/7 Out items carried; false-pass guard + D-1 hard gate + fix-vs-file preserved; OQ-5 correctly deferred to plan.md. Research-grounded additions (FR-012/016/019/021 + 2 folded drifts) judged constraint-surfacing, not scope creep. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: F-292 Post-Merge Verification Runs (T017 + T026)

**Feature Branch**: `295-f292-verification-runs`
**Created**: 2026-07-03
**Status**: Draft
**Input**: User description: "PRD: 295 - f292-verification-runs"
**PRD**: `docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md` (Approved v1.2)
**Source Issue**: [#295](https://github.com/davidmatousek/tachi/issues/295) (type:retro; parent #292, PR #293, squash `0629fa2`, v4.36.0)
**Research**: `specs/295-f292-verification-runs/research.md` (PRD anchors verified 9/9 at HEAD; 2 drifts folded below)

F-292 shipped 2026-05-14 with two success criteria left empirically unverified because both require user/session-initiated `tachi` pipeline runs that could not execute autonomously from `/aod.build` (KB Entry 7 deferral → Issue #295). This feature executes those two verification runs with fail-closed, false-pass-guarded semantics, commits durable evidence, and adds one purpose-built CI check so the new baseline's reproducibility claim cannot silently decay. The deliverable is the **verification record** — a run that discovers a real defect closes honestly via defect filing (fix-vs-file), not inline fixes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - T017: OI no-emission verification on `agentic-app` (Priority: P0, SC-003)

When I maintain the `output-integrity` agent after F-292's Cross-Agent Handoff Sinks cross-link prose landed, I want the no-emission invariant verified empirically against the contract's named fixture (`examples/agentic-app/`), so SC-003 stops being an untested claim and future detection-pattern edits inherit a logged, **working** procedure for scoped no-emission verification (the documented procedure in contract §3 is itself defective — it would have false-passed).

**Why this priority**: This is the deferred F-292 T017 checkbox on Issue #295 — half the reason the issue exists. The contract-§3 false-pass discovery (broken extraction filter diffs empty-vs-empty) makes executing the verification *correctly* more justified, not less: an unverified invariant plus a broken verification procedure is compound decay.

**Independent Test**: Can be fully tested by running the OI-scoped analysis at HEAD, extracting the OI subset from both sides with the corrected filter, and producing the committed verification record — independent of US-2/US-3 (different fixture, different artifacts).

**Acceptance Scenarios**:

1. **Given** current HEAD, **When** the `tachi-output-integrity` agent is dispatched single-agent against `examples/agentic-app/architecture.md` (primary path; scoped full run with the narrative phase skipped as fallback), **Then** the run completes and the corrected extraction over the comparison artifact (filter on `partialFingerprints["findingId/v1"]` prefix `OI-`) yields a **non-empty** OI subset — expected 4 findingIds. An empty extraction is a gate ERROR, never a pass. `[MANUAL-ONLY] live LLM pipeline dispatch, session-initiated; not CI-repeatable` *(Plan-stage note, Architect M-a/OQ-5: the single-agent path emits findings text, not a SARIF — plan.md MUST state which path yields the comparison SARIF: a SARIF-generation step over the assembled findings, or the scoped-full fallback's native SARIF.)*
2. **Given** the pre-292 anchor (`git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif`, where `0629fa2~1` = `3f107e3`), **When** the anchor's OI subset is extracted with the same corrected filter, **Then** it yields exactly `OI-1, OI-2, OI-3, OI-4` (verified live 2026-07-03) — pinning expected cardinality 4 on the anchor side of the false-pass guard.
3. **Given** both OI subsets, **When** they are diffed, **Then** the hard gate (decision D-1) is evaluated on {OI finding count, findingId set, per-finding sink/flow identity}: identical → gate PASS; any gate-field delta → gate FAIL. Byte-level deltas outside the gate fields are each attributed to a named intervening commit/feature (F-260b asset tags, F-098/#311 MAESTRO annotations, #184–#186 crosswalk growth are the three known-benign drift classes); any **unattributable** delta → gate FAIL (fail-closed).
4. **Given** the diff outcome (pass or fail), **When** verification concludes, **Then** a durable SC-003 verification record (commands, anchor SHAs, corrected filter, extraction outputs, diff result, attribution table) is committed under `specs/295-f292-verification-runs/`, linked from Issue #295, and the T017 checkbox on #295 is checked.
5. **Given** a gate FAIL (F-292-attributable or unattributable delta), **When** the failure is recorded, **Then** a defect Issue is filed with the evidence attached and #295 records the failure honestly — no inline fix, no silent pass, and the feature still closes on the committed record.
6. **Given** contract §3's defective procedure, **When** US-1 lands, **Then** a defect Issue is filed against `specs/292-output-integrity-cross-sink-refinement/contracts/cross-link-no-emission-contract.md` documenting **both** confirmed defects — (a) the zero-match `ruleId | startswith("OI-")` filter (real ruleIds are `tachi/*`-family; OI identifiers live at `partialFingerprints["findingId/v1"]`; §6 counter-tests inherit the defect) and (b) §3's invocation of `tachi.threat-model` as a stdout-JSON shell command, which it never was — with the corrected filter recorded. Disposition of the archived artifact (annotate vs correct) is decided in that Issue (OQ-4), not here.
7. **Given** two run attempts that fail on tooling grounds (e.g., context overflow on both primary and fallback paths), **When** the escape hatch triggers (Team-Lead M-1), **Then** the tooling defect is filed as its own Issue and #295 closes with the staged-partial verification record — the feature cannot run open-ended.

---

### User Story 2 - T026: Committed Cat 6 evidence baseline for `multi-tenant-rag-app` (Priority: P0, SC-015)

When I browse `examples/multi-tenant-rag-app/` as an adopter evaluating tachi's Cat 6 (Vector/Search-DSL Injection) coverage, I want committed pipeline artifacts demonstrating the expected finding, so the flagship F-292 fixture honors the `examples/README.md` pairing contract ("each example pairs an architecture with a complete threat model output") like every other listed example, instead of shipping an architecture file with zero committed evidence.

**Why this priority**: This is the deferred F-292 T026 checkbox on Issue #295 — the other half of issue closure. The example is *already listed* in `examples/README.md:15` as the Cat 6 trigger fixture; the missing artifacts are a standing pairing-contract violation visible to every adopter.

**Independent Test**: Can be fully tested by running the pipeline over `examples/multi-tenant-rag-app/architecture.md`, checking the Cat 6 finding is present, committing the artifact set, and re-deriving `threats.sarif` from the committed `threats.md` — independent of US-1 (different fixture; no anchor diff).

**Acceptance Scenarios**:

1. **Given** current HEAD, **When** the full pipeline runs over `examples/multi-tenant-rag-app/architecture.md` (7 components per the README row, +1 external LLM service entry; ~101 lines; narrative phase ON because `threat-report.md` is a required artifact; staged per-skill invocations as overflow fallback; `SOURCE_DATE_EPOCH=1700000000` set for pipeline-uniformity), **Then** at least one `output-integrity` finding under the Cat 6 pattern surface is emitted — expected shape: LLM-synthesized Pinecone metadata filter omitting the `tenant_id` clause, CWE-943 primary, `OI-` finding-id prefix per `schemas/finding.yaml` v1.9. `[MANUAL-ONLY] live LLM pipeline run, session-initiated; not CI-repeatable`
2. **Given** the run output (written to an explicit non-gitignored output directory — the command's default `docs/security/` and `examples/*/test-output/` are both gitignored), **When** artifacts are committed to `examples/multi-tenant-rag-app/` (root-level layout per the README pairing contract and `maestro-reference` precedent), **Then** the committed set is exactly: `threats.md`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif` (LLM-authored, byproducts of the actual run — never hand-edited post-hoc) + `threats.sarif` (script-generated from the committed `threats.md` via the URI-corrected `generate-threats-sarif.py`), with the `## Affected Assets` block populated by the populator step (an all-`[]` block is valid if the architecture carries no `[asset:...]` tags).
3. **Given** the committed `threats.md`, **When** `scripts/generate-threats-sarif.py` re-derives `threats.sarif` from it, **Then** the result is byte-identical to the committed `threats.sarif` (SC-015 clause b, narrowed to the structurally regenerable artifact — the generator is timestamp-free, so determinism is by construction; the epoch pin is convention, not mechanism). `risk-scores.sarif` carries **no** byte-identity claim: `generate-risk-scores-sarif.py` has no CLI, hardcodes agentic-app paths, and gates on ≥80 findings — its parameterization is filed as a follow-up enhancement Issue, not smuggled in.
4. **Given** the new committed `threats.md` carries a "Risk by MAESTRO Layer" table (a current-pipeline run emits one), **When** the `tachi-maestro-coverage` workflow fires (it triggers on `examples/**/threats.md` and its invariant test globs the whole corpus), **Then** the table presents all seven L1–L7 rows and both maestro coverage tests stay green — the one CI-enforced content-shape gate on the new artifacts.
5. **Given** `examples/README.md`, **When** artifacts land, **Then** the existing `multi-tenant-rag-app` row remains accurate (component count 7, Cat 6 trigger description) — updated only if the run evidence contradicts it.
6. **Given** the URI enabler, **When** `generate-threats-sarif.py` derives the SARIF source URI from its input path instead of the constant at `:481` (`build_result()`), **Then** the new example's SARIF references `examples/multi-tenant-rag-app/threats.md` (not agentic-app), a covering assertion exists, and agentic-app regeneration output is byte-unchanged — compared **script-output-before vs script-output-after** the URI change (Architect L-a: never vs the LLM-authored committed SARIF, a different authoring tier).
7. **Given** a run that emits **zero** Cat 6 findings, or a regen that is **not** byte-identical, **When** the gate fails, **Then** a defect Issue is filed with the evidence (fix-vs-file — no inline fix to agents, detection patterns, or generator logic beyond the named URI enabler), #295 records the failure honestly, and US-3 is deferred to that defect Issue per its structural gate.

---

### User Story 3 - Durable reproducibility check for the new baseline (Priority: P1, optional-on-T026-success)

When a future change touches `generate-threats-sarif.py` or the committed `multi-tenant-rag-app` baseline, I want a purpose-built byte-identity test covering the SARIF-regen claim — wired so it actually executes in CI — so SC-015 clause b is continuously enforced instead of decaying as an unenforced one-time claim (the existing PDF byte-identity suite is local-only and wired into no CI workflow; this check is the deliberate contrast).

**Why this priority**: P1 durability addition beyond Issue #295's literal checkboxes (defer-able without breaking issue closure, per AC-3c gate). One runnable check per `code-economy.md`; explicitly **NOT** `BASELINE_EXAMPLES` membership — that suite asserts *PDF* byte-identity (requires a committed `security-report.pdf.baseline`, out of scope) and its F-142 gate asserts every finding carries `agentic_pattern: none`, which a multi-agent RAG example rightly cannot satisfy (mermaid-agentic-app skip-carve precedent).

**Independent Test**: Can be tested by running the new test module in the standard pytest invocation and by verifying the CI workflow change fires on a synthetic edit to a covered path — but only after US-2's artifacts exist (structural dependency, AC-3c).

**Acceptance Scenarios**:

1. **Given** the committed `threats.md` + `threats.sarif` pair, **When** the new purpose-built test runs `generate-threats-sarif.py` over the committed `threats.md`, **Then** it asserts byte-identity against the committed `threats.sarif` and is green in the standard pytest invocation, fail-closed on degenerate inputs (missing file, empty parse → FAIL, never skip).
2. **Given** CI-gating reality (no workflow runs all of `tests/scripts/`; `scripts/generate-threats-sarif.py` is currently in **no** workflow's paths), **When** the check lands, **Then** it is wired to actually execute in CI — the covered surfaces (`scripts/generate-threats-sarif.py`, the new test module, `examples/multi-tenant-rag-app/threats.md` + `threats.sarif`) appear in the triggering paths AND the test invocation, lock-step in the same commit (ADR-039 D-6; mechanism choice — join `tachi-pytest.yml`'s 15-module list vs a dedicated single-runner workflow per the `tachi-catalog-drift.yml` pattern — is a plan.md decision).
3. **Given** the check lands, **Then** the PR body states what the test covers (SARIF-regen byte-identity for this baseline only) and what it deliberately does not (PDF byte-identity, `BASELINE_EXAMPLES` membership, `risk-scores.sarif` regen), so the maintenance surface is explicit.
4. **Given** a T026 gate failure (AC US-2.7), **When** US-3's structural gate evaluates (Team-Lead M-2), **Then** US-3 defers to the follow-up defect Issue **without** counting as a US-3 failure — #295 closure is unaffected.

---

### Edge Cases

- **Empty OI extraction on either side** (fresh run or anchor): gate ERROR (broken filter, wrong artifact, or failed run) — halts the diff; never interpreted as "zero emissions = pass". Expected cardinality 4 is pinned on the anchor side.
- **Orchestrator context overflow**: primary T017 path avoids the orchestrator entirely (single-agent dispatch). T026's architecture is small (7 components; overflow risk genuinely low), and the known overflow point is Phase 5 — after `threats.md`/`threats.sarif` are written; fallback is staged per-skill invocations for the remaining artifacts. Overflow behavior knowledge is 32 days old — re-confirm on first run rather than assume.
- **Two tooling-failure attempts on one story**: escape hatch (M-1) — file the tooling defect Issue, close with the staged-partial record. Never a third open-ended attempt.
- **Genuine verification failure discovered** (F-292-attributable delta, missing Cat 6 finding, non-reproducing regen): the run *worked* — pre-decided disposition is defect-Issue filing with evidence (fix-vs-file); #295 closes on the record either way (KB Entry 17 pattern).
- **`| OI-` row-count cross-check ambiguity**: the 8-row expectation holds only for the top-level `examples/agentic-app/threats.md` (4 findings × §4 + §7 tables); the `sample-report/threats.md` copy has 12 rows (F-260b Affected Assets block adds 4). Any human cross-check must name the file and scope to §4+§7. The SARIF `partialFingerprints` set remains the sole authoritative anchor.
- **Pre-existing red in affected test suites**: literal pre-state totals are recorded before any F-295 artifact lands; inherited reds are dispositioned (fix-vs-file), never silently absorbed into F-295's evidence (KB Entry 15).
- **Corpus-globbing/count-pinned tests**: adding a 7th example's artifacts may hit tests that glob `examples/**` or pin corpus counts — the pre-state sweep enumerates them before the commit; the MAESTRO coverage invariant is the one known CI-enforced instance.
- **Concurrent runs**: T017 and T026 never run in parallel (shared orchestrator context pressure) — serial execution is a hard constraint, not a scheduling preference.
- **Issue auto-close mechanics**: #295 must not close as a side effect of a PR merge before the evidence record and checkbox updates land — closure is a deliberate deliver-stage act (KB Entry 10).

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated. The Given/When/Then acceptance scenarios for FR-001–FR-018 are enumerated per user story above; each FR below names its owning scenarios.

**US-1 — T017 / SC-003 (fail-closed OI no-emission verification)**

- **FR-001**: The system MUST execute a fresh OI-scoped analysis of `examples/agentic-app/architecture.md` at current HEAD, with single-agent `tachi-output-integrity` dispatch as the primary path and a scoped full run (narrative phase skipped) as the sole fallback. *(US-1 scenarios 1, 7)*
- **FR-002**: The verification MUST produce a machine-comparable OI-subset representation of the fresh run carrying, per finding: findingId, and sink/flow identity — extractable by the corrected filter from a SARIF-shaped comparison artifact. Which path yields that artifact (SARIF-generation step over assembled findings vs scoped-full fallback's native SARIF) is a plan.md decision (OQ-5/Architect M-a) that the plan MUST state explicitly. *(US-1 scenario 1)*
- **FR-003**: OI-subset extraction MUST use the corrected filter — `jq '.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))'` — as the authoritative mechanism, superseding contract §3; `threats.md` OI rows (top-level file, §4+§7 scope, 8 rows) serve only as human-readable cross-check. *(US-1 scenarios 1–3)*
- **FR-004**: The diff gate MUST be false-pass-guarded: both extracted OI subsets non-empty before any diff is trusted, with expected cardinality 4 pinned via the live-verified anchor (`0629fa2~1` = `3f107e3` → `OI-1..OI-4`); an empty extraction is a gate ERROR. *(US-1 scenarios 1–2; edge cases)*
- **FR-005**: The hard gate MUST be emission-level identity per decision D-1 — {OI finding count, findingId set, per-finding sink/flow identity} — with all other field deltas relegated to the attributable-drift bucket; every byte-delta MUST be attributed to a named intervening commit/feature (known-benign classes: F-260b asset tags, F-098/#311 MAESTRO, #184–#186 crosswalk) or the gate fails (fail-closed). *(US-1 scenario 3)*
- **FR-006**: A durable SC-003 verification record (commands, anchor SHAs, filter, extraction outputs, diff result, attribution table) MUST be committed under `specs/295-f292-verification-runs/` and linked from Issue #295, with the T017 checkbox checked on completion. *(US-1 scenario 4)*
- **FR-007**: Any gate failure MUST be filed as a defect Issue with evidence attached (fix-vs-file); #295 records the outcome honestly and still closes on the committed record. *(US-1 scenario 5)*
- **FR-008**: A defect Issue MUST be filed against contract §3 documenting both confirmed defects (zero-match filter; non-executable stdout-JSON invocation) and the corrected procedure; the archived artifact's disposition (OQ-4) is decided there. *(US-1 scenario 6)*

**US-2 — T026 / SC-015 (committed Cat 6 evidence baseline)**

- **FR-009**: The system MUST run the full pipeline over `examples/multi-tenant-rag-app/architecture.md` to an explicit non-gitignored output directory, and the run MUST yield ≥1 `output-integrity` finding on the Cat 6 pattern surface (CWE-943 primary; `OI-` prefix). *(US-2 scenarios 1–2)*
- **FR-010**: The committed artifact set at `examples/multi-tenant-rag-app/` root MUST be exactly `threats.md`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif` (LLM-authored run byproducts, never hand-edited) + `threats.sarif` (script-generated from the committed `threats.md`), with the `## Affected Assets` block populated. *(US-2 scenario 2)*
- **FR-011**: The committed `threats.sarif` MUST be byte-identically re-derivable from the committed `threats.md` via `generate-threats-sarif.py`; `risk-scores.sarif` carries no regen claim, with the generator-parameterization gap filed as a follow-up enhancement Issue. *(US-2 scenario 3)*
- **FR-012**: The new committed `threats.md` MUST keep the `tachi-maestro-coverage` workflow green — its "Risk by MAESTRO Layer" table (if present, which a current-pipeline run emits) MUST carry all seven L1–L7 rows. *(US-2 scenario 4)*
- **FR-013**: The `examples/README.md` `multi-tenant-rag-app` row MUST remain accurate after artifacts land (7 components, Cat 6 trigger description). *(US-2 scenario 5)*
- **FR-014**: `generate-threats-sarif.py` MUST derive the SARIF source URI from its input path (replacing the hardcoded constant at `:481` in `build_result()`), with a covering assertion, and agentic-app regeneration MUST be byte-unchanged compared script-output-before vs script-output-after. This is the **only** in-scope generator change. *(US-2 scenario 6)*

**US-3 — Durable reproducibility check (P1, gated on US-2)**

- **FR-015**: A purpose-built test MUST assert byte-identity between `generate-threats-sarif.py` output over the committed `multi-tenant-rag-app/threats.md` and the committed `threats.sarif`, failing closed on degenerate inputs; it MUST NOT be implemented as `BASELINE_EXAMPLES` membership. *(US-3 scenario 1)*
- **FR-016**: The check MUST actually execute in CI: the new test module, `scripts/generate-threats-sarif.py`, and both committed example artifacts MUST appear in a workflow's triggering paths AND its test invocation, wired lock-step in one commit (mechanism — join `tachi-pytest.yml` vs dedicated workflow — decided in plan.md). *(US-3 scenario 2)*
- **FR-017**: The delivery PR body MUST state the check's coverage boundary (covers: this baseline's SARIF-regen byte-identity; deliberately not: PDF byte-identity, `BASELINE_EXAMPLES`, `risk-scores.sarif`). *(US-3 scenario 3)*
- **FR-018**: US-3 MUST proceed only on US-2 regen success (AC-2c/FR-011 pass); on T026 gate failure it defers to the follow-up defect Issue without counting as a US-3 failure. *(US-3 scenario 4)*

**Cross-cutting**

- **FR-019**: Before any F-295 artifact lands, literal pre-state totals for the affected test suites MUST be recorded and committed as `specs/295-f292-verification-runs/test-results/pre-state.md`, including a sweep for corpus-globbing/count-pinned tests over `examples/**`; inherited reds are dispositioned fix-vs-file, never absorbed. *(edge cases; KB Entry 15)*
- **FR-020**: Scope fence: F-295 MUST NOT modify detection-tier files (threat-agent personas, `detection-patterns.md` references, `schemas/finding.yaml`), the archived F-292 contract, or any generator logic beyond FR-014's URI derivation. Everything the runs *discover* is filed, not fixed, under #295. *(US-1 scenario 6; US-2 scenario 7)*
- **FR-021**: T017 and T026 executions MUST be serialized (no concurrent tachi pipeline runs), and each story's live run is capped at two attempts before the M-1 escape hatch fires (file tooling defect; close on staged-partial record). *(US-1 scenario 7; edge cases)*

### Key Entities

- **Pre-292 anchor**: the git-history-pinned "before" state — `0629fa2~1` (= `3f107e3`), specifically its `examples/agentic-app/sample-report/threats.sarif` (authoritative; OI-1..OI-4) and `threats.md` (human cross-check). Immutable; read via `git show`.
- **OI-scoped subset**: the set of findings whose `partialFingerprints["findingId/v1"]` starts with `OI-`, extracted from a SARIF-shaped artifact by the corrected filter; carries per-finding {findingId, sink/flow identity} — the D-1 gate fields.
- **SC-003 verification record**: committed durable evidence for US-1 — commands, anchor SHAs, filter, extraction outputs, diff result, attribution table, gate verdict.
- **Committed evidence baseline**: the 5-artifact set at `examples/multi-tenant-rag-app/` root (4 LLM-authored + 1 script-generated), honoring the README pairing contract; the first committed example whose `threats.sarif` is script-tier by design.
- **Purpose-built regen check**: the US-3 test module + its CI wiring — the durable enforcement surface for SC-015 clause b.
- **Defect/enhancement Issues**: pre-decided dispositions — contract-§3 defect (dual defect, AC-1e/FR-008), gate-failure defects (FR-007/US-2 scenario 7), tooling-overflow defect (M-1), `generate-risk-scores-sarif.py` parameterization enhancement (FR-011).
- **Pre-state record**: `specs/295-f292-verification-runs/test-results/pre-state.md` — literal suite totals + corpus-coupling sweep, committed before artifacts land.

## Success Criteria *(mandatory)*

### Measurable Outcomes

All close gates are **endogenous** (execution + evidence + disposition — controllable by the maintainer); a discovered defect fails a *gate* but not the *feature*, which closes on the honest record (KB Entries 10, 17).

- **SC-001** (SC-003 closure): F-292-attributable OI-subset deltas on `agentic-app`: unknown → **0 or dispositioned** — verified with non-empty 4-findingId extractions on both sides and a committed verification record; T017 checkbox on #295 checked. (Ideal: byte-identical OI subsets; minimum: D-1 gate-field identity with full drift attribution; failure path: defect Issue + honest record.)
- **SC-002** (SC-015 clause a): committed Cat 6 evidence on `multi-tenant-rag-app`: 0 artifacts → complete 5-artifact set with ≥1 Cat 6 `output-integrity` finding present in committed `threats.md`/`threats.sarif`; T026 checkbox on #295 checked; README pairing contract satisfied.
- **SC-003** (SC-015 clause b, narrowed): `threats.sarif` regen byte-identity: unverified → verified at commit time, and CI-enforced by the purpose-built check if US-3 lands (US-3 deferral via AC-3c does not fail this criterion's first half).
- **SC-004** (initiative closure): Issue #295 both task checkboxes checked and the issue deliberately closed; BLP-06 Wave 3 work items complete (only the separately-deferred #325 tail remains in the initiative).
- **SC-005** (procedure repair): the false-pass hazard is retired — corrected extraction filter committed in the verification record and the contract-§3 defect Issue filed; no future consumer can reuse the broken procedure unwarned.

## Assumptions

- **Anchor stability**: `0629fa2~1` is pushed main history (no wasting-asset risk); extraction re-verified live 2026-07-03 → `OI-1..OI-4`.
- **SOURCE_DATE_EPOCH semantics (honest)**: the SARIF generators are timestamp-free — regen byte-identity is structural and needs no env pin; `SOURCE_DATE_EPOCH=1700000000` is set on pipeline runs for convention-uniformity only (ADR-021's mechanism applies to Typst/PDF, none of which is in scope).
- **Overflow knowledge staleness**: the orchestrator context-overflow constraint (and its Phase 5 locus) was last confirmed 2026-05-31; re-confirm empirically on the first run rather than assume.
- **Component count convention**: "7 components" per `examples/README.md:15` (the architecture file's 8th `###` entry is the external Anthropic LLM API); AC accuracy checks use the README convention.
- **Feasibility framing supersession**: the feasibility check's US-3 row ("7th `BASELINE_EXAMPLES` entry") is stale — PRD v1.2/Architect Option A replaced it with the purpose-built test; the 0.5/1.0/2.0 eng-day estimate carries over unchanged.
- **Single serial build wave**: security-analyst leads T017 → T026; tester owns US-3; no parallel tachi runs (Team-Lead wave plan).

## Scope

**In (P0)**: FR-001–FR-014, FR-019–FR-021 — T017 verification run + corrected-filter diff + committed record; T026 pipeline run + 5-artifact commit + regen verification + MAESTRO-shape gate; URI enabler + covering assertion; defect/enhancement filings (contract §3 dual-defect, gate failures, risk-scores generator gap).
**In (P1)**: FR-015–FR-018 — purpose-built SARIF-regen byte-identity test + CI wiring; README row accuracy check.
**Out** (per PRD, verified against code reality):

- `BASELINE_EXAMPLES` membership for `multi-tenant-rag-app` (PDF-suite false premise; F-142 all-`agentic_pattern: none` gate; mermaid-agentic-app skip precedent).
- `security-report.pdf.baseline` / infographic / report-assembly tier for the new example (Gemini dependency, non-deterministic image bytes).
- `risk-scores.sarif` regen verification / parameterizing `generate-risk-scores-sarif.py` (no CLI, hardcoded paths `:38-42`, ≥80-finding gate at `:535` — filed as enhancement).
- `maestro-reference` counter-test (contract §6 secondary fixture; 18 components — overflow territory; SC-003's letter names `agentic-app`).
- `compensating-controls` artifacts for the new baseline (requires a target codebase scan; the example ships an architecture description only).
- Any inline fix to detection-tier files, the archived contract, or discovered defects (fix-vs-file; FR-020).
- Backfilling or re-verifying `agentic-app` committed baseline artifacts (regenerated 2026-06-02 under F-098).

## Dependencies

- Git history access to `0629fa2~1` (verified) — read-only.
- `tachi-output-integrity` agent (Read/Glob/Grep, text-emission) and `tachi-orchestrator` pipeline availability in-session; `/tachi.risk-score` et al. for staged fallback.
- `scripts/generate-threats-sarif.py` + `scripts/populate-affected-assets.py` (deterministic tier).
- `jq` for extraction; `diff`/`git` for comparison; pytest for US-3.
- No external/network dependencies; no schema, agent-persona, or upstream-template changes.

## References

- PRD: `docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md` (v1.2; OQ-5 open → plan.md)
- Research: `specs/295-f292-verification-runs/research.md` (+ 4 track reports under `.aod/results/`)
- Feasibility: `specs/295-f292-verification-runs/feasibility-check.md` (0.5/1.0/2.0 eng-days; M-1/M-2 folded as FR-021/FR-018)
- Contract under test: `specs/292-output-integrity-cross-sink-refinement/contracts/cross-link-no-emission-contract.md` (§3 dual-defective — FR-008)
- Suite/code reality: `tests/scripts/test_backward_compatibility.py:45-52,375-412`; `.github/workflows/tachi-pytest.yml:73-110,181-197`; `.github/workflows/tachi-maestro-coverage.yml`; `scripts/generate-threats-sarif.py:481`; `examples/README.md:9,15`
- Governance: KB Entries 6, 7, 10, 15, 17, 19; ADR-021, ADR-037 D-14, ADR-039 D-6, ADR-046 D1; `.claude/rules/code-economy.md`
