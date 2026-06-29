---
description: "Task list for F-333 Citation-URL Remediation (BLP-06 Wave 1)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED
    notes: "tasks.md faithfully realizes the PM-approved spec + dual-approved plan; full FR/US traceability (US1–US4 ↔ FR-001…FR-008). Research-first discipline structurally enforced — T006 architect fork GATE blocks all apply tasks; no edit (T008/T009/T011/T012/T014) precedes it. Zero scope creep: all 7 Out-of-Scope boundaries held; #325 only documented-deferred (T002+T020), not folded. All carry-forwards honored — M1 (feature-P0 note), M2 (#325 defer = T002+T020), M3 (spot-check 1 NIST + 1 OWASP = T018), M4 (#332 non-close → re-adjudicate = T017). 4 findings, MINOR/observational, 0 blocking. Full: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-06-29
    status: APPROVED_WITH_CONCERNS
    notes: "Dependency ordering verified correct (W0 T003–05 → T006 gate → W1 US1–US3 → US4 aggregate; US4 ⊇ US1+US2+US3; T017 strictly last). Parallel claims real and file-disjoint on the default path. All 5 pattern checks confirmed against actual code at the cited lines — _verdict_for_status receives url (:447), frozensets untouched (:288/:290), --no-cache/should_skip plumbed (:923/:568), Verdict enum (:91-92). OBS-1 (T009) + OBS-2 (T006) folded verbatim; split-valve trigger captured (T006/T008). No ADR-021 breach — only live steps are [MANUAL-ONLY] deliver-adjacent. 1 should-fix OBS-3 (reuse existing tests/schemas/test_citation_linkrot_parity.py importlib loader/socket guard) — FOLDED into T007. 0 blocking. Full: .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-06-29
    status: APPROVED_WITH_CONCERNS
    notes: "Critical path (W0→T006 gate→US1→US4, T017 deliver-async), parallelization, agent balance, split-valve (C2), #325 deferral, C6, and the 3.0d estimate all correct/hold; repo cross-check confirmed _verdict_for_status takes url (split-valve correctly unlikely) and ATLAS re-classify is URL-preserving. 1 HIGH + 1 MED + 4 LOW/INFO, 0 blocking — both structural gaps FOLDED before frontmatter: HIGH (Concern 1) T012 under-scoped OWASP to crosswalk.yaml → widened to owasp.yaml + crosswalk.yaml (10 llm0X2025 + 1 Agentic page) with llm0X/llm0X2025 twin disambiguation + llm01 preserved in both (T005/T012); MED (Concern 2) new test silent-green risk → T015 verifies collection/execution + PR-CI registration consciously deferred to #329 (post-F-338 sequencing recorded); Concern 3 (crosswalk ATLAS refs covered by host-keyed override) → T006 record. Conditions-to-clear-to-full-APPROVED both met in this revision. Full: .aod/results/team-lead.md."
---

# Tasks: Citation-URL Remediation (BLP-06 Wave 1)

**Input**: Design documents from `specs/333-citation-url-remediation/`
**Prerequisites**: plan.md (PM+Architect APPROVED), spec.md (PM APPROVED), research.md, data-model.md, contracts/classifier-verdict-contract.md, quickstart.md

**Tests**: INCLUDED — the spec (FR-008) explicitly requires a synthetic-404 verdict unit test and keeping `test_citation_shape()` green. All tests are **offline** (ADR-021 determinism boundary): no network on any `pytest`/`pull_request`/`push` path.

**Organization**: Grouped by user story. The research phase (W0) is a hard **Foundational gate** — no edit may precede the architect's fork sign-off (NFR-001 "no citation edited on a hunch").

> **Definition of Done** (canonical bar = constitution VII):
> 1. ✅ Pushed to Production — fixes merged; the corrected catalogs are the shipped contract.
> 2. ✅ Tested — offline suite green (`test_citation_shape()` + synthetic-404 verdict test).
> 3. ✅ User Validated — **#332 self-closes** on a `--no-cache` monitor run + landing-content spot-check (the real end-to-end gate, FR-006).

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (ATLAS) · US2 (NIST) · US3 (OWASP) · US4 (Self-Close)
- Exact file paths included. `[MANUAL-ONLY]` marks deliver-adjacent tasks gated out of CI by the determinism boundary (live network / `gh` lifecycle / human judgment).

