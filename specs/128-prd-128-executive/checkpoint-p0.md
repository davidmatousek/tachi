---
feature: 128-prd-128-executive
checkpoint: P0 (pre-Wave-3)
waves_reviewed:
  - Wave 1 (Phase 0): T0a-T0h test infrastructure bootstrap
  - Wave 2 (Phase 1 + Phase 2): T001-T003e baselines, T004 schema enumeration
reviewer: architect
date: 2026-04-09
status: APPROVED_WITH_CONCERNS
go_no_go: GO (proceed to Wave 3)
concerns_raised: 3
blocking: 0
---

# F-128 P0 Checkpoint Review

## 1. One-Line Summary

**STATUS: APPROVED_WITH_CONCERNS** — Wave 1 + Wave 2 deliverables are materially
complete and correct. Two documentation inconsistencies and one Makefile
portability issue are raised as non-blocking concerns. Wave 3 is cleared to
start; concerns should be resolved in-flight or as a pre-US-1-merge cleanup.

## 2. Files Verified (Checklist)

| # | File | Expected State | Actual | Verdict |
|---|---|---|---|---|
| 1 | `specs/128-prd-128-executive/tasks.md` L38-83 | T0a-T0h + T001-T003e + T004 all `[X]` | All `[X]` (L45-52, L62-68, L80) | PASS |
| 2 | `tests/conftest.py` | Shim uses `spec_from_file_location` + `module_from_spec` + `spec.loader.exec_module(module)` | All three steps present (L58, L64, L65), single `_load_hyphenated_script` helper | PASS |
| 3 | `tests/scripts/test_smoke.py` | Smoke test uses fixture to load `extract-infographic-data.py` | `test_extract_infographic_data_module_loads` consumes fixture, asserts non-None + `hasattr(__file__)` | PASS |
| 4 | `pyproject.toml` | `[tool.pytest.ini_options]` with `testpaths = ["tests"]` | Present with `testpaths`, `python_files`, `python_functions`, `addopts = "-ra --strict-markers"` | PASS |
| 5 | `requirements-dev.txt` | `pytest>=8.0`, `pytest-cov>=4.1` | Both present with install-command header | PASS |
| 6 | `Makefile` | `test:` target with `pytest tests/scripts/ --cov=scripts --cov-report=term-missing` | Target present; invocation uses bare `pytest` not `python3 -m pytest` (see Concern C-2) | PASS (with concern) |
| 7 | `make test` run | Exit 0, smoke test passes | See G0 section below | PASS-via-alt-invocation |
| 8 | `specs/128-prd-128-executive/decisions.md` | Decisions 1, 2, 3 present | All 3 present with full rationale; Decision 1 storage path block has a documentation bug (see Concern C-1) | PASS (with concern) |
| 9 | 5 `.baseline` PDFs | Exist, non-zero size | All 5 exist at `examples/{name}/security-report.pdf.baseline` (root, not sample-report/); 1.16-1.28 MB each; matches sizes from wave-2-baselines.md resolution block | PASS |
| 10 | `schemas/infographic.yaml` | New `templates:` section with executive-architecture entry, 6 sections, alias `exec`, visual_directives | Present at L133-222; all 6 sections enumerated; `alias: exec`; portrait orientation; pastel layer fills; red dashed callouts; typography block | PASS |
| 11 | `.aod/results/wave-2-baselines.md` | Escalation + resolution report | Present with full escalation, SOURCE_DATE_EPOCH diagnosis, verified fix, and Resolution section documenting T003c passing | PASS |

## 3. G0 Gate: `make test` Verification

**Stated requirement**: `make test` exits 0 and smoke test passes.

**Observed behavior**:

- `make test` (raw, as specified in tasks.md T0g): **exit 2**
  ```
  make: pytest: No such file or directory
  make: *** [test] Error 1
  ```
  The Makefile target invokes bare `pytest`, which is not on this machine's PATH.
  `which pytest` returns "pytest not found".

