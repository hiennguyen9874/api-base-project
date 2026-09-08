from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.http.exception_handlers import validation_exception_handler


class TokenRequest(BaseModel):
    access_token: str


@pytest.mark.unit
@pytest.mark.parametrize(
    "body",
    [
        '{"access_token":["review-only-not-a-real-token"]}',
        '{"access_token":{"review-only-not-a-real-token":true}}',
        '{"access_token":"review-only-not-a-real-token",',
    ],
)
async def test_validation_does_not_echo_request_secrets(body: str) -> None:
    app = FastAPI()
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore

    @app.post("/token")
    async def submit_token(request: TokenRequest) -> dict[str, Any]:
        return {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/token", content=body, headers={"Content-Type": "application/json"}
        )
    assert response.status_code == 422
    assert "review-only-not-a-real-token" not in response.text
    assert "input" not in response.text
    assert "ctx" not in response.text
