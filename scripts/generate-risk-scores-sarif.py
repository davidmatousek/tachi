#!/usr/bin/env python3
"""Generate SARIF 2.1.0 risk-scores file from a regenerated risk-scores.md.

Reads:
  - risk-scores.md (Section 2 scored table; Section 3 dimensional breakdowns;
    Section 4 governance fields)
  - threats.md (component → trust zone, kind, source_attribution YAML, threat
    text per finding)

Writes:
  - risk-scores.sarif (SARIF 2.1.0 with one result per scored finding,
    properties carrying scoring dimensions, governance fields, and per-finding
    score-source provenance)

F-3 / Feature 219 ASI07 enrichment specifics:
  - AG-8 result emits properties.asi07_emission=true and
    properties.feature='219-asi07-tool-abuse-enrichment'.
"""
from __future__ import annotations

import functools
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sarif_common import (
    PREFIX_TO_RULE,
    build_sarif_envelope,
    level_for_band,
    parse_affected_assets,
    parse_component_metadata,
    prefix_for,
)
from tachi_parsers import parse_markdown_table

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = REPO_ROOT / "examples/agentic-app/sample-report"
RISK_MD = SAMPLE / "risk-scores.md"
THREATS_MD = SAMPLE / "threats.md"
OUT_SARIF = SAMPLE / "risk-scores.sarif"

SOURCE_THREATS_URI = (
    "examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md"
)


def parse_risk_md_section2(md: str) -> list[dict]:
    """Parse Section 2 'Scored Threat Table' rows into typed finding dicts."""
    rows = parse_markdown_table(md, "## 2. Scored Threat Table")
    out: list[dict] = []
    for r in rows:
        out.append(
            {
                "id": r["ID"].strip(),
                "component": r["Component"].strip(),
                "threat_summary": r["Threat"].strip(),
                "cvss_base": float(r["CVSS"]),
                "exploitability": float(r["Exploitability"]),
                "scalability": float(r["Scalability"]),
                "reachability": float(r["Reachability"]),
                "composite": float(r["Composite"]),
                "severity_band": r["Severity"].strip(),
                "sla_days": r["SLA"].strip(),
                "disposition": r["Disposition"].strip(),
            }
        )
    return out


SECTION3_HEADER = re.compile(r"^### (?P<id>[A-Z]+(?:-[A-Z]+)?-\d+):\s+(?P<text>.+)$")
MAESTRO_RE = re.compile(r"^\*\*MAESTRO Layer\*\*:\s+(?P<layer>.+)$")
COMPONENT_RE = re.compile(r"^\*\*Component\*\*:\s+(?P<component>.+)$")
CATEGORY_RE = re.compile(r"^\*\*Category\*\*:\s+(?P<category>.+)$")
CVSS_VECTOR_RE = re.compile(r"^\*\*CVSS Vector\*\*:\s+`(?P<vector>[^`]+)`")
CG_RE = re.compile(r"^\*\*Correlation Group\*\*:\s+Scores inherited from primary finding (?P<primary>[A-Z]+(?:-[A-Z]+)?-\d+)")
SCORE_SOURCE_RE = re.compile(r"^\*Score source:\s+(?P<source>[^*]+)\*")


