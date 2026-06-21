# Bill of Materials

**Status**: Active publish inventory
**Last Updated**: 2026-06-21
**Purpose**: enumerate the repository surfaces that are expected to ship, be
reviewed, or be validated before publishing `tachi-rust` to remote origin
**Scope**: source code, docs, tests, CI, security posture, and release gates

## Publish Model

`tachi-rust` publishes as a Rust workspace with a thin Tauri desktop shell and
documentation-first release controls. The public surface is intentionally broad
because the repository ships:

- Rust workspace code and shared command logic
- Tauri desktop bridge code
- CLI entrypoints
- docs, roadmap, and release policy artifacts
- security and privacy posture documentation
- CI and secret-scanning workflows
- test fixtures and regression data

This BOM is the authoritative inventory for publication review. If a file or
directory is not listed here, it is either internal implementation detail,
temporary scratch state, or a local-only worktree artifact.

## Top-Level Inventory

| Path | Role | Publish status | Notes |
|---|---|---|---|
| `Cargo.toml` | Rust workspace manifest | Publishable | Canonical workspace root for `tachi-core`, `tachi-cli`, `tachi-shell`, and `src-tauri`. |
| `README.md` | Public repository landing page | Publishable | Must stay aligned with the actual build and usage path. |
| `LICENSE` | License text | Publishable | Required public artifact. |
| `SECURITY.md` | Vulnerability disclosure policy | Publishable | Public security policy and private disclosure channel. |
| `CHANGELOG.md` | Release history | Publishable | Keep release notes redaction-safe. |
| `docs/` | Public documentation | Publishable | Long-form docs, roadmap, standards, and review artifacts. |
| `crates/` | Workspace library and binary crates | Publishable | Source of the Rust implementation. |
| `src-tauri/` | Desktop bridge shell | Publishable | Thin Tauri layer only. |
| `.github/` | CI and release workflows | Publishable | Public automation surface. |
| `.claude/` | Agent configuration and runtime rules | Publishable with review | Must avoid secrets and private credentials. |
| `.aod/` | AOD support files | Publishable with review | Contains governance and hook logic; verify no private data. |
| `schemas/` | Validation schemas and taxonomies | Publishable | Needed for parser/report contracts. |
| `tests/` | Fixtures and regression tests | Publishable with review | Synthetic or redacted only; no private source material. |
| `INSTALL_MANIFEST.md` | Install command contract | Publishable with review | Machine-parseable file list that must match distributable paths. |
| `scripts/` | Transitional shell and helper scripts | Publishable with review | Keep no secret-bearing defaults. |
| `brand/` | Visual assets | Publishable | Verify image captions and alt text do not expose private data. |
| `examples/` | Example output and sample artifacts | Publishable with review | Must remain synthetic or sanitized. |

## Source BOM

### Workspace and runtime source

| Path | Contents | Reviewer focus |
|---|---|---|
| `crates/tachi-core/` | Parsers, scoring, reporting, taxonomy, SARIF, coverage helpers | Parser hardening, output shape stability, no panic-based user-facing parsing. |
| `crates/tachi-cli/` | CLI entrypoints and argument-forwarding binaries | Flag correctness, help text, command parity, no duplicated business logic. |
| `crates/tachi-shell/` | Shared command facade and bridge adapter | Shared dispatch, shared errors, identical CLI/Tauri semantics. |
| `src-tauri/` | Thin desktop shell | Registration-only bridge, no business logic drift. |
| `schemas/` | Finding schemas and taxonomy catalogs | Schema compatibility, crosswalk stability, fixture coverage. |

### Transitional helper surface

| Path | Contents | Reviewer focus |
|---|---|---|
| `scripts/` | Init/bootstrap helpers and transitional tooling | No secret leakage, no unreviewed shell injection, clear retirement path. |
| `.aod/` | Governance and operational helpers | Hook safety, no private state, no accidental publish of local settings. |
| `.claude/` | Agent and permissions configuration | Public-safe policy, no credentials, no private repo-specific tokens. |

### Test and fixture surface

| Path | Contents | Reviewer focus |
|---|---|---|
| `tests/fixtures/` | Synthetic regression fixtures | Synthetic only, deterministic, redaction-safe. |
| `tests/scripts/` | Legacy and transitional test fixtures | Keep compatibility data sanitized and representative. |
| `crates/*/tests/` | Rust integration and unit tests | Coverage of parser, command, reporting, and bridge contracts. |
| `crates/*/benches/` | Benchmark gates | Must be stable enough for regression detection. |

## Documentation BOM

