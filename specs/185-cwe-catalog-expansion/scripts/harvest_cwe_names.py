#!/usr/bin/python3
"""F-185 T004 — Harvest verbatim names/types/statuses for the 40 pinned CWE IDs.

Parses the pinned MITRE comprehensive dictionary (cwec_v4.20.xml, see
test-results/corpus-pin.md) and emits a 40-row markdown table to
test-results/harvest-40.md.

Handles ALL THREE top-level element kinds: Weakness, Category, View.
Names are reported VERBATIM from the XML `Name` attribute (XML entities
decoded by the parser; no paraphrase, no case changes) — guards the F-180 R7
name-contamination failure mode.

Type semantics:
  - Weakness with Abstraction="Pillar"  -> "Pillar"
  - Weakness with any other Abstraction -> "Weakness"
  - Category                            -> "Category"
  - View                                -> "View"

Status column reports the verbatim `Status` attribute (Status="Deprecated"
IS the deprecated flag in the CWE schema).

Stdlib only (xml.etree). No production caller — regeneration-only tier (D4).

Usage:
    /usr/bin/python3 harvest_cwe_names.py [xml_path] [out_path]
Exit codes: 0 = all 40 IDs found; 1 = one or more IDs MISSING or duplicated.
"""

import sys
import xml.etree.ElementTree as ET

NS = "{http://cwe.mitre.org/cwe-7}"

DEFAULT_XML = "/tmp/cwec185/cwec_v4.20.xml"
DEFAULT_OUT = (
    "/Users/david/Projects/tachi/specs/185-cwe-catalog-expansion/"
    "test-results/harvest-40.md"
)

# The 40 pinned IDs (spec FR-001), ascending.
PINNED_IDS = [
    16, 73, 201, 213, 255, 256, 259, 260, 295, 307,
    311, 312, 319, 326, 327, 359, 489, 520, 521, 540,
    565, 601, 611, 614, 693, 732, 798, 799, 829, 915,
    916, 937, 1035, 1039, 1104, 1174, 1269, 1357, 1426, 1427,
]

# Spec expectations to CHECK (report discrepancies, never force):
# CWE-16/255/937/1035 are Categories; CWE-693 is a Pillar.
EXPECTED_TYPES = {16: "Category", 255: "Category", 937: "Category",
                  1035: "Category", 693: "Pillar"}

# (container element, child element, type-resolver)
CONTAINERS = [
    ("Weaknesses", "Weakness",
     lambda e: "Pillar" if e.get("Abstraction") == "Pillar" else "Weakness"),
    ("Categories", "Category", lambda e: "Category"),
    ("Views", "View", lambda e: "View"),
]


def md_cell(text):
    """Escape only what would break a markdown table cell (pipe).

    CWE names contain no pipes as of v4.20; if one ever appears we escape it
    for rendering and warn, keeping the underlying string otherwise verbatim.
    """
    if "|" in text:
        sys.stderr.write("WARNING: pipe character in name %r — escaped for "
                         "markdown rendering only\n" % text)
        return text.replace("|", "\\|")
    return text


def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    tree = ET.parse(xml_path)
    root = tree.getroot()
    catalog_version = root.get("Version", "?")
    catalog_date = root.get("Date", "?")

    wanted = set(PINNED_IDS)
    records = {}      # id -> dict(name, type, status, kind)
    duplicates = []   # ids seen in more than one element

    for container_tag, child_tag, type_fn in CONTAINERS:
        container = root.find(NS + container_tag)
        if container is None:
            sys.stderr.write("WARNING: container <%s> not found\n"
                             % container_tag)
            continue
        for elem in container.findall(NS + child_tag):
            try:
                cid = int(elem.get("ID"))
            except (TypeError, ValueError):
                continue
            if cid not in wanted:
                continue
            if cid in records:
                duplicates.append(cid)
                continue
            records[cid] = {
                "name": elem.get("Name", ""),
                "type": type_fn(elem),
                "status": elem.get("Status", ""),
            }

    missing = [cid for cid in PINNED_IDS if cid not in records]
    deprecated = [cid for cid in PINNED_IDS
                  if cid in records
                  and records[cid]["status"] == "Deprecated"]
    type_counts = {}
    for cid in PINNED_IDS:
        if cid in records:
            t = records[cid]["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

    discrepancies = []
    for cid, expected in sorted(EXPECTED_TYPES.items()):
        actual = records[cid]["type"] if cid in records else "MISSING"
        if actual != expected:
            discrepancies.append((cid, expected, actual))

    lines = []
    lines.append("# Harvest — 40 Pinned CWE IDs (T004)")
    lines.append("")
    lines.append("Source: `%s` (catalog Version=%s, Date=%s — see "
                 "corpus-pin.md). Names are verbatim XML `Name` attribute "
                 "values; status is the verbatim `Status` attribute "
                 "(`Deprecated` = deprecated flag)."
                 % (xml_path, catalog_version, catalog_date))
    lines.append("")
    lines.append("| id | verbatim name | type | status |")
    lines.append("|---|---|---|---|")
    for cid in PINNED_IDS:
        if cid in records:
            r = records[cid]
            lines.append("| CWE-%d | %s | %s | %s |"
                         % (cid, md_cell(r["name"]), r["type"], r["status"]))
        else:
            lines.append("| CWE-%d | MISSING | MISSING | MISSING |" % cid)
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("- Rows emitted: %d (pinned: %d)"
                 % (len(PINNED_IDS), len(PINNED_IDS)))
    lines.append("- Found: %d; MISSING: %d%s"
                 % (len(records), len(missing),
                    (" (%s)" % ", ".join("CWE-%d" % c for c in missing))
                    if missing else ""))
    lines.append("- Type counts: %s"
                 % ", ".join("%s=%d" % (t, n)
                             for t, n in sorted(type_counts.items())))
    lines.append("- Deprecated-status records: %d%s"
                 % (len(deprecated),
                    (" (%s)" % ", ".join("CWE-%d" % c for c in deprecated))
                    if deprecated else ""))
    if duplicates:
        lines.append("- DUPLICATE IDs across element kinds: %s"
                     % ", ".join("CWE-%d" % c for c in sorted(set(duplicates))))
    lines.append("")
    lines.append("## Spec expectation check (report-only, XML is ground truth)")
    lines.append("")
    if discrepancies:
        for cid, expected, actual in discrepancies:
            lines.append("- DISCREPANCY: CWE-%d expected %s per spec, XML "
                         "says %s" % (cid, expected, actual))
    else:
        lines.append("- All spec expectations confirmed by the XML: "
                     "CWE-16/255/937/1035 are Categories; CWE-693 is a "
                     "Pillar.")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("Wrote %s" % out_path)
    print("rows=%d found=%d missing=%d deprecated=%d duplicates=%d "
          "discrepancies=%d"
          % (len(PINNED_IDS), len(records), len(missing), len(deprecated),
             len(set(duplicates)), len(discrepancies)))
    if missing:
        print("MISSING: %s" % ", ".join("CWE-%d" % c for c in missing))
    return 1 if (missing or duplicates) else 0


if __name__ == "__main__":
    sys.exit(main())
