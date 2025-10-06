"""
FastAPI routers package.
"""
from .chat import router as chat_router
from .users import router as users_router
from .skills import router as skills_router
from .documents import router as documents_router
from .plans import router as plans_router

__all__ = [
    "chat_router",
    "users_router", 
    "skills_router",
    "documents_router",
    "plans_router"
]
