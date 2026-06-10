# Phase 3: Independent Review - Architecture Critic
**Score:** 7/10
**Recommendation:** ACCEPT WITH CHANGES

## Findings

### [Finding 1] [P1] test_python_surface_inventory fails due to .worktrees scan
* **Location:** [python_surface_inventory.rs](file:///Users/neo/projects/tachi-rust/crates/tachi-core/tests/python_surface_inventory.rs#L32)
* **Description:** The function `collect_python_files` recursively traverses the root workspace directory but does not exclude `.worktrees` or other dot-hidden folders. If the user has active worktrees configured, the test scans their `.py` files, causing an inventory mismatch.
* **Mitigation:** Exclude `.worktrees` and dot-prefixed paths.

### [Finding 2] [P2] SRP Violation in parsers.rs
* **Location:** [parsers.rs](file:///Users/neo/projects/tachi-rust/crates/tachi-core/src/parsers.rs#L1)
* **Description:** `parsers.rs` contains parsing schemas and routines for multiple unrelated formats (Mermaid, Markdown tables, resolved findings, risk summaries, scope structures, asset maps). It has multiple reasons to change.
* **Mitigation:** Segregate into a `parsers/` sub-package.

### [Finding 3] [P2] Case conversion byte alignment vulnerability
* **Location:** [parsers.rs](file:///Users/neo/projects/tachi-rust/crates/tachi-core/src/parsers.rs#L384)
* **Description:** In `replace_br_tags_with_space`, the function constructs `lower` using `input.to_ascii_lowercase()`, then slices `input` using byte indices matched against `lower`. While this works for ASCII, if it is ever modified to use Unicode `to_lowercase()`, character byte sizes can shift, leading to panic boundaries.
* **Mitigation:** Avoid index-sharing between case-converted and raw slices.
