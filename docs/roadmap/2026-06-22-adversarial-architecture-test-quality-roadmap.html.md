# Adversarial Architecture and Test Quality Roadmap

**Date**: 2026-06-22
**Scope**: `tachi-rust` current repository state
**Review mode**: adversarial panel with architecture/SOLID, Rust/Tauri, and test-quality slices
**Execution model**: Beads-managed, test-driven development, small conventional-commit slices
**Status**: planning artifact; implementation pending

## Executive summary

The repository has strong Rust migration momentum, broad integration coverage, active publish gates, and recently remediated dependency alerts. The adversarial panel found the next maturity gap is not feature parity alone; it is hardening the architecture so future features can be added without duplicating command contracts, widening the desktop invoke surface, or relying on fixture-heavy tests as the only safety net.

The highest-priority remediation is to make CI fail closed for behavior and lint regressions, then harden the Tauri boundary before deeper refactors. After that, the roadmap moves command parsing/dispatch/output rendering into typed shared contracts, splits shell responsibilities by SOLID boundaries, narrows the `tachi-core` public API, decomposes large mixed-purpose modules, and upgrades test strategy with semantic, property, fuzz, and mutation-style gates.

### Current repository delta

- `src-tauri/tauri.conf.json`, `src-tauri/capabilities/main.json`, and `src-tauri/build.rs` now exist, so the Tauri surface is no longer a raw scaffold.
- `AQ-021` is partially implemented: the desktop boundary now has least-privilege config and capability tests, but the runtime wiring and typed boundary work remain open.
- `AQ-022` and `AQ-023` are complete: the desktop command schema now rejects control-plane drift and the bridge/offline layer now enforces root-contained IO.
- `AQ-024` is complete: the shared executor now enforces bounded timeout, cancellation cleanup, output caps, and process-group termination where supported.
- `AQ-025` is complete: the desktop boundary now exposes a typed error taxonomy with stable codes while keeping CLI rendering compatible.
- The remaining risk concentrates in public API narrowing and test-quality hardening.

## Panel findings

### High severity

| ID | Finding | Evidence | Risk |
| --- | --- | --- | --- |
| AQ-F01 | PR CI does not expose a full workspace behavioral gate | `.github/workflows/tachi-pytest.yml`, `.github/workflows/tachi-mmdc-preflight.yml`, `Makefile` | Regressions can merge when targeted workflows pass but workspace tests fail. |
| AQ-F02 | Clippy SARIF lane is advisory rather than fail-closed | `.github/workflows/rust-clippy.yml` uses `continue-on-error` semantics | Lint regressions can be hidden behind successful uploads. |
| AQ-F03 | Tauri surface is partially hardened, but runtime wiring is still incomplete | `src-tauri/src/lib.rs::run`, `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json`, `src-tauri/capabilities/main.json` | Desktop boundary now exists, but the invoke surface still needs deeper typed wiring and full least-privilege validation. |
| AQ-F04 | Desktop/control-plane command args remain partially opaque | `src-tauri/src/schema.rs`, `crates/tachi-shell/src/tauri_bridge.rs`, `crates/tachi-shell/src/commands.rs` | UI invoke path can still drift toward a privileged proxy unless the typed registry lands. |
| AQ-F05 | File writes and cache copies need explicit root containment | `crates/tachi-shell/src/tauri_bridge.rs`, `src-tauri/src/offline.rs` | Output/cache paths can escape expected roots if absolute, parent, or symlink paths are accepted. |
| AQ-F06 | Command contracts are stringly and duplicated across adapters | CLI `parse_args`, Tauri schema validation, shell dispatch matches | Violates open/closed principle and creates CLI/Tauri drift risk. |
| AQ-F07 | `tachi-shell::commands` mixes facade, executor, orchestrator, filesystem, serialization, and progress concerns | `crates/tachi-shell/src/commands.rs` | Single-responsibility violations make extension and testing brittle. |

### Medium severity

