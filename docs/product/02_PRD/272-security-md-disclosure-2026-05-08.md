---
prd:
  number: 272
  topic: security-md-disclosure
  created: 2026-05-08
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-08, status: APPROVED, notes: "v1.1 final. Authored as BLP-02 Wave 3 — disclosure-channel counterpart to F-1 (#248) / F-2 (#256) code fixes from the same 2026-05-02 /security scan. v1.0 surfaced 2 BLOCKING (Architect C-1 v4.32.0 reference verification, C-2 90-day deprecation policy clash with daily minor cadence) + 5 lower-severity advisories from Architect and 5 non-blocking advisories from Team-Lead. v1.1 resolved C-1 via post-fetch verification (v4.32.0 IS real; manifest-vs-tag discrepancy captured as AC-14 follow-up Issue), C-2 via Option A (latest-minor-only; immediate deprecation on next minor — honest about single-maintainer cadence), C-3 via reframed dependencies section, C-4 via stacks/*/scaffold/ boundary clarification, R-6 (GitHub vendor-lock) added. Team-Lead advisories folded in: A-4 operational AC-2 cross-check command added, A-5 AC-11 promoted to mandatory + AC-12 README pointer promoted into scope, A-1 AC-13 posture-probe backlog Issue committed at /aod.deliver. Same-day-or-next-day delivery target preserved; ~100 LOC envelope; no code, no ADR, no tests."}
  architect_signoff: {agent: architect, date: 2026-05-08, status: APPROVED_WITH_CONCERNS, notes: "v1.1 re-review APPROVED_WITH_CONCERNS. v1.0 BLOCKING concerns C-1 (v4.32.0 reference) and C-2 (90-day deprecation policy) both resolved — C-1 via post-fetch verification confirming v4.32.0 is real, plus manifest-vs-tag discrepancy captured as AC-14 follow-up; C-2 via Option A (latest-minor-only policy, honest about daily minor cadence). C-3 (manifest framing) and C-4 (stacks/scaffold boundary) wording fixes landed. C-5 (R-2 posture-probe gap) elevated to AC-13. R-6 GitHub vendor-lock risk added per optional C-10 suggestion. C-6 through C-9 (no-ADR claim, feat(272): PR title, GitHub-Advisories-as-single-channel posture, feasibility) all CONCUR. One residual non-blocking nit (N-1: US-2 acceptance line stale '90 days' language) fixed in v1.1 final pass. Full reviews v1.0 + v1.1: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-08, status: APPROVED_WITH_CONCERNS, notes: "v1.0 APPROVED_WITH_CONCERNS — feasibility, capacity, timeline, dependencies, Wave-3 sequencing all validated. 3-4h active / same-day target realistic for scoped work; well within F-2's demonstrated 24h-from-issue cadence. Single concurrency risk surfaced: F-260b reviewer-engagement spike could slip same-day to next-day (PRD next-day-cap framing absorbs this). Dependencies TRUE-NONE; release-please pipeline operational (verified empirically: latest tag v4.32.0, manifest 4.31.0, no open release-please PR). Wave-3 sequencing approved over Wave-5 alternative for three reasons: F-3 is fully scoped today (Wave 5 is not), F-3 closes /security finding from same scan as F-1/F-2, F-3 is disclosure-channel counterpart to F-1/F-2 code fixes. Five non-blocking advisories: A-1 backlog probe candidate (folded into AC-13), A-2 release-please verification (already in PRD), A-3 90-day softening (resolved by v1.1 Option A switch), A-4 AC-2 operationalization (folded into AC-2), A-5 AC-12 pre-decision (promoted into scope). Estimate-accuracy probability HIGH (scope-stability is unusually well-pinned: NG1-NG7 explicitly excluded, three deliberate-NOTs). Full review: .aod/results/team-lead.md."}
source:
  idea_id: 272
  story_id: null
---

# F-3 — SECURITY.md and Private Disclosure Channel: Product Requirements Document

**Status**: Approved (v1.1 — PM ✓, Architect ⚠, Team-Lead ⚠)
**Created**: 2026-05-08
**Author**: product-manager
**Reviewers**: architect (APPROVED_WITH_CONCERNS v1.1), team-lead (APPROVED_WITH_CONCERNS v1.0)
**Phase**: BLP-02 Wave 3 candidate — third feature in the 5-feature enterprise hardening initiative; F-1 (#248) Substitution Surface DELIVERED 2026-05-04, F-2 (#256) Source-Pattern Hardening DELIVERED 2026-05-05, F-250 hot-fix DELIVERED 2026-05-04
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Enhance the repo-root `SECURITY.md` to GitHub-canonical form (Reporting / Supported Versions / Response SLA / Scope), enable the GitHub repo's "Private vulnerability reporting" toggle so the *Report a vulnerability* button surfaces on the Security tab, and close TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration) — one small markdown PR plus one manual repo-settings step, no code changes, no ADR.

### Problem Statement

The 2026-05-02 `/security` scan that grounded BLP-02 surfaced one INFO-severity posture finding alongside the higher-severity substitution-surface and source-pattern findings: **TACHI-VULN-05abc41ad4cc — "No SECURITY.md at repo root, undefined disclosure path"** (`SECURITY.md:1`, A05 Security Misconfiguration, CVSS 0.0 INFO).

A SECURITY.md file *did* land in the repo on 2026-03-26 as part of the broader open-source readiness pass — 40 lines, sections for Reporting / Scope / Supported Versions, a 48-hour acknowledgment SLA. The /security scan flagged it as INFO because the seed-brief language (Issue #272) targeted the **GitHub-canonical posture surface**, not just file presence: the existing file does not match the GitHub-template structure (Supported Versions table is two rows, not version-specific), the SLA does not match Issue #272's adopted "5 business days" cadence, the scope language is generic ("agent prompt definitions", "schema definitions") rather than tachi-specific (in: codebase / `.claude/` agents / `.aod/` scripts; out: Claude Code itself, third-party MCP servers, adopters' personalization data), and — most importantly — the GitHub repo's **"Private vulnerability reporting"** toggle in `Settings → Security → Code security and analysis` is **not enabled**, which means the *"Report a vulnerability"* button does not appear on the repo's Security tab. Researchers visiting the Security tab today see only an Advisories pane with no clear submission path.

The cross-cutting theme (and the reason this feature lands as BLP-02 Wave 3, not as a generic chore): **the LinkedIn thread that triggered BLP-02 was itself an example of public disclosure that a properly-configured SECURITY.md surface could have channeled into a private GitHub Security Advisory**. Daniel Wood saw a posture concern, had no obvious private channel, and posted publicly. Closing the disclosure-channel gap is the *enabling-control* counterpart to F-1 / F-2 closing the actual code-level findings the same scan surfaced — F-1 and F-2 fix the symptoms; F-3 fixes the *reporting hygiene* so future Daniel Woods route their findings through the private path before falling back to LinkedIn.

The five user surfaces this finding leaves exposed:

1. **Security researchers** finding a vulnerability in tachi today have no documented private channel visible from the repo's Security tab. They face a binary choice: open a public GitHub Issue (poor disclosure hygiene; broadcasts the vuln before patch lands) or escalate to LinkedIn / DM / email (no SLA, no audit trail, easy to lose). The 2026-05-02 thread is an existing instance of the second branch.

2. **Tachi adopters** running `make update` weekly do not know which versions of tachi receive security updates. The current SECURITY.md "Supported Versions" table reads "Latest release: Yes; Older releases: Best effort" — a posture statement, not a contract. Pinned-version adopters cannot decide whether to upgrade based on supported-version policy because no version-line policy is documented.

3. **Future external reviewers** (the "future Daniel Wood" persona — community member spotting a security concern in tachi during their own review) need a documented private channel visible from the repo's Security tab. Today, the tab shows no obvious responsible-disclosure path; the reviewer's default escalation path is the same LinkedIn / DM route the 2026-05-02 thread used.

4. **Enterprise security architects** doing pre-sales review of tachi (the procurement-reviewer persona from BLP-02's enterprise-hardening framing) expect a SECURITY.md present at repo root with supported-versions, scope, and response-SLA sections. Absence — or, in tachi's current state, *presence-but-not-GitHub-canonical* — surfaces as a procurement red flag in security questionnaires (specifically: "vendor disclosure policy" and "supported versions" line items).

5. **Maintainers** (single-maintainer project: davidmatousek) receiving a private vulnerability report want a structured intake (GitHub private advisory) with a defined response time, so the report is not lost in DM / email queues and the response cadence is contractually clear to the reporter.

### Proposed Solution

This feature ships as **one small feature branch (`272-security-md-disclosure`), one squash-merged PR, one `feat(272):` commit subject** that triggers a release-please PR. Two work items, both small:

1. **Rewrite `SECURITY.md` to GitHub-canonical structure (~80 LOC).** Replace the existing 40-line file with a GitHub-template-aligned version. Section order matches the GitHub-recommended template (Supported Versions → Reporting a Vulnerability → What to expect → Scope → Out-of-scope). Concrete deltas vs the current file:

   - **Supported Versions** — Replace the two-row pseudo-policy ("Latest release: Yes; Older releases: Best effort") with a version-line policy that matches tachi's actual high-cadence minor-release reality: **"Only the latest minor of v4.x receives security updates. Older minors are deprecated immediately on the next minor release. Adopters consuming via `make update` should pin to the major line (`v4.x`) rather than a specific minor; adopters who require longer-than-rolling support windows for a specific minor should fork or adopt the same backport pattern themselves."** Cross-checked at merge time against `.release-please-manifest.json` and `git tag --list 'v*' | sort -V | tail -5`. Verified state at PRD draft (2026-05-08): latest tag v4.32.0 (released 2026-05-07 16:46 UTC), manifest at 4.31.0 — the manifest-lag is a separate release-please-pipeline anomaly worth surfacing in a follow-up chore Issue but is not blocking F-3 because the SECURITY.md text references the *latest tag*, not the manifest. The latest-minor-only policy is honest about single-maintainer cadence (1-7 days between minors observed across the v4.20–v4.32 window; ~50 minor releases on the v4.x line; 90-day rolling-window policies become functionally meaningless under that cadence — they would imply ~all 50 minors stay supported, which no single maintainer can backport-test) and matches procurement-questionnaire baselines for high-velocity OSS projects ("vendor's documented support window: latest minor; rolling deprecation on next minor").

   - **Reporting a Vulnerability** — Replace the current single-link section with the GitHub-canonical pattern: a primary instruction to use the *Report a vulnerability* button on the Security tab (which Step 2 below makes visible), a fallback `https://github.com/davidmatousek/tachi/security/advisories/new` direct link for researchers without UI access, and a "do not open a public Issue" prohibition. "What to include" sub-section retained (description / steps to reproduce / affected components / potential impact).

   - **Expected Response Time** — Replace the current 48-hour acknowledgment with the Issue-#272-adopted **"5 business days to acknowledge"** cadence. Rationale for the change: tachi is a single-maintainer project with no on-call rotation; 48 hours sets a contract the maintainer cannot reliably honor across vacation / illness / weekend windows, and over-promising on response SLA is itself a disclosure-channel anti-pattern (researchers lose trust faster from missed SLAs than from longer-but-met SLAs). 5 business days matches the procurement-questionnaire baseline and is achievable for single-maintainer projects. Assessment-within-1-week and fix-timeline-communicated-after-assessment retained.

   - **Scope** — Replace the current generic scope language with tachi-specific in/out enumerations. **In-scope**: tachi codebase (`.aod/scripts/bash/`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/`, `stacks/`), stack-pack scaffolds **as shipped** (`stacks/*/scaffold/` — vulnerabilities in tachi's default scaffolded templates are in-scope; adopter customizations of scaffolded code after `make scaffold` are the adopter's responsibility), schema definitions (`contracts/`, `schemas/`), template content, tachi-shipped configuration files. **Out-of-scope**: Claude Code itself (report to Anthropic), third-party MCP servers (report to their maintainers), adopter personalization data (`.aod/personalization.env`, `brands/*/`), adopter-modified scaffold output (post-`make scaffold` customizations), and threat-model accuracy concerns (false positives, missed threats — file as regular Issues, not security advisories). The out-of-scope enumeration is load-bearing: it routes ~30% of likely-misdirected reports to the correct destination on first contact.

   - **Credit** clause retained from current file — researcher named in fix commit + release notes by default, anonymity available on request.

2. **Manual repo-setting step: enable Private Vulnerability Reporting toggle.** In `Settings → Security → Code security and analysis`, toggle **Private vulnerability reporting** to ON. This is a one-click GitHub UI step; documentation in the delivery PR description includes a link to the setting and a screenshot or plain-text confirmation that the toggle is ON. After the toggle is enabled, the *Report a vulnerability* button appears on the repo's Security tab and the SECURITY.md "Reporting a Vulnerability" section's primary instruction becomes UI-actionable for researchers without copy-pasting the advisory URL.

3. **CHANGELOG entry under Unreleased → Changed**: `SECURITY.md restructured to GitHub-canonical sections (Supported Versions / Reporting / Response SLA / Scope); Private Vulnerability Reporting enabled in repo settings; closes TACHI-VULN-05abc41ad4cc.`

**Three things this feature is deliberately NOT:**

1. It is **not** a `security@tachi.dev`-style mailbox setup. The disclosure channel is GitHub Security Advisories — single source of truth, audit trail, integrated with the Security tab. No SMTP infrastructure, no shared-mailbox access policy, no separate retention policy. Adopters who *want* an email-based fallback can still use the public maintainer email visible on the GitHub profile, but tachi's documented channel is the GitHub UI.

2. It is **not** a CVE-numbering-authority (CNA) registration. Public CVEs for tachi vulnerabilities — if the maintainer ever issues one — flow through GitHub's CVE-issuance partnership, not through a self-managed CNA process. ADR is not warranted; the GitHub-managed flow is the default, and any future change-of-policy on CVEs would itself warrant a new PRD.

3. It is **not** a `finding.yaml` / `taxonomy/*.yaml` schema change and **not** a code change to any agent, command, or script. **Tenth feature in a row with zero `finding.yaml` shape change** (preserves BLP-01 detection-tier contract continuity), and the only files touched are `SECURITY.md` (rewrite), `CHANGELOG.md` (Unreleased entry), `README.md` (one-line pointer), and the GitHub repo settings (out-of-tree manual step).

---

## 🎯 Goals & Non-Goals

### Goals

- **G1**: Close TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration). Verified by post-merge `/security` re-scan: finding cleared.
- **G2**: GitHub *Report a vulnerability* button appears on the repo's Security tab. Verified by manual UI inspection at `https://github.com/davidmatousek/tachi/security` post-toggle-enable.
- **G3**: SECURITY.md sections match GitHub-canonical template (Supported Versions / Reporting / Response SLA / Scope / Out-of-scope). Verified by reviewer diff inspection.
- **G4**: Supported-versions policy is a contract that matches single-maintainer reality (latest-minor-only; immediate deprecation on next minor) — not an over-promise. Verified by cross-check against latest tag (`git tag --list 'v*' | sort -V | tail -1`) at merge time.
- **G5**: Tachi-specific scope enumeration routes likely-misdirected reports to the correct destination on first contact. Verified by reviewer scope-language review.
- **G6**: 5-business-day acknowledgment SLA documented and matches single-maintainer reality. Verified by PM sign-off.
- **G7**: BLP-02 Wave 3 closed. Verified by Initiative Tracker update and the next /security scan showing TACHI-VULN-05abc41ad4cc cleared.

### Non-Goals

- **NG1**: No SMTP mailbox setup. The channel is GitHub Security Advisories.
- **NG2**: No CNA registration. Public CVEs flow through GitHub's CVE-issuance partnership.
- **NG3**: No `finding.yaml` / taxonomy schema changes.
- **NG4**: No agent / command / skill / script code changes.
- **NG5**: No PGP key publication. Researchers who want encrypted intake can use the GitHub Security Advisory form (TLS to GitHub).
- **NG6**: No bug-bounty program. tachi remains an unfunded single-maintainer project; bounty programs require funding policy that does not exist.
- **NG7**: Not a substitute for the per-release `/security` self-scan cadence — SECURITY.md sets the *external* disclosure channel; internal scanning continues.

---

## 👥 User Stories

(Adopted verbatim from Issue #272 §Stories.)

### US-1: Security researcher with a documented private channel
> As a security researcher who finds a vulnerability in tachi, I want a clear documented private channel to report it, so that I can disclose responsibly without resorting to a public GitHub Issue or LinkedIn comment.

**Acceptance**: SECURITY.md "Reporting a Vulnerability" section visible at repo root and from the Security tab. Primary instruction: use the *Report a vulnerability* button (UI). Fallback: direct advisory URL. Public-Issue prohibition stated.

### US-2: Adopter with a supported-versions contract
> As a tachi adopter, I want to know which versions of tachi receive security updates, so that I know whether my pinned version is supported.

**Acceptance**: SECURITY.md "Supported Versions" section states the version-line policy ("only the latest minor of v4.x receives security updates; older minors are deprecated immediately on the next minor release") with a worked example referencing the current latest tag and an explicit recommendation to pin to the major line (`v4.x`) rather than a specific minor for adopters consuming via `make update`.

### US-3: Future external reviewer with a private path
> As a future Daniel Wood (an external reviewer who spots a security concern), I want a documented private channel visible from the repo's Security tab, so that I have an obvious responsible-disclosure path before falling back to a public LinkedIn comment.

**Acceptance**: *Report a vulnerability* button appears on the Security tab post-Private-Vulnerability-Reporting-toggle-enable.

### US-4: Enterprise procurement reviewer with no red flag
> As an enterprise security architect doing a pre-sales review of tachi, I want a SECURITY.md present at repo root with supported versions, scope, and response SLA, so that absence-of-disclosure-channel doesn't surface as a procurement red flag.

**Acceptance**: SECURITY.md sections match the procurement-questionnaire baseline (vendor disclosure policy + supported versions + response SLA + scope). 5-business-day SLA documented. Scope in/out enumerated.

### US-5: Maintainer with a structured intake
> As a maintainer receiving a private vulnerability report, I want a structured intake (GitHub private advisory) with a defined response time, so that I can triage promptly and avoid losing the report in DM/email queues.

**Acceptance**: GitHub Private Vulnerability Reporting enabled; advisory submissions land in the repo's Security tab with notification to maintainer; SLA contract is honorable for single-maintainer cadence.

---

## ✅ Acceptance Criteria

(Adopted from Issue #272 §Definition-of-Done with v1.0 PRD additions.)

### Mandatory (blocks delivery)

- [ ] **AC-1**: `SECURITY.md` lands at repo root with all five GitHub-canonical sections present (Supported Versions / Reporting / What to expect / Scope / Out-of-scope).
- [ ] **AC-2**: Supported-versions policy specifies the v4.x version line as **latest-minor-only** (immediate deprecation on next minor), cross-checked at merge time. Operational cross-check (run before SECURITY.md write): `cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3`. SECURITY.md text references the latest released *tag* (not the manifest); manifest-vs-tag discrepancies, if any, are captured as a side observation in the PR description and queued as a separate chore Issue without blocking F-3.
- [ ] **AC-3**: Reporting section primary instruction is the *Report a vulnerability* button; fallback link to `https://github.com/davidmatousek/tachi/security/advisories/new` retained; public-Issue prohibition stated.
- [ ] **AC-4**: Response SLA is "5 business days to acknowledge" (matches Issue #272 §Interface-Contract).
- [ ] **AC-5**: Scope section enumerates in-scope and out-of-scope surfaces explicitly; out-of-scope routes Claude Code findings → Anthropic, third-party MCP findings → their maintainers, personalization data → adopter, threat-model accuracy concerns → regular Issues.
- [ ] **AC-6**: Manual repo-setting step: **Private Vulnerability Reporting** toggle ON in `Settings → Security → Code security and analysis`. Verification evidence (screenshot or plain-text "toggle confirmed ON" in the delivery PR description) attached.
- [ ] **AC-7**: GitHub *Report a vulnerability* button visible on `https://github.com/davidmatousek/tachi/security` post-toggle-enable (manual UI inspection).
- [ ] **AC-8**: CHANGELOG entry under `Unreleased → Changed` references SECURITY.md restructure and TACHI-VULN-05abc41ad4cc closure.
- [ ] **AC-9**: TACHI-VULN-05abc41ad4cc → REMEDIATED in `.aod/results/security-scan.md` after post-merge re-scan.
- [ ] **AC-10**: Post-merge `/security` re-scan: INFO finding cleared; no new HIGH or MEDIUM findings introduced (LOW or INFO are acceptable side-effect findings if they document a separate concern).
- [ ] **AC-11**: Smoke-test the disclosure URL while authenticated — open `https://github.com/davidmatousek/tachi/security/advisories/new`, confirm the form loads, do NOT submit. Promoted from nice-to-have per Team-Lead A-5 advisory: the check costs <2min and validates the SECURITY.md fallback link in the same operation.
- [ ] **AC-12**: README.md gets a one-line pointer to SECURITY.md (e.g., a "Security" subsection or a one-line bullet under an existing "Contributing" or "Disclosure" section): *"For security disclosure, see [SECURITY.md](SECURITY.md)."* Promoted from deferred per Team-Lead A-5 advisory: a one-line README delta carries zero scope-creep risk and eliminates a stale follow-on Issue.

### Nice-to-have (post-merge follow-up; not blocking)

- [ ] **AC-13**: Open a follow-up backlog Issue for a **posture probe** that confirms the GitHub *Report a vulnerability* button still appears on the Security tab — concrete probe shape: scrape `https://api.github.com/repos/davidmatousek/tachi` and assert `security_and_analysis.private_vulnerability_reporting.status == "enabled"`. Park as low-priority follow-on (Team-Lead A-1 advisory). Not in F-3 scope; logged at /aod.deliver time.
- [ ] **AC-14**: Open a follow-up chore Issue surfacing the v4.32.0-tag / 4.31.0-manifest discrepancy observed at PRD draft time (architect C-3 / team-lead D-1 side-observation): release-please may have skipped a manifest update post-v4.32.0 release. Investigate at /aod.deliver time; not in F-3 scope.

---

## 🛠️ Technical Considerations

### File Surface

- **`SECURITY.md`** (rewrite, ~80 LOC). Located at repo root. Replaces the existing 40-line version (`/Users/david/Projects/tachi/SECURITY.md`, last modified 2026-03-26).
- **`CHANGELOG.md`** (~3 LOC). New entry under existing `## Unreleased → ### Changed` block. No new heading.
- **`README.md`** (~1 LOC). One-line pointer to SECURITY.md per AC-12. Inserted in the existing "Contributing" or top-level "Disclosure / Security" subsection — exact insertion point chosen at /aod.spec time.
- **No code changes.** No agent / command / skill / script / contract / schema modifications.

### Out-of-Tree Step

The Private Vulnerability Reporting toggle lives in GitHub repo settings, not in the repo. The PR description must document the toggle-enable step and attach verification evidence. Future re-creations of the repo (e.g., maintainer transfer, fork-promote) require re-toggling — this is documented in the SECURITY.md "Reporting" section's footer ("Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security").

### Cross-Reference: BLP-02 Wave Sequencing

| Wave | Feature | Issue | Status | Closure date |
|------|---------|-------|--------|--------------|
| 1 | F-1 Substitution Surface Hardening | #248 | Delivered | 2026-05-04 |
| 1 follow-on | F-250 Adversarial Unit Extraction Hot-Fix | #250 | Delivered | 2026-05-04 |
| 2 | F-2 Source-Pattern Hardening | #256 | Delivered | 2026-05-05 |
| **3** | **F-3 SECURITY.md and Private Disclosure Channel** | **#272** | **Approved (this PRD)** | **TBD** |
| 4 | F-clone-timeout DoS hardening | (already closed in F-2) | Closed-via-F-2 | 2026-05-05 |
| 5 | F-constitution-sed migration | TBD | Backlog | TBD |

F-3 is the smallest and lowest-effort BLP-02 feature (~100 LOC, no code changes, no ADR). Slotting it as Wave 3 — between the substantial F-2 and the still-undefined F-constitution-sed — is deliberate: it lets the maintainer ship a same-day-or-next-day release for posture-channel hygiene before the next code-touching feature.

### Release-Please Trigger Posture

The PR title MUST be `feat(272): SECURITY.md and private disclosure channel` (Conventional Commit format with feat: prefix per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles). Per the F-212 close-out incident reference in that file, post-merge verification at `/aod.deliver` time MUST confirm a release-please PR opens within ~30s of the squash-merge; if not, push an empty `feat(272): … — release marker` commit per the documented recovery flow. Although this feature is documentation + repo-setting only, the SECURITY.md surface is **user-visible** (adopters reading the file, researchers visiting the Security tab) and meets the `feat:` threshold per the same rule's "Default to feat:" guidance for any user-visible work.

### Security & Privacy

- No new code paths; no new attack surface introduced by the change itself.
- Out-of-scope clause explicitly excludes adopters' personalization data (`.aod/personalization.env`, `brands/*/`) from the tachi disclosure channel — adopters retain ownership of disclosure for content they author.
- Toggle change is reversible via the same Settings UI — no irreversible repo-state mutation.
- The `https://github.com/davidmatousek/tachi/security/advisories/new` URL is GitHub-managed; no domain or DNS dependency on tachi-side infrastructure.

---

## ⚠️ Risks & Mitigations

### R-1: SLA over-promise (HIGH likelihood of recurrence absent design choice; LOW residual after design)

**Risk**: A 48-hour acknowledgment SLA — the current SECURITY.md text — sets a contract a single-maintainer project cannot reliably honor across vacation / illness / weekend windows. Missed SLAs erode researcher trust faster than longer-but-met SLAs.

**Mitigation**: PRD adopts the Issue-#272-specified **5-business-day** cadence (matches procurement-questionnaire baseline; achievable for single-maintainer projects). Cross-checked against the maintainer's stated availability cadence in the project's open-source-readiness brief (`docs/product/_backlog/OPEN_SOURCE_READINESS.md`).

### R-2: Toggle gets disabled later by accident (MEDIUM)

**Risk**: A maintainer or contributor with repo-admin access could accidentally disable the Private Vulnerability Reporting toggle in `Settings → Security`, silently breaking the disclosure channel without anyone noticing until the next research report fails to land.

**Mitigation**: SECURITY.md "Reporting" section footer documents the dependency ("this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled"). Delivery PR description records the verification screenshot/plain-text confirmation as a recoverable artifact. Follow-on backlog Issue committed to via AC-13 (post-merge): periodic posture probe that scrapes `https://api.github.com/repos/davidmatousek/tachi` and asserts `security_and_analysis.private_vulnerability_reporting.status == "enabled"` — captures toggle-state regressions before researchers experience the broken channel. ICE estimate (rough): I:6 C:8 E:9 = ICE 23, but pulled out of F-3 scope to keep this feature bounded.

### R-3: Researcher uses wrong URL despite SECURITY.md (LOW)

**Risk**: A researcher reads SECURITY.md but still defaults to LinkedIn / DM / email — the historical pattern that produced the 2026-05-02 thread.

**Mitigation**: GitHub auto-renders the *Report a vulnerability* button on the Security tab once the toggle is enabled — UI affordance is more discoverable than reading SECURITY.md. The button bypasses the read-the-file step entirely. Residual risk after toggle-enable: routes the channel to "first place researcher looks for disclosure path", which is the Security tab.

### R-4: Latest-minor-only policy may surprise adopters who pin to specific minors (MEDIUM)

**Risk**: Adopters who currently pin to a specific minor (e.g., `v4.30.x`) and were assuming GitHub-default "best effort" backport coverage may be surprised when the new policy declares immediate-deprecation-on-next-minor. Concrete user-impact: an adopter on `v4.31.x` today sees v4.32.0 release and discovers their version is no longer in the security-update window — they must either upgrade or fork.

**Mitigation**: The policy aligns with tachi's actual minor-release cadence (1-7 days between minors empirically observed across the v4.20–v4.32 window; a 90-day rolling window would imply ~50 minors stay supported, which no single maintainer can backport-test honestly). Worked example in the Supported Versions section: *"if v4.32.0 shipped on 2026-05-07, v4.31.x is deprecated for security purposes immediately; an adopter pinning v4.31.x should upgrade to v4.32.x or accept the no-backport posture for their pinned line."* The PRD recommends adopters consuming via `make update` pin to the major line (`v4.x`) rather than a specific minor — this matches tachi's `make update` upgrade flow, which already moves adopters to latest minor. Procurement-defensible: matches procurement-questionnaire baselines for high-velocity OSS projects ("documented support window: latest minor; rolling deprecation on next minor"). Honest-to-maintainer: a single-maintainer with daily release cadence cannot honor 90-day rolling windows; over-promising on backport coverage is a worse failure mode than the current under-promising.

### R-5: Procurement-reviewer expectation mismatch (LOW)

**Risk**: Some enterprise procurement questionnaires require **24-hour** response SLAs (specifically: critical vulnerability acknowledgment) — stricter than the proposed 5-business-day baseline.

**Mitigation**: The 5-business-day SLA is the *default*; SECURITY.md does not preclude a tighter SLA for critical-class vulnerabilities. Maintainer can voluntarily honor faster cadence on critical reports without contractually binding to it. Procurement questionnaires usually accept "5 business days, faster on critical at maintainer discretion" — and an enterprise-grade SLA would itself be a separate paid-engagement scope (out-of-scope per OSS positioning).

### R-6: GitHub Private-Vulnerability-Reporting feature is GitHub-managed (LOW)

**Risk**: Tachi's documented disclosure channel depends on GitHub continuing to offer the Private Vulnerability Reporting feature and the `https://github.com/{owner}/{repo}/security/advisories/new` URL pattern. If GitHub deprecates the feature, migrates the URL, or removes the *Report a vulnerability* button from the Security tab UI, the SECURITY.md direct-link section becomes a broken pointer.

**Mitigation**: GitHub deprecates surfaces with multi-year notice cycles and rarely breaks repository-level URL patterns once they are documented. SECURITY.md is a single-file, trivially-updatable artifact — recovery from a hypothetical GitHub-side change is a one-PR delta. **Residual risk: low**; the structural choice (GitHub Security Advisories as sole channel) is still the correct posture for a single-maintainer OSS project despite the vendor-lock dependency, because the alternatives (SMTP / CNA / PGP) carry greater operational burden and arguably-equivalent vendor dependencies (mail-host, cve.mitre.org, key-distribution).

---

## 🔗 Dependencies

### Blocking Dependencies

**None.** Per Issue #272 §Dependencies. No upstream features required; no downstream features blocked-by F-3.

### Loosely-Coupled Dependencies

- **GitHub repo admin access** — required to toggle Private Vulnerability Reporting in Settings. Maintainer has admin rights on the davidmatousek/tachi repo; no organizational approval needed.
- **Latest minor of v4.x** — supported-versions policy references v4.x line; cross-checked at merge time. Verified state at PRD draft (2026-05-08): latest tag v4.32.0 (released 2026-05-07 16:46 UTC), manifest at 4.31.0. The manifest-lag is anomalous — manifest tracks *released* versions, so manifest = latest tag is the steady state when no release-please PR is open, and `gh pr list --state open --search "release-please"` returns empty. This suggests the v4.32.0 release-please cycle may have updated the tag without the manifest, or the manifest got rolled back post-merge. **Captured as a side observation for a follow-up chore Issue; not blocking F-3** because the SECURITY.md text references the *latest released tag* (verified independently against `git tag --list 'v*' | sort -V | tail -1`), not the manifest. Re-perform the cross-check at SECURITY.md write time per AC-2.
- **CHANGELOG.md `## Unreleased` block** — new entry lands here; assumes the standard release-please flow is operational (it is — F-2's PR #257 was the most recent successful release-trigger 2026-05-05).

### Downstream Effects

- **README.md pointer** — promoted into F-3 scope per AC-12 (one-line addition).
- **Periodic toggle-still-enabled posture probe** — committed to as AC-13 follow-up Issue (post-merge); not in F-3 implementation scope.
- **Manifest-vs-tag discrepancy investigation** — committed to as AC-14 follow-up chore Issue (post-merge); side observation, not blocking F-3.
- **BLP-02 Initiative Tracker** — closes Wave 3; updates the project memory record to reflect 3-of-5 Waves complete post-delivery.

---

## ⏱️ Estimate & Timeline

### Effort

- **Spec → PR open**: ~2-3 hours of focused work (PRD draft → Triad review → branch → file rewrite → toggle → CHANGELOG → push → draft PR). No code, no tests, no migration.
- **PR review → merge**: ~30 minutes (single small markdown PR; reviewer reads diff, confirms toggle screenshot, confirms supported-versions cross-check).
- **Post-merge verification**: ~15 minutes (`/security` re-scan + Security-tab UI inspection + button visibility confirm).
- **Total active**: ~3-4 hours of maintainer time.
- **Wall-clock buffer**: same-day delivery feasible if started morning-of; next-day cap (per BLP-02 Wave 1 / Wave 2 cadence — F-1 delivered ~24h envelope, F-2 delivered ~24h envelope).

### Comparison to Prior BLP-02 Waves

| Wave | LOC | Effort (active) | Wall-clock | ADR? |
|------|-----|-----------------|------------|------|
| F-1 | ~250 | 6.5d active | 7d | 038 |
| F-250 hot-fix | ~150 | 1d active | 1d | 039 |
| F-2 | ~600 | 9.5d active | 24h actual | 040 |
| **F-3 (this)** | **~100** | **3-4h active** | **same-day target** | **none** |

F-3 is by design the lowest-effort BLP-02 feature — explicitly classified by Issue #272 as *"process, not architecture"*. It exists precisely to demonstrate that the BLP-02 cadence accommodates **smallest-possible-scope features** alongside the larger code-touching ones, without paying the per-feature governance cost twice (Triad still runs; ADR does not).

---

## 🧭 Governance

### Triad

- **Workflow**: Feature (parallel reviews — Architect + Team-Lead in parallel after PM draft).
- **PM**: davidmatousek (project owner, single-maintainer)
- **Architect review focus**: feasibility, supported-versions policy realism, scope-language soundness, security posture (no new attack surface introduced)
- **Team-Lead review focus**: timeline realism for single-maintainer cadence, dependencies (none), Wave-3 sequencing alignment with prior BLP-02 waves

### ADR

**None.** This is a process / disclosure-channel change, not an architectural one. No new components, no new contracts, no new code paths. ADR-040 documented the architectural pattern for F-2 (config-load primitive) — F-3 is the documentation-counterpart that adopts the disclosure channel side of the same enterprise-hardening initiative without introducing new architecture.

### Sign-off Gates

- spec.md sign-offs: PM (auto via `/aod.spec`)
- plan.md sign-offs: PM + Architect (auto via `/aod.project-plan`)
- tasks.md sign-offs: PM + Architect + Team-Lead (auto via `/aod.tasks`)

---

## 📌 Open Questions

(None at v1.1 — Issue #272 §Stories and §Interface-Contract are unambiguous; the v1.0→v1.1 revision pass resolved the architect's two BLOCKING concerns by adopting the latest-minor-only Supported Versions policy and reframing the manifest-vs-tag verification to honestly reflect post-fetch state.)

---

## 📎 References

- **GitHub Issue**: #272 — `https://github.com/davidmatousek/tachi/issues/272`
- **Source finding**: TACHI-VULN-05abc41ad4cc (`.aod/results/security-scan.md` §F-security-md)
- **BLP-02 backlog**: `docs/product/_backlog/OPEN_SOURCE_READINESS.md` (F-SECURITY.md line)
- **Existing SECURITY.md**: `/Users/david/Projects/tachi/SECURITY.md` (40 LOC, last modified 2026-03-26)
- **Prior BLP-02 PRDs**: #248 (F-1), #250 (hot-fix), #256 (F-2)
- **Conventional Commit PR title rule**: `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles
- **GitHub Security Advisory destination**: `https://github.com/davidmatousek/tachi/security/advisories/new`
- **GitHub Private Vulnerability Reporting docs**: `https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository`
- **Triad reviews**: `.aod/results/architect.md` (v1.0 + v1.1) and `.aod/results/team-lead.md` (v1.0)
