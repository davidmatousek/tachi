---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-11-16
    status: APPROVED_WITH_CONCERNS
    notes: "Attempt 2 (delta re-review of v1.1): all 8 required items resolved (R-1 dispatch definition at any depth; R-2 AD-13 report-assembler dispatch; trip-wires byte-identical to PRD §9; R-5 TW-A2 split AD-14; PRD §13 items 1-2 as a W1 Lane R task with CF-7 open; R-3 D-3 wording → PRD v1.3 + AD-15; R-4 Linux fallback; R-7 repair hints AD-16) and L-1..L-7 folded; Wording Rules hold. Five attempt-2 LOW items folded before /aod.tasks without re-review (PRD v1.3 fully applied at :51/:137/:219; §8 legend only-what-is-confirmed; manifest example consistency; runbook key-provisioning line; {out}-under-cwd disclosure). Attempt 1 (v1.0) was CHANGES_REQUESTED (2 HIGH: main-transcript-only dispatch definition; senior-backend-engineer dispatch in tachi.security-report.md; 6 MEDIUM). Full review: .aod/results/pm-plan-391.md."
  architect_signoff:
    agent: architect
    date: 2026-11-16
    status: APPROVED_WITH_CONCERNS
    notes: "Attempt 2 (delta re-review of v1.1): RC-P1..RC-P5 verified 5/5 (dispatch definitions at any depth; tracked VERSION placeholder with remove-before/write-after and the re-install test; Python ≥3.9 floor for installed scripts; stamp step at the command layer as Step 2.6 of tachi.threat-model.md; no-frontmatter allow-list predicate + bidirectional roster + fourth negative case); TI-1..TI-3 corrected; new findings 0/0/0/8; one new LOW technical inaccuracy (AD-4 copy sequence lacked mkdir -p) corrected in v1.2 before sign-off; AD-13 confirmed (report-assembler tools cover its steps). Seven remaining LOWs are /aod.tasks carry-forwards. Attempt 1 (v1.0) was CHANGES_REQUESTED (0/1/9/12, 3 technical inaccuracies, two ruling deviations). Full review: .aod/results/architect-plan-391.md."
  techlead_signoff: null  # Added by /aod.tasks
---
# Implementation Plan: Isolated and Auditable Operation

**Branch**: `391-isolated-auditable-operation` | **Date**: 2026-11-16 (v1.2: v1.1 revised after the PM and Architect plan reviews, then their attempt-2 LOW items folded; `.aod/results/pm-plan-391.md`, `.aod/results/architect-plan-391.md`) | **Spec**: [spec.md](spec.md) (v1.2, PM APPROVED_WITH_CONCERNS)
**Input**: Feature specification from `/specs/391-isolated-auditable-operation/spec.md`; PRD-391 v1.3 (`docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md`); define-stage reviews (`.aod/results/architect-391.md` §3, §6.5, §10, §11; `.aod/results/team-lead-391.md` §6–§8; `.aod/results/pm-spec-391.md` §10); `research.md`; draft PR #392.

## Summary

Make tachi's local-first claim true and make its operating envelope auditable, without changing what it detects. Part A (floor): correct every data-locality statement with the D-3 sentence; ship an installed runbook (`docs/guides/ISOLATED_OPERATION_TACHI.md`) with tachi's two-host egress profile, one session profile passed with `claude --settings`, probe checks, retention, reporting routes and a program mapping, validated live in a scratch adopter project; relocate the writes that today land in the installed templates tree and in `/tmp` so a run writes only under its output directory; make `/tachi.security-report` dispatch the tachi report-assembler instead of an AOD build agent (AD-13, a pre-existing defect found in review); publish a CI-guarded privilege matrix (§8 of `CLAUDE_PERMISSIONS.md`) enforced by a stdlib guard in `tachi-permissions-verify.yml`; record the contract in ADR-049. Part B (trip-wire gated, PRD §9): a stdlib archiver that copies a session's transcripts to a non-committable location and writes a structured provenance manifest that follows dispatches at any depth, and a deterministic `tachi_version` stamp at the command layer fed by an installed version marker after a lock-step schema reconciliation. Technical approach: documentation and configuration first, three small stdlib Python tools, one Bash change in `install.sh`, one workflow anchor extension, zero new dependencies.

## Technical Context

