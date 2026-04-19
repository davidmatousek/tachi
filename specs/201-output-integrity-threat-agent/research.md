# Research Summary: `output-integrity` Threat Agent

**Feature**: 201 — output-integrity-threat-agent
**PRD**: `docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md`
**Date**: 2026-04-18

## Codebase Analysis

### Structural Template — `prompt-injection` Agent (Closest Mirror)

- `.claude/agents/tachi/prompt-injection.md` (96 lines) is the authoritative 5-section AI-tier template post-Feature 082. Shape: YAML frontmatter → metadata YAML (`category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`) → `## Purpose` → `## Skill References` (3-row table: detection-patterns, severity-bands-shared, finding-format-shared) → `## Detection Workflow` with exactly **one** `**MANDATORY**: Read` directive at section start → optional `## Example Findings`. Model: `sonnet`. Tools: `Read, Glob, Grep`.
- `.claude/skills/tachi-prompt-injection/README.md` — consumers + purpose header; mirror convention for new companion.
- `.claude/skills/tachi-prompt-injection/references/detection-patterns.md` — frontmatter (`name`, `description`, `consumers: [tachi-prompt-injection]`, `last_updated`); `## Overview` → `## Detection Scope` (Trigger Keywords + Applicable DFD Element Types) → `## Detection Patterns` (numbered categories with primary-source citations, indicators 3-6 bullets, worked example per category).

### Orchestrator Dispatch Registration Points

