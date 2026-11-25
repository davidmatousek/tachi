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
  - **the driver's version fields and the taxa (ruled at W3, 2026-11-23, from the PM's W3 ruling 2c).** In the scorer and controls files, `semanticVersion` and `version` both carry tachi's release version, `tachi_parts.VERSION`, the provenance stamp's `version`; `version` is kept because the templates and both agents' mappings name it (NFR-1). `taxonomies` and `supportedTaxonomies` are `sarif_common`'s taxa table (W1's reading, below). `threats.sarif`'s driver follows its own template in PR 2;
  - no `automationDetails`;
  - no result carries `guid`, `correlationGuid`, `fingerprints` or SARIF's own `baselineState`;
  - **the rules (ruled at W3, 2026-11-23, from the PM's W3 ruling 2, gap A).** The scorer and controls files write one rule per category that has a result. Each has `id`, `shortDescription`, `fullDescription`, `properties` (`tags`, then `security-severity`) and `relationships`, in that order, as all four templates show them.
    - `relationships` holds one entry per taxonomy ID of the renderer's rule table, `sarif_common.RULES`, which both renderers share (`module-signatures.md`), in the table's order, in the templates' form: `{"target": {"id": "CWE-287", "toolComponent": {"name": "CWE"}}, "kinds": ["relevant"]}`. A `CWE-` ID names `CWE`, and an `A01` to `A10` ID names `OWASP`.
    - They are the IDs that ADR-050 D3's `ref` slot calls "its rule's relationships in the renderer's rule table". `risk-scorer.md:470` on `b040fa1` has the agent copy them, and the shipped files that carry them keep the field (NFR-1).
    - The targets name their taxonomy only, as in 1.0 (ADR-050, Known limitations).
- **`message.text`:** the file's own text. A correlated result's ends with one sentence that names its group, and its primary (on a peer) or its peers, up to 10 and then a count (on a primary), for example `Correlated in CG-3; primary S-1.` The message isn't identity, so a regroup changes it and never a key (ruling C, ADR-050 D8).
  - **The sentence's exact form (ruled at W1, 2026-11-22, T023).** It is appended to the file's own text after one space.
    - On a peer: `Correlated in CG-3; primary S-1.`
    - On a primary with at most 10 peers, every peer is named in group order, joined by `, `: `Correlated in CG-3; peers T-2, I-4.`
    - On a primary with more peers, the first 10 are named, then ` and N more` follows, where N counts the unnamed peers: `…, T-11, I-12 and 3 more.`
    - Only the file's members are named, so no RESOLVED ID appears.
  - **A finding with no threat text (recorded at W4, 2026-11-24, for PM W4 ruling R-E).** The file's own text is then the placeholder `No threat description.`, followed by ruling C's sentence where it applies (`module-signatures.md`, the placeholders).
- **The primary location (recorded at W4, 2026-11-24, from T066's groups U-5, U-7 and U-8).** None of these is identity (D7), so a change re-keys nothing.
  - `region` is the constant `{"startLine": 1}` (D7), as v4.48.4's own scorer and controls templates show it.
  - `logicalLocations[0].name` is the finding's component, or the placeholder `Unspecified` where it has none (`module-signatures.md`, the placeholders; recorded at W4 for PM W4 ruling R-E). Its `kind` is the component's Section 1 Type through D8's closed map: `External Entity` gives `external-entity`, `Process` gives `process` and `Data Store` gives `data`. Any other type, or none, gives `process`.
  - `fullyQualifiedName` is `<zone>/<component>`. `<zone>` is the zone of the Section 2 Trust Zones row that lists the component (by name, case-folded), as Section 2 writes it, a layer note such as `(L7)` included. With no such row, the scorer file uses the zone of the finding's reachability input, and the controls file under D8's fallback uses the zone part of the member's own `fullyQualifiedName`. Otherwise it is `Application Zone`. So both files write one location for a finding whose component Section 2 lists.
- **`relatedLocations`:** controls file only, code evidence, omitted when empty.
  - Each entry's `message.text` is `sarif_common.EVIDENCE_MESSAGE`, v4.48.4's own template text, filled with the control category's display name and the entry's `file` (recorded at W4, from T066's group U-11).
  - A resolved evidence `file` takes the resolver's canonical spelling, in `relatedLocations`, `control-evidence` and §3 alike.
  - An entry whose `file` the resolver refuses at render time is left out of `relatedLocations`, flagged `input:evidence.file:unresolved`. `control-evidence` keeps it with the `file` as written (`part-files.md`; ruled at W3, 2026-11-23).
- **Properties:**
  - the correlation keys appear on group members only;
  - `threats.sarif` adds `baseline-run-id`, moved from `partialFingerprints` with its value unchanged;
  - **`threats.sarif`'s other keys (ruled at W2′'s entry, S1P-A28)** are the ones its own contract names. That contract is `sarif-specification.md`'s text, which isn't about identity or membership, and the orchestrator's Phase 4 rules. Its keys are:
    - **`tags`:** the finding's category tags, then `maestro-layer:<ID>`, then, when the finding has a pattern other than `none`, `maestro-pattern:<value>`, `multiple` included.
      - The category tags are `security`, then `stride` or `ai`, then the category's own tag, as today's generator writes them. TE takes AG's tags plus `human-trust-exploitation`.
      - `<ID>` is the layer's ID, `L1` to `L7`, or `Unclassified`;
    - **`maestro-layer`:** the layer's full value from ADR-050 D2's chain, or `Unclassified`;
    - **`severity`:** Section 7's risk level, as D8's fallback reads it;
    - **`baselineState`:** `new`, `unchanged` or `updated`, from the finding's status. It is `new` on every result of a run with no baseline, and for a finding whose form gives no status. `absent` no longer occurs, because RESOLVED findings appear nowhere (D8). This key sits in `properties`: SARIF's own top-level `baselineState` stays forbidden;
    - **`affected_assets`:** always present, from the populator's block (ADR-046).

    No other key is written. The old generator's `likelihood`, `impact`, `owasp_id`, `maestro-pattern` property, and AG-8's `asi07_emission`, `feature` and `pattern_category` are named by no contract, so they are dropped (PM W3 ruling 2). PR 2's comparison of `threats.sarif` lists them, with their counts;
  - in the scorer and controls files, all other keys belong to the scoring and control contracts (D2, D9, D10), and no other key is written (PM W3 ruling 2: NFR-1 keeps the fields a contract names, and the oracle lists each uncontracted key a shipped file carried). Flags are sorted `kind:field:cause` arrays: `score-flags` in the scorer's file and `integrity-flags` in the controls file, both always present. Both carry `reused-id:finding_id:baseline` for the same finding (ruling B, D7);
  - **the controls file's `maestro-layer` (ruled at W3, 2026-11-23, from the PM's W3 ruling 2, gap B).** Every controls result carries it, as `control-analyzer.md:385` names it and four of the five shipped controls files carry it on every result.
    - **The value** is the finding's MAESTRO layer, the string the scorer file writes for that finding. The controls renderer derives it by the scorer's rule, ADR-050 D2's layer chain: the reference set's MAESTRO Layer cell, else the finding's own row in a per-finding table (§3 and §4), both through `tachi_parsers.parse_finding_layers`; else the finding's own layer; else its component's §1 layer; else `Unclassified`. The per-finding tables joined the chain at W4 (2026-11-24, from T066's group U-1), because the v4.48.x threat models hold the layer only there. It reads the `threats.md` that the validated `source_file` names, which it already reads (D7, D8).
    - **Without that file:** under D8's fallback, the member's `details.layer` (P0-3), else `Unclassified`. With no readable `threats.md`, it is `Unclassified`, under the stage record's reason for that file.
    - **Its place** is after `residual-risk`, as Phase 6c lists it. The 1.1 controls template (T060) fixes the full order and shows the key. §2's MAESTRO Layer cell is checked against it (`module-signatures.md`, the controls `matrix_row`);
  - no value names a RESOLVED finding.
    - **The self-check reads** `findingId/v1` and every property, except copied text: `message.text` and `message.markdown`, the scorer's `risk-owner`, and the controls file's `control-evidence`, `recommendation` and `relatedLocations` messages.
    - An ID in copied text, such as a snippet's `# mitigates T-3`, is a mention, not a reference (ADR-050 D8; ruled at W3, 2026-11-23, from T053, which settles P0-10).
- **Key order:** as shown, in two-space JSON (`risk-scorer.md:544`).
- **Readings ruled at W1 (2026-11-22, T023), from T015 and T016:**
  - **The rule map.**
    - The shared emitter's map is `sarif_common.RULE_ID_BY_PREFIX`: the long forms, all twelve prefixes with `TE`, derived from `tachi_scoring`'s one prefix resolver (D10). T010 drift-tests the shared reference against it.
    - `PREFIX_TO_RULE` stays unchanged for the two legacy generators, whose short forms reach no adopter output (ADR-046 D1), so their pinned bytes don't move. Its new `TE` entry equals `generate-risk-scores-sarif.py`'s existing default, so no output changes.
    - No new code imports it. T054 (W3) retires one user, and PR 2's rewrite of `generate-threats-sarif.py` on the shared emitter (lane R3b, W2′) deletes the map with its last user.
  - **The taxa names.** PR 1 keeps the names the scorer and controls files carry today: ASI01 "Agent Autonomy Abuse", and the short CWE-78, CWE-79 and CWE-89 names. A rename would be adopter-visible and is outside this bundle. Aligning ASI and CWE names with the catalogs, and extending the drift test from IDs to names, is a close-out follow-up (T080) that goes to the PM. The OWASP-LLM taxa stay equal to the 2026 catalog, value by value.
  - **JSON** is ASCII-only (`ensure_ascii=True`), and `findingId/v1` is written as Section 7 gives it.
  - **The message (from T027).** `message.text` is the reference set's threat text, as `risk-scorer.md:195` maps it today, with ruling C's sentence appended.
    - A file whose contract maps `message.markdown` keeps it, after `text`. NFR-1 keeps adopter fields, and the message isn't identity.
    - So `risk-scores.sarif` carries `markdown` = the reference set's mitigation text (`risk-scorer.md:196`), which today's shipped scorer files carry.
    - The controls file follows `control-analyzer.md` Phase 6c's own mapping by the same rule (lane D, W3).
    - Before W1's push, R0b lets `build_result` take an optional `markdown`, and the self-check accepts it. R1t's golden expects `{"text": threat, "markdown": mitigation}`.
    - **Always written (ruled at the P0 checkpoint, 2026-11-23, P0-8).** `risk-scores.sarif` writes `markdown` on every result, the empty string included. An empty mitigation gives `{"text": …, "markdown": ""}`, as two of the shipped `agentic-app` scorer results carry today, and the self-check passes. Under D8's SARIF fallback the value is the source result's `message.markdown`, or `""` when it holds none. A shipped scorer file whose results carry no `markdown` today, `predictive-ml-app`'s, gains the key, which is additive under NFR-1. The controls file follows the same rule (Phase 6c, lane D), with the same text (ruled at W3, 2026-11-23, lane D's T038 question): the finding's mitigation from the threat model that the plan read, else its scored input's `message.markdown` under D8's fallback, else `""`. All 86 of `agentic-app`'s controls results carry the `markdown` of its scorer results, and the four shipped controls files that carry none gain the key, which is additive.
- **Test vectors:**
  - `tachi-plh/1|tachi-risk-scorer|S-1` → `4395a0c67e904b90:1`
  - `tachi-plh/1|Tachi|S-1` → `6a1fd93f275ff00b:1`
  - `tachi-plh/1|tachi-control-analyzer|AGP-12` → `40b3517771dc3a11:1`
