---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-01
    status: APPROVED
    notes: "Plan faithfully operationalizes all 24 spec FRs and 18 SCs with stream-by-stream traceability. All three Plan-Day deferrals resolved with sound product rationale (Q-PM-1 single ADR-037, Q-Plan-1 API6→tool-abuse, Q-Plan-2 API9→info-disclosure). All three LOW PM concerns from spec sign-off addressed inline (FR-007 default verification, US-4 framing carry-forward, SC-016..SC-018 operational extensions accepted). Wave breakdown 5–6 working weeks matches PRD Option A budget; Memorial Day Mon 5/25 correctly handled between Waves 4.1 and 4.2; calendar Day 1 Thu 4/30 → Day 29 Wed 6/10. Out-of-scope discipline exemplary — Project Structure explicitly enumerates UNCHANGED files preserving F-7 28-file invariant, finding.yaml v1.8, zero new agent files, zero orchestrator edits, zero new runtime deps. Constitution Check passes all 10 principles. No new concerns identified. Full review: .aod/results/product-manager-plan-241.md."
  architect_signoff:
    agent: architect
    date: 2026-05-01
    status: APPROVED_WITH_CONCERNS
    notes: "Counts: 0 BLOCKING / 0 HIGH / 2 MEDIUM / 1 LOW. Plan architecturally sound on all 13 criteria including 11-host F-A3 scope, ADR-023 additive-only discipline, finding.yaml v1.8 unchanged, tactical-grouping Out-of-Scope strategy on TA0005/7/8/9/10/11/40, Q-PM-1/Q-Plan-1/Q-Plan-2 resolutions, and F-7 28-file zero-edit invariant. M-1 MEDIUM (declined MEDIUM-A's separate ADR but should add ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 — Resolution: tasks.md item to extend ADR-027 with 'Extended in ADR-037 D-7 — see also' addendum at file bottom). M-2 MEDIUM (aggregator filter insertion point misidentified — `_build_per_framework_aggregate()` already receives pre-computed yaml_record_count; filter must be applied upstream at `_load_framework_yaml_records()` or `load_framework_yaml_record_counts()` at lines 1073/1101 — Resolution: tasks.md clarifies chosen extension path; pre-computation flow well-documented at extract-report-data.py:1073-1109). L-1 LOW (2 net-new baselines path divergence — plan cites `examples/{arch}/security-report.pdf.baseline` but F-6/F-7 architectures live at `examples/{arch}/sample-report/security-report.pdf.baseline` — Resolution: tasks.md enumerate canonical path explicitly). None BLOCKING; all addressable in tasks.md (M-1 Wave 5.3, M-2 Wave 4.3, L-1 Wave 5.2). Constitution Check 10/10 PASS. Architect APPROVES_WITH_CONCERNS for /aod.tasks. Full review: .aod/results/architect-plan-241.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]

**Branch**: `241-web-api-coverage-attestation` | **Date**: 2026-05-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/241-web-api-coverage-attestation/spec.md`
**PRD**: [docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md](../../docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md)
**BLP-01 Phase**: Tier 3 — **closure feature** for the 11-feature initiative; combines F-8 (Web/API attestation) + F-A3 (populator wiring) per PRD Option A. Following ADR-036 (F-7) execution at 4–5-agent scope, F-241 operates at **11-host scope** across the entire detection tier.

## Summary

Run the final attestation pass that proves tachi's existing detection coverage per-finding inside every PDF security report. Four coordinated work streams:

1. **Stream 1 (F-A3 Populator Wiring)** — Wire `source_attribution` arrays inline in 11 host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`) per the F-1/F-2/F-4 net-new agent precedent (`primary` taxonomy citation + `related` CWE per pattern category). Wave 1 = 5 STRIDE-heavy hosts (Days 1–5; smoke-test on `web-app` + `agentic-app` + `predictive-ml-app` per Team-Lead MEDIUM-R2). Wave 2 = 6 hosts including `prompt-injection` + `agent-autonomy` (Days 6–11; +1 day absorbed for HIGH-A 11-host expansion).

2. **Stream 2 (Six Partial Web/API Item Closure)** — Close A05, A06, API8, API10 via Primary Source addition + Indicator extension on existing companion `detection-patterns.md` files (Architect Q-Architect-2 closeable under existing patterns). Close API6 + API9 via at most one new Indicator category each per FR-007. **Plan-Day Q-Plan-1 RESOLVED**: API6 → `tachi-tool-abuse` (architectural fit: API6's cross-agent flow-orchestration semantics align with tool-abuse's plugin-host trust-propagation surface; `privilege-escalation` rejected because API6 is about flow exhaustion + business-logic abuse, not direct authorization escalation). **Plan-Day Q-Plan-2 RESOLVED**: API9 → `tachi-info-disclosure` (architectural fit: API9's inventory-lifecycle semantics — undocumented endpoints leaking through stale inventory — align with info-disclosure's data-flow-leakage surface; `repudiation` rejected because API9 root cause is information leakage via undocumented surfaces, not audit-trail loss).

3. **Stream 3 (Taxonomy YAML Expansion)** — Expand `schemas/taxonomy/mitre-attack.yaml` from 38 to full ATT&CK Enterprise inventory using **tactical-grouping Out-of-Scope strategy** (TA0005/7/8/9/10/11/40 design-time-irrelevant; in-scope: TA0001/2/3/4/6/42). Expand `schemas/taxonomy/mitre-atlas.yaml` from 12 to ~30 records. Audit `schemas/taxonomy/owasp.yaml` (already 60 records) for citation completeness — no new rows. Each record gains 2 new optional fields: `out_of_scope: bool` (default `false`) + `out_of_scope_rationale: string` (default empty).

4. **Stream 4 (Pipeline-Generated Coverage Percentage + 8-Baseline Regen)** — Extend `scripts/extract-report-data.py` aggregator with Out-of-Scope-aware denominator filter at `_build_per_framework_aggregate()`. The coverage-percentage computation already exists (research finding); F-241 adds the Out-of-Scope filter. Preserve KB-037-aligned stdlib-only module-load invariant (yaml import remains in function bodies). Regenerate 8 baselines under `SOURCE_DATE_EPOCH=1700000000`: 6 pre-existing (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) + 2 net-new (`predictive-ml-app`, `mobile-banking-app`).

