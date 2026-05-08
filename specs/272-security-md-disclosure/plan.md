---
spec_reference: specs/272-security-md-disclosure/spec.md
prd_reference: docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "Plan faithful to spec; 14/14 FRs traced; 3 prior spec-stage observations explicitly addressed (D-1 README sibling-bullet, plan-stage manifest re-check, D-3 R-2 footer verbatim per PRD §R-2). Constitution Check correctly invokes Principle VII §Exceptions for doc-only DoD with all 3 DoD steps mapped (push/test/user-validate). PRD's three deliberately-NOT decisions respected (no SMTP, no CNA, no schema/code change). File-touch matrix + 5-section outline + verification recipe concrete enough for /aod.tasks. AC-13 + AC-14 remain correctly out-of-scope. Two informational micro-nits — neither requires plan revision. Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-08
    status: APPROVED
    notes: "Plan technically sound and appropriately minimal for docs-only. Constitution Check correctly invokes Principle VII §Exceptions; file-touch matrix complete; D-1..D-6 defensible; manifest 4.31.0/tag v4.32.0/README line-44 re-cross-checks confirmed at review time; SECURITY.md outline matches GitHub-canonical pattern; verification recipe meets AC-9..AC-11 + FR-014; no ADR (correct per PRD §Governance); Principle III preserved (file replacement non-breaking; URL fallback retained); no new attack surface; R-6 vendor-lock acknowledged with appropriate residual-risk framing. Single minor advisory N-1 (Phase 0 cross-link to spec §Edge-Cases) — non-blocking. All 13 architecture-relevant concerns CONCUR. Full review: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-3 — SECURITY.md and Private Disclosure Channel

**Branch**: `272-security-md-disclosure` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/272-security-md-disclosure/spec.md`
**PRD**: `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md` (v1.1, Approved)
**Initiative**: BLP-02 Wave 3

## Summary

Rewrite the repo-root `SECURITY.md` (~80 LOC) into the GitHub-canonical 5-section structure (Supported Versions / Reporting a Vulnerability / What to expect / Scope / Out-of-scope), enable the GitHub repo's **Private vulnerability reporting** toggle so the *Report a vulnerability* button surfaces on the Security tab, add a one-line `README.md` pointer in the existing `## Community` section, and add a `## Unreleased → ### Features` entry to `CHANGELOG.md` referencing TACHI-VULN-05abc41ad4cc closure. **Pure documentation + repo-setting change; no code, no ADR, no tests, no `finding.yaml` or schema delta.** Scoped per spec FR-001..FR-014; deferred AC-13 (posture probe) and AC-14 (manifest discrepancy) are post-merge backlog Issues, not in F-3 implementation scope.

**Technical approach**: Single feature branch `272-security-md-disclosure` (already created at /aod.spec time); single squash-merged PR titled `feat(272): SECURITY.md and private disclosure channel`; manual GitHub-UI toggle out-of-tree with verification evidence captured in PR description; release-please auto-triggers on `feat(272):` squash-merge with the F-212 empty-marker recovery flow held in reserve.

## Technical Context

> **F-3 is a documentation-only feature.** The technical-context fields below are filled with minimum-applicable values — most are N/A for a doc-touch + repo-setting change.

**Language/Version**: Markdown (CommonMark) for `SECURITY.md`, `CHANGELOG.md`, `README.md`. No source code added or modified.
**Primary Dependencies**: Bash 3.2-compatible only for the AC-2 cross-check command (`cat`, `git`, `gh` CLI). All already required by the existing tachi tooling baseline.
**Storage**: Files in repo (markdown + JSON manifest read-only). No database, no persistent state introduced.
**Testing**: N/A — no source code change; no automated tests required by the spec. Verification is post-merge `/security` re-scan (FR-013) plus manual UI inspections (FR-010, FR-011, FR-012). Per Principle VII §Exceptions: "Documentation-only changes may not require production deployment" — this exemption applies; constitution-mandated test coverage thresholds (Principle VI) do not bind for documentation files. Per Principle VII §Non-Negotiable Validation Steps, F-3 still satisfies DoD via: ✅ Pushed to main (squash-merge); ✅ Tested (post-merge `/security` re-scan + UI inspections); ✅ User-validated (PR review + post-merge button-visible check).
**Target Platform**: GitHub-hosted repo (`github.com/davidmatousek/tachi`); read by humans on web (Security tab), in IDE clones, and via `make update`.
**Project Type**: single (documentation-only docs change to existing tachi repo). No new project structure introduced.
**Performance Goals**: N/A — file-render time governed by GitHub web UI, not under tachi control.
**Constraints**: ≤ 4 hours active maintainer time (SC-008); same-day-or-next-day wall-clock target (PRD §Estimate); manifest-vs-tag cross-check must be re-verified at SECURITY.md write time (FR-003).
**Scale/Scope**: SECURITY.md ~80 LOC after rewrite (replacing existing 40 LOC); CHANGELOG.md ~5 LOC delta; README.md ~1 LOC delta; one repo-setting toggle change. Total: ~100 LOC PR + 1 out-of-tree setting.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle-by-principle (only applicable principles enumerated)

