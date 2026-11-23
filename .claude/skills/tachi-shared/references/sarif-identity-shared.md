---
type: shared-reference
name: sarif-identity-shared
version: 1.0.0
source_schema: schemas/finding.yaml
source_code: scripts/sarif_common.py
consumers:
  - risk-scorer
  - control-analyzer
---

# SARIF Identity and Membership — Shared Reference

Canonical rules for what makes a tachi SARIF result the same result from one run to the next (identity), and for which findings get a result at all (membership). One reference covers all three SARIF files, `threats.sarif`, `risk-scores.sarif` and `compensating-controls.sarif`, and replaces the four copies of this contract that older agent and reference files carried. The shared emitter in `scripts/sarif_common.py` implements it, and a drift test keeps the two in step.

GitHub Code Scanning matches an alert across uploads on four parts: the tool and upload category, the `ruleId`, `partialFingerprints.primaryLocationLineHash` and `artifactLocation.uri`. This reference pins all four for each file. Nothing else is identity: message, level, scores, logical locations and properties can change without re-keying an alert.

---

## For the Scorer and Controls Agents

- **You never write SARIF.** The renderer writes `risk-scores.sarif` and `compensating-controls.sarif` from your part files and the reference set. You also never hash, number, group or count results.
- **Your judgments can't move an alert.** They reach SARIF only as scores, levels and properties, which aren't identity. A regroup, a new primary, a re-score or an upgrade leaves every key alone.
- **State no SARIF count in prose.** The number of results is the number of open findings, which the renderer computes.

---

## Files, Tools and Categories

| File | Tool (`tool.driver.name`) | Upload `category` | Status |
|------|---------------------------|-------------------|--------|
| `threats.sarif` | `Tachi` | `threat-model` | dormant |
| `risk-scores.sarif` | `tachi-risk-scorer` | `risk-score` | live |
| `compensating-controls.sarif` | `tachi-control-analyzer` | `compensating-controls` | live |

- **Tool names are verbatim.** The threats tool is `Tachi` with a capital T, never `tachi`. Each name is a hash input, so a different spelling re-keys every alert in the file.
- **The three (tool, category) pairs differ.** Each category is the command's name.
- **No file carries `runs[].automationDetails`.** The upload step's `category` input governs, so tachi recommends a category in its upload snippets and never writes one into a file.
- **`dormant`** means the rules in this reference don't apply to that file yet (see `threats.sarif` below). **`live`** means the shared emitter applies them.
- **Re-key event.** Each file re-keys once, when the shared emitter first writes it: at the release that ships the emitter for the scorer and controls files, and at the release that ships its generator for `threats.sarif`. After that, a still-present finding keeps its alert.

---

## Rule IDs

The `ruleId` is a constant function of the finding's category, shared by all three files. A finding ID's prefix selects its category, and its category selects the rule.

| Prefix | `category` | `ruleId` |
|--------|------------|----------|
| S | spoofing | `tachi/stride/spoofing` |
| T | tampering | `tachi/stride/tampering` |
| R | repudiation | `tachi/stride/repudiation` |
| I | info-disclosure | `tachi/stride/information-disclosure` |
| D | denial-of-service | `tachi/stride/denial-of-service` |
| E | privilege-escalation | `tachi/stride/elevation-of-privilege` |
| AG | agentic | `tachi/ai/agentic-threats` |
| AGP | agentic | `tachi/ai/agentic-threats` |
| TE | agentic | `tachi/ai/agentic-threats` |
| LLM | llm | `tachi/ai/llm-threats` |
| OI | llm | `tachi/ai/llm-threats` |
| MI | llm | `tachi/ai/llm-threats` |

- **Eight rule IDs, twelve prefixes.** `AG`, `AGP` and `TE` map to `agentic`, and `LLM`, `OI` and `MI` map to `llm`.
- **No short forms.** The ruleIds `tachi/ai/agentic` and `tachi/ai/llm` are never emitted.
- **`level` isn't identity.** It keeps each file's own severity mapping (ADR-013 D3), and the emitter takes it from that file's contract.

---

## primaryLocationLineHash

Every result in every file carries tachi's own hash. It is computed from a stable per-finding key and never includes model prose. The recipe, over UTF-8:

```
sha256("tachi-plh/1|" + tool + "|" + id)  ->  first 16 lowercase hex digits  ->  then ":1"
```

