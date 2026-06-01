# Delivery Document: Feature 305 — Adoption Signal Capture (F-3, BLP-04 Wave 3)

**Delivery Date**: 2026-06-01
**Branch**: `305-adoption-signal-capture` (merged + deleted)
**PR**: #306 (squash-merged as `b89cf46`)
**Release**: release-please PR #307 — `chore(main): release 4.38.0`

---

## What Was Delivered

This feature delivers **receiving infrastructure, not content** — the in-repo artifacts form a viable MVP; platform-config and outreach layer activation on top (post-merge tail).

- **Self-serve submission path** (US-1, P1): `docs/adopters/case-study-template.md` — 5 required sections (org/identifier, scale of use, integration point, capabilities used, outcomes) + 3 optional (logo, pull-quote, external public-reference link), with a required **Consent block** (publish org name? · use logo? · preferred attribution + contact) and an explicit **default-deny** note — absent a `yes`, nothing identifying is published (FR-001, FR-002).
- **Discoverable adopters index** (US-4, P2): `docs/adopters/README.md` — accepted-case-study list with a valid, non-broken **empty state** at launch and a "How to submit" pointer routing to the template + the "In the Wild" channel (FR-003).
- **Inbound ledger** (US-3, P1): a gitignored append-only **signal-log subsection** in `_internal/strategy/BLP-03-signed-updates.md` — canonical shape **date · source · signal-type · decision** (`signal-type ∈ {inquiry, citation, procurement-mention, traffic, adopter-story}`), distinct from the existing re-evaluation table (no schema overload), primed with ≥1 genuine entry. Never committed (FR-006).
- **Release framing + cross-links**: `CHANGELOG.md` `feat(305):` entry under a sibling `### … (BLP-04 Wave 3)` heading (FR-007); README §Community "In the Wild" line augmented to also point at `docs/adopters/` (no duplicate link) (FR-016).
- **Pre-merge acceptance gate** (Gate C / T018): privacy/consent pass (FR-008) + positioning-neutrality scan (FR-009) over **all** public artifacts incl. the auto-appended `docs/architecture/01_system_design/README.md` Feature-305 section (Data-Flow diagram **and** prose) — 0 findings; no application code, no new ADR (FR-012); `git status` clean of any `_internal/` path.

**Out of scope / by design**: actual case-study content and inbound responses are **exogenous** — F-3 closes on endogenous SC-001…SC-009, NOT on the ≥1-case-study / ≥3-signal *capture* (SC-010, a measurability assertion = BLP-04 initiative-level DoD).

---

## How to See & Test

1. **Template completeness (SC-001/002)**: open `docs/adopters/case-study-template.md` → 5 required + 3 optional sections present and labeled; consent block has all 3 prompts + default-deny note.
2. **Index renders + empty state (SC-003)**: open `docs/adopters/README.md` on GitHub → "How to submit" routes to template + channel; empty state valid; internal links resolve.
3. **Signal log canonical + private (SC-007/009)**: inspect the gitignored `_internal/strategy/BLP-03-signed-updates.md` signal-log subsection → four-field shape, closed-enum signal-type, distinct from the re-eval table; `git status` shows no `_internal/` path.
4. **CHANGELOG entry (SC-008)**: `grep -A2 "BLP-04 Wave 3" CHANGELOG.md` → `feat(305):` adopter case-study + signal-capture framing.
5. **Positioning-neutrality (FR-009)**: scan `docs/adopters/*`, the CHANGELOG entry, the README cross-link, and the system-design 305 section → no commercial/pricing/competitor/buyer-signal/BLP-03 framing in any public surface.
6. **Full SC recipe**: see [quickstart.md](quickstart.md).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | ~1 day (same-day define→plan→build→deliver, 2026-06-01) |
| Variance | On-target |

---

## Surprise Log

