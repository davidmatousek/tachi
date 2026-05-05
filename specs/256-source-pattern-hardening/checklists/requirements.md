# Specification Quality Checklist: F-2 Source-Pattern Hardening

**Purpose**: Validate specification completeness and quality
**Created**: 2026-05-04
**Feature**: [spec.md](../spec.md)
**PRD**: [256-source-pattern-hardening-2026-05-04.md](../../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — spec describes WHAT, not HOW; bash 3.2 noted as a constraint, not implementation prescription
- [x] Focused on user value and business needs — 8 user stories cover adopters (US-1, US-3, US-4, US-8), maintainers (US-2, US-7), security reviewers (US-5), enterprise architects (US-6)
- [x] Written for non-technical stakeholders — user stories use plain language; technical detail confined to FRs/NFRs/ACs
- [x] All mandatory sections completed — User Scenarios, Edge Cases, Requirements, Key Entities, Success Criteria, Dependencies, Risks, References

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — PRD is fully adjudicated (Q-1 through Q-6 resolved); spec inherits all decisions
- [x] Requirements are testable and unambiguous — every FR has explicit ACs; ACs use Given/When/Then structure
- [x] Success criteria are measurable — SC-001 through SC-015 all have verifiable conditions
- [x] Success criteria are technology-agnostic — SCs name behaviors and exit codes, not specific implementations (bash 3.2 noted as constraint, not prescription)
- [x] All acceptance scenarios are defined — 9 FRs × ≥3 ACs each = 30+ ACs total
- [x] Edge cases are identified — 14 edge cases enumerated covering trailing-newline / CRLF / leading-whitespace / bare-empty-value / bash-3.2 / watchdog-leak / fast-clone / F-1 amendment ripple / perf / `/security` re-scan / release-please variance
- [x] Scope is clearly bounded — Out-of-Scope section lists F-1 (already shipped), F-3/F-4/F-5 (Wave 3+4 deferred), `finding.yaml` schema (preserved), JSON/TOML/YAML alternatives (rejected in ADR-040)
- [x] Dependencies and assumptions identified — Dependencies section lists F-1, F-1 prompt amendment, canonical placeholder array, per-field validators, sibling libraries, pytest CI matrix, F-2 reuse contract; Assumptions section covers bash 3.2 lower-bound, LinkedIn durability, release-please cadence, no-non-KV-bash adopter case, lockstep contract evolution, hanging-listener determinism, AOD_FETCH_TIMEOUT name uniqueness

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria — FR-001 through FR-009 all have AC-N.M sub-criteria
- [x] User scenarios cover primary flows — 8 user stories cover the four call sites + clone timeout + maintenance + audit + enterprise + TOCTOU
- [x] Feature meets measurable outcomes defined in Success Criteria — SC-001 (5 vuln_id closure) is the primary outcome; SC-002 through SC-015 cover correctness, adversarial-input rejection, clone-timeout, performance, ADR/governance/release, cross-cutting
- [x] No implementation details leak into specification — implementation details (e.g., the watchdog `& wait kill` pattern, the `${!var}` indirect expansion) appear only in PRD and will appear in plan.md; spec keeps to the contract level (exit codes, error message shapes, behavior preservation)

## Notes

- The spec mirrors F-1's structure for consistency across BLP-02 features (PM, Architect, Team-Lead all reviewed F-1's structure successfully).
- All Q-1 through Q-6 PRD adjudications are folded into the spec (single-PR default + Day-5 conversion lever; whitelist required at sites A and D, optional at site B; `<key_case>` upper/lower only; `AOD_FETCH_TIMEOUT=0` rejected; sibling-file placement; perf threshold ladder; ADR dual-commit pattern).
- Three [MANUAL-ONLY] markers used: AC-5.2 (strace/dtruss platform-specific), AC-8.2/AC-8.3 (post-merge release-please verification by `/aod.deliver` operator), SC-002/Test-7 (post-merge `/security` re-scan by closing operator).
- Items marked incomplete require spec updates before `/aod.clarify` or `/aod.project-plan`. **All items pass** as of 2026-05-04 — spec is ready for PM review.
