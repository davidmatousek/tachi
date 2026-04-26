#!/usr/bin/env python3
"""
generate-threats-sarif.py

Parses a regenerated threats.md (Sections 3 STRIDE + 4 AG/LLM/OI/MI finding tables)
and emits SARIF 2.1.0 output with:
- 8 rules (STRIDE 6 + AI 2: agentic + llm)
- One result per finding
- Severity-mapped levels (error/warning/note)
- Properties including OWASP ref, agentic pattern, MAESTRO layer
- Special AG-8 properties: asi07_emission, feature, pattern_category

Usage:
    python3 scripts/generate-threats-sarif.py <threats.md> <output.sarif>
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


# ---------- Rule dictionary (8 rules) ----------
RULES = [
    {
        "id": "tachi/stride/spoofing",
        "shortDescription": {"text": "Identity spoofing threats"},
        "fullDescription": {
            "text": (
                "Threats where an attacker assumes the identity of another user, service, "
                "or component to gain unauthorized access or bypass authentication controls."
            )
        },
        "help": {
            "text": (
                "Review authentication mechanisms at all trust boundaries. Verify mTLS, "
                "signed tokens, and session binding controls."
            ),
            "markdown": (
                "Review authentication mechanisms at all trust boundaries.\n\n"
                "**References**: OWASP A07 (Identification and Authentication Failures), "
                "CWE-287 (Improper Authentication), OWASP LLM01:2025 (for LLM-specific identity bypass)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "spoofing", "authentication", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A07", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-287", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/stride/tampering",
        "shortDescription": {"text": "Data tampering threats"},
        "fullDescription": {
            "text": (
                "Threats where an attacker modifies data in transit, at rest, or in processing — "
                "including model context, training data, and inter-agent messages."
            )
        },
        "help": {
            "text": (
                "Review integrity controls on all data flows, stored data, and inter-process "
                "messages. Verify digital signatures, hash verification, and write-access controls."
            ),
            "markdown": (
                "Review integrity controls on all data flows.\n\n"
                "**References**: OWASP A08 (Software and Data Integrity Failures), "
                "CWE-345 (Insufficient Verification of Data Authenticity)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "tampering", "integrity", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A08", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-345", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/stride/repudiation",
        "shortDescription": {"text": "Repudiation threats"},
        "fullDescription": {
            "text": (
                "Threats where an attacker denies having performed an action, or where the "
                "system cannot prove that a specific action occurred — especially critical for "
                "AI agent decisions and clinical outputs."
            )
        },
        "help": {
            "text": (
                "Review audit logging completeness and tamper-evidence. Verify that all agent "
                "actions are logged with content hashes and service key signatures before execution."
            ),
            "markdown": (
                "Review audit logging completeness.\n\n"
                "**References**: OWASP A09 (Security Logging and Monitoring Failures), "
                "CWE-778 (Insufficient Logging)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "repudiation", "logging", "audit", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A09", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-778", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/stride/information-disclosure",
        "shortDescription": {"text": "Information disclosure threats"},
        "fullDescription": {
            "text": (
                "Threats where sensitive data — including system prompts, clinical records, "
                "model internals, or user data — is exposed to unauthorized parties."
            )
        },
        "help": {
            "text": (
                "Review access controls on all data stores and output paths. Verify output "
                "scrubbing, field-level log classification, and query result authorization."
            ),
            "markdown": (
                "Review access controls on data stores and outputs.\n\n"
                "**References**: OWASP A01 (Broken Access Control), CWE-200 (Exposure of Sensitive Information)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "information-disclosure", "data-exposure", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A01", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-200", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/stride/denial-of-service",
        "shortDescription": {"text": "Denial of service threats"},
        "fullDescription": {
            "text": (
                "Threats where system availability is degraded or denied — including resource "
                "exhaustion of LLM inference, inter-agent channel flooding, and knowledge base "
                "query storms."
            )
        },
        "help": {
            "text": (
                "Review rate limiting, resource quotas, circuit breakers, and backpressure "
                "mechanisms on all components."
            ),
            "markdown": (
                "Review rate limiting and resource controls.\n\n"
                "**References**: OWASP A05 (Security Misconfiguration), CWE-400 (Uncontrolled Resource Consumption)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "denial-of-service", "availability", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A05", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-400", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/stride/elevation-of-privilege",
        "shortDescription": {"text": "Privilege escalation threats"},
        "fullDescription": {
            "text": (
                "Threats where an attacker gains capabilities or access beyond their "
                "authorization — including prompt injection enabling agent self-authorization "
                "and compromised learning loop parameter control."
            )
        },
        "help": {
            "text": (
                "Review authorization enforcement at all components. Verify per-session scoped "
                "permissions, zero-trust tool authorization, and model update signing."
            ),
            "markdown": (
                "Review authorization enforcement.\n\n"
                "**References**: OWASP A01 (Broken Access Control), CWE-269 (Improper Privilege Management)"
            ),
        },
        "properties": {
            "tags": ["security", "stride", "elevation-of-privilege", "authorization", "owasp", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "A01", "toolComponent": {"name": "OWASP"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-269", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/ai/agentic",
        "shortDescription": {"text": "AI agent autonomy and misuse threats"},
        "fullDescription": {
            "text": (
                "Threats specific to AI agent frameworks — including unauthorized autonomous "
                "actions, tool call injection, agent collusion, insecure inter-agent "
                "communication (A2A), and temporal capability expansion via model updates."
            )
        },
        "help": {
            "text": (
                "Review agent scope enforcement, tool call validation, inter-agent rate limits, "
                "inter-agent channel authentication, and model update capability auditing."
            ),
            "markdown": (
                "Review agent scope enforcement and tool validation.\n\n"
                "**References**: OWASP Agentic Security Initiative (ASI-01, ASI-07), MCP Top 10 (MCP-03), "
                "MITRE ATLAS (AML.T0060), CWE-693 (Protection Mechanism Failure), CWE-287 (Improper Authentication)"
            ),
        },
        "properties": {
            "tags": ["security", "ai", "agentic", "autonomy", "tool-use", "a2a", "cwe"],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "CWE-693", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
            {"target": {"id": "CWE-287", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
    {
        "id": "tachi/ai/llm",
        "shortDescription": {"text": "LLM-specific threats"},
        "fullDescription": {
            "text": (
                "Threats specific to large language model integrations — including prompt "
                "injection (LLM01), data poisoning (LLM03), improper output handling (LLM05), "
                "model theft (LLM10), and misinformation (LLM09)."
            )
        },
        "help": {
            "text": (
                "Review prompt injection controls, training data provenance, output encoding for "
                "execution sinks, model extraction detection, and factual-output grounding for "
                "advisory systems."
            ),
            "markdown": (
                "Review LLM input/output controls.\n\n"
                "**References**: OWASP LLM Top 10 v2025 (LLM01, LLM03, LLM05, LLM09, LLM10), "
                "CWE-74 (Improper Neutralization of Special Elements)"
            ),
        },
        "properties": {
            "tags": [
                "security", "ai", "llm", "prompt-injection", "data-poisoning",
                "output-integrity", "misinformation", "cwe",
            ],
            "security-severity": "9.0",
        },
        "relationships": [
            {"target": {"id": "CWE-74", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]},
        ],
    },
]


PREFIX_TO_RULE = {
    "S": "tachi/stride/spoofing",
    "T": "tachi/stride/tampering",
    "R": "tachi/stride/repudiation",
    "I": "tachi/stride/information-disclosure",
    "D": "tachi/stride/denial-of-service",
    "E": "tachi/stride/elevation-of-privilege",
    "AG": "tachi/ai/agentic",
    "AGP": "tachi/ai/agentic",
    "LLM": "tachi/ai/llm",
    "OI": "tachi/ai/llm",
    "MI": "tachi/ai/llm",
}


SEVERITY_TO_LEVEL = {
    "Critical": "error",
    "High": "error",
    "Medium": "warning",
    "Low": "note",
    "Note": "note",
}


# Component → trust zone mapping (derived from threats.md Trust Zones)
COMPONENT_ZONE = {
    "User": ("User Zone", "external-entity"),
    "Guardrails Service": ("Application Zone", "process"),
    "LLM Agent Orchestrator": ("Application Zone", "process"),
    "Specialist Agent": ("Application Zone", "process"),
    "Inter-Agent Communication Channel": ("Application Zone", "process"),
    "MCP Tool Server": ("Application Zone", "process"),
    "Knowledge Base": ("Application Zone", "data-store"),
    "Audit Logger": ("Application Zone", "data-store"),
    "Long-Running Learning Loop": ("Application Zone", "process"),
    "Clinical Advisory Sub-Agent": ("Application Zone", "process"),
    "External API": ("External Services", "external-entity"),
}


def parse_findings(md_path: Path) -> list[dict]:
    """
    Parses Section 3 (STRIDE) and Section 4 (AI: AG, LLM, OI, MI) finding tables.
    Returns a list of finding dicts with keys: id, prefix, status, component,
    maestro, agentic_pattern, threat, owasp_ref, likelihood, impact, risk_level, mitigation.
    """
    text = md_path.read_text(encoding="utf-8")

    # Restrict to Sections 3, 4, and 4a (skip Section 5+ which has summary tables)
    sec3_match = re.search(r"^## 3\. STRIDE Threat Tables\s*$", text, re.MULTILINE)
    sec5_match = re.search(r"^## 5\. ", text, re.MULTILINE)
    if not sec3_match or not sec5_match:
        raise RuntimeError("Could not locate Section 3 / Section 5 boundaries")

    findings_region = text[sec3_match.start():sec5_match.start()]

    # Match table rows with at least 9 pipe-separated columns starting with finding ID.
    # STRIDE rows: 10 cols (ID, Status, Component, MAESTRO, Pattern, Threat, Likelihood, Impact, Risk, Mitigation)
    # AI rows: 11 cols (adds OWASP Reference)
    finding_id_re = re.compile(
        r"^\| (?P<id>(?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI)-\d+|AGP-\d+) \| (?P<status>\[NEW\]|\[UNCHANGED\]|\[UPDATED\]|\[RESOLVED\]) \|",
        re.MULTILINE,
    )

    findings = []
    seen_ids = set()
    for match in finding_id_re.finditer(findings_region):
        line_start = match.start()
        line_end = findings_region.find("\n", line_start)
        if line_end < 0:
            line_end = len(findings_region)
        row = findings_region[line_start:line_end]
        cols = [c.strip() for c in row.split("|")]
        while cols and cols[0] == "":
            cols.pop(0)
        while cols and cols[-1] == "":
            cols.pop()

        if len(cols) < 10:
            continue

        fid = cols[0]
        if fid in seen_ids:
            # Skip duplicates (e.g. summary tables in Section 7) — though we limited region
            continue
        seen_ids.add(fid)

        # Extract prefix (everything before first hyphen-digit, but careful with AGP)
        m = re.match(r"^([A-Z]+)-\d+$", fid)
        if not m:
            continue
        prefix = m.group(1)

        # 10-col (STRIDE) layout: [ID, Status, Component, MAESTRO, Pattern, Threat, Likelihood, Impact, Risk, Mitigation]
        # 11-col (AI) layout:    [ID, Status, Component, MAESTRO, Pattern, Threat, OWASP, Likelihood, Impact, Risk, Mitigation]
        if len(cols) >= 11 and prefix in ("AG", "AGP", "LLM", "OI", "MI"):
            (
                _,
                status,
                component,
                maestro,
                pattern,
                threat,
                owasp_ref,
                likelihood,
                impact,
                risk_level,
                mitigation,
            ) = cols[:11]
        else:
            (
                _,
                status,
                component,
                maestro,
                pattern,
                threat,
                likelihood,
                impact,
                risk_level,
                mitigation,
            ) = cols[:10]
            owasp_ref = ""

        findings.append({
            "id": fid,
            "prefix": prefix,
            "status": status,
            "component": component,
            "maestro": maestro,
            "agentic_pattern": pattern if pattern not in ("—", "-", "") else None,
            "threat": threat,
            "owasp_ref": owasp_ref,
            "likelihood": likelihood,
            "impact": impact,
            "risk_level": risk_level,
            "mitigation": mitigation,
        })

    return findings


def normalize_owasp_id(owasp_ref: str, prefix: str) -> str:
    """
    Normalize OWASP / source IDs from finding rows.

    - "OWASP LLM01:2025" -> "LLM-01"
    - "ASI-01" / "ASI-07" -> as-is (already canonical)
    - "MCP-03" -> as-is
    - "" (STRIDE rows) -> derive from prefix mapping
    """
    if owasp_ref:
        s = owasp_ref.strip()
        # OWASP LLM##:YYYY  -> LLM-##
        m = re.match(r"^OWASP\s+LLM(\d+):\d+$", s)
        if m:
            return f"LLM-{int(m.group(1)):02d}"
        # ASI-## or ASI##
        m = re.match(r"^ASI[-]?(\d+)$", s)
        if m:
            return f"ASI-{int(m.group(1)):02d}"
        # MCP-## or MCP##
        m = re.match(r"^MCP[-]?(\d+)$", s)
        if m:
            return f"MCP-{int(m.group(1)):02d}"
        # Already canonical (e.g. "ASI-01" arrived literally)
        return s

    # Derive from STRIDE prefix
    stride_owasp = {
        "S": "A07",
        "T": "A08",
        "R": "A09",
        "I": "A01",
        "D": "A05",
        "E": "A01",
    }
    return stride_owasp.get(prefix, "")


def line_hash_for(fid: str) -> str:
    """
    Stable partialFingerprint compatible with the F-2 vintage:
    short MD5 hex of the finding ID (16 hex chars).
    """
    return hashlib.md5(fid.encode("utf-8")).hexdigest()[:16]


def build_result(finding: dict, run_id_baseline: str = "2026-04-19T03-20-30") -> dict:
    """Build one SARIF 2.1.0 result entry from a parsed threats.md finding row.

    Maps finding prefix → rule id, severity → SARIF level, and component →
    fully-qualified logical location. Emits per-finding properties: status,
    component, MAESTRO layer, normalized OWASP id, signal class, baseline-run
    correlation, and source attribution. AG-8 receives an `asi07_emission`
    marker per the F-219 enrichment contract.
    """
    rule_id = PREFIX_TO_RULE[finding["prefix"]]

    # Level mapping
    level = SEVERITY_TO_LEVEL.get(finding["risk_level"], "note")

    # Component → fully qualified location
    component = finding["component"]
    zone, kind = COMPONENT_ZONE.get(component, ("Application Zone", "process"))
    fq = f"{zone}/{component}"

    # OWASP / source ID normalization
    owasp_id = normalize_owasp_id(finding["owasp_ref"], finding["prefix"])

    # Tags
    tag_map = {
        "S": ["security", "stride", "spoofing"],
        "T": ["security", "stride", "tampering"],
        "R": ["security", "stride", "repudiation"],
        "I": ["security", "stride", "information-disclosure"],
        "D": ["security", "stride", "denial-of-service"],
        "E": ["security", "stride", "elevation-of-privilege"],
        "AG": ["security", "ai", "agentic"],
        "AGP": ["security", "ai", "agentic", "agentic-pattern"],
        "LLM": ["security", "ai", "llm"],
        "OI": ["security", "ai", "llm", "output-integrity"],
        "MI": ["security", "ai", "llm", "misinformation"],
    }
    tags = list(tag_map.get(finding["prefix"], ["security"]))

    # MAESTRO tagging
    maestro_token = finding["maestro"]
    if maestro_token and maestro_token != "—":
        # Compact form for the tag list
        m = re.match(r"^(L\d+)\s", maestro_token)
        layer_short = m.group(1) if m else "Unclassified"
        tags.append(f"maestro-layer:{layer_short}")

    if finding["agentic_pattern"]:
        tags.append(f"maestro-pattern:{finding['agentic_pattern']}")

    properties = {
        "baselineState": "new" if finding["status"] == "[NEW]" else "unchanged",
        "tags": tags,
        "maestro-layer": maestro_token if maestro_token else "Unclassified",
        "severity": finding["risk_level"],
        "likelihood": finding["likelihood"],
        "impact": finding["impact"],
    }
    if finding["agentic_pattern"]:
        properties["maestro-pattern"] = finding["agentic_pattern"]
    if owasp_id:
        properties["owasp_id"] = owasp_id

    # AG-8 special enrichment for F-3 ASI-07 emission
    if finding["id"] == "AG-8":
        properties["asi07_emission"] = True
        properties["feature"] = "219-asi07-tool-abuse-enrichment"
        properties["pattern_category"] = 9

    result = {
        "ruleId": rule_id,
        "message": {
            "text": finding["threat"],
            "markdown": finding["mitigation"],
        },
        "level": level,
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "examples/agentic-app/sample-report/threats.md"
                    },
                    "region": {"startLine": 1},
                },
                "logicalLocations": [
                    {
                        "name": component,
                        "fullyQualifiedName": fq,
                        "kind": kind,
                    }
                ],
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": line_hash_for(finding["id"]),
            "findingId/v1": finding["id"],
            "baselineRunId": "" if finding["status"] == "[NEW]" else run_id_baseline,
        },
        "properties": properties,
    }

    return result


def build_sarif(findings: list[dict]) -> dict:
    results = [build_result(f) for f in findings]

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Tachi",
                        "semanticVersion": "1.7",
                        "informationUri": "https://github.com/davidmatousek/tachi",
                        "supportedTaxonomies": [
                            {"name": "OWASP", "index": 0},
                            {"name": "CWE", "index": 1},
                        ],
                        "rules": RULES,
                    }
                },
                "taxonomies": [
                    {
                        "name": "OWASP",
                        "version": "2021",
                        "informationUri": "https://owasp.org/Top10/",
                        "organization": "OWASP Foundation",
                        "shortDescription": {"text": "OWASP Top 10 Web Application Security Risks"},
                    },
                    {
                        "name": "CWE",
                        "version": "4.13",
                        "informationUri": "https://cwe.mitre.org/",
                        "organization": "MITRE",
                        "shortDescription": {"text": "Common Weakness Enumeration"},
                    },
                ],
                "results": results,
            }
        ],
    }
    return sarif


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate threats.sarif from threats.md")
    parser.add_argument("input", type=Path, help="Path to threats.md")
    parser.add_argument("output", type=Path, help="Path to output threats.sarif")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 1

    findings = parse_findings(args.input)
    sarif = build_sarif(findings)

    args.output.write_text(json.dumps(sarif, indent=2) + "\n", encoding="utf-8")

    # Diagnostic: prefix counts
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["prefix"]] = counts.get(f["prefix"], 0) + 1
    print(f"OK: wrote {len(findings)} findings to {args.output}")
    print(f"Prefix counts: {sorted(counts.items())}")
    ag8 = [f for f in findings if f["id"] == "AG-8"]
    print(f"AG-8 present: {bool(ag8)} ({ag8[0]['status'] if ag8 else 'absent'})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
