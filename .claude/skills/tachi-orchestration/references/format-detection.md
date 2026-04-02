---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# Format Detection Reference

Determine the architecture input format before parsing. The detected format drives which extraction rules are applied for components, data flows, and trust boundaries in Phase 1 (Scope).

## Detection Modes

There are two modes for format determination:

### Explicit Format Override

If the `format` field in the input is set to a value other than `auto`, use that format's parser directly. Skip heuristic detection entirely. Allowed values: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`.

If the value is not one of the allowed values, return an `INVALID_FORMAT_VALUE` error (see output schemas reference, Error Handling section).

### Heuristic Detection (format: auto)

When `format` is `auto` (or not specified), attempt to detect the format by testing recognition patterns in the following priority order. Use the **first** format whose patterns match. If no format matches, return an `UNSUPPORTED_FORMAT` error (see output schemas reference, Error Handling section).

---

## Priority Order and Recognition Patterns

### Priority 1: ASCII

Recognition patterns:
- Box-drawing characters: `+--+`, `|`, `[...]`
- Arrow indicators: `-->`, `<--`, `<-->`
- Component labels enclosed in brackets or boxes

**Heuristic rule**: If the input contains box-drawing characters forming visual structures with arrow connectors, classify as ASCII format.

### Priority 2: Free-text

Recognition patterns:
- No diagram syntax detected (no Mermaid keywords, no PlantUML delimiters, no C4 function calls, no box-drawing characters)
- Prose description of components and relationships
- Natural language narrative format

**Heuristic rule**: Free-text is the fallback for inputs that contain identifiable components and relationships described in natural language but do not match any diagramming syntax. If the input has no diagram syntax but does contain prose describing a system architecture, classify as free-text format.

### Priority 3: Mermaid

Recognition patterns:
- Keywords: `graph`, `flowchart`, `sequenceDiagram`
- Node definitions: `A[Label]`, `B((Label))`, `C{Label}`
- Edge definitions: `-->`, `--->`, `-.->`, `-->`

**Heuristic rule**: If the input contains Mermaid diagram keywords (`graph`, `flowchart`, or `sequenceDiagram`) along with node and edge definitions, classify as Mermaid format.

### Priority 4: PlantUML

Recognition patterns:
- Delimiters: `@startuml` / `@enduml`
- Component declarations: `[Component]`, `actor`, `database`
- Relationship arrows: `->`, `-->`, `.>`

**Heuristic rule**: If the input contains `@startuml` / `@enduml` delimiters with component declarations, classify as PlantUML format.

### Priority 5: C4

Recognition patterns:
- Keywords: `Person`, `System`, `Container`, `Component`
- C4 function syntax: `Person(...)`, `System(...)`, `Container(...)`, `ContainerDb(...)`
- Relationship declarations: `Rel(...)`

**Heuristic rule**: If the input contains C4 model function calls (`Person(...)`, `System(...)`, `Container(...)`, etc.) with relationship declarations, classify as C4 format.

---

## Format Detection Summary Table

| Priority | Format    | Primary Recognition Signals                   |
|----------|-----------|-----------------------------------------------|
| 1        | ASCII     | `+--+`, `\|`, `[...]`, `-->`                 |
| 2        | Free-text | No diagram syntax; prose description          |
| 3        | Mermaid   | `graph`, `flowchart`, `sequenceDiagram`       |
| 4        | PlantUML  | `@startuml` / `@enduml`                      |
| 5        | C4        | `Person`, `System`, `Container`, `Component`  |

---

## Output

Record the detected (or declared) format. This value is used for the `input_format` field in the output frontmatter and determines which format-specific extraction rules are applied for components, data flows, and trust boundaries.

---

## Priority Ordering Rationale

The priority order is designed to resolve ambiguity:

- **ASCII before Free-text**: ASCII diagrams contain characters that could appear in prose, but their structural patterns (box-drawing with arrows) are distinctive. Test ASCII first so that visual diagrams are not misclassified as free-text.
- **Free-text before Mermaid/PlantUML/C4**: Free-text is the absence of diagram syntax. By testing it at Priority 2, inputs that contain no diagram markers are caught before testing for specific diagram formats. This prevents false negatives where a prose input might coincidentally contain a word like "graph" in a non-Mermaid context.
- **Mermaid before PlantUML**: Both use arrow syntax (`-->`), but Mermaid's keywords (`graph`, `flowchart`) are more distinctive than PlantUML's delimiters. Testing Mermaid first ensures that Mermaid diagrams are not mismatched by PlantUML's broader arrow syntax.
- **C4 last**: C4 function call syntax (`Person(...)`, `Container(...)`) is highly distinctive and unlikely to appear in other formats. It is safe to test last.
