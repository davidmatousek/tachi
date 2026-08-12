---
prd_reference: docs/product/02_PRD/362-remap-owasp-llm-top10-2026-2026-08-05.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "All 15 FRs trace 1:1 to PRD; conditions A–E intact; FR-4 coverage-honesty veto satisfied; research count-corrections verified as honest refinements (two scope reductions, no creep). 3 plan-stage warnings to resolve in plan.md: W1 ADR-index prose (docs/architecture/README.md:57-69) vs SC-002 absolute zero; W2 fence cwe_refs posture so 2026 CWE cross-refs cannot pull F-185-scale cwe.yaml growth in-loop unbudgeted; W3 FR-014 residual (~325 refs) evidence bar is file-level. Full review: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Feature Branch**: `362-remap-owasp-llm-top10-2026`
**Created**: 2026-08-06
**Status**: Draft
**Input**: User description: "PRD: 362 - remap-owasp-llm-top10-2026"
**PRD**: [362-remap-owasp-llm-top10-2026-2026-08-05.md](../../docs/product/02_PRD/362-remap-owasp-llm-top10-2026-2026-08-05.md) (v1.2, triple-signed 2026-08-05)
**Research**: [research.md](research.md) (2026-08-06 — all counts below are research-measured at `747805c`; where the PRD and research diverge, this spec adopts the measured value per the research discrepancy table)

OWASP released the Top 10 for LLM Applications 2026 (v1.0, 2026-08-04). The rank order changed (bare codes changed meaning: LLM03 meant Supply Chain in 2025, means Excessive Agency in 2026), one entry was renamed and re-scoped (System Prompt Leakage → Hidden Context Exposure), and four entries absorbed new attack classes. Every tachi LLM-list mapping, emitted finding code, and the coverage claim still targets the superseded 2025 edition. This feature remaps every **contract surface** by category — never by bulk code replacement — governed by the official movement map, with the alias/cutover policy decided first via ADR, coverage re-derived from detection evidence, and the `examples/**` derived-artifact tail split to follow-up F-362b under a declared, time-boxed carve-out.

## Movement Map (remap authority — normative for every mapping decision)

| 2025 code | 2026 code | Category | Handling |
|-----------|-----------|----------|----------|
| LLM01:2025 | LLM01:2026 | Prompt Injection | Rank holds; scope absorbs cross-modal (image/audio) injection |
| LLM02:2025 | LLM02:2026 | Sensitive Information Disclosure | Rank holds |
| LLM06:2025 | LLM03:2026 | Excessive Agency | Up 6 → 3 |
| LLM03:2025 | LLM04:2026 | Supply Chain | Down 3 → 4; scope absorbs model-artifact authenticity |
| LLM04:2025 | LLM05:2026 | Data and Model Poisoning | Down 4 → 5; scope absorbs fine-tuning subversion |
| LLM10:2025 | LLM06:2026 | Unbounded Consumption | Up 10 → 6 |
| LLM09:2025 | LLM07:2026 | Misinformation | Up 9 → 7 |
| LLM07:2025 | LLM08:2026 | System Prompt Leakage → **Hidden Context Exposure** | Renamed + re-scoped (broader hidden-context trust failure) |
| LLM08:2025 | LLM09:2026 | Vector and Embedding Weaknesses | Down 8 → 9 |
| LLM05:2025 | LLM10:2026 | Improper Output Handling | Down 5 → 10; scope spans insecure generated code at scale |

Where a mapping decision is ambiguous, the official crosswalk in the 2026 PDF Appendix A (LLM-to-ASI matrix) is the authority — never an invented mapping. The 2026 release separates the model-as-component (this list) from the model-as-actor (OWASP Agentic Top 10, covered by tachi separately).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Findings cite the current standard (Priority: P1)

**When** I rely on tachi's OWASP-aligned threat modeling as a security engineer, **I want** every LLM Top 10 mapping, emitted finding code, and the coverage page updated to the OWASP Top 10 for LLM Applications 2026, **so I can** trust that tachi findings cite the current standard and the coverage claim stays verifiably true. The harm of stale codes lands hardest on developers without deep security expertise, who cannot self-detect that LLM03 changed meaning; as the upstream machine-readable contract, tachi propagates any error to every downstream consumer.

**Why this priority**: This is the product truth of the feature — a threat harness citing a superseded standard is the analogue of a SAST tool shipping last year's rule pack. Everything else (alias policy, coverage honesty) exists in service of this remap being correct.

