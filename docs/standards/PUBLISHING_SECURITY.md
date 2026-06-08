# Publishing Security and Privacy Checklist

**Status**: Active
**Scope**: public pushes, release preparation, and review-ready publication for `tachi-rust`

Use this checklist before publishing to GitHub or cutting a release.

## Security and privacy gate

- No secrets, credentials, tokens, or private keys in committed files.
- No personal data, customer data, or private assessment output in examples, fixtures, screenshots, SARIF files, logs, or generated reports.
- Security vulnerabilities use GitHub private vulnerability reporting, not public issues.
- Public examples must be synthetic or already committed as redistributable fixtures.
- Any leaked credential must be rotated before publication, even if the commit is later rewritten.

## Rust validation gate

Run the Rust-native validation path from the repository root:

```bash
cargo test -q
cargo clippy --all-targets -- -D warnings
make llvm-cov
```

The coverage report must stay above the project floor. Current publishing work uses an 85% floor for total coverage while the Rust/Tauri-only roadmap continues removing Python surfaces.

## Repository hygiene gate

- `README.md` remains in the repository root.
- New long-form markdown documentation lives under `docs/`.
- Roadmap, planning, and product feature documents live under `docs/roadmap/`.
- Changelog updates use `CHANGELOG.md` under `## Unreleased`.
- Conventional commits describe the user-visible value of the change.

## GitHub publication gate

- Confirm `git status --short --branch` is clean before and after publishing.
- Push only reviewed, tested commits to `origin/main`.
- Use GitHub private vulnerability reporting for embargoed issues.
- Do not include local paths, private tokens, unredacted usernames, or private project names in public release notes.
