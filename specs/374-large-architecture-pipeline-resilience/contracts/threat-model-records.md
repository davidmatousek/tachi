# Contract: dispatch records, briefs, the ID map and chain files (PR 2)

> Normative for F-374. ADR-050 decision D11 to D14 owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## Record, brief and chain schemas (PR 2)

The JSON files are read by D3's strict loader. It enforces closed keys, a size cap, and rejects NaN, Infinity and duplicate keys. The tokens used below:
- `ID`: `tachi_parts`' finding pattern, `(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}`, an ASCII full match, compared in canonical form (ADR-050 D3).
- `DSP`: `tachi_parts`' dispatch pattern, `dsp-[0-9]{3,4}`, an ASCII full match.
- `NAME`: 1–200 characters, with no control bytes.
- `PATH`: absolute, under `{out}`, a regular file and not a symlink. Read takes absolute paths, so prompts and briefs carry them.
- `ROSTER`: one of the 14 typed threat-agent names.
- `CAT`: one of `S T R I D E AG LLM`.

Versions follow D15: every new JSON file names `schema: "tachi.<kind>/<major>"`. The merged tree manifest keeps its existing `schema_version "1.0"` key.

**Dispatch record**: `records/{DSP}.json`, at most 64 KiB.
```
schema "tachi.dispatch-record/1" | dispatch_id DSP (= file stem) | agent_type ROSTER
origin "planned"|"redispatch"|"coverage-gap" | scope {"components": [NAME] 1-500, unique, in inventory}
brief PATH = {out}/.tachi-build/briefs/{dispatch_id}.json | prompt = "Read and follow the brief at " + brief + "."
end_marker bool | status "complete"|"superseded" (complete => end_marker true)
supersedes DSP|null (non-null <=> origin "redispatch") | superseded_by [DSP] (non-empty <=> superseded)
reason "no_end_marker"|"overflow_error"|null (non-null <=> superseded)
count int 0-2000 | local_ids [ID|null], length = count
```
**Brief**: `briefs/{DSP}.json`, at most 32 KiB.
```
schema "tachi.brief/1" | dispatch_id DSP | agent_type ROSTER | targets [NAME] 1-500, unique
inputs {"architecture": PATH, "inventory": PATH, "dispatch_table": PATH}
baseline_focus null | [{"component": NAME, "covered": [CAT]}]
```
**ID map**: `idmap.json`, at most 256 KiB.
```
schema "tachi.idmap/1" | records {DSP: [DISP]}  keys = non-superseded records; length = count
DISP := ID | "=" ID | "~" ID | ">" ID    (kept | matched exactly | matched by similarity | merged into)
```
**Persisted Phase 1 tables**: `phase1/inventory.json` (at most 512 KiB) and `phase1/dispatch.json` (at most 256 KiB).
```
inventory: schema "tachi.phase1-inventory/1"
  components [{"name": NAME, "dfd_type": "External Entity"|"Process"|"Data Store"|"Data Flow",
               "maestro_layer": "L1".."L7"|"Unclassified", "description": str <= 500}] 1-500,
               names unique after casefold + whitespace collapse
  data_flows [{"source": NAME, "destination": NAME, "data": str <= 200, "protocol": str <= 100}] 0-5000
  trust_zones [{"name": NAME, "components": [NAME]}] 0-200     (every NAME is a component)
dispatch:  schema "tachi.phase1-dispatch/1"
  rows [{"component": NAME, "stride": [S|T|R|I|D|E], "ai": [AG|LLM]}]  one row per component, lists unique
```
**The outcome record** in `threats.md`. Exactly one line in the file matches `^\*\*Attack chain outcome\*\*: `.
```
## Attack Chain Outcome

**Attack chain outcome**: OUTCOME
OUTCOME := "chains written (" N "); candidates " C "; surfaced " S
         | "0 chains passed filter (" R "); candidates " C
         | "skipped (" R ")"
N := [1-9][0-9]{0,5}   C := [0-9]{1,6}, C >= N   S := [1-5], S <= N   R := [A-Za-z0-9 .,:=-]{1,80}
```
- **Reasons for 0 chains:** `no STRIDE findings`, `fewer than two layers with STRIDE findings`, `no candidate links`, `no chain with a Critical or High finding`.
- **Reasons the script gives for skipped:** `Section 7 unreadable`, `inventory missing`, `inventory invalid`.
- **Reasons the check gives for skipped:** `no outcome recorded`, `outcome record malformed`, `multiple outcome records`, `attack-chains.md missing`, `attack-chains.md unexpected`, `attack-chains.md unreadable`, `full chains X expected Y`, `compact rows X expected Y`, `remainder X expected Y`, `frontmatter counts differ`.

