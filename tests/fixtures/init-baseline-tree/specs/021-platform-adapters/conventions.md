# Platform Adapter Conventions

**Feature**: 021 - Platform Adapters
**Date**: 2026-03-23
**Status**: Active
**Referenced by**: All file-transformation adapter tasks (T005-T008, T013-T016, T020-T023, T024-T028)

---

## 1. Shared Metadata YAML Format (T003)

When file-transformation adapters (Claude Code, Cursor, Copilot) strip the original tachi YAML frontmatter, tachi-specific metadata fields must be preserved as a `## Metadata` section in the markdown body.

### Placement

The `## Metadata` section is inserted at the **top of the body**, immediately after the platform-specific frontmatter closing `---` and before the first existing heading (e.g., `# Spoofing Threat Agent`).

### Format

The section contains a fenced YAML code block with only the tachi-specific fields that exist in the source agent's frontmatter. Fields that do not exist in the source are omitted entirely -- adapters never fabricate metadata.

```markdown
## Metadata

```yaml
category: stride
threat_class: S
dfd_targets: [External Entity, Process]
owasp_references:
  - "OWASP Top 10 2021 A07:2021 -- Identification and Authentication Failures"
  - "OWASP API Security 2023 API2 -- Broken Authentication"
  - "CWE-287: Improper Authentication"
output_schema: schemas/finding.yaml
```
```

### Field Inventory by Agent Type

Not all agents carry the same frontmatter fields. The following table defines which fields exist per agent type and therefore which fields appear in the `## Metadata` section.

| Field | STRIDE Agents | AI/LLM Agents | Report Agents | Orchestrator |
|-------|:---:|:---:|:---:|:---:|
| `category` | Yes (`stride`) | Yes (`llm`) | Yes (`report`) | Yes (`orchestrator`) |
| `threat_class` | Yes (S/T/R/I/D/E) | Yes (`LLM`) | No | No |
| `dfd_targets` | Yes | Yes | No | No |
| `owasp_references` | Yes | Yes | No | No |
| `output_schema` | Yes | Yes | Yes | Yes (multiple) |
| `input_schema` | No | No | Yes | No |
| `output_files` | No | No | Yes | No |
| `references` | No | No | Yes (schemas, templates) | Yes (schemas, templates, agents) |

**Notes on specific agent types**:

- **STRIDE agents** (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation): Carry `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`. All five fields appear in the Metadata section.
- **AI/LLM agents** (prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse): Same field set as STRIDE agents. `category` is `llm`, `threat_class` is `LLM`.
- **Report agents** (threat-report, threat-infographic): Carry `category`, `input_schema`, `output_schema`, `output_files`, and `references`. No `threat_class`, `dfd_targets`, or `owasp_references`.
- **Orchestrator**: Carries `category` and `references` (schemas, templates, agents). No `threat_class`, `dfd_targets`, or `owasp_references`. The `references` block is complex and includes agent dispatch paths.

### Metadata Section Examples

**STRIDE agent** (e.g., spoofing.md):

```markdown
## Metadata

```yaml
category: stride
threat_class: S
dfd_targets: [External Entity, Process]
owasp_references:
  - "OWASP Top 10 2021 A07:2021 -- Identification and Authentication Failures"
  - "OWASP API Security 2023 API2 -- Broken Authentication"
  - "CWE-287: Improper Authentication"
  - "CWE-290: Authentication Bypass by Spoofing"
  - "CWE-384: Session Fixation"
  - "MITRE ATT&CK T1078: Valid Accounts"
  - "MITRE ATT&CK T1556: Modify Authentication Process"
output_schema: schemas/finding.yaml
```
```

**AI/LLM agent** (e.g., prompt-injection.md):

```markdown
## Metadata

```yaml
category: llm
threat_class: LLM
dfd_targets: [Process]
owasp_references: [OWASP LLM01:2025, OWASP LLM07:2025]
output_schema: schemas/finding.yaml
```
```

**Report agent** (e.g., threat-report.md):

```markdown
## Metadata

```yaml
category: report
input_schema: schemas/output.yaml
output_schema: schemas/report.yaml
output_files:
  - threat-report.md
  - attack-trees/{finding-id}-attack-tree.md
```
```

**Orchestrator** (orchestrator.md):

