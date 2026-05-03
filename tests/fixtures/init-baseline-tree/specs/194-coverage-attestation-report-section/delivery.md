# Delivery Document: Feature 194 — F-B Coverage Attestation Report Section

**Delivery Date**: 2026-04-18
**Branch**: `194-coverage-attestation-report-section` (deleted post-merge)
**PR**: #195 (squash-merged as commit `c4b8dc68f36b59ee7ab49cc587661526ffd1a818`)
**Post-delivery simplify PR**: #197 (squash-merged as commit `8a2a2e3b34daa9b7b06fa7e42540dda94c08f97a`)
**T044 post-merge SHA fill**: direct commit to main `7ac3939`
**Release**: release-please PR #196 auto-opened for v4.18.0 (pending manual merge)

---

## What Was Delivered

- **New conditional Section 10 in PDF security report** (`templates/tachi/security-report/coverage-attestation.typ`, 403 lines) — per-framework coverage matrix pages (5 pages: OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE) with Covered/Partial/Gap badges (WCAG AA dual-encoded ✓/◐/✗ + color) plus per-finding attribution table with 7 columns (Finding ID / Title / Severity / OWASP refs / MITRE refs / NIST refs / CWE refs). MITRE ATT&CK and MITRE ATLAS render as 2 separate framework pages per Q3-C but merge into a single column on the per-finding table with `ATT&CK:` / `ATLAS:` per-ref prefixes per architect L-2. Section gated on `has-source-attribution and per-finding-rows.len() > 0` belt-and-suspenders check per Feature 141 precedent.
- **7 new aggregator functions in `scripts/extract-report-data.py`** (~291 lines): `compute_has_source_attribution` (gate predicate), `_load_framework_yaml_records` (lazy-yaml-import catalog loader), `load_framework_yaml_record_counts` (Q2-A denominator authority), `classify_framework_items` (Q1-A 3-value classification rule), `_build_per_framework_aggregate` (partition invariant + N/A on zero denominator), `build_per_framework_aggregates` (always-5 framework order), `build_per_finding_rows` (MITRE split/merge rule).
- **`main.typ` integration**: new `#import "coverage-attestation.typ"` block, §2b default-value guards using `dictionary(report-data-module).at("name", default: ...)` idiom (T012 guard-pattern selection recorded in ADR-029 Revision History as a Typst-specific implementation detail — required because `#import ... : *` does not bind absent names), and conditional inclusion block placed after findings-detail and before Page 7 control coverage (architect M-1 insertion point).
- **New ADR-029** (`docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`, Status: **Accepted** 2026-04-18) — records 7 numbered decisions: (1) Typst template + aggregator + `has-source-attribution` boolean pattern mirroring Feature 141 + Feature 128, (2) Q1-A 3-value Covered/Partial/Gap classification, (3) Q2-A catalog-length denominator authority restricted to 5 external frameworks, (4) FR-017 zero-crosswalk-JOIN scope boundary (F-C deferred), (5) Q6-D Out-of-Scope deferral collapsing non-cited items into Gap in MVP, (6) SC-009 22-file zero-edit invariant preservation per ADR-023 / ADR-028 lineage, (7) R9/MED-3 Partial disclosure rule requiring equal visual weight on all 3 counts in per-framework headlines.
- **Third consecutive dual-commit Proposed → Accepted ADR governance use** (after ADR-027 / F-A1 and ADR-028 / F-A2): Proposed authored at Day 1 Wave 1.0 decision-lock commit `b71ee24` (unblocks parallel Wave 2.0 authoring), transitioned Accepted at Day 4 Wave 4.2 T043 commit `129456d` with `<pending-post-merge-fill>` SHA placeholder, post-merge T044 SHA fill committed directly to main as provenance-only change `7ac3939`. Pattern is now the confirmed default protocol for foundation-tier features per KB-036.
- **21 new pytest tests** (16 aggregator + 5 pagination smoke) in `tests/scripts/test_coverage_attestation.py` (673 lines) and `tests/scripts/test_coverage_attestation_pagination.py` (482 lines); 4 fixture YAMLs under `tests/scripts/fixtures/coverage_attestation/` + 1 synthetic 100-finding × 5-framework pagination smoke fixture; synthetic fixture generator at `tests/scripts/generate_pagination_fixture.py` (255 lines).
- **Zero runtime dep changes**: empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. `pyyaml` remains dev-only per Feature 128 precedent — a post-merge mid-PR fix commit `6136e6b` deferred `import yaml` inside `_load_framework_yaml_records` to preserve the stdlib-only module-load invariant and unblock the Feature 130 mmdc preflight CI gate.
- **22-file zero-edit invariant preserved** (ADR-023 lineage extended): empty diff on the 11 threat-detection agents + 11 skill-reference detection-patterns files. Populator wiring remains carved out to F-A3.
- **SC-002 byte-identity preserved**: 5 non-agentic baseline PDFs byte-identical under `SOURCE_DATE_EPOCH=1700000000` (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). Section 10 omitted entirely on all baselines because `has-source-attribution` evaluates `false`. Final pytest: 305 passed, 1 skipped (pre-existing mermaid-agentic-app SC-003 narrowing, unrelated).
- **Post-delivery simplify pass** (PR #197): pruned 7 comment/docstring locations of rotting task/wave/FR references per CLAUDE.md guidance (-14 net lines); added docstring cross-reference from `_load_framework_yaml_records` to sibling stdlib-only `tachi_parsers._load_catalog_ids`. Kept substantive WHY comments (Covered/Partial/Gap rule, MITRE merge rule, partition invariant, fail-loud/lazy-import rationale, empty-arrays `.len() > 0` invariant). Two efficiency findings (duplicate YAML reads in `build_per_framework_aggregates`, O(R·F·A) loop in `classify_framework_items`) deliberately deferred — hot path unexercised today because F-A3 populator wiring hasn't shipped.

---

## How to See & Test

1. **Verify ADR-029 Accepted with SHA filled** (T044 post-merge fill):
   ```bash
   grep -E "^\*\*(Status|Accepted-commit-SHA)" docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md
   ```
   Expect `Status: Accepted` + `Accepted-commit-SHA: c4b8dc68f36b59ee7ab49cc587661526ffd1a818`.

2. **Verify gate predicate on non-attributed baseline** (US-3 AS-1 / SC-002):
   ```bash
   SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_coverage_attestation.py::test_has_source_attribution_false_on_empty_fixture -v
   ```
   Expect `has_source_attribution == False`; Section 10 is omitted entirely from the rendered PDF.

3. **Verify 3-value classification on populated fixture** (US-2 AS-1 / Q1-A rule):
   ```bash
   pytest tests/scripts/test_coverage_attestation.py::test_classify_framework_items_three_value_rule -v
   ```
   Expect Covered (≥1 primary citation) / Partial (zero primary + ≥1 related/derived) / Gap (zero citations) partition.

4. **Verify per-framework aggregate partition invariant** (US-2 AS-2):
   ```bash
   pytest tests/scripts/test_coverage_attestation.py::test_partition_invariant_holds -v
   ```
   Expect `covered_count + partial_count + gap_count == yaml_record_count` for every aggregate.

5. **Verify zero-denominator N/A edge case** (US-2 AS-3 / FR-011):
   ```bash
   pytest tests/scripts/test_coverage_attestation.py::test_zero_denominator_yields_n_a -v
   ```
   Expect `coverage_percentage == "N/A"` when the framework YAML is empty (monkeypatch-injected fixture).

6. **Verify MITRE split/merge rule** (US-1 AS-1 / architect L-2):
   ```bash
   pytest tests/scripts/test_coverage_attestation.py::test_mitre_prefix_merge_in_per_finding_column -v
   ```
   Expect `ATT&CK:T1070.001` and `ATLAS:AML.T0051` to render in the same `mitre_refs` column on the per-finding table with per-ref prefixes preserving the taxonomy-of-origin distinction.

7. **Verify fail-loud on malformed YAML** (ADR-022 fail-loud / FR-011(c)):
   ```bash
   pytest tests/scripts/test_coverage_attestation.py::test_aggregator_fails_loud_on_malformed_yaml -v
   ```
   Expect `yaml.YAMLError` (or wrapping `RuntimeError`) to propagate with a message naming the offending framework. Note: this test patches `yaml.safe_load` directly on the shared `yaml` module rather than `extract_report_data.yaml` — the attribute no longer exists at module scope because `import yaml` is lazy inside `_load_framework_yaml_records` (captured as KB-037).

8. **Confirm backward-compatibility byte-identity** (US-3 AS-2 / SC-002):
   ```bash
   SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
   ```
   Expect 13 passed, 1 skipped (mermaid-agentic-app pre-existing SC-003 skip, unrelated to F-B).

9. **Verify pagination on 100-finding synthetic fixture** (US-1 AS-4 / pagination smoke):
   ```bash
   pytest tests/scripts/test_coverage_attestation_pagination.py -v
   ```
   Expect all 5 smoke tests green against the 100-finding × 5-framework synthetic fixture.

10. **Verify mmdc preflight gate still fires in fresh install** (Feature 130 cross-feature invariant preserved):
    ```bash
    pytest tests/scripts/test_mmdc_preflight.py -v
    ```
    Expect all 9 preflight + mid-render aggregator tests green. The Feature 128 stdlib-only module-load invariant is preserved by the `import yaml` defer in `_load_framework_yaml_records`.

11. **Run the full pytest suite**:
    ```bash
    SOURCE_DATE_EPOCH=1700000000 pytest tests/ --timeout=300
    ```
    Expect 305 passed, 1 skipped.

12. **Inspect a rendered coverage-attestation section** (end-to-end visual):
    Author a fixture `threats.md` with at least one finding carrying populated `source_attribution`, run `/tachi.security-report` against its example directory, and open the resulting `security-report.pdf`. Expect Section 10 to render after the findings-detail section, with 5 per-framework matrix pages + a paginated per-finding attribution table.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 3-5 days (4-day / 32h team-lead envelope per tasks.md triple sign-off) |
| Actual Duration | ~2 hours (autonomous `/aod.run` single-session wall-clock on 2026-04-18) |
| Variance | Delivered dramatically ahead of estimate — compression came from the dual-commit ADR governance pattern (already rehearsed by F-A1 + F-A2 the day before) removing governance friction, byte-identical baselines + pytest fixture infrastructure removing the "wait-for-regen" cost, TDD red/green on the aggregator running in parallel with Typst template authoring on disjoint files, and the post-merge SHA fill being a single-line T044 commit. Per KB-030 compressed-delivery pattern. |

---

## Surprise Log

**One cross-feature invariant collision surfaced at the PR CI gate** — module-level `import yaml` in `scripts/extract-report-data.py` collided with two invariants from prior features:

1. **Feature 128 stdlib-only invariant** — `tachi_parsers.py` lines 646 and 804 explicitly comment the project's posture: runtime scripts in `scripts/` are stdlib-only to keep `pyyaml` as a developer-only dependency. The Feature 194 aggregator legitimately needs `yaml.safe_load` to read `schemas/taxonomy/*.yaml` catalogs, but the module-level import violated the invariant silently — local pytest had `pyyaml` installed from `requirements-dev.txt` and passed cleanly.
2. **Feature 130 mmdc preflight CI gate** — `.github/workflows/tachi-mmdc-preflight.yml` runs `python3 scripts/extract-report-data.py` on a fresh Ubuntu image without `pip install`, expecting the mmdc preflight gate inside `render_mermaid_to_png` to fire with its 3 canonical error tokens. The module-level `import yaml` crashed the script at load with `ModuleNotFoundError: No module named 'yaml'` before the preflight gate could fire.

The CI red state surfaced immediately on PR push. Fix committed mid-PR (`6136e6b`) deferred `import yaml` inside `_load_framework_yaml_records` — the sole yaml-using function, guarded by the `has_source_attribution == true` branch that never fires on the mmdc preflight fixture. Also migrated one test patch target from `patch.object(extract_report_data.yaml, "safe_load", ...)` to `patch.object(yaml, "safe_load", ...)` because the module-level attribute no longer exists. All 42 tests green post-fix; mmdc preflight went green; SC-002 backward-compat byte-identity preserved.

The pattern (defer non-stdlib imports inside the functions that need them when runtime-script posture is stdlib-only, AND a CI gate runs in a fresh-install environment, AND the import is guarded by a runtime condition) is captured as KB-037 for future gap-closure features in the BLP-01 tier.

Otherwise smooth execution. The dual-commit Proposed → Accepted ADR governance pattern rehearsed twice the prior day (ADR-027 / F-A1 + ADR-028 / F-A2) reused structurally identically (ADR-029 Decision 7 mirrors ADR-028 Decision 7 / ADR-027 Decision 8) — the pattern is now the confirmed default protocol.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Tooling insight | Defer non-stdlib imports inside the functions that need them when the script is expected to run in a stdlib-only environment. Two CI signals to watch: `.github/workflows/tachi-mmdc-preflight.yml` runs without `pip install`, and `pyproject.toml` + `requirements*.txt` diff should remain empty per Feature 128. Paired test implication: patch targets need to reference the shared module (`yaml.safe_load`) rather than a module-level attribute (`extract_report_data.yaml`) because the attribute no longer exists at module scope. | KB-037 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: None net-new. The BLP-01 Foundation + gap-closure work is already captured in the existing backlog:

- **F-A3** — Populator wiring (11 threat agents emit `source_attribution` against F-A1 catalogs during detection). Explicit downstream scope boundary per F-B PRD. Turns the F-B coverage-attestation surface from "renders meaningful output only on manual opt-in" to "renders fully populated coverage tables on every real pipeline run." Highest-leverage remaining BLP-01 Foundation-tier work. Touches the 22-file detection tier that F-A1/F-A2/F-B deliberately preserved — the zero-edit invariant is carved out specifically for F-A3's scope.
- **F-C..F-8** — Gap-closure features (new agents / pattern enrichment) and final attestation pass (Tier 3 F-8) per BLP-01 sequenced initiative.

**Two efficiency findings deferred** from post-delivery simplify review (PR #197): duplicate YAML reads in `build_per_framework_aggregates` (load each catalog once instead of twice), and O(R·F·A) nested loop in `classify_framework_items` (pre-bucket citation index into a hash for O(F·A + R) lookup per framework). Both real wins, both hot-path-unexercised today because F-A3 hasn't shipped. Documented for follow-up when F-A3 populators make the hot path actually hot; neither finding touches determinism (ADR-021) or the test seam contract.

No new ideas surfaced during the retrospective. The F-B PRD's explicit scope boundaries (populators deferred to F-A3; crosswalk-JOIN deferred to F-C per FR-017) are holding cleanly — no scope drift to capture as follow-on.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/194-coverage-attestation-report-section/spec.md |
| Implementation Plan | specs/194-coverage-attestation-report-section/plan.md |
| Task Breakdown | specs/194-coverage-attestation-report-section/tasks.md |
| Research Notes | specs/194-coverage-attestation-report-section/research.md |
| Data Model | specs/194-coverage-attestation-report-section/data-model.md |
| Typst Data Contract | specs/194-coverage-attestation-report-section/contracts/typst-data-contract.md |
| Quickstart Walkthrough | specs/194-coverage-attestation-report-section/quickstart.md |
| F-A3 Coordination Decision | specs/194-coverage-attestation-report-section/fa3-coordination-decision.md |
| Agent Assignments | specs/194-coverage-attestation-report-section/agent-assignments.md |
| Next Session Handoff | specs/194-coverage-attestation-report-section/NEXT-SESSION.md |
| PRD | docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md |
| ADR | docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md |
| New Typst template | templates/tachi/security-report/coverage-attestation.typ |
| New aggregator | scripts/extract-report-data.py (new functions ~lines 973-1180; Typst emission ~lines 1660-1730; main() wiring ~lines 1985-2005) |
| main.typ integration | templates/tachi/security-report/main.typ (+29 lines conditional import + guards + include) |
| New aggregator tests | tests/scripts/test_coverage_attestation.py |
| New pagination smoke tests | tests/scripts/test_coverage_attestation_pagination.py |
| Synthetic fixture generator | tests/scripts/generate_pagination_fixture.py |
| Test fixtures | tests/scripts/fixtures/coverage_attestation/ (4 YAML fixtures + pagination smoke) |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 4 | APPROVED — `docs/product/02_PRD/INDEX.md` (Feature 194 row Approved → Delivered with PR link), `docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md` (frontmatter + body header to Delivered), `docs/product/05_User_Stories/README.md` (US-194-1/2/3 appended), `docs/product/06_OKRs/README.md` (F-194 delivery-log row) |
| Architecture | architect | 2 | APPROVED — `docs/architecture/00_Tech_Stack/README.md` (3 locations updated), `docs/architecture/01_system_design/README.md` (Feature 194 subsection corroborated) |
| DevOps | devops | 3 | APPROVED — `docs/devops/README.md` (new top-level F-194 section), `docs/devops/01_Local/README.md` (test layout + F-194 paragraph), `docs/devops/CI_CD_GUIDE.md` (aggregate 284 → 305 tests / 15 → 17 modules) |
| Strategy (internal) | n/a | 2 | `_internal/strategy/BLP-01-threat-coverage.md` (Status 2/11 → 3/11; F-B marked Delivered across §0 / §7 Feature Summary / §7 Foundation Tier / §7 F-B section / §12 Completion Tracker / Revision History); `_internal/planning/PLN-2026-04-10-backlog-execution.md` (F-A1 + F-A2 + F-B delivery entries added to Next Up + Dependency Graph + Revision Notes) |
| Institutional Knowledge | n/a | 1 | `docs/INSTITUTIONAL_KNOWLEDGE.md` (KB-037 entry authored; entry count 35 → 36) |

---

## Cleanup

- [x] Feature branch deleted (local + remote)
- [x] All tasks complete (46/46 — 45 on branch + T044 post-merge SHA fill direct to main)
- [x] GitHub Issue #194 closed with `stage:done` label
- [x] Committed and pushed (main: `c4b8dc6` feat merge + `6491f13` docs closure + `7ac3939` T044 fill + `ebb1522` BACKLOG regen + `8a2a2e3` simplify merge)
- [x] BACKLOG.md regenerated via `.aod/scripts/bash/backlog-regenerate.sh`
- [x] Release-please PR #196 auto-opened for v4.18.0 (pending manual merge to publish release tag)

**Feature 194 is officially CLOSED. BLP-01 Foundation tier now stands at 2/3 delivered (F-A1 + F-A2) and Reporting tier at 1/1 delivered (F-B) — F-A3 populator wiring is the highest-leverage remaining Foundation-tier work before ecosystem integrations can consume a fully populated coverage section on every real pipeline run.**
