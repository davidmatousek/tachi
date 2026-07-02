---
prd_reference: docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED
    notes: "Faithful, complete translation of PRD v1.1 — 3/3 stories, 11/11 ACs, all 4 Architect constraints folded into FRs, 3/3 measurable SCs, no scope creep. Two non-blocking nits (priority-scale labels P1/P2/P3 vs PRD P0/P1; --dry-run Out item is scope-tightening beyond PRD Out list). Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Detect-Images Duplicate Cleanup — Opt-In Mislabeled-Image Removal

**Feature Branch**: `217-detect-images-duplicate-cleanup`
**Created**: 2026-07-01
**Status**: Draft
**Input**: User description: "PRD: 217 - detect-images-duplicate-cleanup"
**PRD**: `docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md` (Approved v1.1)
**Research**: `specs/217-detect-images-duplicate-cleanup/research.md`

## Context

Since #215/PR #216, the report-data extraction tool self-heals mislabeled infographic images (a `.jpg` whose bytes are PNG — the `gemini-2.5-flash-image` fallback-era signature) by writing a corrected sibling, deliberately non-destructively. Consequence (Issue #217): both the mislabeled original and its byte-identical corrected sibling persist forever — roughly 2× image storage per affected stem (up to 6 stems per assessment directory) plus path ambiguity. The affected population is frozen (the producer is already fixed); only legacy assessment directories carry pairs. This feature ships the PRD's decision: **option (c)** — an explicit opt-in `--cleanup-mislabeled-images` flag — **plus option (a)** — documentation of the sanctioned cleanup path. Option (b) (destructive-by-default) is rejected.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Opt-in cleanup of mislabeled duplicate images (Priority: P1)

When I run the report pipeline against a legacy assessment directory containing mislabeled/corrected duplicate pairs, I want an explicit opt-in cleanup that removes the mislabeled originals, so I can reclaim the duplicate storage and remove path ambiguity without hand-rolled `rm` one-liners.

**Why this priority**: This is the decided remedy for Issue #217 (PRD P0). Without it there is no sanctioned cleanup path, and adopters resort to the unsafe raw `find … rm` one-liner. Everything else in the feature (dogfood, docs) depends on this flag existing and being safe.

**Independent Test**: Can be fully tested by running the extraction tool with and without `--cleanup-mislabeled-images` against fixture directories seeded with mislabeled/corrected pairs, and asserting deletions, emitted image paths, stderr records, and exit codes.

**Acceptance Scenarios**:

1. **AC-1a — Given** `threat-baseball-card.jpg` with PNG bytes and a byte-identical `threat-baseball-card.png`, **When** extraction runs with `--cleanup-mislabeled-images`, **Then** the `.jpg` is deleted, the emitted image path is the `.png`, and one stderr line records the deletion.
2. **AC-1b — Given** the same directory, **When** extraction runs WITHOUT the flag, **Then** both files persist and emitted output is byte-identical to current behavior.
3. **AC-1c — Given** a mislabeled `.jpg` with no sibling yet, **When** extraction runs with the flag, **Then** the corrected sibling is written first and the original deleted only after byte-identity verification of the written sibling.
4. **AC-1d — Given** a `.jpg` and `.png` that are NOT byte-identical, **When** extraction runs with the flag, **Then** neither file is deleted (never guess which is authoritative).
5. **AC-1e — Given** a directory with only correctly-labeled images, **When** extraction runs with the flag, **Then** no deletions occur and no cleanup output is emitted.
6. **AC-1f — Given** a truncated/failed sibling copy in the recovery path (forced short copy), **When** extraction runs with the flag, **Then** the mislabeled original is NOT deleted and the run still exits 0 (byte-identity doubles as copy-success verification).
7. **AC-1g — Given** a cross-swapped pair (`.jpg` holds PNG bytes AND `.png` holds JPEG bytes), **When** extraction runs with the flag, **Then** no file is deleted (recovery-path deletion fires only when the corrected sibling did not pre-exist the copy).
8. **AC-1h — Given** a self-consistent `.jpg` and `.png` that are different legitimate images, **When** extraction runs with the flag, **Then** neither is deleted (the predicate keys on mislabeled-ness, not sibling-existence).

---

### User Story 2 - In-repo dogfood cleanup of the legacy snapshot (Priority: P2, gated)

When I maintain tachi itself, I want the in-repo legacy snapshot pairs cleaned via the new flag (dogfood), so the repo stops carrying 6 duplicate images (~6.75 MB) and demonstrates the sanctioned cleanup path.