- **`tool`** is the file's driver name from the table above.
- **`id`** is the canonical finding ID, `{PREFIX}-{N}` with leading zeros dropped, so `AGP-01` hashes as `AGP-1`. It must pass the finding-ID allow-list first: `(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}`, an ASCII full match.
- **Form.** `<16 hex>:1` is what GitHub's upload action writes for a line hash that occurs once, and `/1` versions the recipe.

Test vectors, which the emitter must reproduce byte for byte:

| Tool | Finding ID | `primaryLocationLineHash` |
|------|------------|---------------------------|
| `tachi-risk-scorer` | `S-1` | `4395a0c67e904b90:1` |
| `Tachi` | `S-1` | `6a1fd93f275ff00b:1` |
| `tachi-control-analyzer` | `AGP-12` | `40b3517771dc3a11:1` |

- **Stable.** Carry-forward preserves the finding ID, and the hash is a function of the tool and the ID alone. A regroup, a new primary, a re-score, an UPDATED finding's new component or an upgrade leaves it alone.
- **Unique.** No two present results in a file share a hash. If two do, the emitter fails the render and names both IDs. The tool term keeps the three files' hashes apart even if a server ignored the tool.
- **Always tachi's own.** The hash is on every result. It is never copied from an upstream file, and never left to the upload action, whose backfill hashes line 1 of the architecture file and collides.
- **ID reuse.** Because the hash depends only on the tool and the ID, a NEW finding given a resolved finding's ID would inherit that alert, dismissal included. The scorer renderer flags a NEW finding whose canonical ID is in any row of the baseline `risk-scores.md` as `reused-id:finding_id:baseline`, and scores it fresh, never from that row. The controls renderer carries the same flag into its file.

---

## artifactLocation.uri

The URI is the user's architecture file: repo-relative, in one canonical spelling, and identical on every result in a run chain. One shared resolver sets it, and no script takes a finished URI.

1. **Candidates, in order.** A candidate that fails a check below is skipped.
   1. The explicit path: the `--architecture-path` flag on the scorer and controls commands, which reaches the script as `--architecture PATH`.
   2. The architecture-source body line of the `threats.md` that was read.
   3. The constant `docs/security/architecture.md`.
2. **Checks** on a candidate:
   - it is non-empty, at most 4,096 bytes, and holds no control byte, backslash or backtick;
   - `.` and empty components are dropped, and `..` is refused;
   - an absolute path counts only if one of its ancestors is the working directory by `os.path.samefile`, and it is then made relative;
   - every component exists, none is a symlink (an `lstat` walk), and the last is a regular file.
