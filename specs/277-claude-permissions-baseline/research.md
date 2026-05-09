# Research Summary: F-4 Claude Permissions Baseline (PRD #277)

**Date**: 2026-05-08
**Branch**: `277-claude-permissions-baseline`
**PRD**: [docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md](../../docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md)

---

## Knowledge Base Findings

KB directory (`docs/kb/`) does **not exist** in tachi. No prior patterns or institutional-knowledge entries on Claude Code permissions to draw from. Spec authoring proceeds without KB grounding (closest analogue: F-3 #272 spec, which is itself the most similar precedent in the repo).

---

## Codebase Analysis

### Current `.claude/settings.json` state
- **26-rule allow-only** flat array; zero `deny`/`ask` lists.
- All Bash/`gh`/Edit/Write patterns; no host allowlist; no destructive denials.
- Comment-free (strict JSON; no JSONC tolerance — confirms PRD posture).

### Settings local override
- `.claude/settings.local.json` does **not exist** in repo (gitignored). AC-3 smoke-test must verify customizations survive `git pull` of new baseline.

### ADR pattern (ADR-040 as precedent)
- Path: `docs/architecture/02_ADRs/`. Highest existing: ADR-040 (Config File Parsing Hardening, F-2 BLP-02 Wave 2).
- Structure: Status line → Context → Decision (numbered items) → Alternatives Considered (Pros/Cons/Why-Not-Chosen) → Consequences (Positive/Negative/Mitigation) → Related Findings → References.
- **ADR-041 confirmed as next number** (no index file; sequential naming).

### Standards docs shape (`docs/standards/`)
- 12 existing files; H1 → H2 → H3 markdown without YAML frontmatter.
- Typical shape: framing paragraph → enumerated tables/lists → cross-refs.
- CLAUDE_PERMISSIONS.md will follow this pattern (~250 LOC per PRD).

### F-3 (#272) docs-only feature precedent
- Path: `specs/272-security-md-disclosure/`.
- Spec: 5 user stories (P1/P1/P2/P2/P3) with Given-When-Then ACs; 14 mandatory ACs; PM-signed.
- Plan: Constitution Check + 5-section outline + verification recipe.
- Tasks: 25 tasks across phases; `[MANUAL-ONLY]` markers for UI-required smoke-tests; cross-check tasks for AC validation.
- Key lesson: docs-only features document *changes to documentation and configuration* — AC table maps each FR to concrete evidence (cross-check scripts, JSON validity, smoke-tests).
- **F-4 mirrors this pattern with one scaling factor**: ~2x ADR-041 + CLAUDE_PERMISSIONS.md ~250 LOC drives ~8-9h envelope vs F-3's ~3-4h.

### Permissions schema validation surface
- No existing `.claude/settings.json` parsing/validation code in tachi. No `jq` invocations, no schema validators, no smoke tests.
- AC-6 must explicitly add JSON-validity check + `git status` auto-approve regression check + `rm -rf` deny prompt verification.

### Built-in read-only command set
- Documented exclusively in PRD §Category 1; tachi docs do not currently capture this.
- Built-in set per Claude Code docs: `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms — runs without prompt in every mode.
- Listing in `allow` is no-op. CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set is the canonical answer.

### Network egress audit
- 19 domains enumerated in PRD §Category 4. Verification by tachi command-surface egress audit during PRD review (cited in PM sign-off).
- Includes GitHub (7), Anthropic/Claude (5), OWASP (3), MITRE (3), NIST (1).

### CHANGELOG.md format
- Keep-a-Changelog 1.1.0; H3 subsection per feature under `## Unreleased` with prose description, bullet list of files+ADR refs, optional migration guidance.
- F-3 entry shape (lines 54-70): `### SECURITY.md and private disclosure channel (BLP-02 F-3)` + body.
- F-4 entry will follow identical shape.

### release-please config
- `release-please-config.json` — `"release-type": "simple"`; `feat(SCOPE):` triggers `Features` section bump.
- Manifest: current version `4.32.0` → F-4 will bump to `4.33.0` (BLP-02 F-3 already released as 4.33.0; this means F-4 will bump to **4.34.0** — correction noted below).

**CORRECTION**: The PM sign-off in F-3 PRD INDEX states `release-please PR #274 chore(main): release 4.33.0` is currently open. F-4 bumps to **4.34.0** assuming F-3 lands first.

---

## Architecture Constraints

### Constitution
- Path: `.aod/memory/constitution.md`.
- **Principle III (Backward Compatibility — NON-NEGOTIABLE)**: governs F-4 settings-merge precedence — adopter `.claude/settings.local.json` customizations must not break on `git pull`.
- **Principle VII (Definition of Done)**: documentation-only exception applies; F-4 is settings + docs + ADR (no production deployment).
- **Principle X (Product-Spec Alignment — NON-NEGOTIABLE)**: Triad triple sign-off required on tasks.md before implementation. PRD already has these.

### Definition of Done
- Path: `docs/standards/DEFINITION_OF_DONE.md`.
- 3-step gate (Push / Test / User-Validate). F-4 docs-only exception: post-merge `/security` re-scan + JSON-validity check + AC-6 `git status` regression + AC-7 subdomain-matching probe substitute for "Tested" step.

### Adopter customization surface (settings precedence)
- **Currently zero documentation** in tachi standards.
- F-4's CLAUDE_PERMISSIONS.md is the first place to document this — required by AC-3 + Constitution backward-compat principle.
- **Critical clarification from web research (below)**: cross-file precedence model is more nuanced than PRD initially framed.

### Pre-existing security finding H-4
- Path: `docs/security/OPEN_SOURCE_READINESS.md`.
- H-4 (HIGH): "`.claude/settings.json` contains machine-specific paths".
- F-4 baseline rewrite must use **relative paths only** (no `/Users/david/...` absolute paths). Cross-check via `grep` over the new baseline before commit.

---

## Industry Research (Web)

### Settings precedence — Claude Code docs (`code.claude.com`, `docs.claude.com`)

**Hierarchy (highest-to-lowest)**:
1. **Enterprise managed-settings.json** (`/Library/Application Support/ClaudeCode/managed-settings.json` on macOS; `/etc/claude-code/managed-settings.json` on Linux/WSL; `C:\ProgramData\ClaudeCode\managed-settings.json` on Windows).
2. **Project settings** (`.claude/settings.json` — committed, team-wide).
3. **User settings** (`~/.claude/settings.json` — cross-project, lowest).

**Cross-file deny precedence**: *"if a permission is allowed in user settings but denied in project settings, the project setting takes precedence and the permission is blocked"*. **Denylist always takes precedence over allowlist.**

**KEY IMPLICATION FOR PRD WORKED EXAMPLE**: The PRD's "settings.local.json adds `Bash(git push --force:*)` to allow to override settings.json deny" example is **likely incorrect** — deny rules from project `settings.json` are not overridden by `settings.local.json` allow entries. The actual override path is:
- Adopters wishing to permit a denied operation must remove or modify the deny rule in their fork of `.claude/settings.json` (the upstream settings file), not add a competing `allow` in `.claude/settings.local.json`.
- Alternative: adopters add the rule to user settings (`~/.claude/settings.json`) — but project deny still wins.

**Spec must update the worked example** to reflect this. The accurate path is: opt-out via *removal of the deny rule* from `settings.json` (an explicit edit), or via *fork* (the third opt-out path the PRD already documents). The "local override" path works only for *adding new allows* (not in the baseline) or *narrowing already-allowed permissions*, not for overriding denies.

### WebFetch domain subdomain matching — Claude Code GitHub Issues

**Confirmed via Issue #15260, #11972, #1217**:
- `WebFetch(domain:github.com)` does **NOT** match `api.github.com`, `raw.githubusercontent.com`, or any subdomain.
- `WebFetch(domain:*)` wildcard does NOT work as expected (Issue #11972 — bug, still prompts per-domain).
- Workaround: explicit per-subdomain entries (the PRD's current 19-domain posture is correct).
- TLD wildcards (`*.org`) and subdomain wildcards (`*.example.com`) are open feature requests, not yet shipped.

**KEY IMPLICATION FOR AC-7**: AC-7 smoke-test outcome is now **predictable**: subdomains do NOT collapse. The 19 explicit domain entries are required and documented as such. AC-7 remains valuable as adversarial verification, but the PRD's "if subdomain-matching works, collapse to root domains" branch should be downgraded to a citation-only note (CLAUDE_PERMISSIONS.md §Subdomain-Matching).

### Enterprise managed settings — relevance to F-4
- Managed-settings.json is the highest-precedence layer; an enterprise admin can override anything tachi ships.
- F-4 baseline is **shipped as project settings**, knowingly subordinate to enterprise managed-settings policies. CLAUDE_PERMISSIONS.md should document this layering so adopters in managed environments understand their managed policy can further constrain (but not loosen) the baseline.
- ADR-041 §Alternatives-Considered should add (or affirm — already in v1.1) a note that "ship as managed-settings.json" was rejected because tachi is a project-level open-source tool, not an enterprise IT deployment artifact.

### Sources
- [Claude Code settings — Claude Code Docs](https://code.claude.com/docs/en/settings)
- [Configure permissions — Claude API Docs](https://platform.claude.com/docs/en/agent-sdk/permissions)
- [Issue #15260 — Wildcard subdomain matching for WebFetch domain permissions](https://github.com/anthropics/claude-code/issues/15260)
- [Issue #11972 — WebFetch(domain:*) wildcard not working](https://github.com/anthropics/claude-code/issues/11972)
- [Issue #1217 — Domain not allowed even when explicitly allowed](https://github.com/anthropics/claude-code/issues/1217)
- [Issue #31533 — TLD-level wildcard matching feature request](https://github.com/anthropics/claude-code/issues/31533)
- [Issue #27139 — Broad wildcard permissions in settings.local.json not respected](https://github.com/anthropics/claude-code/issues/27139)

---

## Recommendations for Spec

1. **User stories: 5 at P1/P1/P2/P2/P3** — mirror F-3 shape exactly. Map to PRD's five user surfaces.

2. **AC count: 14 mandatory + 2 nice-to-have** — exactly matches PRD §Acceptance Criteria. AC-2 (cross-check script) and AC-6 (JSON-validity + git-status regression + rm -rf deny prompt) are the test backbone for docs-only feature.

3. **Update worked example in CLAUDE_PERMISSIONS.md §Settings-Precedence**:
   - Replace "settings.local.json adds `Bash(git push --force:*)` to allow → overrides settings.json deny" with the **correct cross-file model**: deny precedence holds across files; the override paths are (a) edit `.claude/settings.json` directly, (b) fork the baseline.
   - Document the within-file `deny → ask → allow` precedence using the `Bash(git push:*)` allow + `Bash(git push --force:*)` deny case (this was the PRD's intended example and remains valid as a within-file demonstration).
   - Document the cross-file model with a separate worked example: "an adopter who wants to allow `git push --force` for a personal-fork workflow must edit `.claude/settings.json` to remove the deny rule (Path 2: fork-and-edit), or add the rule to managed-settings.json if shipping in a managed environment".

4. **AC-7 framing**: downgrade "if subdomains match, collapse list" to citation-only note. Smoke-test still verifies (defensive against future Claude Code semantics changes), but expected outcome is documented as "no collapse — explicit per-subdomain required (per Issues #15260, #11972)".

5. **Spec must include**:
   - **FR-001 through FR-014** mapping 1:1 to PRD's 14 ACs.
   - **5 risk mitigations** (R-1 through R-5 from PRD §Risks; R-6 reframed as cross-file precedence clarification per web finding; R-7 through R-10 from PRD v1.1 review).
   - **Verification recipe** in plan.md (not spec.md): JSON validity (`jq -e empty`), grep for absolute paths (H-4 cross-check), `gh issue` smoke-tests (Categories 2-3 surface), AC-7 subdomain probe.

6. **Tasks-time additions** (defer to /aod.tasks):
   - T-N: AC-7 subdomain-matching probe (smoke-test against `api.github.com` with `WebFetch(domain:github.com)` only — expected: prompts).
   - T-N+1: H-4 absolute-path cross-check (grep `/Users/`, `/home/`, `C:\\` in new `settings.json`).
   - T-N+2: cross-file deny precedence smoke-test (per web research finding) — verify `settings.local.json` cannot override `settings.json` deny.

7. **Out-of-scope clarifications**:
   - `WebSearch` allowlisting (schema-infeasible — documented in PRD).
   - Enterprise managed-settings.json shipping (rejected in ADR-041 alternatives — out of scope for F-4).
   - PreToolUse hook approach (rejected in ADR-041 alternative 5 — out of scope).
   - PII/secret-scanning hooks (separate feature; not bundled).

8. **CHANGELOG entry**: H3 subsection `### Claude Code permissions baseline (BLP-02 F-4)` under `## Unreleased`. Body = enumerated files + ADR-041 reference + adopter migration note ("existing customizations in `.claude/settings.local.json` continue to work for adding new allows; deny overrides require fork-and-edit").

9. **Branch/PR**: `277-claude-permissions-baseline` (already created); PR title `feat(277): claude permissions baseline (BLP-02 F-4)`; squash-merge → release-please bumps to v4.34.0 (assuming F-3 v4.33.0 lands first).
