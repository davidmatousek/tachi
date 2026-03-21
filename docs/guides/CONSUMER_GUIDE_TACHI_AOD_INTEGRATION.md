# Auxiliary Guide — Tachi AOD Kit Integration

**Purpose**: Integrate the Tachi threat modeling toolkit into the AOD Kit as an optional, invocable capability.
**When to execute**: After Tachi F-001 through F-009 are shipped (core agents + platform adapters).
**Prerequisite**: A working Tachi installation with the Claude Code adapter (`adapters/claude-code/`).
**Target repo**: This repo (product-led-spec-kit / agentic-oriented-development-kit).

**Related documents**:
- [CONSUMER_GUIDE_TACHI.md](CONSUMER_GUIDE_TACHI.md) — Main consumer guide with 10 seed features
- [CONSUMER_GUIDE_TACHI_RESEARCH.md](CONSUMER_GUIDE_TACHI_RESEARCH.md) — Authoritative framework references (STRIDE, OWASP, SARIF, CVSS, crosswalk)

**How to use this guide**: When Tachi's core is ready, copy the feature block below into `/aod.discover` to create a GitHub Issue, then run `/aod.define` through `/aod.deliver` to implement it.

---

## Feature Summary

| ID | Feature | Stories | Depends On |
|----|---------|---------|------------|
| F-INT-001 | AOD Kit Tachi Integration | 5 | Tachi F-001 – F-009 |

---

### F-INT-001: AOD Kit Tachi Integration

**Goal**: Enable AOD Kit users to opt into automated threat modeling by installing Tachi as a skill, so that any project using the AOD lifecycle can generate STRIDE + AI threat models from their architecture diagrams.

**Stories**:

1. **As a developer, I want a `/aod.threat-model` skill**, so that I can invoke Tachi's orchestrator from within my AOD workflow without leaving the CLI.
   - Skill accepts an architecture input (file path or inline ASCII/Mermaid/C4/PlantUML/free-text)
   - Skill invokes the Tachi orchestrator agent, which dispatches to STRIDE + AI agents
   - Output written to `.aod/threat-model/` directory (threats.md, threats.sarif, threat-report.md)
   - Skill follows AOD subagent return policy (status + file path, not full content)

2. **As a developer, I want Tachi integrated as an optional step in `/aod.build`**, so that threat modeling runs automatically during implementation without a separate manual invocation.
   - New optional flag: `/aod.build --threat-model` (opt-in, not default)
   - When enabled, threat modeling runs after architecture docs exist but before implementation begins
   - Findings at Critical/High severity trigger an acknowledgment gate (similar to `/security` scan)
   - Skippable via `--no-threat-model` for projects that don't need it

3. **As a developer, I want a `tachi` stack pack**, so that I can activate Tachi conventions and agent prompts in my project with a single command.
   - `aod.stack use tachi` copies Tachi agent prompts into the project's `.claude/agents/tachi/` directory
   - Pack includes: orchestrator, 6 STRIDE agents, 2 AI agents, report agent, infographic agent
   - Pack scaffold creates: `docs/architecture/threat-model/` directory structure, example architecture input template
   - `aod.stack remove` cleanly removes all Tachi artifacts

4. **As a security-conscious developer, I want threat model output integrated with my existing CI/CD**, so that SARIF findings from Tachi appear in GitHub Code Scanning alongside my other security tools.
   - Documentation for adding `codeql/upload-sarif@v3` step to upload `threats.sarif`
   - Example GitHub Actions workflow snippet in the stack pack scaffold
   - SARIF output location follows the convention: `.aod/threat-model/YYYY-MM-DD/threats.sarif`

5. **As a developer, I want clear documentation on when and how to use Tachi within the AOD lifecycle**, so that threat modeling fits naturally into my existing workflow without disruption.
   - Update `docs/commands.md` (or equivalent) with `/aod.threat-model` usage
   - Update `CLAUDE.md` commands section with the new skill
   - Add a "Threat Modeling" section to `docs/architecture/README.md` explaining the STRIDE + AI methodology
   - Document the input-to-STRIDE crosswalk (reference `095-tachi-research.md` Section 12) so users understand how their architecture diagrams map to threats

**Interface Contract (consumes)**:
- Tachi Claude Code adapter artifacts from `adapters/claude-code/` (produced by Tachi F-009)
- Tachi orchestrator agent prompt and all threat agent prompts

**Interface Contract (produces)**:
- `.claude/skills/aod-threat-model/` — the `/aod.threat-model` skill definition
- `stacks/tachi/` — the Tachi stack pack (rules, persona, scaffold templates)
- Updated `CLAUDE.md`, command docs, and architecture docs

**Definition of Done**:
- `/aod.threat-model` produces a valid threats.md + threats.sarif from a sample ASCII architecture diagram
- `aod.stack use tachi` installs cleanly and `aod.stack remove` removes cleanly with no orphaned files
- `/aod.build --threat-model` triggers threat analysis and gates on Critical/High findings
- All documentation updated and consistent with existing AOD Kit style
- Changes synced upstream via `/aod.sync-upstream`

---

## Execution

1. Copy the feature block above (from `#### F-INT-001:` to `---`)
2. Run `/aod.discover` and paste as the idea description
3. Run `/aod.define` to create the PRD
4. Run `/aod.plan` to create spec, plan, and tasks
5. Run `/aod.build` to implement
6. Run `/aod.deliver` to close
7. Run `/aod.sync-upstream` to propagate to upstream repo

## Feature Completion Tracker

| ID | Feature | Status |
|----|---------|--------|
| F-INT-001 | AOD Kit Tachi Integration | [ ] |
