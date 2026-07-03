# Research Summary: F-292 Post-Merge Verification Runs (T017 + T026)

**Feature**: 295 | **Date**: 2026-07-03 | **Phase**: pre-spec research (4 parallel tracks)
**Full track reports**: `.aod/results/research-kb.md`, `.aod/results/research-codebase.md`, `.aod/results/research-architecture.md`, `.aod/results/research-web.md`
**Verdict**: PRD v1.2 claims verified 9/9 at HEAD (`dc97fe5`); 2 substantive drifts + 1 stale-framing supersession to fold into the spec.

## Knowledge Base Findings

KB at `docs/INSTITUTIONAL_KNOWLEDGE.md` (21 entries); 12 relevant. Primary:

- **Entry 7** (F-292 post-merge accountability): Issue #295 *is* the codified follow-up-issue pattern — F-295 executes the deferred-task ledger. Close gate = runs executed + evidence committed + disposition recorded, **never** a particular verification outcome.
- **Entry 6** (F-292 build retro): T017's pass criterion is contractually pre-defined — byte-identical **OI-scoped subset** (not whole-file) vs pre-292 anchor. Cat 6 = CWE-943 (distinct from Cat 2's CWE-89). Scope fence: F-295 must not touch detection-tier files at all (pure verification + evidence commits).
- **Entry 15** (consequence-scope): record **literal pre-state pytest totals at T001** before any artifact lands (inherited-vs-own red attribution); sweep for corpus-globbing/count-pinned tests before adding a 7th example's artifacts.
- **Entry 19** (F-329 drift guard): fail-closed on degenerate inputs (empty extraction = FAIL, never vacuous pass); committed goldens must be **byproducts of the real run**, never hand-edited; the PDF byte-identity suite is local-only/no-CI — don't claim CI enforcement it doesn't have.
- **Entry 17** (F-183 live validation): expect a first live run to surface real pre-existing defects; **pre-decide dispositions** (fix-vs-file); a verification that finds real problems is the feature working.
- **Entries 3/9/18** (deliver-stage mechanics): paths-filter + pytest-invocation lock-step; init-baseline-tree lock-step regen at deliver if placeholder-bearing docs change; KB-18 deliver preflight (branch-current + main==origin/main full-tree).
- **Entries 10/21**: endogenous success criteria as the only close gates; evidence shaped as concrete byte-anchored before/after proof, committed not narrated.
- **Memory (orchestrator context limit)**: overflow hits **Phase 5** after `threats.md`+`threats.sarif` are written; skip-Phase-5 proven workaround (F-260b T018). 32 days old — re-confirm on first run.
- **Memory (authoring tiers)**: byte-identity claims must target the deterministic regen-script path, never live-LLM reproduction.

## Codebase Analysis

All 9 PRD anchor claims verified at HEAD (`.aod/results/research-codebase.md` has exact cites):

- `scripts/generate-threats-sarif.py` (571 lines): argparse `<threats.md> <output.sarif>`; hardcoded `"uri": "examples/agentic-app/sample-report/threats.md"` **exactly at `:481`** inside `build_result()`. Bonus: `run_id_baseline` default `"2026-04-19T03-20-30"` at `:405` → `partialFingerprints.baselineRunId`.
- **DRIFT 1 — SOURCE_DATE_EPOCH**: the SARIF generators + `sarif_common.py` contain **zero timestamp calls** — deterministic **by construction**. `SOURCE_DATE_EPOCH=1700000000` is load-bearing only for Typst/PDF compiles (ADR-021). Setting it on SARIF regen is harmless uniformity, not a mechanism — spec must not claim the generator consumes it.
- `generate-risk-scores-sarif.py`: no CLI, hardcoded paths `:38-42`, `>=80`-finding gate at `:535` — confirms the out-of-scope call (7-component example cannot clear it).
- `test_backward_compatibility.py`: `BASELINE_EXAMPLES` = 6 at `:45-52` (PDF byte-identity, `@pytest.mark.slow`, **local-only — wired into no CI workflow**); F-142 gate `:375-412` asserts every finding `agentic_pattern: "none"`; mermaid-agentic-app skip carve `:389-397`. Confirms PRD's rejection of membership for a multi-agent example.
- **CI gate reality**: a new test file does NOT auto-run. `tachi-pytest.yml` runs an explicit 15-module list (`:181-197`) behind a `&hardening_paths` anchor (`:73-110`, reused by `push:[main]`); lock-step rule at header `:38-47` (ADR-039 D-6). `scripts/generate-threats-sarif.py` is currently in **no workflow's paths** — the URI enabler alone would trigger zero CI. Best regen-test precedent: `test_affected_assets_wiring.py:520-647` (importlib load of hyphenated script, function-level replication of `main()`).
- `examples/multi-tenant-rag-app/`: exactly one file (`architecture.md`, 101 lines). 8 `###` component descriptions (8th = Anthropic LLM API, external); `examples/README.md:15` row says **7** — cite "7 components (+1 external LLM service)" consistently. Cat 6 expectation embedded at `architecture.md:92`.
- `examples/agentic-app/`: committed `sample-report/threats.sarif` carries exactly **4** OI findingIds (OI-1..OI-4) via `partialFingerprints["findingId/v1"]`. **DRIFT 2 — OI row counts**: top-level `threats.md` = 8 `| OI-` rows (4 findings × 2 tables); `sample-report/threats.md` = **12** (F-260b `## Affected Assets` block adds 4). Scope any row-count cross-check to §4+§7 or name the file explicitly.
- **Anchor verified live**: `0629fa2~1` = `3f107e3`; corrected filter over the anchor SARIF returns `["OI-1","OI-2","OI-3","OI-4"]`. Anchor `threats.md` (665 lines) accessible.
- **Contract §3 doubly defective** (confirmed): (a) filter `select(.ruleId | startswith("OI-"))` matches zero — real ruleIds are `tachi/*`-style; OI ids live in `partialFingerprints["findingId/v1"]`; §6 counter-tests inherit the same defect; (b) §3 invokes `tachi.threat-model ... > /tmp/x.json` as a stdout-JSON shell binary, which it never was (file-suite into timestamped dir). The AC-1e defect Issue should document **both**.
- `tachi-output-integrity` agent: tools exactly Read/Glob/Grep (no Write/Bash); emits YAML `OI-{N}` finding blocks as text; zero-findings rule. `tachi.threat-model` command has **no scoped/single-agent flag** — single-agent run = direct Agent-tool dispatch; the comparison-SARIF seam (OQ-5/Architect M-a) is real and due at /aod.plan.

