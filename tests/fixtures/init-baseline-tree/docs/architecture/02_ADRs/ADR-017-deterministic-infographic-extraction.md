# ADR-017: Deterministic Infographic Data Extraction with Shared Parser Module

**Status**: Accepted
**Date**: 2026-03-30
**Deciders**: Architect
**Feature**: 071 (Deterministic Infographic Extraction)

---

## Context

Since Feature 018, the threat-infographic agent performed data extraction inline using LLM-based markdown parsing. This created three problems:

1. **Non-deterministic output**: The same threat model inputs could produce different infographic data on each run. Severity percentages, finding selections, and heat map values varied due to LLM interpretation differences. This made infographic output unreliable for audit trails and regression testing.

2. **Duplicated parsing logic**: Feature 067 introduced `extract-report-data.py` for deterministic report data extraction, implementing markdown table parsers, frontmatter parsers, severity distribution parsers, and finding extractors. The infographic agent duplicated this same parsing logic via LLM prompting, creating divergence risk where the same source artifact could be interpreted differently by the report and infographic pipelines.

3. **Percentage rounding errors**: LLM-based percentage calculation produced values that did not always sum to exactly 100, creating visual inconsistencies in pie charts and severity distribution displays.

Feature 067 had already proven the deterministic extraction pattern for the security report pipeline, establishing that Python stdlib-only scripts could replace LLM-based parsing with byte-identical reproducibility.

---

## Decision

Replace LLM-based data extraction in the infographic agent with a deterministic Python script (`scripts/extract-infographic-data.py`) and extract shared parsing logic into a reusable module (`scripts/tachi_parsers.py`).

Key design choices:

1. **Shared parser module**: Common parsing functions (markdown tables, YAML frontmatter, severity distributions, findings, scope data, compensating controls) extracted from `extract-report-data.py` into `tachi_parsers.py`. Both scripts import from the same module, guaranteeing identical interpretation of the same source artifacts.

2. **Largest Remainder Method for percentages**: Integer percentage rounding uses the Largest Remainder Method (also known as the Hamilton method), which guarantees the sum equals exactly the target (100). Ties are broken by lexicographic label order for deterministic output.

3. **JSON output format**: The extraction script outputs JSON (not Typst data format) because infographic templates are markdown specifications, not compiled documents. JSON is the natural interchange format for the agent to consume.

4. **No LLM fallback**: If the extraction script fails (exit code 1 or 2), the agent must halt. No manual LLM-based extraction is permitted as a fallback, because the script's validation catches data integrity issues that LLM extraction would silently propagate.

---

## Rationale

### Why deterministic extraction (not keep LLM-based)?

1. **Reproducibility**: Security infographics serve as audit artifacts. Byte-identical output on identical inputs enables regression testing and change detection. When the underlying threat model does not change, the infographic data must not change.

2. **Proven pattern**: Feature 067 validated this approach for the report pipeline. The infographic pipeline shares the same source artifacts and the same parsing requirements. Applying the same solution reduces architectural divergence.

3. **Cross-pipeline consistency**: With both pipelines importing `tachi_parsers.py`, a severity count of "5 Critical" in `threats.md` is guaranteed to be parsed as 5 in both the report and the infographic. LLM-based parsing offered no such guarantee.

### Why extract a shared parser module (not duplicate)?

1. **Single source of truth**: Parsing logic for tachi markdown artifacts exists in one place. Bug fixes and format changes propagate to both consumers automatically.

2. **Feature 067 already contained the parsers**: The extraction was a refactoring operation, not new development. The parsers were proven correct by Feature 067's validation suite.

3. **Future extensibility**: Additional scripts that need to parse tachi artifacts (e.g., for dashboards or CI integrations) can import from the same module.

### Why Largest Remainder Method (not simple rounding)?

1. **Guaranteed sum**: Simple `round()` can produce percentages summing to 99 or 101 when applied independently to each value. The Largest Remainder Method distributes the rounding remainder across items, guaranteeing the target sum.

2. **Deterministic tie-breaking**: When two items have equal fractional remainders, lexicographic label ordering provides stable, reproducible tie resolution. No random or insertion-order dependencies.

3. **Established method**: Used in proportional representation systems (parliamentary seat allocation) for the same mathematical property -- distributing integer counts that must sum to a fixed total.

---

## Alternatives Considered

### Alternative 1: Keep LLM-Based Extraction, Add Validation Post-Hoc

**Pros**:
- No new scripts; simpler deployment
- LLM can handle format variations gracefully

**Cons**:
- Non-deterministic output remains (validation can reject but not fix)
- Duplicated parsing logic between report and infographic pipelines
- Percentage rounding still unreliable

**Why Not Chosen**: Validation without correction creates a retry loop. The LLM may produce different (still wrong) output on retry, leading to non-convergent behavior.

### Alternative 2: Deterministic Script Without Shared Module

**Pros**:
- Simpler dependency graph (each script is self-contained)
- No import path management

**Cons**:
- ~750 lines of parsing logic duplicated between two scripts
- Bug fixes must be applied in two places
- Divergence risk reintroduced at the code level

**Why Not Chosen**: The duplication cost exceeds the import complexity cost. Python's module system handles same-directory imports cleanly with `sys.path` adjustment.

### Alternative 3: Jinja2 or YAML Templates Instead of JSON Output

**Pros**:
- Richer output formatting options
- Template-level logic for conditional sections

**Cons**:
- Introduces external dependencies (violates zero-dependency constraint)
- JSON is sufficient and directly consumable by the agent

**Why Not Chosen**: The zero-dependency constraint is a hard requirement for adopter portability. JSON via `json.dumps()` is stdlib.

---

## Consequences

### Positive
- Infographic data extraction is byte-identical on identical inputs, enabling regression testing and audit trails
- Shared parser module eliminates parsing logic duplication between report and infographic pipelines
- Percentage values always sum to exactly 100 via Largest Remainder Method
- Zero external dependencies maintained (Python stdlib only)
- Validation catches data integrity issues before they reach the specification

### Negative
- Agent must invoke a Python script before generating specifications (additional step in the workflow)
- Shared module creates a coupling point -- changes to `tachi_parsers.py` affect both pipelines
- No graceful degradation: script failure halts infographic generation entirely

### Mitigation
- Script invocation is a single command with clear exit codes; the agent handles all three exit paths
- Shared module coupling is intentional -- it ensures consistency, and changes are tested against both consumers
- Halt-on-failure is the correct behavior: data integrity issues should not be silently propagated to visual outputs

---

## Related Decisions

- [ADR-016: Infographic Pipeline Decoupling](ADR-016-infographic-pipeline-decoupling.md) -- established the standalone `/infographic` command that this ADR's extraction script integrates with
- [ADR-014: Gemini API Optional Image Generation](ADR-014-gemini-api-optional-image-generation.md) -- spec-first architecture and graceful degradation remain in effect; deterministic extraction applies to the specification data, not the image generation step

---

## References

- Feature 071 spec: `specs/071-deterministic-infographic-extraction/spec.md`
- Feature 071 plan: `specs/071-deterministic-infographic-extraction/plan.md`
- Shared parser module: `scripts/tachi_parsers.py`
- Infographic extraction script: `scripts/extract-infographic-data.py`
- Report extraction script: `scripts/extract-report-data.py` (refactored to use shared module)
- Infographic agent: `.claude/agents/tachi/threat-infographic.md`
- Largest Remainder Method: Hamilton method for proportional allocation
