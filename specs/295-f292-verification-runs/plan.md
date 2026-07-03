---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-03
    status: APPROVED
    notes: "All 21 FRs trace into named plan stages/decisions/contracts; US priorities + FR-018 gate preserved; OQ-5 resolved by D-A without eroding single-agent rationale; only product-code change stays FR-014; zero scope creep; timeline honors 0.5/1.0/2.0. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-07-03
    status: APPROVED
    notes: "M-a RESOLVED (D-A assembler + uniform corrected filter + envelope attribution class + scoped-full fallback); L-a RESOLVED (script-before vs script-after on same input). Load-bearing anchors independently verified. Post-review strengthening folded: sink-identity gate primary = logicalLocations[].name (structural) per review note. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-292 Post-Merge Verification Runs (T017 + T026)

**Branch**: `295-f292-verification-runs` | **Date**: 2026-07-03 | **Spec**: [spec.md](spec.md) (PM APPROVED 2026-07-03)
**Input**: Feature specification from `/specs/295-f292-verification-runs/spec.md`
**PRD**: `docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md` (v1.2) | **Issue**: #295 | **Draft PR**: #353

## Summary

Execute F-292's two deferred verification runs with fail-closed semantics and commit durable evidence: (US-1/T017) single-agent OI no-emission verification on `examples/agentic-app/` diffed against the git-history anchor `0629fa2~1` using the corrected `partialFingerprints` filter; (US-2/T026) full pipeline on `examples/multi-tenant-rag-app/` producing the committed 5-artifact Cat 6 evidence baseline with script-regenerable `threats.sarif`; (US-3, P1, gated on US-2) a purpose-built SARIF-regen byte-identity test wired into CI via a dedicated workflow. Everything the runs *discover* is filed as Issues (fix-vs-file); the only product-code change is the 1-line-class URI derivation in `generate-threats-sarif.py` (FR-014) plus its covering assertion and CI wiring.