**Plan-Day Q-PM-1 RESOLVED — Single combined ADR-037**: One public ADR documenting all four work streams. Rationale: (a) PRD identifies the streams as a single Option A scope; (b) the four streams interlock (Stream 1 produces `source_attribution`, Stream 3 produces denominator inventory, Stream 4 reads both); (c) a split ADR would fragment the F-A3 closure narrative across two artifacts and complicate the cumulative ADR-032/034/035/036 deferral lineage citation. The taxonomy YAML +2-field record-shape extension (Architect MEDIUM-A) is acknowledged in a dedicated ADR-037 D-numbered decision (D-7) rather than a separate ADR. **Architect MEDIUM-A's "separate ADR alongside ADR-037" recommendation declined** with explicit rationale captured in ADR-037 D-7 narrative; PM and Architect joint sign-off on this resolution at plan-day.

**Architectural approach**: Apply ADR-023 Decision 3 additive-only edit discipline. F-A3 wiring on 11 host agents adds Detection Workflow / Example Findings populator blocks (~5–15 lines per agent; well under ADR-036 200-line cap with smallest agent at 53 lines and largest at 114 lines pre-edit). Stream 2 audit modifies up to 5 companion catalogs (`tachi-privilege-escalation`, `tachi-info-disclosure`, `tachi-tampering`, `tachi-tool-abuse` + optionally `tachi-repudiation`); preserves byte-identity on all other companions per F-7 28-file zero-edit invariant. Stream 3 taxonomy expansion adds records to two YAMLs and extends record shape on three. Stream 4 modifies one Python file (`extract-report-data.py`) + 8 baseline PDFs (intentional update). 4 new pytest scripts under `tests/scripts/`.

**Touch points**: 0 new agent files, 0 schema-shape edits to `schemas/finding.yaml`, 0 functional dispatch / orchestrator edits, 0 new runtime dependencies. **11 host agent edits** + **up to 5 companion catalog edits** (Stream 2) + **3 taxonomy YAML edits** + **1 aggregator script edit** + **1 ADR-037** + **8 baseline regenerations** + **4 new test scripts** + **1 §6 Coverage Matrix annotation** in `_internal/strategy/BLP-01-threat-coverage.md`. **Realistic envelope: 5–6 working weeks** per Architect Option A budget.

## Technical Context

**Language/Version**: Markdown + YAML (agent / skill / catalog content) + Python 3.11 (existing — stdlib + `pyyaml` for `extract-report-data.py`); methodology toolkit content, plus aggregator script extension in Stream 4.
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); **zero new runtime or dev dependencies** (FR-022).
**Storage**: File-based; reads `schemas/finding.yaml` (v1.8, **no edit**), writes to:
- `.claude/agents/tachi/{11 host agents}.md` (Stream 1)
- `.claude/skills/tachi-{up to 5 host skills}/references/detection-patterns.md` (Stream 2)
- `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas}.yaml` (Stream 3 — content + record-shape extension)
- `scripts/extract-report-data.py` (Stream 4)
- `examples/{8 architectures}/security-report.pdf.baseline` (Stream 4 intentional regen)
- `examples/predictive-ml-app/security-report.pdf.baseline` + `examples/mobile-banking-app/security-report.pdf.baseline` (Stream 4 net-new baselines)
- `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md` (NEW)
- `_internal/strategy/BLP-01-threat-coverage.md` (§6 Coverage Matrix demotion annotation)
- `tests/scripts/test_f_a3_populator_wiring.py` (NEW)
- `tests/scripts/test_coverage_attestation_audit.py` (NEW)
- `tests/scripts/test_coverage_percentage_computation.py` (NEW)
- `tests/scripts/test_pyyaml_deferred_import.py` (NEW)

**Testing**: pytest (existing harness at `tests/scripts/`) + four new test scripts:
- `test_f_a3_populator_wiring.py` — asserts `grep -l "source_attribution" .claude/agents/tachi/*.md` returns 14/14 detection-tier files (3 pre-existing F-1/F-2/F-4 + 11 newly wired)
- `test_coverage_attestation_audit.py` — walks `schemas/taxonomy/owasp.yaml`, resolves each Covered citation to ≥1 agent + ≥1 detection-pattern category per BLP-01 §8 Quality Bar
- `test_coverage_percentage_computation.py` — independently computes `% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|` from fixture findings; asserts equality (0 percentage point delta) with aggregator output
- `test_pyyaml_deferred_import.py` — asserts `import yaml` remains inside function bodies in `extract-report-data.py` (KB-037-aligned stdlib-only module-load invariant; pattern already in place at line 1085)

Plus regression: `test_backward_compatibility.py` updated to remove all 11 newly-wired hosts from `DETECTION_AGENT_PATHS` and add them to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (extending F-3/F-5/F-6/F-7 multi-host enrichment branch pattern). 6 non-target byte-identity baselines preserved under `SOURCE_DATE_EPOCH=1700000000` per ADR-021; 2 net-new baselines (`predictive-ml-app`, `mobile-banking-app`) added to mutation-target list alongside `agentic-app`, `consumer-agent-app`.