**Language/Version**: Bash 3.2-compatible shell (`install.sh`, workflow steps); Python **≥ 3.9 stdlib** for the installed scripts (archiver, stamp step; `pyproject.toml` declares `requires-python = ">=3.9"`, stock macOS ships 3.9.6) — avoid `hashlib.file_digest`, `datetime.UTC`, `match`, `zip(strict=)` and PEP 604 unions outside annotations; the guard runs on the CI runner's `python3` and locally on ≥ 3.9; CI test jobs run 3.11 and the B1/B2 modules run once more under `setup-python` 3.9; Markdown/YAML (agent frontmatter, docs, workflows); JSON (session profile, manifest).
**Primary Dependencies**: none new. Existing: pytest + PyYAML in `tests/`, typst and mmdc as documented prerequisites (ADR-022), jq on the CI runner, Claude Code ≥ v2.1.285 for the admin-required sandbox semantics the profile relies on.
**Storage**: files only. `~/.tachi/runs/<project-dir>/<date>-<session>/` (archive + `run-manifest.json`), `templates/tachi/VERSION` (tracked placeholder `tachi_version: unknown`, rewritten at install), `{out}/.tachi-build/` (relocated intermediates), `threats.md` frontmatter (`tachi_version`).
**Testing**: pytest modules in `tests/scripts/` gated by `tachi-pytest.yml` (explicit module list + path anchor with each module's *inputs*, same commit; KB Entry 3); the guard runs directly in `tachi-permissions-verify.yml`; the installed-tools assertion joins `tachi-install-fidelity.yml`'s manifest suite; the write-confinement test runs in install-fidelity's Typst-gated `report-posture` job (`TACHI_REQUIRE_TYPST=1`, fails rather than skips); every extractor or pytest run during build happens in a scratch clone (#365); live validation (SC-A1) is a maintainer-run session, recorded in the runbook.
**Target Platform**: macOS (Seatbelt sandbox) and Linux/WSL2 (bubblewrap) for the runbook; native Windows has no sandbox and is documented as unsupported for isolated operation. CI: ubuntu-latest (permissions-verify, install-fidelity) and the macOS + ubuntu pytest matrix.
**Project Type**: single repository harness (agents, commands, skills, scripts, templates, docs, tests, workflows). No application code, no API.
**Performance Goals**: guard < 5 s on the repo; archiver streams line-by-line (chunked `hashlib.sha256().update`) and handles a 100 MB session in < 60 s; stamp step < 1 s; no measurable change to pipeline runtime from the relocation.
**Constraints**: stdlib-only Python; the session profile's key set is closed (no `excludedCommands`, `allowWrite`, `allowNestedUserNamespaces`, `enableWeakerNestedSandbox`, `enableWeakerNetworkIsolation`, `filesystem.disabled`, `ignoreViolations`, `allowAllUnixSockets`, `allowLocalBinding`, `permissions.allow`, `defaultMode`, `autoMode.allow`/`soft_deny`); deterministic artifacts (no `generated_at`; `tachi_version` written by a script at the command layer); no new byte-identity failures vs the W0 pre-state (#365's six reds excepted); no tracked example image, PDF or SARIF baseline changes; Wording Rules (spec) on every public artifact; the key-handling patch merges before the build branches (T0); `feat(391)` merges after #364 or Part A ships alone as `fix(391)` (TW-A2, with the split constraint in AD-14).
**Scale/Scope**: 21 agents + 6 commands in the matrix; 7 workflows (3 touched); ~14 docs edited, 1 runbook + 1 ADR added; 3 new scripts, 6 new test modules, 2 fixture sets; estimate 4.0 eng-days (floor 2.0, ceiling 7.5), Part A 3.2 / Part B 0.8.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Result |
|---|---|---|
| I. General-purpose architecture | No domain coupling added to the harness | PASS. Operating documentation, a privilege guard and provenance tooling; no detection content changes. |
| II. API-first design | Contracts before interfaces | PASS (adapted). No HTTP API exists; the three CLI tools, the manifest, the marker, the profile, the matrix and the runbook outline are specified in `contracts/` before implementation. |
| III. Backward compatibility (non-negotiable) | Existing adopters and files keep working | PASS. Schema bump is additive (1.4 → 1.5); parsers unchanged (static contract test); absence of `tachi_version` is the documented legacy case; installs that skip the marker line read `unknown` because the tracked placeholder resets it; relocated intermediates change no deliverable; the runbook is opt-in; the report-assembler dispatch fix changes a command body only. |
| IV. Concurrency and data integrity | Atomic, race-free state changes | PASS. Archiver: `O_EXCL` creation, never writes into a non-empty destination, refuses a live session, re-archive is a hash-checked no-op; stamp step is idempotent at the command layer; marker removed before and written after the copy loop inside the installer's guards. |
| V. Privacy and data isolation | Data stays where the adopter expects | PASS, core of the feature: D-3 sentence everywhere; two-host egress profile; Read denies for secret paths; masked key; archive owner-only and outside committable paths; manifest structured-only with a fail-loud secret scan. |
| VI. Testing excellence | Every behaviour has a test | PASS. See Testing Strategy (guard red list incl. four roster negatives and self-test; closed-key-set profile test; Typst-gated write-confinement test; archiver fixtures incl. nested dispatch, six planting sites, refusal matrix, denial kinds; marker re-install test; static schema contract test; SC-A4 assertion; W3 doc checks). |
| VII. Definition of Done (non-negotiable) | 3-step validation before "delivered" | PASS. PRD §7 DoD; SC-A1..A5 recorded; Part B by honest stop if a trip-wire fires; `/aod.analyze` before the PR is marked ready. |
| VIII. Observability and root cause | Learnings captured | PASS. KB entry at deliver (the July provenance lesson closes); `delivery.md` records fired trip-wires, the W0' topology, the pre-existing dispatch defect and the C-9 correction. |
| IX. Git workflow (non-negotiable) | Feature branch, draft PR, no destructive git | PASS. Branch `391-…`, draft PR #392, explicit-path staging, no `--no-verify`; Part B on a stacked branch (AD-14). |
| X. Product-spec alignment (non-negotiable) | Triad sign-offs before build | PASS. PRD ✓/⚠/⚠, spec ⚠ (PM); this plan requires PM + Architect; tasks requires triple sign-off. |
| XI. Triad collaboration | Roles respected | PASS. Architect rulings D-1/D-4/D-6/D-8/D-9 and RC-P1..P5 implemented as decided; PM rulings R-1..R-7 implemented as decided; the team-lead's lanes and trip-wires adopted verbatim. |

No violations; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```
specs/391-isolated-auditable-operation/
├── plan.md              # This file (v1.1)
├── spec.md              # v1.2, PM approved
├── research.md          # Spec-stage research + Phase 0 decisions
├── feasibility-check.md # Team-lead estimate (define stage)
├── data-model.md        # Entities: manifest, marker, matrix rows, profile, records
├── quickstart.md        # Adopter and maintainer walkthroughs
├── contracts/
│   ├── cli-contracts.md         # check-agent-privileges, archive-run-transcripts, stamp-tachi-version
│   ├── run-manifest.md          # run-manifest.json v1 field contract and parse rules
│   ├── version-marker.md        # templates/tachi/VERSION placeholder, writers, residuals
│   ├── session-profile.md       # the --settings profile, closed key set, docs citations
│   ├── matrix-section.md        # CLAUDE_PERMISSIONS.md §8 columns (incl. Dispatches), placement, legend
│   └── runbook-outline.md       # runbook sections mapped to spec FR-004..FR-011a
├── checklists/requirements.md
└── tasks.md             # /aod.tasks output
```

### Source Code (repository root)

