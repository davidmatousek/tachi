---
name: Feature Request (maintainer-promoted only)
about: For features already discussed and promoted from a Discussion. Community feature requests go to Discussions first.
labels: enhancement, stage:discover
---

> **Not a maintainer or promoting from a Discussion?**
> Feature requests start as [Discussions](https://github.com/pratik-saptarshi/tachi-rust/discussions/categories/feature-requests), not Issues. Post your proposal there — I promote threads to Issues once they have traction and an ICE score. See [CONTRIBUTING.md](../../CONTRIBUTING.md#how-feature-requests-become-work) for the lifecycle.

## Source Discussion

<!-- Link to the Discussion this Issue was promoted from. -->
Promoted from: #NNN

## Problem Statement

A clear description of the problem or need this feature addresses.

## Proposed Solution

Describe the solution. Reference the Discussion for community context and alternatives already raised.

## ICE Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Impact    | N     | |
| Confidence| N     | |
| Effort    | N     | |
| **Total** | **N** | |

## Triad Impact

Which Triad roles does this feature affect?

- [ ] PM — scope, requirements, product workflows
- [ ] Architect — technical decisions, system design, constraints
- [ ] Team-Lead — timeline, assignments, execution workflows

## Taxonomy Attribution (if applicable)

- OWASP: [LLM / Agentic / Web / API / Mobile / ML item IDs]
- MITRE: [ATT&CK / ATLAS technique IDs]
- NIST AI RMF: [AI 600-1 subcategories]
- CWE: [CWE IDs]

## Additional Context

Mockups, related ADRs, blueprint links, prior art.

## TDD Acceptance Evidence

Maintainers should complete this section before implementation.

- Failing test first:
- Exact validation gate:
- Positive case:
- Negative/adversarial case:
- Property/golden/mutation applicability:

---

## Next Step (for contributors)

This Issue captures discovery context. To pick it up via tachi's AOD lifecycle (replace `<NNN>` with this Issue's number after creation):

1. **Re-score** (if priority needs validation against current strategy): `/aod.score <NNN>`
2. **Promote to PRD**: `/aod.define <NNN>` — generates `docs/product/02_PRD/<NNN>-*.md` with Triad sign-offs (PM + Architect + Team-Lead)
3. **Plan**: `/aod.plan` — chains spec → project-plan → tasks
4. **Build**: `/aod.build` — implements per the plan with quality gates
5. **Deliver**: `/aod.deliver <NNN>` — closure + retrospective

External contributors: see [docs/AOD_TRIAD.md](docs/AOD_TRIAD.md) for governance overview, or jump straight to `/aod.define <NNN>` if scope is already clear from this Issue body.
