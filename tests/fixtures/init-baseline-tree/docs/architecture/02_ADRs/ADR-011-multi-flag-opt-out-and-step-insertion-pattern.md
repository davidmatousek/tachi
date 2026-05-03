# ADR-011: Multi-Flag Opt-Out Pattern and Step Insertion Convention for /aod.build

**Status**: Accepted
**Date**: 2026-03-06
**Deciders**: Architect, Feature 080 Implementation Team
**Feature**: 080 - SAST/SCA Security Review Skill

---

## Context

Feature 080 integrates a security scan step (`/security` skill) into `/aod.build` as Step 6, positioned between Final Validation (Step 5) and Code Simplification (Step 7). This is the second default-on quality gate added to the command (the first being `/simplify` via Feature 065, which established ADR-008).

Two architectural questions arise:

1. **Multi-flag coexistence**: With two opt-out flags (`--no-security` and `--no-simplify`) now present, how should multiple flags coexist? Should they interact or remain independent?

2. **Step insertion convention**: When a new step is inserted between existing numbered steps, how should existing step numbers be managed? This affects all documentation, ADRs, and cross-references throughout the codebase.

3. **Step ordering**: Should the security scan run before or after code simplification?

4. **Cross-reference stability**: Ordinal step numbers (`Step 6`, `Step 7`) change as new steps are inserted. How should internal references remain stable across future insertions?

---

## Decision

### 1. Multi-Flag Independence

Each opt-out flag controls **only its own step**. Flags are fully independent and may coexist in a single invocation:

```
/aod.build --no-security --no-simplify
```

Both flags are parsed in Step 0 sequentially (0a: `--no-simplify`, 0b: `--no-security`). Each sets its own boolean variable (`skip_simplify`, `skip_security`). Neither flag affects the other's step.

This is the **multi-flag opt-out pattern**: each new default-on step added to `/aod.build` receives its own `--no-X` flag, and all flags are independent.

### 2. Security-Before-Simplify Step Ordering

The security scan (Step 6) runs **before** code simplification (Step 7).

Rationale: scanning code before it is simplified captures issues at their source, in the form the developer wrote them. If simplification ran first and restructured code, the security scan would analyze the simplified form — potentially obscuring original vulnerability patterns or producing findings against reformatted code that is harder to trace back to the developer's intent.

### 3. Step Insertion Convention

When inserting a new step between existing numbered steps, **renumber all downstream steps** rather than using fractional numbers (e.g., `Step 6.5`). All documentation, ADRs, patterns, and closure summaries that reference step numbers must be updated at insertion time.

This is a **breaking change to step ordinals** — accepted as the lesser cost compared to maintaining non-sequential or fractional numbering indefinitely.

### 4. Named Stage Identifier Recommendation

For **internal cross-references within `aod.build.md`** (e.g., "Proceed to Step N"), use the step number at time of writing but acknowledge that these will require updating on future insertions.

For **external documentation** (ADRs, patterns, closure summaries), prefer descriptive stage names over ordinal numbers where possible:
- "Security Scan step" rather than "Step 6"
- "Code Simplification step" rather than "Step 7"
- "Final Validation step" rather than "Step 5"

This reduces the blast radius of future step insertions on external documentation.

---

## Rationale

### Why fully independent flags (not flag groups or mutual exclusion)?

1. **Orthogonality**: Security scanning and code simplification serve entirely different purposes. A user may have legitimate reasons to skip either one independently — e.g., skip security on a documentation-only change, skip simplify on a hotfix with time pressure. Coupling them would remove valid use cases.

2. **Precedent**: ADR-008 established the `--no-X` convention for default-on steps. Extending it to a second flag follows the same pattern with zero new concepts.

3. **Discoverability**: Users who learn `--no-simplify` will immediately understand `--no-security`. Consistent naming and behavior reduces cognitive load.

### Why security before simplification?

1. **Scan dirty code**: Simplification may refactor variable names, inline expressions, or restructure conditionals. Scanning post-simplification means the analyzer sees code the developer did not write. Scanning pre-simplification preserves traceability: finding at `file.py:42` matches the developer's own line 42.

2. **No double-scan needed**: If the scan runs first and passes, simplification can proceed freely. If the scan finds issues, the developer fixes them before simplification — avoiding a wasted simplification pass on code that will change again.

