# Architect Review: plan.md for Feature 120

**Reviewer**: Architect Agent
**Date**: 2026-04-09
**Artifact**: `specs/120-architecture-lifecycle-command/plan.md`
**Spec Reference**: `specs/120-architecture-lifecycle-command/spec.md`

---

## Review Summary

| Dimension | Verdict |
|-----------|---------|
| Architecture Soundness | PASS |
| Integration Points | CONCERN — step numbering mismatch |
| Backward Compatibility | PASS |
| Checksum Implementation | PASS with advisory |
| Archive Mechanism | PASS |
| Data Flow Diagram | CONCERN — accuracy gap |
| Risk Assessment | PASS |
| Knowledge System Conventions | PASS |

**Overall**: APPROVED WITH CONCERNS (2 non-blocking concerns requiring documentation fixes before implementation)

---

## Detailed Findings

### Finding 1: Step Numbering Mismatch in Threat Model Integration [CONCERN — Non-blocking]

**Location**: plan.md, "Part 2: Architecture Snapshot in Threat Model", Step 1.4 description (lines 144-153)

The plan refers to "Step 1.3 (output directory creation)" as the insertion point for the new snapshot step. However, the actual `tachi.threat-model.md` command uses a different numbering scheme:

- **Step 0: Parse Flags** -- item 7 computes the timestamp and sets the output_dir path (this is the "unique run folder" creation)
- **Step 1: Validate Prerequisites** -- item 3 creates the output_dir directory via `mkdir -p` equivalent

The plan references "Step 1.3" as though there are sub-steps labeled "Step 1.1", "Step 1.2", "Step 1.3". In reality, Step 1 uses a numbered list (1, 2, 3) without sub-step labels. The correct insertion point is between Step 1 item 3 (output directory creation/validation) and Step 2 (Run Threat Analysis).

**Risk**: An implementer reading the plan might look for a labeled "Step 1.3" and be confused by the mismatch with the actual command file structure.

**Recommendation**: Update the plan to reference "Step 1, item 3 (output directory creation)" or simply "after Step 1 completes and before Step 2 begins". When implementing, the new snapshot step should be added as item 4 under Step 1, or as a new "Step 1.5" section between Step 1 and Step 2. The plan-research.md (Decision 4) correctly describes the intent; the plan.md references need to match the actual command structure.

---

### Finding 2: Mermaid Data Flow Diagram Accuracy [CONCERN — Non-blocking]

**Location**: plan.md, "Data Flow" section, Mermaid diagram (lines 156-177)

The diagram has a structural omission:

1. **Missing "abort" path from Guided Update**: The plan text (Step 0b, item 5) specifies: "If user indicates no changes across all categories: abort update, leave file untouched." The Mermaid diagram shows `G[Guided update P1]` flowing only to `H[Generate updated architecture]` with no abort/exit path. This should include a conditional branch from G that exits the flow when no changes are indicated.

2. **Checksum step ordering**: The diagram shows `I[Inject frontmatter]` flowing to `J[Compute SHA-256 checksum]`. In practice, the checksum must be computed on the body content *before* the frontmatter is injected (since the checksum is a field within the frontmatter). The plan text (Step 3a) correctly states "Extract the markdown body... compute `shasum -a 256` on the body content" -- the diagram should reflect that computation precedes injection, not follows it. The correct flow is: Generate content -> Compute SHA-256 -> Assemble frontmatter (with checksum) -> Write file.

**Risk**: Implementers using the diagram as a quick reference may get the ordering wrong, though the detailed text is correct.

**Recommendation**: (a) Add an abort path from the Guided Update node. (b) Reorder the checksum/frontmatter nodes so that checksum computation precedes frontmatter assembly. This is a documentation accuracy fix -- the detailed step descriptions are correct.

---

### Finding 3: shasum Pipe Pattern Needs Explicit Specification [ADVISORY]

**Location**: plan.md, Step 3a "Checksum computation" (lines 133-134)

The plan says: "write to a temp variable, compute `shasum -a 256` on the body content, prefix with `sha256:`"

The phrase "write to a temp variable" is ambiguous in the context of a Claude Code command file, where the agent executes Bash commands via the Bash tool. In practice, the implementation will need to:

1. Extract the body (everything after the closing `---` of frontmatter)
2. Pipe or echo the body content into `shasum -a 256`
3. Parse the hex digest from the output (shasum outputs `<hash>  -` when reading stdin)

The plan-research.md (Decision 2) correctly identifies the tool but does not specify the pipe pattern. Since `shasum -a 256` reads from stdin or a file, and the body content exists in the agent's context (not yet written to disk), the implementation will likely use `echo` piped to `shasum`, or write the body to a temp file first.

**Risk**: Low. The agent implementing this will determine the correct pipe pattern. However, for a first-time generation, the body content is in memory (not yet on disk), so a file-based `shasum` invocation requires writing the file first and then computing the hash.

**Recommendation**: Consider specifying the two-pass write pattern explicitly: (1) write the body content to the output path without frontmatter, (2) run `shasum -a 256 <output_path>` to get the hash, (3) prepend the assembled frontmatter (with the computed hash) to the file. This avoids echo/pipe issues with large markdown bodies containing special characters.

---

### Finding 4: Architecture Soundness — Two-Part Design [PASS]

