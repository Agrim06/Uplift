from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.middleware import RequestLoggingMiddleware
from contextlib import asynccontextmanager

from app.api.routers import chat, health, schemes
from app.config.errors import setup_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Uplift backend...")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Scheme Recommender AI",
    description="Agentic backend for government scheme eligiblity",
    version="1.0.0",
    lifespan= lifespan
)

#CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup Global Error Handling
setup_exception_handlers(app)

#routers
app.include_router(health.router, prefix="/api/v1", tags=["System"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Agent Workflow"])
app.include_router(schemes.router, prefix="/api/v1/schemes", tags=["Schemes Data"])