```markdown
## Metadata

```yaml
category: orchestrator
references:
  contract: docs/INTERFACE-CONTRACT.md
  schemas:
    finding: schemas/finding.yaml
    input: schemas/input.yaml
    output: schemas/output.yaml
    report: schemas/report.yaml
    infographic: schemas/infographic.yaml
  templates:
    threats: templates/threats.md
    sarif_template: templates/threats.sarif
    threat_report: templates/threat-report.md
  agents:
    stride:
      - spoofing.md
      - tampering.md
      - repudiation.md
      - info-disclosure.md
      - denial-of-service.md
      - privilege-escalation.md
    ai:
      - prompt-injection.md
      - data-poisoning.md
      - model-theft.md
      - agent-autonomy.md
      - tool-abuse.md
    report: threat-report.md
    infographic: threat-infographic.md
```
```

Note: The orchestrator's `references.agents` paths in the Metadata section use the **already-rewritten** flat sibling references (e.g., `spoofing.md` not `agents/stride/spoofing.md`), since the Metadata section reflects the adapter's resolved context, not the source layout.

### Applicability

| Adapter | Uses Metadata Section? | Reason |
|---------|:---:|--------|
| Claude Code | Yes | Platform frontmatter replaces tachi frontmatter; metadata preserved in body |
| Cursor | Yes | Platform frontmatter replaces tachi frontmatter; metadata preserved in body |
| Copilot | Yes | Platform frontmatter replaces tachi frontmatter; metadata preserved in body |
| Generic | **No** | All metadata stripped; prompts are self-contained for chat UI / API usage |
| GitHub Actions | **No** | Agents invoked at runtime via LLM API; no file transformation occurs |

---

## 2. Path Rewriting Rules (T004)

File-transformation adapters install agent files into platform-specific subdirectories. All internal path references (schemas, templates, sibling agents) must be rewritten to resolve correctly from the installation location.

### Installation Paths

| Platform | Installation Directory | Depth from Project Root |
|----------|----------------------|------------------------|
| Claude Code | `.claude/agents/tachi/` | 3 levels deep |
| Cursor | `.cursor/rules/tachi/` | 3 levels deep |
| Copilot | `.github/agents/tachi/` | 3 levels deep |
| Generic | N/A (standalone files) | N/A |
| GitHub Actions | N/A (CI workflow) | N/A |

### Rule 1: Schema and Template Path Rewriting

Source agents reference schemas and templates from the project root (e.g., `schemas/finding.yaml`, `templates/threats.md`). File-transformation adapters must prepend the correct number of parent directory traversals to resolve from the installation directory back to the project root.

**Formula**: `../../../{original-path}` for all three file-transformation adapters (3 levels up).

| Source Reference | Claude Code | Cursor | Copilot |
|-----------------|-------------|--------|---------|
| `schemas/finding.yaml` | `../../../schemas/finding.yaml` | `../../../schemas/finding.yaml` | `../../../schemas/finding.yaml` |
| `schemas/input.yaml` | `../../../schemas/input.yaml` | `../../../schemas/input.yaml` | `../../../schemas/input.yaml` |
| `schemas/output.yaml` | `../../../schemas/output.yaml` | `../../../schemas/output.yaml` | `../../../schemas/output.yaml` |
| `schemas/report.yaml` | `../../../schemas/report.yaml` | `../../../schemas/report.yaml` | `../../../schemas/report.yaml` |
| `schemas/infographic.yaml` | `../../../schemas/infographic.yaml` | `../../../schemas/infographic.yaml` | `../../../schemas/infographic.yaml` |
| `templates/threats.md` | `../../../templates/threats.md` | `../../../templates/threats.md` | `../../../templates/threats.md` |
| `templates/threats.sarif` | `../../../templates/threats.sarif` | `../../../templates/threats.sarif` | `../../../templates/threats.sarif` |
| `templates/threat-report.md` | `../../../templates/threat-report.md` | `../../../templates/threat-report.md` | `../../../templates/threat-report.md` |
| `docs/INTERFACE-CONTRACT.md` | `../../../docs/INTERFACE-CONTRACT.md` | `../../../docs/INTERFACE-CONTRACT.md` | `../../../docs/INTERFACE-CONTRACT.md` |

This rule applies to paths appearing in:
- The `## Metadata` section's `references` block (orchestrator and report agents)
- Inline references within the body content (e.g., "conforming to `schemas/finding.yaml`")

### Rule 2: Sibling Agent Reference Rewriting

The orchestrator's `references.agents` paths reference agents by their source directory structure (e.g., `agents/stride/spoofing.md`). In all file-transformation adapters, agents are installed as flat siblings in the same directory. References must be rewritten to flat filenames with the platform-appropriate extension.

