# Bill of Materials

**Status**: Active publish inventory
**Last Updated**: 2026-06-25
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

For public readers, this document explains which surfaces are expected to ship,
which docs define the user-facing workflow, and which validation gates guard
the release path. Treat it as the contract between repository contents and the
published artifact set.

## Public-Facing Documents

These are the documents that must stay current, redaction-safe, and aligned
with the shipped release workflow before publication.

| Path | Role | Publish status | Notes |
|---|---|---|---|
| `README.md` | Repository landing page and getting-started guide | Publishable | Must describe the current install, usage, auditor workflow, and release path without stale workflow guidance. |
| `adapters/README.md` | Compatibility entrypoint for native adapters and generic fallback | Publishable | Must match the harness matrix, install surfaces, and identical core contract. |
| `docs/platform-compatibility.md` | Harness matrix and fallback behavior guide | Publishable | Must stay aligned with the adapter packs and the generic fallback path. |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | Public developer and auditor walkthrough | Publishable | Must stay aligned with the README and show the actual first-run analysis path. |
| `SECURITY.md` | Security policy | Publishable | Private vulnerability reporting only; keep public disclosure guidance current. |
| `CHANGELOG.md` | Release history | Publishable | Redaction-safe release notes only. |
| `docs/bill-of-materials.html.md` | Publish inventory | Publishable | Canonical inventory of publication surfaces and validation gates. |
| `docs/publish-readiness-checklist.html.md` | Publish readiness checklist | Publishable | Required pre-push gate for security, privacy, docs, CI, release hygiene, and public-doc alignment. |
| `docs/standards/PUBLISHING_SECURITY.md` | Security and privacy gate | Publishable | Source of truth for public-push safety rules, disclosure boundaries, and release-note hygiene. |
| `docs/standards/PRECOMMIT_HOOKS.md` | Secret-scanning hook guide | Publishable with review | Must not imply weaker scanning than the current gate. |

## Top-Level Inventory

| Path | Role | Publish status | Notes |
|---|---|---|---|
| `Cargo.toml` | Rust workspace manifest | Publishable | Canonical workspace root for `tachi-core`, `tachi-cli`, `tachi-mcp`, `tachi-shell`, and `src-tauri`. |
| `README.md` | Public repository landing page | Publishable | Must stay aligned with the actual build, auditor workflow, and usage path. |
| `LICENSE` | License text | Publishable | Required public artifact. |
| `SECURITY.md` | Vulnerability disclosure policy | Publishable | Public security policy and private disclosure channel. |
| `CHANGELOG.md` | Release history | Publishable | Keep release notes redaction-safe. |
| `docs/` | Public documentation | Publishable | Long-form docs, roadmap, standards, and review artifacts. |
| `crates/` | Workspace library and binary crates | Publishable | Source of the Rust implementation. |
| `src-tauri/` | Desktop bridge shell | Publishable | Thin Tauri layer with explicit config and least-privilege main-window capability. |
| `.github/` | CI and release workflows | Publishable | Public automation surface. |
| `.claude/` | Agent configuration and runtime rules | Publishable with review | Must avoid secrets and private credentials. |
| `.aod/` | AOD support files | Publishable with review | Contains governance and hook logic; verify no private data. |
| `schemas/` | Validation schemas and taxonomies | Publishable | Needed for parser/report contracts. |
| `tests/` | Fixtures and regression tests | Publishable with review | Synthetic or redacted only; no private source material. |
| `stacks/` | Scaffold templates and archived stack packs | Publishable with review | Template manifests must not admit known vulnerable dependency floors. |
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
| `crates/tachi-mcp/` | Standalone MCP transport and contract snapshot layer | Canonical command contract reuse, stdio startup path, registered analysis tools, request-context hardening, and artifact-emitting tool dispatch. |
| `crates/tachi-shell/` | Shared command facade and bridge adapter | Shared dispatch, shared errors, identical CLI/Tauri semantics. |
| `crates/tachi-shell/src/commands/script_executor.rs` | Script execution boundary | Process spawning, timeout, cancellation, and output capture stay behind an injected executor seam. |
| `crates/tachi-core/src/infographic/prompt_scaffold.rs` | Prompt scaffold boundary | Template loading and prompt extraction stay isolated from payload rendering with store-injected tests. |
| `crates/tachi-core/src/infographic/payload.rs` | Infographic payload boundary | Filesystem loading and payload orchestration stay separated from infographic parsing helpers. |
| `crates/tachi-core/src/facade.rs` | Stable core facade | Downstream crates should import reporting and scoring helpers through root exports instead of module internals. |
| `src-tauri/` | Thin desktop shell | Registration-only bridge, explicit `tauri.conf.json`, least-privilege `capabilities/main.json`, no business logic drift. |
| `schemas/` | Finding schemas and taxonomy catalogs | Schema compatibility, crosswalk stability, fixture coverage. |

