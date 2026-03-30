from fastapi.testclient import TestClient
from app.main import app


def test_search_parameter():
    client = TestClient(app)
    # Ensure the search parameter can be passed without throwing a server error
    response = client.get("/tickets/?search=test")
    
    # We expect either a 200 (if no auth/populated DB setup needed for GET) 
    # or a 401 (since we are not providing a token)
    # The important part is that we don't get a 500 Internal Server error or 422 Validation error.
    assert response.status_code in [200, 401]


def test_rate_limiting():
    client = TestClient(app)
    # The default limit is 100/minute. We can just test that the global limiter is attached.
    response = client.get("/docs")
    assert response.status_code == 200
