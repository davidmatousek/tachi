"""Unit tests for Phase 3.6 Pattern Synthesis Engine (Feature 142).

Phase 3.6 lives in the orchestrator markdown agent spec
(`.claude/agents/tachi/orchestrator.md`) — it is not implemented as Python
code that the test suite can invoke directly. These tests exercise the
synthesis engine's inputs and outputs through reference implementations
of the canonical algorithm described in:

  - specs/142-maestro-agentic-pattern-expansion/data-model.md
    Entity 3 (Classification Rule), Entity 4 (Multi-Agent Gate Predicate),
    Entity 5 (Net-New Generated Finding)
  - .claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md
    Section 3 (Rule Table), Section 4 (Gate Predicate)

The reference implementations below (`_evaluate_multi_agent_gate`,
`_classify_finding`, `_generate_net_new_findings`) are authoritative for
the test suite. Any divergence between these implementations and the
agent-driven synthesis at runtime is a test-tier bug to fix here, OR an
engine-tier bug to fix in the orchestrator agent — resolution direction
depends on which side diverges from the canonical data-model.md spec.

Six test areas per tasks.md T011:

  1. Multi-agent gate predicate across 6 baseline architectures +
     synthetic single-agent-with-persistent-state fixture (LOW-5)
  2. Classification rule precedence + tied-priority `multiple` assignment
  3. Net-new finding generation triggers + suppression (label match and
     ≥80% token-overlap content match per LOW-7 / LOW-T11-1)
  4. Determinism — same input twice produces byte-identical output (ADR-021)
  5. Backward compat — pre-Feature-142 finding IR without `agentic_pattern`
     field defaults to `none` (FR-017)
  6. Idempotence — run synthesis twice, second run zero new, zero modified
     (PM LOW-2)
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import pytest


# Make tachi_parsers importable the same way test_attack_chains.py does.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tachi_parsers import VALID_AGENTIC_PATTERNS  # noqa: E402


# =============================================================================
# Fixture helpers
# =============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pattern_synthesis"

MULTI_AGENT_KEYWORDS = (
    "multi-agent",
    "swarm",
    "supervisor",
    "delegation",
    "agent mesh",
)

PERSISTENT_STATE_TOKENS = {
    "fine_tuning_pipeline": (
        "fine-tuning pipeline",
        "fine tuning pipeline",
        "training pipeline",
        "fine-tune pipeline",
    ),
    "persistent_agent_memory": (
        "agent memory",
        "persistent memory",
        "memory store",
        "long-term memory",
        "agent state store",
    ),
    "long_running_learning_loop": (
        "learning loop",
        "feedback loop",
        "continual learning",
        "rlhf loop",
        "reward model loop",
        "self-improvement loop",
    ),
}

INTER_AGENT_CHANNEL_KEYWORDS = (
    "inter-agent channel",
    "message bus",
    "agent communication channel",
    "shared queue",
    "shared memory",
)


def _load_simple_yaml(path: Path) -> dict:
    """Load a simple YAML fixture into a Python dict.

    A minimal stdlib-only parser for the subset of YAML used in these
    fixtures: top-level mappings, nested mappings, lists of scalars, and
    lists of mappings. This avoids adding PyYAML as a test-suite runtime
    dependency (FR-020 — zero new runtime dependencies) and keeps the
    fixtures human-readable while remaining stdlib-parseable.

    The parser handles:
      - `key: value` (scalar)
      - `key: >` / `key: |` (folded/literal multi-line block scalars)
      - `key:` followed by indented children (mapping or list)
      - `- value` (list item, scalar)
      - `- key: value` (list item, inline mapping start)
      - `#` line comments

    It does NOT handle flow style, anchors, aliases, tags, or nested
    list-of-list. The fixtures here use only the supported subset.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Strip comments and trailing whitespace
    stripped = []
    for raw in lines:
        if raw.lstrip().startswith("#"):
            continue
        # Strip inline comments (best-effort; fixtures avoid '#' in values)
        if "#" in raw:
            pre = raw.split("#", 1)[0]
            raw = pre.rstrip()
        if raw.strip() == "":
            stripped.append("")
        else:
            stripped.append(raw.rstrip())

    result, _ = _yaml_parse_block(stripped, 0, 0)
    return result if isinstance(result, dict) else {}


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _yaml_parse_block(lines: list, idx: int, base_indent: int):
    """Parse a block (mapping or list) starting at lines[idx] at base_indent.

    Returns (value, next_idx).
    """
    # Skip blank lines
    while idx < len(lines) and lines[idx] == "":
        idx += 1
    if idx >= len(lines):
        return None, idx

    first = lines[idx]
    first_indent = _indent(first)
    stripped = first.lstrip(" ")

    if first_indent < base_indent:
        return None, idx

    # List at this level
    if stripped.startswith("- "):
        items = []
        while idx < len(lines):
            if lines[idx] == "":
                idx += 1
                continue
            ln = lines[idx]
            ind = _indent(ln)
            if ind < base_indent:
                break
            if ind == base_indent and ln.lstrip(" ").startswith("- "):
                rest = ln.lstrip(" ")[2:]
                if ":" in rest and not rest.startswith("- "):
                    # List item opens a mapping. The first key/value is on
                    # this line; subsequent keys are indented children.
                    k, v = _split_kv(rest)
                    item = {}
                    if v == "" or v is None:
                        # Child block belongs to k
                        sub, idx = _yaml_parse_block(lines, idx + 1, base_indent + 2)
                        item[k] = sub
                    else:
                        item[k] = _coerce_scalar(v)
                        idx += 1
                    # Parse remaining sibling keys at base_indent+2
                    while idx < len(lines):
                        if lines[idx] == "":
                            idx += 1
                            continue
                        ln2 = lines[idx]
                        ind2 = _indent(ln2)
                        if ind2 < base_indent + 2:
                            break
                        if ind2 == base_indent + 2 and not ln2.lstrip(" ").startswith("- "):
                            k2, v2 = _split_kv(ln2.lstrip(" "))
                            if v2 == "" or v2 is None:
                                sub, idx = _yaml_parse_block(
                                    lines, idx + 1, base_indent + 4
                                )
                                item[k2] = sub
                            elif v2 in (">", "|"):
                                block, idx = _read_block_scalar(
                                    lines, idx + 1, base_indent + 4, v2
                                )
                                item[k2] = block
                            else:
                                item[k2] = _coerce_scalar(v2)
                                idx += 1
                        else:
                            break
                    items.append(item)
                else:
                    items.append(_coerce_scalar(rest))
                    idx += 1
            else:
                break
        return items, idx

    # Mapping at this level
    out = {}
    while idx < len(lines):
        if lines[idx] == "":
            idx += 1
            continue
        ln = lines[idx]
        ind = _indent(ln)
        if ind < base_indent:
            break
        if ind > base_indent:
            # Unexpected deeper indent — stop, let caller handle
            break
        k, v = _split_kv(ln.lstrip(" "))
        if v == "" or v is None:
            sub, idx = _yaml_parse_block(lines, idx + 1, base_indent + 2)
            out[k] = sub if sub is not None else {}
        elif v in (">", "|"):
            block, idx = _read_block_scalar(lines, idx + 1, base_indent + 2, v)
            out[k] = block
        else:
            out[k] = _coerce_scalar(v)
            idx += 1
    return out, idx