**Independent Test**: On the feature branch, run the taxonomy integrity suite, the repo-wide sweep (suffixed forms + `LLM Top 10 2025` prose), and review the two disposition ledgers — deliverable value is a contract surface (catalog, crosswalk, personas, skills, adapters, emitters, schemas, templates, tests) that is 100% 2026-cited with zero unreviewed 2025 references outside the exclusion list.

**Acceptance Scenarios**:

1. **Given** the movement map and the 10 LLM records in `schemas/taxonomy/owasp.yaml` (ids `LLM01..LLM10`, `full_id: OWASP-LLM-2025-NN`), **When** the catalog surgery completes, **Then** each record carries `full_id: OWASP-LLM-2026-NN`, the verbatim 2026 canonical `name`, a live-verified 2026 `url`, and a re-attested `# citation:` comment matching the category now occupying that id slot — with `id`, sort order, and `out_of_scope` untouched and the full taxonomy integrity suite green.
2. **Given** the Hidden Context Exposure rename, **When** any user-facing surface presents the LLM08:2026 category, **Then** it uses the 2026 name with "System Prompt Leakage (2025 name)" retained as an alias or historical note; the catalog `name` field itself carries only the verbatim 2026 name (no alias field exists in the record shape).
3. **Given** the completed remap, **When** a repo-wide scan runs for suffixed forms (`LLM0N:2025`, `LLM Top 10 2025` prose) using tooling that sees gitignored-but-tracked files (`git grep` or `rg --no-ignore`), **Then** zero references remain outside the FR-008 exclusion list (which includes the declared, time-boxed `examples/**` carve-out → F-362b).
4. **Given** the bare-code disposition ledger (FR-014), **When** ledger review completes, **Then** 100% of in-scope bare `LLM01..LLM10` occurrences are dispositioned (re-mapped, confirmed-correct-as-is, or excluded-with-reason) — no bare code survives on its 2025 meaning.

---

### User Story 2 - Downstream consumers survive the code transition (Priority: P2)

**When** my pipeline consumes tachi SARIF/finding metadata pinned to 2025 identifiers, **I want** a deliberate, documented alias/cutover policy, **so I can** migrate on a known contract instead of silently misinterpreting re-meaning'd codes.

**Why this priority**: The alias decision (ADR-048) is sequenced FIRST — it constrains the mechanics of everything in US-1 — but its user value is consumer continuity, which presupposes the remap itself. It is a hard gate, not the headline.

**Independent Test**: ADR-048 exists as Accepted before any remap commit; the `references[]` token grammar it fixes is enforceable by inspection of the named enforcement points plus a covering unit test for `normalize_owasp_id`.

**Acceptance Scenarios**:

1. **Given** the alias/cutover decision space (hard cutover vs dual-emission for one release), **When** remap mechanics begin, **Then** ADR-048 is already Accepted (dual-commit protocol; Proposed → Accepted Day 1 of plan) and records: (a) the exact `references[]` token grammar for 2026 emissions, (b) the chosen policy with industry precedent considered (MITRE ATLAS dual-versioning, Snyk dual-support, Semgrep deprecation markers), and (c) the migration/consumer note content for FR-011.
2. **Given** production `threats.md`/`.sarif` are LLM-authored and the SARIF generator scripts have no production caller, **When** ADR-048 names its enforcement points, **Then** it names the actual ones — the 9 agent personas, the 15 skill reference files, `schemas/finding.yaml`'s two example blocks, and the sarif-specification skill templates — and requires `generate-threats-sarif.py::normalize_owasp_id` plus a net-new covering test to move in lockstep with the grammar (current regex `^OWASP\s+LLM(\d+):\d+$` silently falls through to raw passthrough; zero test coverage today).
3. **Given** the catalog and crosswalk schemas are shape-frozen (crosswalk edges hard-reject extra keys; any new catalog field requires ADR-027 Extension History churn), **When** ADR-048 selects the aliasing mechanism, **Then** aliasing lives at the token-grammar layer (references[] strings and prose annotations), not as schema shape changes — unless ADR-048 explicitly accepts the documented schema-churn cost with a D-numbered decision.
4. **Given** the cutover ships, **When** a consumer reads the changelog, **Then** it documents the code re-meaning (movement map), the alias policy, and the F-362b examples carve-out including the mid-window risk that example CA pages attribute findings under 2025 meanings until F-362b lands.

---

### User Story 3 - The coverage claim stays honest (Priority: P3)

