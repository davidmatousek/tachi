# ADR-015: Platform Adapter Hub-and-Spoke Distribution Pattern

**Status**: Accepted
**Date**: 2026-03-23
**Deciders**: Architect
**Feature**: 021 (Platform Adapters)

---

## Context

Tachi's 14 threat agent prompts (`agents/`) are authored in a single canonical format: markdown with YAML frontmatter following tachi's own metadata conventions. These agents work natively only when invoked by an LLM that reads the repository directly. Developers using other AI coding platforms -- Claude Code, Cursor, GitHub Copilot, GitHub Actions CI -- cannot use tachi's agents without manual reformatting into each platform's native file format.

Key constraints:
- Agent prompt content must be preserved exactly across all platforms. Any lossy transformation would change threat analysis behavior.
- Each target platform has a distinct file format, frontmatter schema, file extension, installation directory, and activation model.
- The canonical agent files in `agents/` must remain the single source of truth. Platform-specific copies must not diverge from the source over time.
- Some platforms impose size limits (Copilot: ~30K characters per agent file) that require structural adaptation without content loss.
- The GitHub Actions adapter is architecturally distinct: it invokes agents at runtime via LLM API rather than producing static file transformations.

---

## Decision

We will use a **hub-and-spoke distribution pattern** where `agents/` is the immutable hub and each platform adapter under `adapters/{platform}/` is a spoke that transforms hub content into platform-native format. All transformations are metadata-only: frontmatter translation, file extension changes, path rewriting, and (where required) size-aware splitting. Prompt content is never modified.

**Key design choices**:

1. **Immutable hub**: The 14 agent files in `agents/` are the canonical source. Adapters read from the hub and produce derived files. No adapter modifies the hub.

2. **Two adapter categories**: File-transformation adapters (Claude Code, Generic, Cursor, Copilot) produce static files that users install into their project. The CI integration adapter (GitHub Actions) produces a workflow that invokes agents at runtime -- no file transformation occurs.

3. **Metadata preservation via body section**: File-transformation adapters that support frontmatter (Claude Code, Cursor, Copilot) replace tachi's YAML frontmatter with platform-specific frontmatter and relocate tachi metadata to a `## Metadata` section in the markdown body. This preserves all tachi-specific fields (category, threat_class, dfd_targets, owasp_references, output_schema) without conflicting with platform frontmatter requirements.

4. **Path rewriting by installation depth**: Internal references to schemas, templates, and sibling agents are rewritten based on the adapter's installation depth from the project root. All three platform adapters install 3 levels deep (e.g., `.claude/agents/tachi/`), using `../../../` prefixes. Copilot instructions files install 2 levels deep, using `../../` prefixes. Rules are codified in `specs/021-platform-adapters/conventions.md`.

5. **Size-aware splitting for Copilot**: Agents exceeding Copilot's ~30K character limit (orchestrator at ~120K chars, threat-report at ~43K chars) are split into a compact `.agent.md` file plus a `.github/instructions/` companion file containing the full context. Copilot's built-in instructions loading mechanism bridges the two files.

6. **VERSION manifest for drift detection**: Each adapter includes a `VERSION` file with source commit SHA, generation timestamp, and per-agent SHA-256 checksums. This enables users to detect when adapter files have drifted from the hub source.

---

## Rationale

**Reasons**:
1. **Single source of truth**: The hub-and-spoke pattern ensures agent logic is authored and maintained in exactly one place (`agents/`). Changes propagate to all platforms through re-generation, not manual synchronization across 5 copies.
2. **Content fidelity**: By restricting transformations to metadata, paths, and extensions, the pattern guarantees that all platforms execute identical threat analysis logic. Output parity is an architectural invariant, not a testing aspiration.
3. **Platform independence**: Each adapter encapsulates all platform-specific knowledge (frontmatter schema, file extension, activation model, size limits). Adding a new platform requires only a new spoke, not changes to the hub or other spokes.
4. **Existing pattern extension**: Tachi already uses a hub-and-spoke model where `agents/` produces findings conforming to `schemas/`, and `templates/` consumes them. The adapter layer extends this same pattern to distribution, keeping the architecture conceptually unified.
5. **Drift visibility**: The VERSION manifest makes adapter staleness explicit. Without it, users would silently run outdated agent logic with no way to detect divergence from the current hub state.

