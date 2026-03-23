# Research Summary: SARIF Output Generation (Feature 012)

## Knowledge Base Findings

- **PAT-001 (Wave-Based Parallelism)**: Content-heavy features (markdown/YAML) have high parallelism potential. SARIF output is a content feature — wave-based execution applies.
- **PAT-002 (Parallel Agent Validation)**: Independent artifacts (result mapping, rule definitions, severity mapping, correlation representation) can be validated in parallel.
- **PAT-003 (Phased Delivery)**: Each user story should be independently testable. US-1 (core SARIF mapping) is viable without US-2-4.
- **Security skill SARIF precedent**: `.claude/skills/security/SKILL.md` Section 6d contains a working SARIF 2.1.0 writer implementation with JSON template + validation step — directly reusable as a pattern.

## Codebase Analysis

### Key Files
| File | Relevance |
|------|-----------|
| `schemas/finding.yaml` v1.0 | Finding IR schema (10 fields), explicitly names SARIF as consumer |
| `schemas/output.yaml` v1.1 | SARIF severity mapping table (lines 156-164) — Note-level fix needed |
| `agents/orchestrator.md` v1.1 | Phase 4 assembly — where SARIF generation instructions are added |
| `templates/threats.md` | Current markdown output template (7 sections + 4a) |

### Finding IR Schema (10 fields)
- `id`: Pattern `^(S|T|R|I|D|E|AG|LLM)-\d+$`
- `category`: 8 enum values (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm)
- `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`, `references`, `dfd_element_type`

### Category Naming → SARIF Rule ID Mapping (Resolved)
| IR category | SARIF rule ID suffix |
|------------|---------------------|
| `info-disclosure` | `information-disclosure` |
| `privilege-escalation` | `elevation-of-privilege` |
| All others | Same as IR category |

## Architecture Constraints

- **Prompt-only implementation**: All changes are orchestrator prompt instructions in markdown
- **Single-pass execution**: SARIF generated alongside threats.md in Phase 4 (Assess)
- **No application code**: No programming languages, frameworks, or compiled code
- **Orchestrator structure**: Phase 4 currently generates Coverage Matrix, Risk Summary, Recommended Actions — SARIF generation is added as a new step after the output structural validation

## Open Questions Resolved (from Spec)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Note-level severity | `note`/`"0.1"` (not `none`/`"0.0"`) | Keeps findings visible in GitHub as Low |
| partialFingerprints key | component+category (SHA-256 hash) | Category and component are deterministic; threat text varies |
| Taxonomies | P1 (Should Have) | GitHub doesn't display taxonomy data |
| JSON fidelity | Structural self-check in orchestrator prompt | Pattern from security skill SARIF writer |

## Industry Research Highlights

- **Dual-location strategy**: Mandatory — GitHub requires physicalLocation for display
- **GitHub-required rule properties**: shortDescription.text, fullDescription.text, help.text, help.markdown
- **security-severity**: Must be a numeric string (e.g., `"8.0"`)
- **Industry severity values**: PRD values (9.0, 8.0, 5.0, 2.0) align with Trivy and Checkov