**When** I evaluate tachi's 50/50 OWASP coverage claim against the 2026 edition, **I want** per-category coverage re-derived from detection evidence against 2026 definitions, **so I can** trust the published number is earned, not carried forward.

**Why this priority**: Claim integrity is a product-trust requirement, but it consumes the outputs of US-1 (remapped categories) and the gap analysis — it cannot precede them.

**Independent Test**: `docs/standards/OWASP_COVERAGE.md` shows per-category 2026 verdicts each citing detection evidence; every headline restatement in the repo carries the re-derived number; shipping an unchanged "50/50" without re-derivation evidence is a PM veto at spec review (already exercised as a binding PRD condition).

**Acceptance Scenarios**:

1. **Given** the four scope absorptions (cross-modal injection → LLM01, model-artifact authenticity → LLM04, fine-tuning subversion → LLM05, insecure generated code at scale → LLM10), **When** the gap analysis completes, **Then** each absorbed sub-class is either covered by an existing detection with cited evidence (agent + pattern category) or its category verdict drops to **Partial** and a follow-up issue is filed. New detections are out of scope.
2. **Given** `docs/standards/OWASP_COVERAGE.md` is hand-authored canon with no generator, **When** it is updated to 2026, **Then** correctness is gated by review against `schemas/taxonomy/owasp.yaml` and the re-derived verdicts, and it gains an editorial note that the cited detection ADRs (030/031/034/045) are immutable records asserting 2025 codes whose lineage re-keys (ADR-030/045 → LLM10:2026; ADR-031 → LLM07:2026; ADR-034 → LLM06:2026). [MANUAL-ONLY: hand-authored document, human review gate is the correctness mechanism]
3. **Given** the re-derived verdicts, **When** any coverage count changes, **Then** the number is updated at every restatement surface — README sites L7/L19/L24/L48/L390, `.claude/rules/scope.md:21,24`, `docs/guides/DEVELOPER_GUIDE_TACHI.md:1805`, `docs/architecture/01_system_design/README.md:130`, `docs/standards/OWASP_COVERAGE.md` — and a Partial downgrade that edits `.claude/rules/scope.md` is treated as a triad-visible governance change.

---

### Edge Cases

- **2026 per-entry URLs don't exist at authoring time** (research: 2026 entry pages not yet web-indexed; only the release resource page is live): citation re-anchoring MUST live-verify the actual 2026 URL scheme first. If per-entry pages are absent, anchor to the official release resource page (`https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/`) as the interim citation, record the substitution in the crosswalk disposition ledger, and expect the deliver-stage live link-rot dispatch to confirm reachability. Never author URLs from an assumed slug pattern.
- **Crosswalk permutation collision**: the 8-id re-key (LLM03→04→05→10→06; LLM06→03; LLM09→07; LLM07→08; LLM08→09) is a bijection but sequential in-file renames collide on the dedupe key `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` mid-flight — the mechanical pass MUST be a single simultaneous permutation, verified by the integrity suite (0 duplicates, primary floor ≥ 500 unaffected).
- **Sweep tooling blindness**: `examples/*/test-output/` is `.gitignore`d yet 36 files remain tracked (2 with LLM refs) — default `rg`/`grep` silently skips them. All sweep and verification commands use `git grep` or `rg --no-ignore`.
- **Inherited red baseline**: the byte-identity suite is in no CI and ~19 out-of-gate test failures pre-exist. The pre-state task records literal pytest totals (byte-identity suite + gated 15-module subset) before any edit, so any red→green or green→red flip is attributable to this feature.
- **ADR-048 lands dual-emission** (ceiling case): grammar and test scope grow (alias token, possibly per-surface dual citations), but catalog/crosswalk shapes stay frozen (grammar-layer aliasing); the team-lead ceiling (10.0 attention-days) already prices this branch.
- **2026 publication defines CWE cross-refs for LLM entries**: `cwe_refs` is populated only where OWASP explicitly publishes them (2025 did not → `[]` today); if populated, crosswalk CWE-edge resolution requirements apply (F-185 precedent: `cwe.yaml` grown for exactly this reason).
- **A Partial downgrade cascades**: the headline may drop below 50/50 across up to 11 restatement surfaces including a CLAUDE.md-loaded governing rule (`.claude/rules/scope.md`) — this is planned-for, published honestly, and never suppressed to preserve the headline.
- **Protected-file near-miss**: a sweep hit inside the FR-008 exclusion set (952 suffixed refs / 114 files; 2,118 any-form refs / 190 files) is left byte-untouched — immutable delivery records, PRDs, accepted ADRs, and historical run records are never rewritten; `tests/fixtures/init-baseline-tree/**` changes only via its regeneration script, same-commit with its source docs.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.
> **Traceability**: FR-0NN ↔ PRD FR-N mapping is 1:1 as annotated; research-corrected counts are normative.

