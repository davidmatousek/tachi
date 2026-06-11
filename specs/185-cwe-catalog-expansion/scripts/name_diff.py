#!/usr/bin/python3
"""F-185 T016 — R7 name-contamination gate (name_diff.py).

Compares the `name` field of ALL 40 F-A1.2 restoration records inserted into
the live catalog (schemas/taxonomy/cwe.yaml) against the verbatim `Name`
attribute parsed FRESH from the pinned MITRE comprehensive dictionary
(cwec_v4.20.xml — see test-results/corpus-pin.md). This is an INDEPENDENT
path to the names: it does NOT read test-results/harvest-40.md or any other
intermediate harvest artifact, so a transcription error in the harvest chain
cannot self-confirm here.

Comparison semantics: BYTE equality of the UTF-8 encodings of the two decoded
strings (YAML scalar vs XML attribute value). No normalization, no case
folding, no whitespace stripping.

Sentinel case: CWE-1039 was renamed by MITRE at v4.17 (2025-04-03). The
script extracts the Content_History/Previous_Entry_Name evidence from the
corpus itself and additionally asserts the live YAML name is not the stale
pre-v4.17 name.

Provenance guards (structural, exit 2 on failure — BLOCKED class):
  - If the pinned zip sits next to the XML, its SHA-256 MUST equal the pin
    recorded in corpus-pin.md, and the zip's inner XML bytes MUST hash
    identically to the on-disk XML (full chain-of-custody).
  - The XML size must equal the pinned byte size.
  - The catalog root must self-declare Version="4.20".

Handles ALL THREE top-level element kinds: Weakness, Category, View (the 40
include 4 MITRE Categories and 1 Pillar).

Exit codes: 0 = 0 mismatches (R7 gate PASS); 1 = name mismatch(es), exact
(ID, yaml-name, xml-name) triplets printed and written to evidence;
2 = structural/provenance failure (missing file, SHA pin mismatch, wrong
corpus version, ID unresolvable).

Stdlib + pyyaml. No production caller — regeneration-only tier (D4).

Usage:
    /usr/bin/python3 name_diff.py [xml_path] [yaml_path] [out_path]

Defaults:
    xml_path  = /tmp/cwec185/cwec_v4.20.xml
    yaml_path = <repo>/schemas/taxonomy/cwe.yaml
    out_path  = <spec>/test-results/name-diff.md
"""

import hashlib
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import yaml

NS = "{http://cwe.mitre.org/cwe-7}"

SCRIPT = Path(__file__).resolve()
SPEC_DIR = SCRIPT.parents[1]   # specs/185-cwe-catalog-expansion
REPO_ROOT = SCRIPT.parents[3]  # repo root

DEFAULT_XML = Path("/tmp/cwec185/cwec_v4.20.xml")
DEFAULT_YAML = REPO_ROOT / "schemas" / "taxonomy" / "cwe.yaml"
DEFAULT_OUT = SPEC_DIR / "test-results" / "name-diff.md"

# Pin values from test-results/corpus-pin.md (T002). Zip SHA mismatch is a
# hard BLOCKED condition per spec edge case (F-180 R7 lesson).
PINNED_ZIP_SHA256 = "3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50"
PINNED_XML_SIZE = 18192305
EXPECTED_VERSION = "4.20"

# The 40 F-A1.2 restoration record IDs (T016 task text / cwe.yaml header).
INSERTED_IDS = [
    16, 73, 201, 213, 255, 256, 259, 260, 295, 307,
    311, 312, 319, 326, 327, 359, 489, 520, 521, 540,
    565, 601, 611, 614, 693, 732, 798, 799, 829, 915,
    916, 937, 1035, 1039, 1104, 1174, 1269, 1357, 1426, 1427,
]

SENTINEL_ID = 1039
# Stale pre-v4.17 name (also recorded by MITRE in Content_History/
# Previous_Entry_Name, which this script extracts as primary evidence).
SENTINEL_STALE_NAME = (
    "Automated Recognition Mechanism with Inadequate Detection or Handling "
    "of Adversarial Input Perturbations"
)


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def die(msg):
    print("BLOCKED/structural failure: %s" % msg, file=sys.stderr)
    sys.exit(2)


