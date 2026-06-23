import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.database import init_db, close_db


@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试前初始化数据库，测试后关闭连接"""
    await init_db()
    yield
    await close_db()


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
