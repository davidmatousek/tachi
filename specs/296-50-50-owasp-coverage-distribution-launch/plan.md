---
spec_reference: specs/296-50-50-owasp-coverage-distribution-launch/spec.md
prd_reference: docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-28
    status: APPROVED
    notes: "0H/0M/2L. Plan.md faithfully translates PM-signed spec into Wave 0-5 build-ready designs; 13 FR + 8 NFR + 14 SC + 8 US all covered with verification paths; both PM spec-layer LOW findings (SC-014 5-item list aligned 1:1 with FR-012; FR-003 §b 'recommended but not exclusive' soft framing) folded inline at plan-layer per sign-off authorization; tone discipline on @armorer-labs gap-analysis-commenter preserved verbatim in Wave 4 closing comment template; FR-007/SC-007 sequencing + Architect M2 F-2-ship-by-2026-06-11 captured in BLP-04 strategy §4; FR-013/SC-013 memory carve-out concrete; FR-009 material-critique definition propagated to plan risks table; FR-011 allowed file set preserved with zero plan-layer additions. 2 LOW concerns flagged for tasks.md fixtures: cadence elasticity + Discussion incubation explicit deferral; FR-009 follow-up Issue template — both non-blocking. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-28
    status: APPROVED_WITH_CONCERNS
    notes: "0H/2M/3L. Plan technically sound. All PRD-layer Architect findings (H1/H2/M1/M2/M3/M4/L1/L2/L3) resolved faithfully. Wave 0 OWASP_COVERAGE.md composes correctly from schemas/taxonomy/owasp.yaml (60 records verified) + ADR-024→ADR-037 + ADR-045 lineage; 80-line cap appropriate. Wave 1 README hero insertion point (between line 14 divider and line 17 H2) verified-correct against actual file state; brand poster line 7 + Get-Started line 13 preserved. Wave 2 Cybersec §a-§f faithful to FR-003 + M1 reproducibility anchored to byte-deterministic Coverage Attestation page. Wave 3 LinkedIn + profile align ADR-044 dual-frame; Wave 4 Discussion close lead-sentence verbatim US-5 AC-3 + ADR-045 line 133 attribution verified. Wave 5 BLP-04 strategy doc covers all 5 FR-012 topics + SC-014 5-item verify; memory carve-out precisely defines docs-only conditions; F-212 recovery flow explicitly NOT invoked (M3 triple-anchored). File-touch matrix excludes every protected path. F-272 D-6 in-tree-first order-of-operations correct. Constitution Check PASS (Principle VII §Exceptions invoked for docs-only DoD per F-272 precedent). 2 MEDIUM concerns RESOLVED INLINE post-review: M-1 baseline-path layout split (nested vs top-level) documented in Wave 0 recipe + Wave 2 §b 'baseline layout note'; M-2 example-count upper bound widened from 2-3 to 2-4 with slot-bridging trade-off documented. 3 LOW concerns deferred to tasks.md per Architect direction: L-1 README hero `\\*` escape-render check sub-step; L-2 §d ADR-lineage depth bound (700-word budget); L-3 profile-template footer wording at author discretion. Full review at .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

**Branch**: `296-50-50-owasp-coverage-distribution-launch` | **Date**: 2026-05-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/296-50-50-owasp-coverage-distribution-launch/spec.md`
**PRD**: `docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md` (v1.0, Approved)
**Research**: [research.md](research.md)
**Initiative**: BLP-04 Adoption Push, Wave 1 (Distribution Launch)

## Summary

Author one new in-tree canonical anchor file (`docs/standards/OWASP_COVERAGE.md`, ≤80 lines), insert a 5-framework coverage hero block into `README.md` (≤30-line diff, between line 14 divider and line 17 `## What is tachi?` H2), add a CHANGELOG `docs:` entry under "Unreleased", and ship four out-of-tree distribution artifacts (LinkedIn post; ~3000-word Cybersec article; davidmatousek/davidmatousek profile refresh; Discussion #179 closing comment with @armorer-labs gap-analysis attribution). At F-1 close, author the BLP-04 strategy doc (Q5 lean) and update the `feedback_aod_deliver_release_gate.md` project memory carve-out (PM M-2 / SC-013). **Pure documentation + external distribution change; no code, no ADR, no tests, no `finding.yaml` or schema delta.** Scoped per spec FR-001 through FR-013.

