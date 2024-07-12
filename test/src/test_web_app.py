from fastapi.testclient import TestClient
from web_app.app import app
from utils.config_management import log

client = TestClient(app)

def test_query_endpoint():
    log("Starting test: test_query_endpoint", "info")
    response = client.post("/query", json={"query": "What was the total revenue for the company in FY 2023?", "company_id": 123})
    assert response.status_code == 200
    assert "response" in response.json()
    assert isinstance(response.json()["response"], str)
    log("Completed test: test_query_endpoint", "info")