def parse_risk_md_section3(md: str) -> dict[str, dict]:
    """Parse Section 3 'Dimensional Breakdown' for per-finding details."""
    in_section = False
    out: dict[str, dict] = {}
    cur: dict | None = None
    cur_id: str | None = None
    for line in md.splitlines():
        if line.startswith("## 3. Dimensional Breakdown"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            if cur and cur_id:
                out[cur_id] = cur
            break
        if not in_section:
            continue

        m = SECTION3_HEADER.match(line)
        if m:
            if cur and cur_id:
                out[cur_id] = cur
            cur_id = m.group("id")
            cur = {"threat_full": m.group("text").strip()}
            continue
        if cur is None:
            continue

        for rx, key in (
            (COMPONENT_RE, "component"),
            (CATEGORY_RE, "category"),
            (MAESTRO_RE, "maestro_layer"),
            (CVSS_VECTOR_RE, "cvss_vector"),
        ):
            mm = rx.match(line)
            if mm:
                if key == "cvss_vector":
                    cur[key] = mm.group("vector")
                else:
                    cur[key] = mm.group(key if key != "maestro_layer" else "layer")
                break
        else:
            mm = CG_RE.match(line)
            if mm:
                cur["correlation_primary"] = mm.group("primary")
                continue
            mm = SCORE_SOURCE_RE.match(line)
            if mm:
                cur["score_source_raw"] = mm.group("source").strip()
                continue
    if cur and cur_id and cur_id not in out:
        out[cur_id] = cur
    return out


def parse_risk_md_section4(md: str) -> dict[str, dict]:
    """Parse Section 4 'Governance Fields' rows into per-finding governance."""
    rows = parse_markdown_table(md, "## 4. Governance Fields")
    out: dict[str, dict] = {}
    for r in rows:
        fid = r.get("ID", "").strip()
        if not fid:
            continue
        out[fid] = {
            "owner": r.get("Owner", "").strip(),
            "sla_days": r.get("SLA", "").strip(),
            "disposition": r.get("Disposition", "").strip(),
            "review_date": r.get("Review Date", "").strip(),
        }
    return out


THREAT_ROW = re.compile(
    r"^\| (?P<id>[A-Z]+(?:-[A-Z]+)?-\d+) \| \[(?P<status>[A-Z]+)\] \| "
    r"(?P<component>[^|]+?) \|"
)


def parse_threats_status(md: str) -> dict[str, str]:
    """Map finding ID -> status flag ('NEW'/'UNCHANGED'/...)."""
    out: dict[str, str] = {}
    for line in md.splitlines():
        m = THREAT_ROW.match(line)
        if m and m.group("id") not in out:
            out[m.group("id")] = m.group("status")
    return out


def parse_threats_full_text(md: str) -> dict[str, tuple[str, str]]:
    """Map finding ID -> (threat_text, mitigation_text) from STRIDE+AI tables."""
    out: dict[str, tuple[str, str]] = {}
    pat = re.compile(
        r"^\| (?P<id>[A-Z]+(?:-[A-Z]+)?-\d+) \| \[[A-Z]+\] \| "
        r"[^|]+ \| [^|]+ \| [^|]+ \| (?P<threat>[^|]+?) \|"
        r"(?:[^|]+\|){0,4} (?P<mitigation>[^|]+?) \|\s*$"
    )
    for line in md.splitlines():
        m = pat.match(line)
        if not m or m.group("id") in out:
            continue
        out[m.group("id")] = (
            m.group("threat").strip(),
            m.group("mitigation").strip(),
        )
    return out


SOURCE_ATTR_BLOCK = re.compile(r"```yaml\n(?P<body>[\s\S]+?)```", re.MULTILINE)


def parse_source_attribution(md: str) -> dict[str, list[dict]]:
    """Extract per-finding source_attribution lists from inline YAML blocks.

    The threats.md flavor consumed by this generator emits source_attribution
    inside ad-hoc yaml fences (often after Section 4 AI tables, not the
    formally named "## 9. Source Attribution" block that
    `tachi_parsers._extract_source_attribution_block` requires). This function
    therefore scans every yaml fence rather than gating on Section 9.
    """
    out: dict[str, list[dict]] = {}
    for m in SOURCE_ATTR_BLOCK.finditer(md):
        body = m.group("body")
        if "source_attribution" not in body:
            continue
        cur_id: str | None = None
        cur_attrs: list[dict] = []
        cur_attr: dict = {}
        for raw in body.splitlines():
            line = raw.rstrip()
            if not line:
                continue
            if not line.startswith(" "):
                if cur_id and cur_attrs:
                    out[cur_id] = cur_attrs
                cur_id = line.split(":", 1)[0].strip()
                cur_attrs = []
                cur_attr = {}
                continue
            stripped = line.strip()
            if stripped.startswith("- taxonomy:"):
                if cur_attr:
                    cur_attrs.append(cur_attr)
                cur_attr = {"taxonomy": stripped.split(":", 1)[1].strip()}
            elif stripped.startswith("id:"):
                cur_attr["id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("relationship:"):
                cur_attr["relationship"] = stripped.split(":", 1)[1].strip()
        if cur_attr:
            cur_attrs.append(cur_attr)
        if cur_id and cur_attrs:
            out[cur_id] = cur_attrs
    return out


# Slot numbers are editorial per-edition human decisions (F-362 itself re-keyed
# them), so they stay literals; the edition year is derived from the catalog so
# it cannot drift when the next OWASP LLM Top 10 edition lands (FR-012a).
_OWASP_REFERENCE_SLOT_BY_PREFIX = {
    "OI": "LLM10",
    "MI": "LLM07",
}


def derive_owasp_reference(prefix: str) -> str | None:
    slot = _OWASP_REFERENCE_SLOT_BY_PREFIX.get(prefix)
    if slot is None:
        return None
    _, _, edition = _llm_catalog()
    return f"OWASP {slot}:{edition}"


_DFD_TYPE_TO_KIND = {
    "External Entity": "external-entity",
    "Process": "process",
    "Data Store": "data",
}


def build_logical_location(component: str, component_meta: dict[str, dict[str, str]]) -> dict:
    meta = component_meta.get(component, {"zone": "Application Zone", "dfd_type": "Process"})
    zone = meta["zone"]
    kind = _DFD_TYPE_TO_KIND.get(meta["dfd_type"], "process")
    return {
        "name": component,
        "fullyQualifiedName": f"{zone}/{component}",
        "kind": kind,
    }


COMPOSITE_WEIGHTS = "0.35/0.30/0.15/0.20"


def build_result(
    finding: dict,
    s3: dict,
    s4: dict,
    threats_status: dict[str, str],
    threats_full: dict[str, tuple[str, str]],
    source_attribution: dict[str, list[dict]],
    component_meta: dict[str, dict[str, str]],
    affected_assets_by_id: dict[str, list[str]],
) -> dict:
    """Build one SARIF 2.1.0 result entry from a scored finding plus correlated context.

    Merges Section 2 scoring (composite/CVSS/severity), Section 3 metadata
    (CVSS vector, MAESTRO layer, score-source provenance), Section 4 governance
    (owner/SLA/disposition/review-date), threats.md status + full threat text,
    F-A2 source_attribution, and component trust-zone/kind into one SARIF result.
    F-3 emits an `asi07_emission` marker on AG-8 per the F-219 enrichment contract.
    """
    fid = finding["id"]
    pref = prefix_for(fid)
    rule_id = PREFIX_TO_RULE.get(pref, "tachi/ai/agentic")
    level = level_for_band(finding["severity_band"])

    component = finding["component"]
    threat_text, mitigation_text = threats_full.get(
        fid, (finding.get("threat_summary", ""), "")
    )

    composite_str = f"{finding['composite']:.1f}"
    props: dict = {
        "security-severity": composite_str,
        "cvss_base": finding["cvss_base"],
        "exploitability": finding["exploitability"],
        "scalability": finding["scalability"],
        "reachability": finding["reachability"],
        "composite": finding["composite"],
        "composite-weights": COMPOSITE_WEIGHTS,
        "severity_band": finding["severity_band"],
        "cvss-base-score": f"{finding['cvss_base']:.1f}",
        "cvss-vector": s3.get("cvss_vector", ""),
        "maestro-layer": s3.get("maestro_layer", "Unclassified"),
        "governance.owner": s4.get("owner", "Unassigned"),
        "governance.sla_days": s4.get("sla_days", finding["sla_days"]),
        "governance.disposition": s4.get("disposition", finding["disposition"]),
        "review-date": s4.get("review_date", ""),
        "risk-owner": s4.get("owner", "Unassigned"),
        "remediation-sla": s4.get("sla_days", finding["sla_days"]),
        "risk-disposition": s4.get("disposition", finding["disposition"]),
    }

    # FR-004 verification tier: provenance property sourced verbatim from the
    # shared extractor (`sarif_common.parse_affected_assets`), keyed by the same
    # finding ID this result fingerprints. Snake_case key is byte-identical to
    # the threats-sarif emitter; default [] keeps it present on every result and
    # avoids colliding with the reserved SARIF `tags` key. Order is the
    # extractor's (already sorted by the populator — not re-sorted/deduped here).
    props["affected_assets"] = affected_assets_by_id.get(fid, [])

    score_source_raw = s3.get("score_source_raw", "")
    if "fresh" in score_source_raw:
        props["score-source"] = "fresh"
    elif "correlation primary" in score_source_raw:
        props["score-source"] = "inherited"
        props["score-source-detail"] = score_source_raw
    else:
        props["score-source"] = "inherited"

    if "correlation_primary" in s3:
        props["correlation-primary"] = s3["correlation_primary"]

    owasp_ref = derive_owasp_reference(pref)
    if owasp_ref:
        props["owasp-reference"] = owasp_ref

    if fid in source_attribution:
        props["source-attribution"] = source_attribution[fid]

    # F-3 / Feature 219 ASI07 enrichment marker
    if fid == "AG-8":
        props["asi07_emission"] = True
        props["feature"] = "219-asi07-tool-abuse-enrichment"
        props["new-finding"] = True

    if threats_status.get(fid) == "NEW":
        props.setdefault("new-finding", True)

    return {
        "ruleId": rule_id,
        "message": {
            "text": threat_text or finding.get("threat_summary", ""),
            "markdown": mitigation_text,
        },
        "level": level,
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": SOURCE_THREATS_URI},
                    "region": {"startLine": 1},
                },
                "logicalLocation": build_logical_location(component, component_meta),
            }
        ],
        "partialFingerprints": {"findingId/v1": fid},
        "properties": props,
    }


