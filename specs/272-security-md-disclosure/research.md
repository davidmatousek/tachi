# Research Summary: F-3 SECURITY.md and Private Disclosure Channel

**Feature**: F-3 — Issue #272 (BLP-02 Wave 3)
**PRD**: `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md`
**Created**: 2026-05-08
**Streams**: KB query, codebase scan, architecture/governance read, web research (parallel)

---

## Knowledge Base Findings

- **KB store empty** (0 thoughts). `docs/INSTITUTIONAL_KNOWLEDGE.md` has 3 BLP-02 entries:
  1. F-1 (#248) test-fixture baseline-drift pattern
  2. F-250 hot-fix mid-build CI scope-expansion governance
  3. F-2 (#256) CI workflow lock-step coupling
- **Applicability to F-3**: NONE. F-3 is docs-only (no code, no tests, no CI workflow coupling). Patterns above are code/test-coupling specific.
- **Lesson carried forward**: The F-1/F-250/F-2 narrative shows BLP-02 "single-maintainer same-day-or-next-day cadence" is empirically demonstrated (all three delivered within 24-48h envelopes). F-3's 3-4h active estimate is consistent.

---

## Codebase Analysis

### Current `SECURITY.md` (40 LOC, last modified 2026-03-26)
- **Heading**: `# Security Policy` (line 1)
- **Sections** (in order): `## Reporting a Vulnerability` (lines 3–21) → `## Scope` (23–32) → `## Supported Versions` (34–40)
- **Current SLA**: "Acknowledgment within 48 hours" (line 18)
- **Current Supported Versions table**: 2 rows (`Latest release | Yes`; `Older releases | Best effort`)
- **Missing vs GitHub-canonical 5-section target**: dedicated "What to expect" section (currently bundled inside Reporting), explicit "Out-of-scope" section (currently absent), version-line policy (currently absent), latest-tag worked example, *Report a vulnerability* button as primary instruction.

### Current `CHANGELOG.md`
- `## Unreleased` block (lines 10–72) uses `### Hardened config-file load (BLP-02 F-2)` style: feature-titled subsection with bolded labels (`**New library**:`, `**Refactored sites**:`).
- Recent released `v4.31.0` entries (lines 75–100) follow a more compact `### Features` / `### Bug Fixes` style.
- **F-3 insertion point**: top of `## Unreleased` block, new subsection `### SECURITY.md and private disclosure channel (BLP-02 F-3)` matching the F-2 style — bullets for SECURITY.md rewrite, README.md pointer, repo-setting toggle, TACHI-VULN-05abc41ad4cc closure, no ADR.

### Current `README.md`
- `## Community` section (lines 40–48) has an existing security bullet at **line 44**:
  > `- **Security vulnerabilities** → [private advisory](https://github.com/davidmatousek/tachi/security/advisories/new) (do not post publicly)`
- **AC-12 best-fit insertion** (Team-Lead A-5 advisory): extend the existing bullet or append a follow-on bullet referencing `[SECURITY.md](SECURITY.md)`. Option A (minimal-delta): extend the line. Option B (more discoverable): add a sibling bullet "Full security policy → [SECURITY.md](SECURITY.md)". **Recommended for spec: Option B** (matches PRD's "one-line pointer" framing — distinct line, not parenthetical).

### `.aod/results/security-scan.md` finding
- **TACHI-VULN-05abc41ad4cc** at lines 171–184. INFO severity (CVSS 0.0). OWASP A05 Security Misconfiguration. File reference `SECURITY.md:1`. The scan was timestamped 2026-05-02 (predates current SECURITY.md presence) — finding language flags posture-channel inadequacy, not file absence.

### Release-please state (AC-2 cross-check baseline)
- `.release-please-manifest.json` → `{".": "4.31.0"}`
- `git tag --list 'v*' | sort -V | tail -5` → `v4.28.0 / v4.29.0 / v4.30.0 / v4.31.0 / v4.32.0`
- **One-version manifest lag** (manifest=4.31.0, latest tag=v4.32.0). PRD captures this as AC-14 follow-up chore — not blocking F-3 because SECURITY.md text references the *latest released tag*, not the manifest. Re-cross-check at SECURITY.md write time per AC-2.

---

## Architecture & Governance Constraints

### Spec template structure (`.aod/templates/spec-template.md`)
- Mandatory section order: **User Scenarios & Testing → Requirements → Success Criteria**
- User stories require: Priority (P1/P2/P3), Why-this-priority, Independent-Test, Given/When/Then Acceptance Scenarios
- Functional Requirements MUST begin with **Given** and follow Given/When/Then structure; `[MANUAL-ONLY] <reason>` for non-automatable items
- Success Criteria MUST be measurable and technology-agnostic

### Plan template (looking ahead to `/aod.project-plan`)
- Sections: Summary → Technical Context → Constitution Check → Project Structure → Complexity Tracking
- **F-3 implication**: Technical Context will be minimal (no language/storage/testing details — docs only). Constitution Check passes (no new agents, no new contracts, no code paths). Complexity Tracking: empty.

### PR title rule (`.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles)
- F-3 PR title MUST be `feat(272): SECURITY.md and private disclosure channel` (per PRD line 193)
- Pre-merge: re-verify title via `gh pr edit` if necessary
- Post-merge: confirm release-please PR opens within ~30s; if empty, push `feat(272): … — release marker` empty commit
- F-212 incident reference (PR #213 squash-merged without `feat:` prefix → release-please silently skipped → recovered via marker commit) cited in delivery checklist

### Sign-off requirements (`.claude/rules/governance.md`)
- spec.md → PM (auto via `/aod.spec`)
- plan.md → PM + Architect (auto via `/aod.project-plan`)
- tasks.md → PM + Architect + Team-Lead (auto via `/aod.tasks`)

### tachi scope alignment (`.claude/rules/scope.md`)
- tachi IS: a threat-modeling and AI-reasoning vulnerability detection harness for Claude Code; logic-level scanner; instrumentation harness (not SaaS); Apache-2.0 OSS.
- tachi IS NOT: a SAST/SCA replacement; CI/CD tool; agent-agnostic (runs inside Claude Code); SaaS.
- **F-3 implication**: SECURITY.md "Scope" enumerations must reflect this positioning — in-scope = tachi codebase paths + scaffolds-as-shipped; out-of-scope = Claude Code itself (→ Anthropic), 3rd-party MCP servers, adopter personalization.

---

## Industry Research

### GitHub-canonical SECURITY.md
- **GitHub does NOT prescribe a canonical section ordering** — official docs only name two sections by example: **"Supported Versions"** and **"Reporting a Vulnerability"** (verbatim). Common community extensions add Scope, What to expect, Out-of-scope.
- **PRD's proposed 5-section order** (Supported Versions / Reporting / What to expect / Scope / Out-of-scope) is consistent with prevailing community practice, including Electron (GitHub's docs cite Electron as a reference example).
- **Recommendation for spec**: section names use GitHub-canonical wording verbatim ("Supported Versions", "Reporting a Vulnerability"); the additional sections (What to expect, Scope, Out-of-scope) are convention-aligned.

### Private Vulnerability Reporting toggle
- **Verified canonical path** (per GitHub Docs source `data/reusables/security-advisory/`): `Settings → Code security and analysis → Advanced Security subsection → Private vulnerability reporting`. The PRD's path "Settings → Security → Code security and analysis" is functionally equivalent — "Code security and analysis" is the page title; "Advanced Security" is the in-page subsection.
- **Researcher-side affordance**: Security tab → click **Report a vulnerability** button → fill form → click **Submit report**.

### Direct URL `/security/advisories/new`
- **NOT documented as canonical** — works empirically but GitHub Docs route reporters through the UI button, not the URL. Treat as a convenience shortcut.
- **Recommendation for SECURITY.md wording**: lead with the *Report a vulnerability* button on the Security tab; offer the URL as a "or navigate directly to …" fallback.

### Supported-versions policy precedent for high-cadence projects
- **Bun** is the strongest precedent for "latest-only with immediate deprecation": "Since Bun does not follow a structured release schedule like Node.js or Deno, current stable versions of Bun are supported and older versions may be dropped in minor releases without considering it a breaking change." This is exactly the posture PRD adopts.
- **OpenSSF Open Source Project Security Baseline** (2025-10-10) requires only that projects "provide a descriptive statement when releases or versions will no longer receive security updates" — no 90-day mandate. Tachi's latest-minor-only stance is Baseline-compliant.
- **Counterposes**: Node.js (30-month LTS), Deno (LTS channel) — opposite end of the spectrum, explicitly NOT what tachi is adopting.

### Response SLA conventions
- **OSSF Maintainer Guide**: "within 1-2 days" (acknowledgment).
- **CERT Guide to Coordinated Vulnerability Disclosure**: "24-48 hours is common for vendors and coordinators."
- **Procurement-questionnaire baseline** (CAIQ, SIG-Lite): typically accepts ≤ 5 business days for single-maintainer OSS.
- **Web-research recommendation was 48h**, but **PRD adopted 5 business days** (Issue #272 §Interface-Contract — a deliberate deviation from the 48h sweet-spot, chosen because the maintainer cannot honor 48h reliably across vacation/illness/weekend windows; over-promising on response SLA is itself a disclosure-channel anti-pattern). **Spec uses 5 business days per PRD**; the 48h alternative is documented here as a future-revision option, not a current recommendation to override PRD.

### Disclosure window
- Industry norm: **45-90 days**; Google's Project Zero standard is 90 days. Not currently in F-3 scope (PRD does not commit to a disclosure window beyond "fix or mitigation timeline communicated after assessment"); future revision could add a 90-day window if desired.

---

## Recommendations for Spec

1. **Adopt PRD acceptance criteria verbatim** as functional requirements (FR-001..FR-012 mapping to AC-1..AC-12). Mark AC-13 and AC-14 as out-of-scope follow-up Issues, not in spec FRs.
2. **Use exact GitHub-canonical section names** in SECURITY.md: "Supported Versions" and "Reporting a Vulnerability" verbatim; add "What to expect", "Scope", "Out-of-scope" as community-convention sections.
3. **Lead with *Report a vulnerability* button** in the Reporting section; offer `/security/advisories/new` as a fallback shortcut, not the primary instruction.
4. **Cite Bun precedent** if Architect challenges the latest-minor-only policy in plan.md review (already mitigated in PRD §R-4).
5. **README.md AC-12 insertion**: Option B (sibling bullet under `## Community` referencing SECURITY.md) — more discoverable than extending the existing line.
6. **Mark out-of-tree steps explicitly**: AC-6 (toggle enable), AC-7 (button visibility check), AC-11 (smoke-test URL load) are `[MANUAL-ONLY]` — they cannot be automated; verification evidence (screenshot or plain-text confirmation) lands in PR description.
7. **Edge cases worth documenting in spec**: toggle accidentally disabled later (R-2), researcher uses wrong URL despite SECURITY.md (R-3), latest-minor-only policy surprises adopters pinning to specific minors (R-4), GitHub-vendor-lock dependency (R-6).
8. **Defer to PRD on contested decisions**: 5-business-day SLA (vs 48h industry norm), latest-minor-only deprecation (vs 90-day rolling), GitHub Security Advisory as sole channel (vs SMTP/PGP/CNA alternatives) — these were all deliberately decided in PRD v1.0 → v1.1 review and are non-negotiable for spec.

---

## File Pointers Referenced

- `/Users/david/Projects/tachi/SECURITY.md` (40 LOC; rewrite target)
- `/Users/david/Projects/tachi/CHANGELOG.md:10` (`## Unreleased` insertion point)
- `/Users/david/Projects/tachi/README.md:40-48` (`## Community` section; line 44 existing security bullet)
- `/Users/david/Projects/tachi/.aod/results/security-scan.md:171-184` (TACHI-VULN-05abc41ad4cc finding)
- `/Users/david/Projects/tachi/.release-please-manifest.json` (manifest=4.31.0)
- `/Users/david/Projects/tachi/docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md` (PRD; 326 lines)
- `/Users/david/Projects/tachi/.aod/templates/spec-template.md` (spec template structure)
- `/Users/david/Projects/tachi/.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles (PR title + recovery flow)

---

## External References

- [Adding a security policy to your repository — GitHub Docs](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository)
- [Configuring private vulnerability reporting for a repository — GitHub Docs](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
- [Privately reporting a security vulnerability — GitHub Docs](https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
- [OSSF OSS Vulnerability Guide (maintainer guide)](https://github.com/ossf/oss-vulnerability-guide/blob/main/maintainer-guide.md)
- [Open Source Project Security Baseline (2025-10-10)](https://baseline.openssf.org/versions/2025-10-10.html)
- [Bun release-cadence support model — Strapi blog citation](https://strapi.io/blog/bun-vs-nodejs-performance-comparison-guide)