## Path Conventions
Single project: taxonomy data in `schemas/taxonomy/`, the monitor in `scripts/check-citation-urls.py`, the workflow in `.github/workflows/`, tests in `tests/`, feature artifacts in `specs/333-citation-url-remediation/`.

---

## Phase 1: Setup

**Purpose**: Establish the work-list and formalize the deferral, no catalog edits.

- [ ] T001 Read the #332 canonical 41-finding list and map each in-scope dead URL to its source location across `schemas/taxonomy/{mitre-atlas,nist-ai-rmf,crosswalk}.yaml` (no edits) — capture the per-class work-list to `specs/333-citation-url-remediation/test-results/worklist.md`
- [ ] T002 [P] Formalize the #325 deferral (FR-005 / PM-M2): record that the 4 `tachi-control-category → nist-ai-rmf` edges cite a local file (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`), not the dead DOI — distinct defect class, out of F-333 scope, deferred standalone — to `specs/333-citation-url-remediation/deferred-325.md`

---

## Phase 2: Foundational (Blocking Prerequisites) — W0 Research & Adjudication

**Purpose**: Adjudicate each fix-class against its authoritative source BEFORE any edit. **CRITICAL**: no user-story work (Phase 3+) may begin until T006 (the architect fork sign-off) is green — this is the load-bearing W0→W1 gate (Architect OBS-2).

- [ ] T003 [P] Adjudicate the **ATLAS** class: verify all 36 `AML.Txxxx` IDs are present in MITRE `atlas-data/techniques.yaml` (`https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml`); confirm `atlas.mitre.org/techniques/` 404s an automated/runner client while rendering in a browser (dual-UA + **runner-egress** probe); record the verdict (re-classify vs. any per-ID genuine rot) to `specs/333-citation-url-remediation/research-atlas.md`
- [ ] T004 [P] Adjudicate the **NIST** class: identify the current canonical AI 100-1 (core RMF) landing page, confirming intent is AI 100-1 (not AI 600-1, the GenAI profile); verify it returns 2xx dual-UA + runner-egress; record to `specs/333-citation-url-remediation/research-nist.md`
- [ ] T005 [P] Adjudicate the **OWASP** dead-set across **BOTH** `schemas/taxonomy/owasp.yaml` (20 refs: 10 `llm0X2025` + 1 Agentic page + the live `llm01`) **and** `schemas/taxonomy/crosswalk.yaml` (102 refs; carries non-year `llm02/03/05` **and** year-suffixed `llm0X2025` twins + 2 Agentic pages): probe each distinct `genai.owasp.org` URL; record which are actually dead and their restructured canonicals; **disambiguate the `llm0X-` vs `llm0X2025-` canonical twin** so the apply does not leave a stale variant; confirm `llm01-prompt-injection/` is **live** in both files (regression guard); record to `specs/333-citation-url-remediation/research-owasp.md` (Team-Lead Concern 1)
- [ ] T006 **GATE — Architect signs the fork resolution** (Architect OBS-2): review T003–T005 evidence; confirm the ATLAS path is host-scoped re-classify (or authorize a per-ID re-point / the Team-Lead split-valve if R7 is overturned or a `classify_one()` refactor proves necessary). A green sign-off here unblocks Phase 3+. The record MUST explicitly note that the host-scoped override suppresses the **~96 `atlas.mitre.org` refs in `crosswalk.yaml`** too (the override is host-keyed, not file-keyed) so coverage isn't merely assumed (Team-Lead Concern 3). Record to `specs/333-citation-url-remediation/test-results/fork-resolution.md`

**Checkpoint**: Fork resolved with cited evidence → apply phases may begin.

---

## Phase 3: User Story 1 — MITRE ATLAS Citations Adjudicated & Resolved (Priority: P1) MVP

**Goal**: Stop the monitor false-flagging the ~38 ATLAS findings while preserving the correct human-facing citation URL and real-rot detection on every other host.