RULE_DEFS = [
    (
        "tachi/stride/spoofing",
        "Spoofing",
        "Identity spoofing threats targeting system components",
        "Threats where an attacker impersonates a legitimate user, service, or component to gain unauthorized access or inject malicious content.",
        ["security", "stride", "spoofing"],
        "8.2",
    ),
    (
        "tachi/stride/tampering",
        "Tampering",
        "Data or system tampering threats",
        "Threats where an attacker modifies data, configuration, or system behavior without authorization.",
        ["security", "stride", "tampering"],
        "7.1",
    ),
    (
        "tachi/stride/repudiation",
        "Repudiation",
        "Non-repudiation failure threats",
        "Threats where actors deny having performed actions due to insufficient audit trail controls.",
        ["security", "stride", "repudiation"],
        "6.2",
    ),
    (
        "tachi/stride/information-disclosure",
        "Information Disclosure",
        "Unauthorized data exposure threats",
        "Threats where sensitive data is exposed to unauthorized parties through system vulnerabilities.",
        ["security", "stride", "information-disclosure"],
        "7.2",
    ),
    (
        "tachi/stride/denial-of-service",
        "Denial of Service",
        "Service availability disruption threats",
        "Threats where an attacker degrades or eliminates system availability through resource exhaustion or flooding.",
        ["security", "stride", "denial-of-service"],
        "6.7",
    ),
    (
        "tachi/stride/elevation-of-privilege",
        "Elevation of Privilege",
        "Unauthorized privilege escalation threats",
        "Threats where an attacker gains elevated permissions or capabilities beyond their authorized scope.",
        ["security", "stride", "elevation-of-privilege"],
        "7.8",
    ),
    (
        "tachi/ai/agentic",
        "Agentic Threats",
        "AI agent autonomy and multi-agent coordination threats",
        "Threats specific to agentic AI systems including autonomous action abuse, agent collusion, tool call injection, and inter-agent communication vulnerabilities (OWASP ASI 2026 series).",
        ["security", "ai", "agentic"],
        "7.8",
    ),
    (
        "tachi/ai/llm",
        "LLM Threats",
        "Large language model specific threats",
        "Threats specific to LLM systems including prompt injection, data and model poisoning, improper output handling, and misinformation emission.",
        ["security", "ai", "llm", "owasp-llm"],
        "7.7",
    ),
]


