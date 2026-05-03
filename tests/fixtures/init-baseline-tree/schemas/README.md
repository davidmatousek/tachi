# Schemas

Machine-readable contracts defining the data interfaces between tachi components.

## Purpose

Schemas serve as the single source of truth for data structures exchanged between threat agents, output templates, and downstream features. They enable validation, documentation, and contract-driven development.

## Schema Files

| File | Purpose | Producers | Consumers |
|------|---------|-----------|-----------|
| `finding.yaml` | Intermediate Representation (IR) — the atomic finding contract | Threat agents in `agents/stride/` and `agents/ai/` (6 STRIDE + 5 AI) | Output template (`templates/threats.md`), SARIF export, narrative reports |
| `input.yaml` | Input validation — supported formats and recognition patterns | Integrators | Input parser, orchestrator |
| `output.yaml` | Output structure — required sections and field definitions | Template engine | Integrators, downstream exporters |

## Schema Relationships

```
Architecture Input
       │
       ▼
  input.yaml ──── validates ──→ Input Parser
                                    │
                                    ▼
                              Threat Agents
                                    │
                                    ▼
  finding.yaml ──── validates ──→ IR Findings
                                    │
                                    ▼
  output.yaml ──── validates ──→ Threat Model Output
```

- **input.yaml** → Validates architecture input before processing
- **finding.yaml** → Validates each finding produced by agents (the IR contract)
- **output.yaml** → Validates the assembled threat model document

## Versioning Policy

- Current version: `1.0`
- Breaking changes require a new major version with migration guidance
- Additive changes (new optional fields) increment the minor version
- Schema version is tracked in `schema_version` fields throughout the system

## Conventions

- Format: YAML (human-readable, consistent with project conventions)
- Field definitions include: `type`, `enum` or `pattern` (where applicable), and `description`
- All schemas are reference documents — they define structure but are not executable validators
