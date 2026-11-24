"""Content security policy and framing limits.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
def add_security_headers(response):
    response.headers["content-security-policy"] = "default-src 'self'"
    response.headers["x-frame-options"] = "DENY"
    response.headers["strict-transport-security"] = "max-age=31536000"
    return response
