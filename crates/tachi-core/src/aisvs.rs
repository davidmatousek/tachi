use std::collections::HashSet;
use std::fmt;
use std::str::FromStr;

use thiserror::Error;

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash)]
pub enum AisvsControlId {
    C01,
    C02,
    C03,
    C04,
    C05,
    C06,
    C07,
    C08,
    C09,
    C10,
    C11,
    C12,
}

impl AisvsControlId {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::C01 => "C01",
            Self::C02 => "C02",
            Self::C03 => "C03",
            Self::C04 => "C04",
            Self::C05 => "C05",
            Self::C06 => "C06",
            Self::C07 => "C07",
            Self::C08 => "C08",
            Self::C09 => "C09",
            Self::C10 => "C10",
            Self::C11 => "C11",
            Self::C12 => "C12",
        }
    }
}

impl fmt::Display for AisvsControlId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

impl FromStr for AisvsControlId {
    type Err = AisvsError;

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        match input.trim().to_ascii_uppercase().as_str() {
            "C01" => Ok(Self::C01),
            "C02" => Ok(Self::C02),
            "C03" => Ok(Self::C03),
            "C04" => Ok(Self::C04),
            "C05" => Ok(Self::C05),
            "C06" => Ok(Self::C06),
            "C07" => Ok(Self::C07),
            "C08" => Ok(Self::C08),
            "C09" => Ok(Self::C09),
            "C10" => Ok(Self::C10),
            "C11" => Ok(Self::C11),
            "C12" => Ok(Self::C12),
            _ => Err(AisvsError::InvalidControlId),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AisvsControl {
    id: AisvsControlId,
    capability: &'static str,
    feature: &'static str,
    task: &'static str,
    function: &'static str,
    acceptance_criteria: &'static str,
}

impl AisvsControl {
    pub const fn new(
        id: AisvsControlId,
        capability: &'static str,
        feature: &'static str,
        task: &'static str,
        function: &'static str,
        acceptance_criteria: &'static str,
    ) -> Self {
        Self {
            id,
            capability,
            feature,
            task,
            function,
            acceptance_criteria,
        }
    }

    pub const fn id(&self) -> AisvsControlId {
        self.id
    }

    pub const fn capability(&self) -> &'static str {
        self.capability
    }

    pub const fn feature(&self) -> &'static str {
        self.feature
    }

    pub const fn task(&self) -> &'static str {
        self.task
    }

    pub const fn function(&self) -> &'static str {
        self.function
    }

    pub const fn acceptance_criteria(&self) -> &'static str {
        self.acceptance_criteria
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AisvsRegistry {
    framework_name: &'static str,
    framework_version: &'static str,
    controls: Vec<AisvsControl>,
}

impl Default for AisvsRegistry {
    fn default() -> Self {
        aisvs_control_registry()
    }
}

impl AisvsRegistry {
    pub fn new(
        framework_name: &'static str,
        framework_version: &'static str,
        controls: Vec<AisvsControl>,
    ) -> Result<Self, AisvsError> {
        let mut seen = HashSet::new();
        for control in &controls {
            if !seen.insert(control.id) {
                return Err(AisvsError::DuplicateControlId);
            }
        }

        Ok(Self {
            framework_name,
            framework_version,
            controls,
        })
    }

    pub const fn framework_name(&self) -> &'static str {
        self.framework_name
    }

    pub const fn framework_version(&self) -> &'static str {
        self.framework_version
    }

    pub fn controls(&self) -> &[AisvsControl] {
        &self.controls
    }

    pub fn lookup(&self, id: AisvsControlId) -> Option<&AisvsControl> {
        self.controls.iter().find(|control| control.id == id)
    }

    pub fn control(&self, id: AisvsControlId) -> Result<&AisvsControl, AisvsError> {
        self.lookup(id).ok_or(AisvsError::UnknownControl)
    }
}