def _split_kv(line: str):
    if ":" not in line:
        return line, None
    k, rest = line.split(":", 1)
    return k.strip(), rest.strip()


def _coerce_scalar(value: str):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return ""
    # Strip surrounding quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _read_block_scalar(lines: list, idx: int, base_indent: int, kind: str):
    """Read a folded (`>`) or literal (`|`) block scalar starting at idx."""
    parts = []
    while idx < len(lines):
        ln = lines[idx]
        if ln == "":
            parts.append("")
            idx += 1
            continue
        ind = _indent(ln)
        if ind < base_indent:
            break
        parts.append(ln[base_indent:])
        idx += 1
    if kind == ">":
        text = " ".join(p.strip() for p in parts if p.strip() != "")
    else:
        text = "\n".join(parts).rstrip("\n")
    return text, idx


# =============================================================================
# Reference implementation: Multi-Agent Gate Predicate
# =============================================================================

def _evaluate_multi_agent_gate(architecture: dict) -> dict:
    """Reference implementation of the multi-agent gate predicate.

    Authoritative algorithm per data-model.md Entity 4 and
    maestro-agentic-patterns-shared.md Section 4.

    Three OR conditions:
      (a) >=2 components with category in ["agentic", "llm"]
      (b) >=1 inter-component data flow where BOTH source and target
          components are in ["agentic", "llm"]
      (c) case-insensitive substring match on architecture description
          for any of: multi-agent, swarm, supervisor, delegation,
          agent mesh

    Returns a deterministic dict with `result`, `condition_a`,
    `condition_b`, `condition_c`, and `evaluation_metadata`. Output is
    byte-identical across repeated runs with identical input (ADR-021).
    """
    components = architecture.get("components", []) or []
    flows = architecture.get("data_flows", []) or []
    description = architecture.get("description", "") or ""

    # Condition (a)
    agentic_components = [
        c for c in components
        if c.get("category", "").lower() in ("agentic", "llm")
    ]
    agentic_count = len(agentic_components)
    condition_a = agentic_count >= 2

    # Condition (b)
    category_by_name = {
        c.get("name", ""): c.get("category", "").lower() for c in components
    }
    condition_b = False
    matched_flow = None
    for f in flows:
        src_cat = category_by_name.get(f.get("source", ""), "")
        tgt_cat = category_by_name.get(f.get("target", ""), "")
        if src_cat in ("agentic", "llm") and tgt_cat in ("agentic", "llm"):
            condition_b = True
            matched_flow = (f.get("source"), f.get("target"))
            break

    # Condition (c) — case-insensitive substring match
    desc_lower = description.lower()
    matched_keywords = [k for k in MULTI_AGENT_KEYWORDS if k in desc_lower]
    condition_c = len(matched_keywords) >= 1

    result = condition_a or condition_b or condition_c

    return {
        "result": result,
        "condition_a": condition_a,
        "condition_b": condition_b,
        "condition_c": condition_c,
        "evaluation_metadata": {
            "agentic_llm_count": agentic_count,
            "matched_components": [c.get("name") for c in agentic_components],
            "matched_flow": matched_flow,
            "matched_keywords": matched_keywords,
        },
    }


# =============================================================================
# Reference implementation: Topology indicator evaluation
# =============================================================================

