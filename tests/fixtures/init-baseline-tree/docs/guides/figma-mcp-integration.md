# Figma MCP Integration Guide

**Purpose**: Connect Figma design files to AOD workflows via the Figma MCP server so AI coding agents can read design tokens, component specs, and layout rules directly from Figma.
**Audience**: Developers using AOD who receive designs in Figma and want agents to generate code that maps accurately to those designs.
**Read Time**: ~10 minutes

**Related**:
- [AOD Quickstart](AOD_QUICKSTART.md) -- Getting started with the AOD lifecycle
- [Stack Pack Consumer Guide (SwiftUI)](STACK_PACK_CONSUMER_TEST_SWIFTUI.md) -- Example stack-specific workflow

---

## 1. Overview

The Figma MCP (Model Context Protocol) server exposes Figma file data to AI coding agents over the standardized MCP interface. When connected, agents can read Figma layers, extract design tokens, inspect auto-layout properties, and reference component structures -- all without manual copy-paste from the Figma UI.

### What This Enables for AOD Workflows

- **Design token extraction**: Agents read colors, typography scales, spacing values, and border-radius tokens directly from Figma, producing code that matches the source design file.
- **Component spec reading**: Agents inspect named Figma components, their variants, and properties to generate corresponding code components with correct props and states.
- **Layout rule understanding**: Auto-layout settings (direction, gap, padding, alignment) translate to CSS flexbox or framework-specific layout code.
- **Reduced handoff friction**: No manual token export step. The agent queries the Figma file at generation time, so the code stays current with the latest design revision.
- **Design-to-code accuracy**: Color values, font sizes, and spacing are read as exact values rather than approximated by the agent from a screenshot or verbal description.

### How It Fits Into AOD

Figma MCP is a documentation-only integration. It requires no changes to AOD commands, rules, or agents. The MCP server runs alongside your development environment and provides design context to any agent that supports MCP tool use. It complements the `design-quality.md` rule (which tells agents what defaults to avoid) by giving agents access to what defaults to use instead -- the actual project design tokens from Figma.

---

## 2. Setup

Three methods are available. Choose the one that matches your workflow.

### Method A: Remote Server via npx (Recommended)

The simplest setup. Runs the Figma Developer MCP server as a local Node.js process that any MCP-compatible agent can connect to.

**Prerequisites**:
- Node.js 18+ installed
- A Figma Personal Access Token (generate at https://www.figma.com/developers/api#access-tokens)

**Steps**:

1. Generate a Figma API key:
   - Open Figma > Settings > Personal Access Tokens
   - Create a new token with read-only scope
   - Copy the token (it is shown only once)

2. Add the MCP server to your project configuration. Create or update `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["figma-developer-mcp", "--figma-api-key", "YOUR_FIGMA_API_KEY"]
    }
  }
}
```

3. Alternatively, set the key as an environment variable to avoid committing it to version control:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["figma-developer-mcp"],
      "env": {
        "FIGMA_API_KEY": "${FIGMA_API_KEY}"
      }
    }
  }
}
```

Then export the variable in your shell profile:

```bash
export FIGMA_API_KEY="your-token-here"
```

4. Start your AI agent. It detects the MCP server configuration and connects automatically. Verify by asking the agent to list available MCP tools -- you should see Figma-related tools such as `get_file`, `get_node`, and `get_styles`.

**Security note**: Never commit your Figma API key to version control. Use the environment variable approach (step 3) for any shared or public repository. Add `.mcp.json` to `.gitignore` if you use the inline key approach.

### Method B: Figma Desktop Connector

Figma's desktop application can expose MCP endpoints locally, allowing agents to connect without a separate Node.js process.

**Steps**:

1. Open Figma Desktop (ensure you are on the latest version)
2. Navigate to Preferences > Developer Settings
3. Enable "MCP Server" under the experimental features section
4. Note the local endpoint URL displayed (typically `http://localhost:3845`)
5. Configure your agent to connect to this endpoint as an MCP server