**Why this priority**: Valuable (repo hygiene + living proof of the flag) but strictly downstream of User Story 1, and gated: OQ-2 resolved CLEAN (no test consumes the snapshot's images), with a documented defer fallback (AC-2b) if build-stage verification surfaces a consumer.

**Independent Test**: Can be fully tested by running the flag against `examples/agentic-app/test-output/2026-04-19T03-20-30/` and asserting the 6 mislabeled `.jpg` files are gone, the regenerated `report-data.typ` for that directory is byte-identical pre/post (path-invariance), and the extractor test module passes.

**Acceptance Scenarios**:

1. **AC-2a — Given** `examples/agentic-app/test-output/2026-04-19T03-20-30/` (6 mislabeled-`.jpg` + byte-identical corrected-`.png` pairs), **When** the flag runs against it, **Then** the 6 mislabeled `.jpg` files are removed and the safety proof is **path-invariance**: `report-data.typ` generated for that directory is byte-identical before and after cleanup, plus the extractor test module is green. (The backward-compat/byte-identity suites exclude this dir — they are hygiene, not proof.)
2. **AC-2b (fallback only — default is CLEAN per OQ-2) — Given** plan/build-stage verification surfaces a consumer of the snapshot images, **When** the consumer cannot be trivially satisfied, **Then** US-2 is deferred with documented rationale (Issue #217 comment) — do not force. `[MANUAL-ONLY] defer decision is a human judgment call, not an automatable assertion`

---

### User Story 3 - Documented duplicate-pair expectation and sanctioned cleanup path (Priority: P3)

When I read the report-assembly docs as an adopter with legacy directories, I want the duplicate-pair expectation and the sanctioned cleanup command documented, so I know the duplicates are expected and how to remove them safely.

**Why this priority**: Documentation completes Issue #217's option (a) acceptance but delivers value only once the flag (User Story 1) exists.

**Independent Test**: Can be fully tested by inspecting the report-assembly reference surface for the duplicate-pair origin, the flag invocation, and the double-gate safety semantics.

**Acceptance Scenarios**:

1. **AC-3a — Given** the report-assembly reference docs (`.claude/skills/tachi-report-assembly/references/`), **When** I look up legacy image handling, **Then** the duplicate-pair origin (gemini-2.5-flash-image fallback era), the flag invocation, and the double-gate safety semantics are documented, and the raw `find … rm` one-liner is NOT the recommended path.

---

### Edge Cases

- **Non-identical pair** (AC-1d): `.jpg` and `.png` differ in content → no deletion; never guess which is authoritative.
- **Truncated/failed recovery copy** (AC-1f): written sibling fails byte-identity → original preserved, run exits 0; verification doubles as copy-success check.
- **Cross-swapped pair** (AC-1g): both files mislabeled in opposite directions → no deletion; recovery-write deletion is additionally gated on the sibling not having pre-existed the copy, preventing amplification of the pre-existing overwrite behavior into data loss.
- **Legitimate mixed pair** (AC-1h): self-consistent `.jpg` and `.png` of different images → never touched; the predicate keys on mislabeled-ness (content format ≠ extension), not sibling existence.
- **Direction-agnostic rule**: a `.png` holding JPEG bytes is handled the same as a `.jpg` holding PNG bytes.
- **Zero-byte files**: existing candidate validation (non-zero size) is preserved; zero-byte files are never cleanup candidates or counterparts.
- **Deletion failure** (permissions, races): logged to stderr per file, extraction continues and succeeds; emitted output is identical whether cleanup succeeds or not (best-effort).
- **Directory with only correct labels** (AC-1e): flag is a no-op, no cleanup output.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

- **FR-001 (Opt-in flag)**: The report-data extraction tool MUST accept an explicit `--cleanup-mislabeled-images` opt-in flag. Without the flag, behavior MUST be byte-identical to today across emitted output, files on disk, stderr, and exit codes (safe default preserved; Constitution Principle III).
- **FR-002 (Double gate)**: With the flag, the tool MUST delete a file only when BOTH conditions hold: (1) the flag is present, AND (2) a correctly-labeled counterpart exists whose content is byte-identical to the mislabeled file. No code path may delete without both gates (SC-3).
- **FR-003 (Mislabeled predicate, direction-agnostic)**: The deletion predicate MUST key on mislabeled-ness — delete X iff X's content format ≠ X's extension AND a correctly-labeled byte-identical counterpart Y exists. The rule MUST be direction-agnostic (`.jpg` holding PNG bytes and `.png` holding JPEG bytes handled identically). Legitimate self-consistent pairs of different images MUST never be touched (AC-1h).
- **FR-004 (Both moments)**: Cleanup MUST be wired into BOTH moments where a mislabeled/corrected pair can exist: (a) **pre-existing pairs** — the correctly-labeled sibling already exists from an earlier run (the primary legacy case, including the entire User Story 2 target); and (b) **recovery-write time** — the corrected sibling is written this run, verified byte-identical, and only then is the original deleted, additionally gated on the sibling not having pre-existed the copy (AC-1g). Wiring only the recovery moment silently misses the primary case and does NOT satisfy this requirement.
- **FR-005 (Logging & best-effort)**: Each deletion MUST emit exactly one stderr record naming the deleted path. A per-file deletion failure MUST be logged to stderr and MUST NOT fail the extraction (exit code and emitted output unaffected).
- **FR-006 (Caller compatibility)**: The flag MUST thread into the detection routine as a defaulted parameter (`cleanup` defaulting to off) so all existing callers — including the direct two-positional-argument test call — remain valid and behaviorally unchanged without modification.
- **FR-007 (Safety-negative test coverage)**: The test suite MUST include dedicated automated cases for AC-1a through AC-1h, including each safety negative: non-identical pair (AC-1d), truncated copy (AC-1f), cross-swap (AC-1g), and mixed legitimate pair (AC-1h).
- **FR-008 (Dogfood cleanup, gated)**: The 6 mislabeled `.jpg` files in `examples/agentic-app/test-output/2026-04-19T03-20-30/` MUST be removed using the new flag, with path-invariance proof (`report-data.typ` byte-identical pre/post) and the extractor test module green (AC-2a). If verification surfaces a snapshot-image consumer, US-2 MUST be deferred with documented rationale instead of forced (AC-2b).
- **FR-009 (Documentation)**: The report-assembly reference surface MUST document the duplicate-pair origin, the sanctioned flag invocation, and the double-gate safety semantics, and MUST NOT recommend the raw `find … rm` one-liner (AC-3a).

### Key Entities

- **Mislabeled image**: an image file whose extension contradicts its content format (detected by magic-byte probe) — the `gemini-2.5-flash-image` fallback-era signature; the only deletion candidate.
- **Corrected sibling / counterpart**: the correctly-labeled file for the same stem whose content is byte-identical to the mislabeled image; its existence and byte-identity are the second deletion gate, and it is the surviving referenced path.
- **Assessment directory**: a report-pipeline target directory holding up to 6 known infographic stems; the unit against which detection and cleanup run.
- **Cleanup record**: the one-line stderr entry emitted per deletion (and per deletion failure), the operator-facing audit trail.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Cleanup efficacy)**: In a flagged run against a directory with mislabeled/corrected duplicate pairs, duplicate pairs go N → 0 (in-repo target: 6 → 0, subject to the US-2 gate).
- **SC-002 (Zero default-path regression)**: Without the flag, the existing extractor test suite is green and emitted `report-data.typ` is byte-identical on the frozen snapshot — no observable behavior change for any current user or caller.
- **SC-003 (Deletion safety, test-enforced)**: No code path deletes a file without BOTH the flag and byte-identity proof; AC-1d, AC-1f, AC-1g, and AC-1h are each covered by a dedicated automated test.

## Scope

**In (P0)**: opt-in cleanup flag; double-gated, direction-agnostic deletion covering both moments (pre-existing pairs + recovery write); per-deletion stderr record; best-effort error handling; automated tests for AC-1a–AC-1h.
**In (P1)**: US-2 gated in-repo dogfood cleanup with path-invariance proof; US-3 report-assembly reference documentation.

**Out of scope**:
- Option (b) — destructive-by-default behavior (copy → move) in any form.
- Producer-side changes (the infographic-generation agent is already fixed by #215/#216).
- Cleanup of anything beyond the known infographic stems in the target directory (no generic directory janitor).
- Auto-passing the flag from the report-assembler agent — deletion stays a human opt-in decision (OQ-1: default NO; revisit on adopter signal).
- A standalone cleanup script (the magic-byte probe already lives in the extraction tool).
- A `--dry-run` companion mode — the no-flag run is the safe default; industry research notes the pattern, deferred alongside OQ-1 on adopter signal.

## Assumptions

- The affected population is frozen: the producer is fixed, so only legacy assessment directories hold pairs (verified in PRD; bounded at one extra file per stem).
- OQ-2 is answered CLEAN (Architect, 2026-07-01): no test consumes the snapshot's images; US-2 proceeds with AC-2b retained as a documented fallback only.
- OQ-1 is answered default NO: the report-assembler agent never auto-passes the flag.
- Deleted content is always recoverable: the byte-identical survivor remains on disk and git history retains the deleted in-repo files (wasting-asset rule satisfied).
- The existing zero-byte candidate validation and template-relative image-path emission contracts are preserved unchanged; cleanup only removes files that are never selected for emission.
