"""Per-agent tool allowlist.

Synthetic stub for the large-architecture fixture. It is never run.
"""

def allowed(agent_id, tool, arguments):
    entry = ALLOWLIST.get(agent_id, {}).get(tool)
    if entry is None:
        return False
    return entry.accepts(arguments)
