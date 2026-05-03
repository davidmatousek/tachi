# Data Model: Feature 082 — Threat Agent Skill References

**Status**: Phase 1 design artifact
**Parent**: [plan.md](./plan.md)
**Spec**: [spec.md](./spec.md)

> **Note**: This feature modifies markdown configuration files, not runtime data. "Data model" here describes **file-system entities**, their relationships, and invariants enforced during validation. No database schema, no API contract, no serialization format changes.

---

## Entity Relationship Diagram

```
┌──────────────────────┐    1:1    ┌──────────────────────────┐
│  ThreatAgentFile     ├──────────▶│  CompanionSkillDirectory │
│  (11 instances)      │           │  (11 instances)          │
└──────────┬───────────┘           └───────────┬──────────────┘
           │                                   │
           │ 1:N (reads)                       │ 1:N (contains)
           │                                   ▼
           │                       ┌──────────────────────────┐
           │                       │  ReferenceFile           │
           │                       │  (22-33 instances)       │
           │                       └───────────┬──────────────┘
           │                                   │
           │                                   │ 1:N (has)
           │                                   ▼
           │                       ┌──────────────────────────┐
           │                       │  EnrichmentCategory      │
           │                       │  (≥22 aggregate)         │
           │                       └───────────┬──────────────┘
           │                                   │
           │                                   │ N:M (cites)
           │                                   ▼
           │                       ┌──────────────────────────┐
           │                       │  PrimarySource           │
           │                       │  (finite set, ~7)        │
           │                       └──────────────────────────┘
           │
           │ 1..N (reads via **MANDATORY** Read)
           ▼
┌──────────────────────┐
│  SharedReferenceFile │
│  (4 instances)       │
└──────────────────────┘

┌──────────────────────┐
│  ADR-023             │
│  (1 instance, NEW)   │
│  governs pattern     │
└──────────────────────┘
```

---

## Entities

### 1. ThreatAgentFile

**Definition**: A markdown configuration file at `.claude/agents/tachi/<name>.md` consumed by the Claude Code harness to define a threat detection agent.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Agent base name — e.g., `spoofing`, `prompt-injection` |
| `category` | enum | yes | `stride` or `ai` |
| `pre_refactor_lines` | integer | yes | Baseline line count per Appendix A (113-201 range) |
| `post_refactor_lines` | integer | yes | Post-refactor `wc -l` output — must satisfy tier target |
| `model` | string | yes | Always `sonnet` per FR-11 (preserved from pre-refactor state) |
| `tools` | list[string] | yes | Always `[Read, Glob, Grep]` |
| `skill_references_table_present` | boolean | yes | Must be `true` after refactor (FR-2) |
| `detection_workflow_section_present` | boolean | yes | Must be `true` after refactor (FR-1) |
| `mandatory_read_directive_count` | integer | yes | Exactly 1 at the start of Detection Workflow section (FR-1) |
| `has_maestro_reference` | boolean | yes | Must be `false` (FR-9 / SC-010) |
| `companion_skill_directory` | string | yes | Path `.claude/skills/tachi-<name>/references/` — must exist |

**Instances** (11):

| name | category | pre_refactor_lines | tier_target | hard_ceiling |
|------|----------|---------------------|-------------|--------------|
| spoofing | stride | 113 | ≤120 | 180 |
| tampering | stride | 126 | ≤120 | 180 |
| repudiation | stride | 124 | ≤120 | 180 |
| info-disclosure | stride | 128 | ≤120 | 180 |
| denial-of-service | stride | 141 | ≤120 | 180 |
| privilege-escalation | stride | 136 | ≤120 | 180 |
| prompt-injection | ai | 167 | ≤150 | 180 |
| data-poisoning | ai | 171 | ≤150 | 180 |
| model-theft | ai | 188 | ≤150 | 180 |
| tool-abuse | ai | 185 | ≤150 | 180 |
| agent-autonomy | ai | 201 | ≤150 | 180 |

**Invariants**:
- `post_refactor_lines ≤ tier_target` (FR-10, SC-002)
- `post_refactor_lines ≤ hard_ceiling` always
- `skill_references_table_present == true` (FR-2)
- `detection_workflow_section_present == true` (FR-1)
- `mandatory_read_directive_count == 1` (FR-1)
- `has_maestro_reference == false` (FR-9)
- `companion_skill_directory` exists on the file system

