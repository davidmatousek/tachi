# ADR-009: Expanding tachi Template Variable to All User-Facing Template Files

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: Architect, Feature 061 Implementation Team
**Feature**: 061 - init.sh Personalize All Template Files

---

## Context

`tachi` is a template variable that `scripts/init.sh` replaces with the adopter's actual project name at `make init` time via `sed`. Before Feature 061, this variable was used only in `.aod/memory/constitution.md`.

Eleven additional files contained the hardcoded string "Agentic Oriented Development Kit" (or its abbreviation), which caused two problems:

1. **Adopter confusion**: Files presented as templates for the adopter's project still showed the kit's own name instead of the adopter's project name.
2. **Copy-paste friction**: Adopters had to manually find and replace the kit name in every file they referenced or shared.

The affected files were all user-facing template files: `CLAUDE.md`, `README.md`, `.claude/README.md`, `.claude/agents/_README.md`, six `.claude/rules/*.md` files, and `docs/product/02_PRD/INDEX.md`.

---

## Decision

We will expand `tachi` placeholder usage from `constitution.md` alone to all 11 user-facing template files. The `scripts/init.sh` personalization loop already processes these files; no new infrastructure was needed -- only the placeholder was added to each file's content.

No new code was written. No new dependencies were introduced. No infrastructure was changed.

---

## Rationale

1. **Consistency**: `constitution.md` already established `tachi` as the project name placeholder. Extending to all template files follows the same convention rather than introducing a second approach.

2. **Zero implementation cost**: `init.sh` already iterates template files for other substitutions. Adding `tachi` to file content required only editing the files themselves.

3. **Adopter experience**: A template that still shows "Agentic Oriented Development Kit" after `make init` is confusing. Personalization should be thorough, not partial.

4. **Minimal blast radius**: `tachi` is a safe placeholder -- it has no meaning outside the kit's init workflow and will never appear in adopter output after `make init` runs.

---

## Alternatives Considered

### Alternative 1: Keep hardcoded kit name in template files

**Pros**:
- No change needed

**Cons**:
- Adopter-facing files always show the wrong project name
- Violates the intent of the template (deliver a personalized starting point)

**Why Not Chosen**: The problem is real and the fix is zero-cost.

### Alternative 2: Use a different placeholder (e.g., `YOUR_PROJECT_NAME`)

**Pros**:
- More readable to humans inspecting template files before init

**Cons**:
- Inconsistent with the established `{{VARIABLE}}` double-brace convention already used in `constitution.md` and other template variables (`2026-03-21`, `{{TEMPLATE_VARIABLES}}`)
- Would require a second sed pattern in `init.sh`

**Why Not Chosen**: Consistency with the existing convention is more important than readability of pre-init files.

### Alternative 3: Post-init cleanup script (separate step)

**Pros**:
- Could handle more complex replacements

**Cons**:
- Adds a step adopters might miss
- `init.sh` already handles the replacement; a separate script is unnecessary complexity

**Why Not Chosen**: Over-engineered for a simple text substitution.

---

## Consequences

### Positive
- After `make init`, all 11 template files display the adopter's project name instead of "Agentic Oriented Development Kit"
- Consistent `tachi` convention across all template files
- No adopter-visible regressions -- the change only affects pre-init file content

### Negative
- Contributors reading template files before init must understand that `tachi` is a placeholder, not a missing value
- Any future template file added to the kit must remember to use `tachi` instead of the kit name

### Mitigation
- `docs/architecture/00_Tech_Stack/README.md` documents `tachi` as a first-class template variable
- The [Template Variable Expansion pattern](../03_patterns/README.md#pattern-template-variable-expansion) documents when and how to use placeholders in new template files

---

## Related Decisions

- No prior ADR -- this is the first formal decision about template variable scope

---

## References

- Feature 061 Spec: `specs/061-init-personalize-all/spec.md`
- Feature 061 PRD: `docs/product/02_PRD/061-init-personalize-all-template-files-2026-03-03.md`
- Init script: `scripts/init.sh`
- Constitution (first use of placeholder): `.aod/memory/constitution.md`