3. **Consistent with security-first philosophy**: Security review gates should occur as early as reasonable in the quality pipeline.

### Why renumber rather than fractional steps?

1. **Readability**: `Step 6`, `Step 7`, `Step 8` is clearer than `Step 5.5`, `Step 6`, `Step 7` for users reading the command file.

2. **Tooling compatibility**: Some downstream tooling (e.g., progress reporting in `aod.build` output) references step numbers numerically. Fractional numbers complicate parsing.

3. **Finite insertion frequency**: Quality gate steps are added infrequently (Feature 065 in 2026-03-03, Feature 080 in 2026-03-06). The documentation update cost is manageable.

---

## Alternatives Considered

### Alternative 1: Combined opt-out flag (`--no-quality-gates`)

**Pros**:
- Single flag skips both security and simplification
- Simpler flag surface for CI pipelines that want to skip all quality gates

**Cons**:
- Sacrifices granularity: a user who wants security but not simplification (or vice versa) cannot express that preference
- Inconsistent with established `--no-X` per-step convention (ADR-008)
- Forces future quality gates into the same group, even if they have different skip rationales

**Why Not Chosen**: Granularity is worth the cost of a second flag. The per-step convention is already established and consistent.

### Alternative 2: Configuration file for step enablement (`.aod/build-config.json`)

**Pros**:
- Persistent configuration without per-invocation flags
- Repo-level settings for teams with consistent skip requirements

**Cons**:
- New configuration surface not yet established
- Over-engineered for two boolean flags
- Harder to override in CI environments that cannot modify files

**Why Not Chosen**: Deferred per ADR-008. If flag count grows beyond 3–4, revisit configuration file approach.

### Alternative 3: Fractional step numbering (insert as `Step 5.5`)

**Pros**:
- No renumbering of downstream steps
- External documentation references remain valid without updates

**Cons**:
- Non-idiomatic and hard to read
- Breaks sequential numbering assumption in progress reporting
- `Step 5.5` between `Step 5` and `Step 6` is visually confusing

**Why Not Chosen**: The documentation update cost of renumbering is lower than the ongoing confusion of fractional step numbers.

### Alternative 4: Security scan after simplification

**Pros**:
- Scans the "final" form of code that will be committed

**Cons**:
- If findings require fixes, the simplification pass is wasted
- Traceability issue: findings at simplified line numbers don't match developer's original code
- Counter to security-first philosophy

**Why Not Chosen**: Security should gate simplification, not follow it.

---

## Consequences

### Positive
- All `/aod.build` executions include a security scan and simplification pass by default, maximizing quality floor
- Both steps independently skippable for contexts where one or both are inappropriate
- Security scan runs on original developer code (maximum traceability)
- Consistent `--no-X` flag convention across all opt-out steps
- Named stage identifiers in external docs reduce future renumbering blast radius

### Negative
- Two flags to remember instead of one (mitigated by consistent naming pattern)
- Future step insertions still require step-number updates in some documentation (mitigated by named-identifier recommendation)
- Step 7 and Step 8 references in documentation became stale at Feature 080 insertion (updated as part of this feature)

### Mitigation
- `--no-security` and `--no-simplify` documented prominently in `CLAUDE.md` and `.claude/rules/commands.md`
- Named stage identifiers used in all new documentation going forward
- This ADR serves as the canonical reference for future quality gate insertions

---

## Related Decisions

- [ADR-008: Opt-out Flag for Default-On Quality Gate Steps in Commands](ADR-008-opt-out-flag-for-default-quality-gates.md) — established the `--no-X` per-step convention that this ADR extends to multiple flags
- [Pattern: Built-in Skill Invocation from a Command](../03_patterns/README.md#pattern-built-in-skill-invocation-from-a-command) — documents the implementation pattern for wiring built-in skills into commands with opt-out flags

---

## References

- Feature 080 Spec: `specs/080-sast-sca-security/spec.md`
- Feature 080 Plan: `specs/080-sast-sca-security/plan.md`
- Security skill: `.claude/skills/security/SKILL.md`
- Command file: `.claude/commands/aod.build.md`
- ADR-008 (first opt-out flag decision): `docs/architecture/02_ADRs/ADR-008-opt-out-flag-for-default-quality-gates.md`