## Architecture Constraints

- **ADR-021**: epoch `1700000000` frozen; test-path only. **ADR-046 D1**: authoring-tier contract — committing a *script-generated* `threats.sarif` is a first among committed examples (intentional, "byte-identity claimed only where structural"). **ADR-039 D-6**: lock-step rule; test-tree-only decisions need no ADR. **ADR-037 D-14**: taxonomy fingerprint sidecar untouched by a new example baseline.
- **Live CI content gate**: `tachi-maestro-coverage.yml` triggers on `examples/**/threats.md`; `test_maestro_coverage_invariant.py` **globs the whole corpus** — the new committed `threats.md`, which a current pipeline run will emit with a "Risk by MAESTRO Layer" table, MUST carry all seven L1–L7 rows.
- **Run mechanics**: default output dir `docs/security/` is **gitignored** (`.gitignore:198`), as is `examples/*/test-output/` (`:210`); runs land in timestamped subfolders → plan an explicit `--output-dir` + copy-to-root step. Phase 5 opt-out exists at orchestrator level (`--skip-report` / `report: false`, orchestrator.md:795-802) — T017 fallback can use it; T026 keeps Phase 5 ON (`threat-report.md` is a required committed artifact); staged per-skill fallback exists (`/tachi.risk-score` etc.).
- **Committed layout**: two precedents — root-level (web-app, maestro-reference) vs `sample-report/` (agentic-app). README pairing contract (`examples/README.md:9`) + maestro-reference favor **root-level** for the new set.
- **No gitleaks risk**: `examples/.*` path-allowlisted (`.gitleaks.toml:51-58`). No LFS/size constraints. Canonical filenames are parser-load-bearing.
- **Populator**: `populate-affected-assets.py` must run before SARIF authoring (Phase 3.7 / command Step 2.5); an architecture without `[asset:...]` tags yields a valid all-`[]` block.
- `schemas/finding.yaml` v1.9 id regex includes the `OI-` family; SARIF results must carry `partialFingerprints["findingId/v1"]` + `properties.affected_assets`.

## Industry Research

(`.aod/results/research-web.md`, 16 sources) — confirms: SOURCE_DATE_EPOCH is the reproducible-builds standard for timestamp pinning (dict ordering stable in Python 3.7+; locale/encoding are the classic pitfalls); SARIF diffing practice favors **fingerprint-based matching** over byte-diff (partialFingerprints exist for exactly this — aligns with the corrected filter); golden-file discipline = commit baseline, regen-and-compare in CI, explicit regeneration on intentional generator change.

## Recommendations for Spec

1. **Honest SOURCE_DATE_EPOCH semantics**: keep the epoch convention for pipeline uniformity but state that SARIF regen determinism is structural (generator is timestamp-free); byte-identity claims need no env pin.
2. **US-3 framing supersession**: the feasibility check's "7th `BASELINE_EXAMPLES` entry" wording is **stale** — PRD v1.2 (Architect Option A) replaced it with a purpose-built SARIF-regen byte-identity test. Spec follows the PRD; estimate carries over.
3. **US-3 must specify CI wiring as a requirement** (not assume it): a new test executes in CI only if wired lock-step (module list + paths anchor incl. `generate-threats-sarif.py` + both example artifacts) or given a dedicated single-runner workflow (`tachi-catalog-drift.yml` pattern fits: OS-independent, sub-second). Choice of mechanism = plan decision; "the check actually gates CI" = spec requirement.
4. **Add the MAESTRO all-7-row content-shape requirement** for the new committed `threats.md` (only CI-enforced content gate that fires on it).
5. **Pin extraction semantics fail-closed**: corrected filter authoritative; non-empty guard with expected cardinality 4 pinned on the anchor side; scope any `threats.md` row cross-check to §4+§7 tables (8-row expectation holds only for the top-level file).
6. **Pre-decide dispositions** (KB-17/PRD fix-vs-file): gate failure → defect Issue + honest record; contract defect Issue documents both §3 defects (filter + non-executable invocation); risk-scores generator parameterization filed as enhancement.
7. **Pre-state recording** (KB-15): literal pytest totals for affected suites + corpus-globbing/count-pinned test sweep, committed as `specs/295-*/test-results/pre-state.md` before artifacts land.
8. **Execution constraints to carry**: serialize T017 → T026 (shared orchestrator context; no concurrent tachi runs); explicit non-gitignored output dir + copy step; committed artifacts must be run byproducts (no hand-editing); 2-attempt escape hatch files a tooling defect and closes with the staged-partial record.
9. **Component count**: use the README's "7 components" (noting the 8th `###` entry is the external Anthropic LLM API) so AC-2d stays exact.