def verify_provenance(xml_path):
    """Return a list of provenance statements; die() on any hard failure."""
    notes = []
    if not xml_path.is_file():
        die("pinned XML not found at %s — re-download per corpus-pin.md and "
            "verify zip SHA-256 against the pin before re-running" % xml_path)

    xml_sha = sha256_of(xml_path)
    xml_size = xml_path.stat().st_size
    if xml_size != PINNED_XML_SIZE:
        die("XML size %d != pinned size %d (%s is not the pinned corpus)"
            % (xml_size, PINNED_XML_SIZE, xml_path))
    notes.append("XML path: `%s` (%d bytes — matches pin)" % (xml_path, xml_size))
    notes.append("XML SHA-256 (computed): `%s`" % xml_sha)

    zip_path = xml_path.parent / (xml_path.name + ".zip")
    if zip_path.is_file():
        zip_sha = sha256_of(zip_path)
        if zip_sha != PINNED_ZIP_SHA256:
            die("zip SHA-256 mismatch: computed %s != pinned %s"
                % (zip_sha, PINNED_ZIP_SHA256))
        notes.append("Zip SHA-256: `%s` — matches corpus-pin.md EXACTLY" % zip_sha)
        import zipfile
        with zipfile.ZipFile(zip_path) as zf:
            inner = hashlib.sha256()
            with zf.open(xml_path.name) as member:
                for block in iter(lambda: member.read(1 << 20), b""):
                    inner.update(block)
        if inner.hexdigest() != xml_sha:
            die("on-disk XML is NOT byte-identical to the XML inside the "
                "SHA-verified zip (inner %s vs disk %s)"
                % (inner.hexdigest(), xml_sha))
        notes.append("Chain of custody: on-disk XML is byte-identical to the "
                     "member inside the SHA-verified zip (inner SHA-256 == "
                     "on-disk SHA-256)")
    else:
        notes.append("Zip not present beside XML; relied on pinned XML byte "
                     "size + catalog Version self-declaration")
    return notes


def parse_xml_names(xml_path):
    """Fresh, independent harvest: id -> (kind, name, abstraction, status)."""
    root = ET.parse(str(xml_path)).getroot()
    version = root.get("Version")
    if version != EXPECTED_VERSION:
        die("catalog Version=%r, expected %r" % (version, EXPECTED_VERSION))
    catalog_attrs = (root.get("Name"), version, root.get("Date"))

    wanted = set(INSERTED_IDS)
    xml_map = {}
    for kind in ("Weakness", "Category", "View"):
        for el in root.iter(NS + kind):
            cid = int(el.get("ID"))
            if cid in wanted:
                if cid in xml_map:
                    die("CWE-%d appears as both %s and %s in the corpus"
                        % (cid, xml_map[cid][0], kind))
                xml_map[cid] = (kind, el.get("Name"),
                                el.get("Abstraction"), el.get("Status"))

    missing = wanted - set(xml_map)
    if missing:
        die("IDs unresolvable in corpus (no Weakness/Category/View element): %s"
            % ", ".join("CWE-%d" % i for i in sorted(missing)))

    # Sentinel rename evidence straight from MITRE Content_History.
    prev_names = []
    for el in root.iter(NS + "Weakness"):
        if el.get("ID") == str(SENTINEL_ID):
            for pen in el.iter(NS + "Previous_Entry_Name"):
                prev_names.append((pen.get("Date"), pen.text))
            break
    return catalog_attrs, xml_map, prev_names


def parse_yaml_names(yaml_path):
    if not yaml_path.is_file():
        die("live catalog not found: %s" % yaml_path)
    with open(yaml_path, "r", encoding="utf-8") as f:
        records = yaml.safe_load(f)
    if not isinstance(records, list):
        die("%s did not parse to a top-level list" % yaml_path)
    yaml_map = {}
    for rec in records:
        yaml_map[rec["id"]] = rec["name"]
    missing = [i for i in INSERTED_IDS if "CWE-%d" % i not in yaml_map]
    if missing:
        die("inserted IDs absent from cwe.yaml: %s"
            % ", ".join("CWE-%d" % i for i in missing))
    return len(records), yaml_map