### Transitional helper surface

| Path | Contents | Reviewer focus |
|---|---|---|
| `scripts/` | Init/bootstrap helpers and transitional tooling | No secret leakage, no unreviewed shell injection, clear retirement path. |
| `.aod/` | Governance and operational helpers | Hook safety, no private state, no accidental publish of local settings. |
| `.claude/` | Agent and permissions configuration | Public-safe policy, no credentials, no private repo-specific tokens. |
| `stacks/nextjs-supabase/scaffold/` | Next.js/Supabase scaffold template | Dependency floors must exclude known vulnerable `next` and `vitest` ranges. |

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
| `docs/roadmap/implementation-backlog.md` | Backlog navigation hub | Canonical link target for active implementation sequencing and public roadmap context. |
| `docs/roadmap/2026-06-23-aisvs-dependabot-remediation-roadmap.html.md` | Active AISVS/security roadmap | Canonical sequencing for the live Dependabot alert, AISVS C01-C12 rollout, and TDD-backed validation gates. |
| `docs/roadmap/2026-06-23-aisvs-dependabot-remediation-issue-cards.md` | Active AISVS/security issue cards | Beads-ready execution templates for the RT-00i epic and its phase slices. |
| `docs/roadmap/2026-06-23-aisvs-dependabot-remediation-issue-cards.md#phase-5-publish-readiness-and-release-gates` | Phase 5 publish-readiness slice | Tracks `RT-00i.6`, the docs and release-gate follow-up that keeps AISVS work publish-ready after each slice. |
| `docs/roadmap/2026-06-25-standalone-mcp-server-roadmap.html.md` | Active MCP roadmap | Canonical sequencing for the standalone MCP track, including scope boundaries, portability limits, and stage-gated acceptance criteria. |
| `docs/roadmap/2026-06-25-standalone-mcp-server-issue-cards.md` | Active MCP issue cards | Beads-ready execution templates for the MCP epic, features, capabilities, and task slices. |
| `docs/roadmap/2026-06-22-adversarial-architecture-test-quality-roadmap.html.md` | Archived AQ roadmap | Canonical architecture, SOLID, and test-quality remediation plan, now retained as a historical record. |
| `docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md` | Archived parity roadmap | Historical Rust/Tauri parity rebaseline and supersession plan. |
| `docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md` | Archived parity execution cards | Historical Beads issue templates for the parity phases. |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md` | Active docs hygiene roadmap | Separate docs-only sweep for stale workflow-version references. |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md` | Active docs sweep cards | Copy-paste Beads issue templates for docs/version hygiene. |
| `docs/roadmap/2026-06-15-rust-tauri-parity-remediation-roadmap.html.md` | Archived parity roadmap | Historical snapshot of the earlier parity plan. |
| `docs/roadmap/2026-06-15-rust-tauri-parity-issue-cards.md` | Archived parity cards | Historical Beads-ready backlog for the earlier parity track. |
| `docs/roadmap/2026-06-25-standalone-mcp-server-roadmap.html.md` | Active MCP roadmap | MCP core-contract, transport, policy, docs, and portability-stage plan. |
| `docs/roadmap/2026-06-25-standalone-mcp-server-issue-cards.md` | Active MCP issue cards | Tracker-ready issue templates with explicit acceptance criteria and validation paths. |
| `docs/roadmap/2026-06-04-rust-tauri-issue-pack.md` | Historical tracker-neutral pack | Archived provenance for the earlier migration plan. |
| `docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md` | Archived implementation roadmap | Historical planning snapshot, not active scope. |
| `docs/roadmap/2026-06-08-rust-tauri-only-issue-cards.md` | Archived execution cards | Historical Beads-ready backlog from the superseded plan. |
| `docs/roadmap/2026-06-08-python-surface-inventory.md` | Frozen migration evidence | Historical reference, not the active surface. |
| `docs/publish-readiness-checklist.html.md` | Publish gate checklist | Required pre-push security, privacy, docs, CI, and release gate. |
| `docs/standards/PUBLISHING_SECURITY.md` | Security and privacy publish gate | Must remain the security policy source for public pushes and release hygiene. |
| `docs/standards/PRECOMMIT_HOOKS.md` | Secret-scanning hook guide | Security gate for staged content and local commits. |
| `docs/changelog.html` | Release chronology | Must remain redaction-safe. |
| `docs/devops/SECURITY_POSTURE_2026Q2.md` | Public security posture summary | Review for accidental disclosure before publication. |