- **FR-001** (PRD FR-1): The system MUST remap all LLM-list mappings by **category** per the movement map — no bulk code find/replace. Catalog surgery = the 10 LLM records inside six-list `schemas/taxonomy/owasp.yaml` (`full_id` edition flip, verbatim 2026 `name`, live-verified 2026 `url`, `# citation:` re-attestation against the category now occupying each id slot; `id`/sort/`out_of_scope` untouched; `cwe_refs` per the 2026 publication's explicit cross-refs or `[]`).
  - AC: **Given** the catalog surgery is complete, **When** `tests/schemas/test_taxonomy_integrity.py` runs, **Then** all functions pass with 60 records, 10 LLM ids unchanged, and lexicographic sort holding by construction.
  - AC: **Given** the 10 edited records, **When** each `# citation:` comment is reviewed, **Then** it attests ≥1 detection-tier host agent + ≥1 pattern category for the **2026** category in that slot (e.g., the LLM03 record now cites tool-abuse/agent-autonomy for Excessive Agency, not data-poisoning). [MANUAL-ONLY: no test reads comments; review-only audit surface]

- **FR-002** (PRD FR-2): Every user-facing surface presenting the renamed category MUST use "Hidden Context Exposure" with the 2025 name retained as an alias or historical note.
  - AC: **Given** the remap is complete, **When** user-facing surfaces (personas, skill references, coverage page, README, adapters) present LLM08:2026, **Then** the 2026 name appears with "System Prompt Leakage (2025 name)" as alias/historical note at first mention per surface.

- **FR-003** (PRD FR-3): A gap analysis MUST evaluate the four scope absorptions against current detection patterns; each gap is covered in-loop by cited existing evidence or filed as a follow-up issue. New detections are out of scope.
  - AC: **Given** the four absorbed sub-classes, **When** the gap analysis completes, **Then** a per-sub-class disposition exists (evidence citation: agent + pattern category, or follow-up issue number) checked in under `specs/362-remap-owasp-llm-top10-2026/`.

- **FR-004** (PRD FR-4): Per-category coverage MUST be re-derived from detection evidence against 2026 definitions — never carried forward. Categories with undetected absorbed sub-classes drop to **Partial**; `docs/standards/OWASP_COVERAGE.md` and every headline restatement report the re-derived number. **Authority rule**: the evidence-based verdict in `OWASP_COVERAGE.md` is authoritative for the coverage *claim*; the CA-PDF page's `relationship`-derived classification is a per-run report of finding attribution, not the claim. Whether example findings' `relationship` values change under 2026 definitions is an architect ruling at plan (feeds F-362b).
  - AC: **Given** the re-derivation, **When** `OWASP_COVERAGE.md` is reviewed, **Then** each of the 10 LLM rows carries a 2026-definition verdict with cited detection evidence, and any Partial verdict has a filed follow-up issue. [MANUAL-ONLY: evidence review against agent pattern catalogs is human judgment]
  - AC: **Given** a changed coverage count, **When** the restatement sweep runs, **Then** all surfaces listed in US-3 AC-3 carry the same re-derived number (zero stale headlines).

- **FR-005** (PRD FR-5): The crosswalk (`schemas/taxonomy/crosswalk.yaml`, 645 edges) MUST be remapped in two parts: (a) **mechanical** — the 57 re-keying edges' `source.id` permuted in a single simultaneous bijection pass (0 duplicate dedupe keys at every point; primary floor ≥ 500 unaffected; no ordering invariant); (b) **human disposition, mandatory for all 74 LLM-keyed edges** — re-validate `target`, `citation`, `confidence` against the **2026** category definitions (most acute: LLM08:2026 Hidden Context Exposure broader than System Prompt Leakage; LLM01 cross-modal), honoring the anti-drift confidence rule (downgrade when no one-sentence citation supports high/medium), including re-anchoring the 54 year-slugged citation URLs per the Edge Case rule on 2026 URL verification. The disposition ledger lives as a checked-in artifact under `specs/362-*/` (edge shape rejects extra keys — no inline annotations).
  - AC: **Given** the mechanical pass, **When** the taxonomy integrity suite runs, **Then** `test_crosswalk_loads` and `test_crosswalk_referential_integrity` pass with 645 edges, 74 LLM-keyed, 0 duplicates.
  - AC: **Given** the disposition ledger, **When** reviewed, **Then** it shows 74/74 edges dispositioned, 57/57 re-keyed, 54/54 citation URLs re-anchored (or ledger-recorded interim substitution per the URL edge case). [MANUAL-ONLY: per-edge semantic re-validation against 2026 definitions is curator judgment; no test detects a wrong-meaning edge]

- **FR-006** (PRD FR-6): The alias/cutover decision MUST be made **first**, recorded as **ADR-048** (next free number; never reclaim 004/043) in ADR-047 format with architect input, Accepted before remap mechanics begin (dual-commit protocol). ADR-048 MUST: (a) fix the exact `references[]` token grammar; (b) require `normalize_owasp_id` + a net-new covering test to move in lockstep (current: silent raw-passthrough branch, zero coverage); (c) name the real enforcement points — the 9 personas, 15 skill reference files, `schemas/finding.yaml` example blocks, and sarif-specification templates — since the SARIF generators have no production caller; (d) keep aliasing at the token-grammar layer unless schema churn is explicitly decided.
  - AC: **Given** the plan stage, **When** the first remap-mechanics commit lands, **Then** ADR-048 already exists with Status: Accepted and the four mandatory contents present.

- **FR-007** (PRD FR-7): Drift-guard blindness and baseline integrity MUST be handled as: (a) this feature runs `tests/scripts/test_backward_compatibility.py` green pre-merge as the **no-churn proof** (catalog rename alone leaves the 6 CA-PDF baselines byte-identical — render consumes id+classification only), with the #329 guard's green explicitly treated as **uninformative** for this change class; (b) the **unconditional CA-baseline regen + fingerprint-sidecar re-emit** (`scripts/regenerate-ca-baselines.sh`, local-only, typst+PyYAML) is causally bound to **whichever loop re-keys example findings' `source_attribution`** — F-362b under the adopted split — never to a feature number by convenience; (c) `_canonical()` widening is filed as a follow-up issue "decided: defer, with rationale" (widening = co-change coincidence, not causal coupling; also records the pre-existing false docstring claim).
  - AC: **Given** all F-362 commits, **When** `test_backward_compatibility.py` runs against committed HEAD pre-merge, **Then** it is green with zero baseline bytes changed. [MANUAL-ONLY: suite is wired into no CI; must be run and evidenced in-loop]
  - AC: **Given** the pre-state task, **When** the first edit lands, **Then** literal pytest totals (byte-identity suite + gated 15-module subset, including the ~19 known out-of-gate failures) are recorded in a checked-in pre-state artifact.

- **FR-008** (PRD FR-8): The repo-wide sweep MUST honor the exclusion list as a hard boundary: `specs/**`, `docs/product/02_PRD/**`, released `CHANGELOG.md` entries, `docs/guides/CONSUMER_GUIDE_TACHI.md`, accepted ADRs (`docs/architecture/02_ADRs/ADR-0*`), `examples/*/test-output/**` (historical run records), `docs/INSTITUTIONAL_KNOWLEDGE.md`, `tests/fixtures/init-baseline-tree/**` (regenerated via `tests/fixtures/regenerate-baseline.sh` in the **same commit** as its source docs — never hand-swept), **plus the declared time-boxed carve-out**: `examples/**` (excl. test-output) → F-362b, blocking before the next minor release. Measured protected set: 952 suffixed refs / 114 files (2,118 any-form / 190 files). Sweep tooling MUST see gitignored-but-tracked files.
  - AC: **Given** the completed sweep, **When** `git grep` scans for suffixed 2025 forms outside the exclusion list, **Then** the count is 0.
  - AC: **Given** the exclusion boundary, **When** the feature branch diff is reviewed, **Then** zero protected files are modified (except `init-baseline-tree` via its script, same-commit with source).

- **FR-009** (PRD FR-9a): `docs/standards/OWASP_COVERAGE.md` MUST be hand-updated to 2026 (matrix row, headline, anchor URL, ADR-lineage note per US-3 AC-2) — no generator exists and none is built (code-economy rung 1). An **optional cheap consistency test** (doc LLM row ↔ catalog `full_id` edition) is a plan-stage scope decision; research recommends building it.
  - AC: **Given** the hand-update, **When** reviewed against `schemas/taxonomy/owasp.yaml` and the FR-004 verdicts, **Then** row, headline, anchor URL, and editorial note are consistent with the catalog and the re-derived coverage. [MANUAL-ONLY: hand-authored canon; review gate is the mechanism]

- **FR-010** (PRD FR-9b): Byte-determinism MUST be verified where it exists — the 6 CA-PDF baselines via the `SOURCE_DATE_EPOCH=1700000000` recipe, `scripts/regenerate-ca-baselines.sh` (sidecar re-emitted as final step), and green `test_backward_compatibility.py`. This is a local, human-in-the-loop gate and is budgeted as such. [MANUAL-ONLY: local-only tooling (typst) outside CI]
  - AC: **Given** F-362 proper (no example re-keying), **When** the recipe runs pre-merge, **Then** the suite is green with no regen required (no-churn proof); the unconditional regen travels with F-362b per FR-007(b).

- **FR-011** (PRD FR-10): The changelog MUST describe the remap, any behavior change in emitted codes (per ADR-048), the movement map or a pointer to it, and a consumer-facing note on the F-362b examples carve-out **including the mid-window risk** that example CA pages attribute findings under 2025 meanings until F-362b lands.
  - AC: **Given** the delivery, **When** the changelog entry is read, **Then** it contains the remap summary, the alias policy, the migration note, and the carve-out disclosure.

- **FR-012** (PRD FR-11): Emitters and parsers MUST be fixed structurally: (a) `scripts/generate-risk-scores-sarif.py` — replace the hardcoded taxa at **both** sites (`TAXONOMIES` :453 and `supported_taxonomies()` :495 — currently 2023 names under `version: "2025"`) and `_OWASP_REFERENCE_BY_PREFIX` (:234 — becomes OI → LLM10:2026, MI → LLM07:2026 under the movement map) with taxa **derived from `schemas/taxonomy/owasp.yaml` via the existing loader**, making next-edition recurrence structurally impossible; fix the retired `informationUri` (both sites) to the 2026 anchor; also update the 2023-era rule prose in `generate-threats-sarif.py` (:66, :259–260, :271). (b) Add an unmatched-`source_attribution`-ref stderr warning to `extract-report-data.py::classify_framework_items` (byte-neutral; prevents a silent all-gap CA page on form drift). (c) Fix the pre-existing year-suffixed `id:` form bug (catalog contract requires bare ids) at all 8 persona sites (prompt-injection :65/:93/:120, data-poisoning :77/:105, model-theft :75/:127, denial-of-service :134) + the 2 web-api-coverage fixtures in the same pass — do not port a broken shape to 2026.
  - AC: **Given** the FR-012(a) fix, **When** the risk-scores SARIF generator emits taxonomies, **Then** zero hardcoded LLM category names remain in the script (all derived from the catalog) and a covering test asserts the derived taxa match the catalog.
  - AC: **Given** the FR-012(b) warning, **When** a finding carries a `source_attribution` ref that matches no catalog record, **Then** a warning is emitted to stderr and the CA-page bytes are unchanged for well-formed inputs.
  - AC: **Given** the FR-012(c) fix, **When** `git grep -E 'id: "?LLM[0-9]{2}:20' .claude/ tests/` runs, **Then** it returns 0 hits.

- **FR-013** (PRD FR-12): Consumer-facing distribution mirrors MUST be remapped: `adapters/**` (17 files across claude-code/copilot/cursor/generic — the github-actions adapter carries 0 LLM refs) and legacy top-level `agents/**` (**4 files**: `agents/ai/{data-poisoning,model-theft,prompt-injection}.md`, `agents/orchestrator.md` — research-corrected from ~9) = **21 files / 149 refs**, all in `OWASP LLM0N:2025` form (0 bare). Sequenced after `.claude/` agents/skills, before the sweep, with an explicit 4-format checklist task. No parity test exists; the FR-008 sweep is the only net.
  - AC: **Given** the mirror remap, **When** the FR-008 sweep runs over `adapters/**` and `agents/**`, **Then** 0 suffixed-2025 references remain and each of the 4 adapter formats has a checked checklist entry.

- **FR-014** (PRD FR-13): A **bare-code disposition ledger** MUST cover the measured FR-13 surfaces — 45 files / 346 total refs (9 personas: 84; 15 skill refs: 113; adapters: 118; legacy agents: 31) — of which the hand-review concentration is **41 bare occurrences across 8 files** (5 personas + 3 skill reference files; adapters and legacy agents carry 0 bare codes and are fully sweep-visible). Every bare code is dispositioned so none survives on its 2025 meaning; the in-scope bare census is 366 (469 including the `examples/**` carve-out, whose disposition transfers to F-362b). The ledger is a checked-in `specs/362-*/` artifact mirroring the FR-005 crosswalk ledger.
  - AC: **Given** the ledger, **When** reviewed, **Then** 100% of the 41 concentrated bare occurrences carry an explicit disposition and the remaining in-scope bare census is accounted for by file-level entries (dispositioned or exclusion-listed). [MANUAL-ONLY: bare codes are invisible to a suffix-keyed sweep; semantic review is the only detector]

- **FR-015** (PRD FR-14): Tests, fixtures, templates, and schemas MUST be updated: the **8** test files carrying 2025 assertions (`test_llm10_unbounded_consumption_enrichment.py` 35 refs, `test_coverage_attestation.py` 16 — 4 sibling files carry 0, `test_catalog_drift_guard.py`, `test_output_integrity.py`, `test_source_attribution.py`, `test_tool_abuse_enrichment.py`, `generate_pagination_fixture.py`, + `test_backward_compatibility.py:19` module docstring — research-found 8th); the **19** fixture files (13 suffixed / 6 bare-only); `templates/tachi/output-schemas/threats.md:365` golden row; `schemas/finding.yaml` both example blocks (`:109` references[] example, `:330–332` source_attribution examples — note the LLM05 example itself re-keys to LLM10). Any test file add/rename updates `tachi-pytest.yml` `paths:` + pytest invocation atomically, same commit. The `coverage-attestation.typ:48` page-title mislabel (path: `templates/tachi/security-report/`) moves to **F-362b** — an in-loop fix would move PDF bytes and falsify the FR-007(a) no-churn proof.
  - AC: **Given** the test/fixture updates, **When** the gated 15-module pytest subset runs on committed HEAD, **Then** it is green with totals reconciled against the FR-007 pre-state artifact.
  - AC: **Given** FR-015 completes, **When** the FR-008 sweep runs over `tests/`, `templates/`, `schemas/`, **Then** 0 suffixed-2025 references remain outside fixtures explicitly exercising legacy-form handling (each such fixture ledger-dispositioned).

### Key Entities

- **Taxonomy catalog record**: one of 10 LLM entries in `schemas/taxonomy/owasp.yaml` — `id` (bare, stable), `full_id` (the ONE edition-carrying field), `name` (verbatim canonical), `url`, `cwe_refs`, `out_of_scope`, plus a review-only `# citation:` audit comment.
- **Crosswalk edge**: `{source, target, edge_type, confidence, citation}` — shape-frozen (extra keys rejected); LLM-keyed population: 74 (66 primary / 8 related).
- **Movement map**: the normative 2025→2026 category permutation (this spec, §Movement Map) — the remap authority for every mapping decision.
- **Disposition ledgers** (2): the 74-edge crosswalk ledger and the bare-code ledger (45-file surface, 41-occurrence hand-review core) — checked-in `specs/362-*/` artifacts authored before edits begin (Foundational).
- **ADR-048**: the alias/cutover decision record — token grammar, policy, enforcement points, lockstep test requirement.
- **Coverage matrix**: `docs/standards/OWASP_COVERAGE.md` — hand-authored canonical claim surface; its verdicts are authoritative over per-run CA-page classifications.
- **Exclusion list**: the FR-008 protected set (952 suffixed refs / 114 files) + the declared time-boxed `examples/**` carve-out (F-362b).
- **CA-PDF baselines + fingerprint sidecar**: the 6 byte-deterministic PDFs and `examples/ca-baseline-fingerprints.json` — untouched by F-362 proper (no-churn proof); regen travels with F-362b.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Taxonomy currency)**: 100% of contract-surface LLM codes (catalog, crosswalk, personas, skills, adapters, legacy mirrors, schemas, templates, emitters, tests) cite the 2026 edition; baseline 0%. `examples/**` reaches 100% at F-362b (declared carve-out).
- **SC-002 (Sweep completeness)**: 0 suffixed 2025 references outside the FR-008 exclusion list, measured with tooling that sees gitignored-but-tracked files; baseline: 498 suffixed refs / 77 in-scope files (867 any-form / 91 files).
- **SC-003 (Disposition completeness)**: 74/74 crosswalk edges dispositioned; 57/57 re-keyed; 54/54 citation URLs re-anchored or ledger-recorded per the URL edge case; 41/41 concentrated bare-code occurrences dispositioned; 366 in-scope bare census fully accounted.
- **SC-004 (Structural fix)**: 0 hardcoded LLM category names remain in `generate-risk-scores-sarif.py` (both former hardcoded sites derive from the catalog); `normalize_owasp_id` has ≥1 covering test exercising the grammar and the passthrough branch.
- **SC-005 (Claim honesty)**: every `OWASP_COVERAGE.md` LLM verdict carries 2026-definition detection evidence; any Partial downgrade is published across all restatement surfaces (README ×5, scope.md, developer guide, system-design README), not suppressed.
- **SC-006 (Baseline integrity)**: `test_backward_compatibility.py` green pre-merge with zero baseline bytes changed (no-churn proof); pre-state artifact records literal totals; regen gate travels to F-362b.
- **SC-007 (Governance sequencing)**: ADR-048 Accepted before the first remap-mechanics commit; F-362b filed at deliver as a blocking-before-next-minor follow-up issue naming the mid-window wrong-attribution risk.
- **SC-008 (Consumer continuity)**: changelog migration note published; live link-rot dispatch at deliver returns no unaccounted new rot attributable to the re-anchoring (any new rot is filed, not absorbed).