def _architecture_has_topology(architecture: dict, indicator: str) -> bool:
    """Check whether an architecture satisfies a named topology indicator.

    Authoritative list per data-model.md Entity 3 and
    maestro-agentic-patterns-shared.md Section 4 (Topology Indicator List).

    Supported indicators:
      - multi_agent: >=2 agentic/llm components
      - inter_agent_data_flow: >=1 flow where both endpoints are agentic/llm
      - persistent_state: >=1 component matches a persistent_state token
      - inter_agent_channel: >=1 inter_agent_channel token match AND
        multi_agent (composite; both conditions must hold)
    """
    gate = _evaluate_multi_agent_gate(architecture)

    if indicator == "multi_agent":
        return gate["condition_a"]

    if indicator == "inter_agent_data_flow":
        return gate["condition_b"]

    if indicator == "persistent_state":
        text_pool = _architecture_text_pool(architecture)
        for _token_name, keywords in PERSISTENT_STATE_TOKENS.items():
            for kw in keywords:
                if kw in text_pool:
                    return True
        return False

    if indicator == "inter_agent_channel":
        if not gate["condition_a"]:
            return False
        text_pool = _architecture_text_pool(architecture)
        return any(kw in text_pool for kw in INTER_AGENT_CHANNEL_KEYWORDS)

    return False


def _architecture_text_pool(architecture: dict) -> str:
    """Concatenate lowercased text used for component_type token matching."""
    parts = [architecture.get("description", "") or ""]
    for c in architecture.get("components", []) or []:
        parts.append(c.get("name", "") or "")
    return " ".join(parts).lower()


# =============================================================================
# Reference implementation: Rule evaluation / classification
# =============================================================================

def _finding_matches_rule(finding: dict, rule: dict, architecture: dict) -> bool:
    """Return True iff a rule's match_conditions are satisfied for a finding.

    All listed conditions conjoin (AND); each condition's disjunctive
    values conjoin within the condition (ANY).
    """
    mc = rule.get("match_conditions", {}) or {}

    # category_in
    cats = mc.get("category_in")
    if cats is not None:
        if finding.get("category", "") not in cats:
            return False

    # maestro_layer_in (reserved for future rules)
    layers = mc.get("maestro_layer_in")
    if layers is not None:
        if finding.get("maestro_layer", "") not in layers:
            return False

    # target_component_matches
    tcm = mc.get("target_component_matches")
    if tcm:
        regex = tcm.get("type_or_name_regex")
        if regex:
            import re
            component = finding.get("component", "") or ""
            if not re.search(regex, component, flags=re.IGNORECASE):
                return False

    # architecture_has.topology
    arch_has = mc.get("architecture_has") or {}
    topo = arch_has.get("topology")
    if topo:
        if not any(_architecture_has_topology(architecture, t) for t in topo):
            return False

    # description_contains
    desc_tokens = mc.get("description_contains")
    if desc_tokens is not None:
        fdesc = (finding.get("description", "") or "").lower()
        if not any(tok.lower() in fdesc for tok in desc_tokens):
            return False

    return True


def _classify_finding(
    finding: dict, rules: list, architecture: dict
) -> str:
    """Classify a single finding per the rule table.

    Returns the assigned pattern string: one of the six canonical
    pattern names, `none` (no matching rule), or `multiple` (≥2 rules
    match with equal priority).

    Rules are evaluated in ascending priority order (lowest = most
    specific = first). If the lowest-priority match has no tied peer,
    that rule's pattern wins. If two or more rules tie on the lowest
    matching priority, `multiple` is returned.
    """
    matching = [
        r for r in rules if _finding_matches_rule(finding, r, architecture)
    ]
    if not matching:
        return "none"

    matching.sort(key=lambda r: r.get("priority", 10_000))
    best_priority = matching[0].get("priority")
    tied = [r for r in matching if r.get("priority") == best_priority]

    if len(tied) > 1:
        return "multiple"
    return tied[0]["pattern"]


def _jaccard_overlap(a: str, b: str) -> float:
    """Compute token Jaccard similarity between two strings.

    Tokenization: case-fold, split on whitespace, strip common
    punctuation. Returns the ratio |intersection| / |union| of the two
    token sets, with empty-pair handled as 0.0.
    """
    def tokens(s: str) -> set:
        s = (s or "").lower()
        out = set()
        for raw in s.split():
            t = raw.strip(".,;:!?()[]{}\"'`—–-")
            if t:
                out.add(t)
        return out

    ta = tokens(a)
    tb = tokens(b)
    if not ta and not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# =============================================================================
# Reference implementation: Net-new finding generation
# =============================================================================

def _classify_all_findings(
    findings: list, rules: list, architecture: dict, gate_result: bool
) -> list:
    """Return a new list of findings with `agentic_pattern` assigned.

    If the multi-agent gate predicate is FALSE, every finding receives
    `agentic_pattern: none` regardless of the rule table. If TRUE, each
    finding is classified via `_classify_finding`.

    Idempotence invariant (PM LOW-2 / data-model.md Entity 1 State
    Transitions): `agentic_pattern` is set EXACTLY ONCE during Phase
    3.6 synthesis. If a finding already carries a non-default
    `agentic_pattern` (anything other than missing/None/empty/`none`),
    its value is preserved — re-classification is suppressed. This
    preserves net-new generated findings (which carry their rule's
    pattern from Step 3) across a subsequent Phase 3.6 re-invocation.
    """
    out = []
    for f in findings:
        enriched = dict(f)
        if not gate_result:
            enriched["agentic_pattern"] = "none"
        else:
            existing = enriched.get("agentic_pattern")
            if existing and existing != "none":
                # Preserve prior assignment — idempotence (PM LOW-2)
                pass
            else:
                enriched["agentic_pattern"] = _classify_finding(
                    enriched, rules, architecture
                )
        out.append(enriched)
    return out


