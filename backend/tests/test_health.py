import pytest

from tests.conftest import client as client_fixture  # noqa: F401


@pytest.mark.anyio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "auth_exists" in data


@pytest.mark.anyio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data


@pytest.mark.anyio
async def test_videos_endpoint(client):
    resp = await client.get("/api/videos")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
