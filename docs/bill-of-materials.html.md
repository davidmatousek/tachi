# Bill of Materials

**Status**: Active publish inventory
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
| `docs/roadmap/implementation-backlog.md` | Backlog navigation hub | Canonical link target for implementation sequencing. |
| `docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md` | Implementation roadmap | Canonical staging, dependency, and validation plan. |
| `docs/roadmap/2026-06-08-rust-tauri-only-issue-cards.md` | Execution cards | Copy-paste Beads issue templates. |
| `docs/roadmap/2026-06-04-rust-tauri-issue-pack.md` | Historical tracker-neutral pack | Keep synchronized with the canonical roadmap. |
| `docs/roadmap/2026-06-08-python-surface-inventory.md` | Frozen migration evidence | Historical reference, not the active surface. |
| `docs/standards/PUBLISHING_SECURITY.md` | Security and privacy publish gate | Must remain the security policy source for public pushes. |
| `docs/standards/PRECOMMIT_HOOKS.md` | Secret-scanning hook guide | Security gate for staged content and local commits. |
| `docs/changelog.html` | Release chronology | Must remain redaction-safe. |
| `docs/devops/SECURITY_POSTURE_2026Q2.md` | Public security posture summary | Review for accidental disclosure before publication. |

## CI and Release BOM

| Path | Purpose | Publish note |
|---|---|---|
| `.github/workflows/gitleaks.yml` | Full-repo secret scanning | Required publication gate. |
| `.github/workflows/rust-clippy.yml` | Rust lint gate | Prevents warnings from shipping. |
| `.github/workflows/release-please.yml` | Release orchestration | Keep release metadata aligned with docs. |
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
| Lint gate | `cargo clippy --all-targets -- -D warnings` | No warnings allowed. |
| Coverage gate | `make llvm-cov` | Coverage remains above the repo floor. |
| Diff hygiene | `git diff --check` | No whitespace or patch-format issues. |
| Secret scan | `pre-commit run --all-files` or `gitleaks` / CI workflow | No secrets or private data leak into the publish set. |
| Docs gate | README and docs cross-links | Public docs match the shipped behavior. |
| CI gate | GitHub Actions run status | Release and security workflows are green. |

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

