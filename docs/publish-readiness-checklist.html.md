# Publish Readiness Checklist

**Status**: Active release gate
**Last Updated**: 2026-06-23
**Purpose**: confirm `tachi-rust` is ready to publish to `origin/main`
**Scope**: security, privacy, docs, tests, coverage, CI, and release hygiene

Use this checklist before publishing to GitHub or cutting a release.

## 0. Canonical publish sequence

- [ ] `pre-commit run --all-files` or the equivalent `gitleaks` scan passes.
- [ ] `make publish-gate` passes on the release candidate branch.
- [ ] `cargo test -p tachi-shell` passes after the script executor boundary
      slice and coverage-invariant cleanup.
- [ ] `make scaffold-dependency-gate` passes before publishing scaffold or template changes.
- [ ] `git push origin main --follow-tags` is the intended publish command.
- [ ] `gh run list --branch main --limit 10` is ready for post-push monitoring.
- [ ] `gh run watch <run-id>` will be used until the publish workflow completes.

## 1. Repository hygiene

- [ ] `git status --short --branch` is clean except for intentional, reviewed work.
- [ ] `git diff --check` passes.
- [ ] No untracked scratch files, temporary exports, or local-only artifacts are
      present in the publish set.
- [ ] The branch name and commit messages are conventional and self-explanatory.

## 2. Security and privacy

- [ ] No secrets, API keys, tokens, private keys, or credentials exist in the
      commit range to be published.
- [ ] No personal data, customer data, or private assessment output appears in
      examples, fixtures, screenshots, logs, or generated docs.
- [ ] Public-facing examples are synthetic, redacted, or already committed as
      safe fixtures.
- [ ] Security issues that are not safe for public disclosure stay in private
      vulnerability reporting.
- [ ] The BOM at [bill-of-materials.html.md](./bill-of-materials.html.md) was
      reviewed for any sensitive surfaces that need redaction.
- [ ] `README.md`, `SECURITY.md`, `CHANGELOG.md`, and the public docs under
      `docs/` do not leak private paths, credentials, internal-only status, or
      unreleased operational details.

## 3. Secret scanning

- [ ] `pre-commit run --all-files` passes, or the equivalent gitleaks command has
      been run successfully.
- [ ] The secret scan covers committed examples, fixtures, docs, generated
      reports, and workflow files.
- [ ] `.github/workflows/gitleaks.yml` is present and matches the local secret
      scan policy.
- [ ] Any legitimate placeholder or fixture match is documented and justified.
- [ ] No new warnings were introduced by hook configuration changes.
- [ ] `rg "actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|::set-output" .github/workflows` returns no matches.

## 4. Rust validation

- [ ] `cargo test -q` passes.
- [ ] `cargo test --workspace --all-targets` passes or the equivalent
      `.github/workflows/rust-workspace.yml` PR gate is green.
- [ ] Parser hardening regression tests pass, including delta-count normalization and panic-free status handling.
- [ ] Reporting goldens pass for coverage, report, threat, risk, and infographic outputs.
- [ ] `cargo clippy --all-targets -- -D warnings` passes.
- [ ] `make llvm-cov` passes and the coverage floor remains above the project
      baseline.
- [ ] Any benchmark or regression gate referenced by the roadmap has its current
      baseline recorded.
- [ ] `INSTALL_MANIFEST.md` only references files/directories that exist in the
      repository and expected install command paths.
- [ ] `make scaffold-dependency-gate` passes and blocks scaffold ranges that admit
      currently known vulnerable `next` or `vitest` versions.

## 5. Documentation readiness

- [ ] `README.md` matches the actual build, install, usage, and release path.
- [ ] `SECURITY.md` matches the current private-reporting and privacy policy.
- [ ] `CHANGELOG.md` is redaction-safe and reflects only releasable notes.
- [ ] `docs/roadmap/implementation-backlog.md` points at the active AQ
      roadmap, archived parity roadmap, active docs sweep roadmap, and
      archived provenance docs.
- [ ] The active AQ roadmap is
      `docs/roadmap/2026-06-22-adversarial-architecture-test-quality-roadmap.html.md`.