**Technical approach**: Single feature branch `296-50-50-owasp-coverage-distribution-launch` (already created at /aod.spec time); single squash-merged in-tree PR titled `docs(296): F-1 50/50 OWASP coverage distribution launch (BLP-04 Wave 1)` (PR #297 — opened draft on 2026-05-28). Out-of-tree artifacts (Cybersec PR, profile PR, LinkedIn post, Discussion close) fire post-in-tree-merge inside the F-1 acceptance window; URLs recorded back in Issue #296 closing comment. **Release-please will NOT open a release PR on the `docs(296):` squash-merge** — this is the EXPECTED behavior per `docs:` mapping in `release-please-config.json` (Architect M3); the F-212 empty-`feat(NNN):` marker-commit recovery flow is **NOT** invoked.

## Technical Context

> **F-1 is a writing-bound feature** (not code-bound). The technical-context fields below are filled with minimum-applicable values — most are N/A for a docs + external-distribution change.

**Language/Version**: Markdown (CommonMark) for `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md` (index update), Cybersec article (`davidmatousek/Cybersecurity-Content`), GitHub profile README (`davidmatousek/davidmatousek`), Discussion #179 closing comment. YAML for `schemas/taxonomy/owasp.yaml` (READ-ONLY — verification source for FR-008 pre-check, NOT modified). LinkedIn post: plain-text.
**Primary Dependencies**: `git` + `gh` CLI (for Discussion close + Issue #296 close + PR ready-for-review); browser for github.com rendering inspection + LinkedIn publication; YAML parser for `schemas/taxonomy/owasp.yaml` read-only count verification (`grep -c "^- id:"`). All already present in the tachi maintainer baseline.
**Storage**: Files in repo (`README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md`, `docs/product/_internal/strategy/BLP-04-adoption-push.md`); external GitHub repos (`davidmatousek/davidmatousek`, `davidmatousek/Cybersecurity-Content`); LinkedIn platform; GitHub Discussion #179. Project memory (`feedback_aod_deliver_release_gate.md`). No database, no schemas modified.
**Testing**: N/A — no source code change; no automated tests required by the spec. Verification is post-in-tree-merge `/security` re-scan (regression-only; should report zero new findings since no code changed) + manual UI inspections of all 5 published artifacts. **Per Principle VII §Exceptions**: "Documentation-only changes may not require production deployment" — this exemption applies; Constitution-mandated test coverage thresholds (Principle VI) do not bind for documentation files. Per Principle VII §Non-Negotiable Validation Steps, F-1 still satisfies DoD via: ✅ Pushed to main (squash-merge in-tree PR + 4 out-of-tree PRs/posts/comments); ✅ Tested (post-merge `/security` re-scan + 5-artifact UI inspections + FR-008 pre-check evidence); ✅ User-validated (PR review + each published artifact's URL recorded in Issue #296 + Discussion #179 receives the maintainer-authored close comment).
**Target Platform**: GitHub-hosted repos (`github.com/davidmatousek/tachi`, `github.com/davidmatousek/davidmatousek`, `github.com/davidmatousek/Cybersecurity-Content`); LinkedIn (web + mobile); read by humans on web and via `make update`.
**Project Type**: single — documentation refresh + external-distribution publication. No new project structure introduced.
**Performance Goals**: N/A — file-render time governed by GitHub web UI and LinkedIn platform.
**Constraints**:
- `README.md` hero block ≤30-line diff (FR-011 + SC-011). Escape hatch (Architect M4): if exceeded, requires Architect sign-off in `/aod.plan` cited in CHANGELOG entry and F-1 close-out commit.
- `docs/standards/OWASP_COVERAGE.md` ≤80 lines (Architect H2 Option B lean).
- Cybersec article 2400–3600 words (~3000 ±20%).
- No application code modifications under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, `.aod/scripts/` (NFR-004 + SC-010). Allowed file set enumerated in SC-010.
- F-1 wall-clock target: 5 working days from PRD sign-off (2026-05-28 → 2026-06-04). Hard ceiling: 2026-06-11 (NFR-007).
- Discussion #179 closing comment within 7 days of PRD sign-off (FR-005 + SC-005).
- F-2 sequencing hold binding throughout the F-1 window (FR-007 + SC-007).
- F-2 ship-by-2026-06-11 (Architect M2) — if F-2 slips, F-1 close-out comment is edited (post-close) with the new restoration date.
**Scale/Scope**: 5 in-tree files modified/created + 4 out-of-tree artifacts published.
- In-tree: `README.md` (≤30 lines), `CHANGELOG.md` (~10 lines), `docs/standards/OWASP_COVERAGE.md` (≤80 lines, new), `docs/standards/README.md` (1 index row, ~3 lines), `docs/product/_internal/strategy/BLP-04-adoption-push.md` (~150 lines, new, authored at F-1 close per Q5 lean).
- Out-of-tree: 1 LinkedIn post (~200–400 words), 1 Cybersec article PR (~3000 words), 1 GitHub profile refresh PR (~20–40 line README delta), 1 Discussion #179 closing comment (~200–400 words).
- 1 project memory file edited (`feedback_aod_deliver_release_gate.md` carve-out).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle-by-principle (only applicable principles enumerated)

| Principle | Applicability | Status | Note |
|---|---|---|---|
| I. General-Purpose Architecture | N/A | PASS | Documentation; no domain-specific logic added |
| II. API-First Design | N/A | PASS | No API change |
| III. Backward Compatibility | APPLIES | PASS | README hero block is additive; existing `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference at line 7 preserved; existing 50/50 mention at line 29 may be deduped at hero-author discretion within the 30-line cap or left in place; `docs/standards/OWASP_COVERAGE.md` is first-of-kind; `docs/standards/README.md` index gains one row. No file deleted, no contract broken. |
| IV. Concurrency & Data Integrity | N/A | PASS | No state transitions |
| V. Privacy & Data Isolation | N/A | PASS | No data handling; tachi is local-first per `.claude/rules/scope.md` |
| VI. Testing Excellence | EXEMPTED | PASS | **Per Principle VII §Exceptions for documentation-only changes**; verification is via `/security` re-scan (regression-only; should report zero net change) + FR-008 narrative-defensibility pre-check + 5-artifact UI inspection. |
| VII. Definition of Done (NON-NEGOTIABLE) | APPLIES | PASS | DoD steps satisfied: (1) **Pushed**: in-tree squash-merge to main + 4 out-of-tree publications (LinkedIn, Cybersec PR, profile PR, Discussion #179 close); (2) **Tested**: post-merge `/security` regression-only re-scan + FR-008 pre-check evidence in `notes/narrative-defensibility-check.md` + 5-artifact rendering inspection; (3) **User-validated**: PR review + 5-artifact URLs recorded in Issue #296 + Discussion #179 close visible to @armorer-labs. |
| VIII. Observability & RCA | N/A | PASS | No code paths instrumented; no runtime observability impact |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | APPLIES | PASS | Feature branch `296-50-50-owasp-coverage-distribution-launch` exists (created 2026-05-28); draft PR #297 opened with `docs(296):` Conventional-Commits-formatted title; squash-merge subject inherits `docs(296):` prefix → release-please correctly skips per `release-please-config.json` `docs:` mapping (EXPECTED; Architect M3); F-212 empty-marker recovery flow NOT invoked. **F-1 NFR-005 explicitly acknowledges the cadence break** and FR-007 binds F-2 to restore cadence within ~1 week (by 2026-06-11). |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | APPLIES | PASS | PRD approved 2026-05-28 (PM/Architect/Team-Lead all APPROVED_WITH_CONCERNS with HIGH findings resolved inline); spec PM-signed APPROVED 2026-05-28 (0H/0M/2L); plan dual-signoff this gate. **No new ADR required for F-1** (positioning, not capability; `docs/standards/OWASP_COVERAGE.md` is derivative composition of `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage, NOT an architecture decision — Assumption A-7 + Architect Pre-Mortem). |
| XI. SDLC Triad Collaboration | APPLIES | PASS | Triad reviewed PRD (all APPROVED_WITH_CONCERNS, 4 HIGH findings resolved inline); PM signed spec (APPROVED 0H/0M/2L); Architect + Team-Lead reviewing plan and tasks per `/aod.plan` and `/aod.tasks`. |

### Gate verdict

**Constitution Check: PASS — no violations to track.** F-1's writing-bound, docs-only profile means most principles either don't apply or are exempted by Principle VII §Exceptions. The mandatory-applicable principles (III, VII, IX, X, XI) all have clear satisfaction paths via the spec's FR-001–FR-013.

### Complexity Tracking

*Empty — no Constitution Check violations to justify.*

## Project Structure

### Documentation (this feature)

```
specs/296-50-50-owasp-coverage-distribution-launch/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research phase output (created at /aod.spec time)
├── spec.md              # Feature specification (PM-signed APPROVED)
├── checklists/
│   └── requirements.md  # Spec quality checklist (created at /aod.spec time)
├── notes/
│   └── narrative-defensibility-check.md  # FR-008 pre-check evidence (Wave 1 PM)
└── tasks.md             # Task breakdown (/aod.tasks output — pending)
```

### Repository Changes (in-tree)

```
README.md                                                 # Hero block ≤30-line diff
CHANGELOG.md                                              # Unreleased > F-296 docs entry (~10 lines)
docs/standards/OWASP_COVERAGE.md                          # NEW, ≤80 lines (Architect H2 lean)
docs/standards/README.md                                  # +1 index row for OWASP_COVERAGE.md
docs/product/_internal/strategy/BLP-04-adoption-push.md   # NEW, ~150 lines (authored at F-1 close per Q5)
docs/product/02_PRD/INDEX.md                              # Already updated 2026-05-28 (registry)
docs/product/_backlog/BACKLOG.md                          # Already regenerated 2026-05-28
specs/296-*/                                              # This feature workspace
```

### External Artifacts (out-of-tree)

```
LinkedIn post (maintainer account)                        # 1 native-content post, URL → Issue #296
davidmatousek/Cybersecurity-Content (article PR)          # ~3000 words, §a–§f, URL → Issue #296
davidmatousek/davidmatousek (profile refresh PR)          # tachi flagship surface, URL → Issue #296
Discussion #179 (closing comment + close)                 # @armorer-labs attribution, URL → Issue #296
```

**Structure Decision**: docs + external-distribution single-project. No new source directories. Feature workspace under `specs/296-*/` follows tachi convention (research.md/spec.md/plan.md/tasks.md/checklists/notes).

---

## PM LOW Finding Resolutions (folded inline)

The PM sign-off (2026-05-28, 0H/0M/2L, APPROVED) flagged two LOW findings explicitly marked "may be addressed at `/aod.plan` without re-review". Both are resolved here:

### L-1: SC-014 verify-list 1:1 alignment with FR-012(a)–(e)

PM's recommendation: restructure SC-014 verify as a 5-item bulleted list aligned 1:1 with FR-012(a)–(e). **Adopted in plan.md** (carried verbatim to tasks.md verification fixtures). Verification template:

```
SC-014 verify (5-item):
- [a] `docs/product/_internal/strategy/BLP-04-adoption-push.md` (or equivalent) contains the
       4-feature sequencing rationale (F-1 → F-2 → F-3 → F-4).
- [b] Doc contains BLP-03 trigger mechanics including enterprise-buyer-signal acceptance
       criteria (US-7: ≥3 inbound signals across stars/watches/issues/discussions/direct
       contacts that name enterprise-buyer evaluation context).
- [c] Doc contains §3 Sequencing Discipline narrative (writing-voice vs code-voice + asset-tag
       distinctness + release-cadence restoration window).
- [d] Doc states F-2 kickoff target (Fri 2026-06-05 AM or Mon 2026-06-08 AM at latest;
       Team-Lead M-3).
- [e] Doc states explicit "F-2 PRD/spec/plan/tasks may not be drafted before F-1 close
       timestamp" language (Team-Lead M-1).
- Doc is referenced from F-1 close-out commit and Issue #296 closing comment.
```

### L-2: FR-003 §b example-pairing soft framing

PM's recommendation: soften the example pairing list so readers don't interpret it as a hard requirement on exactly those 3 examples. **Adopted in plan.md** (carried verbatim to tasks.md):

> FR-003 §b: MUST pair 2–3 example runs to cover all 5 framework slots. **Recommended** (but not exclusive): `examples/web-app/` + `examples/agentic-app/` + one of `examples/predictive-ml-app/`, `examples/mobile-banking-app/`, or `examples/maestro-reference/`. **Other combinations that cover all 5 slots are acceptable** — author chooses based on reproducibility ergonomics. Reproducibility is anchored to per-framework `Coverage Attestation` PAGE in `security-report.pdf` (byte-deterministic per ADR-021), NOT narrative outputs.

No spec.md edit required — these are plan-layer instructions to the article author. If Architect or Team-Lead Triad review at plan stage requests an explicit spec.md amendment, that lands at tasks.md (no spec rerun).

---

## Architect MEDIUM Finding Resolutions (folded inline)

The Architect plan-layer sign-off (2026-05-28, 0H/2M/3L, APPROVED_WITH_CONCERNS) flagged two MEDIUM technical-correctness findings. Both resolved here:

### M-1: Wave 0 baseline-path glob inconsistency

**Observation**: `examples/*/sample-report/security-report.pdf.baseline` matches only 4 of the existing baselines (`agentic-app`, `consumer-agent-app`, `mobile-banking-app`, `predictive-ml-app`); the `examples/web-app/` baseline lives at the top-level (`examples/web-app/security-report.pdf.baseline`), so the recipe fails verbatim for the recommended Web/API pairing.

**Resolution** (folded into Wave 0 template above): the OWASP_COVERAGE.md "Reproducibility" section now documents both baseline layouts explicitly (nested vs top-level) and provides two recipe variants. Tasks.md author MUST use the path matching the example's actual layout.

### M-2: Wave 2 §b example-count upper bound tight vs 5-slot coverage

**Observation**: 3 single-slot examples cover ≤3 framework slots; full 5-slot coverage requires either 4+ examples OR slot-bridging examples (e.g., `agentic-app` covers Agentic + LLM; `web-app` covers Web + API).

**Resolution** (folded into Wave 2 §b template above): upper bound widened from "2–3" to "2–4" examples. Slot-bridging trade-off explicitly documented. Author chooses based on walkthrough ergonomics.

### L-1, L-2, L-3 deferred to tasks.md

Per Architect "All concerns are tasks.md-layer authoring instructions":
- **L-1** (README hero `\*` escape-render check on github.com): tasks.md adds a render-check sub-step before in-tree merge. Mitigation: swap to unicode dagger (`†`) or superscript `(¹)` if render is broken.
- **L-2** (§d ADR-lineage depth not explicitly bounded — 700-word budget tight for full 50-catalog-ID enumeration): tasks.md adds a per-§ word-count discipline note; §d prefers ADR/agent enumeration over per-catalog-ID enumeration.
- **L-3** (profile-template footer wording): tasks.md leaves at author discretion within ADR-044 dual-frame alignment.

PM plan-layer sign-off (0H/0M/2L) also flagged 2 LOW concerns (cadence elasticity / Discussion incubation explicit deferral + FR-009 follow-up Issue template) — both folded into tasks.md fixtures.

---

## Phase 0: Wave-0 Prerequisites — Canonical Anchor Authoring

**Prerequisite gate**: `docs/standards/OWASP_COVERAGE.md` (≤80 lines) MUST exist before any Wave 1 work begins. This is the Architect H2 Option B lean. Wave 0 lands as the first build step.

### Wave 0 design: `docs/standards/OWASP_COVERAGE.md`

**Length budget**: ≤80 lines (Architect H2 Option B). If exceeded, Architect sign-off required.

**Composition source-of-truth (read-only)**:
- `schemas/taxonomy/owasp.yaml` — 6 buckets × 10 items = 60 records (verified at research time, 2026-05-28; `grep -c "^- id:"` = 60).
- ADR-024 → ADR-037 — per-framework closure ADRs (full lineage in research.md §3).
- ADR-045 — F-292 cross-sink refinement; line 133 attributes @armorer-labs.
- ADR-029 — Coverage Attestation report section contract.
- ADR-037 D-2 — Web/API combined-slot narrative compression.
- Per-baseline `Coverage Attestation` page in `examples/*/sample-report/security-report.pdf.baseline` (byte-deterministic per ADR-021 + ADR-029 + ADR-037 D-11).

**Section outline** (≤80 lines, ~7 sections):

```markdown
# OWASP Five-Framework Coverage Matrix (50/50)

Canonical reference for tachi's OWASP coverage claim. Composed from
`schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage.

## Headline

**OWASP five-framework total: 50/50 Covered** (LLM 2025 10/10 + Agentic 2026
10/10 + ML 2023 10/10 + Mobile 2024 10/10 + Web/API 2021/2023 10/10).

The schema (`schemas/taxonomy/owasp.yaml`) carries **6 framework buckets ×
10 items = 60 records**. The "five-framework" headline compresses Web Top
10:2021 (A01–A10) and API Security Top 10:2023 (API1–API10) into one
narrative slot per ADR-037 D-2.

## Matrix

| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |
|---|---|---|---|---|---|
| LLM 2025 | OWASP-LLM-2025 | LLM01–LLM10 | 10/10 | https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ | ADR-030, ADR-031, ADR-034, ADR-045 |
| Agentic 2026 | OWASP-AGENTIC-2026 | ASI01–ASI10 | 10/10 | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | ADR-032, ADR-033 + pre-BLP-01 |
| ML 2023 | OWASP-ML-2023 | ML01–ML10 | 10/10 | https://owasp.org/www-project-machine-learning-security-top-10/ | ADR-035 |
| Mobile 2024 | OWASP-MOBILE-2024 | M1–M10 | 10/10 | https://owasp.org/www-project-mobile-top-10/ | ADR-036 |
| Web 2021 | OWASP-2021 | A01–A10 | 10/10 | https://owasp.org/Top10/ | ADR-037 |
| API 2023 | OWASP-API-2023 | API1–API10 | 10/10 | https://owasp.org/API-Security/ | ADR-037 |

**Per-bucket total: 60/60.** **Headline framing: 5 slots × 10 items = 50/50** (Web + API combined).

## Reproducibility (byte-deterministic)

The per-framework `Coverage Attestation` page in committed baselines is
byte-deterministic under `SOURCE_DATE_EPOCH=1700000000` (ADR-021 +
ADR-029 + ADR-037 D-11). **Baseline layouts differ across examples**:

- **Nested layout** (4 baselines: `agentic-app`, `consumer-agent-app`,
  `mobile-banking-app`, `predictive-ml-app`):
  `examples/{name}/sample-report/security-report.pdf.baseline`
- **Top-level layout** (e.g., `web-app`):
  `examples/{name}/security-report.pdf.baseline`

The recipe below uses the nested-layout `agentic-app` baseline; swap the
path to match the example's actual layout when reproducing on others.

\`\`\`bash
# Nested-layout example (agentic-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/
diff examples/agentic-app/sample-report/security-report.pdf{,.baseline}
# Compare specifically the Coverage Attestation page bytes.

# Top-level-layout example (web-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/web-app/
diff examples/web-app/security-report.pdf{,.baseline}
\`\`\`

## Anti-claims (NOT covered by 50/50)

- Zero-false-positive guarantee.
- Coverage of OWASP frameworks NOT enumerated above (e.g., OWASP IoT, OWASP Serverless).
- Application-source-code SAST replacement.
- CVE detection (SCA) replacement.

## See also

- [Threat Categories](../../README.md#threat-categories) — the 14 specialized agents.
- [`schemas/taxonomy/owasp.yaml`](../../schemas/taxonomy/owasp.yaml) — machine-readable source-of-truth.
- ADR-024 → ADR-037 + ADR-045 — per-framework closure decisions.
```

This outline targets ~70 lines; remaining 10-line budget reserved for prose polish and any reviewer-requested additions during build review.

**Indexed at**: `docs/standards/README.md` — append one row: `| [OWASP_COVERAGE.md](OWASP_COVERAGE.md) | OWASP five-framework coverage matrix (50/50) — canonical anchor, reproducibility recipe, anti-claims |`.

---

## Phase 1: Wave-1 through Wave-5 Distribution Artifact Design

### Wave 1: README hero block + FR-008 narrative-defensibility pre-check

**File**: `README.md`
**Insertion point**: between line 14 (`---` divider) and line 17 (`## What is tachi?` H2) — preserves `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference at line 7 + Get-Started line 13.
**Diff budget**: ≤30 lines (FR-011 + SC-011). Escape hatch (Architect M4) cited in CHANGELOG entry + close-out commit if exceeded.

**Hero block template** (~22 lines, leaving 8-line slack):

\`\`\`markdown
## OWASP Coverage

**50/50 across five frameworks** — every catalogued threat in each framework
has a tachi detection agent.

| Framework | Coverage | Anchor |
|---|---|---|
| OWASP LLM Top 10 (2025) | 10/10 | [LLM 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) |
| OWASP Agentic Top 10 (2026) | 10/10 | [Agentic 2026](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) |
| OWASP ML Security Top 10 (2023) | 10/10 | [ML 2023](https://owasp.org/www-project-machine-learning-security-top-10/) |
| OWASP Mobile Top 10 (2024) | 10/10 | [Mobile 2024](https://owasp.org/www-project-mobile-top-10/) |
| OWASP Web/API\* (2021 + 2023) | 10/10 | [Web 2021](https://owasp.org/Top10/) · [API 2023](https://owasp.org/API-Security/) |

\\* Web/API combined slot: OWASP Web Top 10:2021 (A01–A10) + OWASP API
Security Top 10:2023 (API1–API10) — 20 items, 20/20.

Canonical matrix: [`docs/standards/OWASP_COVERAGE.md`](docs/standards/OWASP_COVERAGE.md) ·
Byte-deterministic Coverage Attestation: [examples/*/sample-report/](examples/)
\`\`\`

**Existing line-29 50/50 mention**: at hero-author discretion within the 30-line cap, the body mention may stay (redundant but harmless) or be deduped. **Default lean: leave in place** to avoid scope creep on the body section and to keep the diff at ≤30 lines.

**FR-008 narrative-defensibility pre-check** runs in parallel during Wave 1, evidence captured in `specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md`:

\`\`\`markdown
# Narrative-Defensibility Pre-Check (FR-008 / SC-009)

**Date**: 2026-05-29 (Day 1 PM)
**Author**: maintainer

## Sources verified

- [ ] `docs/standards/OWASP_COVERAGE.md` (canonical anchor — Wave 0 output)
- [ ] `schemas/taxonomy/owasp.yaml` — 6 buckets × 10 items = 60 records (`grep -c "^- id:" schemas/taxonomy/owasp.yaml`)
- [ ] Per-baseline `Coverage Attestation` byte-deterministic reproduction (≥1 example):
    SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/
    diff examples/agentic-app/sample-report/security-report.pdf{,.baseline} → empty
- [ ] OWASP framework canonical URLs (6 anchors, all 200 OK):
    - LLM 2025: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
    - Agentic 2026: https://genai.owasp.org/2025/12/09/...
    - ML 2023: https://owasp.org/www-project-machine-learning-security-top-10/
    - Mobile 2024: https://owasp.org/www-project-mobile-top-10/
    - Web 2021: https://owasp.org/Top10/
    - API 2023: https://owasp.org/API-Security/

## Halt-condition

If any framework's bucket count ≠ 10 OR any URL returns non-200 OR any
ADR-anchor reference is broken: HALT, scope-reduce the claim to the
verified subset, do NOT publish unverified surfaces.
\`\`\`

**Wave 1 also includes**: CHANGELOG entry under "Unreleased" (~10 lines).

CHANGELOG entry template:

\`\`\`markdown
### OWASP Coverage Matrix Documentation (F-296)

- Add `README.md` hero OWASP coverage block (5-framework, 50/50; Web/API combined-slot footnote).
- Add canonical anchor `docs/standards/OWASP_COVERAGE.md` (composes from `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage).
- Index entry in `docs/standards/README.md`.
- See PRD #296 and BLP-04 strategy doc (`docs/product/_internal/strategy/BLP-04-adoption-push.md`) for context.
\`\`\`

### Wave 2: Cybersec article — `~3000 words, §a–§f`

**Target repo**: `davidmatousek/Cybersecurity-Content` (separate GitHub repo per `reference_cybersecurity_content_repo.md`).
**Word budget**: 2400–3600 (~3000 ±20%; PRD FR-3 ±20% band confirmed via PRD Q1 default).
**Filename pattern**: `articles/2026-06-01-50-50-owasp-coverage-tachi-distribution.md` or equivalent matching the repo's existing structure (to be confirmed at build time).

**Article structure** (§a–§f):

\`\`\`
§a — Problem framing + 50/50 headline (per-bucket breakdown)
  - 6 buckets × 10 items = 60 records (separate Web 2021 + API 2023 URLs)
  - Five-slot 50/50 narrative compression (combined Web/API explicit)
  - "What 10/10 means": catalogued threats × detection agents (not zero-FP)
  ~400 words

§b — Verification walkthrough (2–4 example runs)
  - Recommended pairing (soft per PM L-2; bound widened to 2–4 per Architect M-2):
    examples/web-app/ (Web/API combined) + examples/agentic-app/ (Agentic + LLM)
    + examples/predictive-ml-app/ (ML) + examples/mobile-banking-app/ (Mobile)
    OR substitute examples/maestro-reference/ as a multi-slot bridging architecture.
  - **Slot-bridging trade-off** (Architect M-2): three single-slot examples cover
    ≤3 framework slots; full 5-slot coverage requires either (a) 4 examples
    one-per-slot OR (b) at least one slot-bridging example (e.g., agentic-app
    covers Agentic + LLM; web-app covers Web + API). Choose based on
    walkthrough ergonomics.
  - **Baseline layout note** (Architect M-1): baselines exist in two layouts —
    nested (most examples; `examples/{name}/sample-report/...`) and top-level
    (e.g., `examples/web-app/security-report.pdf.baseline`). Reproducibility
    recipe uses correct path per example (see OWASP_COVERAGE.md reproducibility
    section).
  - Single-architecture impossible by construction (Architect M1)
  - Byte-deterministic Coverage Attestation page reproduction recipe
    (SOURCE_DATE_EPOCH=1700000000 + diff)
  - Code blocks with command + expected output (no screenshots)
  ~700 words

§c — Coverage matrix table
  - Derived from docs/standards/OWASP_COVERAGE.md (Wave 0 anchor)
  - Per-bucket counts + per-framework ADR lineage
  ~300 words (mostly table)

§d — "10/10" framing per framework
  - Per framework: which threats (catalog IDs), which agents, which ADRs
  - ADR-024 → ADR-037 + ADR-045 lineage
  ~700 words

§e — Link back to tachi repo
  ~100 words

§f — Contribution invitation (US-8 / PM L-1)
  - 1–3 sentences pointing to Discussions, Issues, F-260/F-292 community-merge precedent
  - Names the comment-first-give-choice path A default
  ~150 words

Frontmatter/headings/links: ~50–100 words
Total target: 2400–3600 (~3000)
\`\`\`

**NFR-008 self-review checklist** (must pass before self-merge, ≥24h hold):
- [ ] (a) framework citation accuracy (every OWASP URL is 200 OK; every framework count is 10/10)
- [ ] (b) coverage matrix accuracy (matches `docs/standards/OWASP_COVERAGE.md` + `schemas/taxonomy/owasp.yaml`)
- [ ] (c) verification walkthrough reproducibility (commands run; output matches; `SOURCE_DATE_EPOCH=1700000000` cited)
- [ ] (d) link validity (no broken URLs to tachi repo, ADRs, or external)
- [ ] (e) word count in 2400–3600 band
- [ ] (f) **asset-tag mention NOT present** (FR-007 sequencing guard; Team-Lead L-2)

### Wave 3: GitHub profile refresh + LinkedIn post draft

**Profile refresh PR**: `davidmatousek/davidmatousek` repo, README delta.
- Tachi flagship surface with 50/50 tagline + STRIDE+AI harness description + repo link.
- AOD-Kit secondary position (visible, not removed).
- Minimal scope per Q7 lean — flagship project table only (no "Now" section).
- Self-merge after ≥24-hour hold mirror (R4 mitigation).

**Profile README block template** (~20 lines):

\`\`\`markdown
## Flagship project: tachi

**[tachi](https://github.com/davidmatousek/tachi)** — Threat Modeling and
Vulnerability Detection Harness for Claude Code. AI-Reasoning Scanner —
STRIDE + AI + MAESTRO. **OWASP 50/50 coverage** across LLM 2025 + Agentic
2026 + ML 2023 + Mobile 2024 + Web/API 2021/2023.

SAST catches syntax-level bugs; tachi reasons over your architecture
description to catch logic-level ones.

## Methodology backing: AOD-Kit

**[AOD-Kit](https://github.com/davidmatousek/agentic-oriented-development-kit)** — Agentic-Oriented Development Kit. The SDLC Triad methodology (PM + Architect + Team-Lead sign-offs) that governs how tachi is built.
\`\`\`

**LinkedIn post template** (~250 words, native-content-first per 2026 algorithm research):

\`\`\`
50/50 OWASP coverage milestone for tachi — every catalogued threat in
LLM 2025, Agentic 2026, ML 2023, Mobile 2024, and Web/API 2021/2023 now
has a detection agent.

What 10/10 means: the agent for each framework slot catches every threat
catalogued in that OWASP framework. Not zero-false-positive, not full-app
coverage — catalogued-threat coverage with reproducible verification.

This thread responds to Daniel Wood's BLP-02 enterprise-hardening
discussion (2026-05-02) — Daniel flagged three gaps in tachi's enterprise
posture. Three iterations later, all six BLP-02 features shipped through
v4.36.0 (2026-05-14), and the 50/50 coverage closure (BLP-01) shipped
2026-05-01.

How to verify yourself: clone tachi, run `/tachi.security-report` on any
example architecture with `SOURCE_DATE_EPOCH=1700000000` set, and the
Coverage Attestation page bytes match the committed baseline. No marketing
trust required — byte-deterministic anchor (ADR-021 + ADR-029 + ADR-037).

Long-form article with the full per-bucket breakdown + verification
walkthrough: [Cybersec article URL]

Repo: https://github.com/davidmatousek/tachi
BLP-02 closure receipts: https://github.com/davidmatousek/tachi/pull/293
\`\`\`

**LinkedIn algorithm discipline (2026)**:
- Native-content first; deliver core insight in post body.
- Article URL inline in body acceptable (per research §4: link-in-body reduces reach ~18.8%, but link-in-comments-as-primary-CTA is suppressed ~80% — net-net: in-body is the lesser penalty).
- No hashtag spam (LinkedIn 2026 topic detection replaced hashtag signal).
- Schedule for peak audience window (first 60–90 min governs reach).
- Tone discipline: name the gap (Daniel Wood's specific feedback), name the fix (six BLP-02 features), ship the receipts (PR #293). No sycophancy.

### Wave 4: Discussion #179 closing comment + close

**Discussion**: https://github.com/davidmatousek/tachi/discussions/179
**Status verification**: `gh discussion view 179 --repo davidmatousek/tachi` at build time to confirm discussion remains open (Assumption A-4).

**Closing comment template** (~300 words, drafted Day 1 PM for incubation per Team-Lead L-3):

\`\`\`
**Shipped:** F-292 Output-Integrity Cross-Sink Refinement (v4.36.0,
2026-05-14, PR #293).

Thanks to @armorer-labs's gap-analysis comment (2026-05-12) surfacing
three pattern-catalog gaps, we shipped a refinement of the
`output-integrity` agent that addresses each:

1. **Vector-filter / search-DSL injection**: new Cat 6 pattern in
   `.claude/skills/tachi-output-integrity/references/detection-patterns.md`,
   CWE-943, OWASP LLM08:2025.
2. **Package-manager / CI-workflow execution sinks**: trigger-keyword
   extension on existing Cat 1, mitigations include registry allowlist +
   sandbox isolation + Sigstore signature verification.
3. **Cross-agent handoff sinks** (tool-call argument + durable-memory
   write): new Gap 3 subsection with Memory-Promotion Rules schema
   example; cross-link to `tool-abuse` and `data-poisoning` agents.

Architectural decisions documented in ADR-045 (`docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md`, line 133 attributes @armorer-labs's gap-analysis contribution).

CHANGELOG: see v4.36.0 entry (also attributes @armorer-labs).

The community-merge precedent is the F-260 (@north-echo, PR #262, v4.31.0)
contribution chain — comment-first-give-choice → maintainer
gap-analysis → PRD → spec → plan → tasks → ADR → implementation →
CHANGELOG attribution. F-292 followed the same chain.

Closing as **shipped**.

Subsequent distribution (50/50 OWASP coverage milestone, BLP-04 Wave 1)
ships in F-296 (this Issue's parent: #296).
\`\`\`

**Tone discipline anchored in PRD H-1 + R5 + Q3**: @armorer-labs is the **gap-analysis commenter**, NOT "the requester" or "discussion-opener". Lead sentence framing: "Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292" — verbatim per spec US-5 AC-3.

**`gh discussion close`**: after comment publication. Mark as resolved / shipped status.

### Wave 5: F-1 close-out — BLP-04 strategy doc + memory carve-out + Issue #296 close + PR ready-for-review

#### Wave 5.1: BLP-04 strategy doc (Q5 lean)

**File**: `docs/product/_internal/strategy/BLP-04-adoption-push.md` (gitignored `_internal/` directory; ~150 lines).

**Structure** (5 required topics per FR-012 + SC-014 5-item verify per PM L-1):

\`\`\`markdown
# BLP-04 Adoption Push — Strategy

**Initiative**: BLP-04 (4-feature)
**PROPOSED**: 2026-05-28
**Status**: In flight as of F-1 close

## §1: 4-feature sequencing rationale (FR-012 §a)

F-1 → F-2 → F-3 → F-4 sequential:
- F-1 (Issue #296): 50/50 OWASP coverage distribution launch (this feature).
- F-2 (F-260b @north-echo asset-tag output wiring): SARIF schema wiring,
  risk-scorer populator, finding.yaml `affected_assets[]` plumbing.
- F-3 (BLP-04 Wave 2): adoption signal capture (instrumented per BLP-03
  trigger acceptance criteria below).
- F-4 (BLP-04 Wave 3): MAESTRO 7-layer announcement.

## §2: BLP-03 trigger mechanics + enterprise-buyer signal acceptance (FR-012 §b / US-7)

**Trigger condition #1** (already met): BLP-02 closed 2026-05-14.
**Trigger condition #2** (this initiative manufactures): enterprise-buyer
signal.

**Enterprise-buyer signal acceptance**:
- Definition: ≥1 inbound that names enterprise evaluation context — team
  / org name, evaluation rubric, SOC2 / FedRAMP / SLSA framing, or
  procurement intent.
- Capture mechanism: Issue label `signal:enterprise-buyer`, Discussion
  category, or maintainer-noted DM.
- Aggregation threshold for BLP-03 trigger: ≥3 signals across all 5 F-1
  surfaces.
- Measurement window: from F-1 close through F-3 close (BLP-04 Wave 2).

## §3: Sequencing Discipline narrative (FR-012 §c / NFR-006)

Writing-voice (F-1: long-form article, LinkedIn post, Discussion close)
vs code-voice (F-2: SARIF wiring, populator, schema plumbing) preserved
by sequential execution. Asset-tag (F-2) gets its own distribution
moment. Release-cadence break (NFR-005) restored within ~1 week.

## §4: F-2 kickoff target (FR-012 §d / Team-Lead M-3)

**Earliest F-2 start**: 2026-06-05 (Fri, Buffer-1 day if F-1 closes on
2026-06-04 target).
**Latest F-2 start**: 2026-06-08 AM (Mon) to preserve ~1-week cadence
restoration window before 2026-06-11 NFR-005 ceiling.
**F-2 ship deadline**: 2026-06-11 (per FR-007 + Architect M2).

## §5: F-2 no-pre-draft binding (FR-012 §e / Team-Lead M-1)

F-2 PRD, spec, plan, tasks may NOT be drafted before F-1 close timestamp.
No `/aod.discover`, `/aod.define`, `/aod.spec`, `/aod.plan`, `/aod.tasks`,
or `/aod.build` invocations for F-2 may occur during the F-1 acceptance
window.

## §6: Release-cadence carve-out (NFR-005(d) memory anchor)

F-1 ships `docs:` (no release-please bump). The carve-out is documented
in project memory `feedback_aod_deliver_release_gate.md` (SC-013 + FR-013).
Conditions: docs-only feature + follow-on `feat:` within ~1 week.

## §7: References

- Memory: `project_blp04_adoption_push.md`
- PRD #296
- Spec: `specs/296-*/spec.md`
- Plan: `specs/296-*/plan.md`
- F-260 community-merge precedent: PR #262, v4.31.0
- F-292 (BLP-02 origin): PR #293, v4.36.0
\`\`\`

#### Wave 5.2: Memory carve-out update

**File**: `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/feedback_aod_deliver_release_gate.md`

**Update**: append a section documenting the F-1-and-similar carve-out:

\`\`\`markdown
## Carve-out: docs-only features (added 2026-05-XX at F-296 close-out)

Conditions under which `/aod.deliver` does NOT yield a release-please PR
(and the absence is EXPECTED, not a release-please skip incident):

- Feature ships `docs:`-prefixed (e.g., `docs(NNN):` PR title +
  `docs:`-prefixed CHANGELOG subsection).
- Follow-on `feat:` / `fix:` / `perf:` feature ships within ~1 week to
  restore release cadence.
- Cadence break explicitly acknowledged in PRD NFR (e.g., F-296 NFR-005).

Example: F-296 (BLP-04 Wave 1; `docs(296):`; release-please correctly
skipped; F-2 F-260b restored cadence by 2026-06-11).

Do NOT invoke F-212 empty-`feat(NNN):` marker-commit recovery flow for
intentional `docs:`-prefixed deliveries — that recovery flow is for
release-please failures on `feat:`-prefixed merges only.
\`\`\`

#### Wave 5.3: Issue #296 close

**Closing comment** on Issue #296 (~300 words, all 5 artifact URLs):

\`\`\`
F-1 closed.

**Artifacts shipped** (all 5 URLs):
1. **README hero PR (in-tree)**: [PR #297](https://github.com/davidmatousek/tachi/pull/297) — `docs(296):` squash-merged.
2. **LinkedIn post**: [URL]
3. **Cybersec article**: [PR URL in davidmatousek/Cybersecurity-Content]
4. **GitHub profile refresh**: [PR URL in davidmatousek/davidmatousek]
5. **Discussion #179 close**: [discussion URL with closing comment].

**FR-008 pre-check evidence**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md`.

**SC-007 verification**: zero F-2/F-260b/asset-tag commits during F-1
window (verified via `git log --grep ...`).

**BLP-04 strategy doc**: `docs/product/_internal/strategy/BLP-04-adoption-push.md` (5 §§ per FR-012).

**Release-cadence**: F-1 ships `docs:`; release-please correctly
skipped per `docs:` mapping (EXPECTED; Architect M3). F-2 (F-260b
asset-tag wiring) target ship: 2026-06-11.

**Memory carve-out**: `feedback_aod_deliver_release_gate.md` updated
with docs-only carve-out (SC-013 + FR-013).
\`\`\`

#### Wave 5.4: PR #297 ready-for-review

`gh pr ready 297` after in-tree squash-merge gate passes.

---

## File-touch matrix

| File | Wave | Action | LOC delta | Notes |
|---|---|---|---|---|
| `README.md` | 1 | edit | ≤30 (FR-011 + SC-011) | Hero block insertion between line 14 + line 17 |
| `CHANGELOG.md` | 1 | edit | ~10 | "Unreleased" > `### OWASP Coverage Matrix Documentation (F-296)` |
| `docs/standards/OWASP_COVERAGE.md` | 0 | create | ≤80 (Architect H2) | New canonical anchor |
| `docs/standards/README.md` | 0 | edit | +1 (~3) | Index row for OWASP_COVERAGE.md |
| `specs/296-*/notes/narrative-defensibility-check.md` | 1 | create | ~30 | FR-008 pre-check evidence |
| LinkedIn post (external) | 3/4 | publish | ~250 words | Maintainer LinkedIn |
| `davidmatousek/Cybersecurity-Content` (external PR) | 2 | create | ~3000 words | New article |
| `davidmatousek/davidmatousek` (external PR) | 3 | edit | ~20–40 (README) | Flagship surface refresh |
| Discussion #179 close comment | 4 | post + close | ~300 words | @armorer-labs gap-analysis attribution |
| `docs/product/_internal/strategy/BLP-04-adoption-push.md` | 5 | create | ~150 | 5 §§ per FR-012 |
| `feedback_aod_deliver_release_gate.md` (memory) | 5 | edit | ~30 | Docs-only carve-out (SC-013 + FR-013) |
| Issue #296 close comment | 5 | post + close | ~300 words | 5 artifact URLs |

**Allowed file set verification** (SC-010): all in-tree files above are within the allowed file set (`README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md`, `docs/product/02_PRD/296-*.md`, `docs/product/02_PRD/INDEX.md`, `docs/product/_backlog/BACKLOG.md`, `docs/product/_internal/strategy/BLP-04-adoption-push.md`, `specs/296-*/`, `.aod/results/*.md`). Zero files modified under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, `.aod/scripts/`.

---

## Order of operations at delivery time (F-272 D-6 pattern)

**In-tree work merges first; out-of-tree fires post-merge inside acceptance window.** Pre-publication FR-008 narrative-defensibility check runs before any external surface ships.

\`\`\`
Wave 0 (Day 1 PM)   → docs/standards/OWASP_COVERAGE.md (≤80 lines) + index row
                      [/aod.build sub-step]
Wave 1 (Day 1 PM)   → README hero block + CHANGELOG entry
                      + FR-008 pre-check evidence
                      [/aod.build sub-step; can parallelize with Wave 0]
Wave 4-draft (Day 1 PM) → Discussion #179 closing comment DRAFTED (not published)
                          for incubation (Team-Lead L-3 optional)
                          → drafts file: specs/296-*/notes/discussion-179-draft.md
Wave 2 (Day 2)      → Cybersec article DRAFT (~3000 words; §a–§f)
Wave 2 (Day 2 PM)   → Self-review pass 1 against NFR-008 checklist
                      (compressed Day 2 PM is acceptable if needed — Team-Lead L-1)
Wave 3 (Day 3 AM)   → GitHub profile refresh PR open + LinkedIn post draft
Wave 3 (Day 3 PM)   → Cybersec article 24-hour hold complete; self-merge

== IN-TREE PR MERGE GATE ==
At any time after Wave 0 + Wave 1 complete (typically Day 1 PM or Day 2 AM),
the in-tree PR #297 can squash-merge. Out-of-tree work continues in parallel.

Wave 4 (Day 4 AM)   → LinkedIn post publishes (AFTER Cybersec article merge per Q2 lean)
Wave 4 (Day 4 PM)   → GitHub profile PR self-merge (after 24-hour hold)
Wave 4 (Day 5 AM)   → Discussion #179 closing comment PUBLISHED (from Day 1 PM draft)
                      + gh discussion close 179
Wave 5 (Day 5 PM)   → BLP-04 strategy doc authored (Q5 lean)
                      + memory carve-out updated (SC-013)
                      + Issue #296 closed with 5 URLs
                      + PR #297 ready-for-review → squash-merge if not already merged
\`\`\`

**Critical-path adjustments per Team-Lead L-1**: if Cybersec article drafting consumes the full Day 2, self-review pass 1 slips to Day 3 AM, and the 24-hour hold ends Day 3 PM. This compresses Wave 3 AM but keeps the overall timeline within target.

**Buffer days**: Buffer-1 (2026-06-05 Fri), Buffer-2 (2026-06-08 Mon). Hard ceiling 2026-06-11 (NFR-007 escalation).

---

## Verification matrix

| SC | Verification method | Automation level | Owner |
|---|---|---|---|
| SC-001 | `git log --oneline -1 README.md` + render `README.md` first 80 lines on github.com | semi-automated | maintainer |
| SC-002 | `gh issue view 296 --comments` contains LinkedIn URL; URL renders maintainer-authored post | [MANUAL-ONLY] | maintainer |
| SC-003 | `gh pr view {cybersec-PR-URL}` + word count check (2400–3600); §a–§f present | semi-automated | maintainer |
| SC-004 | `gh issue view 296 --comments` contains profile PR URL; URL renders flagship section | [MANUAL-ONLY] | maintainer |
| SC-005 | `gh discussion view 179`: status closed; comment cites F-292 + v4.36.0 + ADR-045 line 133 + @armorer-labs gap-analysis attribution | semi-automated | maintainer |
| SC-006 | `git log main -- CHANGELOG.md`: commit cites Issue #296; subject uses `docs:` (NOT `feat:`); PR title `docs(296):` | automated | maintainer |
| SC-007 | `git log --all --grep="F-2\|F-260b\|asset-tag wiring" --since="2026-05-28"`: zero substantive commits (after Architect L1 false-positive review) | semi-automated | maintainer |
| SC-008 | `gh issue view 296 --comments`: closing comment has all 5 URLs | semi-automated | maintainer |
| SC-009 | `specs/296-*/notes/narrative-defensibility-check.md` exists; first commit timestamp BEFORE LinkedIn URL + article PR merge timestamps | automated | maintainer |
| SC-010 | `git diff main --name-only`: zero files outside allowed set | automated | maintainer |
| SC-011 | `git diff main -- README.md \| grep -E "^[+-]" \| wc -l` ≤30 | automated | maintainer |
| SC-012 | `gh issue view 296`: close-timestamp ≤ 2026-06-11 23:59 UTC | automated | maintainer |
| SC-013 | `feedback_aod_deliver_release_gate.md` mtime > 2026-05-28 + content documents docs-only carve-out | automated | maintainer |
| SC-014 | 5-item list verification per PM L-1 fold-in above (a/b/c/d/e + cross-link) | automated | maintainer |

---

## Risks and mitigations (plan-layer additions to PRD §Risks)

| Risk | Mitigation | Source |
|---|---|---|
| `docs/standards/OWASP_COVERAGE.md` ≤80-line cap exceeded during authoring | If draft exceeds 80 lines, trim Anti-claims section + "See also" section first; if still over, scope-reduce Matrix to 5 narrative slots (drop Web/API per-bucket split — combined slot only) | Wave 0 design |
| README hero diff exceeds 30 lines | FR-011 escape hatch invoked; Architect sign-off cited in CHANGELOG + close-out commit | Architect M4 |
| Cybersec article ~3000-word band exceeded under § verbosity pressure | Drop §d depth (per-framework ADR enumeration) first; §f stays (PM L-1 binding); §b stays (Architect M1 binding) | NFR-008 + PRD R3 |
| LinkedIn post draws material critique (R1) | FR-009 material-critique definition pre-decided in spec (named gap OR verifiable counter-example OR ≥5 confirming independent reactions/replies); response in-thread per NFR-003 | PM L-2 + PRD R1 |
| Discussion #179 close comment lands before incubation period; tone discipline at risk | Team-Lead L-3 optional: draft Day 1 PM, publish Day 5 AM. Incubation period = 4 days. Spec US-5 AC-3 lead-sentence framing enforced | Team-Lead L-3 |
| F-2 work begins in parallel violating BLP-04 §3 (R7) | FR-007 + SC-007 binary check at close; Architect L1 false-positive carve-out applies; offending commits reverted or held | Architect L1 + PRD R7 |
| Release-please skip incorrectly triggers F-212 marker-commit recovery flow | Edge Case + NFR-005 + Architect M3: `docs(296):` skip is EXPECTED; do NOT invoke F-212 recovery flow | Architect M3 |
| `docs/standards/OWASP_COVERAGE.md` first-of-kind anchor file gets inconsistent links across artifacts | All in-tree + out-of-tree artifacts back-link to the same canonical anchor (Architect H2 anchor reuse pattern); FR-008 pre-check verifies anchor existence before any external surface ships | Architect H2 |

---

## Open questions resolved (PRD Q1–Q7)

The 7 PRD-deferred questions are resolved here per the PRD-layer leans (already approved in Triad review):

| Q | Decision | Reference |
|---|---|---|
| Q1 (Cybersec article length tolerance) | ±20% (2400–3600) — PRD default. Discipline applied through NFR-008 checklist + word-count gate. | PRD §Q1 lean |
| Q2 (LinkedIn post timing relative to article merge) | (c) AFTER article merges — prevents broken-link risk. Wave 4 ordering reflects this. | PRD §Q2 lean |
| Q3 (Discussion #179 close-comment authorship) | Maintainer authors with explicit @armorer-labs gap-analysis attribution. F-260 precedent applies to PR authorship, NOT to discussion close comments. Spec US-5 AC-3 lead-sentence framing enforced. | PRD §Q3 lean + R5 |
| Q4 (Asset-tag mention deferral) | NO asset-tag mention in any F-1 artifact. NFR-008 self-review checklist §f enforces. | PRD §Q4 + Team-Lead L-2 |
| Q5 (BLP-04 strategy doc authorship timing) | Author at F-1 close-out (Wave 5.1). F-1 results inform Wave 2+ sequencing; pre-F-1 authoring is premature. | PRD §Q5 lean |
| Q6 (CHANGELOG `docs:` prefix) | `docs:` correct. Release-please skip is EXPECTED, NOT incident (Architect M3). | PRD §Q6 lean |
| Q7 (GitHub profile README scope) | Minimal — flagship project table only. No "Now" section (avoid ongoing maintenance burden). | PRD §Q7 lean |

---

## Out-of-scope (deferred to F-2/F-3/F-4 or follow-up Issues)

- **F-2 (F-260b @north-echo asset-tag output wiring)** — BLP-04 Wave 2 sequencing target 2026-06-05 → 2026-06-11; binding constraint.
- **F-3 (BLP-04 Wave 2: adoption signal capture)** — instrument the BLP-03-trigger acceptance criteria defined in BLP-04 strategy doc §2.
- **F-4 (BLP-04 Wave 3: MAESTRO 7-layer announcement)** — separate distribution moment.
- **Hacker News / Reddit / Twitter-X / dev.to crossposts** — F-3+ scope per PRD §Scope.
- **Multi-language coverage messaging** (Spanish, Mandarin, French) — depends on F-3 signal capture.
- **Conference talk submissions referencing 50/50** — depends on F-3 + F-4 closure.
- **Mid-form re-hosts** (dev.to or Medium re-publish of Cybersec article) — depends on F-3.

Any out-of-scope artifact that can NOT complete inside the F-1 acceptance window goes to a follow-up Issue (F-292 pattern: PR #293 close-out commit `a90146e` deferred T017+T026 to Issue #295).
