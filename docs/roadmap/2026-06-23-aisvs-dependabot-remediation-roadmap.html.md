# AISVS Dependabot Remediation Roadmap

**Date**: 2026-06-23
**Scope**: current live Dependabot alert set, AISVS 1.0 control framework, and
TDD-backed backlog slices for `tachi-rust`
**Status**: active roadmap; phase 1-4 are implemented locally, phase 0
remains blocked on upstream `gtk`/`glib` compatibility, phase 5 is the active
publish gate and docs-sync lane

## Executive summary

The current Dependabot alert surface has one open runtime advisory: `glib`
`0.18.5` is vulnerable in the workspace lockfile, with the patched line at
`0.20.0`. The alert is transitive through the desktop stack (`src-tauri`
depends on `tauri 2.6.3`, and the lockfile resolves `gio` / `glib` / `gtk`
`0.18.x` packages). The remediation plan must therefore refresh the transitive
desktop stack, not just edit the lockfile.

In parallel, the repository needs an AISVS 1.0 control framework that is
complementary to the existing OWASP-oriented security surfaces. The framework
should make AISVS C01-C12 explicit in Rust types, validation seams, tests, and
release gates so future security controls are incremental instead of ad hoc.

Current implementation status:

- Phase 0 remains open because the workspace still resolves `glib 0.18.5`
  through the transitive desktop stack and the `gtk` line has not yet accepted
  `glib 0.20.0`.
- Phases 1-4 are already implemented locally in `crates/tachi-core/src/aisvs.rs`
  with targeted tests in `crates/tachi-core/tests/aisvs_registry.rs` and
  `crates/tachi-core/tests/aisvs_controls.rs`.
- Phase 5 is active: publish-readiness now depends on the BOM, checklist, CI,
  and Beads export staying synchronized after each slice.

## Live alert analysis

| Alert | Current state | Package path | Fixed version | Risk |
|---|---|---|---|---|
| 15 | open | `Cargo.lock` -> `tauri` / `gtk` -> `glib 0.18.5` | `glib 0.20.0` | Unsound iterator implementation in `glib::VariantStrIter` can trigger undefined behavior and crashes |

### Immediate remediation objective

1. Upgrade the transitive desktop stack to a `glib` line at or above `0.20.0`.
1. Re-resolve `Cargo.lock` so the vulnerable `glib 0.18.5` package disappears.
1. Validate the update with workspace tests, tauri-specific tests, clippy, and
   the existing release-readiness gates.
1. Close the Dependabot alert only after the lockfile and validation evidence
   prove the fix.

## Adversarial review integration

The review pass surfaced one documentation gap and one structural blocker that
needed to be made explicit in the roadmap:

| Finding | Severity | Category | Remediation |
|---|---|---|---|
| Roadmap status drifted from the live repo state | MEDIUM | Correction | Replace "implementation pending" with the actual phase status so future readers do not treat implemented control phases as work still needing build-out. |
| Phase 0 closure remains blocked by upstream `gtk` compatibility | HIGH | Gap | Keep `RT-00i.2.2`, `RT-00i.7`, and `RT-00i.2.4` as the explicit blocker/follow-up lane; do not widen manifest bounds until the upstream desktop stack accepts the fixed `glib` line. |

This roadmap already contains the necessary Beads graph, but the phase narrative
and status text must stay aligned with the tracker and the local implementation
state.

## Roadmap model

`Epic -> Capability -> Feature -> Task -> Function`

- `Epic` states the security outcome.
- `Capability` names the control family or containment result.
- `Feature` groups work by remediable slice.
- `Task` is the smallest TDD-first change set.
- `Function` names the concrete module, command, workflow, or test seam.