- `python3 -m pytest tests/scripts/ --cov=scripts --cov-report=term-missing`
  (equivalent invocation through the Python launcher): **exit 0**
  ```
  collected 1 item
  tests/scripts/test_smoke.py .                                            [100%]
  1 passed in 0.14s
  ```
  Smoke test passes cleanly. Coverage report emitted (8% for
  extract-infographic-data.py, expected — Wave 3 adds the real coverage).

**Interpretation**:

- The pytest shim and conftest work correctly. The smoke test PASSES when pytest
  is invoked via its canonical entry point.
- The Makefile target as authored in T0e is **not portable** on a user-scheme
  install where pytest is not on PATH but is reachable through
  `python3 -m pytest`. On my machine, `pytest` is installed under
  `~/Library/Python/3.9/lib/python/site-packages/` but no shim is on PATH.
- This is a documentation/packaging issue, not a testing infrastructure failure.
  The tests themselves run and pass. See Concern C-2.

**G0 Verdict**: **PASS via alt-invocation.** The infrastructure is functionally
sound. The Makefile portability issue is Concern C-2 and should be fixed as part
of Wave 3 cleanup or as an explicit `sys.executable`-based wrapper. It is not
a blocker for Wave 3 because Wave 3 will invoke the tests directly (the authors
writing T006 will run them locally one way or another), and the CI integration
can set the path appropriately.

## 4. G1 Gate: Baseline PDF Existence and Non-Zero Size

**Stated requirement**: All 5 `.baseline` files exist, non-zero size.

**Observed**:

| Example | Path | Size (bytes) | Present |
|---|---|---|---|
| web-app | `examples/web-app/security-report.pdf.baseline` | 1,190,256 | YES |
| microservices | `examples/microservices/security-report.pdf.baseline` | 1,224,854 | YES |
| ascii-web-api | `examples/ascii-web-api/security-report.pdf.baseline` | 1,160,602 | YES |
| mermaid-agentic-app | `examples/mermaid-agentic-app/security-report.pdf.baseline` | 1,281,622 | YES |
| free-text-microservice | `examples/free-text-microservice/security-report.pdf.baseline` | 1,185,200 | YES |

**Checksum cross-reference**: Sizes exactly match the values recorded in
`wave-2-baselines.md` Resolution section (lines 203-205), which reports the
post-SOURCE_DATE_EPOCH byte-deterministic values. Confidence is high that these
are the same files that passed the T003c determinism gate.

**Path anomaly**: The baselines live at the example **root**
(`examples/{name}/security-report.pdf.baseline`), not at
`examples/{name}/sample-report/security-report.pdf.baseline` as T003b, T003d,
and `decisions.md` Decision 1 "Storage path" block all state. The wave-2-baselines.md
escalation report correctly notes at line 30: "No `sample-report/` subdirectory
exists for these 5 (only `agentic-app` has one), confirming the orchestrator's
adjusted scope is correct." So the actual placement is factually correct — the
5 unmodified examples only have `threats.md` at their root — but tasks.md and
decisions.md were never updated to reflect this reality. See Concern C-1.

**G1 Verdict**: **PASS.** Files exist, are non-zero, and match the deterministic
sizes from the resolved T003c verification. The path mismatch between docs
and reality is Concern C-1.

## 5. G2 Gate: Schema Enumeration Correctness

**Stated requirement**: `schemas/infographic.yaml` contains a top-level
`templates:` section with an `executive-architecture` entry including name,
alias (`exec`), six required sections, and a `visual_directives` block.

**Observed at `schemas/infographic.yaml` L133-222**:

- `templates:` top-level key present (L142), with explanatory comment noting
  F-128 additive scope
- Entry at L143: `name: executive-architecture`, `alias: exec` (L144)
- `purpose` and `positioning_in_pdf` fields — not required by the gate but
  valuable for downstream consumers
- `output_artifacts.spec_file: threat-executive-architecture-spec.md`
- `output_artifacts.image_file: threat-executive-architecture.jpg`
- `required_sections` list (L161-193) with all 6 sections:
  1. **Metadata** — template name, tier source, timestamp, qualifying count, skip flag
  2. **Architecture Layers** — ordered layer list with components/counts
  3. **Threat Callouts** — one callout per layer with finding ID, severity, description, composite score
  4. **Severity Distribution** — Critical/High counts only
  5. **Visual Layout Directives** — portrait, layer order, pastel fills, red callouts, typography
  6. **Gemini Prompt Construction Notes** — guidance on layered diagram + callout rewrite to ≤25 words
  All 6 marked `required: true`.
