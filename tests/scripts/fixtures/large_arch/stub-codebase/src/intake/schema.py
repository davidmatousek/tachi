"""Schema validation of structured requests.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
def parse_request(payload):
    data = REQUEST_SCHEMA.validate(payload, extra="forbid")
    if len(data["text"]) > MAX_TEXT:
        raise Rejected("request too large")
    return data
