"""Generate a 100-finding × 5-framework pagination smoke fixture.

Feature 194 / T038 (Wave 3.2 — US1 / Phase 5): produces a synthetic finding
list with 100 findings, each carrying source_attribution citations spread
across the 5 external framework taxonomies (owasp, mitre-attack, mitre-atlas,
nist-ai-rmf, cwe), with a mix of primary / related / derived relationships.

The generated fixture exercises the per-finding attribution table's
pagination behavior on portrait US Letter. Typst native row-break on
``table`` plus ``table.header(repeat: true)`` should paginate the long
table across multiple pages with the column header re-rendered on each.

The fixture is FIXED-SEED deterministic — a given invocation always
produces byte-identical output. This supports repeatable smoke-test runs
without introducing cross-run flakes.

Usage:

    # Write to stdout
    python tests/scripts/generate_pagination_fixture.py

    # Write to a YAML fixture file
    python tests/scripts/generate_pagination_fixture.py \
      --output tests/scripts/fixtures/coverage_attestation/pagination_smoke/findings.yaml

The output shape matches the other coverage_attestation fixtures:

    - id: <finding-id>
      component: <component>
      threat: <threat description>
      severity: high|critical|medium|low
      source_attribution:
        - {taxonomy: owasp, id: LLM05, relationship: primary}
        - ...

The fixture is consumed by tests/scripts/test_coverage_attestation_pagination.py
which invokes ``build_per_finding_rows`` + ``build_per_framework_aggregates``
on the loaded fixture, composes a report-data.typ that the Typst main
template can compile, and asserts the resulting PDF has enough pages for
the per-finding table to have paginated (i.e., more than 1 per-finding
table page).

All citations use IDs sourced from the F-A1 taxonomy catalogs (see
schemas/taxonomy/*.yaml) so the aggregator's classification logic produces
meaningful Covered / Partial / Gap classifications.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Taxonomy ID pools (sourced from schemas/taxonomy/*.yaml in F-A1).
# ---------------------------------------------------------------------------
# Small representative subsets of each framework catalog. The smoke test is
# about pagination, not classification coverage, so 5-10 IDs per framework
# is sufficient to produce a mix of Covered / Partial / Gap classifications
# on the aggregator output.

OWASP_IDS = [
    "LLM01", "LLM02", "LLM03", "LLM04", "LLM05",
    "LLM06", "LLM07", "LLM08", "LLM09", "LLM10",
    "A01", "A02", "A03", "A04", "A05",
]

MITRE_ATTACK_IDS = [
    "T1070.001", "T1078", "T1059", "T1082", "T1083",
    "T1021", "T1005", "T1110", "T1486", "T1566",
]

MITRE_ATLAS_IDS = [
    "AML.T0051", "AML.T0018", "AML.T0010", "AML.T0024", "AML.T0048",
]

# NIST IDs contain literal spaces; F-A2 parser regex uses \S+ and stops at
# whitespace (known limitation documented on multi_mixed_attribution.yaml).
# We still cite NIST IDs here because the coverage-attestation aggregator
# reads the raw YAML dicts directly (not through the parser regex) for the
# Typst data extraction path. The pagination smoke only cares about
# populated ref cells — not referential validity.
NIST_IDS = [
    "MAP 4.2", "MEASURE 2.7", "MEASURE 2.10", "MANAGE 1.3", "GOVERN 1.4",
]

CWE_IDS = [
    "CWE-200", "CWE-1333", "CWE-79", "CWE-287", "CWE-306",
    "CWE-352", "CWE-862", "CWE-89", "CWE-78", "CWE-611",
]

RELATIONSHIPS = ["primary", "related", "derived"]

SEVERITIES = ["critical", "high", "medium", "low"]

TAXONOMY_POOLS = [
    ("owasp", OWASP_IDS),
    ("mitre-attack", MITRE_ATTACK_IDS),
    ("mitre-atlas", MITRE_ATLAS_IDS),
    ("nist-ai-rmf", NIST_IDS),
    ("cwe", CWE_IDS),
]


def _yaml_escape(value: str) -> str:
    """Minimal YAML string escape — quote if the value contains characters
    that trip the plain-scalar parse.
    """
    if not value:
        return '""'
    needs_quote = any(c in value for c in [":", "#", "&", "*", "!", "|", ">", '"', "'", ",", "[", "]", "{", "}"])
    if needs_quote:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def generate_findings(count: int = 100, seed: int = 194) -> list[dict]:
    """Generate ``count`` synthetic findings with deterministic citations.

    Each finding gets 1-4 citations spread across random taxonomies with
    random relationships. The deterministic seed means two invocations
    with the same arguments produce byte-identical output.

    Args:
        count: number of findings to generate (default 100).
        seed: RNG seed for determinism (default 194).

    Returns:
        list of finding dicts matching the shape consumed by
        ``build_per_finding_rows`` and ``build_per_framework_aggregates``.
    """
    rng = random.Random(seed)
    findings = []

    for idx in range(count):
        # 4 finding-ID categories mimicking the tachi STRIDE prefixes:
        #   S-, T-, R-, I-, D-, E-, LLM-, AG-, AGP-
        prefixes = ["S", "T", "R", "I", "D", "E", "LLM", "AG"]
        prefix = rng.choice(prefixes)
        finding_id = f"{prefix}-{idx + 1:03d}"

        # Vary severities so the table exercises all 4 badge colors.
        severity = rng.choice(SEVERITIES)

        # Pick 1-4 citations across a random subset of the 5 taxonomies.
        # Mix primary / related / derived to exercise the bold / plain
        # weight differentiation in the Typst cell renderer.
        num_citations = rng.randint(1, 4)
        chosen_taxonomies = rng.sample(TAXONOMY_POOLS, k=min(num_citations, len(TAXONOMY_POOLS)))

        citations = []
        for taxonomy, id_pool in chosen_taxonomies:
            citation = {
                "taxonomy": taxonomy,
                "id": rng.choice(id_pool),
                "relationship": rng.choice(RELATIONSHIPS),
            }
            citations.append(citation)

        # Construct the finding record.
        # component / threat / mitigation are short representative strings
        # so the Title column exercises wrap behavior without being so long
        # it overwhelms the test output.
        finding = {
            "id": finding_id,
            "component": f"Component-{idx % 20 + 1}",
            "threat": f"Synthetic threat {idx + 1} for pagination smoke test",
            "likelihood": "\u2014",
            "impact": "\u2014",
            "risk_level": severity.capitalize(),
            "mitigation": f"Synthetic mitigation {idx + 1}",
            "agentic_pattern": "none",
            "source_attribution": citations,
        }
        findings.append(finding)

    return findings


def serialize_yaml(findings: list[dict]) -> str:
    """Serialize findings to YAML in the format expected by the fixture
    loaders (mimics the hand-authored fixture shape).
    """
    lines = [
        "# Pagination Smoke Fixture — 100 findings × 5 frameworks",
        "#",
        "# Feature 194 / T038 (Wave 3.2): synthetic fixture for exercising the",
        "# per-finding attribution table's pagination behavior. Generated",
        "# deterministically by tests/scripts/generate_pagination_fixture.py.",
        "#",
        "# Regenerate with: python tests/scripts/generate_pagination_fixture.py \\",
        "#   --output tests/scripts/fixtures/coverage_attestation/pagination_smoke/findings.yaml",
        "",
    ]

    for finding in findings:
        lines.append(f"- id: {_yaml_escape(finding['id'])}")
        lines.append(f"  component: {_yaml_escape(finding['component'])}")
        lines.append(f"  threat: {_yaml_escape(finding['threat'])}")
        lines.append(f"  likelihood: {_yaml_escape(finding['likelihood'])}")
        lines.append(f"  impact: {_yaml_escape(finding['impact'])}")
        lines.append(f"  risk_level: {_yaml_escape(finding['risk_level'])}")
        lines.append(f"  mitigation: {_yaml_escape(finding['mitigation'])}")
        lines.append(f"  agentic_pattern: {_yaml_escape(finding['agentic_pattern'])}")
        lines.append("  source_attribution:")
        for cit in finding["source_attribution"]:
            lines.append(
                f"    - {{taxonomy: {_yaml_escape(cit['taxonomy'])}, "
                f"id: {_yaml_escape(cit['id'])}, "
                f"relationship: {_yaml_escape(cit['relationship'])}}}"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of findings to generate (default 100).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=194,
        help="RNG seed for determinism (default 194).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output YAML file (default: write to stdout).",
    )
    args = parser.parse_args()

    findings = generate_findings(count=args.count, seed=args.seed)
    yaml_text = serialize_yaml(findings)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml_text)
        print(f"Wrote {len(findings)} findings to {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(yaml_text)


if __name__ == "__main__":
    main()
