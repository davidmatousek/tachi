# AISVS Dependabot Remediation Issue Cards

**Last Updated**: 2026-06-23
**Status**: Beads-ready execution slices for the AISVS / Dependabot roadmap
**Source**: [2026-06-23-aisvs-dependabot-remediation-roadmap.html.md](./2026-06-23-aisvs-dependabot-remediation-roadmap.html.md)

These cards are TDD-first and follow the roadmap ordering:
write the failing proof first, then implement the minimal change, then validate
with the exact commands named in the card.

## Card Format

- `Epic`
- `Feature`
- `Capability`
- `Task`
- `Function`
- `Dependencies`
- `Acceptance criteria`
- `Validation`
- `Implementation owner`
- `Stage label`
- `Next test seam`
- `Notes`

## Phase 0 - Live Dependabot containment

### RT-00i.2 - Remediate glib/tauri transitive advisory

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 0 live Dependabot containment
- `Capability`: supply-chain remediation for the open `glib` advisory
- `Task`: reproduce the alert, upgrade the transitive desktop stack to a fixed
  `glib` line, and close the live advisory without regressing the shell
- `Function`: `src-tauri/Cargo.toml`, `Cargo.lock`,
  `crates/tachi-core/tests/scaffold_dependency_floors.rs`,
  `src-tauri/tests/*`, `Makefile scaffold-dependency-gate`
- `Dependencies`: live Dependabot alert 15, current `tauri 2.6.3` dependency
  line
- `Acceptance criteria`:
  - The vulnerable `glib 0.18.5` resolution no longer appears in the lockfile.
  - The Dependabot alert is closed or documented as an explicit non-blocking exception.
  - The desktop and workspace tests stay green after the dependency refresh.
  - The fix is conventional-commit sized and preserves publish-readiness gates.
- `Validation`: `cargo test -p tachi-tauri`, `cargo test --workspace --all-targets`,
  `make scaffold-dependency-gate`
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 0
- `Next test seam`: `Cargo.lock`
- `Notes`: This slice contains the live open alert and should land first.

#### RT-00i.2 task beads

- `RT-00i.2.1` Reproduce glib advisory and capture failing proof
  - Acceptance: the vulnerable `glib 0.18.5` resolution is asserted by a
    reproducible lockfile check; the transitive `tauri` -> `gtk` -> `glib`
    path is documented; and the proof is repeatable in CI.
  - Status: closed with `crates/tachi-core/tests/scaffold_dependency_floors.rs`
    coverage and a recorded `cargo tree -i glib --locked --target all` path.
- `RT-00i.2.2` Upgrade desktop stack to fixed glib release
  - Acceptance: `Cargo.lock` no longer resolves `glib 0.18.5`; the workspace
    and desktop tests stay green; and any upstream incompatibility is recorded
    as an explicit blocker or decision note.
- `RT-00i.7` Record gtk/glib compatibility decision for Dependabot alert
  - Acceptance: the upstream compatibility decision captures the current
    `tauri -> gtk -> glib 0.18.5` path, the failed `glib 0.20.0` update, and
    the condition required before the alert can be closed.
  - Notes: decision landing zone for the unresolved desktop-stack blocker.
- `RT-00i.2.3` Prove alert closure and publish gate evidence
  - Acceptance: the post-fix scan or explicit exception is recorded; the
    release-readiness docs reflect the current state; and the Beads export
    matches the tracker state.
  - Dependencies: `RT-00i.2.2`
- `RT-00i.2.4` Recheck gtk/glib compatibility when upstream release lands
  - Acceptance: a follow-up probe records whether the desktop stack can now
    resolve glib 0.20.0 or later; the lockfile and dependency tree are
    re-audited; and the alert is either closed or kept open with refreshed
    evidence.
  - Dependencies: `RT-00i.7`

## Phase 1 - AISVS framework foundation

