# Security Policy

## Supported Versions

`tachi-rust` is in active Rust/Tauri migration. Security fixes are published on the latest `main` branch until the first stable release line is cut. After a stable release line exists, only the latest stable minor will receive security updates unless a longer support window is explicitly documented in the release notes.

## Reporting a Vulnerability

Use GitHub private vulnerability reporting for the public repository:

`https://github.com/pratik-saptarshi/tachi-rust/security/advisories/new`

Do not open a public GitHub Issue for security vulnerabilities. Public issues can disclose a vulnerability before a fix is available.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected components, such as Rust crates, Tauri command handlers, CLI binaries, templates, schemas, or scaffold files
- Potential impact
- Whether any secrets, personal data, or private assessment output may have been exposed

## What to expect

- Acknowledgment within 5 business days.
- Initial assessment within 1 week of acknowledgment.
- Fix or mitigation timeline after assessment.
- Credit in the fix commit and release notes by default; anonymity is available on request.

## Scope

In scope for private vulnerability reports:

- Rust crates under `crates/`
- Tauri shell and desktop bridge code under `src-tauri/`
- CLI command binaries and shared command handlers
- Schemas, templates, and generated-report helpers
- GitHub Actions workflows, release configuration, and repository security controls
- Shipped stack scaffolds until those Python-based scaffolds are retired by the Rust/Tauri-only roadmap

## Privacy and data handling

- Do not include customer data, private assessment output, credentials, API keys, tokens, or private keys in public issues, pull requests, examples, fixtures, or logs.
- Keep security reports, SARIF files, screenshots, and architecture diagrams sanitized before publishing.
- Use synthetic examples for tests and documentation unless a public, redistributable fixture is already committed.
- Rotate any credential that may have been committed, printed in logs, uploaded in artifacts, or shared in a public report.

## Publishing checklist

Before publishing to GitHub or cutting a release, follow [docs/standards/PUBLISHING_SECURITY.md](docs/standards/PUBLISHING_SECURITY.md). That checklist records the required security, privacy, and Rust validation gates for public pushes.

## Out of scope

The following are not handled through this private disclosure channel:

- Vulnerabilities in third-party tools or platforms; report those to their maintainers.
- Adopter personalization data, private assessment inputs, or modified scaffold output after installation.
- Threat-model accuracy concerns, false positives, and missed findings; file those as regular GitHub Issues unless they expose sensitive data.
