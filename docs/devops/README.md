# DevOps Documentation - {{PROJECT_NAME}}

**Last Updated**: {{CURRENT_DATE}}
**Owner**: DevOps Agent
**Status**: Template

---

## Overview

This directory contains deployment and infrastructure documentation for {{PROJECT_NAME}}.

---

## Structure

### 01_Local/
Local development environment setup
- Docker Compose configuration
- Development database setup
- Environment variables
- Troubleshooting

### 02_Staging/
Staging environment documentation
- Staging infrastructure
- Deployment procedures
- Testing workflows
- Access credentials

### 03_Production/
Production environment documentation
- Production infrastructure
- Deployment procedures
- Monitoring and alerts
- Incident response
- Pre-deployment checklist

### CI_CD_GUIDE.md
CI/CD setup instructions for common platforms. Also documents reference template-maintenance workflows (manifest-coverage, extract-coverage, stack-contract) and the BATS test harness — patterns you can adopt if you extend the upstream template.

---

## Quality Gates (CI) — Reference Patterns

The patterns below describe CI that the upstream template uses to protect its own release-tooling integrity. **They do not ship to adopter projects** — adopt them only if you extend the template or want the same guarantees in your own repo.

All three workflows share the same bash:3.2 Docker pattern, SHA-pinned checkout action, `contents: read` permissions, and cancel-in-progress concurrency. See `docs/devops/CI_CD_GUIDE.md` for the reusable pattern including the `apk add git` + `safe.directory` setup.

### Reference: Manifest Coverage Workflow (F129)

`.github/workflows/manifest-coverage.yml` (upstream template only) runs on every push/PR against `main` and asserts that every git-tracked file is categorized in `.aod/template-manifest.txt` — either with an explicit ownership rule or as `ignore`. This guarantees feature 129's 100% file-ownership invariant (FR-008) for all template updates.

- **Validator**: `scripts/check-manifest-coverage.sh` (bash 3.2 compatible)
- **Execution**: runs inside the `bash:3.2` Docker image so CI enforces the same shell floor that macOS workstations use (KB Entry 6)
- **Exit code 0**: every tracked file matches a manifest entry
- **Exit code 1**: uncategorized files — stderr reports `<path>:1: uncategorized (no manifest entry or ignore match)` (compiler-diagnostic format; GitHub Actions annotators parse it automatically)
- **Local equivalent**: run `scripts/check-manifest-coverage.sh` before pushing, or install the opt-in pre-commit hook documented in `CONTRIBUTING.md`

### Reference: Extract Coverage Workflow (F128)

**Added in Feature 128** (directory-based extraction manifest). `.github/workflows/extract-coverage.yml` (upstream template only) runs on every push/PR against `main` and asserts that every git-tracked file's classification in `scripts/extract-classification.txt` matches what the current `scripts/extract.sh` MANIFEST_DIRS / MANIFEST_ROOT_FILES / `.extractignore` configuration would produce. This guards Layer 4 of the 5-layer defense against private-data leak in extraction (FR-014–FR-018).

- **Validator**: `scripts/check-extract-coverage.sh` (bash 3.2 compatible)
- **Execution**: runs inside the `bash:3.2` Docker image (identical pattern to manifest-coverage)
- **Exit code 0**: snapshot matches live classification
- **Exit code 1**: snapshot missing, malformed, or diverged — stderr reports `extract-classification.txt:1: <message>: <path>` (compiler-diagnostic format)
- **Emergency override**: commit message containing `[skip extract-check]` bypasses the check for a single commit (FR-018). The workflow emits a `::warning::` annotation on skip. Guidance caps routine use at once per quarter (PM Decision).
- **Local equivalents**:
  - `make extract-check` — run the validator
  - `make extract-classify` — regenerate `scripts/extract-classification.txt` (maintainer acknowledgement step after a legitimate manifest change)

See `docs/devops/CI_CD_GUIDE.md` for both workflows' full walk-through, the reusable bash:3.2 Docker pattern, and the env-var contract.

### Reference: Stack Contract Workflow (F130)

**Added in Feature 130** (Stack Pack Test Contract), merged via PR #141 on 2026-04-21. `.github/workflows/stack-contract.yml` (upstream template only) runs on every push/PR against `main` and asserts that every `stacks/*/STACK.md` file (excluding the content-pack allowlist) contains a valid machine-readable test-contract block between the `<!-- BEGIN: aod-test-contract -->` / `<!-- END: aod-test-contract -->` sentinels. This keeps the AOD test-orchestration pipeline's stack → test-command resolution deterministic for every active app-stack pack (no heuristics, no fallbacks).