## Scope

**In (P0)**: ADR-048 (first, hard gate) → catalog 10-record surgery → crosswalk 74-edge disposition (57 re-keys, single-pass bijection) → 9 personas + 15 skill reference files → adapters + legacy agents (21 files) → emitters/parsers (FR-012, three-site structural fix + warning + form bug) → tests/fixtures/templates/schemas (FR-015, 8 test files + 19 fixtures) → gap analysis + coverage re-derivation (FR-003/FR-004) → headline restatements (README ×5, scope.md, developer guide, architecture docs) → exclusion-listed sweep + bare-code ledger → `OWASP_COVERAGE.md` hand-update → changelog.

**Out**:
- **`examples/**` derived-artifact refresh → F-362b** (blocking before next minor; carries the unconditional CA-baseline regen + sidecar re-emit, the 4 non-gated sample-report baselines, and the `coverage-attestation.typ:48` page-title fix; declared FR-008 carve-out until it lands).
- New detections for FR-003 gaps (each its own follow-up issue).
- The other five OWASP lists (Web, Agentic, API, Mobile, ML) — unaffected by this release; the threats-SARIF `run.taxonomies[]` block (OWASP-2021/CWE) explicitly out of scope and index-stable.
- `_canonical()` widening (follow-up issue, "decided: defer, with rationale", incl. the false-docstring defect).
- Roadmap/OKR governance gap (separate item).

