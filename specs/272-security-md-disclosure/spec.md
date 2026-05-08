---
prd_reference: docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "Faithful to PRD v1.1. 12/12 mandatory ACs covered (14 FRs incl. FR-003 operational cross-check + FR-014 PR-title rule). 5/5 user stories with priority + independent test + Given/When/Then. 7/7 PRD goals mapped to SCs + SC-008 effort cap. 6/6 PRD risks as edge cases. AC-13 + AC-14 correctly deferred to post-merge follow-up Issues. 5-business-day SLA verbatim throughout (zero 48h/24h leakage). Three non-blocking observations for plan-stage author (README line-44 ref refresh, manifest-tag re-check timing, R-2 footer wording handoff) — none require spec revision. Full review: .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: F-3 — SECURITY.md and Private Disclosure Channel

**Feature Branch**: `272-security-md-disclosure`
**Created**: 2026-05-08
**Status**: Draft
**Input**: User description: "PRD: 272 - security-md-disclosure (source: docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md)"

**PRD Reference**: `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md`
**Initiative**: BLP-02 Wave 3 — disclosure-channel counterpart to F-1 (#248) and F-2 (#256) code fixes from the 2026-05-02 `/security` scan.
**Closes finding**: TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration; CVSS 0.0).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Security researcher with a documented private channel (Priority: P1)

A security researcher who finds a vulnerability in tachi can locate a clear, documented private disclosure channel by reading SECURITY.md at the repo root, and uses that channel to report responsibly without resorting to a public GitHub Issue or LinkedIn comment.

**Why this priority**: This is the core problem F-3 closes. The 2026-05-02 LinkedIn thread that triggered BLP-02 was itself an example of public disclosure that a properly configured SECURITY.md surface could have channeled into a private GitHub Security Advisory. Without SECURITY.md present in GitHub-canonical form, the researcher's default escalation is the public path that produced that thread.

**Independent Test**: Open `https://github.com/davidmatousek/tachi/blob/main/SECURITY.md`, scroll to the "Reporting a Vulnerability" section, follow the primary instruction (the *Report a vulnerability* button) or the fallback URL — confirm a private advisory form is reachable. Delivers value even before the toggle is enabled (URL fallback works; toggle adds the Security-tab button for discovery).

**Acceptance Scenarios**:

1. **Given** the repo root, **When** a researcher opens `SECURITY.md`, **Then** the "Reporting a Vulnerability" section presents the *Report a vulnerability* button on the Security tab as the primary instruction, with a fallback direct URL `https://github.com/davidmatousek/tachi/security/advisories/new`, and an explicit "do not open a public Issue" prohibition.
2. **Given** the SECURITY.md "What to include" subsection, **When** a researcher prepares a report, **Then** they see prompts for: description, steps to reproduce, affected components, potential impact.
3. **Given** the SECURITY.md "What to expect" subsection, **When** a researcher submits a report, **Then** they see the 5-business-day acknowledgment SLA, assessment-within-1-week commitment, and fix-timeline-communicated-after-assessment commitment.

---

### User Story 2 — Future external reviewer with a private path visible from the Security tab (Priority: P1)

A future Daniel Wood (community member who spots a security concern during their own review of tachi) lands on the repo's Security tab, sees a *Report a vulnerability* button as a primary affordance, and uses it before falling back to a public LinkedIn comment.

**Why this priority**: Closes the LinkedIn-fallback-pattern that produced the 2026-05-02 thread. The Security tab is the first place a researcher looks for disclosure path; the button makes the channel discoverable without requiring the researcher to read SECURITY.md first.

**Independent Test**: Visit `https://github.com/davidmatousek/tachi/security` in a logged-in browser session — confirm the *Report a vulnerability* button is rendered as a primary call-to-action above any advisory list. This story is fully delivered by enabling the GitHub repo's Private Vulnerability Reporting toggle, independent of SECURITY.md content.

**Acceptance Scenarios**:

1. **Given** the GitHub repo settings have the **Private vulnerability reporting** toggle enabled, **When** any visitor (authenticated) navigates to `https://github.com/davidmatousek/tachi/security`, **Then** the **Report a vulnerability** button is visible on the page.
2. **Given** an authenticated reviewer with no prior knowledge of tachi's disclosure channel, **When** they look for "how to report a vulnerability", **Then** the Security-tab button is the first discoverable affordance — no LinkedIn / DM / email fallback is required.