- **Validator**: `.aod/scripts/bash/stack-contract-lint.sh` (bash 3.2 compatible, runs on stock macOS `/bin/bash` 3.2.57)
- **Execution**: runs inside the `bash:3.2` Docker image (identical pattern to manifest-coverage + extract-coverage)
- **Path filter**: workflow only triggers on changes under `stacks/**/STACK.md`, `.aod/scripts/bash/stack-contract-lint.sh`, `.github/workflows/stack-contract.yml`, or `tests/fixtures/stack-contracts/**`
- **Exit codes**: `0` VALID, `1` RUNTIME_ERROR, `2` MISSING_TEST_COMMAND (or opt-out rationale too short), `3` XOR_VIOLATION (`test_command` + `e2e_opt_out` both set), `4` UNKNOWN_KEY, `5` MISSING_BLOCK. `--all` mode exits with the numerically lowest non-zero code so the first failing pack surfaces deterministically.
- **Content-pack allowlist**: packs listed in the script's `CONTENT_PACKS` array (currently `knowledge-system`) are skipped in `--all` mode; single-file mode ignores the list so maintainers can still lint content packs explicitly when transitioning them to test-bearing.
- **Local equivalents**:
  - `bash .aod/scripts/bash/stack-contract-lint.sh --all` (matches CI exactly)
  - `bash .aod/scripts/bash/stack-contract-lint.sh stacks/<pack>/STACK.md` (single-pack, fastest)

See `docs/devops/CI_CD_GUIDE.md` → "Stack Contract Workflow (F130)" for the full walkthrough, and `docs/stacks/TEST_COMMAND_CONTRACT.md` for the contract authoring guide.

---

## Deployment Policy (MANDATORY)

**ALL deployments MUST go through the devops agent.**

Before deploying to ANY environment:
1. Invoke devops agent (never run deploy commands directly)
2. DevOps reads: `docs/architecture/04_deployment_environments/{env}.md`
3. DevOps reads: `docs/devops/{01_Local|02_Staging|03_Production}/README.md`
4. DevOps outputs verification summary
5. Only then proceed with deployment

**Never deploy without verification** - Mismatched targets can cause data loss or service disruption.

---

## Environment Strategy

```
Development (Local):
  - Docker Compose for services
  - Local PostgreSQL
  - Fast iteration
  - Cost: $0

Staging ({{STAGING_PLATFORM}}):
  - Production-like configuration
  - Separate database
  - Auto-deploy on PR
  - Cost: {{STAGING_COST}}

Production ({{PRODUCTION_PLATFORM}}):
  - Auto-scaling
  - Monitoring and alerts
  - Manual promotion
  - Cost: {{PRODUCTION_COST}}
```

---

## Quick Links

- [Local Setup](01_Local/README.md)
- [Staging Deployment](02_Staging/README.md)
- [Production Deployment](03_Production/README.md)
- [CI/CD Guide](CI_CD_GUIDE.md) — includes manifest-coverage + extract-coverage + stack-contract workflows, bash:3.2 Docker pattern, BATS harness, update-script env vars
- [Downstream Template Update Guide](../guides/DOWNSTREAM_UPDATE.md) — authoritative adopter walkthrough for `make update` / `/aod.update`
- [PLSK Maintainer Guide](../guides/PLSK_MAINTAINER_GUIDE.md) — authoritative walkthrough for extraction + sync-upstream (feature 128)
- [Stack Pack Test Contract Guide](../stacks/TEST_COMMAND_CONTRACT.md) — authoring guide for the `<!-- BEGIN: aod-test-contract -->` block guarded by `stack-contract.yml` (feature 130)

---

## Feature 129 Additions (2026-04-19)