## Phase 0: Contain the open Dependabot alert

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` AISVS framework and Dependabot remediation |
| Capability | Supply-chain containment for the live `glib` alert |
| Feature | `RT-00i.2` Remediate glib/tauri transitive advisory |
| Tasks | `RT-00i.2.1` reproduce alert, `RT-00i.2.2` bump transitive stack, `RT-00i.2.3` verify alert closure |
| Functions | `src-tauri/Cargo.toml`, `Cargo.lock`, `src-tauri/tests/*`, `Makefile publish-gate`, `Makefile scaffold-dependency-gate` |

**TDD acceptance criteria**

- Add or preserve a failing proof that captures the vulnerable `glib 0.18.5`
  lockfile state before the upgrade.
- Make the smallest dependency update that moves the resolved `glib` line to
  `0.20.0` or later.
- Keep the desktop shell and workspace tests green after the upgrade.
- Prove the Dependabot alert is closed or reduced to a documented, explicit
  exception.

## Phase 1: AISVS framework foundation

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` |
| Capability | AISVS 1.0 control registry and error model |
| Feature | `RT-00i.1` Introduce typed AISVS control registry |
| Tasks | define control ids, control families, typed states, and a safe error enum |
| Functions | `crates/tachi-core/src/aisvs.rs`, `crates/tachi-core/tests/aisvs_registry.rs`, `crates/tachi-core/src/lib.rs`, `crates/tachi-core/src/facade.rs` |

**TDD acceptance criteria**

- Invalid control states are unrepresentable at compile time.
- The error enum uses `thiserror`-style composition and does not leak internal
  model strings, credentials, or system details.
- The registry covers AISVS C01-C12 and is `Send + Sync` friendly.
- Tests prove lookup, invalid-state rejection, and serialization/deserialization
  behavior before the implementation lands.

**Status**

- Implemented locally with typed control ids, a sanitized error enum, and
  failing-first registry tests.

## Phase 2: AISVS C01-C04 control cluster

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` |
| Capability | Training-data, input, lifecycle, and infrastructure controls |
| Feature | `RT-00i.3` Implement AISVS C01-C04 control cluster |
| Tasks | training-data traceability, user-input validation, lifecycle gating, infrastructure hardening |
| Functions | `crates/tachi-core/src/aisvs/training_data.rs`, `crates/tachi-core/src/aisvs/input_validation.rs`, `crates/tachi-core/src/aisvs/model_lifecycle.rs`, `crates/tachi-core/src/aisvs/infrastructure.rs` |

**TDD acceptance criteria**

- C01 tests prove third-party data provenance and integrity metadata are
  validated before use.
- C02 tests prove invalid prompt/input states fail before execution.
- C03 tests prove lifecycle transitions are typed and cannot skip gates.
- C04 tests prove infrastructure policy surfaces are explicit and testable.

**Status**

- Implemented locally in `crates/tachi-core/src/aisvs.rs` with
  `crates/tachi-core/tests/aisvs_controls.rs`.
- The control slice is intentionally narrow and typed, with parse-time
  rejection for invalid inputs and explicit transition-policy tests.

## Phase 3: AISVS C05-C08 control cluster

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` |
| Capability | Identity, supply chain, model behavior, and memory controls |
| Feature | `RT-00i.5` Implement AISVS C05-C08 control cluster |
| Tasks | access-control policy, supply-chain verification, behavior constraints, memory/embeddings controls |
| Functions | `crates/tachi-core/src/aisvs/access_control.rs`, `crates/tachi-core/src/aisvs/supply_chain.rs`, `crates/tachi-core/src/aisvs/model_behavior.rs`, `crates/tachi-core/src/aisvs/memory.rs` |

**TDD acceptance criteria**

- C05 tests prove identity and authorization decisions are explicit and
  composable.
- C06 tests prove model/artifact supply-chain evidence is required and audited.
- C07 tests prove unsafe or policy-breaking behavior is rejected by typed state.
- C08 tests prove memory and embedding surfaces remain bounded and validated.

**Status**

- Implemented locally in `crates/tachi-core/src/aisvs.rs` with
  `crates/tachi-core/tests/aisvs_controls.rs`.
- The phase-3 slice keeps explicit access, supply-chain, behavior, and memory
  contracts typed and bounded.

## Phase 4: AISVS C09-C12 control cluster

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` |
| Capability | Orchestration, MCP security, robustness, and monitoring |
| Feature | `RT-00i.4` Implement AISVS C09-C12 control cluster |
| Tasks | orchestration approval, MCP security, adversarial robustness, monitoring/logging |
| Functions | `crates/tachi-core/src/aisvs/orchestration.rs`, `crates/tachi-core/src/aisvs/mcp_security.rs`, `crates/tachi-core/src/aisvs/adversarial.rs`, `crates/tachi-core/src/aisvs/monitoring.rs` |

**TDD acceptance criteria**

- C09 tests prove orchestration permissions and escalation boundaries stay
  explicit.
- C10 tests prove MCP transport, schema, and message validation are covered.
- C11 tests prove adversarial robustness cases have failing-first tests and
  targeted regressions.
- C12 tests prove monitoring and audit outputs are redaction-safe and stable.

**Status**

- Implemented locally in `crates/tachi-core/src/aisvs.rs` with
  `crates/tachi-core/tests/aisvs_controls.rs`.
- The phase-4 slice keeps orchestration, MCP, adversarial, and monitoring
  controls typed and fail-closed.

## Phase 5: Publish-readiness and release gates

| Layer | Mapping |
|---|---|
| Epic | `RT-00i` |
| Capability | Publish gate and alert monitoring |
| Feature | CI and docs readiness for the AISVS framework |
| Tasks | update publish checklist, BOM, release monitoring, and Beads follow-ups |
| Functions | `docs/bill-of-materials.html.md`, `docs/publish-readiness-checklist.html.md`, `.github/workflows/fuzz-mutation-audit.yml`, `.github/workflows/rust-workspace.yml`, `.github/workflows/rust-clippy.yml` |

**TDD acceptance criteria**

- The publish checklist names the new AISVS and advisory security gates.
- The BOM lists the AISVS roadmap and the advisory fuzz/mutation lane.
- GitHub Actions remains green after each slice.
- Any new survivors or regressions become explicit Beads issues before merge.

## Sequencing

1. Keep the Phase 0 blocker explicit until an upstream-compatible `gtk` line
   accepts the fixed `glib` floor.
1. Preserve the already-implemented AISVS foundation and control clusters as
   the canonical local state.
1. Land any future AISVS deltas as separate TDD slices using the existing
   Beads task graph and acceptance criteria.
1. Keep the BOM, publish checklist, and `bd export` synchronized after each
   slice and before any release push.

## Implementation checkpoints

### Checkpoint A: blocker containment

- Keep `RT-00i.2`, `RT-00i.7`, and `RT-00i.2.4` as the retry path for the
  unresolved `glib` advisory.
- Re-run `cargo tree -i glib --locked --target all` and the workspace gates
  when the upstream desktop stack changes.
- Do not widen the desktop manifest bounds before the upstream compatibility
  constraint is resolved.

### Checkpoint B: typed AISVS framework

- Keep the AISVS control registry and sanitized error model as the canonical
  foundation for C01-C12.
- Preserve the `Send + Sync` and invalid-state rejection invariants already
  covered by tests.
- Add future control slices only as separate TDD-backed phases.

### Checkpoint C: publish readiness

- Keep `docs/bill-of-materials.html.md` and
  `docs/publish-readiness-checklist.html.md` synchronized with the roadmap and
  Beads export.
- Require `make publish-gate` plus post-push GitHub Actions monitoring before a
  release is considered complete.
- Keep docs-sweep and archived roadmap references clearly labeled historical.

## Definition of done

- The open Dependabot alert is closed or explicitly documented as accepted.
- AISVS C01-C12 exist as typed, test-backed controls in the Rust workspace.
- The roadmap and Beads tracker expose the exact validation commands for each
  slice.
- No secrets, private paths, or customer data enter the plan, tests, or docs.