---

### User Story 3 — Adopter with a supported-versions contract (Priority: P2)

A tachi adopter consuming releases via `make update` reads the SECURITY.md "Supported Versions" section and learns which versions of tachi receive security updates, so they can decide whether to upgrade based on a documented version-line policy rather than guessing.

**Why this priority**: Procurement-defensible and adopter-trust-building, but secondary to the core disclosure-channel surface. An adopter without supported-versions clarity still has the disclosure path open via US-1; the supported-versions contract is auxiliary peace-of-mind.

**Independent Test**: Open SECURITY.md, scroll to "Supported Versions" — confirm a version-line policy is stated (latest-minor-only of v4.x; immediate deprecation on next minor) with a worked example referencing the current latest tag and a recommendation to pin to the major line for `make update` adopters.

**Acceptance Scenarios**:

1. **Given** the SECURITY.md "Supported Versions" section, **When** an adopter reads it, **Then** the policy is stated as: "only the latest minor of v4.x receives security updates; older minors are deprecated immediately on the next minor release."
2. **Given** the same section, **When** the adopter reads further, **Then** a worked example references the latest released tag (verified at write-time against `git tag --list 'v*' | sort -V | tail -1`).
3. **Given** the same section, **When** an adopter consuming via `make update` reads it, **Then** they see an explicit recommendation to pin to the major line (`v4.x`) rather than a specific minor.

---

### User Story 4 — Maintainer with a structured intake (Priority: P2)

