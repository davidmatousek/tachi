#!/usr/bin/env bash
# polish-release-notes.sh — Rewrite auto-generated release notes via Claude API
#
# Run locally after merging a Release PR:
#   TAG_NAME=v4.5.0 ./scripts/polish-release-notes.sh
#
# ANTHROPIC_API_KEY must be set in your environment (e.g., .zshrc or .env).
# Requires: gh (authenticated), jq, curl
# Graceful fallback: keeps auto-generated notes if Claude API is unavailable.

set -euo pipefail

: "${TAG_NAME:?TAG_NAME is required}"
: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY is required}"

# Get the auto-generated release body
RELEASE_BODY=$(gh release view "$TAG_NAME" --json body --jq '.body')

# Extract feature numbers from the release body (e.g., **112:** ...)
FEATURE_NUMS=$(echo "$RELEASE_BODY" | grep -oP '\*\*\K\d{2,4}' | sort -u || true)

# Gather spec context for each feature
SPEC_CONTEXT=""
for num in $FEATURE_NUMS; do
  padded=$(printf "%03d" "$num")
  spec_file=$(find specs/ -path "*${padded}*/spec.md" -o -path "*${num}-*/spec.md" 2>/dev/null | head -1)
  if [ -n "$spec_file" ]; then
    stories=$(sed -n '/^## User Scenarios/,/^## Requirements/p' "$spec_file" | head -60)
    if [ -n "$stories" ]; then
      SPEC_CONTEXT="${SPEC_CONTEXT}
=== Feature ${num} ===
${stories}
"
    fi
  fi
done

# Build the prompt
read -r -d '' PROMPT << 'ENDPROMPT' || true
Rewrite these auto-generated release notes into polished, user-facing release notes.

Rules:
- Write for adopters, not maintainers. Describe outcomes, not commits.
- Each feature gets 1-2 sentences explaining what it does and why it matters.
- Each bug fix gets one sentence explaining what was broken and what is fixed.
- Group under What's New, Bug Fixes, Performance as applicable.
- Remove internal references (PR numbers, commit SHAs, agent names).
- Keep the version header and date from the original.
- If a change is a breaking change, call it out prominently.
- Be concise. No filler. No marketing language.
- Output ONLY the rewritten markdown. No preamble.
ENDPROMPT

# Call Claude API
PAYLOAD=$(jq -n \
  --arg prompt "$PROMPT" \
  --arg notes "$RELEASE_BODY" \
  --arg context "$SPEC_CONTEXT" \
  '{
    model: "claude-sonnet-4-20250514",
    max_tokens: 2048,
    messages: [{
      role: "user",
      content: ($prompt + "\n\n## Auto-generated notes:\n\n" + $notes + "\n\n## Feature context from specs:\n\n" + $context)
    }]
  }')

RESPONSE=$(curl -s -w "\n%{http_code}" \
  https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Warning: Claude API returned $HTTP_CODE — keeping auto-generated notes"
  echo "$BODY" | head -5
  exit 0
fi

POLISHED=$(echo "$BODY" | jq -r '.content[0].text')

if [ -z "$POLISHED" ] || [ "$POLISHED" = "null" ]; then
  echo "Warning: Empty response from Claude API — keeping auto-generated notes"
  exit 0
fi

gh release edit "$TAG_NAME" --notes "$POLISHED"
echo "Release notes polished for $TAG_NAME"
