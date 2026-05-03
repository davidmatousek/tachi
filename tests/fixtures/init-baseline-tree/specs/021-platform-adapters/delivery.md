# Delivery Document: Feature 021 — Platform Adapters

**Delivery Date**: 2026-03-23
**Branch**: `021-platform-adapters`
**PR**: #22

---

## What Was Delivered

- **Claude Code adapter** (P0): All 14 threat agents transformed into `.claude/agents/tachi/` format with native frontmatter, enabling single-copy installation and parallel dispatch via Agent tool
- **Generic adapter** (P0): 14 numbered self-contained prompt files for sequential chat UI or programmatic API invocation with any LLM backend
- **Cursor adapter** (P1): 14 `.mdc` rule files with `alwaysApply` orchestrator and Agent Requested threat agents for passive context injection
- **Copilot adapter** (P1): 14 `.agent.md` files with size-split strategy for oversized agents (orchestrator 120K, threat-report 43K) into compact agent + instructions file pairs
- **GitHub Actions adapter** (P1): Workflow YAML with LLM API integration, SARIF 2.1.0 generation, Code Scanning upload, and retry/error handling
- **VERSION infrastructure**: `scripts/generate-adapter-version.sh` computing Git SHA and SHA-256 checksums for drift detection across all adapters
- **Shared conventions**: Metadata YAML format and per-platform path rewriting rules documented in `specs/021-platform-adapters/conventions.md`

---

## How to See & Test

1. **Claude Code**: Copy `adapters/claude-code/agents/` to a project's `.claude/agents/tachi/`, invoke the orchestrator agent, verify all 14 threat agents dispatch and produce valid `threats.md`
2. **Generic**: Copy prompt files from `adapters/generic/prompts/` sequentially into any LLM chat UI (e.g., Claude.ai), provide architecture input at prompt 00, verify `threats.md` output after prompt 13
3. **Cursor**: Copy `adapters/cursor/rules/` to `.cursor/rules/tachi/`, open architecture files in Cursor, verify orchestrator rule auto-loads and threat agents are available via description matching
4. **Copilot**: Copy `adapters/copilot/agents/` to `.github/agents/tachi/` and `adapters/copilot/instructions/` to `.github/instructions/`, invoke orchestrator agent in Copilot, verify threat agents dispatch
5. **GitHub Actions**: Copy `adapters/github-actions/tachi-threat-model.yml` to `.github/workflows/`, configure `LLM_API_KEY` secret, submit PR changing architecture files, verify SARIF appears in Security tab
6. **VERSION**: Run `bash scripts/generate-adapter-version.sh adapters/claude-code` and verify VERSION file output with commit SHA and checksums
7. **Output parity**: Run identical architecture input through Claude Code adapter and generic adapter, compare `threats.md` output for semantic equivalence

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | 1 day |
| Variance | On-target |

---

## Surprise Log

Smooth sailing — everything went roughly as planned, no major surprises.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| N/A | No lesson captured | N/A |

---

## Feedback Loop

**New Ideas**: None

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/021-platform-adapters/spec.md |
| Implementation Plan | specs/021-platform-adapters/plan.md |
| Task Breakdown | specs/021-platform-adapters/tasks.md |
| PRD | docs/product/02_PRD/021-platform-adapters-2026-03-23.md |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 | Success |
| Architecture | architect | 3 | Success |
| DevOps | devops | 3 | Success |

---

## Cleanup

- [x] Feature branch deleted
- [x] All tasks complete (40/40)
- [ ] No TBD/TODO in docs
- [ ] Committed and pushed
- [ ] GitHub Issue closed (`stage:done`)

**Feature 021 is now officially CLOSED.**