| ID | Finding | Evidence | Risk |
| --- | --- | --- | --- |
| AQ-F08 | Process execution is blocking, unbounded, and only weakly cancellable | `crates/tachi-shell/src/commands.rs` process loop | Long-running scripts can hang workers, leak grandchildren, or emit unbounded output. |
| AQ-F09 | Tauri output validation relies on text markers instead of typed results | `src-tauri/src/schema.rs::validate_invoke_output` | Presentation wording changes can break desktop validation, while malformed outputs can pass. |
| AQ-F10 | Error handling is status/string based | `Result<_, String>` and raw `CommandOutput` across Tauri/release/offline helpers | UI cannot distinguish policy, validation, IO, timeout, cancellation, and internal failures reliably. |
| AQ-F11 | `tachi-core` public surface is overexposed | broad `pub mod` exports in `crates/tachi-core/src/lib.rs` | Internal parser/report modules become de facto public API, slowing refactors. |
| AQ-F12 | Large modules mix domain, IO defaults, taxonomy loading, and presentation models | `crates/tachi-core/src/infographic.rs`, `crates/tachi-core/src/coverage_attestation.rs` | Alternate taxonomy stores, templates, or packaging contexts require core changes. |
| AQ-F13 | Coverage is broad but integration-heavy | coverage audit reports 81 active modules, 77 integration, 2 unit | Many edge cases require expensive fixture setup; failures are less local. |
| AQ-F14 | Exact golden assertions are centralized and brittle | `crates/tachi-core/tests/reporting_goldens.rs` | Useful regressions are caught, but semantic intent is obscured and updates are costly. |
| AQ-F15 | No property/fuzz/mutation framework surfaced | no `proptest`, `quickcheck`, `cargo fuzz`, or `cargo-mutants` wiring observed | Parser and report invariants rely mainly on hand examples. |
| AQ-F16 | Coverage audit assertions are count-brittle | `coverage_audit_cli.rs` exact inventory totals | Adding or moving tests can fail audits without product behavior changing. |

## Architecture principles assessment

| Principle | Current posture | Required improvement |
| --- | --- | --- |
| Single Responsibility | `tachi-shell::commands` and large core reporting modules have multiple reasons to change. | Split command registry, execution, filesystem, progress, output rendering, and domain use-cases. |
| Open/Closed | New commands require duplicated parser/schema/dispatch/output updates. | Introduce typed command specs so adapters derive parsing and validation from one registry. |
| Liskov Substitution | Few explicit traits exist for execution, IO, taxonomy, or template providers. | Define substitutable `CommandExecutor`, `OutputSink`, `TaxonomyProvider`, and template/content provider traits. |
| Interface Segregation | Public modules expose more internals than consumers need. | Publish narrow facade APIs; keep parser/template internals `pub(crate)` where possible. |
| Dependency Inversion | Core modules infer workspace paths and load YAML directly in places. | Inject providers and adapters; keep filesystem/runtime details outside pure domain logic. |

## Multi-phase roadmap

### Phase 0: Fail-closed quality gates

**Goal**: protect every later refactor with required behavior, lint, and acceptance-quality gates.

| Layer | Mapping |
| --- | --- |
| Epic | AQ-001 Architecture and test quality maturity program |
| Capability | AQ-010 Fail-closed CI and acceptance gates |
| Features | workspace PR test workflow; fail-closed clippy; Beads TDD acceptance template |
| Tasks | AQ-011, AQ-012, AQ-013 |
| Functions/surfaces | `.github/workflows/*`, `Makefile`, `docs/roadmap/*`, `.github/ISSUE_TEMPLATE/*`, Beads descriptions |

**TDD acceptance criteria**:

- Add failing branch/fixture proof or documented dry-run showing a failing workspace test fails the PR workflow.
- `cargo test --workspace --all-targets` has a visible PR gate or equivalent matrix.
- Clippy violations fail the job while SARIF upload remains best-effort after analysis.
- Every new Beads item names failing test first, exact gate command, positive case, negative/adversarial case, and property/golden/mutation applicability.

### Phase 1: Tauri and desktop security boundary

**Goal**: make the desktop surface least-privilege and path-contained before expanding UI capabilities.

| Layer | Mapping |
| --- | --- |
| Epic | AQ-001 |
| Capability | AQ-020 Tauri least-privilege desktop boundary |
| Features | real Tauri config/capabilities; typed control-plane args; root-contained IO; bounded process execution; typed errors |
| Tasks | AQ-021, AQ-022, AQ-023, AQ-024, AQ-025 |
| Functions/surfaces | `src-tauri/src/lib.rs::run`, `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json`, `src-tauri/capabilities/*`, `src-tauri/src/schema.rs`, `src-tauri/src/offline.rs`, `crates/tachi-shell/src/tauri_bridge.rs`, `crates/tachi-shell/src/commands.rs` |

**TDD acceptance criteria**:

- Tests fail before adding real Tauri config/capabilities and pass only when commands are registered through a least-privilege allowlist.
- Desktop invoke tests reject unknown flags, help-as-execution, absolute paths, parent traversal, and symlink escapes.
- Process tests prove timeout, cancellation, output byte cap, and child cleanup behavior.
- UI-facing errors carry stable codes for validation, policy, IO, timeout, cancellation, and internal failures.

