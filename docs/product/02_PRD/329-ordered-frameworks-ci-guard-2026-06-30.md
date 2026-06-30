---
prd:
  number: 329
  topic: ordered-frameworks-ci-guard
  created: 2026-06-30
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-06-30, status: APPROVED, notes: "v1.1 final, authored via ~aod-define as BLP-06 Wave 2 CI-hardening-tail lead. Both reviewers APPROVED_WITH_CONCERNS, zero blockers, and ratified the core fork (ship the lightweight guard / defer full-byte-identity-in-CI on the determinism rationale). v1.1 folds every Triad correction: HIGH-1/C1 (FALSE regen-script citation — regenerate-baseline.sh is the init.sh fixture, NOT the CA-PDF baselines; FR-2 reframed to formalize the manual baseline-regen.contract.md recipe into an executable regen script that emits the sidecar); HIGH-2+HIGH-3 (count-only false-negatives on id-swap/rename and out_of_scope-flip — FR-1 upgraded from bare count to a fingerprint of the ordered in-scope (id,out_of_scope) records, closing both while preserving the #333 count-neutral pass); MED-1 (the existing #329-tagged xfail is the init.sh-substitution baseline, a DIFFERENT surface — scoped OUT explicitly, OQ-6); MED-2 (pinned-pyyaml honesty on NFR-1/3); MED-3 (OQ-4 resolved: dedicated tachi-catalog-drift.yml, NOT folded into tachi-pytest.yml's matrix; tachi-maestro-coverage.yml named as the near-exact M2 template); MED-4 (FR-5 path-filter lock-step + sidecar/regen-script in trigger); LOW-1 (OQ-5 resolved: amend ADR-037); C2 (T001 pre-state front-loaded to hour-zero of M1); C3 (FR-7 lru_cache cache_clear foot-gun); C4 (single-runner is a determinism consequence). Timeline traces 1:1 to feasibility-check.md (floor 1.0 / planning 1.5 / ceiling 3.0). Plan-stage gates: OQ-1 (sidecar emission mechanism), OQ-3 (T001), OQ-6 (init-baseline-tree scope)."}
  architect_signoff: {agent: architect, date: 2026-06-30, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 3 HIGH / 4 MED / 3 LOW; every load-bearing claim verified against the live tree @ 644b5329. FORK RATIFIED: ship (b) lightweight guard / defer (a) full byte-identity-in-CI — NFR-1 determinism rationale confirmed correct (baseline-regen.contract.md D-9 invariant 2 itself flags typst-version drift as the first suspect for any non-CA delta, so (a)-in-CI is a flaky gate). #333 count-neutrality DECISIVELY verified (mitre-atlas 36→36, nist-ai-rmf 72→72) — FR-3 empirically vindicated. #338 dual-trigger pattern confirmed exact. HIGH-1 (load-bearing): FR-2 cited the WRONG regen artifact — regenerate-baseline.sh regenerates the F-248 init.sh fixture, not the 6 PDF baselines; the real regen is a manual recipe in baseline-regen.contract.md (no executable to emit a sidecar from), so the cheat-resistance must be earned by promoting the recipe to a real script. HIGH-2: count-only guard false-negatives on a constant-count id swap/rename. HIGH-3: FR-1 cited the RAW count (:1152) but the CA partition renders against the IN-SCOPE count (:1168) — out_of_scope flip is a second false-negative. All three folded into v1.1 (FR-1 fingerprint reframe + FR-2 executable-regen-script). Plan sign-off gated on OQ-1 (sidecar mechanism), and the FR-1/FR-2 corrections carried into spec. OQ-2→defer(a), OQ-4→dedicated workflow, OQ-5→amend ADR-037 all adjudicated. Full: .aod/results/architect-prd-329.md. Will re-review the plan."}
  techlead_signoff: {agent: team-lead, date: 2026-06-30, status: APPROVED_WITH_CONCERNS, notes: "Feasible, well-scoped. ESTIMATE (authoritative, traces to feasibility-check.md): floor 1.0 / planning 1.5 / ceiling 3.0 eng-days. Central 1.5d CONFIRMED and well-calibrated vs 3 sibling CI features (tachi-maestro-coverage.yml is the near-exact structural twin of M2 — single-runner, reuses a canonical count/invariant fn, fails naming the entity; #338 dual-trigger is a 1-anchor copy; #329 ≤ #282 effort, no binary/SARIF). Floor 0.75→1.0 and ceiling 2.5→3.0 both raised for the single FR-2 risk (C1): there is NO CA-baseline regen script — it is a hand-run 6× markdown recipe, so the sidecar requires authoring a regen wrapper + one real local regen/byte-compare cycle. C2 (MEDIUM): T001 pre-state (is main green on the byte-identity suite now?) is the schedule-defining gate — FRONT-LOADED to hour-zero of M1 in v1.1; git evidence strongly indicates main is green (last baseline touch = F-185 2aa1bf5 which absorbed #186's ATLAS delta; only member-YAML change since = #333 count-neutral). C3/C4 (LOW): lru_cache cache_clear() foot-gun in synthetic test + single-runner is a determinism consequence — both folded. Capacity = one engineer (senior-backend profile), no wave fan-out; write-set disjoint from open work (only open PR is #341 release). Proceed to /aod.plan. Full: .aod/results/team-lead-prd-329.md."}
source:
  idea_id: 329
  story_id: null
---

# ORDERED_FRAMEWORKS Catalog-Drift CI Guard - Product Requirements Document

**Status**: Approved (both reviewers APPROVED_WITH_CONCERNS — zero blockers; plan-stage gates carried as OQ-1/OQ-3/OQ-6)
**Created**: 2026-06-30
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (BLP-06 Wave 2 / CI-hardening tail — lead item)

---

## 📋 Executive Summary

### The One-Liner
Add a fast, environment-independent CI guard that **fails the build when an `ORDERED_FRAMEWORKS` member catalog's render-coupled fingerprint drifts without the 6 Coverage-Attestation PDF baselines being regenerated in the same change-set** — so the silent-red-main failure that F-186 left for F-185 to discover (KB Entry 15) can never ship undetected again.

> **v1.1 design note**: Issue #329 framed option (b) as a "catalog-**count** drift guard." The Architect's review (HIGH-2/HIGH-3) showed a bare count false-negatives on two real edits — a constant-count ID swap/rename, and an `out_of_scope` flag flip. v1.1 therefore upgrades the guard key from a record *count* to a **fingerprint of each member's ordered in-scope `(id, out_of_scope)` records** (FR-1). This is a strict superset of the count, closes both false-negatives, and still passes the count-neutral #333 case. "Count" survives only as the human-readable summary in the failure message.

### Problem Statement
Five taxonomy catalogs are members of `ORDERED_FRAMEWORKS` ([`scripts/extract-report-data.py:1077`](scripts/extract-report-data.py#L1077)): `owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`. For any member, the **rendered Coverage-Attestation (CA) pages are catalog-coupled**: every regenerated PDF security report prints per-framework denominators (both a RAW total and an IN-SCOPE total, `extract-report-data.py:1140`/`:1155`) and per-`id` Covered/Partial/Gap rows. The byte-identity suite [`tests/scripts/test_backward_compatibility.py`](tests/scripts/test_backward_compatibility.py) byte-compares 6 committed CA-page baselines (`examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,maestro-reference,free-text-microservice}/security-report.pdf.baseline`). When a member catalog's in-scope ID set changes, those baselines must be regenerated (ADR-037 D-9 lane, per `specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md`) or the suite goes red.

**The suite is local-only — it is wired into no `.github/workflows/**`** (Architect-verified: zero matches for `test_backward_compatibility` across the workflows dir). So a red state is invisible on `main`. This already happened once: F-186 grew `mitre-atlas` 30 → 36 **without** regenerating the baselines, leaving the suite **silently red on `main`** — discovered only weeks later at F-185's plan-review (KB Entry 15). The cost was a late timeline revision and an errata trail (PRD v1.2). **This is a recurring failure *class*, not a one-off bug**: every future catalog-edit against an `ORDERED_FRAMEWORKS` member can repeat it, and the gap is structural (no CI surfaces the red).

### The Evaluation Fork (the issue's core question)
Issue #329 asks us to **evaluate** two remediations:

| Option | What it is | Verdict |
|---|---|---|
| **(a) Full byte-identity suite in CI** | Wire `test_backward_compatibility.py` itself into CI — render the 6 PDFs on a runner and byte-compare to the committed baselines. | **Deferred (not primary).** It re-checks the real artifact, but its hard dependency is **cross-environment PDF byte-determinism**: the suite pins `SOURCE_DATE_EPOCH=1700000000`, yet byte-identity also depends on the exact Typst version, font set, and platform. `baseline-regen.contract.md` (D-9 invariant 2) *itself* names typst-version drift as the first suspect for any non-CA byte delta — i.e. the contract concedes the renderer is version-fragile. A CI runner on a different Typst build produces a **false red** unrelated to catalog drift — a flaky gate that erodes trust. **Architect-ratified as deferred.** |
| **(b) Lightweight catalog-fingerprint drift guard** | A CI check that recomputes each member's render-coupled fingerprint and fails when it diverges from the fingerprint the baselines were last regenerated against. | **PRIMARY (recommended, Architect-ratified).** Targets the *exact* failure mode deterministically and environment-independently (no Typst, no rendering, sub-second), reuses the renderer's own record-loading function, and follows the proven `tachi-maestro-coverage.yml` / `tachi-pytest.yml` path-filtered + push-to-main patterns. |

**Recommendation (ratified by both reviewers): ship (b); explicitly defer (a)** as a possible future complement only if the guard proves insufficient. This PRD specifies (b).

### Proposed Solution
A real AOD feature (full lifecycle) delivering an environment-independent **catalog-fingerprint drift guard**:

1. **Fingerprint, don't render.** For each `ORDERED_FRAMEWORKS` member, compute a deterministic fingerprint of its **ordered in-scope `(id, out_of_scope)` records** by reusing the renderer's own [`_load_framework_yaml_records`](scripts/extract-report-data.py#L1090) (the function the CA-page denominators at `:1140`/`:1155` are built from) — so the guard's notion of "what the CA page depends on" is identical to the renderer's, by construction. The bare per-framework count is retained only as the human-readable summary.
2. **Compare against a regeneration-emitted sidecar.** The expected per-member fingerprints are written **by the CA-baseline regeneration process itself**, so a stale sidecar ≡ stale baselines. **Because no executable CA-baseline regen exists today** (it is a manual recipe in `baseline-regen.contract.md` — Architect HIGH-1), this feature must first **promote that recipe to a thin executable regen script** that loops the 6 examples, runs the documented `extract-report-data.py … && typst compile …` sequence, and writes the sidecar as its last step. That is what makes the sidecar a genuine, cheat-resistant byproduct (Risk-1). The guard **fails closed** on a missing/partial sidecar.
3. **Iterate `ORDERED_FRAMEWORKS` dynamically** so a future 6th member is covered automatically (no hardcoded list of 5).
4. **Wire it into CI on the proven pattern**: a **new, dedicated** path-filtered workflow (`.github/workflows/tachi-catalog-drift.yml`) firing on **both `pull_request` and `push: branches:[main]`** (the #338 lesson — a direct-to-main commit bypasses the PR trigger, which is exactly how hardening was silently reverted once). Single `ubuntu-latest` runner (a cross-platform matrix would contradict NFR-1 — the result must not vary by platform), `permissions: contents: read`. Structurally a near-clone of `tachi-maestro-coverage.yml`.
5. **Prove it with a synthetic test**: reproduce the F-186 scenario (in-scope fingerprint drifts without regen → guard fails) AND the #333 regression case (citation-string edits change a member YAML but not its in-scope ID set → guard passes) AND a non-member change (e.g., `nist-ai-600-1`) → guard passes. Each case must clear the `lru_cache` on the count function (C3) to avoid a false-green test.

### Success Criteria
1. A CI guard fails the build when any `ORDERED_FRAMEWORKS` member's render-coupled fingerprint (ordered in-scope `(id, out_of_scope)` records) diverges from the fingerprint its baselines were last regenerated against — covering the F-186 grow, **and** the constant-count ID swap/rename (HIGH-2), **and** the `out_of_scope` flip (HIGH-3).
2. The guard runs on **both** `pull_request` and `push: branches:[main]` (the #338 silent-revert lesson) — a direct-to-main catalog edit without regen reddens CI.
3. The guard is **environment-independent**: no Typst, no PDF rendering, no cross-runner byte-determinism dependency → **zero false reds** from rendering nondeterminism (the single property that justifies (b) over (a)). Deterministic given a pinned `pyyaml` (NFR-1/MED-2).
4. A synthetic unit test proves the guard **catches** fingerprint drift (grow / ID-swap / `out_of_scope`-flip without regen) and **ignores** a citation-string-only edit (#333 class) and a non-member catalog change — each case clearing the `lru_cache` (C3).
5. The guard's failure message names the offending framework(s), shows expected-vs-actual, and points to the regen entry point (the new regen script / `baseline-regen.contract.md` / ADR-037 D-9 lane) so the fix path is self-evident.
6. No new runtime dependency; the no-network / no-rendering determinism boundary is preserved (consistent with #183/#333 CI discipline).
7. KB Entry 15's define-time "grep `ORDERED_FRAMEWORKS`" process lesson gains an automated backstop: the human checklist is now enforced by CI.

### Timeline & Milestones
**Estimate: 1.5 engineer-days central** (floor 1.0 / ceiling 3.0; Team-Lead-authoritative, both boundaries widened from the PRD's preliminary 0.75/2.5 for the single FR-2 regen-lane risk). Traces 1:1 to `specs/329-ordered-frameworks-ci-guard/feasibility-check.md`.

| Milestone | Effort (of 1.5d) | Content |
|---|---|---|
| **T001 — Pre-state gate (hour-zero of M1)** | ~0.1d | **Front-loaded (C2).** Run the 6-example byte-identity suite locally (the one place rendering is allowed) and record literal pre-state totals (KB-15's own lesson). Go/no-go: if `main` is red, a bounded baseline remediation precedes the guard going green (Risk-4 — git evidence says Low). |
| **M1 — Guard logic + sidecar-by-regen** | ~0.7d | Fingerprint checker reusing `_load_framework_yaml_records` (raw + in-scope), iterating `ORDERED_FRAMEWORKS`, fail-closed on missing sidecar. **The load-bearing work**: promote the manual `baseline-regen.contract.md` recipe to an executable regen script that emits the sidecar as its last step (FR-2 / OQ-1), proven with one real local regen/byte-compare cycle. |
| **M2 — CI workflow + synthetic test** | ~0.4d | Dedicated `tachi-catalog-drift.yml` (PR + push:[main], single `ubuntu-latest`, `contents: read`), structurally cloned from `tachi-maestro-coverage.yml`; synthetic test (grow/ID-swap/`out_of_scope`-flip → fail; #333 count-neutral / non-member → pass; `cache_clear()` each case). Startable in parallel with M1, stubbing the sidecar path. |
| **M3 — Docs / closeout** | ~0.4d | ADR-037 amendment (count→fingerprint guard + sidecar contract + (a)-deferral rationale, OQ-5); docs note (KB-15 checklist now CI-backstopped); CHANGELOG. |
| **Dev Complete** | **1.5d** | Guard green on a clean tree; synthetic test passing; workflow live on PR + push:[main]; sidecar emitted by the regen script. |

---

## 🎯 Strategic Alignment

### Product Vision Alignment
tachi's authority rests on a **machine-readable taxonomy contract** that downstream tools consume ([`tachi_source_of_truth`]). The CA pages of every shipped PDF report assert per-framework coverage denominators drawn from these catalogs. A silently-red byte-identity suite means the project can ship a report whose CA page is stale or wrong **without any signal** — directly undermining the contract's credibility. This guard defends the integrity of the rendered coverage claims at the point they can drift.

### Roadmap Fit
This is the **lead item of BLP-06's CI-hardening tail (Wave 2)**. BLP-06 is the first *subtractive* (maintenance/consolidation) initiative; its Wave 1 (#333 citation remediation) closed a defect adopters could *see*, and this item closes a defect-detection *gap* in the build itself. It is the natural CI counterpart to #338, which added the `push: branches:[main]` trigger to `tachi-pytest.yml` after a direct-to-main clobber — this feature reuses that exact lesson for a different surface.

### Predecessor Relationship
Direct endogenous follow-on of **KB Entry 15 (F-185 consequence-scope lesson)** and its named backlog item: *"The local-only byte-identity suite gap that enabled the inherited red is now tracked as a backlog item (#329 — evaluate CI wiring / catalog-count drift guard)."* The triggering incident is **F-186** (the ATLAS 30→36 growth that left the inherited red, KB Entry 13). Reinforces the BLP-05/BLP-06 thesis that the taxonomy contract's *rendered* assertions must be guarded, not just its data.

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: tachi Taxonomy Steward / Catalog-Growth Feature Author
Owns `schemas/taxonomy/`. Ships catalog-edit features (the #184/#185/#186 pattern). Needs a **fast, deterministic** signal at PR time that says "you changed a render-coupled member catalog but didn't regenerate the CA baselines" — *before* merge, not weeks later at a sibling's plan review. Does not want a flaky PDF-rendering gate that false-reds on unrelated runner differences.

### Secondary Persona: tachi Maintainer / Reviewer on `main`
Relies on `main` being green as a precondition for any new branch. The #338 lesson taught that direct-to-main commits bypass PR gates; this persona needs the guard to fire on `push: branches:[main]` too, so a stale-baseline state cannot persist invisibly on the trunk.

### Tertiary Persona: AOD Process Author (KB Entry 15)
Codified the define-time "grep `ORDERED_FRAMEWORKS`" checklist as a human discipline. Wants that discipline backstopped by automation so a future author who forgets the checklist is still caught.

---

## 📖 User Stories

### US-1: Catch drift-without-regen at PR time
**When** I open a PR that changes an `ORDERED_FRAMEWORKS` member catalog's render-coupled content (adds/removes/renames a record, or flips `out_of_scope`) but I forget to regenerate the 6 CA-page baselines,
**I want** CI to fail fast with a clear message pointing me to the regen script/contract,
**So I can** fix it before merge instead of leaving `main` silently red for a sibling feature to discover weeks later (the F-186 → F-185 path).

**Acceptance**: Given a member whose live fingerprint ≠ its regen-emitted sidecar fingerprint, when the drift-guard workflow runs (on PR or push:[main]), then it fails with a message naming the framework, expected-vs-actual, and the regen entry point.

### US-2: Don't false-red on count-neutral edits
**When** I edit a member catalog in a way that does **not** change its in-scope ID set — e.g., the #333 citation-URL string fixes to `mitre-atlas.yaml`/`nist-ai-rmf.yaml`,
**I want** the guard to stay green,
**So I can** ship count-neutral data fixes without a spurious "regenerate baselines" demand (those edits do not change the rendered CA pages).

**Acceptance**: Given a member-catalog edit that leaves every member's in-scope `(id, out_of_scope)` fingerprint unchanged, when the guard runs, then it passes. (Verified against the real #333 change shape — Architect confirmed `mitre-atlas` 36→36 and `nist-ai-rmf` 72→72 with citation-only edits, correctly requiring no regen.)

### US-3: Guard the trunk, not just PRs
**When** a catalog-edit change reaches `main` via a direct push (not a PR),
**I want** the guard to fire on `push: branches:[main]` as well,
**So I can** trust that a stale-baseline state cannot live invisibly on the trunk (the #338 direct-to-main lesson, reused).

**Acceptance**: Given a direct push to `main` that drifts a member fingerprint without regen, when the push trigger fires, then the workflow fails on `main`.

### US-4: Future member coverage is automatic
**When** a future framework is added to the `ORDERED_FRAMEWORKS` tuple,
**I want** the guard to cover it without code changes,
**So I can** avoid a second silent-gap class for the new member.

**Acceptance**: Given the guard iterates `ORDERED_FRAMEWORKS` dynamically, when a 6th member is added to the tuple, then the guard fingerprints it automatically (no hardcoded list).

---

## ⚙️ Functional Requirements

### FR-1: Render-coupled fingerprint (reuse the renderer's record loader; raw + in-scope)
The guard MUST compute, per `ORDERED_FRAMEWORKS` member, a deterministic fingerprint of the **ordered list of in-scope `(id, out_of_scope)` records**, derived by reusing [`_load_framework_yaml_records`](scripts/extract-report-data.py#L1090) — the same loader behind the CA-page RAW denominator (`load_framework_yaml_record_counts`, `:1140`/`:1152`) and the IN-SCOPE denominator (`load_framework_yaml_in_scope_record_counts`, `:1155`/`:1168`). The fingerprint MUST capture **both** the raw record set and the in-scope partition, so it detects: add/remove (count delta), ID rename/swap at constant count (HIGH-2), and `out_of_scope` flips at constant count (HIGH-3). The bare per-framework count is retained only for the human-readable failure message. The guard MUST iterate `ORDERED_FRAMEWORKS` dynamically (FR-4), never a hardcoded list, and never a re-implemented YAML walk.

### FR-2: Sidecar emitted by a *real* CA-baseline regen process (cheat-resistant)
The expected fingerprints the guard compares against MUST be produced **by the CA-baseline regeneration process**, so a stale sidecar ≡ stale baselines. **There is no executable CA-baseline regen today** (Architect HIGH-1 / Team-Lead C1: `tests/fixtures/regenerate-baseline.sh` regenerates the unrelated F-248 init.sh fixture; the real CA regen is a manual recipe in `baseline-regen.contract.md:26-38`). Therefore this feature MUST **promote that recipe to a thin executable regen script** (e.g. `scripts/regenerate-ca-baselines.sh`) that loops `BASELINE_EXAMPLES`, runs the exact documented `extract-report-data.py … && typst compile …` sequence with `SOURCE_DATE_EPOCH=1700000000` and the contract's `git checkout -- report-data.typ` cleanup, and **writes the sidecar as its final step**. This makes "single canonical regen route" true and the sidecar a genuine byproduct. *(Sidecar-by-regen-script vs. a hand-maintained manifest fallback is OQ-1, Architect-owned at /aod.plan; the manifest fallback forfeits the Risk-1 cheat-resistance — flag the trade if chosen.)*

### FR-3: Fingerprint-based, never file-diff-based (the #333 regression guard)
The guard MUST key on the **fingerprint** (FR-1), not on "did the member YAML file change." A file-diff approach would false-red on count-neutral edits — concretely, #333's citation-string fixes to two member catalogs on `main` correctly required no regen (Architect-verified 36→36, 72→72). The guard MUST pass for any edit that leaves the in-scope `(id, out_of_scope)` fingerprint unchanged.

### FR-4: Dynamic member coverage
The guard MUST derive its target set from `ORDERED_FRAMEWORKS` at runtime so adding a future member (the way #184's `nist-ai-600-1` was deliberately a *non*-member, but a future framework might be a member) extends coverage with zero guard-code change.

### FR-5: CI workflow — dedicated, path-filtered, dual-trigger, single-runner, least-privilege
A **new dedicated** workflow `.github/workflows/tachi-catalog-drift.yml` (NOT a job in `tachi-pytest.yml` — its macOS/ubuntu bash-version matrix is irrelevant and would waste a leg; MED-3) MUST:
- Fire on **`pull_request`** AND **`push: branches:[main]`** (the #338 dual-trigger lesson; reuse the single-source `&anchor`/`*anchor` paths pattern from `tachi-pytest.yml`).
- Path-filter, **in lock-step with the check invocation** (the F-250 lock-step discipline documented in `tachi-pytest.yml:38-48`; MED-4), to every surface that can change a fingerprint or its sidecar: `schemas/taxonomy/*.yaml`, the 6 `examples/*/security-report.pdf.baseline` files, **the sidecar file**, **the new regen script + `baseline-regen.contract.md`** (so a regen-only commit re-runs the guard), and the guard script/test/workflow themselves.
- Run on a **single `ubuntu-latest` runner** — load-bearing for NFR-1, not merely a CI-minute saving (C4): a matrix would imply the result can vary by platform, contradicting the (b)-over-(a) thesis.
- Declare `permissions: contents: read`.

### FR-6: Self-evident failure message
On drift, the guard MUST emit a message naming the offending framework(s), the expected-vs-actual fingerprint (with the human-readable count summary), and the remediation entry point (the new regen script / `baseline-regen.contract.md` / ADR-037 D-9 lane).

### FR-7: Synthetic-only test, cache-cleared (no live rendering in the test/CI path)
The guard's correctness MUST be proven by a synthetic unit test (manipulating records/sidecar in a tmp fixture), never by rendering real PDFs in the test or CI path — preserving the no-rendering / no-network determinism boundary (#183/#333). The test MUST cover: (a) add/remove grow → fail; (b) constant-count ID swap/rename → fail (HIGH-2); (c) `out_of_scope` flip → fail (HIGH-3); (d) citation-string-only edit / #333 class → pass; (e) non-member catalog change → pass; (f) clean tree → pass. **Each case MUST call `_load_framework_yaml_records.cache_clear()`** (the loader is `@functools.lru_cache`, `:1089`) — or monkeypatch the count functions as existing tests do — to avoid a stale-cache **false-green** (C3), the worst outcome for a guard whose entire value is trustworthiness.

### FR-8: Fail closed on missing/partial sidecar
The guard MUST treat a missing, partial, or unparseable sidecar as a **failure**, never a pass — so deleting or truncating the sidecar cannot silence the guard (Risk-5).

---

## 🚀 Non-Functional Requirements

> Pure CI/governance change: **no UI surface** (Accessibility N/A) and **no runtime product surface** (this is build-time tooling). The NFRs below cover the determinism and CI characteristics that are load-bearing for this feature.

### NFR-1: Determinism / zero false-reds (load-bearing)
The guard MUST be deterministic and environment-independent — its result depends only on the YAML in-scope record fingerprints and the committed sidecar, never on Typst version, fonts, platform, or wall-clock. This is the single property that justifies (b) over (a): a guard that can false-red is worse than no guard (it trains reviewers to ignore it). Zero rendering, zero network in the guard path. Determinism is *given a pinned `pyyaml`* (the guard inherits pyyaml's parse semantics, MED-2) — already a CI dependency in `tachi-pytest.yml` and imported by `conftest.py`; stated honestly the same way the suite treats a pinned Typst.

### NFR-2: Speed
The guard MUST complete in well under the `tachi-pytest.yml` matrix time — the fingerprint comparison is sub-second of actual work; total job time should be dominated by checkout + Python setup, not the check.

### NFR-3: No new runtime dependency
Implementation MUST use the standard library plus already-present `pyyaml`. No new package in any manifest.

### NFR-4: Scope discipline / write-set disjointness
The feature MUST NOT modify `ORDERED_FRAMEWORKS` membership, the CA-page rendering logic, or any of the 6 baselines (unless the T001 pre-state finds `main` already red — see OQ-3/Risk-4). Its write-set is the new regen script, the guard script, its test, the new sidecar artifact, the new workflow, the ADR-037 amendment, and docs/CHANGELOG. (Team-Lead-verified disjoint from open work — only open PR is #341, a release.)

---

## 📊 Success Metrics

| Metric | Baseline (today) | Target |
|---|---|---|
| CI surfaces a member fingerprint drift without regen | **No** (suite is local-only; F-186 shipped red undetected) | **Yes** — fails on PR and push:[main] |
| False-red rate from rendering nondeterminism | N/A (suite not in CI) | **Zero** (guard does not render) |
| Constant-count drift detection (ID swap / `out_of_scope` flip) | **No** (a bare count misses both) | **Yes** (fingerprint key, HIGH-2/HIGH-3) |
| #333-class count-neutral edit blocked spuriously | Would be blocked by a naive file-diff guard | **Never** (fingerprint-based, proven by synthetic test) |
| Define-time KB-15 checklist enforcement | Human-discipline only | **Automated backstop** in CI |

---

## 🔍 Scope & Boundaries

### In Scope (P0)
- ✅ The catalog-fingerprint drift guard (option **b**), reusing `_load_framework_yaml_records` (raw + in-scope), iterating `ORDERED_FRAMEWORKS` dynamically, fail-closed on missing sidecar.
- ✅ **Promotion of the manual CA-baseline regen recipe to an executable regen script** that emits the sidecar as a byproduct (FR-2 — the load-bearing deliverable).
- ✅ A new dedicated, path-filtered CI workflow firing on PR + push:[main], single `ubuntu-latest`, `contents: read`.
- ✅ Synthetic unit test (grow / ID-swap / `out_of_scope`-flip → fail; #333 / non-member / clean → pass; cache-cleared).
- ✅ Self-evident failure message → regen entry point.
- ✅ T001 pre-state check (front-loaded) that `test_backward_compatibility.py` is currently green on `main`.
- ✅ ADR-037 amendment (OQ-5) + docs note (KB-15 checklist now CI-backstopped) + CHANGELOG.

### Out of Scope
- ❌ **Option (a): wiring the full byte-identity suite into CI.** Evaluated and **deferred** (Architect-ratified) for the cross-environment PDF-determinism risk (NFR-1). May be revisited as a complement only if (b) proves insufficient; documented as the rejected-as-primary alternative in the ADR-037 amendment.
- ❌ **The init.sh-substitution baseline (`tests/fixtures/init-baseline-tree/`) and its `#329`-tagged xfail.** The existing xfail at [`test_init_sh_substitution.py:35`](tests/scripts/test_init_sh_substitution.py#L35) (`test_personalized_tree_bytes_match_baseline`) was tagged "regen under #329" by #338, but it is a **different baseline surface** (the F-248/F-256 init.sh fixture regenerated by `regenerate-baseline.sh`), unrelated to the CA-PDF baselines this feature guards (MED-1, corrected on live-tree verification). It is `strict=False` (non-blocking). **Decision: out of scope; re-tag or track separately (OQ-6)** — folding it would scope-creep a focused CI-guard feature across an orthogonal surface.
- ❌ Changing `ORDERED_FRAMEWORKS` membership or CA-page rendering.
- ❌ Regenerating current CA baselines (unless T001 finds `main` red — then a bounded remediation precedes the guard going green).
- ❌ The broader ~19 documented out-of-gate pytest failures (a separate concern).
- ❌ A general-purpose "every taxonomy file is rendered-consistent" checker — YAGNI; the spec requires only the `ORDERED_FRAMEWORKS` fingerprint↔baseline coupling.

### Assumptions
- `main` is currently **green** on `test_backward_compatibility.py` (F-185's `2aa1bf5` regenerated the 6 baselines and absorbed #186's ATLAS delta; #333's subsequent member-YAML edits were count-neutral, Team-Lead-verified). **Validated at T001.**
- After FR-2, the new regen script is the single canonical place CA baselines are produced, so emitting the sidecar there covers all regen routes (FR-8 fails closed otherwise).

### Constraints
- Determinism boundary: no network, no PDF rendering in the guard/CI path (NFR-1); rendering is allowed only in the local T001 pre-state and the local regen script.
- Reuse-first (code-economy): the record loader already exists (`:1090`) — the guard wraps it; the regen recipe already exists — the script formalizes it. Neither is re-implemented from scratch.

---

## ⚠️ Risks & Dependencies

**Risk-1 — Sidecar bump-without-regen cheat.** If expected fingerprints were a hand-editable manifest, a developer could advance them without regenerating baselines, passing the guard while the suite is red. *Likelihood: Med / Impact: High.* **Mitigation**: FR-2 emits the sidecar **as the last step of the executable regen script** so it cannot be advanced without a real regen (the manifest fallback forfeits this — OQ-1).

**Risk-2 — False-red on count-neutral edits.** A file-diff-based guard would block #333-class citation edits. *Likelihood: High if mis-designed / Impact: High (trust erosion).* **Mitigation**: FR-3 makes the guard strictly fingerprint-based; FR-7(d) proves it against the real #333 change shape.

**Risk-3 — Stale-cache false-green test.** The `lru_cache` on `_load_framework_yaml_records` can make a synthetic case read stale records and pass for the wrong reason. *Likelihood: Med if unaware / Impact: High (a guard that lies).* **Mitigation**: FR-7 mandates `cache_clear()` (or monkeypatch) per case (C3).

**Risk-4 — `main` already red at T001.** If the pre-state finds the suite red today, the guard would correctly start failing immediately. *Likelihood: Low (git evidence: F-185 left it green; only count-neutral member edits since) / Impact: Med.* **Mitigation**: T001 front-loaded as a go/no-go gate (C2); a bounded baseline remediation precedes the guard going green if needed.

**Risk-5 — Sidecar deleted/partial to silence the guard.** *Likelihood: Low / Impact: Med.* **Mitigation**: FR-8 fails closed on missing/partial/unparseable sidecar.

### Dependencies
- **Internal**: `scripts/extract-report-data.py` (`_load_framework_yaml_records`, the two count functions, `ORDERED_FRAMEWORKS`); the manual regen recipe `baseline-regen.contract.md` (to be promoted to a script, FR-2); the 6 `examples/*/security-report.pdf.baseline` files; `tachi-maestro-coverage.yml` + `tachi-pytest.yml` (pattern references, not modified); local Typst (0.14.2 confirmed installed) for T001 + the regen script only.
- **External**: none (no new dependency; GitHub Actions only).

---

## ❓ Open Questions

- [ ] **OQ-1 (Architect, /aod.plan — load-bearing)**: Confirm the sidecar mechanism = "emitted as the last step of a newly-formalized executable CA-baseline regen script" (recommended, cheat-resistant) vs. a hand-maintained manifest fallback (forfeits Risk-1 mitigation). Resolves FR-2 + Risk-1 + Assumption 2.
- [x] **OQ-2 (resolved — Architect)**: Defer option (a). NFR-1 determinism rationale confirmed correct.
- [ ] **OQ-3 (Build, T001)**: Is `test_backward_compatibility.py` green on `main` right now? (Record literal pre-state totals per KB-15; git evidence says yes.)
- [x] **OQ-4 (resolved — both reviewers)**: New dedicated `tachi-catalog-drift.yml`, single-runner — NOT a job in `tachi-pytest.yml`.
- [x] **OQ-5 (resolved — Architect)**: Amend ADR-037 (count→fingerprint guard + sidecar contract + (a)-deferral). Not a standalone ADR.
- [ ] **OQ-6 (PM/Build, /aod.plan)**: Disposition the `#329`-tagged init.sh-substitution xfail (`test_init_sh_substitution.py:35`) — re-tag to a dedicated fixture-regen item, or fold a tiny `init-baseline-tree` regen in? Recommendation: re-tag / track separately (out of scope here).

---

## 📚 References

- **Issue**: [#329](https://github.com/davidmatousek/tachi/issues/329) (type:retro, BLP-06 CI-hardening tail lead)
- **KB Entry 15** (`docs/INSTITUTIONAL_KNOWLEDGE.md`): F-185 consequence-scope lesson — the `ORDERED_FRAMEWORKS` membership predicate and the silent-red-main mechanism this guard backstops.
- **KB Entry 13**: F-186 (ATLAS 30→36) — the triggering incident. **KB Entry 18**: F-338 — the `push:[main]` dual-trigger lesson reused by FR-5.
- **Coupling source**: [`scripts/extract-report-data.py:1077`](scripts/extract-report-data.py#L1077) (`ORDERED_FRAMEWORKS`), [`:1090`](scripts/extract-report-data.py#L1090) (`_load_framework_yaml_records`, `@lru_cache`), `:1140`/`:1152` (raw count), `:1155`/`:1168` (in-scope count).
- **Byte-identity suite**: [`tests/scripts/test_backward_compatibility.py`](tests/scripts/test_backward_compatibility.py); baselines at `examples/*/security-report.pdf.baseline`.
- **Regen recipe (to be scripted, FR-2)**: `specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md` (ADR-037 D-9 lane). **NOT** `tests/fixtures/regenerate-baseline.sh` (that is the unrelated F-248 init.sh fixture regen — HIGH-1).
- **CI patterns**: [`.github/workflows/tachi-maestro-coverage.yml`](.github/workflows/tachi-maestro-coverage.yml) (near-exact structural template — single-runner, reuses a canonical fn, fails naming the entity); [`.github/workflows/tachi-pytest.yml`](.github/workflows/tachi-pytest.yml) (the `&anchor`/`*anchor` dual-trigger + path-filter lock-step discipline).

---

## ✅ Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-06-30 | v1.1 folds all Triad corrections; see frontmatter notes. |
| Architect | architect | 🟡 Approved with Concerns | 2026-06-30 | Fork ratified (ship b / defer a). 0 blockers; HIGH-1/2/3 folded; OQ-1 carried to plan. `.aod/results/architect-prd-329.md`. |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-06-30 | Estimate 1.0/1.5/3.0d. 0 blockers; C1/C2 folded (FR-2 + T001 front-load). `.aod/results/team-lead-prd-329.md`. |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-30 | product-manager | Initial PRD — drafted via ~aod-define; Feature workflow; evaluates issue #329's (a)-vs-(b) fork and recommends the count-drift guard (b). |
| 1.1 | 2026-06-30 | product-manager | Folded all Triad corrections (both APPROVED_WITH_CONCERNS, 0 blockers). FR-1 upgraded count→fingerprint (closes HIGH-2 ID-swap + HIGH-3 out_of_scope-flip); FR-2 corrected (regenerate-baseline.sh was the wrong artifact — HIGH-1; promote the manual recipe to an executable regen script that emits the sidecar); FR-8 added (fail-closed); FR-7 cache_clear() (C3); FR-5 dedicated workflow + lock-step + single-runner-as-determinism (MED-3/4, C4); NFR-1/3 pinned-pyyaml honesty (MED-2); MED-1 corrected (the #329 xfail is the init.sh surface — scoped out, OQ-6); T001 front-loaded (C2); estimate 0.75/1.5/2.5 → 1.0/1.5/3.0; OQ-2/4/5 resolved. |