- `visual_directives` block (L194-222) with:
  - `orientation: portrait`
  - `page_aspect_ratio: "8.5:11"`
  - `layer_visualization`: horizontal_bands, pastel_per_layer fill, thin_solid border, left_aligned labels
  - `callout_visualization`: red_dashed_2pt border, warning_triangle icon, white_with_alpha fill, leader_line_or_anchor connection, text_max_words 25, plain_english_no_jargon style
  - `color_palette`: critical `#DC2626`, high `#F97316`, 5 pastel layer fills
  - `typography`: title_size large, callout_text_size medium, layer_label_size medium_bold, intent readable_for_projection_or_print

**G2 Verdict**: **PASS.** All stated requirements met plus valuable extras.
See Concern C-3 about the additive-only enumeration scope.

## 6. L-1 Tracking: Component Name Normalization on Critical Path

**Original L-1 observation (from plan review)**: Component name matching between
trust zone definitions and finding `affected_component` fields is at risk of
case and whitespace inconsistencies. Required a documented normalization helper
plus tests covering the mixed-case and orphaned-finding cases.

**Wave 3 coverage** (verified in tasks.md, not yet implemented — correct for P0):

- **T005 fixtures** (L94): Creates `mixed_case_components/threats.md` (fixture 5)
  and `orphaned_finding/threats.md` (fixture 6) specifically for L-1 coverage.
- **T006 tests** (L105-106): Two dedicated tests:
  - `test_executive_architecture_orphaned_finding_dropped` — asserts orphaned
    finding is filtered out (dedicated to L-1).
  - `test_executive_architecture_component_name_normalization` — asserts
    mixed-case finding matches layer after normalization (dedicated to L-1).
  Both tests are annotated "(architect L-1 observation)" in the task text.
- **T009 implementation** (L115-116): Two helper functions:
  - `_normalize_component_name(name)` — lowercased, trimmed, punctuation-stripped
    normalization (annotated "to address architect observation L-1").
  - `_select_critical_high_callouts(findings, layers)` — matches findings to
    layers via normalized names, drops orphans.

**L-1 Status**: **Still on the critical path.** Wave 3 has not started, so no
implementation exists yet — this is expected and correct for P0. The test
fixtures, test cases, and implementation helpers are all explicit in the task
list and will be caught by the T007 test-first gate (all 12 US-1 tests must
FAIL before T008 implementation begins).

**No action required at P0.** L-1 will be re-verified at the next Architect
checkpoint (post-Wave-3, post-T012), where `make test` must show
`test_executive_architecture_orphaned_finding_dropped` and
`test_executive_architecture_component_name_normalization` both passing.

## 7. L-2 Status: Baseline Storage Decision

**Original L-2 observation (from plan review)**: The plan referenced comparing
post-F-128 PDFs against pre-F-128 PDFs without specifying how baselines would be
stored, generated, or versioned. Risk of non-reproducible test artifacts.

**Wave 2 resolution**:

- `decisions.md` Decision 1 "Baseline PDF Storage Approach" records the three
  options considered (commit `.baseline` files, CI regeneration from parent,
  git-stash/worktree at test time) and explicitly chooses option (a): **commit
  `.baseline` files alongside each example**. Rationale covers repeatability,
  self-containment, traceability, storage cost (~1.5 MB), and determinism
  prerequisite.
- Decision 1 is dated 2026-04-09, status "Approved", and referenced from both
  the L-2 original observation (via the "architect L-2 observation" phrase)
  and from the T024 backward-compatibility test consumer.
- The chosen approach matches what my original L-2 review asked for: a concrete,
  documented storage strategy that the backward-compat test can consume
  deterministically without git-history dependencies.

**Matches original observation**: **YES.** The decision is faithful to the
L-2 observation and resolves it cleanly.