**Independent Test**: The synthetic-404 unit test proves `atlas.mitre.org`,404→NEEDS_REVIEW and any-other-host,404→LINK_ROT; the corrected monitor no longer reports the ATLAS URLs as confirmed rot.

### Tests for User Story 1 (write FIRST, ensure they FAIL before T008)

- [ ] T007 [P] [US1] Write the offline synthetic-404 verdict unit test **by extending the existing `tests/schemas/test_citation_linkrot_parity.py`** (reuse its importlib hyphenated-module loader for `check-citation-urls.py` + its socket guard — do NOT spin up a fresh `tests/scripts/` file; Architect OBS-3): assert `_verdict_for_status("https://atlas.mitre.org/techniques/AML.T0051", 404, ...) == NEEDS_REVIEW`, `(other-host, 404) == LINK_ROT`, and `("https://atlas.mitre.org/...", 410) == LINK_ROT` (genuine *gone* still flags). No network. Confirm it FAILS pre-implementation.

### Implementation for User Story 1 (re-classify path per T006; per-ID re-point only if T006 authorized)

- [ ] T008 [US1] Add the bounded `_HOST_STATUS_OVERRIDES` table + guard at the top of `_verdict_for_status(url, status, ...)` in `scripts/check-citation-urls.py` (host-scoped: `atlas.mitre.org` 404 → `NEEDS_REVIEW`); leave the global `_HARD_ROT_STATUSES`/`_NEEDS_REVIEW_STATUSES` frozensets untouched (NFR-005)
- [ ] T009 [US1] Update the `schemas/taxonomy/mitre-atlas.yaml` R7 TRIPWIRE / FR-033 header comment to cross-reference the new `_HOST_STATUS_OVERRIDES` code-side override so the data note and the code override point at each other (Architect OBS-1)
- [ ] T010 [US1] Run the T007 synthetic-404 test in `tests/schemas/test_citation_linkrot_parity.py` → green; confirm the ATLAS URLs are reclassified to needs-review and no other host's 404 handling changed

**Checkpoint**: ATLAS class resolved and offline-validated.

---

## Phase 4: User Story 2 — NIST AI RMF DOI Citation Corrected (Priority: P1)

**Goal**: One corrected URL cascades to all 73 `nist-ai-rmf.yaml` records.

**Independent Test**: All 73 records carry the verified AI 100-1 canonical; no other record changed; `test_citation_shape()` still green.

- [ ] T011 [US2] Replace the shared dead `https://doi.org/10.6028/NIST.AI.100-1` in `schemas/taxonomy/nist-ai-rmf.yaml` with the T004-verified canonical AI 100-1 URL (cascades to all 73 records); confirm intent (AI 100-1, not AI 600-1)

**Checkpoint**: NIST class resolved.

---

## Phase 5: User Story 3 — OWASP GenAI Citations Corrected (Priority: P2)

**Goal**: Re-point the confirmed-dead `genai.owasp.org` citations; leave the live `llm01` untouched.

**Independent Test**: Each confirmed-dead URL points at its restructured canonical; `llm01-prompt-injection/` is byte-unchanged; `test_citation_shape()` green.