**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged).
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates + scripts + tests in a unified repo); no frontend/backend split.
**Performance Goals**: Per Architect Performance Requirements — coverage-percentage computation adds <2s to `extract-report-data.py` runtime per example (set-difference computation over ~700 total taxonomy items with tactical-grouping applied). YAML parse + index ≤500ms per framework on full-inventory ATT&CK YAML (~600 records).
**Constraints**: (a) **SC-001 + Metric 4**: 14/14 detection-tier agents emit `source_attribution` (BLOCKER); (b) **SC-007**: 8/8 baselines render non-empty Coverage Attestation section (BLOCKER); (c) **SC-009**: 0 percentage point delta between PDF-rendered and audit-script-computed coverage % per framework (BLOCKER); (d) **SC-014**: `schemas/finding.yaml` unchanged at v1.8 (BLOCKER); taxonomy YAML record shape gains exactly +2 fields with backward-compat default behavior (BLOCKER); (e) **SC-015**: `SOURCE_DATE_EPOCH=1700000000` byte-identity preserved on **non-Coverage-Attestation pages** of all 8 baseline PDFs (BLOCKER); the 8 PDFs are intentionally updated only on Coverage Attestation pages; (f) **SC-003 + ADR-036 cap**: no host agent's `.md` file exceeds 200 lines post-wiring (BLOCKER); (g) **FR-014** stdlib-only module-load invariant — `import yaml` stays in function bodies (BLOCKER, asserted by new test); (h) **FR-021** F-7 28-file detection-tier zero-edit invariant for non-target files (BLOCKER); (i) **FR-022** zero new runtime deps (BLOCKER, empty diff on `pyproject.toml`).
**Scale/Scope**: 11 host agent files modified (additive ~5–15 lines each, smallest 53 lines + largest 114 lines pre-edit); up to 5 companion catalog edits in Stream 2; 3 taxonomy YAML files modified (content expansion + record-shape +2 fields); 1 Python aggregator file extended; 4 new test scripts (~150–250 lines each); 1 new ADR (~500–600 lines including 10-decision structure + Mapping table); 1 §6 Coverage Matrix demotion annotation. **Edit surface is the largest single-feature scope in BLP-01 history** (combined attestation + populator-wiring across detection tier). Realistic envelope: 5–6 working weeks (Day 1 = Thu 2026-04-30 → Day 29 = Wed 2026-06-10), Memorial Day Mon 2026-05-25 non-working.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | F-241 is methodology-tier content/script enhancement; preserves the agent-pluralism architecture. No domain-specific logic added. The Out-of-Scope tactical-grouping on ATT&CK applies a generic design-time-vs-runtime distinction defensible across project types. |
| II. API-First Design | N/A | No REST/GraphQL surface; aggregator is internal report-data extraction. |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Taxonomy YAML record-shape extension is backward-compatible: existing F-A1 records that omit `out_of_scope` / `out_of_scope_rationale` parse correctly under YAML defaults (asserted by test). `schemas/finding.yaml` unchanged at v1.8 — sixth zero-`finding.yaml`-bump BLP-01 detection feature. F-A3 populator wiring is additive only; existing finding emissions continue to work. Pre-existing 6 baselines remain byte-identical except on Coverage Attestation pages. The §6 Coverage Matrix file remains readable (only its source-of-truth status is demoted via annotation). |
| IV. Concurrency & Data Integrity | N/A | F-241 is content authoring + script extension; no concurrent state machinery. |
| V. Privacy & Data Isolation | PASS | Worked examples + synthetic baselines only; no PII, no adopter data. ADR-037 + taxonomy YAMLs carry no commercial framing per SDR-001 Option C. |
| VI. Testing Excellence (MANDATORY) | PASS | Four new test scripts cover (1) F-A3 wiring audit (14/14 hosts), (2) coverage attestation audit (BLP-01 §8 Quality Bar), (3) coverage-percentage cross-check (0 ppt delta), (4) stdlib-only module-load invariant. Existing `test_backward_compatibility.py` updated for 11-host enrichment branch. Pytest harness preserved. Coverage targets: each new SC has a grep-checkable / wc-checkable / byte-identity / set-equality predicate. |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | 18 SCs (15 PRD-derived + 3 operational) map to verifiable predicates. SC-001/004/005/006/007/008/009/010/011/013/014/015 are BLOCKER-level gates. Delivery retrospective at `/aod.deliver` close-out. R12 release-please gate enforced via `.claude/rules/git-workflow.md` two-step. |
| VIII. Product-Spec Alignment | PASS | PRD 241 v1.2 has triple Triad sign-off (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS). spec.md has PM APPROVED_WITH_CONCERNS sign-off (3 LOW non-blocking concerns addressed in §"PM Concern Resolutions" below). |
| IX. Git Workflow | PASS | Feature branch `241-web-api-coverage-attestation` created; draft PR #242 opened with `feat(241):` Conventional Commits title at plan stage. ADR-037 Proposed → Accepted dual-commit pattern per ADR-027/032/034/035/036 lineage. R12 release-please mitigation enforced via two-step Pre-merge + Post-merge per `.claude/rules/git-workflow.md`. |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | F-7 28-file detection-tier zero-edit invariant carries forward for non-target files. Stream 1 modifies 11 host agents (Detection Workflow / Example Findings populator blocks); Stream 2 modifies up to 5 companion catalogs; remaining detection-tier files stay byte-identical. `finding-format-shared.md` unchanged. Orchestrator dispatch tier unchanged. |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/241-web-api-coverage-attestation/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (consolidated PRD + spec research)
├── data-model.md            # Phase 1 output — source_attribution shape, taxonomy record extension, coverage-aggregate Typst contract
├── contracts/
│   └── finding-contract.md  # Finding source_attribution + taxonomy record contracts
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (PM-validated)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── spoofing.md                                  # MODIFY (Stream 1, additive populator block) — 55 → ~70 lines
│   │       ├── tampering.md                                 # MODIFY (Stream 1, additive populator block) — 60 → ~75 lines
│   │       ├── info-disclosure.md                           # MODIFY (Stream 1, additive populator block) — 60 → ~75 lines
│   │       ├── privilege-escalation.md                      # MODIFY (Stream 1, additive populator block) — 55 → ~70 lines
│   │       ├── repudiation.md                               # MODIFY (Stream 1, additive populator block) — 53 → ~68 lines
│   │       ├── denial-of-service.md                         # MODIFY (Stream 1, additive populator block) — 56 → ~71 lines
│   │       ├── tool-abuse.md                                # MODIFY (Stream 1, additive populator block) — 100 → ~115 lines
│   │       ├── data-poisoning.md                            # MODIFY (Stream 1, additive populator block) — 90 → ~105 lines
│   │       ├── model-theft.md                               # MODIFY (Stream 1, additive populator block) — 105 → ~120 lines
│   │       ├── prompt-injection.md                          # MODIFY (Stream 1, additive populator block; per HIGH-A) — 96 → ~111 lines
│   │       ├── agent-autonomy.md                            # MODIFY (Stream 1, additive populator block; per HIGH-A) — 114 → ~129 lines
│   │       ├── output-integrity.md                          # UNCHANGED (F-1 net-new agent — already populates source_attribution)
│   │       ├── misinformation.md                            # UNCHANGED (F-2 net-new agent — already populates)
│   │       ├── human-trust-exploitation.md                  # UNCHANGED (F-4 net-new agent — already populates)
│   │       ├── orchestrator.md                              # UNCHANGED (no functional dispatch edit)
│   │       └── {other infrastructure agents}                # UNCHANGED (28-file detection-tier zero-edit invariant)
│   │
│   └── skills/
│       ├── tachi-privilege-escalation/                      # MODIFY (Stream 2: A05 + API8 closures via Primary Source addition + Indicator extension on existing Pattern Categories)
│       │   └── references/detection-patterns.md
│       ├── tachi-info-disclosure/                           # MODIFY (Stream 2: API9 closure via NEW Indicator category per Q-Plan-2 RESOLVED + API10 SSRF cross-reference)
│       │   └── references/detection-patterns.md
│       ├── tachi-tampering/                                 # MODIFY (Stream 2: A06 closure via Primary Source on Cat 8 Software Supply Chain + API10 Injection cross-reference)
│       │   └── references/detection-patterns.md
│       ├── tachi-tool-abuse/                                # MODIFY (Stream 2: API6 closure via NEW Indicator category per Q-Plan-1 RESOLVED)
│       │   └── references/detection-patterns.md
│       ├── tachi-repudiation/                               # UNCHANGED (Q-Plan-2 RESOLVED API9 to info-disclosure, not repudiation; companion stays byte-identical)
│       │   └── references/detection-patterns.md
│       ├── tachi-spoofing/                                  # UNCHANGED (Stream 2 has no spoofing-host items)
│       ├── tachi-denial-of-service/                         # UNCHANGED
│       ├── tachi-data-poisoning/                            # UNCHANGED
│       ├── tachi-model-theft/                               # UNCHANGED
│       ├── tachi-prompt-injection/                          # UNCHANGED
│       ├── tachi-agent-autonomy/                            # UNCHANGED
│       ├── tachi-output-integrity/ tachi-misinformation/ tachi-human-trust-exploitation/  # UNCHANGED
│       └── tachi-orchestration/  tachi-shared/              # UNCHANGED
│
├── schemas/
│   ├── finding.yaml                                         # UNCHANGED — schema_version stays "1.8"; id.pattern unchanged (sixth zero-bump BLP-01 detection feature)
│   └── taxonomy/
│       ├── owasp.yaml                                       # MODIFY (Stream 3) — 60 records preserved (no new rows); record shape +2 fields (out_of_scope + out_of_scope_rationale, default false/empty); citation-completeness audit per BLP-01 §8 Quality Bar
│       ├── mitre-attack.yaml                                # MODIFY (Stream 3) — 38 → ~600 records (full Enterprise inventory); tactical-grouping Out-of-Scope on TA0005/7/8/9/10/11/40 (5–7 tactic-level rationales); per-item Out-of-Scope only on items inside in-scope tactics (TA0001/2/3/4/6/42)
│       └── mitre-atlas.yaml                                 # MODIFY (Stream 3) — 12 → ~30 records (full ATLAS inventory); per-item Out-of-Scope annotations
│
├── scripts/
│   ├── extract-report-data.py                               # MODIFY (Stream 4) — extend `_build_per_framework_aggregate()` (line 1144) with Out-of-Scope-aware denominator filter; preserve stdlib-only module-load invariant (yaml import stays in function bodies); +~30-50 lines
│   └── tachi_parsers.py                                     # UNCHANGED (validates references field — F-241 changes no parser logic)
│
├── templates/
│   └── tachi/security-report/coverage-attestation.typ       # UNCHANGED — coverage-percentage rendering already in place at line 168 (already binds `coverage-percentage` field from `per-framework-aggregates` data contract; F-241's incremental work is upstream — Stream 1 populates inputs, Stream 4 fills percentage values)
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-037-web-api-coverage-attestation-and-populator-wiring.md  # NEW — Proposed → Accepted dual-commit; single combined ADR per Q-PM-1 plan-day RESOLVED; 10 D-numbered decisions
│
├── tests/
│   └── scripts/
│       ├── test_f_a3_populator_wiring.py                    # NEW (Stream 1 verification) — asserts 14/14 detection-tier agents emit source_attribution
│       ├── test_coverage_attestation_audit.py               # NEW (Stream 2 + Stream 3 verification) — walks taxonomy YAMLs, resolves each Covered citation to ≥1 agent + ≥1 pattern category
│       ├── test_coverage_percentage_computation.py          # NEW (Stream 4 verification) — independently computes coverage % from fixtures; asserts 0 ppt delta with aggregator output
│       ├── test_pyyaml_deferred_import.py                   # NEW (Stream 4 invariant) — asserts `import yaml` inside function bodies in extract-report-data.py
│       ├── test_backward_compatibility.py                   # MODIFY (additive infrastructure update) — DETECTION_AGENT_PATHS removes 11 newly-wired hosts; DETECTION_PATTERN_REF_ENRICHMENT_HOSTS frozenset adds 11 hosts
│       └── fixtures/
│           └── web_api_coverage_attestation/                # NEW — fixture findings exercising source_attribution arrays for 6 Partial-item closures + cross-framework citation patterns
│
├── examples/
│   ├── web-app/security-report.pdf.baseline                 # MODIFY (Stream 4 intentional regen — Coverage Attestation section populated; non-CA pages byte-identical)
│   ├── microservices/security-report.pdf.baseline           # MODIFY (Stream 4 intentional regen)
│   ├── ascii-web-api/security-report.pdf.baseline           # MODIFY (Stream 4 intentional regen)
│   ├── mermaid-agentic-app/security-report.pdf.baseline     # MODIFY (Stream 4 intentional regen)
│   ├── free-text-microservice/security-report.pdf.baseline  # MODIFY (Stream 4 intentional regen)
│   ├── maestro-reference/security-report.pdf.baseline       # MODIFY (Stream 4 intentional regen)
│   ├── predictive-ml-app/security-report.pdf.baseline       # NEW (Stream 4 net-new baseline; F-6's example architecture gains its first baseline)
│   ├── mobile-banking-app/security-report.pdf.baseline      # NEW (Stream 4 net-new baseline; F-7's example architecture gains its first baseline)
│   ├── agentic-app/                                         # UNCHANGED (no baseline; out of F-241 scope per spec FR-021)
│   └── consumer-agent-app/                                  # UNCHANGED (no baseline; out of F-241 scope per spec FR-021)
│
└── _internal/
    └── strategy/
        └── BLP-01-threat-coverage.md                        # MODIFY (Stream 4 close-out) — §6 Coverage Matrix annotated "historical — superseded by pipeline-generated attestation" + pointer to F-B Coverage Attestation section
