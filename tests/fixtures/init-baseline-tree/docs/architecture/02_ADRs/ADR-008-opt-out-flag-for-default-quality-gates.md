# ADR-008: Opt-out Flag for Default-On Quality Gate Steps in Commands

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: Architect, Feature 065 Implementation Team
**Feature**: 065 - Add /simplify Command to AOD Process

---

## Context

Feature 065 integrates the Claude Code built-in `/simplify` skill as Step 6 of the `/aod.build` command. This adds a code simplification and readability pass after implementation tasks complete.

The question is: should this step be **opt-in** (off by default, users must request it) or **opt-out** (on by default, users can skip it)?

Two distinct contexts exist for `/aod.build`:

1. **Application code repos**: Users have source files modified during the build session. Running `/simplify` provides genuine value -- it reduces complexity and improves readability before commit.

2. **Methodology-only repos** (like this kit itself, where build sessions modify only Markdown command files and documentation): Running `/simplify` is a no-op or potentially counterproductive -- documentation phrasing should not be "simplified" in the same way code is.

Additionally, CI/CD pipelines that invoke `/aod.build` programmatically need deterministic, reproducible runs. An agent-driven simplification step introduces non-determinism that may be undesirable in automated contexts.

---

## Decision

We will implement `/simplify` as a **default-on step with an `--no-simplify` opt-out flag**.

The flag must be:
- Declared in the command's flag-parsing section
- Checked immediately before the Code Simplification step executes
- Documented in CLAUDE.md and `.claude/rules/commands.md` alongside the command

The step is skipped and logged (`"Simplification skipped (--no-simplify)"`) when the flag is present.

**Multi-flag extension (Feature 080)**: Feature 080 added a second opt-out flag, `--no-security`, following the same `--no-X` convention established here. Both flags are fully independent — either or both may be specified in a single invocation (`/aod.build --no-security --no-simplify`). See [ADR-011](ADR-011-multi-flag-opt-out-and-step-insertion-pattern.md) for the multi-flag coexistence pattern and step insertion convention.

---

## Rationale

**Why default-on (not opt-in)**:

1. **Quality intent is primary**: The purpose of integrating `/simplify` is to raise the quality floor for all builds. Opt-in behavior would mean most users never benefit from it.
2. **Discoverability**: Default-on ensures new users encounter the feature immediately; an opt-in flag buried in documentation would be invisible.
3. **Consistent with existing gates**: Other quality gates in `/aod.build` (architect checkpoints, governance reviews) are also default-on. A simplification step follows the same philosophy.

**Why opt-out (not mandatory)**:

1. **Context sensitivity**: Methodology-only repos, CI pipelines, and time-sensitive hotfix builds have legitimate reasons to skip the step. A mandatory step with no escape hatch would make the command unusable in these contexts.
2. **No new dependencies**: The opt-out flag requires zero additional tooling. Users who never need to skip the step are not burdened by its existence.
3. **Precedent**: `--dry-run` (Feature 027) established the pattern of flag-gating steps in commands. `--no-simplify` follows the same convention.

**Why `--no-simplify` (negative flag) rather than `--simplify` (positive flag)**:

Negative flags (`--no-X`) communicate that X is the default. Positive flags (`--X`) communicate that X is optional. Using `--no-simplify` correctly signals to users that simplification is the expected path.

---

## Alternatives Considered

### Alternative 1: Opt-in (`--simplify` flag)

**Pros**:
- No risk of unexpected behavior for users unaware of the step
- Fully deterministic by default in CI contexts

**Cons**:
- Most users would never discover or use the feature
- Contradicts the intent: quality gates should be the norm, not the exception
- Inconsistent with other default-on gates in `/aod.build`

**Why Not Chosen**: Sacrifices the quality intent of the feature. Opt-in is appropriate for experimental or high-risk steps; code simplification is low-risk and broadly beneficial.

### Alternative 2: Mandatory (no flag)

**Pros**:
- Simplest implementation
- Guarantees all builds go through the simplification pass

**Cons**:
- Breaks methodology-only repos where no source code is modified
- Blocks CI pipelines that need deterministic, reproducible output
- No escape hatch for time-sensitive builds where the simplification step would delay delivery

**Why Not Chosen**: Forces a step on contexts where it is inappropriate. A quality gate that cannot be bypassed becomes an obstacle rather than a guardrail.

### Alternative 3: Configuration file (`.aod/config.json`)

**Pros**:
- Persistent opt-out without specifying the flag on each invocation
- Repo-level configuration separate from per-invocation flags

**Cons**:
- Introduces a new configuration surface (`.aod/config.json`) that doesn't exist yet
- Significantly more implementation complexity for a single flag
- Harder to document and discover than a command-line flag

**Why Not Chosen**: Over-engineered for a single boolean preference. If multiple commands accumulate opt-out flags, a config file may become appropriate -- but that decision should be made when the need is demonstrated, not pre-emptively.

---

## Consequences

### Positive
- All `/aod.build` executions include a simplification pass by default, raising quality floor
- Methodology-only repos, CI pipelines, and hotfix builds can skip the step cleanly
- Establishes a documented convention for future default-on quality gate steps
- No new dependencies introduced

### Negative
- Users running `/aod.build` for the first time on a methodology-only repo will encounter a step that does nothing meaningful (until they discover `--no-simplify`)
- Negative flags (`--no-X`) are slightly less discoverable than positive flags in `--help` output

### Mitigation
- The step log message ("Simplification skipped") is clear
- `--no-simplify` is documented at the top level in CLAUDE.md and `commands.md`
- Future commands with opt-out steps should follow the same `--no-X` convention for consistency

---

## Related Decisions

- ADR-002: On-Demand Reference File Segmentation (Feature 030) -- established the pattern of reading built-in skill references only when needed
- [ADR-011: Multi-Flag Opt-Out Pattern and Step Insertion Convention](ADR-011-multi-flag-opt-out-and-step-insertion-pattern.md) -- extends this decision to multiple independent opt-out flags; documents step insertion convention and security-before-simplify ordering rationale
- [Pattern: Built-in Skill Invocation from a Command](../03_patterns/README.md#pattern-built-in-skill-invocation-from-a-command) -- documents the implementation pattern for this decision

---

## References

- Feature 065 Spec: `/specs/065-add-simplify-command/spec.md`
- Feature 065 Plan: `/specs/065-add-simplify-command/plan.md`
- Command file: `.claude/commands/aod.build.md`
- Prior flag pattern: `--dry-run` in `/aod.build` (Feature 027)
