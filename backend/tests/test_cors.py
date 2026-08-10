from fastapi.testclient import TestClient

from main import app


def test_local_frontend_preflight_is_allowed_in_development() -> None:
    response = TestClient(app).options(
        "/api/users/create",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