def main(argv):
    xml_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_XML
    yaml_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_YAML
    out_path = Path(argv[3]) if len(argv) > 3 else DEFAULT_OUT

    provenance = verify_provenance(xml_path)
    catalog_attrs, xml_map, sentinel_prev = parse_xml_names(xml_path)
    total_records, yaml_map = parse_yaml_names(yaml_path)

    rows, mismatches = [], []
    for cid in sorted(INSERTED_IDS):
        kind, xml_name, abstraction, status = xml_map[cid]
        yaml_name = yaml_map["CWE-%d" % cid]
        equal = yaml_name.encode("utf-8") == xml_name.encode("utf-8")
        kind_label = "Pillar" if (kind == "Weakness" and abstraction == "Pillar") else kind
        rows.append((cid, kind_label, status, equal, xml_name))
        if not equal:
            mismatches.append(("CWE-%d" % cid, yaml_name, xml_name))

    sentinel_yaml = yaml_map["CWE-%d" % SENTINEL_ID]
    sentinel_xml = xml_map[SENTINEL_ID][1]
    sentinel_ok = (sentinel_yaml.encode("utf-8") == sentinel_xml.encode("utf-8")
                   and sentinel_yaml != SENTINEL_STALE_NAME)

    # --- evidence markdown ---
    lines = [
        "# Name Diff — R7 Name-Contamination Gate (T016)",
        "",
        "Feature 185 (CWE Catalog Expansion) — Wave 2 Track 2 evidence. "
        "Byte-equality comparison (UTF-8) of the `name` field for all 40 "
        "F-A1.2 restoration records in `schemas/taxonomy/cwe.yaml` against "
        "the verbatim `Name` attribute parsed FRESH from the pinned MITRE "
        "corpus by `scripts/name_diff.py` (independent of harvest-40.md).",
        "",
        "Run date: %s. Live catalog: `schemas/taxonomy/cwe.yaml` "
        "(%d records total)." % (date.today().isoformat(), total_records),
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| IDs checked | %d / 40 |" % len(rows),
        "| Mismatches | **%d** |" % len(mismatches),
        "| R7 gate | **%s** |" % ("PASS" if not mismatches else "FAIL"),
        "| CWE-1039 sentinel | **%s** |" % ("CONFIRMED current v4.20 name" if sentinel_ok else "FAILED"),
        "",
        "## XML Provenance",
        "",
    ]
    lines += ["- %s" % n for n in provenance]
    lines += [
        "- Catalog root self-declares: Name=%r Version=%r Date=%r" % catalog_attrs,
        "- Pinned zip SHA-256 (corpus-pin.md): `%s`" % PINNED_ZIP_SHA256,
        "",
        "## Sentinel — CWE-1039 (renamed by MITRE at v4.17)",
        "",
        "- Current v4.20 corpus name (verbatim): `%s`" % sentinel_xml,
        "- Live cwe.yaml name (verbatim): `%s`" % sentinel_yaml,
        "- Byte-equal: **%s**" % ("YES" if sentinel_yaml.encode("utf-8") == sentinel_xml.encode("utf-8") else "NO"),
        "- Stale pre-v4.17 name NOT present in yaml: **%s**"
        % ("confirmed" if sentinel_yaml != SENTINEL_STALE_NAME else "VIOLATED"),
    ]
    if sentinel_prev:
        lines.append("- MITRE Content_History rename evidence "
                     "(`Previous_Entry_Name`, from the corpus itself):")
        for d, n in sentinel_prev:
            lines.append("  - Date=%s: `%s`" % (d, n))
    if mismatches:
        lines += ["", "## MISMATCHES (exact triplets)", ""]
        for cid, yn, xn in mismatches:
            lines += ["- **%s**" % cid,
                      "  - yaml-name: `%s`" % yn,
                      "  - xml-name:  `%s`" % xn]
    lines += [
        "",
        "## Per-ID Table (all 40)",
        "",
        "| CWE ID | XML kind | v4.20 Status | Byte-equal | Name (verbatim, yaml == xml unless flagged) |",
        "|---|---|---|---|---|",
    ]
    for cid, kind_label, status, equal, xml_name in rows:
        lines.append("| CWE-%d | %s | %s | %s | %s |"
                     % (cid, kind_label, status,
                        "PASS" if equal else "**FAIL**",
                        xml_name.replace("|", "\\|")))
    lines += [
        "",
        "---",
        "Generated by `specs/185-cwe-catalog-expansion/scripts/name_diff.py` "
        "(exit 0 = 0 mismatches). Regeneration-only — no production caller.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")

    # --- console summary ---
    print("name_diff: checked %d/40 inserted IDs against %s"
          % (len(rows), xml_path))
    print("name_diff: mismatches = %d" % len(mismatches))
    print("name_diff: CWE-1039 sentinel = %s"
          % ("CONFIRMED" if sentinel_ok else "FAILED"))
    print("name_diff: evidence written to %s" % out_path)
    if mismatches:
        print("\nR7 GATE FAIL — exact (ID, yaml-name, xml-name) triplets:")
        for cid, yn, xn in mismatches:
            print("  %s\n    yaml: %r\n    xml:  %r" % (cid, yn, xn))
        return 1
    print("R7 GATE PASS — 0 mismatches")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
