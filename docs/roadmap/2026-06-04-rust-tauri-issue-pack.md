# Rust/Tauri Migration Issue Pack

Status: archived completion record

This issue pack is complete and retained for provenance only. New
execution work belongs in
[the 2026-06-15 parity remediation roadmap](2026-06-15-rust-tauri-parity-remediation-roadmap.html.md).

**Last Updated**: 2026-06-14
**Purpose**: tracker-neutral backlog cards for the Rust/Tauri parity track
**Architecture Guardrail**: keep `tachi-rust` Rust and Tauri based

## Progress Snapshot

- Current completion: 9/9 issue cards, or 100%.
- RT-003, RT-004, RT-006, RT-007, and RT-008 now have merged Rust slices for threat parsing, attack-chain parsing, the thin `src-tauri` shell scaffold, SARIF emission, and MAESTRO/OWASP taxonomy data.
- RT-005 is complete, and RT-009 is complete after the docs refresh and retirement pass.
- The navigation hub now lives at [implementation-backlog.md](./implementation-backlog.md) and points at the canonical roadmap, issue pack, and issue-card set.
- The detailed Rust/Tauri implementation roadmap now lives at [2026-06-08-rust-tauri-only-roadmap.md](./2026-06-08-rust-tauri-only-roadmap.md) and expands the remaining Rust/Tauri implementation work into BEADS-style epics, features, capabilities, tasks, and functions.
- The execution-level issue card set now lives at [2026-06-08-rust-tauri-only-issue-cards.md](./2026-06-08-rust-tauri-only-issue-cards.md) and sequences the migration into task-sized Beads templates.

GitHub Issues are not the source of truth in this repository right now, so the
items below are written as importable issue cards rather than live issues.

## Pack Format

Each card includes:

- `Title`
- `Priority`
- `Labels`
- `Summary`
- `Acceptance`
- `Depends on`

## Issue Cards

### RT-001 - Publish the Rust/Tauri parity contract

- **Priority**: P0
- **Labels**: `rust`, `tauri`, `parity`, `docs`
- **Summary**: Build a feature-family parity map from the shipped surface in
  README, docs, scripts, and tests, and bind each family to a Rust owner target.
- **Acceptance**:
  - Every shipped feature family appears in the parity matrix.
  - The matrix states that the repo remains Rust and Tauri based.
  - The roadmap references the parity matrix directly.
- **Depends on**: none

### RT-002 - Extend Rust-native test taxonomy and e2e boundary

- **Priority**: P0
- **Labels**: `rust`, `testing`, `coverage`, `tauri`
- **Summary**: Keep the current pytest inventory classified as unit,
  integration, smoke, true end-to-end, and support/regression while defining
  the Rust/Tauri harness boundary.
- **Acceptance**:
  - Coverage reporting explicitly excludes fixture-tree copies.
  - The audit reports active-module count and category counts.
  - The Tauri e2e boundary is documented, even if the harness is not present
    yet.
- **Depends on**: RT-001

### RT-003 - Port deterministic parsing and report extraction into Rust

- **Priority**: P1
- **Labels**: `rust`, `core`, `reports`, `parity`
- **Summary**: Move the deterministic parsing and report-data generation
  surfaces into `tachi-core`.
- **Acceptance**:
  - Frozen fixtures reproduce current output.
  - Report extraction behavior stays stable across the Rust port.
- **Depends on**: RT-001, RT-002

### RT-004 - Port attack-chain and pattern-analysis surfaces into Rust

- **Priority**: P1
- **Labels**: `rust`, `analysis`, `parity`, `security`
- **Summary**: Move attack-chain extraction, pattern synthesis, and classification
  logic into Rust.
- **Acceptance**:
  - Rust fixtures cover attack-chain and pattern-analysis behavior.
  - The parity contract names the shipped pattern families explicitly.
- **Depends on**: RT-001, RT-002

### RT-005 - Port install, init, update, and bootstrap command handlers

- **Priority**: P1
- **Labels**: `rust`, `cli`, `bootstrap`, `tauri`
- **Summary**: Move the control-plane scripts into Rust command handlers so
  Python stops being the canonical entry point.
- **Acceptance**:
  - Rust commands preserve the current CLI contract.
  - Install/init/update workflows run through shared Rust logic.
- **Depends on**: RT-001, RT-002

### RT-006 - Add a thin Tauri shell around the Rust core

- **Priority**: P1
- **Labels**: `rust`, `tauri`, `desktop`, `shell`
- **Summary**: Introduce a `src-tauri` shell that calls shared Rust code
  without duplicating business logic in the frontend.
- **Acceptance**:
  - The `src-tauri` shell exists and routes through the shared Rust bridge.
  - Desktop commands call the same Rust core used by CLI paths.
  - The shell remains thin.
- **Depends on**: RT-003, RT-005

### RT-007 - Port SARIF, coverage attestation, and coverage catalog surfaces

- **Priority**: P1
- **Labels**: `rust`, `sarif`, `coverage`, `maestro`
- **Summary**: Move SARIF emitters, coverage attestation, and coverage family
  data into Rust.
- **Acceptance**:
  - Rust artifacts match current shipped outputs.
  - Coverage and attestation reporting remain available from Rust.
- **Depends on**: RT-003, RT-004

### RT-008 - Rehost MAESTRO and OWASP coverage data in Rust

- **Priority**: P1
- **Labels**: `rust`, `taxonomy`, `owasp`, `maestro`
- **Summary**: Model the current OWASP and MAESTRO coverage families in Rust
  so the reports and docs can share one source of truth.
- **Acceptance**:
  - Rust has explicit domain data for the coverage families.
  - The coverage matrix can be generated from shared Rust data.
- **Depends on**: RT-001, RT-003

### RT-009 - Refresh docs and retire legacy compatibility paths

- **Priority**: P2
- **Labels**: `rust`, `docs`, `cleanup`, `migration`
- **Summary**: Update quickstarts, roadmap, backlog, and release docs after
  parity lands, then retire legacy shims and stale instructions.
- **Acceptance**:
  - Canonical docs point at Rust/Tauri commands.
  - Legacy compatibility paths are explicitly transitional or removed.
- **Depends on**: RT-006, RT-007, RT-008

## Import Notes

- Use the RT-### identifier as a stable tracker reference.
- Keep RT-001 through RT-002 as the planning baseline.
- Do not treat this pack as a commitment to any non-Rust rewrite.
