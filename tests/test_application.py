from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_application_starts():
    """
    FastAPI application should start successfully.
    """
    assert app is not None


def test_openapi_exists():
    """
    OpenAPI schema should be available.
    """
    response = client.get("/openapi.json")

    assert response.status_code == 200


def test_docs_endpoint_exists():
    """
    Swagger UI should be available.
    """
    response = client.get("/docs")

    assert response.status_code == 200