```

**Structure Decision**: Single-project layout (existing tachi repo structure). **Zero new top-level directories**. All changes confined to `.claude/agents/tachi/`, `.claude/skills/tachi-{4 catalogs}/references/`, `schemas/taxonomy/`, `scripts/`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/{8 baselines}/`, `_internal/strategy/`. F-241 follows ADR-023 (additive-only edits), ADR-027 (taxonomy catalog shape extended +2 fields per Architect MEDIUM-A), ADR-028 (`source_attribution` schema unchanged), ADR-029 (F-B rendering surface preserved), ADR-032/034/035/036 (F-A3 deferral lineage closed), and Feature 128 (stdlib-only module-load invariant preserved per KB-037). **F-241 is the first BLP-01 feature to exercise ADR-023 Decision 3 at 11-host scope simultaneously** — 7× the 1-host F-3 surface, 5.5× the 2-host F-5 surface, 3.7× the 3-host F-6 surface, 2.2× the 5-host F-7 surface.

## System Design

### Components

**Modified components (additive edits only — F-241-owned)**:

#### Stream 1 — F-A3 Populator Wiring (11 host agents)

For each of the 11 host agents, the additive edit pattern is:

1. **`## Example Findings` section** (or equivalent Detection Workflow Step 5 References block) — add an inline YAML example showing `source_attribution` array with the canonical pattern: one `primary` taxonomy citation + ≥1 `related` CWE per pattern category. Pattern matches F-1/F-2/F-4 net-new agent precedent verbatim (e.g., `output-integrity.md` lines 64–70 for the canonical shape).

