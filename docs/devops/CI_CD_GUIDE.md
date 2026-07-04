# CI/CD Setup Guide - {{PROJECT_NAME}}

**Last Updated**: {{CURRENT_DATE}}
**Owner**: DevOps Agent

---

## Overview

This guide provides instructions for setting up CI/CD pipelines for {{PROJECT_NAME}}. Choose your platform based on your hosting provider.

---

## When to Add CI/CD

Add CI/CD after you have:
1. ✅ Working local development environment
2. ✅ At least one deployable feature
3. ✅ Basic test coverage (unit tests)
4. ✅ Defined deployment environments

---

## Reference Patterns: Template-Maintenance CI Workflows

This section documents three reference CI workflows that the upstream template uses to protect its own release-tooling integrity. **None ship to adopter projects** — adopt them only if you extend the template and want the same guarantees.

| Workflow | Feature | Protects |
|----------|---------|----------|
| `.github/workflows/manifest-coverage.yml` | F129 (downstream template update) | File-ownership invariant for `.aod/template-manifest.txt` |
| `.github/workflows/extract-coverage.yml` | F128 (directory-based extraction manifest) | Classification-snapshot invariant for `scripts/extract-classification.txt` |
| `.github/workflows/stack-contract.yml` | F130 (Stack Pack Test Contract) | Test contract invariant for every `stacks/*/STACK.md` (excluding content-pack allowlist) |

All three workflows share the same CI pattern (bash:3.2 Docker, SHA-pinned checkout action, `contents: read` permissions, cancel-in-progress concurrency). Use any as a template when adding a new maintenance workflow.

### Shared Workflow Conventions

| Property | Value |
|----------|-------|
| Runner | `ubuntu-latest` |
| Execution shell | `bash:3.2` Docker image (matches macOS workstation floor) |
| Permissions | `contents: read` (principle of least privilege) |
| Concurrency | `cancel-in-progress: true` on same ref (force-push safe) |
| Action pinning | `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` (v4.2.2) pinned by SHA, NOT tag |
| Trigger | `push` and `pull_request` against `main` (stack-contract adds a `paths:` filter — see F130 subsection) |

### Manifest Coverage Workflow (F129)

`.github/workflows/manifest-coverage.yml` enforces that every tracked file in the repo appears in `.aod/template-manifest.txt` (either with an explicit ownership rule or as an `ignore` entry).

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/manifest-coverage.yml` |
| Validator script | `scripts/check-manifest-coverage.sh` (bash 3.2 compatible) |
| Local invocation | `scripts/check-manifest-coverage.sh` |

**Exit contract**:

| Exit | Meaning | Stderr |
|------|---------|--------|
| 0 | Every `git ls-files` entry matches a manifest entry | (empty) |
| 1 | Manifest missing, malformed, or any file uncategorized | `<path>:1: uncategorized (no manifest entry or ignore match)` per offending file (compiler-diagnostic format — GitHub Actions annotators parse it automatically) |

### Extract Coverage Workflow (F128)

**Added in Feature 128** (directory-based extraction manifest).

`.github/workflows/extract-coverage.yml` enforces the classification-snapshot invariant required by feature 128's 5-layer defense against private-data leak: every git-tracked file must be classified in the committed `scripts/extract-classification.txt` snapshot, and the classification must match what the current `MANIFEST_DIRS` / `MANIFEST_ROOT_FILES` / `.extractignore` configuration would produce. Divergence blocks the PR.

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/extract-coverage.yml` |
| Validator script | `scripts/check-extract-coverage.sh` (bash 3.2 compatible) |
| Snapshot artifact | `scripts/extract-classification.txt` (committed, sorted) |
| Local invocation (validate) | `make extract-check` |
| Local invocation (regenerate) | `make extract-classify` |
| Workflow name | `Extract Coverage` |
| Job ID | `check-extract-coverage` |
| Concurrency group | `extract-coverage-${{ github.ref }}` |

**Exit contract**:

| Exit | Meaning | Stderr |
|------|---------|--------|
| 0 | Snapshot matches reality (or emergency override triggered) | (empty) |
| 1 | Snapshot missing, malformed, or diverged from computed classification | `extract-classification.txt:1: <message>: <path>` per divergence (compiler-diagnostic format) |

**Classification values** (per `specs/128-directory-based-extraction-manifest/data-model.md` Entity 3):

- `SHIP` — file ships downstream (covered by MANIFEST_DIRS / MANIFEST_ROOT_FILES, not excluded by `.extractignore`)
- `EXCL-by-override` — covered by MANIFEST but excluded by `.extractignore`
- `EXCL-by-construction` — not covered by MANIFEST at all (private-by-default)

**Emergency override** (FR-018): include the literal marker `[skip extract-check]` in the head commit message to bypass the check for a single commit. The workflow emits a `::warning::` annotation on skip so the override is visible in the Actions log. Use sparingly — guidance in `docs/guides/PLSK_MAINTAINER_GUIDE.md` caps routine use at "no more than once per quarter" (PM Decision).

**Full contract**: `specs/128-directory-based-extraction-manifest/contracts/classification-snapshot.md` and `contracts/extract-cli.md`.

### Stack Contract Workflow (F130)

**Added in Feature 130** (Stack Pack Test Contract), merged via PR #141 on 2026-04-21.

