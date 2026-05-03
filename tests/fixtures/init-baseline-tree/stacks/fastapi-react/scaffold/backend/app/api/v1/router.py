"""API v1 router aggregation.

Include domain-specific routers here as the application grows.
Each domain gets its own APIRouter in a separate module
(e.g., users.py, auth.py, items.py).

Example:
    from app.api.v1.users import router as users_router
    api_router.include_router(users_router, prefix="/users", tags=["users"])
"""

from fastapi import APIRouter

api_router = APIRouter()

# Include domain routers below:
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
