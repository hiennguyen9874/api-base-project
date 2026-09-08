"""OpenAPI contract for the cookie-based authentication surface (#24).

The generated web client is produced from this document, so the auth endpoints
must describe the shapes the browser actually receives: form-encoded login, the
bare Token login body, the enveloped refresh body, and the 401/429 failures the
session layer must handle.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.main import app


@pytest.mark.api
def test_login_documents_form_encoding_and_bare_token_response() -> None:
    schema = app.openapi()
    login = schema["paths"]["/api/v0/authen/login"]["post"]

    content = login["requestBody"]["content"]
    assert "application/x-www-form-urlencoded" in content
    assert "application/json" not in content

    assert login["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/Token"
    }


@pytest.mark.api
def test_auth_surface_documents_unauthorized_and_rate_limit_failures() -> None:
    schema = app.openapi()
    paths = {
        "login": schema["paths"]["/api/v0/authen/login"]["post"],
        "refresh": schema["paths"]["/api/v0/authen/refresh"]["post"],
        "logout": schema["paths"]["/api/v0/authen/logout"]["post"],
        "users/me": schema["paths"]["/api/v0/users/me"]["get"],
    }

    for name, operation in paths.items():
        assert "401" in operation["responses"], name
        assert operation["responses"]["401"]["content"]["application/json"]["schema"][
            "$ref"
        ].startswith("#/components/schemas/ErrorResponse"), name

    assert "429" in paths["login"]["responses"]
    assert paths["login"]["responses"]["429"]["content"]["application/json"]["schema"][
        "$ref"
    ].startswith("#/components/schemas/ErrorResponse")


@pytest.mark.api
def test_refresh_and_users_me_document_enveloped_success_bodies() -> None:
    schema = app.openapi()
    components: dict[str, Any] = schema["components"]["schemas"]

    refresh = schema["paths"]["/api/v0/authen/refresh"]["post"]
    refresh_ref = refresh["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert refresh_ref == "#/components/schemas/SuccessfulResponse_Token_"
    assert set(components["SuccessfulResponse_Token_"]["properties"]) == {
        "status",
        "data",
        "error",
    }
    assert components["SuccessfulResponse_Token_"]["properties"]["data"] == {
        "$ref": "#/components/schemas/Token",
        "title": "Data",
    }

    me = schema["paths"]["/api/v0/users/me"]["get"]
    me_ref = me["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert me_ref == "#/components/schemas/SuccessfulResponse_User_"