| Path | Purpose | Publish note |
|---|---|---|
| `docs/roadmap/implementation-backlog.md` | Backlog navigation hub | Canonical link target for active implementation sequencing. |
| `docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md` | Active parity roadmap | Canonical Rust/Tauri parity rebaseline and supersession plan. |
| `docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md` | Active parity execution cards | Copy-paste Beads issue templates for the parity phases. |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md` | Active docs hygiene roadmap | Separate docs-only sweep for stale workflow-version references. |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md` | Active docs sweep cards | Copy-paste Beads issue templates for docs/version hygiene. |
| `docs/roadmap/2026-06-15-rust-tauri-parity-remediation-roadmap.html.md` | Archived parity roadmap | Historical snapshot of the earlier parity plan. |
| `docs/roadmap/2026-06-15-rust-tauri-parity-issue-cards.md` | Archived parity cards | Historical Beads-ready backlog for the earlier parity track. |
| `docs/roadmap/2026-06-04-rust-tauri-issue-pack.md` | Historical tracker-neutral pack | Archived provenance for the earlier migration plan. |
| `docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md` | Archived implementation roadmap | Historical planning snapshot, not active scope. |
| `docs/roadmap/2026-06-08-rust-tauri-only-issue-cards.md` | Archived execution cards | Historical Beads-ready backlog from the superseded plan. |
| `docs/roadmap/2026-06-08-python-surface-inventory.md` | Frozen migration evidence | Historical reference, not the active surface. |
| `docs/publish-readiness-checklist.html.md` | Publish gate checklist | Required pre-push security, privacy, docs, and CI gate. |
| `docs/standards/PUBLISHING_SECURITY.md` | Security and privacy publish gate | Must remain the security policy source for public pushes. |
| `docs/standards/PRECOMMIT_HOOKS.md` | Secret-scanning hook guide | Security gate for staged content and local commits. |
| `docs/changelog.html` | Release chronology | Must remain redaction-safe. |
| `docs/devops/SECURITY_POSTURE_2026Q2.md` | Public security posture summary | Review for accidental disclosure before publication. |

## CI and Release BOM

| Path | Purpose | Publish note |
|---|---|---|
| `.github/workflows/gitleaks.yml` | Full-repo secret scanning | Required publication gate. |
| `.github/workflows/rust-clippy.yml` | Rust lint gate | Prevents warnings from shipping. |
| `.github/workflows/release-please.yml` | Release orchestration | Main-push release automation without release-PR branch churn; release gate now covers manifest and checksum parity. |
| `.github/workflows/tachi-mmdc-preflight.yml` | Mermaid preflight | Protects docs and renderable diagram outputs. |
| `.github/workflows/tachi-pytest.yml` | Transitional compatibility tests | Must be reviewed for retirement or narrowing as migration completes. |

## Security and Privacy BOM

The following surfaces require explicit review before publication:

- Any file that may contain tokens, credentials, private keys, or API secrets.
- Any example, fixture, or log that may contain customer data, personal data,
  or private assessment output.
- Any workflow that can emit secrets into logs or artifacts.
- Any documentation that describes private internal process, unreleased release
  state, or unredacted operational details.

The repository policy for these surfaces is:

1. Keep secrets out of committed files.
1. Keep public examples synthetic or redacted.
1. Route security issues through private disclosure, not public issue trackers.
1. Re-scan before publish and again after release merges.

## Validation BOM

| Gate | Evidence | Acceptance |
|---|---|---|
| Rust unit and integration tests | `cargo test -q` | Must pass cleanly. |
| Rust e2e and bridge checks | `cargo test -p tachi-shell --test init_substitution` and `cargo test -p tachi-core --test rt009_docs` | Must pass for CLI/tidy report contract parity surfaces. |
| Parser hardening regression | `cargo test -p tachi-core compute_delta_counts_trims_case_and_ignores_unknown_statuses -- --nocapture` | Must pass for panic-free delta counting and status normalization. |
| Lint gate | `cargo clippy --all-targets -- -D warnings` | No warnings allowed. |
| Coverage gate | `make llvm-cov` | Coverage remains above the repo floor. |
| Reporting goldens | `cargo test -p tachi-core --test reporting_goldens -- --nocapture` | Canonical report, threat, risk, coverage, and infographic outputs remain stable. |
| Diff hygiene | `git diff --check` | No whitespace or patch-format issues. |
| Secret scan | `pre-commit run --all-files` or `gitleaks` / CI workflow | No secrets or private data leak into the publish set. |
| Docs gate | README and docs cross-links | Public docs match the shipped behavior. |
| Docs/version sweep | `make docs-version-gate` | Maintained docs are current and examples stay synthetic. |
| CI gate | GitHub Actions run status | Release and security workflows are green. |
| Release-please gate | `release-please.yml` push filter | Docs-only publishes do not churn release refs and push runs avoid PR-branch churn. |
| Workflow hardening | `rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|::set-output" .github/workflows` | No legacy checkout, toolchain, SARIF, or set-output usage remains. |

## Exclusions

- Local worktree scratch files.
- Generated caches that are ignored by git.
- Temporary benchmark data created outside the checked-in benchmark fixtures.
- Anything in the tree explicitly labeled archived, retired, or compatibility
  only, unless it is being published as historical evidence.

## Publish Rule

If a surface is listed as publishable, it must be reviewed for security,
privacy, doc accuracy, and release readiness before `main` is pushed to
`origin`.

## Publish Evidence Checklist (required before push)

- [ ] `rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|::set-output" .github/workflows` returns no matches.
- [ ] `docs/roadmap/implementation-backlog.md` points at the active parity roadmap and issue cards.
- [ ] `docs/roadmap/implementation-backlog.md` points at the active parity roadmap, the active docs sweep roadmap, and archived provenance docs.
- [ ] The active parity roadmap is `docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md`.
- [ ] The active parity Beads cards are `docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md`.
- [ ] The active docs-sweep roadmap is `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md`.
- [ ] The active docs-sweep Beads cards are `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md`.
- [ ] Archived roadmap docs are clearly marked as historical only.
- [ ] `make docs-version-gate` passes.
- [ ] `git status --short --branch` has no unexpected untracked or dirty state.
- [ ] `cargo test -q` and `make llvm-cov` are green on the release candidate branch.
- [ ] `cargo clippy --all-targets -- -D warnings` is clean.
- [ ] Public examples and fixtures are synthetic or redacted.