- [ ] The archived parity roadmap is
      `docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md`.
- [ ] The archived parity Beads-ready issue set is
      `docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md`.
- [ ] The active docs-sweep roadmap is
      `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md`.
- [ ] The active docs-sweep Beads-ready issue set is
      `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md`.
- [ ] The archived roadmap docs are clearly marked historical only.
- [ ] The roadmap and issue cards reflect the current phase sequencing.
- [ ] The DOC-00X documentation-update plan remains separate from the parity
      and docs-sweep tracks.
- [ ] `docs/bill-of-materials.html.md` and `docs/publish-readiness-checklist.html.md`
      agree on the publish gate, security surfaces, and remote publication flow.
- [ ] The shell executor seam is documented in the BOM and covered by focused
      shell crate tests.
- [ ] The infographic prompt scaffold seam is documented in the BOM and
      covered by focused core crate tests.
- [ ] The infographic payload seam is documented in the BOM and covered by
      focused core crate tests.
- [ ] `make docs-version-gate` passes.
- [ ] `make docs-archive-version-gate` passes.
- [ ] Public docs do not promise unsupported features or outdated workflows.
- [ ] `tachi-core` reporting and scoring consumers compile against root facade exports instead of module internals.
- [ ] Release notes, changelog entries, and user-facing examples are current and
      redaction-safe.

## 6. CI and GitHub readiness

- [ ] `.github/workflows/gitleaks.yml` is green for the publish branch.
- [ ] `.github/workflows/rust-workspace.yml` is green and is not
      path-filtered on pull requests.
- [ ] `.github/workflows/rust-clippy.yml` is green.
- [ ] `.github/workflows/rust-clippy.yml` fails closed on warnings while still
      uploading SARIF with `if: always()`.
- [ ] The latest main-push Actions run does not emit Node 20 deprecation warnings from the updated workflows.
- [ ] `.github/workflows/release-please.yml` ignores docs-only and roadmap-only
      pushes and does not churn release-PR branches on main pushes.
- [ ] `.github/workflows/tachi-mmdc-preflight.yml` is green.
- [ ] `.github/workflows/tachi-pytest.yml` is either retired or scoped strictly to
      transitional compatibility with a documented deprecation plan.
- [ ] The docs/version gate is green on the current branch.
- [ ] The release artifact gate and checksum matrix pass via `make publish-gate`.
- [ ] `src-tauri/tauri.conf.json` and `src-tauri/capabilities/main.json`
      remain least-privilege and do not grant filesystem or shell permissions
      without the corresponding AQ-022/AQ-023 policy tests.
- [ ] The scaffold dependency-floor audit passes via `make scaffold-dependency-gate`
      and is included in `make publish-gate`.
- [ ] Any release workflow required for the branch has succeeded or is queued
      without failures.
- [ ] GitHub Actions status was checked after the last merge or rebase.
- [ ] No workflow emits secrets, private paths, or private data into logs.

## 7. Remote publication

- [ ] The branch to publish is up to date with the intended base branch.
- [ ] The publish commit history is linear or intentionally merged.
- [ ] The push target is `origin/main` or a clearly named release branch.
- [ ] `make publish-gate` runs clean on the branch being published, including
      workflow drift, scaffold dependency-floor, and release artifact parity checks.
- [ ] The post-push CI monitor command is ready, for example:

```bash
gh run list --branch main --limit 10
gh run watch <run-id>
```
- [ ] The CI monitor runs until the relevant release, lint, security, and docs
      jobs all finish successfully.

## 8. Publish decision

- [ ] The repo is safe to publish.
- [ ] The repo is documented well enough for an outside reader to use.
- [ ] The repo is passing the required validation gates.
- [ ] The repo can be pushed to `origin` without exposing secrets or private
      material.

## Required exit criteria

Do not push to `origin/main` until all of the following are true:

1. Repository hygiene passes.
2. Security and privacy pass.
3. Secret scanning passes.
4. Rust validation passes.
5. Documentation is current.
6. GitHub Actions status is green or understood.

If any item fails, fix the failing gate first and rerun the checklist from the
top.