This method is useful when you want a single connection that automatically reflects whichever file you have open in Figma Desktop. The limitation is that it only exposes the currently active file.

### Method C: Figma Dev Mode Plugin

For teams already using Figma Dev Mode, the MCP integration is available as a native plugin within the Dev Mode inspection panel.

**Steps**:

1. Open your Figma file and switch to Dev Mode (toggle in the top toolbar)
2. In the Inspect panel, look for the MCP plugin section
3. Enable the plugin and copy the connection details
4. Configure your agent with the provided endpoint

This method works best for targeted inspection of specific frames and components rather than full-file extraction. It is the most interactive of the three options.

### Verifying the Connection

Regardless of which method you chose, verify the connection by asking your agent:

> "List the pages and top-level frames in this Figma file: [paste Figma file URL]"

A successful connection returns page names, frame names, and node IDs. If you see an error, refer to Section 7 (Troubleshooting).

---

## 3. Design-to-Code Workflow

This is the primary workflow: reading design data from Figma and generating code that matches.

### Step-by-Step

```
Figma File                    MCP Server                     AI Agent
    |                              |                              |
    |  1. Agent requests file  --->|                              |
    |                              |  2. Returns layer tree   --->|
    |                              |                              |  3. Agent selects
    |                              |                              |     target frame
    |  4. Agent requests node  --->|                              |
    |                              |  5. Returns properties   --->|
    |                              |                              |  6. Agent extracts
    |                              |                              |     tokens + layout
    |                              |                              |  7. Agent generates
    |                              |                              |     code
```

**Step 1 -- Connect and select file**: Provide the agent with your Figma file URL. The agent calls the MCP server to retrieve the file structure (pages, frames, components).

**Step 2 -- Select target frame**: Tell the agent which frame or component to implement. Use the frame name or paste the node URL from Figma (right-click a frame > Copy link). The agent requests that specific node's data.

**Step 3 -- Extract design tokens**: The agent reads properties from the node response:

| Figma Property | Extracted Token | Code Output |
|----------------|-----------------|-------------|
| Fill colors | Color palette values | CSS custom properties, Tailwind config |
| Text styles | Font family, size, weight, line-height | Typography scale |
| Auto-layout gap | Spacing values | Gap utilities, margin/padding |
| Auto-layout padding | Container padding | Padding values |
| Corner radius | Border-radius tokens | Rounded corners |
| Effects (shadows) | Shadow definitions | Box-shadow values |
| Stroke | Border definitions | Border width, color, style |

**Step 4 -- Understand layout**: Auto-layout properties map to code layout:

| Figma Auto-Layout | CSS/Flexbox Equivalent |
|--------------------|------------------------|
| Horizontal | `flex-direction: row` |
| Vertical | `flex-direction: column` |
| Space between | `justify-content: space-between` |
| Gap: 16 | `gap: 16px` (or `gap-4` in Tailwind) |
| Padding: 24 | `padding: 24px` (or `p-6` in Tailwind) |
| Hug contents | `width: fit-content` |
| Fill container | `width: 100%` / `flex: 1` |

**Step 5 -- Generate code**: The agent produces framework-appropriate code using the extracted values. When used alongside AOD's `design-quality.md` rule, the agent cross-references Figma tokens with the rule's banned-defaults list to ensure the output meets quality standards.

### Practical Example

Prompt to your agent:

> "Using the Figma file at [URL], implement the 'Hero Section' frame from the 'Homepage' page as a React component with Tailwind CSS. Extract all colors and spacing from the design."

The agent will:
1. Fetch the file structure via MCP
2. Locate the "Hero Section" node on the "Homepage" page
3. Read its fill colors, text styles, auto-layout settings, and child elements
4. Generate a React component with Tailwind classes that match the exact Figma values

---

## 4. Code-to-Canvas Workflow

The reverse direction: keeping Figma updated with what exists in the codebase. This uses Figma's **Code Connect** feature to link code components back to their Figma counterparts.

### Why This Matters

