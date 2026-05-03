# Delivery Document: Feature 129 — Attack Tree Delta Sub-Agent

**Delivery Date**: 2026-04-14
**Branch**: `129-attack-tree-delta`
**PR**: #162

---

## What Was Delivered

- New leaf agent `tachi-attack-tree-delta` extracts attack tree generation and delta reconciliation from the threat-report agent into a focused sub-agent (single-responsibility decomposition)
- Deterministic dispatch on `delta_counts`: Rule 1 (carry-forward all baseline trees byte-identical), Rule 2 (fresh generate for all Critical/High + per-finding Rule 3 reconciliation for UNCHANGED), no-baseline fallback
- Rule 3 structural similarity algorithm with named constants (LEAF_MATCH_THRESHOLD=0.70, TREE_SIMILARITY_THRESHOLD=0.80, NODE_COUNT_VARIANCE=0.20) — UNCHANGED findings keep baseline tree when token-overlap, gate types, and node count all match within bounds
- `attack_tree_count` definition unified across `schemas/report.yaml`, `templates/tachi/output-schemas/threat-report.md`, and the sub-agent manifest as "total trees produced (fresh + carried-forward)" — reverses the Feature 104 narrow-count interpretation to match developer mental model
- Sub-agent emits standalone `attack-trees/{finding-id}-attack-tree.md` files plus structured `.manifest.json` consumed by parent threat-report for inline Section 5 assembly
- Reference content additions: `attack-tree-construction.md` (Baseline Reconciliation methodology) and `narrative-templates.md` (Section 5 Delta Annotations)

---

## How to See & Test

1. Inspect new sub-agent definition: `cat .claude/agents/tachi/attack-tree-delta.md` — confirm frontmatter (name, description, tools, model) and manifest schema description.
2. Verify threat-report refactor: `git diff main~1 .claude/agents/tachi/threat-report.md` — confirm 56 lines removed (Section 5 generation logic relocated).
3. Verify `attack_tree_count` consistency across the 3 enforcement points:
   - `grep -A 2 attack_tree_count schemas/report.yaml`
   - `grep -A 2 attack_tree_count templates/tachi/output-schemas/threat-report.md`
   - `grep -A 2 attack_tree_count .claude/agents/tachi/attack-tree-delta.md`
4. Confirm Rule 3 named constants present: `grep -E "LEAF_MATCH_THRESHOLD|TREE_SIMILARITY_THRESHOLD|NODE_COUNT_VARIANCE" .claude/skills/tachi-threat-reporting/references/attack-tree-construction.md`
5. Re-run threat report generation on an example with a baseline (Rule 1 path): UNCHANGED findings should produce byte-identical attack tree files vs baseline.
6. Re-run threat report generation on an example with NEW findings (Rule 2 path): all Critical/High get fresh trees; UNCHANGED findings get fresh trees + Rule 3 reconciliation (similar → carry forward; different → annotate as regenerated).
7. Confirm INSTALL_MANIFEST coverage: `grep "attack-tree-delta" INSTALL_MANIFEST.md` shows the new agent is shipped (count bumped 17→18).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | ~1 day (branch created 2026-04-13, merged 2026-04-14) |
| Variance | On-target |

---

## Surprise Log

Smooth sailing — no major surprises. The decomposition fit cleanly inside the existing Phase 5 pipeline shape, and the Triad sign-offs ran without rework.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| N/A | None captured — smooth delivery, no novel learning to codify | N/A (developer override) |

---

## Feedback Loop

**New Ideas**: None

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | `specs/129-attack-tree-delta/spec.md` |
| Implementation Plan | `specs/129-attack-tree-delta/plan.md` |
| Task Breakdown | `specs/129-attack-tree-delta/tasks.md` |
| PRD | `docs/product/02_PRD/129-attack-tree-delta-sub-agent-2026-04-13.md` |
| Security Scan | `specs/129-attack-tree-delta/security-scan.md` |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 (PRD INDEX, PRD frontmatter, BACKLOG.md) | SUCCESS |
| Architecture | architect | 2 (CLAUDE.md, docs/architecture/00_Tech_Stack/README.md) | SUCCESS |
| DevOps | devops | 1 (INSTALL_MANIFEST.md — agent count 17→18) | SUCCESS |

---

## Cleanup

- [x] Feature branch deleted (squash-merged via PR #162)
- [x] All tasks complete (13/13)
- [x] No TBD/TODO in docs
- [x] Committed and pushed
- [x] GitHub Issue closed (`stage:done`)

**Feature 129 is now officially CLOSED.**
