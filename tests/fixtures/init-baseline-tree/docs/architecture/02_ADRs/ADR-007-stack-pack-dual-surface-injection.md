# ADR-007: Stack Pack Dual-Surface Injection and Copy-Not-Symlink Strategy

**Status**: Accepted
**Date**: 2026-02-27
**Deciders**: Architect, Feature 058 Implementation Team
**Feature**: 058 - Stack Packs

---

## Context

Stack packs need to inject technology-specific conventions into the AI agent runtime at two distinct points:

1. **Rules surface**: Stack-specific coding rules (conventions, security patterns) must be discoverable by all agents through the standard `.claude/rules/` directory, which Claude Code auto-loads at session start.
2. **Persona surface**: Persona supplements must be loaded by specialized and hybrid agents during `/aod.build` task execution, providing role-specific stack expertise.

These two surfaces serve different audiences (all agents vs. specialized agents) and have different loading semantics (auto-loaded at session start vs. on-demand during build). The architecture must handle activation, deactivation, and single-pack-at-a-time constraints while keeping pack source files immutable.

Additionally, a decision was needed on file delivery: should activation create symbolic links from `.claude/rules/stack/` to `stacks/{pack}/rules/`, or should files be copied?

A third decision involved state tracking: how to record which pack is active and allow commands to query activation status without reading the rules directory.

---

## Decision

We will use a **dual-surface injection pattern** with **copy-not-symlink** file delivery and **JSON state tracking**.

### Surface 1: Rules injection (`.claude/rules/stack/`)

On activation (`/aod.stack use`), all `.md` files from `stacks/{pack}/rules/` are **copied** into `.claude/rules/stack/`. A generated `persona-loader.md` file is also placed in this directory, instructing specialized/hybrid agents to read their persona supplement from the pack's `agents/` directory.

On deactivation (`/aod.stack remove`), all files in `.claude/rules/stack/` are deleted.

### Surface 2: Persona injection (build-time prompt augmentation)

During `/aod.build`, the build command reads `.aod/stack-active.json` to determine the active pack. For each dispatched agent task, if the agent is classified as specialized or hybrid, the build prompt includes an instruction to read `stacks/{pack}/agents/{agent-name}.md` as supplementary context.

Core agents (product-manager, architect, team-lead, orchestrator, web-researcher) are never modified by pack activation.

### File delivery: Copy, not symlink

Pack rule files are copied to `.claude/rules/stack/` rather than symlinked.

### State tracking: `.aod/stack-active.json`

A JSON file records the active pack name, activation timestamp, and schema version. All `/aod.stack` subcommands read this file to determine current state.

---

## Rationale

### Why dual-surface?

**Rules and personas serve different roles at different times.** Rules are broad conventions that every agent should follow (e.g., "ALWAYS use Server Components for data fetching"). Personas are role-specific expertise (e.g., the frontend-developer's knowledge of Next.js App Router patterns). Collapsing both into a single surface would either over-load all agents with role-specific details or under-serve specialized agents with only generic rules.

**Separation enables independent evolution.** Rules can be updated without touching personas, and vice versa. New agent types can be added without modifying the rules injection path.

### Why copy, not symlink?

1. **Cross-platform safety**: Symlinks behave differently on Windows (requires admin privileges or developer mode) vs. Unix. Copy works identically everywhere.
2. **Deactivation is a clean delete**: Removing copies is straightforward (`rm .claude/rules/stack/*.md`). Removing symlinks requires checking whether the target still exists to avoid broken link warnings.
3. **Immutability of source**: Copies prevent accidental edits to pack source files through the rules directory. Pack files under `stacks/` remain the canonical, committed source.
4. **Git cleanliness**: `.claude/rules/stack/` is gitignored. Copies create no git tracking issues. Symlinks pointing to tracked files in `stacks/` could confuse git status in some configurations.
5. **Re-activation refresh**: When a user re-activates the same pack (to pick up pack source changes), copy naturally overwrites with the latest version. Symlinks would already point to the updated source, but this makes re-activation a no-op, which is less explicit.

### Why JSON state file?

1. **Queryable**: Any command can read `.aod/stack-active.json` to check activation status without scanning the filesystem.
2. **Atomic**: JSON file is a single read/write operation, consistent with the Atomic File Write pattern used by `run-state.json`.
3. **Extensible**: Future versions can add fields (e.g., pack version, activation options) without schema migration.
4. **Consistent with codebase**: Follows the same JSON state pattern as `.aod/run-state.json` (Feature 022/030).

---

## Alternatives Considered

### Alternative 1: Single-surface injection (rules only)

Copy all pack content (rules + personas) into `.claude/rules/stack/`.

**Pros**:
- Simpler activation logic
- All pack context auto-loaded by Claude Code rules discovery

**Cons**:
- Core agents would load persona supplements intended for other agents, wasting context tokens
- No way to selectively load persona supplements per agent role
- Violates context budget (800-line limit would be exceeded for full packs)

**Why Not Chosen**: Context budget enforcement requires selective loading. All-or-nothing injection is wasteful.

### Alternative 2: Symlinks instead of copies

Create symbolic links from `.claude/rules/stack/` to `stacks/{pack}/rules/`.

**Pros**:
- No file duplication
- Source changes immediately reflected
- Smaller disk footprint

**Cons**:
- Cross-platform issues (Windows)
- Broken symlinks if pack directory is renamed or deleted
- Implicit source changes (edits to `stacks/` immediately affect runtime)
- Git may track symlinks differently across platforms

**Why Not Chosen**: Cross-platform safety and immutability of pack source outweigh disk savings (files are small Markdown).

### Alternative 3: Environment variable or config file instead of JSON state

Use an environment variable or a simple text file to track the active pack.

**Pros**:
- Simpler to read (no JSON parsing needed)
- Environment variables persist across shell sessions

**Cons**:
- Environment variables do not persist across agent sessions
- Text files lack structure for future extensibility
- Inconsistent with existing JSON state pattern in the codebase

**Why Not Chosen**: JSON provides structured, extensible state consistent with codebase conventions.

---

## Consequences

### Positive

- Clean separation of concerns between rules (all agents) and personas (role-specific agents)
- Context budget enforcement is natural -- rules load via auto-discovery, personas load on-demand
- Pack activation and deactivation are fully reversible with no side effects on source files
- Single-pack constraint is easily enforced by checking `stack-active.json` before activation
- Cross-platform compatibility (copy works everywhere)
- State file enables future features (pack versioning, activation history)

### Negative

- File duplication between `stacks/{pack}/rules/` and `.claude/rules/stack/` (mitigated: files are small Markdown, typically <200 lines total)
- Two-step mental model: developers must understand both injection surfaces
- Re-activation requires explicit user action to refresh rules from source

### Mitigation

- Context budget validation runs automatically on activation, warning if thresholds are exceeded
- Inconsistent state detection handles orphaned rules, corrupted state files, and missing pack directories
- Activation summary clearly shows what was copied and where

---

## Related Decisions

- ADR-001: Atomic State Persistence (same JSON state pattern used by `stack-active.json`)
- Pattern: Dual-Surface Injection (docs/architecture/03_patterns/README.md)

---

## References

- Feature 058 Spec: `specs/058-prd-058-stack/spec.md`
- Stack Pack Skill: `.claude/skills/aod-stack/SKILL.md`
- Stack Packs README: `stacks/README.md`
