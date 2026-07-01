---
name: Gitleaks Pin Bump
about: Track a gitleaks version bump per the canonical pin-bump cadence
title: "chore(deps): bump gitleaks v"
labels: chore
---

> **Canonical recipe**: [`docs/standards/PRECOMMIT_HOOKS.md` §10 — Gitleaks pin-bump cadence](../../docs/standards/PRECOMMIT_HOOKS.md#10-gitleaks-pin-bump-cadence) is the single source of truth for this process (grounded in [ADR-042 Decision Item 6](../../docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md)). This checklist mirrors that section — if the two ever disagree, §10 wins.

## Bump details

- Current pinned version: `v...`
- Target version: `v...`
- Release type: <!-- minor / patch / major — see §10.1 for the policy per type -->

**Major release?** Stop — do not proceed on this checklist alone. Per §10.1, major releases (e.g., `v8.x` → `v9.x`) require ADR re-evaluation before bumping, since they can carry schema breaks (the `[allowlist]` → `[[allowlists]]` v8.25.0 transition is the canonical example). Open an ADR addendum or successor ADR first.

## Checklist (§10.2 six-step recipe)

- [ ] **Step 1** — Update the gitleaks version in two places: the `rev` tag in `.pre-commit-config.yaml`, and the pinned-download version + SHA256 checksum in `.github/workflows/gitleaks.yml` (fetched from the upstream `gitleaks_<ver>_checksums.txt`).
- [ ] **Step 2** — Re-freeze the pin: `pre-commit autoupdate --freeze`.
- [ ] **Step 3** — Re-run the synthetic-fixture suite: `tests/fixtures/gitleaks-rule-interaction/run.sh` — **16/16 required**.
- [ ] **Step 4** — Full-repo hook run: `pre-commit run --all-files` — **0 findings required**.
- [ ] **Step 5** — Re-derive the §3 default-rule coverage catalog: re-run the coverage probe, re-read each hit's `RuleID:` field, update the "Default-rule coverage catalog" table in `PRECOMMIT_HOOKS.md` §3. **This step is load-bearing** — step 3's fire/no-fire matrix stays green on a silent upstream RuleID rename; only this re-derivation catches it.
- [ ] **Step 6** — On any guarantee change (coverage gained/lost, a rule-ID rename, a threshold shift): update `ADR-042` §References and add/adjust a note in `PRECOMMIT_HOOKS.md` §8 Known-Limitations.

## Additional Context

Upstream release notes, CVE/regression links (for patch bumps), or other context for this bump.