def build_rules() -> list[dict]:
    return [
        {
            "id": rid,
            "name": name,
            "shortDescription": {"text": short},
            "fullDescription": {"text": full},
            "properties": {"tags": tags, "security-severity": sev},
        }
        for (rid, name, short, full, tags, sev) in RULE_DEFS
    ]


# --- OWASP-LLM taxa: derived from schemas/taxonomy/owasp.yaml (FR-012a) -------
# Reuses extract-report-data.py's own catalog loader (established repo pattern
# — see scripts/check-catalog-drift.py::_load_extract_module, which reuses the
# same loader in production, not just in tests) instead of hardcoding LLM
# category names/numbers/edition here. A future OWASP LLM Top 10 edition bump
# now only requires updating the catalog; this module cannot drift from it.
# Everything is loaded lazily on first taxonomy access (cached thereafter), so
# importing this module for its parsers alone execs no sibling module and
# reads no disk.
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract-report-data.py"


@functools.lru_cache(maxsize=None)
def _load_extract_module():
    """Import the hyphenated ``scripts/extract-report-data.py`` via importlib.

    Mirrors ``scripts/check-catalog-drift.py::_load_extract_module``: the
    module isn't importable by name (hyphen), so it's loaded from its file
    path. ``scripts/`` is already on ``sys.path`` (inserted at the top of this
    file), so the loaded module's own sibling imports (``tachi_parsers``)
    resolve without a second path insertion.
    """
    spec = importlib.util.spec_from_file_location(
        "extract_report_data", str(EXTRACT_SCRIPT)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=None)
