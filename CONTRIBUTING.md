# Contributing to tachi

Thank you for your interest in contributing to tachi — the threat modeling and AI-reasoning vulnerability detection harness for Claude Code.

## Where to start

| What you have | Where it goes |
|---------------|---------------|
| **Reproducible bug** | [GitHub Issue](https://github.com/davidmatousek/tachi/issues) using the bug-report template |
| **Question or unclear behavior** | [Discussions → Q&A](https://github.com/davidmatousek/tachi/discussions/categories/q-a) |
| **Feature idea** | [Discussions → Feature Requests](https://github.com/davidmatousek/tachi/discussions/categories/feature-requests) (not Issues — see below) |
| **Real-world usage report** | [Discussions → In the Wild](https://github.com/davidmatousek/tachi/discussions/categories/in-the-wild) |
| **Security vulnerability** | [Private advisory](https://github.com/davidmatousek/tachi/security/advisories/new) — do NOT post publicly |

## Development setup

```bash
git clone https://github.com/davidmatousek/tachi.git
cd tachi
make init
make check
```

The full pipeline requires two external CLIs:

- `typst` — PDF security report compilation
- `mmdc` (`@mermaid-js/mermaid-cli`) — attack tree rendering

See [README.md](README.md) "Prerequisites" for platform-specific install commands.

## How feature requests become work

Feature requests start as Discussions, not Issues. The lifecycle:

1. **Propose** — Open a thread in [Discussions → Feature Requests](https://github.com/davidmatousek/tachi/discussions/categories/feature-requests) describing the problem you're trying to solve.
2. **Triage** — Maintainer reviews, asks clarifying questions, gathers community signal.
3. **Promote** — Once a thread has traction and an [ICE score](docs/AOD_TRIAD.md), the maintainer promotes it to a GitHub Issue (auto-labeled `enhancement`, `stage:discover`).
4. **Pick up** — Contributors take the Issue through the AOD lifecycle: `/aod.define` → `/aod.plan` → `/aod.build` → `/aod.deliver`. See [docs/AOD_TRIAD.md](docs/AOD_TRIAD.md) for the governance overview.

Why the gate? It keeps the Issue tracker focused on actionable, scoped, traction-validated work. Discussions are where ideas grow; Issues are where work happens.

## Branch and PR workflow

**Always use feature branches** — never commit to main directly.

- **Branch format**: `NNN-descriptive-name` where `NNN` is the GitHub Issue number, zero-padded to 3 digits (e.g., `266-tachi-flavor-contributing`).
- **PR title**: must be Conventional-Commit-formatted because squash-merge subjects feed into release-please:
  - `feat(NNN): <description>` — new feature or user-visible improvement (minor bump)
  - `fix(NNN): <description>` — bug fix (patch bump)
  - `perf(NNN): <description>` — performance improvement (patch bump)
  - `docs:` / `chore:` / `refactor:` / `test:` / `style:` — hidden bump, no release
- **Draft PR**: open at plan stage for early visibility; mark ready at delivery time.
- **Triad sign-offs**: PRs touching `spec.md`, `plan.md`, or `tasks.md` require PM / Architect / Team-Lead sign-offs per [docs/AOD_TRIAD.md](docs/AOD_TRIAD.md).

See [.claude/rules/git-workflow.md](.claude/rules/git-workflow.md) for the full git workflow including the post-merge release-please verification step.

## Guidelines

- Follow existing patterns and conventions
- Keep commits atomic and focused on a single change
- Update documentation when changing workflows or templates
- No secrets, credentials, or PII in committed files (see [docs/security/OPEN_SOURCE_READINESS.md](docs/security/OPEN_SOURCE_READINESS.md))
- Be respectful and constructive in all interactions

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open a [Discussion](https://github.com/davidmatousek/tachi/discussions) — happy to help.
