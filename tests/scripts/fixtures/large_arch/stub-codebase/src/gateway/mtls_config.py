"""Mutual TLS between internal services.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
def internal_context(ca_bundle, cert, key):
    ctx = new_tls_context(purpose="server")
    ctx.load_chain(cert, key)
    ctx.require_client_certificate(ca_bundle)
    return ctx