def _generate_net_new_findings(
    classified_findings: list,
    rules: list,
    architecture: dict,
    gate_result: bool,
    overlap_threshold: float = 0.80,
) -> list:
    """Return a list of net-new AGP-NN findings appended by Phase 3.6 Step 3.

    Generation per data-model.md Entity 5 and plan.md Wave 1:
      - Only rules with `generates_finding_when_no_match: true` may emit
      - Multi-agent gate predicate must be TRUE
      - Suppressed when any existing finding already carries the
        pattern label
      - Also suppressed when any existing finding's description has
        >= `overlap_threshold` Jaccard token overlap with the rule's
        generation_template (LOW-7 / LOW-T11-1 content-overlap
        defense-in-depth)
      - Max 1 net-new finding per pattern per architecture
      - Net-new id format: AGP-NN (sequential per architecture)
    """
    if not gate_result:
        return []

    assigned_patterns = {
        f.get("agentic_pattern") for f in classified_findings
        if f.get("agentic_pattern") not in (None, "", "none")
    }

    new_findings = []
    sequence = 1

    # Evaluate generation candidates in priority order for determinism
    gen_rules = sorted(
        [r for r in rules if r.get("generates_finding_when_no_match")],
        key=lambda r: r.get("priority", 10_000),
    )

    for rule in gen_rules:
        pattern = rule["pattern"]
        if pattern in assigned_patterns:
            continue

        # Check whether architectural context matches the rule's
        # non-finding-level predicates. We ignore category_in,
        # maestro_layer_in, target_component_matches, and
        # description_contains for generation — those are finding-level
        # predicates. architecture_has is the architectural-context
        # gate that governs generation.
        arch_has = (rule.get("match_conditions") or {}).get("architecture_has") or {}
        topo = arch_has.get("topology")
        if topo and not any(
            _architecture_has_topology(architecture, t) for t in topo
        ):
            continue

        # Content-overlap suppression (LOW-7)
        template = rule.get("generation_template") or ""
        if template:
            suppress = False
            for f in classified_findings:
                desc = f.get("description", "") or ""
                if desc and _jaccard_overlap(desc, template) >= overlap_threshold:
                    suppress = True
                    break
            if suppress:
                continue

        # Target component resolution: first agentic/llm component
        target_component = _pick_target_component(architecture, rule)
        if target_component is None:
            continue

        new_findings.append({
            "id": f"AGP-{sequence:02d}",
            "category": "agentic",
            "agentic_pattern": pattern,
            "component": target_component,
            "description": template.replace("{component}", target_component).strip(),
            "likelihood": "Medium",
            "impact": "Medium",
            "risk_level": "Medium",
            "delta_status": "NEW",
        })
        sequence += 1

    return new_findings


def _pick_target_component(architecture: dict, rule: dict) -> str | None:
    """Choose the first matching agentic/llm component as target."""
    components = architecture.get("components", []) or []
    for c in components:
        if c.get("category", "").lower() in ("agentic", "llm"):
            return c.get("name")
    # Fallback to first component if none is agentic/llm (should not
    # happen under multi-agent gate predicate TRUE but preserves
    # defensive safety)
    if components:
        return components[0].get("name")
    return None


def _run_synthesis(
    findings: list, rules: list, architecture: dict
) -> dict:
    """Run Phase 3.6 synthesis end-to-end deterministically.

    Returns a dict with:
      - `gate`: gate predicate evaluation record
      - `classified`: list of existing findings with agentic_pattern set
      - `net_new`: list of net-new AGP-NN findings
      - `has_agentic_patterns`: boolean (has any non-none pattern)
    """
    gate = _evaluate_multi_agent_gate(architecture)
    classified = _classify_all_findings(findings, rules, architecture, gate["result"])
    net_new = _generate_net_new_findings(classified, rules, architecture, gate["result"])
    all_patterns = {
        f.get("agentic_pattern") for f in classified + net_new
        if f.get("agentic_pattern") not in (None, "", "none")
    }
    return {
        "gate": gate,
        "classified": classified,
        "net_new": net_new,
        "has_agentic_patterns": len(all_patterns) > 0,
    }


# =============================================================================
# Pytest fixtures
# =============================================================================

@pytest.fixture(scope="session")
def rules_table():
    """Load the test-local rule-table mirror from rules.yaml.

    The fixture copy is kept in sync with Section 3 of
    maestro-agentic-patterns-shared.md. Including two synthetic
    tied-priority rules (R-TIE-A / R-TIE-B) enables the
    `multiple`-assignment test without editing the shared reference.
    """
    data = _load_simple_yaml(FIXTURES_DIR / "rules.yaml")
    return data.get("rules", [])


@pytest.fixture(scope="session")
def canonical_rules(rules_table):
    """Return only R-01 through R-06 — the canonical rule table."""
    return [r for r in rules_table if str(r.get("rule_id", "")).startswith("R-0")]


@pytest.fixture(scope="session")
def synthetic_tie_rules(rules_table):
    """Return the two synthetic tied-priority rules R-TIE-A and R-TIE-B."""
    return [r for r in rules_table if str(r.get("rule_id", "")).startswith("R-TIE")]