def _llm_catalog() -> tuple[list[dict], str, str]:
    """Return ``(taxa, information_uri, edition)`` for the OWASP LLM Top 10.

    Derived once from the 10 ``LLM*`` records in schemas/taxonomy/owasp.yaml
    via ``extract_report_data._load_framework_yaml_records`` (the renderer's
    own catalog loader) rather than re-implementing the YAML walk. Catalog
    order is alphabetical per FR-032, so taxa arrive LLM01..LLM10 with no
    re-sort needed.

    - ``taxa``: bare catalog id + verbatim current-edition name per taxon — no
      hardcoded LLM category name literal anywhere in this module.
    - ``information_uri``: T005 set every LLM record's ``url`` to the single
      interim GenAI anchor per the feature's T003 URL-policy gate; read back
      here rather than re-authoring the URL as a second literal.
    - ``edition``: the year segment of ``full_id`` (``OWASP-LLM-2026-NN``),
      consumed by ``version`` fields and ``derive_owasp_reference`` so no
      edition literal is hand-maintained in this module.

    Fails loudly (never silently) if the catalog records ever disagree on url
    or edition — raised at first taxonomy access, where both real consumers
    (the CLI ``main()`` and the FR-012a contract tests) still hit it.
    """
    records = _load_extract_module()._load_framework_yaml_records("owasp")
    llm_records = [
        r for r in records if isinstance(r, dict) and r.get("id", "").startswith("LLM")
    ]
    taxa = [{"id": r["id"], "name": r["name"]} for r in llm_records]
    urls = {r["url"] for r in llm_records}
    if len(urls) != 1:
        raise RuntimeError(
            "OWASP LLM catalog records disagree on url "
            f"(schemas/taxonomy/owasp.yaml): {sorted(urls)}"
        )
    editions = {str(r["full_id"]).split("-")[2] for r in llm_records}
    if len(editions) != 1:
        raise RuntimeError(
            "OWASP LLM catalog records disagree on full_id edition "
            f"(schemas/taxonomy/owasp.yaml): {sorted(editions)}"
        )
    return taxa, urls.pop(), editions.pop()