### RT-00i.1 - Introduce typed AISVS control registry

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 1 AISVS framework foundation
- `Capability`: typed AISVS control registry and error model
- `Task`: add a typed AISVS control registry, framework metadata, and a
  non-leaking error enum so C01-C12 can be handled as a sixth control family
- `Function`: `crates/tachi-core/src/aisvs/*`, `crates/tachi-core/tests/*`
- `Dependencies`: RT-00i.2, current core facade and reporting seams
- `Acceptance criteria`:
  - Invalid control states are unrepresentable at compile time.
  - The registry covers AISVS C01-C12 and is `Send + Sync` friendly.
  - Errors use a dedicated `thiserror`-style enum without leaking internal
    model strings or system details.
  - Unit tests prove lookup, serialization, invalid-state rejection, and
    control-family mapping before implementation is accepted.
- `Validation`: `cargo test -p tachi-core`, `cargo clippy --workspace --all-features --all-targets -- -D warnings`
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 1
- `Next test seam`: `crates/tachi-core/src/aisvs/control_registry.rs`
- `Notes`: This is the shared foundation for every AISVS control slice.

#### RT-00i.1 task beads

- `RT-00i.1.1` Define AISVS control registry and typed control IDs
  - Acceptance: control identifiers parse into strongly typed values; invalid
    IDs fail closed; lookup and display logic is table-driven; and tests prove
    the registry covers C01-C12 without relying on stringly-typed state.
- `RT-00i.1.2` Define AISVS error enum and sanitized lookup failures
  - Acceptance: registry lookups and parse failures return a dedicated
    non-leaking error type; no variant exposes model strings or internal
    paths; and tests prove invalid states fail closed with stable messages.
- `RT-00i.1.3` Prove AISVS registry Send+Sync and serialization invariants
  - Acceptance: the AISVS registry and control-state types are Send + Sync;
    serialization or display stays stable for known controls; and compile-time
    or unit tests prove no invalid control state can be constructed from
    public APIs.

## Phase 2 - AISVS C01-C04 cluster

### RT-00i.3 - Implement AISVS C01-C04 control cluster

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 2 AISVS control cluster
- `Capability`: training-data, input, lifecycle, and infrastructure controls
- `Task`: implement C01-C04 as typed policies with failing-first tests and
  explicit validation seams
- `Function`: `crates/tachi-core/src/aisvs/training_data.rs`,
  `crates/tachi-core/src/aisvs/input_validation.rs`,
  `crates/tachi-core/src/aisvs/model_lifecycle.rs`,
  `crates/tachi-core/src/aisvs/infrastructure.rs`
- `Dependencies`: RT-00i.1
- `Acceptance criteria`:
  - C01 tests prove provenance and integrity validation for model/data assets.
  - C02 tests prove invalid input states fail before execution.
  - C03 tests prove lifecycle transitions cannot skip validation gates.
  - C04 tests prove infrastructure policy is typed and explicitly testable.