### Phase 2: Typed command contract and SOLID shell split

**Goal**: remove adapter drift and isolate responsibilities so CLI, shell, and desktop adapters compose the same command model.

| Layer | Mapping |
| --- | --- |
| Epic | AQ-001 |
| Capability | AQ-030 Typed command contract and shell SOLID refactor |
| Features | command registry; shared argument decoder; typed command results; executor and output-sink traits; CLI/Tauri parity tests |
| Tasks | AQ-031, AQ-032, AQ-033, AQ-034 |
| Functions/surfaces | CLI `parse_args` functions, `crates/tachi-shell/src/tauri_bridge.rs`, `crates/tachi-shell/src/commands.rs`, `src-tauri/src/schema.rs`, `CommandOutput` |

**TDD acceptance criteria**:

- A single typed command registry defines command name, args, help, dispatch target, output type, and policy classification.
- CLI and Tauri parsing derive from the same registry or shared decoder.
- Adding a synthetic command in tests requires no duplicated parser/schema changes.
- Shell execution, file writes, output rendering, and progress reporting are separable behind narrow traits.

### Phase 3: Core API hygiene and module decomposition

**Goal**: make `tachi-core` easier to evolve without exposing internal parser/report implementation details.

| Layer | Mapping |
| --- | --- |
| Epic | AQ-001 |
| Capability | AQ-040 Core API facade and reporting decomposition |
| Features | public facade boundary; infographic module split; provider injection for taxonomy/templates; semantic reporting contracts |
| Tasks | AQ-041, AQ-042, AQ-043 |
| Functions/surfaces | `crates/tachi-core/src/lib.rs`, `crates/tachi-core/src/infographic.rs`, `crates/tachi-core/src/coverage_attestation.rs`, parser/report modules, downstream crate imports |

**TDD acceptance criteria**:

- Downstream crates compile through facade APIs while internal modules move toward `pub(crate)`.
- Infographic domain parsing, MAESTRO aggregation, executive architecture models, template lookup, and payload rendering live behind explicit interfaces.
- Taxonomy/template loading can be substituted in tests without workspace-root inference.
- Existing output fixtures remain behavior-compatible through semantic assertions and compact goldens.

### Phase 4: Test strategy maturity

**Goal**: retain current coverage breadth while adding local, semantic, property, fuzz, and mutation signals.

| Layer | Mapping |
| --- | --- |
| Epic | AQ-001 |
| Capability | AQ-050 Test quality and adversarial verification upgrades |
| Features | unit/integration balance; semantic golden policy; property tests; fuzz harness; mutation audit lane; count-stable coverage audit |
| Tasks | AQ-051, AQ-052, AQ-053, AQ-054, AQ-055 |
| Functions/surfaces | parser modules, normalization, coverage math, SARIF builders, `reporting_goldens.rs`, `coverage_audit_cli.rs`, Makefile/workflows |

**TDD acceptance criteria**:

- Parser/classifier/scorer edge cases move into source-level unit tests where practical.
- Exact goldens are paired with semantic schema/invariant assertions.
- `proptest` or equivalent covers normalization, coverage percentages, source attribution ordering, and parser robustness.
- Fuzz/mutation lanes start non-blocking with baseline reports, then promote high-value survivors to failing Beads tasks.
- Coverage audit tests assert stable category invariants and sentinel modules rather than global counts unless using a controlled fixture root.

## Implementation sequencing

1. Create Phase 0 branch and land fail-closed CI/test gate fixes first.
2. Create Phase 1 branch and make Tauri boundary tests fail before implementing capabilities, arg policy, path containment, process limits, and typed errors.
3. Create Phase 2 branch and introduce the typed command registry behind compatibility adapters; migrate one command at a time.
4. Create Phase 3 branch and narrow `tachi-core` facades after adapter parity is protected.
5. Create Phase 4 branch and add property/fuzz/mutation lanes as non-blocking first, then promote stable signals into publish gates.

## Definition of done for each Beads task

- A failing test is committed or documented before implementation.
- Positive and negative/adversarial cases are included.
- The exact local validation command is documented in the Beads acceptance criteria.
- The task updates roadmap/docs when user-facing behavior, publish gates, or security posture changes.
- The task lands as a conventional commit and leaves `make publish-gate` green unless the task explicitly changes the gate in a staged branch.

## Beads hierarchy created from this plan

- AQ-001: epic, Architecture and test quality maturity program.
- AQ-010/AQ-020/AQ-030/AQ-040/AQ-050: phase capabilities.
- AQ-011..AQ-055: executable TDD tasks with dependency edges and acceptance criteria.
