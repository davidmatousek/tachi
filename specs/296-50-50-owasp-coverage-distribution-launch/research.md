# Research Summary: F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

**Feature**: 296-50-50-owasp-coverage-distribution-launch
**Date**: 2026-05-28
**PRD**: [docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md](../../docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md)

Research was conducted across four parallel surfaces (KB, codebase, architecture, web) before spec generation, per the `/aod.spec` Step 2 mandate. Findings are synthesized here; the spec.md acceptance criteria reference this document via the Architect H2 resolution chain (PRD → research.md → spec.md → plan.md).

---

## 1. Knowledge Base Findings

### F-272 SECURITY.md disclosure (PR #273, 2026-05-08) — closest precedent

Only "docs-only feature with full Triad governance" in the project's history. Same shape as F-1: no code, no tests, no schema delta, no ADR; verification via post-merge `/security` re-scan + manual UI checks. Constitution **Principle VII §Exceptions** was invoked for docs-only DoD (push/test/user-validate substitutions).

- Spec: [specs/272-security-md-disclosure/spec.md](../272-security-md-disclosure/spec.md)
- Plan invoked Principle VII §Exceptions explicitly; "testing" mapped to manual UI inspection of public surfaces.
- Delivery split in-tree work from out-of-tree work — pattern to adopt for F-1.

### README hero refactor precedents

`git log --oneline -- README.md` surfaces prior docs-only hero refreshes that did NOT yield a release:
- `1d8bca4` "docs: update README with MAESTRO, security-report, and recent features"
- `d6ae00e` "docs: refresh README + developer guide for BLP-01 closure"
- `e752f46` "12 → 14 threat agents" counts alignment
- `87d15f2` "docs: feature Developer Guide prominently in README"

**Pattern**: README hero refactors as plain `docs:` are project-precedent; NFR-5 cadence break (no release on F-1) is consistent with prior practice. F-1's NFR-5 acknowledgment formalizes a pattern that was previously implicit.

### Community-attribution precedents

