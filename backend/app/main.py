from fastapi import FastAPI

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routers import auth, tickets, dashboard, comments, files

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def create_app() -> FastAPI:
    app = FastAPI(title="Smart Support Desk API")

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
    app.include_router(comments.router, prefix="/comments", tags=["comments"])
    app.include_router(files.router, prefix="/files", tags=["files"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

    return app


app = create_app()

