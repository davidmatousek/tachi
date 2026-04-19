# Data Model: `output-integrity` Agent

**Feature**: 201 — output-integrity-threat-agent

## Entities

### E1 — Agent File (`output-integrity.md`)

**Path**: `.claude/agents/tachi/output-integrity.md`
**Line cap**: ≤150 (AI tier per ADR-023), hard ceiling 180

**Structure**:

```
---
name: output-integrity
description: "Analyzes LLM Process components whose output flows into downstream execution sinks for OWASP LLM05:2025 Improper Output Handling — XSS, SQLi, command injection, SSRF, template injection, and path traversal vulnerabilities. Activate when a DFD element involves an LLM Process whose output is rendered in a browser, concatenated into SQL, passed to a shell, used as a template input, used as an outbound URL, or used as a file path."
tools: Read, Glob, Grep
model: sonnet
---

category: llm
threat_class: LLM
dfd_targets: [Process]
owasp_references: [OWASP LLM05:2025, OWASP ML09:2023]
output_schema: ../../../schemas/finding.yaml

## Purpose

{1-2 paragraphs. Name the output-handling threat surface. List the 5 sink categories
 (client-side execution, server-side execution, SSRF, template/expression injection,
 path traversal). Resolve ASI09 scope explicitly: per ADR-030 Heuristic A Outcome B,
 human-trust exploitation is out of scope here — forward-reference `trust-exploitation`
 (F-4) as the future owner.}

## Skill References

| Reference | File | Load When | Purpose |
|---|---|---|---|
| Detection patterns | ../../skills/tachi-output-integrity/references/detection-patterns.md | Detection start | Canonical pattern catalog with trigger keywords, indicators, worked examples, and CWE mappings |
| Severity bands | ../../skills/tachi-shared/references/severity-bands-shared.md | After indicator collection | OWASP 3×3 risk matrix for severity computation |
| Finding format | ../../skills/tachi-shared/references/finding-format-shared.md | Before emission | Canonical finding IR + producer-audience section |

## Detection Workflow

**MANDATORY**: Read `.claude/skills/tachi-output-integrity/references/detection-patterns.md` before analyzing any component.

1. **Identify candidate Process components**: scan the DFD for Process elements matching one or more trigger keywords from the pattern catalog's Detection Scope section (e.g., `LLM output`, `rendered HTML`, `model output to SQL`, `template engine`, `outbound HTTP from agent`, `LLM-synthesized URL`, `command construction`, `file path from model`).
2. **Collect structural indicators** per candidate: does the Process have at least one output Data Flow into a component that performs execution (browser render, SQL execute, shell invoke, template render, URL fetch, file write)? Per FR-011, BOTH a trigger keyword AND a structural indicator are required. Keyword alone MUST NOT produce a finding.
3. **Classify the pattern category** per candidate: one of the 5 catalog categories (client-side execution, server-side execution, SSRF, template injection, path traversal).
4. **Compute severity** using the OWASP 3×3 matrix from `severity-bands-shared.md` based on likelihood (ease of LLM output influence: high when prompt injection vector present, medium-high when upstream poisoning possible) and impact (blast radius of downstream sink: critical for RCE/SQL data leakage, high for XSS/SSRF, medium for path traversal).
5. **Emit an `OI-{N}` finding** per qualifying candidate using the canonical shape from `finding-format-shared.md`. Every finding MUST include:
   - `id: "OI-{N}"` (monotonically increasing)
   - `category: "llm"`
   - `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-{NUMBER}, relationship: related}]` per pattern category CWE mapping
   - `mitigation:` naming at least one specific encoding, library, or defensive pattern
   - `description:` distinguishing server-side vs client-side execution
6. **Zero findings on non-qualifying architectures** — if no candidate passed step 2, emit an empty findings list. No speculation.

## Example Findings

{2-3 worked examples demonstrating the canonical shape with OI-{N} IDs, category: llm,
 source_attribution populated, stack-specific mitigation. See contracts/finding-contract.md
 for fully-worked examples.}
```

**Invariants**:
- Exactly ONE `**MANDATORY**: Read` directive at start of `## Detection Workflow` (ADR-023 Decision 1)
- ZERO MAESTRO references anywhere in file (ADR-023 Decision 2; grep-auditable)
- Skill References table has exactly 3 rows (detection-patterns, severity-bands-shared, finding-format-shared)
- `agentic_pattern` field NOT declared in metadata (FR-016; orchestrator Phase 3.6 assigns downstream)

