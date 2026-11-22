# Specification Quality Checklist: Large-Architecture Pipeline Resilience

**Purpose**: Validate specification completeness and quality
**Created**: 2026-11-22
**Feature**: [spec.md](../spec.md)

## Content Quality
- [x] No implementation details (languages, frameworks, APIs). *Note:* the spec names file paths, SARIF fields and a Python version floor. For this developer tool those are product contracts that adopters and Code Scanning consume, as in the F-373 precedent. Module layout, algorithms beyond the product rules, and the part-file format are left to `plan.md` and ADR-050 (plan inputs P-1 to P-10).
- [x] Focused on user value and business needs (eight stories, each with a user, a need and a reason).
- [x] Written for non-technical stakeholders. *Note:* tachi's stakeholders are adopters and security leads. Each story says why it matters in their terms; the requirements are necessarily technical.
- [x] All mandatory sections completed (scenarios, requirements, success criteria).

## Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain. Three product choices went to the PM as flagged rulings S-3(d), (f) and (g), not as markers, and the PM amended all three at the spec review.
- [x] Requirements are testable and unambiguous. All 56 FRs link to an acceptance scenario or carry their own. FR-E.8 drops under R-34.
- [x] Success criteria are measurable (SC-1 to SC-9, each with a baseline and a target).
- [x] Success criteria are technology-agnostic. *Note:* SARIF identity (SC-6) is the product surface itself; no criterion depends on how it is implemented.
- [x] All acceptance scenarios are defined (8 stories, 61 scenarios).
- [x] Edge cases are identified (18).
- [x] Scope is clearly bounded (in scope, the R-34 split, the split valves, NG1–NG10, S-16's follow-ups).
- [x] Dependencies and assumptions identified.

## Feature Readiness
- [x] All functional requirements have clear acceptance criteria. Validation pass 1 found seven without (FR-N4.4, FR-E.1, FR-E.5, FR-E.9, FR-E.10, FR-E.13, FR-E.15); each now carries its own scenario.
- [x] User scenarios cover primary flows: the scorer and controls stages, the threat model and report, chains, controls schema, typed dispatch, inheritance, and identity for all three SARIF files.
- [x] Feature meets measurable outcomes defined in Success Criteria (each story maps to SC-1 to SC-8; SC-9 is lagging).
- [x] No implementation details leak into specification (same note as the first item).

## Notes
- **Validation:** five passes (2026-11-22).
  - Pass 1 fixed the seven missing scenarios.
  - Pass 2 found no failing items.
  - Pass 3 followed the PM's review (APPROVED_WITH_CONCERNS, 13 findings). It folded the amended S-3(d), (f) and (g) and findings 1 to 12, adding FR-E.18, US-1a #8, US-6a #7–#9 and one edge case, and marking 13 live scenarios `[MANUAL-ONLY]` inline. It found no failing items. Finding 13 went to the plan (P-11).
  - Pass 4 followed the PM's plan review. It folded rulings A, B, C and P-7, plus findings 4, 6 and 8's spec half. That added FR-E.19 and FR-E.20 (56 FRs) and US-5 #13–#14, US-6a #10–#11 and US-6b #5 (61 scenarios). It found no failing items.
  - Pass 5 followed ADR-050 rev. 1, the Architect's re-review and the PM's confirmation of rev. 1's dispositions (CONFIRMED_WITH_AMENDMENTS). It aligned NFR-1's oracle (four classes, with the reference-set class bounded), NFR-10's ID allow-list (ASCII digits, whole-string match, KB 24), P-1 and Key Artifacts (ADR-026 amended, ADR-047 unchanged), the Flags glossary (`retagged`'s scope; the `input` kind, including truncation), PR 1's release-note item 3 and both PRs' fallback notes. It recorded the confirmation, including the 25% return to the PM, under the plan-review rulings. The counts are unchanged (56 FRs, 61 scenarios), and it found no failing items.
- **Public hygiene (NFR-6):** a scan of `spec.md` and `research.md` found no real-world target names, no local paths and no N3 specifics.
- Items marked incomplete would require spec updates before `/aod.clarify` or `/aod.project-plan`; none are.
