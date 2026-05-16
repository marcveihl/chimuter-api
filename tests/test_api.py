import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.commutes import load_commutes
from app.main import app, limiter

load_commutes()


@pytest_asyncio.fixture
async def client():
    limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_commutes_returns_list(client):
    resp = await client.get("/api/commutes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_commutes_has_real_commute(client):
    resp = await client.get("/api/commutes")
    data = resp.json()
    ids = [c["id"] for c in data]
    assert "cortland-upnw" in ids


@pytest.mark.asyncio
async def test_commute_structure(client):
    resp = await client.get("/api/commutes")
    data = resp.json()
    commute = next(c for c in data if c["id"] == "cortland-upnw")
    assert commute["name"] == "Cortland / Ashland ↔ UP-NW"
    assert commute["status"] == "active"
    assert "morning" in commute
    assert "evening" in commute
    assert len(commute["morning"]["feeders"]) == 2
    assert commute["morning"]["feeders"][0]["type"] == "bus"
    assert commute["morning"]["transfer"]["walk_min"] == 6
    assert commute["morning"]["metra"]["line"] == "UP-NW"


@pytest.mark.asyncio
async def test_commutes_has_placeholders(client):
    resp = await client.get("/api/commutes")
    data = resp.json()
    placeholders = [c for c in data if c["status"] == "placeholder"]
    assert len(placeholders) >= 1


@pytest.mark.asyncio
async def test_rate_limit(client):
    for _ in range(3):
        await client.get("/api/commutes")
    resp = await client.get("/api/commutes")
    assert resp.status_code == 429