### E2 — Pattern Catalog (`detection-patterns.md`)

**Path**: `.claude/skills/tachi-output-integrity/references/detection-patterns.md`
**Typical line count**: 150-250 (no hard cap)

**Structure**:

```yaml
---
name: output-integrity-detection-patterns
description: "Canonical pattern catalog for output-integrity threat agent. Detects OWASP LLM05:2025 Improper Output Handling across client-side execution (XSS/DOM), server-side execution (SQLi/OS-command/code-injection), SSRF, template injection, and path traversal surfaces."
consumers: [tachi-output-integrity]
last_updated: 2026-04-22   # or actual merge date
---

## Overview

{1 paragraph. Scope = LLM output crossing an unsanitized boundary into a downstream
 execution sink. ML09:2023 bundling rationale documentation-only per BLP-01 §4;
 pattern primary remains LLM05:2025. Forward-reference F-4 `trust-exploitation` for
 human-victim signal class (per ADR-030 Heuristic A Outcome B).}

## Detection Scope

### Trigger Keywords (case-insensitive)

- `LLM output`
- `rendered HTML` / `model output to browser`
- `model output to SQL` / `LLM-generated query`
- `template engine` / `template injection`
- `outbound HTTP from agent` / `LLM-synthesized URL`
- `command construction` / `shell from LLM`
- `file path from model` / `LLM-generated path`

### Applicable DFD Element Types

- `Process` only (precedent-preserving across 11 existing AI agents per Q3 architect decision)

## Detection Patterns

### Pattern Category 1: Client-Side Execution Sinks (XSS / DOM Injection)

**Primary source**: OWASP LLM05:2025
**Related CWE**: CWE-79 (Cross-site Scripting)
**Indicators**:
- LLM output assigned to `element.innerHTML` or injected via document.write
- No Content Security Policy declared
- No framework-native escape helper (React {}, Vue v-text, Angular text-interpolation)
- Missing HTML entity encoding pre-render
- Response mixed with LLM-generated HTML in a web-UI-facing component

**Worked example**: {See Example 1 in contracts/finding-contract.md}

### Pattern Category 2: Server-Side Execution Sinks (SQLi / Command Injection / Code Injection)

**Primary source**: OWASP LLM05:2025
**Related CWEs**: CWE-89 (SQL Injection), CWE-78 (OS Command Injection), CWE-94 (Code Injection)
**Indicators**:
- LLM output concatenated into SQL query string
- LLM output passed to shell via `subprocess.run(shell=True)`, `os.system`, `exec`, `eval`
- LLM output interpolated into dynamic code evaluation paths
- Missing parameterized-query usage
- Missing arg-vector command construction

**Worked example**: {See Example 2 in contracts/finding-contract.md}

### Pattern Category 3: SSRF from LLM-Synthesized URLs

**Primary source**: OWASP LLM05:2025
**Related CWE**: CWE-918 (Server-Side Request Forgery)
**Indicators**:
- LLM output used as URL for outbound HTTP request
- No allowlist enforcement on hostnames
- No egress firewall controls
- Missing scheme validation (allows file://, gopher://, etc.)
- Redirect-following enabled to arbitrary hosts

**Worked example**: {See Example 3 in contracts/finding-contract.md}

### Pattern Category 4: Template / Expression Injection

**Primary source**: OWASP LLM05:2025
**Related CWE**: CWE-94 (Improper Control of Generation of Code — covers template-engine code injection; substitutes for absent CWE-1336)
**Indicators**:
- LLM output passed to Jinja2 / Handlebars / EJS / Mustache / Freemarker template render
- Escape mode disabled (autoescape=False)
- Template engine receiving model output verbatim
- No sandboxed renderer

**Worked example**: {Jinja2 without autoescape rendering LLM-generated content — CWE-94 primary}

### Pattern Category 5: Path Traversal + Unsafe File Writes

**Primary source**: OWASP LLM05:2025
**Related CWE**: CWE-22 (Improper Limitation of a Pathname to a Restricted Directory; substitutes for absent CWE-73)
**Indicators**:
- LLM output used as file path component
- No canonicalization (missing `os.path.realpath` or `pathlib.Path.resolve`)
- No allowlist directory enforcement
- Write operations to model-supplied paths
- Paths containing `..` segments or absolute paths accepted

**Worked example**: {File upload handler where LLM-generated filename is written to disk — CWE-22 primary}

### (Conditional — Outcome A only) Pattern Category 6: Human-Trust Exploitation via LLM Output

**Omitted entirely** — Heuristic A resolved Outcome B per ADR-030 Decision 2. Human-victim
output handling is scope-distinct and owned by F-4 `trust-exploitation` (forward-reference).
This pattern category intentionally does NOT ship in F-1.
```

