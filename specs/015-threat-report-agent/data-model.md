# Data Model: Threat Report Agent & Attack Trees

**Feature**: 015 | **Date**: 2026-03-23

## Input Schema: threats.md (existing)

The report agent consumes `threats.md` as its sole input. The structure is defined by `schemas/output.yaml` (v1.1).

### Finding IR Fields (from `schemas/finding.yaml` v1.0)

| Field | Type | Values | Report Agent Usage |
|-------|------|--------|--------------------|
| `id` | string | `{CATEGORY}-{N}` (S-1, AG-2, LLM-1) | Finding reference, attack tree file naming, traceability |
| `category` | enum | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm | Agent-by-agent narrative grouping |
| `component` | string | Free text | Narrative annotations, cross-cutting theme detection, roadmap grouping |
| `threat` | string | Free text | Attack tree root goal, narrative content |
| `likelihood` | enum | LOW, MEDIUM, HIGH | Risk context in narrative |
| `impact` | enum | LOW, MEDIUM, HIGH | Risk context in narrative |
| `risk_level` | enum | Critical, High, Medium, Low, Note | Attack tree filter (Critical/High only), roadmap ordering |
| `mitigation` | string | Free text | Remediation roadmap items (preserved verbatim) |
| `references` | list[string] | OWASP/CWE IDs | Compliance relevance annotations |
| `dfd_element_type` | enum | External Entity, Process, Data Store, Data Flow | Architecture overview context |

### Correlation Group Fields (Section 4a)

| Field | Type | Report Agent Usage |
|-------|------|--------------------|
| `group_id` | string (CG-N) | Unified narrative grouping, consolidated roadmap items |
| `findings` | list[string] | Cross-references in attack trees and narrative |
| `component` | string | Theme detection input |
| `threat_summary` | string | Grouped narrative description |
| `risk_level` | enum | Inherited from highest-severity finding in group |

## Output Schema: threat-report.md (new)

Defined in `schemas/report.yaml`. The report has YAML frontmatter followed by 7 required sections.

### Report Frontmatter

| Field | Type | Source |
|-------|------|--------|
| `schema_version` | string | "1.0" (fixed) |
| `date` | string (YYYY-MM-DD) | Generation date |
| `source_file` | string | Path to input `threats.md` |
| `finding_count` | integer | Total findings from input |
| `risk_distribution` | object | Counts by risk level {Critical: N, High: N, Medium: N, Low: N} |
| `attack_tree_count` | integer | Number of generated attack trees |

### Report Section Entities

| Section | Key Fields | Completeness Rule |
|---------|-----------|-------------------|
| Executive Summary | risk_posture, top_threats, recommendations, compliance, timeline | ≤500 words, no jargon |
| Architecture Overview | components, trust_boundaries, data_flows | Derived from threats.md Sections 1–2 |
| Threat Analysis | category_narratives (one per agent) | Every finding ID addressed |
| Cross-Cutting Themes | theme_descriptions, contributing_finding_ids | At least 1 theme when >5 findings on same component |
| Attack Trees | mermaid_blocks, finding_ids | One tree per Critical/High finding |
| Remediation Roadmap | roadmap_items | All findings included |
| Appendix: Finding Reference | finding_id_to_section_mapping | 100% coverage — zero loss |

### Remediation Item Entity

| Field | Type | Source |
|-------|------|--------|
| `finding_id` | string | From finding IR `id` |
| `component` | string | From finding IR `component` |
| `priority_tier` | enum | Critical→Immediate, High→Short-term, Medium→Medium-term, Low→Backlog |
| `mitigation` | string | From finding IR `mitigation` (preserved verbatim) |
| `effort` | enum (Low/Medium/High) | Agent assessment based on mitigation complexity |
| `dependencies` | string | Agent analysis of prerequisites |
| `correlation_notes` | string (optional) | If part of correlation group: group ID + peer finding IDs |

### Attack Tree Entity

| Field | Type | Description |
|-------|------|-------------|
| `finding_id` | string | Source finding ID (e.g., AG-1) |
| `severity` | enum | Critical or High |
| `root_goal` | string | Attacker's ultimate objective (from finding `threat`) |
| `node_count` | integer | Total nodes in tree (target: ≤20) |
| `depth` | integer | Levels of decomposition (min 3 Critical, min 2 High) |
| `gate_types` | list[enum] | AND/OR gates used |
| `inline_location` | string | Section heading in threat-report.md |
| `standalone_file` | string | Path: `attack-trees/{finding-id}-attack-tree.md` |