@pytest.fixture(scope="session")
def architectures():
    """Load all architecture fixtures into a name-keyed dict."""
    names = [
        "web_app",
        "microservices",
        "ascii_web_api",
        "mermaid_agentic_app",
        "free_text_microservice",
        "agentic_app_extended",
        "single_agent_with_fine_tuning",
    ]
    out = {}
    for n in names:
        out[n] = _load_simple_yaml(FIXTURES_DIR / f"arch_{n}.yaml")
    return out


# =============================================================================
# Tests — Area 1: Multi-Agent Gate Predicate
# =============================================================================

class TestMultiAgentGatePredicate:
    """Gate predicate evaluation across 6 baselines + synthetic single-agent."""

    def test_web_app_gate_false(self, architectures):
        """web-app: no agentic components, predicate FALSE."""
        gate = _evaluate_multi_agent_gate(architectures["web_app"])
        assert gate["result"] is False
        assert gate["condition_a"] is False
        assert gate["condition_b"] is False
        assert gate["condition_c"] is False

    def test_microservices_gate_false(self, architectures):
        """microservices: non-agentic architecture, predicate FALSE."""
        gate = _evaluate_multi_agent_gate(architectures["microservices"])
        assert gate["result"] is False
        assert gate["condition_a"] is False
        assert gate["condition_b"] is False
        assert gate["condition_c"] is False

    def test_ascii_web_api_gate_false(self, architectures):
        """ascii-web-api: non-agentic architecture, predicate FALSE."""
        gate = _evaluate_multi_agent_gate(architectures["ascii_web_api"])
        assert gate["result"] is False

    def test_free_text_microservice_gate_false(self, architectures):
        """free-text-microservice: non-agentic architecture, predicate FALSE."""
        gate = _evaluate_multi_agent_gate(architectures["free_text_microservice"])
        assert gate["result"] is False

    def test_mermaid_agentic_app_gate_true_via_condition_a(self, architectures):
        """mermaid-agentic-app: TRUE via condition (a) alone (2 agents).

        No inter-agent flow, no multi-agent keyword — rule table must
        not subsequently match any non-`none` pattern on this
        architecture (backward-compat preservation).
        """
        gate = _evaluate_multi_agent_gate(architectures["mermaid_agentic_app"])
        assert gate["result"] is True
        assert gate["condition_a"] is True
        assert gate["condition_b"] is False
        assert gate["condition_c"] is False

    def test_agentic_app_extended_gate_true_all_conditions(self, architectures):
        """agentic-app-extended: TRUE via ALL three conditions a/b/c."""
        gate = _evaluate_multi_agent_gate(architectures["agentic_app_extended"])
        assert gate["result"] is True
        assert gate["condition_a"] is True
        assert gate["condition_b"] is True
        assert gate["condition_c"] is True

    def test_single_agent_with_fine_tuning_gate_false(self, architectures):
        """Synthetic LOW-5 fixture: single agent + fine-tuning, predicate FALSE.

        Only one agentic component (Specialist Agent). The fine-tuning
        pipeline is `process` category, not agentic. No multi-agent
        keywords. All three gate conditions fail.

        This validates the spec Edge Case 4 scope boundary: Temporal
        Attacks on single-agent architectures are deliberately excluded.
        """
        arch = architectures["single_agent_with_fine_tuning"]
        gate = _evaluate_multi_agent_gate(arch)
        assert gate["result"] is False
        assert gate["condition_a"] is False
        assert gate["condition_b"] is False
        assert gate["condition_c"] is False
        assert gate["evaluation_metadata"]["agentic_llm_count"] == 1

    @pytest.mark.parametrize(
        "arch_name,expected",
        [
            ("web_app", False),
            ("microservices", False),
            ("ascii_web_api", False),
            ("free_text_microservice", False),
            ("single_agent_with_fine_tuning", False),
            ("mermaid_agentic_app", True),
            ("agentic_app_extended", True),
        ],
    )
    def test_gate_result_parametrized(self, architectures, arch_name, expected):
        """Parametrized sweep over all 7 architectures (6 baselines + synthetic)."""
        gate = _evaluate_multi_agent_gate(architectures[arch_name])
        assert gate["result"] is expected


# =============================================================================
# Tests — Area 2: Classification rule precedence + tied-priority `multiple`
# =============================================================================