`.github/workflows/stack-contract.yml` enforces that every app-stack pack's `stacks/*/STACK.md` contains a valid, machine-readable test-contract block between the `<!-- BEGIN: aod-test-contract -->` / `<!-- END: aod-test-contract -->` sentinels. This guarantees the AOD test-orchestration pipeline can discover a deterministic test command for every active stack pack without falling back to heuristics. The workflow runs on push/PR to `main` and blocks the PR on any lint violation.

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/stack-contract.yml` |
| Validator script | `.aod/scripts/bash/stack-contract-lint.sh` (bash 3.2 compatible) |
| Invocation (CI) | `bash .aod/scripts/bash/stack-contract-lint.sh --all` |
| Local invocation (single pack) | `bash .aod/scripts/bash/stack-contract-lint.sh stacks/<pack>/STACK.md` |
| Local invocation (all packs) | `bash .aod/scripts/bash/stack-contract-lint.sh --all` |
| Workflow name | `Stack Contract` |
| Job ID | `check` |
| Concurrency group | `stack-contract-${{ github.ref }}` |
| Path filter | `stacks/**/STACK.md`, `.aod/scripts/bash/stack-contract-lint.sh`, `.github/workflows/stack-contract.yml`, `tests/fixtures/stack-contracts/**` |

**Exit contract** (stable forever — do not repurpose):

| Exit | Meaning |
|------|---------|
| 0 | `VALID` — all non-allowlisted packs have a well-formed contract block |
| 1 | `RUNTIME_ERROR` — missing dependencies, filesystem error, or invalid invocation |
| 2 | `MISSING_TEST_COMMAND` — `test_command` key absent, or `e2e_opt_out` rationale below minimum length |
| 3 | `XOR_VIOLATION` — both `test_command` and `e2e_opt_out` present (mutually exclusive) |
| 4 | `UNKNOWN_KEY` — contract block contains a key outside the allowed schema |
| 5 | `MISSING_BLOCK` — no `<!-- BEGIN: aod-test-contract -->` / `<!-- END: aod-test-contract -->` sentinels found |

In `--all` mode the script exits with the **numerically lowest non-zero code** across all non-allowlisted packs so the failing-fast diagnostic stays deterministic across CI and local runs (per FR-030 byte-identical stderr).

**Content-pack allowlist**: Packs listed in the script's `CONTENT_PACKS` array (currently `knowledge-system`) are skipped in `--all` mode because they carry no runnable tests. Single-file mode ignores the allowlist so maintainers can still lint a pack explicitly when intentionally transitioning it from content-only to test-bearing.

**Local-parity guarantee**: `stack-contract-lint.sh` is strictly bash-3.2 clean (no associative arrays, no `readarray`, no case-modification parameter expansion) so it runs on stock macOS `/bin/bash` 3.2.57 without any shim. Combined with the `bash:3.2` Docker image used in CI, stderr output is byte-identical between a developer's workstation and the GitHub Actions runner (modulo runner path prefixes). See KB Entry 6 for why this floor matters.

**Full contract**: `specs/130-e2e-hard-gate/contracts/stack-contract-lint.md` and `docs/stacks/TEST_COMMAND_CONTRACT.md`. The STACK.md block schema is defined in `specs/130-e2e-hard-gate/data-model.md` §1, §2, §5.

**Feature 142 Update (2026-04-23)**: The workflow itself (`.github/workflows/stack-contract.yml`) and the validator (`.aod/scripts/bash/stack-contract-lint.sh`) are **unchanged** by F142 (PR #151) — the exit-code contract (0–5) was already strict as of F130. F142 only removes the grace-period fallback that previously lived inside `/aod.deliver` Step 9a, which translated a lint exit 5 (MISSING_BLOCK) into a silent skip. Post-F142, `/aod.deliver` surfaces exit 5 as an explicit error with the lint stderr diagnostic shown verbatim in the delivery report. **Effective impact on CI consumers**: any pipeline that parses delivery.md rendered by `/aod.deliver` should read `e2e_validation.status` (`error` vs. `skipped` vs. `success`) from the payload rather than pattern-matching grace-period language in the human-readable rendering. The stack-contract CI workflow continues to fail any PR that would have tripped its exit 5 anyway — F142 closes the same gap at the `/aod.deliver` boundary for branches not guarded by the CI workflow. PRD: `docs/product/02_PRD/142-remove-grace-period-fallback-2026-04-23.md`.

### Why bash:3.2 in Docker

All three workflows run inside `bash:3.2` so CI enforces the same shell constraints that bind adopter workstations on macOS (GPLv3 licensing means Apple ships `/bin/bash` 3.2.57). GitHub's `ubuntu-latest` ships bash 5.x — without Docker isolation, bash 4+ regressions (associative arrays, `readarray`, case-modification parameter expansion, etc.) would pass CI and break macOS adopters. See `docs/INSTITUTIONAL_KNOWLEDGE.md` KB Entry 6 for background.

### bash:3.2 Docker Pattern (Reusable)

The `bash:3.2` image is Alpine-based and **does not ship with git**. Validators that shell out to `git ls-files` (both `check-manifest-coverage.sh` and `check-extract-coverage.sh`) need git installed at runtime; `stack-contract-lint.sh --all` also benefits from the same bootstrap because repo-wide mode expects the same mounted git worktree. Additionally, the mounted working tree triggers git's dubious-ownership check because the container runs as root while the host runner owns the files. All three workflows use this identical three-line pattern — **mirror it exactly when adding a new bash:3.2 CI step**:

```bash
docker run --rm \
  -v "$PWD:/w" \
  -w /w \
  bash:3.2 \
  sh -c "apk add --no-cache git >/dev/null && git config --global --add safe.directory /w && scripts/<validator>.sh"
```

Three concerns addressed:

1. **`apk add --no-cache git`** — installs git inside the Alpine container (the `bash:3.2` image only ships bash + coreutils). `--no-cache` keeps the layer small; git version is whatever Alpine ships at run time — workflows do not depend on a specific version.
2. **`git config --global --add safe.directory /w`** — suppresses git's `dubious ownership in repository` error when the container runs as root against files owned by the runner user. The UID mismatch is expected and safe in CI.
3. **`sh -c "..."`** — the `bash:3.2` image's default entrypoint is bash, but for the `&&`-chained setup we use `sh -c` to keep the command string compact.

`manifest-coverage.yml`, `extract-coverage.yml`, and `stack-contract.yml` all use this exact pattern (the two-step fix — add git + configure safe.directory — was applied to the coverage workflows during F128 delivery after the Alpine image surfaced the issue on first run, and `stack-contract.yml` was authored against the same pattern in F130). New template-maintenance workflows SHOULD copy this pattern verbatim to guarantee CI parity.

### Action Pinning Convention

All third-party GitHub Actions are pinned by full commit SHA, never by floating tag. All three workflows share the same pinned SHA so maintainers can upgrade them at once:

```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

When upgrading, bump the SHA in `manifest-coverage.yml`, `extract-coverage.yml`, AND `stack-contract.yml` together along with the maintainer-friendly comment. This mirrors the same retag-defense philosophy the update script enforces against upstream template releases.

**Fetch-depth invariant**: Each of the three workflows relies on the full working tree being mounted into the bash:3.2 container. `actions/checkout` defaults to `fetch-depth: 1` which is sufficient for the current validators (they shell out to `git ls-files` against the checked-out worktree, not against history). If a future maintenance workflow needs history (e.g., `git log`, `git merge-base`), set `fetch-depth: 0` on its checkout step — do not regress the existing three by changing the default underneath them.

### Running Validators Locally

Before pushing, run any validator directly. A `make` target is available for extract-coverage:

```bash
# Manifest coverage (F129)
scripts/check-manifest-coverage.sh

# Extract coverage (F128 — validate)
make extract-check
# or: scripts/check-extract-coverage.sh

# Extract coverage (F128 — regenerate snapshot after legitimate manifest change)
make extract-classify
# Writes: scripts/extract-classification.txt
# After running, review the diff (`git diff scripts/extract-classification.txt`)
# as the maintainer acknowledgement step, then commit.

# Stack contract (F130 — repo-wide, matches CI exactly)
bash .aod/scripts/bash/stack-contract-lint.sh --all

# Stack contract (F130 — single pack, fastest while iterating on one STACK.md)
bash .aod/scripts/bash/stack-contract-lint.sh stacks/<pack>/STACK.md
```

Exit code `0` means you're clean. A non-zero exit prints divergences in the compiler-diagnostic format listed above.

### Optional Pre-Commit Hook

Strongly recommended for maintainers. All three checks are fast enough for the pre-commit path. Install with:

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
set -e
scripts/check-manifest-coverage.sh
make extract-check
bash .aod/scripts/bash/stack-contract-lint.sh --all
EOF
chmod +x .git/hooks/pre-commit
```

---

## BATS Test Harness Setup (Feature 129+)

**Added in Feature 129.** The bash test suite for shell-scripted features uses [BATS](https://github.com/bats-core/bats-core) (Bash Automated Testing System). Tests live in `tests/unit/*.bats` and `tests/integration/*.bats`.

### Install

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install bats-core` |
| Linux (Debian/Ubuntu) | `sudo apt-get install bats` |
| Any (no-root / CI fallback) | `git submodule add https://github.com/bats-core/bats-core.git tests/vendor/bats-core` then invoke via `tests/vendor/bats-core/bin/bats` |

Verify with `bats --version` (expected: 1.x or newer).

See `CONTRIBUTING.md` for the authoritative install guide and the full `bash 3.2` compatibility rules.

### CI Integration (current status)

BATS is **not yet wired into** `manifest-coverage.yml`, `extract-coverage.yml`, or `stack-contract.yml` — those workflows' sole jobs are their respective invariant checks. BATS tests are run locally during development and before PRs. A future CI workflow can opt in by adding a `bats tests/unit/ tests/integration/` step; the `bash:3.2` image already contains `bats` via `apk add bats` (Alpine base).

---

## Playwright E2E in Adopter CI (FastAPI Stack Packs)

**Added in Feature 138** (2026-04-21). No new CI workflows were added to this template repo — the existing `stack-contract.yml` (F130) validates the `e2e_command` declaration is present and well-formed. Adopters who scaffold `fastapi-react` or `fastapi-react-local` receive an opt-in `test:e2e` npm script they can wire into their own CI.

Reference CI snippet (GitHub Actions; adapt to your provider):

```yaml
- name: Install backend deps
  run: cd backend && uv sync

- name: Install frontend deps
  run: cd frontend && npm ci

- name: Install Playwright browsers
  run: cd frontend && npx playwright install chromium --with-deps

- name: Run E2E tests
  env:
    TEST_DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}  # fastapi-react (Postgres) only
    CI: true
  run: npm --prefix frontend run test:e2e

- name: Upload traces on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-traces
    path: frontend/test-results/
    retention-days: 14
```

`CI=true` disables `reuseExistingServer`. Trace artifacts redact `Authorization` / `Cookie` headers by default but keep retention short on public repos. Full adopter walkthrough: `specs/138-playwright-e2e-fastapi-stack-packs/quickstart.md`.

---

## `/aod.deliver` Exit-Code Contract (Feature 139)

**Added in Feature 139** (PR #149, merged 2026-04-23). CI pipelines that shell out to `/aod.deliver` — most commonly inside `/aod.run --autonomous` or a post-merge automation job — MUST branch on the full exit-code taxonomy. The three new codes (10, 11, 12) are **additive** to the existing PRD 130 taxonomy (0-5) and are stable forever.

| Exit | Symbol | Source | CI Action |
|------|--------|--------|-----------|
| 0 | `success` | Delivery clean: tests pass, AC coverage complete, docs updated, lock released | Proceed to next pipeline stage. |
| 1 | `runtime_error` | PRD 130 — unexpected runtime failure | Fail the job. Surface stderr. |
| 2 | `missing_test_command` | PRD 130 — stack pack has no declared `test_command` | Fail the job. Operator fixes `STACK.md`. |
| 3 | `xor_violation` | PRD 130 — `test_command` + `e2e_opt_out` both set | Fail the job. Operator resolves. |
| 4 | `unknown_key` | PRD 130 — contract block has an unrecognized key | Fail the job. Operator resolves. |
| 5 | `missing_block` | PRD 130 — no `<!-- BEGIN: aod-test-contract -->` sentinels | Fail the job. Operator resolves. |
| **10** | **`halt-for-review`** | **F139 — verification gate tripped; heal-PR opened/updated** | **NOT a failure. Notify reviewer. Pipeline continues.** Halt record at `.aod/state/deliver-{NNN}.halt.json`. |
| **11** | **`lock-conflict`** | **F139 — another `/aod.deliver {NNN}` holds `.aod/locks/deliver-{NNN}.lock`** | **Retry with bounded backoff.** Conflicting invocation is expected to release the lock on its own exit. |
| **12** | **`abandoned-sentinel`** | **F139 — crash-recovery detected orphaned `.aod/state/deliver-{NNN}.state.json`** | **Operator intervention required.** Do NOT auto-clear from CI — this is a safety rail against concurrent-run corruption. Page on-call if autonomous. |

### Three-Channel Halt Signal (Exit 10)

Exit code 10 is emitted alongside two other signals, **all co-equal by design**:

1. **Stdout line**: `DELIVERY_HALTED: {NNN}` — consumers that tail stdout (humans, log scrapers) see the signal immediately.
2. **Halt-record JSON**: `.aod/state/deliver-{NNN}.halt.json` — consumers that persist state across runs (orchestrators, dashboards) reconstruct halt context.
3. **Exit code 10**: CI shells branch on this.

Do NOT suppress any channel — different consumers read different channels, and muting one breaks the consumer that relies on it. Full rationale: `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md` Q&A.

### Reference CI Snippet

```bash
/aod.deliver "$FEATURE" --autonomous
rc=$?
case $rc in
  0)       echo "::notice::Delivered cleanly"; continue_pipeline ;;
  10)      echo "::notice::Halted for review — heal-PR opened"; notify_reviewer; exit 0 ;;
  11)      echo "::warning::Lock contention — retrying"; retry_with_backoff ;;
  12)      echo "::error::Abandoned sentinel — operator intervention required"; page_on_call; exit 1 ;;
  1|2|3|4|5) echo "::error::Contract failure rc=$rc"; exit "$rc" ;;
  *)       echo "::error::Unknown exit code $rc"; exit "$rc" ;;
esac
```

### Flag Deprecation — `--require-tests`

`/aod.deliver --require-tests` is a **silent no-op** with a stderr deprecation notice for 2 release cycles (grace window ends at release N+2 relative to F139). The flag's original intent — "require tests before closing the feature" — is now the default hard-gate behaviour, so the flag is redundant. Remove it from any CI invocation at your convenience; after release N+2 it will fail argument parsing with exit code 2.

Adopter migration walkthrough: `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md`. AC-coverage migration (legacy prose specs): `docs/guides/AC_COVERAGE_MIGRATION.md`. No new CI workflows are added for this feature — the gate is internal to the `/aod.deliver` skill.

---

## Update-Script Environment Variables

**Added in Feature 129.** `scripts/update.sh` (invoked by `make update` / `/aod.update`) respects the following environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CI` | unset | When set (e.g., by GitHub Actions), update.sh defaults to `--dry-run` mode. Explicit `--apply` required to write. Safety guard to prevent accidental writes in automation. |
| `AOD_UPDATE_TMP_DIR` | `.aod/update-tmp` under adopter root | Staging directory override. Must be on the same filesystem as the project root (atomicity via `rename(2)` within the same mount). |
| `FORCE_RETAG` | unset | Override the retag-detection tripwire. Proceeds even if an upstream tag's SHA changed since the last pin. Logs a WARN. Paired with `--force-retag` CLI flag. |
| `AOD_COVERAGE_FILES` | (derived from `git ls-files`) | Test-harness override for `scripts/check-manifest-coverage.sh`. Newline-separated file list. **NOT public contract — for BATS tests only.** |
| `AOD_COVERAGE_MANIFEST` | `<repo_root>/.aod/template-manifest.txt` | Test-harness override. **NOT public contract.** |
| `AOD_COVERAGE_REPO_ROOT` | `git rev-parse --show-toplevel` | Test-harness override. **NOT public contract.** |

**Added in Feature 134.** `scripts/update.sh --bootstrap` (invoked by `make update-bootstrap`) and `scripts/update.sh --check-placeholders` (invoked by `make update --check-placeholders`) respect the following environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `YES` | unset | When set to `1` (via `make update-bootstrap YES=1`), the bootstrap subcommand engages `--yes` mode (non-interactive). Pass-through into the underlying `scripts/update.sh --bootstrap --yes` invocation. |
| `AOD_BOOTSTRAP_TECH_STACK_DATABASE` | unset | **Required in `--yes` mode.** Always-prompt architecture value. Examples: `Postgres`, `MySQL`, `SQLite`. |
| `AOD_BOOTSTRAP_TECH_STACK_VECTOR` | unset | **Required in `--yes` mode.** Always-prompt architecture value. Examples: `pgvector`, `Pinecone`, `Weaviate`, `none`. |
| `AOD_BOOTSTRAP_TECH_STACK_AUTH` | unset | **Required in `--yes` mode.** Always-prompt architecture value. Examples: `JWT`, `Auth0`, `Clerk`, `Supabase Auth`. |
| `AOD_BOOTSTRAP_CLOUD_PROVIDER` | unset | **Required in `--yes` mode.** Always-prompt architecture value. Examples: `Vercel`, `Railway`, `AWS`, `GCP`. |
| `AOD_BOOTSTRAP_<FIELD>` | unset | **Required in `--yes` mode for any auto-discovered field that fell back to low-confidence detection.** Pattern `AOD_BOOTSTRAP_<UPPERCASE_FIELD_NAME>=<value>` for each of the 8 auto-discovered canonical placeholders (e.g., `AOD_BOOTSTRAP_PROJECT_NAME`, `AOD_BOOTSTRAP_PROJECT_URL`). Per-field override only — no global accept-all escape hatch. |
| `AOD_UPSTREAM_URL` | unset | Fallback upstream URL when `CANONICAL_URL=...` is not findable in `scripts/sync-upstream.sh`. In `--yes` mode with no `CANONICAL_URL` discoverable, this env var is required and the command refuses to proceed without it. |

**Added in Feature 128.** `scripts/check-extract-coverage.sh` (invoked by `make extract-check` and the Extract Coverage CI workflow) respects the following environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKIP_MARKER` | unset | When set to any non-empty value in default (validate) mode, short-circuits to exit 0. The CI workflow does NOT use this directly — it gates via `if:` on the commit marker `[skip extract-check]`. Intended for local pre-commit hooks that need the same emergency-override semantics. |
| `AOD_COVERAGE_FILES` | (derived from `git ls-files`) | Test-harness override (shared convention with check-manifest-coverage). **NOT public contract.** |
| `AOD_COVERAGE_MANIFEST` | `<repo_root>/scripts/extract-classification.txt` | Test-harness override for the extract-classification snapshot path. **NOT public contract.** |
| `AOD_COVERAGE_REPO_ROOT` | `git rev-parse --show-toplevel` | Test-harness override. **NOT public contract.** |
| `AOD_COVERAGE_EXTRACT_SH` | `<repo_root>/scripts/extract.sh` | Test-harness override for the `extract.sh` path under test. **NOT public contract.** |
| `AOD_COVERAGE_EXTRACTIGNORE` | `<repo_root>/.extractignore` | Test-harness override for the `.extractignore` path under test. **NOT public contract.** |

### Lock Contention & Concurrency

The update script holds `.aod/update.lock` while applying changes. Concurrency mechanics:

- **Lock acquisition**: `flock` fast-path on Linux; atomic `set -o noclobber` create on macOS (and all POSIX systems lacking `flock`). Lock contents: `pid`, 16-char hex `nonce`, ISO-8601 `started_at`, `cmdline`.
- **Default timeout**: ~30 s total wait with bounded retries.
- **Exit code 2**: lock contention — another `/aod.update` is running.
- **Stale-lock handling**: if the recorded PID is dead (`kill -0` returns non-zero) AND the lock is older than 1 hour, the update script force-acquires with nonce re-verify. Dead + <1h returns exit code 2 with a hint to investigate.

Full contract and edge-case behaviour: see `docs/guides/DOWNSTREAM_UPDATE.md` — this is the single source of truth. Spec references: `specs/129-downstream-template-update/spec.md` FR-005 (atomicity) and FR-008 (manifest coverage); `specs/129-downstream-template-update/plan.md` concurrency + CI design.

### Feature 132 Regression Guard (2026-04-23)

**Added in Feature 132** (PR #152, merge commit `47d8956`). `tests/integration/132-coverage-violation-output.bats` guards the `scripts/update.sh` exit-5 output contract against future refactors. The bug it prevents: a command substitution under `set -euo pipefail` previously aborted the script before `local cat_rc=$?` could capture the helper's return value, silently skipping the `[aod] ERROR: manifest coverage violation —` collector. The fix is a 3-line `set +e` / `set -e` bracket around the helper call; the test exercises both the rc=5 (uncategorized file) and rc=1 (malformed manifest) paths.

- **Test file**: `tests/integration/132-coverage-violation-output.bats`
- **Test count**: 2 (rc=5 path + rc=1 path)
- **Fixture isolation**: each test builds a self-contained bare upstream git repo under `$BATS_TEST_TMPDIR` — independent of the live `.aod/template-manifest.txt`, survives future 100%-coverage states
- **Local invocation**: `bats tests/integration/132-coverage-violation-output.bats`
- **CI integration**: no new workflow; the existing BATS harness (`bash:3.2` Docker pattern from F128/F129) already covers this test when BATS is wired into CI. The `manifest-coverage.yml` workflow continues to protect the upstream template's own manifest invariant — the new test protects the update script's output contract, a different layer.

Why-this-matters: F129's initial implementation shipped with 514 BATS tests, none of which exercised the rc=5 collector path — the silent-exit regression only surfaced when adopters ran `make update` against an upstream with uncategorized files. This test closes that gap so the next refactor cannot silently remove the adopter-facing diagnostic. PRD: `docs/product/02_PRD/132-fix-update-sh-silent-exit-2026-04-23.md`.

### Feature 134 Bootstrap + Placeholder Migration BATS Suite (2026-04-25)

**Added in Feature 134** (PR #153, merge commit `f09035b`). `tests/integration/134-bootstrap-placeholder-migration.bats` adds 20 BATS test cases exercising the new `--bootstrap` and `--check-placeholders` subcommands, the `--yes` env-var contract, the sharpened-fingerprint PLSK-internal refusal, and the new exit-code 13 path for placeholder drift. The suite is included in the existing BATS test harness (no new CI workflow) — the `bash:3.2` Docker pattern from F128/F129 already covers it.

- **Test file**: `tests/integration/134-bootstrap-placeholder-migration.bats`
- **Test count**: 20 cases (subcommand mutual-exclusivity, refuse-to-overwrite per FR-002-a, sharpened-fingerprint per FR-002-b, `--yes` env-var enforcement per FR-007, drift-scan output format per SC-002, exit-13 placeholder-drift contract)
- **Fixture isolation**: each test builds its own self-contained adopter fixture under `$BATS_TEST_TMPDIR` — independent of the live `.aod/template-manifest.txt`, the live `scripts/sync-upstream.sh`, and the production `.aod/personalization.env` (if any)
- **Local invocation**: `bats tests/integration/134-bootstrap-placeholder-migration.bats`
- **CI integration**: no new workflow; runs alongside the rest of the BATS suite when wired into CI. The new exit code 13 is asserted in the suite's drift-scan tests (SC-002)

**New exit code: 13 — `placeholder-drift`**: emitted by `scripts/update.sh --check-placeholders` when legacy placeholder occurrences are detected outside the canonical 12-member `AOD_CANONICAL_PLACEHOLDERS` set defined in `.aod/scripts/bash/template-substitute.sh`. Findings format: `<file>:<line>: {{<name>}}` per occurrence on stdout, followed by a migration-guide table. The exit code is **additive** to the existing F129 taxonomy (0–5) and F139 taxonomy (10–12) — CI consumers that branch on update-script exit codes should add explicit handling for `13)` if they call `make update --check-placeholders` from automation. Stable forever.

PRD: `docs/product/02_PRD/134-update-bootstrap-placeholder-migration-2026-04-24.md`. Spec: `specs/134-update-bootstrap-placeholder-migration/spec.md`. Adopter walkthrough: `docs/guides/DOWNSTREAM_UPDATE.md`.

---

## Tachi Pytest Workflow

**Workflow file**: `.github/workflows/tachi-pytest.yml`

This workflow runs the F-248 substitution-surface suite and the F-256 source-pattern-hardening suite (`tests/scripts/test_init_sh_*.py` + `tests/scripts/test_template_*.py`) on a two-runner cross-platform matrix (macOS bash 3.2.57 + ubuntu bash 5.x). Both matrix legs must pass green.

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/tachi-pytest.yml` |
| Runner matrix | `macos-latest` (bash 3.2.57) + `ubuntu-latest` (bash 5.x) |
| Python version | 3.11 |
| Pytest dependencies | `pytest>=8`, `pytest-timeout>=2`, `pyyaml>=6` |
| Per-test timeout | `--timeout=1080` (hardcoded flag; see F-250 outer-cap rationale in spec) |
| Permissions | `contents: read` |

### Trigger Design (F-338 — push:[main] guard, PR #340, 2026-06-30)

**Added in Feature 338** (Restore F-248/F-256 Substitution Hardening, PR #340, merged 2026-06-30, release v4.45.1).

The workflow fires on **both** `pull_request` and `push: branches: [main]`. The path filter is shared between the two triggers via a single YAML anchor (`&hardening_paths` / `*hardening_paths`) so the trigger surface stays single-source — no third list to keep in lock-step.

```yaml
on:
  pull_request:
    paths: &hardening_paths
      - scripts/init.sh
      - .aod/scripts/bash/template-substitute.sh
      # ... (full list in .github/workflows/tachi-pytest.yml)
  push:
    branches: [main]
    paths: *hardening_paths
```

**Why `push: branches: [main]`**: a direct-to-`main` push (e.g., a `/aod.update` apply commit) bypasses the `pull_request` trigger. That is exactly how the F-248/F-256 hardening was silently reverted on `main` in June 2026 (issue #338) — an `/aod.update` run clobbered four hardening-surface files and the gap went undetected until manual inspection. The `push: [main]` trigger closes this regression class: any future direct-to-`main` commit that touches a hardening-surface path will immediately fail CI on `main`, surfacing the regression in minutes rather than shipping it silently to adopters.

**Regression class defended**: silent hardening clobber via direct-to-`main` push (e.g., `/aod.update`). The `pull_request` trigger alone cannot defend this because direct pushes bypass it entirely.

### Path Filter

The `paths:` filter (`&hardening_paths`) covers the hardening surfaces in lock-step with the pytest invocation. When adding a new test file or refactoring a new bash library file, update both the `paths:` trigger list and the `python -m pytest ...` command in the same commit (per F-250 lock-step lesson). Current surfaces include:

- `scripts/init.sh`, `.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-config-load.sh`, `.aod/scripts/bash/init-input.sh`, `.aod/scripts/bash/template-validate.sh`
- Constitution templates, template manifest, stack-pack `defaults.env` files (F-256 Site A)
- All `tests/scripts/test_*.py` modules in the suite
- `.github/workflows/tachi-pytest.yml` itself (self-watching)

See the workflow file for the authoritative full list.

### Feature History

| Feature | PR | Change |
|---------|----|--------|
| F-248 | #249 | Initial substitution-surface suite + macOS matrix |
| F-256 | #257 | Source-pattern-hardening suite; `template-config-load.sh`; `AOD_FETCH_TIMEOUT` watchdog |
| F-250 | — | `--timeout=1080` outer cap; session-scoped fixture rationale |
| F-5 / F-282 | #286 | `test_init_precommit_matrix.py` added to suite |
| F-302 / F-260b | #303 | Asset-tag test modules + `populate-affected-assets.py` / `sarif_common.py` / `schemas/finding.yaml` path-filter lock-step |
| **F-338** | **#340** | **`push: branches: [main]` trigger added; paths shared via YAML anchor `&hardening_paths`; defends against direct-to-`main` hardening clobber** |
| F-295 | #353 | `scripts/generate-threats-sarif.py` added to path filter (FR-014 input-path-derived `artifactLocation.uri`, covered by 4 assertions in the existing suite); no new test module or workflow added — the planned US-3 byte-identity CI wiring was structurally deferred to defect #356 after the T026 Cat 6 gate failed |

### Environment Variables

The workflow itself reads **no adopter-facing environment variables** — `--timeout=1080` is a hardcoded flag, not an env var. The test fixtures invoke `AOD_FETCH_TIMEOUT` and `AOD_RATIFICATION_DATE_OVERRIDE` indirectly via `tests/scripts/init_sh_helpers.run_init_in_clone()` for determinism; see `docs/devops/environment-variables.md` for the full contracts.

---

## Tachi Catalog Drift Guard Workflow

**Workflow file**: `.github/workflows/tachi-catalog-drift.yml`

**Added in Feature 329** (Ordered-Frameworks Catalog-Drift CI Guard, PR #344, merged 2026-06-30, release v4.46.0).

This workflow reddens CI — on PRs AND direct-to-`main` pushes — when an `ORDERED_FRAMEWORKS` catalog member drifts from its committed fingerprint sidecar without a CA-baseline regen. It renders nothing and makes no network calls (NFR-001: zero-network, zero-render).

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/tachi-catalog-drift.yml` |
| Runner | `ubuntu-latest` |
| Permissions | `contents: read` (principle of least privilege) |
| Pytest dependencies | `pytest`, `pytest-timeout`, `pyyaml` |
| Test file | `tests/scripts/test_catalog_drift_guard.py` |
| Invocation | `pytest tests/scripts/test_catalog_drift_guard.py` |

### Trigger Design (F-329 — dual-trigger with YAML anchor)

The workflow fires on **both** `pull_request` and `push: branches: [main]`. The path filter is shared between the two triggers via a single YAML anchor (`&drift_paths` / `*drift_paths`) so the trigger surface stays single-source — no second list to drift out of sync.

```yaml
on:
  pull_request:
    paths: &drift_paths
      - catalog/*.yaml
      - catalog/*.sidecar.json
      - tests/scripts/test_catalog_drift_guard.py
      # ... (full list in .github/workflows/tachi-catalog-drift.yml)
  push:
    branches: [main]
    paths: *drift_paths
```

**Why `push: branches: [main]`**: a direct-to-`main` push (e.g., a `/aod.update` apply commit or a catalog edit) bypasses the `pull_request` trigger. The `push: [main]` trigger closes this regression class: any future direct-to-`main` commit that touches a catalog or fingerprint path will immediately fail CI on `main`, surfacing a drift in minutes rather than shipping it silently.

### What it guards

`ORDERED_FRAMEWORKS` is an ordered list of catalog framework identifiers. When a catalog YAML is edited (a record added, removed, or modified), the corresponding fingerprint sidecar must be regenerated (`make catalog-regen` or equivalent CA-baseline regen). If the sidecar is stale, the drift guard test fails:

- **Drift detected → CI red** — PR is blocked; a direct-to-`main` push surfaces the regression immediately.
- **Sidecar current → CI green** — no action required.

### Local invocation

```bash
# Run the guard locally (matches CI exactly)
pytest tests/scripts/test_catalog_drift_guard.py

# After editing a catalog file, regenerate the sidecar then re-run:
make catalog-regen   # or the project's CA-baseline regen command
pytest tests/scripts/test_catalog_drift_guard.py
```

### Relationship to `tachi-pytest.yml`

`tachi-catalog-drift.yml` is a **sibling** workflow to `tachi-pytest.yml`, not a sub-job of it. The two workflows share the same shared-anchor dual-trigger pattern but guard independent test surfaces:

| Workflow | Guards | Test module |
|----------|--------|-------------|
| `tachi-pytest.yml` | Substitution-surface hardening (init.sh, template-substitute.sh, etc.) | `tests/scripts/test_init_sh_*.py`, `test_template_*.py`, etc. |
| `tachi-catalog-drift.yml` | ORDERED_FRAMEWORKS catalog fingerprint integrity | `tests/scripts/test_catalog_drift_guard.py` |

Both workflows use `ubuntu-latest`, `contents: read`, and install the same pytest stack. New catalog-level CI guards SHOULD follow this sibling-workflow pattern rather than adding jobs to `tachi-pytest.yml`.

---

## Tachi Permissions-Verify Workflow

**Workflow file**: `.github/workflows/tachi-permissions-verify.yml`

**Added in Feature 281** (CI & Governance Hardening Tail, F-4/F-5 follow-ups; PR #347, merged 2026-07-01). This workflow reddens CI — on PRs AND direct-to-`main` pushes — when `.claude/settings.json` and its governing doc (`docs/standards/CLAUDE_PERMISSIONS.md`) drift out of sync with each other or become internally invalid. It ports the already-shipped F-4 local pre-commit recipe (jq validity + AC-2 cross-check) into a CI back-stop, so a `--no-verify` commit, an uninstalled hook, or a GitHub-web-UI edit to `.claude/settings.json` cannot land on `main` unchecked.

| Property | Value |
|----------|-------|
| Workflow file | `.github/workflows/tachi-permissions-verify.yml` |
| Runner | `ubuntu-latest` (single OS — every check is an OS-independent string/JSON assertion) |
| Permissions | `contents: read` (no `security-events: write` — this workflow emits no SARIF) |
| Checkout | Full, non-sparse (`actions/checkout@v4` default) — required by step 3's `git rev-parse --show-toplevel` root resolution |
| Reused script | `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (delivered #280 — reused verbatim, not reimplemented) |

### Trigger Design (F-281 — dual-trigger with YAML anchor)

The workflow fires on **both** `pull_request` and `push: branches: [main]`. The path filter is shared between the two triggers via a single YAML anchor (`&verify_paths` / `*verify_paths`) so the trigger surface stays single-source — no second list to drift out of sync (the same F-250 lock-step rule applied by `tachi-pytest.yml` and `tachi-catalog-drift.yml`).

```yaml
on:
  pull_request:
    paths: &verify_paths
      - .claude/settings.json
      - docs/standards/CLAUDE_PERMISSIONS.md
      - .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh
      - .github/workflows/tachi-permissions-verify.yml
  push:
    branches: [main]
    paths: *verify_paths
```

**Why `push: branches: [main]`**: a `.claude/settings.json` or `CLAUDE_PERMISSIONS.md` edit can reach `main` via a direct push that bypasses the `pull_request` trigger entirely — the same direct-to-`main` bypass class already documented for `tachi-pytest.yml` (F-338) and `tachi-catalog-drift.yml` (F-329). The push leg closes that gap: any future direct-to-`main` commit touching the settings/doc pair will immediately fail CI, surfacing the drift in minutes rather than shipping it silently.

### What it checks (four ordered steps)

1. **jq-presence guard** — fails loudly (`::error::jq missing on runner`) if a future runner-image change drops `jq`, rather than erroring ambiguously inside the next step.
2. **`jq empty .claude/settings.json`** — asserts the file is well-formed JSON.
3. **AC-2 cross-check** (`bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`) — the reused #280 script. The job fails on **any** non-zero exit: exit 1 (orphaned rule / mismatched table row) and exit 2 (invariant violation — missing files, jq parse error, empty section) both fail; there is no `continue-on-error` and the exit code is never swallowed.
4. **Doc-presence grep** — asserts `CLAUDE_PERMISSIONS.md` §3 ("Settings precedence") and §4 ("Per-rule rationale table") are present. This covers the two interactive-only acceptance criteria (AC-7, AC-12) that the AC-2 script cannot exercise on its own. The greps match byte-exact live headings — a future heading rename must update both the doc and the greps in the same commit.

### Local invocation

```bash
# Steps 1-2 (JSON validity)
jq empty .claude/settings.json

# Step 3 (AC-2 cross-check — matches CI exactly)
bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh

# Step 4 (doc-presence — manual grep, matches CI exactly)
grep -qE '^## 3\. Settings precedence' docs/standards/CLAUDE_PERMISSIONS.md && echo "§3 OK"
grep -qE '^## 4\. Per-rule rationale table' docs/standards/CLAUDE_PERMISSIONS.md && echo "§4 OK"
```

### Relationship to sibling dual-trigger workflows

`tachi-permissions-verify.yml` follows the same anchor-based dual-trigger pattern as `tachi-pytest.yml` (F-338) and `tachi-catalog-drift.yml` (F-329), but owns its **own** anchor and file — it MUST NOT touch either sibling's anchor (`&hardening_paths` / `&drift_paths`).

| Workflow | Guards | Anchor |
|----------|--------|--------|
| `tachi-pytest.yml` | Substitution-surface hardening (init.sh, template-substitute.sh, etc.) | `&hardening_paths` |
| `tachi-catalog-drift.yml` | ORDERED_FRAMEWORKS catalog fingerprint integrity | `&drift_paths` |
| `tachi-permissions-verify.yml` | `.claude/settings.json` ↔ `CLAUDE_PERMISSIONS.md` sync | `&verify_paths` |

**Reference**: `specs/281-ci-governance-hardening-tail/spec.md` FR-281.1 through FR-281.8. ADR precedent: `docs/architecture/02_ADRs/ADR-037-*.md` D-14 (catalog-drift-guard direct-invocation / single-OS / anchor pattern). No new environment variables introduced — see `docs/devops/environment-variables.md`.

---

## Platform Guides

### GitHub Actions (Recommended)

**Best For**: Projects hosted on GitHub, flexible workflow needs

**Setup**:
1. Create `.github/workflows/ci.yml`
2. Define workflow stages (lint, test, build, deploy)
3. Add repository secrets (Settings → Secrets and Variables)

**Example Workflow**:
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run lint

  deploy-staging:
    needs: test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Staging
        run: |
          # Platform-specific deployment command
          echo "Deploy to staging"

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Production
        run: |
          # Platform-specific deployment command
          echo "Deploy to production"
```

**Resources**:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

### Vercel (Frontend/Full-Stack)

**Best For**: Next.js, React, Vue, static sites

**Setup**:
1. Install Vercel CLI: `npm i -g vercel`
2. Link project: `vercel link`
3. Configure via `vercel.json` or dashboard

**Auto-Deploy**:
- **PR**: Auto-deploys to preview URL
- **main branch**: Auto-deploys to production

**Configuration** (`vercel.json`):
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "{{FRAMEWORK}}",
  "regions": ["{{REGION}}"]
}
```

**Resources**:
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Integration](https://vercel.com/docs/concepts/git/vercel-for-github)

---

### Railway (Backend/Full-Stack)

**Best For**: Node.js, Python, Go, Docker-based apps

**Setup**:
1. Connect GitHub repository
2. Configure build command
3. Set environment variables
4. Define services in `railway.toml`

**Resources**:
- [Railway Documentation](https://docs.railway.app/)

---

### GitLab CI

**Best For**: Projects on GitLab

**Setup**: Create `.gitlab-ci.yml`

**Example**:
```yaml
stages:
  - test
  - deploy

test:
  stage: test
  script:
    - npm ci
    - npm test

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

---

## Essential CI/CD Components

### 1. Linting
```yaml
- name: Lint Code
  run: npm run lint
```

### 2. Type Checking
```yaml
- name: Type Check
  run: npm run typecheck
```

### 3. Unit Tests
```yaml
- name: Run Tests
  run: npm test
```

### 4. Build Verification
```yaml
- name: Build Application
  run: npm run build
```

### 5. Security Scanning
```yaml
- name: Security Audit
  run: npm audit --audit-level=moderate
```

---

## Environment Variables in CI/CD

### GitHub Actions
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

### Vercel
- Set via dashboard: Settings → Environment Variables
- Or CLI: `vercel env add VARIABLE_NAME`

---

## Best Practices

### DO ✅
- Run tests before deployment
- Use separate workflows for staging and production
- Cache dependencies to speed up builds
- Set up failure notifications
- Use environment-specific secrets

### DON'T ❌
- Commit secrets to repository
- Skip tests in CI
- Deploy directly to production without staging
- Ignore failed builds
- Use hardcoded credentials

---

## Monitoring CI/CD

Track these metrics:
- **Build Time**: Target <5 minutes
- **Success Rate**: Target >95%
- **Deployment Frequency**: Measure velocity
- **Mean Time to Recovery**: Track incident response

---

## Troubleshooting

### Build Fails on CI but Works Locally
- Check Node.js versions match
- Verify all dependencies in package.json
- Check environment variables are set
- Review CI logs for specific errors

### Slow Builds
- Enable dependency caching
- Parallelize test suites
- Optimize build commands
- Use smaller Docker base images

---

## Next Steps

After setting up CI/CD:
1. ✅ Add status badges to README
2. ✅ Configure branch protection rules
3. ✅ Set up deployment notifications
4. ✅ Document deployment process in README
5. ✅ Train team on CI/CD workflows

---

**Template Instructions**: Choose ONE platform and set up basic CI/CD. Expand with additional checks as project matures.
