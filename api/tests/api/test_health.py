import pytest
from httpx import AsyncClient


@pytest.mark.unit
@pytest.mark.api
async def test_health(asgi_client: AsyncClient) -> None:
    response = await asgi_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
