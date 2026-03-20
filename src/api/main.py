"""FastAPI application for Bittensor Subnet Intelligence System."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import subnets, signals, reports
from src.api.routes.signal_flow import router as signal_flow_router

_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Bittensor Intel API",
    description="Subnet intelligence system — flow analysis, signals, reports",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subnets.router)
app.include_router(signals.router)
app.include_router(reports.router)
app.include_router(signal_flow_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if _FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")
