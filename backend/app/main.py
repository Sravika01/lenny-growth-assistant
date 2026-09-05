from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.database import AsyncSessionLocal
from app.config import settings

app = FastAPI(
    title="Lenny Growth Assistant API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Lenny Growth Assistant API is running!"
    }


@app.get("/api/health")
async def health():
    health_status = {
        "status": "ok",
        "database": "unknown",
        "ollama": "unknown",
    }

    # Check PostgreSQL
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))

        health_status["database"] = "ok"

    except Exception:
        health_status["database"] = "error"
        health_status["status"] = "degraded"

    # Check Ollama
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.ollama_base_url}/api/tags"
            )

        response.raise_for_status()
        health_status["ollama"] = "ok"

    except Exception:
        health_status["ollama"] = "error"
        health_status["status"] = "degraded"

    return health_status