Smooth sailing — same-day define→plan→build→deliver with all three Triad sign-offs (APPROVED_WITH_CONCERNS, 0 blocking) and the pre-merge acceptance gate (Gate C) passing with 0 blocking findings.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process Improvement | For docs/outreach features with a post-merge maintainer tail, merge the in-repo MVP first (release-please fires on the `feat(NNN):` squash regardless of the pending tail) and split success criteria into **endogenous** (close-gate: the ≥3 outreach *sends*, SC-005) vs **exogenous** (measurability-only: inbound capture, SC-010). GitHub auto-closes the feature issue on merge — *before* the tail runs — so reopen it as the tracking anchor and close it deliberately (T021) only once the endogenous gate is met. | Entry 10 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None — the only successor (F-4 MAESTRO 7-layer, #98) is already tracked as BLP-04's final wave.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/305-adoption-signal-capture/spec.md |
| Implementation Plan | specs/305-adoption-signal-capture/plan.md |
| Task Breakdown | specs/305-adoption-signal-capture/tasks.md |
| PRD | docs/product/02_PRD/305-adoption-signal-capture-2026-06-01.md |
| Data Model | specs/305-adoption-signal-capture/data-model.md |
| Quickstart | specs/305-adoption-signal-capture/quickstart.md |
| Session Handoff | specs/305-adoption-signal-capture/NEXT-SESSION.md |
| ADR | None — FR-012: docs + platform-config, no architectural decision |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This is a **docs + GitHub platform-config feature with no application code** (FR-012). Per the docs-only DoD (Constitution Principle VII §Exceptions; KB Entry 4), there are **no automated test tasks** — verification is **manual inspection** (in-repo) + **post-merge attestation** (platform/outreach). The active pack (`knowledge-system`) declares no E2E test contract, so the `/aod.deliver` E2E validation gate is not applicable.

| Verification | Method | Status |
|--------------|--------|--------|
| T005 (template completeness, SC-001/002) | manual inspection (tester) | ✅ PASS |
| T010 (signal-log canonical + private, SC-007/009) | manual inspection (tester) | ✅ PASS |
| T012 (index renders + empty state, SC-003) | manual inspection (tester) | ✅ PASS |
| Gate B (T017 outreach tone-review vs house voice) | PM review | ✅ PASS |
| Gate C (T018 privacy/consent + positioning-neutrality) | security-analyst + PM + architect | ✅ PASS — 0 findings |

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | skipped |
| Gate Mode | n/a (no stack E2E contract) |
| Gate Result | skip |
| Skip Reason | Active pack `knowledge-system` declares no `e2e_command`; docs-only feature, no application code (FR-011 backward-compat path) |

**Failure Details**: N/A

#### Build-Wave Test Results

From `specs/305-adoption-signal-capture/test-results/summary.json`:

| Field | Value |
|-------|-------|
| Total Waves | 7 |
| Waves Tested | 0 |
| Waves Skipped | 3 |
| Skip Reason | Docs + GitHub platform-config feature, no application code (FR-012); not in the `tachi-pytest.yml` CI `paths:` filter (plan D8); Constitution VII §Exceptions — DoD mapped to manual inspection. `git diff` shows only `.md` changes. Not a silent skip. |
| Regressions | 0 |

**Build Summary**: `waves_tested: 0` recorded with explicit `skip_reason` — the correct, expected outcome for a docs-only feature, not a bypass.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 (`docs/product/02_PRD/INDEX.md` → "Delivered (MVP; post-merge tail pending)") | ✅ pass |
| Architecture | architect | 0 (docs-only feature; no tech-stack/ADR/arch change; existing system-design 305 section intact) | ✅ pass (verified no-op) |
| DevOps | devops | 0 (no CI/env/deploy surface touched) | ✅ pass (verified no-op) |

---

## Post-Merge Tail — Resolved (2026-06-01)

The post-merge tail was worked the same day. Platform tasks completed; the outreach send was deferred by maintainer decision. **Issue #305 closed (`stage:done`) 2026-06-01.**

| Task | Action | Status |
|------|--------|--------|
| T019 | Merge + release-please verify | ✅ **DONE** — PR #306 merged `b89cf46`; #307 release 4.38.0 opened |
| T007/T008 | Publish "In the Wild" welcome post; verify links | ✅ **DONE** — [Discussion #309](https://github.com/davidmatousek/tachi/discussions/309); links resolve. *(Pin + category-description are UI-only — GitHub exposes no `pinDiscussion`/category-description API; left as optional maintainer clicks.)* |
| T013/T014 | AIVSS v1.0 tracking comment + pin on **#168** | ✅ **DONE** — comment posted, #168 pinned (`pinIssue`) |
| T020 | ≥3 warm-outreach sends (endogenous SC-005) | ⏸️ **DEFERRED (maintainer decision)** — descoped from the close gate; it is an optional activation step, not delivered infrastructure. Tone-gated message copy + enumerable candidate set (@north-echo, @armorer-labs, @maorkuriel, @ChrisJr404) preserved in #305 for optional later use |
| T021 | Close #305 with deliverable URLs | ✅ **DONE** — #305 closed `stage:done` with deliverable URLs + `_internal/` signal-log cross-link |

**Close model (as resolved)**: the receiving infrastructure (SC-001/002/003/004/006/007/008/009) is delivered. SC-005 (outreach sends) was consciously **deferred**, not completed — recorded honestly rather than claimed. SC-010 (inbound capture) stays exogenous (BLP-04 initiative-level DoD, never an F-3 gate).

---

## Cleanup

- [x] Feature branch deleted (local + remote, pruned)
- [x] In-repo MVP delivered (14/21 build tasks); platform tail (T007/T008, T013/T014, T019) completed; T020 outreach deferred
- [x] No new TBD/TODO in committed docs
- [x] Committed and pushed (delivery docs → main)
- [x] GitHub Issue #305 closed (`stage:done`) — outreach (SC-005) deferred by maintainer decision, copy + candidates preserved in-issue

**Feature 305 is DELIVERED and RELEASED (v4.38.0 via #307); Issue #305 CLOSED 2026-06-01. The adopter receiving-infrastructure (template, index, "In the Wild" welcome post, AIVSS watch, signal log) is live; the ≥3-send outreach (SC-005) was deferred by maintainer decision as an optional activation step.**
