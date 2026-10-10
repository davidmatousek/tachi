# Specification Quality Checklist: Adopter Install + Output Fidelity Fixes

**Purpose**: Validate specification completeness and quality
**Created**: 2026-09-27
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
  - *Note*: file paths, flag names, regexes, API field names and model IDs appear because they are the subject matter of this defect bundle. The repo is the product surface, and the PRD's altitude sets the same. The precedents are specs 281 and 362. The spec selects no new technology. The width algorithm (FR-K11.5) is the PRD's D-2 data contract. The *how-to-build* (code structure, test layout, YAML shape) is deferred to `plan.md`, and seven plan inputs are registered explicitly.
- [x] Focused on user value and business needs: adopter install completeness and safety, report fidelity for security leads, and a working render path.
- [x] Written for the relevant stakeholders. The audience (adopters, security leads, maintainers) is technical by nature. User value is stated in plain language per story, and FR precision is required for a governed defect bundle.
- [x] All mandatory sections completed (User Scenarios & Testing, Requirements, Success Criteria).

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain (0). Plan-stage decisions (P-1, P-2, P-4 reopened, the funnel constants and numeric semantics, splitter hardening, the release-notes mechanism, where the tool provisioning lives, OQ-5, K14 timing) are registered as plan and tasks inputs, not ambiguities.
- [x] Requirements are testable and unambiguous. Every FR carries a `→ US-x #y` mapping to Given/When/Then scenarios. Non-automatable scenarios are marked `[MANUAL-ONLY]` with reasons (US-4a #5, US-4b #4).
- [x] Success criteria are measurable (SC-1 to SC-8, each with a baseline and a target).
- [~] Success criteria are technology-agnostic
  - *Note*: SC-3, SC-5 and SC-6 name the installer flag, the render path and the release mechanism, because those are the feature's substance. They stay outcome-framed: 0 files written, 6/6 renders, notices in the published notes. They don't prescribe a solution.
- [x] All acceptance scenarios are defined: US-1 ×4, US-2 ×12, US-3a ×11, US-3b ×10, US-3c ×5, US-4a ×5, US-4b ×4, US-5 ×9, US-6 ×3 (63 in total).
- [x] Edge cases are identified: 11 installer, 12 extraction, 5 render-path, 1 bundle.
- [x] Scope is clearly bounded: in scope, the split valve (TW-0 to TW-7, decided mechanically at `/aod.tasks` and during the build), and out of scope (NG1–NG9 plus four named follow-up candidates).
- [x] Dependencies and assumptions identified: #374, #370, #364 (with a handoff comment), #365, the delivered foundations and GA model availability; seven assumptions, including the API schema and the GNU userland.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria. All 44 FRs (FR-K1.1 to FR-370.2) map to scenarios, with 1:1 PRD traceability kept and spec additions marked *(spec …)* or *(carry-forward …)*.
- [x] User scenarios cover primary flows: installing, refusing and opting in; each extraction surface; rendering and hardening; drift detection; the #370 guard.
- [x] Feature meets measurable outcomes defined in Success Criteria (SC-1 to SC-8, traced to the stories).
- [x] No implementation details leak into the specification beyond intrinsic subject-matter references (per the Content Quality note).

## Notes

- **Research corrected three PRD premises**, each resolved inside the PRD's goals by a spec ruling (research.md, "PRD Corrections"):
  - the configured image models are retired or retiring (S-8);
  - no code reads the templates' configuration blocks (FR-K14.2);
  - BSD `cp` can't write through nested links (S-6).
- **Spec rulings S-1 to S-13** are listed with their basis in spec.md § Rulings. Four answer questions the PRD left open (S-1 to S-5 cover OQ-1, L-N2, FR-K13.1, L-N4 and L-N3). The rest respond to research findings.
- The architect's v1.2 carry-forwards (M-N1, M-N2, L-N1 to L-N6) each appear as an FR or an acceptance case. L-N6 is restated, because no inline fallback exists. L-N7 was a PRD-text fix, already applied in v1.2.
- Validation result: **PASS** on the first iteration. There are no blocking items. One item is annotated `[~]` because a CI/installer/render feature necessarily names its own subject matter; it is flagged openly.
- **PM review (2026-09-27): APPROVED_WITH_CONCERNS.** Required changes RC-1 to RC-8 are folded into spec.md:
  - RC-1: a DoD pointer, plus SC-6's M5 release-note bullet;
  - RC-2: K14 doesn't bend the cut line;
  - RC-3: the non-blocking HTTP 400 row;
  - RC-4: the verification methods in the AC rule;
  - RC-5: MUST NOT;
  - RC-6: 7 files;
  - RC-7: the detection failure mode;
  - RC-8: the D-1 note names the always-refused links.

  Recommendations R-a, R-c to R-g and PM rulings P-9.1 to P-9.5 are also recorded. The PM verifies the fold at the `/aod.project-plan` sign-off. Review: `.aod/results/product-manager-373-spec.md`.