- **F-260 (@north-echo, PR #262, v4.31.0, 2026-05-06)**: comment-first-give-choice (path A contributor-authored / path B maintainer-authored); authorship preserved via CHANGELOG entry + commit trailer. Memory [project_f260_asset_tags.md](../../../../.claude/projects/-Users-david-Projects-tachi/memory/project_f260_asset_tags.md).
- **F-292 (@armorer-labs, PR #293, v4.36.0, 2026-05-14)**: same precedent applied; ADR-045 §"Provenance / Attribution Note" (lines 130–134) codifies the contribution chain ("discussion → maintainer gap-analysis → PRD → spec → plan → tasks → ADR → implementation → CHANGELOG attribution"). Same-day hybrid path B used (offer window collapsed inside 48h).
- **F-292 close-out commit `a90146e`**: deferred 2 post-merge community-engagement tasks (T017 + T026) to follow-up Issue #295 rather than leave open. **Pattern: post-merge community tasks belong in follow-up Issues**, not blocking the close.

### Release-cadence break precedents

Project memory [feedback_aod_deliver_release_gate.md](../../../../.claude/projects/-Users-david-Projects-tachi/memory/feedback_aod_deliver_release_gate.md) requires every `/aod.deliver` to yield a release-please PR. The release-please-config.json mapping of `docs:` / `chore:` / `refactor:` / `test:` / `style:` to "hidden, no bump" is the explicit exception. F-1's `docs(296):` PR title is the deliberate exception; NFR-5 must acknowledge it and SC-013 (added in this spec) records the memory carve-out.

F-212 recovery flow (empty `feat(NNN):` marker commit when release-please silently skips) does NOT apply here — F-296 is intentionally `docs(296):` and the absence of a release PR is the **EXPECTED** behavior, not an incident.

### Sequencing-constraint precedents

- **BLP-02 W4 → W4+ split**: F-4 (#277) and F-5 (#282) were parallel-planned but F-5 was held back to ship solo after F-4 to preserve clean release cadence + reviewer attention.
- **F-260 → F-260b**: Asset-tag prototype merged with explicit follow-on hold; the SARIF/finding-schema/populator wiring was scoped as a separate feature.
- **BLP-04 §3 Sequencing Discipline**: F-1 distribution → F-2 F-260b asset-tag wiring. Rationale: writing-voice vs code-voice focus preservation + asset-tag announcement distinctness + 1-week release-cadence restoration window.

**Pattern**: explicit sequencing holds are documented in the PRD §Sequencing/§Risks and enforced via FR + SC pairs (FR-7 + SC-7 in PRD; FR-007 + SC-007 in this spec).

---

## 2. Codebase Findings

### README.md current state

- **Total lines**: 477.
- **H2 heading structure** (collapse points on github.com): "What is tachi?" (line 17), "Community" (line 40), "Prerequisites" (line 53), "Quick Start" (line 82), "Command Options" (line 190), "How It Works" (line 287), "Threat Categories" (line 341), "OWASP Coverage" (line 369), "Examples" (line 385), "Integration Reference" (line 408), "Known Issues" (line 423), "Built with AOD Kit" (line 442), "Releases" (line 448), "Running Tests" (line 456), "Contributing" (line 469), "License" (line 475).
- **Get-Started line**: line 13 — "**Get started**: [Quick Start](#quick-start) | [Developer Guide](...)".
- **Insertion point for F-1 hero block**: between line 14 (divider `---`) and line 17 (`## What is tachi?`). This aligns with Architect L2 lean.
- **Existing 50/50 mention**: line 29 (within "What is tachi?" section) lists "50/50 across five frameworks". **F-1 promotes this to hero AND adds canonical anchor file**; the body mention may stay or be deduped at hero-author discretion (≤30-line diff cap from FR-11 applies to the hero block, not the body).
- **Existing brand asset**: line 7 references `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` — must be preserved (do NOT collide with hero block).

### schemas/taxonomy/owasp.yaml — canonical source of 6 buckets

- **6 framework buckets × 10 items = 60 records** (`grep -c "^- id:"` = 60).
- Buckets (verified): `OWASP-2021` (A01–A10), `OWASP-API-2023` (API1–API10), `OWASP-AGENTIC-2026` (ASI01–ASI10), `OWASP-LLM-2025` (LLM01–LLM10), `OWASP-MOBILE-2024` (M1–M10), `OWASP-ML-2023` (ML01–ML10).
- Each record schema: `{id, full_id, name, url, cwe_refs: [], out_of_scope: bool, out_of_scope_rationale: string}`.
- Front-matter lines 1–41 contain composition notes + citation-completeness audit-trail + F-241 Wave 3.2 record-shape extension docs.
- **Web/API combined-slot framing** (PRD FR-1a) compresses `OWASP-2021` + `OWASP-API-2023` into one narrative slot for README hero; per Architect H1 resolution, hero MUST include a footnote making the combined-slot explicit, and the Cybersec article (FR-3) MUST show all 6 buckets with separate URLs (FR-3 §a + Architect L3).

### ADR lineage anchors

- **ADR-021** (2026-04-10): SOURCE_DATE_EPOCH=1700000000 for byte-deterministic PDF regeneration. Combined with ADR-029 (Coverage Attestation page) and ADR-037 D-11 (surgical Section 9 backfill), the per-baseline Coverage Attestation page is byte-deterministic.
- **ADR-024** (2026-04-16): OWASP AIVSS Evaluation and Tachi Composite Scoring Posture.
- **ADR-029**: Coverage Attestation report section — per-framework Covered/Partial/Gap classifications computed via `aggregate_coverage_attestation()` in `scripts/extract-report-data.py`. **Denominator = `len(schemas/taxonomy/{framework}.yaml)` per framework** — meaning a single baseline's Coverage Attestation page shows 6 separate framework pages, NOT a combined 50/50 view. The combined view exists only in narrative (`docs/standards/OWASP_COVERAGE.md`, new).
- **ADR-037** (2026-05-01): Web/API Coverage Attestation + Populator Wiring — F-8 Tier 3 Closure + F-A3 Heuristic A Closure across 11 Host Agents. **D-2 narrative compresses Web 2021 + API 2023 into "5 frameworks"** for marketing positioning.
- **ADR-044** (2026-05-07): Dual-Frame Public Positioning — codifies the **harness** positioning that README hero MUST align to:
  - Headline: "Threat Modeling and Vulnerability Detection Harness for Claude Code"
  - Sub-line: "AI-Reasoning Scanner — STRIDE + AI + MAESTRO"
  - Signature: "SAST catches syntax-level bugs; tachi reasons over your architecture description to catch logic-level ones."
- **ADR-045** (2026-05-14): Output-Integrity Cross-Sink Refinement (F-292). **Line 133 attributes @armorer-labs** for gap-analysis contributions via Discussion #179 (2026-05-12).

### examples/ directory — Cybersec article verification walkthrough candidates

- `examples/agentic-app/sample-report/` (9 artifacts) → LLM + Agentic walkthrough.
- `examples/maestro-reference/` (28 subdirs) → MAESTRO showcase.
- `examples/web-app/sample-report/` → Web/API walkthrough.
- `examples/predictive-ml-app/sample-report/` → ML walkthrough (new BLP-01 baseline).
- `examples/mobile-banking-app/sample-report/` → Mobile walkthrough (new BLP-01 baseline).
- `examples/consumer-agent-app/` → F-4 trust-exploitation/ASI09 walkthrough.

All 8 baselines validated byte-identical at ADR-037 D-9. Cybersec article (FR-3 §b) can pair 2–3 example runs to cover all 5 framework slots; single-architecture reproducibility is impossible by construction per Architect M1.

### CHANGELOG.md current state

- **Latest Unreleased section** (lines 10–50+) carries the BLP-02 F-2 hardened-config-load entry.
- **x-release-please-version** marker (line 101) currently `v4.35.0`; release-please will update on next `feat:`/`fix:`/`perf:` merge (which will be F-2, not F-1).
- F-1 docs entry goes in Unreleased as a new subsection — e.g., `### OWASP Coverage Matrix Documentation (F-296)` — with 2–3 bullets describing README hero + new `docs/standards/OWASP_COVERAGE.md`.

### docs/standards/ — pattern for OWASP_COVERAGE.md

- 13 existing standards docs use `UPPER_SNAKE_CASE.md` (e.g., DEFINITION_OF_DONE.md, GIT_WORKFLOW.md, NAMING_GUIDELINES.md).
- Index pattern: docs/standards/README.md contains Document | Purpose table; new file MUST be indexed.
- **`OWASP_COVERAGE.md` is first-of-kind in `docs/standards/`** — no OWASP framework doc exists today.

### release-please-config.json prefix mapping

- `docs:`, `chore:`, `refactor:`, `test:`, `style:` → all `"hidden": true` (no bump). ✓ confirmed.
- `feat:`, `fix:`, `perf:` → visible, cause version bump. ✓ confirmed.
- F-1 PR title `docs(296):` will correctly skip release-please.

---

## 3. Architecture Findings

### ADR-021 byte-deterministic reproducibility model (anchors FR-008)

ADR-021 codifies `SOURCE_DATE_EPOCH=1700000000` (reproducible-builds.org convention) for byte-identical PDF regeneration. Combined with ADR-029 (Coverage Attestation page) and ADR-037 D-11 (Section 9 backfill), the per-baseline Coverage Attestation page in `examples/*/sample-report/security-report.pdf.baseline` is **byte-deterministic**.

**External reader reproduction model**: clone tachi, run `/tachi.security-report` against any example architecture with `SOURCE_DATE_EPOCH=1700000000` set; the resulting Coverage Attestation page bytes match the committed baseline. F-1 narrative-defensibility (FR-008) MUST anchor to this — NOT to narrative outputs which are LLM-variable per Architect M1.

### ADR-037 D-2 combined-slot framing (anchors FR-001a)

ADR-037 closes BLP-01 with OWASP five-framework total **50/50 Covered** (catalog line 13: LLM 10/10 + Agentic 10/10 + ML 10/10 + Mobile 10/10 + Web/API 10/10). Compression from 6 schema buckets to 5 narrative slots happens at D-2 (11-host F-A3 closure). Article §a CANNOT compress; MUST show all 6 buckets × 10 items + separate URLs (`https://owasp.org/Top10/` + `https://owasp.org/API-Security/`).

### ADR-044 dual-frame positioning (anchors hero tone)

Current `README.md` already carries the harness frame (line 3) and a 50/50 line at line 29. F-1 hero refresh layers atop, not replaces. Hero block tone MUST align to ADR-044 wording:
- "Threat Modeling and Vulnerability Detection Harness for Claude Code"
- "AI-Reasoning Scanner — STRIDE + AI + MAESTRO"
- "SAST catches syntax-level bugs; tachi reasons over your architecture description to catch logic-level ones."

### Recent ADRs

Top 5 most recent: ADR-045 (2026-05-14 @armorer-labs F-292), ADR-044 (2026-05-07 positioning), ADR-042 (2026-05; pre-commit secret scanning), ADR-041 (2026-05-09; Claude permissions), ADR-040 (2026-05-05; config parsing hardening). **ADR-043 is reserved for BLP-03 (signed updates)** per project memory but does not yet exist in `02_ADRs/`. No 2026-04/05 ADRs are unreflected in coverage docs.

### Architectural gaps for spec to call out

1. **No `docs/standards/OWASP_COVERAGE.md` exists** — first-of-kind; must be authored at `/aod.plan` Wave 0 per Architect H2 lean (≤80 lines).
2. **`brands/` directory does not exist in tachi** (only `brand/posters/` for the cycle-outcomes infographic) — F-1 hero block authoring has no brand identity layer to follow. README tone is the authoritative voice precedent.
3. **`docs/standards/` lacks a long-form writing style guide** — no doc covers Cybersec article tone. PRD NFR-8 self-review checklist is the operational stand-in.
4. **Per-baseline Coverage Attestation page is per-framework (6 pages), not combined** — article §c must compose the 50/50 combined view manually from per-framework counts; `docs/standards/OWASP_COVERAGE.md` resolves this gap.
5. **`brand/posters/2026-05-08-cycle-outcomes-poster.jpg`** referenced in README line 7 — F-1 hero MUST NOT collide with this asset.

---

## 4. Industry Research (2026 Tactical Patterns)

### README hero — OSS security tool conventions (2026)

Tier-1 scanners (Semgrep, Trivy) do NOT lead with precision percentages. They use **two-dimensional matrix framing** (targets × scanners; use-case tables linking to playground examples) and lead with badges (package managers, CI status, Docker pulls). Coverage tables — when present — link to separate pages rather than embedding the full matrix.

**Tactical for F-1**: 5 framework × Top 10 matrix is novel and credible IF presented as a verification table (anchors to evidence: `schemas/taxonomy/owasp.yaml` + per-baseline Coverage Attestation pages), not as a marketing claim. Lead with what tachi detects that SAST cannot (ADR-044 signature line); place the matrix below the badge cluster; link rows to evidence.

**Cautionary**: Semgrep CE explicitly says "will miss many true positives." Tachi should mirror this transparency — say what `50/50` means (catalogued threat coverage), not what it doesn't (zero false positives, complete app coverage).

### OWASP coverage messaging conventions (2026)

2026 industry consensus (AppSec Santa, Aikido): *"No single tool category covers all OWASP Top 10 risks."* Tools claiming coverage without category-level mapping draw critique. The convention is **per-category mapping with explanation of why the finding falls in that category**. Generic "OWASP alignment" claims are flagged as non-substantive.

**Verified anchor URLs**:
- LLM 2025: `https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/`
- Agentic 2026: `https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/`
- Web 2021: `https://owasp.org/Top10/`
- API 2023: `https://owasp.org/API-Security/`
- Mobile 2024: `https://owasp.org/www-project-mobile-top-10/`
- ML 2023: `https://owasp.org/www-project-machine-learning-security-top-10/`

### Long-form article structure for security devs (2026)

Evidence-first reporting wins. Pattern: Problem → Approach → Reproducibility section (run-this-command-yourself) → Limitations → Future work. Successful 2026 security articles (Semgrep blog, dev.to scanner posts, Microsoft SecOps blog) cite "100% reproducibility across N runs" as the credibility move.

**Tactical for F-3**: structure the ~3000-word article as: (i) Problem framing — why OWASP coverage matters; (ii) The 50/50 claim with per-bucket breakdown; (iii) Verification walkthrough using 2–3 examples; (iv) Limitations and out-of-scope items; (v) Contribution invitation (folds PM L-1 prospective-contributor persona). Use fenced code blocks with output diffs; avoid hero screenshots of dashboards.

### LinkedIn 2026 algorithm shift (CRITICAL)

**Link-in-body reduces reach by ~18.8% (median); link-in-comments now suppressed up to 80%** — LinkedIn detects "bridge behavior" and penalizes posts designed to funnel readers to a comment link.

**2026 winning format**: native-first content that stands alone; deliver the core insight in the post body; mention links naturally in comments only if asked. Knowledge/expertise content prioritized over "viral" content. Hashtags carry minimal weight (topic detection replaced them).

**Tactical for F-2 (LinkedIn post)**: post the 50/50 matrix as native content (carousel/document or in-feed text). Put the article URL in a comment ONLY in response to engagement, not as the primary CTA. First 60–90 min determines reach — schedule for peak audience window. Responding to Daniel Wood's prior thread: quote the specific gap he flagged, show how it was addressed, ship the receipts (PR/commit). Avoid sycophancy — name the gap, name the fix, link to merged work.

### GitHub profile README (2026)

Flagship pattern: pin 4–6 repos, each with strong individual README. Add a VISION section to anchor scope. Low-volume/high-quality maintainers benefit from a "Now" section — but only if maintainable (quarterly cadence). Daily/weekly "Now" sections become stale and signal abandonment.

**Tactical for FR-4 (profile refresh)**: tachi as flagship, AOD-Kit as secondary methodology backing. Per PRD Q7 lean = minimal — flagship project table only, no "Now" section (avoid ongoing maintenance burden).

### Discussion close patterns for OSS

Best pattern: close with three elements — (1) reference what shipped (PR # + release version), (2) attribute the specific gap surfaced, (3) link to the artifact that closes it. Avoid effusive thanks — name the technical contribution.

**Tactical for FR-5 (Discussion #179)**: lead with "Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292" (PRD H-1 + Q3 + R5 explicit framing). Treat as peer-engineer, not customer. Cite PR #293, v4.36.0, ADR-045 line 133.

### Rollback discipline (NFR-3 anchor)

Industry consensus: silent retraction widely considered a credibility failure in 2026 security discourse. Evidence-first reporting (Microsoft, Anchore) — when a claim is challenged, surface the evidence, correct in public if wrong, document the correction in CHANGELOG.

**Tactical for FR-9 / NFR-3**: if a public artifact draws material critique, correction goes on the same surface (LinkedIn update post, article edit-log) — not a quiet deletion. Pre-commit to this discipline in the rollback plan.

---

## 5. Recommendations Synthesized for Spec

1. **Adopt F-272 Principle VII §Exceptions DoD framing**: push/test (post-merge `/security` regression-only) + user-validate (manual UI inspection of public surfaces).
2. **Split in-tree from out-of-tree work** (F-272 D-6 pattern): in-tree (README, CHANGELOG, OWASP_COVERAGE.md) merges first; out-of-tree (LinkedIn, Cybersec article PR, profile PR, Discussion #179 close) fires post-merge inside acceptance window.
3. **Adopt F-292 follow-up-Issue pattern**: if any out-of-tree task cannot complete inside the acceptance window, defer to a follow-up Issue at delivery time rather than block close.
4. **Adopt ADR-045 §Provenance precedent verbatim** for Discussion #179 close-comment attribution.
5. **Skip `feat:` PR title**: PRD mandates `docs(296):`; cadence break acknowledged in NFR-005 + SC-006; no AC verifies release-please opens (it won't, by design — Architect M3 resolution).
6. **Add SC-013 (PM M-2 resolution)**: `feedback_aod_deliver_release_gate.md` memory carve-out documented before F-1 close-out.
7. **Add US-7 (PM M-1 resolution)**: enterprise-buyer persona with BLP-03 signal anchor — converts "manufactures the BLP-03 enterprise-buyer signal" from strategic claim to testable AC.
8. **Add US-8 (PM L-1 resolution)**: prospective-contributor persona — folded into FR-003 §f (Cybersec article contribution invitation closing paragraph).
9. **Add NFR-008 §f**: self-review checklist explicit item "Asset-tag mention NOT present (Q4 + FR-7 enforcement)" (Team-Lead L-2).
10. **Add to FR-007 / NFR-005**: F-2 ship-by-2026-06-11 constraint (Architect M2); if F-2 slips, F-1 close-out comment MUST state the new release-cadence-restoration date.
11. **Anchor FR-008 (narrative-defensibility) to byte-deterministic Coverage Attestation pages** + `docs/standards/OWASP_COVERAGE.md` + `schemas/taxonomy/owasp.yaml` (Architect M1; ADR-021/ADR-029/ADR-037 chain).
12. **Add SC-007 carve-out** (Architect L1): false-positive incidental references to F-2/F-260b/asset-tag in non-substantive contexts (e.g., research notes, prior PR discussion) require human review before being flagged as violations.
13. **README hero insertion point** (Architect L2): between line 14 (divider) and line 17 (`## What is tachi?`). Existing 50/50 mention at line 29 may stay or be deduped at hero-author discretion within the 30-line FR-011 cap.