Without a code-to-canvas link, Figma and the codebase drift apart over time. Designers see one version in Figma while the code reflects another. Code Connect solves this by displaying the actual code implementation directly in Figma's Dev Mode inspect panel, so designers always see the current code for any component they inspect.

### How It Works

1. You define a mapping between a Figma component and its code implementation (see Section 5)
2. Code Connect publishes this mapping to Figma
3. When a designer inspects the component in Dev Mode, they see the actual code snippet alongside the design
4. Component prop mappings ensure that Figma variants correspond to the correct code props

### What Code Connect Does NOT Do

- It does not auto-generate code from Figma (that is the Design-to-Code workflow in Section 3)
- It does not modify your code based on Figma changes
- It does not sync visual changes -- it displays code alongside design for reference

Code Connect is a documentation bridge: it annotates Figma components with their code equivalents so the design-development loop stays informed.

---

## 5. Code Connect Configuration

Code Connect links Figma components to their codebase counterparts. This section covers practical setup.

### Installation

```bash
npm install --save-dev @figma/code-connect
```

### Defining a Connection

Create a Code Connect file alongside your component. For a React `Button` component:

```tsx
// src/components/Button.figma.tsx
import figma from "@figma/code-connect";
import { Button } from "./Button";

figma.connect(Button, "https://www.figma.com/design/FILE_KEY/FILE_NAME?node-id=NODE_ID", {
  props: {
    label: figma.string("Label"),
    variant: figma.enum("Variant", {
      Primary: "primary",
      Secondary: "secondary",
      Ghost: "ghost",
    }),
    disabled: figma.boolean("Disabled"),
    icon: figma.instance("Icon"),
  },
  example: (props) => (
    <Button variant={props.variant} disabled={props.disabled}>
      {props.icon}
      {props.label}
    </Button>
  ),
});
```

### How to Find the Figma Node URL

1. Open the Figma file containing your component
2. Select the component in the canvas
3. Right-click > "Copy link to selection"
4. The URL contains the `node-id` parameter needed for `figma.connect()`

### Prop Mapping Reference

| Figma Property Type | Code Connect Function | Description |
|---------------------|-----------------------|-------------|
| Text content | `figma.string("PropName")` | Maps a text layer to a string prop |
| Enum/Variant | `figma.enum("PropName", mapping)` | Maps variant properties to code values |
| Boolean toggle | `figma.boolean("PropName")` | Maps boolean properties |
| Nested instance | `figma.instance("PropName")` | Maps nested component instances |
| Children | `figma.children("LayerName")` | Maps child layers to React children |

### Publishing Connections

After defining your `.figma.tsx` files, publish them:

```bash
npx figma connect publish
```

This uploads the connection mappings to Figma. Designers inspecting the component in Dev Mode now see the `example` code snippet you defined, with prop values that update based on the selected variant.

### Project-Level Configuration

For projects with many components, create a `figma.config.json` in your project root:

```json
{
  "codeConnect": {
    "include": ["src/components/**/*.figma.tsx"],
    "importPaths": {
      "@/components/*": "src/components/*"
    }
  }
}
```

This tells Code Connect where to find connection files and how to resolve import paths displayed in Figma.

---

## 6. Limitations

### API Tier Restrictions

| Figma Plan | API Rate Limit | MCP Suitability |
|------------|---------------|-----------------|
| Free / Starter | ~6 tool calls per month | Evaluation only |
| Professional | Higher rate limits | Suitable for active development |
| Organization | Highest rate limits + admin controls | Recommended for teams |
| Enterprise | Custom limits + SSO + audit | Production team use |

**Recommendation**: Use Professional or higher for any project where agents will query Figma regularly. The free tier's approximately 6 monthly API tool calls are consumed quickly during iterative development -- a single design-to-code session can use multiple calls (file fetch, node fetch, style fetch).

### Known Constraints