```
docs/guides/ISOLATED_OPERATION_TACHI.md                 # NEW runbook (installed; INSTALL_MANIFEST.md + completeness test); profile between <!-- BEGIN/END TACHI SESSION PROFILE --> markers
docs/standards/CLAUDE_PERMISSIONS.md                    # header scope note; FR-003 corrections (:11, :43/:46, :235/:237, §6, §7.4); NEW §8 at :279-281 (before Cross-references); §3-§5 headings byte-exact
docs/architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md   # NEW (incl. "Known limitations": skills' allowed-tools unguarded; pre-391 downgrade cannot reset the marker)
docs/architecture/02_ADRs/ADR-014-*.md, ADR-019-*.md    # dated Notes only
README.md (:164, :267-286, :308-321)                    # D-3 sentence (PRD v1.3 wording), key decision point, runbook link; keep x-release-please-version markers
docs/guides/DEVELOPER_GUIDE_TACHI.md (:55-67, :1607-1608, :1710-1732, :1798-1802)   # D-3 sentence; old compile path; repair path -> install.sh; runbook link
.claude/rules/scope.md (:16, :37), SECURITY.md          # D-3 sentence; runbook link; reporting routes
.claude/commands/tachi.security-report.md (:162, :178-180)   # AD-13: dispatch tachi-report-assembler (body only); relocated build path text
.claude/commands/tachi.threat-model.md (:67, new Step 2.6 between :194 and :195)   # repair hint -> install.sh; stamp step at the command layer [B2]
.claude/commands/tachi.risk-score.md (:42), tachi.compensating-controls.md (:47), tachi.infographic.md (:56, :160-166)   # repair hints -> install.sh; relocated --output path; grep -E fix (CF-10)
.claude/agents/tachi/report-assembler.md (Steps 2a, 2c, 3a, 3b, 3d)   # relocation into {out}/.tachi-build/security-report/ (clear first; cp -R src/. idiom; {out}-under-cwd precondition)
.claude/agents/tachi/threat-infographic.md (:166-180)   # --output {out}/.tachi-build/infographic-{template}.json; python -> python3 (CF-10); stale "--output defaults to stdout" claim fixed
templates/tachi/security-report/README.md (:70, :94-95, :138), .claude/skills/tachi-report-assembly/references/typst-artifacts.md (:118-123),
typst-template-contract.md (:22), .gitignore (:207)     # same-commit doc updates for the relocation
scripts/extract-report-data.py (:940, :1600)            # honour TACHI_MMDC_PUPPETEER_CONFIG (absolute path to a regular file; else fail loud) -> mmdc -p (AD-9); no other change
scripts/check-agent-privileges.py                       # NEW guard (stdlib; --self-test; see cli-contracts.md)
scripts/archive-run-transcripts.py                      # NEW archiver (stdlib ≥ 3.9) [B1]
scripts/stamp-tachi-version.py                          # NEW deterministic stamp step (stdlib ≥ 3.9) [B2]
scripts/install.sh (:325-350 checked set, :552-598)     # remove templates/tachi/VERSION before the copy loop; write it after; align fallbacks (`unknown`); git-dir detection via rev-parse [B2]; keep markers
templates/tachi/VERSION                                 # NEW tracked placeholder `tachi_version: unknown` (joins the K3 checked set via find) [B2]
schemas/output.yaml (single schema_version source), .claude/skills/tachi-orchestration/references/output-schemas.md (:26, :35, :285),
templates/tachi/output-schemas/threats.md (:6, :24…), .claude/skills/tachi-orchestration/references/sarif-specification.md (:53, :551),
scripts/generate-threats-sarif.py (:554 -> sourced from output.yaml), examples/agentic-app/threats.md (:2), examples/consumer-agent-app/sample-report/threats.md (:2)   # lock-step reconciliation + 1.5 [B2]; SARIF twins per AD-7(c)
schemas/run-manifest.yaml                               # NEW manifest schema doc [B1] (schemas/ is installed)
INSTALL_MANIFEST.md (:19, :77, :96-134)                 # runbook; archiver + stamp script whitelist lines; VERSION rides the templates/tachi/ directory entry
release-please-config.json                              # one extra-files entry: the runbook (its matrix-link line carries the only version string) (AD-2)
.github/workflows/tachi-permissions-verify.yml (:12-15 header, :62-66 anchor, new steps)   # anchor += agents, commands, guard script, runbook; python3 presence guard; guard step
.github/workflows/tachi-pytest.yml (:84-127 anchor, :147-150 python, :199-219 run list)   # new modules + their inputs; one extra 3.9 run of the B1/B2 modules
.github/workflows/tachi-install-fidelity.yml (:52-92 anchor, :171-194 report-posture job)   # anchor += docs/standards/CLAUDE_PERMISSIONS.md; test_write_confinement.py in the Typst-gated job
tests/scripts/test_agent_privilege_guard.py             # NEW
tests/scripts/test_isolated_profile_contract.py         # NEW (closed key set; hard_deny byte-exact; extracts the marked block)
tests/scripts/test_write_confinement.py                 # NEW (Typst-gated; steps in Testing Strategy)
tests/scripts/test_install_manifest_completeness.py     # SC-A4 assertion; runbook + scripts entries; end-to-end install accepts VERSION
tests/scripts/test_coverage_attestation.py (:221-250)   # stale-data swap moves to the build-dir location
tests/scripts/test_archive_run_transcripts.py           # NEW [B1]
tests/scripts/test_tachi_version_marker.py, test_threats_schema_contract.py   # NEW [B2] (incl. the re-install case)
tests/fixtures/transcripts/{synthetic-gen1,synthetic-gen2}/, tests/fixtures/transcripts/recorded-w2-scrubbed/   # [B1]; placeholders only, key-shaped values assembled at runtime (ADR-042)
tests/fixtures/init-baseline-tree/docs/architecture/01_system_design/README.md   # regenerate in the same commit if the live README is edited (spec FR-021 rule; see research.md L-2/L-11 note)
CHANGELOG.md                                            # Unreleased entry, neutral wording
```

**Structure Decision**: single-repository harness; every change lands in existing directories. New runtime surfaces are three stdlib scripts under `scripts/` (house convention: `#!/usr/bin/env python3`, docstring with feature id and exit codes, `_build_arg_parser()`, `main(argv=None) -> int`, exit 0/1/2), their tests under `tests/scripts/`, fixtures under `tests/fixtures/`, one installed runbook under `docs/guides/` with the `_TACHI` suffix, and one tracked placeholder under `templates/tachi/`.

## Components

| Component | Kind | Part | Owner lane | Notes |
|---|---|---|---|---|
| D-3 egress sentence (PRD v1.3 wording) | docs edit | A1 | D (after R confirms the field list, PM approves) | Six locations; immutable records untouched (ADR-014 gets a Note) |
| Runbook `ISOLATED_OPERATION_TACHI.md` | installed doc | A2 | R | Sections per `contracts/runbook-outline.md`; profile in marked block; live-validation record |
| Session profile | JSON block in the runbook | A2 | R | Contract in `contracts/session-profile.md`; closed-key-set test; validated live |
| Write relocation | agent/command edits | A2 | E (audit) + D (edits) | `{out}/.tachi-build/…`; `templates/tachi/` byte-unchanged; precondition `{out}` under cwd |
| Report-assembler dispatch (AD-13) | command body edit | A3 | E (audit) + D (edit) | `tachi.security-report.md:162` → `tachi-report-assembler`; pre-existing defect recorded |
| Privilege matrix §8 | docs section | A3 | E | Columns in `contracts/matrix-section.md` incl. Dispatches; single source |
| Guard `check-agent-privileges.py` | stdlib script + CI step | A3 | E | Bidirectional roster, closed key set, C6 tokenization, self-test |
| ADR-049 + Notes | ADRs | A | D | Privilege contract, write confinement, dispatch fix; conditional Part B paragraphs; Known limitations |
| Archiver `archive-run-transcripts.py` | stdlib script | B1 | B1 | D-8 rules; manifest v1 with dispatch-at-any-depth attribution |
| Version marker + stamp | placeholder + `install.sh` + stdlib script | B2 | B2 | `templates/tachi/VERSION`; `stamp-tachi-version.py` as Step 2.6 of `/tachi.threat-model`; schema reconciliation |

## Data Flow

