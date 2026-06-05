// Parity surface for the first Rust migration crate.
//
// This module starts with a tiny contract so the workspace has a real,
// testable boundary before broader porting work begins.

/// Returns the canonical name for the first parity crate.
pub fn crate_name() -> &'static str {
    "tachi-core"
}