2. **Per-pattern-category Primary Source attribution** — wire the `source_attribution` array to cite the Primary Source already established in the companion `references/detection-patterns.md` file. No companion catalog edit needed except in Stream 2 (where 4 catalogs gain new Indicator categories or Primary Source extensions).

The populator wiring is **purely additive** — no functional changes to existing detection logic, no removal of existing pattern categories, no modification to Pattern Category → Primary Source maps. Each host agent gains ~5–15 net-new lines (single YAML example block + 1–2 lines of explanatory text).

#### Stream 2 — Six Partial Web/API Item Closures

| Item | Closure Path | Target Companion Catalog |
|------|--------------|--------------------------|
| A05 Security Misconfiguration | Primary Source addition + non-mobile Indicator extension on Pattern Category 11 | `tachi-privilege-escalation/references/detection-patterns.md` |
| A06 Vulnerable and Outdated Components | Primary Source block on Pattern Category 8 (Software Supply Chain Integrity Failures) | `tachi-tampering/references/detection-patterns.md` |
| API6 Unrestricted Access to Sensitive Business Flows | **NEW Indicator category** per Q-Plan-1 RESOLVED → `tachi-tool-abuse` | `tachi-tool-abuse/references/detection-patterns.md` |
| API8 Security Misconfiguration | API-specific Indicator extension on Pattern Category 11 | `tachi-privilege-escalation/references/detection-patterns.md` (same file as A05; consolidates) |
| API9 Improper Inventory Management | **NEW Indicator category** per Q-Plan-2 RESOLVED → `tachi-info-disclosure` | `tachi-info-disclosure/references/detection-patterns.md` |
| API10 Unsafe Consumption of APIs | Primary Source + cross-reference on Cat 9 (Injection) and Cat 7 (SSRF) | `tachi-tampering/...` (Injection) + `tachi-info-disclosure/...` (SSRF cross-reference; same file as API9) |

Net: 4 catalog files modified (`tachi-privilege-escalation`, `tachi-info-disclosure`, `tachi-tampering`, `tachi-tool-abuse`); `tachi-repudiation` companion remains byte-identical (Q-Plan-2 RESOLVED API9 to info-disclosure, not repudiation).

#### Stream 3 — Taxonomy YAML Expansion (3 files)

- **`owasp.yaml`** (60 records, no new rows): Citation-completeness audit. Each existing row gains 2 new fields (`out_of_scope: false`, `out_of_scope_rationale: ""`) per ADR-027 D1 record-shape extension. Each Covered row attests at least one agent + one detection-pattern category citation per BLP-01 §8 Quality Bar (no shape change to citation field; this is an audit confirmation, not an edit).
- **`mitre-attack.yaml`** (38 → ~600 records): Full Enterprise inventory expansion. Tactical-grouping Out-of-Scope strategy:
  - Out-of-Scope at tactic level: TA0005 Defense Evasion, TA0007 Discovery, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command and Control, TA0040 Impact (5–7 tactic-level rationales). Items in these tactics inherit Out-of-Scope from the tactic; per-item rationale not required (clarification: Out-of-Scope is annotated at the tactic-level group; individual items in those tactics carry `out_of_scope: true` with the tactic-level rationale referenced).
  - In-Scope tactics: TA0001 Initial Access, TA0002 Execution, TA0003 Persistence, TA0004 Privilege Escalation, TA0006 Credential Access, TA0042 Resource Development. Per-item Out-of-Scope rationale only on individual items inside these tactics (e.g., specific runtime-only sub-techniques).
- **`mitre-atlas.yaml`** (12 → ~30 records): Full ATLAS inventory expansion with per-item Out-of-Scope annotations where applicable.

Record shape extension (applies to all 3 files):
```yaml
- id: A05
  full_id: OWASP-2021-A05
  name: Security Misconfiguration
  url: https://owasp.org/Top10/2021/A05_2021-Security_Misconfiguration/
  cwe_refs: [CWE-16, CWE-2, ...]
  out_of_scope: false                                       # NEW (default false)
  out_of_scope_rationale: ""                                # NEW (default empty)
```

Backward-compat: Existing F-A1 records that omit the two new fields parse correctly (YAML defaults applied at load time).

#### Stream 4 — Aggregator Extension + Baseline Regen

**Aggregator extension** (`scripts/extract-report-data.py`):

- `_load_framework_yaml_records()` (line 1085) — preserves stdlib-only module-load invariant (`import yaml` stays inside function body); no change required to import structure.
- `classify_framework_items()` (lines 1112–1140) — preserve existing 3-value classification (Covered / Partial / Gap) per ADR-029 contract.
- `_build_per_framework_aggregate()` (line 1144) — **EXTEND**: filter denominator by `out_of_scope: false` records before computing `(covered_count / yaml_record_count) * 100`. Numerator preserved (covered count only, not covered+partial). New computation:
  ```python
  in_scope_records = [r for r in records if not r.get("out_of_scope", False)]
  denominator = len(in_scope_records)
  coverage_pct = (covered_count / denominator) * 100 if denominator else None
  ```
  Edge case: `denominator == 0` returns "N/A" (preserve existing behavior).

**Baseline regen** (8 architectures):

- 6 pre-existing baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. Coverage Attestation pages updated with populated source_attribution + per-framework coverage percentages. Non-CA pages remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`.
- 2 net-new baselines: `predictive-ml-app` (F-6 example), `mobile-banking-app` (F-7 example). First-time baseline authoring; full PDF generated under `SOURCE_DATE_EPOCH=1700000000`.

#### Cross-Cutting

- **ADR-037** (~500–600 lines, 10 D-numbered decisions per the Q-PM-1-resolved single-ADR scope; mirrors ADR-035 D-9 / ADR-036 D-10 structural precedent).
- **§6 Coverage Matrix demotion** (`_internal/strategy/BLP-01-threat-coverage.md`) — annotation only; matrix prose preserved.
- **4 new test scripts** under `tests/scripts/` (Stream 1/2/3/4 verification + invariant guard).

### Data Flow

```
1. STREAM 1 — F-A3 Populator Wiring
   Pre-condition: 11 host agents emit findings without source_attribution arrays.
   ↓ (Wave 1: Days 1–5; Wave 2: Days 6–11)
   Post-condition: All 11 host agents include inline `source_attribution` examples
   in their Detection Workflow / Example Findings sections, citing one `primary`
   taxonomy + ≥1 `related` CWE per pattern category. grep returns 14/14 hits.

