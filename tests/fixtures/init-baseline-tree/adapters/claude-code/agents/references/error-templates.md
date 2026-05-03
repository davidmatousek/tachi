---
source_agent: orchestrator.md
loaded_at: Error condition encountered
extracted_from: Error Handling YAML templates (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE)
version: "1.0"
---

### UNSUPPORTED_FORMAT Error

**Trigger**: The `format` field is set to `auto` (or not specified), and heuristic detection fails to match any of the 5 supported format recognition patterns. This error is raised during Phase 1 format detection after all 5 priority-ordered pattern checks have been exhausted without a match.

**When to raise**: After testing ASCII (Priority 1), Free-text (Priority 2), Mermaid (Priority 3), PlantUML (Priority 4), and C4 (Priority 5) recognition patterns against the architecture input, and none match.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to component extraction or any subsequent phase.

```yaml
error:
  code: UNSUPPORTED_FORMAT
  message: "Input format not recognized."
  supported_formats:
    - ascii
    - free-text
    - mermaid
    - plantuml
    - c4
  guidance: >
    The architecture input did not match any supported format's recognition
    patterns during auto-detection. To resolve this:

    1. Set the 'format' field explicitly to one of the supported formats
       listed above, bypassing auto-detection.
    2. Or restructure the input to match one of the supported format
       recognition patterns:
       - ASCII: Use box-drawing characters (+--+, |, [...]) with arrow
         connectors (-->, <--, <-->).
       - Free-text: Describe components and relationships in natural
         language prose.
       - Mermaid: Use 'graph', 'flowchart', or 'sequenceDiagram' keywords
         with node and edge definitions.
       - PlantUML: Use @startuml/@enduml delimiters with component
         declarations.
       - C4: Use Person(...), System(...), Container(...), or Component(...)
         function calls with Rel(...) declarations.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for complete format examples
    and ../../../schemas/input.yaml for recognition pattern details.
```

This error is distinct from INVALID_FORMAT_VALUE. UNSUPPORTED_FORMAT applies when `format: auto` detection fails. INVALID_FORMAT_VALUE applies when the `format` field contains a value outside the allowed enum (see below).

---

### NO_COMPONENTS Error

**Trigger**: The architecture input is in a recognized format (format detection succeeded), but parsing finds fewer than 1 identifiable component or 0 data flows between components. This error is raised during the Phase 1 component inventory self-check after extraction and classification are complete.

**When to raise**: After format detection succeeds and component extraction completes, the self-check verifies minimum requirements. If the component inventory contains fewer than 1 component or 0 data flows, raise this error.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to Phase 2.

```yaml
error:
  code: NO_COMPONENTS
  message: "No architecture components or data flows detected in input."
  minimum_requirements:
    components: 1
    data_flows: 1
  guidance: >
    The input was recognized as a valid format, but it does not contain
    enough architectural structure for threat analysis. A valid architecture
    input must include:

    1. At least one identifiable component -- a service, database, user,
       agent, API, gateway, or any system element that can be classified
       as a DFD element type (External Entity, Process, Data Store, or
       Data Flow).
    2. At least one data flow or relationship -- a connection, API call,
       message, or data transfer between two components indicating how
       data moves through the system.

    Common causes of this error:
    - Input contains only a title or heading with no component descriptions.
    - Input describes a single component with no relationships to other
      components.
    - Input contains diagram syntax (e.g., Mermaid keywords) but no
      node or edge definitions.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for example inputs in each
    supported format that meet the minimum requirements.
```

---

### INVALID_FORMAT_VALUE Error

**Trigger**: The `format` field in the input is set to a value that is not one of the allowed enum values: `auto`, `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`. This error is raised at the start of Phase 1 format detection, before any parsing or heuristic detection begins.

**When to raise**: Before any format detection or parsing occurs, check the `format` field. If it is present and its value is not one of the 6 allowed values listed above, raise this error immediately.

**Response**: Return the following error response instead of a `threats.md` document. Do not proceed to any parsing or detection.

```yaml
error:
  code: INVALID_FORMAT_VALUE
  message: "The 'format' field contains an invalid value."
  provided: "<the-invalid-value-from-input>"
  allowed_values:
    - auto
    - ascii
    - free-text
    - mermaid
    - plantuml
    - c4
  guidance: >
    The 'format' field must be one of the allowed values listed above,
    or omitted entirely (which defaults to 'auto'). To resolve this:

    1. Set 'format' to one of the 6 allowed values.
    2. Use 'auto' (or omit the field) to enable heuristic format
       detection based on recognition patterns.
    3. Use an explicit format value ('ascii', 'free-text', 'mermaid',
       'plantuml', 'c4') to bypass auto-detection and parse the input
       directly with the specified format's parser.

    See ../../../docs/INTERFACE-CONTRACT.md Section 1 for the format field
    specification and supported values.
```

Replace `<the-invalid-value-from-input>` with the actual value provided in the input's `format` field so the user can see exactly what was rejected.

This error is distinct from UNSUPPORTED_FORMAT. INVALID_FORMAT_VALUE applies when the `format` field itself contains an invalid enum value. UNSUPPORTED_FORMAT applies when `format: auto` detection fails to match the input content against any recognition pattern.