class TestClassificationRulePrecedence:
    """Classification rule evaluation: precedence and tied-priority handling."""

    def test_rule_precedence_lowest_priority_wins(
        self, canonical_rules, architectures
    ):
        """Among matching rules, lowest priority wins.

        Construct a finding that matches both R-01 (priority 10) and
        R-04 (priority 40) on the agentic-app-extended architecture.
        R-01 fires first because priority 10 < priority 40.
        """
        arch = architectures["agentic_app_extended"]
        finding = {
            "id": "AG-9",
            "category": "agentic",
            "component": "LLM Agent Orchestrator",
            "description": "Coordinated peer-agent exploit with identity spoofing.",
        }
        assigned = _classify_finding(finding, canonical_rules, arch)
        assert assigned == "agent_collusion"

    def test_tied_priority_assigns_multiple(
        self, synthetic_tie_rules, architectures
    ):
        """Two rules share priority and both match → `multiple`."""
        arch = architectures["agentic_app_extended"]
        finding = {
            "id": "AG-77",
            "category": "agentic",
            "component": "LLM Agent Orchestrator",
            "description": "A synthetic_tie_marker threat exercising both tied rules.",
        }
        assigned = _classify_finding(finding, synthetic_tie_rules, arch)
        assert assigned == "multiple"

    def test_no_matching_rule_assigns_none(
        self, canonical_rules, architectures
    ):
        """A finding that matches no rule receives `none`.

        Uses mermaid-agentic-app: gate predicate TRUE via condition (a)
        but architecture has NO persistent_state, NO inter_agent_channel,
        and the description lacks emergent-behavior keywords — so none
        of R-01 through R-06 match on a process-category finding.
        """
        arch = architectures["mermaid_agentic_app"]
        finding = {
            "id": "X-1",
            "category": "process",  # Does not match any canonical rule
            "component": "User Interface",
            "description": "Clickjacking attack on the login form.",
        }
        assigned = _classify_finding(finding, canonical_rules, arch)
        assert assigned == "none"

    def test_r03_requires_description_token(
        self, canonical_rules, architectures
    ):
        """R-03 fires only when description contains an emergent token.

        Uses mermaid-agentic-app (gate TRUE via condition (a), no
        persistent_state, no inter_agent_channel). This isolates R-03
        cleanly — R-01 requires inter_agent_data_flow (absent), R-02
        requires persistent_state (absent).
        """
        arch = architectures["mermaid_agentic_app"]

        hit = {
            "id": "AG-20",
            "category": "agentic",
            "component": "Agent One",
            "description": "A cascade of agent interactions amplifies errors.",
        }
        miss = {
            "id": "AG-21",
            "category": "agentic",
            "component": "Agent One",
            "description": "A benign workflow handling a simple user query.",
        }
        # Use only R-03 so lower-priority rules cannot claim the hit
        r03 = [r for r in canonical_rules if r["rule_id"] == "R-03"]
        assert _classify_finding(hit, r03, arch) == "emergent_behavior"
        assert _classify_finding(miss, r03, arch) == "none"


# =============================================================================
# Tests — Area 3: Net-new finding generation — triggers + suppression
# =============================================================================

class TestNetNewFindingGeneration:
    """Net-new AGP-NN finding emission, label-match suppression, content-overlap."""

    def test_netnew_triggered_when_no_existing_match(
        self, canonical_rules, architectures
    ):
        """Generate net-new findings for uncovered patterns when none exist.

        agentic-app-extended satisfies the gate predicate + topology
        indicators for R-01 (Agent Collusion) + R-02 (Temporal Attack)
        + R-03 (Emergent Behavior). With no existing findings, all
        three generator rules emit AGP-NN findings.
        """
        arch = architectures["agentic_app_extended"]
        result = _run_synthesis([], canonical_rules, arch)

        assert result["gate"]["result"] is True
        patterns = {f["agentic_pattern"] for f in result["net_new"]}
        assert "agent_collusion" in patterns
        assert "temporal_attack" in patterns
        assert "emergent_behavior" in patterns
        assert len(result["net_new"]) == 3

        # All net-new ids follow AGP-NN format, sequential
        ids = [f["id"] for f in result["net_new"]]
        assert ids == ["AGP-01", "AGP-02", "AGP-03"]

    def test_netnew_skipped_when_existing_label_match(
        self, canonical_rules, architectures
    ):
        """Skip generation for a pattern when an existing finding carries it.

        Pre-populate one existing finding tagged `agent_collusion`.
        Generation must skip R-01 and emit only R-02 + R-03 net-new.
        """
        arch = architectures["agentic_app_extended"]
        existing = [
            {
                "id": "AG-1",
                "category": "agentic",
                "component": "LLM Agent Orchestrator",
                "description": "Existing agent collusion finding from detection tier.",
                "agentic_pattern": "agent_collusion",
            },
        ]
        result = _run_synthesis(existing, canonical_rules, arch)

        patterns = {f["agentic_pattern"] for f in result["net_new"]}
        assert "agent_collusion" not in patterns
        assert "temporal_attack" in patterns
        assert "emergent_behavior" in patterns
        assert len(result["net_new"]) == 2

    def test_netnew_skipped_when_existing_content_overlap_80pct(
        self, canonical_rules, architectures
    ):
        """Per LOW-7 / LOW-T11-1: suppress when existing description has
        >=80% Jaccard token overlap with the rule's generation_template.

        Build an existing finding whose description is nearly
        token-identical to the R-01 generation_template. Label does
        NOT match (finding has `agentic_pattern: none`), so the
        label-based skip does not fire. Content overlap must suppress.
        """
        arch = architectures["agentic_app_extended"]
        r01 = next(r for r in canonical_rules if r["rule_id"] == "R-01")
        template = r01["generation_template"]

        existing = [
            {
                "id": "AG-99",
                "category": "agentic",
                "component": "LLM Agent Orchestrator",
                # Verbatim copy of the template — maximum overlap
                "description": template,
                "agentic_pattern": "none",
            },
        ]
        result = _run_synthesis(existing, canonical_rules, arch)

        patterns = {f["agentic_pattern"] for f in result["net_new"]}
        assert "agent_collusion" not in patterns
        # R-02 + R-03 still generate (their templates do not overlap)
        assert "temporal_attack" in patterns
        assert "emergent_behavior" in patterns

    def test_jaccard_overlap_self_identity(self):
        """Sanity: Jaccard self-overlap is 1.0 for identical strings."""
        s = "cascade of emergent behavior across peer agents"
        assert _jaccard_overlap(s, s) == pytest.approx(1.0)

    def test_jaccard_overlap_disjoint(self):
        """Sanity: Jaccard overlap of disjoint strings is 0.0."""
        assert _jaccard_overlap("alpha beta", "gamma delta") == 0.0

    def test_netnew_skipped_when_gate_false(
        self, canonical_rules, architectures
    ):
        """Generation is suppressed entirely when the gate predicate is FALSE."""
        arch = architectures["single_agent_with_fine_tuning"]
        result = _run_synthesis([], canonical_rules, arch)
        assert result["gate"]["result"] is False
        assert result["net_new"] == []
        assert result["has_agentic_patterns"] is False

    def test_netnew_not_emitted_for_non_generator_rules(
        self, canonical_rules, architectures
    ):
        """R-04, R-05, R-06 have generates_finding_when_no_match: false.

        Even without existing findings, these rules MUST NOT emit.
        Only R-01, R-02, R-03 may generate net-new findings.
        """
        arch = architectures["agentic_app_extended"]
        result = _run_synthesis([], canonical_rules, arch)
        patterns = {f["agentic_pattern"] for f in result["net_new"]}
        assert "trust_exploitation" not in patterns
        assert "communication_vulnerability" not in patterns
        assert "resource_competition" not in patterns


