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
    validation_command: &'static str,
    acceptance_criteria: &'static str,
}

impl AisvsControl {
    pub const fn new(
        id: AisvsControlId,
        capability: &'static str,
        feature: &'static str,
        task: &'static str,
        function: &'static str,
        validation_command: &'static str,
        acceptance_criteria: &'static str,
    ) -> Self {
        Self {
            id,
            capability,
            feature,
            task,
            function,
            validation_command,
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

    pub const fn validation_command(&self) -> &'static str {
        self.validation_command
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
    #[error("invalid AISVS access context")]
    InvalidAccessContext,
    #[error("invalid AISVS supply chain evidence")]
    InvalidSupplyChainEvidence,
    #[error("invalid AISVS model behavior policy")]
    InvalidModelBehaviorPolicy,
    #[error("invalid AISVS memory scope")]
    InvalidMemoryScope,
    #[error("invalid AISVS orchestration policy")]
    InvalidOrchestrationPolicy,
    #[error("invalid AISVS MCP policy")]
    InvalidMcpPolicy,
    #[error("invalid AISVS adversarial case")]
    InvalidAdversarialCase,
    #[error("invalid AISVS monitoring event")]
    InvalidMonitoringEvent,
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
            Self::InvalidAccessContext => "AISVS_INVALID_ACCESS_CONTEXT",
            Self::InvalidSupplyChainEvidence => "AISVS_INVALID_SUPPLY_CHAIN_EVIDENCE",
            Self::InvalidModelBehaviorPolicy => "AISVS_INVALID_MODEL_BEHAVIOR_POLICY",
            Self::InvalidMemoryScope => "AISVS_INVALID_MEMORY_SCOPE",
            Self::InvalidOrchestrationPolicy => "AISVS_INVALID_ORCHESTRATION_POLICY",
            Self::InvalidMcpPolicy => "AISVS_INVALID_MCP_POLICY",
            Self::InvalidAdversarialCase => "AISVS_INVALID_ADVERSARIAL_CASE",
            Self::InvalidMonitoringEvent => "AISVS_INVALID_MONITORING_EVENT",
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum AccessMode {
    Observer,
    Operator,
    Service,
}

impl AccessMode {
    const fn rank(self) -> u8 {
        match self {
            Self::Observer => 0,
            Self::Operator => 1,
            Self::Service => 2,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AccessContext {
    subject: String,
    mode: AccessMode,
}

impl AccessContext {
    pub fn new(subject: &str, mode: AccessMode) -> Result<Self, AisvsError> {
        let subject = subject.trim();
        if subject.is_empty() {
            return Err(AisvsError::InvalidAccessContext);
        }

        Ok(Self {
            subject: subject.to_string(),
            mode,
        })
    }

    pub fn subject(&self) -> &str {
        &self.subject
    }

    pub const fn mode(&self) -> AccessMode {
        self.mode
    }

    pub const fn permits(&self, required: AccessMode) -> bool {
        self.mode.rank() >= required.rank()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SupplyChainEvidence {
    package: String,
    version: String,
    checksum: String,
    attestation_uri: String,
}

impl SupplyChainEvidence {
    pub fn new(
        package: &str,
        version: &str,
        checksum: &str,
        attestation_uri: &str,
    ) -> Result<Self, AisvsError> {
        let package = package.trim();
        let version = version.trim();
        let checksum = checksum.trim();
        let attestation_uri = attestation_uri.trim();

        let Some(digest) = checksum.strip_prefix("sha256:") else {
            return Err(AisvsError::InvalidSupplyChainEvidence);
        };

        if package.is_empty()
            || version.is_empty()
            || attestation_uri.is_empty()
            || !attestation_uri.starts_with("https://")
            || digest.len() != 64
            || !digest.chars().all(|c| c.is_ascii_hexdigit())
        {
            return Err(AisvsError::InvalidSupplyChainEvidence);
        }

        Ok(Self {
            package: package.to_string(),
            version: version.to_string(),
            checksum: checksum.to_string(),
            attestation_uri: attestation_uri.to_string(),
        })
    }

    pub fn package(&self) -> &str {
        &self.package
    }

    pub fn version(&self) -> &str {
        &self.version
    }

    pub fn checksum(&self) -> &str {
        &self.checksum
    }

    pub fn attestation_uri(&self) -> &str {
        &self.attestation_uri
    }

    pub fn audit_tag(&self) -> String {
        format!("{}@{}", self.package, self.version)
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ModelBehaviorPolicy {
    output_schema: String,
    max_output_chars: usize,
    redaction_required: bool,
}

impl ModelBehaviorPolicy {
    pub fn new(
        output_schema: &str,
        max_output_chars: usize,
        redaction_required: bool,
    ) -> Result<Self, AisvsError> {
        let output_schema = output_schema.trim();
        if output_schema.is_empty() || max_output_chars == 0 || !redaction_required {
            return Err(AisvsError::InvalidModelBehaviorPolicy);
        }

        Ok(Self {
            output_schema: output_schema.to_string(),
            max_output_chars,
            redaction_required,
        })
    }

    pub fn strict(output_schema: &str, max_output_chars: usize) -> Result<Self, AisvsError> {
        Self::new(output_schema, max_output_chars, true)
    }

    pub fn output_schema(&self) -> &str {
        &self.output_schema
    }

    pub const fn max_output_chars(&self) -> usize {
        self.max_output_chars
    }

    pub const fn is_redaction_required(&self) -> bool {
        self.redaction_required
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MemoryScope {
    max_entries: usize,
    retention_days: u16,
    cross_scope_allowed: bool,
}

impl MemoryScope {
    pub fn new(
        max_entries: usize,
        retention_days: u16,
        cross_scope_allowed: bool,
    ) -> Result<Self, AisvsError> {
        if max_entries == 0 || retention_days == 0 || retention_days > 30 || cross_scope_allowed {
            return Err(AisvsError::InvalidMemoryScope);
        }

        Ok(Self {
            max_entries,
            retention_days,
            cross_scope_allowed,
        })
    }

    pub fn bounded(max_entries: usize, retention_days: u16) -> Result<Self, AisvsError> {
        Self::new(max_entries, retention_days, false)
    }

    pub const fn max_entries(&self) -> usize {
        self.max_entries
    }

    pub const fn retention_days(&self) -> u16 {
        self.retention_days
    }

    pub const fn allows_cross_scope(&self) -> bool {
        self.cross_scope_allowed
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OrchestrationPolicy {
    requires_approval: bool,
    allows_escalation: bool,
}

impl OrchestrationPolicy {
    pub fn new(requires_approval: bool, allows_escalation: bool) -> Result<Self, AisvsError> {
        if allows_escalation && !requires_approval {
            return Err(AisvsError::InvalidOrchestrationPolicy);
        }

        Ok(Self {
            requires_approval,
            allows_escalation,
        })
    }

    pub const fn requires_approval(&self) -> bool {
        self.requires_approval
    }

    pub const fn allows_escalation(&self) -> bool {
        self.allows_escalation
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OrchestrationAction {
    name: String,
    escalation: bool,
}

impl OrchestrationAction {
    pub fn new(name: &str, escalation: bool) -> Result<Self, AisvsError> {
        let name = name.trim();
        if name.is_empty() {
            return Err(AisvsError::InvalidOrchestrationPolicy);
        }

        Ok(Self {
            name: name.to_string(),
            escalation,
        })
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub const fn is_escalation(&self) -> bool {
        self.escalation
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct McpPolicy {
    schema_name: String,
    allowed_tools: Vec<String>,
}

impl McpPolicy {
    pub fn new(schema_name: &str, allowed_tools: &[&str]) -> Result<Self, AisvsError> {
        let schema_name = schema_name.trim();
        if schema_name.is_empty() || allowed_tools.is_empty() {
            return Err(AisvsError::InvalidMcpPolicy);
        }

        let mut tools = Vec::new();
        for tool in allowed_tools {
            let tool = tool.trim();
            if tool.is_empty() || tools.iter().any(|existing| existing == tool) {
                return Err(AisvsError::InvalidMcpPolicy);
            }
            tools.push(tool.to_string());
        }

        Ok(Self {
            schema_name: schema_name.to_string(),
            allowed_tools: tools,
        })
    }

    pub fn schema_name(&self) -> &str {
        &self.schema_name
    }

    pub fn allows_tool(&self, tool: &str) -> bool {
        let tool = tool.trim();
        !tool.is_empty() && self.allowed_tools.iter().any(|allowed| allowed == tool)
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct McpInvocation {
    tool_name: String,
    payload: String,
}

impl McpInvocation {
    pub fn new(tool_name: &str, payload: &str) -> Result<Self, AisvsError> {
        let tool_name = tool_name.trim();
        let payload = payload.trim();
        if tool_name.is_empty() || payload.is_empty() {
            return Err(AisvsError::InvalidMcpPolicy);
        }

        Ok(Self {
            tool_name: tool_name.to_string(),
            payload: payload.to_string(),
        })
    }

    pub fn tool_name(&self) -> &str {
        &self.tool_name
    }

    pub fn payload(&self) -> &str {
        &self.payload
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AdversarialCase {
    family: String,
    payload: String,
}

impl AdversarialCase {
    pub fn new(family: &str, payload: &str) -> Result<Self, AisvsError> {
        let family = family.trim();
        let payload = payload.trim();
        if family.is_empty() || payload.is_empty() {
            return Err(AisvsError::InvalidAdversarialCase);
        }

        Ok(Self {
            family: family.to_string(),
            payload: payload.to_string(),
        })
    }

    pub fn family(&self) -> &str {
        &self.family
    }

    pub fn payload(&self) -> &str {
        &self.payload
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MonitoringPolicy {
    redacts_secrets: bool,
}

impl MonitoringPolicy {
    pub const fn strict_redaction() -> Self {
        Self {
            redacts_secrets: true,
        }
    }

    pub const fn redacts_secrets(&self) -> bool {
        self.redacts_secrets
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MonitoringEvent {
    component: String,
    message: String,
}

impl MonitoringEvent {
    pub fn new(component: &str, message: &str) -> Result<Self, AisvsError> {
        let component = component.trim();
        let message = message.trim();
        if component.is_empty() || message.is_empty() {
            return Err(AisvsError::InvalidMonitoringEvent);
        }

        Ok(Self {
            component: component.to_string(),
            message: message.to_string(),
        })
    }

    pub fn component(&self) -> &str {
        &self.component
    }

    pub fn message(&self) -> &str {
        &self.message
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
                "cargo test -p tachi-core --test aisvs_controls c01_training_data_asset_requires_provenance_and_integrity",
                "Tests prove invalid lineage is unrepresentable and provenance is preserved.",
            ),
            AisvsControl::new(
                AisvsControlId::C02,
                "Input validation and normalization",
                "Typed input envelopes",
                "Reject malformed or ambiguous prompts",
                "Input validation and normalization",
                "cargo test -p tachi-core --test aisvs_controls c02_prompt_input_rejects_blank_ambiguous_and_control_bytes",
                "Tests prove malformed inputs fail closed before downstream use.",
            ),
            AisvsControl::new(
                AisvsControlId::C03,
                "Model lifecycle management",
                "Versioned model policies",
                "Pin, promote, and retire models safely",
                "Model lifecycle management",
                "cargo test -p tachi-core --test aisvs_controls c03_lifecycle_gate_forbids_skipping_validation_states",
                "Tests prove lifecycle transitions require explicit approval states.",
            ),
            AisvsControl::new(
                AisvsControlId::C04,
                "Infrastructure hardening",
                "Runtime isolation boundaries",
                "Constrain execution and deployment surfaces",
                "Infrastructure hardening",
                "cargo test -p tachi-core --test aisvs_controls c04_infrastructure_policy_defaults_to_least_privilege",
                "Tests prove infrastructure defaults stay least privilege.",
            ),
            AisvsControl::new(
                AisvsControlId::C05,
                "Access control and identity",
                "Typed authorization contexts",
                "Authorize only authenticated actors",
                "Access control and identity",
                "cargo test -p tachi-core --test aisvs_controls c05_access_context_requires_explicit_mode_and_role",
                "Tests prove identity and authorization decisions are explicit.",
            ),
            AisvsControl::new(
                AisvsControlId::C06,
                "Supply chain assurance",
                "Pinned dependency evidence",
                "Track and remediate upstream advisories",
                "Supply chain assurance",
                "cargo test -p tachi-core --test aisvs_controls c06_supply_chain_evidence_requires_attestation_and_audit_tag",
                "Tests prove vulnerable dependencies are surfaced and gated.",
            ),
            AisvsControl::new(
                AisvsControlId::C07,
                "Model behavior control",
                "Typed output contracts",
                "Constrain model outputs to expected schemas",
                "Model behavior control",
                "cargo test -p tachi-core --test aisvs_controls c07_model_behavior_policy_rejects_unbounded_free_form_output",
                "Tests prove outputs are normalized before use.",
            ),
            AisvsControl::new(
                AisvsControlId::C08,
                "Memory and embeddings governance",
                "Scoped retrieval policies",
                "Prevent unsafe reuse of stored context",
                "Memory and embeddings governance",
                "cargo test -p tachi-core --test aisvs_controls c08_memory_scope_rejects_unbounded_retention_and_cross_scope_use",
                "Tests prove retrieval obeys scope and retention rules.",
            ),
            AisvsControl::new(
                AisvsControlId::C09,
                "Orchestration and agentic action",
                "Typed action boundaries",
                "Gate autonomous actions behind policy checks",
                "Orchestration and agentic action",
                "cargo test -p tachi-core --test aisvs_controls c09_orchestration_policy_requires_approval_before_escalation",
                "Tests prove action execution cannot bypass policy seams.",
            ),
            AisvsControl::new(
                AisvsControlId::C10,
                "MCP security",
                "Typed tool invocation policies",
                "Restrict tool access to approved capabilities",
                "MCP security",
                "cargo test -p tachi-core --test aisvs_controls c10_mcp_policy_requires_schema_and_tool_allowlist",
                "Tests prove tool calls cannot exceed declared capability scope.",
            ),
            AisvsControl::new(
                AisvsControlId::C11,
                "Adversarial robustness",
                "Robustness regression suite",
                "Capture hostile inputs and rejection behavior",
                "Adversarial robustness",
                "cargo test -p tachi-core --test aisvs_controls c11_adversarial_case_is_explicit_and_fail_closed",
                "Tests prove adversarial cases remain fail-closed.",
            ),
            AisvsControl::new(
                AisvsControlId::C12,
                "Monitoring and logging",
                "Redaction-safe telemetry",
                "Log security evidence without secrets or PII leakage",
                "Monitoring and logging",
                "cargo test -p tachi-core --test aisvs_controls c12_monitoring_policy_redacts_secrets_and_rejects_empty_events",
                "Tests prove logs remain sanitized and actionable.",
            ),
        ],
    }
}