**The ID high-water mark** in `threats.md` (ruling B, ADR-050 D7). Exactly one line, between the frontmatter and the first `## ` heading and outside code fences, matches `^\*\*ID high-water mark\*\*: `. Zero or several read as absent.
```
**ID high-water mark**: `MARKS`
MARKS := ID (", " ID)*     one per prefix in use, in S-2 prefix order
```
Only `tachi-stage.py id-mark` writes it. The reissue check reads the baseline's line, never this run's.

**`attack-chains.md`** (S-3(g)):
```
frontmatter: schema_version (D15) | date (threats.md's) | chain_count N | surfaced_count S | candidate_count C
## 1. Chain Summary    S rows: today's columns + "Converging Chains"
## 2. Chain Details    S sections "### CHAIN-NNN: {title}" with today's keys,
                       "**Surfaced**: Yes" and "**Converging chains**: k"
## 3. Other Consolidated Chains
| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target |
|---|---|---|---|---|
| CHAIN-007 | L2 → L3 → L7 | T-4 → I-9 → S-2 | High | I-9 |      rows = min(100, N - S), rank order
**Consolidated chains not listed**: K                              last line; K = N - S - rows
```
**Merged tree manifest**: `attack-trees/.manifest.json`. Schema 1.0 is unchanged and its key set is closed.
```
schema_version "1.0" | rule_applied "Rule 1"|"Rule 2"|"no-baseline"|"no-op" (the plan's)
attack_tree_count int = len(trees) = tree files on disk
trees [{"finding_id": ID, "delta_status": "NEW"|"UNCHANGED"|"UPDATED",
        "action": "carried_forward"|"generated_fresh"|"regenerated",
        "similarity_score": number in [0,1] (Rule 3 entries only, otherwise omitted),
        "file_path": "attack-trees/{id-lowercase}-attack-tree.md"}]   Critical first, then High, each in S-2 order
summary {"fresh", "carried_forward", "regenerated"}: ints summing to attack_tree_count
```
A tree batch's part is its manifest: D3's envelope, with one item per finding, `{finding_id, delta_status, action, similarity_score}` (the last under Rule 3 only), where `delta_status` and `action` equal the batch input's. Each tree goes to the path the batch input's `tree_paths` names, and the merge adds `file_path` (ADR-050 D6).

**Chain files** (`chains/`, D13):
- `chains/chains.json`: `tachi.chains/1`. It holds every computed chain field (members in order, layers, roles, max severity, rank, ID, surfaced flag, converging count, chain-breaking target), the counts C, N and S, and the digests of both inputs. Only `attack-chains.py plan` writes it.
- `chains/narratives.json`: `tachi.chain-narratives/1`, written by the orchestrator. It maps each surfaced chain ID, and only those, to `{title, narrative}`. Both are narrative-class text (D3), with the slots D3's table gives chain narratives: `finding`, `ref`, `name` as `component:<ID>`, and `count` as `members`, `layers` or `converging`. No numerals outside slots; at most 120 characters for a title and 2,000 for a narrative. A failure takes D13's one rewrite, then its fixed text. `render` refuses unknown IDs and stale digests.