| Principle | Applicability | Status | Note |
|-----------|---------------|--------|------|
| I. General-Purpose Architecture | N/A | PASS | Documentation; no domain-specific logic added |
| II. API-First Design | N/A | PASS | No API change |
| III. Backward Compatibility | APPLIES | PASS | File replacement is non-breaking; URL fallback in SECURITY.md preserves disclosure path even pre-toggle-enable |
| IV. Concurrency & Data Integrity | N/A | PASS | No state transitions |
| V. Privacy & Data Isolation | N/A | PASS | No data handling |
| VI. Testing Excellence | EXEMPTED | PASS | Per Principle VII §Exceptions for documentation-only changes; verification is via /security re-scan + manual UI checks (FR-010..FR-013) |
| VII. Definition of Done (NON-NEGOTIABLE) | APPLIES | PASS | DoD steps satisfied: (1) Pushed via squash-merge to main; (2) Tested via post-merge /security re-scan + manual UI inspections per FR-013/FR-011/FR-012; (3) User-validated via PR review + post-merge button-visible check |
| VIII. Observability & RCA | N/A | PASS | No code paths instrumented |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | APPLIES | PASS | Feature branch `272-security-md-disclosure` exists; conventional-commit PR title `feat(272): …` planned per FR-014; F-212 incident recovery flow on standby |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | APPLIES | PASS | PRD approved 2026-05-08 (PM ✓, Architect ⚠, Team-Lead ⚠); spec PM-signed APPROVED 2026-05-08; plan dual-signoff this gate |
| XI. SDLC Triad Collaboration | APPLIES | PASS | Triad reviewed PRD; PM authored spec and signed off; Architect + Team-Lead reviewing plan and tasks per /aod.plan and /aod.tasks |

### Gate verdict

**Constitution Check: PASS — no violations to track.** F-3's documentation-only profile means most principles either don't apply or are exempted by Principle VII §Exceptions. The mandatory-applicable principles (III, VII, IX, X, XI) all have clear satisfaction paths via the spec's FR-001..FR-014.

### Complexity Tracking

*Empty — no Constitution Check violations to justify.*

## Project Structure

### Documentation (this feature)

```
specs/272-security-md-disclosure/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research phase output (already created at /aod.spec time; updated below)
├── spec.md              # Feature specification (PM ✓ APPROVED 2026-05-08)
├── checklists/
│   └── requirements.md  # Spec quality checklist (created at /aod.spec time, all items pass)
└── tasks.md             # Task breakdown (/aod.tasks output — pending)
```

> **No `data-model.md`, `contracts/`, or `quickstart.md` Phase-1 design artifacts**: F-3 is documentation-only. There are no API contracts to specify, no entities with state transitions to model, and no source-code quickstart to author. The "verification recipe" (post-merge `/security` re-scan + UI inspections) is captured in plan.md §Phase 1 Design Notes below rather than as a standalone quickstart file.

### Source Code (repository root)

```
# tachi repo root — files touched by F-3
SECURITY.md           # REWRITE: 40 LOC → ~80 LOC; GitHub-canonical 5-section structure (FR-001..FR-007)
README.md             # APPEND: 1 LOC under ## Community section line 44 area (FR-008)
CHANGELOG.md          # APPEND: ~5 LOC under ## Unreleased → ### Features subsection (FR-009)
```

```
# Out-of-tree (GitHub repo settings)
Settings → Code security and analysis → Advanced Security → Private vulnerability reporting  # TOGGLE: OFF → ON (FR-010)
```

**Structure Decision**: Single-project documentation overlay onto the existing tachi repo root. No new directories introduced. No agent / command / skill / script / contract / schema modifications (per PRD §Non-Goals NG3 + NG4). Spec §Assumptions explicitly restates these absences-of-action (no `finding.yaml` shape change, no code change). PR title `feat(272): SECURITY.md and private disclosure channel` enforced per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles to ensure release-please trigger (per FR-014; F-212 incident recovery flow on standby if release-please skips).