## CI and Release BOM

| Path | Purpose | Publish note |
|---|---|---|
| `.github/workflows/gitleaks.yml` | Full-repo secret scanning | Required publication gate. |
| `.github/workflows/rust-workspace.yml` | Full Rust workspace PR test gate | Required non-path-filtered behavior gate for `cargo test --workspace --all-targets`. |
| `.github/workflows/rust-clippy.yml` | Rust lint gate | Prevents warnings from shipping. |
| `.github/workflows/release-please.yml` | Release orchestration | Main-push release automation without release-PR branch churn; release gate now covers manifest and checksum parity. |
| `.github/workflows/fuzz-mutation-audit.yml` | Advisory fuzz/mutation lane | Scheduled/manual non-blocking lane for parser and reporting survivor discovery. |
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
1. Keep `README.md`, `CHANGELOG.md`, and all release-facing docs free of private paths, tokens, usernames, and unredacted operational details.

## Validation BOM

| Gate | Evidence | Acceptance |
|---|---|---|
| Rust unit and integration tests | `cargo test -q` | Must pass cleanly. |
| Full workspace PR behavior gate | `cargo test --workspace --all-targets` and `.github/workflows/rust-workspace.yml` | Pull requests run the whole Rust workspace without path filters. |
| Rust e2e and bridge checks | `cargo test -p tachi-shell --test init_substitution` and `cargo test -p tachi-core --test rt009_docs` | Must pass for CLI/tidy report contract parity surfaces. |
| MCP scaffold and contract checks | `cargo test -p tachi-mcp --test contract_snapshot --test schema_snapshot --test tools_registration --test session_policy --test stdio` and `cargo build -p tachi-mcp --features stdio` | MCP registry, stdio transport, request-id continuity, cancellation handling, schema snapshots, and contract snapshots remain deterministic. |
| Core infographic and scaffold seams | `cargo test -p tachi-core` | Prompt scaffold, infographic payload, parser, and reporting seams remain green after boundary splits. |
| Infographic payload seam | `cargo test -p tachi-core` | Payload orchestration remains behavior-compatible after moving filesystem loading and template assembly. |
| Parser hardening regression | `cargo test -p tachi-core compute_delta_counts_trims_case_and_ignores_unknown_statuses -- --nocapture` | Must pass for panic-free delta counting and status normalization. |
| Lint gate | `cargo clippy --all-targets -- -D warnings` and `.github/workflows/rust-clippy.yml` | No warnings allowed; SARIF upload remains `if: always()` but clippy status fails closed. |
| Coverage gate | `make llvm-cov` | Coverage remains above the repo floor; validated at 85.33% line coverage on 2026-06-24. |
| Reporting goldens | `cargo test -p tachi-core --test reporting_goldens -- --nocapture` | Canonical report, threat, risk, coverage, and infographic outputs remain stable through semantic projections and compact snapshots. |
| Advisory fuzz/mutation lane | `make fuzz-mutation-gate` and `.github/workflows/fuzz-mutation-audit.yml` | Commands stay documented, scheduled/manual runs remain non-blocking, and survivor reports stay offline-safe. |
| Diff hygiene | `git diff --check` | No whitespace or patch-format issues. |
| Secret scan | `pre-commit run --all-files` or `gitleaks` / CI workflow | No secrets or private data leak into the publish set, including examples, fixtures, logs, and generated docs. |
| Scaffold dependency gate | `make scaffold-dependency-gate` | Next.js/Supabase scaffold dependency ranges exclude currently known vulnerable `next` and `vitest` floors. |
| Docs gate | `README.md`, `docs/platform-compatibility.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `SECURITY.md`, `CHANGELOG.md`, and public docs cross-links | Public docs match the shipped behavior and the disclosure policy. |
| AISVS security gate | `cargo test -p tachi-core --test aisvs_registry`, `cargo test -p tachi-core --test aisvs_controls`, `cargo test -p tachi-core --test scaffold_dependency_floors`, `cargo clippy --workspace --all-features --all-targets -- -D warnings` | AISVS C01-C12 remain typed, test-backed, and fail-closed while the live `glib` advisory proof stays reproducible in Beads, the registry exposes stable per-control validation commands, and the upgrade slice remains blocked on upstream `gtk` compatibility. |
| AISVS publish-readiness follow-up | `RT-00i.6` | The Phase 5 docs/release-gate follow-up stays visible in the BOM and issue cards so publish-readiness work keeps pace with each control slice. |
| Docs/version sweep | `make docs-version-gate` + `make docs-archive-version-gate` | Maintained docs stay current; archived docs and examples retain only intentional historical references. |
| Publish gate | `make publish-gate` | The release candidate passes the full local publish-readiness suite before remote publication. |
| CI gate | GitHub Actions run status | Release, security, lint, and docs workflows are green. |
| Remote monitor | `git push origin main --follow-tags` + `gh run watch` | Post-push CI is observed to completion before the release is considered published. |
| Release-please gate | `release-please.yml` push filter | Docs-only publishes do not churn release refs and push runs avoid PR-branch churn. |
| Workflow hardening | `rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|::set-output" .github/workflows` | No legacy checkout, toolchain, SARIF, or set-output usage remains. |
| MCP readiness gate | MCP roadmap, MCP issue cards, BOM, publish checklist, and MCP CI lane | MCP publish surfaces stay in sync with the canonical command contract, release checklist, request-context hardening, portability matrix, and CI evidence before promotion. |
| MCP CI lane | `.github/workflows/rust-workspace.yml` with `tachi-mcp` package matrix | Dedicated MCP package lane covers contract snapshot, schema snapshot, stdio transport, and tool registration regressions. |

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
- [ ] `docs/roadmap/implementation-backlog.md` points at the active AISVS/security roadmap, the active docs sweep roadmap, and archived provenance docs.
- [ ] The active AISVS roadmap is `docs/roadmap/2026-06-23-aisvs-dependabot-remediation-roadmap.html.md`.
- [ ] The active AISVS Beads cards are `docs/roadmap/2026-06-23-aisvs-dependabot-remediation-issue-cards.md`.
- [ ] The active docs-sweep roadmap is `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md`.
- [ ] The active docs-sweep Beads cards are `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md`.
- [ ] The live `glib` Dependabot alert proof is captured in `crates/tachi-core/tests/scaffold_dependency_floors.rs`, and `RT-00i.2` remains open until the desktop stack can resolve a fixed `glib` line.
- [ ] Archived roadmap docs are clearly marked as historical only.
- [ ] `make docs-version-gate` passes.
- [ ] `git status --short --branch` has no unexpected untracked or dirty state.
- [ ] `cargo test -q` and `make llvm-cov` are green on the release candidate branch.
- [ ] `make scaffold-dependency-gate` is green for scaffold dependency floors.
- [ ] `cargo clippy --all-targets -- -D warnings` is clean.
- [ ] Public examples and fixtures are synthetic or redacted.
