"""Role check on every request.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
# review note 3
def require_role(role):
    def guard(request):
        if role not in directory.roles_for(request.principal):
            raise Forbidden(request.principal, role)
    return guard