## Phase 0 — Research (Already Complete)

`research.md` was authored during /aod.spec on 2026-05-08 with four parallel research streams (KB lookup, codebase scan, architecture/governance read, web research). Key plan-stage-relevant findings re-confirmed at /aod.project-plan time:

### Plan-stage re-cross-check (per PM Observation 2)

The manifest-vs-tag state was re-checked at plan-stage time (2026-05-08, just now):

```
$ cat .release-please-manifest.json
{ ".": "4.31.0" }

$ git tag --list 'v*' | sort -V | tail -5
v4.28.0  v4.29.0  v4.30.0  v4.31.0  v4.32.0

$ gh pr list --state open --search "release-please" --limit 3
(empty)
```

**State unchanged from PRD draft**: manifest 4.31.0, latest tag v4.32.0, no open release-please PR. The discrepancy is real and persistent. AC-14 (post-merge follow-up chore Issue) remains warranted. SECURITY.md text MUST reference the latest *tag* (`v4.32.0`), not the manifest version, per FR-003.

### Plan-stage re-cross-check (per PM Observation 1)

The `README.md` `## Community` section was re-checked at plan-stage time:

```
$ grep -n "## Community\|Security vulnerabilities" README.md
40:## Community
44:- **Security vulnerabilities** → [private advisory](https://github.com/davidmatousek/tachi/security/advisories/new) (do not post publicly)
```

**Line numbers unchanged from spec draft**: `## Community` at line 40, security bullet at line 44. FR-008's reference is accurate at plan-stage time. The implementation phase will re-verify (one final time at SECURITY.md/README.md write time).

### Open decisions resolved at plan stage

| Decision | Choice | Rationale | Alternatives rejected |
|----------|--------|-----------|-----------------------|
| **D-1**: Where to insert AC-12 README pointer | Sibling bullet under `## Community` (after line 44 existing security bullet) | More discoverable than extending the existing bullet; matches PRD's "one-line pointer" framing as a distinct line | (A) Extend existing line-44 bullet inline (rejected: less discoverable, blurs existing direct-URL pattern) (B) Add new top-level `## Security` subsection (rejected: duplicates Community-section role; would crowd the README TOC) |
| **D-2**: SECURITY.md section order | Supported Versions → Reporting a Vulnerability → What to expect → Scope → Out-of-scope (per PRD §Proposed-Solution) | GitHub Docs prescribes "Supported Versions" and "Reporting a Vulnerability" verbatim; community convention adds the other three; PRD adopted ordering matches procurement-questionnaire baseline | (A) Reporting-first ordering (rejected: PRD §Proposed-Solution explicitly chose Supported-Versions-first to put procurement-relevant content above the fold) |
| **D-3**: SECURITY.md "Reporting" R-2 footer wording | Use PRD §R-2 verbatim: *"Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security"* | Per PM Observation 3 — preserve PRD wording exactly; do not paraphrase | Paraphrased footer (rejected: PRD §Risks-and-Mitigations R-2 specifies exact wording for the maintainer-facing operational note) |
| **D-4**: CHANGELOG entry style | Match F-2 precedent: subsection under `## Unreleased → ### Features` titled `### SECURITY.md and private disclosure channel (BLP-02 F-3)`; bullets cite SECURITY.md restructure, README.md pointer, PVR toggle, TACHI-VULN-05abc41ad4cc closure | F-2's PR #257 pattern is the most recent BLP-02 successful release-trigger; matching it ensures release-please picks up the entry consistently | (A) Compact one-liner under `### Changed` (rejected: less expressive; F-2 multi-line precedent is the BLP-02 cadence-norm) (B) Standalone `### Security` subsection (rejected: not a CHANGELOG-keepachangelog convention used in this repo) |
| **D-5**: Toggle-enable verification evidence format | Plain-text confirmation in PR description plus a screenshot. Plain-text is the primary fallback if screenshot upload is impractical at delivery time. | Per AC-6 the PR description must capture verification; plain-text is reviewable without image attachments and survives PR-archive scenarios where screenshots are sometimes lost | Screenshot-only (rejected: brittle in archived/exported-PR scenarios; plain-text is durable) |
| **D-6**: Order of operations at delivery time | (1) Run AC-2 cross-check; (2) Write SECURITY.md; (3) Append CHANGELOG entry; (4) Append README pointer; (5) Push branch + open PR (draft); (6) Toggle PVR ON in repo settings; (7) Capture verification evidence in PR description; (8) Smoke-test advisory URL; (9) Mark PR ready for merge; (10) Squash-merge; (11) Verify release-please PR opens (FR-014 recovery flow on standby) | Splits in-tree work (steps 2-5) from out-of-tree work (steps 6-8) so reviewers see file diff before manual repo-setting; matches BLP-02 prior-wave cadence | (A) Toggle-first then PR (rejected: review attention is best at the file-diff stage; toggle is reversible) (B) All-in-one commit before toggle (rejected: pre-merge smoke-test of the URL helps catch GitHub-side regressions before commitment) |

