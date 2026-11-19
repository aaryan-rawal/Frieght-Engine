"""Backend package entry point.

The FastAPI application is created here and includes routers for auth, cargo, match and health.
"""

from fastapi import FastAPI
from .api import auth, cargo, match, health

app = FastAPI(title="OptiFreight AI Backend", version="0.1.0")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cargo.router, prefix="/cargo", tags=["cargo"])
app.include_router(match.router, prefix="/match", tags=["match"])
app.include_router(health.router, prefix="/health", tags=["health"])
