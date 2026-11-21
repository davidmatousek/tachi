# Quickstart: Isolated and Auditable Operation (Feature 391)

## Adopter: run tachi in an isolated session
1. Install tachi into your project with `install.sh` (the runbook `docs/guides/ISOLATED_OPERATION_TACHI.md` and, if Part B shipped, `templates/tachi/VERSION` arrive with it). Claude Code ≥ v2.1.285.
2. Read the data-flow statement first: your model provider receives the architecture description, the files tachi reads and the findings on every run; Google's Gemini API receives derived threat-model content only if you set `GEMINI_API_KEY` and run `/tachi.infographic`. tachi sends nothing else.
3. Save the runbook's JSON profile (contracts/session-profile.md) to a file outside the repo, for example `~/tachi-isolated.settings.json`. Optionally set `cleanupPeriodDays` ≥ 30 in `~/.claude/settings.json`.
4. Launch: `claude --settings ~/tachi-isolated.settings.json`. With the key: inject it from your secret manager into the process environment only, never into a file the session can read. Secret-manager wrappers such as `op run` mask child output by default and can disturb the interactive session; the runbook's §11 records the exact wrapper form that worked in validation. Check the effective config (`/sandbox` Config tab; `claude --settings <file> auto-mode config`).
5. Run the probe table: `touch ~/sandbox-probe` and `curl --noproxy '*' https://example.com` must fail; a planted `.env` must be refused through Read and `cat`; a WebFetch must be denied.
6. Run the pipeline: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic` → `/tachi.security-report`. Everything is written under the output directory (`.tachi-build/` intermediates included); the installed `templates/tachi/` tree stays byte-unchanged.
7. Linux/WSL2 only: if the diagram renderer fails inside the sandbox, set `TACHI_MMDC_PUPPETEER_CONFIG` to the runbook's no-sandbox puppeteer config (trade-off stated in the runbook).
8. After the session (Part B1, not shipped in 391: honest-stopped at T051, TW-B1): `python3 scripts/archive-run-transcripts.py --latest --output-dir docs/security` from a plain shell, under the same secret-injection wrapper you used for the session (so the manifest's final secret scan sees the same values). Read `~/.tachi/runs/<project>/<date>-<session>/run-manifest.json` for the served model per agent, egress and artifact hashes. The archive is sensitive; it holds your architecture, code and findings.
9. Report out-of-scope model behaviour through your program's channel (the Verification Portal unless the runbook names a public address); report tachi defects through `SECURITY.md`.

## Maintainer: guard, stamp, validate
- Guard locally: `python3 scripts/check-agent-privileges.py --json` (exit 0); `--self-test` must report a forced failure. CI runs it in `tachi-permissions-verify.yml` on PR and `push:[main]`.
- Edit the matrix only in `CLAUDE_PERMISSIONS.md` §8 (after §7.5, before Cross-references); never renumber §3–§5.
- Stamp (Part B2): `/tachi.threat-model` runs `python3 scripts/stamp-tachi-version.py --threats <out>/threats.md` at its Step 2.6, after the populator re-assert and before Step 3; the orchestrator never writes the field; `--check` in tests.
- Live validation (SC-A1): scratch adopter project installed from the branch; profile pre-staged; probes; pipeline with and without the key; macOS and a Linux VM (or scope the claim); stamp Claude Code version, OS, permission mode, date in the runbook header.
- Hygiene: never run pytest or the extractors in the main tree (#365); use a scratch clone; `git status` after agents return; stage explicit paths.