- `.claude/agents/tachi/orchestrator.md` lines 31–45: hardcoded dispatch list. Current AI-tier section lists 5 agents (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`). New agent inserts after `tool-abuse.md` on line 45.
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` lines 63–73: LLM dispatch trio (`prompt-injection`, `data-poisoning`, `model-theft`) paired with LLM keywords (`"LLM"`, `"model"`, `"GPT"`, `"Claude"`). Quartet extension inserts `output-integrity` as 4th LLM-dispatch agent; no new keywords required (shared LLM keyword set).

### Additive-Only Shared-Reference Edit

- `.claude/skills/tachi-shared/references/finding-format-shared.md` frontmatter lines 6–19: `consumers:` list in tier-grouping order — `orchestrator` → STRIDE-canonical (6) → AI-LLM (`prompt-injection`, `data-poisoning`, `model-theft`) → AI-AG (`agent-autonomy`, `tool-abuse`) → infra (`risk-scorer`). Natural insertion point for `output-integrity`: after `tool-abuse` (line 18), before `risk-scorer` (line 19). All `## ` headings must remain byte-identical pre/post edit per ADR-023 Decision 3.

### Finding Schema Current State (Feature 189)

- `schemas/finding.yaml:13` — `schema_version: "1.5"` (F-A2 source_attribution).
- `schemas/finding.yaml:18` — `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"`. `OI` prefix is **absent** → regex must extend to `(S|T|R|I|D|E|AG|LLM|AGP|OI)`. Minor bump 1.5 → 1.6 per ADR-026 Complex-Shape Clarifier (additive; shape unchanged; existing IDs remain valid).
- `category` enum (lines 31–39): already contains `llm`; **no enum change**. `OI-{N}` findings emit `category: llm` distinguished via ID prefix.
- `agentic_pattern` field (lines 149–178): assigned downstream by orchestrator Phase 3.6 (Feature 142 / ADR-026); NOT declared in agent metadata. Output-integrity findings will receive `agentic_pattern: none` post-hoc (single-agent output-side surface, not multi-agent pattern).

### Source Attribution (F-A2) Contract

- `schemas/finding.yaml` `source_attribution`: list-of-record with `{taxonomy, id, relationship}`; taxonomy ∈ 5-value closed enum (`owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`); relationship ∈ 3-value enum (`primary`, `related`, `derived`) default `primary`.
- `scripts/tachi_parsers.py:826` — `validate_source_attribution(findings, taxonomy_dir)` resolves every `{taxonomy, id}` pair against the top-level records in `schemas/taxonomy/{taxonomy}.yaml`. Invocation is orchestrator Phase 4 per ADR-028 Decision 5.
- **Verified present in `schemas/taxonomy/cwe.yaml`**: CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-918. **Verified absent**: CWE-73, CWE-1336 (PRD BLOCKING-1 correction — CWE-94 substitutes for CWE-1336 at template injection; CWE-22 alone at path traversal).
- **Verified present in `schemas/taxonomy/owasp.yaml`**: LLM05 record.

### ADR Lineage

- `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` — lean-agent detection variant. Decision 1 (single-point load), Decision 2 (zero MAESTRO references — grep-auditable invariant), Decision 3 (additive-only shared-reference edits).
- `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md` — byte-identity harness for 5 non-agentic baselines.
- `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md` — minor-bump rule for additive schema changes.
- `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` — 5-value taxonomy enum source.
- `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md` — `source_attribution` contract F-1 produces.
- `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md` — downstream consumer; `has-source-attribution` boolean fires `true` on regenerated example post-F-1.
- **ADR-030 does not yet exist** (confirmed via find) — no forward-dependency conflict.

### Example Architecture Regeneration Target

- `examples/agentic-app/architecture.md` — extended in Feature 142 with second LLM agent, learning loop, inter-agent communication channel. Has LLM Process components with downstream data flows (Delegation Message, Response) that match LLM05 output-side surface. PM default per Q4 architect leaning.
- Alternative: extend `examples/web-app/` to introduce an LLM-content-generation component. Currently no LLM components (Auth Service, API Gateway, Session Store, User DB).

### Backward Compatibility Baselines

- `tests/scripts/test_backward_compatibility.py` `BASELINE_EXAMPLES` — 6 baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. `agentic-app` excluded per Feature 128 convention (regeneration target for new AI agents).
- `mermaid-agentic-app` IS in the baseline list — needs scrutiny: does it contain any LLM Process matching output-integrity triggers? If yes, byte-identity may break and a re-baseline is required. Plan stage must verify.

## Industry Research (OWASP LLM05:2025)

- **Canonical taxonomy**: OWASP LLM05:2025 Improper Output Handling — insufficient validation/sanitization of LLM outputs before downstream consumption. Attack vectors: XSS/CSRF (browser sinks), SSRF, privilege escalation, RCE (backend sinks).
- **Primary attack classes**:
  - **XSS** — LLM generates JS/HTML/CSS executing in browser when not encoded (reflected and stored; stored XSS via LLM output persisted to DB).
  - **SQL Injection** — LLM-crafted queries without parameterization.
  - **Remote Code Execution** — LLM output passed to `exec()`, `eval()`, shell commands without validation.
- **Standard mitigations**:
  1. Output validation/sanitization (HTML entity encoding, SQL escaping, command-pattern stripping, regex/parser checks)
  2. Strict Content Security Policy (CSP) for XSS
  3. Fine-grained authorization (OAuth 2.0 scopes, FGA retrievers) so LLM actions fail if user lacks permission
  4. Output filtering / semantic analysis (toxicity, bias, sensitive leaks, prohibited-instruction detection)
  5. Monitoring + logging for unusual output patterns
  6. Human review on consequential actions (regulatory/financial/safety)
  7. Parameterized queries
- **Framing insight**: Auth0's "Why Improper Output Handling is the New XSS" framing reinforces that LLM05 is a **symmetry restoration** threat class — input-side input validation has matured into "prompt injection defense", but output-side is still treated as "trust the AI" in many stacks. Our agent's mitigation text should name **specific** encodings/patterns (not generic "sanitize output") to match the developer-facing expectations this ecosystem has converged on.

## Architecture Constraints

- **ADR-023 invariants** (lean-agent detection variant):
  1. Single-point load — exactly one `**MANDATORY**: Read` directive under `## Detection Workflow`.
  2. Zero MAESTRO references in agent file and companion `detection-patterns.md` — grep-auditable.
  3. Additive-only shared-reference edits — `## ` headings byte-identical pre/post.
- **ADR-021 determinism** — `SOURCE_DATE_EPOCH=1700000000` byte-identity on 5 non-agentic baselines.
- **22-file zero-edit invariant** (ADR-023 lineage, extended by F-A1/F-A2/F-B) — zero edits to the 11 existing threat-agent files + 11 companion `detection-patterns.md` files. Orchestrator-tier files (`orchestrator.md`, `dispatch-rules.md`) are **carved out** and DO receive additive edits.
- **Tier caps** — AI tier ≤150 lines, hard ceiling 180 (per Feature 082 FR-10).
- **Zero new runtime deps** — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.

## Recommendations for Spec

- **User stories (3)**: preserve verbatim from PRD US-201-1/2/3 with job-story restructuring. All three P1 priority (PRD states P0; translate to P1 as the spec's top priority band).
- **Functional requirements**: translate PRD FR-1 through FR-7 into testable predicates. Keep implementation file paths (agent/skill/schema paths ARE the product artifacts in this repo).
- **Success criteria**: translate PRD SC-1 through SC-10 into measurable outcomes. Add one or two scope-boundary predicates if the PRD left them implicit (e.g., explicit zero-edit enumeration per SC-9).
- **Edge cases**: pattern false-positives on LLM Process with no downstream sink, ML09 bundling ambiguity, Heuristic A sixth-pattern conditional, `mermaid-agentic-app` baseline-break risk, F-A2 referential validation failure on malformed source_attribution, Q4 Heuristic A timing cascade past Day 1 EOD.
- **[NEEDS CLARIFICATION] markers**: target zero. PRD architect-owned Q-set (Q1-Q5) has architect leanings captured and these decisions belong in `/aod.plan` (project-plan) / ADR-030, NOT in the spec.
- **Out-of-scope**: mirror PRD's 11-item Out-of-Scope list verbatim where possible; it's the authoritative scope boundary.
- **Do NOT**:
  - Re-author the Heuristic A determination (architect-owned in ADR-030).
  - Specify trigger-keyword final set (architect-owned at plan; PRD Q2 leans 8-12 keywords curation).
  - Specify DFD target set beyond Process (architect-owned per Q3).
  - Pick example regeneration target (architect-owned per Q4; PM default is `agentic-app`).
