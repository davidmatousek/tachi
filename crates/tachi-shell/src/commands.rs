use std::path::Path;

use tachi_core::coverage_audit::{collect_audit, render};

pub fn coverage_audit_output(root: &Path) -> String {
    let audit = collect_audit(root);
    render(&audit, root)
}