---

### 2. CompanionSkillDirectory

**Definition**: A directory at `.claude/skills/tachi-<agent-name>/references/` containing the detection pattern reference file(s) for one threat agent.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `directory_path` | string | yes | Absolute path |
| `parent_agent_name` | string | yes | The threat agent that owns this directory |
| `reference_file_count` | integer | yes | ≥1 (at minimum `detection-patterns.md`) |
| `total_lines` | integer | yes | Sum across all reference files in directory |

**Instances** (11, one per agent). Created in Phase 1 (prototype agents) and Phase 2a/2b (remaining agents).

**Invariants**:
- Directory exists on file system
- `reference_file_count ≥ 1`
- `directory_path` matches pattern `.claude/skills/tachi-<parent_agent_name>/references/` exactly (no tier prefix, per FR-3)
- No shared content exists in this directory — cross-agent content goes to `SharedReferenceFile` (via Phase 2c consolidation)

---

### 3. ReferenceFile

**Definition**: A markdown file inside a `CompanionSkillDirectory` containing externalized detection patterns, finding field guidance, or example findings.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | yes | Absolute path |
| `parent_directory` | string | yes | Points to the `CompanionSkillDirectory` |
| `file_type` | enum | yes | `detection-patterns` / `finding-field-guidance` / `example-findings` |
| `frontmatter_present` | boolean | yes | YAML frontmatter with `name`, `description`, `consumers` |
| `line_count` | integer | yes | Typical 60-300 |
| `pattern_categories` | list[string] | yes | List of `## Pattern Category: <name>` headings |
| `primary_source_citations` | list[string] | yes | Citations to OWASP/CWE/MITRE/NIST URLs |
| `is_self_documenting` | boolean | yes | Can a contributor understand the threat from this file alone? (FR-4) |
| `enrichment_count` | integer | yes | Number of `EnrichmentCategory` instances added beyond pre-refactor inline content |

**Typical instance**: `tachi-spoofing/references/detection-patterns.md` with ~5-10 pattern categories (pre-refactor ~5 + enrichment ≥2).

**Invariants**:
- `frontmatter_present == true`
- `is_self_documenting == true` (FR-4) — validated during review, not automated
- `pattern_categories` size ≥ pre-refactor category count (enrichment is additive, not replacement)
- If `enrichment_count > 0`, every new category has at least one entry in `primary_source_citations`

---

### 4. SharedReferenceFile

**Definition**: A markdown file at `.claude/skills/tachi-shared/references/<name>.md` consumed by multiple agents (threat tier + infrastructure tier).

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_name` | string | yes | `severity-bands-shared`, `finding-format-shared`, `stride-categories-shared`, `maestro-layers-shared` |
| `pre_refactor_lines` | integer | yes | 110, 177, 146, 213 respectively |
| `post_refactor_lines` | integer | yes | `pre_refactor_lines + additive_delta` |
| `consumers_declared` | list[string] | yes | Frontmatter `consumers:` list |
| `consumers_actual` | list[string] | yes | Agents that actually `**MANDATORY**: Read` this file (verified via grep) |
| `content_orientation` | enum | yes | `consumer` / `producer` / `both` |
| `edit_policy` | enum | yes | Always `additive-only` (FR-5 / C9) |
| `additive_delta` | integer | yes | Lines added in Phase 2c (0 for unchanged files) |

**Instances** (4, pre-existing):

| file_name | pre_refactor_lines | expected post_refactor_lines | orientation | edit in Phase 2c |
|-----------|---------------------|-------------------------------|-------------|------------------|
| severity-bands-shared.md | 110 | 110 | producer (already) | None |
| finding-format-shared.md | 177 | 217-237 | both (consumer today, producer added) | APPEND "## For Threat Agents (Producers)" section |
| stride-categories-shared.md | 146 | 146 | producer (already) | None (threat agents start reading aspirational-consumer frontmatter) |
| maestro-layers-shared.md | 213 | 213 | producer | NONE (FR-9 forbids threat agent access) |

**Invariants**:
- `consumers_declared ⊇ consumers_actual` (declared is a superset of actual — frontmatter may be aspirational)
- For Feature 082 Phase 2c: edits are **additive-only** — existing sections are byte-identical pre/post
- `edit_policy == additive-only` always
- `maestro-layers-shared.md` is not added to any threat agent's Skill References table (FR-9)
- Post-Phase 2c: `consumers_actual` for `finding-format-shared.md` and `stride-categories-shared.md` expands to include all 11 threat agents (the aspirational frontmatter finally matches reality)

---

### 5. EnrichmentCategory

**Definition**: A new detection pattern category added to a `ReferenceFile` during Phase 1b or Phase 2a/2b extraction — one that was NOT in the pre-refactor inline version of the source agent.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_name` | string | yes | Human-readable name — e.g., "OAuth token replay", "ReDoS algorithmic complexity" |
| `parent_agent` | string | yes | Agent that owns this enrichment — e.g., `spoofing`, `agent-autonomy` |
| `parent_reference_file` | string | yes | Reference file it lives in |
| `primary_source` | enum | yes | `owasp-top-10` / `owasp-llm-top-10` / `owasp-ai-exchange` / `mitre-attack` / `mitre-atlas` / `cwe-top-25` / `nist-ai-rmf` / `nist-ai-600-1` |
| `citation_url` | string | yes | Canonical URL or identifier (e.g., `https://cwe.mitre.org/data/definitions/918.html`) |
| `is_de_scoped` | boolean | yes | `true` if Phase 2e security-analyst review removed this category |

