# Corpus Pin — CWE Comprehensive Dictionary v4.20 (T002)

Feature 185 (CWE Catalog Expansion) — Wave 0 Lane A evidence. Pins the exact MITRE corpus used for the 40-record harvest (research.md Decision D1).

| Field | Value |
|---|---|
| Corpus | CWE comprehensive dictionary (XML) |
| Corpus version | 4.20 |
| MITRE release date | 2026-04-30 |
| Download URL | `https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip` |
| Retrieval date | 2026-06-11 |
| Zip SHA-256 | `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50` |
| Zip size (bytes) | 2,021,351 |
| Extracted XML | `cwec_v4.20.xml` (18,192,305 bytes) |
| Local extracted path | `/tmp/cwec185/cwec_v4.20.xml` |

## Verification

- Downloaded via `curl -fL --retry 3` directly from MITRE (no aggregator fallback — F-180 R7 lesson; spec edge case mandates BLOCKED over aggregator sources).
- SHA-256 computed with `shasum -a 256` over the zip as downloaded.
- XML root element self-declares `<Weakness_Catalog Name="CWE" Version="4.20" Date="2026-04-30">` — internal version and date match the pin.
- XML namespace: `http://cwe.mitre.org/cwe-7` (schema `cwe_schema_v7.3.xsd`).

## Notes for downstream tasks (T006/T016)

- The zip and extracted XML live in `/tmp/cwec185/` only — NEVER committed.
- If `/tmp/cwec185/cwec_v4.20.xml` is absent (e.g., after reboot), re-download from the pinned URL and verify the zip SHA-256 above matches before use.