**No NEEDS CLARIFICATION markers remain.** All plan-stage decisions are resolved.

## Phase 1 — Design & Contracts

**This feature has no API contracts, data model entities, or quickstart-style script artifact.** Phase 1 design output is the file-touch matrix and verification recipe below.

### File-touch matrix

| Artifact | Action | LOC delta | Spec FR | Verification |
|----------|--------|-----------|---------|--------------|
| `SECURITY.md` | Rewrite (40 → ~80) | +40 net | FR-001..FR-007 | Reviewer diff inspection; section-name verbatim check (Supported Versions, Reporting a Vulnerability) |
| `CHANGELOG.md` | Append entry to `## Unreleased → ### Features` | +5 | FR-009 | Reviewer diff; entry style matches F-2 precedent |
| `README.md` | Append sibling bullet under `## Community` after line 44 | +1 | FR-008 | Reviewer diff; pointer to `[SECURITY.md](SECURITY.md)` is discoverable |
| GitHub repo Settings | Toggle Private Vulnerability Reporting OFF → ON | (out of tree) | FR-010 [MANUAL-ONLY] | Plain-text confirmation + screenshot in PR description |
| `https://github.com/davidmatousek/tachi/security` | Visit page (read-only) | (out of tree) | FR-011 [MANUAL-ONLY] | Manual UI inspection: *Report a vulnerability* button visible |
| `https://github.com/davidmatousek/tachi/security/advisories/new` | Visit page (read-only smoke test; no submit) | (out of tree) | FR-012 [MANUAL-ONLY] | Form loads; no 404; no submission |
| `.aod/results/security-scan.md` | Re-scan post-merge | (autogenerated) | FR-013 | TACHI-VULN-05abc41ad4cc → REMEDIATED; no new HIGH/MEDIUM |
| GitHub PR title | Set to `feat(272): SECURITY.md and private disclosure channel` | (PR metadata) | FR-014 | `gh pr view <PR>` confirms title; release-please PR opens within ~30s post-merge |

### Section-by-section SECURITY.md outline (drafted; final wording at /aod.tasks step + implementation)

**Heading**: `# Security Policy` (kept from current file).

**Section 1 — Supported Versions** (FR-002):
- Statement: *"Only the latest minor of v4.x receives security updates. Older minors are deprecated immediately on the next minor release."*
- Worked example: *"v4.32.0 is the current latest minor (released 2026-05-07). Once v4.33.0 ships, v4.32.x will be deprecated for security purposes immediately. Adopters consuming via `make update` should pin to the major line (`v4.x`) rather than a specific minor; adopters who require longer-than-rolling support windows for a specific minor should fork or adopt the same backport pattern themselves."*
- Note: cross-checked at SECURITY.md write time per FR-003. Latest tag re-verified at plan stage = v4.32.0 (manifest still at 4.31.0; AC-14 chore Issue covers the discrepancy).

**Section 2 — Reporting a Vulnerability** (FR-004):
- Primary instruction: *"Use the **Report a vulnerability** button on the [Security tab](https://github.com/davidmatousek/tachi/security) of this repo."*
- Fallback: *"Or navigate directly to `https://github.com/davidmatousek/tachi/security/advisories/new` to open a private advisory."*
- Prohibition: *"Please do not open a public GitHub Issue for security vulnerabilities — public Issues broadcast the vulnerability before a fix is available."*
- Subsection `### What to include`: description / steps to reproduce / affected components / potential impact.
- Footer (per D-3, PRD §R-2 verbatim): *"Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security."*

