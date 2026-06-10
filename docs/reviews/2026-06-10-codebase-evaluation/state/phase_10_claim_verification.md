# Phase 10: Claim Verification

| Finding | Cited Path | Line Range | Status | Notes |
|---------|------------|------------|--------|-------|
| Test Fail | `crates/tachi-core/tests/python_surface_inventory.rs` | 32-35 | [VERIFIED] | Path prefix checks omit hidden directories. |
| SRP Violation | `crates/tachi-core/src/parsers.rs` | 1-20 | [VERIFIED] | Parses multiple unrelated schemas. |
| Case Conversion | `crates/tachi-core/src/parsers.rs` | 384-394 | [VERIFIED] | Unsafe index slicing assumptions. |
