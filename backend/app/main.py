from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import httpx

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.database import AsyncSessionLocal, create_tables
from app.config import settings


app = FastAPI(
    title="Lenny Growth Assistant API",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://lenny-growth-assistant-eight.vercel.app",
    ],
    allow_origin_regex=r"https://lenny-growth-assistant-[a-z0-9-]+-sravika-s-projects\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    await create_tables()


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(sessions_router)
app.include_router(chat_router)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Lenny Growth Assistant API is running!"
    }


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/api/health")
async def health():
    health_status = {
        "status": "ok",
        "database": "unknown",
        "ollama": "not_used",
        "llm_provider": settings.default_llm_provider,
        "llm": "unknown",
    }

    # Database health
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))

        health_status["database"] = "ok"

    except Exception:
        health_status["database"] = "error"
        health_status["status"] = "degraded"

    # LLM health
    provider = settings.default_llm_provider.lower()

    if provider == "ollama":

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.ollama_base_url}/api/tags"
                )

            response.raise_for_status()

            health_status["ollama"] = "ok"
            health_status["llm"] = "ok"

        except Exception:
            health_status["ollama"] = "error"
            health_status["llm"] = "error"
            health_status["status"] = "degraded"

    elif provider in ["gemini", "google"]:

        if settings.gemini_api_key:
            health_status["ollama"] = "not_used"
            health_status["llm"] = "configured"

        else:
            health_status["llm"] = "not_configured"
            health_status["status"] = "degraded"

    elif provider == "anthropic":

        if settings.anthropic_api_key:
            health_status["ollama"] = "not_used"
            health_status["llm"] = "configured"

        else:
            health_status["llm"] = "not_configured"
            health_status["status"] = "degraded"

    else:

        health_status["llm"] = "unsupported"
        health_status["status"] = "degraded"

    return health_status