- **Large files may timeout**: Figma files with hundreds of pages or thousands of components can exceed the MCP server's response timeout. Mitigate by querying specific nodes rather than fetching the full file tree.
- **Deeply nested instances can lose context**: Components nested more than 3-4 levels deep may not fully resolve their overridden properties through the API. Flatten critical nested structures in Figma or query inner components directly by node ID.
- **Design token changes require re-query**: The MCP server reads the file at request time. If a designer updates tokens in Figma, the agent does not automatically receive updates -- you must re-query the file or restart the workflow.
- **MCP server restart on structural changes**: If the Figma file structure changes significantly (pages renamed, top-level frames reorganized), restart the MCP server process to clear its internal cache.
- **No write access**: The MCP server provides read-only access to Figma files. Agents cannot modify Figma designs through the MCP connection. Use Code Connect (Section 5) for the reverse direction.
- **Image export limitations**: Raster images and complex vector illustrations in Figma are not directly extractable through the MCP API as usable image files. Export those manually or use Figma's REST API export endpoints separately.

---

## 7. Troubleshooting

### "API key not found" or "Invalid token"

**Cause**: The Figma API key is missing, expired, or incorrectly configured.

**Fix**:
1. Verify the environment variable is set: `echo $FIGMA_API_KEY`
2. If using `.mcp.json` with an inline key, confirm there are no extra spaces or quotes around the value
3. Generate a new token at https://www.figma.com/developers/api#access-tokens if the existing one has expired
4. Restart the MCP server after updating the key

### "File not accessible" or "403 Forbidden"

**Cause**: The API key's owner does not have access to the Figma file.

**Fix**:
1. Open the Figma file in your browser and confirm you can view it
2. Check sharing permissions -- the file must be at minimum "can view" for the account that generated the API token
3. For organization files, verify that the token has the correct scopes (file:read)
4. If the file is in a private project, the token owner must be a member of that project

### "Rate limit exceeded" or "429 Too Many Requests"

**Cause**: You have exceeded your Figma plan's API call quota.

**Fix**:
1. For free-tier users: wait for the monthly quota to reset, or upgrade to Professional
2. Reduce API calls by querying specific nodes (provide node IDs) rather than fetching the entire file tree
3. Cache results locally when iterating on the same component -- ask the agent to reuse previously fetched data rather than re-querying Figma
4. For teams: use an Organization or Enterprise plan for higher limits

### "Component not found" or empty node response

**Cause**: The component is not published to the Figma library, or the node ID is incorrect.

**Fix**:
1. In Figma, verify the component is published: right-click the component > "Go to main component" > ensure it shows as a library component
2. Confirm the node ID matches: select the component in Figma, copy its link, and extract the `node-id` parameter from the URL
3. If the component was recently created, publish the library update in Figma before querying via MCP

### Connection dropped or server unresponsive

**Cause**: The MCP server process has crashed or lost its connection.

**Fix**:
1. Check if the npx process is still running: `ps aux | grep figma-developer-mcp`
2. Restart the server: kill the existing process and re-run `npx figma-developer-mcp --figma-api-key=$FIGMA_API_KEY`
3. If using the Desktop Connector (Method B), restart Figma Desktop
4. Verify network connectivity -- the MCP server requires internet access to reach the Figma API

### Agent does not detect Figma MCP tools

**Cause**: The MCP configuration is not being read by the agent.

**Fix**:
1. Verify `.mcp.json` is in the project root (the directory where you start the agent)
2. Check the JSON syntax -- a trailing comma or missing quote breaks parsing
3. Restart the agent session after adding or modifying `.mcp.json`
4. Ask the agent to list its available MCP tools to confirm what it can see

---

## Summary

| Workflow | Direction | Tool | Section |
|----------|-----------|------|---------|
| Read design tokens | Figma --> Code | Figma MCP Server | Section 3 |
| Generate code from design | Figma --> Code | MCP + AI Agent | Section 3 |
| Display code in Figma | Code --> Figma | Code Connect | Sections 4-5 |
| Link components bidirectionally | Both | MCP + Code Connect | Sections 3-5 |

For questions or issues not covered here, consult the Figma Developer MCP documentation at https://github.com/nichochar/figma-developer-mcp and the Code Connect documentation at https://github.com/figma/code-connect.