- [ ] T012 [US3] Re-point the T005-confirmed-dead `genai.owasp.org` citations in **BOTH `schemas/taxonomy/owasp.yaml` AND `schemas/taxonomy/crosswalk.yaml`** to their restructured canonicals (Team-Lead Concern 1 — `owasp.yaml` carries 10 `llm0X2025` + 1 Agentic page, unaddressed if only crosswalk is edited → #332 would not self-close); resolve the `llm0X-`/`llm0X2025-` twin per T005 so no stale variant survives; leave `llm01-prompt-injection/` **byte-unchanged in BOTH files** (regression guard)

**Checkpoint**: OWASP class resolved.

---

## Phase 6: User Story 4 — Tracker Self-Closes End-to-End (Priority: P1)

**Goal**: A `--no-cache` monitor run finds zero in-scope confirmed rot and self-closes #332 — the real DoD. **Depends on US1 + US2 + US3 complete.**

**Independent Test**: Dispatch the monitor; observe #332 auto-close with its recovery comment; landing spot-check passes.

- [ ] T013 [US4] Add a `no_cache` boolean `workflow_dispatch` input to `.github/workflows/tachi-citation-linkrot.yml`, wired to the script's existing `--no-cache` flag (D3); stays inside the scheduled-only/`workflow_dispatch` surface (NFR-003 / ADR-021 intact)
- [ ] T014 [P] [US4] FR-007 rendering-exposure grep (D5): grep the byte-baselined render artifacts (the `examples/*/security-report.pdf.baseline` text layer + coverage/personalized-tree baseline docs) for `atlas.mitre.org/techniques`, `doi.org/10.6028/NIST.AI.100-1`, `genai.owasp.org`; expected **zero** hits (render path reads record IDs/counts). Record to `specs/333-citation-url-remediation/test-results/fr7-exposure.md`; run the ADR-037 D-9 baseline-regen lane ONLY if a string surfaces
- [ ] T015 [US4] Run the full offline suite: `pytest tests/schemas/test_taxonomy_integrity.py::test_citation_shape` + the T007 synthetic-404 test → all green, no network (FR-008). **Verify the synthetic-404 test is actually COLLECTED and EXECUTED (not silently skipped)** — guard the #185/KB-15-16 silent-green failure mode (Team-Lead Concern 2). **CI-enforcement decision**: this offline test is enforced at the `/aod.build` gate + locally (matching the existing citation tests' posture); PR-CI allowlist registration in `tachi-pytest.yml` is **deferred to #329** (per plan D4 / YAGNI — #329 owns wiring all citation tests into PR CI). If a maintainer later registers it, add to BOTH the `paths:` list and the `pytest` invocation, sequenced onto **post-F-338 `main`** (F-338 concurrently edits that file)
- [ ] T016 [US4] Code review (binding, NFR-005): confirm the `_HOST_STATUS_OVERRIDES` change is host-scoped, documented, and reversible; global frozensets untouched; `llm01` untouched; no network added to any PR/push path
- [ ] T017 [US4] [MANUAL-ONLY live Actions run + gh issue lifecycle] Dispatch the monitor as a full sweep (`gh workflow run tachi-citation-linkrot.yml -f no_cache=true`) and await **#332 self-close** with its recovery comment + zero in-scope confirmed rot; record the run URL + comment to `specs/333-citation-url-remediation/test-results/acceptance.md`. **Fallback (PM-M4 / spec R1)**: if #332 does NOT self-close, the fork was resolved wrong → loop back to T006/W0 re-adjudication. (Deliver-adjacent — run during `/aod.deliver`, per F-183 KB Entry 17.)
- [ ] T018 [US4] [MANUAL-ONLY human landing judgment] Landing-content spot-check: open **1 NIST + 1 OWASP** corrected URL in a browser; confirm each renders the specific cited item, not a generic/un-anchored page (PM-M3 sample; the ATLAS re-classify path changes no URL, so no ATLAS sample). Record to the acceptance file

**Checkpoint**: #332 self-closed; landing spot-check passed → feature is done.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T019 [P] Record the fork-resolution evidence (which ATLAS path was taken and why, per-class research summary) in the delivery record for SC-004 — `specs/333-citation-url-remediation/delivery.md` (created at deliver)
- [ ] T020 [P] Confirm the #325 deferral doc (T002) is complete and linked so deliver can cite FR-005 AC-1 (documented-deferred artifact)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational / W0 (Phase 2)**: depends on Setup; **BLOCKS all user stories**. T006 (architect fork sign-off) is the hard gate.
- **US1 / US2 / US3 (Phases 3–5)**: each depends only on its W0 verdict (T003/T004/T005) + the T006 gate — then independent and parallelizable across the three classes.
- **US4 (Phase 6)**: depends on **US1 + US2 + US3** complete (it validates the aggregate). T017 is strictly last/async.
- **Polish (Phase 7)**: depends on US4.

### Within Each User Story
- US1: test (T007, FAIL first) → implementation (T008–T009) → green (T010).
- US2 / US3: single data edit each, validated by `test_citation_shape()` in T015.
- US4: setup input (T013) + exposure grep (T014) ∥ → offline green (T015) → code review (T016) → live gate (T017) → spot-check (T018).

### Parallel Opportunities
- T003 / T004 / T005 (the three research classes) run in parallel under one `web-researcher` fan-out.
- After T006: US1, US2, US3 proceed in parallel — file-disjoint: US1 → `check-citation-urls.py` + `mitre-atlas.yaml` (comment only); US2 → `nist-ai-rmf.yaml`; US3 → `owasp.yaml` + `crosswalk.yaml`. (US1's re-classify path edits no ATLAS data, so even the shared `crosswalk.yaml` is touched only by US3 — no write collision.)
- T002 ∥ Setup; T014 ∥ within US4; T019 / T020 ∥ in Polish.

---

## Parallel Example: W0 Research (Foundational)

```bash
# One web-researcher fan-out over the three fix-classes (T003–T005):
Task: "Verify 36 ATLAS IDs in atlas-data + runner-egress reachability → research-atlas.md"
Task: "Find NIST AI 100-1 canonical (not AI 600-1) → research-nist.md"
Task: "Adjudicate the real OWASP genai.owasp.org dead-set, keep llm01 → research-owasp.md"
# THEN (barrier): architect signs the fork resolution (T006) before any apply task.
```

## Parallel Example: W1 Apply (after T006 gate)

```bash
# Three classes, different files, in parallel:
Task: "[US1] Add _HOST_STATUS_OVERRIDES in check-citation-urls.py + mitre-atlas.yaml comment"
Task: "[US2] Replace NIST DOI in nist-ai-rmf.yaml (73 records)"
Task: "[US3] Re-point dead OWASP citations in owasp.yaml + crosswalk.yaml (resolve llm0X/llm0X2025 twin, leave llm01)"
```

---

## Implementation Strategy

### MVP / Highest-leverage first
1. Phase 1 Setup → Phase 2 W0 research (the gate).
2. **STOP at T006** — the architect fork sign-off decides re-classify vs re-point and is the single highest-leverage decision.
3. US1 (ATLAS, the ~38) → US2 (NIST, 73 records) → US3 (OWASP) — parallelizable.
4. US4 — the live #332 self-close gate (deliver-adjacent).

### Split valve (Team-Lead C2 / D2)
If T008 reveals host-scoping needs a `classify_one()` control-flow refactor (it should not — `_verdict_for_status` already receives `url`), split the classifier work to a BLP-06 Wave 2 sibling and ship F-333 with the NIST + OWASP data fixes. Record the trigger at T006/T008.

---

## Notes
- [P] = different files, no dependencies. [Story] maps task → user story for traceability.
- The research-first gate (T006) is non-negotiable — it is the structural enforcement of NFR-001.
- `test_citation_shape()` must stay green throughout; the synthetic-404 test is the only new test (offline).
- Zero new runtime dependencies; the ATLAS likely path edits zero catalog data.
- Commit after each logical group; the live FR-006 gate (T017) runs at `/aod.deliver`, not in CI.

### Triple-review concerns folded in (2026-06-29)
- **Team-Lead HIGH (Concern 1)** → T005 + T012 widened to cover `owasp.yaml` (10 `llm0X2025` + 1 Agentic page) in addition to `crosswalk.yaml`, with `llm0X`/`llm0X2025` twin disambiguation and `llm01` preserved in BOTH files. Without this, #332 would not self-close (SC-002).
- **Team-Lead MED (Concern 2)** → T015 now verifies the synthetic-404 test is actually collected/executed (anti silent-green); PR-CI allowlist registration in `tachi-pytest.yml` is consciously deferred to #329 (consistent with plan D4 and the existing citation tests' posture), with the post-F-338 sequencing caveat recorded if/when done.
- **Architect OBS-3** → T007 extends the existing `tests/schemas/test_citation_linkrot_parity.py` (reusing its importlib hyphenated-module loader + socket guard) instead of a fresh file.
- **Team-Lead Concern 3 (LOW)** → T006 fork-resolution record must note the host-keyed override also covers the ~96 `atlas.mitre.org` crosswalk refs.
- **Team-Lead Concerns 4–6 (LOW/INFO)** → `--no-cache` already exists (T013 is workflow-input-only, no script change); T007→T008→T010 FAIL-checkpoint is intra-US1-serial even under US1∥US2∥US3; estimate holds at 3.0d central.
