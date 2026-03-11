"""
LeadRadar — FastAPI ana uygulama
B2B lead intelligence platformu backend.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from enrichment.queue_worker import start_queue_worker, stop_queue_worker
from routers.discovery import router as discovery_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç/bitiş — kuyruk worker'ı yönetir."""
    # Startup: enrichment kuyruğu dinlemeye başla
    start_queue_worker()
    yield
    # Shutdown: worker'ı durdur
    stop_queue_worker()


app = FastAPI(
    title="LeadRadar API",
    description="B2B Lead Intelligence Platformu",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — Next.js frontend için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discovery_router)


@app.get("/")
async def root():
    """Sağlık kontrolü."""
    return {"status": "ok", "service": "LeadRadar API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
