---
prd_reference: docs/product/02_PRD/329-ordered-frameworks-ci-guard-2026-06-30.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-30
    status: APPROVED
    notes: "Faithful, complete, disciplined translation of approved PRD v1.1. FR-1..8→FR-001..008, NFR-1..4→NFR-001..004, US-1..4→US-1..4, and all 7 PRD success criteria map 1:1; spec SC-008 is a justified promotion of the T001 milestone gate into a measurable [MANUAL-ONLY] criterion (deliberate 7→8 split, NOT scope creep). The (b)-over-(a) evaluation fork is carried as a settled decision, not re-litigated. All 6 PRD out-of-scope exclusions preserved; the init.sh-xfail (OQ-6) deferral PM-verified against live source (test_init_sh_substitution.py:35/:54, strict=False, 'Tracked for fixture regen under #329' — confirmed orthogonal init.sh surface, correctly out of scope). The three plan-stage OQs (OQ-1 sidecar mechanism, OQ-3 T001, OQ-6 xfail) carried forward verbatim with correct owners/recommendations; resolved OQ-2/4/5 correctly baked in. 0 blockers, 0 critical, 0 warnings, no changes requested. 2 LOW advisories (plan-stage, no spec change): (1) /aod.analyze may flag the 7→8 SC delta — it is the deliberate T001-promotion split, not drift; (2) the plan should make the T001 go/no-go branch explicit so team-lead can size the baseline-remediation tail if main is found red (git evidence: Low likelihood). Full: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: ORDERED_FRAMEWORKS Catalog-Drift CI Guard

**Feature Branch**: `329-ordered-frameworks-ci-guard`
**Created**: 2026-06-30
**Status**: Draft
**Input**: PRD 329 — `docs/product/02_PRD/329-ordered-frameworks-ci-guard-2026-06-30.md` (BLP-06 Wave 2, CI-hardening-tail lead, P1)

## Summary