---

## Alternatives Considered

### Alternative 1: Multi-Format Source Agents

Author each agent once in a format-agnostic intermediate representation, then compile to all target formats.

**Pros**:
- Clean separation between content and format
- Could automate generation with a build tool

**Cons**:
- Introduces a new intermediate representation that must be maintained
- Agent authors would need to learn a custom format instead of standard markdown
- Build step adds complexity; current agents work directly as prompts
- The "compilation" would still need the same per-platform transformation logic

**Why Not Chosen**: The canonical markdown format is already the simplest possible representation. Adding an intermediate layer doubles the abstraction without reducing the transformation work.

### Alternative 2: Symlinks or Includes

Use filesystem symlinks or platform-specific include mechanisms to reference `agents/` files directly from platform directories.

**Pros**:
- Zero duplication; always reads the latest source
- No drift detection needed

**Cons**:
- Most target platforms do not support symlinks or includes in their agent file directories
- Copilot and Cursor require specific frontmatter that cannot be injected via symlink
- Git symlinks are fragile across operating systems (Windows)
- Does not solve the frontmatter translation or size-splitting requirements

**Why Not Chosen**: Platform file format requirements (frontmatter, extensions, size limits) make direct file sharing impossible. Each platform needs derived files with platform-specific adaptations.

### Alternative 3: Runtime Translation Layer

Build a runtime adapter that reads `agents/` files and translates on the fly when a platform requests an agent.

**Pros**:
- Always up to date; no static files to maintain
- No VERSION/drift concern

**Cons**:
- Requires a running service or CLI tool -- violates tachi's zero-runtime-dependency principle
- Adds latency to agent loading
- Platforms expect static files at known paths; runtime injection is not supported by Claude Code, Cursor, or Copilot
- GitHub Actions adapter already uses runtime invocation where appropriate

**Why Not Chosen**: Target platforms require static files at fixed filesystem paths. A runtime layer cannot satisfy this constraint.

---

## Consequences

### Positive
- All 5 target platforms receive tachi agents in their native format with zero manual reformatting
- Agent logic is maintained in exactly one place; changes propagate through re-generation
- The VERSION manifest provides explicit drift detection for adapter consumers
- The pattern is extensible: new platforms require only a new spoke adapter, no hub changes
- Output parity across platforms is an architectural guarantee, not a testing hope

### Negative
- Adapter files are derived copies that can become stale if not regenerated after hub changes
- Five sets of platform-specific files increase repository size (though all are text/markdown)
- The conventions document (`specs/021-platform-adapters/conventions.md`) must be consulted for any new adapter, adding onboarding overhead

### Mitigation
- VERSION manifest makes staleness explicit; `scripts/generate-adapter-version.sh` automates regeneration
- Repository size impact is minimal (text files, typically <200KB per adapter)
- Conventions document is a single reference covering all transformation rules; it reduces ambiguity rather than adding complexity

---

## Related Decisions

- ADR-003: STRIDE-per-Element Dispatch (defines the agent dispatch pattern that adapters preserve)
- ADR-013: SARIF Output Format Adoption (GitHub Actions adapter uploads SARIF to Code Scanning)

---

## References

- Feature 021 spec: `specs/021-platform-adapters/spec.md`
- Feature 021 plan: `specs/021-platform-adapters/plan.md`
- Adapter conventions: `specs/021-platform-adapters/conventions.md`
- Claude Code agent format: https://docs.anthropic.com/en/docs/claude-code/agents
- Cursor rules format: https://docs.cursor.com/context/rules
- GitHub Copilot custom agents: https://docs.github.com/en/copilot/customizing-copilot/adding-custom-agents-for-copilot-coding-agent
- GitHub Code Scanning SARIF upload: https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github
