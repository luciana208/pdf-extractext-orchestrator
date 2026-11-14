import httpx
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from tests.integration.fake_services import FakeServices


@pytest_asyncio.fixture
async def services():
    return FakeServices()


@pytest_asyncio.fixture
async def client(services):
    # la app real con la red reemplazada por los servicios falsos
    app = create_app(transport=httpx.MockTransport(services.handler))
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
            yield http_client