## Dependencies & Assumptions

- **Dependency**: OWASP Top 10 for LLM Applications 2026 v1.0 PDF (CC BY-SA 4.0) — movement-map source (validated at define); Appendix A is the mapping-ambiguity authority; 2026 per-entry URL scheme requires live verification at build (research: not yet web-indexed).
- **Dependency**: ADR-048 acceptance (Day 1 of plan) gates all remap mechanics.
- **Assumption**: the movement map in this spec is final per the 2026 v1.0 release; a v1.0.x errata changing category order would reopen FR-001/FR-005 dispositions.
- **Assumption**: LLM01/LLM02 edges (17 of 74) need disposition review but no re-keying (rank holds).
- **Assumption**: F-362 proper moves zero CA-PDF baseline bytes (verified by both reviewers: render consumes id+classification only; crosswalk is not consumed by the report pipeline). If any in-loop change is discovered to move baseline bytes, FR-007(b)'s causal binding pulls the regen + sidecar re-emit into that loop — with the architect ruling recorded before build.
- **Assumption**: open tracker #332 (41 pre-existing link-rot findings) churns expectedly when the monitored URL set changes; new-rot attribution at deliver distinguishes F-362-introduced URLs from pre-existing rot.

## Plan-Stage Decision Register (inputs to `/aod.project-plan` — not clarifications)

1. **ADR-048 policy choice**: hard cutover vs dual-emission + exact token grammar (architect + PM; Day 1 hard gate; industry precedents in research.md).
2. **FR-009 optional consistency test**: build or skip (architect + PM; research recommends build — one pytest, doc LLM row ↔ catalog `full_id` edition).
3. **FR-004 relationship-values ruling**: do example findings' `relationship` values change under 2026 definitions (architect; feeds F-362b scope).
4. **ICE effort re-score**: PM recommended E:4; team-lead measurement supports E:5 — formalize via `/aod.score #362` (non-blocking).