# =============================================================================
# Tests — Area 4: Determinism
# =============================================================================

class TestDeterminism:
    """Two runs on identical inputs produce byte-identical output (ADR-021)."""

    def test_gate_predicate_determinism(self, architectures):
        """Gate predicate returns byte-identical output across runs."""
        for name, arch in architectures.items():
            a = _evaluate_multi_agent_gate(arch)
            b = _evaluate_multi_agent_gate(arch)
            assert a == b, f"Non-deterministic gate for arch={name}"

    def test_full_synthesis_determinism(
        self, canonical_rules, architectures
    ):
        """Full synthesis produces byte-identical JSON across runs (ADR-021 / SC-005)."""
        arch = architectures["agentic_app_extended"]
        findings = [
            {
                "id": "AG-1",
                "category": "agentic",
                "component": "LLM Agent Orchestrator",
                "description": "Cascade of agent interactions amplifies failures.",
            },
            {
                "id": "S-2",
                "category": "spoofing",
                "component": "Specialist Agent",
                "description": "Identity impersonation attack across peer agents.",
            },
            {
                "id": "D-3",
                "category": "denial-of-service",
                "component": "Inter-Agent Channel",
                "description": "Resource monopolization by one peer agent starving others.",
            },
        ]
        run1 = _run_synthesis(copy.deepcopy(findings), canonical_rules, arch)
        run2 = _run_synthesis(copy.deepcopy(findings), canonical_rules, arch)

        # Normalize via JSON round-trip with sorted keys for byte comparison
        j1 = json.dumps(run1, sort_keys=True, default=str)
        j2 = json.dumps(run2, sort_keys=True, default=str)
        assert j1 == j2

    def test_classification_order_independent(
        self, canonical_rules, architectures
    ):
        """Classification output does not depend on finding list order.

        Shuffling the input list yields the same per-id pattern
        assignment (different finding order in output, same pattern on
        each finding).
        """
        arch = architectures["agentic_app_extended"]
        findings = [
            {
                "id": f"ID-{i}",
                "category": "agentic",
                "component": "LLM Agent Orchestrator",
                "description": "cascade interaction amplifier",
            }
            for i in range(5)
        ]
        forward = _classify_all_findings(findings, canonical_rules, arch, True)
        backward = _classify_all_findings(
            list(reversed(findings)), canonical_rules, arch, True
        )
        forward_map = {f["id"]: f["agentic_pattern"] for f in forward}
        backward_map = {f["id"]: f["agentic_pattern"] for f in backward}
        assert forward_map == backward_map


# =============================================================================
# Tests — Area 5: Backward compatibility (FR-017)
# =============================================================================

class TestBackwardCompatibility:
    """Pre-Feature-142 finding IR parses with default `agentic_pattern: none`."""

    def test_pre_f142_finding_defaults_to_none(
        self, canonical_rules, architectures
    ):
        """A finding missing the `agentic_pattern` field gets `none` after
        classification under a gate-FALSE architecture."""
        arch = architectures["web_app"]
        finding_no_pattern = {
            "id": "S-1",
            "category": "spoofing",
            "component": "Auth Service",
            "description": "Token forgery via weak signature.",
        }
        result = _run_synthesis([finding_no_pattern], canonical_rules, arch)
        assert result["classified"][0]["agentic_pattern"] == "none"

    def test_pre_f142_threats_md_parses_with_default_none(self):
        """Pre-F142 threats.md table lacks the Pattern column.

        The reference implementation defaults `agentic_pattern: none` on
        any finding that did not carry the field before entering
        Phase 3.6 (consistent with FR-017 / schema 1.4 additive default).
        """
        content = (FIXTURES_DIR / "threats_pre_f142.md").read_text()
        # Import inline to avoid triggering tachi_parsers sys.path at
        # module import time (kept consistent with test_attack_chains)
        from tachi_parsers import parse_threats_findings
        findings = parse_threats_findings(content)
        assert len(findings) == 3
        for f in findings:
            # Pre-F142 baselines should parse successfully; the current
            # parser does not yet emit the field (T005 pending), but the
            # reference synthesis path treats missing field as `none`.
            pattern = f.get("agentic_pattern", "none") or "none"
            assert pattern == "none"

    def test_post_f142_threats_md_parses_findings(self):
        """Post-F142 threats.md table parses all rows (including AGP-01).

        The Pattern column's presence does not break the Section 7
        row extractor, and the AGP-NN id is accepted as a regular id.
        """
        content = (FIXTURES_DIR / "threats_post_f142.md").read_text()
        from tachi_parsers import parse_threats_findings
        findings = parse_threats_findings(content)
        ids = {f["id"] for f in findings}
        assert "AGP-01" in ids
        assert len(findings) == 5

    def test_valid_agentic_patterns_count(self):
        """Schema 1.4 enum has exactly 8 values (6 canonical + none + multiple)."""
        assert len(VALID_AGENTIC_PATTERNS) == 8
        canonical = set(VALID_AGENTIC_PATTERNS) - {"none", "multiple"}
        assert canonical == {
            "agent_collusion",
            "emergent_behavior",
            "temporal_attack",
            "trust_exploitation",
            "communication_vulnerability",
            "resource_competition",
        }


