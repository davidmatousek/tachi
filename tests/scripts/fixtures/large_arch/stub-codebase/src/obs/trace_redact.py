"""Trace redaction before storage.

Synthetic stub for the large-architecture fixture. It is never run.
"""

def redact(span):
    for field in SENSITIVE_FIELDS:
        if field in span.attributes:
            span.attributes[field] = "[redacted]"
    return span
