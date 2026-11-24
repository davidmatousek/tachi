"""Anti-forgery token on state changes.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
def check_csrf(request):
    sent = request.headers.get("x-csrf-token", "")
    if not constant_time_equal(sent, request.session.csrf_token):
        raise Forbidden("anti-forgery check failed")