**Caveat**: The Decision 1 "Storage path" block (decisions.md L36-42) lists the
5 paths as `examples/{name}/sample-report/security-report.pdf.baseline`, which
is wrong for these 5 examples (they don't have a sample-report/ subdirectory).
The actual placement at `examples/{name}/security-report.pdf.baseline` is
correct per reality, and the wave-2-baselines.md escalation report documents
this clearly. The inconsistency is in decisions.md Decision 1 and in tasks.md
T003b/T003d — both still reference the non-existent sample-report/ subpath.
See Concern C-1.

**L-2 Verdict**: **Resolved at the substantive level.** The storage strategy is
the right one, the files exist, determinism is verified. Only the documentation
path strings need correction.

## 8. SOURCE_DATE_EPOCH Decision (Decision 3): Endorse or Dissent

**What was decided**: Set `SOURCE_DATE_EPOCH=1700000000` before every `typst
compile` invocation used for baseline generation or for the T024
backward-compatibility test. Leave normal user invocations unchanged. Recorded
in `decisions.md` Decision 3.

**Why the orchestrator authorized this without formal architect escalation**
(per the task instructions to me): the SOURCE_DATE_EPOCH environment variable
is a standard reproducible-builds.org mechanism honored natively by Typst.
It is not a source code change. It does not weaken backward compatibility. The
orchestrator judged it a low-risk procedural fix and proceeded.

**My assessment**:

- **Technical correctness**: SOURCE_DATE_EPOCH is the industry-standard
  reproducible-builds env var (reproducible-builds.org/docs/source-date-epoch/),
  honored by gcc, cargo, setuptools, Debian's dpkg, and — as verified in the
  wave-2-baselines escalation — by Typst for PDF `/ModDate`, `/CreationDate`,
  XMP metadata timestamps, and `xmpMM:InstanceID` (the last being derived from
  the timestamp). The devops agent verified byte-determinism on all 5 examples.
  The fix is technically sound.

- **Scope discipline**: The env var is applied **only** in the baseline
  generation path and the T024 test path. Normal users running
  `/tachi.security-report` continue to get real wall-clock timestamps in their
  PDF metadata, which is the correct behavior for real-world reports (auditors
  and readers expect real timestamps). This is exactly the right scope — we're
  not changing production behavior, we're pinning test-time inputs so a
  byte-level cmp can work.

- **No source code changes**: Decision 3 correctly refuses Option (b)
  ("modify scripts or main.typ to strip/normalize PDF metadata post-compile")
  and Option (c) ("fuzzy comparison"). Both would either weaken the test's
  backward-compatibility guarantee or add code surface that could mask future
  regressions. Option (a) was the right call.

- **No weakening of backward compatibility**: The test still uses `cmp` for
  exact byte comparison. The env var only removes the one source of
  non-determinism that was unrelated to tachi's actual output content. Any
  actual content regression in a future PR — Typst layout change, font subset
  drift, template bug, extraction bug — will still produce a `cmp` failure.
  The test's signal is preserved.

- **Escalation discipline**: The orchestrator did honor the "escalate on
  determinism failure" rule by having the devops agent stop and write the
  wave-2-baselines.md escalation report rather than unilaterally applying
  the fix. The orchestrator then authorized the fix without further architect
  consultation because it did not change source code or touch the
  backward-compatibility guarantee. Given that escalation-report plus the
  technical analysis I just reviewed, **I would have made the same call**.
  Formal architect consultation at escalation time would have delayed Wave 2
  without changing the decision.

**Verdict**: **ENDORSE Decision 3.** The fix is correct, minimally invasive,
scoped only to test/baseline paths, and preserves the signal of the backward
compatibility test. I would not have chosen differently.

**One small addition I'd like to see** (non-blocking, tracked as C-2b below):
The `SOURCE_DATE_EPOCH=1700000000` value should be documented somewhere the
T024 test author can find it without reading wave-2-baselines.md — ideally in
a constant in `tests/scripts/conftest.py` or in a dedicated
`tests/scripts/baseline_config.py`. This is a forward-looking concern for
Wave 4 when T024 gets authored, not a P0 blocker.

## 9. Concerns Raised (3 total, 0 blocking)

### C-1 (non-blocking, documentation only): Baseline path docstrings inconsistent with reality

**Observation**: The actual committed baseline files live at
`examples/{name}/security-report.pdf.baseline` (example directory root),
because the 5 unmodified examples do not have a `sample-report/` subdirectory.
Only `agentic-app/` has one. This is confirmed by `ls` and by
wave-2-baselines.md line 30.

**However**, three documents still describe the storage path as
`examples/{name}/sample-report/security-report.pdf.baseline`:

1. `specs/128-prd-128-executive/decisions.md` Decision 1, "Storage path" block
   (L36-42) lists all 5 paths with the `sample-report/` segment.
2. `specs/128-prd-128-executive/tasks.md` T003b (L65) says "run
   `/tachi.security-report --target-dir examples/{name}/sample-report/`".
3. `specs/128-prd-128-executive/tasks.md` T003d (L67) says "recommended path:
   `examples/{name}/sample-report/security-report.pdf.baseline`".

**Risk**: Low. The files are correctly placed; only the docs drift. But the
T024 test author will read these docs when writing the backward-compatibility
comparison code, and will spend 15-30 minutes debugging path-not-found errors
before checking the actual filesystem. It will also make the PR review
confusing.

**Recommended fix** (can be done in Wave 3 or as a standalone cleanup commit):
Update decisions.md Decision 1 Storage path block and tasks.md T003b/T003d to
use `examples/{name}/security-report.pdf.baseline` (no sample-report/ segment
for these 5 examples). Add a one-line note in decisions.md explaining the
reason: "These 5 examples do not have a sample-report/ subdirectory; only
agentic-app does."

**Severity**: non-blocking documentation inconsistency. Does not affect Wave 3
execution (Wave 3 does not touch these baselines). Will affect Wave 4 (T024).

### C-2 (non-blocking, portability): Makefile `test` target not portable to user-scheme pip installs

**Observation**: The `Makefile` `test:` target invokes `pytest` as a bare
command. On my machine, pytest 8.4.2 is installed via user-scheme pip at
`~/Library/Python/3.9/lib/python/site-packages/` but no `pytest` launcher shim
is on PATH. `which pytest` returns "pytest not found" and `make test` fails
with exit 2: `make: pytest: No such file or directory`.

The smoke test itself **passes** when invoked via
`python3 -m pytest tests/scripts/ --cov=scripts --cov-report=term-missing`
(exit 0, 1 test passed in 0.14s with coverage report). So the harness is
functionally correct; only the Makefile invocation is not portable.

**Contributing factor**: T0d recommends `pip install -r requirements-dev.txt`
in the requirements-dev.txt header comment, but does not specify whether to
use a venv, `--user`, or an unscoped install. On a macOS system where the
system Python ships with SIP, a user-scheme install is the path of least
resistance — but it often does not add pytest to the user PATH.

**Risk**: Medium for developer onboarding. Any developer who runs
`pip install --user -r requirements-dev.txt` (or who is inside a Python
environment manager like asdf or pyenv with user-scheme packages) will hit
the same "pytest: No such file or directory" error.

**Recommended fix** (one-line Makefile change, no code impact):
Change the `test:` target in Makefile line 36 from:
```
@pytest tests/scripts/ --cov=scripts --cov-report=term-missing
```
to:
```
@python3 -m pytest tests/scripts/ --cov=scripts --cov-report=term-missing
```

`python3 -m pytest` is the canonical invocation documented in pytest's own
Getting Started guide and works whether pytest is installed in a venv, as
`--user`, or globally. It adds zero behavior change when pytest IS on PATH.

**C-2b (sub-concern, forward-looking)**: Consider adding a
`SOURCE_DATE_EPOCH` constant to `tests/scripts/conftest.py` or a dedicated
`tests/scripts/baseline_config.py` so T024 can import the value rather than
hardcoding `1700000000` directly. Future-proofs the baseline regeneration
workflow.

**Severity**: non-blocking. G0 gate passes via the alt invocation. A Wave 3
cleanup touch-up.

### C-3 (non-blocking, scope observation): `templates:` enumeration is F-128-only; 5 pre-existing templates are not enumerated

**Observation**: The new `templates:` section in `schemas/infographic.yaml`
(L133-222) explicitly states in its header comment (L134-141):

> Templates above executive-architecture (baseball-card, system-architecture,
> risk-funnel, maestro-stack, maestro-heatmap) are omitted here because they
> predate this enumeration; future schema cleanup may add them for parity.

**Risk**: Low.

- The executive-architecture enumeration is complete and correct for F-128's
  immediate needs.
- The schema file continues to work for the 5 pre-existing templates because
  they use the original `required_sections` block at L43-102, which is
  unchanged.
- No backward-compatibility break — existing validators that ignored the new
  `templates:` key still work; new validators that consume it only see the
  new template.

**However**, a new contributor reading schemas/infographic.yaml for the first
time will be confused by the apparent asymmetry: "Why is only one template
enumerated in the new section?" The comment at L134-141 answers this, but
this kind of partial enumeration is a common code smell that invites future
inconsistency.

**Recommended fix** (not required for F-128, but worth filing): Create a
follow-up task in the backlog — "Enumerate all 6 infographic templates under
the F-128 `templates:` section for parity" — so that the next developer who
touches this file can finish the normalization pass. This is NOT something
to add to F-128 scope, because it would expand the feature beyond its PRD
boundaries and require test fixture parity work for all 5 pre-existing
templates.

**Severity**: non-blocking technical debt observation. Does not affect Wave 3.
Acceptable as-is for F-128. Recommend backlog creation post-F-128 delivery.

## 10. Go/No-Go Call for Wave 3

### Green (ready to proceed)

- Pytest infrastructure bootstrapped and functionally correct (importlib shim
  uses all three required steps; smoke test passes via alt-invocation).
- `pyproject.toml`, `requirements-dev.txt`, `Makefile`, `conftest.py`,
  `test_smoke.py` all present and readable.
- 5 `.baseline` files exist on disk, non-zero size, matching post-T003c
  byte-deterministic sizes.
- `decisions.md` records all 3 decisions (storage, regeneration target,
  SOURCE_DATE_EPOCH) with rationale.
- SOURCE_DATE_EPOCH decision is technically correct and I endorse it.
- `schemas/infographic.yaml` executive-architecture enumeration is complete
  with all 6 sections, alias, and visual_directives block.
- L-1 (component name normalization) still on critical path for Wave 3 via
  T005 fixtures, T006 tests, and T009 implementation helpers.
- L-2 (baseline storage) substantively resolved and correct in the filesystem.

### Yellow (non-blocking concerns to fix in-flight)

- **C-1**: Fix the path strings in decisions.md Decision 1 and tasks.md
  T003b/T003d to match the actual filesystem layout (drop `sample-report/`
  from the 5 non-agentic-app paths). 10-minute fix. Do it before Wave 4 starts
  so T024 test author reads correct docs.
- **C-2**: Change Makefile `test:` target to `python3 -m pytest …` for
  portability. 1-line fix. Do it opportunistically in any Wave 3 commit that
  touches Makefile, or as a standalone cleanup commit at the end of Wave 3.
- **C-3**: File backlog item for "enumerate all infographic templates for
  schema parity" as post-F-128 tech debt. Do NOT expand F-128 scope.

### Red (blockers)

- **None.**

### Decision

**GO for Wave 3.** The P0 checkpoint is APPROVED_WITH_CONCERNS. The concerns
are documentation and portability issues that do not affect Wave 3's execution
(Wave 3 creates fixtures, writes tests, implements helpers — none of which
depend on the specific `.baseline` path strings or on the bare-`pytest`
Makefile invocation). Wave 3 may start immediately.

The concerns should be tracked and resolved either (a) in-flight during Wave 3,
or (b) as a pre-Wave-4 cleanup commit, or (c) in the final F-128 cleanup pass.
They are **not** reasons to block Wave 3 start.

---

**Reviewer signature**: architect
**Date**: 2026-04-09
**Go/No-Go**: **GO**
**Next checkpoint**: Post-Wave-3 (after T012), which will verify all 12 US-1
tests pass, L-1 coverage is exercised, and the dispatch branch emits correct
JSON for the `executive-architecture` template.