2. STREAM 2 — Six Partial Item Closures
   Pre-condition: 6 Partial Web/API items (A05, A06, API6, API8, API9, API10)
   carry no Primary Source attribution in companion catalogs.
   ↓ (Days 6–13; parallel with Stream 1 Wave 2)
   Post-condition: 4 catalog files modified with citation-grounded Primary Source
   blocks or new Indicator categories. Each closed item attests ≥1 agent + ≥1
   detection-pattern category per BLP-01 §8 Quality Bar.

3. STREAM 3 — Taxonomy YAML Expansion
   Pre-condition: owasp.yaml (60), mitre-attack.yaml (38), mitre-atlas.yaml (12).
   ↓ (Days 14–19, ATT&CK-bottleneck week)
   Post-condition: owasp.yaml (60, audited + +2 fields per record),
   mitre-attack.yaml (~600, +2 fields, tactical-grouping Out-of-Scope on 7 tactics),
   mitre-atlas.yaml (~30, +2 fields, per-item Out-of-Scope where applicable).

4. STREAM 4 — Aggregator + 8-Baseline Regen
   Pre-condition: extract-report-data.py reads source_attribution arrays without
   Out-of-Scope filter; 6 pre-existing baselines render empty Coverage Attestation
   sections (5 of 6 baselines today + agentic-app one renders today per F-1/F-2/F-4
   findings).
   ↓ (Days 20–25)
   Post-condition: Aggregator filters denominator by Out-of-Scope; 8 baselines
   regenerate with populated Coverage Attestation sections. Non-CA pages remain
   byte-identical under SOURCE_DATE_EPOCH=1700000000. Audit-script-vs-PDF
   coverage-% delta = 0 ppt across all 5 frameworks × 8 baselines.

5. CROSS-CUTTING — ADR-037 + §6 Demotion + Tests
   Pre-condition: 4-feature F-A3 deferral debt accumulated (ADR-032/034 D-8/035
   D-10/036 D-10); §6 Coverage Matrix is hand-curated source of truth.
   ↓ (Days 22–29)
   Post-condition: ADR-037 Proposed at Day 26 → Accepted at Day 27 (post-merge
   SHA fill-in per dual-commit governance). §6 Coverage Matrix annotated
   "historical — superseded by pipeline-generated attestation" with pointer to
   F-B section. 4 new test scripts pass green; test_backward_compatibility.py
   updated for 11-host enrichment branch. PR #242 squash-merged with feat(241):
   title at Day 29; release-please PR opens within ~30s per R12 verification.
```

### Tech Stack

- **Markdown + YAML** (agent + skill + catalog content authoring) — Stream 1, Stream 2, Stream 3.
- **Python 3.11 + stdlib + pyyaml** (aggregator extension) — Stream 4. `pyyaml` already declared (deferred import inside function bodies per FR-014).
- **pytest** (test harness) — 4 new test scripts + 1 modified test script. Already declared.
- **Typst + Mermaid CLI** (PDF rendering) — UNCHANGED. F-B template (`coverage-attestation.typ`) already binds `coverage-percentage` field at line 168; F-241 fills the value via Stream 4.
- **Git + GitHub CLI** (`gh`) — branch + draft PR + merge + release-please verification. UNCHANGED workflow per `.claude/rules/git-workflow.md` two-step.

## Phase 0 — Outline & Research

Research consolidated in `research.md` (created during `/aod.spec`). Key findings:

- **F-A3 wiring template**: F-1/F-2/F-4 net-new agents populate `source_attribution` in `## Example Findings` sections. Pattern: `{taxonomy: owasp, id: <ID>, relationship: primary}` + `{taxonomy: cwe, id: <CWE>, relationship: related}`.
- **Aggregator semantics**: `classify_framework_items()` at `extract-report-data.py:1112` reads `finding.source_attribution[].id` directly with no implicit prefix-attribution path. Coverage % computed at `_build_per_framework_aggregate()` line 1144 — `(covered_count / yaml_record_count) * 100`. F-241 adds Out-of-Scope-aware denominator filter.
- **YAML import discipline**: `import yaml` already at function scope (line 1085); test `test_pyyaml_deferred_import.py` codifies invariant.
- **Taxonomy state**: `owasp.yaml` already at 60 records (audit-only, no expansion); `mitre-attack.yaml` 38 → ~600 (largest delta); `mitre-atlas.yaml` 12 → ~30. Record shape +2 fields backward-compat preserved.
- **Eight-baseline scope**: 6 pre-existing baselines + 2 net-new (`predictive-ml-app` F-6, `mobile-banking-app` F-7) per Architect Q-Architect-4 MEDIUM resolution.
- **ADR-037 next available**: ADR-036 highest existing; ADR-004 historically absent; F-241 = ADR-037.

No NEEDS CLARIFICATION markers remain. Phase 0 complete.

## Phase 1 — Design Artifacts

To be generated as separate files at `specs/241-web-api-coverage-attestation/`:

- **`data-model.md`** — Documents:
  - `source_attribution` array shape (per ADR-028: `{taxonomy, id, relationship}` with 5-value taxonomy enum + 3-value relationship enum; default `relationship: primary`).
  - Taxonomy YAML record shape extension (per ADR-027 D1 + Architect MEDIUM-A: `out_of_scope: bool` default `false` + `out_of_scope_rationale: string` default empty).
  - F-B Typst data contract (`per-framework-aggregates` array with `coverage-percentage` field, already in place at line 168 of `coverage-attestation.typ`).
  - 6 Partial item closure mapping (A05/A06/API6/API8/API9/API10 → host catalogs per Stream 2 table above).
  - Tactical-grouping Out-of-Scope rationale set (5–7 ATT&CK tactic-level rationales for TA0005/7/8/9/10/11/40).

