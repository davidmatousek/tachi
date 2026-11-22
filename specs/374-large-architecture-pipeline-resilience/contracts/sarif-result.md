# Contract: SARIF identity and membership

> Normative for F-374. ADR-050 decision D7 and D8 owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## The result shape written by the shared emitter (`scripts/sarif_common.py`)

```json
{
  "ruleId": "tachi/stride/tampering",
  "message": { "text": "<file contract>" },
  "level": "<file contract>",
  "locations": [{
    "physicalLocation": {
      "artifactLocation": { "uri": "docs/security/architecture.md" },
      "region": { "startLine": 1 }
    },
    "logicalLocations": [{ "name": "<component>", "fullyQualifiedName": "<zone>/<component>", "kind": "<dfd kind>" }]
  }],
  "relatedLocations": [{
    "id": 0,
    "message": { "text": "Control evidence: <category> detected in <file>" },
    "physicalLocation": { "artifactLocation": { "uri": "<evidence file>" }, "region": { "startLine": 42 } }
  }],
  "partialFingerprints": { "primaryLocationLineHash": "<16 lowercase hex>:1", "findingId/v1": "T-2" },
  "properties": { "correlation-group": "CG-1", "correlation-role": "peer", "correlation-primary": "S-1" }
}
```

- **The run:**
  - `tool.driver.name` per D7, with the real `informationUri` (FR-E.9);
  - no `automationDetails`;
  - no result carries `guid`, `correlationGuid`, `fingerprints` or SARIF's own `baselineState`.
- **`message.text`:** the file's own text. A correlated result's ends with one sentence that names its group, and its primary (on a peer) or its peers, up to 10 and then a count (on a primary), for example `Correlated in CG-3; primary S-1.` The message isn't identity, so a regroup changes it and never a key (ruling C, ADR-050 D8).
- **`relatedLocations`:** controls file only, code evidence, omitted when empty.
- **Properties:**
  - the correlation keys appear on group members only;
  - `threats.sarif` adds `baseline-run-id`, moved from `partialFingerprints` with its value unchanged;
  - all other keys belong to the scoring and control contracts (D2, D9, D10). Flags are sorted `kind:field:cause` arrays: `score-flags` in the scorer's file and `integrity-flags` in the controls file, both always present. Both carry `reused-id:finding_id:baseline` for the same finding (ruling B, D7);
  - no value names a RESOLVED finding.
- **Key order:** as shown, in two-space JSON (`risk-scorer.md:544`).
- **Test vectors:**
  - `tachi-plh/1|tachi-risk-scorer|S-1` → `4395a0c67e904b90:1`
  - `tachi-plh/1|Tachi|S-1` → `6a1fd93f275ff00b:1`
  - `tachi-plh/1|tachi-control-analyzer|AGP-12` → `40b3517771dc3a11:1`
