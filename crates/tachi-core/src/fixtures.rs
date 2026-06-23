use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::normalization::normalize_value;

pub const FIXTURE_SCHEMA_VERSION: u32 = 1;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CommandFixture {
    pub schema_version: u32,
    pub command: String,
    pub input: Value,
    pub input_hash: String,
    pub output: Value,
    pub output_hash: String,
}

pub fn serialize_fixture(command: &str, input: &Value, output: &Value) -> Result<String, String> {
    let fixture = CommandFixture {
        schema_version: FIXTURE_SCHEMA_VERSION,
        command: command.trim().to_string(),
        input: input.clone(),
        input_hash: hash_fixture_payload(input)?,
        output: output.clone(),
        output_hash: hash_fixture_payload(output)?,
    };

    serde_json::to_string_pretty(&fixture)
        .map_err(|err| format!("failed to serialize command fixture: {err}"))
}

pub fn hash_fixture_payload(payload: &Value) -> Result<String, String> {
    let canonical = canonical_json(payload)?;
    let mut hasher = Sha256::new();
    hasher.update(canonical.as_bytes());
    Ok(format!("{:x}", hasher.finalize()))
}

pub fn validate_fixture_schema(text: &str) -> Result<CommandFixture, String> {
    let fixture: CommandFixture = serde_json::from_str(text)
        .map_err(|err| format!("failed to parse command fixture: {err}"))?;

    if fixture.schema_version != FIXTURE_SCHEMA_VERSION {
        return Err(format!(
            "schema version mismatch: expected {} but found {}",
            FIXTURE_SCHEMA_VERSION, fixture.schema_version
        ));
    }
    if fixture.command.trim().is_empty() {
        return Err(String::from("command name must not be empty"));
    }

    let input_hash = hash_fixture_payload(&fixture.input)?;
    if fixture.input_hash != input_hash {
        return Err(format!(
            "input hash mismatch for {}: expected {} but found {}",
            fixture.command, fixture.input_hash, input_hash
        ));
    }

    let output_hash = hash_fixture_payload(&fixture.output)?;
    if fixture.output_hash != output_hash {
        return Err(format!(
            "output hash mismatch for {}: expected {} but found {}",
            fixture.command, fixture.output_hash, output_hash
        ));
    }

    Ok(fixture)
}

fn canonical_json(value: &Value) -> Result<String, String> {
    let normalized = normalize_value(value);
    serde_json::to_string(&normalized)
        .map_err(|err| format!("failed to serialize canonical fixture payload: {err}"))
}