**Aggregate invariants** (FR-7, SC-006):
- Sum of `EnrichmentCategory` instances with `is_de_scoped == false` across all 11 agents ≥ 22
- Per-agent count is flexible — some agents may contribute 0, others 5+
- 100% of non-de-scoped categories have non-empty `primary_source` and `citation_url` (FR-8, SC-007)

**Phase 2e de-scope policy**: If security-analyst flags a category as speculative, false-positive risk, or taxonomically incorrect, the category is set `is_de_scoped = true` and removed from its parent reference file. This does NOT affect the architectural refactor — the agent still ships with its reference file containing all remaining patterns.

---

### 6. PrimarySource

**Definition**: One of the approved authoritative sources for detection pattern enrichment citations (FR-8).

**Instances** (finite, 7-8):

| source_id | canonical_name | license | fit |
|-----------|----------------|---------|-----|
| `owasp-top-10` | OWASP Top 10 (2021+) | CC BY 3.0 | STRIDE baseline |
| `owasp-llm-top-10` | OWASP LLM Top 10 (v2025+) | CC BY-SA 4.0 | AI canonical |
| `owasp-ai-exchange` | OWASP AI Exchange | CC0 1.0 | AI (best — zero attribution) |
| `mitre-attack` | MITRE ATT&CK (v15+) | Free w/ attribution | STRIDE industrial |
| `mitre-atlas` | MITRE ATLAS (v5.1+ Nov 2025) | Free w/ attribution | AI adversarial |
| `cwe-top-25` | CWE Top 25 (2024+) | Royalty-free | STRIDE weaknesses |
| `nist-ai-rmf` | NIST AI Risk Management Framework | US Federal public domain | AI framing (supporting only) |
| `nist-ai-600-1` | NIST AI 600-1 (July 2024+) | US Federal public domain | AI framing (supporting only) |

**Invariants**:
- An `EnrichmentCategory` citing `nist-ai-rmf` or `nist-ai-600-1` as its **sole** source is not acceptable (FR-8 treats NIST as supporting citation only). Must have at least one other source.
- Citation URLs are stored in reference files but never fetched at runtime — no network dependency (C1).

---

### 7. ADR023

**Definition**: The architectural decision record governing the sibling variant pattern.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | yes | `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` |
| `status` | enum | yes | `Draft` → `Accepted` |
| `decisions_count` | integer | yes | 4 (per plan.md §1.4) |
| `decisions` | list[string] | yes | [sibling-variant, MAESTRO-boundary, additive-only, consumer-producer-separation] |
| `referenced_from_tech_stack_README` | boolean | yes | Must become `true` by Phase 3 |