**Section 3 — What to expect** (FR-005):
- *"**Acknowledgment** within 5 business days."* (Issue-#272-adopted SLA per PRD §AC-4.)
- *"**Assessment** within 1 week of acknowledgment."*
- *"**Fix or mitigation** timeline communicated after assessment."*
- *"**Credit** in the fix commit and release notes by default; anonymity available on request."*

**Section 4 — Scope** (FR-006):
- In-scope tachi codebase paths: `.aod/scripts/bash/`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/`, `stacks/`
- Stack-pack scaffolds **as shipped**: `stacks/*/scaffold/` (vulnerabilities in tachi's default scaffolded templates are in-scope)
- Schema definitions: `contracts/`, `schemas/`
- Template content
- tachi-shipped configuration files

**Section 5 — Out-of-scope** (FR-007):
- Claude Code itself → report to Anthropic
- Third-party MCP servers → report to their maintainers
- Adopter personalization data: `.aod/personalization.env`, `brands/*/`
- Adopter-modified scaffold output (post-`make scaffold` customizations) → adopter's responsibility
- Threat-model accuracy concerns (false positives, missed threats) → file as regular [GitHub Issues](https://github.com/davidmatousek/tachi/issues), not security advisories

### CHANGELOG.md entry outline (FR-009)

```markdown
## Unreleased

### Features

### SECURITY.md and private disclosure channel (BLP-02 F-3)

Restructured `SECURITY.md` to GitHub-canonical sections (Supported Versions /
Reporting a Vulnerability / What to expect / Scope / Out-of-scope) and enabled
the GitHub repo's **Private vulnerability reporting** toggle so the *Report a
vulnerability* button surfaces on the Security tab.

- **Supported Versions**: latest-minor-only of v4.x; older minors deprecated
  immediately on next minor release.
- **Reporting**: primary path is the Security-tab button; fallback URL retained.
- **Response SLA**: 5 business days to acknowledge.
- **Scope**: tachi codebase + scaffolds-as-shipped in-scope; Claude Code,
  third-party MCP servers, and adopter personalization explicitly out-of-scope.
- **README pointer**: one-line link to `SECURITY.md` from the Community section.

Closes [TACHI-VULN-05abc41ad4cc](.aod/results/security-scan.md) (INFO,
A05 Security Misconfiguration). BLP-02 Wave 3.
```

### README.md insertion outline (FR-008)

Insert as a sibling bullet immediately after line 44 in the `## Community` section:

```markdown
- **Full security policy** → [SECURITY.md](SECURITY.md) (supported versions, response SLA, scope)
```

### Verification recipe (post-merge)

1. **Run `/security`** — should output `TACHI-VULN-05abc41ad4cc → REMEDIATED` in `.aod/results/security-scan.md`. No new HIGH/MEDIUM findings; LOW/INFO side-effect findings acceptable if they document a separate concern.
2. **Visit Security tab** at `https://github.com/davidmatousek/tachi/security` — confirm *Report a vulnerability* button is visible.
3. **Smoke-test advisory URL** at `https://github.com/davidmatousek/tachi/security/advisories/new` — confirm form loads; do NOT submit.
4. **Verify release-please PR** opened within ~30s of squash-merge: `gh pr list --state open --search "release-please" --limit 3`. If empty, push empty marker commit per F-212 recovery flow.
5. **Update INDEX.md and BLP-02 memory record** at /aod.deliver time: status flip Approved → Delivered with PR link; BLP-02 Wave 3 → DELIVERED.

### Agent context update

Per /aod.project-plan Step 2c, update agent context for the active stack. Run `.aod/scripts/bash/update-agent-context.sh claude` at the implementation time to refresh any agent-specific context that depends on the spec/plan deliverables. For F-3 specifically, expected delta is minimal because no new code, agent, or skill is introduced.

## Constitution Re-check (post-Phase-1 design)

| Principle | Status post-design | Note |
|-----------|---------------------|------|
| III. Backward Compatibility | PASS | File replacement preserves URL fallback for pre-toggle-enable researchers; no breaking change to local workflows |
| VII. Definition of Done | PASS | All three DoD steps mapped: ✅ Pushed (squash-merge); ✅ Tested (post-merge re-scan + UI inspection per FR-013/FR-011/FR-012); ✅ User-validated (PR review + button-visible inspection) |
| IX. Git Workflow | PASS | Feature branch ready; PR title `feat(272):` per FR-014; F-212 recovery on standby |
| X. Product-Spec Alignment | PASS | PRD ✓ Approved, spec ✓ PM-signed; this plan dual-signoff via /aod.project-plan |
| XI. SDLC Triad Collaboration | PASS | Triad reviewed PRD; PM authored spec; Architect + Team-Lead review at plan and tasks stages |

**Verdict: PASS — no new violations introduced by the Phase-1 design.**

## Complexity Tracking

*Empty — no Constitution Check violations to justify.*
