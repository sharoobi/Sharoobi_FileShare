from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.bootstrap import seed_database
from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.models import Base
from app.routers import agent_runtime, auth, devices, health, host_bridge, jobs, overview, packages, policies, shares

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session, settings)
    yield


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="Local-first shared-path control plane for Sharoobi FileShare.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(agent_runtime.router)
app.include_router(overview.router)
app.include_router(host_bridge.router)
app.include_router(shares.router)
app.include_router(devices.router)
app.include_router(jobs.router)
app.include_router(policies.router)
app.include_router(packages.router)
