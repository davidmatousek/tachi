---
prd_reference: docs/product/02_PRD/333-citation-url-remediation-2026-06-29.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED
    notes: "Faithful, complete 1:1 translation of the approved v1.1 PRD — all 8 FRs, 5 NFRs, 9 success metrics mapped EXACT; ATLAS fork framed non-co-equal (re-classify PREFERRED, flat-blob re-point = anti-pattern, same-host = non-starter, per-ID real rot); #325 explicitly OUT (FR-005); FR-006 monitor-driven #332 self-close + landing spot-check + --no-cache full sweep all present; zero scope creep. 4 findings, all MINOR/observational, zero blocking — several are improvements over the PRD (verified test_citation_shape() not-in-CI correction folded into Assumptions; [MANUAL-ONLY] AC tagging for live-network/gh-lifecycle/landing-judgment ACs; SC-009 live-llm01 regression-guard promotion). F1 (P0-feature vs P1/P2-story clarifier) folded in. Carry-forward to plan/tasks (non-blocking): anchor any re-point edit-surface math on 36 distinct / ~133 occurrences not the ~38 finding count; resolve the synthetic-404 test CI placement; resolve the --no-cache acceptance mechanism (add dispatch input or clear ledger). Full review: .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Citation-URL Remediation (BLP-06 Wave 1)

**Feature Branch**: `333-citation-url-remediation`
**Created**: 2026-06-29
**Status**: Draft
**Input**: User description: "PRD: 333 - citation-url-remediation"
**PRD**: `docs/product/02_PRD/333-citation-url-remediation-2026-06-29.md` (Approved)

## Overview

The #183 link-rot monitor's first live sweep flagged **41 citation URLs** as dead (HTTP 404) across the taxonomy catalogs, held open in self-healing tracker **#332**. Because tachi is positioned as the upstream machine-readable contract downstream AI-security tools consume, a citation that resolves to a 404 erodes the evidentiary value of every crosswalk edge that cites it. This feature corrects (or correctly re-classifies) those 41 URLs in **three research-first fix-classes**, so the monitor stops reporting them and **#332 self-closes** on a subsequent run — without introducing a "wrong-but-alive" redirect that masks the breakage.

The 41 findings are **not** a bulk find-replace. Fix-class 1 (MITRE ATLAS) collides with a previously documented determination (the `mitre-atlas.yaml` R7 TRIPWIRE note) that the ATLAS 404s are **anti-bot gating**, not link rot. Resolving that fork against MITRE's authoritative `atlas-data` repo is the single highest-leverage task, and it changes the *kind* of fix (a monitor-classifier change, not a data edit).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - MITRE ATLAS Citations Adjudicated & Resolved (Priority: P1)

A taxonomy steward needs the ~38 MITRE ATLAS technique citations (36 distinct IDs) adjudicated against MITRE's authoritative `atlas-data` repo, then resolved by the path the evidence supports — **most likely a host-scoped re-classification** of the #183 monitor so its anti-bot 404s on `atlas.mitre.org` stop being reported as confirmed rot, preserving the correct human-facing citation URL and real-rot detection on every other host. Only if the evidence overturns the R7 determination are the citations re-pointed to a runner-reachable canonical.

**Why this priority**: This is ~38 of the 41 findings and the central research fork. It is the hardest, highest-leverage, and most error-prone class — re-pointing to any `atlas.mitre.org` path still 404s the monitor's runner (so #332 never closes), and re-pointing to the flat `atlas-data` blob is a self-inflicted "wrong-but-2xx" trap. Getting this class right is what makes the rest of the feature meaningful.