3. **Spelling.** The path is rebuilt from the working directory down. Each component takes the name of the parent-directory entry with the same `(st_dev, st_ino)`. On a tie, the name as typed wins, then the lowest code point. So a case variant of the path gives the same URI. The result is percent-encoded per RFC 3986, except for unreserved characters and `/`.
4. **The body line's name check.** `{run}` is the directory of the `threats.md` that was read, and `{basename}` is the candidate's last component.
   - The snapshot `{run}/{basename}` must be a regular file that isn't a symlink.
   - Its basename must not be one of the canonical output names (`threats.md`, `threats.sarif`, `threat-report.md`, `attack-chains.md`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`), and by `samefile` the snapshot must not be the candidate itself. So a line can't name a tachi output or a per-run snapshot, and the default snapshot name, `architecture.md`, passes.
   - With no snapshot, the line fails closed: it is untrusted content with no anchor.
5. **Fallback.** An absent or failed candidate passes to the next, with a warning that names the candidate, the failed check and the flag. The stage record lists the warning. The constant is emitted in its canonical spelling if it validates, and otherwise literally. Nothing here stops a run.
6. **The body line** is ``**Architecture source**: `<canonical path>` ``.
   - It appears once, between the frontmatter and the first `## ` heading, outside code fences. Zero matches, or several, read as absent.
   - `/tachi.threat-model` writes it through the shipped upsert (`tachi-stage.py architecture-source`) from the command's own path, through the same resolver. If that fails, the upsert removes any existing line, so a line the orchestrator wrote can't survive.
   - The controls command reaches `threats.md` through `risk-scores.md`'s validated `source_file`.
7. **Controls evidence.** Each controls `evidence[].file` becomes a SARIF URI, so it passes the same checks relative to the target directory, and it must be relative: no scheme, leading `/`, backslash or drive letter.

---

## region and partialFingerprints

- **`region`** is the constant `{"startLine": 1}`, never a line derived from content. Architecture-level analysis has no line-level granularity.
- **`partialFingerprints`** holds exactly two keys, in this order: `primaryLocationLineHash` and `findingId/v1`. `findingId/v1` is the finding ID as Section 7 of `threats.md` writes it.
- **Why only two.** SARIF counts every partial fingerprint toward identity. A key that changes on a regroup or a re-assessment would re-key the alert, so `correlationGroup` moves to `properties` (below), and so does `threats.sarif`'s `baselineRunId`.
- **`findingId/v1` is a cross-reference to `threats.md`, not a key.** GitHub reads no key but the hash, so `findingId/v1` can't separate findings that share a rule and a component. Two such findings are two results with two hashes.

---

## Membership and the Counting Rule

**One top-level result per open finding, in every file.** Peers in a correlation group are results too.

| File | The member set |
|------|----------------|
| `threats.sarif` | The reference set's open findings: Section 7 of `threats.md`, statuses NEW, UPDATED and UNCHANGED, read through the shared wrapper, drift forms included |
| `risk-scores.sarif` | The same set |
| `compensating-controls.sarif` | The open rows of the input `risk-scores.md`, which is the same set |

- **The counting rule.** A file's findings are `runs[0].results[]`. N is the number of results, which equals the number of distinct `findingId/v1` values, which equals the size of the member set. Nothing else counts.
- **No `relatedLocations` entry names a finding, in any file.** The controls file's entries are code evidence only, each with a `physicalLocation` in the scanned code.
- **RESOLVED findings appear nowhere.** A finding in Section 4c, or a legacy result with `baselineState: absent`, is not a result, not a `relatedLocations` entry and not a property value.
- **One alert per open finding per file.** A correlation group changes properties, never membership or a key.

---

## Correlation Properties

Correlation is recorded on each member's own result, in `properties`. An uncorrelated result carries none of these three keys.

| Property | Value |
|----------|-------|
| `correlation-group` | the group ID, `CG-N` |
| `correlation-role` | `primary` or `peer` (the peer marker) |
| `correlation-primary` | the primary's finding ID |

- **Group membership** comes from Section 4a of `threats.md`, through the one shared parser, `tachi_parsers.parse_correlation_groups`. The generator, both renderers and the scorer's score inheritance all use it.
- **Order.** Groups keep Section 4a's order, and members keep their listed order, filtered to the file's member set.
- **The primary** is the first remaining member. A group left with fewer than two members emits nothing. An ID listed in two groups stays in the first.
- **Malformed rows.** A row whose group ID fails `CG-[0-9]{1,6}`, or whose members fail the finding-ID allow-list, is skipped and listed in the parse-error section. A missing or empty Section 4a means no groups.
- **The controls renderer** reads the `threats.md` that its input's validated `source_file` names. If that file can't be read, the file gets no correlation properties, the stage record says why, and no key changes.

**The message sentence.** Each correlated result's `message.text` ends with one sentence that names its group and either its primary (on a peer) or its peers (on a primary, up to a cap, then a count). The message isn't identity, so a regroup changes the text and never a key. The shared emitter appends the sentence, after one space, to the file's own message text.

| Role | Sentence |
|------|----------|
| peer | `Correlated in CG-3; primary S-1.` |
| primary, at most 10 peers | `Correlated in CG-3; peers T-2, I-4.` |
| primary, more than 10 peers | `Correlated in CG-3; peers T-2, I-4, S-5, R-6, D-7, E-8, AG-9, LLM-10, T-11, I-12 and 3 more.` |

- **The cap is 10 peers.** A primary names its first 10 peers in group order, joined by `, `. When it has more, ` and N more` follows, where N is the number of peers left unnamed.
- **Only the file's members are named,** so no RESOLVED ID appears. An uncorrelated result's message has no such sentence.

---

## The Result Shape

The shared emitter writes every result in this shape and key order, in two-space JSON:

```json
{
  "ruleId": "tachi/stride/tampering",
  "message": { "text": "<the file's own text>" },
  "level": "<the file's own mapping>",
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

- **The run.** `tool.driver.name` per the table above, and `tool.driver.informationUri` set to the real repository URL, never a placeholder. No `automationDetails`. `runs[0].properties.tachi_provenance` holds the renderer's stamp: `renderer`, `version` and `input_digest`.
- **No result carries** `guid`, `correlationGuid`, `fingerprints` or SARIF's own `baselineState`.
- **`relatedLocations`** appear in the controls file only, as code evidence, and are omitted when empty.
- **Properties.**
  - The correlation keys appear on group members only.
  - `threats.sarif` adds `baseline-run-id`, moved out of `partialFingerprints` with its value unchanged.
  - Every other key belongs to the scoring and controls contracts. Flags are sorted arrays of `kind:field:cause` strings: `score-flags` in the scorer's file and `integrity-flags` in the controls file, both always present. Both carry `reused-id:finding_id:baseline` for the same finding.
  - No value names a RESOLVED finding.

---

## Emitter Constants

| Constant | Value |
|----------|-------|
| Hash recipe tag | `tachi-plh/1` |
| Hash digest | SHA-256 over UTF-8, first 16 lowercase hex digits, then `:1` |
| `region` | `{"startLine": 1}` |
| `partialFingerprints` keys | `primaryLocationLineHash`, `findingId/v1` |
| `informationUri` | `https://github.com/davidmatousek/tachi` |
| Default architecture path | `docs/security/architecture.md` |
| Longest candidate path | 4,096 bytes |
| Correlation property keys | `correlation-group`, `correlation-role`, `correlation-primary` |
| Correlation roles | `primary`, `peer` |
| Peer cap | 10 |
| Peer sentence | `Correlated in {group}; primary {id}.` |
| Primary sentence | `Correlated in {group}; peers {ids}.`, or `Correlated in {group}; peers {ids} and {n} more.` over the cap |
| Controls evidence message | `Control evidence: {category} detected in {file}` |
| Flag properties | `score-flags` (scorer), `integrity-flags` (controls) |

---

## Self-Check Before Any Write

The emitter runs these checks on the finished result list, before any file is written. A failure fails the render.

- The result count equals the number of distinct finding IDs, which equals the member set.
- No two present results share a `primaryLocationLineHash`.
- No RESOLVED ID appears anywhere in the file.
- No `relatedLocations` entry names a finding.
- Every `correlation-primary` and every group member is a result, with one primary per group.
- Every correlated result's message ends with the sentence above, and an uncorrelated result's message has none.

Tests add the checks that need two runs: a regroup pair keeps every carried key, and an unchanged re-run keeps its keys and its bytes.

---

## Reading a SARIF Input

When the markdown input is absent, a stage reads membership from the SARIF instead: `threats.sarif` for the scorer, or `risk-scores.sarif` for controls.

- **The member set** is the SARIF's results, by `findingId/v1`, plus any legacy peer references in `relatedLocations`. A legacy reference is an allow-listed finding ID at the start of `message.text`, followed by `: `. Each one is grouped under its result.
- **Dropped:** results whose `baselineState` or `baseline-state` property is `absent`. Correlation properties supply groups where present.
- **An empty extraction is an error.** It stops the run before dispatch, and never passes as an empty member set.
- **Hashes are recomputed, never read.** A hash in an input SARIF is never used for matching.

---

## threats.sarif (dormant)

> **Dormant.** Nothing in this section applies to `threats.sarif` yet. Until the shipped generator takes over, the orchestrator keeps writing that file under `sarif-specification.md`, whose identity and membership text is unchanged. A model can't compute the hash, and identity rules applied before the generator ships would re-key its alerts twice.

When the generator ships, this section becomes live, and `threats.sarif` follows every rule above:

- the tool `Tachi` and the upload category `threat-model`;
- the shared rule map, hash, resolver, `region`, fingerprints, counting rule and correlation properties;
- one extra property, `baseline-run-id`, in baseline-aware runs, with its value unchanged from today's `baselineRunId`;
- a member set of Section 7's open findings;
- generation by `scripts/generate-threats-sarif.py` from the compiled `threats.md`, so no agent authors the file;
- finding IDs that are never reissued, so a NEW finding can't inherit a resolved finding's alert.

---

## What This Reference Replaces

It replaces the identity and membership text in these four copies, which each point here or are retired as their files change:

- `sarif-specification.md`, whose threats-file text stays in force while this reference's `threats.sarif` section is dormant;
- `risk-scorer.md` section 10;
- the installed `sarif-generation.md`;
- the control analyzer's Phase 6c.

It also corrects three older statements:

- **`sarif-specification.md`'s result-count check ("exactly N entries")** said N was the deduplicated finding count, while its correlation rules kept peers out of `results`, so the two disagreed. N is now the number of open findings, one result each, under the counting rule above.
- **`sarif-specification.md`'s fingerprint section and its fingerprint-preservation section contradict each other** about findings that share a rule and a component: one calls a shared hash intentional deduplication, and the other says `findingId/v1` tells the findings apart. This reference replaces both. Findings never share a hash, and `findingId/v1` is a cross-reference.
- **`risk-scorer.md` names the threats tool `"tachi"` in lowercase.** The name is `Tachi`.