**Invariants**:
- ZERO MAESTRO references anywhere in file (ADR-023 Decision 2; grep-auditable)
- Frontmatter `consumers:` = `[tachi-output-integrity]` (ADR-023 detection-variant precedent)
- ≥5 pattern categories with all 4 required elements per category (indicators, citation, keywords, example)

### E3 — Companion Skill README (`README.md`)

**Path**: `.claude/skills/tachi-output-integrity/README.md`
**Typical line count**: 30-50

**Structure**: Mirror `.claude/skills/tachi-prompt-injection/README.md` shape (title + short description + consumer list + purpose header). No body content required beyond the canonical pattern.

### E4 — Orchestrator Dispatch Entry

**File**: `.claude/agents/tachi/orchestrator.md`
**Edit**: add line `  - output-integrity.md` after `  - tool-abuse.md` in the AI-tier section (around line 44-45)
**Invariant**: no other dispatch-list ordering changes

### E5 — Dispatch Rules LLM Quartet

**File**: `.claude/skills/tachi-orchestration/references/dispatch-rules.md`
**Edit**: extend LLM dispatch trio (around lines 70-73) to quartet:
- Add `- \`output-integrity\` (OWASP LLM05:2025)` after `- \`model-theft\` (OWASP LLM10:2025)` line
- Add trigger-keyword activation rule: "`output-integrity` activates iff the dispatched LLM Process has at least one output Data Flow into a component performing execution (browser render, SQL execute, shell invoke, template render, URL fetch, file write). Keyword match alone is insufficient per FR-011."

### E6 — Shared Finding-Format Consumer List

**File**: `.claude/skills/tachi-shared/references/finding-format-shared.md`
**Edit**: frontmatter `consumers:` list — insert `- output-integrity` between `- tool-abuse` and `- risk-scorer`
**Invariant**: all `## ` headings byte-identical pre/post edit (ADR-023 Decision 3 grep audit)

### E7 — Finding Schema Regex Bump

**File**: `schemas/finding.yaml`
**Edits**:
- Line 13: `schema_version: "1.5"` → `schema_version: "1.6"`
- Line 18: `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"`

**Invariant**: All pre-1.6 finding IDs remain valid against the 1.6 regex (additive enum-expansion per ADR-026 Complex-Shape Clarifier).

### E8 — Public ADR-030

**File**: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
**Status lifecycle**: Proposed (Wave 1.1) → Accepted (Wave 5 at PR merge)

**Required body sections** (per FR-008 + PRD FR-5):
1. Title + metadata (status, date, deciders)
2. Context (BLP-01 Tier 1 framing, LLM threat-surface asymmetry problem statement)
3. Decisions (7 numbered):
   - D1: Adopt new `output-integrity` agent for LLM05 closure
   - D2: Heuristic A Outcome B (split) — forward-reference F-4 `trust-exploitation` for human-victim signal class
   - D3: Lean-agent shape conformance per ADR-023 (single-point load, ≤150 lines, zero MAESTRO)
   - D4: LLM05 + ML09 bundling documentation-only per BLP-01 §4
   - D5: 22-file zero-edit invariant preserved (grep-auditable enumeration)
   - D6: Proposed → Accepted dual-commit pattern per ADR-027/028/029 precedent
   - D7: Post-merge SHA fill recording squash commit
4. Cross-references: ADR-021 (determinism), ADR-023 (lean shape — extended), ADR-026 (schema minor-bump rule — extended to regex prefix addition), ADR-027 (taxonomy enum), ADR-028 (source_attribution contract), ADR-029 (coverage attestation downstream consumer)
5. Consequences (intended + potential risks)
6. Revision History table tracking Proposed → Accepted dates and post-merge SHA fill
7. No Layer 2 / tachi Cloud / commercial framing (public ADR stands on technical merits)