- `Validation`: `cargo test -p tachi-core --tests`, targeted AISVS unit tests
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-core/src/aisvs/input_validation.rs`
- `Notes`: Keep the implementation slices small and control-specific.
- `Status`: implemented locally in `crates/tachi-core/src/aisvs.rs` with
  targeted phase-2 tests in `crates/tachi-core/tests/aisvs_controls.rs`.

## Phase 3 - AISVS C05-C08 cluster

### RT-00i.5 - Implement AISVS C05-C08 control cluster

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 3 AISVS control cluster
- `Capability`: identity, supply chain, behavior, and memory controls
- `Task`: implement C05-C08 with typed checks, safe errors, and regression
  tests that protect against adversarial drift
- `Function`: `crates/tachi-core/src/aisvs/access_control.rs`,
  `crates/tachi-core/src/aisvs/supply_chain.rs`,
  `crates/tachi-core/src/aisvs/model_behavior.rs`,
  `crates/tachi-core/src/aisvs/memory.rs`
- `Dependencies`: RT-00i.1, RT-00i.2
- `Acceptance criteria`:
  - C05 tests prove identity and authorization decisions are explicit.
  - C06 tests prove supply-chain evidence is required and audited.
  - C07 tests prove unsafe or policy-breaking behavior is rejected by typed state.
  - C08 tests prove memory and embedding surfaces remain bounded and validated.
- `Validation`: `cargo test -p tachi-core --tests`, `make publish-gate`
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 3
- `Next test seam`: `crates/tachi-core/src/aisvs/supply_chain.rs`
- `Notes`: This phase should close the security/control gap between the AISVS
  plan and the core reporting path.
- `Status`: implemented locally in `crates/tachi-core/src/aisvs.rs` with
  targeted phase-3 tests in `crates/tachi-core/tests/aisvs_controls.rs`.

## Phase 4 - AISVS C09-C12 cluster

### RT-00i.4 - Implement AISVS C09-C12 control cluster

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 4 AISVS control cluster
- `Capability`: orchestration, MCP, robustness, and monitoring controls
- `Task`: implement C09-C12 with policy checks, adversarial cases, and
  redaction-safe reporting
- `Function`: `crates/tachi-core/src/aisvs/orchestration.rs`,
  `crates/tachi-core/src/aisvs/mcp_security.rs`,
  `crates/tachi-core/src/aisvs/adversarial.rs`,
  `crates/tachi-core/src/aisvs/monitoring.rs`
- `Dependencies`: RT-00i.1, RT-00i.3, RT-00i.5
- `Acceptance criteria`:
  - C09 tests prove orchestration permissions and escalation boundaries stay
    explicit.
  - C10 tests prove MCP transport, schema, and message validation are covered.
  - C11 tests prove adversarial robustness cases have failing-first tests and
    targeted regressions.
  - C12 tests prove monitoring and audit outputs are redaction-safe and stable.
- `Validation`: `cargo test -p tachi-core --tests`, `cargo clippy --workspace --all-features --all-targets -- -D warnings`
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 4
- `Next test seam`: `crates/tachi-core/src/aisvs/monitoring.rs`
- `Notes`: Finish the control family with observability and alerting surfaces.
- `Status`: implemented locally in `crates/tachi-core/src/aisvs.rs` with
  targeted phase-4 tests in `crates/tachi-core/tests/aisvs_controls.rs`.

## Phase 5 - Publish-readiness and release gates

### RT-00i.6 - CI and docs readiness for AISVS framework

- `Epic`: RT-00i AISVS framework and Dependabot remediation
- `Feature`: Phase 5 publish-readiness and release gates
- `Capability`: publish gate and alert monitoring
- `Task`: update the publish checklist, BOM, release monitoring, and Beads
  follow-ups so the AISVS framework stays release-ready after each slice
- `Function`: `docs/bill-of-materials.html.md`,
  `docs/publish-readiness-checklist.html.md`,
  `.github/workflows/fuzz-mutation-audit.yml`,
  `.github/workflows/rust-workspace.yml`,
  `.github/workflows/rust-clippy.yml`
- `Dependencies`: RT-00i.1, RT-00i.2, RT-00i.3, RT-00i.4, RT-00i.5
- `Acceptance criteria`:
  - The publish checklist names the AISVS and advisory security gates.
  - The BOM lists the AISVS roadmap and the advisory fuzz/mutation lane.
  - GitHub Actions remains green after each slice.
  - Any new survivors or regressions become explicit Beads issues before merge.
- `Validation`: `make publish-gate`, `bd export -o .beads/issues.jsonl`
- `Implementation owner`: `docs`
- `Stage label`: Phase 5
- `Next test seam`: `docs/publish-readiness-checklist.html.md`
- `Notes`: This closes the docs and release-readiness gap after the control
  rollout lands.

#### RT-00i.6 task beads

- `RT-00i.6.1` Synchronize AISVS publish-readiness docs and Beads export
  - Acceptance: the BOM and publish checklist explicitly call out the AISVS
    framework and Dependabot gate; the Beads export matches the live tracker;
    and the release validation path stays reproducible with the documented
    commands.