The 6-PDF byte-identity suite (`tests/scripts/test_backward_compatibility.py`) byte-compares committed Coverage-Attestation (CA) page baselines, but it is **local-only — wired into no CI workflow**. So when a member of `ORDERED_FRAMEWORKS` (`owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`) changes its render-coupled record set without the 6 CA baselines being regenerated, the suite goes **silently red on `main`** with no signal. This already happened (F-186 grew ATLAS 30→36 without regen; discovered weeks later at F-185's plan review — KB Entry 15/13).

This feature adds a fast, **environment-independent** CI guard that recomputes each member's render-coupled **fingerprint** (the ordered list of in-scope `(id, out_of_scope)` records) and fails the build when it diverges from the fingerprint the baselines were last regenerated against — recorded in a **sidecar emitted by the CA-baseline regeneration process itself**. The guard renders nothing, hits no network, runs sub-second, and reuses the renderer's own record loader so its notion of "what the CA page depends on" is identical to the renderer's by construction.

**Evaluation fork (both reviewers ratified):** ship **(b)** the lightweight fingerprint guard; **defer (a)** wiring the full byte-identity suite into CI (cross-environment Typst byte-determinism makes (a) a flaky gate). This spec specifies (b).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch drift-without-regen at PR time (Priority: P1)

As a **Taxonomy Steward / catalog-growth feature author** (the #184/#185/#186 pattern), when I open a PR that changes an `ORDERED_FRAMEWORKS` member's render-coupled content — adds/removes/renames a record, or flips `out_of_scope` — but I forget to regenerate the 6 CA baselines, I want CI to fail fast with a clear message pointing me to the regeneration entry point, so I can fix it before merge instead of leaving `main` silently red for a sibling feature to discover weeks later (the F-186 → F-185 path).

**Why this priority**: This is the MVP. It directly closes the recurring failure *class* KB Entry 15 named. A guard that catches the drift at PR time — and nothing else — already delivers the core value.

**Independent Test**: Fully testable in isolation via a synthetic fixture: mutate a member's in-scope record set without updating the sidecar, run the guard, observe a non-zero exit naming the framework. No CI, no rendering, no other story required.

**Acceptance Scenarios**:

1. **Given** a member whose live in-scope `(id, out_of_scope)` fingerprint differs from its sidecar-recorded fingerprint (a record added/removed), **When** the guard runs, **Then** it exits non-zero and names the offending framework with expected-vs-actual (including the human-readable count summary) and the regeneration entry point.
2. **Given** a member edited so a record's `id` is renamed/swapped at **constant record count**, **When** the guard runs, **Then** it fails (the fingerprint, not a bare count, detects the change — HIGH-2).
3. **Given** a member edited so one record's `out_of_scope` flag flips at **constant raw count**, **When** the guard runs, **Then** it fails (the in-scope partition changed — HIGH-3).
4. **Given** a clean tree where every member's live fingerprint equals its sidecar fingerprint, **When** the guard runs, **Then** it exits zero (pass).

### User Story 2 - Don't false-red on count-neutral edits (Priority: P1)

As a **maintainer shipping count-neutral data fixes** (e.g., the #333 citation-URL string fixes to `mitre-atlas.yaml` / `nist-ai-rmf.yaml`), when I edit a member catalog in a way that does **not** change its in-scope ID set, I want the guard to stay green, so I can ship those fixes without a spurious "regenerate baselines" demand — because those edits do not change the rendered CA pages.

**Why this priority**: Co-critical with US-1, not optional. A guard that false-reds is **worse than no guard** (NFR-1): it trains reviewers to ignore it. The fingerprint design must deliver both faces — catch real drift *and* stay green on count-neutral edits — or it fails its purpose.

**Independent Test**: Testable in isolation by applying a citation-string-only edit (real #333 change shape) to a member fixture, leaving the `(id, out_of_scope)` set untouched, and observing the guard pass.

**Acceptance Scenarios**:

1. **Given** a member-catalog edit that changes only non-fingerprint fields (citation strings, descriptions) and leaves every member's in-scope `(id, out_of_scope)` fingerprint unchanged, **When** the guard runs, **Then** it exits zero (the #333 class — Architect-verified `mitre-atlas` 36→36, `nist-ai-rmf` 72→72 required no regen).
2. **Given** a change to a taxonomy catalog that is **not** an `ORDERED_FRAMEWORKS` member (e.g., `nist-ai-600-1.yaml`), **When** the guard runs, **Then** it exits zero (only members are CA-coupled).

### User Story 3 - Guard the trunk, not just PRs (Priority: P2)

As a **maintainer who relies on `main` being green**, when a catalog-edit change reaches `main` via a direct push rather than a PR, I want the guard to fire on `push: branches:[main]` as well, so a stale-baseline state cannot live invisibly on the trunk (the #338 direct-to-main lesson, reused).

**Why this priority**: Important hardening, but secondary to the guard logic existing at all. The PR trigger covers the dominant path; the push trigger closes the direct-to-main bypass that silently reverted hardening once before (KB Entry 18).

**Independent Test**: Testable by inspecting the workflow trigger block — both `pull_request` and `push: branches:[main]` present, sharing one path-filter list via a YAML anchor — independent of the guard's internal logic.

**Acceptance Scenarios**:

1. **Given** a direct push to `main` that drifts a member fingerprint without regen, **When** the `push` trigger fires, **Then** the workflow fails on `main`.
2. **Given** the workflow definition, **When** its triggers are inspected, **Then** `pull_request` and `push: branches:[main]` resolve the **same** path-filter list (single-source anchor — no PR/push drift).

### User Story 4 - Future member coverage is automatic (Priority: P3)

As a **future catalog author**, when a new framework is added to the `ORDERED_FRAMEWORKS` tuple, I want the guard to cover it without any guard-code change, so a second silent-gap class cannot open for the new member.

**Why this priority**: Forward-looking robustness. No member is being added now, but a hardcoded list of 5 would silently miss a 6th. Cheap to satisfy (iterate the tuple); valuable insurance.

**Independent Test**: Testable by adding a synthetic 6th entry to a stubbed framework tuple in a fixture and confirming the guard fingerprints it with no code edit.

**Acceptance Scenarios**:

1. **Given** the guard derives its target set from `ORDERED_FRAMEWORKS` at runtime, **When** a 6th member is added to the tuple, **Then** the guard fingerprints it automatically (no hardcoded list of 5).

### Edge Cases

- **Missing / partial / unparseable sidecar** → the guard MUST **fail closed** (treat as drift), never pass — so deleting or truncating the sidecar cannot silence it (Risk-5 / FR-008).
- **`main` already red at T001** → the pre-state gate finds it; a bounded baseline remediation precedes the guard going green (git evidence says Low likelihood — F-185 left it green, only count-neutral member edits since). [MANUAL-ONLY] T001 is a local human-run rendering check; rendering is disallowed in CI.
- **`lru_cache` stale-read in the synthetic test** → each test case MUST clear the loader cache (`cache_clear()`) or monkeypatch the count functions, or a case can read stale records and pass for the wrong reason — a **false-green** (Risk-3 / FR-007).
- **Regen-only commit** (sidecar + baselines change, catalog unchanged) → the path filter MUST include the sidecar and the regen script so the guard re-runs and confirms agreement.
- **Two members drift in one change** → the failure message names **all** offending frameworks, not just the first.

## Requirements *(mandatory)*

### Functional Requirements

> Acceptance criteria for these FRs are exercised by the synthetic unit test (FR-007) and the workflow definition (FR-005); the Given/When/Then forms appear in the user stories above. Each FR below is independently testable.

- **FR-001 (Render-coupled fingerprint)**: The guard MUST compute, per `ORDERED_FRAMEWORKS` member, a deterministic fingerprint of the **ordered list of in-scope `(id, out_of_scope)` records**, derived by **reusing** `_load_framework_yaml_records` (`scripts/extract-report-data.py:1090`, which already exposes `in_scope_only`) — the same loader behind the CA-page RAW denominator (`:1140`) and IN-SCOPE denominator (`:1155`). The fingerprint MUST capture both the raw record set and the in-scope partition, so it detects add/remove (count delta), ID rename/swap at constant count, and `out_of_scope` flips at constant count. The bare per-framework count is retained **only** for the human-readable failure summary. The guard MUST NOT re-implement the YAML walk.

- **FR-002 (Sidecar emitted by a real CA-baseline regen process — cheat-resistant)**: The expected fingerprints the guard compares against MUST be produced **by the CA-baseline regeneration process**, so a stale sidecar ≡ stale baselines. Because **no executable CA-baseline regen exists today** (`tests/fixtures/regenerate-baseline.sh` regenerates the unrelated F-248 init.sh fixture; the real CA regen is the manual recipe in `baseline-regen.contract.md`), this feature MUST **promote that recipe to a thin executable regen script** that loops the 6 `BASELINE_EXAMPLES`, runs the documented `extract-report-data.py … && typst compile …` sequence with `SOURCE_DATE_EPOCH=1700000000` and the `git checkout -- …/report-data.typ` cleanup, and **writes the sidecar as its final step**. *(The precise sidecar emission mechanism — regen-script byproduct vs. hand-maintained manifest fallback — is **OQ-1**, Architect-owned at /aod.plan. The manifest fallback forfeits the Risk-1 cheat-resistance; if chosen, the trade MUST be flagged.)*

- **FR-003 (Fingerprint-based, never file-diff)**: The guard MUST key on the fingerprint (FR-001), not on "did the member YAML file change." A file-diff approach would false-red on count-neutral edits — concretely #333's citation-string fixes correctly required no regen. The guard MUST pass for any edit that leaves the in-scope `(id, out_of_scope)` fingerprint unchanged.

- **FR-004 (Dynamic member coverage)**: The guard MUST derive its target set from `ORDERED_FRAMEWORKS` at runtime, so adding a future member extends coverage with zero guard-code change. No hardcoded list of 5.

- **FR-005 (CI workflow — dedicated, path-filtered, dual-trigger, single-runner, least-privilege)**: A **new dedicated** workflow `.github/workflows/tachi-catalog-drift.yml` (NOT a job in `tachi-pytest.yml`, whose macOS/ubuntu matrix is irrelevant here) MUST:
  - Fire on **`pull_request`** AND **`push: branches:[main]`**, both resolving a **single-source path-filter list** via a YAML `&anchor`/`*anchor` (the `tachi-pytest.yml` lock-step pattern — no PR/push drift).
  - Path-filter, in lock-step with the check invocation, to every surface that can change a fingerprint or its sidecar: `schemas/taxonomy/*.yaml`, the 6 `examples/*/security-report.pdf.baseline` files, the sidecar file, the new regen script + `baseline-regen.contract.md`, and the guard script / test / workflow themselves.
  - Run on a **single `ubuntu-latest`** runner (load-bearing for NFR-001 — a matrix would imply platform-varying results), with `permissions: contents: read`.
  - Structurally follow `tachi-maestro-coverage.yml` (single-runner, `contents: read`, path-filtered) plus the `tachi-pytest.yml` dual-trigger anchor.

- **FR-006 (Self-evident failure message)**: On drift, the guard MUST emit a message naming the offending framework(s), the expected-vs-actual fingerprint (with the human-readable count summary), and the remediation entry point (the new regen script / `baseline-regen.contract.md` / ADR-037 D-9 lane).

- **FR-007 (Synthetic-only test, cache-cleared)**: The guard's correctness MUST be proven by a synthetic unit test (manipulating records/sidecar in a tmp fixture), never by rendering real PDFs in the test or CI path. The test MUST cover: (a) add/remove grow → fail; (b) constant-count ID swap/rename → fail; (c) `out_of_scope` flip → fail; (d) citation-string-only / #333 class → pass; (e) non-member catalog change → pass; (f) clean tree → pass. **Each case MUST call `_load_framework_yaml_records.cache_clear()`** (the loader is `@functools.lru_cache`, `:1089`) or monkeypatch the count functions — to avoid a stale-cache false-green.

- **FR-008 (Fail closed on missing/partial sidecar)**: The guard MUST treat a missing, partial, or unparseable sidecar as a **failure**, never a pass.

### Non-Functional Requirements

- **NFR-001 (Determinism / zero false-reds — load-bearing)**: The guard's result MUST depend only on the YAML in-scope record fingerprints and the committed sidecar — never on Typst version, fonts, platform, or wall-clock. Zero rendering, zero network in the guard path. This is the single property that justifies (b) over (a). Determinism is stated honestly as *given a pinned `pyyaml`* (the guard inherits pyyaml parse semantics) — already a CI dependency.
- **NFR-002 (Speed)**: The guard MUST complete well under the `tachi-pytest.yml` matrix time; the fingerprint comparison is sub-second, with job time dominated by checkout + Python setup.
- **NFR-003 (No new runtime dependency)**: Implementation MUST use the standard library plus already-present `pyyaml`. No new package in any manifest.
- **NFR-004 (Scope discipline / write-set disjointness)**: The feature MUST NOT modify `ORDERED_FRAMEWORKS` membership, CA-page rendering logic, or any of the 6 baselines (unless T001 finds `main` already red). Its write-set is the new regen script, the guard script, its test, the new sidecar artifact, the new workflow, the ADR-037 amendment, and docs/CHANGELOG.

### Key Entities

- **`ORDERED_FRAMEWORKS` member catalog** — one of 5 taxonomy YAML files (`schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml`) whose in-scope record set is rendered onto every report's CA pages. The guarded population.
- **Render-coupled fingerprint** — a deterministic digest of a member's **ordered in-scope `(id, out_of_scope)` records** (plus the raw record set). The unit of comparison. Strict superset of the bare count.
- **Sidecar** — a new committed artifact recording the expected per-member fingerprints, **written by the regen script as its last step**. Stale sidecar ≡ stale baselines. The guard's source of truth for "what the baselines were last regenerated against."
- **CA-page baselines** — the 6 committed `examples/*/security-report.pdf.baseline` PDFs the byte-identity suite compares. Not modified by this feature (NFR-004) except under the T001-red contingency.
- **CA-baseline regen script** (new, e.g. `scripts/regenerate-ca-baselines.sh`) — the formalization of the manual `baseline-regen.contract.md` recipe; the single canonical place CA baselines are produced and the sidecar is emitted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CI fails the build when any `ORDERED_FRAMEWORKS` member's render-coupled fingerprint diverges from its sidecar — covering the F-186 grow, the constant-count ID swap/rename (HIGH-2), and the `out_of_scope` flip (HIGH-3). *(Baseline today: No — suite is local-only.)*
- **SC-002**: The guard runs on **both** `pull_request` and `push: branches:[main]`; a direct-to-main catalog edit without regen reddens CI.
- **SC-003**: The guard is environment-independent — no Typst, no PDF rendering, no cross-runner byte-determinism dependency → **zero false reds** from rendering nondeterminism (target rate: 0).
- **SC-004**: A synthetic unit test proves the guard **catches** fingerprint drift (grow / ID-swap / `out_of_scope`-flip without regen) and **ignores** a citation-string-only edit (#333 class) and a non-member catalog change — each case clearing the `lru_cache`. All 6 cases pass.
- **SC-005**: The guard's failure message names the offending framework(s), shows expected-vs-actual (with count summary), and points to the regen entry point — fix path self-evident from the message alone.
- **SC-006**: No new runtime dependency is added to any manifest; the no-network / no-rendering determinism boundary is preserved (consistent with #183/#333 CI discipline).
- **SC-007**: KB Entry 15's define-time "grep `ORDERED_FRAMEWORKS`" human checklist gains an automated CI backstop — a future author who forgets the checklist is still caught.
- **SC-008**: T001 pre-state confirms `test_backward_compatibility.py` is green on `main` before the guard goes green (or a bounded remediation precedes it). [MANUAL-ONLY] local rendering check, disallowed in CI.

## Scope

### In Scope (P0)

- The catalog-fingerprint drift guard (option **b**): reuse `_load_framework_yaml_records` (raw + in-scope), iterate `ORDERED_FRAMEWORKS` dynamically, fail-closed on missing sidecar.
- Promotion of the manual CA-baseline regen recipe to an **executable regen script** that emits the sidecar as a byproduct (FR-002 — the load-bearing deliverable).
- A new dedicated, path-filtered CI workflow firing on PR + push:[main], single `ubuntu-latest`, `contents: read`.
- Synthetic unit test (grow / ID-swap / `out_of_scope`-flip → fail; #333 / non-member / clean → pass; cache-cleared).
- Self-evident failure message → regen entry point.
- T001 pre-state check (front-loaded) that the byte-identity suite is currently green on `main`.
- ADR-037 amendment (OQ-5) + docs note (KB-15 checklist now CI-backstopped) + CHANGELOG.

### Out of Scope

- **Option (a): wiring the full byte-identity suite into CI** — evaluated and **deferred** (Architect-ratified) for the cross-environment PDF-determinism risk (NFR-001). Documented as the rejected-as-primary alternative in the ADR-037 amendment; may be revisited only if (b) proves insufficient.
- **The init.sh-substitution baseline (`tests/fixtures/init-baseline-tree/`) and its `#329`-tagged xfail** (`test_init_sh_substitution.py:35` marker, function at `:54`, `strict=False`) — a **different baseline surface** (the F-248/F-256 init.sh fixture), unrelated to the CA-PDF baselines this feature guards. **Decision: out of scope; re-tag / track separately (OQ-6).** Folding it would scope-creep across an orthogonal surface.
- Changing `ORDERED_FRAMEWORKS` membership or CA-page rendering logic.
- Regenerating the current CA baselines (unless T001 finds `main` red → bounded remediation precedes the guard going green).
- The broader ~19 documented out-of-gate pytest failures.
- A general-purpose "every taxonomy file is rendered-consistent" checker (YAGNI — only the `ORDERED_FRAMEWORKS` fingerprint↔baseline coupling is required).

### Assumptions

- `main` is currently **green** on `test_backward_compatibility.py` (F-185's regen absorbed #186's ATLAS delta; #333's later edits were count-neutral). **Validated at T001.**
- After FR-002, the new regen script is the single canonical place CA baselines are produced, so emitting the sidecar there covers all regen routes (FR-008 fails closed otherwise).

### Constraints

- Determinism boundary: no network, no PDF rendering in the guard / CI path (NFR-001). Rendering is allowed only in the local T001 pre-state and the local regen script.
- Reuse-first (code-economy): the record loader already exists (`:1090`) — the guard wraps it; the regen recipe already exists — the script formalizes it. Neither is re-implemented from scratch.

### Dependencies

- **Internal**: `scripts/extract-report-data.py` (`_load_framework_yaml_records`, the two count functions, `ORDERED_FRAMEWORKS`); the manual regen recipe `baseline-regen.contract.md` (promoted to a script, FR-002); the 6 `examples/*/security-report.pdf.baseline` files; `tachi-maestro-coverage.yml` + `tachi-pytest.yml` (pattern references, not modified); local Typst (0.14.2 installed) for T001 + the regen script only.
- **External**: none (no new dependency; GitHub Actions only).

### Plan-Stage Open Questions (carried from PRD)

- **OQ-1** (Architect, load-bearing): confirm sidecar mechanism = "emitted as the last step of the newly-formalized executable CA-baseline regen script" (recommended, cheat-resistant) vs. a hand-maintained manifest fallback. Resolves FR-002 + Risk-1 + Assumption 2.
- **OQ-3** (Build, T001): is `test_backward_compatibility.py` green on `main` right now? (Record literal pre-state totals per KB-15.)
- **OQ-6** (PM/Build): disposition the `#329`-tagged init.sh-substitution xfail — recommend re-tag / track separately (out of scope here).