@functools.lru_cache(maxsize=None)
def _taxonomies() -> list[dict]:
    """SARIF ``taxonomies`` payload; cached so every caller shares one object."""
    llm_taxa, llm_uri, llm_edition = _llm_catalog()
    return [
        {
            "name": "OWASP-LLM",
            "version": llm_edition,
            "guid": "b4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
            "informationUri": llm_uri,
            "taxa": llm_taxa,
        },
        {
            "name": "OWASP-ASI",
            "version": "2026",
            "guid": "c4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
            "informationUri": "https://owasp.org/",
            "taxa": [
                {"id": "ASI01", "name": "Agent Autonomy Abuse"},
                {"id": "ASI07", "name": "Insecure Inter-Agent Communication"},
            ],
        },
        {
            "name": "CWE",
            "version": "4.13",
            "guid": "a4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
            "informationUri": "https://cwe.mitre.org/",
            "taxa": [
                {"id": "CWE-78", "name": "OS Command Injection"},
                {"id": "CWE-79", "name": "Cross-site Scripting"},
                {"id": "CWE-89", "name": "SQL Injection"},
                {"id": "CWE-223", "name": "Omission of Security-relevant Information"},
                {"id": "CWE-287", "name": "Improper Authentication"},
                {"id": "CWE-345", "name": "Insufficient Verification of Data Authenticity"},
                {"id": "CWE-918", "name": "Server-Side Request Forgery (SSRF)"},
            ],
        },
    ]


def supported_taxonomies() -> list[dict]:
    # Derived from _taxonomies() (key order deliberately reproduces the
    # historical hand-written entries byte-for-byte in the emitted JSON), so
    # version/informationUri edits happen in exactly one place.
    return [
        {
            "name": t["name"],
            "index": i,
            "guid": t["guid"],
            "version": t["version"],
            "informationUri": t["informationUri"],
        }
        for i, t in enumerate(_taxonomies())
    ]


def __getattr__(name: str):
    # PEP 562: keep the historical module-attribute API (used by the FR-012a
    # contract tests and any external importer) working over the lazy accessors.
    if name == "TAXONOMIES":
        return _taxonomies()
    if name == "LLM_INFORMATION_URI":
        return _llm_catalog()[1]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> int:
    risk_md = RISK_MD.read_text(encoding="utf-8")
    threats_md = THREATS_MD.read_text(encoding="utf-8")

    findings = parse_risk_md_section2(risk_md)
    s3_map = parse_risk_md_section3(risk_md)
    s4_map = parse_risk_md_section4(risk_md)

    component_meta = parse_component_metadata(threats_md)
    threats_status = parse_threats_status(threats_md)
    threats_full = parse_threats_full_text(threats_md)
    source_attribution = parse_source_attribution(threats_md)
    affected_assets_by_id = parse_affected_assets(threats_md)

    if len(findings) < 80:
        print(
            f"FAIL: parsed only {len(findings)} findings from risk-scores.md Section 2",
            file=sys.stderr,
        )
        return 1

    results = []
    for f in findings:
        s3 = s3_map.get(f["id"], {})
        s4 = s4_map.get(f["id"], {})
        results.append(
            build_result(
                f,
                s3,
                s4,
                threats_status,
                threats_full,
                source_attribution,
                component_meta,
                affected_assets_by_id,
            )
        )

    driver = {
        "name": "tachi-risk-scorer",
        "version": "1.1",
        "semanticVersion": "1.1",
        "informationUri": "https://github.com/owner/tachi",
        "supportedTaxonomies": supported_taxonomies(),
        "rules": build_rules(),
    }
    sarif = build_sarif_envelope(driver, _taxonomies(), results)

    OUT_SARIF.write_text(
        json.dumps(sarif, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"OK: wrote {OUT_SARIF.relative_to(REPO_ROOT)} with {len(results)} results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