| Source Reference | Claude Code | Cursor | Copilot |
|-----------------|-------------|--------|---------|
| `agents/stride/spoofing.md` | `spoofing.md` | `spoofing.mdc` | `spoofing.agent.md` |
| `agents/stride/tampering.md` | `tampering.md` | `tampering.mdc` | `tampering.agent.md` |
| `agents/stride/repudiation.md` | `repudiation.md` | `repudiation.mdc` | `repudiation.agent.md` |
| `agents/stride/info-disclosure.md` | `info-disclosure.md` | `info-disclosure.mdc` | `info-disclosure.agent.md` |
| `agents/stride/denial-of-service.md` | `denial-of-service.md` | `denial-of-service.mdc` | `denial-of-service.agent.md` |
| `agents/stride/privilege-escalation.md` | `privilege-escalation.md` | `privilege-escalation.mdc` | `privilege-escalation.agent.md` |
| `agents/ai/prompt-injection.md` | `prompt-injection.md` | `prompt-injection.mdc` | `prompt-injection.agent.md` |
| `agents/ai/data-poisoning.md` | `data-poisoning.md` | `data-poisoning.mdc` | `data-poisoning.agent.md` |
| `agents/ai/model-theft.md` | `model-theft.md` | `model-theft.mdc` | `model-theft.agent.md` |
| `agents/ai/agent-autonomy.md` | `agent-autonomy.md` | `agent-autonomy.mdc` | `agent-autonomy.agent.md` |
| `agents/ai/tool-abuse.md` | `tool-abuse.md` | `tool-abuse.mdc` | `tool-abuse.agent.md` |
| `agents/threat-report.md` | `threat-report.md` | `threat-report.mdc` | `threat-report.agent.md` |
| `agents/threat-infographic.md` | `threat-infographic.md` | `threat-infographic.mdc` | `threat-infographic.agent.md` |

### Rule 3: Generic Adapter -- Strip All References

The generic adapter produces self-contained prompt files for manual chat UI or API usage. All internal path references are **removed** because:

- Users cannot resolve filesystem paths from a chat interface
- Each prompt must be independently usable without a project directory structure
- Schema and template content is inlined or referenced by description rather than path

**Handling**:
- Schema references (e.g., "conforming to `schemas/finding.yaml`") are kept as descriptive text but not as resolvable paths. The prompt body already describes the expected format inline.
- Agent references are removed entirely; the generic orchestrator uses numbered steps instead of dispatch paths.
- Template references are removed; output format is described inline within each prompt.

### Rule 4: GitHub Actions -- No Path Rewriting

The GitHub Actions adapter invokes agents at runtime via LLM API. Source agent files are read from their original locations in the repository (`agents/`). No path rewriting is needed because:

- The workflow checks out the full repository
- Agent files are read from `agents/` at their original paths
- Schema and template files are accessed from project root

### Rule 5: Copilot Instructions File Path Resolution

Copilot has a special case for oversized agents (orchestrator at ~120K characters, threat-report at ~43K characters) that exceed the 30K character prompt body limit. These are split into:

1. A compact `.agent.md` file at `.github/agents/tachi/` (under 30K characters)
2. A full-context `.md` instructions file at `.github/instructions/`

The instructions files are at `.github/instructions/` (a sibling directory to `.github/agents/`), which means:

- Path references **within instructions files** resolve from `.github/instructions/`, which is 2 levels deep from the project root: `../../schemas/finding.yaml`, `../../templates/threats.md`
- Path references **within agent files** at `.github/agents/tachi/` resolve from 3 levels deep: `../../../schemas/finding.yaml`
- Cross-references between agent files and instructions files: agents reference instructions via Copilot's built-in instructions loading mechanism (not filesystem paths)

| File Location | Depth | Schema Path | Template Path |
|--------------|-------|-------------|---------------|
| `.github/agents/tachi/*.agent.md` | 3 levels | `../../../schemas/` | `../../../templates/` |
| `.github/instructions/*.md` | 2 levels | `../../schemas/` | `../../templates/` |

### Summary Matrix

| Aspect | Claude Code | Cursor | Copilot (agents) | Copilot (instructions) | Generic | GitHub Actions |
|--------|-------------|--------|-------------------|----------------------|---------|----------------|
| Installation path | `.claude/agents/tachi/` | `.cursor/rules/tachi/` | `.github/agents/tachi/` | `.github/instructions/` | N/A | N/A |
| Levels to root | 3 | 3 | 3 | 2 | N/A | N/A |
| Schema prefix | `../../../` | `../../../` | `../../../` | `../../` | Removed | N/A |
| Template prefix | `../../../` | `../../../` | `../../../` | `../../` | Removed | N/A |
| Agent refs | Flat sibling `.md` | Flat sibling `.mdc` | Flat sibling `.agent.md` | N/A | Removed | N/A |
| File extension | `.md` | `.mdc` | `.agent.md` | `.md` | `.md` | `.yml` |