```mermaid
flowchart LR
  subgraph Adopter machine
    RB[Runbook] -->|save profile| P[(--settings profile)]
    P --> CC[Claude Code session: sandbox + auto mode]
    CC -->|Bash via proxy| GEM[(generativelanguage.googleapis.com, optional)]
    CC -->|model API| MP[(Claude model provider)]
    CC --> OUT[{out}/ threats.md, sarif, report, .tachi-build/]
    CC --> TR[~/.claude/projects/<slug>/<session>.jsonl + <session>/subagents/]
    TR -->|archive-run-transcripts.py, dispatches at any depth| AR[~/.tachi/runs/<project>/<date>-<session>/ + run-manifest.json]
    INST[install.sh] -->|remove, copy, rewrite| VER[templates/tachi/VERSION]
    VER -->|stamp-tachi-version.py, Step 2.6 of /tachi.threat-model| OUT
  end
  subgraph CI
    PR[PR / push main] --> WF[tachi-permissions-verify.yml]
    WF -->|check-agent-privileges.py| MX[CLAUDE_PERMISSIONS.md §8]
    WF --> AG[.claude/agents/tachi/*.md, .claude/commands/tachi.*.md]
  end
```

Egress is exactly two hosts during a run: the model provider (inherent to Claude Code) and, only with a key and the infographic step, the Gemini host. Claude Code's own operational traffic is named separately and switched off by `env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. `install.sh` additionally runs a best-effort `git fetch --tags` at install time (stated in the runbook for air-gapped installs).

## Tech Stack

Bash 3.2 (`install.sh`, workflow steps, probe commands); Python ≥ 3.9 stdlib for installed scripts (`argparse`, `json`, `hashlib` with chunked updates, `os`, `pathlib`, `re`, `subprocess` for `git rev-parse`/`git check-ignore` only); pytest + PyYAML (tests only); GitHub Actions (existing workflows); Claude Code sandbox (Seatbelt / bubblewrap + local proxy), permission rules, `--settings` launch profile, auto-mode `environment`/`hard_deny`; typst + mmdc (existing). No new runtime dependency.

## Design Decisions (implementing the PRD rulings and the plan-review rulings)

