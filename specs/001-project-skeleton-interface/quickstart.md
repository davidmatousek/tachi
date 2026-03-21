# Implementation Quickstart: F-001 Project Skeleton & Interface Contract

## Before You Start

- Branch: `001-project-skeleton-interface`
- All deliverables are markdown + YAML — no runtime code
- Follow knowledge system naming: PascalCase for directories/config, kebab-case for agent/content files
- Reference `schemas/finding.yaml` as the canonical IR contract from agent files

## Implementation Order

### Phase 1: Foundation (Schemas + Config)
1. Create `schemas/` directory and `README.md`
2. Write `schemas/finding.yaml` — the IR contract (11 fields with types and allowed values)
3. Write `schemas/input.yaml` — input validation (5 formats with recognition patterns)
4. Write `schemas/output.yaml` — output structure (7 sections matching template)
5. Update `adapters/ContextLoading.yaml` — correct 7 scaffold paths
6. Update `adapters/ProjectMeta.yaml` — populate tachi metadata
7. Update `adapters/ScoringRubric.md` — add OWASP 3x3 dimensions
8. Create `LICENSE` — Apache 2.0

### Phase 2: Agent Files (Hub Content)
9. Create 6 STRIDE agents in `agents/stride/` using standard frontmatter format
10. Create 5 AI agents in `agents/ai/` using standard frontmatter format
11. Update `agents/ai/README.md` with 5-agent-to-2-table mapping
12. Create `agents/orchestrator.md` placeholder

### Phase 3: Core Documents
13. Write `docs/INTERFACE-CONTRACT.md` — all 7 sections
14. Write `templates/threats.md` — all 7 output sections with field descriptions and examples

### Phase 4: Examples + Root
15. Create `examples/ascii-web-api/` with `input.md` and `threats.md`
16. Create `examples/mermaid-agentic-app/` with `input.md` and `threats.md`
17. Create `examples/free-text-microservice/` with `input.md` and `threats.md`
18. Update root `README.md` with quickstart

## Key References

- IR Schema: See `contracts/finding-ir.md` for field definitions
- Input Formats: See `contracts/input-format.md` for recognition patterns
- Output Structure: See `contracts/output-schema.md` for section definitions
- PRD: `docs/product/02_PRD/001-project-skeleton-interface-contract-2026-03-21.md`
- Spec: `specs/001-project-skeleton-interface/spec.md`

## Validation Checklist

After implementation, verify:
- [ ] All paths in `ContextLoading.yaml` resolve to existing files
- [ ] All agent files have correct frontmatter with `output_schema: schemas/finding.yaml`
- [ ] `templates/threats.md` has all 7 sections with field descriptions and examples
- [ ] All 3 example `threats.md` files follow the template structure
- [ ] Every top-level directory has a README.md
- [ ] `schemas/finding.yaml` defines all 11 fields with types and allowed values
