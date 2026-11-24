"""Append-only audit writer.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
# review note 3
def record(event):
    entry = {"at": utc_now(), "who": event.principal, "what": event.action}
    entry["prev"] = ledger.tail_hash()
    ledger.append(entry)
    return entry["prev"]
