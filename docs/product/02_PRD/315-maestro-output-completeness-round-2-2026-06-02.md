---
prd:
  number: 315
  topic: maestro-output-completeness-round-2
  created: 2026-06-02
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-06-02, status: APPROVED, notes: "Authored via /aod.define. Scope SPLIT per unanimous reviewer recommendation (Q5 split valve exercised, user-confirmed): F-315 = US-2 (#312) + US-3 (#313) only; US-1 Model B (#311) carved into its own ADR-bearing feature. The split RESOLVES both reviewers' HIGH findings and the entire Q-A1 ADR (all US-1-specific) and isolates the NFR-1 cross-surface-consistency hazard from the front-light pair. Remaining plan-stage items are US-2/US-3 only (script-emit counts, dedicated CI job, regen-order, US-3∥US-2 parallelism). Accuracy corrections folded inline. Provenance corrected: v4.39.0 NOT yet released (PR #314 OPEN; F-098 code merged to main ac07085)."}
  architect_signoff: {agent: architect, date: 2026-06-02, status: APPROVED_WITH_CONCERNS, notes: "Reviewed full bundle: 0 BLOCKING / 2 HIGH / 3 MEDIUM / 3 LOW. ALL 3 PRD accuracy corrections CONFIRMED vs live repo, 0 inaccuracies + 1 FAVORABLE nuance (maestro-stack infographic is SCRIPT-FED not prose-authored → lower NFR-1 risk). Both HIGHs (HIGH-1 FR-1 derivation/home; HIGH-2 NFR-1 over-weight) and the sole ADR (Q-A1, 3 options incl. recommended Section-6-carried-state) are US-1-specific → RESOLVED by the split; they transfer to #311's feature along with MEDIUM-1 (cite existing 3-state coverage-matrix-model.md n/a prior art). Carried into F-315 (US-2/US-3): MEDIUM-2 (script should compute+emit empty_layers/layers_with_findings, agent renders not counts — folded FR-2); MEDIUM-3 (Q-C1 → DEDICATED CI job, not allowlist expansion — folded FR-3); LOW-1 (regen upstream threats.md via populate-maestro-coverage.py BEFORE PDFs in one deterministic pass — folded FR-4); LOW-2 (don't expand gated baseline set — folded Q2). Security: non-issue (local-first, no schema change, n/a reveals less than Section-1 table). Full review .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-06-02, status: APPROVED_WITH_CONCERNS, notes: "Reviewed full bundle: 0 BLOCKING / 2 HIGH / 3 MEDIUM / 2 LOW. HEADLINE: SPLIT NOW — both Q5 sub-triggers (US-1 ≥ ½ bundle effort AND ADR with non-trivial blast radius) already met by file-level inspection (US-1 reaches 3 renderers across two 2000+-line scripts + prose directives). Split TAKEN + user-confirmed → H-1 satisfied, H-2 (NFR-1/SC-6 dedicated task+fixture) transfers to #311. Carried into F-315: M-1 (US-3 ∥ US-2 — zero shared files/deps → model as one parallel wave, folded §Sequencing); M-2 (Q-C1 → dedicated MAESTRO job per repo scope-hygiene convention, concurs architect MEDIUM-3 — folded FR-3); M-3 (#311 carve-out needs own issue [exists] + own feat + ADR on its own branch). CALENDAR PASS (today 2026-06-02 Tue; 0 forward-dated build dates; deferred to /aod.tasks). CAPACITY: full headroom (0 in-flight builds; only non-blocking release PR #314). L-2: v4.39.0 not yet cut (#314 OPEN) — merge before/alongside F-315 branch. Full review .aod/results/team-lead.md."}
source:
  idea_id: 315
  story_id: null
---

# Feature 315 — MAESTRO Output Completeness (Round 2): Infographic + CI Durability

**Status**: Approved (scope split per reviewer recommendation; MEDIUM/LOW concerns folded inline; residual items → `/aod.plan`)
**Created**: 2026-06-02
**Spec**: TBD (will land at `specs/315-maestro-output-completeness-round-2/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead (both APPROVED_WITH_CONCERNS on the full bundle; split resolves the HIGH findings)
**Type**: Feature (output fidelity)
**Priority**: P1 (High) — *front-light pair; effort reduced from the umbrella bundle by the US-1 carve-out*
**Parent**: Follow-on cluster to **Feature 098** (MAESTRO 7-layer coverage matrix). **NOT a BLP-04 wave** — BLP-04 closed 4/4 on 2026-06-02; per BLP-04 §3 scope discipline, output-fidelity follow-ons live outside the closed initiative.
**Source**: Umbrella Issue [#315](https://github.com/davidmatousek/tachi/issues/315) (captured + ICE-seeded 2026-06-02). This feature delivers **US-2 ([#312](https://github.com/davidmatousek/tachi/issues/312)) + US-3 ([#313](https://github.com/davidmatousek/tachi/issues/313))**.
**Carved out**: **US-1 Model B two-state annotation ([#311](https://github.com/davidmatousek/tachi/issues/311))** is split into its **own ADR-bearing feature** (unanimous Architect + Team-Lead recommendation, user-confirmed 2026-06-02 — see §Carve-Out). It is **out of scope here.**
**ICE**: umbrella #315 scored 22 (I 8 / C 7 / E 7) for all three stories; post-split this feature is the front-light, lower-effort subset (formal re-score deferred — `/aod.score` if needed).

---

## 📋 Executive Summary

### The One-Liner

Finish the visible and durable half of the F-098 "always show all 7 MAESTRO layers" story — make the `maestro-stack` infographic render all seven layer bands (zero-finding layers muted, not omitted), and lock the 7-row guarantee into CI with a dedicated job plus a deterministic refresh of the drifted example PDFs — while the semantic "clean vs n/a" upgrade (US-1 Model B) ships separately as #311.

### Problem Statement

Feature 098 made the `threats.md` "Risk by MAESTRO Layer" table and the PDF "MAESTRO Layer Analysis" page **always render all 7 canonical layers (L1–L7)**, annotating each zero-finding layer with `Analyzed — no findings this scan`. Two parts of that story were explicitly deferred and remain open:

1. **The shareable visual is unverified (US-2 / #312).** The matrix and PDF now guarantee 7 layers, but the `maestro-stack` infographic — the artifact a reader is most likely to screenshot and share — has no enforced all-7 guarantee. Its template *already specifies* all seven bands; the gap is in the **data path and agent enumeration**: the count of empty layers is filled by the generating agent from per-layer data rather than computed deterministically, so completeness depends on incidental data flow. The sibling `maestro-heatmap` infographic already renders empty intersections and is unaffected. Risk: the most-shared output visually contradicts the matrix's completeness.

2. **The guarantee is unprotected in CI (US-3 / #313).** An invariant test (`tests/scripts/test_maestro_coverage_invariant.py`) asserts the 7-row guarantee across example reports, but it is **intentionally not wired into CI** (per its own header comment). A future refactor of the parser or renderer could silently drop below 7 rows with no failing check. Separately, several committed example PDFs have drifted from current content and need a deterministic refresh.

The cost is asymmetric: F-098 already paid for the hard structural fix. Leaving the visual surface unverified and the guarantee ungated means the headline output (matrix), the shareable output (infographic), and the regression net (CI) tell inconsistent stories about MAESTRO coverage — the exact credibility surface tachi sells.

### Proposed Solution

Two independent, front-light stories that can run as a single parallel wave (zero shared files, zero cross-dependency):

1. **US-2 — `maestro-stack` infographic completeness (#312, moderate, visual).** Ensure all seven layer bands render (zero-finding muted), and push the empty-layer/with-findings **counts into the script's deterministic JSON payload** so the agent renders rather than counts.
2. **US-3 — CI durability (#313, small, quick win).** Add a **dedicated MAESTRO CI job** that runs the invariant test (failing, and naming the missing layer, on any <7-row regression), and deterministically refresh the drifted non-gated example PDFs.

### Scope

**In Scope (this feature)**:
- **US-2 (#312):** `maestro-stack` infographic renders all 7 layer bands in canonical L1→L7 order, zero-finding layers muted; the maestro-stack JSON payload emits `empty_layers` / `layers_with_findings` counts deterministically; agent directive (`threat-infographic.md`) enumerates all 7 bands.
- **US-3 (#313):** `test_maestro_coverage_invariant.py` gated by a dedicated CI job; non-gated example PDFs refreshed deterministically (upstream `threats.md` regenerated first).
- `CHANGELOG.md` entry; delivering PR `Closes #312 + #313` (umbrella #315 closed when both land).

**Out of Scope (deferred / belongs elsewhere)**:
- ❌ **US-1 Model B two-state ("clean" vs "n/a") annotation** — carved to its own feature, **Issue #311** (see §Carve-Out). All cross-pipeline plumbing, the Q-A1 ADR, and the cross-surface consistency fixture belong there.
- ❌ **`maestro-heatmap` infographic changes** — already renders empty cells; verified unaffected.
- ❌ **`threat-report.md` per-layer roster** — no such roster exists; net-new structure, not polish (Architect-confirmed exclusion in F-098).
- ❌ **SARIF / output-schema changes** — already structured; no schema change.
- ❌ **Frozen `examples/**/test-output/**` snapshots** — historical artifacts, intentionally not regenerated.
- ❌ **Changing the F-098 Model A guarantee** — all-7 rendering and the existing clean annotation string are preserved unchanged.

---

## 🎯 User Stories

> Job-Story format (Intercom). Preserved in substance from Issues #312 / #313.

**US-2 — Complete infographic (maintainer / sharer)**
**When** I generate or share the `maestro-stack` infographic, **I want** all seven MAESTRO layers visible (zero-finding layers muted, not omitted), **so** the shareable visual matches the matrix's all-7 completeness and doesn't read as "only N layers assessed."
*AC*: Given any scan, when the `maestro-stack` infographic is generated, then all 7 layer bands appear in canonical L1→L7 order, zero-finding layers are visually muted/dashed, and the empty-layer count is correct and derived from a deterministic source. The `maestro-heatmap` infographic is unchanged.

**US-3 — Regression-proof guarantee (maintainer)**
**When** a future change touches the matrix renderer, the parser, or the example reports, **I want** CI to fail if any MAESTRO matrix drops below 7 rows, **so** the F-098 guarantee can't silently regress, and **I want** the committed example PDFs to match current output deterministically.
*AC*: Given a change that would render a MAESTRO matrix with <7 canonical layers, when CI runs, then a dedicated job fails and names the missing layer ID(s). Given the non-gated example PDFs, when regenerated under the deterministic build (`SOURCE_DATE_EPOCH`), then they match current content; the 6 byte-gated baselines remain byte-identical.

---

## ✅ Functional Requirements

### US-2 — `maestro-stack` infographic completeness (#312, Moderate)

**FR-1 — All-7 band rendering.** The `maestro-stack` infographic (`templates/tachi/infographics/infographic-maestro-stack.md`) MUST render all 7 layer bands in canonical L1→L7 order, with zero-finding layers muted. *(Accuracy note: the template prose already specifies all-7; the gap is the data path + agent enumeration. Post-F-098 the upstream Section-6 distribution now feeds 7 rows — FR-1 verifies/locks that path rather than rewriting the template.)*

**FR-2 — Deterministic empty-layer counts.** The `maestro-stack` JSON payload produced by `scripts/extract-infographic-data.py` (the `--template maestro-stack` `template_data` block) MUST compute and emit `empty_layers` and `layers_with_findings` counts, so the generating agent **renders** these values rather than counting them. *(Architect MEDIUM-2: pushes determinism upstream, removes an LLM counting step; same principle that makes completeness not depend on incidental data flow.)* The agent directive (`threat-infographic.md`) gains an explicit instruction to enumerate all 7 bands and consume the emitted counts.

### US-3 — CI durability (#313, Small / quick win)

**FR-3 — Dedicated CI job for the invariant test.** `tests/scripts/test_maestro_coverage_invariant.py` MUST run in CI via a **dedicated MAESTRO coverage job** (not by expanding `tachi-pytest.yml`'s allowlist), such that a MAESTRO matrix regressing below 7 canonical layers fails the build and names the missing layer ID(s). *(Architect MEDIUM-3 + Team-Lead M-2: `tachi-pytest.yml` is a path-filtered, file-allowlist job semantically scoped to init.sh/asset-tag surfaces on a 2-OS bash matrix; bolting MAESTRO on muddies its identity, burns 2× minutes, and risks NFR-4. A dedicated single-OS ubuntu / py3.11 + pytest job (~25 lines) firing on MAESTRO-relevant paths — `examples/**/threats.md`, `scripts/tachi_parsers.py`, `scripts/extract-report-data.py`, the orchestrator directive, the Typst template, the test file — gives correct triggering and self-explaining failures.)* The test file's "intentionally NOT wired into CI" comment is removed on wiring.

**FR-4 — Deterministic refresh of non-gated example PDFs.** Regenerate the drifted non-gated example PDFs deterministically (`SOURCE_DATE_EPOCH=1700000000`): at minimum `examples/maestro-reference/security-report.pdf` and the `sample-report` PDFs/baselines under `agentic-app`, `consumer-agent-app`, `mobile-banking-app`, `predictive-ml-app`. **Regenerate the upstream `threats.md` first** (via the F-098 regeneration-only harness `scripts/populate-maestro-coverage.py`) so any example whose `threats.md` predates F-098's all-7 output is brought current in the **same deterministic pass** — a row-count content change, not drift *(Architect LOW-1)*. The 6 byte-gated baselines (`test_backward_compatibility.py:BASELINE_EXAMPLES`) MUST remain byte-identical. Frozen `test-output/` snapshots are untouched.

---

## 🔒 Non-Functional Requirements

- **NFR-1 — Build determinism.** All PDF regeneration MUST be byte-reproducible under `SOURCE_DATE_EPOCH=1700000000`; the 6 gated baselines stay byte-identical; no nondeterministic timestamps introduced.
- **NFR-2 — No F-098 regression.** All-7 rendering and the existing `Analyzed — no findings this scan` annotation remain intact; the invariant test MUST pass for current clean architectures.
- **NFR-3 — Backward compatibility.** No SARIF / output-schema field changes; existing consumers of `threats.md` and the PDF are unaffected.
- **NFR-4 — CI scope hygiene.** The new MAESTRO CI job MUST fire only on MAESTRO-relevant paths and MUST NOT cause `tachi-pytest.yml` (or any unrelated job) to fire spuriously. (Drives the dedicated-job decision in FR-3.)
- **NFR-5 — `maestro-heatmap` untouched.** The heatmap infographic already renders empty cells; this feature MUST NOT alter it.

---

## 🏛️ Architecture Notes (for plan/spec)

- **Canonical layers** (`scripts/tachi_parsers.py:MAESTRO_LAYERS`): L1 Foundation Model, L2 Data Operations, L3 Agent Framework, L4 Deployment Infrastructure, L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem.
- **US-2 is script-fed, not prose-authored** (Architect accuracy nuance L): `extract-infographic-data.py --template maestro-stack` emits deterministic `per_layer_summaries` JSON; the agent renders the template from that JSON and fills `{empty_layers}`/`{layers_with_findings}`. FR-2 moves the counting into the script — a small, contained, deterministic change. **No ADR required for this feature** (the only ADR, Q-A1, went with US-1 to #311).
- **Upstream completeness source**: post-F-098 the orchestrator emits all 7 rows in Section 6; both the PDF parser (`extract-report-data.py:parse_maestro_data`) and the infographic parser carry them through without padding. FR-1 relies on that already-shipped behavior.
- **Determinism harness already exists**: F-098 shipped `scripts/populate-maestro-coverage.py` (regeneration-only, not wired into any command) and uses `SOURCE_DATE_EPOCH` for byte-gated baselines. FR-4 reuses this discipline.
- **No new runtime dependencies**; reuses stdlib parsers + the existing Typst toolchain.

---

## ❓ Open Questions (resolve in `/aod.plan`)

- **Q1 (US-3, CI):** Confirm the dedicated-job shape (single-OS ubuntu, py3.11 + pytest) and the exact `paths:` trigger set. *Recommendation (both reviewers): dedicated job — already folded into FR-3; the plan finalizes the yml.*
- **Q2 (US-3, baselines):** After FR-4 refresh, do any non-gated PDFs get promoted into the byte-gated `BASELINE_EXAMPLES` set? *Recommendation (Architect LOW-2): no — do not expand gating in this feature; refreshed files' content is changing in-feature.*
- **Q3 (US-2, rendering):** Exact muted treatment for zero-finding bands (grayed fill vs dash label) — align with the template's existing prose. Visual-only; resolve in spec.
- **Q4 (US-3, regen ordering):** Confirm the single-pass order (regenerate `threats.md` via `populate-maestro-coverage.py` → then PDFs) and which example apps' `threats.md` predate F-098 all-7. *Folded into FR-4; plan enumerates the exact file set.*

---

## 📏 Success Criteria

- **SC-1:** `maestro-stack` infographic renders all 7 layer bands (zero-finding muted) in canonical order; `maestro-heatmap` unchanged. *(US-2)*
- **SC-2:** The maestro-stack JSON payload emits correct `empty_layers` / `layers_with_findings` counts; the agent consumes them rather than counting. *(US-2)*
- **SC-3:** A dedicated CI job runs `test_maestro_coverage_invariant.py` and fails — naming the missing layer ID(s) — on any <7-row regression; it does not cause unrelated jobs to fire. *(US-3)*
- **SC-4:** Non-gated example PDFs (and their upstream `threats.md`) refreshed deterministically; the 6 byte-gated baselines remain byte-identical. *(US-3)*
- **SC-5:** Delivering PR `Closes #312 + #313`; umbrella #315 closed; **#311 remains open** as the carved Model-B feature.

---

## 🔗 Dependencies & Sequencing

- **One parallel wave.** US-2 (#312) and US-3 (#313) share **no files and no dependency** — US-2 touches the infographic template + `extract-infographic-data.py` + `threat-infographic.md`; US-3 touches `.github/workflows/`, the invariant test, and example PDFs. They can run **concurrently** *(Team-Lead M-1)*. Neither depends on the carved US-1/#311.
- **External dependencies:** none beyond F-098 deliverables already in `main` (squash `ac07085`). No new runtime libraries.
- **Release-state note (Team-Lead L-2):** v4.39.0 is **not yet cut** — release PR [#314](https://github.com/davidmatousek/tachi/issues/314) is OPEN. F-098 code is in `main`; merge #314 before/alongside F-315 branch creation so the "F-098 released" premise is literally true at delivery, and verify the F-315 delivery itself yields a release-please PR (deliver-release gate).

---

## ✂️ Carve-Out: US-1 Model B → Issue #311 (separate feature)

Per unanimous Architect + Team-Lead recommendation (user-confirmed 2026-06-02), the **Model B two-state ("clean" vs "n/a") annotation is removed from this feature** and tracked as its own ADR-bearing feature on Issue #311. Carried to #311's planning:

- **Scope:** distinguish *clean* (analyzed, ≥1 mapped component, 0 findings) from *n/a* (no component maps) across the matrix, PDF, and infographic.
- **ADR (Q-A1):** evaluate **three** options — (a) parser-derived shared module in `tachi_parsers.py`, (b) port/duplicate (rejected), (c) **Section-6-carried-state** (orchestrator encodes clean/n/a in the existing `Highest Severity` cell; both downstream scripts inherit it → NFR-1 becomes *structural*). **Architect recommendation: (c).**
- **Prior art (Architect MEDIUM-1):** reuse the existing three-state model in `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md` (count / `---` clean / `n/a`) — it already answers the "n/a wording / semantics" questions; do not reinvent.
- **Cross-surface consistency (Team-Lead H-2):** the n/a-layer fixture consistency check is **net-new test scaffolding** and must be its own task with its own fixture — the dominant risk and the reason for the carve-out.
- **Tracking (Team-Lead M-3):** #311 gets its own `feat(311)` branch/PR and its ADR lands on that branch; pre-allocate at its `/aod.define`.

---

## 📦 Provenance / Evidence

- Follow-on to **Feature 098** (PR #310, squash `ac07085`). **Release status:** v4.39.0 **not yet cut** — release-please PR #314 OPEN as of 2026-06-02 (latest cut release v4.38.0). F-098 code is merged to `main`. Source-of-truth: `specs/098-maestro-7-layer/{spec,delivery,plan}.md` + KB Entry 11.
- Component issues: [#312](https://github.com/davidmatousek/tachi/issues/312) (infographic FR-012, in scope), [#313](https://github.com/davidmatousek/tachi/issues/313) (CI durability, in scope), [#311](https://github.com/davidmatousek/tachi/issues/311) (Model B, **carved out**) — all `follow-on-98`, board-synced 2026-06-02.
- Current-state grounding verified against the live repo on 2026-06-02 (both infographic templates, `extract-infographic-data.py`, `test_maestro_coverage_invariant.py`, `tachi-pytest.yml`, `BASELINE_EXAMPLES`, `SOURCE_DATE_EPOCH`); Architect confirmed all three of the PRD's accuracy corrections with 0 inaccuracies. Reviews: `.aod/results/architect.md`, `.aod/results/team-lead.md`.

---

## 📈 Metadata

- **Source:** F-098 follow-on triage (2026-06-02)
- **Priority:** P1 (High)
- **Origin Feature:** F-098 MAESTRO 7-layer coverage matrix
- **Initiative:** none (standalone output-fidelity cluster; explicitly not BLP-04)
- **Scope change:** US-1 Model B (#311) carved out 2026-06-02 per Triad recommendation (split valve / Q5)
