# Research Summary: Automated Release Tagging via GitHub Actions

## Knowledge Base Findings
- No prior KB entries for GitHub Actions or release automation
- Feature 066 (Install Script and Version Tagging) is the direct predecessor — established v4.0.0 tag and install.sh --version support
- PRD 066 explicitly deferred release-please under "Out of Scope" with escalation triggers

## Codebase Analysis
- **No existing GitHub Actions workflows**: `.github/workflows/` directory does not exist
- **install.sh fully compatible**: Uses `git rev-parse --verify "refs/tags/$VERSION_TAG"` for validation, `git checkout` for tag checkout, `git describe --tags --always` for version reporting — all work with release-please annotated tags
- **CHANGELOG.md exists**: Uses Keep a Changelog format with an "Unreleased" section containing Features 066, 078, 074, 075, 071. No versioned headers yet beyond baseline
- **Single git tag**: `v4.0.0` exists as baseline (created by Feature 066)
- **Conventional commits established**: Constitution Principle IX mandates conventional commit format
- **No release-please config files**: Neither `.release-please-manifest.json` nor `release-please-config.json` exist

## Architecture Constraints
- Repository is public on GitHub — GitHub Actions available at no cost
- Single-maintainer project (@davidmatousek) — no team coordination needed for release merges
- tachi is not an npm/PyPI package — `simple` release type is correct
- GITHUB_TOKEN is automatically available — no secrets configuration needed

## Industry Research
- release-please is the most widely adopted release automation for GitHub (40k+ stars)
- v4 is the current stable version (`googleapis/release-please-action@v4`)
- `simple` release type: tracks version in `.release-please-manifest.json`, no package manager integration
- Workflow requires permissions: `contents: write`, `pull-requests: write`
- Release PR is idempotent — accumulates commits until merged
- Sources: [release-please](https://github.com/googleapis/release-please), [release-please-action](https://github.com/googleapis/release-please-action)

## Recommendations for Spec
- Scope is minimal: 3 new files + optional docs update
- No changes needed to install.sh — tag format is compatible
- CHANGELOG.md transition is seamless — release-please prepends new entries
- Manifest baseline must be `{"." : "4.0.0"}` to match existing v4.0.0 tag
- First Release PR after setup may be large (14+ features since v4.0.0 in Unreleased)
