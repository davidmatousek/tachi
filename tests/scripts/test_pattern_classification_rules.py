"""Structural invariant tests for the classification rule table in
``.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md``
Section 3 (Feature 142 — MAESTRO Phase 3 Agentic Pattern Expansion).

Four invariants validated (per Feature 142 tasks.md T012):

1. **All 6 patterns covered by >=1 rule**: every canonical CSA MAESTRO
   pattern name appears as at least one rule's ``pattern`` value. No
   orphan patterns (FR-001).

2. **Every rule's ``match_conditions`` references only documented tokens**:
   ``category_in`` subset-of finding.category enum,
   ``maestro_layer_in`` subset-of finding.maestro_layer enum,
   ``architecture_has.component_type`` subset-of the 4 Entity 3 tokens,
   ``architecture_has.topology`` subset-of the 4 Entity 3 indicators.

3. **All net-new generation rules have a non-empty template with
   placeholders**: every rule with
   ``generates_finding_when_no_match: true`` must carry a non-empty
   ``generation_template`` containing at least one ``{placeholder}``.

4. **Rule priority is total-ordered** (no ambiguous priority on equal
   specificity) — every rule has an integer ``priority`` field and the
   initial rule set R-01..R-06 uses distinct priorities (10/20/30/40/
   50/60 per data-model.md Initial Rule Set table).

These tokens are authoritative per
``specs/142-maestro-agentic-pattern-expansion/data-model.md`` Entity 3
Component Type Token List / Topology Indicator Token List. Adding a
new token requires a minor version bump on
``maestro-agentic-patterns-shared.md`` (per the determinism invariant
in Section 3) and a corresponding update to this test file's constants.

Zero new runtime dependencies per FR-020 — uses stdlib + PyYAML
(already present transitively via pytest / typical dev environments).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

# =============================================================================
# Constants: Documented token lists (specs/142-.../data-model.md Entity 3)
# =============================================================================

# Repo root resolved from this test file location: tests/scripts/test_*.py
REPO_ROOT = Path(__file__).resolve().parents[2]

SHARED_REF_PATH = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-shared"
    / "references"
    / "maestro-agentic-patterns-shared.md"
)

FINDING_SCHEMA_PATH = REPO_ROOT / "schemas" / "finding.yaml"

# Six canonical pattern names per data-model.md Entity 2 (matches the
# ``agentic_pattern`` enum in schemas/finding.yaml minus ``none`` and
# ``multiple`` sentinels). Ordering matches Section 1 canonical ordering.
CANONICAL_PATTERNS = {
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
}

# Four component_type tokens per data-model.md Entity 3 Component Type Token
# List (authoritative finite enumeration; per determinism invariant).
DOCUMENTED_COMPONENT_TYPES = {
    "fine_tuning_pipeline",
    "persistent_agent_memory",
    "long_running_learning_loop",
    "inter_agent_channel",
}

# Four topology indicators per data-model.md Entity 3 Topology Indicator
# Token List (authoritative finite enumeration; per determinism invariant).
DOCUMENTED_TOPOLOGY_INDICATORS = {
    "multi_agent",
    "inter_agent_data_flow",
    "persistent_state",
    "inter_agent_channel",
}

# Rules with generates_finding_when_no_match: true — per data-model.md
# Entity 3 Initial Rule Set table, these are exactly R-01, R-02, R-03
# (the three previously-uncovered patterns).
EXPECTED_NET_NEW_RULE_IDS = {"R-01", "R-02", "R-03"}

# Expected priorities for the initial rule set R-01..R-06 per data-model.md
# Initial Rule Set table. Distinct values (total ordering) is the tested
# expectation for Invariant 4.
EXPECTED_RULE_PRIORITIES = {
    "R-01": 10,
    "R-02": 20,
    "R-03": 30,
    "R-04": 40,
    "R-05": 50,
    "R-06": 60,
}

# Placeholder regex — matches Python str.format() style ``{name}`` tokens.
PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


# =============================================================================
# Rule table extraction
# =============================================================================

# Match the FIRST fenced YAML block in Section 3 of the shared reference.
# The rule table is published inside a ```yaml ... ``` block immediately
# after the ``## Section 3`` heading. We anchor on ``## Section 3`` to
# avoid accidentally picking up later code fences (e.g., Section 4
# algorithm pseudocode).
_SECTION_3_RE = re.compile(
    r"##\s+Section\s+3[^\n]*\n(.*?)(?:\n##\s+|\Z)",
    re.DOTALL,
)
_YAML_FENCE_RE = re.compile(
    r"```yaml\s*\n(.*?)\n```",
    re.DOTALL,
)


def _extract_rule_table_yaml(shared_ref_text: str) -> str:
    """Return the raw YAML string containing the rule table.

    Raises ``AssertionError`` with a diagnostic message if the expected
    structure (Section 3 heading followed by a fenced ``yaml`` block) is
    not found — this is itself a structural invariant on the shared ref.
    """
    sec3_match = _SECTION_3_RE.search(shared_ref_text)
    assert sec3_match is not None, (
        "Section 3 heading not found in "
        f"{SHARED_REF_PATH} — expected ``## Section 3`` heading."
    )
    fence_match = _YAML_FENCE_RE.search(sec3_match.group(1))
    assert fence_match is not None, (
        "No fenced ``yaml`` block found inside Section 3 — expected "
        "```yaml ... ``` code fence containing the ``rules:`` list."
    )
    return fence_match.group(1)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def rule_table() -> list[dict]:
    """Parse the rule table from the shared reference Section 3 once per module."""
    shared_ref_text = SHARED_REF_PATH.read_text(encoding="utf-8")
    yaml_text = _extract_rule_table_yaml(shared_ref_text)
    parsed = yaml.safe_load(yaml_text)
    assert isinstance(parsed, dict) and "rules" in parsed, (
        "Rule table YAML block must parse as a dict with a top-level ``rules`` key; "
        f"got keys={list(parsed) if isinstance(parsed, dict) else type(parsed).__name__}"
    )
    rules = parsed["rules"]
    assert isinstance(rules, list) and len(rules) >= 6, (
        f"Rule table must contain at least 6 rules (R-01..R-06); got {len(rules) if isinstance(rules, list) else 'non-list'}"
    )
    return rules


@pytest.fixture(scope="module")
def finding_schema_enums() -> dict:
    """Parse ``schemas/finding.yaml`` once per module and return enum lists.

    Returns a dict with:
        ``category``          — set[str] of 8 STRIDE+AI finding categories
        ``maestro_layer``     — set[str] of 8 MAESTRO layer enum values
        ``agentic_pattern``   — set[str] of 8 agentic_pattern enum values
    """
    schema_text = FINDING_SCHEMA_PATH.read_text(encoding="utf-8")
    schema = yaml.safe_load(schema_text)
    finding = schema["finding"]
    return {
        "category": set(finding["category"]["enum"]),
        "maestro_layer": set(finding["maestro_layer"]["enum"]),
        "agentic_pattern": set(finding["agentic_pattern"]["enum"]),
    }


def _rule_id_param(rule: dict) -> str:
    """Return a stable pytest parametrize id from a rule dict."""
    return str(rule.get("rule_id", "<missing-rule_id>"))


# =============================================================================
# Invariant 1: All 6 canonical patterns covered by >=1 rule
# =============================================================================


def test_all_six_patterns_covered_by_at_least_one_rule(rule_table):
    """Every canonical CSA MAESTRO pattern appears as a rule.pattern value.

    Per FR-001: the initial rule set R-01..R-06 covers all six patterns
    one-to-one. Orphan patterns (declared in the schema enum but unreachable
    from any rule) would undermine the gap analysis purpose of the Coverage
    Mapping Table (Section 2).
    """
    patterns_in_rules = {rule.get("pattern") for rule in rule_table}
    missing = CANONICAL_PATTERNS - patterns_in_rules
    assert not missing, (
        f"Patterns declared canonical in data-model.md Entity 2 but not covered "
        f"by any rule in Section 3: {sorted(missing)}. "
        f"Patterns found in rules: {sorted(p for p in patterns_in_rules if p)}"
    )


def test_rule_patterns_are_within_schema_enum(rule_table, finding_schema_enums):
    """Every rule.pattern value is a valid agentic_pattern enum member.

    Rules must not assign pattern values outside the finding schema enum —
    doing so would produce findings that fail schema validation downstream.
    The ``none`` and ``multiple`` sentinels are NOT valid rule outputs (they
    are assigned by the synthesis engine's default / tie-breaking logic).
    """
    valid_rule_patterns = finding_schema_enums["agentic_pattern"] - {"none", "multiple"}
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        pattern = rule.get("pattern")
        assert pattern in valid_rule_patterns, (
            f"Rule {rule_id} has pattern={pattern!r} — must be one of "
            f"{sorted(valid_rule_patterns)} (canonical patterns minus "
            "``none`` and ``multiple`` sentinels)."
        )


# =============================================================================
# Invariant 2: match_conditions reference only documented tokens
# =============================================================================


@pytest.fixture(scope="module")
def rule_table_params(rule_table):
    """Return pytest.param list of (rule_id, rule) tuples for parametrize."""
    return [pytest.param(rule, id=_rule_id_param(rule)) for rule in rule_table]


def test_every_rule_has_match_conditions(rule_table):
    """Every rule declares a ``match_conditions`` block (may be empty)."""
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        assert "match_conditions" in rule, (
            f"Rule {rule_id} missing required ``match_conditions`` field."
        )
        assert isinstance(rule["match_conditions"], dict), (
            f"Rule {rule_id} ``match_conditions`` must be a dict; "
            f"got {type(rule['match_conditions']).__name__}."
        )


def test_rule_category_in_values_are_schema_enum_members(
    rule_table, finding_schema_enums
):
    """Every ``category_in`` value is a finding.category enum member.

    Per schemas/finding.yaml, valid categories are the 8 STRIDE+AI strings:
    spoofing, tampering, repudiation, info-disclosure, denial-of-service,
    privilege-escalation, agentic, llm. A typo or stale enum value would
    produce a rule that never fires (silent miss).
    """
    valid_categories = finding_schema_enums["category"]
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        cond = rule["match_conditions"]
        category_list = cond.get("category_in") or []
        invalid = set(category_list) - valid_categories
        assert not invalid, (
            f"Rule {rule_id} ``category_in`` contains values not in "
            f"schemas/finding.yaml category enum: {sorted(invalid)}. "
            f"Valid values: {sorted(valid_categories)}."
        )


def test_rule_maestro_layer_in_values_are_schema_enum_members(
    rule_table, finding_schema_enums
):
    """Every ``maestro_layer_in`` value (if present) is a schema enum member.

    R-01..R-06 do not use this field (reserved for future rules per
    Section 3 Match Condition Semantics note). When introduced, values
    must match the Feature 136 canonical layer names (``L1 — Foundation
    Model``, ... ``L7 — Agent Ecosystem``, ``Unclassified``).
    """
    valid_layers = finding_schema_enums["maestro_layer"]
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        cond = rule["match_conditions"]
        layer_list = cond.get("maestro_layer_in") or []
        invalid = set(layer_list) - valid_layers
        assert not invalid, (
            f"Rule {rule_id} ``maestro_layer_in`` contains values not in "
            f"schemas/finding.yaml maestro_layer enum: {sorted(invalid)}. "
            f"Valid values: {sorted(valid_layers)}."
        )


def test_rule_architecture_has_component_type_values_are_documented(rule_table):
    """Every ``architecture_has.component_type`` token is documented.

    Tokens are constrained to the 4 Entity 3 Component Type Token List
    values. Fuzzy matching and LLM interpretation are prohibited per
    Section 3 determinism invariant.
    """
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        arch_has = rule["match_conditions"].get("architecture_has") or {}
        component_types = arch_has.get("component_type") or []
        invalid = set(component_types) - DOCUMENTED_COMPONENT_TYPES
        assert not invalid, (
            f"Rule {rule_id} ``architecture_has.component_type`` contains "
            f"undocumented tokens: {sorted(invalid)}. "
            f"Valid tokens per data-model.md Entity 3: "
            f"{sorted(DOCUMENTED_COMPONENT_TYPES)}."
        )


def test_rule_architecture_has_topology_values_are_documented(rule_table):
    """Every ``architecture_has.topology`` token is documented.

    Tokens are constrained to the 4 Entity 3 Topology Indicator Token List
    values. Adding new indicators requires a minor version bump on the
    shared reference (per Section 3 determinism invariant).
    """
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        arch_has = rule["match_conditions"].get("architecture_has") or {}
        topology = arch_has.get("topology") or []
        invalid = set(topology) - DOCUMENTED_TOPOLOGY_INDICATORS
        assert not invalid, (
            f"Rule {rule_id} ``architecture_has.topology`` contains "
            f"undocumented indicators: {sorted(invalid)}. "
            f"Valid indicators per data-model.md Entity 3: "
            f"{sorted(DOCUMENTED_TOPOLOGY_INDICATORS)}."
        )


# =============================================================================
# Invariant 3: generates_finding_when_no_match: true rules have templates
# =============================================================================


def test_generation_flag_present_on_every_rule(rule_table):
    """Every rule declares ``generates_finding_when_no_match`` as a boolean."""
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        assert "generates_finding_when_no_match" in rule, (
            f"Rule {rule_id} missing required "
            "``generates_finding_when_no_match`` field."
        )
        flag = rule["generates_finding_when_no_match"]
        assert isinstance(flag, bool), (
            f"Rule {rule_id} ``generates_finding_when_no_match`` must be a "
            f"bool; got {type(flag).__name__}={flag!r}"
        )


def test_net_new_generation_rules_match_expected_rule_ids(rule_table):
    """Exactly R-01, R-02, R-03 set the generation flag to true.

    Per data-model.md Entity 3 Initial Rule Set table, these are the three
    previously-uncovered patterns (Agent Collusion, Temporal Attack,
    Emergent Behavior). R-04/R-05/R-06 rely on existing agents (spoofing,
    tool-abuse, info-disclosure, denial-of-service) to produce findings
    that the rule retroactively classifies — no net-new generation.
    """
    actual_true = {
        rule["rule_id"]
        for rule in rule_table
        if rule.get("generates_finding_when_no_match") is True
    }
    assert actual_true == EXPECTED_NET_NEW_RULE_IDS, (
        f"Rules with generates_finding_when_no_match=true mismatch data-model.md "
        f"Entity 3 Initial Rule Set table. Expected: "
        f"{sorted(EXPECTED_NET_NEW_RULE_IDS)}. Got: {sorted(actual_true)}."
    )


def test_net_new_generation_rules_have_non_empty_template_with_placeholder(
    rule_table,
):
    """Rules with ``generates_finding_when_no_match: true`` carry a usable template.

    Three checks:
        1. ``generation_template`` is present.
        2. Template is a non-empty string (after stripping whitespace).
        3. Template contains at least one ``{placeholder}`` token (otherwise
           the rendered finding description would be identical across all
           architectures — a degenerate generation).
    """
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        if not rule.get("generates_finding_when_no_match"):
            continue
        assert "generation_template" in rule, (
            f"Rule {rule_id} has generates_finding_when_no_match=true but "
            "no ``generation_template`` field."
        )
        template = rule["generation_template"]
        assert isinstance(template, str), (
            f"Rule {rule_id} ``generation_template`` must be a string; "
            f"got {type(template).__name__}."
        )
        assert template.strip(), (
            f"Rule {rule_id} ``generation_template`` is empty/whitespace-only."
        )
        placeholders = PLACEHOLDER_RE.findall(template)
        assert placeholders, (
            f"Rule {rule_id} ``generation_template`` contains no "
            "``{placeholder}`` tokens — rendered finding description would "
            "be constant across architectures. Expected at least one "
            "placeholder (e.g., ``{component}``, ``{architecture_context}``)."
        )


def test_non_generating_rules_do_not_require_template(rule_table):
    """Rules with ``generates_finding_when_no_match: false`` MAY omit a template.

    This invariant is the converse of the prior test: R-04/R-05/R-06 are not
    required to carry ``generation_template``. The test documents this
    flexibility — if a future rule is refactored from generating to
    non-generating, no template cleanup is required.
    """
    # This test is intentionally permissive — it passes whether or not
    # non-generating rules carry templates. Documents the flexibility.
    non_generating_rules = [
        rule for rule in rule_table
        if rule.get("generates_finding_when_no_match") is False
    ]
    assert non_generating_rules, (
        "Expected at least one rule with generates_finding_when_no_match=false "
        "(R-04/R-05/R-06 per data-model.md)."
    )


# =============================================================================
# Invariant 4: Rule priority is total-ordered (initial rule set R-01..R-06)
# =============================================================================


def test_every_rule_has_integer_priority(rule_table):
    """Every rule declares an integer ``priority`` field."""
    for rule in rule_table:
        rule_id = rule.get("rule_id", "<unknown>")
        assert "priority" in rule, (
            f"Rule {rule_id} missing required ``priority`` field."
        )
        priority = rule["priority"]
        # Reject bool (which is a subclass of int in Python); priorities
        # must be genuine integers.
        assert isinstance(priority, int) and not isinstance(priority, bool), (
            f"Rule {rule_id} ``priority`` must be a non-boolean integer; "
            f"got {type(priority).__name__}={priority!r}."
        )


def test_initial_rule_set_priorities_are_total_ordered(rule_table):
    """R-01..R-06 priorities are distinct (no ambiguous tie-breaking).

    Per Section 3 Rule Priority and Tie-Breaking note: the initial rule
    set uses distinct priorities (10/20/30/40/50/60). Equal priority
    triggers ``agentic_pattern: multiple`` (rare; a design signal, not a
    default). A duplicate priority in R-01..R-06 would be an accidental
    tie — this test catches that.
    """
    priorities = [rule["priority"] for rule in rule_table]
    duplicates = [p for p in set(priorities) if priorities.count(p) > 1]
    assert not duplicates, (
        f"Duplicate priority values in rule table: {sorted(duplicates)}. "
        "The initial rule set R-01..R-06 must use distinct priorities per "
        "data-model.md Entity 3 Initial Rule Set table. Equal priority is "
        "reserved for intentional ``agentic_pattern: multiple`` assignment "
        "and requires an explicit tie-breaking design note on the rule's "
        "minor version bump."
    )


def test_initial_rule_set_priorities_match_data_model(rule_table):
    """R-01..R-06 priorities match data-model.md exactly (10/20/30/40/50/60).

    This is a stronger check than total-ordering: it asserts the specific
    priority values documented in the data-model.md Initial Rule Set
    table. Changing a priority without updating data-model.md would
    drift the two surfaces.
    """
    actual = {
        rule["rule_id"]: rule["priority"]
        for rule in rule_table
        if rule.get("rule_id") in EXPECTED_RULE_PRIORITIES
    }
    assert actual == EXPECTED_RULE_PRIORITIES, (
        "Rule priorities do not match data-model.md Initial Rule Set table. "
        f"Expected: {EXPECTED_RULE_PRIORITIES}. Got: {actual}."
    )


def test_priority_ascending_order_matches_rule_id_order(rule_table):
    """Ascending priority order corresponds to ascending R-NN rule_id order.

    Human readers scan rule tables top-to-bottom. When priority order
    matches rule_id order, the reader's mental model (R-01 evaluated
    first) aligns with runtime behavior (priority 10 evaluated first).
    Divergence is a readability footgun.

    Only checked for the initial rule set (R-NN with NN <= 06); future
    rules MAY be inserted between existing rules with non-monotonic
    rule_id ordering if a design rationale is documented.
    """
    initial_rules = sorted(
        [r for r in rule_table if r.get("rule_id") in EXPECTED_RULE_PRIORITIES],
        key=lambda r: r["rule_id"],
    )
    priorities = [r["priority"] for r in initial_rules]
    assert priorities == sorted(priorities), (
        "R-01..R-06 priority order does not match rule_id ascending order. "
        f"rule_id order: {[r['rule_id'] for r in initial_rules]}, "
        f"priorities: {priorities}. For readability, ascending rule_id "
        "should map to ascending priority in the initial rule set."
    )