**Independent Test**: Verify each of the 36 ATLAS IDs exists in `atlas-data/techniques.yaml`; confirm the chosen fix yields a 2xx-to-the-runner outcome (re-classify: the host's 404s are no longer reported as confirmed rot; re-point: the new URL resolves from the runner); confirm the delivery record states which fork was taken and why. Deliverable value: the crosswalk cites live, verifiable authority for every ATLAS technique and the monitor stops false-flagging them.

**Acceptance Scenarios**:

1. **Given** the 36 distinct ATLAS technique IDs cited in `mitre-atlas.yaml` and `crosswalk.yaml`, **When** each ID is checked against MITRE's authoritative `atlas-data/techniques.yaml`, **Then** every ID is confirmed present (or any genuinely retired/moved ID is individually identified) and the result is recorded as the fork-resolution evidence.
2. **Given** the R7 determination that `atlas.mitre.org/techniques/` 404s are anti-bot gating (the IDs being valid), **When** the adjudication confirms R7, **Then** the resolution is the host-scoped re-classify path (citations unchanged) and **not** a re-point to the flat `atlas-data` blob.
3. **Given** the re-classify path is applied to the monitor's verdict logic, **When** a 404 from `atlas.mitre.org` is classified, **Then** it is treated as needs-review (not confirmed rot), **And** a 404 from any other host is still treated as confirmed rot (no signal loss). [MANUAL-ONLY] runner-egress reachability is observable only on the live GitHub-hosted runner, not in offline CI.
4. **Given** the adjudication instead overturns R7 for a specific ID (genuine rot), **When** that record is resolved, **Then** it is re-pointed to its new canonical location (or marked `confidence: low` with a TODO), not left dead.

---

### User Story 2 - NIST AI RMF DOI Citation Corrected (Priority: P1)

A taxonomy steward needs the single dead `https://doi.org/10.6028/NIST.AI.100-1` citation re-pointed to NIST's current canonical AI RMF (AI 100-1, the core RMF) landing page, so that all **73** citing records in `nist-ai-rmf.yaml` resolve again from one corrected URL.

**Why this priority**: One fix cascades to 73 records — the highest impact-per-edit class and unambiguously real rot (a moved document). Independently shippable and high value on its own.

**Independent Test**: Confirm the replacement URL resolves 2xx to the runner client and lands on the AI 100-1 document (distinct from AI 600-1, the GenAI profile, which is separately catalogued); confirm all 73 records reflect the corrected URL.

**Acceptance Scenarios**:

1. **Given** the dead DOI shared by all 73 `nist-ai-rmf.yaml` records, **When** the verified canonical AI 100-1 URL replaces it, **Then** all 73 records carry the corrected URL and no other record is altered.
2. **Given** the replacement URL, **When** its intent is confirmed against the document, **Then** it targets AI 100-1 (the core RMF) and not AI 600-1 (the GenAI profile). [MANUAL-ONLY] document-intent confirmation requires human reading of the landing page.
3. **Given** the corrected URL, **When** it is probed dual-UA with redirects followed, **Then** it returns 2xx to both a browser UA and the monitor's runner client. [MANUAL-ONLY] runner-egress 2xx is observable only on the live runner.

---

### User Story 3 - OWASP GenAI Citations Corrected (Priority: P2)

A taxonomy steward needs the confirmed-dead `genai.owasp.org` citations re-pointed to their restructured canonical locations, while the still-live `llm01-prompt-injection/` citation is left untouched as a regression guard.

**Why this priority**: Smallest class by count and the messiest to scope (the crosswalk carries 16 distinct `genai.owasp.org` URLs — non-year `llm02/03/04/05`, nine year-suffixed `llm0X2025` variants, and two Agentic resource pages — so the *actual* dead-set must be adjudicated, not assumed at "4"). Lower leverage than US-1/US-2; correctly deferred to P2 but still required for full #332 closure.

**Independent Test**: For each URL the research confirms dead, verify its restructured canonical resolves 2xx to the runner; verify `llm01-prompt-injection/` is unchanged and still live.

**Acceptance Scenarios**:

1. **Given** the 16 distinct `genai.owasp.org` citation URLs, **When** the actual dead-set is adjudicated, **Then** only the confirmed-dead URLs (including any confirmed year-suffixed `llm0X2025` variants and Agentic resource pages) are slated for change.
2. **Given** the live `llm01-prompt-injection/` citation, **When** the OWASP corrections are applied, **Then** that citation is left byte-unchanged (regression guard).
3. **Given** each confirmed-dead OWASP URL, **When** it is re-pointed to its restructured canonical, **Then** the new URL resolves 2xx to the runner client and lands on the cited risk content. [MANUAL-ONLY] runner-egress 2xx + landing content require live verification.

---

### User Story 4 - Tracker Self-Closes End-to-End (Priority: P1)

A maintainer needs the **#332** tracking issue to self-close on a subsequent `--no-cache` scheduled / `workflow_dispatch` monitor run after the fixes land, giving an automated end-to-end confirmation that the rot is genuinely cleared — not just a local edit that looks right.

**Why this priority**: This is the *real* Definition of Done. A green #332 is the only signal that proves the fixes reach the monitor's runner egress. It is independently observable (run the monitor, watch #332), and it is the gate that distinguishes a correct fix from a plausible-but-wrong one.

**Independent Test**: Trigger a `--no-cache` full-sweep monitor run after the fixes; observe #332 auto-close with its recovery comment and zero confirmed rot for the in-scope URLs; corroborate with a landing-content spot-check on a sample.

**Acceptance Scenarios**:

1. **Given** all three fix-classes are applied, **When** a `--no-cache` full-sweep monitor run executes (scheduled or dispatched), **Then** it finds zero confirmed rot for the in-scope URLs **And** #332 self-closes with its recovery comment, **And** the run URL + self-close comment are recorded as delivery evidence. [MANUAL-ONLY] requires a live GitHub Actions run with network + `gh` issue lifecycle (gated out of CI by the determinism boundary).
2. **Given** #332 has self-closed, **When** a sampled corrected URL is opened in a browser, **Then** it renders the specific cited technique/control/risk, not a generic or un-anchored page. [MANUAL-ONLY] landing-content spot-check requires human judgment.
3. **Given** the monitor's TTL ledger (`should_skip`, default 21 days), **When** the acceptance run is arranged, **Then** it is a full sweep (`--no-cache` or a cleared ledger) so no in-scope URL is skipped on stale `last_ok` data.

---

### Edge Cases

- **Anti-bot 404 vs. genuine rot**: a headless 404 on a page that renders in a browser must be adjudicated against the authoritative source repo, never auto-trusted as dead (the ATLAS fork). 404 is *usually* genuine but is the ambiguous case here.
- **Same-host re-point trap**: re-pointing an ATLAS citation to any other `atlas.mitre.org/...` path still 404s the runner → #332 never closes. Such a "fix" must be rejected.
- **Wrong-but-2xx redirect**: a replacement URL that returns 2xx but lands on a generic/changed/un-anchored page (e.g., the flat `atlas-data` blob) silently misleads analysts — worse than a known 404. Must be caught by the landing-content spot-check.
- **Partial OWASP dead-set**: `llm01-prompt-injection/` is live; editing it would introduce a regression. The dead-set is larger and messier than the headline "4".
- **Hidden render coupling**: if a corrected citation string unexpectedly appears in a byte-identity-baselined PDF/coverage artifact (the #185 trap), the baseline-regen lane applies and baselines must be regenerated green (expected: no exposure).
- **Re-classify over-broadening**: narrowing the monitor must stay host-scoped — a blanket "treat all 404s as needs-review" would blind it to real rot elsewhere.
- **OWASP re-restructure**: if the OWASP site moves again later, the monitor re-flags it and this loop repeats — the monitor working as designed (out of scope to prevent).

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC begins with **Given** and follows Given/When/Then. `[MANUAL-ONLY] <reason>` marks ACs that cannot be automated (live network, `gh` lifecycle, or human landing-content judgment — all gated out of CI by the ADR-021 determinism boundary).

- **FR-001 (Research-first, load-bearing)**: For each of the three fix-classes, the correct remediation MUST be identified **before any edit**, grounded in authoritative sources (ATLAS → MITRE `atlas-data/techniques.yaml`; NIST → current AI 100-1 canonical; OWASP → restructured GenAI site), with each candidate verified dual-UA (browser + automated client), redirects followed to final status, and confirmed to return 2xx from the #183 monitor's GitHub-runner egress. Evidence MUST be recorded per fix-class for the delivery record.
  - **AC-1**: **Given** the three fix-classes, **When** research completes, **Then** each class has a documented resolution (corrected URL or re-classification) with its supporting authoritative source cited. [MANUAL-ONLY] external-source research and runner-egress probing require live network.
  - **AC-2**: **Given** any candidate replacement URL, **When** it is validated, **Then** the evidence shows 2xx to a browser UA, to an automated-client UA, and to the runner-client egress. [MANUAL-ONLY] live network verification.

- **FR-002 (ATLAS resolution — paths are not co-equal)**: Based on FR-001, the ~38 ATLAS citations MUST be resolved by the evidence-supported path: **re-classify (preferred)** — a narrow, host-scoped adjustment to the monitor's verdict logic so `atlas.mitre.org` 404s become needs-review while all other hosts retain confirmed-rot detection, citations unchanged; **re-point to the flat `atlas-data` blob is an anti-pattern** (permitted only if FR-001 overturns R7); **re-point to another `atlas.mitre.org` path is a non-starter**; **per-ID genuine rot** is re-pointed individually. On the re-point path the edit surface is ~133 occurrences (37 `url:` in `mitre-atlas.yaml` + ~96 `citation:` in `crosswalk.yaml`, 36 distinct) that MUST all change consistently; on the re-classify path there are zero data edits. Edited header comments (R7 TRIPWIRE / FR-033 URL-pattern note) MUST record what changed and why.
  - **AC-1**: **Given** FR-001 confirms the ATLAS IDs valid and the 404s anti-bot, **When** the fix is applied, **Then** it is the host-scoped re-classify (citations unchanged) and not a flat-blob re-point.
  - **AC-2**: **Given** the re-classify change, **When** a synthetic 404 from `atlas.mitre.org` is classified offline, **Then** the verdict is needs-review; **And When** a synthetic 404 from any other host is classified, **Then** the verdict is confirmed rot.
  - **AC-3**: **Given** the chosen path, **When** the change is recorded, **Then** the relevant header comment is updated to explain the resolution and the delivery record names the fork taken.

- **FR-003 (NIST DOI fix)**: The single dead `https://doi.org/10.6028/NIST.AI.100-1` citation in `nist-ai-rmf.yaml` MUST be replaced with the verified canonical AI 100-1 URL; the fix cascades to all 73 citing records.
  - **AC-1**: **Given** the 73 records sharing the dead DOI, **When** the corrected URL is applied, **Then** all 73 carry it and no other record changes.
  - **AC-2**: **Given** the replacement, **When** intent is confirmed, **Then** it targets AI 100-1 (core RMF), not AI 600-1. [MANUAL-ONLY] document-intent confirmation requires human reading.

- **FR-004 (OWASP fix)**: The confirmed-dead `genai.owasp.org` citations in **both `crosswalk.yaml` and `owasp.yaml`** (LLM02/03/05 + Agentic resource page(s) + any year-suffixed `llm0X2025` variants FR-001 confirms dead — `owasp.yaml` carries 10 `llm0X2025` + 1 Agentic page; `crosswalk.yaml` carries both non-year and `llm0X2025` twin forms + 2 Agentic pages) MUST be re-pointed to their restructured canonical locations, with the `llm0X-`/`llm0X2025-` twin disambiguated so no stale variant survives; the live `llm01-prompt-injection/` citation MUST be left unchanged **in both files**.
  - **AC-1**: **Given** the adjudicated OWASP dead-set, **When** corrections are applied, **Then** only confirmed-dead URLs change and `llm01-prompt-injection/` is byte-unchanged.
  - **AC-2**: **Given** each corrected OWASP URL, **When** validated, **Then** it resolves 2xx to the runner and lands on the cited risk. [MANUAL-ONLY] live network + landing judgment.

- **FR-005 (#325 deferred — out of scope)**: The 4 citation-unsupported `tachi-control-category → nist-ai-rmf` edges (#325) MUST remain out of this feature's scope; they cite a local file (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`), not the dead DOI, so the FR-003 fix does not resolve them (distinct defect class). The deferral decision is formalized here.
  - **AC-1**: **Given** the #325 edges, **When** F-333 scope is finalized, **Then** they are documented as deferred-standalone and not modified by this feature.

- **FR-006 (Monitor-driven acceptance)**: The feature is NOT done on local edit. Acceptance REQUIRES a subsequent scheduled or `workflow_dispatch` monitor run, executed as a `--no-cache` full sweep, that finds zero confirmed rot for the in-scope URLs and self-closes #332; plus a landing-content spot-check confirming a sampled corrected URL renders the cited item. Because the workflow exposes no `--no-cache` dispatch input today (only `inject_sentinel_rot`), the full sweep MUST be arranged (add a dispatch input or clear the ledger). The deliver stage MUST trigger/await at least one such run and record the run URL + self-close comment.
  - **AC-1**: **Given** all fixes are applied, **When** a `--no-cache` full-sweep run executes, **Then** #332 self-closes with zero in-scope confirmed rot and the run URL + comment are recorded. [MANUAL-ONLY] live Actions run + `gh` issue lifecycle.
  - **AC-2**: **Given** #332 has closed, **When** a sampled corrected URL is opened, **Then** it renders the specific cited item, not a generic page. [MANUAL-ONLY] human landing-content judgment.

- **FR-007 (Rendering-exposure check — the #185 watch-out)**: Because `mitre-atlas` and `nist-ai-rmf` are `ORDERED_FRAMEWORKS` members, this feature MUST verify (not assume) whether any corrected citation string appears in a byte-identity-baselined PDF page or coverage artifact. Expected outcome: no exposure (the report aggregator reads record IDs/counts, never citation strings). If a string surfaces (or if FR-002 ever adds/removes a catalog record), the baseline-regen lane applies and baselines MUST be regenerated and remain green.
  - **AC-1**: **Given** the corrected citation strings, **When** the baselined PDF/coverage artifacts are searched, **Then** the result is recorded; **And** if zero hits, no regen is required; **And** if any hit, baselines are regenerated green.

- **FR-008 (Syntactic-integrity & determinism preservation)**: All edits MUST keep the offline `test_citation_shape()` URL-syntax guard green and MUST NOT introduce any network call into `tests/` or any `pull_request`/`push`-triggered job (ADR-021 boundary). Any monitor-classifier change MUST stay within the scheduled-only workflow surface and be unit-tested over a **synthetic 404**, never a live fetch.
  - **AC-1**: **Given** all edits, **When** `test_citation_shape()` runs, **Then** it passes with no network access.
  - **AC-2**: **Given** the re-classify verdict logic (if taken), **When** it is tested, **Then** the test exercises a synthetic 404 with no live fetch, and no network is added to any PR-triggered job.

### Non-Functional Requirements

- **NFR-001 (Evidence-before-edit)**: No citation is edited on a hunch; each change is justified by an authoritative source + dual-UA reachability confirmed against the runner. A wrong-but-2xx URL is worse than a known 404 — the flat-blob re-point is the named anti-pattern this kills.
- **NFR-002 (Zero new runtime dependency)**: Data-only YAML edits and, on the likely path, a stdlib-only monitor tweak. No new runtime dependency.
- **NFR-003 (Determinism boundary intact)**: Reachability validation stays scheduled-only, off the `pytest`/PR path; this feature must not weaken it.
- **NFR-004 (Minimal, reversible edits)**: The smallest change per class (a cascading pattern fix per class; a bounded host-override map for the classifier). Explanatory header comments updated as load-bearing institutional memory.
- **NFR-005 (Signal-quality preservation)**: A re-classify change MUST be host-scoped, documented, and reversible — never broadened to "treat all 404s as needs-review," which would blind the monitor to real rot on other hosts.

### Key Entities

- **Citation finding**: one of the 41 dead URLs from #332 — attributes: source location (catalog file + line/record), the dead URL, the fix-class (ATLAS / NIST / OWASP), and the adjudicated resolution (corrected URL, re-classification, or per-ID re-point).
- **Fix-class**: a group of findings sharing a root cause and remediation strategy. Three in scope: ATLAS (~38, 36 distinct, re-classify likely), NIST (1 URL → 73 records, re-point), OWASP (subset of 16 distinct URLs, re-point).
- **Authoritative source**: the existence/canonical oracle per class — MITRE `atlas-data/techniques.yaml`; NIST AI 100-1 canonical landing; OWASP restructured GenAI site.
- **Monitor verdict logic**: the classifier surface (`_verdict_for_status`) that maps an HTTP status to HEALTHY / LINK_ROT / NEEDS_REVIEW / TRANSIENT — the FR-002 re-classify target (host-scoping added inside it).
- **Acceptance signal**: tracker #332 — self-closes on a `--no-cache` full-sweep monitor run when zero in-scope confirmed rot remains.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 41 / 41 in-scope citations are resolved or correctly re-classified (each verified 2xx-to-the-runner or correctly moved to needs-review).
- **SC-002**: #332 self-closes on a subsequent `--no-cache` scheduled / `workflow_dispatch` monitor run (the end-to-end acceptance gate) — run URL + self-close comment recorded.
- **SC-003**: A landing-content spot-check on a sampled corrected URL passes (renders the cited item, not a generic/un-anchored page).
- **SC-004**: The fix-class-1 fork (anti-bot 404 vs. genuine rot) is resolved with cited evidence in the delivery record — not assumed.
- **SC-005**: Zero wrong-but-2xx introductions (no misleading redirect or un-anchored blob re-point).
- **SC-006**: Zero `test_citation_shape()` regressions; any re-classify logic validated by a synthetic-404 unit test only (zero live-fetch tests).
- **SC-007**: Zero new runtime dependencies.
- **SC-008**: Zero byte-identity baseline regressions (expected: no rendering exposure; if FR-007 finds any, baselines regenerated green).
- **SC-009**: The live `llm01-prompt-injection/` OWASP citation is byte-unchanged (regression guard holds).

## Scope & Boundaries

### In Scope (P0)

> **Priority note**: "P0" denotes the **feature's** BLP-06 Wave 1 priority; the P1/P2 labels on the user stories above are **intra-feature** relative priorities. No story is feature-P0.

- FR-001 research/verification for all three fix-classes (incl. runner-egress reachability).
- FR-002 ATLAS resolution (host-scoped re-classify, likely) / FR-003 NIST / FR-004 OWASP corrections.
- FR-006 monitor-driven acceptance (#332 self-close via `--no-cache` sweep) + landing spot-check.
- FR-007 rendering-exposure check + conditional baseline regen.
- Updated explanatory header comments in any edited YAML.

### Out of Scope
- **#325** — its 4 NIST edges cite a local file, not the dead DOI; different defect class. Deferred standalone (FR-005).
- **Net-new monitoring capability** — the #183 monitor is shipped; this feature consumes its output (a narrow re-classify tweak is the only monitor touch).
- **Auto-replacement tooling** — remediation is human-triaged research + edit, not an automated URL-rewriter.
- **General docs/markdown link fixing** — scope is `schemas/taxonomy/*.yaml` citations only.
- **Wayback/archival snapshotting** — possible future enhancement, not here.
- **Schema/field changes** to the taxonomy record shape — citation *values* (and classifier logic) only.
- **BLP-06 Waves 2–3** (CI hardening #329/#338; bug closures) — separate features. If FR-002 balloons into a `classify_one()` refactor, the classifier work splits to a Wave 2 sibling (pre-authorized split valve).

### Assumptions
- MITRE's `atlas-data` repo remains the authoritative source for ATLAS technique-ID existence and returns 2xx to automated clients.
- NIST and OWASP publish discoverable current canonical locations for the moved documents.
- The #183 monitor's `workflow_dispatch` is available to drive FR-006 acceptance on demand (confirmed in-tree).
- The new synthetic-404 unit test's CI placement is a plan/tasks decision; the offline `test_citation_shape()` guard is currently local/pre-commit only (not wired into any CI gate), and the determinism boundary permits the network-free synthetic-404 test as a PR gate if the plan chooses to add one.

### Constraints
- Inherits the ADR-021 determinism boundary (FR-008/NFR-003).
- Must respect the #185 consequence-scope lesson (FR-007) — verify rendering exposure, don't assume.
- Edits must keep `test_citation_shape()` green.

## Dependencies

- **Feature 183 (DELIVERED)** — the monitor + #332 tracker; provides the acceptance gate (FR-006) and, on the re-classify path, the classifier surface.
- **Features 186 / 184 / F-180** — introduced the affected ATLAS, NIST, and crosswalk citations.
- **MITRE `atlas-data` / NIST / OWASP GenAI sites** — authoritative sources for FR-001.
- **No write-set collision** with in-flight branch `338-restore-substitution-hardening` (disjoint, confirmed by diff). INFO: if a re-classify unit test is added to a CI job F-338 also edits, run F-333's test against post-338 `main` if merges are near-simultaneous.