- **`contracts/finding-contract.md`** — Documents:
  - `source_attribution` populator contract for the 11 newly-wired host agents (one `primary` OWASP/ASI/LLM/Mobile citation + ≥1 `related` CWE per pattern category).
  - Coverage-percentage computation contract (`% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|`).
  - Catalog-resolvable vs prose-only reference rule (catalog-resolvable references appear in `source_attribution` array; prose-only references appear in finding `references:` array as narrative context only — preserves F-7 ADR-036 D-7 precedent).

- **`quickstart.md`** — Verification walkthrough:
  - `grep -l "source_attribution" .claude/agents/tachi/*.md` returns 14 files
  - `pytest tests/scripts/test_f_a3_populator_wiring.py` — green
  - `pytest tests/scripts/test_coverage_attestation_audit.py` — green
  - `pytest tests/scripts/test_coverage_percentage_computation.py` — green
  - `pytest tests/scripts/test_pyyaml_deferred_import.py` — green
  - `make regenerate` (or per-example invocation) — 8 baselines render Coverage Attestation
  - Manual diff: non-CA pages of 6 pre-existing baselines remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`

- **Agent context update**: `.aod/scripts/bash/update-agent-context.sh claude` invoked at plan-day to refresh agent-specific context with F-241 scope.

## Plan-Day Decisions Resolved

The three Plan-Day deferrals from spec.md resolved at plan authoring:

| ID | Question | Resolution | Rationale |
|----|----------|-----------|-----------|
| Q-PM-1 | Single combined ADR-037 vs split (one for F-8 attestation + one for F-A3 + record-shape extension)? | **Single combined ADR-037** with 10 D-numbered decisions. Architect MEDIUM-A's "separate ADR alongside ADR-037" recommendation declined. | (a) Four streams interlock and share the F-A3 closure narrative; (b) PRD identifies the streams as a single Option A scope; (c) split would fragment ADR-032/034/035/036 deferral lineage citation; (d) record-shape extension acknowledged in dedicated D-7 narrative within ADR-037. PM + Architect joint sign-off on the resolution at plan day. |
| Q-Plan-1 | API6 closure host: `tachi-tool-abuse` vs `tachi-privilege-escalation`? | **`tachi-tool-abuse`** | API6's semantics (cross-agent flow orchestration / business-flow exhaustion / abuse-of-functionality) align with tool-abuse's plugin-host trust-propagation surface. `privilege-escalation` rejected because API6 root cause is flow exhaustion + business-logic abuse, not direct authorization escalation. Architect Q2 dual-candidate language preserved both as in-scope; tool-abuse fit is stronger architecturally. |
| Q-Plan-2 | API9 closure host: `tachi-info-disclosure` vs `tachi-repudiation`? | **`tachi-info-disclosure`** | API9's semantics (improper inventory management / undocumented endpoints / shadow APIs leaking through stale inventory) align with info-disclosure's data-flow-leakage surface. `repudiation` rejected because API9 root cause is information leakage via undocumented surfaces, not audit-trail loss. Architect Q2 dual-candidate language preserved both as in-scope; info-disclosure fit is stronger architecturally. |

## PM Concern Resolutions

The three LOW concerns from PM review (`.aod/results/product-manager.md` §8) addressed at plan authoring:

- **Concern §8.1 (Stream 2 FR-007 Plan-Day default attestation)**: Resolved at plan-day per Q-Plan-1 + Q-Plan-2 above. Architect first-principles fit analysis applied; the spec's Plan-Day defaults converged with Architect's analysis (no disagreement). Concern fully resolved.

- **Concern §8.2 (US-4 Independent Test "non-AI baselines" framing)**: Spec wording will be carried forward without change; the framing is operationally unambiguous given that US-4 AC-2 already enumerates per-baseline expectations. No spec.md edit required. (Minor editorial choice; addressed in tasks.md narrative for Wave 2 build documentation but does not block sign-off.)

- **Concern §8.3 (SC-016..SC-018 operational extensions)**: PM acknowledges these three additive SCs as operational extensions of the PRD (not scope expansion). Origin trace: SC-016 derives from `.claude/rules/git-workflow.md` R12 enforcement; SC-017 derives from PRD §"Validation Rules"; SC-018 derives from PRD §Week 1 Day 5 smoke test. Acknowledged + accepted at plan-day. PM and Architect agree these belong in the spec at the operational-completeness layer, not in the PRD at the scope-definition layer.

## Wave Breakdown (5–6 working weeks)

**Calendar**: Day 1 = Thu 2026-04-30 → Day 29 = Wed 2026-06-10. Memorial Day Mon 2026-05-25 non-working (4 working days that week).

| Wave | Days | Stream | Deliverable |
|------|------|--------|-------------|
| 0.0 | Day 0 (Wed 4/29) | All | Plan-day approvals on plan.md (PM + Architect sign-off; this document). Pair-authoring reservation (senior-backend-engineer + security-analyst) confirmed. |
| 1.1 | Days 1–2 (Thu 4/30 + Fri 5/1) | Stream 1 Wave 1 | Wire `tachi-spoofing` + `tachi-tampering` + `tachi-info-disclosure` (3 of 5 STRIDE-heavy hosts). Pair-authoring per Team-Lead MEDIUM-R1 keeps senior-backend-engineer load within 80%/day cap. |
| 1.2 | Days 3–4 (Mon 5/4 + Tue 5/5) | Stream 1 Wave 1 | Wire `tachi-privilege-escalation` + `tachi-repudiation` (final 2 of 5 STRIDE-heavy hosts). Pair-authoring continues. |
| 1.3 | Day 5 (Wed 5/6) | Stream 1 Wave 1 | F-A3 wiring smoke test on 3 baselines (`web-app` + `agentic-app` + `predictive-ml-app`) per Team-Lead MEDIUM-R2. **Deliverable**: 5/11 hosts wired; smoke test green on 3 baselines surfacing STRIDE/AI/ML coverage early. |
| 2.1 | Days 6–7 (Thu 5/7 + Fri 5/8) | Stream 1 Wave 2 + Stream 2 start | Wire `tachi-denial-of-service` + `tachi-tool-abuse`. Begin Stream 2 audit: A05 + A06 closures via Primary Source addition. |
| 2.2 | Days 8–9 (Mon 5/11 + Tue 5/12) | Stream 1 Wave 2 + Stream 2 | Wire `tachi-data-poisoning` + `tachi-model-theft`. Continue Stream 2: API8 closure. |
| 2.3 | Days 10–11 (Wed 5/13 + Thu 5/14) | Stream 1 Wave 2 + Stream 2 | Wire `tachi-prompt-injection` + `tachi-agent-autonomy` (the +1 day absorbed for HIGH-A 11-host expansion). F-A3 closure verification across all 8 baselines. **Deliverable**: 11/11 hosts wired; 14/14 detection-tier total; F-A3 deferral debt fully cleared. |
| 3.1 | Days 12–13 (Fri 5/15 + Mon 5/18) | Stream 2 completion | Close API6 (NEW Indicator on `tachi-tool-abuse` per Q-Plan-1) + API9 (NEW Indicator on `tachi-info-disclosure` per Q-Plan-2) + API10 (Cat 9 + Cat 7 cross-references). **Deliverable**: 6/6 Partial items closed (or any non-closing item surfaces with Deferral ADR rationale + follow-on Issue per FR-008). |
| 3.2 | Days 14–16 (Tue 5/19 + Wed 5/20 + Thu 5/21) | Stream 3 OWASP + ATLAS | Audit `owasp.yaml` for citation completeness; expand `mitre-atlas.yaml` from 12 → ~30 records with per-item Out-of-Scope; add +2 fields to all records in both YAMLs. **Deliverable**: 2 of 3 taxonomy YAMLs complete. |
| 4.1 | Day 17 (Fri 5/22) | Stream 3 ATT&CK start | Begin ATT&CK Enterprise tactical-grouping audit: 5–7 tactic-level Out-of-Scope rationales for TA0005/7/8/9/10/11/40. |
| --- | Mon 5/25 | --- | Memorial Day — non-working. |
| 4.2 | Days 18–19 (Tue 5/26 + Wed 5/27) | Stream 3 ATT&CK | Complete ATT&CK Enterprise inventory expansion (per-item rationale on in-scope tactics TA0001/2/3/4/6/42). **Deliverable**: 3 of 3 taxonomy YAMLs at full inventory. |
| 4.3 | Days 20–21 (Thu 5/28 + Fri 5/29) | Stream 4 aggregator | Extend `_build_per_framework_aggregate()` with Out-of-Scope-aware denominator filter; preserve stdlib-only module-load invariant. **Deliverable**: aggregator extension complete + green unit-test fixture. |
| 5.1 | Days 22–23 (Mon 6/1 + Tue 6/2) | Tests | Author 4 new test scripts: `test_f_a3_populator_wiring.py`, `test_coverage_attestation_audit.py`, `test_coverage_percentage_computation.py`, `test_pyyaml_deferred_import.py`. Update `test_backward_compatibility.py`. **Deliverable**: 4 new test scripts green + 1 modified test script green. |
| 5.2 | Days 24–25 (Wed 6/3 + Thu 6/4) | Stream 4 baseline regen | Regenerate 8 example baselines under `SOURCE_DATE_EPOCH=1700000000`; verify non-CA pages byte-identical on 6 pre-existing baselines; author 2 net-new baselines (`predictive-ml-app`, `mobile-banking-app`). **Deliverable**: 8 of 8 baselines regenerated + byte-identity assertion passing. |
| 5.3 | Day 26 (Fri 6/5) | Cross-cutting | §6 Coverage Matrix demotion annotation; ADR-037 Proposed (10-decision structure including Q-PM-1 D-7 record-shape extension narrative). |
| 6.1 | Day 27 (Mon 6/8) | Cross-cutting | ADR-037 Accepted (post-merge SHA fill-in per dual-commit governance pattern from ADR-035 D-10). |
| 6.2 | Day 28 (Tue 6/9) | Cross-cutting | Triple Triad sign-off on tasks.md (PM + Architect + Team-Lead). |
| 6.3 | Day 29 (Wed 6/10) | Cross-cutting | PR #242 squash-merge with `feat(241):` Conventional Commit title; release-please PR fires within ~30s per R12 verification. |
| Buffer | Days 30+ | Reserve | Reserved for Risk 1 (ATT&CK depth overrun) or Risk 3 (1–2 Partial item Deferrals require ADR rationale + follow-on Issue). |

## Complexity Tracking

*No constitution violations. No Complexity Tracking entries required.*

## ADR-037 D-numbered Decision Outline

The single combined ADR-037 (per Q-PM-1 plan-day RESOLVED) is structured as 10 D-numbered decisions:

| ID | Decision | Stream |
|----|----------|--------|
| D-1 | Combined-vs-split-ADR scope (RESOLVED single combined per Q-PM-1) | Cross-cutting |
| D-2 | F-A3 11-host expansion (per Architect HIGH-A: includes `prompt-injection` + `agent-autonomy` because aggregator reads only `source_attribution[].id` directly) | Stream 1 |
| D-3 | F-A3 wiring template (one `primary` + ≥1 `related` CWE per pattern category, mirroring F-1/F-2/F-4 net-new agent precedent) | Stream 1 |
| D-4 | Six Partial item closure mapping (4 closeable + 2 new-Indicator per Architect Q2; with Q-Plan-1 + Q-Plan-2 plan-day RESOLVED for API6 + API9 host placement) | Stream 2 |
| D-5 | Tactical-grouping Out-of-Scope strategy on ATT&CK Enterprise (5–7 design-time-irrelevant tactics: TA0005/7/8/9/10/11/40) | Stream 3 |
| D-6 | ATLAS + OWASP audit-only scope (ATLAS 12 → ~30 with per-item Out-of-Scope; OWASP 60 records audited for citation completeness, no new rows) | Stream 3 |
| D-7 | Taxonomy YAML record-shape +2-field extension (`out_of_scope` + `out_of_scope_rationale`) acknowledged per Architect MEDIUM-A; backward-compat preserved via YAML defaults | Stream 3 / cross-cutting |
| D-8 | Aggregator Out-of-Scope-aware denominator filter at `_build_per_framework_aggregate()`; coverage-percentage = `|cited_ids| / |taxonomy_ids_not_out_of_scope|`; stdlib-only module-load invariant preserved | Stream 4 |
| D-9 | Eight-baseline scope expansion (6 pre-existing + 2 net-new for `predictive-ml-app` + `mobile-banking-app`); intentional baseline updates only on Coverage Attestation pages, byte-identity preserved on non-CA pages | Stream 4 |
| D-10 | F-A3 deferral lineage closure (ADR-032 / ADR-034 D-8 / ADR-035 D-10 / ADR-036 D-10 → ADR-037 closes all four); §6 Coverage Matrix demoted to historical with pointer to F-B section | Cross-cutting |

ADR-037 lifecycle: Proposed at Day 26 (Fri 6/5) → Accepted at Day 27 (Mon 6/8) per dual-commit governance pattern (ADR-035 D-10 / ADR-036 D-10 precedent).