#[derive(Clone, Debug, Error, PartialEq, Eq)]
pub enum AisvsError {
    #[error("invalid AISVS control id")]
    InvalidControlId,
    #[error("unknown AISVS control")]
    UnknownControl,
    #[error("duplicate AISVS control")]
    DuplicateControlId,
    #[error("invalid AISVS training data asset")]
    InvalidTrainingDataAsset,
    #[error("invalid AISVS prompt input")]
    InvalidPromptInput,
    #[error("invalid AISVS lifecycle transition")]
    InvalidLifecycleTransition,
    #[error("overbroad AISVS infrastructure policy")]
    OverbroadInfrastructurePolicy,
}

impl AisvsError {
    pub const fn code(&self) -> &'static str {
        match self {
            Self::InvalidControlId => "AISVS_INVALID_CONTROL_ID",
            Self::UnknownControl => "AISVS_UNKNOWN_CONTROL",
            Self::DuplicateControlId => "AISVS_DUPLICATE_CONTROL_ID",
            Self::InvalidTrainingDataAsset => "AISVS_INVALID_TRAINING_DATA_ASSET",
            Self::InvalidPromptInput => "AISVS_INVALID_PROMPT_INPUT",
            Self::InvalidLifecycleTransition => "AISVS_INVALID_LIFECYCLE_TRANSITION",
            Self::OverbroadInfrastructurePolicy => "AISVS_OVERBROAD_INFRASTRUCTURE_POLICY",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct TrainingDataAsset {
    source: String,
    checksum: String,
    provenance: String,
}

impl TrainingDataAsset {
    pub fn parse(source: &str, checksum: &str, provenance: &str) -> Result<Self, AisvsError> {
        let source = source.trim();
        let checksum = checksum.trim();
        let provenance = provenance.trim();

        let Some(digest) = checksum.strip_prefix("sha256:") else {
            return Err(AisvsError::InvalidTrainingDataAsset);
        };

        if source.is_empty()
            || provenance.is_empty()
            || digest.len() != 64
            || !digest.chars().all(|c| c.is_ascii_hexdigit())
        {
            return Err(AisvsError::InvalidTrainingDataAsset);
        }

        Ok(Self {
            source: source.to_string(),
            checksum: checksum.to_string(),
            provenance: provenance.to_string(),
        })
    }

    pub fn source(&self) -> &str {
        &self.source
    }

    pub fn checksum(&self) -> &str {
        &self.checksum
    }

    pub fn provenance(&self) -> &str {
        &self.provenance
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PromptInput(String);

impl PromptInput {
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl FromStr for PromptInput {
    type Err = AisvsError;

    fn from_str(input: &str) -> Result<Self, Self::Err> {
        let normalized = input.trim();
        if normalized.is_empty()
            || normalized
                .chars()
                .any(|c| c == '\0' || (c.is_control() && !c.is_whitespace()))
        {
            return Err(AisvsError::InvalidPromptInput);
        }

        Ok(Self(normalized.to_string()))
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum LifecycleStage {
    Draft,
    Validated,
    Approved,
    Deployed,
    Retired,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub struct LifecycleGate {
    stage: LifecycleStage,
}

impl LifecycleGate {
    pub const fn new(stage: LifecycleStage) -> Self {
        Self { stage }
    }

    pub const fn stage(self) -> LifecycleStage {
        self.stage
    }

    pub fn advance_to(self, next: LifecycleStage) -> Result<Self, AisvsError> {
        let allowed = matches!(
            (self.stage, next),
            (LifecycleStage::Draft, LifecycleStage::Validated)
                | (LifecycleStage::Validated, LifecycleStage::Approved)
                | (LifecycleStage::Approved, LifecycleStage::Deployed)
                | (LifecycleStage::Deployed, LifecycleStage::Retired)
        );

        if allowed {
            Ok(Self { stage: next })
        } else {
            Err(AisvsError::InvalidLifecycleTransition)
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct InfrastructurePolicy {
    allow_network: bool,
    allow_secret_access: bool,
    allow_writes: bool,
}

impl InfrastructurePolicy {
    pub fn new(
        allow_network: bool,
        allow_secret_access: bool,
        allow_writes: bool,
    ) -> Result<Self, AisvsError> {
        let enabled_controls = allow_network as u8 + allow_secret_access as u8 + allow_writes as u8;
        if enabled_controls > 1 {
            return Err(AisvsError::OverbroadInfrastructurePolicy);
        }

        Ok(Self {
            allow_network,
            allow_secret_access,
            allow_writes,
        })
    }

    pub const fn least_privilege() -> Self {
        Self {
            allow_network: false,
            allow_secret_access: false,
            allow_writes: false,
        }
    }

    pub const fn allows_network(&self) -> bool {
        self.allow_network
    }

    pub const fn allows_secret_access(&self) -> bool {
        self.allow_secret_access
    }

    pub const fn allows_writes(&self) -> bool {
        self.allow_writes
    }

    pub const fn is_least_privilege(&self) -> bool {
        !self.allow_network && !self.allow_secret_access && !self.allow_writes
    }
}

pub fn aisvs_control_registry() -> AisvsRegistry {
    AisvsRegistry {
        framework_name: "AISVS 1.0",
        framework_version: "1.0",
        controls: vec![
            AisvsControl::new(
                AisvsControlId::C01,
                "Training-data integrity and traceability",
                "Immutable training lineage",
                "Capture provenance for AI input sets",
                "Training-data integrity and traceability",
                "Tests prove invalid lineage is unrepresentable and provenance is preserved.",
            ),
            AisvsControl::new(
                AisvsControlId::C02,
                "Input validation and normalization",
                "Typed input envelopes",
                "Reject malformed or ambiguous prompts",
                "Input validation and normalization",
                "Tests prove malformed inputs fail closed before downstream use.",
            ),
            AisvsControl::new(
                AisvsControlId::C03,
                "Model lifecycle management",
                "Versioned model policies",
                "Pin, promote, and retire models safely",
                "Model lifecycle management",
                "Tests prove lifecycle transitions require explicit approval states.",
            ),
            AisvsControl::new(
                AisvsControlId::C04,
                "Infrastructure hardening",
                "Runtime isolation boundaries",
                "Constrain execution and deployment surfaces",
                "Infrastructure hardening",
                "Tests prove infrastructure defaults stay least privilege.",
            ),
            AisvsControl::new(
                AisvsControlId::C05,
                "Access control and identity",
                "Typed authorization contexts",
                "Authorize only authenticated actors",
                "Access control and identity",
                "Tests prove identity and authorization decisions are explicit.",
            ),
            AisvsControl::new(
                AisvsControlId::C06,
                "Supply chain assurance",
                "Pinned dependency evidence",
                "Track and remediate upstream advisories",
                "Supply chain assurance",
                "Tests prove vulnerable dependencies are surfaced and gated.",
            ),
            AisvsControl::new(
                AisvsControlId::C07,
                "Model behavior control",
                "Typed output contracts",
                "Constrain model outputs to expected schemas",
                "Model behavior control",
                "Tests prove outputs are normalized before use.",
            ),
            AisvsControl::new(
                AisvsControlId::C08,
                "Memory and embeddings governance",
                "Scoped retrieval policies",
                "Prevent unsafe reuse of stored context",
                "Memory and embeddings governance",
                "Tests prove retrieval obeys scope and retention rules.",
            ),
            AisvsControl::new(
                AisvsControlId::C09,
                "Orchestration and agentic action",
                "Typed action boundaries",
                "Gate autonomous actions behind policy checks",
                "Orchestration and agentic action",
                "Tests prove action execution cannot bypass policy seams.",
            ),
            AisvsControl::new(
                AisvsControlId::C10,
                "MCP security",
                "Typed tool invocation policies",
                "Restrict tool access to approved capabilities",
                "MCP security",
                "Tests prove tool calls cannot exceed declared capability scope.",
            ),
            AisvsControl::new(
                AisvsControlId::C11,
                "Adversarial robustness",
                "Robustness regression suite",
                "Capture hostile inputs and rejection behavior",
                "Adversarial robustness",
                "Tests prove adversarial cases remain fail-closed.",
            ),
            AisvsControl::new(
                AisvsControlId::C12,
                "Monitoring and logging",
                "Redaction-safe telemetry",
                "Log security evidence without secrets or PII leakage",
                "Monitoring and logging",
                "Tests prove logs remain sanitized and actionable.",
            ),
        ],
    }
}