# =============================================================================
# Tests — Area 6: Idempotence (PM LOW-2)
# =============================================================================

class TestIdempotence:
    """Running synthesis twice: zero net-new on run 2, zero existing modified."""

    def test_idempotence_no_new_patterns_on_second_run(
        self, canonical_rules, architectures
    ):
        """Run synthesis, feed output back in, run again.

        Second run must:
          (a) produce zero additional net-new findings (all generator
              patterns already labeled)
          (b) leave every existing finding's `agentic_pattern` unchanged
        """
        arch = architectures["agentic_app_extended"]
        run1 = _run_synthesis([], canonical_rules, arch)

        # Concatenate classified (empty) + net_new to simulate the
        # finding IR handed to a second synthesis pass
        merged = run1["classified"] + run1["net_new"]
        run2 = _run_synthesis(merged, canonical_rules, arch)

        # (a) zero additional net-new findings
        assert run2["net_new"] == []

        # (b) every existing finding's pattern is unchanged
        run1_by_id = {f["id"]: f["agentic_pattern"] for f in merged}
        run2_by_id = {f["id"]: f["agentic_pattern"] for f in run2["classified"]}
        assert run1_by_id == run2_by_id

    def test_idempotence_with_existing_findings(
        self, canonical_rules, architectures
    ):
        """Idempotence holds with a pre-populated finding set."""
        arch = architectures["agentic_app_extended"]
        existing = [
            {
                "id": "AG-1",
                "category": "agentic",
                "component": "LLM Agent Orchestrator",
                "description": "cascade peer-agent interaction amplifies errors",
            },
            {
                "id": "S-2",
                "category": "spoofing",
                "component": "Specialist Agent",
                "description": "Identity impersonation across peer agents.",
            },
        ]
        run1 = _run_synthesis(existing, canonical_rules, arch)
        merged = run1["classified"] + run1["net_new"]
        run2 = _run_synthesis(merged, canonical_rules, arch)

        assert run2["net_new"] == []

        run1_by_id = {f["id"]: f["agentic_pattern"] for f in merged}
        run2_by_id = {f["id"]: f["agentic_pattern"] for f in run2["classified"]}
        assert run1_by_id == run2_by_id

    def test_idempotence_under_gate_false(
        self, canonical_rules, architectures
    ):
        """Idempotence trivially holds under gate FALSE (all `none`)."""
        arch = architectures["web_app"]
        existing = [
            {
                "id": "S-1",
                "category": "spoofing",
                "component": "Auth Service",
                "description": "Token forgery via weak signature.",
            },
        ]
        run1 = _run_synthesis(existing, canonical_rules, arch)
        run2 = _run_synthesis(run1["classified"], canonical_rules, arch)
        assert run1 == run2
        assert run2["net_new"] == []


# =============================================================================
# Tests — Reference-implementation integrity
# =============================================================================

class TestReferenceImplementationIntegrity:
    """Meta-checks on the reference implementation itself.

    These tests catch regressions in the test-tier reference algorithm
    before they mask engine-tier bugs.
    """

    def test_rules_table_has_all_canonical_rules(self, canonical_rules):
        """rules.yaml mirrors R-01 through R-06 exactly."""
        ids = {r["rule_id"] for r in canonical_rules}
        assert ids == {"R-01", "R-02", "R-03", "R-04", "R-05", "R-06"}

    def test_rules_table_priority_total_ordered(self, canonical_rules):
        """Canonical R-01..R-06 priorities are total-ordered (no ties).

        The shared reference notes: 'Total-ordered priority (no two
        rules currently share a priority value) — no `multiple`
        assignments are emitted by the initial rule set R-01 through
        R-06.'
        """
        priorities = sorted(r["priority"] for r in canonical_rules)
        assert priorities == sorted(set(priorities))
        assert len(priorities) == 6

    def test_generator_rules_have_templates(self, canonical_rules):
        """Every `generates_finding_when_no_match: true` rule has a template."""
        for r in canonical_rules:
            if r.get("generates_finding_when_no_match"):
                assert r.get("generation_template"), (
                    f"Rule {r['rule_id']} is a generator but lacks a template"
                )

    def test_rule_patterns_subset_of_valid_enum(self, canonical_rules):
        """Rule patterns are a subset of the finding-schema enum."""
        rule_patterns = {r["pattern"] for r in canonical_rules}
        valid = set(VALID_AGENTIC_PATTERNS)
        assert rule_patterns.issubset(valid)
        # Rules do not assign `none` / `multiple` directly — those are
        # outcomes of rule evaluation, not rule content.
        assert "none" not in rule_patterns
        assert "multiple" not in rule_patterns
