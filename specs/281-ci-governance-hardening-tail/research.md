# Research Summary: CI & Governance Hardening Tail (Feature 281)

**Date**: 2026-07-01 · **Feeds**: `spec.md` · **PRD**: `docs/product/02_PRD/281-ci-governance-hardening-tail-2026-06-30.md`

Grounding for a **bundle** feature (lead #281; members #285/#286/#287) that ports F-4/F-5's local pre-commit verification into CI and documents gitleaks coverage/cadence/extensibility. All facts below verified against live `main` on 2026-07-01.

---

## Knowledge Base Findings

- **KB Entry 19 (#329 catalog-drift guard) — the 1:1 clone model for #281.** Design DNA to reuse: (1) **dual-trigger** `pull_request` + `push:[main]` — the push leg exists specifically to close the direct-to-main bypass; (2) **single `paths:` list via YAML anchor** (`&name`/`*name`) so no second list can drift; (3) `contents: read`, single `ubuntu-latest`, **direct** script invocation (no wrapper, no slash command); (4) **fail-closed everywhere** — missing/partial/unparseable inputs redden, never skip; (5) self-documenting header comment block (`tachi-catalog-drift.yml` lines 1–43 is the model). Delivered under ADR-037 **D-14**.
- **F-250 lock-step rule** (`docs/INSTITUTIONAL_KNOWLEDGE.md:128`, the "#338 lesson" cited by Architect C-3): a `paths:` filter and the runner invocation it gates are **coupled and MUST move in the same commit**; keep **ONE** YAML-anchored `paths:` list. Path-filter-only → triggers but never runs; invocation-only → runs but never triggers. Both are *silent* gaps. Generalized from F-248→F-256 (PR #257 added 5 pytest modules without wiring them into the `paths:` + invocation).
- **Path-filter under/over-triggering (F-260b lesson)**: **under-triggering is the real risk** (a governed edit slips through); **over-triggering is the SAFE direction** (a non-member edit just re-runs and passes). `/aod.deliver`'s own post-merge doc commits re-drift baselines immediately — which is exactly why the `push:[main]` leg matters.
- **F-248/F-256 CI test-gating**: the gated pytest suite is a **15-module subset** in `tachi-pytest.yml` under the `&hardening_paths` anchor. **#281 emits no SARIF and runs no pytest → it gets its OWN workflow and MUST NOT touch `&hardening_paths`.** (Precedent only.)

## Codebase Analysis (exact structural facts)

- **`.github/workflows/tachi-catalog-drift.yml`** (clone target): `on: pull_request` with `paths: &drift_paths` anchor, `push: branches:[main]` reusing `*drift_paths`; `permissions: contents: read`; `runs-on: ubuntu-latest`; `actions/checkout@v4`; direct check invocation.
- **`.github/workflows/gitleaks.yml`** (binary-provisioning stanza for FR-285.5 / C-1): `GITLEAKS_VERSION="8.30.1"`; downloads release tarball via `curl`; **SHA256 verify** `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` via `sha256sum --check`. Emits SARIF → has `security-events: write` (#281 does NOT — no SARIF).
- **`.github/workflows/tachi-pytest.yml`**: dual-trigger `pull_request` + `push:[main]` reusing a `&hardening_paths` anchor (dual-trigger precedent).
- **`.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`** (reused #280 script): exit **0**=pass, **1**=orphaned rule/table-row diff, **2**=invariant violation (missing files, jq parse error, empty awk section). Resolves root via `git rev-parse --show-toplevel` (fallback `pwd`). Deps: `jq`, `awk`, `grep`, `sed`, `diff`. Bash 3.2 compatible. → **Workflow must fail on ANY non-zero exit (1 *and* 2), not just 1.**
- **`docs/standards/CLAUDE_PERMISSIONS.md`** (doc-presence targets): actual headings are **`## 3. Settings precedence`** (cross-file/within-file deny precedence — AC-12) and **`## 4. Per-rule rationale table`** (per-rule rationale + Category-4 subdomain allowlist — AC-7). *The PRD paraphrased these; the CI grep must match the real heading text.*
- **`docs/standards/PRECOMMIT_HOOKS.md`**: `## 3. What gets scanned` (target for #285 catalog); `## 9. Adopter customization` (target for #286 template pointer). Existing `[MANUAL-ONLY]` note at §per-rule catalog (AC-10 reviewer parity).
- **`tests/fixtures/gitleaks-rule-interaction/run.sh`**: **16 fixtures** (6 should-fire, 10 should-nofire across 3 allowlist types); reports `X passed, Y failed (16 total)`; invokes `gitleaks dir … --config=… --report-format=json`; **hard-fails without `gitleaks` on PATH** (`command -v gitleaks || ERROR`).
- **`.gitleaks.toml`**: `[extend] useDefault = true`; 2 custom warn-only rules + 3 allowlists.
- **`.pre-commit-config.yaml`**: gitleaks `rev: v8.30.1` (comment: `autoupdate --freeze` → pinned SHA).

## Architecture Constraints

- **ADR-041 (Claude permissions baseline, Accepted)**: four-category `.claude/settings.json` + self-contained `CLAUDE_PERMISSIONS.md` policy log, cross-checked 1:1 by the AC-2 script. **AC-7 (subdomain probe) and AC-12 (cross-file deny precedence) are `[MANUAL-ONLY]`** — need an interactive Claude Code session; #281 degrades them in CI to a **doc-presence check of §3/§4** (Architect endorses this as "the right altitude").
- **ADR-042 (pre-commit secret-scanning, Accepted)**: gitleaks v8.30.1 via pre-commit + local wrapper + CI-parity back-stop; 16-fixture rule-interaction test.
  - **Decision Item 6 = the pin-bump cadence #287 formalizes**: `rev` starts as a tag → pinned SHA via `pre-commit autoupdate --freeze`; **bump on each MINOR release with empirical 16-fixture re-test BEFORE merge**; PATCH opportunistic on CVE/regression; MAJOR triggers ADR re-eval (the v8.25.0 `[allowlist]`→`[[allowlists]]` schema break is what the fixture re-test guards). The folklore already lives in-comment at `.pre-commit-config.yaml:31`; #287 promotes it to a canonical referenceable surface.
  - **Alternatives (ground #286's tool-swap doc)**: **trufflehog** rejected on allow-list ergonomics (Go verifiers vs. gitleaks TOML) — note the ADR's own correction that trufflehog v3 runtime is Go (runtime does NOT differentiate; the axis is allow-list ergonomics). **detect-secrets** rejected on smaller ruleset (~30 vs ~150+) + `.secrets.baseline` drift model + Python cold-start.

## Industry Research

- **Least-privilege `permissions:`**: `contents: read` only is GitHub's recommended default for read-only assertion workflows (GitHub *Secure use reference*). Confirms FR-281.5 / NFR-3.
- **`paths:` filtering**: standard way to zero-cost unrelated commits. Gotchas: **tag pushes bypass path filters** (N/A here — #281 triggers only on `pull_request` + `push:[main]`, not tags); PR uses 3-dot / push uses 2-dot diffs; 300-file cap.
- **`actions/checkout` pinning**: web best-practice now favors **SHA-pinning** (post-2025 supply-chain enforcement; `@v4` tags are force-pushable — tj-actions/changed-files compromise, Mar 2025). **Decision**: match the repo's established `@v4` convention (all 7 workflows use it) for consistency + reuse (NFR-4); a repo-wide SHA-pin migration is a **separate supply-chain decision, out of scope for #281** (recorded as an assumption).
- **gitleaks `useDefault = true`**: inherits ~150+ embedded default rules; named IDs exist (`aws-access-token`, GitHub-PAT, PEM/private-key, generic) but **specific names vary by version** and **upstream gives no immutable-ID guarantee** → the #285 catalog must be **empirically derived** (run gitleaks against fixtures, read actual hit rule IDs), and #287 must **re-derive** on each bump (validates R-2).

## Recommendations for Spec

1. Preserve the PRD's namespaced FR IDs (`FR-281.x` / `FR-285.x` / `FR-286.x` / `FR-287.x`) for 1:1 traceability.
2. Prioritize: **US-1 (#281) = P1**, **US-4 (#287) = P2** (both load-bearing hardening core, SC-1/SC-4); **US-2 (#285) = P3**, **US-3 (#286) = P3** (enhancement, split-valve candidates).
3. Make the doc-presence AC grep the **actual** headings (`## 3. Settings precedence`, `## 4. Per-rule rationale table`).
4. State the workflow fails on **any non-zero** AC-2-script exit (1 and 2).
5. Mark AC-7/AC-12 full behavioral verification `[MANUAL-ONLY]`; CI covers only doc-presence.
6. Bind #285-catalog **rule-ID re-derivation** into #287's cadence checklist (Architect A-1).
7. Keep OQ-1 (AC-7 ANOMALY compaction) OUT (sibling issue) and OQ-2 (scheduled release-detector, FR-287.3) OPTIONAL/split-valve; confirm #285/#286 carve at `/aod.tasks` (3.0-d ceiling trip-wire).
8. `tachi-permissions-verify.yml` / `name: tachi permissions-verify`; own workflow; must not touch `&hardening_paths`.
