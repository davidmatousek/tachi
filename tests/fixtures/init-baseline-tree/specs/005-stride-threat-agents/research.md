# Research Summary: STRIDE Threat Agents (F-005)

## Knowledge Base Findings
- No existing KB entries found (KB not yet populated)
- No prior patterns, lessons learned, or bug fixes to reference

## Codebase Analysis

### Existing STRIDE Agent Files (`agents/stride/`)
All 6 STRIDE agent prompt files exist with complete content (100-116 lines each):

| File | Lines | DFD Targets | Detection Patterns |
|------|-------|-------------|-------------------|
| spoofing.md | ~101 | External Entity, Process | 6 patterns (auth bypass, credential theft, session hijack, service impersonation, etc.) |
| tampering.md | ~107 | Process, Data Store, Data Flow | 5 patterns (input injection, data flow manipulation, storage corruption, etc.) |
| repudiation.md | ~105 | External Entity, Process | 5 patterns (missing audit logging, log integrity, timestamp manipulation, etc.) |
| info-disclosure.md | ~116 | Process, Data Store, Data Flow | 6 patterns (data leakage, excessive exposure, error message disclosure, etc.) |
| denial-of-service.md | ~115 | Process, Data Store, Data Flow | 5 patterns (resource exhaustion, app-layer attacks, cascading failures, etc.) |
| privilege-escalation.md | ~115 | Process | 5 patterns (vertical escalation, horizontal escalation, permission boundary violations, etc.) |

**Structural consistency**: All agents share identical structure: frontmatter, purpose, detection scope, patterns, finding template, risk computation, references.

### Schema Files (`schemas/`)
- **finding.yaml** (140 lines): 10-field IR with ID prefix validation, OWASP 3x3 risk matrix rules, enum values for categories
- **input.yaml** (143 lines): 5 supported formats (ascii, free-text, mermaid, plantuml, c4), heuristic auto-detection priority
- **output.yaml** (146 lines): 7 required sections in threats.md, frontmatter fields, STRIDE + AI table structure

### Orchestrator (`agents/orchestrator.md`, F-003 delivered)
- Implements OWASP 4-phase workflow: Scope, Determine Threats, Determine Countermeasures, Assess
- Two-layer dispatch: structural (STRIDE-per-Element normalization) + semantic (AI keyword matching)
- Self-check intermediate outputs at each phase
- Deterministic dispatch guarantee: same input always produces same agent dispatch

### Patterns to Follow
- F-001 spec: 20 requirements across 3 user stories, template-based approach
- F-003 spec: 36 acceptance scenarios across 6 stories, comprehensive edge case coverage
- Both specs follow same template with frontmatter, user stories with Given/When/Then, requirements, and success criteria

## Architecture Constraints

### Key Docs
- `docs/INTERFACE-CONTRACT.md` (514 lines): Single integration reference, input/output specification, dispatch rules, error conditions
- `docs/architecture/02_ADRs/ADR-003-stride-per-element-dispatch.md`: Core dispatch methodology decision
- `templates/threats.md` (371 lines): Canonical output template with all 7 sections

### Constraints
- Agent files are markdown prompts only (no application code, no runtime dependencies)
- Output must conform to `schemas/finding.yaml` without schema modifications
- Agents work within orchestrator's existing dispatch protocol (F-003)
- Side-effect guarantee: no network requests, no input modification, no state persistence
- Architecture input treated as DATA, not INSTRUCTIONS (prompt security boundary)
- Hub-and-spoke model: agent files are immutable hub content, never modified per-output

### Dependencies
- F-001 (delivered): Repository skeleton, schemas, interface contract
- F-003 (delivered): Orchestrator dispatch logic and STRIDE-per-Element normalization

## Industry Research

### STRIDE-per-Element Matrix (Microsoft canonical)
| DFD Element | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| Processes | X | X | X | X | X | X |
| Data Flows | | X | | X | X | |
| Data Stores | | X | | X | X | |
| External Entities | X | | X | | | |

**Open question**: Some sources include Repudiation for Data Stores (audit logging gaps). PRD uses Microsoft original (excludes it). Architect should confirm.

### STRIDE-to-CWE Mapping (top references per category)
- **Spoofing**: CWE-287, CWE-290, CWE-384, CWE-295
- **Tampering**: CWE-345, CWE-20, CWE-89, CWE-79, CWE-94
- **Repudiation**: CWE-778, CWE-223, CWE-532
- **Information Disclosure**: CWE-200, CWE-209, CWE-312, CWE-319
- **Denial of Service**: CWE-400, CWE-770, CWE-404, CWE-835
- **Elevation of Privilege**: CWE-269, CWE-862, CWE-863, CWE-250

### STRIDE-to-OWASP Top 10 Mapping
- S -> A07 (Identification & Auth Failures), T -> A03 (Injection), R -> A09 (Logging Failures)
- I -> A02 (Cryptographic Failures), D -> A06 (Vulnerable Components), E -> A01 (Broken Access Control)

### STRIDE-to-OWASP API Security 2023 Mapping
- S -> API2 (Broken Auth), T -> API3 (Broken Object Property Auth), R -> API9 (Improper Inventory)
- I -> API3 (Excessive Data Exposure), D -> API4 (Unrestricted Resource), E -> API1/API5 (Broken Object/Function Auth)

### Good vs Bad Finding Criteria
**Good**: Names specific component, concrete attack mechanism, states violated trust assumption, actionable mitigation with specific technology, framework cross-references
**Bad**: Generic component ("the system"), vague threat ("could be tampered"), non-actionable mitigation ("implement proper security"), missing framework grounding

### Common Pitfalls
1. Generic untargeted findings (no component specificity)
2. Missing STRIDE-per-Element compliance (wrong DFD targeting)
3. No risk scoring or prioritization
4. LLM variability producing inconsistent output
5. Lack of framework grounding (no CWE/OWASP/ATT&CK)

## Recommendations for Spec
- Lock STRIDE-per-Element matrix as hard validation constraint (FR-2 in PRD)
- Define explicit "good finding" vs "bad finding" quality criteria as validation rules
- Require CWE and ATT&CK identifiers embedded in detection patterns, not as separate lookup
- Include OWASP mapping tables in agent frontmatter for automatic citation
- Document known limitation: design-time analysis only (no runtime vulnerability detection)
- Validation against sample architecture (`examples/mermaid-agentic-app/input.md`) is the primary correctness check
- Each agent's `dfd_targets` frontmatter must match exactly one row of the STRIDE-per-Element matrix
