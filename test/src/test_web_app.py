from fastapi.testclient import TestClient
from src.web_app.app import app
from utils.utils import log, log_error

client = TestClient(app)

def test_query_endpoint():
    try:
        log("Starting test: test_query_endpoint", "info")
        response = client.post("/query", json={"query": "What was the total revenue for the company in FY 2023?", "company_id": 123})
        assert response.status_code == 200
        assert "response" in response.json()
        assert isinstance(response.json()["response"], str)
        log("Completed test: test_query_endpoint", "info")
    except Exception as e:
        log_error(f"Error in test_query_endpoint: {e}", exception_to_raise=RuntimeError)