The separation into Part 1 (lifecycle management in `/tachi.architecture`) and Part 2 (snapshot in `/tachi.threat-model`) is architecturally sound:

- **Single Responsibility**: Each command gains one focused capability. The architecture command manages version lifecycle; the threat-model command captures a point-in-time snapshot.
- **Decoupled**: The snapshot is informational only -- it does not affect the orchestrator's behavior or any downstream pipeline stage. This is the correct design; coupling the snapshot to orchestrator input would create fragile dependencies.
- **Append-Only Archive**: The `.archive/vN/` structure is sound for local-first, single-user workflows. Version directories are immutable after creation (with idempotent retry support for the same version number).
- **No Schema Changes**: The plan correctly avoids modifying any output schemas, parser functions, or agent definitions. Frontmatter is produced but not consumed by downstream stages.

---

### Finding 5: Backward Compatibility [PASS]

The plan correctly handles all backward compatibility scenarios:

- **Legacy files (no frontmatter)**: Treated as v0, archived before upgrade to v1. This preserves the pre-versioning content.
- **Example files**: Explicitly excluded from modification (FR-021). The 3 example architectures (`examples/agentic-app/architecture.md`, `examples/microservices/architecture.md`, `examples/web-app/architecture.md`) remain unchanged.
- **Orchestrator transparency**: The orchestrator receives architecture content via `<architecture-input>` tags in the Step 2 prompt. YAML frontmatter is indistinguishable from free text to the format detector (Phase 1 of orchestrator). Confirmed by reading the orchestrator agent definition.
- **Downstream stages**: All downstream stages (risk-scorer, control-analyzer, infographic, report-assembler) consume `threats.md`, not `architecture.md`. No changes needed.

---

### Finding 6: Checksum Implementation [PASS]

- `shasum -a 256` is available on macOS (confirmed: `/usr/bin/shasum`, version 6.02) and most Linux distributions.
- `sha256sum` is also available on the test platform (confirmed: `/sbin/sha256sum`).
- The `sha256:` prefix convention is clear and unambiguous.
- Body-only hashing (excluding frontmatter) is the correct approach -- it means the checksum verifies content integrity independent of metadata changes.

---

### Finding 7: Archive Mechanism [PASS]

- **Path derivation**: `{parent_dir}/.archive/v{N}/{filename}` is correct. Using the architecture file's parent directory means archives stay co-located with the source file regardless of where it lives.
- **Dot-prefix convention**: `.archive/` follows standard Unix hidden directory conventions. Consistent with `.aod/`, `.claude/`, `.github/` patterns already in the project.
- **Idempotent retry**: Overwriting the same version number in the archive (e.g., re-archiving v3 if a previous run failed) is the right choice for resilience.
- **No cleanup mechanism needed for MVP**: Archive is append-only and local-only. Disk space management is out of scope and appropriate for a single-user tool.

---

### Finding 8: Risk Assessment [PASS]

The four risks identified in the plan are well-calibrated:

1. **Frontmatter breaks orchestrator**: Correctly assessed as Low/Medium. The `<architecture-input>` tag mechanism means the orchestrator treats the entire file as text input, not parsed YAML.
2. **Archive path conflicts**: Correctly assessed as Low/Low. The dot-prefix convention is standard.
3. **shasum unavailable**: Correctly assessed as Low/Low. Both `shasum` and `sha256sum` are available on the target platform.
4. **Guided update complexity**: Correctly assessed as Medium/Low and correctly deferred to P1. The core versioning mechanism is independent of the guided update UX.

One risk not explicitly listed but implicitly handled: **frontmatter corruption on partial write** (e.g., if the agent crashes mid-write). The archive-before-overwrite pattern mitigates this -- the previous version is always preserved before the new write begins.

---

### Finding 9: Knowledge System Conventions [PASS]

- **Command-per-workflow**: Each command maintains a single responsibility. `/tachi.architecture` handles lifecycle; `/tachi.threat-model` handles analysis with snapshot.
- **No new commands**: The plan correctly modifies existing commands rather than creating new ones (e.g., no `/tachi.archive` or `/tachi.snapshot` commands).
- **No agent modifications**: The orchestrator, threat agents, and report agents are untouched. Correct for a feature that adds metadata management at the command layer.
- **Build-time/run-time separation**: Both modified commands are run-time product commands. No AOD lifecycle commands are affected.
- **Phase ordering**: P0 (versioning + snapshot) before P1 (guided update UX) is the correct dependency ordering.

---

## Concerns Summary

| # | Type | Severity | Finding | Blocking? |
|---|------|----------|---------|-----------|
| 1 | Documentation | Low | Step numbering mismatch with actual threat-model command structure | No |
| 2 | Documentation | Low | Mermaid diagram missing abort path and incorrect checksum ordering | No |
| 3 | Advisory | Informational | Checksum pipe pattern could be more explicit | No |

---

## Sign-off

**STATUS**: APPROVED_WITH_CONCERNS

The architecture is sound. The two-part design (lifecycle + snapshot) correctly separates concerns, the archive mechanism is well-designed, backward compatibility is preserved, and no downstream pipeline changes are needed. The two non-blocking concerns are documentation accuracy issues in the plan (step numbering reference and Mermaid diagram accuracy) that should be corrected before implementation to avoid implementer confusion, but do not affect the architectural validity of the design.