The **Downstream Template Update Mechanism** (PR #131) introduced production-critical DevOps surfaces for adopters:

- **Adopter update lifecycle**: `make update` / `/aod.update` pulls upstream template releases over HTTPS with no git remote required. Version pinning lives in `.aod/aod-kit-version`. Supply-chain defences include SHA-pinned GitHub Actions, manifest SHA-256 verification, and a retag tripwire (`FORCE_RETAG=1` override).
- **Concurrency model**: update-script acquires `.aod/update.lock` via `flock` on Linux (fast path) and atomic `noclobber` on macOS (PID + 16-char hex nonce + ISO-8601 timestamp). Liveness via `kill -0`, staleness threshold at 1 hour. Default timeout ~30 s; exits code 2 on contention. See `docs/guides/DOWNSTREAM_UPDATE.md` for full contract.
- **CI-aware safety default**: when `CI` env var is set, `scripts/update.sh` defaults to `--dry-run` mode (explicit `--apply` required for writes in CI).

The upstream template itself also gained a manifest-coverage CI workflow and a BATS test harness for shell scripts. These are reference patterns (see Quality Gates section above) — they do not ship to adopters, but you can adopt them if you extend the template.

---

## Feature 128 Additions (2026-04-21)

The **Directory-Based Extraction Manifest** (PR #135) hardened the upstream template's extraction/sync pipeline. Adopters see zero runtime impact — all changes are template-maintenance infrastructure:

- **Extract Coverage CI workflow**: `.github/workflows/extract-coverage.yml` runs on every push/PR to `main` and validates that `scripts/extract-classification.txt` matches live classification. Layer 4 of the 5-layer defense against private-data leak. Emergency override `[skip extract-check]` in commit message bypasses for a single commit (FR-018).
- **New Makefile targets**: `make extract-check` (runs validator) and `make extract-classify` (regenerates the committed snapshot after a legitimate manifest change — maintainer acknowledgement step).
- **bash:3.2 Docker pattern finalization**: the three-line runtime setup (`apk add --no-cache git` + `git config --global --add safe.directory /w` + validator invocation) is now the standard pattern for all bash:3.2 CI steps. The fix landed simultaneously in both `manifest-coverage.yml` and `extract-coverage.yml` during F128 delivery when the Alpine base image surfaced the missing-git / dubious-ownership issues. Copy this pattern verbatim when adding new maintenance workflows. Documented in `docs/devops/CI_CD_GUIDE.md` → "bash:3.2 Docker Pattern".
- **Sync-upstream non-interactive flags**: `scripts/sync-upstream.sh` and `/aod.sync-upstream` now accept `--yes`, `--dry-run`, and `--strategy={main,branch,manual}` for automation. No-flags interactive default preserved (backwards-compatible, FR-024). Full contract in `specs/128-directory-based-extraction-manifest/contracts/sync-upstream-cli.md`.
- **Externalized reset templates**: `scripts/reset-templates/` now holds the `IK.md` and `PRD_INDEX.md` content-reset bodies (previously inline heredocs). Missing template → fail-loud exit 1 (Layer 5, FR-009).

These are reference patterns — they do not ship to adopters (extract-coverage workflow, reset-templates directory, and classification snapshot are all upstream-only), but you can adopt them if you extend the template.

---

## Feature 130 Additions (2026-04-21)

The **Stack Pack Test Contract** (PR #141, feature branch `130-e2e-hard-gate` squash-merged on 2026-04-21) closed a long-standing gap in the AOD test-orchestration pipeline: stack packs now declare their test entry point in a machine-readable block inside `STACK.md`, and CI enforces the contract on every PR. Adopters see zero runtime impact — all changes are template-maintenance infrastructure:

- **Stack Contract CI workflow**: `.github/workflows/stack-contract.yml` runs on every push/PR to `main` (path-filtered to contract-relevant files) and executes `bash .aod/scripts/bash/stack-contract-lint.sh --all` inside the `bash:3.2` Docker image. Blocks PRs on any non-zero exit code.
- **Stack contract linter**: `.aod/scripts/bash/stack-contract-lint.sh` is strictly bash-3.2 clean (no associative arrays, no `readarray`, no case-modification parameter expansion) so it runs on stock macOS `/bin/bash` 3.2.57. Supports single-file mode (`<path>`), repo-wide mode (`--all`), and `--help`. Exit codes 0–5 are stable forever (see CI_CD_GUIDE → "Stack Contract Workflow (F130)" for the table).
- **Local-parity guarantee**: Because both local macOS and CI run the same validator against the same shell floor, stderr output is byte-identical modulo runner path prefixes (per FR-030). Maintainers can run `bash .aod/scripts/bash/stack-contract-lint.sh --all` before pushing and get the same diagnostics CI would emit.
- **Template-manifest entries**: `.aod/template-manifest.txt` gained three new rules — `owned|docs/stacks/**`, `owned|tests/contract/**`, and `ignore|.aod/scratch/**` — to keep the manifest-coverage invariant from F129 passing against the 39 new files this feature introduced. The classification snapshot at `scripts/extract-classification.txt` was regenerated in lockstep to acknowledge the new files (F128 maintainer-acknowledgement step).
- **bash:3.2 Docker pattern reuse**: `stack-contract.yml` adopts the established three-line runtime setup (`apk add --no-cache git` + `git config --global --add safe.directory /w` + validator invocation) verbatim from `manifest-coverage.yml` / `extract-coverage.yml`. All three workflows now share the same SHA-pinned `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` — bump them together when upgrading.
- **No adopter-facing env vars, no secret changes, no deployment-environment changes**: Feature 130 is template/tooling infrastructure. Staging and Production README content was intentionally left unchanged.

These are reference patterns — they do not ship to adopters (stack-contract workflow and lint script protect the upstream template's stack-pack ecosystem), but you can adopt them if you extend the template with new app-stack packs.

---

## Feature 138 Additions (2026-04-21)

The **Playwright E2E Layer for FastAPI Stack Packs** (PR #146, feature branch `138-playwright-e2e-fastapi-stack-packs` squash-merged on 2026-04-22, merge commit `7569dc5`) shipped Playwright E2E scaffolds into both FastAPI stack packs. Unlike F128/F129/F130 which were template-maintenance only, F138 changes the adopter-facing scaffold surface:

- **Adopter-facing scaffolds**: `stacks/fastapi-react/scaffold/frontend/e2e/` and `stacks/fastapi-react-local/scaffold/frontend/e2e/` now ship a Playwright smoke test, fixtures, adopter `auth-crud.template.ts`, and `playwright.config.ts` per pack. Both packs declare `e2e_command: npm --prefix frontend run test:e2e` in their `STACK.md` (enforced by F130's stack-contract lint).
- **New adopter env vars** (only for `fastapi-react` / Postgres variant):
  - `TEST_DATABASE_URL` — required. DSN must contain `test_` or `_test` in the database name AND must not equal `DATABASE_URL`. Both invariants are enforced by the Playwright fixture at test-run time.
  - `TEST_SECRET_KEY` — optional override. Scaffold ships a test-only default so fresh scaffolds run without user configuration.
  - `BACKEND_TEST_PORT` (default `8001`) and `FRONTEND_TEST_PORT` (default `5173`) — optional overrides for port-collision cases. Both packs share these defaults.
- **Zero config for `fastapi-react-local`**: the SQLite variant creates an ephemeral `/tmp/e2e-<uuid>.db` per run — no env vars needed.
- **One-time browser install**: adopters run `npx playwright install chromium` once per workstation (~200-300 MB). Chromium-only by design (Firefox/WebKit are not bundled).
- **No new CI workflows in this template repo**: `stack-contract.yml` (F130) already validates the `e2e_command` declaration. Adopters wire the `test:e2e` script into their own CI using the snippet in `CI_CD_GUIDE.md` → "Playwright E2E in Adopter CI (FastAPI Stack Packs)".
- **Classification snapshot update**: `scripts/extract-classification.txt` regenerated for the 24 new shipped files (`SHIP` for scaffold paths, `EXCL-by-construction` for spec artifacts — F128 maintainer acknowledgement step).
- **No staging/production deployment changes**: F138 is a test-layer feature. Runtime deployment targets, secrets, and infrastructure are unchanged.

Adopter quickstart (authoritative): `specs/138-playwright-e2e-fastapi-stack-packs/quickstart.md`. Local setup reference: `docs/devops/01_Local/README.md` → "Playwright E2E (FastAPI Stack Packs) — Adopter Quickstart".

---

## Feature 139 Additions (2026-04-23)

The **Delivery Means Verified, Not Documented** feature (PR #149, feature branch `139-delivery-verified-not-documented` squash-merged on 2026-04-23, merge commit `6925ce8`) converted `/aod.deliver` from a documentation-only retrospective into a verification hard-gate with bounded auto-fix, heal-PR escalation, and deterministic halt signalling for orchestrators. The feature is adopter-facing — CI consumers that shell out to `/aod.deliver` MUST update their branch logic.

- **Additive exit codes (orchestrator contract)**: `/aod.deliver` now exits with one of three new codes **in addition to** the existing PRD 130 taxonomy (0=success, 1=runtime error, 2=missing test command, 3=XOR violation, 4=unknown key, 5=missing block). CI scripts that branched on `0..5` MUST add explicit handling for:
  - **10 — `halt-for-review`**: the verification gate tripped (failing tests survived the auto-fix loop, or AC coverage is incomplete). A heal-PR was opened or updated idempotently, and the halt record is written to `.aod/state/deliver-{NNN}.halt.json`. Orchestrators should treat this as "human review required" — not a runtime failure.
  - **11 — `lock-conflict`**: another `/aod.deliver {NNN}` invocation holds `.aod/locks/deliver-{NNN}.lock`. Retry-with-backoff is appropriate.
  - **12 — `abandoned-sentinel`**: crash-recovery detected an orphaned state sentinel from a prior run that did not exit cleanly. The operator must inspect `.aod/state/deliver-{NNN}.state.json` and resolve before re-running. Do NOT auto-clear this from CI — it is a safety rail.
- **Three-channel halt signal**: exit code 10 is emitted alongside a stdout line (`DELIVERY_HALTED: {NNN}`) and the halt-record JSON file. All three channels are co-equal by design so humans, log scrapers, and CI shells each see the signal on the channel they read. Do NOT suppress any of the three.
- **Filesystem additions under `.aod/`** (runtime state + append-only audit):
  - `.aod/audit/deliver-opt-outs.jsonl` — **append-only, checked in**. Every `--no-tests=<reason>` invocation appends one JSONL record (feature id, reason, timestamp, invoker). Intentionally version-controlled so the audit trail survives branch churn.
  - `.aod/state/deliver-{NNN}.halt.json` — **gitignored**. Halt record written whenever exit code 10 fires. Read by orchestrators to reconstruct halt context.
  - `.aod/state/deliver-{NNN}.state.json` — **gitignored**. Ephemeral per-invocation state + crash-recovery sentinel. Presence on re-run without a clean prior exit triggers exit code 12.
  - `.aod/locks/deliver-{NNN}.lock` — **gitignored**. Per-feature lockfile. Presence blocks concurrent `/aod.deliver {NNN}` invocations with exit code 11.
- **New optional config file**: `.aod/config.json` (schema version 1; see `.aod/config.json.example` + `.aod/config.json.example.md`). Absent by default — readers fall back to defaults via `jq '<path> // default'`. Two knobs control the auto-fix loop: `deliver.heal_attempts` (default `2`; set `0` to disable the loop) and `deliver.heal_max_timeout_multiplier` (default `1.5`; raise for slow CI). Full reader contract in `specs/139-delivery-verified-not-documented/contracts/config-schema.md`.
- **Flag deprecation**: `--require-tests` is a silent no-op with a stderr deprecation notice for 2 release cycles. Invocations still succeed and honour the new hard-gate behaviour (tests are now always required unless `--no-tests=<reason>` is provided). The flag is removed at release N+2. Adopter migration: `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md`.
- **AC-coverage gate**: `/aod.deliver` now binds spec acceptance criteria to automated scenarios before allowing exit 0. Legacy prose specs without AC structure migrate via `[MANUAL-ONLY]` markers — full walkthrough in `docs/guides/AC_COVERAGE_MIGRATION.md`.
- **Stack-pack contract extension**: `STACK.md` test-contract blocks optionally accept a new `test_paths` key (backwards-compatible; absence means "use stack-default paths"). No existing packs require changes.
- **Zero new runtime dependencies**: bash 3.2 clean. No new env vars, no new secrets, no new deployment targets. Orchestration design keeps the authorization path out of the LLM — the scope guard that bounds the auto-fix loop is pure bash.
- **CI impact (upstream template only)**: `.aod/template-manifest.txt` and `scripts/extract-classification.txt` were regenerated to cover the new template paths. Both quality gates (F129 manifest coverage + F128 extract coverage) stay green. No new CI workflows — the feature's gate is internal to the `/aod.deliver` skill.

**Adopter action required**: if any CI pipeline shells out to `/aod.deliver`, update the exit-code branch table:

```bash
/aod.deliver "$FEATURE" --autonomous
rc=$?
case $rc in
  0)       echo "Delivered cleanly"; continue_pipeline ;;
  10)      echo "Halted for review — heal-PR open"; notify_reviewer; exit 0 ;;   # not a failure
  11)      echo "Lock contention — retrying"; retry_with_backoff ;;
  12)      echo "Abandoned sentinel detected — operator intervention required"; page_on_call; exit 1 ;;
  1|2|3|4|5) echo "Runtime/contract failure (rc=$rc)"; exit "$rc" ;;
  *)       echo "Unknown exit code $rc"; exit "$rc" ;;
esac
```

Full adopter walkthrough: `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md`. PRD: `docs/product/02_PRD/139-delivery-verified-not-documented-2026-04-22.md`. Contracts: `specs/139-delivery-verified-not-documented/`.

---

## Feature 142 Additions (2026-04-23)

The **Remove Grace-Period Fallback from Stack Contract Lint** feature (PR #151, feature branch `142-remove-grace-period` squash-merged on 2026-04-23, merge commit `c0cf15b`) closed Feature 130's one-release migration window by removing the grace-period fallback in `/aod.deliver` Step 9a. Packs missing a `<!-- BEGIN: aod-test-contract -->` block now surface as explicit errors instead of silent skips. This is a **tightening of effective CI behavior** even though no workflow YAML changes shipped:

- **`.github/workflows/stack-contract.yml` is unchanged**. The workflow and `.aod/scripts/bash/stack-contract-lint.sh` exit-code contract (0–5) were already strict as of Feature 130 — exit code 5 (MISSING_BLOCK) has always failed CI. F142 does not alter the lint workflow, the validator, or any exit codes.
- **Effective behavior tightens inside `/aod.deliver`**: previously, a lint exit 5 for a missing contract block was translated by `/aod.deliver` Step 9a into a grace-period skip with `skip_reason: "no_contract_declared — migrate before next release"`. Post-F142, the same exit 5 is translated to `status: "error"` with the lint stderr diagnostic surfaced verbatim. The delivery report's E2E Validation Gate row now shows Error (not Skipped) for missing-block cases.
- **CI impact is indirect but real**: any pipeline that shells out to `/aod.deliver` (typically inside `/aod.run --autonomous` or a post-merge automation job) will see a different rendered delivery.md for packs with missing contract blocks. Exit codes 0/10/11/12 from `/aod.deliver` (per F139) are unchanged — the error is non-fatal per ADR-006 and does not change the delivery exit code. But the Failure Details column now contains the lint stderr instead of grace-period language, which is what downstream log scrapers and reviewers read.
- **Build-gate in this feature's plan**: the Wave-0 devops step in `specs/142-remove-grace-period/plan.md` includes a release-gate attestation (NFR-001) that verifies the release containing PR #141 has shipped to adopters before F142 can proceed. This is recorded in the delivery retrospective for auditability. Future features that close migration windows should use the same pattern.
- **No new CI workflows, no env vars, no secret changes, no deployment-environment changes**: F142 is pure cleanup. Zero adopter runtime impact at the infrastructure layer.

For adopters running custom delivery pipelines: if your pipeline parses the delivery.md rendered by `/aod.deliver`, update any grace-period-specific log-scraping patterns. The canonical fix is to read `e2e_validation.status` from the delivery payload (`error` vs. `skipped` vs. `success`) rather than pattern-matching against the human-readable rendering. PRD: `docs/product/02_PRD/142-remove-grace-period-fallback-2026-04-23.md`. Spec + contracts: `specs/142-remove-grace-period/`.

---

## Feature 132 Additions (2026-04-23)

The **Fix `scripts/update.sh` Silent Exit 5 on Uncategorized Files** feature (PR #152, feature branch `132-fix-scripts-update` squash-merged on 2026-04-23, merge commit `47d8956`) restored a visible diagnostic that Feature 129's initial implementation silently regressed. Adopters running `make update` / `/aod.update` against an upstream whose manifest does not cover every tracked file now see the `[aod] ERROR: manifest coverage violation — N upstream file(s) not categorized:` header on stderr with each uncategorized path listed, instead of an empty exit 5.

- **Adopter-facing behavior change**: `make update` exit 5 is unchanged as a code (per F129 exit-code taxonomy — `docs/devops/CI_CD_GUIDE.md` → "Update-Script Environment Variables") — what changed is that stderr now carries the diagnostic payload. A first `make update` after upgrading into a repo with an uncategorized upstream file will surface the message; this is the **restored safety net**, not a new failure mode. Adopter guide: `docs/guides/DOWNSTREAM_UPDATE.md` troubleshooting section lists exit 5 with the expected output.
- **Root cause (for future maintainers)**: a command substitution captured `aod_template_category_for_path` under `set -euo pipefail`. When the helper returned rc=5 (uncategorized) or rc=1 (malformed manifest), errexit aborted the script before `local cat_rc=$?` could capture the return value, skipping both the rc=5 collector emission and the defensive `elif [ "$cat_rc" != "0" ]` branch. The fix uses explicit `set +e` / `set -e` bracketing around the helper call (the `|| true` form was rejected because on bash 3.2, `local cat_rc=$?` after `<cmd> || true` captures `true`'s exit code, not the helper's — silently removing the defensive branch).
- **Regression guard**: `tests/integration/132-coverage-violation-output.bats` adds 2 BATS test cases that exercise both the rc=5 coverage-violation path and the rc=1 helper-error path. Each test constructs its own self-contained bare upstream git repo in `$BATS_TEST_TMPDIR` — the fixtures are independent of the live `.aod/template-manifest.txt` and survive future 100%-coverage states. Run locally with `bats tests/integration/132-coverage-violation-output.bats`.
- **No CI workflow changes**: the bash:3.2 Docker pattern (F128) and BATS harness (F129) already cover the new test. `.github/workflows/manifest-coverage.yml` continues to protect the upstream template's own manifest invariant; the new regression guard protects the `scripts/update.sh` output contract against future refactors.
- **No env var changes, no secret changes, no deployment-environment changes**: F132 is a 3-line bash fix plus a 2-case regression test. Zero infrastructure impact.

**Adopter action required**: none, unless you currently log-scrape `make update` output for the empty-exit-5 pattern. If you do, update the scraper to expect `[aod] ERROR: manifest coverage violation` on stderr when exit code is 5. PRD: `docs/product/02_PRD/132-fix-update-sh-silent-exit-2026-04-23.md`. Spec + tests: `specs/132-fix-scripts-update/` and `tests/integration/132-coverage-violation-output.bats`.

---

## Feature 134 Additions (2026-04-25)

The **Downstream Update Bootstrap + Placeholder Migration** feature (PR #153, feature branch `134-update-bootstrap-placeholder-migration` squash-merged on 2026-04-25, merge commit `f09035b`) closed the pre-F129 onboarding gap by giving adopters who cloned AOD-kit before the update mechanism shipped a one-shot path to bootstrap the prerequisite files (`/.aod/aod-kit-version` + `/.aod/personalization.env`) and a drift-detection scanner for legacy placeholders. Two new CLI/automation entrypoints land at the adopter surface:

- **`make update-bootstrap` (with `YES=1` env var pass-through)**: Auto-discovers 8 of 12 canonical placeholder values from repo state, prompts for the 4 always-prompt architecture values (database, vector, auth, cloud provider), and writes both prerequisite files atomically. Refuses to run when `.aod/aod-kit-version` already exists (exit 2) or when invoked from inside the PLSK meta-template (exit 2 with sharpened-fingerprint check per FR-002-b).
- **`make update --check-placeholders`**: Scans the working tree for legacy `{{...}}` placeholder occurrences not in the canonical 12-member set. Reports findings in `<file>:<line>: {{<name>}}` form with a migration-guide table. Exit status 13 on drift (new exit code, additive to the F129 0–5 taxonomy and F139 10–12). Explicit-only invocation — does NOT run as part of the default `make update` happy path.
- **New exit code: 13 — `placeholder-drift`**: Additive to existing exit-code taxonomy (F129: 0=success, 1=runtime, 2=lock-conflict, 3=missing-prereq, 4=manifest-mismatch, 5=manifest-coverage-violation; F139: 10=halt-for-review, 11=lock-conflict, 12=abandoned-sentinel). CI consumers that branch on update-script exit codes should add explicit handling for `13)` if they call `make update --check-placeholders` from automation. Stable forever.
- **New env vars (FR-007 — `--yes` mode contract)**:
  - `AOD_BOOTSTRAP_TECH_STACK_DATABASE` — required in `--yes` mode (always-prompt field)
  - `AOD_BOOTSTRAP_TECH_STACK_VECTOR` — required in `--yes` mode (always-prompt field)
  - `AOD_BOOTSTRAP_TECH_STACK_AUTH` — required in `--yes` mode (always-prompt field)
  - `AOD_BOOTSTRAP_CLOUD_PROVIDER` — required in `--yes` mode (always-prompt field)
  - `AOD_BOOTSTRAP_<FIELD>` — required in `--yes` mode for any of the 8 auto-discovered fields that fall back to low-confidence detection. Pattern `AOD_BOOTSTRAP_<UPPERCASE_FIELD_NAME>=<value>`.
  - `AOD_UPSTREAM_URL` — fallback when `CANONICAL_URL=...` is not findable in `scripts/sync-upstream.sh`. In `--yes` mode with no `CANONICAL_URL` discoverable, this env var is required (no global accept-all escape hatch — resolves PRD Q-3).
- **Bash 3.2 compatibility maintained**: No `declare -A`, no `readarray`, no `${var^}`/`${var,,}`, no `|&`. Local + CI parity preserved (KB Entry 6).
- **Regression guard**: `tests/integration/134-bootstrap-placeholder-migration.bats` adds 20 BATS test cases covering subcommand mutual-exclusivity, refuse-to-overwrite, sharpened-fingerprint PLSK-internal detection, `--yes` env-var contract, drift-scan output format, and exit-13 path. Run locally with `bats tests/integration/134-bootstrap-placeholder-migration.bats`.
- **No CI workflow changes**: existing `manifest-coverage.yml` (F129) and `extract-coverage.yml` (F128) workflows continue to apply unchanged. `scripts/extract-classification.txt` was regenerated to acknowledge the new artifacts (F128 maintainer-acknowledgement step).
- **No staging/production deployment changes, no secret changes, no monitoring changes**: F134 is a CLI/automation feature, not a deployment surface. The adopter walkthrough is in `docs/guides/DOWNSTREAM_UPDATE.md` — that doc is the single source of truth for the bootstrap flow and is co-updated alongside the implementation.

**Adopter action**: pre-F129 adopters (no `.aod/aod-kit-version` pin) should run `make update-bootstrap` once to gain access to the F129 update mechanism. CI pipelines that wrap `make update` with explicit subcommand invocation should add exit 13 handling if they include `--check-placeholders` in their drift-cleanup workflows. PRD: `docs/product/02_PRD/134-update-bootstrap-placeholder-migration-2026-04-24.md`. Spec + tests: `specs/134-update-bootstrap-placeholder-migration/` and `tests/integration/134-bootstrap-placeholder-migration.bats`. Adopter quickstart: `docs/guides/DOWNSTREAM_UPDATE.md` → "Bootstrap pre-F129 adopters".

---

## Feature 158 Additions (2026-05-01)

The **Anti-Rationalization Tables for AOD Command/Skill Files** feature (PR #159, feature branch `158-anti-rationalization-tables` squash-merged on 2026-05-01, merge commit `75004cd`) added `## Common Rationalizations` and `## Red Flags` sections to 18 AOD command/skill files under `.claude/commands/` and `.claude/skills/`. The pattern is adapted from [addyosmani/agent-skills `docs/skill-anatomy.md`](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md). This is a **markdown-only governance content** feature with **zero infrastructure surface area**:

- **No CI workflow changes**: `.github/workflows/manifest-coverage.yml` (F129) and `.github/workflows/extract-coverage.yml` (F128) continue to apply unchanged. The 18 modified files were already covered by existing manifest rules — no `.aod/template-manifest.txt` edits required. `scripts/extract-classification.txt` was regenerated on the feature branch (`chore(158): regenerate extract-classification snapshot`) to acknowledge the additive content; `bash scripts/check-extract-coverage.sh` returns rc=0 against merged main.
- **No new scripts, no script modifications**: F158 touched zero `.sh` files, zero `Makefile` targets, zero `.github/workflows/*.yml` files. Pure additive markdown to existing `.claude/` files (~341 lines added across 18 files).
- **No env vars, no secrets, no Docker services, no deployment-environment changes**: The feature ships as content inside command/skill prompts that the Claude Code harness reads at invocation time. There is no runtime, no daemon, no service, no networking surface — the harness already loads `.claude/commands/*.md` and `.claude/skills/*/SKILL.md` as part of its standard slash-command resolution.
- **No adopter action required at the infrastructure layer**: Adopters who run `make update` will receive the new sections via the standard F129 manifest-driven sync. Existing CI invocations of `/aod.*` slash-commands continue to behave identically — the new sections are read by the LLM but do not change command exit codes or the YAML frontmatter contract.
- **CI parity verified post-merge**: `bash scripts/check-extract-coverage.sh` returns rc=0 against `main` at commit `75004cd`, confirming the regenerated classification snapshot remains consistent with the merged tree.

**Adopter action**: none at the DevOps layer. The `## Common Rationalizations` and `## Red Flags` sections improve LLM decision quality during command execution but do not alter any CI gate, exit-code taxonomy, or environment configuration. PRD: `docs/product/02_PRD/158-anti-rationalization-tables-2026-04-30.md`. Spec + retro: `specs/158-anti-rationalization-tables/`.

---

**Maintained By**: DevOps Agent