All five plan-stage decisions (D-A…D-E) are recorded with rationale and alternatives in [research.md](research.md#plan-stage-decisions-phase-0--resolves-all-open-seams-no-needs-clarification-remain). **D-A resolves PRD OQ-5 / Architect M-a** (the one open question due at this stage). No NEEDS CLARIFICATION markers remain.

## Technical Context

**Language/Version**: Python 3.11+ (existing test/scripts toolchain); Bash (jq/git/diff); no new languages
**Primary Dependencies**: `jq`, `git show` (anchor access), `scripts/generate-threats-sarif.py` + `scripts/sarif_common.py` (importlib reuse), `scripts/populate-affected-assets.py` (pipeline step), pytest ≥8 + pytest-timeout (CI); in-session agents: `tachi-output-integrity` (Read/Glob/Grep, text-emission), `tachi-orchestrator` (fallback + T026), `/tachi.risk-score` (staged fallback)
**Storage**: git-committed artifacts only — `examples/multi-tenant-rag-app/` (5-file evidence baseline), `specs/295-f292-verification-runs/` (verification records, tools, pre-state), git history read-only at `0629fa2~1` (= `3f107e3`)
**Testing**: pytest (new US-3 module + FR-014 assertion in `test_affected_assets_wiring.py`); live-run ACs are `[MANUAL-ONLY]` (session-initiated LLM pipeline, not CI-repeatable)
**Target Platform**: local Claude Code session (runs) + GitHub Actions `ubuntu-latest` (US-3 workflow; OS-independent assertion)
**Project Type**: single (verification harness + evidence commits inside the existing repo layout)
**Performance Goals**: N/A product-runtime; US-3 CI job target < 1 min wall-clock (sub-second assertion + setup)
**Constraints**: serial execution T017 → T026 (shared orchestrator context; FR-021); ≤2 live-run attempts per story then M-1 escape hatch; fail-closed gates (empty extraction = ERROR); no detection-tier edits (FR-020); output dirs must be non-gitignored-aware (default `docs/security/` and `examples/*/test-output/` are gitignored — D-D)
**Scale/Scope**: 2 live runs, 1 assembler tool (specs-scoped), 1 generator line-class change + 1 assertion, 1 test module + 1 workflow, 5 committed artifacts, 2 verification records, 1 pre-state record, 3–4 filed Issues

## Constitution Check

*GATE: evaluated pre-Phase-0; re-checked post-Phase-1 — PASS (no violations; Complexity Tracking empty).*

| Principle | Verdict | Note |
|---|---|---|
| I–V (platform generics) | N/A / PASS | No API/UI/storage/concurrency surface; local-first workflow untouched (III: all artifacts are local files in-repo) |
| VI Testing Excellence | PASS | US-3 purpose-built test + FR-014 covering assertion; live-run ACs `[MANUAL-ONLY]` with recorded evidence (KB Entry 4 precedent: validation = the runs themselves, rationale in records); pre-state totals per KB Entry 15 |
| VII Definition of Done | PASS | Endogenous close gates (SC-001–SC-005); DoD 3-step maps to: evidence committed + suites green + #295 checkboxes/record linked |
| VIII Observability/RCA | PASS | Verification records carry commands, SHAs, outputs, attribution tables — replayable procedure supersedes the broken contract §3 |
| IX Git Workflow | PASS | Feature branch `295-*`, draft PR #353 open, conventional title `feat(295):` already set |
| X Product-Spec Alignment | PASS | PRD v1.2 → spec (PM APPROVED) → this plan; OQ-5 resolved here as designated; fix-vs-file boundary preserved |
| XI Triad Collaboration | PASS | PM+Architect dual review this stage; Team-Lead wave plan (serial, 2-agent roster) honored in Execution Design |

## Project Structure

### Documentation (this feature)

```
specs/295-f292-verification-runs/
├── plan.md                      # This file
├── research.md                  # Research + Phase-0 decisions D-A…D-E
├── spec.md                      # Approved spec
├── feasibility-check.md         # Team-Lead estimate (0.5/1.0/2.0)
├── data-model.md                # Phase-1: entities & gate-field model
├── quickstart.md                # Phase-1: execution runbook (3 stories)
├── contracts/
│   ├── oi-extraction-contract.md        # Corrected filter, false-pass guard, D-1 gate semantics
│   └── regen-byte-identity-contract.md  # US-3 test + CI wiring contract
├── checklists/requirements.md   # Spec quality checklist (all-pass)
├── tools/                       # (build) T017 assembler — verification tooling, NOT product code
├── test-results/                # (build) pre-state.md; T026 run provenance
└── tasks.md                     # /aod.tasks output (next stage)
```

### Source Code (repository root — touched surfaces only)

```
scripts/
└── generate-threats-sarif.py    # FR-014 ONLY: derive artifactLocation.uri from input path (build_result(), :481)

tests/scripts/
├── test_affected_assets_wiring.py   # +FR-014 covering assertion (existing gated module; D-C)
└── test_sarif_regen_identity.py     # NEW (US-3, P1): byte-identity multi-tenant-rag-app regen (D-B)

.github/workflows/
├── tachi-pytest.yml             # +scripts/generate-threats-sarif.py in &hardening_paths (D-C, lock-step)
└── tachi-sarif-regen.yml        # NEW (US-3, P1): dedicated single-runner workflow (D-B)

examples/multi-tenant-rag-app/
├── architecture.md              # existing (untouched)
├── threats.md                   # NEW committed (LLM-authored run byproduct)
├── threat-report.md             # NEW committed (LLM-authored)
├── risk-scores.md               # NEW committed (LLM-authored)
├── risk-scores.sarif            # NEW committed (LLM-authored; NO regen claim)
└── threats.sarif                # NEW committed (script-generated from threats.md)

examples/README.md               # row accuracy check only (FR-013; edit only if evidence contradicts)
```

**Structure Decision**: no new source directories; verification tooling is specs-scoped (`specs/295-*/tools/`) to keep `scripts/` product-tier clean (ADR-046 tier boundary). Committed baseline uses root-level layout (D-D; README pairing contract, `maestro-reference` precedent).

## Plan Decisions (architect-owned; full rationale + alternatives in research.md Phase-0)

| ID | Decision | Resolves |
|---|---|---|
| **D-A** | T017 comparison SARIF = **assembler step over single-agent findings** (specs-scoped tool reusing `sarif_common.build_sarif_envelope` / `build_result` via importlib; raw YAML committed verbatim; corrected filter applies uniformly to both sides; "assembler-tier envelope" = standing attribution class). Scoped-full run (Phase 5 skipped) stays the fallback, its native SARIF feeding the same filter. Sink/flow identity compared as **identifiers** (components + quoted flow names) via a per-finding table in the record; message prose stays drift-bucket. | PRD OQ-5 / Architect M-a; spec FR-002 |
| **D-B** | US-3 CI wiring = **dedicated workflow** `tachi-sarif-regen.yml` (catalog-drift pattern: single ubuntu-latest, `contents: read`, PR+push:[main] via one paths anchor). No ADR needed: derivative of ADR-039 D-6 + #329/#183 dedicated-workflow precedents (test-tree + CI-infra only; no schema/agent surface). | spec FR-016 mechanism |
| **D-C** | FR-014 covering assertion → **existing** `test_affected_assets_wiring.py` (P0, already CI-gated, already importlib-loads the generator) + add `scripts/generate-threats-sarif.py` to `&hardening_paths` same-commit (lock-step). Keeps P0 assertion independent of US-3's P1 fate. | spec FR-014/FR-016 seam |
| **D-D** | T026 run → `--output-dir examples/multi-tenant-rag-app/test-output/` (gitignored, conventional); copy 4 LLM-authored artifacts to example root; script-generate `threats.sarif` 5th; commit exactly 5. Provenance in record; attack-trees/chains uncommitted (AC-2b exact set). | spec FR-009/FR-010 |
| **D-E** | Pre-state set = `test_backward_compatibility.py` + maestro pair + `test_catalog_drift_guard.py` + `test_affected_assets_wiring.py` + corpus-glob/count-pin sweep → `test-results/pre-state.md` BEFORE any artifact/enabler commit. | spec FR-019 |

## Execution Design (single serial wave — Team-Lead plan honored)

### Stage 0 — Pre-state (FR-019, blocks everything)
Run D-E suite set locally, record literal pass/skip/fail totals + the corpus-coupling sweep; commit `test-results/pre-state.md`. Inherited reds → disposition (fix-vs-file) before proceeding.

### Stage 1 — T017 / US-1 (owner: security-analyst)
1. **Anchor extraction** (deterministic): `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif` → corrected jq filter → `anchor-oi-subset.json`. Guard: non-empty, cardinality 4 (`OI-1..OI-4`, pre-verified 2026-07-03). Empty/≠4 ⇒ gate ERROR, stop.
2. **Fresh run** (primary): dispatch `tachi-output-integrity` single-agent with the orchestrator's own context payload shape (component set + full `examples/agentic-app/architecture.md` + OI analysis scope); persist raw YAML findings verbatim. Attempt cap 2 (then M-1: file tooling defect, close on staged-partial record). Fallback (attempt 2): scoped-full run, Phase 5 skipped (`report: false`), native `threats.sarif`.
3. **Assemble + extract** (D-A): assembler → `fresh-oi.sarif` → same jq filter → `fresh-oi-subset.json`. Guard: non-empty (expected 4).
4. **D-1 gate**: count + findingId set (jq-deterministic) + sink/flow identity table (identifier-level, both sides' verbatim text committed). Identical ⇒ PASS. Any gate-field delta ⇒ FAIL ⇒ defect Issue w/ evidence (FR-007). Non-gate byte deltas ⇒ attribution table (3 named benign classes + assembler-envelope class); unattributable ⇒ FAIL.
5. **Record + filings**: commit `sc-003-verification-record.md` (commands, SHAs, filter, subsets, diff, attribution, verdict); file contract-§3 dual-defect Issue (FR-008); link record from #295; check T017 box.

### Stage 2 — T026 / US-2 (owner: security-analyst; starts only after Stage 1 concludes)
1. **Run** (D-D): `tachi.threat-model examples/multi-tenant-rag-app/architecture.md --output-dir examples/multi-tenant-rag-app/test-output/` with `SOURCE_DATE_EPOCH=1700000000` (convention-uniformity; SARIF determinism is structural). Phase 5 ON (`threat-report.md` required). Populator step confirmed in provenance. Attempt cap 2; overflow fallback = staged per-skill (`/tachi.risk-score` etc. — threats.md/threats.sarif land pre-overflow per KB memory).
2. **Cat 6 gate**: ≥1 `OI-*` finding on the Cat 6 surface (CWE-943 primary; Pinecone `tenant_id`-omission shape per `architecture.md:92`). Zero ⇒ FAIL ⇒ defect Issue; artifacts NOT committed; US-3 defers (FR-018); #295 records honestly.
3. **URI enabler first** (FR-014/D-C, independent commit): derive `artifactLocation.uri` from input path in `build_result()`; covering assertion in `test_affected_assets_wiring.py`; `&hardening_paths` addition; **agentic-app byte-unchanged proof = script-output-before vs script-output-after** (Architect L-a semantics), committed in the record.
4. **Commit baseline**: copy 4 LLM-authored artifacts to root; regen `threats.sarif` via corrected generator; verify regen byte-identity locally (FR-011); MAESTRO all-7-row shape check (FR-012 — maestro-coverage workflow will fire on the PR); README row accuracy (FR-013). Commit exactly 5 + T026 record. File `generate-risk-scores-sarif.py` parameterization enhancement Issue.

### Stage 3 — US-3 / P1 (owner: tester; gated on Stage 2 regen success per FR-018)
1. New `test_sarif_regen_identity.py`: importlib-load generator, regen from committed `threats.md`, `read_bytes()` equality vs committed `threats.sarif`; fail-closed (missing file/empty parse ⇒ FAIL, never skip).
2. New `tachi-sarif-regen.yml` (D-B) with the 6-path anchor + invocation, lock-step one commit.
3. PR-body coverage-boundary statement (FR-017).

## Verification Data Flow

```
T017: git-history anchor ──git show──► anchor SARIF ──jq(corrected)──► anchor OI subset ─┐
      agentic-app arch ──single-agent──► YAML findings ──assembler──► fresh-oi.sarif ──jq──► fresh OI subset ─┤
                                                                                          D-1 gate + attribution ──► SC-003 record + filings
T026: rag-app arch ──full pipeline──► run dir (gitignored) ──copy 4──► example root ──generator──► threats.sarif (5th)
                                                                     └──regen check (FR-011) ──► T026 record + baseline commit
US-3: committed pair ──pytest module──► byte-identity assertion ──dedicated workflow──► CI-enforced (paths lock-step)
```

## Toolchain & Dependencies

Existing only: Python 3.11+/pytest, jq, git, `sarif_common.py`/`generate-threats-sarif.py` (importlib), populate-affected-assets.py, in-session tachi agents/skills, gh CLI (Issues/PR). **No new dependencies, no schema changes, no detection-tier edits, no ADR required** (D-B note; FR-014 is a behavior-preserving line-class change with covering assertion — ADR-039 promotion rule not triggered).

## Risks & Mitigations (delta over PRD R-1…R-6)

| Risk | Plan-level mitigation |
|---|---|
| R-2 false-pass | Corrected filter + cardinality-4 pin both sides + fail-closed ERROR on empty (Stage 1.1/1.3 guards) |
| R-3 overflow | Primary path = no orchestrator at all; T026 small arch + Phase-5-after-artifacts locus + staged fallback; attempt cap 2 + M-1 hatch (FR-021) |
| R-4 LLM nondeterminism | Gate on identifiers, not prose (D-A identity-table semantics); byte-identity claimed only on script tier (FR-011/US-3) |
| R-1 drift misattribution | 3 named benign classes + assembler-envelope class; unattributable ⇒ FAIL (fail-closed) |
| R-6 scope creep at generator seam | FR-020 fence; only FR-014 touches product code; risk-scores gap filed as enhancement Issue |
| NEW: assembler correctness | Assembler is specs-scoped, reuses production envelope/result builders via importlib, output committed + human-checkable against raw YAML (both in record) |
| NEW: US-3 workflow false-green | Lock-step anchor includes both example artifacts + generator + sarif_common + test + workflow file; fail-closed test semantics |

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*

## Phase 1 Artifacts

- [data-model.md](data-model.md) — entities, gate-field model, state transitions
- [contracts/oi-extraction-contract.md](contracts/oi-extraction-contract.md) — the corrected, working SC-003 procedure (supersedes 292 contract §3 for execution; the archived contract itself gets the FR-008 defect Issue, not an edit)
- [contracts/regen-byte-identity-contract.md](contracts/regen-byte-identity-contract.md) — US-3 test + wiring contract
- [quickstart.md](quickstart.md) — execution runbook (stages 0–3, commands, guards)
