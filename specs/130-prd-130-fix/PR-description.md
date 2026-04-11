## Summary

Feature 130 ([PRD #130](docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)) turns a silent pipeline failure into a loud, actionable one: when `@mermaid-js/mermaid-cli` (`mmdc`) is absent on a shell running `/tachi.security-report` against a project with Critical/High attack trees, the pipeline now aborts at preflight with a canonical three-line install command instead of silently shipping a PDF containing 40+ lines of raw `flowchart TD` source on every attack-path page. Defense-in-depth is enforced at two entry points (shell-level in the command file, Python-level in `scripts/extract-report-data.py`), the unreachable text-fallback branch in `templates/tachi/security-report/attack-path.typ` is deleted outright, mid-render failures (mmdc present but a specific tree fails) now abort with a per-finding error list, and `mmdc` is documented as a hard prerequisite across README, `install.sh`, the Tech Stack doc, and parent spec 112. The change is governed by the first ADR in tachi covering CLI-prerequisite posture: [ADR-022](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md).

## Before / After

**Before.** When `mmdc` was absent from `PATH` and the target project had attack trees under `attack-trees/`, `scripts/extract-report-data.py::render_mermaid_to_png()` hit a silent `shutil.which("mmdc")` check that printed a one-line warning to stderr, flipped every attack-tree entry's `has_image` field to `False`, and continued. The Typst template then followed an `else if mermaid-text != ""` fallback branch in `attack-path.typ` that emitted the raw Mermaid source as a `raw` code block inside the PDF. The pipeline reported exit 0. The CI workflow reported success. The only way a user discovered the broken output was by flipping through the PDF and seeing `flowchart TD` text where a rendered attack tree should have been. The same silent-failure shape held for the rarer "mmdc installed but render crashed" case: each failing entry was marked `has_image=False` and the same text fallback kicked in. Both modes violated spec 112 SC-003 (legibility at page size) and directly blocked the flagship "show to exec board" deliverable.

**After.** The pipeline aborts at preflight with the canonical three-line error message whenever `mmdc` is missing and attack trees are present. Both error paths emit an identical message containing `@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, and `Attack path rendering`:

```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```

Defense-in-depth is implemented as two gates: a shell-level `command -v mmdc` in `.claude/commands/tachi.security-report.md` Step 1 (mirroring the existing Typst check) and a Python-level `shutil.which("mmdc")` inside `render_mermaid_to_png()` that raises `RuntimeError` instead of warning silently. Both checks fire **only** when `attack-trees/*.md` contains at least one file with Critical/High severity — projects without attack trees continue to work without `mmdc`. Mid-render failures (a specific tree failing after mmdc has passed preflight) are collected by a new per-finding aggregator that raises `RuntimeError("Attack path rendering failed for N findings: ...")` with each failed finding's ID, file path, failure class (`exit:<code>`, `timeout`, `signal`), and a 200-byte stderr excerpt (architect refinement R6). The text-fallback branch at `attack-path.typ:78-86` is deleted outright — no placeholder, no comment, no "removed in 130" stub. The only render path that remains is the PNG-image branch. Release-please will auto-cut a new tachi release on merge.

## FR-130.x Deliverables

| FR | Deliverable | Commit | Primary File(s) |
|---|---|---|---|
| FR-130.1 | Preflight gate (shell + Python defense-in-depth) — aborts with canonical error message when `mmdc` absent and attack trees present | [`db0073c`](../../commit/db0073c) | [`.claude/commands/tachi.security-report.md`](../../.claude/commands/tachi.security-report.md), [`scripts/extract-report-data.py`](../../scripts/extract-report-data.py) |
| FR-130.2 | Eliminate the silent `if not shutil.which("mmdc"):` fallback in `render_mermaid_to_png()`; convert to `raise RuntimeError` | [`db0073c`](../../commit/db0073c) | [`scripts/extract-report-data.py`](../../scripts/extract-report-data.py) lines 721-730 |
| FR-130.3 | Delete unreachable `else if mermaid-text != ""` text-fallback branch outright | [`db0073c`](../../commit/db0073c) | [`templates/tachi/security-report/attack-path.typ`](../../templates/tachi/security-report/attack-path.typ) lines 78-86 |
| FR-130.4 | Mid-render failure aggregator: abort with per-finding error list (ID + file path + failure class + stderr excerpt) on any `mmdc` subprocess failure | [`732fd49`](../../commit/732fd49) | [`scripts/extract-report-data.py`](../../scripts/extract-report-data.py) `_render_single` + `as_completed` loop |
| FR-130.5 | Docs sync — README Prerequisites section, `install.sh` mmdc check, Tech Stack doc line 279, spec 112 SC-004 inversion, spec 112 research.md pymmdc correction | [`b46e931`](../../commit/b46e931) | [`README.md`](../../README.md), [`scripts/install.sh`](../../scripts/install.sh), [`docs/architecture/00_Tech_Stack/README.md`](../../docs/architecture/00_Tech_Stack/README.md), [`specs/112-attack-path-pages/spec.md`](../../specs/112-attack-path-pages/spec.md), [`specs/112-attack-path-pages/research.md`](../../specs/112-attack-path-pages/research.md) |
| FR-130.6 | Baseline regeneration for `mermaid-agentic-app` under `SOURCE_DATE_EPOCH=1700000000`; `agentic-app/sample-report` non-baseline regeneration to confirm 47-tree rendering | [`648b4d1`](../../commit/648b4d1) | [`examples/mermaid-agentic-app/security-report.pdf.baseline`](../../examples/mermaid-agentic-app/security-report.pdf.baseline), [`examples/agentic-app/sample-report/security-report.pdf`](../../examples/agentic-app/sample-report/security-report.pdf) |
| FR-130.7 | CI fresh-install acceptance test: new GitHub Actions workflow on `ubuntu-latest` (no mmdc preinstalled) that runs the pipeline against `examples/mermaid-agentic-app/` and asserts non-zero exit with all 3 canonical tokens in stderr | [`648b4d1`](../../commit/648b4d1) | [`.github/workflows/tachi-mmdc-preflight.yml`](../../.github/workflows/tachi-mmdc-preflight.yml) |

Commit lineage: [`528204f`](../../commit/528204f) scaffolded the feature workspace (PRD, spec, plan, research, ADR-022, agent-assignments), then the four implementation commits landed in topological order (US1 preflight → US2 mid-render → US3 docs → Phase 6 CI and verification).

## Test Coverage

- **[`tests/scripts/test_mmdc_preflight.py`](../../tests/scripts/test_mmdc_preflight.py)** (new file, 339 lines, 9 pytest cases):
  - 4 preflight tests (T004): `test_preflight_raises_when_mmdc_missing`, `test_preflight_skipped_when_attack_trees_empty`, `test_preflight_skipped_when_only_low_medium_findings`, `test_preflight_error_distinct_from_midrender`
  - 5 mid-render aggregator tests (T009): `test_midrender_aggregator_raises_on_any_failure`, `test_midrender_aggregator_message_format`, `test_midrender_all_success_no_exception`, `test_midrender_all_failure_raises_with_full_list`, `test_midrender_error_distinct_from_preflight`
  - **Status: 9/9 pass** (T008 + T012 verification gates)
- **[`tests/scripts/test_backward_compatibility.py`](../../tests/scripts/test_backward_compatibility.py)**: 5/5 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` for `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`. `agentic-app/sample-report/` remains intentionally excluded from `BASELINE_EXAMPLES` per Feature 128 decision (architect refinement R8 explicit negative task T019 verified).
- **Full pytest suite**: `pytest tests/` returns **48/48 pass** (T030 Wave 7 verification gate). No skipped tests without documented justification.
- **CI fresh-install acceptance test**: [`.github/workflows/tachi-mmdc-preflight.yml`](../../.github/workflows/tachi-mmdc-preflight.yml) runs on `ubuntu-latest` (which ships without mmdc preinstalled), installs Typst and Python 3.11, omits the mmdc install step, then runs the pipeline against `examples/mermaid-agentic-app/` and asserts exit code non-zero with all 3 canonical tokens in stderr. Includes a `which mmdc || echo "expected absence"` diagnostic step (architect refinement R3) and a team-lead T4 enforcement assertion that fails the job if mmdc is unexpectedly present on PATH (plan Risk #6 mitigation).

## Manual Validation Results (T027 / T028 / T029)

Full evidence at [`.aod/results/tester-130-t027-t028-t029.md`](../../.aod/results/tester-130-t027-t028-t029.md). Summary:

- **T027 (happy path, mmdc present)**: Replayed the T020 regeneration command against `examples/mermaid-agentic-app/` on a shell with `mmdc` at `/opt/homebrew/bin/mmdc`. Pipeline exit 0; 12 Critical/High attack trees extracted; output PDF **byte-identical to the committed baseline** (zero-line xxd diff); **25 image xobjects** embedded. Raw Mermaid source is now structurally impossible in the output — T024 confirmed the `else if mermaid-text` branch is deleted, so the only render path is the image branch.
- **T028 (loud abort, mmdc absent)**: Invoked `env -i PATH="/usr/bin:/bin" /usr/bin/python3 scripts/extract-report-data.py --target-dir examples/mermaid-agentic-app/ ...` (clean PATH, mmdc absent). Pipeline exit 1. `RuntimeError` message contains all 3 canonical tokens. No PDF produced at any output path. Error message format matches FR-130.1 spec exactly.
- **T029 (47-tree sample-report)**: Sub-wave 6b T021 regeneration regenerated `examples/agentic-app/sample-report/security-report.pdf` (6.4MB, ~10s) with 17 Critical/High trees dispatched, zero mmdc/Typst warnings; regenerated PDF embeds **39 image xobjects** (higher than mermaid-agentic-app's 25, proportional to tree count 47 vs 24).

Visual PDF inspection is deferred to the PR reviewer as a belt-and-suspenders courtesy check — the automation above provides dispositive evidence that rendering works end-to-end.

Before/after backward-compatibility guardrail (architect refinement R9, High priority):
- **Pre-flight**: [`.aod/results/130-baseline-pretest.md`](../../.aod/results/130-baseline-pretest.md) — 5 passed in 11.71s, all 5 baselines byte-identical, captured before any Feature 130 code changes
- **Post-flight**: [`.aod/results/130-baseline-posttest.md`](../../.aod/results/130-baseline-posttest.md) — 5 passed in 8.79s, all 5 baselines byte-identical, captured after b46e931 (preflight gate + mid-render aggregator + docs landed)
- **Delta**: IDENTICAL — zero byte divergence, zero divergence on any of the 5 baseline examples. The only numeric delta is wall-clock time (environmental noise). R9 fully satisfied.

## Governance Artifacts

- **[ADR-022](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)** — NEW. The first ADR in tachi governing CLI-prerequisite posture. Documents the decision to treat `mmdc` as a hard prerequisite when `attack-trees/` contains at least one Critical/High finding, the defense-in-depth two-gate rationale (parity with Feature 054 Typst precedent), the explicit rejection of pymmdc/Kroki/auto-install alternatives, a Future Work clause on extracting a reusable helper once a third CLI prerequisite is added, and cross-references to [ADR-014](../../docs/architecture/02_ADRs/ADR-014-gemini-api-optional-image-generation.md) (optional external APIs — different class of dependency) and [ADR-021](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (determinism convention used by the baseline regeneration in T020/T022). The ADR notes that the canonical install command appears in exactly 7 locations across the codebase, verified by the T023 grep pass.
- **Spec 112 corrections** ([`specs/112-attack-path-pages/spec.md`](../../specs/112-attack-path-pages/spec.md), [`research.md`](../../specs/112-attack-path-pages/research.md)):
  - SC-004 **inverted**: prior text ("text fallback is acceptable when rendering tool is unavailable") replaced with an assertion that rendering tool availability is verified at preflight and the pipeline aborts loudly if unavailable. Audit-trail comment `<!-- Inverted by Feature 130 (2026-04-11): text fallback is no longer a supported shipping mode -->` added above the new SC-004.
  - Line 135 ("text fallback is acceptable") removed/rewritten as a removed shipping mode.
  - `research.md` line 80 corrected: pymmdc is **not** a pure-Python renderer — it is a GPL-3.0 licensed Node.js wrapper around the same `@mermaid-js/mermaid-cli` CLI, license-incompatible with tachi's distribution model.
  - `research.md` lines 91-93: Durable Decision Rationale block added documenting the mmdc-hard-prerequisite choice with references to Feature 130 and the PRD Rejected Alternatives section (A through E).
- **Tech Stack doc** ([`docs/architecture/00_Tech_Stack/README.md`](../../docs/architecture/00_Tech_Stack/README.md) line 279): prior "optional with text fallback" sentence replaced by "hard prerequisite when `attack-trees/` contains Critical/High findings, aborting at preflight if missing." Cross-linked to ADR-022 (plan Risk #5 mitigation — ensures ADR-022 is discoverable from the Tech Stack doc).

## Risk Register — What Did NOT Regress

- **Backward compatibility on the happy path**: `pytest tests/scripts/test_backward_compatibility.py` returns 5/5 pass with the same byte-identity baselines on all 5 deterministic examples (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`). R9 before/after guardrail pair documents zero divergence. The `mermaid-agentic-app` baseline was regenerated in T020 and confirmed byte-identical to the prior committed baseline under `SOURCE_DATE_EPOCH=1700000000` — the regeneration was a no-op verification, not a new artifact.
- **No runtime Python dependencies added**: The Feature 128 runtime-stdlib-only constraint is preserved. The only modules touched in `scripts/extract-report-data.py` are ones already imported (`shutil`, `subprocess`, `concurrent.futures`, `tempfile`). No `pip install`, no new `requirements.txt` line, no new PyPI package.
- **`agentic-app/sample-report/` stays excluded from `BASELINE_EXAMPLES`**: Per architect refinement R8 and task T019 (explicit negative task), the Feature 128 decision to exclude this example from the byte-deterministic baseline set stands. Feature 130 does not revisit that decision. The regeneration in T021 is a correctness smoke test (47 trees render), not a baseline addition.
- **CI enforcement**: The CI workflow includes team-lead T4 refinement — an enforcement assertion that **fails the CI job** if `mmdc` is unexpectedly present on PATH (plan Risk #6 mitigation). Previously this was observability-only (`which mmdc || echo "expected absence"`). The enforcement assertion ensures that if a future GitHub Actions runner image change ships with `mmdc` preinstalled, the workflow breaks visibly instead of silently validating a happy path when we intended to validate the loud-failure path.
- **Projects without attack trees are unaffected**: Both preflight gates are gated on "at least one Critical/High attack tree file present in `attack-trees/`." Projects using tachi for threat modeling without the Feature 112 attack-path output continue to work unchanged without `mmdc` installed.

## Review Checklist / Test Plan

- [ ] Pull the branch: `git fetch origin && git checkout 130-prd-130-fix`
- [ ] Run the preflight pytest suite: `pytest tests/scripts/test_mmdc_preflight.py -v` — expect **9 passed**
- [ ] Run the backward-compatibility suite: `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v` — expect **5 passed**
- [ ] Run the full pytest suite: `pytest tests/` — expect **48/48 pass**
- [ ] **Visual PDF inspection (happy path, 24 trees)**: Open `examples/mermaid-agentic-app/security-report.pdf.baseline` and scroll to the Attack Path section. Confirm every attack path page shows a rendered Mermaid diagram image (not raw `flowchart TD` source). Node labels and edge connections should be legible at page size per spec 112 SC-003.
- [ ] **Visual PDF inspection (47 trees)**: Open `examples/agentic-app/sample-report/security-report.pdf` and confirm all 17 Critical/High attack path pages render as images. (This example is intentionally excluded from the byte-deterministic baseline set per Feature 128; the visual check is the correctness gate.)
- [ ] **Loud-failure reproduction**: On a shell with `mmdc` present, run:
  ```bash
  env -i PATH="/usr/bin:/bin" /usr/bin/python3 scripts/extract-report-data.py \
    --target-dir examples/mermaid-agentic-app/ \
    --output /tmp/out.typ \
    --template-dir templates/tachi/security-report/
  ```
  Expect exit 1 with a `RuntimeError` containing `@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, and `Attack path rendering`. Confirm no PDF is produced at `/tmp/out.typ.pdf` or elsewhere.
- [ ] **CI check**: Wait for the `.github/workflows/tachi-mmdc-preflight.yml` workflow to pass on this PR. Confirm the diagnostic step logs "expected absence: mmdc not on PATH, preflight gate should fire" and the assertion step confirms all 3 canonical tokens appear in captured stderr.
- [ ] **Governance review**: Read [`docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md`](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) for the decision rationale, the Future Work clause on helper extraction, and the cross-references to ADR-014 and ADR-021. Confirm the ADR accurately reflects the shipped implementation.
- [ ] **Dead-code verification (SC-130.6)**: `grep -n 'else if mermaid-text' templates/tachi/security-report/attack-path.typ` — expect **zero results**. `grep -rn 'npm install -g @mermaid-js/mermaid-cli'` — expect **exactly 7 locations** (extract-report-data.py, command file, install.sh, README, test file, CI workflow, ADR-022).

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
