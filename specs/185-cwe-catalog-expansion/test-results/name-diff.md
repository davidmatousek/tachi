# Name Diff — R7 Name-Contamination Gate (T016)

Feature 185 (CWE Catalog Expansion) — Wave 2 Track 2 evidence. Byte-equality comparison (UTF-8) of the `name` field for all 40 F-A1.2 restoration records in `schemas/taxonomy/cwe.yaml` against the verbatim `Name` attribute parsed FRESH from the pinned MITRE corpus by `scripts/name_diff.py` (independent of harvest-40.md).

Run date: 2026-06-11. Live catalog: `schemas/taxonomy/cwe.yaml` (93 records total).

## Result

| Metric | Value |
|---|---|
| IDs checked | 40 / 40 |
| Mismatches | **0** |
| R7 gate | **PASS** |
| CWE-1039 sentinel | **CONFIRMED current v4.20 name** |

## XML Provenance

- XML path: `/tmp/cwec185/cwec_v4.20.xml` (18192305 bytes — matches pin)
- XML SHA-256 (computed): `1f5a78bd62e00f86436b4fe32d5034a57e8f0da88e4063b2072b664ae510912e`
- Zip SHA-256: `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50` — matches corpus-pin.md EXACTLY
- Chain of custody: on-disk XML is byte-identical to the member inside the SHA-verified zip (inner SHA-256 == on-disk SHA-256)
- Catalog root self-declares: Name='CWE' Version='4.20' Date='2026-04-30'
- Pinned zip SHA-256 (corpus-pin.md): `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`

## Sentinel — CWE-1039 (renamed by MITRE at v4.17)

- Current v4.20 corpus name (verbatim): `Inadequate Detection or Handling of Adversarial Input Perturbations in Automated Recognition Mechanism`
- Live cwe.yaml name (verbatim): `Inadequate Detection or Handling of Adversarial Input Perturbations in Automated Recognition Mechanism`
- Byte-equal: **YES**
- Stale pre-v4.17 name NOT present in yaml: **confirmed**
- MITRE Content_History rename evidence (`Previous_Entry_Name`, from the corpus itself):
  - Date=2025-04-03: `Automated Recognition Mechanism with Inadequate Detection or Handling of Adversarial Input Perturbations`

## Per-ID Table (all 40)

| CWE ID | XML kind | v4.20 Status | Byte-equal | Name (verbatim, yaml == xml unless flagged) |
|---|---|---|---|---|
| CWE-16 | Category | Obsolete | PASS | Configuration |
| CWE-73 | Weakness | Draft | PASS | External Control of File Name or Path |
| CWE-201 | Weakness | Draft | PASS | Insertion of Sensitive Information Into Sent Data |
| CWE-213 | Weakness | Draft | PASS | Exposure of Sensitive Information Due to Incompatible Policies |
| CWE-255 | Category | Draft | PASS | Credentials Management Errors |
| CWE-256 | Weakness | Incomplete | PASS | Plaintext Storage of a Password |
| CWE-259 | Weakness | Draft | PASS | Use of Hard-coded Password |
| CWE-260 | Weakness | Incomplete | PASS | Password in Configuration File |
| CWE-295 | Weakness | Draft | PASS | Improper Certificate Validation |
| CWE-307 | Weakness | Draft | PASS | Improper Restriction of Excessive Authentication Attempts |
| CWE-311 | Weakness | Draft | PASS | Missing Encryption of Sensitive Data |
| CWE-312 | Weakness | Draft | PASS | Cleartext Storage of Sensitive Information |
| CWE-319 | Weakness | Draft | PASS | Cleartext Transmission of Sensitive Information |
| CWE-326 | Weakness | Draft | PASS | Inadequate Encryption Strength |
| CWE-327 | Weakness | Draft | PASS | Use of a Broken or Risky Cryptographic Algorithm |
| CWE-359 | Weakness | Incomplete | PASS | Exposure of Private Personal Information to an Unauthorized Actor |
| CWE-489 | Weakness | Draft | PASS | Active Debug Code |
| CWE-520 | Weakness | Incomplete | PASS | .NET Misconfiguration: Use of Impersonation |
| CWE-521 | Weakness | Draft | PASS | Weak Password Requirements |
| CWE-540 | Weakness | Incomplete | PASS | Inclusion of Sensitive Information in Source Code |
| CWE-565 | Weakness | Incomplete | PASS | Reliance on Cookies without Validation and Integrity Checking |
| CWE-601 | Weakness | Draft | PASS | URL Redirection to Untrusted Site ('Open Redirect') |
| CWE-611 | Weakness | Draft | PASS | Improper Restriction of XML External Entity Reference |
| CWE-614 | Weakness | Draft | PASS | Sensitive Cookie in HTTPS Session Without 'Secure' Attribute |
| CWE-693 | Pillar | Draft | PASS | Protection Mechanism Failure |
| CWE-732 | Weakness | Draft | PASS | Incorrect Permission Assignment for Critical Resource |
| CWE-798 | Weakness | Draft | PASS | Use of Hard-coded Credentials |
| CWE-799 | Weakness | Incomplete | PASS | Improper Control of Interaction Frequency |
| CWE-829 | Weakness | Incomplete | PASS | Inclusion of Functionality from Untrusted Control Sphere |
| CWE-915 | Weakness | Incomplete | PASS | Improperly Controlled Modification of Dynamically-Determined Object Attributes |
| CWE-916 | Weakness | Incomplete | PASS | Use of Password Hash With Insufficient Computational Effort |
| CWE-937 | Category | Obsolete | PASS | OWASP Top Ten 2013 Category A9 - Using Components with Known Vulnerabilities |
| CWE-1035 | Category | Incomplete | PASS | OWASP Top Ten 2017 Category A9 - Using Components with Known Vulnerabilities |
| CWE-1039 | Weakness | Incomplete | PASS | Inadequate Detection or Handling of Adversarial Input Perturbations in Automated Recognition Mechanism |
| CWE-1104 | Weakness | Incomplete | PASS | Use of Unmaintained Third Party Components |
| CWE-1174 | Weakness | Draft | PASS | ASP.NET Misconfiguration: Improper Model Validation |
| CWE-1269 | Weakness | Incomplete | PASS | Product Released in Non-Release Configuration |
| CWE-1357 | Weakness | Incomplete | PASS | Reliance on Insufficiently Trustworthy Component |
| CWE-1426 | Weakness | Incomplete | PASS | Improper Validation of Generative AI Output |
| CWE-1427 | Weakness | Incomplete | PASS | Improper Neutralization of Input Used for LLM Prompting |

---
Generated by `specs/185-cwe-catalog-expansion/scripts/name_diff.py` (exit 0 = 0 mismatches). Regeneration-only — no production caller.
