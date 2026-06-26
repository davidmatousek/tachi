use crate::{build_contract_snapshot, McpContractSnapshot};

pub fn supported_contract_snapshot() -> McpContractSnapshot {
    build_contract_snapshot()
}
