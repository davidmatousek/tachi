# Agent Assignments: Example Threat Models (Feature 024)

**Generated**: 2026-03-23
**Tasks**: 50 total
**Timeline**: ~2.5 days (4 waves)

## Agent Assignment Matrix

| Task Range | Agent | Rationale |
|------------|-------|-----------|
| T001–T003 (Setup) | `senior-backend-engineer` | Directory creation, file scaffolding |
| T004 (Web-app diagram) | `senior-backend-engineer` | Mermaid markdown authoring |
| T005–T014 (Web-app threats) | `senior-backend-engineer` | Schema v1.1 compliant content authoring |
| T015 (Agentic-app diagram) | `senior-backend-engineer` | Mermaid markdown with AI dispatch keywords |
| T016–T025 (Agentic-app threats) | `senior-backend-engineer` | Schema v1.1 + AI findings + correlations |
| T026 (Microservices diagram) | `senior-backend-engineer` | Mermaid markdown multi-service topology |
| T027–T036 (Microservices threats) | `senior-backend-engineer` | Schema v1.1 cross-service analysis |
| T037–T040 (Examples README) | `senior-backend-engineer` | Documentation with Mermaid framework hierarchy |
| T041 (Project README) | `senior-backend-engineer` | Documentation update |
| T042–T046 (Schema validation) | `tester` | Schema compliance, risk matrix consistency |
| T047–T048 (OWASP validation) | `tester` | Cross-reference accuracy verification |
| T049 (Existing examples check) | `tester` | Integrity verification |
| T050 (Quickstart validation) | `tester` | File path existence check |

## Parallel Execution Waves

### Wave 1: Setup + Architecture Diagrams (0.5 days)

| Parallel Track | Tasks | Agent |
|----------------|-------|-------|
| Track A | T001, T004 | `senior-backend-engineer` |
| Track B | T002, T015 | `senior-backend-engineer` |
| Track C | T003, T026 | `senior-backend-engineer` |

**Quality Gate**: All 3 directories exist, all 3 Mermaid diagrams render in GitHub.

### Wave 2: Threat Model Authoring (1–1.5 days)

| Parallel Track | Tasks | Agent |
|----------------|-------|-------|
| Track A | T005–T014 (web-app) | `senior-backend-engineer` |
| Track B | T016–T025 (agentic-app) | `senior-backend-engineer` |
| Track C | T027–T036 (microservices) | `senior-backend-engineer` |

**Quality Gate**: All 3 `threats.md` files have schema v1.1 frontmatter and all 8 sections.

### Wave 3: Documentation (0.5 days)

| Sequential Track | Tasks | Agent |
|-------------------|-------|-------|
| Step 1 | T037–T040 (examples README) | `senior-backend-engineer` |
| Step 2 | T041 (project README) | `senior-backend-engineer` |

**Quality Gate**: READMEs link correctly to all examples.

### Wave 4: Validation (0.5 days)

| Parallel Track | Tasks | Agent |
|----------------|-------|-------|
| Track A | T042–T046 (schema + risk) | `tester` |
| Track B | T047–T050 (OWASP + integrity) | `tester` |

**Quality Gate**: All validation tasks pass. Zero schema or OWASP cross-reference errors.

## Time Estimates

| Wave | Duration | Agents Active | Blocking? |
|------|----------|---------------|-----------|
| Wave 1 | 0.5 days | 3 parallel tracks | No — start immediately |
| Wave 2 | 1–1.5 days | 3 parallel tracks | Depends on Wave 1 |
| Wave 3 | 0.5 days | 1 sequential track | Depends on Wave 2 |
| Wave 4 | 0.5 days | 2 parallel tracks | Depends on Wave 3 |
| **Total** | **~2.5 days** | | |

## Critical Path

```
Wave 1 (any track) → Wave 2 (same track) → Wave 3 → Wave 4
```

The critical path runs through the longest Wave 2 track (agentic-app, most complex due to AI findings + correlations) then through Wave 3 (sequential) and Wave 4.

## Notes

- All content authoring uses `senior-backend-engineer` as the fallback for markdown/documentation work
- Validation uses `tester` for schema compliance and accuracy verification
- 3 parallel tracks in Waves 1–2 maximize throughput
- Wave 3 is sequential because the project README depends on the examples README