A maintainer (single-maintainer project: davidmatousek) receives a private vulnerability report via the GitHub Private Vulnerability Reporting flow rather than DM / email / LinkedIn, so the report lands in a structured intake (the repo's Security tab) with a defined SLA the maintainer can honor.

**Why this priority**: Operational quality of received reports. Without the toggle, the maintainer still receives reports (via the URL fallback if SECURITY.md is in place), but discoverability is degraded and the intake is less structured.

**Independent Test**: With the toggle enabled, ask a trusted second account to submit a low-severity test advisory via the *Report a vulnerability* button — confirm the advisory appears on the maintainer's repo Security tab with notification. (Test is non-destructive; the test advisory can be closed without action.)

**Acceptance Scenarios**:

1. **Given** the Private Vulnerability Reporting toggle is enabled, **When** a researcher submits an advisory, **Then** the advisory lands on the repo's Security tab and the maintainer receives a notification.
2. **Given** the SECURITY.md "What to expect" subsection, **When** the maintainer triages a report, **Then** the contractual SLA (5 business days to acknowledge) is honorable within single-maintainer working cadence — no on-call rotation required.

---

### User Story 5 — Enterprise procurement reviewer with no red flag (Priority: P3)

An enterprise security architect doing a pre-sales review of tachi reads the repo-root SECURITY.md and finds a procurement-questionnaire-baseline match: vendor disclosure policy, supported versions, response SLA, scope. The reviewer marks the "vendor disclosure policy" and "supported versions" line items GREEN rather than YELLOW.

**Why this priority**: Derivative — satisfied automatically by US-1, US-2, US-3, US-4 together. Listed for traceability to the procurement-reviewer persona that motivates the BLP-02 enterprise-hardening initiative.

**Independent Test**: Apply a representative procurement-questionnaire (e.g., CAIQ, SIG-Lite) "vendor disclosure policy" + "supported versions" rubric to SECURITY.md — confirm both line items pass.

**Acceptance Scenarios**:

1. **Given** SECURITY.md at repo root, **When** a procurement reviewer applies a CAIQ-style "vendor disclosure policy" rubric, **Then** the disclosure channel, response SLA, and scope sections are present and concrete.
2. **Given** SECURITY.md at repo root, **When** the reviewer applies a "supported versions" rubric, **Then** a documented version-line policy is present with a worked example.

---

### Edge Cases

- **Toggle silently disabled later** (PRD R-2): A future maintainer or contributor with repo-admin access could accidentally toggle Private Vulnerability Reporting OFF in `Settings → Code security and analysis`. Mitigation in spec scope: SECURITY.md "Reporting" section footer notes the dependency. Out of spec scope (deferred to AC-13 follow-up Issue): periodic posture probe scraping `https://api.github.com/repos/davidmatousek/tachi` and asserting `security_and_analysis.private_vulnerability_reporting.status == "enabled"`.
- **Researcher uses wrong URL despite SECURITY.md** (PRD R-3): A researcher reads SECURITY.md but still defaults to LinkedIn / DM / email. Mitigation: GitHub auto-renders the *Report a vulnerability* button on the Security tab once the toggle is enabled — UI affordance is more discoverable than reading the file.
- **Adopter on pinned minor surprised by latest-minor-only policy** (PRD R-4): An adopter pinning to `v4.31.x` discovers v4.32.0 release deprecates their pinned line. Mitigation: SECURITY.md worked example explicitly states this, recommends pinning to the major line (`v4.x`) for `make update` adopters.
- **GitHub deprecates Private Vulnerability Reporting** (PRD R-6): Tachi's documented channel depends on GitHub continuing to offer the feature and the URL pattern. Mitigation: SECURITY.md is a single-file, trivially-updatable artifact — recovery from a hypothetical GitHub-side change is a one-PR delta.
- **Procurement reviewer requires stricter 24-hour SLA** (PRD R-5): Some questionnaires require 24h critical-vulnerability acknowledgment, stricter than the 5-business-day baseline. Mitigation: SECURITY.md does not preclude faster cadence on critical reports — maintainer can voluntarily honor faster cadence without contractually binding to it.
- **`.release-please-manifest.json` lags the latest tag** (PRD AC-14, observed at PRD draft 2026-05-08): manifest=4.31.0 vs latest tag v4.32.0. SECURITY.md text references the latest *tag*, not the manifest, so the lag does not block F-3. Operational note: re-cross-check the manifest-vs-tag state at SECURITY.md write time per FR-003; if the discrepancy persists, queue as a separate chore Issue without blocking F-3.

---

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each FR begins with **Given** and follows Given/When/Then structure. `[MANUAL-ONLY] <reason>` marks FRs that cannot be automated.

#### Documentation surface

- **FR-001** (covers AC-1): **Given** the repo root, **When** a reader opens `SECURITY.md`, **Then** the file MUST present these five top-level sections in order: **Supported Versions**, **Reporting a Vulnerability**, **What to expect**, **Scope**, **Out-of-scope**. **And** section names MUST use GitHub-canonical wording verbatim where GitHub Docs prescribes a name (Supported Versions, Reporting a Vulnerability).

- **FR-002** (covers AC-2): **Given** the SECURITY.md "Supported Versions" section, **Then** the policy MUST state: *"only the latest minor of v4.x receives security updates; older minors are deprecated immediately on the next minor release."* **And** a worked example MUST reference the latest released tag (verified at write-time). **And** the section MUST recommend pinning to the major line (`v4.x`) for adopters consuming via `make update`.

- **FR-003** (operationalizes AC-2): **Given** the SECURITY.md write step, **Before** the file is committed, the maintainer MUST run the operational cross-check: `cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3`. **Then** SECURITY.md text MUST reference the latest *tag* (not the manifest). **And** any manifest-vs-tag discrepancy MUST be captured as a side observation in the PR description and queued as a separate chore Issue per AC-14, without blocking F-3.

- **FR-004** (covers AC-3): **Given** the SECURITY.md "Reporting a Vulnerability" section, **When** a researcher reads it, **Then** the primary instruction MUST direct them to the **Report a vulnerability** button on the Security tab. **And** a fallback direct URL `https://github.com/davidmatousek/tachi/security/advisories/new` MUST be present. **And** an explicit "do not open a public Issue" prohibition MUST be stated. **And** a "What to include" subsection MUST list: description, steps to reproduce, affected components, potential impact.

- **FR-005** (covers AC-4): **Given** the SECURITY.md "What to expect" section, **Then** the acknowledgment SLA MUST be stated as **"5 business days to acknowledge"**. **And** the assessment-within-1-week commitment MUST be retained. **And** the fix-timeline-communicated-after-assessment commitment MUST be retained. **And** the credit clause (researcher named in fix commit + release notes by default; anonymity available on request) MUST be retained.

- **FR-006** (covers AC-5, in-scope half): **Given** the SECURITY.md "Scope" section, **Then** in-scope surfaces MUST be enumerated explicitly: tachi codebase paths (`.aod/scripts/bash/`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/`, `stacks/`), stack-pack scaffolds **as shipped** (`stacks/*/scaffold/`), schema definitions (`contracts/`, `schemas/`), template content, tachi-shipped configuration files.

- **FR-007** (covers AC-5, out-of-scope half): **Given** the SECURITY.md "Out-of-scope" section, **Then** out-of-scope routing MUST be enumerated: Claude Code itself → Anthropic; third-party MCP servers → their maintainers; adopter personalization data (`.aod/personalization.env`, `brands/*/`) → adopter; adopter-modified scaffold output (post-`make scaffold` customizations) → adopter; threat-model accuracy concerns (false positives, missed threats) → regular Issues, not security advisories.

- **FR-008** (covers AC-12): **Given** the repo-root `README.md`, **When** a reader scans visible top-level sections, **Then** a discoverable one-line reference to `[SECURITY.md](SECURITY.md)` MUST be present. **And** the insertion MUST integrate with the existing `## Community` section (line 44 currently contains a security-vulnerabilities bullet pointing directly at the GitHub private advisory URL — the one-line reference adds discoverability of the local SECURITY.md content).

- **FR-009** (covers AC-8): **Given** the repo-root `CHANGELOG.md`, **When** the reviewer reads the `## Unreleased` block, **Then** a new feature subsection MUST be present referencing: SECURITY.md restructure to GitHub-canonical sections, Private Vulnerability Reporting toggle enable, and TACHI-VULN-05abc41ad4cc closure. **And** the entry style MUST match the F-2 precedent (subsection header `### SECURITY.md and private disclosure channel (BLP-02 F-3)`, bullet-point body).

#### Repo-settings surface

- **FR-010** (covers AC-6): **Given** the GitHub repo settings, **When** the maintainer navigates to `Settings → Code security and analysis → Advanced Security`, **Then** the **Private vulnerability reporting** toggle MUST be set to ON. **And** verification evidence (screenshot or plain-text confirmation that the toggle is ON) MUST be attached to the delivery PR description. *[MANUAL-ONLY] GitHub repo-settings UI is not script-accessible from F-3's tooling; toggle change must be performed in-browser by an account with repo-admin rights.*

- **FR-011** (covers AC-7): **Given** FR-010 is satisfied (toggle is ON), **When** any authenticated visitor opens `https://github.com/davidmatousek/tachi/security`, **Then** the **Report a vulnerability** button MUST be visible on the page. *[MANUAL-ONLY] UI inspection — no programmatic check in F-3 scope; deferred posture probe captured as AC-13 follow-up Issue.*

#### Verification surface

- **FR-012** (covers AC-11): **Given** an authenticated GitHub session, **When** the maintainer opens `https://github.com/davidmatousek/tachi/security/advisories/new`, **Then** the advisory submission form MUST load successfully (no 404, no permission error). **And** the form MUST NOT be submitted (smoke-test only). *[MANUAL-ONLY] Authenticated-UI smoke-test — no automation in F-3 scope.*

- **FR-013** (covers AC-9 + AC-10): **Given** the post-merge `/security` re-scan, **Then** TACHI-VULN-05abc41ad4cc MUST be recorded as REMEDIATED in `.aod/results/security-scan.md`. **And** no new HIGH or MEDIUM findings MUST be introduced. **And** LOW or INFO side-effect findings MAY appear if they document a separate concern.

#### Conventional Commit + release-please surface

- **FR-014** (covers PRD §Release-Please-Trigger-Posture): **Given** the F-3 PR, **When** the maintainer opens or edits the PR title, **Then** the title MUST be `feat(272): SECURITY.md and private disclosure channel`. **And** post-merge, the maintainer MUST verify a release-please PR opens within ~30s via `gh pr list --state open --search "release-please" --limit 3`. **And** if no release-please PR opens, the maintainer MUST push an empty release-marker commit per the F-212 incident recovery flow documented in `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles.

#### Out of F-3 scope (committed as post-merge follow-up Issues)

- **AC-13 / posture probe**: Periodic check that `security_and_analysis.private_vulnerability_reporting.status == "enabled"` against `https://api.github.com/repos/davidmatousek/tachi`. Logged at `/aod.deliver` time as a low-priority backlog Issue. NOT a F-3 functional requirement.
- **AC-14 / manifest-vs-tag chore**: Investigate the v4.32.0-tag / 4.31.0-manifest discrepancy observed at PRD draft. Logged at `/aod.deliver` time as a chore Issue. NOT a F-3 functional requirement.

### Key Entities *(include if feature involves data)*

- **`SECURITY.md`**: Repo-root markdown file (~80 LOC after rewrite). Sections: Supported Versions, Reporting a Vulnerability, What to expect, Scope, Out-of-scope. Replaces the existing 40-LOC file from 2026-03-26.
- **`CHANGELOG.md` `## Unreleased` block**: Contains the new feature-subsection entry for F-3.
- **`README.md` `## Community` section**: Receives the AC-12 one-line pointer.
- **GitHub Private Vulnerability Reporting toggle**: Repo-setting state (boolean: ON/OFF). Lives in GitHub UI, not in the repo. Cross-referenced from SECURITY.md "Reporting" footer.
- **TACHI-VULN-05abc41ad4cc**: The /security finding F-3 closes. INFO severity, OWASP A05 Security Misconfiguration, file reference `SECURITY.md:1`. Tracked in `.aod/results/security-scan.md` lines 171–184.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (PRD G1): Post-merge `/security` re-scan records TACHI-VULN-05abc41ad4cc as REMEDIATED. Verified by reading `.aod/results/security-scan.md` after re-scan.
- **SC-002** (PRD G2): GitHub *Report a vulnerability* button is visible on the repo's Security tab. Verified by manual UI inspection at `https://github.com/davidmatousek/tachi/security`.
- **SC-003** (PRD G3): SECURITY.md sections match the GitHub-canonical 5-section structure. Verified by reviewer diff inspection of the merged file.
- **SC-004** (PRD G4): Supported-versions policy is verifiable against the latest released tag at merge time. Verified by re-running the operational cross-check command (FR-003) at merge time and inspecting the SECURITY.md text.
- **SC-005** (PRD G5): tachi-specific scope routes likely-misdirected reports to the correct destination. Verified by reviewer scope-language review (in-scope surfaces enumerated; out-of-scope routing to Anthropic / third-party MCP / adopter / regular Issues stated).
- **SC-006** (PRD G6): 5-business-day acknowledgment SLA is documented and is honorable within single-maintainer working cadence. Verified by PM sign-off (single-maintainer reality) and by SECURITY.md "What to expect" section content review.
- **SC-007** (PRD G7): BLP-02 Wave 3 closed. Verified by:
  - Initiative Tracker memory entry update (BLP-02 Wave 3 → DELIVERED) at /aod.deliver time.
  - Post-merge `/security` re-scan showing TACHI-VULN-05abc41ad4cc cleared (also covers SC-001).
  - PRD INDEX.md status flip Approved → Delivered with PR link.
- **SC-008** (operational, derived from PRD §Estimate-and-Timeline): Total active maintainer time ≤ 4 hours; wall-clock delivery ≤ next-day cap (consistent with F-1 / F-2 BLP-02 cadence). Verified at /aod.deliver time by retrospective time-tracking.

---

## Assumptions

- **Maintainer holds GitHub repo-admin rights** for `davidmatousek/tachi` — required for FR-010 toggle change. PRD §Loosely-Coupled-Dependencies confirms this.
- **`.aod/personalization.env`** is the canonical adopter-personalization file; if a future migration moves it, FR-007's out-of-scope enumeration must be updated. Outside F-3 scope.
- **GitHub's URL pattern `https://github.com/{owner}/{repo}/security/advisories/new`** remains stable through the F-3 delivery window. Treated as low-vendor-risk per PRD §R-6.
- **Release-please pipeline is operational** at PRD draft (latest successful release: v4.31.0 / F-2 PR #257 / 2026-05-05). PRD §Loosely-Coupled-Dependencies confirms.
- **The 5-business-day SLA** is a maintainer-facing contract, not an organizational SLA. PM sign-off in PRD v1.1 explicitly endorses this as honorable for single-maintainer cadence.
- **No `finding.yaml` / taxonomy schema change** is required (PRD §Non-Goals NG3). Tenth feature in a row preserving BLP-01 detection-tier contract continuity.
- **No agent / command / skill / script code change** is required (PRD §Non-Goals NG4). Pure documentation + repo-setting toggle.
