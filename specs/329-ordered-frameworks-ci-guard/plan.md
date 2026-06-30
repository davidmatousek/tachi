---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-30
    status: APPROVED
    notes: "Faithful, scope-disciplined translation of the PM-approved spec with zero drift. All 8 FRs, 4 NFRs, 8 SCs, and 4 user stories map 1:1 to the build surface (5 named components + sidecar contract). The (b)-over-(a) fork is carried as settled — not re-litigated, not silently reversed (entire guard path renders nothing; (a)-deferral routed to the ADR-037 amendment). NFR-004 write-set disjointness honored via an explicit READ-ONLY/NAMED-UNTOUCHED block; the only mutating exception is the spec-authorized T001-red contingency. Both spec-PM LOW advisories honored: 7→8 SC count is the deliberate T001 milestone-gate promotion (not creep), and the T001 go/no-go branch is explicit in three places (OQ-3 resolution, build-sequence step 1, Risk R4). OQ-6 init.sh xfail correctly OUT of scope (re-tag follow-up). All load-bearing claims re-verified @ 644b532. 0 blockers, 0 critical, 0 warnings; 3 non-blocking doc-consistency LOWs (xfail line-cite reconciled to :35 marker; regen loop ordering immaterial to per-framework fingerprints; SC 7→8 is the deliberate T001 promotion — /aod.analyze may note it). Full: .aod/results/product-manager-plan.md"
  architect_signoff:
    agent: architect
    date: 2026-06-30
    status: APPROVED_WITH_CONCERNS
    notes: "OQ-1 RATIFIED. Sidecar-as-regen-byproduct is the correct golden-master approval-script pattern: the only writer is the regen script that re-renders the baselines, so expected fingerprints cannot be advanced without a real regen (Risk-1 structurally closed); hand-maintained-manifest rejection correct. Fingerprint algorithm verified against live loader semantics (extract-report-data.py:1089-1137) — catches the F-186 grow, HIGH-2 constant-count ID-swap, HIGH-3 out_of_scope-flip (both partitions), and passes the #333 count-neutral case (canonical() projects to [id, out_of_scope] only). Order-preserved-never-sorted backed by the loader's list(data). Loader reuse via importlib over the hyphenated module right; workflow composite (maestro skeleton + pytest dual-trigger anchor) faithfully sourced — maestro confirmed PR-only, so the anchor IS needed for push:[main]. Determinism boundary held (no leak); cache_clear()-per-case defends the lru_cache false-green; data-model→contract fold acceptable code-economy. All claims verified @ HEAD 014eebe. 2 non-blocking WARNINGs, both FOLDED before sign-off: C-1 (use a NEW ADR-037 decision D-14 + Revision-History row + D-9 forward-pointer, NOT a D-9 body rewrite — folded into plan M3 + Project Structure) and C-2 (canonical() must mirror the loader's isinstance(r,dict) guard so a non-dict record fails closed, not AttributeError — folded into the sidecar contract §2). 4 build-stage advisories (importlib mechanics, glob-breadth comment, OQ-6 re-tag concurrence, T001 sizing) carried to tasks.md. Full: .aod/results/architect-plan.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: ORDERED_FRAMEWORKS Catalog-Drift CI Guard

