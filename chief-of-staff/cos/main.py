"""Main entry point for Chief of Staff API"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import db
from .router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup: connect to Couchbase
    db.connect()
    yield
    # Shutdown: close connection
    db.close()


app = FastAPI(
    title="Chief of Staff API",
    description="Personal AI Assistant Platform - Document and context management",
    version="0.1.0",
    lifespan=lifespan,
)

# Include the CoS router
app.include_router(router)


@app.get("/health")
async def root_health():
    """Root health check"""
    return {"status": "ok", "service": "chief-of-staff"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