- **AD-1 (D-1) Pins stay `sonnet`.** No agent frontmatter changes. The manifest records `pinned_model` (from the agent file matched by `agent_type`) beside `served_model_histogram`. ADR-019 Note: dated, "pins kept deliberately"; "served model evidenced by the run manifest" only if B1 ships, otherwise "recorded in Claude Code's transcripts". The runbook states only what is confirmed about model selection: a per-invocation `model` overrides the frontmatter, tachi passes none, and the manifest or transcripts record what served; the `ANTHROPIC_DEFAULT_SONNET_MODEL` / `CLAUDE_CODE_SUBAGENT_MODEL` precedence is a Lane R confirmation task (PRD §13 item 1) and is stated only if confirmed.
- **AD-2 (D-4a) Matrix home and link.** §8 appended at `CLAUDE_PERMISSIONS.md:279-281`; §3–§5 headings byte-exact. The runbook links the matrix at `https://github.com/davidmatousek/tachi/blob/v{RELEASE}/docs/standards/CLAUDE_PERMISSIONS.md#<exact-slug-of-§8>`, pinned by adding the runbook to `release-please-config.json` `extra-files` with an `x-release-please-version` marker on that one line, which carries exactly one version string (v2.1.285 and every other version stay off it). The guard or the profile test asserts the heading slug. D-9's "no `extra-files`" is scoped to the version marker (PM R-6 ratified). Caveat printed beside the link: a post-release `main` install sees the previous release's matrix, and no matrix exists before the first release that carries §8.
- **AD-3 (D-4b) Guard host.** `check-agent-privileges.py` runs as a new step in `tachi-permissions-verify.yml` after a `python3` presence guard, on both triggers; the path anchor gains `.claude/agents/tachi/**`, `.claude/commands/tachi.*.md`, `scripts/check-agent-privileges.py` and `docs/guides/ISOLATED_OPERATION_TACHI.md`; the header comment lists the new steps; anchor edits sequenced with #369. The guard's pytest module joins `tachi-pytest.yml` with its inputs in `&hardening_paths` (agents, commands, `CLAUDE_PERMISSIONS.md`, runbook, the three scripts, `schemas/output.yaml`, the output-schemas template, `tests/fixtures/transcripts/**`).
- **AD-4 (D-4c) Relocation.** *Mechanism amended at `/aod.tasks` (architect ruling RC-T4, 2026-11-16): the build-directory lifecycle lives in `scripts/extract-report-data.py` (`--build-dir PATH` creates it after `shutil.rmtree` of any stale copy and `shutil.copytree` of the template, with the `{out}`-under-cwd precondition enforced in code; `--remove-build-dir PATH` removes it after a verified compile), because the repository's own deny rule blocks `rm -rf` in agent recipes and the agent's Bash families must stay {`test`, `python3`, `typst`}. The shell-side description that follows is superseded by that contract.* Report-assembler (superseded wording): `rm -rf "{out}/.tachi-build/security-report"`, then `mkdir -p "{out}/.tachi-build/security-report"` and `cp -R templates/tachi/security-report/. "{out}/.tachi-build/security-report/"`, write `report-data.typ` and any custom `report-config.typ` there, pass `--output`/`--template-dir` to the build dir, compile `typst compile {out}/.tachi-build/security-report/main.typ {out}/security-report.pdf --root .` (root stays the working directory so `brand/final` and `{out}/attack-trees` resolve); precondition checked and failed loud: `{out}` is under the working directory (now required even for image-less reports because `main.typ` lives under `{out}`), and disclosed in the runbook's write-locations section and in `tachi.security-report.md`'s option text (same commit); on success remove `{out}/.tachi-build/security-report/`, on failure keep it. Infographic: `--output {out}/.tachi-build/infographic-{template}.json`, kept and listed in the write set (no deletion). Python `tempfile` and the mmdc/Chromium child write to `$TMPDIR` (allowed by FR-7). `templates/tachi/` is never written; the custom-config path is tested (SC-A5). `test_coverage_attestation.py:221-250` moves its stale-data swap to the build-dir location. Same-commit doc updates listed in Project Structure, including the stale "`--output` defaults to stdout" claim at `threat-infographic.md:176`.
- **AD-5 (D-6) Session profile delivery.** One JSON block in the runbook between `<!-- BEGIN TACHI SESSION PROFILE -->` / `<!-- END … -->` markers (the single source), saved by the adopter and passed with `claude --settings <file>`; `test_isolated_profile_contract.py` extracts it and asserts a **closed key set** (the profile's exact key paths), the invariants (one host; `injectHosts` ⊆ `allowedDomains`; `"$defaults"` present in every `autoMode` list; `tlsTerminate` present with any `mask`; the `hard_deny` sentence byte-exact against the PRD FR-6 wording), and the named weakening keys as explicit negatives. User-global settings: `cleanupPeriodDays` (never lowered; operators archive with B1 before starting another session if any settings file lowers it, since the sweep's cross-project scope is undocumented) plus the opt-in always-on alternative, merge-not-replace. `--setting-sources`: not recommended by default (excluding `project` disables tachi's installed agents, commands and skills); excluding `user` is offered as opt-in hardening with its costs listed (provider/auth config, user-scope masks, retention default, auto-mode re-prompt) and run once in SC-A1 if offered; the effective-config check names user-scope `excludedCommands`, `allowWrite`, `allowedDomains` and `WebFetch(domain:…)` allows as things to look for. SC-A1 confirms `--settings` honours `autoMode`, `strictAllowlist` and `tlsTerminate` from a file (fallback: inline JSON). Nothing is written into adopters' settings files.
- **AD-6 (D-8) Archiver.** Single stdlib (≥ 3.9) module; discovery by `cwd` match against the project realpath under `~/.claude/projects/` (or `CLAUDE_CONFIG_DIR`); destination `~/.tachi/runs/<project-dir-name>/<YYYY-MM-DD>-<session>/` (first timestamp, UTC via `timezone.utc`) or `--dest`; refusal rules: nearest existing ancestor realpath → `git rev-parse --show-toplevel` → inside a work tree only if `git check-ignore -q <dest>/.probe` passes; never a non-empty destination (hash-checked no-op); live session (mtime within the window) refused without `--allow-live`; dirs 0700, files 0600, `O_EXCL`; copies without following symlinks; never follows a symlink into a work tree. Copies `<session>.jsonl` and the whole `<session>/` directory verbatim (`subagents/*.jsonl`, `*.meta.json`, `tool-results/`). Attribution follows **dispatches at any depth** (RC-P1 / PM R-1): a *dispatch* is an `Agent` (legacy `Task`) `tool_use` whose `input.subagent_type` names a tachi agent in any archived transcript; *recorded* when a subagent meta's `toolUseId` equals the `tool_use` id and its `agentType` equals the name; *dispatch-failed* when the matching `tool_result` is an error (listed, does not trip TW-B1); *not recorded* when the dispatch succeeded and no meta matches (listed, trips TW-B1); additionally every installed tachi agent (the matrix roster) with neither a recorded instance nor a dispatch is listed as *not dispatched*, so the manifest can never be silently empty when the orchestrator analyses inline. Parse contract per `contracts/run-manifest.md` (name agreement on lines that carry `attributionAgent`, `<synthetic>` exempt, at least one non-synthetic attributed line; unknown entry `type` values and keys tolerated and counted; "unparseable" = invalid JSON only); `pinned_model` from the agent file; redaction structural first then a final scan whose hit exits non-zero with no manifest; the scan sees only the archiver's own environment, so operators run it under the same secret-injection wrapper as the session. Archives are never swept; retention is the operator's. Tests in `tachi-pytest.yml`; script in the manifest whitelist; `schemas/run-manifest.yaml` documents the fields.
- **AD-7 (D-9) Marker, stamp, reconciliation.** `templates/tachi/VERSION` is a **tracked placeholder** (`tachi_version: unknown`), so it joins the K3 pre-flight checked set through the existing `find` and every copy path resets it; `install.sh` removes any existing marker before the copy loop and, after the loop (`:585`) inside the containment and symlink guards and before the EXIT trap restores the ref, writes `tachi_version: <git describe --tags --always --dirty>`, detecting the git dir with `git -C "$SOURCE_DIR" rev-parse --git-dir` (worktrees, submodules), falling back to `<manifest ".">-release-manifest` when no git tree exists (labelled so it cannot read as a describe string) and to `unknown` otherwise; the existing `untagged` fallback is aligned to `unknown`. The README manual-install loop writes the same line after its copy; installs that skip the line read `unknown` (the placeholder), with the residual that a pre-391 installer used to downgrade cannot reset the marker (ADR-049 Known limitations). `stamp-tachi-version.py --threats <path> [--marker templates/tachi/VERSION]` inserts or updates `tachi_version:` after `schema_version:` (or at the end of the frontmatter when absent) idempotently; it runs **at the command layer as Step 2.6 of `.claude/commands/tachi.threat-model.md`**, between the Step 2.5 populator re-assert (`:150-194`) and Step 3 (`:195`); `orchestrator.md` is untouched (which also removes the #374 collision). Reconciliation first, in one commit, with **`schemas/output.yaml`'s `schema_version` as the single source**: output.yaml (1.1 → 1.5, declare the six de-facto keys + `tachi_version`), `output-schemas.md` (:26, :35; checklist :285), the template (:6 and the "1.4" literals), the SARIF spec (:53, :551), `generate-threats-sarif.py:554` sourced from output.yaml, and the two drifted examples corrected to "1.4" frontmatter-only after #364 (measured first in a scratch clone). Tracked SARIF twins: the generator sources `semanticVersion` from the input file's `schema_version` with `output.yaml` as the fallback (PM L-5 ruling at `/aod.tasks`), so tracked 1.7/1.8 twins reproduce unchanged; the consumer-agent-app twin's "1.8" goes to a follow-up; if any tracked SARIF baseline would move, carve out. CF-21: `--schema-version-from-template` writes `schema_version` from output.yaml if the measurement shows zero baseline churn; otherwise `schema_version` stays model-authored and declared-only, and the schema doc says so. Consumer guidance ("feature-detect `tachi_version`; treat pre-1.5 `schema_version` as declared, not ordinal") lives in `output-schemas.md` and `schemas/output.yaml`'s comments. Any `docs/architecture/01_system_design/README.md` edit regenerates `tests/fixtures/init-baseline-tree/` in the same commit (spec FR-021; research.md records that the current fixture already diverges, which does not change the rule).
- **AD-8 Guard semantics.** Roster: walk `.claude/agents/tachi/` recursively; a symlink anywhere is red; classify each file as (i) agent candidate when it has leading YAML frontmatter (lenient: BOM, blank lines, CRLF tolerated) — then `name: tachi-*`, unique, with a §8 row, else red; (ii) allow-listed non-agent only when it is on the explicit list (`_TACHI_AGENT_BEST_PRACTICES.md`) **and** has no leading frontmatter; (iii) anything else red. C1 is bidirectional: every §8 row needs a file. Per agent: `tools:` as a set (block list, flow list and comma string all parsed; any other shape exits 2), `model:` value, frontmatter key set == `{name, description, tools, model}`; per command: frontmatter keys equal the §8 commands table (values recorded once `allowed-tools`/`model` are set). C6 Bash families: fenced blocks labelled `bash`, `sh`, `shell` or `zsh` in the three Bash-capable agents, indented fences included, unlabelled fences out of scope (agent commands must use labelled fences); join `\` continuations, split on `&&`, `||`, `;`, `|`, strip leading `VAR=value`, take each segment's first token; `$(…)`, backticks, `eval`, `bash -c`/`sh -c`, `xargs <cmd>` are red unless allow-listed; prose never scanned (TW-A3). C7: the runbook's write-locations table equals the §8 writes column. `--self-test`: copy to a temp dir, mutate (tool add; planted `name: helper`; unlisted file without frontmatter; duplicate name; `_TACHI_AGENT_BEST_PRACTICES.md` with planted frontmatter) and assert failure, every run. Exit 0/1/2, `--json`.
- **AD-9 Linux sandbox fix (R-2, PM R-4).** `extract-report-data.py` honours `TACHI_MMDC_PUPPETEER_CONFIG=<absolute path to a regular file>` by passing `-p <path>` to mmdc at both call sites (`:940`, `:1600`), failing loud otherwise; the runbook ships `{"args": ["--no-sandbox"]}` for Linux/WSL2 sandboxed sessions with the trade-off stated (the renderer then processes LLM-authored diagrams derived from the analysed repository with Claude Code's sandbox as its only boundary), checked under auto mode in SC-A1. If it fails and no skip path exists, the Linux "validated" claim is scoped to exclude the report step's attack-tree rendering (header and platform section) and a follow-up is filed for a skip path; TW-A1 governs the time. Running a step outside the isolated session is outside the runbook's scope and is never presented as an isolated-operation step. Never `excludedCommands`, never `allowWrite`, never `allowNestedUserNamespaces` or `enableWeakerNestedSandbox`.
- **AD-10 Wording sweep.** A recorded `grep -E` over the spec's Surface for Pattern A (zero hits) and Pattern B (dispositions) in the W3 sweep record and `delivery.md`; no new tool.
- **AD-11 ADR-049.** "Privilege contract and write confinement for tachi agents": the CI-enforced `tools:`/`model:`/key-set contract, the bidirectional roster rule, the enforced-vs-declared statement (model column: only what is confirmed, as in AD-1), the write confinement to `{out}` + `$TMPDIR` with the disclosed precondition that `{out}` sits under the working directory, the report-assembler dispatch fix (AD-13); conditional sections for the manifest (B1) and the schema change (B2), each marked "if shipped"; a **Known limitations** section (skills' `allowed-tools`/`model` are an unguarded privilege surface, follow-up filed; a pre-391 installer downgrade cannot reset the marker; the pinned link lags for post-release `main` installs). Dated Notes on ADR-014 (egress profile pointer) and ADR-019 (AD-1).
- **AD-12 Live validation protocol (SC-A1).** Scratch adopter project installed with the branch's `install.sh`; profile pre-staged from `contracts/session-profile.md`; Claude Code ≥ v2.1.285 and auto-mode availability confirmed; probe table first (`touch ~/sandbox-probe`, `curl --noproxy '*' https://example.com`, planted `.env` via Read and `cat`, WebFetch denied); full pipeline without the key, then with the key injected from the maintainer's secret store into the process environment only; offline mmdc render check in a scratch clone (byte-identical PNGs); Gemini client CA trust under `tlsTerminate`; auto mode with non-essential traffic off, or the pre-ruled fallback (default mode, header stamps the mode, recipe marked "not yet run live" + follow-up issue); `--setting-sources` without `user` run once if the runbook offers it; macOS and a Linux VM or the claim scoped; stamp Claude Code version, OS, permission mode, date. Pre-conditions: the Gemini client form pinned in `gemini-prompt-construction.md` (by the key-handling patch or Lane R); the W2 sessions are archived with the B1 archiver (if built) and feed the recorded fixture, the denial sample and the SC-B3 field check.
- **AD-13 (PM R-2) Report-assembler dispatch.** `tachi.security-report.md:162` dispatches `tachi-report-assembler` instead of `senior-backend-engineer` (an AOD build agent that adopters never install and that declares no `tools:`); body only, prompt kept, command frontmatter unchanged. Architect confirmation at the W1 P0 checkpoint: the report-assembler's declared tools {Read, Glob, Grep, Bash, Write} cover its four steps (its body names no other tool). §8's commands table gains a **Dispatches** column; ADR-049 records the change; `delivery.md` records it as a pre-existing defect found in review. If a reason emerges that the dispatch must stay, §8 and the runbook disclose the inherited toolset, SC-A1 must show the command completing in the scratch project without that agent, and a follow-up is filed.
- **AD-14 (PM R-5) TW-A2 split mechanics.** If Part A ships alone, its PR contains no Part B path or hunk: not the archiver, the stamp script, the placeholder marker, the `install.sh` marker block, the schema bump, Step 2.6, the Part B test modules and their `tachi-pytest.yml` entries, the Part B whitelist lines, nor the Part B conditional text in ADR-049, ADR-019 and the runbook. Mechanics: B1 and B2 commit from W1 on a branch stacked on the Part A branch (`391-isolated-auditable-operation-part-b`), and shared files get per-part commits. Delivery: Part A closes under `fix(391)`; `delivery.md` records "Part B: built, awaiting #364" (distinct from an honest stop); the Part B PR carries the conditional texts and gets its own release check.
- **AD-15 (PM R-3) D-3 wording and Gemini field list.** PRD v1.3 fixes the parenthetical as "finding IDs with one-line threat descriptions; component, trust-zone and data-flow labels; severity counts and the overall risk posture". At the start of W1, Lane R checks that list against the pinned client form and `extract-infographic-data.py`; if it differs, the PM approves the final text before Lane D writes it anywhere; the same list replaces the audiences parenthetical in the profile's `environment` entry (`contracts/session-profile.md`).
- **AD-16 (PM R-7) Repair hints.** The four command files that print `cp -r <tachi-repo>/adapters/claude-code/agents/… .claude/agents/tachi/` (`tachi.threat-model.md:67`, `tachi.risk-score.md:42`, `tachi.compensating-controls.md:47`, `tachi.infographic.md:56`) point at `install.sh` instead; bodies only. SC-A4's install-fidelity assertion then covers every documented path.

## Phase 0: Research

`research.md` (spec stage) grounds the file:line surfaces; its "Phase 0 (plan) decisions" table records AD-2, AD-4, AD-5, AD-7 and AD-9 in Decision / Rationale / Alternatives form, and its init-baseline row is a measured observation that leaves the spec FR-021 rule unchanged. No open clarification markers remain.

## Phase 1: Design Artifacts

`data-model.md`, `contracts/` (six contracts, including `runbook-outline.md`), `quickstart.md`. `update-agent-context.sh` is absent in this repository (known gotcha); no agent context file is updated by script; the new technology list is empty.

## Phases, Lanes and Waves (from the team-lead feasibility check, with the plan-review additions)

| Session | Wave | Lanes | Window |
|---|---|---|---|
| P | Plan | this plan, then `/aod.tasks` (TW-0, TW-B0, TW-A3 evaluated there) | 0.40 d |
| any time before T0 | W0' attribution spike | maintainer runs `/tachi.threat-model` on the smallest example in a scratch project (stock tachi, no sandbox, no key, **no** `/tachi.infographic`); transcripts copied privately, never committed; tester checks: subagent transcripts exist, `agentType` and `message.model` present, name agreement, and explicitly whether `Agent` `tool_use` blocks appear **inside subagent transcripts** (spawnDepth ≥ 2) with matching metas — recording the topology, the Claude Code version and the observed layout in `delivery.md`; **TW-B1 decided here** under the AD-6 definitions | 0.15 d |
| S1 | W0 pre-state | devops: rebase on post-patch `main` (T0); record green workflows at HEAD, #365's six reds, scratch clone path; create the stacked Part B branch (AD-14) | 0.10 d |
| S1 | W1 (5 lanes, disjoint files) | **R first steps**: confirm the Gemini field list (AD-15), pin the client form if the patch did not, record PRD §13 items 1–2 (model-env precedence; `--setting-sources` disposition; sweep scope; pre-stage the profile) — CF-7 stays open until this task closes. **D** docs (A1 with the approved D-3 text, FR-013/014 repair paths incl. AD-16, D-11 links, manifest lines, AD-13 command edit, ADR-049 + Notes). **R** runbook per `contracts/runbook-outline.md` (web-researcher → devops authors → PM framing/mapping → architect profile review). **E** guard: write-set audit incl. `tachi.security-report.md` → §8 matrix (Dispatches column) → guard + tests → SC-A4 assertion → workflow wiring; E hands R the audited write table before C7 is wired (or C7 lands last). **B1** archiver core on the synthetic two-generation fixture (incl. nested dispatch, `<synthetic>` line without `attributionAgent`, `api-request*` entries, `Task` legacy name; security-analyst on redaction/refusal), on the stacked branch. **B2** placeholder + `install.sh` marker + Step 2.6 + stamp script + reconciliation + SARIF twins decision + init-baseline regen if needed (tester: marker and re-install tests, contract test), on the stacked branch. Cut line: D and E committed green before W1 closes. Architect P0 checkpoint: audited write set, guard placement, AD-13 tool coverage, RC-P1 definition in the spike checklist, Step 2.6 placement, the re-install test, B2 contract, B1 manifest contract | ≈ 1.45 d |
| L | W2 live validation | maintainer, per AD-12; each session archived with the B1 archiver (if built) | 0.60 d |
| S2 | W3 | recorded fixture (structure-preserving scrub) + denial parsing; security-analyst leakage review + snippet review (incl. the `/proc/self/environ` Read question); runbook corrections + "Last validated" stamp + FR-010 record; SC-A3 red/green evidence; SC-A2, Wording and W3 doc checks sweep records; gated modules in a scratch clone; code-reviewer full diff; architect final checkpoint | ≈ 0.65 d |
| S2 | W4 | PM release notes (neutral wording) and deferral or "built, awaiting #364" record; C-9 record (maintainer corrects published copies); devops PR title per TW-A2; release-please check after merge | 0.25 d |

NEXT-SESSION handoffs at the end of S1 and L. Load check: no agent instance above 80% of its wave window (team-lead §7).

## Scope and Deferral Gate (PRD §9, verbatim; binding; copied into tasks.md)

**In (P1)**: Groups A1, A2 (with the write relocation) and A3, and FR-20. **In (P2/P3, trip-wire gated)**: Groups B1 and B2. **Out**: see Non-Goals.

**Cut line.** Lanes D (docs) and E (matrix and guard) are committed green before W1 closes; from then on, Part A's deterministic half can ship on its own.

The v1.0 gate (Part B waits until D-1, D-8 and D-9 are decided) opened at review, because all three are now ruled. The team-lead's trip-wires replace it. The team-lead evaluates them, and `delivery.md` records any that fire.

| Trip-wire | When | Rule |
|---|---|---|
| **TW-0** aggregate | `/aod.tasks` | Projected duration above 5.0 d (planning + 1.0) → carve the FR-11 body scan, then Part B (SARIF is already out). |
| **TW-B0** Part B entry | `/aod.tasks` | Part B proceeds only if D-1, D-8 and D-9 are ruled in plan.md, the examples and SARIF rulings are recorded (§4 records both), and Part B's tasks total 3.0 effort-days or less; otherwise honest-stop Part B (F-295 precedent). |
| **TW-A3** FR-11 bound | `/aod.tasks` | The Bash check is limited to fenced shell blocks in the three Bash-capable agents, against a per-agent allow-list; if it cannot be bounded, carve it (SC-A3 still ships). |
| **TW-B1** attribution, the honest stop | W0' spike; re-confirmed on the W2 sessions | B1 stops if any dispatched tachi agent's turns cannot be attributed to its name from transcript structure, any subagent that ran yields an empty histogram, meta and line agent names disagree, or a planted denial kind goes undetected. The denial criterion applies from W2, where the probes plant denials; the spike runs without a sandbox. It fails closed: an empty or partial histogram never passes. `delivery.md` records the observed layout; B2 may still ship. |
| **TW-B2** cost | Start of build session 2 | Part B's remaining work above 1.5 d, or any B lane more than 50% over budget → ship Part A at the cut line and defer Part B. |
| **TW-B3** layout | During B1 | Parser rework above 0.5 d, or a layout change mid-build → honest-stop B1. |
| **TW-B4** scrub | W3 | Scrub plus leakage review above 0.35 d, or a review that does not clear → commit a synthetic structure-only fixture and check the recorded run locally only (§4 fallback ruling). |
| **TW-A1** live budget | W2 | At most 3 debug loops or 1.0 d on SC-A1. Beyond that: document the limitation, make the key-less path the isolated default (R-1), stamp only what ran, file a follow-up, and do not hold the bundle. |
| **TW-A2** merge gate | Part A merge-ready | If #364 has not merged, Part A ships alone as `fix(391)` (PM ruling, §4). |

B1 and B2 defer independently. B2 also waits for #364 and the schema reconciliation; it does not depend on D-1 or D-8.

*Sourced addition (team-lead §8, TW-0 formula)*: projected duration = Σ(lane × 1.25) + 0.6 (live session) + 0.9 (plan, handoffs, deliver). *Operational reading of TW-B1 (AD-6 / RC-P1 / PM R-1)*: "dispatched" is any `Agent`/`Task` `tool_use` naming a tachi agent in any transcript at any depth with a successful `tool_result`; only a successful dispatch without a matching meta trips TW-B1; dispatch-failed and not-dispatched agents are listed, never inferred.

## Testing Strategy

| Test | Module / record | Gate | Proves |
|---|---|---|---|
| Guard red list (tool add/remove, model change, added key, command frontmatter), roster negatives ×4, bidirectional rows, C6 cases (chained `curl`, env-prefixed command, indented fence), self-test | `test_agent_privilege_guard.py` + the guard step | `tachi-pytest.yml`; `tachi-permissions-verify.yml` | SC-003 |
| Profile contract: closed key set, invariants, `hard_deny` byte-exact, named weakening keys as negatives | `test_isolated_profile_contract.py` | `tachi-pytest.yml` | FR-005/006 |
| Write confinement: copy template → write custom config → run the extractor on a fixture without attack trees (no mmdc) → compile → hash `templates/tachi/` before/after → list new paths, all under `{tmp}/out` or `$TMPDIR` | `test_write_confinement.py` | `tachi-install-fidelity.yml` `report-posture` job (`TACHI_REQUIRE_TYPST=1`, fails rather than skips) | SC-005 |
| Installed tools match matrix; end-to-end install accepts `VERSION` | assertion in `test_install_manifest_completeness.py` | `tachi-install-fidelity.yml` | SC-004 |
| Archiver: refusal matrix (incl. dotfiles repo at `$HOME` with ignored runs dir), two-generation synthetic fixture with nested dispatch and legacy `Task` name, dispatch-failed and not-dispatched listings, six planting sites (run succeeds, keys absent), forced-leak backstop (no manifest), denial kinds, name agreement with `<synthetic>` exemption, `api-request*` tolerance, empty histogram, `denial_detection` fails closed across versions | `test_archive_run_transcripts.py` (+ a 3.9 run) | `tachi-pytest.yml` | SC-006, SC-007 |
| Marker: installer write, manual-loop write, skip → `unknown`, **re-install after a marker-writing install → `unknown`**, `--version` local-clone cases, fallbacks (`unknown`, `-release-manifest`) | `test_tachi_version_marker.py` on `install_sh_helpers.py` (+ a 3.9 run) | `tachi-pytest.yml` | SC-008 |
| Schema contract: parsers unchanged, declarations agree with `schemas/output.yaml`, additive 1.5, stamp idempotent, Step 2.6 present in the command | `test_threats_schema_contract.py` | `tachi-pytest.yml` | SC-008 |
| W3 doc checks: FR-002 order; FR-003 five corrections + two gap statements; FR-011a links (none dead from the installed guide; matrix link pinned to the §8 slug); FR-015 Notes dated; consumer guidance present in `output-schemas.md`/`output.yaml`; runbook outline complete (FR-006 trust/classifier statements, FR-009 domain-fronting caveat) | W3 record | manual | US1, US2, US5 |
| Live validation | SC-A1 record in the runbook | manual (W2) | SC-001 |
| Sweeps | SC-A2 + Wording sweep records | manual (W3) | SC-002, SC-009 |

Hygiene: no pytest or extractor runs in the main tree (#365); scratch clones only; `git status` after every agent return; explicit-path staging; fixtures hold placeholders and tests assemble key-shaped dummies at runtime from fragments (never a key-shaped literal, never a wider `.gitleaksignore`; ADR-042).

## Risks and Mitigations

- Auto mode blocks the Gemini POST despite the environment entry → SC-A1 documents it; key-less path is the isolated default (pre-ruled).
- Chromium fails in the Linux sandbox → AD-9 fix, else scoped claim + follow-up (never a weaker sandbox).
- Nested dispatch is refused or the orchestrator analyses inline → the manifest lists dispatch-failed / not-dispatched agents; TW-B1 trips only on a successful dispatch without a transcript; the W0' spike records the topology before any B1 code.
- Transcript layout drift → minimal contract, fail-loud, two-generation fixture, `claude_code_versions` recorded; TW-B3.
- `--settings` does not honour a sandbox or auto-mode key from a file → inline JSON fallback confirmed in SC-A1.
- A 3.11-only API slips into an installed script → the extra 3.9 CI run of the B1/B2 modules.
- #364 / #374 collisions on `output-schemas.md` → whichever merges second rebases; the orchestrator body is no longer touched.
- The real key sits in the Claude Code process environment; on Linux the Read tool could read `/proc/self/environ` → security-analyst confirms in W3 whether Claude Code blocks it; otherwise add `Read(//proc/**)` to the credential-store extension note or qualify the "injected only toward the Gemini host" claim.
- Wording regressions → Pattern A/B sweep in W3 and at deliver.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified* — none.

## Technical debt register (ADR-049 Known limitations; tasks.md and delivery.md carry it)

Skills' `allowed-tools`/`model` are an unguarded privilege surface (follow-up); a pre-391 installer downgrade cannot reset the marker; the pinned matrix link lags for post-release `main` installs and does not exist before the first release carrying §8; command frontmatter is declared-only until `allowed-tools`/`model` are set; `denial_detection` is `validated` only for Claude Code versions with a passing fixture.

## Carry-forwards resolved here

CF-1 (rulings folded) · CF-2 (AD-11) · CF-3 (matrix columns incl. Dispatches, `contracts/matrix-section.md`) · CF-4 (AD-3, AD-8) · CF-5 (AD-4) · CF-6 (runbook content, `contracts/runbook-outline.md`, D-11, D-12) · **CF-7 open until the W1 Lane R task closes** (PRD §13 items 1–2: model-env precedence; `--setting-sources`; sweep scope; pre-staged profile) · CF-8/CF-22 (AD-12, W0' constraints incl. private copies) · CF-9 (FR-003 list, sweep scope) · CF-10 (`python` → `python3` at `threat-infographic.md:167`; `grep -P 'L[1-7] [—–-]'` → `grep -E 'L[1-7] (—|–|-)'` at `tachi.infographic.md:166`) · CF-11/CF-12 (AD-6) · CF-13 (AD-7) · CF-14 (trip-wires verbatim) · CF-15 (hygiene) · CF-17 (matrix legend) · CF-18 (AD-2) · CF-19/CF-23 (spec) · **CF-20 (AD-6 definitions, replacing v1.0's main-transcript-only wording)** · CF-21 (AD-7, measured) · architect plan-review attempt-2 LOWs (manifest example ids, roster source, stale research row, PRD v1.3 field-list wording — the PRD is now fully aligned, guard tokenizer and junk-file handling, an anchor entry, delivery mechanics) carried to tasks · architect plan-review CF-P1..CF-P9 (RC-P1..P5 applied here; M-5..M-9 and L-1..L-12 folded into AD-4..AD-8, the Testing Strategy, the debt register and the W1/W3 rows; CF-P9 is the W1 P0 checkpoint list) · PM plan-review items 1–9 (AD-6, AD-13..AD-16, trip-wires verbatim, W1 Lane R task, L-1..L-7 folded: `release-please-config.json` in the structure, research row reworded, CF-21 conditional text, W3 doc checks row + runbook outline, W0'/W4 records, quickstart secret-manager wording, `denial_detection` fails closed, `hard_deny` byte-exact).
