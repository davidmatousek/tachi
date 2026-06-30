# Research Summary: ORDERED_FRAMEWORKS Catalog-Drift CI Guard (Feature 329)

**Date**: 2026-06-30 · **Stage**: Plan / spec · **Grounding commit**: `644b532` (= Architect's PRD-review tree `644b5329`)

All load-bearing PRD claims were re-verified against the live tree by a codebase Explore pass. **No discrepancies** in substance; two cosmetic line-number drifts noted below.

## Knowledge Base Findings

- **KB Entry 15** (F-185, `INSTITUTIONAL_KNOWLEDGE.md:551`) — *the predecessor lesson*. CWE growth (53→93) was spec'd as pure-data, but `ORDERED_FRAMEWORKS` membership pulled CA-page baseline regen + test-pin sweep into consequence scope. Codified the define-time discipline: "check `ORDERED_FRAMEWORKS` membership (`extract-report-data.py:1077`) — membership ⇒ regen lane (ADR-037 D-9) enters scope." This guard makes that human checklist a CI backstop (SC-7).
- **KB Entry 13** (F-186, `:519`) — *the triggering incident*. ATLAS grew 30→36 without baseline regen, leaving the byte-identity suite silently red on `main`, discovered weeks later at F-185's plan review.
- **KB Entry 18** (F-338, `:599`) — *the dual-trigger lesson*. `/aod.update` direct-to-main bypassed the PR-gated suite; fix added `push: branches:[main]`. FR-5 reuses this exact pattern. Also: the regression can recur **at deliver** — verify branch-current + local `main`==`origin/main` before any merge/push (relevant to this feature's own closeout).

## Codebase Analysis (all verified)

| Claim | Verified | Location |
|---|---|---|
| `ORDERED_FRAMEWORKS = ("owasp","mitre-attack","mitre-atlas","nist-ai-rmf","cwe")`, module-level tuple | ✓ exact | `extract-report-data.py:1077` |
| `_load_framework_yaml_records(framework_name: str, in_scope_only: bool=False) -> list`, `@functools.lru_cache(maxsize=None)` | ✓ — **already has `in_scope_only` param** | `:1089-1138` |
| In-scope filter = `r.get("out_of_scope", False)` | ✓ | `:1132-1136` |
| `load_framework_yaml_record_counts()` (RAW) | ✓ | `:1140-1152` |
| `load_framework_yaml_in_scope_record_counts()` (IN-SCOPE) | ✓ | `:1155-1170` |
| Records are dicts carrying `id` + `out_of_scope` | ✓ | `:1135`, `:1186` |
| Byte-identity suite renders 6 PDFs via `typst compile`, byte-compares baselines, pins `SOURCE_DATE_EPOCH=1700000000` | ✓ | `test_backward_compatibility.py:43`, `:73-165`; `BASELINE_EXAMPLES` at **`:45-52`** (contract said 37-44 — file grew) |
| `test_backward_compatibility` wired into **0** workflows | ✓ (grep, 0 hits) | `.github/workflows/` |
| `regenerate-baseline.sh` regenerates the **init.sh fixture** (`tests/fixtures/init-baseline-tree/`), NOT CA baselines | ✓ — confirms HIGH-1 | `regenerate-baseline.sh:6` |
| `#329`-tagged xfail = `test_personalized_tree_bytes_match_baseline`, reason "Tracked for fixture regen under #329", `strict=False` | ✓ — **init.sh surface, scope OUT (OQ-6)** | `test_init_sh_substitution.py:54` (marker `:35`) |
| No existing sidecar / fingerprint file anywhere | ✓ (grep, 0 hits) | — (this feature creates it) |
| `pyyaml>=6` is a CI dep in both workflows + `requirements-dev.txt` | ✓ | `tachi-pytest.yml:142`, `tachi-maestro-coverage.yml:85` |

## Patterns to Follow (CI workflow — the composite)

- **`tachi-maestro-coverage.yml`** = the structural skeleton: `runs-on: ubuntu-latest` (single OS, `:67`), `permissions: contents: read` (`:60`), `pull_request:` + `paths:` filter, Python 3.11, installs `pytest pytest-timeout pyyaml`, runs target test modules. **BUT it is `pull_request`-only** (no push trigger).
- **`tachi-pytest.yml`** = the dual-trigger discipline: `&hardening_paths` YAML anchor (`:73`) reused via `*hardening_paths` on `push: branches:[main]` (`:111`) — single-source path list, no drift between PR and push legs (F-250/MED-4 lock-step).
- **FR-5 workflow = maestro skeleton (single-runner, `contents:read`, path-filter) + pytest's anchor dual-trigger (PR + push:[main]).** Single `ubuntu-latest` is load-bearing for NFR-1 (a matrix would imply platform-varying results — C4).

## Architecture Constraints

- **ADR-037** (`docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md`, Status: Accepted) — **D-9 "Eight-Baseline Scope Expansion"** (`:170`) is the intentional CA-page baseline-regen lane. Decision structure is D-1..D-13; the OQ-5 amendment adds a new D-N (or Revision-History subsection) recording count→fingerprint guard + sidecar contract + (a)-deferral rationale.
- **Regen recipe** (`specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md`) — the manual recipe FR-2 promotes to a script: per example, `SOURCE_DATE_EPOCH=1700000000` → `extract-report-data.py --target-dir examples/{name} --output templates/tachi/security-report/report-data.typ ...` → `typst compile templates/tachi/security-report/main.typ examples/{name}/security-report.pdf.baseline --root .`, run **sequentially** (shared `report-data.typ` is mutated per run), then `git checkout -- templates/tachi/security-report/report-data.typ` (no residue, D-9 invariant 5). The script emits the sidecar as its final step.
- **Determinism boundary** (ADR-021): no network, no PDF rendering in the guard or any PR-triggered job. Rendering is allowed only in the local T001 pre-state and the local regen script.

## Industry Research

- The design is the canonical **approval-testing / golden-master** pattern ([approval vs characterization tests](https://understandlegacycode.com/blog/characterization-tests-or-approval-tests/), [golden master / ApprovalTests](https://blog.markpearl.co.za/Setting-Up-The-Golden-Master)): an "approved" snapshot is regenerated by an explicit **approval script**, and drift from the approved state fails the check. The sidecar-emitted-by-regen (FR-2) *is* that approval-script mechanism — recording the approved fingerprint as a byproduct of regeneration is precisely what makes the approval cheat-resistant (you cannot advance the approved state without re-running the generator). External validation that "fingerprint a derived-from input, regenerate the approval atomically" is the correct shape, not a bespoke invention.

## Recommendations for Spec

- Key on the **fingerprint of ordered in-scope `(id, out_of_scope)` records** (FR-1), never a file-diff (FR-3) or bare count — a strict superset of the count that catches grow + constant-count ID swap/rename (HIGH-2) + `out_of_scope` flip (HIGH-3) while passing #333-class citation edits.
- Reuse `_load_framework_yaml_records` directly (it already exposes `in_scope_only`); never re-implement the YAML walk (code-economy rung 2).
- Sidecar **emitted by the formalized regen script** (cheat-resistance, Risk-1); **fail closed** on missing/partial/unparseable sidecar (FR-8, Risk-5).
- Synthetic test only; **`cache_clear()` per case** (the loader is `lru_cache` — Risk-3 false-green) (FR-7).
- Carry plan-stage gates: **OQ-1** (sidecar mechanism — Architect), **OQ-3** (T001 pre-state — Build), **OQ-6** (init.sh xfail — scope OUT / re-tag).
- Hold the determinism line: no rendering/network in the guard path; single `ubuntu-latest`; no new runtime dependency.
