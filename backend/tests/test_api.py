import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Lenny Growth Assistant API is running!"
    )


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "database" in data
    assert "ollama" in data