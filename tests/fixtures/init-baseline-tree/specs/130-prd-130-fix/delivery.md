# Delivery Document: Feature 130 — Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Delivery Date**: 2026-04-11
**Branch**: `130-prd-130-fix` (deleted post-merge)
**PR**: [#148](https://github.com/davidmatousek/tachi/pull/148) — squash commit `d35a667`

---

## What Was Delivered

- **Preflight gate with defense-in-depth** — `/tachi.security-report` now aborts at preflight with a canonical three-line install command whenever `@mermaid-js/mermaid-cli` (`mmdc`) is missing and the target project contains Critical/High attack trees. Two enforcement points: shell-level `command -v mmdc` in `.claude/commands/tachi.security-report.md` Step 1 (mirrors the existing Typst check) and Python-level `shutil.which("mmdc") → raise RuntimeError(...)` in `scripts/extract-report-data.py::render_mermaid_to_png()`. Projects without attack trees remain unaffected.
- **Mid-render failure aggregator** — When `mmdc` is present but a specific attack tree fails to render, the pipeline now raises a `RuntimeError` containing a per-finding error list (finding ID, file path, failure class of `exit:<code>`/`timeout`/`signal`, and a 200-byte stderr excerpt) instead of silently flipping `has_image=False` and continuing with a text fallback.
- **Text-fallback Typst branch deleted outright** — `templates/tachi/security-report/attack-path.typ` lines 78-86 (the `else if mermaid-text != ""` block) removed entirely. No placeholder, no comment, no "removed in 130" stub — the only render path that remains is the PNG-image branch.
- **New governing ADR** — `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` is the first tachi ADR covering CLI-prerequisite posture. Establishes the rule: "pipeline is fail-loud when a required CLI is absent, gated on input detection." Cross-references ADR-014 (optional external APIs) and ADR-021 (determinism). Future Work clause flags extraction of a reusable `install.sh` prerequisite helper once a third CLI prerequisite is added.
- **Fresh-install CI acceptance test** — new `.github/workflows/tachi-mmdc-preflight.yml` runs on `ubuntu-latest` (no mmdc preinstalled), installs Typst + Python 3.11, asserts the pipeline aborts non-zero with all three canonical tokens (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`) in stderr. Includes a team-lead T4 enforcement assertion that fails the CI job if mmdc is unexpectedly present on PATH (plan Risk #6 mitigation).
- **Hard-prerequisite documentation sync** — README gains a new `## Prerequisites` section naming `typst` + `@mermaid-js/mermaid-cli` with macOS/Linux/WSL install commands; `scripts/install.sh` gains a courtesy `command -v mmdc` warning; `docs/architecture/00_Tech_Stack/README.md` line 279 rewritten as hard prerequisite with ADR-022 cross-ref; `specs/112-attack-path-pages/spec.md` SC-004 inverted (text fallback is no longer a supported shipping mode) with audit-trail comment; `specs/112-attack-path-pages/research.md` line 80 pymmdc factual correction plus a Durable Decision Rationale block.
- **Canonical command consistency** — the install command `npm install -g @mermaid-js/mermaid-cli` appears in exactly 7 enforcement locations, verified by the T023 grep consistency check.

---

## How to See & Test

1. **Happy path (mmdc present)** — `which mmdc && SOURCE_DATE_EPOCH=1700000000 python3 -m pytest tests/scripts/test_backward_compatibility.py -v`. Expect 5/5 baselines byte-identical. Pre/post refactor output is byte-identical per ADR-021.
2. **Loud abort (mmdc absent)** — `env -i PATH="/usr/bin:/bin" /usr/bin/python3 scripts/extract-report-data.py --target-dir examples/mermaid-agentic-app/ --output-dir /tmp/test-130`. Expect exit code 1 and stderr containing `@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, and `Attack path rendering`.
3. **Preflight unit tests** — `python3 -m pytest tests/scripts/test_mmdc_preflight.py -v`. Expect 9 passed (4 preflight + 5 mid-render aggregator).
4. **Full test suite** — `python3 -m pytest tests/` (T030 gate). Expect 48/48 passed, zero skipped.
5. **Projects without attack trees are unaffected** — run `/tachi.security-report` on `examples/web-app/` (no `attack-trees/` directory) on a shell without mmdc. Expect clean completion with no mmdc check firing.
6. **CI acceptance** — watch the `tachi-mmdc-preflight.yml` workflow run on PR #148 (passed in 8s). The job asserts the loud-failure path from a clean Ubuntu runner without mmdc preinstalled.
7. **Verify ADR-022 is discoverable** — `cat docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` and confirm it is listed in `docs/architecture/README.md` ADR index.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days (PRD plan: ~4.35d, 5d target) |
| Actual Duration | ~1.5 hours wall-clock (first commit 2026-04-11 10:37 → merge 12:11) |
| Variance | Massively under — delivered in a fraction of the original estimate; autonomous wave orchestration compressed the timeline |

---

## Surprise Log

Actual << estimate. The PRD plan projected ~4.35 days of work with a 5-day target; the feature delivered end-to-end in ~1.5 hours of wall-clock time. Autonomous wave orchestration (7 waves across Setup, Foundational, US1, US2, US3, CI & Docs, Polish) compressed the timeline dramatically by running independent work streams in parallel. Trade-off: wall-clock time bought against attention available for surgical inspection of individual commits.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Governance / ADR | Silent dead-code fallbacks are invisible failure modes that mask themselves as success exit codes. Defense-in-depth enforcement at two entry points (shell preflight + Python raise) converts silent failures to loud failures while preserving backward compatibility for gated inputs. When adding a new CLI prerequisite, mirror the Typst/mmdc pattern: check at command entry AND at the function boundary, gate on input detection, and delete the fallback branch rather than leaving it as a "safety net." | KB-029 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: None

No new ideas surfaced from this retrospective. The feature was tightly scoped and all follow-up items (e.g., `install.sh` helper extraction) are already captured in ADR-022 Future Work clauses with explicit conditional triggers.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | [specs/130-prd-130-fix/spec.md](spec.md) |
| Implementation Plan | [specs/130-prd-130-fix/plan.md](plan.md) |
| Task Breakdown | [specs/130-prd-130-fix/tasks.md](tasks.md) |
| Research | [specs/130-prd-130-fix/research.md](research.md) |
| Agent Assignments | [specs/130-prd-130-fix/agent-assignments.md](agent-assignments.md) |
| Quickstart | [specs/130-prd-130-fix/quickstart.md](quickstart.md) |
| PR Description | [specs/130-prd-130-fix/PR-description.md](PR-description.md) |
| Security Scan | [specs/130-prd-130-fix/security-scan.md](security-scan.md) |
| PRD | [docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md](../../docs/product/02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md) |
| ADR-022 (governance output) | [docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 — `docs/product/02_PRD/INDEX.md` (flipped row 130 from Approved to Delivered) | OK |
| Architecture | architect | 1 — `docs/architecture/README.md` (added ADR-022 to ADR index, bumped Last Updated) | OK |
| DevOps | devops | 3 — `docs/devops/README.md` (mmdc hard-prereq section), `docs/devops/CI_CD_GUIDE.md` (workflow docs subsection), `docs/devops/01_Local/README.md` (mmdc bullet update) | OK |

Details at `.aod/results/product-manager-deliver-130.md`, `.aod/results/architect-deliver-130.md`, `.aod/results/devops-deliver-130.md`.

---

## Cleanup

- [X] Feature branch deleted (local and remote, via `gh pr merge --delete-branch`)
- [X] All tasks complete (32/32 including T030 full pytest run and T031 pre-merge constitutional checklist)
- [X] No TBD/TODO in docs (post-delivery scan clean)
- [X] Committed and pushed (PR #148 squash-merged to main, release-please will auto-cut next tachi release)
- [X] GitHub Issue closed (`stage:done`)

**Feature 130 is now officially CLOSED.**
