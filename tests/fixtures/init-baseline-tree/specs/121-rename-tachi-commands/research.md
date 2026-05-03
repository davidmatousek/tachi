# Research Summary: Rename Tachi Commands to tachi.* Namespace

## Knowledge Base Findings
- **PAT-008 (Feature 039)**: Command reorganization (decoupling `/infographic` from `/threat-model`) touched 32 files across 5 adapters. Lesson: atomic task decomposition and adapter mirror tasks make cross-cutting renames mechanical. Same-day delivery achievable when changes follow established patterns.
- **PAT-018 (Feature 078)**: Prototype-first gate — rename one command first, validate, then scale to remaining commands to catch issues early (missed cross-references).
- **NAMING_GUIDELINES**: Docs already document old-to-new naming migration formats with explicit mappings. Precedent for documenting rename mappings.
- **ADR-007 (Stack Packs)**: Renaming/deleting directories breaks symlinks — relevant if any commands are symlinked from adapter directories.

## Codebase Analysis
- **Command files**: 5 targets in `.claude/commands/` (threat-model.md, risk-score.md, compensating-controls.md, infographic.md, security-report.md)
- **Adapter copies**: 3 in `adapters/claude-code/commands/`, 1 GitHub Actions workflow in `adapters/github-actions/`
- **Cross-reference scope**: ~2,207 invocations across 344 unique files
  - Agents: 124 references across 21 files in `.claude/agents/`
  - Skills: 115 references across 22 files in `.claude/skills/`
  - Templates: 116 references across 15 files in `templates/`
  - Schemas: 26 references across 8 files in `schemas/`
  - Docs/guides: 200+ references across 54 files in `docs/`
  - Commands (internal cross-refs): 73 references
- **aod.* pattern**: 19 commands using `aod.` prefix — established model to follow. Naming rule: `{prefix}.{command-name}.md`
- **Pipeline chain**: `/threat-model` -> `/risk-score` -> `/compensating-controls` -> `/infographic` / `/security-report`

## Architecture Constraints
- **Manifest-driven install**: `INSTALL_MANIFEST.md` is the single source of truth. Machine-parseable section between `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers.
- **Install script**: Parses manifest for file paths, copies atomically. No hardcoded command names — filesystem-based. Supports `--version <tag>` checkout.
- **ADR-009**: `{{tachi}}` template variable for project name substitution during init. Sed-based replacement in `init.sh`.
- **No command naming ADR exists** — this rename establishes the convention.
- **Atomic delivery**: Install script forbids self-installation, reports success/failure counts.

## Industry Research
- Dot-separated namespace prefixes (e.g., `kubectl.plugin`, `git-flow.*`) are standard CLI/IDE patterns for avoiding command collision in plugin ecosystems.
- Atomic rename-and-redirect is the standard approach for breaking changes in pre-1.0 projects — no backward compatibility shims.
- Prototype-first validation (rename one, verify, then scale) is an established risk mitigation pattern for large-scale renames.

## Recommendations for Spec
- Follow the aod.* naming convention exactly: `tachi.{command-name}.md`
- Use prototype-first approach: rename one command, validate cross-references, then scale
- Update INSTALL_MANIFEST.md as part of the atomic rename (install script auto-picks up changes)
- Add deprecated-file cleanup to install.sh for upgrade scenarios
- Historical artifacts (PRDs, archived specs, old CHANGELOG entries) are immutable — do not update
- Grep verification as final validation step to catch missed references
- No backward-compat shims — tachi is pre-1.0