**Lifecycle**:
- **Phase 0**: Architect creates draft
- **Phase 1 gate**: Status → `Accepted` as gate exit criterion E-4 (FR-13f)
- **Phase 3**: Referenced from `docs/architecture/00_Tech_Stack/README.md` agent inventory

**Invariants**:
- `file_path` exists by end of Phase 1
- `decisions_count == 4` at all times after creation
- By Phase 3 close: `status == Accepted` AND `referenced_from_tech_stack_README == true`

---

## Cross-Cutting Invariants

**INV-1 (File existence)**: All 11 `ThreatAgentFile` + all 11 `CompanionSkillDirectory` + all 4 (existing) `SharedReferenceFile` + 1 new ADR023 exist on the file system post-refactor.

**INV-2 (Line count)**: For each `ThreatAgentFile`, `post_refactor_lines ≤ tier_target` (STRIDE ≤120, AI ≤150). No agent exceeds `hard_ceiling = 180`.

**INV-3 (Pattern integrity)**: For each `ReferenceFile` with `enrichment_count > 0`, every enriched `EnrichmentCategory` has a non-empty `primary_source` and `citation_url`.

**INV-4 (Aggregate floor)**: Sum of `EnrichmentCategory` instances where `is_de_scoped == false` ≥ 22 across all 11 agents (FR-7 / SC-006).

**INV-5 (MAESTRO boundary)**: No `ThreatAgentFile` references `maestro-layers-shared.md`. No `CompanionSkillDirectory` contains a file importing or inheriting MAESTRO content. Verified via `grep -l "maestro\|MAESTRO"` returning zero matches in threat agents and their companion directories.

**INV-6 (Shared reference additivity)**: For each `SharedReferenceFile`, `post_refactor_lines ≥ pre_refactor_lines`. The diff between pre-refactor and post-refactor content is **additive only** — no deletion or modification of existing sections. Verified via `git diff` review during Phase 2c.

**INV-7 (Commit discipline)**: `git log --oneline 082-threat-agent-skill..main` shows at least 11 commit messages identifiable by agent name — one per extracted agent (FR-15 / SC-011). Shared reference consolidation (Phase 2c) is a separate commit.

**INV-8 (Regression equivalence)**: For each of 6 example architectures, the pre-refactor and post-refactor `threats.md` have equivalent content: finding count per category within ±2, severity distribution within ±1 per level, zero dropped findings (FR-18 / SC-005).

**INV-9 (Byte-determinism re-baselined)**: The 5 byte-deterministic example PDFs (all except agentic-app) regenerate successfully under `SOURCE_DATE_EPOCH=1700000000` after Phase 2c shared reference edits. New baselines are committed (FR-17 / SC-008).

---

## Validation Responsibilities

| Invariant | Validated By | Phase | Method |
|-----------|--------------|-------|--------|
| INV-1 (Existence) | senior-backend-engineer | Phase 1a, 2a, 2b | `ls` + `find` |
| INV-2 (Line count) | senior-backend-engineer | Phase 1a, 2a, 2b, 3 | `wc -l` |
| INV-3 (Citation presence) | web-researcher, security-analyst | Phase 0, 1b, 2e | Reference review |
| INV-4 (Aggregate floor) | senior-backend-engineer | Phase 2e | Tally in `enrichment-tally.md` |
| INV-5 (MAESTRO boundary) | code-reviewer | Phase 2, 3 | `grep` |
| INV-6 (Additivity) | architect, code-reviewer | Phase 2c | `git diff` review |
| INV-7 (Commit discipline) | team-lead | Phase 2, Delivery | `git log --oneline` |
| INV-8 (Regression) | tester | Phase 1a, 1b, 3 | `threats.md` diff |
| INV-9 (Re-baseline) | tester, devops | Phase 3 | PDF byte comparison with new baselines |

---

## Notes on Scope

This data model is intentionally **file-system oriented** because the feature refactors files. There is no database, no API, no persistent runtime state, and no serialization boundary being modified. The finding schema (`schemas/finding.yaml` v1.3) — which IS the serialization boundary — is explicitly out of scope per C5.

A future PRD that introduces automated pytest coverage for threat agents would add `TestCase` entities to this model. That is out of scope for Feature 082.
