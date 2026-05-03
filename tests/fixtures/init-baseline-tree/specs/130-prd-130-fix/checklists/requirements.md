# Specification Quality Checklist: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

**Purpose**: Validate specification completeness and quality
**Created**: 2026-04-11
**Feature**: [spec.md](../spec.md)

## Content Quality
- [x] No implementation details (languages, frameworks, APIs)
  - Note: File paths and line numbers are referenced for traceability to the PRD and parent spec 112. This is not "implementation detail" in the sense the checklist means — it is citation of existing code that must be modified. The spec does not prescribe *how* the preflight gate is implemented; that is left to Plan Stage per the explicit assumption block.
- [x] Focused on user value and business needs (fresh-install experience, loud-failure contract, board-ready PDFs)
- [x] Written for non-technical stakeholders
  - Note: Some FRs cite file paths because the feature is a bug fix with precise scope. The user stories and success criteria are stakeholder-readable.
- [x] All mandatory sections completed (User Scenarios, Requirements, Success Criteria)

## Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (loud-failure rate, rendered-output rate, baseline byte-determinism)
- [x] Success criteria are technology-agnostic (SC-130.1 through SC-130.6 describe outcomes, not implementations)
- [x] All acceptance scenarios are defined (Given/When/Then for each of 3 user stories, 11 total scenarios)
- [x] Edge cases are identified (6 listed: empty attack-trees dir, Low/Medium-only findings, mmdc out of version range, hang, SOURCE_DATE_EPOCH drift, Node.js absent)
- [x] Scope is clearly bounded (in-scope FRs 130.1-130.7; out-of-scope list of 7 items)
- [x] Dependencies and assumptions identified (Internal: 054, 112, 128; External: @mermaid-js/mermaid-cli; 6 Assumptions)

## Feature Readiness
- [x] All functional requirements have clear acceptance criteria (FR ↔ US ↔ SC traceable)
- [x] User scenarios cover primary flows (preflight missing, happy path, mid-render failure, doc posture)
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification
  - Exception with rationale: FR-130.1 references `shutil.which` as the signal mechanism because the PRD pinned this. FR-130.2, FR-130.3, FR-130.5, FR-130.6, FR-130.7 cite file paths and line numbers because the feature's entire scope is "modify these specific files." This is a bug fix on a known corpus, not greenfield design. The spec explicitly defers *mechanism* decisions (where preflight lives, how mid-render failure is surfaced, install.sh consistency strategy, CI infra) to Plan Stage.

## Traceability

| PRD item | Spec mapping |
|---|---|
| US-130.1 | Spec US-1 (P1) |
| US-130.2 | Spec US-2 (P1) |
| US-130.3 | Spec US-3 (P1) |
| FR-130.1 preflight gate | Spec FR-130.1 |
| FR-130.2 extract-report-data refactor | Spec FR-130.2 |
| FR-130.3 delete Typst branch | Spec FR-130.3 |
| FR-130.4 loud mid-render failure | Spec FR-130.4 |
| FR-130.5 docs sync (5 files) | Spec FR-130.5 (6 files — adds Tech Stack doc) |
| FR-130.6 example regeneration | Spec FR-130.6 (with PRD correction for attack-tree-bearing examples) |
| FR-130.7 CI fresh-install test | Spec FR-130.7 |
| SC-130.1 through SC-130.5 | Spec SC-130.1 through SC-130.6 (adds SC-130.6 for code-removal grep) |
| Plan Day 0 spike S1/S2/S3 | Spec Assumption #4 |

## PRD Deviations Documented in Spec

1. **Attack-tree-bearing examples corrected**: PRD named `examples/web-app/`; research found only `examples/agentic-app/sample-report/` and `examples/mermaid-agentic-app/` have attack trees. Spec FR-130.6 uses the correct examples and documents the deviation inline.
2. **Added Tech Stack doc to docs-sync list**: PRD's FR-130.5 missed `docs/architecture/00_Tech_Stack/README.md` line 279 (the optional-mmdc description). Spec FR-130.5 adds it for corpus consistency.
3. **Added SC-130.6**: PRD's success criteria did not include a grep-verified assertion that deleted code is actually deleted. Spec adds SC-130.6 so code review can verify FR-130.2 and FR-130.3 are fully applied.
4. **Spec 112 line 80 contains the pymmdc error**: Research confirmed the exact text at line 80 is `- Pure Python alternative: \`pymmdc\` package (no Node.js dependency)`. The PRD stated the same; no deviation, just verified.

## Notes
- Items marked incomplete require spec updates before `/aod.clarify` or `/aod.project-plan`
- All items currently pass on first validation pass
- Spec is ready for PM sign-off review
