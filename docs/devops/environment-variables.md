# Environment Variables Contract

**Last Updated**: 2026-05-10
**Owner**: DevOps Agent
**Scope**: Adopter-facing, test-only, and CI-only environment variables for the upstream template repository.

---

## Overview

This document is the single source of truth for environment variables read by template scripts, CI workflows, and test harnesses. Variables fall into two categories:

1. **Adopter-facing** — variables that adopter projects set in their own environments (e.g., `AOD_BOOTSTRAP_*`, `CI`, `FORCE_RETAG`, `AOD_FETCH_TIMEOUT`). The bulk of these are documented in `CI_CD_GUIDE.md` → "Update-Script Environment Variables" and in `docs/guides/DOWNSTREAM_UPDATE.md`. Adopter-facing variables introduced by individual hardening features (e.g., F-256 `AOD_FETCH_TIMEOUT`) are mirrored below for cross-reference.
2. **Test-only / CI-only** — variables used solely by the test harness or CI workflows for determinism, fixture regeneration, or matrix isolation. These are NOT public contract and NOT for production use. Documented below.

---

## F-256 Source-Pattern-Hardening Adopter Variable

**Added in Feature 256** (Source-Pattern Hardening, PR #257, merged 2026-05-05).

This variable is **adopter-facing** — adopters MAY set it in their own environments (typically CI runners) to bound the wall-clock cost of `git clone` operations performed by `aod_template_fetch_upstream` (invoked transitively by `/aod.update` and `make update`). It is read by `.aod/scripts/bash/template-git.sh` and validated against a strict regex BEFORE any clone is attempted (Q-3 footgun-rejection ruling).

| Variable | Default | Read at | Purpose |
|----------|---------|---------|---------|
| `AOD_FETCH_TIMEOUT` | `60` (seconds; positive integer) | `.aod/scripts/bash/template-git.sh:98` (within `aod_template_fetch_upstream`) | Caps the wall-clock duration of the `git clone` subprocess that fetches the upstream template. On expiry, the watchdog SIGTERMs the clone PID, the partial checkout at `destdir` is `rm -rf`'d, and the function returns exit `9` with stderr `[aod] ERROR: upstream fetch timed out after ${seconds}s for url=<url> ref=<ref>`. Default of 60s matches the pre-F-256 implicit ceiling typical adopters expect; CI runners that want a tighter ceiling (e.g., for fail-fast on hung upstreams) can pass `AOD_FETCH_TIMEOUT=10` or similar. |

**Validation contract** (per ADR-040 + spec FR-7 + Q-3 ruling):

- Regex: `^[1-9][0-9]*$` (positive integer; rejects `0`, leading-zero forms like `01`, signed forms like `+5`, decimals, non-numeric strings, and the empty string).
- Validation runs BEFORE the clone is attempted — invalid values cause exit `1` with stderr `[aod] ERROR: AOD_FETCH_TIMEOUT must be a positive integer (default 60); rejected: '<value>'`. The clone subprocess never starts, so the failure is fast and free of partial-checkout cleanup concerns.
- Footgun rejection: `AOD_FETCH_TIMEOUT=0` is treated as malformed (not as "no timeout") because a zero-second timeout would unconditionally kill every clone before it could resolve DNS. The Q-3 PRD adjudication explicitly chose loud-rejection over silently treating it as the default.

**Exit-code contract**:

| Exit | Meaning |
|------|---------|
| `0` | Clone succeeded within the configured budget. |
| `1` | `AOD_FETCH_TIMEOUT` rejected by validation (not numeric, zero, leading-zero, etc.). The clone never started. |
| `9` | Clone exceeded the configured timeout. The watchdog SIGTERM'd the clone PID and removed the partial checkout. |

**Adopter usage examples**:

```bash
# CI runner — tight ceiling for fail-fast on hung upstream:
AOD_FETCH_TIMEOUT=15 make update

# Slow corporate proxy — relaxed ceiling:
AOD_FETCH_TIMEOUT=120 /aod.update

# Default — most adopter workstations:
make update    # 60s ceiling applied automatically
```

**Watchdog process-leak invariant** (per L-1 mitigation in spec): if the outer script (`init.sh` or `update.sh`) is interrupted (Ctrl+C) BEFORE the watchdog fires, `aod_template_fetch_upstream` traps `INT TERM EXIT` and kills the watchdog subshell on the way out — preventing orphaned `sleep ${AOD_FETCH_TIMEOUT}` processes from continuing in the background. Adopters should NOT rely on `wait` against the watchdog PID directly; the in-function trap is the canonical cleanup path.

**Reference**: `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` §Stream 4 Watchdog. Spec FR-7 + AC-7.1..AC-7.5 + SC-8 + SC-9 in `specs/256-source-pattern-hardening/spec.md`. Test coverage: `crates/tachi-shell/tests/template_git_clone_timeout.rs` (Rust-native watchdog timeout, exit-1 footgun rejection for `0` / non-numeric / leading-zero, fast-clone happy path, and cleanup invariants).

---

## F-248 Substitution-Surface Test Variables

**Added in Feature 248** (Substitution Surface Hardening, PR #249, merged 2026-05-04).

These variables are read by `scripts/init.sh` and used by the Rust init suite (`crates/tachi-shell/tests/init_substitution.rs`, `crates/tachi-shell/tests/init_constitution.rs`, and `tests/fixtures/regenerate-baseline.sh`) to make placeholder substitution byte-deterministic. They are **test-only** — production invocations of `scripts/init.sh` MUST NOT set them.

| Variable | Default | Read at | Purpose |
|----------|---------|---------|---------|
| `AOD_RATIFICATION_DATE_OVERRIDE` | unset (falls back to `date +%Y-%m-%d`) | `scripts/init.sh:123` | Pins the constitution `RATIFICATION_DATE` substitution to a fixed value (typically `2026-05-04` for the F-248 baseline). Used by `tests/fixtures/regenerate-baseline.sh` and by the Rust init fixtures to produce byte-deterministic init output. NOT for production use — production invocations rely on the `date(1)` fallback. |
| `AOD_CURRENT_DATE_OVERRIDE` | unset (falls back to `date +%Y-%m-%d`) | `scripts/init.sh:124` | Pins the `CURRENT_DATE` substitution to a fixed value. Same pattern and constraints as `AOD_RATIFICATION_DATE_OVERRIDE`. NOT for production use. |

**Why two variables, not one**: `RATIFICATION_DATE` and `CURRENT_DATE` are semantically distinct — the constitution's ratification date is a one-time historical record, while `CURRENT_DATE` is a refresh-on-init timestamp. Bundling them into a single override would conflate the two and risk masking a regression where one is updated and the other is not. The two-variable contract is intentional and stable.

**Production invariant**: `scripts/init.sh` MUST NOT change the fallback expression (`$(date +%Y-%m-%d)`) without a coordinated update to `regenerate-baseline.sh`. Any change to the date-formatting string would invalidate the entire `tests/fixtures/init-baseline-tree/` snapshot.

**Local test invocation** (matches `tests/fixtures/regenerate-baseline.sh:95-96`):

```bash
AOD_RATIFICATION_DATE_OVERRIDE=2026-05-04 \
  AOD_CURRENT_DATE_OVERRIDE=2026-05-04 \
  bash scripts/init.sh
```

**CI invocation**: the Rust init matrix workflow does NOT set these variables directly — instead, the Rust fixtures invoke them via `scripts/init.sh` helpers after the test harness sets a deterministic value. This isolates per-test determinism from cross-test fixture coupling.

**Reference**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` §Test Coverage. Spec FR-001..FR-011 in `specs/248-substitution-surface-hardening/spec.md`.

---

## F-129 Update-Script Test-Harness Overrides

**Added in Feature 129** (Downstream Template Update Mechanism).

These variables are read by `scripts/check-manifest-coverage.sh`, `scripts/check-extract-coverage.sh`, and the BATS test harness for fixture isolation. They are **NOT public contract** — adopter projects MUST NOT rely on them, and they may change without notice between template releases.

| Variable | Default | Purpose |
|----------|---------|---------|
| `AOD_COVERAGE_FILES` | derived from `git ls-files` | BATS-only override for the file list passed to coverage validators. Newline-separated. |
| `AOD_COVERAGE_MANIFEST` | `<repo_root>/.aod/template-manifest.txt` | BATS-only override for the manifest path under test. |
| `AOD_COVERAGE_REPO_ROOT` | `git rev-parse --show-toplevel` | BATS-only override for the repo-root path. |
| `AOD_COVERAGE_EXTRACT_SH` | `<repo_root>/scripts/extract.sh` | BATS-only override for the `extract.sh` path under test (F128). |
| `AOD_COVERAGE_EXTRACTIGNORE` | `<repo_root>/.extractignore` | BATS-only override for the `.extractignore` path under test (F128). |

**Why these exist**: the BATS suite (`tests/integration/*.bats`) needs to construct synthetic fixtures under `$BATS_TEST_TMPDIR` and run the validators against them, not against the live repo. The override variables let each test build a self-contained fixture graph without touching production paths.

---

## F-282 / F-5 Pre-commit Secret-Scanning — No New Environment Variables

**Added in Feature 282 / F-5** (Pre-commit Secret-Scanning Defaults, PR #283, merged 2026-05-10). For cross-reference: F-5 introduces **no new environment variables** of any kind (adopter-facing, test-only, or CI-only). The adjacent contracts F-5 interacts with are:

- `SKIP=gitleaks` — pre-existing pre-commit framework env var (NOT tachi-specific). Single-commit bypass for the gitleaks hook only — other hooks still run. Documented in `docs/standards/PRECOMMIT_HOOKS.md` §4.1 as the recommended bypass for one-off commits with intentional credential-shaped content.
- `pre-commit` framework version floor: enforced via the `pre-commit --version` shell call inside `scripts/init.sh`, NOT via an environment variable. Below v3.5.0 the init script logs a WARN with upgrade guidance and continues — does NOT abort.
- `--precommit` / `--no-precommit` flags on `scripts/init.sh`: CLI-level, NOT env-var-level. The flags affect first-run init only; post-init opt-out is `pre-commit uninstall`.

The CI parity workflow at `.github/workflows/gitleaks.yml` reads no environment variables either — gitleaks version (`v8.30.1`) and SHA256 checksum (`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`) are hardcoded constants in the workflow YAML, intentionally NOT externalized to env vars or repository secrets. Bumping gitleaks requires editing both constants together (see `docs/devops/CI_CD_GUIDE.md` → "Gitleaks CI Parity Workflow (F-282 / F-5)" → Bumping gitleaks).

**Reference**: `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` §Decision. Spec FR-001..FR-013 in `specs/282-pre-commit-secret-scanning-defaults/spec.md`. Policy log: `docs/standards/PRECOMMIT_HOOKS.md`.

---

## Cross-References

- **Adopter-facing update env vars**: `docs/devops/CI_CD_GUIDE.md` → "Update-Script Environment Variables" (`CI`, `FORCE_RETAG`, `AOD_UPDATE_TMP_DIR`, `AOD_BOOTSTRAP_*`, `AOD_UPSTREAM_URL`, `YES`, `SKIP_MARKER`).
- **Adopter-facing fetch-timeout var (F-256)**: `AOD_FETCH_TIMEOUT` documented above. Read by `.aod/scripts/bash/template-git.sh` to bound `git clone` wall-clock cost. Default 60s; positive-integer validation; exit 9 on timeout, exit 1 on invalid value.
- **Archived legacy guidance**: `docs/guides/Archive/STACK_PACK_CONSUMER_GUIDE_FASTAPI_REACT.md` preserves the historical FastAPI pack E2E environment-variable notes.
- **`/aod.deliver` exit codes** (consumed by CI scripts, not env vars): `docs/devops/CI_CD_GUIDE.md` → "/aod.deliver Exit-Code Contract".
- **F-5 / F-282 pre-commit secret-scanning** (no new env vars; framework-level `SKIP=gitleaks` bypass only): `docs/standards/PRECOMMIT_HOOKS.md` §4. CI parity workflow: `docs/devops/CI_CD_GUIDE.md` → "Gitleaks CI Parity Workflow (F-282 / F-5)".

---

**Maintained By**: DevOps Agent
