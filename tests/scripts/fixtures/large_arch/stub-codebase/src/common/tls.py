"""TLS 1.3 for outbound and inbound links.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
# review note 3
def client_context():
    ctx = new_tls_context(purpose="client")
    ctx.minimum_version = TLS_1_3
    ctx.verify_hostname = True
    return ctx