**Branch**: `329-ordered-frameworks-ci-guard` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/329-ordered-frameworks-ci-guard/spec.md` (PM-approved 2026-06-30)
**Research**: [research.md](./research.md) (Phase 0 — complete; all PRD claims re-verified @ `644b532`)

## Summary

Add an environment-independent CI guard that fails the build when an `ORDERED_FRAMEWORKS` member catalog's **render-coupled fingerprint** (the ordered in-scope `(id, out_of_scope)` records, plus the raw record set) drifts without the 6 Coverage-Attestation (CA) PDF baselines being regenerated — closing the silent-red-`main` gap KB Entry 15 named.

The guard reuses the renderer's own `_load_framework_yaml_records` (so its notion of "what the CA page depends on" is the renderer's, by construction), compares each member's live fingerprint against a committed **sidecar** (`examples/ca-baseline-fingerprints.json`), and fails closed on a missing/partial sidecar. The sidecar is **emitted as the final step of a newly-formalized executable CA-baseline regen script** (`scripts/regenerate-ca-baselines.sh`) — promoting the manual `baseline-regen.contract.md` recipe — so a stale sidecar ≡ stale baselines and cannot be advanced without a real regen (the **OQ-1 resolution**, Architect to ratify). A dedicated, path-filtered workflow (`tachi-catalog-drift.yml`, single `ubuntu-latest`, `contents: read`, PR + `push:[main]`) runs a synthetic+live pytest module that both catches drift and ignores #333-class count-neutral edits.

**Evaluation fork** (settled at PRD, both reviewers): ship **(b)** the fingerprint guard; **defer (a)** full-byte-identity-in-CI (Typst version/platform fragility → flaky gate). No rendering, no network in the guard path.

## Technical Context

**Language/Version**: Python 3.11 (the guard module; matches `tachi-maestro-coverage.yml`'s runner) + bash 3.2.57+ (the regen wrapper; macOS-compatible, mirrors the existing recipe).
**Primary Dependencies**: **none added.** Standard library (`hashlib`, `json`, `importlib`) + already-present `pyyaml>=6` (inherited transitively via the reused loader in `extract-report-data.py`; a CI dep in both workflows + `requirements-dev.txt`). Local `typst` (0.14.2 installed) is used ONLY by the regen script and the T001 pre-state — never in the guard or any CI-triggered job (NFR-001).
**Storage**: one new committed JSON artifact (`examples/ca-baseline-fingerprints.json`, the sidecar); the 6 existing `examples/*/security-report.pdf.baseline` PDFs (read-only for this feature, NFR-004). No datastore.
**Testing**: pytest (`tests/scripts/test_catalog_drift_guard.py`) — one live-tree assertion (the real gate) + 6 synthetic cases, each clearing the `@lru_cache` (FR-007 / Risk-3).
**Target Platform**: GitHub Actions `ubuntu-latest` (single runner — load-bearing for NFR-001) + local dev shells (for the regen script and T001).
**Project Type**: single (CI/CD tooling + test harness). No frontend, backend, API, datastore, or UI surface.
**Performance Goals**: guard comparison is sub-second of real work; job wall-clock dominated by checkout + Python setup (NFR-002).
**Constraints**: **determinism / zero false-reds** (NFR-001) — result depends only on YAML in-scope fingerprints + committed sidecar, never Typst/fonts/platform/wall-clock; no network, no rendering in the guard path; single-runner (a matrix would imply platform-varying results — C4); deterministic given pinned `pyyaml` (MED-2).
**Scale/Scope**: 5 `ORDERED_FRAMEWORKS` members today (dynamic — FR-004), 6 byte-gated baselines, 1 sidecar. M-effort (1.5 eng-day central per feasibility-check); single Plan→Build→Deliver cycle, no wave fan-out.

## Constitution Check

*GATE: must pass before build. Re-checked post-design (below).*

| Principle | Relevance | Status |
|-----------|-----------|--------|
| I. General-Purpose Architecture | The guard is domain-agnostic build tooling (fingerprint↔baseline coupling); no product-domain logic added to core | ✅ PASS |
| III. Backward Compatibility (NON-NEGOTIABLE) | No change to `ORDERED_FRAMEWORKS` membership, CA rendering, or the 6 baselines (NFR-004); the sidecar is additive; the reused loader is untouched. Local `.aod/` workflows unaffected | ✅ PASS |
| VI. Testing Excellence (NON-NEGOTIABLE) | The feature *is* test infrastructure; FR-007 mandates a synthetic test matrix (grow/swap/flip→fail; #333/non-member/clean→pass) + a live-tree assertion that gates CI on both PR and `push:[main]` | ✅ PASS |
| VII. Definition of Done (NON-NEGOTIABLE) | Deliver via DoD: guard green on clean tree (tested, both triggers live), workflow operational on `main`, sidecar emitted by the regen script; CHANGELOG + ADR-037 amendment | ✅ PASS (gated at deliver) |
| VIII. Observability & RCA | FR-006 self-evident failure message (names framework, expected-vs-actual, regen entry point); the feature itself is the automated backstop for KB-15's RCA lesson | ✅ PASS |
| IX. Git Workflow (NON-NEGOTIABLE) | On feature branch `329-*`; draft PR #344 open; conventional-commit `feat(329):` title; no direct-main commit; **the feature's own dual-trigger means premature catalog drift on the branch is caught by the PR leg** | ✅ PASS |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | PM sign-off on spec ✓; PM+Architect dual sign-off on this plan (in progress); triple on tasks next | ✅ in progress |
| Code-Economy laziness ladder | Rung 1 (spec/PRD requires it — closes a recurring failure class) + rung 2 (reuse): guard **wraps** the existing `_load_framework_yaml_records`; regen script **formalizes** the existing manual recipe; zero new deps (rung 5); zero new abstraction beyond one guard module + one sidecar | ✅ PASS |
| II API-First · IV Concurrency · V Privacy | No API, no concurrency, no user data in this build-time surface | N/A |

**No violations** → Complexity Tracking intentionally empty. `data-model.md` is folded into [`contracts/sidecar.contract.md`](./contracts/sidecar.contract.md) (the sidecar schema + fingerprint algorithm *is* the data model); a standalone `data-model.md` and a REST `contracts/` directory would be cargo-cult artifacts for a CLI/CI guard (the template's "API contracts" is advisory) — omission is intentional code-economy, re-checked post-design.

## Implementation Approach

### Components (the build surface — all new except the reused loader)

| # | Component | Path | Role |
|---|-----------|------|------|
| 1 | **Guard module** | `scripts/check-catalog-drift.py` | Computes per-member fingerprints (reusing the loader via `importlib`), reads the sidecar, finds drift, formats the failure message; `--check` (default, exit 1 on drift) and `--emit` (write sidecar) CLI modes |
| 2 | **Regen script** | `scripts/regenerate-ca-baselines.sh` | Formalizes the `baseline-regen.contract.md` recipe: loops the 6 `BASELINE_EXAMPLES`, runs `extract-report-data.py … && typst compile …` under `SOURCE_DATE_EPOCH=1700000000`, does the `git checkout -- …/report-data.typ` cleanup, **emits the sidecar as its last step** (`python3 scripts/check-catalog-drift.py --emit`) |
| 3 | **Sidecar** | `examples/ca-baseline-fingerprints.json` | New committed artifact: per-member `{raw_fingerprint, in_scope_fingerprint, raw_count, in_scope_count}`, co-located with the 6 baselines it tracks. The guard's source of truth; the regen script's output |
| 4 | **Synthetic + live test** | `tests/scripts/test_catalog_drift_guard.py` | pytest module: 1 live-tree assertion (real gate, fail-closed on missing sidecar) + 6 synthetic cases (FR-007), each `cache_clear()`-ed |
| 5 | **CI workflow** | `.github/workflows/tachi-catalog-drift.yml` | Dedicated, path-filtered, dual-trigger (PR + `push:[main]`), single `ubuntu-latest`, `contents: read`; runs `pytest tests/scripts/test_catalog_drift_guard.py` |
| — | **Reused loader** (unchanged) | `scripts/extract-report-data.py` | `_load_framework_yaml_records(fw, in_scope_only=…)` (`:1090`, `@lru_cache`), `ORDERED_FRAMEWORKS` (`:1077`) — imported via `importlib`, never re-implemented (FR-001/004) |

### Fingerprint algorithm (FR-001 — full detail in the sidecar contract)

Per member `fw ∈ ORDERED_FRAMEWORKS`, canonical record tuple = `[record.get("id"), bool(record.get("out_of_scope", False))]`:
- **`raw_fingerprint`** = `sha256` over the **ordered** list of canonical tuples for ALL records (`_load_framework_yaml_records(fw)`) — catches add/remove (count delta) and `out_of_scope` flips of any record (HIGH-3).
- **`in_scope_fingerprint`** = `sha256` over the ordered canonical tuples for in-scope records (`_load_framework_yaml_records(fw, in_scope_only=True)`) — catches in-scope add/remove and ID rename/swap at constant count (HIGH-2), and the in-scope-set change an `out_of_scope` flip causes.
- Order is **preserved, never sorted** (YAML document order is what renders onto the CA page). `raw_count`/`in_scope_count` are stored for the human-readable failure summary only (FR-006). Hashing is stdlib `hashlib` over a `json.dumps(..., ensure_ascii=False)` serialization → deterministic given pinned `pyyaml` parse semantics.

### OQ resolution (cut-line decisions — Architect to ratify)

- **OQ-1 [load-bearing] — sidecar = regen-script byproduct, NOT a hand-maintained manifest.** The sidecar is written ONLY by `scripts/regenerate-ca-baselines.sh`'s final `--emit` step, so it cannot be advanced without a real baseline regen (Risk-1 cheat-resistance). The rejected alternative — a hand-editable manifest — would let a developer bump the expected fingerprints without regenerating, passing the guard while the suite is red; it forfeits the entire Risk-1 mitigation and is declined. *(If the Architect prefers the manifest fallback, the trade MUST be recorded in the ADR-037 amendment.)*
- **OQ-3 — T001 pre-state is the schedule-defining go/no-go gate (front-loaded to build hour-zero).** Run the 6-example byte-identity suite locally (the one place rendering is allowed) and record literal pre-state totals (KB-15). **Branch**: if green → emit the sidecar from the current tree and wire the guard (it goes green immediately). If **red** → a *bounded* baseline remediation (regen the 6 baselines via the new script, which also emits the sidecar) precedes the guard going green, and the regen lands in this same change-set. Git evidence (F-185 `2aa1bf5` regenerated + absorbed #186's ATLAS delta; only count-neutral member edits since — #333) ⇒ **green is highly likely** (Risk-4 Low). The remediation tail is the ceiling-day driver the Team-Lead sizes.
- **OQ-6 — the `#329`-tagged init.sh xfail is OUT of scope.** `test_init_sh_substitution.py:35` (the `@pytest.mark.xfail` marker on `test_personalized_tree_bytes_match_baseline`, function at `:54`; `strict=False`, "Tracked for fixture regen under #329") guards the **init.sh-substitution baseline** (`tests/fixtures/init-baseline-tree/`, regenerated by `regenerate-baseline.sh`) — an orthogonal surface to the CA-PDF baselines. **Recommendation: re-tag** the xfail reason to a dedicated fixture-regen backlog item (a one-line follow-up, filed at deliver), so the `#329` reference doesn't falsely imply this feature regenerates it. Folding it in would scope-creep across an unrelated surface.

### Build sequence (single track; M1∥M2 partially parallel per feasibility-check)

1. **T001 (hour-zero, go/no-go)** — run `tests/scripts/test_backward_compatibility.py` locally; record totals; branch per OQ-3. *(Rendering allowed here only.)*
2. **M1 — guard logic + sidecar-by-regen** (load-bearing): build `check-catalog-drift.py` (fingerprint + check + emit); promote the recipe to `regenerate-ca-baselines.sh`; run one real local regen/byte-compare cycle to prove the script reproduces the baselines AND emits a correct sidecar.
3. **M2 — workflow + synthetic test** (startable in parallel with M1, stubbing the sidecar path): `tachi-catalog-drift.yml` (maestro skeleton + pytest dual-trigger anchor); `test_catalog_drift_guard.py` (live + 6 synthetic, cache-cleared).
4. **Integration** — guard green on the clean tree; both triggers live; sidecar committed.
5. **M3 — docs/closeout**: ADR-037 amendment via a **new decision D-14** (count→fingerprint guard + sidecar contract + (a)-deferral rationale, OQ-5) + a Revision-History row + a one-line D-9 forward-pointer — **do NOT rewrite D-9's body text** (preserves ADR-037's Accepted/byte-unchanged discipline; Architect C-1); docs note (KB-15 checklist now CI-backstopped); CHANGELOG; file the OQ-6 re-tag follow-up.
6. **Deliver gate**: per KB-18, verify branch-current + local `main`==`origin/main` before any merge/direct-main push; merge via devops; verify release-please opens (the `feat(329):` PR squash-merge is the release trigger; M3 doc commits are hidden-bump).

### CI invocation & test design (FR-005 / FR-007)

CI runs `pytest tests/scripts/test_catalog_drift_guard.py` (the `tachi-maestro-coverage.yml` pattern — a pytest module that asserts an invariant on the real tree). The module's `test_live_tree_fingerprints_match_sidecar` is the real gate (computes live fingerprints, reads the committed sidecar, asserts equality; **fails** — not skips — on missing/partial/unparseable sidecar, FR-008). The 6 synthetic cases prove the *logic* (grow/swap/flip → drift; citation-only/non-member/clean → no drift) against crafted record sets (monkeypatch the loader or a tmp-YAML fixture), **each clearing `_load_framework_yaml_records.cache_clear()`** to prevent a stale-cache false-green (Risk-3). Path filter (single-source `&drift_paths` anchor, reused on both triggers — F-250 lock-step): `schemas/taxonomy/*.yaml`, `examples/*/security-report.pdf.baseline`, the sidecar, the regen script, `baseline-regen.contract.md`, `scripts/extract-report-data.py` (loader source), the guard, the test, and the workflow itself.

## Risks & Mitigations

| Risk | L / I | Mitigation |
|------|-------|------------|
| **R1** Sidecar bump-without-regen cheat | M / H | OQ-1: sidecar emitted ONLY as the regen script's last step — un-advanceable without a real regen (manifest fallback declined) |
| **R2** False-red on count-neutral edits (#333 class) | High-if-misdesigned / H (trust erosion) | FR-003 fingerprint-keyed (never file-diff); FR-007(d) proves it against the real #333 change shape (`mitre-atlas` 36→36, `nist-ai-rmf` 72→72) |
| **R3** Stale-`lru_cache` false-green test | M-if-unaware / H (a guard that lies) | FR-007 mandates `cache_clear()` (or loader monkeypatch) per case |
| **R4** `main` already red at T001 | Low (git evidence) / M | T001 front-loaded go/no-go; bounded baseline remediation in-change-set if red; sizes the ceiling day |
| **R5** Sidecar deleted/partial to silence the guard | Low / M | FR-008 fail-closed: missing/partial/unparseable ⇒ failure, never pass |
| **R6** Loader change silently alters fingerprints | Low / M | `scripts/extract-report-data.py` is in the path filter → a loader edit re-runs the guard |

## Project Structure

### Documentation (this feature)
```
specs/329-ordered-frameworks-ci-guard/
├── spec.md                 # PM-approved 2026-06-30
├── research.md             # Phase 0 — complete (all PRD claims re-verified)
├── plan.md                 # This file
├── contracts/
│   └── sidecar.contract.md # Sidecar schema + fingerprint algorithm + regen-emission contract (the data model)
├── quickstart.md           # Local verification recipe (Phase 1)
├── feasibility-check.md    # Team-Lead (from /aod.define)
└── tasks.md                # /aod.tasks output (next)
```
**Omitted by design**: standalone `data-model.md` (folded into the sidecar contract — one small JSON schema, not a relational model) and a REST `contracts/` (no API surface). Intentional code-economy, not a gap.

### Source code (build surface — repository root)
```
scripts/check-catalog-drift.py            # NEW — guard module (fingerprint + --check + --emit)
scripts/regenerate-ca-baselines.sh        # NEW — formalized CA regen; emits the sidecar last
examples/ca-baseline-fingerprints.json    # NEW — the sidecar (regen-emitted, committed)
tests/scripts/test_catalog_drift_guard.py # NEW — live assertion + 6 synthetic cases (cache-cleared)
.github/workflows/tachi-catalog-drift.yml # NEW — dedicated, path-filtered, PR + push:[main], single-runner
docs/architecture/02_ADRs/ADR-037-*.md    # AMEND — NEW decision D-14 + Revision-History row + D-9 forward-pointer (NOT a D-9 body rewrite; Architect C-1)
CHANGELOG.md                              # AMEND — feature entry
# READ-ONLY / NAMED-UNTOUCHED (NFR-004):
scripts/extract-report-data.py            # reused loader + ORDERED_FRAMEWORKS — imported, NOT modified
examples/*/security-report.pdf.baseline   # the 6 baselines — NOT modified (unless T001 red → bounded regen)
specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md  # recipe source — referenced, not moved
.github/workflows/{tachi-maestro-coverage,tachi-pytest}.yml           # pattern templates — NOT modified
tests/scripts/test_init_sh_substitution.py # the OQ-6 xfail — OUT of scope (re-tag follow-up only)
```
**Structure Decision**: net-new build tooling alongside existing patterns; one guard module + one regen wrapper + one sidecar + one test + one workflow. No new directories beyond `specs/329-*/contracts/`. Reuses the renderer's loader; formalizes the existing recipe. No greenfield abstraction.

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*
