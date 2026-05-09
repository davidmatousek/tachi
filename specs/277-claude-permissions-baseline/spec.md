---
prd_reference: docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "Faithful to PRD v1.1 + research.md cited corrections. 14/14 ACs → FR-001..FR-014 (AC-14 README pointer non-blocking obs). 5/5 user stories map to PRD's 5 user surfaces P1/P1/P2/P2/P3. 9 PRD goals → SC-001..SC-008. Two corrections (FR-012 cross-file deny per code.claude.com/docs/en/settings; FR-007 subdomain non-collapse per Issues #15260/#11972/#1217) honor architect-approved v1.1 cascade — doc-fidelity fixes not scope creep. Out-of-scope correctly deferred. Three non-blocking observations for plan-stage author. Full review: .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: F-4 — Claude Permissions Baseline

**Feature Branch**: `277-claude-permissions-baseline`
**Created**: 2026-05-08
**Status**: Draft
**Input**: User description: "PRD: 277 - claude-permissions-baseline (source: docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md)"

**PRD Reference**: `docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md`
**Initiative**: BLP-02 Wave 4 — fourth feature in the 5-feature enterprise hardening initiative; same 2026-05-02 Daniel Wood LinkedIn-thread trigger as F-3 (#272). Closes the *deployment-readiness* half of the thread (F-3 closed the *disclosure-channel* half).
**Closes**: No `/security` finding directly; closes a posture-gap (no documented permissions baseline + permissive default ruleset) called out in BLP-02 enterprise-hardening initiative scope and Daniel Wood's published recommendation.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Enterprise developer adopting tachi in a managed environment (Priority: P1)

An enterprise developer in a SecOps-reviewed managed environment runs `make update` (or freshly clones tachi for the first time) and inherits `.claude/settings.json` as a default-deny baseline they can ship as-is, with `docs/standards/CLAUDE_PERMISSIONS.md` providing per-rule rationale that satisfies their organization's audit-policy requirement for inherited AI-agent permission sets.

**Why this priority**: This is the core gap F-4 closes. The 2026-05-02 Daniel Wood thread named "hardened Claude permissions profile" as a load-bearing prerequisite for enterprise developer environments. Without F-4, an enterprise developer either fails their SecOps review (inheriting tachi's permissive default) or pays the design cost themselves. F-4 ships the baseline so they can pass review on first contact.

**Independent Test**: Clone tachi into a fresh sandbox; open `.claude/settings.json` and `docs/standards/CLAUDE_PERMISSIONS.md` side-by-side; verify every rule in `settings.json` has a matching row (or row group) in CLAUDE_PERMISSIONS.md describing rule + category + rationale + failure mode. The test passes regardless of whether the developer ships tachi to production — the artifacts ARE the deliverable.

**Acceptance Scenarios**:

1. **Given** a fresh clone of tachi at the F-4 merge SHA, **When** the developer opens `.claude/settings.json`, **Then** the file MUST be valid strict-JSON (parseable by `jq empty`) with `permissions.allow`, `permissions.deny`, and `permissions.ask` arrays present (any of which MAY be empty), AND every rule MUST be a string pattern (no comments, no JSONC).
2. **Given** the same fresh clone, **When** the developer opens `docs/standards/CLAUDE_PERMISSIONS.md`, **Then** the file MUST contain a rule-by-rule table where every non-built-in rule from `.claude/settings.json` appears at least once with columns: Rule, Category (1–4), Rationale, Failure mode.
3. **Given** the cross-check between `settings.json` and `CLAUDE_PERMISSIONS.md`, **When** the AC-2 cross-check script (defined in plan.md and run as a task) is executed, **Then** the script MUST report ZERO orphaned rules (rules in `settings.json` not documented in CLAUDE_PERMISSIONS.md) and ZERO orphaned table rows (rows referencing rules not in `settings.json`).

---

### User Story 2 — Security-conscious solo developer with defense-in-depth (Priority: P1)

A solo developer running tachi commands (e.g., `/aod.build`, `/tachi.threat-model`) inside a fresh repo gets a defense-in-depth gate against accidental destructive operations: a typo'd `git push --force origin main` (whether typed by the developer or proposed by an LLM-driven session) is blocked at the permission layer with an explicit deny prompt, not auto-approved alongside the regular `git push`.

**Why this priority**: This is the safety-net story. Without F-4, the current 26-rule allow-only file silently approves `git push:*` matching `git push --force origin main`; the developer's only line of defense is the user-prompt that Claude Code shows for not-in-allow operations, which a fatigued user can click through. F-4 makes the force-push case an explicit deny, with a corresponding row in CLAUDE_PERMISSIONS.md explaining why and how to override (Path 1 disable / Path 2 fork / Path 3 explicit edit per ADR-041 §Opt-Out-Paths). Tied for P1 with US-1 because the safety net is the consumer-side counterpart to enterprise-side audit-readiness — both close the BLP-02 enterprise-hardening gap from different angles.

**Independent Test**: With the F-4 baseline loaded, run a dry-run of `git push --force origin <test-branch>` through Claude Code in agentic mode; confirm Claude Code surfaces a deny prompt (not an auto-approve, not a regular ask). Independent of US-1's documentation surface — the developer benefits from the deny rule even without reading CLAUDE_PERMISSIONS.md.

**Acceptance Scenarios**:

1. **Given** the F-4 baseline is loaded, **When** Claude Code attempts `Bash(git push --force origin <branch>)` (or alias `git push -f`), **Then** the operation MUST match a `deny` rule and present a deny prompt to the user (not auto-approve via the broader `Bash(git push:*)` allow rule).
2. **Given** the F-4 baseline is loaded, **When** Claude Code attempts `Bash(rm -rf <path>)`, `Bash(git reset --hard:*)`, `Bash(gh release delete:*)`, `Bash(gh repo delete:*)`, `Bash(npm publish:*)`, or any other Tier-3a deny rule, **Then** the operation MUST present a deny prompt.
3. **Given** the F-4 baseline is loaded, **When** Claude Code attempts a Tier-3b `ask` rule (`Bash(git push --force-with-lease:*)`, `Bash(gh release create:*)`, `Bash(brew install:*)`, etc.), **Then** the operation MUST present an ask prompt distinct from a deny prompt and distinct from auto-approve.

---

### User Story 3 — Existing adopter with `.claude/settings.local.json` customizations (Priority: P2)

An adopter who has previously created `.claude/settings.local.json` with their own personal allow/deny rules pulls the F-4 baseline via `git pull` (or `make update`) and finds their customizations still working: their personal allows continue to auto-approve, and their personal denies continue to deny — without manual reconciliation steps.

**Why this priority**: Adopter-trust + Constitution Principle III backward-compatibility. Without confidence that customizations survive, adopters either avoid pulling F-4 (reducing the safety-net coverage) or hand-merge `settings.json` files (reducing the baseline's audit-readiness because now the file diverges per-adopter). Constitution Principle III makes this a non-negotiable expectation. P2 because the *mechanical* survival is guaranteed by Claude Code's native `settings.local.json` precedence — F-4's contribution is the *documented* contract that survives the upgrade, plus a cross-file deny-precedence clarification (per industry research, Path 2 fork-and-edit is required for adopters wishing to permit a baseline-denied operation; `settings.local.json` cannot override a project `settings.json` deny).

**Independent Test**: Create a fixture `.claude/settings.local.json` with one allow (`Bash(custom-tool:*)`) and one deny (`Bash(forbidden-tool:*)`) BEFORE pulling F-4; pull F-4 (`git pull && git checkout main`); re-run a representative tachi command that does not invoke either rule; confirm the file is unchanged and the rules still resolve as expected. Test the cross-file deny case separately: with F-4 loaded, attempt `Bash(rm -rf <path>)` — confirm the project deny holds even if `.claude/settings.local.json` has `Bash(rm -rf:*)` in `allow`.

**Acceptance Scenarios**:

1. **Given** an adopter has `.claude/settings.local.json` with personal allows/denies BEFORE F-4 lands on main, **When** they `git pull` the F-4 baseline, **Then** their `.claude/settings.local.json` MUST be unchanged (it is not under version control; F-4 only touches `.claude/settings.json`).
2. **Given** the F-4 baseline is loaded AND the adopter's `.claude/settings.local.json` contains an allow rule for a tool not covered by F-4 (e.g., a custom-internal-tool path), **When** Claude Code invokes that tool, **Then** the local allow rule MUST take precedence (auto-approve), confirming `settings.local.json` precedence for permissive overrides of operations not denied at the project level.
3. **Given** the F-4 baseline is loaded AND the adopter's `.claude/settings.local.json` contains an allow rule that conflicts with a project-level F-4 deny (e.g., local `Bash(git push --force:*)` in `allow` vs. project `Bash(git push --force:*)` in `deny`), **When** Claude Code invokes that operation, **Then** the project-level deny MUST hold (cross-file deny precedence — verified by AC-12 cross-file smoke test); AND CLAUDE_PERMISSIONS.md §Settings-Precedence MUST document this mechanic with a worked example so adopters understand the override path is fork-and-edit (or removal of the rule from project `settings.json`), not local-file allow.

---

### User Story 4 — SecOps reviewer auditing AI-agent permissions (Priority: P2)

A SecOps reviewer auditing tachi's AI-agent permission posture (in support of an organization's broader AI-tool risk review or pre-adoption questionnaire) reads `docs/standards/CLAUDE_PERMISSIONS.md`, finds a per-rule rationale catalog with audit-policy framing, and produces an audit report for their organization without reverse-engineering the maintainer's intent.

**Why this priority**: Procurement-defensible posture for the BLP-02 enterprise-hardening rubric. Without CLAUDE_PERMISSIONS.md, the reviewer must reverse-engineer 80+ rules to answer "why is X auto-approved while Y requires confirmation"; with it, they get the answer in one cell of a table. P2 because the audit happens after adoption, not at first contact — but procurement-defensible audit posture is a buying-decision input for enterprise adopters. Story is fully delivered by US-1's documentation surface plus the explicit policy-decision-log structure of CLAUDE_PERMISSIONS.md (which goes beyond the per-rule rationale table and includes governance framing: why this baseline exists, how it's maintained, opt-out paths, known limitations).

**Independent Test**: Apply a representative AI-agent permission audit rubric (e.g., NIST AI RMF GV.RR.RX-01-aligned policy log requirements; CSA AICM Pre-Procurement-Questionnaire item "Vendor publishes audit-ready agent permissions baseline") to CLAUDE_PERMISSIONS.md — confirm the document satisfies the rubric: rules categorized, rationales present, governance framing present, opt-out paths documented, known limitations enumerated.

**Acceptance Scenarios**:

1. **Given** `docs/standards/CLAUDE_PERMISSIONS.md`, **When** the SecOps reviewer reads it, **Then** the document MUST include sections for: framing paragraph (why this baseline exists), four-category description (read-only / local-state / destructive / network), settings precedence (within-file deny→ask→allow + cross-file project-deny holds), per-rule rationale table, opt-out paths (3 paths documented), known limitations (Bash pattern fragility / process-wrapper bypass / read-only built-in shadow / subdomain matching unsupported per upstream issues).
2. **Given** the same document, **When** the SecOps reviewer asks "why is `Bash(ls:*)` not in the `allow` list?", **Then** the §Built-in-Read-Only-Set section MUST provide the answer: Claude Code's built-in read-only set runs without prompt in every mode, so explicit allow is no-op; the section MUST list which commands fall into the built-in set.
3. **Given** the same document, **When** the SecOps reviewer asks "what overrides this baseline?", **Then** the §Opt-Out-Paths section MUST describe three paths: (1) per-tool disable via Claude Code CLI flag where applicable, (2) fork-and-edit `.claude/settings.json` (the load-bearing path for adopters wishing to permit a baseline-denied operation, given cross-file deny precedence), (3) `.claude/settings.local.json` for *adding* personal allows for operations not denied at the project level.

---

### User Story 5 — Future external reviewer with no permissions red flag (Priority: P3)

A future "Daniel Wood" persona (community member spotting posture concerns during their own review of tachi) lands on tachi's `.claude/` surface, sees a documented permissions baseline + ADR-041 + CLAUDE_PERMISSIONS.md, and marks the "AI-agent permissions posture" line item GREEN rather than YELLOW in their published review.

**Why this priority**: Derivative — satisfied automatically by US-1, US-2, US-3, US-4 together. Listed for traceability to the external-reviewer persona that motivates the BLP-02 enterprise-hardening initiative. The 2026-05-02 Daniel Wood thread is the proof-of-concept review that produced this category of feedback; F-4 closes the half of the thread F-3 did not.

**Independent Test**: Apply a representative external-review rubric (e.g., the Daniel-Wood-style enterprise-readiness checklist published 2026-05-02) to tachi's permissions surface — confirm `.claude/settings.json` is categorized + documented, CLAUDE_PERMISSIONS.md is present, ADR-041 is accepted.

**Acceptance Scenarios**:

1. **Given** tachi's repo at the F-4 merge SHA, **When** an external reviewer applies the "AI-agent permissions baseline" rubric, **Then** the rubric MUST find: (a) `.claude/settings.json` with non-empty `deny` list, (b) `docs/standards/CLAUDE_PERMISSIONS.md` documenting rules + opt-outs, (c) `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` accepted with ≥6 alternatives-considered.
2. **Given** the same review, **When** the reviewer applies a "documented adopter customization path" rubric, **Then** they MUST find an opt-out path in CLAUDE_PERMISSIONS.md §Opt-Out-Paths (the cross-file deny-precedence clarification per US-3 AC-3 closes the question of *how* an adopter overrides a baseline deny).

---

### Edge Cases

- **Cross-list precedence misuse** (PRD R-3 reframed): An adopter or future maintainer assumes that adding `Bash(git push --force:*)` to `permissions.allow` would override the same pattern in `permissions.deny` (intra-file). Mitigation: CLAUDE_PERMISSIONS.md §Settings-Precedence documents the within-file rule explicitly: `deny → ask → allow`, first match wins, deny always takes precedence. Worked example uses the `Bash(git push:*)` allow + `Bash(git push --force:*)` deny case to walk a SecOps reviewer through the cross-list resolution.
- **Cross-file precedence misuse** (new from web research): An adopter assumes that adding `Bash(git push --force:*)` to `.claude/settings.local.json` `allow` would override the project-level `.claude/settings.json` `deny`. Per Claude Code documentation (`code.claude.com/docs/en/settings`), denylist always takes precedence over allowlist *across files*; project deny holds even if user-settings or settings.local.json have a competing allow. Mitigation: CLAUDE_PERMISSIONS.md §Settings-Precedence includes a *second* worked example documenting cross-file deny precedence and pointing adopters to Path 2 (fork-and-edit) for legitimate baseline-deny overrides. AC-12 verifies this cross-file model with a deliberate smoke-test.
- **Bash pattern fragility** (PRD R-8): `deny` rules pattern-match on the literal command-line string. `Bash(rm -rf:*)` does not match `bash -c 'rm -rf /tmp/x'` because the `bash -c` wrapper changes the matched string. Mitigation: CLAUDE_PERMISSIONS.md §Known-Limitations documents this explicitly. Defense-in-depth posture: deny rules are **calibrated against casual-typo case**, not adversarial-bypass case. Adversarial bypass surface is a separate threat model out of F-4 scope.
- **Process-wrapper bypass** (PRD R-9): `npx`, `docker exec`, `devbox run`, `mise exec`, and similar wrappers re-shell-out commands; `Bash(rm -rf:*)` deny does not match `npx <package-that-runs-rm-rf>`. Mitigation: documented as known limitation in CLAUDE_PERMISSIONS.md §Known-Limitations; same calibration as R-8 (casual-typo not adversarial).
- **Read-only built-in shadow** (PRD R-10): A future Claude Code update may ship a built-in command (e.g., `Bash(grep:*)`) that shadows an explicit allow rule. The allow rule becomes no-op silently. Mitigation: AC-2 cross-check script verifies every non-built-in rule has a CLAUDE_PERMISSIONS.md row; CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set documents the current built-in set with a "verify against latest Claude Code release" maintenance note.
- **JSON validity regression on edit** (PRD R-1 reframed via Team-Lead A-4): A future PR editing `.claude/settings.json` introduces a syntax error (trailing comma, unclosed bracket) that breaks Claude Code's settings load. Mitigation: AC-6 sub-check runs `jq empty .claude/settings.json` as part of the verification recipe in plan.md. CI integration is out of scope for F-4 (tracked as backlog Issue at /aod.deliver time per F-3 deferred-AC pattern).
- **Auto-approve regression on `git status`** (PRD R-1 + Team-Lead A-4): A baseline that incorrectly forces a prompt on every `git status` (built-in read-only command) would be a usability regression. Mitigation: AC-6 sub-check verifies that `git status` continues to auto-approve (built-in read-only set) and that `rm -rf <path>` continues to surface a deny prompt — the two probes calibrate the baseline against the prompt-flood vs deny-fail axes simultaneously.
- **AC-7 subdomain-matching outcome** (predictable per industry research): Claude Code Issues #15260, #11972, #1217, #27139 confirm `WebFetch(domain:github.com)` does NOT match `api.github.com` and `WebFetch(domain:*)` wildcard does NOT work as expected. Mitigation: the 19 explicit per-subdomain rules in Category 4 are the correct posture; AC-7 retained as adversarial verification (defends against future Claude Code semantics changes), but the expected outcome is documented as "no collapse — explicit per-subdomain required" with citations.
- **Built-in `gh` shadow** (PRD R-10 derivative): If Claude Code adds `gh` (or any subcommand thereof) to its built-in read-only set in a future release, the Category 1 `Bash(gh issue view:*)` and similar rules become no-op silently. Mitigation: same as R-10 — the §Built-in-Read-Only-Set maintenance note in CLAUDE_PERMISSIONS.md instructs verification against the latest release.

---

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each FR begins with **Given** and follows Given/When/Then structure. `[MANUAL-ONLY] <reason>` marks FRs that cannot be automated.

#### Settings file surface

- **FR-001** (covers AC-1): **Given** the post-merge state of main, **When** any reader opens `.claude/settings.json`, **Then** the file MUST be valid strict-JSON (parseable by `jq empty .claude/settings.json` returning exit code 0). **And** the file MUST contain `permissions.allow`, `permissions.deny`, and `permissions.ask` arrays (each MAY be empty, but all three keys MUST be present). **And** the file MUST be ≤ ~150 LOC after Category 1 deduplication (target ~80 LOC per PRD; ceiling ~150 to allow rationale-row growth).

- **FR-002** (covers AC-2 cross-check): **Given** `.claude/settings.json` and `docs/standards/CLAUDE_PERMISSIONS.md`, **When** the AC-2 cross-check script (defined in plan.md §Verification-Recipe and run as task `T-cross-check`) is executed, **Then** the script MUST report ZERO orphaned rules in `settings.json` (every non-built-in rule MUST appear in CLAUDE_PERMISSIONS.md per-rule table) AND ZERO orphaned table rows in CLAUDE_PERMISSIONS.md (every row MUST reference a rule in `settings.json` or be flagged as a built-in-read-only-set entry).

- **FR-003** (covers AC-3 backward-compat): **Given** an adopter who has `.claude/settings.local.json` with personal customizations BEFORE F-4 lands, **When** they `git pull` the F-4 baseline, **Then** their `.claude/settings.local.json` MUST be untouched by the F-4 PR (the file is not under version control; F-4 modifies only `.claude/settings.json` + the two new docs). **And** the smoke-test fixture defined in plan.md §Verification-Recipe MUST verify a representative custom allow rule still resolves correctly post-pull.

- **FR-004** (covers AC-4 four-category structure): **Given** `.claude/settings.json`, **When** a reader maps each rule to a CLAUDE_PERMISSIONS.md category, **Then** every non-built-in rule MUST belong to exactly one of: Category 1 (read-only auto-approve), Category 2 (local-state auto-approve), Category 3 (destructive deny+ask), Category 4 (network host-allowlist). **And** Category 1 rules MUST NOT include any built-in-read-only command (per Claude Code docs: `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms — verified in CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set).

#### Documentation surface

- **FR-005** (covers AC-5 CLAUDE_PERMISSIONS.md content): **Given** `docs/standards/CLAUDE_PERMISSIONS.md`, **When** a SecOps reviewer reads the file, **Then** it MUST contain the following sections in order: framing paragraph (why this baseline exists), four-category description (with safety promise + failure modes per category), settings precedence (within-file deny→ask→allow worked example + cross-file project-deny-holds worked example), per-rule rationale table (rule | category | rationale | failure mode), built-in read-only set documentation, opt-out paths (≥3 paths), known limitations (Bash pattern fragility R-8, process-wrapper bypass R-9, read-only built-in shadow R-10, subdomain-matching unsupported per upstream issues). **And** the file MUST be ≤ ~350 LOC (target ~250 LOC per PRD).

- **FR-006** (covers AC-6 verification recipe sub-checks): **Given** the verification recipe defined in plan.md §Verification-Recipe, **When** the recipe is executed at /aod.build time and again post-merge, **Then** all of the following MUST pass: (a) `jq empty .claude/settings.json` returns exit code 0 (JSON validity), (b) Claude Code in a fresh session auto-approves a `git status` invocation without prompting (built-in read-only auto-approve regression check), (c) Claude Code in a fresh session presents a deny prompt for `Bash(rm -rf <test-path>)` (deny-tier verification), (d) the AC-2 cross-check script reports zero orphaned rules and zero orphaned table rows.

- **FR-007** (covers AC-7 subdomain-matching probe): **Given** the F-4 baseline is loaded with `WebFetch(domain:github.com)` in `permissions.allow` but no entry for `api.github.com`, **When** Claude Code attempts `WebFetch(api.github.com/repos/davidmatousek/tachi)`, **Then** the operation MUST surface a prompt (not auto-approve) — confirming the upstream-documented behavior that subdomain matching is not transitive. **And** if the probe instead auto-approves (an upstream behavior change), the result MUST be captured in the PR description as a side observation and the 19-domain explicit list MAY be reviewed for compaction in a follow-up Issue. *[MANUAL-ONLY] Requires interactive Claude Code session — no programmatic probe in F-4 scope.*

- **FR-008** (covers AC-8 ADR-041 content): **Given** `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, **When** a reviewer opens it, **Then** the file MUST follow the ADR-040 structure (Status / Context / Decision / Alternatives Considered / Consequences / Related Findings / References) with status "Accepted" and date 2026-05-08. **And** §Alternatives-Considered MUST enumerate ≥6 alternatives with Pros/Cons/Why-Not-Chosen sections, including: (1) keep current 26-rule allow-only, (2) ship `.claude/settings.example.json` as template, (3) ship empty `.claude/settings.json` (let adopters BYO), (4) ship managed-settings.json, (5) PreToolUse hooks, (6) explicit `.claude/settings.local.json` template. **And** the file MUST be ≤ ~150 LOC (target ~100 LOC per PRD).

- **FR-009** (covers AC-9 absolute-path cross-check): **Given** `.claude/settings.json` after the F-4 rewrite, **When** the security cross-check `grep -E '/(Users|home)/|^[A-Z]:\\\\' .claude/settings.json` is run, **Then** the grep MUST report ZERO matches — confirming the H-4 finding (`docs/security/OPEN_SOURCE_READINESS.md`) is not regressed by the new baseline (no machine-specific absolute paths in committed rules).

- **FR-010** (covers AC-10 CHANGELOG entry): **Given** `CHANGELOG.md`, **When** a reviewer reads the `## Unreleased` block, **Then** a new H3 subsection MUST be present with header `### Claude Code permissions baseline (BLP-02 F-4)` referencing: `.claude/settings.json` rewrite to four-category structure (~80 LOC after dedup), `docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC self-contained policy decision log), `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (~100 LOC, 6 alternatives-considered). **And** the entry style MUST match the F-3 precedent (subsection header + bullet-point body + ADR cross-reference + adopter migration note).

#### Risk-mitigation surface

- **FR-011** (covers AC-11 §Settings-Precedence within-file worked example): **Given** CLAUDE_PERMISSIONS.md §Settings-Precedence subsection, **When** a SecOps reviewer reads the within-file precedence walkthrough, **Then** the walkthrough MUST use the `Bash(git push:*)` allow + `Bash(git push --force:*)` deny case as the worked example, demonstrating that `git push` auto-approves while `git push --force` denies under `deny → ask → allow; first match wins` ordering.

- **FR-012** (covers AC-12 cross-file precedence smoke-test): **Given** the F-4 baseline is loaded AND a fixture `.claude/settings.local.json` containing `Bash(rm -rf:*)` in `allow`, **When** Claude Code attempts `Bash(rm -rf <test-path>)`, **Then** the project-level deny MUST hold (deny prompt surfaces; the local-file allow does NOT override). **And** CLAUDE_PERMISSIONS.md §Settings-Precedence MUST include this cross-file case as a second worked example, pointing adopters wishing to permit a baseline-denied operation to Path 2 (fork-and-edit) rather than local-file allow. *[MANUAL-ONLY] Requires interactive Claude Code session.*

#### Conventional Commit + release-please surface

- **FR-013** (covers PRD §Release-Please-Trigger-Posture): **Given** the F-4 PR, **When** the maintainer opens or edits the PR title, **Then** the title MUST be `feat(277): claude permissions baseline (BLP-02 F-4)`. **And** post-merge, the maintainer MUST verify a release-please PR opens within ~30s via `gh pr list --state open --search "release-please" --limit 3`. **And** if no release-please PR opens, the maintainer MUST push an empty release-marker commit per the F-212 incident recovery flow documented in `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles.

- **FR-014** (covers post-merge `/security` re-scan): **Given** the post-merge `/security` re-scan, **Then** no new HIGH or MEDIUM findings MUST be introduced by F-4. **And** LOW or INFO side-effect findings MAY appear if they document a separate concern (e.g., a CHANGELOG style nit). **And** any pre-existing finding linked to the permissions surface (none currently expected; no `/security` finding directly closed by F-4 — F-4 is posture-gap-closure, not vuln-closure) MUST be re-scored if the rescan classifier flags one.

#### Out of F-4 scope (committed as post-merge follow-up Issues per F-3 pattern)

- **AC-15 (nice-to-have)**: Pre-commit hook integration (`jq empty` + AC-2 cross-check) on `.claude/settings.json` and CLAUDE_PERMISSIONS.md edits. Logged at /aod.deliver time as a low-priority backlog Issue. NOT a F-4 functional requirement.
- **AC-16 (nice-to-have)**: CI integration of the verification recipe (run JSON-validity + cross-check + AC-7 subdomain probe on PR diffs touching the permissions surface). Logged at /aod.deliver time as a backlog Issue. NOT a F-4 functional requirement.
- **PII / secret-scanning hooks**: separate feature, out of scope for F-4 per ADR-041 §Out-of-Scope.
- **Enterprise managed-settings.json shipping**: rejected in ADR-041 §Alternatives-Considered #4 (tachi is a project-level open-source tool; managed-settings.json is enterprise IT deployment artifact). Out of scope for F-4.
- **WebSearch allowlisting**: schema-infeasible per Claude Code permissions docs. Out of scope for F-4.

### Key Entities *(include if feature involves data)*

- **`.claude/settings.json`** (rewritten): Project-level Claude Code settings file. Strict JSON. Four-category logical structure (reflected in CLAUDE_PERMISSIONS.md, not in JSON keys; the JSON has only `permissions.allow`, `permissions.deny`, `permissions.ask`). ~80 LOC after Category 1 deduplication.
- **`docs/standards/CLAUDE_PERMISSIONS.md`** (new): Self-contained policy decision log + per-rule rationale catalog. ~250 LOC. Lives in `docs/standards/` alongside DEFINITION_OF_DONE.md, GIT_WORKFLOW.md, etc.
- **`docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`** (new): Architecture decision record. ~100 LOC. Status: Accepted. ≥6 alternatives considered.
- **`CHANGELOG.md` `## Unreleased` block**: Receives the F-4 H3 subsection entry.
- **`.claude/settings.local.json`** (referenced, not modified): Adopter personal-override file. Gitignored. F-4 does not touch this file; FR-003 verifies adopter customizations there survive `git pull`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (PRD G1 — enterprise audit-ready): SecOps reviewer applying a representative AI-agent permission audit rubric (e.g., NIST AI RMF GV.RR aligned policy log requirements) to CLAUDE_PERMISSIONS.md MUST find: rule rationale present, governance framing present, opt-out paths documented, known limitations enumerated. Verified by reviewer-rubric test described in US-4 Independent Test (run by PM at /aod.deliver time as part of US-4 sign-off).
- **SC-002** (PRD G2 — defense-in-depth gate): F-4 baseline blocks a typo'd `git push --force` with an explicit deny prompt (not auto-approve, not regular ask). Verified by manual interactive Claude Code session per US-2 Independent Test.
- **SC-003** (PRD G3 — backward compat): Adopter `.claude/settings.local.json` customizations survive `git pull` of F-4. Mechanically guaranteed by Claude Code native precedence; verified by FR-003 fixture smoke-test in plan.md §Verification-Recipe.
- **SC-004** (PRD G4 — cross-list precedence honest): CLAUDE_PERMISSIONS.md §Settings-Precedence documents both within-file `deny → ask → allow` ordering AND cross-file project-deny-holds mechanic with two worked examples. Verified by reviewer-diff inspection at /aod.build PM-review-time.
- **SC-005** (PRD G5 — host-allowlist coverage): All 19 PRD-enumerated domains are present in `.claude/settings.json` `permissions.allow` with `WebFetch(domain:<host>)` pattern. Verified by `jq -r '.permissions.allow[] | select(test("^WebFetch"))' .claude/settings.json | wc -l` returning ≥19.
- **SC-006** (PRD G6 — H-4 not regressed): Post-rewrite `.claude/settings.json` contains zero machine-specific absolute paths. Verified by FR-009 grep cross-check.
- **SC-007** (PRD G7 — BLP-02 Wave 4 closed): Verified by:
  - Initiative Tracker memory entry update (BLP-02 Wave 4 → DELIVERED) at /aod.deliver time.
  - PRD INDEX.md status flip Approved → Delivered with PR link.
  - Post-merge `/security` re-scan recording no new HIGH/MEDIUM findings (FR-014).
- **SC-008** (operational, derived from PRD §Estimate-and-Timeline): Total active maintainer time ≤ 9 hours; wall-clock delivery ≤ next-day cap. Verified at /aod.deliver time by retrospective time-tracking.

---

## Assumptions

- **Cross-file deny precedence** (industry-research clarification): Per Claude Code documentation (`code.claude.com/docs/en/settings`), denylist always takes precedence over allowlist *across files*; project `.claude/settings.json` deny rules hold even if `.claude/settings.local.json` (or user-settings, or managed-settings) contains a competing allow. This is the load-bearing assumption for AC-12 cross-file smoke-test and for the second §Settings-Precedence worked example. If this behavior changes in a future Claude Code release, FR-012 and US-3 AC-3 require revision.
- **Subdomain matching not transitive** (per Issues #15260, #11972, #1217): `WebFetch(domain:github.com)` does NOT match `api.github.com`. Verified-by-citation in research.md; verified-by-probe in AC-7. The 19 explicit per-subdomain entries in Category 4 are the correct posture given upstream behavior.
- **`WebFetch(domain:*)` wildcard is broken** (per Issue #11972): Cannot fall back to `WebFetch(domain:*)` as a permissive default for adopters who want broader allowlisting; documented as known limitation in CLAUDE_PERMISSIONS.md §Known-Limitations.
- **Built-in read-only command set is stable** at the F-4 merge SHA: `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms run without prompt. CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set documents the set with a maintenance note for re-verification on Claude Code upgrades.
- **No `finding.yaml` / taxonomy schema change** required (PRD §Non-Goals).
- **No agent / command / skill / script code change** required — pure documentation + settings file rewrite. Same docs-only-feature shape as F-3.
- **Maintainer holds GitHub repo-admin rights** for `davidmatousek/tachi` — required for PR merge + release-please marker push if needed.
- **Release-please pipeline is operational** at PRD draft (latest successful release: v4.32.0; v4.33.0 in-flight from F-3). F-4 will trigger v4.34.0 bump assuming F-3 lands first.
- **AC-7 expected outcome is "subdomains do not collapse"** based on industry research; if the probe instead returns auto-approve, the 19-domain list MAY be reviewed for compaction in a follow-up Issue without blocking F-4.
